---
date: 2011-01-04T18:00:00Z
title: "*BSD su un MacMini 4,1? Neanche per sogno. :-("
tags: [apple, freebsd]
---

{{< retrospective year="2026" >}}
Buone notizie: FreeBSD supporta pienamente l'hardware del MacMini 4,1 (NV MCP89 SATA, BCM57762 NIC) da FreeBSD 9.x (2012). Anche NetBSD e OpenBSD hanno aggiunto il supporto. Il "neanche per sogno" nel titolo non è invecchiato bene — i BSD girano tranquillamente su questa macchina ormai.
{{< /retrospective >}}

<img src="/posts/2011-01-04-bsd-onto-a-macmini-4-1-no-way/mini-daemon.png" style="float: right" />

<p>Ho passato gli ultimi due giorni a cercare di configurare il Mac Mini in alluminio (rev. 4,1)
come <span class="caps">NAS</span> server casalingo con storage crittografato, e
volevo metterci un sistema <span class="caps">BSD</span>. C'è già un
OpenBSD embedded sul gateway soekris, e un compagno sarebbe stato
carino. :-)</p>

<p>Indovinate un po', non c'è verso:</p>

<ul> <li>FreeBSD 8.1 non completa il processo di boot, a causa di <a
href="http://wiki.freebsd.org/AppleMacbook">un bug nel chipset <span
class="caps">SATA</span>, <span class="caps">NV MCP89</span></a>;</li>
<li>FreeBSD 8.2-RC1 fa il boot ma, a causa dello stesso bug, non riconosce nessun
drive <span class="caps">SATA</span> né nessun dispositivo <span class="caps">USB</span>
umass;</li> <li>NetBSD 5.1 fa il boot senza problemi, gestisce i
dischi <span class="caps">SATA</span> tramite il driver generico pciide (niente <span
class="caps">DMA</span>, quindi piuttosto lento) ma, sfortunatamente, non gestisce
il controller ethernet <span class="caps">BCM57762</span>. Ho provato con
patch veloci e sporche per <a
href="http://code.bsd64.org/cvsweb/netbsd/src/sys/dev/pci/if_bge.c">portare il
driver bge al livello di -current</a>, ma niente da fare: il <span
class="caps">MII</span> link detection funziona, la scheda trasmette ma
non riceve. Anche il controller sdmmc funziona con -current ma non
con la 5.1-RELEASE. L'<span class="caps">ACPI</span> funziona correttamente;</li>
<li>OpenBSD 4.8 fa il boot, accede ai drive <span class="caps">SATA</span>
senza <span class="caps">DMA</span>, e riconosce la scheda di rete bge, ma
mostra lo stesso identico comportamento di NetBSD 5.1 col driver di -current;</li>
<li>DragonFlyBSD 2.8.2 non entra nemmeno in kernel mode, sospetto
a causa di bug <span class="caps">ACPI</span>;</li> <li>PureDarwin non mi ha
ispirato granché, a causa dei tanti <a
href="http://www.puredarwin.org/blockers">problemi bloccanti</a>.</li> </ul>

<p>Tutti supportano lo storage crittografato, ho tirato su un disco <a
href="http://netbsd.gw.com/cgi-bin/man-cgi?cgd+4+NetBSD-5.0">NetBSD <span
class="caps">CGD</span></a> senza problemi su dk wedge; FreeBSD ha gli
interessanti strumenti <a
href="http://www.freebsd.org/doc/handbook/disks-encrypting.html">gbde(8) e
geli(8)</a> basati su GEOM che non ho potuto testare, mentre OpenBSD
supporta la crittografia tramite una <a
href="http://www.openbsd.org/cgi-bin/man.cgi?query=softraid&amp;sektion=4">personality
softraid</a>. Purtroppo, il supporto per l'hardware Apple, ormai esotico, è
fuori discussione.</p>

<p>Quindi, senza altra via d'uscita, ho deciso di prendere la strada Linux, usando
l'eccellente <a href="http://sysresccd.org/">sysresccd</a>, che eleggo oggi a
successore del <a href="http://rescuecd.pld-linux.org/">rescuecd di pld-linux</a>,
compagno di infinite recovery di sistema :-). Ad ogni modo, serve il kernel
2.6.36 per farlo partire sul MacMini4,1, a causa del suddetto
bug <span class="caps">MCP89</span>. Scheda ethernet e lettore SD card funzionano
out-of-the-box.</p>

<p>Ora sto giocando con <a
href="http://code.google.com/p/cryptsetup/wiki/FrequentlyAskedQuestions"><span
class="caps">LUKS</span></a> e, anche se non sono un esperto di
crittografia, sembra più evoluto delle controparti *BSD, ed è comunque uno
strumento più versatile rispetto a quelli di OpenBSD e NetBSD. Su
quest'ultimo, dover configurare <span class="caps">GPT</span> e DK Wedge per far
funzionare il <span class="caps">CGD</span> e sincronizzare <span class="caps">MBR</span> e
Disklabel per far funzionare il boot loader (bleah!), il tutto accoppiato con rEFIt,
è un bel casino&#8482;. C'è un <a
href="http://www.netbsd.org/~mishka/gptboot/howto.html">loader <span
class="caps">GPT</span> per NetBSD</a> ma non ho avuto modo di
provarlo.</p>

<p>Spero che queste informazioni siano utili a chiunque tenti un'avventura simile,
i commenti sono apprezzati :-).</p>
