---
title: "GL-X3000 on Vanilla OpenWrt 25.12: Every Pitfall, Documented"
date: 2026-04-28
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "A full migration diary: stock GL.iNet firmware off, vanilla OpenWrt 25.12 on, seven pitfalls documented so you don't have to rediscover them."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** I migrated my GL-iNet GL-X3000 (Spitz AX) — Jeeves, my 5G backup
uplink — from stock GL.iNet firmware (OpenWrt 21.02, kernel 5.4) to vanilla
OpenWrt 25.12 (kernel 6.12.79). The modem — a Quectel RM520N-GL on PCIe/MHI
— works perfectly. There are at least seven distinct ways to get things
wrong before you get there. I found most of them. This is the map.

<!--more-->

## Why Bother

Jeeves is my 5G backup uplink. When fiber goes down — [and fiber goes down,
always at the worst possible
moment](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) — Jeeves is
what stands between me and a missed meeting. The hardware is excellent:
MediaTek MT7981B (Filogic 820), Wi-Fi 6, USB 3.0, and a Quectel RM520N-GL
5G modem on an M.2 slot wired to both PCIe and USB.

The stock firmware is GL.iNet's flavour of OpenWrt 21.02, shipping on
kernel 5.4. That kernel reached end of life in December 2022. But the
kernel age is not the main reason I switched.

The main reason is **control**. I do heavy customization on this network:
band locking, cell locking, automatic reconnect logic when 5G drops or
signal degrades. The stock GL.iNet firmware gets in the way on all three
fronts.

The most frustrating issue: when 5G drops and only LTE Band 3 stays up,
GL.iNet's automation keeps Jeeves on 4G-only — and stays there.
Indefinitely. My local LTE averages around 5 Mbit/s. If I don't notice and
manually intervene, I sit on a 5 Mbit/s backup for hours before the radio
goes back to 5G. That is not acceptable for a link that is supposed to
cover for fiber outages.

The second issue: GL.iNet ships its own band and cell locking logic, and
it conflicts with mine. My carrier deploys 5G-NSA (non-standalone), and
GL.iNet's stock automation does not handle the NSA attach sequence
correctly for my provider. Every time I tried to hold a specific cell, I
ended up fighting the firmware.

Vanilla OpenWrt 25.12 offers mainline MHI support for the modem's PCIe
data path, ModemManager integration, a proper apk-based package manager,
and the entire current package ecosystem. GL.iNet's firmware is a fork
with proprietary drivers and its own update cycle. Vanilla is the real
thing — and it lets me own every bit of the connectivity stack.

The migration took longer than it should have. Here is everything I
learned.

## The Lay of the Land

Before diving into pitfalls, a quick orientation on how this hardware works.
The RM520N-GL talks to the host over **both** PCIe and USB simultaneously.
Stock GL.iNet firmware used a proprietary `pcie_mhi` driver exposing
`/dev/mhi_*` devices. Vanilla OpenWrt uses the mainline `mhi_pci_generic`
driver, which exposes `/dev/wwan0mbim0` (MBIM data path), `/dev/wwan0at0`
(AT command port), and friends — no QMI over MHI, MBIM only.

The USB side exposes four serial ports (`/dev/ttyUSB0`–`3`) for AT/NMEA/DIAG
commands, and — after a composition switch — an ADB interface. More on that
later.

## Pitfall 1: Use the Sysupgrade Bin, Not the Factory Bin

This one is in the OpenWrt wiki but easy to miss. The stock GL.iNet U-Boot
web recovery validates image headers. It rejects the OpenWrt factory bin with:

> *"Something went wrong during update. Probably you have chosen wrong file."*

The sysupgrade bin goes through fine. So does everything after that: the
sysupgrade bin is also what you flash for in-place upgrades once you're on
vanilla OpenWrt. The factory bin is only useful once you've replaced the stock
bootloader with OpenWrt U-Boot — which is optional and which I haven't done.

The flashing procedure itself is straightforward: hold Reset while powering on,
set your PC to a static IP in the `192.168.1.0/24` range, open `192.168.1.1`
in a browser, and feed it the sysupgrade bin. Takes about 90 seconds.

Back up the stock bootloader first:

```sh
ssh root@192.168.253.254
dd if=/dev/mmcblk0boot0 of=/tmp/stock_preloader.bin
dd if=/dev/mmcblk0p4 of=/tmp/stock_uboot_fip.bin
scp root@192.168.253.254:/tmp/stock_*.bin .
```

You probably won't need them. Do it anyway.

## Pitfall 2: The Modem Needs a Kernel Patch

The RM520N-GL sold with the GL-X3000 is the GLAP variant — slightly different
sub-device PCI ID (`17cb:0308`, sub-vendor `17cb`, sub-device **`5201`**).
The mainline `mhi_pci_generic` driver doesn't recognise `5201` out of the
box. The modem doesn't enumerate. You're looking at an empty `mmcli -L` and a
kernel log with nothing mentioning `wwan`.

The fix is a [one-liner kernel
patch](https://github.com/vjt/openwrt-glinet-x3000/blob/openwrt-25.12/target/linux/generic/pending-6.12/gl-x3000-quectel-pci-id.patch)
that adds the sub-device ID to the driver's PCI match table. Without it, you
have a 5G router with no 5G. I ship it as
`target/linux/generic/pending-6.12/gl-x3000-quectel-pci-id.patch` in the
build tree.

The same fix [was submitted to
linux-arm-msm](https://lore.kernel.org/mhi/20250729-add-rm520n-glap-support-v1-1-736ee6bbb385@fritscher.net/T/#u)
in July 2025 by Michael Fritscher, who hit the same problem. It hasn't landed
in mainline yet — the maintainer raised a question about Quectel reusing
Qualcomm's own PCI vendor IDs, and the patch has been parked pending
clarification from Quectel. Until it merges, the out-of-tree patch is the
only path.

## Pitfall 3: PCIe Runtime Power Management Will Crash Your Modem

This one cost me the most time. Symptoms: the modem comes up fine,
ModemManager connects, traffic flows — and then, **two minutes later,
reproducibly every time**, the modem disappears with a cascade of kernel
errors:

```
pci 0000:01:00.0: AER: Correctable error message received
pci 0000:01:00.0: PCIe Bus Error: severity=Correctable, type=Physical Layer
pci 0000:01:00.0: MHI: channel not open
pci 0000:01:00.0: PCIe: ERROR CmpltTO
```

What's happening: the kernel's PCIe port power management is putting the PCIe
port into D3hot (link power-down). When traffic arrives, the port wakes up,
but the MHI bus never fully recovers from the link-down event. The PCIe AER
layer starts logging Completion Timeouts. The modem goes silent.

The [fix is
blunt](https://github.com/vjt/openwrt-glinet-x3000/commit/4087faad55849b7891008482fe0d8beae81714b8)
and permanent:

```
pcie_port_pm=off
```

in the kernel command line. This disables PCIe port power management globally.
On the GL-X3000 that means the modem link stays at full power. No more
crashes.

Note for the cautious: if the modem *does* wedge in this state, runtime
mitigations don't help. The only recovery is a host reboot. You cannot
`rmmod` and `modprobe` your way out of a CmpltTO storm.

## Pitfall 4: Don't Casually Reboot the Modem

Related to the above: `AT+CFUN=1,1` reboots the modem. On this hardware,
modem reboot while the PCIe link is active can wedge the PCIe host port
into the same error state. The modem goes through its power cycle, the PCIe
link bounces, MHI loses sync, and you're back to the CmpltTO cascade without
the PM trigger.

This means: if you need to reboot the modem, stop ModemManager first, issue
`AT+CFUN=0` to clean radio-off the modem, *then* bounce it. Or just reboot
the router — it's faster and less exciting.

## Pitfall 5: ModemManager Will Steal Your AT Ports

The vanilla OpenWrt `modemmanager` package includes a udev/hotplug rule
(`/etc/hotplug.d/tty/25-modemmanager-tty`) that hands every USB serial port
that looks like a modem to ModemManager. The RM520N-GL's `/dev/ttyUSB0`–`3`
all match. ModemManager opens them and keeps them exclusively — which means
my own AT command tooling (more on that below) can't talk to the modem
while MM is running.

The modem data path goes over PCIe/MHI, so MM doesn't *need* the ttyUSB
ports. It uses `/dev/wwan0at0` for control. But the hotplug rule doesn't
know that.

The fix is an ignore list plus [a patch to the hotplug
script](https://github.com/vjt/openwrt-glinet-x3000/blob/openwrt-25.12/x3000/patches/0001-modemmanager-tty-honour-ignore-tty.patch):
`/etc/modemmanager/ignore-tty` lists the device nodes to leave alone, and the
patched `/etc/hotplug.d/tty/25-modemmanager-tty` checks that file before
handing a tty to MM. The patch applies cleanly and fails loudly if the
upstream script drifts.

With this in place, `/dev/ttyUSB0`–`3` stay free for direct AT access. MM
uses `/dev/wwan0at0` for everything it needs. Everyone is happy — most
importantly, [my telemetry pipeline](https://github.com/vjt/quectel-5g-tools)
keeps reading signal metrics straight from the modem without a fight.

## Pitfall 6: ADB Is Behind a Firmware Gate

The RM520N-GL runs its own Linux inside the Qualcomm SDX62 baseband SoC.
ADB access into that userland is extremely useful — logs, firmware
diagnostics, `/usrdata` — and it is locked by default.

There are two locks. First, the ADB USB interface is disabled in the default
USB composition. You enable it with a composition switch:

```sh
# Inspect current composition
quectel-at 'AT+QCFG="usbcfg"'
# +QCFG: "usbcfg",0x2C7C,0x0801,1,1,1,1,1,0,0   ← ADB off (second-to-last bit)

# Flip the ADB bit on
quectel-at 'AT+QCFG="usbcfg",0x2C7C,0x0801,1,1,1,1,1,1,0'
# OK
```

Then there's the second lock — a challenge-response on `AT+QADBKEY`:

```sh
# Step 1: get the challenge
quectel-at 'AT+QADBKEY?'
# +QADBKEY: 12345678

# Step 2: compute the response (offline tool)
./qadbkey-unlock 12345678
# 0jXKXQwSwMxYoeg

# Step 3: submit
quectel-at 'AT+QADBKEY="0jXKXQwSwMxYoeg"'
# OK
```

The response is derived from a private key Quectel baked into the modem
firmware. The unlock state persists on NVRAM through reboots and modem
firmware upgrades — as long as you stay on a compatible firmware branch.

Once both locks are open, you can shell into the modem's SoC:

```
root@jeeves:~# uname -a
Linux jeeves 6.12.79 #0 SMP Tue Apr 28 15:21:30 2026 aarch64 GNU/Linux
root@jeeves:~# adb shell
/ # uname -a
Linux sdxlemur 5.4.210-perf #1 PREEMPT Fri Mar 1 06:52:45 UTC 2024 armv7l GNU/Linux
```

A router-shaped box. Two SoCs, two architectures, two kernels. The aarch64
one runs your network. The armv7l one runs inside your modem, and you can
shell into it.

Here is the gate: Quectel removed `AT+QADBKEY?` entirely in firmware
`RM520NGLAAR_A0.301` and later. EU Radio Equipment Directive (RED DA)
compliance — there's a whole [discussion
thread](https://github.com/iamromulan/cellular-modem-wiki/discussions/122)
about it. Once you flash firmware `≥ A0.301`, ADB is gone. There is no
supported path back.

Jeeves is currently on `A03A03M4G`, which is safely below the gate. I keep a
mandatory checklist before any modem firmware update: read `AT+QGMR`, compare
the build identifier against `A0.301` lexically, and either proceed or stop.

## Pitfall 7: qfirehose 1.4.11 Bricks Modems

The standard Quectel firmware flasher is `qfirehose`. The upstream release at
the time of my migration was 1.4.11. It has a known bug that bricks RM520N
modules — leaves them in a partially flashed state they can't recover from
without RMA.

The `nippynetworks/qfirehose` fork patched this at version 1.4.17. I forked
that into [vjt/qfirehose](https://github.com/vjt/qfirehose) to add a clean
OpenWrt package recipe under `openwrt/`, so the binary lands directly in the
image instead of being something I install later. Do not use upstream 1.4.11.

## The Build Plumbing: Three More Surprises

Beyond the hardware pitfalls, the build system had its own surprises.

**Brotli is not in OpenWrt 25.12 feeds.** The `adb`/`fastboot` tools depend
on `libbrotli`. OpenWrt 25.12's package feeds don't ship Brotli. I had to
build it myself and wire it into a local feed alongside an `android-tools`
package that compiles cleanly against the feed's `libbrotli`. Both live in
[vjt/openwrt-android-tools](https://github.com/vjt/openwrt-android-tools), a
multi-package repo that the builder picks up via `src-link` in `feeds.conf`.

**`telegraf-full`, not `telegraf`.** The standard `telegraf` package is
compiled with a limited set of input plugins. I use the `dns_query` input
plugin to monitor the latency and reachability of my recursive resolvers,
and `dns_query` is not in the minimal build. If your `telegraf.conf`
references a plugin that wasn't compiled in, the config parser refuses to
start with an explicit error about the unknown input type — fair enough,
nothing cryptic. The `-full` variant compiles every plugin. The image size
difference is significant — jumping from ~41 MB to ~81 MB — but there are
no surprises at runtime.

**`fwtool` must be present at build time.** The OpenWrt build system's
`Build/append-metadata` step embeds metadata (board name, compatible devices,
version string) into the sysupgrade image. Without `staging_dir/host/bin/fwtool`,
this step silently no-ops instead of failing. The image builds, looks fine, and
then fails `sysupgrade --test` with *"Image metadata not present"* when you try
to flash it. The fix is to build `fwtool` as part of the host toolchain before
building the target image.

## What I Actually Baked In

The final image includes, beyond the standard OpenWrt 25.12 package set:

- **[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools)** — a
  collection of Lua tools I wrote for monitoring and interacting with the
  Quectel modem. `5g-info` dumps a full snapshot, `5g-monitor` is a live TUI
  with signal quality display and configurable audio beeps, `5g-lock`
  handles band and cell locking, `quectel-at` is a zero-ceremony AT command
  wrapper. There's also a Prometheus collector and `5g-led-bars` — a procd
  daemon that drives the four 5G signal LEDs on the GL-X3000's front panel
  from PCC/SCC NR-RSRP in real time.
- **[`qfirehose`](https://github.com/vjt/qfirehose) 1.4.17** — patched fork
  with the OpenWrt build recipe.
- **[`adb` + `fastboot`
  35.0.2](https://github.com/vjt/openwrt-android-tools)** — for modem USB
  composition switches and ADB access into the SDX62.
- **`telegraf-full`** — pushing metrics to my internal Prometheus.
- **[`wifi-dethrash-collector`](https://github.com/vjt/openwrt-dethrash)** — a
  Prometheus collector tracking Wi-Fi parameters.
- A rootfs overlay with my internal CA and the apk feed signing key.

The feed is served from
[nowhere](/posts/2026-01-20-raspberry-pi-luks-encrypted-root/) (my
always-on Raspberry Pi) via a [custom
builder](https://github.com/vjt/openwrt-builder) that polls GitHub for
changes, kicks off remote SDK builds on Hetzner spot instances, and serves
the resulting apk index over HTTP on the management VLAN. Signed with an
ECDSA P-256 key; the pubkey is baked into the image so `apk add` works out
of the box.

{{< figure src="signal-rabdomant.jpg" alt="A phone resting on an orange tool bag, screen showing the 5g-monitor TUI: TIM carrier, IDLE state, BEEP:ON, LTE Band 3 with PCI 427 SINR 8 dB, 5G-NSA Band n78 with PCI 920 SINR 14 dB, full carrier aggregation breakdown and a list of neighbour cells, with a multitool half-visible on the side" caption="`5g-monitor` in the field. PCC, SCC, neighbour cells, all the signal you need to decide whether to keep climbing." >}}

<video controls preload="metadata" width="100%">
  <source src="5g-monitor-beep.mp4" type="video/mp4">
</video>

## Epilogue: The SINR Mystery

About two weeks before this migration, my 5G SINR dropped from a baseline
of around 18 dB to 12 dB — over the course of a couple of minutes. Same
RSRP, same cell, same beam, just 6 dB more noise. Nothing changed on my
side. I wasn't watching the dashboard at the time, and didn't notice.

I noticed the morning *after* I flashed vanilla OpenWrt. I ran a speed test
out of habit: ~200 Mbps where I used to see ~350. That made me unhappy. My
first instinct was to suspect the migration — a regression in the kernel,
in MHI, in something I'd just changed. But I had something the previous-me
didn't: long-term telemetry.

{{< figure src="sinr-drop.png" alt="Two stacked Grafana panels labelled SINR and RSRP, ranging from 03/30 to 04/27. The SINR panel shows a baseline around 17–18 dB until mid-April, then drops to ~11–13 dB and stays there. The RSRP panel stays flat between -94 and -97 dBm across the entire window, with several visible vertical gaps where data is missing. Multiple coloured series, one per PCI on the n78 band" caption="Two months of SINR (top) and RSRP (bottom) for every n78 cell I've seen. RSRP is flat across the whole window — same signal strength. The SINR baseline shifts down mid-April. The vertical gaps in RSRP are real 5G outages, minutes-long windows where the modem lost the carrier entirely. Those outages are the other reason I'm running my own firmware." >}}

I've been collecting RSRP, RSRQ, SINR, band, PCI, and carrier aggregation
state via [quectel-5g-tools](https://github.com/vjt/quectel-5g-tools) since
January, fed into an internal VictoriaMetrics. The telemetry made it
unambiguous: the SINR drop happened weeks before I touched the firmware.
Same signal strength (flat RSRP), 6 dB more noise, same PCI, no handover.
The migration is not the cause. I didn't roll back to stock — confidence
from data, not from hope.

Flat RSRP with SINR down 6 dB means the noise floor rose. The modem is
still receiving the same signal from the same tower; there is now
significantly more interference on top of it. The preserved daily
oscillation (interference is lower at night, when fewer devices are
active) tells you the new interference source varies with load, not with
weather or geometry. The diagnosis: the carrier almost certainly activated
a new n78 cell nearby. The GL-X3000 is on n78 (3.5 GHz TDD), the primary
5G band in Italy and the one being most aggressively densified right now.
Nothing to fix on my end. The carrier densified their network. My SINR is
collateral damage.

Naturally, I went up a ladder to see if a tighter antenna alignment could
claw back a dB.

{{< figure src="me-ladder.jpg" alt="The author on a stepladder on a balcony, wearing a Slackware t-shirt, looking at the camera. A phone showing 5g-monitor signal output is propped on the ladder rail next to him; an apartment building and potted plants are visible behind" caption="Scientific method: hold the phone showing live SINR on the rail, tilt the antenna with the other hand, watch the number." >}}

{{< figure src="me-antenna.jpg" alt="Selfie taken from below — the author at bottom-left of frame, the directional 5G antenna mounted on the building wall above him, sunlit countryside and a vineyard in the background under a clear sky" caption="It worked. ~+1 dB SINR after re-pointing, ~+40 Mbps throughput. Five minutes of ladder time, well spent." >}}

The other thing the graph shows are the gaps in RSRP — those are not
plotting artifacts. Those are full 5G outages. Minutes-long windows where
the modem lost signal entirely. That is the other reason I'm done with
GL.iNet stock firmware. When 5G drops on stock, the router falls back to
4G — and stays there. My local LTE is around 5 Mbit/s. I've already
[learned the hard
way](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) what a
surprise 5G outage costs in a meeting that matters. With vanilla OpenWrt
and my own reconnect logic, I can detect the outage, wait for 5G to
restore, and flip back automatically — in seconds, not hours, and without
trusting a fork's automation to do the right thing.

Reliability is not a setting. Reliability is something you build. And to
build it, you need the source.

---

The migration docs, build scripts, custom packages, and the
quectel-5g-tools source are all on GitHub under
[vjt/](https://github.com/vjt). The kernel patches, local feed wiring, and
rootfs overlay live in
[vjt/openwrt-glinet-x3000](https://github.com/vjt/openwrt-glinet-x3000).
If you're doing the same migration, start with the [OpenWrt wiki page for
the GL-X3000](https://openwrt.org/toh/gl.inet/gl-x3000) — it's reasonably
accurate — and treat the pitfalls above as the errata.
