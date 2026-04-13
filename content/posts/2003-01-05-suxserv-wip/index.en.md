---
title: "Sux Services: threading works, we are 0.1 =)"
date: 2003-01-05
tags: [irc, c, azzurra, open-source]
description: "WIP on my IRC services for Azzurra. Threading finally works, the thing connects, tracks users and channels. Time to rewrite everything."
image: sourceforge.png
featuredImage: sourceforge.png
---

So I`ve been coding through the holidays and things are finally coming together.

Quick context if you ended up here randomly: I`m writing IRC services from scratch in C for the [Azzurra IRC Network](https://www.azzurra.org/). NickServ, ChanServ, the whole deal. Using [GLib 2](https://developer.gnome.org/glib/) for threading and data structures, [gperf](https://www.gnu.org/software/gperf/) for the command dispatch tables, and connecting to a [Bahamut](http://bahamut.dal.net/) IRCd via the server-to-server protocol.

Yesterday I got the multithreading working properly. Three threads: one for the network I/O (using GLib`s async main loop), one for parsing IRC messages and dispatching commands, and one for signal handling. They coordinate through mutexes and a GAsyncQueue. I was going mad with the dbufs and the broken realloc for a while but now it actually works without segfaulting, which is nice.

The gperf stuff is really cool. You give it a list of commands and it generates a perfect hash function -- zero collisions, O(1) lookup. So when the parser thread gets a NICK or SJOIN or PRIVMSG from the server, it maps to the handler function in constant time. No strcmp chains, no linear search. I stole the basic parsing logic from bahamut`s parse.c (credited in the comments of course) and adapted it.

Here`s what the parse.gperf looks like:

```c
struct Message { gchar *cmd; void (*func)(User *, gint, gchar **); };
%%
NICK, m_nick
PRIVMSG, m_private
SJOIN, m_sjoin
QUIT, m_quit
KICK, m_kick
MODE, m_mode
%%
```

Feed that to gperf and you get a hash_get_cmd() function that does the lookup. Sweet.

Current state: the services connect to the IRC server, negotiate the link, track all users and channels in memory with thread-safe hash tables backed by GMemChunk pools, handle PING/PONG, support SJOIN and BURST, and can respond to basic /stats queries. It even forks into the background properly now.

What`s missing: everything else =). No NickServ, no ChanServ, no database, no config file (still using hardcoded defines.. I know, I know). The user/channel tracking is solid though, and the architecture is clean enough that adding services on top should be straightforward.

I tagged it 0.1. Today I`m already rethinking some things and will probably do a rewrite of the core. The code works but it`s messy -- I learned a lot in the last three months about how GLib threading actually works vs how I thought it worked.

The [project home page is here](https://suxserv.sourceforge.net/) and the [SourceForge project page is here](http://sourceforge.net/projects/suxserv) if you want to grab the code or follow along. BSD-licensed. There`s even a [download](http://sourceforge.net/project/showfiles.php?group_id=70725) if you want to try it, though right now it won`t do much except connect and track users.

Back to coding.
