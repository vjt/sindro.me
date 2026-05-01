---
title: "mwan3 Failover Without the Hung Connections"
date: 2026-05-01
tags: [openwrt, mwan3, networking, conntrack, nftables, devlog]
description: "mwan3 reroutes new flows on uplink failure. Existing flows hang for up to two hours. Here's why, and a small selective conntrack flush that fixes it without nuking the rest of the router."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** mwan3 reroutes *new* flows when an uplink dies. Existing
flows stay pinned to the dead mark — conntrack remembers, fw4 flow
offload happily keeps shovelling packets down a dead pipe, and
long-lived TCP sockets hang until `tcp_keepalive_time` fires (default:
two hours). The native `flush_conntrack` option is a global nuke. The
fix is a fifteen-line `/etc/mwan3.user` that does a *selective*
conntrack flush by mwan3 mark on `disconnected` events only.

<!--more-->

## How I Got Here

After [migrating Jeeves to vanilla OpenWrt
25.12](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/) I
decided to do something I'd been putting off for embarrassingly long:
actually *test* failover end-to-end on the gateway. Pull the fiber,
watch what happens. Pull the 5G, watch what happens. Repeat.

mwan3 did its job: pings to `1.1.1.1` recovered in a handful of
seconds, the routing tables flipped over to the surviving member, new
sessions came up on the right interface. Looked great.

What didn't look great: my Technitium DoT sockets to upstream
resolvers were hung. SSH sessions through the gateway were hung. The
HA WebSocket was hung. Anything with a long-lived TCP connection
established *before* the failover was sitting there, dead, while new
connections worked fine. They eventually came back, but on a wall-clock
timer measured in minutes-to-hours, not in seconds.

That's not failover. That's a coin flip.

## What's Actually Happening

`golem` runs mwan3 with two members:

| Member | Iface     | Device         | Mark (mmx_mask `0x3F00`) |
|--------|-----------|----------------|--------------------------|
| fiber  | `wan`     | `eth1`         | `0x100` (id 1 << 8)      |
| 5G     | `wan5g`   | `br-lan.253`   | `0x200` (id 2 << 8)      |

When fiber dies, mwan3:

1. Updates the routing tables so new connections go via 5G.
2. Walks away.

What it does *not* do: anything to the conntrack entries created while
fiber was alive. Those entries still carry `ct mark = 0x100`. The fw4
flow offload table — `hook ingress priority filter`, devices include
`eth1` — is still happily offloading those flows down `eth1`. Packets
hit the dead device and drop at L2.

The TCP layer in the client doesn't know. As far as the kernel is
concerned, the socket is healthy. There is no RST, no ICMP unreachable,
no signal. The send buffer fills. Eventually `tcp_keepalive_time`
fires, the kernel notices, and the socket dies. With the default of
**7200 seconds** that's two hours.

You can shorten the keepalive globally, but doing so is risky and
generic — and it doesn't help the actual problem, which is that
conntrack is wrong.

## Things I Tried That Didn't Work

I came at this from four angles before landing on the right one. None
of these worked, and the reasons are interesting.

**`ss -K` on the client.** The plan: kill the offending sockets from
the client side and let the application reconnect. Sounds clean. It
doesn't work on `nowhere`, the Pi 5 that hosts most of those sockets,
because the `rpt-rpi-2712` kernel ships without
`CONFIG_INET_DIAG_DESTROY`. `ss -K` returns 0 and does nothing. Silent
no-op. I now have a memory note on this for future me.

**Forge a spoofed RST from the gateway.** The plan: have `golem`
inject a TCP RST into the existing flow with the right tuple, so the
client kernel marks the socket `ECONNRESET` and the app reconnects.
Won't work because RFC 5961 requires the RST sequence number to be
within the receive window — and conntrack does not expose the current
sequence numbers. `conntrack -L -o extended` and `-o xml` both omit
them. Out-of-window RSTs are silently discarded.

**Permanent nft `reject with tcp reset` rule on the dead mark.** The
plan: stand a forwarding rule that issues a TCP reset for any packet
still trying to leave via the dead-uplink mark. Bypassed by fw4 flow
offload. Offloaded packets skip the `forward` chain entirely — that's
literally what offload *does*. The rule never fires until the offload
entry is invalidated. Which only happens on... a conntrack flush.

**mwan3's native `flush_conntrack` option.** This one looked promising
right up until I read the source. It's implemented as `echo f >
/proc/net/nf_conntrack`: a *global* flush. Every flow on the router.
Wireguard, Tailscale, LAN-to-LAN forwarding, the surviving WAN's
established connections, all of it. Every time mwan3 emits any tracked
event. Massive collateral damage for a problem that needs surgery.

## The Fix

What was needed: flush *only* the conntrack entries marked with the
dead uplink's mwan3 mark, *only* on `disconnected` events. Conntrack
already supports this — `conntrack -D -m <mark>/<mask>` deletes by
mark. mwan3 already labels every flow with its member's mark. The two
just needed to meet.

`/etc/mwan3.user` runs on every mwan3 hotplug event:

```sh
. /usr/share/libubox/jshn.sh
. /lib/functions.sh
. /usr/share/mwan3/common.sh

config_load mwan3

flush_dead_uplink() {
    local id mark
    mwan3_get_iface_id id "$1"
    [ -n "$id" ] && [ "$id" != "0" ] || return 0
    mark=$((id << 8))
    conntrack -D -m "${mark}/0x3F00" 2>/dev/null
    logger -t mwan3-flush "selective conntrack flush iface=$1 mark=$(printf 0x%x $mark)"
}

case "$ACTION" in
    disconnected) flush_dead_uplink "$INTERFACE" ;;
esac
```

Two non-obvious parts.

`config_load mwan3` is mandatory. `mwan3_get_iface_id` reads from
`mwan3_iface_tbl`, which is populated by walking the mwan3 config.
Without the load, the lookup returns empty, the mark is `0x000`, and
`conntrack -D -m 0/0x3F00` matches every unmarked flow on the router
— local traffic, the lot. I caught it manually before the script
shipped. The empty-id guard is the seatbelt.

The `local` declarations live inside a function because
`/etc/hotplug.d/iface/16-mwan3-user` invokes the script through
`env -i ACTION=… INTERFACE=… DEVICE=… /etc/mwan3.user` under bare ash
— which doesn't allow `local` at top level.

## What Happens Now

When fiber dies:

1. mwan3track misses pings, emits `disconnected wan`.
2. mwan3 updates routing: new flows mark `0x200` (5G).
3. `/etc/mwan3.user` runs.
4. Conntrack entries with `mark & 0x3F00 == 0x100` are deleted, which
   also drops their fw4 flowtable offload entries.
5. The next packet on a previously-pinned socket hits `golem` with no
   conntrack match → kernel forwards via the current default route
   (5G), creates a fresh conntrack entry with `mark=0x200`, SNAT swaps
   the source IP from the fiber WAN address to the 5G one.
6. The remote sees a TCP segment from a new tuple.

The remote's behaviour is now the dominant variable.

**Polite remote** (most CDNs, Google, Cloudflare DoT): unsolicited
segment → RST back → client kernel marks the socket `ECONNRESET` →
application reconnects within an RTT. This is what 99% of the internet
does.

**Silent-drop remote** (some enterprise firewalls, some BGP anycast
frontends): swallows the segment, no reply. Client retransmits per
`tcp_retries2` until the kernel gives up (~15 minutes by default) or
the application's own timeout fires. For DoT specifically, Technitium
has short app-level timeouts and reissues queries on a fresh socket
within seconds. The bound is set by the application, not by the
kernel.

That's enough. Failover now actually fails over. Pings recover, *and*
sockets recover, on the same timescale.

## If Silent-Drop Becomes A Problem

It hasn't, for me. If it ever does, the escalation path is:

1. Turn off TCP flow offload on the gateway. Then forwarding
   *actually* traverses `forward`, and a permanent nft `reject with
   tcp reset` rule on packets exiting the wrong device for their mark
   fires on the first segment of any zombie flow. CPU cost per
   packet goes up; profile before/after.
2. App-level "force reload" in the few hold-outs. Out of scope.

## Verifying It

`golem` ships logs to `nowhere`'s rsyslog → Telegraf → VictoriaLogs.
Live tail:

```sh
ssh root@golem 'logread -f | grep mwan3-flush'
```

Or query VictoriaLogs directly:

```sh
curl -sk 'https://victoria.bad.ass/select/logsql/query' \
  --data-urlencode 'query=_stream:{tags.hostname="golem"} mwan3-flush' \
  --data-urlencode 'start=-1d' | jq .
```

Manual fire (will flush real conntrack — only do this on a router you
can afford to have hiccup briefly):

```sh
ACTION=disconnected INTERFACE=wan /etc/mwan3.user
```

Expect a single log line. Expect `conntrack -L | grep -c 'mark=256'`
to go to roughly zero — `256` decimal is `0x100` hex, the fiber mark.

---

The whole thing is fifteen lines of shell pinned to one hotplug event.
The mwan3 author already did the hard part — every flow is marked,
every event is fired, every primitive is sitting there waiting to be
composed. All that was missing was the surgical flush. Reliability is
not a setting. Reliability is something you build.
