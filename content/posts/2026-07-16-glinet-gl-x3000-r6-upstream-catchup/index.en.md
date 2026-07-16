---
title: "GL-X3000 r6: Catching Up With Upstream Without Breaking the Modem"
date: 2026-07-16
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "Rebasing my GL-X3000 image onto 155 commits of newer OpenWrt 25.12, the one build trap that bit me, and how I flashed a live 5G uplink and proved the radio didn't regress."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** I rebuilt Jeeves — [my GL-iNet GL-X3000 5G backup
uplink](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/) — on the
latest OpenWrt 25.12, jumping the kernel from 6.12.85 to 6.12.94. My 20
device-enablement commits rebased cleanly onto 155 commits of upstream. One
build trap cost me a rebuild. Then I flashed the running modem router and
checked the telemetry to confirm the 5G leg came back exactly as it was.
The image is `jeeves-r6` on the
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases).

<!--more-->

## Why rebuild at all

The [April migration](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
got Jeeves onto vanilla OpenWrt 25.12 with the Quectel RM520N-GL modem fully
working. Since then, upstream moved: 155 commits, a nine-point kernel bump
(6.12.85 → 6.12.94), and the usual churn of security fixes and package
updates. None of it changes what Jeeves *does* — this is pure hygiene. But
hygiene on a device with two out-of-tree kernel patches is never quite free.

My stack is 20 commits on top of upstream. Two of them are kernel patches
and they are the ones I watch on every rebase:

- one that teaches the generic MHI PCI driver to claim the RM520N-GL by its
  Qualcomm subvendor ID, so the modem binds at all;
- one that disables PCIe runtime power management on this board. Without it,
  the port suspends the modem into D3hot and the MHI link dies in a
  completion-timeout / AER cascade that only a full reboot recovers from.

Lose the second one and the modem crashes the way it did before I found the
fix. So the rebase rule is simple: those two must survive, intact, or the
build doesn't ship. They rebased without conflict this time — but I've now
[opened an issue to upstream both](https://github.com/vjt/openwrt-glinet-x3000/issues/6),
because the correct long-term fix is to not carry them at all.

## The one build trap: a stale configure cache

First build failed. Not in my code — in `vim`, of all things.

Upstream had changed the target compiler flags (they added
`-Wl,-z,max-page-size=4096` to the global `CFLAGS`/`LDFLAGS`). Most OpenWrt
packages re-run `configure` from scratch on every build, so they never
notice. But `vim` keeps its autotools `config.cache` around between builds,
and when the flags changed underneath it, `configure` refused to continue:

```
configure: error: changes in the environment can compromise the build
configure: error: run 'make distclean' and/or 'rm auto/config.cache'
```

My build container had a `build_dir` left over from the r5 era, so the stale
cache was sitting right there. The fix is a `make clean` to wipe the target
`build_dir` and force every package to reconfigure against the new flags —
the toolchain is preserved, so it costs time but not a from-scratch rebuild.
If you rebase across a flag change and hit a lone package failing at
`configure` with that message, this is why. Don't go hunting your own
patches; clean the tree.

## Flashing a live uplink without losing it

Jeeves is a *backup* gateway, not the main one, and I was on-site — which is
the only reason I flashed it remotely at all. A firmware write reboots the
device, and if the modem hadn't come back I'd have needed physical recovery.
The sequence I used, in order:

1. Pull a full config backup **off** the device first, so a reflash-to-r5
   can restore state.
2. `sysupgrade --test` the image on the device to confirm the metadata and
   board compatibility before touching flash.
3. Flash over a **synchronous** SSH command — not a backgrounded/detached
   one. `sysupgrade` hands the actual write to a second stage over ubus, and
   if you detach the session that call silently no-ops and nothing gets
   written. Let the connection block; it drops on reboot, and that's normal.
4. Keep config on upgrade (same config lineage), then wait and watch.

It came back in about seventy seconds.

## Did the radio survive?

This is the part that actually matters. A kernel bump touches every modem
driver — MHI, the MBIM control path, USB — and the only honest way to know
it didn't regress the radio is to look at the numbers, not the boot log.

The modem re-enumerated over PCIe/MHI cleanly, and `dmesg` showed the PCIe
link coming up with **no AER cascade** — the runtime-PM patch earning its
keep across the kernel jump. ModemManager had the modem `connected` on
LTE+5G-NSA within about ten seconds of starting.

Then I compared telemetry from before and after the flash. My watchdog and
signal collectors push to VictoriaMetrics, so I have per-carrier RSRP and
SINR and a ground-truth "is NR attached" gauge. The 5G leg — the n78 NSA
carrier that is the whole point of this box — was **statistically identical**
across the flash: RSRP around −95 dBm, SINR around 11.8 dB, NR attached 100%
of the time both before and after.

One thing nearly fooled me. The post-flash window briefly showed *more* LTE
carrier aggregation than the pre-flash window, which looks like an
improvement. It isn't — I checked a week of history and the pre-flash sample
just happened to land in a single-carrier lull, while the device normally
aggregates one to three LTE carriers depending on what the network feels
like giving me. Carrier-aggregation depth is network-driven, not firmware.
The honest verdict is *no change*, which for a pure upstream catch-up is
exactly the result you want.

To keep myself honest, I've scheduled a follow-up that re-runs the same
comparison over a full matched 24-hour window once r6 has a day of data
behind it — a 35-minute spot check right after a reboot is not a radio
verdict.

## What rode along

Because my custom package feeds track their main branches, a few of my own
tools advanced with the rebuild — most notably
[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools) went from 1.4.0
to 1.6.0, pulling in the Grafana dashboard generator and the stats work I did
this cycle. That's a deliberate choice: I want my own code current on every
build, even when upstream itself hasn't moved.

`jeeves-r6` is on the
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases) if you
run the same box. As always: it's a backup uplink, flash accordingly, and
keep the r5 image around for recovery.
