---
date: 2009-05-16T04:00:00
title: The conceptual foundations and the economics network neutrality [Part 2] - 14 May 2009, Rome
tags: [economics, network, neutrality, politics]
categories: [politics]
---

<p>This is the second part of my recap of the <a
href="http://www.nnsquad.it/">nnsquad.it</a> convention held in Rome on May 14,
2009, and hosted by the <span class="caps">ICT</span> consultants foundation <a
href="http://www.fub.it/">Fondazione Ugo Bordoni</a>.</p>


<p>In the <a
href="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-rome">first
part</a> I described the morning session, dedicated to the definition of
Network neutrality, and how global economics  can cope with it. The afternoon
was dedicated to more technical talks, and I had the occasion to hear telcos
spokesmen remarks over the current situation and possible future
developments.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/rospigliosi-palace-statues-room-nnsquad-convention.jpg"
alt="" /></p>


<p><a name="continue"></a> The first speech started at 2.15PM and was held by
Prof. <a
href="http://www.sede-cremona.polimi.it/organizzazione/dettagli_docente.php?id_nav=6582&amp;aa=2008&amp;sede_cds=cr&amp;k_docente=176618&amp;n_docente=TRECORDI%20VITTORIO">Vittorio
Trecordi</a> (slides available <a
href="http://www.fub.it/files/Slide_Trecordi_14_05_09.pdf">here</a>). He
introduced it by stating that net neutrality could possibly contrast with the
economic development and security assessment, because of the wiretapping needed
for the latter, tap that is strongly against the individual freedom to
communicate.</p>


<p>Strangely (or maybe not) enough, no mention was made to current ways to
bypass both wiretapping and localization of communicating peers: I&#8217;m
referring to the <a href="http://tor.eff.org/">tor project</a>, the most known
bastion that guarantees privacy and is <a
href="https://www.torproject.org/about/overview.html.en">currently used by
journalists working in &quot;hot&quot; areas</a>, among many others.</p>


<p>Another point about legislation is that it isn&#8217;t the same in all
countries, althought the Internet is spread all over the world; moreover we
should define on what networks we should assess neutrality, because not
necessarily an IP network is connected to the Internet (think about <span
class="caps">ISP</span>-owned walled gardens).</p>


<p>Also, again on the Quality of Service: Trecordi stated the Internet
succeeded because of its &quot;hourglass model&quot; and &#8220;the capability
to decouple communications services and network infrastructure&#8221;, but QoS
requirements (e.g. for VoIP) stress the protocol stack pile, moreover where the
network pipes are &#8220;overbooked&#8221;. Furthermore, even overprovisioning
fails, because of the decentralized architecture of the Internet, and
bottlenecks are mainly located in <a
href="http://www.mix-it.net/">interconnection points between ISPs</a>.</p>


<p>So, the Internet is a best-effort platform, where an <span
class="caps">ISP</span> can&#8217;t control how its customers&#8217; packets
will be treated when crossing its borders, and reach a geographically far
provider. In this area reside the business model of the <a
href="http://en.wikipedia.org/wiki/Content_delivery_network">content delivery
networks</a>, that we&#8217;re transparently using everyday to access heavily
trafficked <a href="http://facebook.com/">web</a> <a
href="http://www.cnn.com/">sites</a>, and that also caused some funny
misunderstandings in the past, when <a href="http://www.akamai.com/">akamai</a>
started proxying the <a href="http://www.microsoft.com/">microsoft</a> with <a
href="http://squid-cache.org/">squid</a> running on Linux, and <a
href="http://news.netcraft.com/">netcraft</a> shown in its statistics that <a
href="http://www.linuxjournal.com/article/4962">microsoft servers are running
on linux</a> :).</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/akamai-how-content-delivery-network-works.png" alt="" /></p>


<p style="text-align:right;"><cite>Source: <a
href="http://www.akamai.net/">Akamai</a></cite></p>


<p>Apart from that funny joke (from 2001), <span class="caps">CDN</span>
shorten the routing path between users and static content of a service, using
geographically distributed data centers running <a
href="http://varnish.projects.linpro.no/">Varnish</a> (or equivalent software)
and a geolocation-enabled <span class="caps">DNS</span> server such as <a
href="http://www.powerdns.com/">PowerDNS</a>. This way, when some random client
tries to resolve an hostname, the <span class="caps">DNS</span> answers with
the nearest datacenter virtual IP address, and then serves content off the
cache.</p>


<p>This are approaches that try to mitigate the best-effort nature of the
Internet, but maybe there are better solutions. <span class="caps">NGN</span>
aims to be one of those, by providing multiple network pipes dedicated to
deliver different types of network traffic, with their specific QoS needs.
Especially in peering connections between ISPs, which should provide SLAs to
assess a global (albeit best-effort :) QoS between networks. Fully guaranteed
QoS was and will be assured <strong>only</strong> into walled gardens.</p>


<p>Another approach to shorten routing paths and single-point network load is
to use a <a
href="http://en.wikipedia.org/wiki/Distributed_hash_table">distributed hash
table</a>, or <span class="caps">DHT</span> in short, that implements a
decentralized distributed infrastructure upon which can be built efficient
services like distributed file systems, peer-to-peer sharing, and in general
content distribution systems. <a
href="http://www.bittorrent.com/">bittorrent</a> is an example of <span
class="caps">DHT</span>, as is the <a
href="http://en.wikipedia.org/wiki/Kademlia">Kademlia</a> used by the popular
<a href="http://emule-project.net/">emule</a> file-sharing software. Another
example is <a href="http://tools.ietf.org/html/draft-ietf-p2psip-sip-01"><span
class="caps">RELOAD</span></a>, currently (still) in draft status, used to
implement peer-to-peer <a
href="http://en.wikipedia.org/wiki/Session_Initiation_Protocol"><span
class="caps">SIP</span></a>, and so a decentralized VoIP infrastructure with no
big name behind it. I&#8217;m no surprised that <span
class="caps">RELOAD</span> and <span class="caps">P2PSIP</span> weren&#8217;t
mentioned in the talk.</p>


<p>Of course neither NGNs neither <span class="caps">P2P</span>/CDN
technologies will cover the entire internet in no time: the good &#8216;ol net
will <em>float</em> upon these new technologies and on legacy ones (such as
IPv4) in the next years, because changing network infrastructure imposes heavy
costs on ISPs. One may ask whether also content providers should contribute to
network infrastructure development, as they&#8217;re the ones that would
benefit from wider BW and lower latency. Prof. Trecordi said yes, <a
href="http://precursorblog.com/content/google-uses-21-times-more-bandwidth-it-pays-first-ever-research-study">google
uses 21 times more bandwidth it pays for</a>. Hell. LaTeX isn&#8217;t enough to
make content, mr Ph.D. <a
href="http://precursorblog.com/content/google-uses-21-times-more-bandwidth-it-pays-first-ever-research-study#comment-4558">This
comment</a> explains my point of view on this matter, and was also exposed
later by a member of the audience.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/bandwidth-usage-p2p.png"
alt="" /></p>


<p style="text-align:right;"><cite>Source: <a
href="http://www.fub.it/files/Slide_Trecordi_14_05_09.pdf">Trecordi&#8217;s
slides</a></cite></p>


<p>Whichever networking infrastructure we may adopt in the future, we cannot
prescind from a plain fact: just a minority of the users will consume the
majority of the bandwidth.. as happened with Napster in 2000, when because of
<a href="http://en.wikipedia.org/wiki/Shawn_Fanning's">Shawn Fanning</a>
software was allegedly consuming <a
href="http://en.wikipedia.org/wiki/Napster#cite_ref-2">80% of the aggregate
external bandwidth</a> of his <a
href="http://en.wikipedia.org/wiki/Northeastern_University">college</a>.
Considering this scenario, the speaker argued that it is reasonable for ISPs to
put caps on specific services (file sharing über alles) to limit the &#8220;all
you can eat&#8221; model, because the few users making a massive use actually
could impact the ones using fewer resources. I&#8217;ve got mixed opinions
about this, because ISPs too often cross the line.. and reasonable caps can too
easily become <strong>unacceptable</strong> ones.</p>


<p>Then the professor talked about <a
href="http://en.wikipedia.org/wiki/Proactive_network_Provider_Participation_for_P2P"><span
class="caps">P4P</span></a> as a possible mitigation factor of network
congestion. <span class="caps">P4P</span> means that ISPs collaborate with
bittorrent clients implementors to develop custom versions to <em>optimize</em>
P2P connections between customers. What is this <em>optimization</em> about? In
short, to not favor the fastest clients, but the <em>nearest</em> ones, in
terms of routing hops. This happens via a dedicated iTracker set up by the
<span class="caps">ISP</span> (ouch!) that contains additional information
about the physical location of clients, and can thus direct <span
class="caps">P2P</span> connections to the nearest ones.</p>


<p>The <a
href="http://torrentfreak.com/uncovering-the-dark-side-of-p4p-080824/">dark
side of <span class="caps">P4P</span></a>, as Ernesto&#8217;s Torrentfreak
founder points out, is that it can open a big can of worms, because the <span
class="caps">P4P</span> working group <a
href="http://www.awesomehighlighter.com/page/display/S4E2UjZZH">&quot;includes
some prominent members of the entertainment industry and well known anti-piracy
lobbyists&quot;</a> (sorry but the highlighter didn&#8217;t work well on this
page). I&#8217;m unable to say Ernesto is  wrong, also because of statement
like the one Sony pictures <span class="caps">CEO</span> said yesterday May 15
2009: <a
href="http://www.boingboing.net/2009/05/15/sony-pictures-ceo-no.html">&quot;<cite>nothing
good has come from the internet, period.</cite>&quot;</a>. Heh. No
comments.</p>


<p>Then, <span class="caps">DPI</span> (Deep Packet Inspection). Can ISPs use
it? And for which purposes? Security? Well, it could work, as long as automated
procedures filter <span class="caps">SPAM</span> and Virii out of residential
networks, ok.. but AT&#38;T has used <a
href="http://en.wikipedia.org/wiki/Narus">Narus</a> and split fibers to <a
href="http://en.wikipedia.org/wiki/Deep_packet_inspection#United_States">identify
and collect VoIP calls</a> data bits, <span class="caps">DPI</span> can also be
used to deliver <a
href="http://www.itworld.com/internet/66943/att-sends-mixed-message-behavioral-advertising">targeted
advertising</a>, and can be abused way too easily: In Italy we had the infamous
<a
href="http://www.infoworld.com/t/business/telecom-italia-embroiled-in-new-espionage-scandal-999">Tiger
Team</a> espionage scandal, so we need precise rules to regulate these possibly
evil technologies, and make sure ISPs respect them. We need a huge dose of
<strong>Faith</strong>, I&#8217;d guess.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/have-faith.jpg"
alt="" /></p>


<p style="text-align:right;"><cite>Photo by <a
href="http://www.flickr.com/photos/shrued/108950211/">shrued</a></cite></p>


<h2>Round table with telcos spokesmen</h2>


<p>This was the really interesting part of the event: seeing men that represent
telcos speak to each other about Internet matters, and referring each other as
the companies they represent. Quite funny, considering the quite complicated
status quo here in Italy (governative concessions, last mile cables owned by a
single company for historic reasons, and so on).</p>


<p>The involved parties (and condensed key points) were:</p>


<ul> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/vodafone.png"
alt="" /><br/><a
href="http://www.linkedin.com/pub/paolo-di-domenico/5/267/95">Paolo di
Domenico</a> &#8211; <a href="http://www.vodafone.it/">Vodafone</a> &#8211;
<em>(Score: 3)</em> <ul> <li>Heavy internet users should not be able to degrade
user experience for other customers</li> <li>We won&#8217;t block traffic on an
application basis</li> <li>We should be able to manage traffic load and put
caps when we&#8217;re over capacity</li> <li>SLAs and TOSs trasparency is a
must</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/tre.png"
alt="" /><br/>Anton Giulio Lombardi &#8211; <a
href="http://www.tre.it/">Tre</a> &#8211; <em>(Score: 3)</em> <ul> <li>Devices
are <a href="http://www.apple.com/iphone">iMproving</a> and becoming
multi-connected (wifi, gsm, hsdpa), this implies convergence of services that
today are separated (telephony and internet)</li> <li>Frequencies: on May 6th
2009 in Italy has been voted a law proposal that if will pass, mobile operators
will be allowed to make a broader use of frequencies than now</li> <li>Content
is being partitioned by the producers in order to get more revenue;
multi-connected devices which kind of access do they provide? E.g. a PC with an
<span class="caps">HSDPA</span> module which kind of access does provide?
Broadband?  <span class="caps">UMTS</span>? We need sane regulations in order
to alleviate load on the mobile operators, or everyone will start using
non-compatible platforms. (I really could not understand his point).</li>
<li>On regulations again: people could use our mobile phones (70M in Italy) for
payment, but legislation is not ready. Also, our company broadcasts <a
href="http://www.rai.it/"><span class="caps">RAI</span></a> television via
<span class="caps">DVBH</span>, but <span class="caps">RAI</span> does not
broadcast itself. Quite odd.</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/wind.png"
alt="" /><br/><a
href="http://www.key4biz.it/Who_is_who/2008/09/Mosca_Raffaele.html">Raffaele
Mosca</a> &#8211; <a href="http://www.wind.it/">Wind</a> &#8211; <em>(Score:
3)</em> <ul> <li>Neutrality is the common basis upon which to start any further
discussion. We cannot block access to a site like <a
href="http://www.cnn.com/"><span class="caps">CNN</span></a> or <a
href="http://english.aljazeera.net/">Al Jazeera</a> for any reason</li> <li>We
could define a greatest common divisor in a service set that gives neutrality
and doesn&#8217;t need QoS. Because IP is a best-effort protocol, no one should
invest in network resources not efficiently used (because of file sharing,
editor&#8217;s note).</li> <li>In the end, we need a sane and precise
regulation, because in a multiplayer business context everyone tries to feather
his own nest (and I hate this status quo, editor&#8217;s note)</li> </ul> </li>
<li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/telecom-w.png"
alt="" /><br/><a
href="http://www.key4biz.it/Who_is_who/2008/06/Nocentini_Stefano.html">Stefano
Nocentini</a> &#8211; <a href="http://www.telecomitalia.it/">Telecom Italia</a>
&#8211; <em>(Score: 5, Insightful)</em> <ul> <li>Think about the internet as an
highway, so we can elucubrate more thoughtly.  <ul> <li>Speed limits equal BW
limits, because you can reach them, but not when there&#8217;s a traffic
jam.</li> <li>An highway is sized upon a mean usage, and so is the network
infrastructure: so the idea of an &#8220;intelligent departure&#8221;, if you
plan your trip in hot hours, you&#8217;ll be likely to be slowed down by
jams.</li> <li>Neutrality: there are laws that deny trucks access to highways
in &#8220;hot&#8221; weekends, except those that carry perishable goods. This
is institutional regulation, not <span class="caps">ISP</span> one.</li>
<li>Costs are spread through multiple factors (distance, vehicle type,
etc)</li> <li><span class="caps">DPI</span>: recently italian highways
introduced <a href="http://en.wikipedia.org/wiki/SPECS_(speed_camera">speed
cameras</a>), that&#8217;s the perfect parallel to <span
class="caps">DPI</span> on packet networks!</li> <li>Digital divide: not every
town is reached by an highway, just like DSLs (but it&#8217;s a shame,
editor&#8217;s note).</li> </ul> </li> <li>Conclusion: we need sane regulations
designed by a scientific round table, and such regulations must be kept
up-to-date, because the Internet ecosystem is constantly evolving.</li>
<li><em>Applause</em>.</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/fastweb.png"
alt="" /><br/><a
href="http://www.linkedin.com/pub/roberto-scrivo/5/19b/87a">Roberto Scrivo</a>
&#8211; <a href="http://www.fastweb.it/">Fastweb</a> &#8211; <em>(Score:
1)</em> <ul> <li>We need regulations</li> <li>We suffer from tech-savvyness
failure</li> <li>Neutrality isn&#8217;t the problem here, it&#8217;s just
management</li> <li>We&#8217;ll implement NGNs when they&#8217;ll be
profitable</li> </ul></li> </ul>


<p>And eventually <a
href="http://www.linkedin.com/pub/eugenio-prosperetti/0/424/6a4">Eugenio
Prosperetti</a> from the <a
href="http://www.isimm.it/chisiamo/chisiamo.php"><span
class="caps">ISIMM</span></a> (Hey guys, fix the encoding on your web site ;)
made a recap of the concepts expressed by the telco spokesmen and stressed on
the need of accessibility of a service that is becoming a common facility to
get the work done. We need 4G, we need fiber, and the state should promote
these issues (and not demonize the Internet, editor&#8217;s note).</p>


<h2>Politics</h2>


<div style="float:right;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/gentiloni.jpg"
alt="" /></div> 

<p><a href="http://www2.paologentiloni.it/">Paolo Gentiloni</a>, former
telecommunications minister, said that the State is not just watching:
it&#8217;ll have a prominent role in the future. He said that Microsoft <a
href="http://www.readwriteweb.com/archives/microsoft_europe_internet_usage_will_overtake_trad.php">reported</a>
that in 2010 internet usage will overtake traditional TV, and as such work load
on the Public Administration will rise, also because the PA missed it (hey this
reminds me when Microsoft&#8217;s Ballmer stated that <a
href="http://www.pcmag.com/article2/0,2817,2331369,00.asp">we missed the
internet</a>). He also reminded of a <a
href="http://borsaitaliana.it.reuters.com/article/businessNews/idITMIE52C0K820090313">Caio
Report</a> that promises <a
href="http://ict.asca.it/interna.php?articolo=BANDA_LARGA__ECCO_IL_RAPPORTO_CAIO&amp;idnotizia=1085&amp;sezione=news">to
cover 99% of the population with <span class="caps">DSL</span> or fiber</a>
within 2011, if works will start in June 2009 (we&#8217;ll see, editor&#8217;s
note).</p>


<blockquote> <strong><span class="caps">UPDATE</span></strong>: The Caio Report
was <a
href="https://www.wikileaks.org/wiki/Comparing_broadband_in_Italy_with_other_countries:_Francesco_Caio_report:_Portare_l%27Italia_verso_la_leadership_europea_nella_banda_larga:_Considerazioni_sulle_opzioni_di_politica_industriale%2C_12_Mar_2009">leaked
on wikileaks</a> on May 15, 2009 (thanks <a
href="http://blog.quintarelli.it/blog/2009/05/online-il-rapporto-caio.html">Quinta</a>
for sharing).  </blockquote>

<p>It&#8217;s difficult for EU to implement infrastructure development
practices like Asian ones, where the State takes decisions and businesses
execute them.. because in a capitalistic world the only thing that counts is
<span class="caps">ROI</span>. We need to find a sane equilibrium for everyone,
and we&#8217;re working on this.</p>


<h2>Conclusions</h2>


<p>In a nutshell, the event was interesting, a bit pleonastic because the same
topics were carried over and over through the day, and it was an assessment of
the current situation (un-chartered territory) but at least I heard politicians
say &#8220;yes the internet is important, is valuable, and is worth
pushing&#8221;. I don&#8217;t remember how many times I said these words in the
past.</p>


<p>Hope you had a nice read, and congratulations that you made it!</p>
