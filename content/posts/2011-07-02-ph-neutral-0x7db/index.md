---
title: PH-Neutral 0x7db
date: 2011-07-02T17:00:00
tags: [conference, hack, security]
---

<p>&#8220;<strong>If it is good, they stop making it</strong>&#8221;, the
payoff printed on the conference necklaces, distributed to every participant,
along with an über-l33t badge customized with our nickname and the key
hash.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/phneutral-badge.jpg" alt="" /></p>


<p>Being my first experience at an international security conf (I’ve only been
to the ccc2k+7 camp), and being a ph outsider &#8216;cause I never participated
to previous editions, the boot keynote held by <a
href="http://twitter.com/41414141">FX</a>, staffer and frontman, has been
enlightening: &#8220;you ought to be here!&#8221;, he yelled while pointing at
the stage, wearing a white shirt with the Phenoelit logo printed on both
arms.</p>


<p><a name="continue"></a></p>


<p>&#8220;This conference has never started on time&#8221;, he continued,
&#8220;so there was no reason to do that for this last one&#8221;. the schedule
is straightforward: party, the next days talks from 12.00PM to 7.30PM, then
party, and the last days talks from 12.00PM to 5.30PM. definitely a setup
well-playing with the available alcohol :-D.</p>


<p>Afterwards, another speaker informed us that the wi-fi access keys we
received at the registration allows us to use a 6 APs/3 repeaters beast driven
by an OpenBSD box &#8211; they want the audience to hack it because, well,
&#8220;you are the Worst Case Scenario.&#8221; :-)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/ap-tree.jpg" alt="" /></p>


<p>Then, the funny Hacker Hacker video was presented:</p>


<p style="text-align:center;"><iframe width="100%" height="400"
src="https://www.youtube.com/embed/IZYQILfxHiw" frameborder="0"
allowfullscreen="yay"></iframe></p>


<p style="text-align:center;">:-D</p>


<p>After a lousy and not so exciting first night (due to tiredness), we’ll wait
and see what the next day would bring.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/funny-nhaima.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/sj.html">Sniffjoke &#8211; a
sniffer-evasion toolkit</a></h2>


<p>High capacity sniffers used in big cos and on border national gateways that
collect user generated traffic on order to find possibly &#8220;criminal&#8221;
patterns are today generally available for bandwidth to the 10Gbps, there will
be soon appliances that&#8217;ll process streams of 100Gbps.  Sniffjoke, by <a
href="http://twitter.com/sniffjoke">vecna</a> and <a
href="http://www.evilaliv3.org/">evilaliv3</a> is a tool that can inject into
<span class="caps">TCP</span> connections outsider packets that will fool the
intercepting sniffer but with no remarkable effect on the receiver. these
packets for instance trick the sniffer into thinking that the connection has
been reset even it is not true &#8211; by injecting a wrong-checksummed <span
class="caps">RST</span> or a packet with a <span class="caps">TTL</span> less
than 1 of the hop count &#8211; or try to consume its processing power by using
known vendor-specific interpretations of the <span class="caps">TCP RFC</span>.
Details: <a href="http://delirandom.net/sniffjoke/">website</a>, <a
href="http://www.slideshare.net/diocanaglia/sniffjoke-04">slides</a>, <a
href="http://www.wireshark.org/lists/wireshark-dev/200904/msg00343.html">wireshark
thread</a>.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/dante-poirot.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/wlan.html"><span
class="caps">WLAN</span> router horror stories</a></h2>


<p>Did you ever woder what happens when the wireless network password is
directly tied to the device <span class="caps">MAC</span> address, from which
it can be inferred because it is part of the essid? horror stories, as the an
Austrian (<a href="http://twitter.com/sviehb">ViBi</a>) and a German (<a
href="http://twitter.com/5m7x">5M7X</a>) researchers showed us. many carriers
who sell wifi equipment ship it with similar vulnerabilities, as also mayhem
and cyrax show us in <a
href="http://www.video.mediaset.it/video/iene/puntata/227136/viviani-haker-e-wifi.html">this
video</a> (italian only)</p>


<p>We&#8217;re talking about a technology whose potential is not maximized, as
a result leads to flawed the security measures, because of bad engineering and
misleading instructions: some wifi apparatus manuals even recommended the user
to never fiddle with the configuration and leave the default passwords in
place. clever.  Other examples of bad engineering include making the network
key the last 4 bytes of the internal eth <span class="caps">MAC</span> address
and then broadcasting that <span class="caps">MAC</span> via a multicast packet
sent to 224.0.1.0 (<a
href="http://www.samsung.com/global/business/telecommunication/productInfo.do?ctgry_group=14&amp;ctgry_type=32&amp;b2b_prd_id=217">Samsung
<span class="caps">G3200</span></a> / <span class="caps">G2210</span> / <span
class="caps">G3220</span>).</p>


<p>Other companies, such as the synchron who produce the <a
href="http://dsl.vodafone.de/hilfe/index.php?aktion=anzeigen&amp;rubrik=004&amp;id=269">easybox</a>
has a patented way to provide a key recognition method, and direct
correspondence between the mac and the key seed. eventually, there are even
companies who sell their devices with the management <span
class="caps">SSHD</span> open on the external interface, and who base the
network key entirely on the internal <span class="caps">MAC</span>. Couple it
with default passwords and you get the picture.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/wifi-armory.jpg" alt="" /></p>


<p>If you want to know more, you should get some <a
href="http://net-wifi.it/">armory</a> and either reverse engineer the
algorithms yourself, or participate to security conferences and ask the
researchers for the slides :-). Once the industry will be ready, all the
details will be revealed.</p>


<h2>Hacking <span class="caps">TETRA</span></h2>


<p>Held by Harald Welte (<a href="http://twitter.com/laf0rge">@laf0rge</a>),
member of the <a href="http://gnumonks.de/">gnumonks.de</a> crew, the talk
described a terrestrial radio communication technology that is similar to <span
class="caps">GSM</span> but runs on lower frequencies of the spectrum, thus
achieving wider coverage with less transceivers. <span
class="caps">TETRA</span> employs ways to authenticate and encrypt
communications, features a signaling channel over 140-chars messages are
exchanged and identifies each user on the network using the match between the
subscriber number and the terminal one.</p>


<p><a href="http://en.wikipedia.org/wiki/TETRA"><span
class="caps">TETRA</span></a> is widely deployed over the world as a
communication medium for public transport, public safety, firefighters, etc. it
is a technology suitable for these uses, but laforge correctly reminded us that
even if the tools allow us to implement secure networks, often the
implementations of such tools is ineffective and prone to breakage.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/laf0rge.jpg" alt="" /></p>


<p>He showed us how the signaling on the network works. He started by first
showing us packet dumps in wireshark, thanks to chinese hackers who wrote the
dissectors. He was also able to associate to a tetra network used by <span
class="caps">BVG</span>, the german public transportation system, and listen to
a call between the headquarters and all train drivers: the former was asking
the latters to push a button contemporarily. Yes, sir: in the 21st century you
still need people to do that. Awesome.  If you want to build your own, you
should first learn how radio communication works, buy yourself a <a
href="http://www.funcubedongle.com/">FUNcube</a> dongle and check out the <a
href="http://osmocomtetra/">OsmocomTETRA</a> project. An introduction is
available on <a
href="http://www.h-online.com/security/news/item/TETRA-digital-radio-now-for-everyone-1254088.html">heise.de</a>.</p>


<h2>Printer Hacking</h2>


<p>Find vulnerability into a printer management interface, write a java applet
that exploits it,  define hooks to drive it from Javascript, and your web-based
printer vulnerability scanner is done!</p>


<p>I missed the first part of the talk, so I don&#8217;t have the details, but
as the speaker told me later when I asked him how it all fitted together,
&#8220;it&#8217;s everything on the paper!&#8221; so just <span
class="caps">RTFM</span> <a href="http://andreicostin.com/papers/Conf -
EuSecWest2010_AndreiCostin_HackingPrintersForFunAndProfit_full.pdf">here</a>
:)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/naif-sleeping.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/chip_and_pin.html">Chip &#38;
<span class="caps">PIN</span> is definitely broken</a></h2>


<p>Moving on in the list of badly-implemented technologies, nowadays credit /
debit cards are vulnerable to a typical downgrade attack when it comes to
validating the <span class="caps">PIN</span>. There are different types of
chips, ones that only allow plaintext authentication between the <span
class="caps">POS</span> and the chip, others that employ a challenge-response
mechanism, and almost every one of them allow the <span class="caps">PIN</span>
to be validated online with the bank.</p>


<p>No matter what, the <span class="caps">SIM</span> exposes an interface to
the card readers, that can be queried and whose communication can be
eavesdropped by an intercepting device. Because cards must be
backwards-compatible with existing POSes and viceversa, such an intercepting
device is able to alter the advertised capabilities of the card and force the
<span class="caps">POS</span> to use plaintext authentication, and then
intercepting the pin as the user types it.</p>


<p>Such a skimmer is a 4&#215;4cm device, that can be installed
<strong>inside</strong> a <code>POS</code> or an <code>ATM</code>, thus
possibly going unnoticed for a long period of time. And even if there are
insurances that cover you against these frauds, if you&#8217;re a frequent
traveller, you can hard time in demonstrating you were a victim, both because
the card number and pin match, and because this is now considered as a
&#8220;secure&#8221; technology that cannot be broken.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/inversepath.jpg" alt="" /></p>


<p>Thanks to Andrea Barisani and Davide Bianco for making us aware of the
downgrade flaw. If you want to know more, here are their slide published on
their company site, <a href="http://inversepath.com/">inversepath.com</a>.</p>


<h2><a href="http://ph-neutral.darklab.org/talks/freebsd.html">FreeBSD kernel
exploitation</a></h2>


<p>As years go by, stack smashing is still alive and powerful, as <a
href="http://twitter.com/_argp">argp</a> explained during his talk. <a
href="http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2008-3531"><span
class="caps">CVE</span>-2008-3531</a> is a known vulnerability of the FreeBSD
kernel that allows code execution in kernel space, whilst the <span
class="caps">UMA</span> &#8211; FreeBSD&#8217;s memory allocator &#8211; <a
href="http://www.phrack.org/issues.html?issue=66&amp;id=8#article">has known
flaws in it as well</a>.</p>


<p>Without going into deeper details, the main issue here is the &#8220;if it
ain&#8217;t broken, don&#8217;t fix it&#8221; approach employed by many system
administrators when it comes to production machines: as a result, they do not
get updated for years. Maybe it&#8217;s not broken today (if ever, ya&#8217;now
0dayz?) but it will be broken tomorrow, and you&#8217;ll get pwned if you do
not keep up to date. <span class="caps">WORD</span>.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/argp.jpg" alt="" /></p>


<h2>Advances in win32 <span class="caps">ASLR</span> evasion</h2>


<p>When I think about Microsoft products, I always feel that they&#8217;re not
built to be used by people, because it looks to me that coders who write them
never care about using them in the first place. <a
href="http://en.wikipedia.org/wiki/Eating_your_own_dog_food">They do not eat
their own dog food</a>. just go on and try to use IE developer tools and
you&#8217;ll get the point.</p>


<p>Their software is written for business, it must match some higher-order
requirement agreed by some random manager 7 layers up in the hierarchy, and
very often it fails to implement them correctly. Thus, as <a
href="http://twitter.com/not_me">JF</a> pointed out during the talk
&#8220;Microsoft has spent a lot of money fixing the exploitation problem, but
they only created more of them&#8221;. Word, dword and qword! :-)</p>


<p><a href="http://en.wikipedia.org/wiki/ASLR"><span
class="caps">ASLR</span></a> is a mitigating factor for exploits that assume
the return address of vulnerable code lies in at a well-known address in
memory. These locations are used to compute where to write the shellcode in
order to trigger its execution after exploitation. If the return address gets
randomized (thus Address Space Layout Randomization), then the exploit will
just crash the vulnerable software by making it reference an address outside
its space.</p>


<p>Problem is that, for some obscure side effect, for each 16 threads you
create, if their base address is even (<code>0x02xxxxxx</code>,
<code>0x04xxxxxx</code>), 13 of them will end up being based at a known
location, thus making <span class="caps">ASLR</span> ineffective and bypassed.
<strong><span class="caps">PWN</span></strong>!</p>


<p>Check JF slides out <a
href="/posts/2011-07-02-ph-neutral-0x7db/Advances_in_Win32_ASLR_Evasion.pdf">here</a>
&#8211; thanks for sharing <a href="http://twitter.com/not_me">@not_me</a>!</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/jf.jpg" alt="" /></p>


<p>JF apologized at least 4 times before ending up closing its laptop and
ending the presentation with vodka and gin, because he said that he did not do
a good work in explaining but, as I also told him later, he was more than
effective: it&#8217;s not easy at all to understand how all the side effects
played together. Only he that was on this stuff for months was able to see the
patterns in addresses and convey a successful exploitation of an <span
class="caps">ASLR</span>-protected process. Enlightening!</p>


<h2><a href="http://ph-neutral.darklab.org/talks/lfh.html">Modern heap
exploitation using the low-fragmentation heap</a></h2>


<p>I&#8217;m no MM guy and I didn&#8217;t get most of the concepts of the talk,
but its abstract is very explanatory:</p>


<blockquote> <p><em>Heap memory management has matured over time, but with
complex new code comes new opportunity for exploitation. This presentation will
focus on understanding the Low Fragmentation heap on Windows 7 (32-bit). After
a foundation of integral concepts is laid, new exploitation techniques will be
thoroughly discussed. Finally, we will use this new found knowledge to leverage
<strong>supposed</strong> non-exploitable vulnerabilities. Specifically we will
cover a case study showing how to craft an exploit for the <span
class="caps">IIS FTP 7</span>.5 <strong>denial of service</strong> (<a
href="http://blogs.technet.com/b/srd/archive/2010/12/22/assessing-an-iis-ftp-7-5">http://blogs.technet.com/b/srd/archive/2010/12/22/assessing-an-iis-ftp-7-5-=
unauthenticated-denial-of-service-vulnerability.aspx</a>-=
unauthenticated-denial-of-service-vulnerability.aspx), resulting in full
control of <span class="caps">EIP</span>.</em></p> </blockquote>


<p>What is interesting is that in order to use a memory allocation optimization
subsystem to do what you want, you have to mix and match 7 different attack
primitives, understand thoroughly how the block allocations are made and how
they interact with the host <span class="caps">CPU</span>. As well as battle
with all the side effects in order to write in the program counter the address
you want to execute. “@You say <span class="caps">JMP</span>, we say what
addr@”, a T-shirt was correctly stating in front of me. :-)</p>


<p>Incredibly complicated as it sounds, <a
href="http://twitter.com/nudehaberdasher">Chris Valasek</a> was able to find,
exploit and explain the vulnerabilities, with a mental exercise that is both
brilliant than inspirating: always dig deeper, and you&#8217;ll be able to
reach any goal.</p>


<p><a
href="https://prezi.com/secure/73006c52fbfde4eddf935b5e09103df23580c39d/">Here
are Chris’ slides</a>, but you’ll have to enable Flash unfortunately.</p>


<h2>Exploiting the Hard-Working <span class="caps">DWARF</span>: Trojans with
no Native Executable Code</h2>


<p>Could you ever imagine that in every <span class="caps">GCC</span>-compiled
binary may lie a complete virtual machine subsystem, that gets invoked on every
call/ret and has the ability to read and write the heap and every cpu register?
indeed it is, and it&#8217;s called <span class="caps">DWARF</span>, a
debugging instrumentation used by <span class="caps">GDB</span> to help the
developer debug his/her software.</p>


<p><em>“It’s a <a href="http://en.wikipedia.org/wiki/DWARF"><span
class="caps">DWARF</span></a> and <a
href="http://en.wikipedia.org/wiki/Executable_and_Linkable_Format"><span
class="caps">ELF</span></a> story&#8230;”</em> LOL! :-D.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/dwarf.jpg" alt="" /></p>


<p>What&#8217;s interesting is also that <span class="caps">DWARF</span> code
is not considered by analysis tools as being part of the object code of a
binary, thus making it an injection vector to attach trojans to a binary.
Moreover, <span class="caps">DWARF</span> is platform and architecture
independent, being a finite-state machine on its own: a <span
class="caps">DWARF</span>-based trojan can be used over multiple platforms and
attached to any <span class="caps">ELF</span> binary.</p>


<p>If <span class="caps">DWARF</span> code is present, it gets executed for
each function called and on each return, as the stack gets unwinded, and yes
you can read and write the <span class="caps">CPU</span> and on the heap. Neat.
For all the details, check <a
href="http://ph-neutral.darklab.org/talks/tr2011-680.pdf">the whitepaper</a>
out.</p>


<p>Here we see an example of hobby-ism and poor project management on the <span
class="caps">GCC</span> side &#8211; no offense intended of course &#8211; but
such a crafted and complex subsystem ends up being available in the vast
majority of OSs, possibly making up an infection vector.</p>


<p>I infer this because <span class="caps">DWARF</span> is an obscure,
undocumented, cargo-culted piece of code written because somehow today and
tomorrow the <span class="caps">GDB</span> devs needed instrumentations, and
<span class="caps">GCC</span> devs built in an excessively powerful tool to
support them, but said tool can then be abused and no one really know how the
first releases work &#8211; unless you skim through random posts on the <span
class="caps">GCC</span> mailing list. More recent releases are pretty
documented, <a href="http://dwarfstd.org/Download.php">though</a>.</p>


<p>Funnily enough, I think to support <span class="caps">GDB</span>, even the
<a href="http://llvm.org/"><span class="caps">LLVM</span> compiler
infrastructure</a>, built with clean design from the ground up, uses <span
class="caps">DWARF</span>! That said, the moral of the story is that ugly hacks
today, will call you for trouble tomorrow &#8211; or the next day.</p>


<h2>Party! (<a href="http://82.94.215.218/download/ph-neutral/0x7db/DJ/">Music
Here</a>)</h2>


<blockquote> <p>- &#8220;hey man, are you the guy behind the openbsd box acting
as an host AP for the ph wifi network?&#8221;<br/> - &#8220;yeah, I
am&#8221;<br/> - &#8220;may I ask you a root shell?&#8221;<br/> - &#8220;you
want&#8230; <span class="caps">WHAT</span>?&#8221;<br/> - &#8220;yeah, you
know, I&#8217;d like to issue <code>ifconfig</code>, <code>brconfig</code>,
<code>pfctl -s</code>, <code>ls -lrt /etc | tail</code>, stuff like that
&#8211; just to see how the thing works :)&#8221;</p> </blockquote>


<p>Kudos to the OpenBSD panda, that didn&#8217;t give me a shell, but
illustrated me how the dorepanda access point &#8220;cluster&#8221; works,
creating a network that spans all the 802.11b/g and n spectrums. It load
balances clients between the APs, using cryptography to verify the AP identity
and trying to prevent eavesdropping.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/party1.jpg" alt="" /></p>


<blockquote> <p>- &#8220;man, you are actually a grey beard at a security
conference!&#8221;<br/> - &#8221;... so what?!&#8221;</p> </blockquote>


<p>... and then you talk with a 20-yrs experienced <span
class="caps">DBA</span> that tells you &#8220;<em>Oracle is flawed by
design</em>&#8221; and you chat with him about how the security scenario has
changed over the years.</p>


<blockquote> <p>- &#8220;nothing really changed, it just got more complicated
along the way&#8221;<br/> - &#8220;you mean, the bottom line is always you have
to snatch some shellcode in memory and then find a mean to execute
it?&#8221;<br/> - &#8220;exactly &#8211; you may have an NX bit, <span
class="caps">ASLR</span> and canaries, but there&#8217;s alway a way around
it.&#8221;</p> </blockquote>


<p>A good sysadm <a href="http://signalos.org/">friend of mine</a> told me
similarly, in terms of &#8220;as long as I read enough documentation, I&#8217;m
able to set up and deploy whatever system. no challenges anymore.&#8221;</p>


<p>To me, confs like this one make you wonder, think and activate mental
circuitry that stimulate your passion: you see brilliant humans solving tricky
problems, walking deeply into details and actually learning new things in the
process. human beings whose model of the world includes sequences of
interactions happening inside the machine. Like a skilled netadmin recognizes
AS numbers from netblocks, a kernel hacker learns to recognize portions of the
address space: he/she literally breathes within the operating system.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/party2.jpg" alt="" /></p>


<p>It amazes me how I found strong matches of Jeff Hawkins&#8217; <a
href="http://www.amazon.com/Intelligence-Jeff-Hawkins/dp/0805074562">theory of
intelligence</a> (<a
href="http://www.ted.com/talks/jeff_hawkins_on_how_brain_science_will_change_computing.html"><span
class="caps">TED</span> video</a>) in hackers&#8217; minds. I talked about the
<a href="http://numenta.com/htm-overview/htm-algorithms.php">HTMs</a> <a
href="http://numenta.com/htm-overview/education.php">paper</a> to the folks I
met, and I was surprised no one of them knew about a technology aimed at
building intelligent machines by reimplementing the human brain&#8217;s
cortical algorithm in silicon.  For instance, Chris Valasek and JF talks
demonstrate the basis of expertise: more and more you receive inputs from a
context, the more your brain will be able to see deeper and complicated
patterns, because they get moved lower in the cortex hierarchy, whose job is to
recognize details &#8211; as they did with <span class="caps">ASLR</span> and
the low-fragmentation heap.</p>


<blockquote> <p>- &#8220;sir, you are the only one wearing a tie in this
hall&#8221;<br/> - &#8221;...&#8221;<br/> - &#8220;so you must definitely work
for Microsoft!&#8221;<br/> - &#8220;ahem, no&#8230;&#8221;<br/> - &#8220;ah, ok
so my assumption was incorrect. sorry for bothering! :D&#8221;<br/></p>
</blockquote>


<p>At 5:15, it&#8217;s really better to get to bed, waiting for the next good
morning!</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/morning.jpg" alt="" /></p>


<h2>Day 3 &#8211; <a href="http://ph-neutral.darklab.org/talks/newav.html"
title="by natural language training">98% Zero-Day Virus Detection</a></h2>


<p>After such a party, both the <a
href="http://ph-neutral.darklab.org/talks/jes.html">social engineering</a> and
<a
href="http://www.slideshare.net/nbrito01/phneutral-0x7db-exploit-next-generation">Exploit
Next Generation++</a> talks were a bit foggy, I ever failed to recognized the
metasploit source code language (ahem). :-)</p>


<p>Then shirtie (<a href="http://twitter.com/skjortan">@skjortan</a>) on stage
illustrated how you can use a <a
href="http://en.wikipedia.org/wiki/Bayesian_classifier">Bayesian</a> / <a
href="http://en.wikipedia.org/wiki/Maximum_entropy_classifier"><span
class="caps">MAXENT</span></a> classifier to identify unknown, 0day
malware.</p>


<p>Exactly like an anti-spam filter catches spam by first analyzing a training
set, identifying the recurring patterns and then matching them with novel data,
malware as well as spam has typical features that can be used to find it. For
instance, the presence of a reference to the <code>CreateProcess</code> API or
the absence of the <code>&lt;a
href="http://en.wikipedia.org/wiki/Pentium_FDIV_bug"&gt;_check_fdiv&lt;/a&gt;</code>
one, to whether the binary is <a href="http://upx.sourceforge.net/"><span
class="caps">UPX</span>-packed</a> or not.</p>


<p>The technology looks effective, it is not a replacement of a signature-based
AV rather it is an augmentation, because it is prone to false positives, but it
is the only that identifies unknown, 0-day malware &#8211; the one for which no
signatures exist.</p>


<h2>Offensive <span class="caps">XSLT</span></h2>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/xslt.jpg" alt="" /></p>


<p><code>XSLT</code> is a language used to transform <span
class="caps">XML</span> documents into another form, and it is a
turing-complete language executed either in the server or in the client
context. it is used both by content management systems and in client-side
applications, the most prominent example being the index of a subversion
repository.</p>


<p>Because <code>XSLT</code> is a (functional) programming language, it offers
means to read and write files and to execute code. If the user input is not
sanitized and/or the <span class="caps">XSLT</span> engine exposed, it can be
used to pwn a machine. Of course, the abusable features can be turned off if
they&#8217;re not needed, or alternatively wrapped with a secure <span
class="caps">API</span> if they are.  Check <a
href="http://twitter.com/Agarri_FR">Nicolas Gregoire’s</a> slides out <a
href="http://prezi.com/y_fuybfudgnd/offensive-xslt/">here</a>. Liferay users,
<a href="http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-1571">you’ve
been warned</a> :-)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/an0nym0us.jpg" alt="" /></p>


<h2>Final words</h2>


<p>Thanks <a href="http://twitter.com/nhaima">@nhaima</a> for telling me about
the conf and allowing me to have a grant (thanks nobody :)</p>


<p>Thanks <a href="http://twitter.com/techdoer">@techdoer</a> for editing the
post &#8211; hopefully this is my first one without grammar errors :-D</p>


<p>Thanks <a href="http://twitter.com/phonoelit">@phenoelit</a> and <a
href="http://twitter.com/41414141">@41414141</a> for organizing the party
(you&#8217;re da men), everyone who was there. I hope to see you soon on stage
:). Yay!</p>
