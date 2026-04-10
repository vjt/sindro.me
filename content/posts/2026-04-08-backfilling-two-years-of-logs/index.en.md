---
title: "Three Telegraf Bugs and 25 Million Log Lines"
date: 2026-04-08
tags: [ai-generated, sysadmin, observability, projects]
description: "How a syslog backfill through Telegraf on a Raspberry Pi uncovered three upstream bugs — a DNS retry storm, a missing serialization mode, and a pipe deadlock."
---

![BSD daemon with telemetry flowing through an enrichment pipeline into VictoriaLogs](/posts/2026-04-08-backfilling-two-years-of-logs/cover.jpg)

I have a FreeBSD server called m42 that's been running for years. Email, web, firewall, the usual. Two and a half years of monthly [restic](https://restic.net/) backups sitting in snapshots — roughly 25 million syslog lines across four formats: BSD syslog, fail2ban, pf packet filter, and nginx. A goldmine of security telemetry, completely unindexed and unsearchable.

I built an observability stack on a Raspberry Pi 5 at home — [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) for storage, [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) for processing, [Grafana](https://grafana.com/) for visualization — and decided to backfill every single one of those 25 million entries through the exact same enrichment pipeline that processes live data. GeoIP geolocation, ASN identification, reverse DNS for every IP address.

The backfill itself was straightforward. What wasn't straightforward: the three bugs it exposed in Telegraf's internals. The kind of bugs that only surface under sustained load. The kind nobody hits because nobody does this.

## The architecture: replay, don't rewrite

The naive approach is to write Python scripts that replicate your pipeline — parse logs, enrich with GeoIP, POST to your log store. I did this. Twice. Each time the scripts drifted from the live pipeline: different field names, missing enrichment, parsing inconsistencies between Starlark and Python regex.

The fix was embarrassingly simple: **stop duplicating the pipeline and just replay the raw logs through the real thing.**

The live pipeline:

```
m42 (syslog-ng) → TCP:514 → Telegraf → Starlark → GeoIP → Reverse DNS → VictoriaLogs
```

The backfill script became a log replayer: read the raw files, wrap each line in an [RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424) envelope with the correct timestamp, send it to Telegraf over TCP with [octet-counting framing](https://datatracker.ietf.org/doc/html/rfc6587#section-3.4.1). That's it. Zero content parsing. The enrichment pipeline handles everything identically to live data.

```python
def send_rfc5424(sock, msg):
    encoded = msg.encode("utf-8")
    frame = f"{len(encoded)} ".encode("ascii") + encoded
    sock.sendall(frame)
```

TCP backpressure handles flow control — when Telegraf can't keep up, `sendall()` blocks. No buffering complexity, no rate limiting logic, no data loss. The protocol does the work.

In theory, anyway. In practice, we found three bugs.

## Bug 1: The DNS retry storm (reverse_dns negative cache)

The first thing that happened when we started pumping 8,000 lines per second was that Telegraf ground to a halt. Zero throughput. Every worker blocked.

The `reverse_dns` processor does PTR lookups for every IP address in every log line. Most external IPs — scanner bots, brute-force attackers, random internet noise — have no PTR record. The DNS server returns NXDOMAIN immediately. Stock Telegraf's response: **delete the cache entry and try again next time.** Every. Single. Time.

With 25 million log lines containing thousands of unique unresolvable IPs, this creates an infinite retry storm. All 200 DNS workers permanently saturated retrying IPs that will never resolve. The blocking `Enqueue()` in the parallel worker pool propagates backpressure through the entire pipeline. Nothing moves.

The fix: **negative caching.** When a PTR lookup fails, cache the negative result for a configurable `negative_cache_ttl` (default 15 minutes) instead of deleting the entry. The workers stay busy for a few minutes while the cache warms, then throughput stabilizes as cached negatives prevent retries.

```go
// Before (stock): delete on failure → infinite retries
delete(d.cache, lookup.ip)

// After (patched): cache negative result → retry after TTL
lookup.completed = true
lookup.domains = nil
lookup.expiresAt = time.Now().Add(d.negativeTTL)
d.lockedSaveToCache(lookup)
```

The evidence was dramatic. We verified it during the backfill by sampling DNS errors 30 seconds apart:

- **T=0**: 13 unique IPs failing (first-time lookups, cold cache)
- **T=30s**: **zero** failures — negative cache serving cached results silently

Every new IP fails exactly once, gets cached, and never retries for 15 minutes. Stock Telegraf would hammer the same IPs forever.

## Bug 2: NDJSON batching (1000x fewer HTTP requests)

VictoriaLogs' `/insert/jsonline` endpoint expects [newline-delimited JSON](https://jsonlines.org/) — one JSON object per line. Telegraf's JSON serializer has a `SerializeBatch()` method that wraps metrics in `{"metrics":[...]}`, which VictoriaLogs doesn't understand. So each metric was being sent as a separate HTTP POST.

At 1,000 metrics per flush (default `metric_batch_size`), that's 1,000 HTTP round-trips per flush cycle instead of one. Over TLS. To localhost, but still.

We added a `json_newline_batch` option — when enabled, `SerializeBatch()` concatenates individual `Serialize()` outputs instead of wrapping them in an array:

```go
func (s *Serializer) SerializeBatch(metrics []telegraf.Metric) ([]byte, error) {
    if s.NewlineBatch {
        var buf []byte
        for _, m := range metrics {
            b, err := s.Serialize(m)
            if err != nil { return nil, err }
            buf = append(buf, b...)
        }
        return buf, nil
    }
    // ... existing {"metrics":[...]} logic
}
```

Ten lines of code, 1000x fewer HTTP requests. The kind of improvement that makes you wonder why it didn't exist already.

## Bug 3: The pipe deadlock (TCP stream input)

This one was the nastiest. After running smoothly at 8K/s for about five minutes, the pipeline would silently stop. No errors. No crashes. Just... zero throughput. TCP backpressure kicked in, the sender blocked on `sendall()`, and everything froze.

The goroutine dump told the story. In `plugins/common/socket/stream.go`, each TCP connection creates an `io.Pipe()` — the writer reads from the TCP socket, the reader feeds the parser:

```go
reader, writer := io.Pipe()
defer writer.Close()
go onConnection(src, reader)  // ← the problem

for {
    n, err := decoder.Read(buf)
    // ...
    writer.Write(buf[:n])  // blocks forever when reader exits
}
```

The `onConnection` callback runs in a goroutine. When it exits — for any reason — it doesn't close the pipe reader. The writer's `Write()` call blocks forever waiting for a reader that will never consume. The `defer writer.Close()` never fires because the function is stuck at the `Write()`. Classic resource leak deadlock.

The fix is one line:

```go
go func() {
    defer reader.Close()
    onConnection(src, reader)
}()
```

Nobody hit this before because it only manifests under sustained high-volume TCP input. Normal syslog at 1 msg/sec never triggers the race — the `onConnection` callback doesn't exit mid-stream. You need thousands of messages per second for minutes to hit it.

## The enrichment pipeline

Here's what makes the replay-through-Telegraf approach worth it. A single pf firewall entry goes from this:

```
2024-05-29T22:00:08 rule 1/0(match): block in on vtnet0:
  141.98.7.190.56034 > 46.38.233.77.8728: Flags [S]
```

To this:

```
pf_action     = block
pf_direction  = in
pf_src_ip     = 141.98.7.190
pf_dst_port   = 8728
pf_src_host   = (cached negative — no PTR)
geo_country   = DE
geo_city      = Frankfurt am Main
asn           = AS215439
as_org        = Play2go International Limited
```

Every log type gets this treatment. Postfix entries get mail client geolocation and reverse DNS. Fail2ban gets jail/action/IP with full geo. Nginx gets vhost, client IP, and ASN. All of it searchable and filterable in Grafana. Both IPv4 and IPv6 — m42 is dual-stack, and a surprising amount of brute-force traffic comes over IPv6.

The Starlark processors handle the parsing (four scripts, one per log format). A custom Go binary does GeoIP enrichment via MaxMind's GeoLite2 databases. The reverse DNS processor — now with negative caching — does PTR lookups through a local [Technitium](https://technitium.com/dns/) DNS server.

## The numbers

- **25.3 million entries** across four log formats (BSD syslog, fail2ban, pf, nginx)
- **34 monthly files**, July 2023 through April 2026
- **~8,000 lines/sec** sustained throughput (DNS-bound with 200 workers)
- **Zero data loss** — TCP backpressure, zero buffer drops
- **~1 hour** total replay time
- **Three upstream bugs** found and fixed
- Running on a **Raspberry Pi 5** (4 cores, 16GB RAM, NVMe) in my living room

## What made this possible

This project would not exist without AI assistance. I would not have had the time to build both a robust enrichment pipeline AND debug three Telegraf internals bugs AND write a full backfill system. Claude did the heavy lifting on code while I made the architectural decisions and caught the design errors.

But — and this is the crucial point — **AI didn't build this from nothing.** The reason Claude could be so effective is that the infrastructure was already clean:

- **restic snapshots** — two and a half years of monthly server backups, consistently structured
- **Docker with macvlan networking** — every service has its own IP on a dedicated VLAN
- **Telegraf already running** — the processor pipeline was structured and documented
- **VictoriaLogs already ingesting** — live logs flowing, schema proven
- **A well-maintained CLAUDE.md** — engineering principles that kept the AI focused

Clean infrastructure compounds. Every shortcut you didn't take, every backup you configured, every piece of documentation you wrote — it becomes leverage when you need to build something ambitious on top of it. AI amplifies what's already there. If the foundation is solid, the amplification is extraordinary.

## A word on iteration

Here's what I'd do differently: **spend even more time designing before coding.**

It's remarkably easy to get Claude to produce a working proof of concept. You describe what you want, and 30 seconds later you have running code. The dopamine hit is real. But for tasks like backfilling — where execution takes hours and you can't easily undo — a bad design means you redo the entire run.

I went through several iterations. Each time I discovered something the pipeline handled that the backfill scripts didn't — IPv6 support, reverse DNS interaction, a Starlark processor I'd forgotten about. Each redo meant: delete millions of entries, wait, re-run, verify. The final iteration — replaying raw RFC5424 through the actual pipeline — was the one that should have been the first.

The cost of an extra hour of design is trivial compared to a backfill you have to throw away.

## Try this at home

The entire stack is open and reproducible:

- [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) — free, single-binary log storage with LogsQL
- [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) — plugin-based metrics and log processor
- [Grafana](https://grafana.com/) — dashboards and alerting
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — free IP geolocation databases
- [restic](https://restic.net/) — encrypted, deduplicated backups
- [Claude Code](https://claude.ai/code) — the AI that made building all of this feasible in the time I had

If you have server backups sitting around, your historical logs are in there. And if you have a pipeline that processes live data, you already have everything you need to enrich them. Don't write a separate backfill tool — replay through the real thing.

Your past data deserves the same treatment as your live data. It's all signal.
