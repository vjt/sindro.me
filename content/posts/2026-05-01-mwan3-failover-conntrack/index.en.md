---
title: "mwan3 Failover Without the Hung Connections"
date: 2026-05-01
draft: true
tags: [openwrt, mwan3, networking, conntrack, nftables, devlog]
description: "mwan3 reroutes new flows on uplink failure. Existing flows hang for hours. Here's why, and a small selective conntrack flush that fixes it without nuking the rest of the router."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** mwan3 reroutes *new* flows when an uplink dies. Existing
flows stay pinned to the dead path — conntrack remembers, the firewall
flow offload happily keeps shovelling packets down a dead pipe, and
long-lived TCP sockets hang until the kernel keepalive fires (default:
two hours). The native `flush_conntrack` option is a global nuke. The
fix is a fifteen-line `/etc/mwan3.user` that does a *selective*
conntrack flush by mwan3 mark on `disconnected` events only.

<!--more-->

## How I Got Here

After [migrating Jeeves to vanilla OpenWrt
25.12](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/), I
finally ran the failover tests I should have been running monthly all
along: pull the fiber, watch what happens. Pull the 5G, watch what
happens. Repeat.

The scenario was always the same. mwan3 itself did its job — pings to
`1.1.1.1` recovered in seconds, the routing tables flipped to the
surviving member, new sessions came up on the right interface — but
every long-lived TCP connection that had been established *before* the
failover just sat there, dead. They came back eventually. On a
wall-clock measured in *hours*, not seconds.

I had known about this for a while and had been working around it.
Embarrassingly long, in fact. The trigger to finally sit down and fix
it properly was that the failover testing made the lingering
connections impossible to keep ignoring.

The casualty list, on my home network: the [Technitium DNS
server](https://technitium.com/dns/) that forwards every outbound
query in the house over DNS-over-TLS to upstream resolvers (so my ISP
doesn't get to log who I'm talking to) holds long-lived TLS sockets
that hung. SSH sessions through the gateway hung. The Home Assistant
WebSocket to its mobile companion app hung. Anything with a
persistent TCP connection from before the failover sat there, mute,
while new connections worked fine.

That's not failover. That's a coin flip.

## What's Actually Happening

My default gateway, `golem`, is a [GL.iNet
GL-MT6000](https://www.gl-inet.com/products/gl-mt6000/) running
vanilla OpenWrt — a quad-core ARM box with two SFP cages and decent
NAT throughput. It runs mwan3 across two members:

| Member | mwan3 iface | Linux device  | Mark (mmx_mask `0x3F00`) |
|--------|-------------|---------------|--------------------------|
| fiber  | `wan`       | `eth1` (PPPoE) | `0x100` (id 1 << 8)      |
| 5G     | `wan5g`     | `br-lan.253` (VLAN to Jeeves) | `0x200` (id 2 << 8)      |

When fiber dies, mwan3:

1. Updates the routing tables so new connections go via 5G.
2. Walks away.

What it does *not* do: anything to the conntrack entries created while
fiber was alive. Those entries still carry `ct mark = 0x100`, the
fiber mark.

That's already a problem on its own. But on this router I make it
worse on purpose: I run with **software flow offload** enabled in fw4
(OpenWrt's nftables-based firewall). Flow offload is a kernel
fast-path: once conntrack has classified a flow as ESTABLISHED,
subsequent packets bypass the regular netfilter chains and ride a
dedicated forwarding shortcut, halving (roughly) the per-packet CPU
cost. Important for a 1 Gbit fiber line on an ARM router; very
important for not melting under heavy 5G NAT.

The shortcut is keyed on the flow's tuple plus output device. After
fiber dies, the offloaded entries for fiber-marked flows still point
at `eth1`. The router cheerfully keeps shovelling packets at a device
whose link is down. Packets drop at L2 — no ICMP, no error, no
nothing. The TCP layer in the client doesn't know.

As far as the client kernel is concerned, the socket is healthy. The
send buffer fills. Eventually `tcp_keepalive_time` fires, the kernel
notices, and the socket dies. With the default of **7200 seconds**
that's two hours. (Some applications run their own short keepalives
and recover sooner; many don't, and inherit whatever the kernel does.)

You can shorten the kernel keepalive globally, but doing so is risky
and generic — and it doesn't help the actual problem, which is that
conntrack is wrong.

## Things I Considered That Didn't Work

I came at this from four angles before landing on the right one. The
reasons each one fails are interesting in themselves.

**`ss -K` on the clients.** Kill the offending sockets from the client
side, let the application reconnect. Two problems. First, it's a
per-client fix: I'd have to deploy a hook on every device that ever
holds a long-lived socket through this gateway, and keep doing so as
the device list grows. Wrong layer. Second, even on the one client
where I'd actually started prototyping it (`nowhere`, the Pi 5 that
hosts most of the heavy long-lived sockets), the `rpt-rpi-2712`
kernel ships without `CONFIG_INET_DIAG_DESTROY`. `ss -K` returns 0
and does nothing. Silent no-op. Two strikes; never sent a packet.

**Forge a spoofed RST from the gateway.** Have `golem` inject a TCP
RST into each affected flow with the right tuple, so the client kernel
marks the socket `ECONNRESET` and the application reconnects. RFC 5961
requires the RST sequence number to be inside the receiver's window —
and conntrack does not expose the current sequence numbers (`-o
extended` and `-o xml` both omit them). Out-of-window RSTs are
silently discarded. Dead end without a packet capture per flow.

**Permanent nft `reject with tcp reset` rule on the dead mark.** Stand
a firewall rule in the forward chain that issues a TCP reset whenever
a packet still tries to leave with the dead-uplink mark. The rule is
correct in spirit, but the moment a flow is in the offload table it
no longer traverses the forward chain at all — that's literally what
offload *does*: skip the chains. The rule never sees the packet
unless the offload entry is invalidated first. Which only happens
on... a conntrack flush. Circular.

**mwan3's native `flush_conntrack` option.** Looked promising right
up until I read the source: it's implemented as `echo f >
/proc/net/nf_conntrack`, a *global* flush of every flow on the router.
Wireguard, Tailscale, LAN-to-LAN forwarding, the surviving WAN's
established connections, all of it. Every time mwan3 emits any
configured event. Massive collateral damage for a problem that needs
surgery.

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

One thing that almost shot my foot off: `config_load mwan3` is
mandatory. `mwan3_get_iface_id` reads from a runtime table that is
only populated after the mwan3 config has been walked. Skip the load,
the lookup returns empty, the mark computes to `0x000`, and `conntrack
-D -m 0/0x3F00` matches every *unmarked* flow on the router —
local-origin traffic, LAN-to-LAN, the lot. The `[ -n "$id" ] && [
"$id" != "0" ]` line is the seatbelt that refuses to fire on an empty
or zero id, so even if something else changes upstream, the script
won't go on a rampage. I tripped the bug once at the prompt while
prototyping and the guard caught it.

## What Happens Now

When fiber dies:

1. mwan3track misses pings, emits `disconnected wan`.
2. mwan3 updates the routing tables: new flows mark `0x200` (5G).
3. `/etc/mwan3.user` runs.
4. Conntrack entries with `mark & 0x3F00 == 0x100` are deleted, which
   also drops their fw4 flow offload entries. Subsequent packets for
   those flows go back to traversing the regular netfilter path.
5. The next packet on a previously-pinned socket reaches `golem`
   without a matching conntrack entry. Provided
   `nf_conntrack_tcp_loose` is on (the OpenWrt default), the kernel
   accepts the mid-stream segment as a fresh ESTABLISHED conntrack
   entry, routes it via the now-current default route (5G), and the
   masquerade rule on the 5G WAN rewrites its source IP and port to
   the 5G WAN address.
6. The remote receives a TCP segment from a tuple it has never seen
   before.

The remote's behaviour is now the dominant variable.

**Polite remote** (most CDNs, Google, Cloudflare DoT): unsolicited
segment for an unknown tuple → RST back → the client kernel marks the
socket `ECONNRESET` → the application reconnects within an RTT. This
is what 99% of the internet does.

**Silent-drop remote** (some enterprise firewalls, some BGP anycast
frontends): swallows the segment, no reply. The client retransmits
per `tcp_retries2` until the kernel gives up (~15 minutes by default)
or the application's own timeout fires first. For DoT, Technitium has
short app-level timeouts and reissues queries on a fresh socket
within seconds. The bound is set by the application, not by the
kernel. If a particular long-lived service of yours happens to live
behind a silent-drop remote and has a long app timeout, you have an
escalation path: turn flow offload off and add the nft RST rule on
the wrong-mark exit — but I have not needed to.

That's enough. Failover now actually fails over. Pings recover, *and*
sockets recover, on the same timescale.

---

The whole thing is fifteen lines of shell hooked to one hotplug event.
The mwan3 author already did the hard part — every flow is marked,
every event is fired, every primitive is sitting there waiting to be
composed. All that was missing was the surgical flush. Reliability is
not a setting. Reliability is something you build.
