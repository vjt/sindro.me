---
title: "5G as Fiber Backup: Never Miss a Meeting Again"
date: 2026-01-31
tags: [ai-generated, iot, networking, openwrt, python, sysadmin, open-source]
description: "Open source Python tools for Quectel 5G modems on OpenWRT. Real-time signal monitoring with audio feedback for antenna pointing. MIT licensed."
---

![Directional antenna on a wall aimed at a cell tower, fiber cable snapping on one side while 5G waves bridge the gap](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/cover.jpg)

A couple of months ago, my fiber went down. As per Murphy’s first corollary, it happened at the absolute worst moment: right before a crucial meeting with a partner company. I found myself frantically jamming between a distant neighbor’s AP and my phone’s hotspot, but both sucked hard. We’re talking 200ms RTT and 15% packet loss. I was apologizing profusely while my video feed turned into a 1998 slideshow; no one could parse a word I was saying. I ended up cutting the video and staying silent. Missed opportunity. **Never. Again.**

So I went full paranoid and built a proper 5G backup setup.

## The Hardware

- [GL.iNet X-3000](https://www.gl-inet.com/products/gl-x3000/) with a Quectel RM520N-GL modem
- [Poynting XPOL-24](https://poynting.tech/antennas/xpol-24/) directional antenna mounted on the wall outside my home office

5G signal here is non-existent, so I had to use heavy artillery. The Poynting is a beast. 11 dBi gain, real 4x4 MIMO, cross-polarized, weather-sealed. Point it at the nearest tower and suddenly your SINR jumps from "meh" to "holy shit."

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

*Update, April 2026: the X3000 has since migrated off stock GL.iNet firmware to vanilla OpenWrt 25.12 — full story in [GL-X3000 on Vanilla OpenWRT 25.12: Fully Working](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/). And `mwan3` turned out to have its own subtle failure mode with banIP — postmortem in [How banIP Nuked My WireGuard Throughput Since February](/posts/2026-04-07-banip-icmp-mwan3/).*

The code is MIT licensed and lives at [github.com/vjt/quectel-5g-tools](https://github.com/vjt/quectel-5g-tools). PRs welcome.

## Images

The Poynting right after unboxing and set up on the test tripod:

![Poynting test](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-testing.jpg)

The X3000 wall-mounted a couple days after the "holy shit!" 300Mbit download moment during testing

![X3000 Wall Mount](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/x3000-wall-mount.jpg)

The Poynting wall mounted in its (semi) final setup. My biggest DIY so far - I had never drilled concrete before while standing on a 2m ladder on a first floor terrace :-D

![Poynting Wall Mount](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-wall-mount.jpg)

Have fun!
