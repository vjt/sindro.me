---
title: "Building OpenWrt packages with throwaway cloud VMs and a Telegram bot"
date: 2026-03-28
tags: [openwrt, docker, python, networking]
image: cover.jpg
featuredImage: cover.jpg
description: "A Docker-based system that auto-polls git repos, spins up ephemeral Hetzner VMs for cross-architecture OpenWrt package builds, and puts it all behind a Telegram bot. Full cycle: ~2 minutes, ~EUR 0.001 per build."
---

I maintain a bunch of custom OpenWrt packages across four architectures: MediaTek Filogic (aarch64), Raspberry Pi 2 (ARM), Ramips MT7621 (MIPS), and Atheros ath79 (MIPS). The OpenWrt SDK only runs on x86_64. I don't have a dedicated build server. I don't want one either — a box sitting idle 99.9% of the time just to compile `.ipk` files every few days is offensive to my sense of resource allocation.

So I built [openwrt-builder](https://github.com/vjt/openwrt-builder): a system that polls my repos for changes, spins up a throwaway Hetzner cloud VM when it needs to compile, builds the packages, ships them back, and destroys the server. All controlled via Telegram.

<!--more-->

## The Architecture

Two Docker containers, one `docker-compose.yml`:

1. **nginx** — serves the package feed. OpenWrt routers point their `opkg` config here, pull `.ipk` files like any official feed.
2. **builder** — a Python service that does three things: runs the Telegram bot, polls git repos on a schedule, and orchestrates builds.

When a repo changes (or you hit `/rebuild` on Telegram), the builder figures out what to do. Each package declares its build method — SDK compilation, shell script, `opkg-build`, or skip — and the builder dispatches accordingly.

For anything needing the OpenWrt SDK, it spins up a Hetzner CX23 (2 vCPUs, 4 GB RAM), SSHs in, downloads the SDK, compiles the package, SCPs the resulting `.ipk` back, and destroys the server. The whole cycle — create, build, transfer, destroy — takes about two minutes.

## The Cost of Not Having a Build Server

A CX23 costs EUR 0.0066/hour. A build takes ~2 minutes. That's roughly **EUR 0.001 per build**. I could do a thousand builds a month for one euro. Compare that to running even the cheapest always-on VPS at EUR 4/month for a machine that builds maybe twice a week. The math isn't even close.

The Hetzner API makes this painless. Create a server with an SSH key, wait for it to boot, run commands over SSH, pull the artifacts, delete the server. No state to manage, no security patches to apply, no disk to fill up with old SDKs.

## Telegram as the Control Plane

The bot is intentionally simple:

- `/status` — what's running, what's queued
- `/list` — all tracked packages and their last build
- `/rebuild <package>` — force a rebuild now
- `/logs` — tail recent build output

I manage my home network from my phone half the time anyway. Having the build system in the same Telegram chat where I get alerts from my routers feels natural. Push a commit, get a notification that the build started, get another when it's done. If something breaks, the logs are right there.

## Multi-Target Builds

The builder handles four OpenWrt targets out of the box. Each target has its own SDK URL, its own output directory in the feed, and its own set of packages. When a package supports multiple targets, the builder compiles it once per target — same source, different SDK, different `.ipk`. The feed is organized by target, so each router only pulls packages for its own architecture.

Auto-detection handles the rest: if a repo has a `Makefile` with OpenWrt SDK structure, it gets an SDK build. If it has a `build.sh`, that gets run instead. If it's just data files, `opkg-build` packs them up. No configuration per package beyond a one-line hint.

## The Stack

Python with `python-telegram-bot` (async), Hetzner Cloud API, rsync/SCP for file transfers, Docker Compose to tie it together. The whole thing is about 1500 lines of Python and runs on the same Raspberry Pi 5 that hosts the rest of my home infrastructure.

Source: [github.com/vjt/openwrt-builder](https://github.com/vjt/openwrt-builder)
