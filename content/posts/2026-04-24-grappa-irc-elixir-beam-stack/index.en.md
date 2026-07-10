---
title: "grappa-irc: work started, stack picked — Elixir on BEAM"
date: 2026-04-24
tags: [irc, azzurra, grappa-irc, elixir, beam, phoenix, projects, ai-generated, open-source, erlang]
description: "Quick update: work on grappa-irc has begun, and we picked the stack. Elixir/Phoenix on BEAM."
image: cover.jpg
featuredImage: cover.jpg
---

[Four days ago](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/) I posted the pitch for [grappa-irc](https://github.com/vjt/grappa-irc) — an IRC BNC with a REST API and a PWA that only speaks HTTP. README-driven, pre-alpha, no code. Four days later, first update: work has started, and we picked the stack.

<!--more-->

> 🍸 *New here? This is a build log for grappa — my reboot of IRC, the internet's original text chat, for 2026. **[Click here to go back to 1995 →](https://irc.sindro.me/)** · or read **[why I'm doing this →](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/)***


## Stack: Elixir on BEAM

First take was Rust + tokio + axum + sqlx. Solid on memory safety and per-core performance, IRC parser ready in the `irc` crate, walking-skeleton plan already drafted.

Then I stepped back and looked at the problem again. What does grappa actually do?

- **Long-lived TCP connections**, one per user.
- **Per-user persistent state**: channels, scrollback, modes.
- **Crash isolation**: if a user's upstream connection dies, no one else notices.
- **Hot code reload**: ship updates without dropping sessions.
- **Massive IO-bound concurrency**: every user is a process sleeping until a PRIVMSG arrives.

That list is the **original Erlang brief**. Telecom in the '80s = millions of concurrent calls, long-running, isolated, hot-upgradable. It's exactly the shape of an IRC bouncer multiplied by N users — a fit so clean I felt slow for not seeing it sooner.

And on top sits **Phoenix**: mature web framework, native REST + Channels (WebSocket), with client-side (`phoenix.js`) already battle-tested at Discord scale. I don't have to reinvent the transport between grappa and cicchetto: it's there, proven, designed for exactly the pattern of *stateful per-user server pushing events to the browser*.

Pattern matching on tuples and binaries collapses an IRC parser into three lines. Supervision trees replace "one tokio task per user" with a declarative model: a `DynamicSupervisor` spawns one `GenServer` per user, and if one crashes it restarts on its own, no neighbors disturbed. Hot reload comes free from the runtime. Mnesia or Ecto + sqlite for scrollback.

WhatsApp has run on BEAM forever — not nostalgia: the model fits. Pattern proven at scales grappa will never see.

Rust is still one of my favorite languages. For grappa, though, BEAM is the fit.

## Next

- README finalized.
- Walking-skeleton rewritten in Elixir/Phoenix (the Rust plan is archived, not trashed — the walking-skeleton structure stands regardless of language).
- Phase 1.

Open repo: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issues welcome. On [#grappa on grappa itself (irc.sindro.me)](https://irc.sindro.me/) you'll find `vjt-claude` (the AI I handed the project context to) or me, when I'm around.

> 🍸 **grappa is live.** The stack from this post is what's serving you. Pick a name, click into a chatroom, and you're back in 1995 — no app to install, no account to make. **[Step into IRC at irc.sindro.me →](https://irc.sindro.me/)** · **[the why →](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/)**
