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
- ~750–900 words each language. Tight. Each section lean. No section padding just because there's room.
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

### 1. Opener — perché IRC (~180 words)

The "why it's worth saving" framing. Punchy, not preachy. Not nostalgia-first — argument on merits, nostalgia lands on top.

Beats, one-two lines each:

- **Text is the feature, not the limit.** IRC is text-only. Never a limitation — the whole point.
- **MUD parallel.** Giant imagined worlds on text alone. Flashes distract; text stimulates.
- **Modern messenger bloat.** Reactions, stickers, unfurling, voice notes, typing indicators, push-with-sound. Attention tax sold as features.
- **Owned infrastructure.** WhatsApp/iMessage/Discord/Slack aren't yours. Can't fork, can't self-host. IRC runs on a $5 VPS. That asymmetry matters.
- **Then nostalgia.** `#it-opers` is still alive after twenty-five years. Not small.

Tone: opinionated, short sentences. No blasphemy.

### 2. Il pitch (~180 words)

Author's voice, direct continuation of the opener.

Beats:

- I went back on IRC a few days ago. `tmux` + `irssi` + VPS + VPN. Still loved it.
- But: on mobile, scrollback is brutal. Re-entering a busy channel from a phone is painful.
- **Reboot IRC keeping it IRC.** Still text, still `PRIVMSG`, same channels, same ircds. **Add only convenience.**
- Your `tmux + irssi + VPS + VPN` setup keeps working. grappa sits next to it. The ircd doesn't know anything changed.
- On top: **cicchetto** — a PWA that *looks* like irssi. Loads fast. No images, no voice, no push server, no unfurling. Deliberately.
- [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). README-driven. Zero code yet — README **is** the spec.

### 3. Inline illustration

Primary plan: attempt a generated image via `/generate-image`.

**Concept brief:** a Venetian *bàcaro* scene at night, warm wood bar counter. On the counter: a bottle of grappa (label: grappa) next to a small wine glass of cicchetto. The glass surface reflects or shows text in an irssi-like terminal aesthetic (visible monospaced lines). Mood: cozy, warm, Italian neighbourhood bar. **No CRT monitors. No cyberpunk neon. No clichéd hacker visuals.**

**Acceptance criteria:**
- Readable "grappa" / "cicchetto" naming visible or implied
- Terminal/irssi text motif without a CRT
- Warm color palette, classic over flashy (per prior feedback)
- No anachronisms

**Fallback if generation fails or is wrong:** use the mermaid flowchart from the README inlined as a Hugo mermaid code fence. (Theme already supports mermaid.)

### 4. Architettura (~150 words)

Lean. No bullet padding. Key points:

- Two components: **grappa** (server, REST-first BNC) + **cicchetto** (PWA, irssi-shape).
- Core choice: **the web client does not parse IRC. Ever.** IRC terminates at the server. Browser sees REST + SSE.
- Scrollback bouncer-owned (sqlite). No upstream `CHATHISTORY` required.
- Two facades, one store: REST+SSE (primary); IRCv3 listener (phase 2+, optional, for Goguma/Quassel).
- Auth: SASL bridge against upstream NickServ. Self-hostable on any VPS.

### 5. Perché cazzo ci stai spendendo tempo (~200 words)

Meta-section, short. Answers the reader question: *"ok, but why you, in 2026, when soju + gamja exist?"*

Beats, tight:

- **Started by accident.** Rummaging in old CVS I found my [Bahamut fork at 21](/it/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/), then [Sux Services](/it/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/). Reading my 2002 code put me back on IRC as a user.
- **The old crew was still there.** `#it-opers` still alive. Twenty-five years, lights on.
- **Claude walked in.** Hypnotize suggested it in channel one evening. Five minutes later `vjt-claude` was on the network — [write-up](/it/posts/2026-04-17-claude-walks-into-it-opers/), POC code [vjt/claude-ircbot](https://github.com/vjt/claude-ircbot), ~250 lines of Python stdlib. That night was the unlock: chatting with an LLM over a 1988 protocol was the most fun I'd had in chat in years. Precisely because no stickers, no reactions, no typing bubble. Just text.
- **So: reinvent the ergonomics, not the protocol.** soju + gamja exist and are excellent — I diverge on one axis (no IRC parsing in the browser). Details in the README.

Tone: blunt title, straight body. Colorful OK; no blasphemy.

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
