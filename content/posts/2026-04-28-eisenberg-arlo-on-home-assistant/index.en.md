---
title: "Eisenberg: Arlo cameras on Home Assistant, the easy way"
date: 2026-04-28
tags: [home-assistant, arlo, hacs, mqtt, python, devlog]
description: "A small, typed, event-driven Home Assistant integration for Arlo cameras. Push approval once, then silent for 14 days. No IMAP, no Cloudflare bypass, no rate-limit roulette."
image: cover.jpg
featuredImage: cover.jpg
---

Setting up an Arlo camera on Home Assistant should look like this:

1. You install the integration from HACS.
2. You type your Arlo email and password.
3. Your phone buzzes. You tap **Approve** in the Arlo app.
4. You click **Submit** in Home Assistant.
5. You're in.

<!--more-->

That's the entire flow. There is no IMAP setup, no 2FA-code-pasting dialog, no waiting screen with a spinner that times out, no "rate-limited, try again in two hours" surprise. It is the same trusted-browser flow that `my.arlo.com` runs in your laptop — the integration just routes one push through your phone, captures the 14-day trust cookie, and goes silent.

You'll need that push approval again only when the cookie expires. The integration persists it across restarts and re-uses it on every wake-up. In the common case, you authenticate once and then never see another auth dialog.

The project lives at [github.com/vjt/ha-eisenberg](https://github.com/vjt/ha-eisenberg). I called it Eisenberg, after Arlo Eisenberg the skater. The name was an act of weakness. Move on.

## What you get out of the box

- **A camera entity** with on-demand snapshots, motion thumbnails, and live RTSPS streaming. Sub-second lag in HLS. The dashboard tile keeps an image even when the camera is disarmed (Arlo refuses cloud snapshots in standby) by caching the last good frame on disk.
- **Motion binary sensors**, both the generic kind and AI-classified person / vehicle / animal sensors that auto-reset.
- **A security-mode select** — `armAway`, `armHome`, `standby` — that you can drive from any automation. Tie it to your alarm panel, your `person.*` state, a time schedule, anything.
- **A siren switch**, **battery and signal-strength sensors**, **base-station connectivity**.
- **An `eisenberg.snapshot` service** for dashboard buttons or motion-driven automations. Fails loudly if the camera is in standby instead of silently no-op'ing, because that's the kind of thing you only debug at 1 AM.
- **Optional rolling archival** of motion clips, thumbnails and stream keyframes to a `media_dirs` location, with user-configurable retention (default 14 days).

Every motion event also fires an `eisenberg_media` event on HA's bus with the AI categories, the content URL, the thumbnail URL, the duration, the timestamp. Hook automations onto it.

## Under the hood (briefly)

The integration is event-driven. There is no polling loop. Arlo's MQTT firehose carries every state change — motion, AI classification, snapshot URL, mode change, base-station heartbeat — and a single coordinator distributes those to entities the moment they arrive. REST is used only for commands (start a stream, set a mode, fire a snapshot) and the initial device discovery.

The client library is a typed `aiohttp` + `asyncio` package on PyPI ([`pyeisenberg`](https://pypi.org/project/pyeisenberg/)). MQTT 3.1.1 is implemented from scratch over the existing WebSocket session — no second TCP stack to keep alive. Every API and MQTT payload lands in a Pydantic model, so unknown shapes log loudly during development instead of silently succeeding. That discipline surfaced three event types Arlo had quietly started emitting and would have been invisible otherwise.

For the curious: there is no Cloudflare bypass, no User-Agent spoofing rituals beyond the one place Arlo gates RTSP on a mobile UA, and no IMAP scraping for 2FA codes. The whole thing is small enough to read in an afternoon, and that was the point.

## Tested on, limitations

Built and run on an **Arlo Essential XL HD** (battery + solar, WiFi, cloud-only). Other Arlo models that share the v3 automation and MQTT shapes should work — file an issue if yours doesn't. All Arlo cameras are cloud-only by hardware design; this integration cannot fix that, only make the cloud path feel local.

## Get it

```
HACS → Custom repositories → https://github.com/vjt/ha-eisenberg
```

Or click the **Open in HACS** badge in the README — it deep-links into your instance with the repo pre-filled. Source is MIT. The client library is `pyeisenberg` on PyPI. The whole thing fits in your head.
