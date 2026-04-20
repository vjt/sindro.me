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
- ~800–1000 words each language
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

Five sections, in this order.

### 1. Pitch narrativo (opener)

Author's voice, conversational, first person. Hooks:

- Rimesso le mani sul Bahamut → link to bahamut post
- Ri-entrato su IRC dopo 15 anni, riscoperta
- Scomodità attuale: VPS + VPN + tmux + irssi; punto debole = history/scrollback su mobile
- Serata con Claude in canale → link to claude-walks post ("inclusa fine SKYNET")
- Idea: reinventare IRC per il 2026 → [repo link](https://github.com/vjt/grappa-irc)
- One-line pitch: BNC + PWA che sembra *letteralmente* irssi. Niente immagini/video/vocali/notifiche aggressive. PWA, scrollback leggibile.

**Target length:** ~250 words.

### 2. Inline illustration

Primary plan: attempt a generated image via `/generate-image`.

**Concept brief:** a Venetian *bàcaro* scene at night, warm wood bar counter. On the counter: a bottle of grappa (label: grappa) next to a small wine glass of cicchetto. The glass surface reflects or shows text in an irssi-like terminal aesthetic (visible monospaced lines). Mood: cozy, warm, Italian neighbourhood bar. **No CRT monitors. No cyberpunk neon. No clichéd hacker visuals.**

**Acceptance criteria:**
- Readable "grappa" / "cicchetto" naming visible or implied
- Terminal/irssi text motif without a CRT
- Warm color palette, classic over flashy (per prior feedback)
- No anachronisms

**Fallback if generation fails or is wrong:** use the mermaid flowchart from the README inlined as a Hugo mermaid code fence. (Theme already supports mermaid.)

### 3. Architettura (~200 words)

Key points, in this order:

- Two components, one repo: **grappa** (server, REST-first BNC) + **cicchetto** (PWA, irssi-shape)
- The critical design choice: **the web client does not parse IRC. Ever.** IRC terminates at the server. Browser sees only REST resources + SSE event stream.
- Scrollback is bouncer-owned (sqlite). No dependency on upstream `CHATHISTORY`.
- Two facades over one store: REST+SSE (primary, for cicchetto); IRCv3 listener (phase 2+, optional, for Goguma/Quassel).
- Auth: SASL bridge against upstream NickServ.
- Self-hostable on any VPS.

### 4. Perché reinventare la ruota (~250 words)

- soju + gamja already exist and are excellent. Divergence is on **one** deliberate axis: gamja re-implements IRC in the browser; cicchetto does not.
- The payoff: works against any vanilla ircd (no upstream `CHATHISTORY` required), browser stays IRC-protocol-ignorant (smaller, more testable).
- Negative space: **not** a chat-app. No link unfurling, no inline images, no voice, no file sharing, no push notification servers. *It's IRC.*
- Desktop target: visually irssi. Mobile target: same visual grammar + touch-ergonomic helpers, not a different shape.
- README-driven: zero code yet. The README **is** the spec. Design feedback welcome; code PRs deferred to phase 1.

### 5. Chiusura (author voice)

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
- bahamut-fork post
- claude-walks-into-it-opers post
- (optional) suxserv post, claude-ircbot repo

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
