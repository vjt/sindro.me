---
title: "The Azzurra forum, pulled back out of the Wayback Machine"
date: 2026-09-05
tags: [irc, azzurra, wayback-machine, digital-archaeology, python, sqlite, open-source]
description: "forum.azzurra.org has been dead for years. The Wayback Machine still had nearly all of it: 159484 posts from 2001 to 2016, readable and searchable again."
image: cover.jpg
featuredImage: cover.jpg
---

For fifteen years `forum.azzurra.org` was the place where the Italian IRC network argued
calmly. Then it died, the way forums die: not with an announcement, but with a domain that
stops resolving. You always remember the Wayback Machine too late — not this time.

<!--more-->

> 🍸 *Landed here by accident? This is the story of recovering fifteen years of an IRC
> network's forum. If you're wondering why anyone in 2026 does IRC archaeology, the long
> answer is [here](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/), and the short
> one is that IRC still works: **[click here and go back to 1995 →](https://grappa.chat/)** —
> pick a name, walk into a room, you're in. No app, no account.*

The result is online and needs no registration:
**<https://vjt.github.io/azzurra-forum-archive/>** — the old address
`sindro.me/t/forum-azzurra/` redirects there, deep links included. The code, the raw
snapshots and everything needed to rebuild it are on GitHub:
**<https://github.com/vjt/azzurra-forum-archive>**.

Numbers, because without numbers it's hot air: **114 forums, 7070 threads, 159484 posts**,
from 28 June 2001 to 29 July 2016. Client-side full-text search, one page per thread,
static HTML you can pull down with `wget -r` and that will outlive me.

## Why

Because it's digital archaeology, and dragging dead things back into circulation is one of
the finest jobs there is. That forum is still on `web.archive.org`, in theory: in practice
every page is a request to a machine that holds up the memory of the entire web on
donations, and it takes half a minute to serve you a thread from 2004. Here it takes as
long as a `GET` on a file: it's static HTML, and you can download the lot.

That's not a complaint about the Archive, it's the opposite. Without them this material no
longer existed: the domain lapsed, the database went where databases go, nobody had a
backup. They had been photographing it for fifteen years without anyone asking. I send them
10 dollars a month and I'll keep sending them; if you've ever found something you'd given
up for lost thanks to them, consider doing the same. The history of the internet does not
preserve itself: it leaves quietly, one domain at a time, and you notice the day you go
looking for it.

## How it was done

A note up front, because leaving it out would be dishonest: **the code of this archive is
entirely LLM-generated**. I described what I wanted to Claude over a long session — the
importer, the merge, the renderer, the download scripts and this post came out of there. I
gave the instructions, read what came back, said where it was wrong and decided what to
keep. The craft didn't disappear, it moved: the machine does the boring part, knowing what
you want and noticing when the result is nonsense is still on you.

The architecture fits in one line. You ask the Archive for its index, you download the list
of URLs, you fetch them **one at a time**, you parse them, you dump them into SQLite, and
from SQLite you generate the static pages.

The first step is the CDX index: `web.archive.org/cdx/search/cdx?url=forum.azzurra.org*`,
twenty pages of results, filtered to `statuscode:200`, and **without `collapse=urlkey`** —
the collapsed index keeps exactly one snapshot per URL, and if that one is the one the
Archive serves empty, you have no fallback. Out come timestamp, original URL, mimetype and
digest for every shot of every page: from there you extract, per thread, the list of good
snapshots in order of preference.

The second is the download, and it has to be serial. Every URL is fetched as
`web/<timestamp>id_/<url>`: the `id_` suffix returns the original 2004 bytes, without the
navigation bar the Archive injects. Three seconds of pause between requests, and after five
consecutive failures a two-minute cooldown, because at that point it isn't your error: the
Archive has shut the door. The script is resumable and never refetches a file already on
disk — which, with a ten-thousand-page list and a network that gets bored, is the
difference between finishing and starting over.

The third is parsing, in three passes and not one. The forum changed software twice — phpBB
1.4.0, then phpBB 2.0.x, then vBulletin — and the Wayback Machine photographed all three
eras, with every skin that came and went: five different markups for the same content,
ISO-8859-1, often cut in half. First the 8834 vBulletin snapshots go into the real tables
(`forums`, `threads`, `posts`, plus the FTS5 index), then the 1604 pages of the old board
into separate staging tables, and only at the end does a third script fold the latter into
the former. The database is not an archival format, it's a working index: throw it away and
it comes back in three minutes.

The last step reads SQLite and spits out HTML: one page per thread, one per section, plus
the client-side full-text index. No database in production, no process to keep alive,
nothing that can fall over at three in the morning.

## Where you trip

**Downloading in parallel doesn't work, and it won't tell you.** The first run fired
batches in parallel and answered `HTTP 200` to everything. Around 2360 of those 200s had a
zero-length body: that's how the Archive says no, without declaring it. `curl` exits
`rc=0`, you read "success", and you take home empty files. Serially, with a four-second
pause and a long cooldown, the same list returned 100%. An honest error is worth a thousand
fake successes.

**Parsing strictly throws away data that is there.** Demanding the "right" HTML delimiters
zeroed out 1939 perfectly readable threads in an older skin; demanding the closing `</div>`
threw away every snapshot the Archive had cut mid-body. Two fixes of two regex characters
each, ~16000 posts recovered. The parser now accepts a body that ends at EOF and marks it
`truncated = 1` — there are 771. Half a post from 2001 beats no post.

**The old board is not a second forum, it's the same one.** vBulletin had already carried
over part of the phpBB content, so the mirror isn't appended: it's merged, with dedup. And
the dedup can't look at the clock, because there's an hour of drift between the two corpora
(the DST change around the migration) and two posts by the same user two minutes apart are
two real posts. The key that holds is the **body**: token containment ≥ 0.8 and Jaccard
≥ 0.5, within 180 seconds of one of the 0/±1h offsets, with the offset **measured on the
nearest duplicate** and not decided once for the whole thread. Result: 8686 posts in the
mirror, 5286 genuinely new.

**Position in the downloaded page is not position in the forum.** 144 threads read out of
order, and none of it was the parser's fault: the old board's page holds ten posts and not
fifteen, vBulletin writes the time in the format of whoever was looking (460 dates were
`01:21 PM`, and dropping the marker moved them twelve hours), and a snapshot taken months
after another doesn't agree on positions because somebody deleted a post in between. Where
the board left an id, the id decides the order. Eight threads out of 7070 still have a jump
backwards: there the clock lies and the ids don't.

The rest is a `Makefile`: `make db` rebuilds the SQLite database from scratch in three
minutes, `make site` spits out 6634 static pages in twenty-five seconds, `make search` puts
the index on top. The database is disposable and indeed it isn't in the repository —
`pages/` is the opposite, and twelve threads are lost for good anyway: every snapshot the
Archive lists for them comes back empty.

What's left belongs to whoever wrote it. If you're the author of a message and you want it
gone, open an issue and it goes.

> 🍸 *Azzurra is still there, and so is IRC. If this gave you the urge to see what it looks
> like today: **[grappa.chat](https://grappa.chat/)** — pick a name, click a room, and
> you're in 1995 without installing anything. The reason for all of this is written
> [here](/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/).*
