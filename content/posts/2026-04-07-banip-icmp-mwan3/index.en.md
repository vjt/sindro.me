---
title: "How banIP Nuked My WireGuard Throughput Since February"
date: 2026-04-07
tags: [openwrt, wireguard, networking, debugging, mwan3, banip]
description: "A firewall ICMP rate limit was dropping mwan3 health check replies, making the fiber link look flaky, forcing WireGuard traffic onto a 2 Mbps 5G backup. For two months."
featuredImage: cover.jpg
---

**TL;DR:** If you run OpenWrt with mwan3 (multi-WAN failover) and a **split-tunnel** WireGuard VPN (i.e., you're NOT routing all traffic through it), add `nohostroute=1` to your WireGuard interface. Without it, netifd creates a static route for the WireGuard endpoint at interface-up time, pinned to whatever uplink happens to be active at that moment. By the first corollary of Murphy's Law, anything that can go wrong will go wrong *at the worst possible moment* — so your primary link will be down precisely when WireGuard starts, and the endpoint route gets permanently stuck on the backup. Your VPN will be stuck on the slow backup while your primary link sits there doing nothing. You won't notice until you need to transfer something big.

(If you *are* routing all traffic through WireGuard, you **need** the host route to prevent a routing loop — but on a multi-WAN setup, the same stale-route problem applies. You'll need a different workaround, like a hotplug script that updates the endpoint route when mwan3 switches uplinks.)

Today I discovered that my WireGuard tunnel to a remote server has been crawling at **2 Mbps** since early February. The fix took two UCI commands. The root cause was the missing `nohostroute` flag — plus a bonus: my own firewall was sabotaging my own health checks, making the fiber look unreliable enough that the system never self-corrected.

Here's the full forensic story, because I'm still furious and you deserve to learn from my suffering.

But first, some context on how this investigation actually happened. I was working with an AI coding assistant (Claude Code) that has SSH access to my infrastructure. This is possible because I have a clean foundation: SSH key authentication everywhere, proper internal DNS (`m42`, `golem` resolve to the right VPN addresses), WireGuard mesh between all nodes, and the assistant connects through a `ssh-agent` running as a systemd user service. One environment variable and the AI can reach every machine in my network — and, critically, *cross-reference* what it finds on one machine with data from another. This investigation would have taken me hours of jumping between terminals. The AI did it in minutes, methodically testing hypotheses across three machines simultaneously. The infrastructure investment in proper SSH, DNS, and VPN paid off enormously.

## The symptom

I was rsync'ing some log archives from a remote FreeBSD server (`m42`, colocated in a datacenter) to my home Raspberry Pi 5 (`nowhere`). The transfer was agonizingly slow — about 200 KB/s for rsync, maybe 1 MB/s for tar over SSH.

I have a beefy fiber connection at home. The remote server is on a 100 Mbps line. The WireGuard tunnel between them runs through an OpenWrt router (`golem`, a GL.iNet MT-6000 running my own OpenWrt build) that handles dual-WAN failover via mwan3. Everything is properly configured. There's no reason this should be slow.

Yet here we are.

## Measuring the damage

```
$ iperf3 -c m42 -t 5 -R
[ ID] Interval  Transfer    Bitrate
[  5] 0.00-1.00  256 KBytes  2.10 Mbits/sec
[  5] 1.00-2.00  128 KBytes  1.05 Mbits/sec
[  5] 2.00-3.00  256 KBytes  2.10 Mbits/sec
```

**2 Mbps**. Through a WireGuard tunnel that should be doing 70+.

HTTPS downloads from the same server's public IP? 28 Mbps. So the server is fine. The internet is fine. WireGuard is the problem — or so I thought.

## Step 1: Is WireGuard the bottleneck?

My first instinct was that WireGuard crypto was somehow saturating the Pi's CPU. So I installed iperf3 and tested properly:

```
$ iperf3 -c m42 -t 5
[  5] 0.00-5.00  5.38 MBytes  9.01 Mbits/sec  sender
```

9 Mbps upload. Then the download (reverse) test:

```
$ iperf3 -c m42 -t 5 -R
[  5] 0.00-5.00  1.00 MBytes  1.68 Mbits/sec  receiver
```

Upload 9 Mbps, download 1.7 Mbps. Massive asymmetry. But then HTTPS from the server's public IP:

```
$ curl -o /dev/null -sk "https://46.38.233.77/test-10m.bin"
speed: 3,587,090 bytes/sec  # 28 Mbps
```

28 Mbps over HTTPS bypassing the VPN. The server's uplink is fine.

## Step 2: The dual-WAN rabbit hole

My router `golem` does dual-WAN failover with mwan3. Two uplinks:
- **Fiber** (`eth1`, metric 10) — primary
- **5G** (`br-lan.253`, VLAN on the LAN bridge to a 5G modem, metric 20) — backup

The default mwan3 policy `fiber_5g_backup` routes 100% via fiber when it's online. All looked correct:

```
$ ssh root@golem 'mwan3 status'
interface wan is online (online 60h:53m)
interface wan5g is online (online 83h:06m, uptime 1485h:25m)
fiber_5g_backup: wan (100%)
```

Both links online, fiber getting all traffic. But then I checked the actual WireGuard endpoint route:

```
$ ip route show 46.38.233.77
46.38.233.77 via 192.168.253.254 dev br-lan.253 proto static metric 20
```

The WireGuard endpoint was **pinned to the 5G backup link**. This is a static route created by netifd's `proto_add_host_dependency` when the WireGuard interface comes up. It resolves the endpoint hostname, looks up the current default route, and creates a static host route so the encrypted WireGuard UDP packets don't try to go through the tunnel itself (routing loop prevention).

The problem: this route is created once and never re-evaluated. Whatever gateway was active when WG came up is what it uses forever.

But **why would the system have picked the 5G link?** The fiber would need to be *down* for 5G to become the default.

## Step 3: Testing both uplinks

I ran iperf3 from golem directly to m42 through each WAN:

```
# Via WireGuard (through 5G, as we now know)
$ ssh root@golem 'iperf3 -c 192.168.50.42 -t 5'
5.25 MBytes  8.81 Mbits/sec  sender

# Reverse (m42 uploading to golem through WG)
$ ssh root@golem 'iperf3 -c 192.168.50.42 -t 5 -R'
768 KBytes  2.06 Mbits/sec  sender  # 15 retransmissions!
```

And confirmed the LAN between nowhere and golem was gigabit:

```
$ iperf3 -c 192.168.42.254 -t 3
335 MBytes  935 Mbits/sec
```

So the bottleneck was definitively **golem ↔ m42** through the WireGuard tunnel, which was going through the 5G link.

I then traced the actual network path. The 5G uplink goes through CGNAT (`172.20.x.x`), 25ms latency. The fiber goes through a different CGNAT (`172.17.x.x`), 3ms latency. The 5G link was never meant for bulk transfers.

## Step 4: But WHY was WG on the 5G link?

The fiber would have to be *down* at boot for 5G to become the default. First stop: `logread` on the router. Useless — the ring buffer only holds the current day's logs. But what it contained was already suspicious: page after page of mwan3 ping failures on the fiber interface:

```
Check (ping) failed for target "8.8.8.8" on interface wan (eth1). Current score: 10
Check (ping) failed for target "1.1.1.1" on interface wan (eth1). Current score: 10
Check (ping) failed for target "8.8.8.8" on interface wan (eth1). Current score: 10
```

Thousands of failures. Score bouncing between 9 and 10 — individual pings fail constantly, but enough succeed each cycle to keep the score from dropping to 0 (which would declare the interface dead). This was the first real clue.

All syslog from this router ships to VictoriaLogs (centralized log storage). Time for forensics. First, nail down when this started:

```
$ ssh root@golem 'mwan3 status | grep wan5g'
interface wan5g is online (online 83h:06m, uptime 1485h:25m)
```

1485 hours ÷ 24 = 61.8 days before April 7th → **February 4th**. Then I queried every mwan3 interface state change since:

```
$ curl -sk 'https://victorialogs/select/logsql/query' \
  --data-urlencode 'query=tags.hostname:golem AND ("is online" OR "is offline")'
```

The timeline was damning:

```
# First log entry: ping failures start immediately
2026-02-04T21:00  Check (ping) failed for "8.8.8.8" on wan (eth1). Score: 10
...failures every few minutes for 90 minutes...

# Then the score finally hits zero:
2026-02-04T22:30  Interface wan (eth1) is offline

# 8.7 HOURS later:
2026-02-05T07:13  Interface wan (eth1) is online

# Two more long outages in the next two days:
2026-02-06T10:45  Interface wan (eth1) is offline
2026-02-06T14:03  Interface wan (eth1) is online              # 3.3 hours offline
2026-02-06T22:56  Interface wan (eth1) is offline
2026-02-07T12:34  Interface wan (eth1) is online              # 13.6 hours offline

# Then silence for a month. After Feb 7, only brief blips:
2026-03-10T15:54  Interface wan (eth1) is offline
2026-03-10T15:58  Interface wan (eth1) is online              # 4 minutes
2026-03-14T00:03  Interface wan (eth1) is offline
2026-03-14T00:04  Interface wan (eth1) is online              # 52 seconds
2026-04-03T03:35  Interface wan (eth1) is offline
2026-04-03T03:36  Interface wan (eth1) is online              # 52 seconds
2026-04-05T06:53  Interface wan (eth1) is offline
2026-04-05T06:53  Interface wan (eth1) is online              # 53 seconds
```

Meanwhile, the 5G link logged dozens of offline/online flaps (the 5G modem reconnects constantly — noisy but irrelevant).

The picture was clear. In the first three days, mwan3 declared the fiber *dead* three times — for **8.7 hours**, **3.3 hours**, and **13.6 hours** respectively. After February 7th, the pattern changed: offline events became brief blips of under a minute.

And now I remembered: in early February, I had just finished setting up the [5G backup link](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) and was testing failover by **manually taking the fiber down** to see if the 5G could hold the entire household. During that testing, I noticed WireGuard kept sticking on the dead link, so I restarted it — `ifdown wg && ifup wg`. Which created the endpoint route through the 5G backup, because that's what was active at the time:

```
$ ip route show 46.38.233.77
46.38.233.77 via 192.168.253.254 dev br-lan.253 proto static metric 20
```

`proto static` — set by netifd at WireGuard interface-up time, present in both the main table and table 2 (wan5g). **Never updated. Never re-evaluated.** I brought the fiber back, everything looked fine, traffic flowed normally. But the WG endpoint route stayed cemented on 5G. I didn't dig into *why* WireGuard kept sticking — I just restarted it and moved on. Now I know: every restart re-created the static route via whatever gateway was active at that moment.

And those 102,935 "Check (ping) failed" entries VictoriaLogs had collected since? They explained the rest of the story. Even after my testing was done, mwan3 saw constant ping failures on the fiber, keeping the score at 9-10 (just barely online). Periodically, enough failures aligned to push the score to zero, and mwan3 would declare the fiber offline. In early February, those drops lasted hours because the score struggled to recover. By March, something shifted in the timing and recovery was fast — but the WG route was already cemented, and the system had no mechanism to fix it.

But wait — the fiber can't *actually* have this much packet loss. Right?

## Step 5: But the fiber is fine!

A sustained ping shows zero packet loss:

```
$ ssh root@golem 'ping -I eth1 -c 50 -W 2 8.8.8.8'
50 packets transmitted, 50 received, 0% packet loss
rtt min/avg/max/mdev = 12.631/13.010/13.827/0.264 ms
```

Perfect. 13ms, zero loss. So why do the one-shot pings from mwan3 fail?

## Step 6: Replicating mwan3's exact behavior

mwan3track uses a clever mechanism to bind pings to a specific interface: `LD_PRELOAD=/lib/mwan3/libwrap_mwan3_sockopt.so.1.0` — a shared library that intercepts socket calls and sets `SO_BINDTODEVICE` and the fwmark. I read through the mwan3track shell script to understand exactly how it pings, then replicated it:

```bash
# 30 one-shot pings, each a separate process
for i in $(seq 1 30); do
  ping -I eth1 -n -c 1 -W 4 8.8.8.8 > /dev/null 2>&1
  [ $? -ne 0 ] && echo "FAIL at $i"
done
```

Result:
```
FAIL at 8
FAIL at 11
FAIL at 19
FAIL at 27
Total failures: 4/30
```

**13% failure rate** — and the pattern is suspiciously regular. Every ~8 iterations.

But `ping -c 50` (single process, persistent socket) works perfectly. The difference between spawning 50 processes and keeping one socket open.

I tested three variants — with mwan3's `LD_PRELOAD` wrapper, with just `-I eth1`, and with no interface binding at all. **Same 4/30 failure rate in every case.** Not the wrapper, not the interface binding, not a timeout issue. Something about running `ping -c 1` as separate processes.

## Step 7: tcpdump reveals the truth

I captured packets during the failing pings:

```
19:56:00.406147 IP 192.168.254.1 > 8.8.8.8: ICMP echo request, id 20886
19:56:00.418955 IP 8.8.8.8 > 192.168.254.1: ICMP echo reply, id 20886
```

**The replies ARE arriving.** Every single one. The network has zero packet loss. Something between the network interface and the ping process is eating the replies.

## Step 8: The culprit — banIP ICMP flood protection

```
$ nft list ruleset | grep icmpflood
counter cnt_icmpflood { packets 8951 bytes 651072 }
meta nfproto . meta l4proto { ipv4 . icmp } limit rate over 25/second burst 5 packets
  counter name "cnt_icmpflood" drop
```

**8,951 ICMP packets dropped** by banIP's flood protection rule. Sitting in the `pre-routing` chain, applied only to the fiber WAN interface (`iifname "eth1"`).

The rule: drop any ICMP traffic exceeding 25 packets/second with a burst tolerance of **5 packets**.

Here's what happens: mwan3 tracks both WAN interfaces by pinging 3 targets each (1.1.1.1, 8.8.8.8, 208.67.222.222). That's 6 pings per cycle. Each one spawns a separate `ping -c 1` process. The replies arrive in a burst — and when that burst exceeds 5 packets within the rate window, nftables drops the excess **before they reach the ping process's socket**.

The `ping -c 50` persistent test works because it sends one packet per second with a single socket — well within the rate limit. The one-shot loop fails because the rapid-fire process spawning creates reply bursts.

## The full cascade

1. banIP drops ICMP replies arriving in bursts (by design — "flood protection")
2. mwan3 health checks + Telegraf pings create bursty ICMP patterns that hit the limit
3. mwan3 sees constant ping failures on fiber, periodically declaring it offline
4. In early February, while testing the new 5G backup, I manually downed the fiber and restarted WG
5. netifd created the WG endpoint route via 5G — the only active gateway at that moment
6. Fiber came back, traffic flowed normally — **but the WG static route stayed on 5G**
7. banIP kept causing sporadic fiber "outages," preventing the system from ever self-correcting
8. All WireGuard traffic: 2 Mbps instead of 70 Mbps. **For two months.**

## The fix

Two UCI commands:

```bash
# 1. Stop banIP from dropping mwan3's health check replies
uci set banip.global.ban_icmplimit=250
uci commit banip
/etc/init.d/banip restart

# 2. Stop netifd from creating a static endpoint route for WireGuard
uci set network.wg.nohostroute=1
uci commit network
ifdown wg && ifup wg
```

The first command raises the ICMP rate limit from 25/sec to 250/sec, so mwan3's bursty pings never hit the drop threshold.

The second command is the **actual root cause fix**. By default, netifd creates a static host route for the WireGuard endpoint IP to prevent routing loops (if all traffic went through the VPN, the encrypted packets would also try to go through the VPN → infinite loop). But I'm **not** routing all traffic through the VPN — only `192.168.50.0/24`. The endpoint IP `46.38.233.77` should just follow the default route, which mwan3 manages. Without `nohostroute=1`, a static route gets created at WireGuard interface-up time, pinned to whatever gateway happens to be active at that instant. If the fiber happens to be down when WG starts — because you're testing failover, because of a real outage, because banIP made mwan3 think it's dead — the route goes to 5G and stays there forever.

With `nohostroute=1`, there's no static route. WireGuard traffic to the endpoint follows the default route. If fiber goes down, mwan3 switches the default to 5G, and WireGuard follows automatically. When fiber comes back, it switches back. No stale routes, no manual intervention.

After applying both fixes:

```
$ iperf3 -c m42 -t 5 -R
[  5] 0.00-1.00  1.62 MBytes  13.6 Mbits/sec
[  5] 1.00-2.00  5.00 MBytes  41.9 Mbits/sec
[  5] 2.00-3.00  8.38 MBytes  70.3 Mbits/sec
[  5] 3.00-4.00  11.8 MBytes  98.5 Mbits/sec
[  5] 4.00-5.00  15.1 MBytes   127 Mbits/sec
```

**From 2 Mbps to 127 Mbps.** A 63x improvement.

## "Do you really need all these pings?"

After the fix, I asked myself: is banIP's default burst of 5 too low, or am I pinging too much?

Let's count. mwan3 tracks 3 targets per interface, `ping -c 1` each, every 5 seconds. That's 3 ICMP echo replies arriving on eth1 within ~20ms (13ms for 8.8.8.8, 16ms for 1.1.1.1, ~20ms for 208.67.222.222). At a burst tolerance of 5 packets with a refill rate of 25/sec (one token every 40ms), 3 replies in 20ms consumes 3 tokens while only half a token has refilled. Tight, but should survive — barely.

Except I also have **Telegraf** running on the same router, doing latency measurements:

```toml
[[inputs.ping]]
  urls = ["google.com", "reddit.com", "facebook.com", "sindro.me", "8.8.8.8", "1.1.1.1"]
  method = "native"
  count = 10
  ping_interval = 0.5
  interface = "192.168.254.1"
```

Six targets, 10 pings each, every 0.5 seconds, bound to the same `eth1` interface. That's **60 ICMP echo replies** per measurement cycle, all arriving in bursts on the fiber WAN. With a burst tolerance of 5, banIP was massacring them.

So the constant mwan3 failures weren't just from mwan3's own 3 pings hitting the limit — it was Telegraf's 60 pings **consuming all the burst tokens**, leaving nothing for mwan3's health checks that happened to arrive in the same window. The two systems were unknowingly competing for the same 5-packet burst budget.

Individually, every default is reasonable:
- banIP burst 5 is fine for ICMP flood protection
- mwan3 with 3 tracking targets is standard
- Telegraf ping monitoring is useful for latency dashboards

The combination is what kills you. Raising the rate to 250/sec makes the burst budget effectively unlimited for legitimate traffic while still protecting against real floods (nobody does legitimate ICMP at 250+ packets/second).

## Lessons

**Your firewall can sabotage your own infrastructure monitoring.** banIP's ICMP flood protection is well-intentioned — you don't want external actors flooding your WAN with ICMP. But the rate limit makes no distinction between external flood traffic and your own router's health check replies arriving in a burst.

**Persistent pings and one-shot pings behave differently under rate limiting.** If your monitoring uses `ping -c 1` in a loop (as mwan3 does), bursty reply patterns are inevitable. A rate limiter with a small burst tolerance will drop replies even when the actual packet rate is low.

**Static routes are silent killers.** The WireGuard endpoint route was created at interface-up time and never re-evaluated. When the "right" gateway changed, the route stayed. There was no alarm, no log entry, no indication that WireGuard traffic was going through a 2 Mbps 5G link instead of a 100 Mbps fiber.

**tcpdump is the ultimate arbiter.** Without packet capture, I would have blamed the fiber ISP, the WireGuard crypto overhead, or the Pi's CPU. The packets on the wire told the real story: the replies were arriving perfectly, and something in the kernel network stack (nftables, in pre-routing) was eating them.

**Check the `cnt_icmpflood` counter on your OpenWrt box.** If it's non-zero and you're running mwan3, you probably have this exact problem.

```bash
nft list counters | grep -A1 icmpflood
```

You're welcome.

## Epilogue: the 5G mystery

After fixing the route, I tested WireGuard over both links:

| Path | TCP Download | Retransmissions |
|------|-------------|-----------------|
| Raw TCP via 5G (no WG) | 273 Mbps | 2 |
| Raw UDP via 5G (no WG) | 300 Mbps | 0.18% loss |
| WireGuard via 5G | 1.7 Mbps | 26 in 5 sec |
| WireGuard via Fiber | 63 Mbps | 0 |

The 5G link does 300 Mbps raw. WireGuard turns it into 1.7 Mbps. A 175x throughput collapse. Not a port issue, not a throttling issue, not a CPU issue, not an MTU issue — I tested all of them.

I don't know why yet. Investigation is ongoing. Next post.
