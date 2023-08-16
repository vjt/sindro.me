---
date: "2008-06-03T00:00:00Z"
title: "What does your .bash_history say?"
tags: ["bash", "geek", "history", "shell"]
categories: [number-42, all]
---

A [friend of mine](http://www.linkedin.com/in/easter) told me that on techie
blogs there is a new meme going on: show off the most used commands, starting
from shell history:

```bash
history | \
awk '{a[$2]++}END{for(i in a){print a[i] " " i}}' | \
sort -rn | head -15
```

I've got 20 times the default bash history size (10k lines), so it'll yield
interesting results. I also use the history timestamp feature, so I've added a
little sed to the code in order to strip timestamps out.

Let's see:

```bash
vjt@voyager:~/code*$* history | 
 sed 's#^[ 0-9\[\/\:]*\]\([^ ]*\).*#\1#' |  
 awk '{a[$1]++}END{for(i in a){print a[i] " " i}}' | 
 sort -rn | head -15
928 l
577 ssh
389 ping
381 cd
300 dig
259 telnet
153 sudo
126 ifconfig
125 whois
113 ps
96 svn
91 cat
73 fg
68 vi
61 ..
```

Yeah, I do a LOT of ls, l is actually ls -alFGs (I'm on Darwin). This list
exposes my recent habits, because I'm coding less and managing more (no gcc, no
irb, lots of dig & whois). `svn` is still there, of course ;). `ssh` means that
these results should be aggregated with other histories coming from the other
boxes I log on to.. but that's a topic for another post ;).

Which are your results?

Post them here! :D

## UPDATE 2008-06-03

As my recent habits are more coding than writing docs, I re-ran the history analysis.. and these are the new results:

```
1796 l
981 svn
705 ssh
693 cd
666 ping
402 vi
356 ifconfig
352 telnet
321 dig
315 sudo
283 fg
240 grep
188 ..
183 cat
157 ps
```

## UPDATE 2009-02-20

```
5427 l
4379 git
3128 svn
2812 vi
2105 cd
1408 ping
1392 fg
1328 ssh
935 ifconfig
893 grep
890 sudo
733 rake
653 cat
554 ..
535 ruby
```

## UPDATE 2009-05-24

```
7374 l
5041 git
3265 vi
3131 svn
2753 cd
1881 ssh
1763 ping
1618 fg
1101 sudo
1100 ifconfig
977 grep
867 cat
767 rake
721 telnet
671 ..
```

## UPDATE 2010-06-01

```
20517 git
7794 l
1906 cd
1631 rg
1518 vi
1108 rake
1041 cat
1010 ruby
790 sudo
754 fg
676 make
670 script/console
626 rm
496 ping
474 ..
```

## UPDATE 2012-07-23

```
3367 l
2685 ssh
1289 cd
1013 curl
976 git
857 sudo
815 ping
526 telnet
521 ps
497 cat
472 port
422 fg
400 vi
274 rm
259 dig
```
