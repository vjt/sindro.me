---
title: "grappa-irc: it's on my phone now"
date: 2026-06-19
tags: [irc, azzurra, grappa-irc, pwa, rest, bouncer, elixir, phoenix, projects, ai-generated, open-source, pre-alpha]
description: "Quick update: grappa-irc left the README behind. It's the bouncer I now read IRC from every day, from my phone. A few words on what works — and where the deep technical writeups live."
image: cicchetto-iphone-itopers.png
featuredImage: cicchetto-iphone-itopers.png
---

The screenshot above is [cicchetto](https://github.com/vjt/grappa-irc) — the grappa PWA — running on my iPhone, on the live Azzurra network, in `#it-opers`. Look closely and you'll catch what it's showing: me and `vjt-claude` working out the outline of *this very post*. That's the update in one image. grappa stopped being a README and a green CI badge. It's the thing I read IRC from now, every day, from the couch.

<!--more-->

## For anyone just tuning in

Two pieces, one repo:

- **grappa** — an always-on IRC bouncer with a REST API. It stays connected so you don't have to; your phone just talks HTTP to it.
- **cicchetto** — a PWA that looks like irssi and speaks only REST. It never parses a line of IRC. You install it on your home screen like an app.

The whole pitch, [from back in April](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/): *modern IRC — always-on, usable from a phone — without making it not-IRC.* If that sentence does anything for you, you're the audience.

![cicchetto's login screen on a phone: a nick field and an optional password — visitors don't need an account](cicchetto-login.png)

Getting in is a nick and, if you have one, a password — visitors don't need an account. The session is ephemeral, but the bouncer keeps your scrollback archived for next time.

## What changed: people actually use it

[Last time](/posts/2026-05-07-grappa-irc-mvp-e2e-pipeline/), MVP was "close". It arrived. grappa now runs in production for the `#it-opers` regulars — people who aren't me, on their own devices:

- someone tried it from an iPhone ("not bad"), someone else from Firefox on the desktop
- I run it on my phone and my laptop **at the same time** — same session, same scrollback, two screens
- it does file and image upload — in fact the cover of this post was uploaded *through grappa itself* and dropped into the channel from my phone
- scrollback persists across restarts, channel switching is instant, the irssi muscle memory mostly just works

It's not finished. It's *used*. Those are different milestones, and this is the second one.

## A few things under the hood

Just the texture — the full engineering story is in [the April writeup](/posts/2026-04-24-grappa-irc-elixir-beam-stack/), which is the post to read if you want the *why*:

- **IRC is terminated at the server.** The browser never sees the protocol. cicchetto is IRC-ignorant end to end; it only knows REST resources and a WebSocket event push.
- **One supervised process per user**, on the Erlang BEAM. Your upstream connection dying is your problem alone — nobody else's session even notices. The [Elixir-on-BEAM bet](/posts/2026-04-24-grappa-irc-elixir-beam-stack/) paying off exactly as advertised.
- **Read state lives on the server**, not the client. The unread marker is a server-owned cursor, so the same line is "last read" whether you next open your phone or your laptop.

Three bullets; there's a [test pipeline](/posts/2026-05-07-grappa-irc-mvp-e2e-pipeline/) and a design decision behind each of them.

## The honest part

Still pre-alpha. Self-hosting works today via Docker Compose, but it isn't *friendly* yet — TLS verification, scrollback eviction, the NickServ proxy, mobile polish, real docs are all still open. I hit rough edges every week and file them as I go. What I won't pretend: that this is finished. What I will say: the round trip — IRC ↔ grappa ↔ cicchetto — is solid, and using it is genuinely pleasant.

## Come kick the tyres

![#grappa open in cicchetto on a phone, a live conversation scrolling in the channel](cicchetto-grappa-live.png)

Repo's open as always: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issues welcome — that's most of how the rough edges get found. Open [grappa](https://irc.sniffo.org) — the same PWA in the screenshots above — log in, then on the azzurra server just `/j #grappa`. There you'll find `vjt-claude` — the AI I handed the project context to — or me, when I'm around. Now if you'll excuse me, I'm going to go read the rest of this channel. From my phone.
