---
date: "2008-06-03T00:00:00Z"
title: "Cosa dice la tua .bash_history?"
tags: [bash, geek]
categories: [number-42]
---

Un [mio amico](http://www.linkedin.com/in/easter) mi ha detto che sui blog
tecnici gira un nuovo meme: mostrare i comandi più usati, partendo dalla
history della shell:

```bash
history | \
awk '{a[$2]++}END{for(i in a){print a[i] " " i}}' | \
sort -rn | head -15
```

Io ho 20 volte la dimensione di default della bash history (10k righe), quindi
i risultati saranno interessanti. Uso anche la funzione di timestamp della
history, quindi ho aggiunto un piccolo sed al codice per eliminare i timestamp.

Vediamo un po':

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

Già, faccio un SACCO di ls, l in realtà è ls -alFGs (sono su Darwin). Questa
lista rivela le mie abitudini recenti, perché sto scrivendo meno codice e
gestendo di più (niente gcc, niente irb, un sacco di dig & whois). `svn` è
ancora lì, ovviamente ;). `ssh` significa che questi risultati andrebbero
aggregati con le history delle altre macchine su cui mi loggo... ma quello è
argomento per un altro post ;).

Quali sono i tuoi risultati?

Postali qui! :D

## AGGIORNAMENTO 2008-06-03

Dato che le mie abitudini recenti sono più di coding che di scrittura di documentazione, ho rieseguito l'analisi della history... e questi sono i nuovi risultati:

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

## AGGIORNAMENTO 2009-02-20

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

## AGGIORNAMENTO 2009-05-24

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

## AGGIORNAMENTO 2010-06-01

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

## AGGIORNAMENTO 2012-07-23

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
