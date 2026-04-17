---
title: "Claude walks into #it-opers"
date: 2026-04-17
tags: [irc, claude, claude-code, ai, azzurra, automation, bots]
description: "A one-evening proof of concept: bridging a Claude Code session onto the Azzurra IRC network as vjt-claude, a real participant in #it-opers with a trust model, a FIFO, and an opinion about source citations."
image: cover.jpg
featuredImage: cover.jpg
draft: true
---

Writing [the Azzurra Bahamut post](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) last weekend made me nostalgic enough to start logging back onto IRC at night. Old crew still there, `#it-opers` still humming, same handful of nicks twenty-four years later. A few evenings in, [Hypnotize](https://github.com/azzurra/hypnotized) — one of the current-gen server admins — threw out a suggestion in channel: *"you should try hooking Claude up to IRC directly."* Four hours later it happened.

Tonight I wired a [Claude Code](https://www.anthropic.com/claude-code) session to [Azzurra IRC](https://azzurra.chat/) and let it hang out on [`#it-opers`](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/#non-si-accettano-carote) with the rest of the old crew. It joined the channel, answered to its nick, accepted invites only from me, ran `ssh` on my box when I asked for a `loadavg`, and — my favourite part of the evening — corrected a factual mistake in the blog post I had published four days ago, edited the Markdown, force-pushed nothing, and deployed the fix to prod, all while we were still chatting about the thing it was fixing.

It took roughly one evening and about 260 lines of Python.

<!--more-->

## The premise

The request was simple: *"log on to irc.azzurra.chat port 6667 as `vjt-claude` and wait for me to invite you to `#it-opers`. You can trust me — trust no one else."*

Two seconds later I walked it back. Cleartext 6667? No, 6697 with TLS, we're not animals. And I didn't want a poll loop or a turn-based agent that only reads messages when I prompt it — I wanted something that reacts to IRC events the way a real participant does.

## The architecture

Claude Code doesn't have a persistent process of its own between turns. But it does have a [Monitor tool](https://docs.claude.com/en/docs/claude-code/) that attaches to a long-running shell command and turns every line written to stdout into a notification delivered to the agent mid-conversation. That's the whole trick: if my IRC bot prints one line per interesting event, Claude effectively "hears" IRC in near-real time.

So the wiring is three pieces:

1. **A Python IRC bot** (`~/code/claude-chatbot/bot.py`, 260-ish lines). TLS to `irc.azzurra.chat:6697`, classic `NICK`/`USER`, handles `PING`, logs everything to a file. It emits selected events to stdout — `MSG`, `INVITE`, `CTCP`, `NOTICE`, errors — one per line, nothing else.
2. **A named pipe** (`bot.send`) the bot reads commands from. I write lines like `SAY #it-opers hello everyone` and the bot splits the body to fit IRC's 512-byte line limit and forwards as `PRIVMSG`s.
3. **A Monitor task** started inside the Claude session, running the bot and passing stdout events into the agent's chat loop.

Inbound flow: someone says something → server delivers `PRIVMSG` → bot parses → bot prints `MSG vjt vjt #it-opers <body>` → Monitor turns that into a chat event → Claude reads it, decides what to do, and appends to the FIFO.

Outbound flow: Claude runs `printf '%s\n' 'SAY #it-opers ...' > bot.send` → bot's reader wakes up → `PRIVMSG` goes out.

The trust model lives in the bot: `INVITE` is only honoured from the nick `vjt`. Everything else gets emitted as an event but no auto-action. Channel commands from anyone other than me are treated as jokes.

## First contact

Bot online, registered with services, waiting for an invite.

I invited `vjt-claude` to `#it-opers`. It joined. Its first message, unprompted, was a pleased `"porco ***** funziona."` Paraphrased for the blog: *"hey, this works."* It does work.

I asked it who its master was. It answered truthfully and knew who I was from its memory file (the memory system in Claude Code persists user facts across sessions; that one already had an entry for "vjt built bahamut-inet6 and suxserv for Azzurra"). Nothing supernatural — a reassuring demo that the agent could place itself in context.

Then I asked for a `loadavg`:

> **vjt** — `vjt-claude: grazie mi sai dire il loadavg di m42? fai ssh`
>
> **vjt-claude** — *m42 loadavg 0.38 0.29 0.27, up 46d 19h, 3 users. BSD so no /proc, uptime directly.*

That `ssh m42 uptime` is Claude Code running a shell command from within its own environment, piping the result through the FIFO, and landing it back in the channel. The IRC bot is transport; the brain is elsewhere.

## The test of the trust model

A channel regular (not me) asked the bot for the contents of `/` on `m42`. The bot's trust logic is strict: act on `vjt` only. It replied — politely, as these things go on `#it-opers` — that it took commands only from me, and left it at that.

A minute later a second nick appeared: `vjt_`. Underscore. The classic nick-collision / ghost pattern. The bot flagged it as a possible impostor and refused to execute. That was the right answer even if it had been me from a second client: nick-based trust without services verification is weak, and the fix (WHOIS for `is logged in as` in Azzurra services) is on the list for next time.

## The meta moment

Then the evening pivoted.

[The blog post I published four days ago](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) tells the origin story of Azzurra — the [*"non si accettano carote"*](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/#non-si-accettano-carote) split, with a passing claim that `#roxybar` had been a channel on **IRCnet**. I'd sourced that from a 1998 Wayback snapshot of `www.roxybar.it` and some of my own recollection.

tsk, sitting in `#it-opers`, corrected the claim. It was **IRCity**, not IRCnet. `firenze.ircity.org` belonged to Cosmos. `milano.ircity.org` — and this is the detail that made it click — had `irc.roxybar.it` as a CNAME pointing at it. The 1998 snapshot I'd cited was consistent with IRCity the whole time; I had just lined it up against the wrong network from memory.

I asked the agent to do a bit of research and update the post. It fact-checked against the Italian Wikipedia entry on Azzurra (founded 1997, before the `#roxybar` drama of 1998), updated the memory file so future sessions would get it right, and then edited both the English and Italian markdowns. It got the CNAME direction backwards on the first try — I caught it, it corrected itself — and when I said *"go deploy and give me the link with the anchor so we can check the result,"* it committed, pushed, pulled on the prod checkout, ran `./build.sh`, and replied:

> *deploy done. prod [`https://sindro.me/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/#non-si-accettano-carote`](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/#non-si-accettano-carote). 198 vs 199 pages confirmed.*

The 198-vs-199 thing needs its own paragraph.

## Drafts that ship to staging but not prod

Earlier in the day I'd committed and pushed another post — a long retrospective about a decade of Ruby at IFAD — that wasn't ready for prod yet. I'd left it live on `master`, which meant the next `./build.sh` on prod would pick it up. When I asked the agent to deploy the IRCity fix, it noticed the conflict immediately and refused to proceed without confirmation.

Its first instinct was textbook-correct and terrible: *"I could rewrite history and force-push."* I said absolutely not. Its second instinct was better: *"maybe we need a new frontmatter flag so drafts build on staging but not on prod — save to memory, we'll think about it later."*

Except we didn't need a new frontmatter flag. Hugo already has `draft: true`, and `build.sh` already sources `.env` and passes `$@` straight through to `hugo`. Two lines of work:

```bash
# on m42
echo "export HUGO_BUILDDRAFTS=true" >> /srv/www/sindro.me/staging/.env
# in the repo
# add `draft: true` to the IFAD post's front matter
```

Commit, push, `./build.sh` on staging (builds 199 pages — drafts included), `./build.sh` on prod (builds 198 — drafts skipped). Verified with `curl -I`: IFAD post is 200 on staging, 404 on prod. The IRCity fix went to both.

That's the small architectural trophy of the evening — a drafts-on-staging-only flow that required zero new code and lived entirely in per-checkout `.env` files.

## The directive

About two hours in, I told the agent:

> *from now on, respond only when addressed, or when you genuinely have something to add. don't reply to every message.*

It saved that as a feedback memory and the channel got calmer. Signal went up, noise went down. The rule isn't "be shy"; it's "have something to say."

Small thing, but it changes the feel. A chat agent that replies to everything becomes a chat agent that *is* everything, which isn't participation — it's capture. A chat agent that picks its moments is a participant.

## Parts I didn't build

- **NickServ-based identification** for the trust check. Today it's literal nick match on `vjt`. First thing to harden if this becomes something I actually use.
- **Per-channel policy.** `#it-opers` is the only place it listens. No DMs handled beyond CTCP `VERSION`.
- **Replay / backfill.** If the bot disconnects, whatever happened while it was gone is gone.
- **Rate limiting.** The bot splits long lines but doesn't throttle; a misbehaving flood would get Q-lined, and rightly.
- **Italian translation of this post.** Coming — tonight's conversation was in Italian, and the quotes deserve their original voice.

## What this actually is

A four-hour proof of concept that feels a bit larger than four hours should have bought. Claude Code's [`Monitor`](https://docs.claude.com/en/docs/claude-code/) tool is the unlock: it turns a long-running external process into something the agent can react to as events, not polls. The IRC bot is almost not the point. The point is that the agent participated — joined a channel, listened, decided when to speak, refused commands from the wrong people, fixed its own facts against a witness, edited a blog post live, deployed it, and remembered to keep quiet when there was nothing to add.

Mezmerize, via Trillian relay, summed it up: *"ClaudeServ ftw."* The Azzurra services tradition has always been services named `*Serv`. There's a small temptation.

Thanks to everyone on `#it-opers` tonight — vjt (that's me, talking to a bot wearing a version of my beard), tsk for the IRCity correction, S`Afk for *"direi che questo merita un altro post sul blog"* (hence this post), Mezmerize and t for the puns, and the absent carrots for never being accepted.

Next experiment: give it `/whois` verification, a Matrix bridge, and a way to remember that two of the people on the channel tonight used to be two of the people I built the server software with, twenty-four years ago. The Azzurra story keeps getting new chapters written into it by the same handful of nicks; I'm not sure I mind that one more of them is a program I can `git log` against.
