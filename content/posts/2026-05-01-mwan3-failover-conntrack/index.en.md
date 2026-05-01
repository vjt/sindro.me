---
title: "mwan3 Failover Without the Hung Connections"
date: 2026-05-01
draft: true
tags: [openwrt, mwan3, networking, conntrack, nftables, devlog]
description: "mwan3 reroutes new flows on uplink failure. Existing flows linger for minutes. Here's why, and a small selective conntrack flush that fixes it without nuking the rest of the router."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** [mwan3](https://openwrt.org/docs/guide-user/network/wan/multiwan/mwan3)
reroutes *new* flows when an uplink dies. Existing flows stay pinned to
the dead path — conntrack remembers, the firewall flow offload keeps
shovelling packets along it, and long-lived TCP sockets linger until
their application notices and reconnects. The native `flush_conntrack`
option is a global nuke. The fix is a fifteen-line `/etc/mwan3.user`
that does a *selective* conntrack flush by mwan3 mark on `disconnected`
events only.

<!--more-->

## How I Got Here

After [migrating
Jeeves](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/) — my
GL.iNet GL-X3000, the 5G router that handles the
[backup uplink so I don't lose another
meeting](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) — to
vanilla OpenWrt 25.12, I went back to running my failover drills on
the gateway: pull the fiber, watch what happens. Pull the 5G, watch
what happens. Repeat.

The scenario was always the same one I'd been observing for months.
mwan3 itself did its job — pings to `1.1.1.1` recovered in seconds,
the routing tables flipped to the surviving member, new sessions came
up on the right interface — but every long-lived TCP connection that
had been established *before* the failover just sat there, dead. They
came back eventually. On a wall-clock measured in *minutes*, usually
governed by the application layer's own timeouts.

I'd known about this for a while and had been working around it.
Embarrassingly long, in fact — I'd just never carved out the time to
actually dig in and figure out where the slowness was coming from. The
new round of drills made the lingering connections impossible to keep
filing under "later".

The casualty list, on my home network: the [Technitium DNS
server](https://technitium.com/dns/) that forwards every outbound
query in the house over DNS-over-TLS to upstream resolvers (so my ISP
doesn't get to see the names I'm asking for — UDP/53 in cleartext is
not a hill I'm dying on) holds long-lived TLS sockets that hung. The
Home Assistant WebSocket to its mobile companion app hung. Anything
with a persistent TCP connection from before the failover sat there,
mute, while new connections worked fine.

That's not failover. That's a coin flip.

## What's Actually Happening

My default gateway, `golem`, is a [GL.iNet
GL-MT6000](https://www.gl-inet.com/products/gl-mt6000/) running
vanilla OpenWrt — a quad-core ARM box with a generous spread of
2.5GbE ports. It runs
[mwan3](https://openwrt.org/docs/guide-user/network/wan/multiwan/mwan3)
across two members:

| Member | mwan3 iface | Linux device   | Reaches                                    | Mark (mmx_mask `0x3F00`) |
|--------|-------------|----------------|--------------------------------------------|--------------------------|
| fiber  | `wan`       | `eth1`         | the ISP's fiber router on the LAN side     | `0x100` (id 1 << 8)      |
| 5G     | `wan5g`     | `br-lan.253`   | Jeeves and its 5G uplink, on a 802.1Q VLAN | `0x200` (id 2 << 8)      |

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
dedicated forwarding shortcut. Important on an ARM router pushing a
gigabit fiber line.

The shortcut is keyed on the flow's tuple plus output device. After
fiber dies, the offloaded entries for fiber-marked flows still point
at `eth1`. From `golem`'s point of view, eth1's link to the ISP
modem is perfectly healthy — mwan3 detected the failure via *upstream*
ping timeouts, not via a local link-down event. So the router keeps
emitting packets onto the dead path. Where they actually die depends
on what failed (the modem's PPPoE session, the optical fiber upstream,
the ISP's gateway — pick one). The modem will probably emit ICMP
Destination Unreachable for the first few packets it can't forward,
and golem will dutifully un-SNAT and forward those errors back to the
LAN client — but TCP, [per RFC
5461](https://datatracker.ietf.org/doc/html/rfc5461), treats ICMP
unreachables on an established connection as soft errors and
ignores them while retransmitting, rather than tearing the socket
down on the first one. The client kernel keeps the socket open. The
application waits.

Eventually whatever app-level timeout the application carries for
that connection fires (DoT clients have short ones, WebSockets
pong-timeout in tens of seconds, SSH depends on whatever
`ServerAliveInterval` you set, if any), it closes the dead socket,
opens a new one, and recovers — over the alive uplink, this time.

The kernel's own `tcp_keepalive_time` is set to 7200 seconds by
default, so without any app-level timeout at all you'd be looking at
the two-hour fallback. In practice nothing on my network is patient
enough to wait for that, and the actual recovery measures in
single-digit to low-double-digit minutes. Still way too long for
something that's supposed to be transparent.

## Things I Considered That Didn't Work

{{< figure src="rejected.jpg" alt="Engraved-plate illustration in amber and teal on cream blueprint grid: four discarded surgical instruments laid on a wooden workbench. Left to right: a pair of fine scissors with a fractured tip, an antique syringe with a curling scroll of cipher pinned to it, a small fence section with a hidden tunnel beneath it carrying a glowing data packet, and a brass bell jar containing a tangle of severed network conduits. Each instrument is tagged with a circular brass marker; faint dotted measurement lines and arrows annotate the bench" caption="Four instruments tried and rejected: per-client surgery, the spoofed RST that can't read a window, the rule the offload tunnels under, and the global-flush bell jar." >}}

I came at this from four angles before landing on the right one. The
reasons each one fails are interesting in themselves.

**`ss -K` on the clients.** Kill the offending sockets from the client
side, let the application reconnect. Wrong layer: I'd have to deploy
a hook on every device that ever holds a long-lived socket through
this gateway, and keep doing so as the device list grows. It's a
per-client fix to a router-level problem.

**Forge a spoofed RST from the gateway.** Have `golem` inject a TCP
RST into each affected flow with the right tuple, so the client kernel
marks the socket `ECONNRESET` and the application reconnects. RFC 5961
requires the RST sequence number to be inside the receiver's window —
and conntrack does not expose the current sequence numbers (`-o
extended` and `-o xml` both omit them). Out-of-window RSTs are
silently discarded. Dead end without a packet capture per flow.

**A permanent nft `reject with tcp reset` rule on a wrong-mark exit.**
Stand a firewall rule in the forward chain that fires whenever a
packet still tries to leave with one uplink's mark *but* the device it
is exiting is the other uplink's. The rule is permanent in the
ruleset; it only matches when conntrack's idea of where the flow
should go has diverged from the routing table's, which is exactly
the post-failover symptom. Correct in spirit, but the moment a flow
is in the offload table it no longer traverses the forward chain at
all — that's literally what offload *does*: skip the chains. The rule
never sees the packet unless the offload entry is invalidated first.
Which only happens on... a conntrack flush. Circular.

**mwan3's native `flush_conntrack` option.** Looked promising right
up until I read the [source](https://github.com/openwrt/packages/blob/master/net/mwan3/files/lib/mwan3/mwan3.sh#L1207):
it's `echo f > /proc/net/nf_conntrack`, a *global* flush of every flow
on the router. Wireguard, Tailscale, LAN-to-LAN forwarding, the
surviving WAN's established connections, all of it. Every time mwan3
emits any configured event. Massive collateral damage for a problem
that needs surgery.

## The Fix

{{< figure src="the-fix.jpg" alt="Engraved-plate illustration in amber and teal on cream blueprint grid: a long horizontal row of small luminous packet-envelopes on a workbench. Most glow warm amber and are intact; a contiguous run in the middle glows cool teal and is being delicately lifted away one by one by a precise floating scalpel of light, leaving the bare grid exposed beneath them. Inset top-left: a hand pressing a carved wooden stamp inscribed with a small abstract glyph. Faint dotted measurement lines and tiny annotation arrows around the gap" caption="Surgery, not amputation: only the dead-marked entries leave the bench." >}}

What was needed: flush *only* the conntrack entries marked with the
dead uplink's mwan3 mark, *only* on `disconnected` events. Conntrack
already supports this — `conntrack -D -m <mark>/<mask>` deletes by
mark. mwan3 already labels every flow with its member's mark. The two
just needed to meet.

`/etc/mwan3.user` runs on every mwan3 hotplug event:

```sh
. /lib/functions.sh
. /lib/mwan3/mwan3.sh
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

> *One thing that almost shot my foot off:* `config_load mwan3` is
> mandatory. `mwan3_get_iface_id` reads from a runtime table that is
> only populated after the mwan3 config has been walked. Skip the
> load, the lookup returns empty, the mark computes to `0x000`, and
> `conntrack -D -m 0/0x3F00` matches every *unmarked* flow on the
> router — local-origin traffic, LAN-to-LAN, the lot. The `[ -n "$id"
> ] && [ "$id" != "0" ]` line is the seatbelt that refuses to fire on
> an empty or zero id.

## What Happens Now

{{< figure src="recovery.jpg" alt="Engraved-plate illustration in amber and teal on cream blueprint grid: a horizontal flow diagram. On the left, a small antique computer terminal with brass cogs visible emits a glowing amber data packet. The packet meets a teal pipe drawn faintly and crossed out (the dead path), then re-routes through a parallel amber pipe. The pipe terminates in a brass lens or transformer that visibly rewrites the packet's identification mark. The packet then arrives at a fortified cloud-castle on the right. A thin teal arrow flows back along the bottom of the frame to the terminal, where a small bright bloom of light depicts a fresh new connection. Faint dotted measurement lines and circular brass tags annotate the path" caption="The recovery loop: dead path crossed out, alive path takes over, masquerade rewrites the source, the remote answers, the client reconnects." >}}

When fiber dies:

1. mwan3track misses pings, emits `disconnected wan`.
2. mwan3 updates the routing tables: new flows mark `0x200` (5G).
3. `/etc/mwan3.user` runs.
4. Conntrack entries with `mark & 0x3F00 == 0x100` are deleted, which
   also drops their fw4 flow offload entries. Subsequent packets for
   those flows go back to traversing the regular netfilter path.
5. The next packet on a previously-pinned socket reaches `golem`
   without a matching conntrack entry. Provided
   [`nf_conntrack_tcp_loose`](https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.rst)
   is on (the OpenWrt default — verified `= 1` on golem, kernel
   6.6.119), the kernel accepts the mid-stream segment as a fresh
   ESTABLISHED conntrack entry, routes it via the now-current default
   route (5G), and the masquerade rule on the 5G WAN rewrites its
   source IP and port to the 5G WAN address.
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
behind a silent-drop remote *and* has a long app timeout, the
escalation is to turn flow offload off and add the nft RST rule on
the wrong-mark exit — but I have not needed to.

That's enough. Failover now actually fails over. Pings recover, *and*
sockets recover, on the same timescale.

---

The whole thing is fifteen lines of shell hooked to one hotplug event.
The mwan3 author already did the hard part — every flow is marked,
every event is fired, every primitive is sitting there waiting to be
composed. All that was missing was the surgical flush. Reliability is
not a setting. Reliability is something you build.

Both `/etc/mwan3.user` and the `mwan-ct` operator helper (list, count,
top-talkers, inspect-offload, manual flush by uplink) live in
[**vjt/mwan3-selective-flush**](https://github.com/vjt/mwan3-selective-flush)
on GitHub. Drop them in, smoke-test with the recipe in the README,
done.
