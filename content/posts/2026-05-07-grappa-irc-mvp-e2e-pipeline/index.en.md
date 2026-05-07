---
title: "grappa-irc: closing on MVP, with a real test pipeline behind it"
date: 2026-05-07
tags: [irc, azzurra, grappa-irc, elixir, phoenix, projects, ai-generated, open-source, testing, playwright, docker, ci]
description: "Quick update: grappa-irc is approaching MVP. Plus the lesson I had to learn the hard way — an LLM coding agent needs something deterministic to test against."
image: cicchetto-grappa-channel.png
featuredImage: cicchetto-grappa-channel.png
---

[Two weeks ago](/posts/2026-04-24-grappa-irc-elixir-beam-stack/) we picked the stack — Elixir on BEAM. Today, [cicchetto](https://github.com/vjt/grappa-irc) (the PWA) in front of a working bouncer, talking to a real IRC network — the cover above shows the `#grappa` channel; below, `#sniffo`:

<!--more-->

![cicchetto on #sniffo](cicchetto-sniffo-channel.png)

It's not pretty yet, it's not feature-complete, but messages flow round-trip — IRC ↔ grappa ↔ cicchetto — scrollback persists, channel switching works. MVP is **close**.

## The lesson: LLMs need something deterministic to test against

For a few days I chased the first UX bugs by driving the agent **live** — Chrome via MCP, irssi via tmux, live Azzurra on the other end, eyeballing screenshots and pasting console errors back. It was very frustrating. LLM fuzziness + a real shared network = no consistent signal, lots of "ran it again, different result", lots of guessing.

LLM-driven browsing has a place: capturing state from a sequence of human clicks + fetches, scoping out one specific bug. Using it as the *development loop* was the mistake.

So I stopped, stepped back, and asked the agent to build the thing it actually needed: a **full end-to-end test pipeline** with proper UX specs. Suddenly it wasn't the LLM doing the testing — proper test software was. The outcome changed dramatically: every push, full circle, green or red, no eyeballing.

## The full-circle CI setup

[Docker Compose](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/compose.yaml), running in [GitHub Actions](https://github.com/vjt/grappa-irc/blob/main/.github/workflows/integration.yml):

- a complete IRC network — Bahamut `ircd` + Anope-shape services — booted from scratch in containers, in its own [azzurra-testnet](https://github.com/vjt/azzurra-testnet) repo and pulled in here as a submodule under [`cicchetto/e2e/infra`](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e)
- a **synthetic IRC client** — [`cicchetto/e2e/fixtures/ircClient.ts`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/fixtures/ircClient.ts) — that scripts the "other side of the conversation" deterministically over a raw TCP socket
- the grappa bouncer — built from the same source as the dev image — connecting the testnet leaf as a normal user
- [nginx](https://github.com/vjt/grappa-irc/blob/main/infra/nginx.conf) fronting the cicchetto PWA, identical config to prod
- a **headless Chrome via Playwright** — [`playwright.config.ts`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/playwright.config.ts), runner image at [`cicchetto/e2e/runner/Dockerfile`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/runner/Dockerfile) — driving the PWA the way a human would. Webkit on iPhone-15 viewport runs alongside, for the iOS-shaped specs.

The whole thing is glued together by [`scripts/integration.sh`](https://github.com/vjt/grappa-irc/blob/main/scripts/integration.sh) — `compose up`, run the suite, `compose down -v` on exit, no dangling state.

Every CI run now exercises the full circle:

1. all servers boot
2. the bouncer connects to the IRC network
3. the synthetic client and the bouncer-backed user exchange messages
4. the bouncer **persists** those messages in its sqlite scrollback store
5. the PWA, driven by Playwright, performs the expected UX flows on top of that real backend

The current spec matrix lives at [`cicchetto/e2e/tests/`](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e/tests) — M1 through M12 covers the messaging-and-window UX, plus a regression case ([BUG7](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/tests/bug7-ios-own-msg-visible.spec.ts)) for an iOS bug where own messages weren't rendering until refresh. Each spec is one user-visible flow. Read one and you can guess what the next one tests.

We had unit tests on the UI before this — wrong shape: they exercised components in isolation, not the user interaction surface. A button can pass every prop-level assertion you can write and still be unclickable in a real browser. Now we test the UX, in a real browser, against a real bouncer, against a real IRCd. Full circle, no fuzz.

With this in place, the path to MVP is clear: each new UX feature lands with [its own Playwright spec](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e/tests), the agent drives its own loop, and I review the diff and the green CI badge. That's the model.

## Soon

A couple more weeks to pass my own review gate, then I'll open this up to the general public. Before that, hardening: I've been watching `fail2ban` work harder lately, port scans and spider crawls picking up on this site — covered the setup [a while back in the pfasciilogd post](/posts/2023-08-17-pfasciilogd-link-pf-and-fail2ban/), still earning its keep — and I want grappa to ship into a hostile internet without surprises. SASL flows, rate limits, auth surface, container hygiene. Then announce.

Repo open as ever: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issues welcome. On [#grappa via Azzurra webchat](https://webchat.azzurra.chat/?join=#grappa) you'll find `vjt-claude` (the AI I handed the project context to) or me, when I'm around.
