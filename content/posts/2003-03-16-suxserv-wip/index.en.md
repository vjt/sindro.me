---
title: "Sux Services 0.2.8"
date: 2003-03-16
tags: [irc, c, azzurra, open-source]
description: "Release 0.2.8 of my IRC services. NickServ, ChanServ, MemoServ, OperServ all working. Currently stress testing with 100 bots."
image: sourceforge.png
featuredImage: sourceforge.png
---

{{< retrospective year="2026" >}}
Twenty-three years later, I [recovered the CVS history from SourceForge](/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/) — 954 commits, three authors, a continuous trail from September 2002 to November 2005. The full retrospective covers what I built, what I never finished, and why. There's a [companion piece on the Bahamut IRC server fork](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) that this depends on.
{{< /retrospective >}}

So I just tagged 0.2.8 and I think this thing is getting close to usable.

Quick recap for those who don't know: [Sux Services](https://suxserv.sourceforge.net/) are IRC services I'm writing from scratch in C for the [Azzurra IRC Network](https://azzurra.chat). The idea is: multithreaded, modular, SQL backend instead of flat files, and not a complete mess to maintain. We'll see about that last part.

What works right now: NickServ does registration, identification, password change, ghost kill. ChanServ has channel registration, access lists (CF/SOP/AOP/VOP/AKICK) with masks support, and it actually enforces access on join. MemoServ sends and reads memos, notifies you on connect if you have new ones. OperServ has AKILL, server MAP, STATS. There's even a RootServ for the really scary stuff.

The whole thing connects to a [Bahamut](http://bahamut.dal.net/) IRCd, negotiates the server link, syncs all users and channels, and then the five service agents boot up as virtual users. Modules are compiled as .so files and loaded at runtime via GLib's GModule. If I want to reload NickServ I just unload and reload the module, no restart needed. Pretty cool.

I'm testing it with [netxplode](http://sourceforge.net/projects/suxserv) which is a perl script that spawns 100 IRC clients and hammers services with random commands -- IDENTIFY, INFO, REGISTER, JOIN, you name it. Basically 100 bots going completely nuts on NickServ and ChanServ at the same time. Found a lot of bugs this way. Also found an SQL injection in the nickname handling last week which was fun. Fixed now, we use sql_printf() to escape everything, but yeah, that could have been bad.

The threading is solid at this point. Four threads: network I/O on a GLib main loop, a parser that splits the receive buffer and dispatches commands through gperf-generated perfect hash tables (O(1) lookup, zero collisions, I love this thing), a signal handler thread, and the master that manages everything. Mutexes and condition variables for synchronization, GMemChunk pools for allocation. It doesn't segfault anymore which honestly took a while.

If you want to try it or look at the code: [project page](http://sourceforge.net/projects/suxserv), [home page](https://suxserv.sourceforge.net/), or just grab the [download](http://sourceforge.net/project/showfiles.php?group_id=70725). You'll need GLib 2.2+, MySQL, and a Bahamut IRCd. BSD licensed.

Next up: OperServ needs more work, I want to add nick expiry, and the whole help system needs to be loaded from the database instead of being hardcoded. Also someone already filed a [bug](https://sourceforge.net/tracker/index.php?func=detail&aid=705501&group_id=70725&atid=528793) on sourceforge so I guess people are actually trying it =)


---

**Azzurra IRC, 2002–2026:** **Sux Services 0.2.8 (WIP) (2003)** • [Bahamut fork: IPv6 + SSL](/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) (2026) • [Sux Services retrospective](/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/) (2026)
