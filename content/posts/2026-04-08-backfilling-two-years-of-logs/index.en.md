---
title: "Backfilling Two Years of Logs: Enterprise-Grade Observability on a Raspberry Pi"
date: 2026-04-08
tags: [ai-generated, sysadmin, observability, projects]
description: "How I replayed 25 million log entries through a full enrichment pipeline — GeoIP, ASN, reverse DNS — on a Raspberry Pi 5, with Claude doing the heavy lifting on code."
---

![BSD daemon with telemetry flowing through an enrichment pipeline into VictoriaLogs](/posts/2026-04-08-backfilling-two-years-of-logs/cover.png)

I have a FreeBSD server called m42 that's been running for years. It handles email (Postfix + Dovecot + Rspamd), web (nginx with a dozen vhosts), firewall (pf), and all the usual suspects. It generates thousands of log entries per day across four distinct formats: BSD syslog, fail2ban, pf packet filter, and nginx access/error logs.

I even wrote [pfasciilogd](/posts/2023-08-17-pfasciilogd-link-pf-and-fail2ban/) back in 2023 to convert pf's binary logs into ASCII text so fail2ban could parse them — a foundational piece that now feeds structured firewall telemetry into the whole pipeline.

I also have two years of monthly backups sitting in [restic](https://restic.net/) snapshots. That's roughly 25 million log lines, just... sitting there. A goldmine of security telemetry, traffic patterns, and attack data — completely unindexed and unsearchable.

I built a full observability stack on a Raspberry Pi 5 at home — [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) for storage, [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) for processing, [Grafana](https://grafana.com/) for visualization — and then I backfilled every single one of those 25 million entries through the exact same pipeline that processes live data. With full enrichment: GeoIP geolocation, ASN identification, and reverse DNS resolution for every IP address.

This is enterprise-grade log management. Running on a $80 single-board computer. In my living room.

## Why backfills are hard (and usually skipped)

Let's be honest: nobody does backfills. They're the broccoli of operations work. You know you should, but the effort-to-reward ratio feels terrible.

The problem is that a backfill isn't just "load old data." Your pipeline has evolved. The parsing rules you wrote six months ago don't match today's processors. The enrichment you added last week doesn't exist in your old backfill scripts. You end up with two classes of data: rich live entries and impoverished historical ones.

The naive approach — writing Python scripts that replicate your pipeline's logic — works initially. I did it. Twice. It produced data that looked right but was subtly wrong: different field names, missing enrichment, different parsing behavior. Every time I added a new processor to the live pipeline, the backfill scripts drifted further from reality.

## The architectural insight: replay, don't rewrite

The fix was embarrassingly simple: **stop duplicating the pipeline in Python and just replay the raw logs through the real thing.**

The live pipeline works like this:

```
m42 (syslog-ng) → TCP:514 → Telegraf → Starlark → GeoIP → Reverse DNS → VictoriaLogs
```

syslog-ng on m42 wraps every log line in an [RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424) envelope and ships it over TCP with a reliable disk-backed buffer. Telegraf receives it and runs it through a chain of processors:

1. **Starlark processors** (order 1) — four separate scripts that extract structured fields from each log type: pf firewall rules get parsed into action/direction/IPs/ports/protocol, fail2ban entries get jail/action/IP, nginx gets vhost/kind/client IP, postfix gets queue IDs and mail addresses
2. **GeoIP enricher** (order 2) — a custom Go binary running as an execd processor that maps every public IP to country, city, coordinates, ASN, and organization using MaxMind's GeoLite2 databases
3. **Reverse DNS** (order 3) — PTR lookups for every extracted IP, resolved through a local [Technitium](https://technitium.com/dns/) DNS server with aggressive caching

The backfill script became a **log replayer**: read the raw files, wrap each line in an RFC 5424 envelope with the correct timestamp and metadata, and send it to Telegraf over TCP. That's it. Zero content parsing. The script went from ~700 lines of Python (with GeoIP libraries, regex extractors, HTTP posting) to ~350 lines that do nothing but envelope construction and TCP sending.

```python
def rfc5424(pri: int, ts: str, appname: str, procid: str, msg: str) -> str:
    return f"<{pri}>1 {ts} {HOSTNAME} {appname} {procid} - - {msg}"

def send_rfc5424(sock: socket.socket, msg: str) -> None:
    encoded = msg.encode("utf-8")
    frame = f"{len(encoded)} ".encode("ascii") + encoded
    sock.sendall(frame)
```

TCP backpressure handles flow control — when Telegraf can't keep up (mostly due to DNS lookups), the TCP send blocks. No data loss, no buffering complexity, no rate limiting logic. The protocol does the work.

## The enrichment pipeline

Here's what a single pf firewall entry looks like after full processing:

```
Raw log line:
  2024-05-29T22:00:08.006704+02:00 rule 1/0(match): block in on vtnet0:
  141.98.7.190.56034 > 46.38.233.77.8728: Flags [S]

After enrichment:
  pf_action     = block
  pf_direction  = in
  pf_interface  = vtnet0
  pf_proto      = tcp
  pf_src_ip     = 141.98.7.190
  pf_src_port   = 56034
  pf_dst_ip     = 46.38.233.77
  pf_dst_port   = 8728
  geo_country   = DE
  geo_city      = Frankfurt am Main
  asn           = AS215439
  as_org        = Play2go International Limited
```

Every log type gets this treatment. A postfix entry gets `mail_client_ip`, `mail_client_host` (reverse DNS), geolocation, and ASN for the connecting mail server. A fail2ban entry gets `f2b_jail`, `f2b_action`, `f2b_ip` with full geo and DNS. An nginx entry gets `vhost`, `client_ip`, `client_host`, and geo. All of it searchable, filterable, and visualizable in Grafana.

The Starlark processors handle both IPv4 and IPv6 natively — m42 is dual-stack, and a surprising amount of traffic (especially SSH brute-force attempts) comes over IPv6.

## What made this possible

This project would not exist without AI assistance. I would not have had the time to build both a robust enrichment pipeline AND a full backfill system. One or the other, maybe. Both? Not a chance.

But — and this is the crucial point — **AI didn't build this from nothing.** The reason Claude could be so effective is that the infrastructure was already clean:

- **restic snapshots** — two years of monthly server backups, consistently structured, ready to be read
- **Docker with macvlan networking** — every service has its own IP on a dedicated VLAN, clean isolation
- **Telegraf already running** — the processor pipeline (inputs, processors, outputs) was already structured and documented
- **VictoriaLogs already ingesting** — live logs were flowing, the schema was proven
- **A well-maintained CLAUDE.md** — engineering principles that kept the AI focused: "read before writing," "fix root causes not symptoms," "never fabricate explanations"

Clean infrastructure compounds. Every shortcut you didn't take, every backup you configured, every piece of documentation you wrote — it all becomes leverage when you need to build something ambitious on top of it. AI amplifies what's already there. If the foundation is solid, the amplification is extraordinary. If the foundation is chaos, AI just amplifies the chaos faster.

## A word on iteration

Here's what I'd do differently: **spend even more time designing before coding.**

It's remarkably easy to get Claude to produce a working proof of concept. You describe what you want, and 30 seconds later you have running code. The dopamine hit is real. But for tasks like backfilling — where execution takes hours and you can't easily undo — a bad design means you redo the entire run. Multiple times.

I went through several iterations of this backfill. Each time I discovered something the pipeline handled that the backfill scripts didn't — IPv6 support, reverse DNS, a Starlark processor I'd forgotten about. Each redo meant: delete 25 million entries, wait, re-run for 8+ hours, verify. 

The lesson: the cost of an extra hour of design is trivial compared to an 8-hour backfill you have to throw away. Do your brainstorming. Audit field by field. Compare live entries against what your tool produces. Then — and only then — pull the trigger.

## The numbers

- **25 million entries** across four log formats (BSD syslog, fail2ban, pf, nginx)
- **Two years** of restic snapshots (2024-05 through 2026-04)
- **~350 lines of Python** for the replay script (down from ~700 lines that duplicated pipeline logic)
- **Four Starlark processors**, one Go GeoIP enricher, one reverse DNS resolver
- **~8 hours** to replay everything through the full pipeline
- Running on a **Raspberry Pi 5** (4 cores, 16GB RAM, NVMe) in my living room

The Pi hit a load average of 19 on 4 cores during the backfill — it was working hard, but it handled it. The live pipeline kept running in parallel throughout. No entries lost, no services disrupted.

## Try this at home

The entire stack is open and reproducible:

- [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) — free, single-binary log storage with LogsQL
- [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) — plugin-based metrics and log processor
- [Grafana](https://grafana.com/) — dashboards and alerting
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — free IP geolocation databases
- [restic](https://restic.net/) — encrypted, deduplicated backups
- [syslog-ng](https://www.syslog-ng.com/) — reliable log transport with disk-backed buffering
- [Claude Code](https://claude.ai/code) — the AI that made building all of this feasible in the time I had

If you have server backups sitting around, your historical logs are in there. And if you have a pipeline that processes live data, you already have everything you need to enrich them. Don't write a separate backfill tool — replay through the real thing.

Your past data deserves the same treatment as your live data. It's all signal.
