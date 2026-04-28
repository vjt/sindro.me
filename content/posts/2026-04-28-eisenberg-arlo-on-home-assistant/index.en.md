---
title: "Eisenberg: Arlo cameras on Home Assistant, the easy way"
date: 2026-04-28
tags: [home-assistant, arlo, hacs, mqtt, python, devlog]
description: "A small, typed, event-driven Home Assistant integration for Arlo cameras. Push approval once, then silent for 14 days."
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

That's the entire flow. It is the same trusted-browser flow that `my.arlo.com` runs in your laptop — the integration just routes one push through your phone, captures the 14-day trust cookie Arlo issues, and goes silent.

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

## How it works

The integration is event-driven. There is no polling loop. Arlo pushes its state changes — motion, AI classification, snapshot URL, mode change, base-station heartbeat — over an MQTT firehose, and a single coordinator distributes those to entities the moment they arrive. REST is used only for the things that actually need a request/response: starting a stream, setting a mode, firing a snapshot, the initial device discovery.

### Auth

The first login does the full handshake: `POST /api/auth` with the password (base64-encoded) yields a short-lived token. That token then drives `POST /api/getFactorId` to ask Arlo whether this browser is already trusted. If it is, `POST /api/startAuth` completes the trip silently and you're authenticated. If not, you get a push — exactly one — that the user approves on their phone, then a single `POST /api/finishAuth` confirms. Arlo's response includes a 14-day trust cookie which we persist into the Home Assistant config entry. Every subsequent restart re-uses that cookie and login completes silently in three round trips.

Crucially: the form-driven flow makes one HTTP call per user click in the HA dialog. There's no polling task hammering `finishAuth` while the user fumbles for their phone — Arlo rate-limits that endpoint hard, and a tight retry loop is the fastest way to lock yourself out for hours.

The token expires after roughly two hours; the coordinator checks every 30 minutes and refreshes silently at the 60-minute mark, which keeps a comfortable headroom against expiry.

### MQTT

Arlo's event firehose is plain MQTT 3.1.1 over a WebSocket. The integration implements that protocol directly on top of the same `aiohttp` WebSocket session it uses for REST — no second TCP stack, no separate library to keep alive across reconnects. The MQTT codec is a small module that does packet framing for the half-dozen control packets that matter (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ) and drops everything else.

Each subscribed topic has a typed handler. Camera state lands in `cameras/+/is`, motion events in `feed/live`, snapshot URLs in `fullFrameSnapshotAvailable`, mode changes in `automation/activeMode/is`, and so on. The coordinator routes each frame to the right handler, parses the payload into a Pydantic model, and updates entity state. If a payload doesn't match the expected shape, it's logged at WARNING — that discipline surfaced three event types Arlo had quietly started emitting that nobody had noticed before.

### Streaming

Arlo serves live streams over RTSP-on-port-443-with-TLS, which is technically RTSPS. The API tells you `rtsp://`. Don't believe it: rewrite the URL to `rtsps://` before handing it to Home Assistant's stream worker, and force TCP transport (UDP can't traverse TLS). Then add three ffmpeg flags — `fflags=nobuffer`, `flags=low_delay`, `use_wallclock_as_timestamps` — and HLS lag drops from ~30 seconds to under one. I checked.

The browser User-Agent gets RTSP from Arlo's `startStream` endpoint. A mobile UA gets DASH instead, which is harder to bend to HA's stream component, so the integration sends a Chrome UA for everything except this one call.

### Mode setting

Arming the camera lives in Arlo's v3 location automation API: `PUT /hmsweb/automation/v3/activeMode?locationId=…&revision=N` with body `{"mode": "armAway"}`. The revision counter is the optimistic-concurrency token — bump it on every read, echo it on every write. If a parallel client (the Arlo mobile app, an automation) bumps the counter behind us, the PUT fails; we re-fetch the live revision and retry once.

### Image persistence

The dashboard tile would otherwise blank out every time the camera is disarmed (no live snapshots) or every restart (no in-memory cache). Both problems get solved the same way: every snapshot, motion thumbnail, or stream-end keyframe goes both to the in-memory cache and to disk under the configured `media_dirs` location. On boot, the coordinator scans that location for the newest image per camera and seeds the cache from disk. A retention prune (configurable, default 14 days) sweeps old files on every health-check tick.

## Why I built it

I have one Arlo camera. It's cloud-only by design and there was nothing I could do about that, but I wanted the part *between my Home Assistant and Arlo's cloud* to be small enough that I could read it end to end. Native `asyncio`, types at every boundary, no scraping tricks, no library I didn't want to inherit. Roughly 1500 lines of Python in the integration plus the client library, all of it on PyPI under MIT, and that was the whole goal.

## Get it

```
HACS → Custom repositories → https://github.com/vjt/ha-eisenberg
```

Or click the **Open in HACS** badge in the README — it deep-links into your instance with the repo pre-filled. Source is MIT. The client library is `pyeisenberg` on PyPI.
