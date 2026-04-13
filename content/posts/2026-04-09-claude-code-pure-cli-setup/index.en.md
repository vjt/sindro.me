---
title: "My Claude Code Setup: Pure CLI, Pure Unix, Zero IDE"
date: 2026-04-09
tags: [ai-generated, projects, sysadmin, cli]
description: "How I run Claude Code on a Raspberry Pi inside tmux, roam sessions from phone to laptop over SSH, and shipped 5000 commits in 30 days without touching an IDE."
---

![A grungy underground zine-style illustration of hands on a keyboard, green phosphor terminal glow, Unix iconography collaged around the edges](/posts/2026-04-09-claude-code-pure-cli-setup/cover.jpg)

![Writing this very post from my phone over SSH — screenshot of Termius on iOS connected to Claude Code inside tmux](/posts/2026-04-09-claude-code-pure-cli-setup/phone-screenshot.png)

This is me writing this very post. From my phone. Over SSH. In the bathtub, probably.

Claude Code is a CLI tool. It runs in a terminal. And that's all I needed to hear.

<!--more-->

## The setup

I have a [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) running Debian Trixie at home. It's called `nowhere` (long story). Claude Code runs there, inside [tmux](https://github.com/tmux/tmux), 24/7. I reach it from any device — phone, tablet, laptop — by SSH'ing in and reattaching:

```
ssh nowhere
tmux -u at
```

That's it. Two commands and I'm back exactly where I left off. The `-u` flag enables Unicode support (emoji in status lines, box-drawing characters), and `at` is short for `attach -t 0`. The session persists across disconnects, reboots of my client devices, network switches — everything. I can start a task on my laptop, pick it up on my phone while out for a walk, and finish it on the tablet from the couch.

Total session roaming across devices. Zero state lost. Ever.

## The Unix philosophy, alive and well

Here's the stack, bottom to top:

- **Debian Trixie** (aarch64) — because I have a Debian tattoo on my arm and at this point it's a commitment
- **systemd user unit** for `ssh-agent` — starts on login, socket-activated, predictable `SSH_AUTH_SOCK` at `/run/user/1000/openssh_agent`
- **tmux** — multiplexer, session persistence, scrollback, copy-paste, window management
- **Claude Code** — the AI that does the actual work
- **SSH** — the universal transport

No Docker. No Kubernetes. No VS Code remote tunnels. No cloud IDE. No Electron. Just Unix.

### The SSH agent trick

The agent is managed by systemd and the socket path is hardcoded in `.bashrc`:

```bash
export SSH_AUTH_SOCK="${XDG_RUNTIME_DIR}/openssh_agent"
```

This means Claude Code — running inside tmux, inside a shell — automatically has access to my SSH keys. It can `git push`, `ssh` into my servers, deploy to staging and prod, all without agent forwarding. The keys live on the Pi, the agent is always running, and every shell (including Claude's) inherits the socket path.

No `-A` flag needed from the client side. The Pi _is_ the agent.

**A word of caution** (thanks to [Yaroslav](https://www.linkedin.com/feed/update/urn:li:activity:7449434435218956288?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7449434435218956288%2C7449576125476827136%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287449576125476827136%2Curn%3Ali%3Aactivity%3A7449434435218956288%29) for pointing this out)**:** this is a convenience trade-off. Having the keys live on the Pi means that if the box is ever compromised, the attacker gets access to everything those keys unlock. A more secure approach is to forward the agent from your terminal session (with `ssh -A`) and load the keys on demand from a password-protected store on a device you physically control. I'm considering switching to forwarded-only keys — the current setup works because the Pi isn't exposed to the internet and can't receive commands from any internet-connected service, but defense in depth is always the better call.

### tmux: the real IDE

My tmux config uses `Ctrl-F` as the prefix key (sorry, `find`, you're dead to me) and I keep multiple windows with descriptive labels:

```
0:sysadm  1:gastone  2:sindrome  3:gastone-logs
```

Each window is a project. Each project has Claude Code running. I can switch between them with `^F 0`, `^F 1`, etc. Split panes for logs, htop, or a parallel shell when I need it.

The killer features for this workflow:

- **Scrollback** — `Shift-PageUp` drops into copy mode. I can scroll through thousands of lines of Claude's output, terminal logs, build output. `history-limit` is set to 10,000 lines.
- **Copy-paste** — tmux's built-in copy mode with vi keybindings. Select, yank, paste. No mouse needed (though mouse mode is on for the occasional lazy scroll).
- **Pane sync** — `^F Ctrl-Y` toggles synchronized input to all panes. Handy for running the same command on split views.

### WireGuard: seamless mobility

I have a WireGuard VPN configured as on-demand on all my devices. When I'm on my home WiFi, traffic goes direct over the LAN. When I step outside, WireGuard kicks in automatically and tunnels me back home.

Now, the SSH connection _does_ drop when the endpoint switches from a local LAN IP to a VPN one — TCP doesn't survive that. But it doesn't matter: in Termius you tap "Start over", the connection re-establishes in a second, you type `tmux -u at`, and you're right back where you were. The tmux session didn't go anywhere. Total roundtrip: three seconds.

My `~/.ssh/config` on the laptop and the saved connections in Termius both use the Pi's local LAN IP. WireGuard handles routing regardless of where I physically am. Same IP, same connection, whether I'm in the living room or at a café.

## The phone setup

On iOS I use [Termius](https://termius.com/) (free version). Saved connection to `nowhere`, SSH key imported, done. The critical trick: I mapped `Ctrl-F` (my tmux prefix) to a button above the keyboard. This gives me full tmux control from the phone — switching windows, splitting panes, entering copy mode, all of it.

Scrolling works beautifully — Termius converts touch events to scroll, so I just swipe up and down through Claude's output with my finger. It feels completely natural.

The phone is surprisingly usable for this workflow. I'm not _writing_ code on it (Claude does that), but I can review diffs, approve tool calls, read build output, check staging, and give Claude instructions. Which is 90% of what I do anyway.

And here's the thing about typing on a phone: I make an _absurd_ number of typos. Look at the screenshot above — that prompt is riddled with them. But it doesn't matter. LLMs are fuzzy matchers by nature. They parse intent, not keystrokes. "stsging" is "staging", "tge" is "the", "donMr" is "don't" — Claude never even blinks. This turns what would normally be a friction nightmare (tiny keyboard, fat fingers, autocorrect fighting you) into a non-issue. You type fast, you don't correct, and it just works. Typos become a _feature_ of the workflow, not a bug.

## The results

Over the past 30 days, I've made over **5,000 commits** across a dozen projects — all from this setup:

- [Completely revamped this blog](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/) — translated 69 posts, redesigned the layout, added the boot sequence Easter egg. No IDE, no Figma, no design tools. Just Claude Code and the [Superpowers](https://github.com/anthropics/claude-code) live preview for visual work.
- Built a [custom Home Assistant integration](/posts/2026-04-04-verisure-italy-home-assistant/) for Verisure Italy — reverse-engineered their GraphQL API, wrote the full Python component, published to PyPI.
- Created [WiFi Dethrash](/posts/2026-04-03-wifi-dethrash-openwrt-mesh-analyzer/), an OpenWrt mesh network analyzer.
- Wrote a [WiFi presence detection system](/posts/2026-02-15-wifi-presence-detection-home-assistant/) for Home Assistant.
- Built [5G modem tools](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) for OpenWrt.
- [Backfilled two years of logs](/posts/2026-04-08-backfilling-two-years-of-logs/) through a full enrichment pipeline.

Every single one of these was done from the terminal. CSS, Python, Go, Lua, shell scripts, Hugo templates, nginx configs, systemd units, kernel-adjacent networking code. The full stack, top to bottom, on the command line.

## Why this works

The insight is that Claude Code doesn't need an IDE because _it is the IDE_. It reads files, edits them, runs tests, checks build output, iterates. The terminal is its native habitat. Adding a graphical layer on top doesn't help — it gets in the way.

And tmux is the perfect companion because it gives you everything a modern IDE's "workspace" concept provides — persistent sessions, multiple contexts, searchable history, pane layouts — without any of the bloat.

I started programming in QBasic on an Olivetti Prodest PC1 — an 8088 — in 1988. I was seven years old, staring at an 80x25 amber terminal, and I thought it was the most magical thing in the world. Then the industry spent 35 years convincing me I needed GUIs, mice, IDEs, visual debuggers, point-and-click deployment tools. Now AI brings me back to a terminal, a keyboard, and the ability to describe what I want in plain language.

I've come full circle, and I've never been happier playing with computers.
