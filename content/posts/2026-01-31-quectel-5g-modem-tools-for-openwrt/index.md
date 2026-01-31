---
title: "5G as Fiber Backup: Never Miss a Meeting Again"
date: 2026-01-31
tags: ["5g", "networking", "openwrt", "python", "sysadmin"]
description: "Open source Python tools for Quectel 5G modems on OpenWRT. Real-time signal monitoring with audio feedback for antenna pointing. MIT licensed."
---

A couple months ago my fiber went down - as per Murphy's Law - on the day of an important work meeting with a partner company. Jamming between the distant AP of my neighbor and my phone hotspot, but both sucked hard. 200ms rtt, 15% packet loss. I was then apologizing profusely while my video started looking like a slideshow from 1998 - and no one could parse what I was saying. Shut down video, keep silent, missed opportunity. Never again!

So I went full paranoid and built a proper 5G backup setup.

## The Hardware

- [GL.iNet X-3000](https://www.gl-inet.com/products/gl-x3000/) with a Quectel RM520N-GL modem
- [Poynting XPOL-24](https://poynting.tech/antennas/xpol-24/) directional antenna mounted on the wall outside my home office

5G signal here is non-existing, so I had to use heavy artillery. The Poynting is a beast. 11 dBi gain, real 4x4 MIMO, cross-polarized, weather-sealed. Point it at the nearest tower and suddenly your SINR jumps from "meh" to "holy shit."

But pointing a directional antenna without visual feedback is painful. You're basically spinning in circles, refreshing a web UI, cursing at the sky.

## The Software

I wrote a set of tools to solve this: [quectel-5g-tools](https://github.com/vjt/quectel-5g-tools).

`5g-info` dumps everything your modem knows in a readable format:

![5g-info output](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/5g-info.png)

`5g-monitor` is an ncurses TUI that refreshes in real-time and—here's the good part—**beeps based on your SINR**. Higher signal quality = more beeps. Point the antenna, listen for beeps, tighten the bolts. Done.

![5g-monitor TUI](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/5g-monitor.png)

It's like a metal detector, but for 5G.

## Technical Notes

The modem speaks AT commands over `/dev/ttyUSB2`. The tools parse responses from `AT+QENG`, `AT+QCAINFO`, and friends to extract serving cell info, carrier aggregation status, and neighbor cells.

Everything runs on OpenWRT. Install deps with `opkg install python3-pyserial python3-toml python3-ncurses`, clone the repo, and run `./bin/5g-monitor`. No compilation, no containers, no bullshit.

There's also `force-bands` if you want to lock your modem to specific LTE/NR bands (useful when the modem insists on connecting to a faraway tower with better RSRP but worse throughput).

## Result

My 5G backup now sits at 300+ Mbps down, 50+ up. When fiber dies, my router fails over automatically courtesy of `mwan3`. Meetings continue. Clients remain unaware. Blood pressure stays normal.

The code is MIT licensed and lives at [github.com/vjt/quectel-5g-tools](https://github.com/vjt/quectel-5g-tools). PRs welcome.

## Images

The Poynting right after unboxing and set up on the test tripod:

![Poynting test](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-testing.jpg)

The X3000 wall-mounted a couple days after the "holy shit!" 300Mbit download moment during testing

![X3000 Wall Mount](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/x3000-wall-mount.jpg)

The Poynting wall mounted in its (semi) final setup. My biggest DIY so far - I had never drilled concrete before while standing on a 2m ladder on a first floor terrace :-D

![Poynting Wall Mount](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-wall-mount.jpg)

Have fun!
