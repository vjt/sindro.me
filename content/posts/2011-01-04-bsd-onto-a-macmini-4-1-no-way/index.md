---
date: 2011-01-04T18:00:00Z
title: "*BSD onto a MacMini 4,1? No way. :-("
tags: [apple, bsd]
---

<img src="/posts/2011-01-04-bsd-onto-a-macmini-4-1-no-way/mini-daemon.png" style="float: right" />

<p>I spent the last two days trying to set up the Aluminium Mac Mini (rev. 4,1)
as a home <span class="caps">NAS</span> server with encrypted storage, and I
wanted a <span class="caps">BSD</span> system on it. There&#8217;s already an
embedded OpenBSD onto the soekris gateway, and another companion would have
been nice. :-)</p>

<p>Guess what, there&#8217;s no way out:</p>

<ul> <li>FreeBSD 8.1 doesn&#8217;t complete the boot process, due to <a
href="http://wiki.freebsd.org/AppleMacbook">a bug in the <span
class="caps">SATA</span> chipset, <span class="caps">NV MCP89</span></a>;</li>
<li>FreeBSD 8.2-RC1 boots but, due to the same bug, doesn&#8217;t recognize any
<span class="caps">SATA</span> drive nor any <span class="caps">USB</span>
umass device;</li> <li>NetBSD 5.1 boots fine, handles <span
class="caps">SATA</span> disks via the generic pciide driver (no <span
class="caps">DMA</span>, thus quite slow) but, unluckily, doesn&#8217;t handle
the <span class="caps">BCM57762</span> ethernet controller. I tried with quick
and dirty patches to <a
href="http://code.bsd64.org/cvsweb/netbsd/src/sys/dev/pci/if_bge.c">bring the
bge driver up to date with -current</a>, but still no luck: the <span
class="caps">MII</span> link detection works, the card transmits but
doesn&#8217;t receive. The sdmmc controller as well works with -current but not
with 5.1-RELEASE. <span class="caps">ACPI</span> works correctly;</li>
<li>OpenBSD 4.8 boots, can access the <span class="caps">SATA</span> drives
without <span class="caps">DMA</span>, and recognizes the bge network card, but
exposes the very same behaviour as NetBSD 5.1 with the -current driver fitted
in;</li> <li>DragonFlyBSD 2.8.2 doesn&#8217;t even enter kernel mode, I suspect
due to <span class="caps">ACPI</span> bugs;</li> <li>PureDarwin didn&#8217;t
inspire me too much, due to the many <a
href="http://www.puredarwin.org/blockers">blocking issues</a>.</li> </ul>

<p>All of them support encrypted storage, I built up a <a
href="http://netbsd.gw.com/cgi-bin/man-cgi?cgd+4+NetBSD-5.0">NetBSD <span
class="caps">CGD</span></a> disk flawlessly onto dk wedges; FreeBSD has got the
interesting <a
href="http://www.freebsd.org/doc/handbook/disks-encrypting.html">gbde(8) and
geli(8)</a> GEOM-based tools that I wasn&#8217;t able to test, while OpenBSD
supports crypto via a <a
href="http://www.openbsd.org/cgi-bin/man.cgi?query=softraid&amp;sektion=4">softraid
personality</a>. Unluckily, support for the, nowadays, exotic Apple hardware is
a no-brainer.</p>

<p>So, with no other way left open, I decided to go the Linux route, using the
excellent <a href="http://sysresccd.org/">sysresccd</a>, that I elect today as
the successor of the <a href="http://rescuecd.pld-linux.org/">pld-linux
rescuecd</a>, companion of endless system recoveries :-). Anyway, you&#8217;ll
need the 2.6.36 kernel to make it boot onto the MacMini4,1, due to the
aforementioned <span class="caps">MCP89</span> bug. Ethernet card and SD card
reader work out-of-the-box.</p>

<p>Now, I&#8217;m playing with <a
href="http://code.google.com/p/cryptsetup/wiki/FrequentlyAskedQuestions"><span
class="caps">LUKS</span></a> and, while I&#8217;m not that competent in
cryptography, looks like it is more evolved than the *BSD counterparts, and
anyway it is more versatile tool than the tools in OpenBSD and NetBSD. On the
latter, having to set up <span class="caps">GPT</span> and DK Wedges to make
the <span class="caps">CGD</span> and synch <span class="caps">MBR</span> and
Disklabel to make the boot loader work (yuck!), everything coupled with rEFIt
is quite a mess&#8482;. There&#8217;s a <a
href="http://www.netbsd.org/~mishka/gptboot/howto.html"><span
class="caps">GPT</span> loader for NetBSD</a> but I hadn&#8217;t a chance to
try it out.</p>

<p>I hope this information is useful to anyone who tries a similar adventure,
comments are appreciated :-).</p>

