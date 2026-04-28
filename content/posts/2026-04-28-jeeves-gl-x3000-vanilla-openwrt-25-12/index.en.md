---
title: "GL-X3000 on Vanilla OpenWrt 25.12: Every Pitfall, Documented"
date: 2026-04-28
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "A full migration diary: stock GL.iNet firmware off, vanilla OpenWrt 25.12 on, seven pitfalls documented so you don't have to rediscover them."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** I migrated my GL-iNet GL-X3000 (Spitz AX) 5G router from the
stock GL.iNet firmware (OpenWrt 21.02, kernel 5.4) to vanilla OpenWrt 25.12
(kernel 6.12.79). The modem — a Quectel RM520N-GL on PCIe/MHI — works
perfectly. There are at least seven distinct ways to get things wrong before
you get there. I found most of them. This is the map.

<!--more-->

## Why Bother

The GL-X3000 is a fine piece of hardware: MediaTek MT7981B (Filogic 820),
Wi-Fi 6, USB 3.0, and a Quectel RM520N-GL 5G modem on an M.2 slot wired to
both PCIe and USB. The stock firmware is GL.iNet's flavour of OpenWrt 21.02,
which shipped on kernel 5.4. That kernel reached end of life in December 2022.

The router is Jeeves — it sits in front of my whole home network as the 5G WAN
gateway. Running a kernel that's three major versions behind on something that
handles all my traffic started feeling wrong. But the bigger pull was what
vanilla OpenWrt 25.12 offers: mainline MHI support for the modem's PCIe data
path, ModemManager integration, a proper apk-based package manager, and the
entire current package ecosystem. GL.iNet's firmware is a fork with proprietary
drivers and a separate update cycle. Vanilla is the real thing.

The migration took longer than it should have. Here is everything I learned.

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
set your PC to a static IP on `192.168.1.0/24`, open `192.168.1.1` in a
browser, and feed it the sysupgrade bin. Takes about 90 seconds.

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

The fix is a one-liner kernel patch adding the sub-device ID to the driver's
PCI match table. Without it, you have a 5G router with no 5G. I ship this
as `target/linux/generic/pending-6.12/gl-x3000-quectel-pci-id.patch` in the
build tree.

## Pitfall 3: PCIe Runtime Power Management Will Crash Your Modem

This one cost me the most time. Symptoms: the modem comes up fine, ModemManager
connects, traffic flows — and then, some minutes or hours later, the modem
disappears with a cascade of kernel errors:

```
pci 0000:01:00.0: AER: Correctable error message received
pci 0000:01:00.0: PCIe Bus Error: severity=Correctable, type=Physical Layer
pci 0000:01:00.0: MHI: channel not open
pci 0000:01:00.0: PCIe: ERROR CmpltTO
```

What's happening: the kernel's PCIe port power management is putting the PCIe
port into D3hot (link power-down). When traffic arrives, the port wakes up, but
the MHI bus never fully recovers from the link-down event. The PCIe AER layer
starts logging Completion Timeouts. The modem goes silent.

The fix is blunt and permanent:

```
pcie_port_pm=off
```

in the kernel command line. This disables PCIe port power management globally.
On the GL-X3000 that means the modem link stays at full power. No more crashes.

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
your AT command tools (`quectel-at`, `picocom`) can't talk to the modem while
MM is running.

The modem data path goes over PCIe/MHI, so MM doesn't *need* the ttyUSB ports.
It uses `/dev/wwan0at0` for control. But the hotplug rule doesn't know that.

The fix is an ignore list: `/etc/modemmanager/ignore-tty` listing the device
nodes to leave alone, plus a patch to the hotplug script that honours it.
The patched script checks the file before handing a tty to MM. I ship this as
a unified diff in `data-trunk/x3000/patches/` so it applies cleanly and fails
loudly if the upstream script drifts.

With this in place, `/dev/ttyUSB0`–`3` stay free for direct AT access. MM uses
`/dev/wwan0at0` for everything it needs. Everyone is happy.

## Pitfall 6: ADB Is Behind a Firmware Gate

The RM520N-GL runs its own Linux inside the Qualcomm SDX62 baseband SoC.
ADB access into that userland is extremely useful — logs, firmware diagnostics,
`/usrdata` — and it is locked by default.

Unlocking is a two-step challenge-response:

```sh
# Step 1: get the challenge
quectel-at 'AT+QADBKEY?'
# +QADBKEY: 29501379

# Step 2: compute the response (offline tool)
./qadbkey-unlock 29501379
# PVGyBuHqovCAiSF

# Step 3: submit
quectel-at 'AT+QADBKEY="PVGyBuHqovCAiSF"'
# OK
```

The response is derived from a private key Quectel baked into the modem
firmware. The key persists on NVRAM through reboots and modem firmware upgrades
— as long as you stay on a compatible firmware branch.

Here is the gate: Quectel removed `AT+QADBKEY?` entirely in firmware
`RM520NGLAAR_A0.301` and later. EU Radio Equipment Directive (RED DA)
compliance — there's a whole
[discussion thread](https://github.com/iamromulan/cellular-modem-wiki/discussions/122)
about it. Once you flash firmware `≥ A0.301`, ADB is gone. There is no
supported path back. The command doesn't exist anymore.

Jeeves is currently on `A03A03M4G`, which is safely below the gate. I keep a
mandatory checklist before any modem firmware update: read `AT+QGMR`, compare
the build identifier against `A0.301` lexically, and either proceed or stop.

## Pitfall 7: qfirehose 1.4.11 Bricks Modems

The standard Quectel firmware flasher is `qfirehose`. The upstream release at
the time of my migration was 1.4.11. It has a known bug that bricks RM520N
modules — leaves them in a partially flashed state they can't recover from
without RMA.

The `nippynetworks/qfirehose` fork was patched at version 1.4.17. That's what
I use and that's what's baked into the image as a custom package from
`vjt/qfirehose`. Do not use upstream 1.4.11.

## The Build Plumbing: Three More Surprises

Beyond the hardware pitfalls, the build system had its own surprises.

**Brotli is not in OpenWrt 25.12 feeds.** The `adb`/`fastboot` tools
(`nmeum/android-tools`) depend on `libbrotli`. OpenWrt 25.12's package feeds
don't ship Brotli. I had to build it myself and wire it into a local feed
alongside the android-tools package. Both live in `vjt/openwrt-android-tools`,
a multi-package repo that the builder picks up via `src-link` in `feeds.conf`.

**`telegraf-full`, not `telegraf`.** The standard `telegraf` package is compiled
with a limited set of input plugins. If your `telegraf.conf` references a plugin
that wasn't compiled in, the config parser blows up at startup with a cryptic
error about an unknown input type. The full variant compiles every plugin, which
is what you want. The image size difference is significant — jumping from ~41 MB
to ~81 MB — but there are no surprises at runtime.

**`fwtool` must be present at build time.** The OpenWrt build system's
`Build/append-metadata` step embeds metadata (board name, compatible devices,
version string) into the sysupgrade image. Without `staging_dir/host/bin/fwtool`,
this step silently no-ops instead of failing. The image builds, looks fine, and
then fails `sysupgrade --test` with *"Image metadata not present"* when you try
to flash it. The fix is to build `fwtool` as part of the host toolchain before
building the target image.

## What I Actually Baked In

The final image includes, beyond the standard OpenWrt 25.12 package set:

- **`quectel-5g-tools`** — a collection of Lua tools I wrote for monitoring and
  interacting with the Quectel modem. `5g-info` dumps a full snapshot, `5g-monitor`
  is a live TUI with signal quality display and configurable audio beeps,
  `5g-lock` handles band and cell locking, `quectel-at` is a zero-ceremony AT
  command wrapper. There's also a Prometheus collector and `5g-led-bars` — a
  procd daemon that drives the four 5G signal LEDs on the GL-X3000's front panel
  from PCC/SCC NR-RSRP in real time.
- **`qfirehose` 1.4.17** (patched fork)
- **`adb` + `fastboot` 35.0.2** — for modem USB composition switches and ADB access
- **`telegraf-full`** — pushing metrics to my internal Prometheus
- **`wifi-dethrash-collector`** — a Prometheus collector tracking Wi-Fi parameters
- A rootfs overlay with my internal CA, the apk feed signing key, and an
  `/etc/sysupgrade.conf` that keeps `/root` across in-place upgrades

The feed is served from `nowhere` (my always-on host) via a custom builder that
polls GitHub for changes, kicks off remote SDK builds on Hetzner spot instances,
and serves the resulting apk index over HTTP on the management VLAN. Signed with
an ECDSA P-256 key; the pubkey is baked into the image so `apk add` works out
of the box.

## Epilogue: The SINR Mystery

A few weeks after the migration settled in and everything was running well, my
5G SINR dropped from a baseline of around 18 dB to 12 dB — over the course of
about two minutes. Nothing changed on my side: no software update, no antenna
movement, no hardware change.

Checking the obvious: RSRP stayed flat at around -96 dBm (signal power
unchanged), RSRQ moved by 1 dB (barely). PCI unchanged (same cell, same beam,
no handover). Throughput dropped from ~350 Mbps to ~200 Mbps. The SINR drop
has a daily oscillation pattern — higher at night, lower during the day — but
the whole envelope shifted down uniformly.

Flat RSRP with SINR down 6 dB means the noise floor rose. The modem is still
receiving the same signal from the same tower; there's now significantly more
interference on top of it. The preserved daily oscillation (traffic-modulated
interference is lower at night when fewer devices are active) tells you the
new interference source varies with load, not with weather or geometry.

The diagnosis: the carrier almost certainly activated a new n78 cell nearby.
The GL-X3000 is on n78 (3.5 GHz TDD), which is the primary 5G band in Italy
and the one being most aggressively densified right now. A new co-channel cell
means a permanently higher interference floor — the structural baseline shift —
while traffic-dependent interference coordination still follows the same daily
pattern, just at a lower absolute level.

Nothing to fix on my end. The carrier densified their network. My SINR is
collateral damage. 200 Mbps at SINR 12 dB is still usable — it's just not as
satisfying as 350 at 18.

---

The migration docs, build scripts, custom packages, and the quectel-5g-tools
source are all on GitHub under [vjt/](https://github.com/vjt). The kernel
patches, local feed wiring, and rootfs overlay live in the build tree. If
you're doing the same migration, start with the [OpenWrt wiki page for the
GL-X3000](https://openwrt.org/toh/gl.inet/gl-x3000) — it's reasonably
accurate — and treat the pitfalls above as the errata.
