---
title: "Batocera in Home Assistant"
date: 2026-11-15
draft: true
tags: [home-assistant, batocera, retrogaming, emulationstation, mqtt, hacs, claude-code, ai-generated]
description: "ha-batocera: a Home Assistant integration for a Batocera retrogaming box. Search the catalog and launch games from the phone, see what gets played and for how long, watch the TV live, quit a stuck game, and set playtime limits."
---

> **Before we start.** Batocera is a Linux distribution for retrogaming:
> it boots a PC straight into EmulationStation, a gamepad-driven menu with
> emulators for old consoles and home computers behind it. The games in the
> screenshots are backup copies of originals I own. This post does not
> endorse downloading games, and nothing described here downloads any.

Under our TV there's **joker**, a mini PC running Batocera 43: the kids'
console. Now it's also a device in Home Assistant, through an integration I
wrote with Claude Code: [ha-batocera](https://github.com/vjt/ha-batocera).

## Why

- **Search.** joker holds thousands of games, and searching them with a pad
  means an on-screen keyboard, one letter at a time. On the phone I type
  "mario", get every Mario on every system, and one tap starts it on the TV.
- **What the kids play, and for how long.** You want that data before
  setting any limit. The limits came after.
- **Quitting a stuck game.** Sometimes the exit hotkey just doesn't respond.
  The stop button on the phone always does.

## How it works

A small daemon on the box (Python, standard library only) hears about every
game start and stop from Batocera's launch hook, reads the catalog from
EmulationStation's local API, and talks to Home Assistant over MQTT. HACS
ships it together with the integration.

```mermaid
graph LR
    launcher[Batocera launcher] -->|start / stop| daemon[daemon]
    es[EmulationStation] <-->|catalog, launch| daemon
    daemon <-->|MQTT| ha[Home Assistant]
```

## The page

The integration adds a **Batocera** page to the sidebar: dark CRT look,
pixel font, because of course. Favourites, recently played, one tile per
system with its logo.

![The Batocera page on a phone: INSERT COIN, a search box, and tiles for favourites, recently played and each system](/posts/2026-11-15-batocera-in-home-assistant/page-systems.jpg)

Search works at every level, across all systems or inside one.

![Searching "mario" with the phone keyboard](/posts/2026-11-15-batocera-in-home-assistant/page-search.jpg)

Recently played answers the first question, what actually gets played:

![Recently played: Super Mario Bros. Wonder, New Super Mario Bros. U and others; one title blurred](/posts/2026-11-15-batocera-in-home-assistant/page-recently-played.jpg)

Tap a game, **PRESS START**, and it runs on the TV. If something is
already running, the sheet says what it's about to quit.

![The launch sheet for Mario Kart 8, warning that it quits Mario Kart 8 Deluxe](/posts/2026-11-15-batocera-in-home-assistant/page-press-start.jpg)

While a game runs, the bar on top shows what's playing, for how long, and
how much time is left. KILL takes two taps, because a game quit by mistake
loses what wasn't saved.

![The now-playing bar: Mario Kart 8 Deluxe, one minute in, FREE PLAY, with KILL](/posts/2026-11-15-batocera-in-home-assistant/page-now-playing.jpg)

Everyone can browse; launching and stopping take an admin or a user picked
in the options.

## The live screen

The preview in the bar is a screenshot of the TV, refreshed every 15
seconds. Tap it and it goes live, about a frame per second, for as long as
someone's watching.

![The live screen: Mario Kart 8 Deluxe's title screen, as the TV shows it](/posts/2026-11-15-batocera-in-home-assistant/page-live-screen.jpg)

## Limits

Three, for the whole box: a daily limit in minutes, a window of allowed
hours, and a manual lock. They're set on the device page, and only an admin
can change them. Five minutes before the end Home Assistant fires an event
you can turn into a notification; at the end it stops the game, and keeps
stopping any new one.

![joker's device page: allowed from, allowed until and daily limit](/posts/2026-11-15-batocera-in-home-assistant/device-limits.jpg)

It's not a fortress, and the README says where the holes are.

## One warning

EmulationStation's web API can be opened to the whole LAN with its
`PublicWebAccess` setting, and then anyone on the network can launch games
or send input, no authentication. ha-batocera never opens it, and if it
finds it open, it says so under **Settings, Repairs**.

## Installing it

You need an MQTT broker the box can reach and root SSH on the box. Add the
repository to HACS as a custom one (the request for the default store is
[open](https://github.com/hacs/default/pull/14180)), install, then "Add
integration, Batocera": Home Assistant installs the daemon over SSH and
keeps it up to date, never in the middle of a game. Details in the
[README](https://github.com/vjt/ha-batocera).

## How it was born

Two days of work with Claude Code, a week apart: I said what I wanted,
tried it on joker and on my phone, and sent back what was wrong. 0.2 to
0.5.4, thirteen releases, about two hundred tests.

Along the way I hit enough Batocera pitfalls to write them down:
[batocera-skill](https://github.com/vjt/batocera-skill), a Claude Code skill
to drive a Batocera box over SSH. No ROMs, no daemon, nothing left running.

Both MIT.
