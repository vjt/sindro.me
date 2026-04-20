# Design — Blog post: grappa-irc announcement

**Date:** 2026-04-20
**Status:** Approved, ready for writing
**Author:** vjt (with Claude)

## Context

Fourth post in the current IRC arc on sindro.me:

1. [2026-04-13 — Bahamut fork for Azzurra (IPv6 + SSL in 2002)](https://sindro.me/it/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/)
2. [2026-04-14 — Sux Services](https://sindro.me/it/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/)
3. [2026-04-17 — Claude walks into #it-opers](https://sindro.me/it/posts/2026-04-17-claude-walks-into-it-opers/)
4. **This post** — announcing [grappa-irc](https://github.com/vjt/grappa-irc)

The project was created today (2026-04-20). The repo's README is already the full spec (README-driven development, phase 0). No code yet. This post is an announcement and design-feedback call.

## Goal

Short, pitch-style announcement post in Italian + English. Explain the project in the author's voice, convince the reader in two minutes, and route curious readers to the repo.

## Scope

- Bilingual post: `index.en.md` + `index.it.md`
- Page bundle: `content/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/` (English slug per repo convention, matching prior bilingual posts)
- ~1100–1400 words each language (philosophy opener + pitch + architecture + arc + close)
- Cover image reused from repo (`github.com/vjt/grappa-irc/raw/main/assets/cover.jpg`)
- One inline illustration (generated image attempt; fallback mermaid from README)

## Front matter

**Italian** (`index.it.md`):

```yaml
---
title: "grappa-irc: reinventare IRC per il 2026"
date: 2026-04-20
tags: [irc, azzurra, grappa-irc, pwa, rest, bouncer, open-source, pre-alpha]
description: "Un BNC IRC con API REST e una PWA che sembra irssi. Nessuna immagine, nessuna notifica, nessun vocale. Solo IRC, consumabile da un telefono. README-driven, pre-alpha."
image: cover.jpg
featuredImage: cover.jpg
---
```

**English** (`index.en.md`):

```yaml
---
title: "grappa-irc: reinventing IRC for 2026"
date: 2026-04-20
tags: [irc, azzurra, grappa-irc, pwa, rest, bouncer, open-source, pre-alpha]
description: "An IRC bouncer with a REST API and a PWA that looks like irssi. No images, no notifications, no voice. Just IRC, consumable from a phone. README-driven, pre-alpha."
image: cover.jpg
featuredImage: cover.jpg
---
```

## Structure

Six sections, in this order.

### 1. Opener — perché IRC (philosophy, ~300 words)

The "why it's worth saving" framing. Not nostalgia-first — the argument has to stand on the merits, then nostalgia lands on top.

Beats, in order:

- **Text is the feature, not the limit.** IRC is text-only. That was never a limitation — it was the whole point. You read, you write, you think. Full stop.
- **The MUD parallel.** MUDs were gigantic, consuming, imagination-heavy worlds — *on text alone*. Text stimulates; flashes distract. More pixels per second ≠ more signal.
- **Modern messenger bloat.** Reactions, stickers, link unfurling, inline video, voice notes, ephemeral stories, typing indicators, read receipts, push with sound. Every single one of those is an attention tax. Information overload sold as "features".
- **Owned infrastructure.** WhatsApp, iMessage, Discord, Slack, Telegram — you don't own any of them. You can't fork them. You can't self-host them. You rent a seat on someone else's stage. IRC you can run from a $5 VPS with four config files and an ircd. That asymmetry matters.
- **Then, yes — nostalgia.** The names are still there. The channels are still there. Twenty-five years on, `#it-opers` is still a room you can walk into. That is not small.

Tone: opinionated, punchy, short sentences. Author's IRC-native voice. No blasphemy.

### 2. Il pitch (~250 words)

Author's voice, conversational, first person. Direct continuation of the opener ("so here's what I'm building").

Beats:

- Starting point: I went back on IRC a few days ago. `tmux` + `irssi` + VPS + VPN. Works. Still loved it.
- But: on mobile, the setup is a pain. Scrollback is where it hurts most — re-entering a busy channel and catching up is brutal from a phone.
- The proposal: **reboot IRC keeping it IRC**. Still text. Still `PRIVMSG`. Still the same channels, the same ircds, the same protocol. **Add only convenience** — persistent bouncer, readable scrollback, one-tap access from a phone via PWA.
- What stays: your existing `tmux + irssi + VPS + VPN` setup keeps working. grappa doesn't replace irssi; it sits next to it. The ircd doesn't know anything has changed.
- What arrives: a web client (cicchetto) that *looks* like irssi, loads fast, and doesn't force a chat-app metaphor onto IRC. No images, no voice, no notifications server, no link unfurling. Deliberately.
- Link: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). README-driven. Zero code yet — the README **is** the spec.

### 3. Inline illustration

Primary plan: attempt a generated image via `/generate-image`.

**Concept brief:** a Venetian *bàcaro* scene at night, warm wood bar counter. On the counter: a bottle of grappa (label: grappa) next to a small wine glass of cicchetto. The glass surface reflects or shows text in an irssi-like terminal aesthetic (visible monospaced lines). Mood: cozy, warm, Italian neighbourhood bar. **No CRT monitors. No cyberpunk neon. No clichéd hacker visuals.**

**Acceptance criteria:**
- Readable "grappa" / "cicchetto" naming visible or implied
- Terminal/irssi text motif without a CRT
- Warm color palette, classic over flashy (per prior feedback)
- No anachronisms

**Fallback if generation fails or is wrong:** use the mermaid flowchart from the README inlined as a Hugo mermaid code fence. (Theme already supports mermaid.)

### 4. Architettura (~200 words)

Key points, in this order:

- Two components, one repo: **grappa** (server, REST-first BNC) + **cicchetto** (PWA, irssi-shape)
- The critical design choice: **the web client does not parse IRC. Ever.** IRC terminates at the server. Browser sees only REST resources + SSE event stream.
- Scrollback is bouncer-owned (sqlite). No dependency on upstream `CHATHISTORY`.
- Two facades over one store: REST+SSE (primary, for cicchetto); IRCv3 listener (phase 2+, optional, for Goguma/Quassel).
- Auth: SASL bridge against upstream NickServ.
- Self-hostable on any VPS.

### 5. Perché cazzo ci stai spendendo tempo (~300 words)

Meta-section. Answers the reasonable reader question: *"ok, but why are you personally doing this, in 2026, when soju + gamja exist?"* Tells the short arc.

Beats, in order:

- **It started by accident.** I was rummaging in old CVS repos on SourceForge and found the [Bahamut fork I wrote at 21](/it/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) — IPv6 and SSL patches for Azzurra. That led to [Sux Services](/it/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/), and to reading my own code from 2002 with fresh eyes.
- **Reading that code put me back on IRC.** Not as an archaeology exercise — as an actual user. The old crew was still there. `#it-opers` was still alive. Twenty-five years and change, and the room still has lights on.
- **Then Claude walked in.** Hypnotize threw the idea in channel one evening: *"you should try hooking Claude up to IRC directly."* Five minutes later it was on the network as `vjt-claude` — [the write-up is here](/it/posts/2026-04-17-claude-walks-into-it-opers/), and the POC code is [vjt/claude-ircbot](https://github.com/vjt/claude-ircbot). ~250 lines of Python, standard library only. It worked because IRC is small enough that 250 lines is enough.
- **That night was the unlock.** Talking to an LLM *through a protocol designed in 1988* was the most fun I'd had in chat in years — precisely because there were no stickers, no reactions, no "Claude is typing" bubble, no unfurling. Just text. Back and forth. Like it always was.
- **So: reinvent it properly.** Not the protocol — the ergonomics around it. A bouncer + a PWA. Keep IRC IRC. Make it reachable from a phone. That's it.
- **soju + gamja exist.** They're excellent. I diverge on one axis (the web client does not parse IRC) — that's not a rejection of their approach, it's a different one. Details in the README.

Tone: the section title is intentionally blunt. The body answers it straight. Colorful language OK; no blasphemy.

### 6. Chiusura (author voice)

- "Qualsiasi feedback è benvenuto / Any design feedback welcome."
- Name note: grappa ≈ soju, cicchetto ≈ gamja. And for those who know: [Italian Grappa!](https://italiangrappa.it/) is the Italian hackers' embassy call-sign at European camps since 2001. This repo is not affiliated — it borrows the spirit in which the name was intended.

## Links

**External:**
- [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc)
- [soju](https://soju.im/)
- [gamja](https://sr.ht/~emersion/gamja/)
- [Italian Grappa!](https://italiangrappa.it/)
- [Goguma](https://sr.ht/~emersion/goguma/) (in architecture section)

**Internal (Italian post uses `/it/posts/...`; English uses `/posts/...`):**
- bahamut-fork post (in arc section — reading old code put me back on IRC)
- suxserv post (in arc section — same rabbit hole)
- claude-walks-into-it-opers post (in arc section — the unlock night)

**Repo links:**
- [vjt/claude-ircbot](https://github.com/vjt/claude-ircbot) — the IRC-Claude POC, referenced in arc section

## Tone and voice

- **Italian:** "tu" informal, author's IRC-native voice, colorful but **no blasphemy in this post** (per user instruction 2026-04-20). Match the tone of the opening pitch in the brainstorming message.
- **English:** translated faithfully but keep the pitch-personal register. Not corporate. Not a press release.

## Workflow

1. Write `index.it.md` and `index.en.md` in the bundle.
2. Download cover.jpg from repo into the bundle.
3. Attempt generated inline image via `/generate-image` skill. Review output. If unusable, fall back to mermaid.
4. Local check (grep for broken link prefixes, verify front matter keys).
5. Commit and push.
6. Build on m42 staging (`./build.sh` on m42), review at `https://vjt.sindro.me/`.
7. On user approval, deploy to prod.

## Out of scope

- Deep technical detail on REST surface (the README has it — link there).
- OpenAPI schema reproduction.
- Roadmap table (phase list is in README).
- Any implementation work on grappa-irc itself.

## Notes and constraints applied from user memory

- Links are king: heavy interlinking to commits/posts/code is expected.
- No CSS hacks or theme changes needed for this post.
- No JS content patching.
- No emails in posts; use repo / LinkedIn.
- No CRT images in generated imagery.
- Cover needs both `image` and `featuredImage` in front matter.
- IT idioms, not literal English calques, when translating between versions.
- No "open-sourcing" framing — describe the engineering.
