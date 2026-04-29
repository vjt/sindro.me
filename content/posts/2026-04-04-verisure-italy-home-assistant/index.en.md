---
title: "How I replaced the Verisure app with Home Assistant"
date: 2026-04-04
tags: [ai-generated, reverse-engineering, iot, home-assistant, python, security]
description: "The Verisure app is garbage: slow, ad-infested, zero automations. I replaced it with a custom Home Assistant integration."
image: cover.jpg
featuredImage: cover.jpg
---

The Verisure app is garbage. There, I said it.

It's not that the alarm itself is bad — the SDVECU panel is solid, the
sensors are reliable, the installation is professional. But the app. Good
lord, the app.

## The problem

You open the app to check your alarm status and you're greeted by **an ad
for Verisure itself**. I pay through the nose for the service and they
shove ads _inside_ the app. It's 2026 and a security company is showing me
banner ads when I'm trying to verify that my house is protected.

But the ads are the least of it. The real problems are:

- **Blind routines.** Yes, the app has "routines" — arm at midnight,
  disarm at 7. But they have no idea where you are. It's midnight
  and you're still in the garden? The alarm arms and the sensors
  go off. Window open? The panel announces it can't arm, but if you
  don't hear it the alarm stays disarmed. Go on vacation and forget
  to disable the morning disarm routine? Alarm off with an empty
  house. And routine changes take _20 minutes to propagate_ — "or
  the next day". In 2026.
- **Zero presence awareness.** The app doesn't know where you are.
  It doesn't know who's home. It doesn't know if the cleaning lady
  has left. No location-based automation whatsoever.
- **One camera at a time.** Want to see all your cameras? Tap, wait,
  go back, tap the next one, wait. No overview. No "capture all".
- **Biblically slow.** Request an image, wait, wait, maybe it arrives.
  Sometimes you reload the app and try again. In 2026.
- **No permanent storage.** Captured images vanish. There's no
  browsable history.
- **No timestamps on images.** You capture a photo and you don't know
  _when_ it was taken or _which camera_ took it. You have to
  remember. For a security system, that's embarrassing.
- **Generic notifications.** One notification, same for everyone. No
  actionable notifications, no critical alerts that bypass Do Not
  Disturb.

What I wanted: my alarm, integrated into my smart home, with intelligent
automations, notifications for all residents, and a dashboard that shows
_everything_ at a glance. No ads.

## The solution: Home Assistant + a custom integration

I wrote [ha-verisure-italy](https://github.com/vjt/ha-verisure-italy),
a custom component for Home Assistant that talks directly to the
Verisure Italy GraphQL APIs (`customers.verisure.it`). It completely
replaces the app for alarm control and camera monitoring.

### What it does

- **Alarm control** — arm partial+perimeter ("at home"),
  full+perimeter ("away"), disarm
- **Force arm** — when the alarm won't arm because a window is open,
  one tap to force it. Or better: an automation that forces
  automatically when you leave
- **Cameras** — auto-discovered, parallel capture with timestamp
  overlay, buttons for single camera and "capture all"
- **Auto-generated dashboard** — alarm panel, camera grid, capture
  buttons, everything auto-populated in the HA sidebar

![The auto-generated Verisure dashboard](/posts/2026-04-04-verisure-italy-home-assistant/dashboard.png)

### The automations the app can't do

Here's what runs in production at my house:

**Arm when the last person leaves.** A binary sensor tracks who's home
(GPS + WiFi via [OpenWrt presence detection](https://github.com/vjt/openwrt-ha-presence)).
When everyone's out, the alarm arms automatically.

**Safety net.** Every 5 minutes, if nobody's home and the alarm is off,
it re-arms and sends a notification. Because life is complicated and
presence sensors get it wrong sometimes.

**Automatic force-arm.** If the alarm won't arm because a window is
open, the integration detects the block, notifies which zones are
open, and forces the arm. An armed alarm with exceptions is better
than a disarmed alarm. Verisure routines? The panel announces the
failure — but if you're not there to hear it, the alarm stays off.

![Force arm: alarm blocked, one tap to force](/posts/2026-04-04-verisure-italy-home-assistant/force-arm.png)

**Smart night arming.** Not "arm at midnight" like Verisure routines.
It arms between midnight and 7 AM only when it detects that both
residents are home and at rest. You're in the garden at 2 AM? The
alarm waits.

**Safe morning disarm.** Disarms at 7, but _only if someone is home_.
Go to the beach and forget? The alarm stays armed. With Verisure
routines you have to remember to disable them — and if you forget,
you wait 20 minutes (or a day) for propagation.

**Actionable notification on arrival.** You arrive home with the alarm
armed? A notification with a "Disarm" button right on your phone.
Auto-dismisses if the alarm gets disarmed by other means.

**Critical status notification.** If the alarm reports an unknown
state, a critical notification that bypasses iOS Do Not Disturb.
This is security software — no error can go unnoticed.

And all of this works via **CarPlay** — I see the alarm status and
receive notifications right from the car.

## Technical design

This isn't a weekend project. It's security software: one wrong
behavior = alarm disarmed = the burglar gets in. Every decision
optimizes for correctness, not convenience.

### Two-layer architecture

- **API Client** (`verisure-italy` on [PyPI](https://pypi.org/project/verisure-italy/)) —
  typed GraphQL client, Pydantic models for every request/response,
  no `dict`, no `Any`. If the response doesn't match: `ValidationError`.
  Crash loud at the boundary, guaranteed types on the inside.
- **HA Integration** (`custom_components/verisure_italy/`) — alarm
  control panel, camera, buttons, config flow with 2FA, auto-generated
  dashboard. Our code, clean, Italy-specific.

### State machine

The Verisure panel has 6 protocol states across two axes:
interior (OFF/PARTIAL/FULL) x perimeter (OFF/ON). The state machine
enumerates all of them. An unknown state is an error, never a
default. The code crashes loud and notifies a human.

### Engineering principles

- **Fail-secure.** Unknown state = ERROR, never "probably disarmed".
  Timeout = keep previous state and notify.
- **Parse at the boundary.** JSON from the API → Pydantic models at
  the HTTP level. If parsing fails, it blows up there. Inside the
  codebase, types guarantee correctness.
- **No silent defaults.** No `.get()` with fallbacks on data that
  must exist. No `= None` hiding degradations.
- **Strict type system.** Pyright in strict mode, 0 errors, 14
  seconds. 165 tests. Ruff for linting. `scripts/check.sh` runs
  everything in one shot.

### Iterations, not big bang

The project started as a POC: "can I talk to the Verisure APIs from
Python?" Yes. Then: "can I integrate it into HA?" Yes. From there,
iteration after iteration:

1. Working POC
2. Basic HA integration (arm/disarm/status)
3. Cameras with parallel capture
4. Config flow with 2FA
5. Auto-generated dashboard
6. Force-arm with exception handling
7. **v0.7.0** — hardening from code review: 3 CRITICAL and 7 HIGH resolved
8. **v0.8.0** — second review: all HIGH and MEDIUM resolved, pyright
   clean, 165 tests, clean boundaries, thread safety

At every iteration, code review with 8 parallel agents (4 line-level +
4 architecture) combing through every file. Nothing gets left behind.

## Installation

The integration installs via [HACS](https://hacs.xyz/) (Home Assistant
Community Store) — the community's custom component manager. If you
haven't installed it yet,
[follow the official guide](https://www.hacs.xyz/docs/use/download/download/).

Once HACS is active:

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=vjt&repository=ha-verisure-italy&category=integration)

Or manually via HACS → Custom repositories →
`https://github.com/vjt/ha-verisure-italy` → Integration.

The API client installs automatically from PyPI. The config flow
guides setup with full 2FA support. The dashboard generates itself.

> **Why isn't it in the official HA catalog?** The integration is
> young — I'm putting it through its paces with early adopters before
> submitting it for official inclusion. HACS is the right channel
> for this stage.

## What's missing

- **Permanent image storage.** The building blocks are there
  (captured images are bytes in memory), the persistence layer
  is missing.
- **Event timeline.** The API exposes events, but we don't consume
  them yet.
- **Multi-installation support.** The code handles one installation.
  The guard against duplicates is there, but multi-install is yet
  to be implemented.

## Conclusion

The Verisure app is a black box with ads slapped on top.
Home Assistant is an open platform where every piece is
programmable. It's no contest.

The code is on [GitHub](https://github.com/vjt/ha-verisure-italy),
the API client on [PyPI](https://pypi.org/project/verisure-italy/),
example automations in the
[documentation](https://github.com/vjt/ha-verisure-italy/blob/master/docs/automations.md).

Happy hacking!
