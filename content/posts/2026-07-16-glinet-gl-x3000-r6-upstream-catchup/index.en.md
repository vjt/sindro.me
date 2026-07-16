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
device-enablement commits rebased cleanly onto 155 upstream commits. One
build trap cost me a rebuild. Then I flashed the running router and checked
the telemetry to confirm the 5G leg came back unchanged. The image is
`jeeves-r6` on the
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases).

<!--more-->

## Why rebuild

The [April migration](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
put Jeeves on vanilla OpenWrt 25.12 with the Quectel RM520N-GL modem fully
working. Since then upstream moved 155 commits and bumped the kernel from
6.12.85 to 6.12.94. None of it changes what Jeeves does — it's hygiene. But
hygiene isn't free when your stack carries two out-of-tree kernel patches.

Mine has 20 commits on top of upstream, and two are the ones I watch on every
rebase:

- one teaches the generic MHI PCI driver to claim the RM520N-GL by its
  Qualcomm subvendor ID, so the modem binds at all;
- one disables PCIe runtime power management on this board. Without it the
  port suspends the modem into D3hot and the MHI link dies in a
  completion-timeout / AER cascade that only a reboot clears.

Lose the second and the modem crashes the way it did before I found the fix.
They rebased without conflict this time — and I've
[opened an issue to upstream both](https://github.com/vjt/openwrt-glinet-x3000/issues/6),
because the right long-term fix is to not carry them at all.

## The one build trap: a stale configure cache

The first build failed — in `vim`, not in my code. Upstream had added
`-Wl,-z,max-page-size=4096` to the target `CFLAGS`/`LDFLAGS`. Most OpenWrt
packages re-run `configure` every build and never notice, but `vim` keeps its
autotools `config.cache` around, and with the flags changed underneath it,
`configure` bailed:

```
configure: error: changes in the environment can compromise the build
configure: error: run 'make distclean' and/or 'rm auto/config.cache'
```

My build container still had a `build_dir` from the r5 era, so the stale cache
was sitting right there. A `make clean` wipes the target `build_dir` and forces
every package to reconfigure against the new flags — the toolchain is
preserved, so it costs time but not a from-scratch rebuild. If a lone package
fails at `configure` with that message after a rebase, don't hunt your patches;
clean the tree.

## Flashing without losing the box

A firmware write reboots the device, and if the modem doesn't come back you
need physical recovery. The sequence I used:

1. Pull a full config backup **off** the device first, so a reflash to the
   previous image can restore state.
2. `sysupgrade --test` the image on the device to check metadata and board
   match before touching flash.
3. Flash over a **synchronous** SSH command, not a detached one. `sysupgrade`
   hands the write to a second stage over ubus; detach the session and that
   call silently no-ops. Let the connection block — it drops on reboot, which
   is normal.
4. Keep config on upgrade, then wait and watch.

It came back in about seventy seconds.

## Did the radio survive?

A kernel bump touches every modem driver — MHI, MBIM, USB — so the only real
check is the numbers, not the boot log. The modem re-enumerated over PCIe/MHI
cleanly and `dmesg` showed the link come up with no AER cascade — the
runtime-PM patch earning its keep across the jump. ModemManager had it
`connected` on LTE+5G-NSA within about ten seconds.

Then I compared telemetry from before and after. The n78 NSA carrier — the
whole point of this box — was statistically identical: RSRP around −95 dBm,
SINR around 11.8 dB, NR attached 100% of the time on both sides.

One thing nearly fooled me: the post-flash window showed *more* LTE carrier
aggregation, which looks like a win. It isn't — a week of history showed the
pre-flash sample had just landed in a single-carrier lull, while the box
normally aggregates one to three LTE carriers depending on the network. CA
depth is network-driven, not firmware. The honest verdict is no change —
exactly what a pure upstream catch-up should produce. I've scheduled a
follow-up over a full 24-hour window to confirm; 35 minutes after a reboot
isn't a radio verdict.

## What rode along

Because my custom feeds track their main branches, a few of my own tools
advanced with the build — notably
[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools) went 1.4.0 →
1.6.0, pulling in the Grafana dashboard generator and this cycle's stats work.
Deliberate: I want my own code current on every build, even when upstream
hasn't moved.

`jeeves-r6` is on the
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases). Keep the
previous image around for rollback — and think about your own setup before you
flash. I could take the remote-flash risk because Jeeves is my *backup* path
and I was on-site; if that box is the only thing standing between you and the
internet, treat it accordingly.
