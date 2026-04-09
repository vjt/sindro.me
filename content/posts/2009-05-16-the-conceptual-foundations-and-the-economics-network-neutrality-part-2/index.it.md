---
date: 2009-05-16T04:00:00
title: Le basi concettuali e l'economia della neutralita' della rete [Parte 2] - 14 maggio 2009, Roma
tags: [politics, networking]
---

<p>Questa e' la seconda parte del mio resoconto del convegno <a
href="http://www.nnsquad.it/">nnsquad.it</a> tenutosi a Roma il 14 maggio 2009,
ospitato dalla fondazione di consulenti <span class="caps">ICT</span> <a
href="http://www.fub.it/">Fondazione Ugo Bordoni</a>.</p>


<p>Nella <a
href="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-rome">prima
parte</a> ho descritto la sessione mattutina, dedicata alla definizione della
neutralita' della rete e a come l'economia globale possa conciliarsi con essa.
Il pomeriggio e' stato dedicato a interventi piu' tecnici, e ho avuto
l'occasione di sentire le osservazioni dei portavoce delle telco sulla
situazione attuale e sui possibili sviluppi futuri.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/rospigliosi-palace-statues-room-nnsquad-convention.jpg"
alt="" /></p>


<p><a name="continue"></a> Il primo intervento e' iniziato alle 14:15 ed e'
stato tenuto dal prof. <a
href="http://www.sede-cremona.polimi.it/organizzazione/dettagli_docente.php?id_nav=6582&amp;aa=2008&amp;sede_cds=cr&amp;k_docente=176618&amp;n_docente=TRECORDI%20VITTORIO">Vittorio
Trecordi</a> (slide disponibili <a
href="http://www.fub.it/files/Slide_Trecordi_14_05_09.pdf">qui</a>). Lo ha
introdotto affermando che la net neutrality potrebbe potenzialmente contrastare
con lo sviluppo economico e le esigenze di sicurezza, a causa delle
intercettazioni necessarie per queste ultime, intercettazioni che sono
fortemente contrarie alla liberta' individuale di comunicare.</p>


<p>Stranamente (o forse no), non e' stato fatto alcun cenno ai modi attuali per
aggirare sia le intercettazioni che la localizzazione dei comunicanti: mi
riferisco al <a href="http://tor.eff.org/">progetto Tor</a>, il piu' noto
bastione che garantisce la privacy ed e' <a
href="https://www.torproject.org/about/overview.html.en">attualmente usato da
giornalisti che lavorano in zone &quot;calde&quot;</a>, tra molti altri.</p>


<p>Un altro punto sulla legislazione e' che non e' uguale in tutti i paesi,
sebbene Internet sia diffuso in tutto il mondo; inoltre dovremmo definire su
quali reti valutare la neutralita', perche' non necessariamente una rete IP e'
connessa a Internet (pensate ai walled garden di proprieta' degli <span
class="caps">ISP</span>).</p>


<p>Inoltre, di nuovo sulla Quality of Service: Trecordi ha affermato che
Internet ha avuto successo grazie al suo &quot;modello a clessidra&quot; e alla
&#8220;capacita' di disaccoppiare i servizi di comunicazione dall'infrastruttura
di rete&#8221;, ma i requisiti di QoS (ad es. per il VoIP) stressano la pila
protocollare, soprattutto dove i condotti di rete sono &#8220;in
overbooking&#8221;. Inoltre, anche l'overprovisioning fallisce, a causa
dell'architettura decentralizzata di Internet, e i colli di bottiglia si
trovano principalmente nei <a href="http://www.mix-it.net/">punti di
interconnessione tra ISP</a>.</p>


<p>Quindi, Internet e' una piattaforma best-effort, dove un <span
class="caps">ISP</span> non puo' controllare come i pacchetti dei suoi clienti
verranno trattati una volta varcati i suoi confini e raggiunto un provider
geograficamente distante. In quest'area risiede il modello di business delle <a
href="http://en.wikipedia.org/wiki/Content_delivery_network">content delivery
network</a>, che usiamo in modo trasparente ogni giorno per accedere a <a
href="http://facebook.com/">siti</a> <a href="http://www.cnn.com/">web</a>
molto trafficati, e che hanno anche causato qualche divertente malinteso in
passato, quando <a href="http://www.akamai.com/">Akamai</a> ha iniziato a fare
da proxy per <a href="http://www.microsoft.com/">Microsoft</a> con <a
href="http://squid-cache.org/">Squid</a> su Linux, e <a
href="http://news.netcraft.com/">Netcraft</a> ha mostrato nelle sue statistiche
che <a href="http://www.linuxjournal.com/article/4962">i server Microsoft
girano su Linux</a> :).</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/akamai-how-content-delivery-network-works.png" alt="" /></p>


<p style="text-align:right;"><cite>Fonte: <a
href="http://www.akamai.net/">Akamai</a></cite></p>


<p>A parte quella battuta divertente (del 2001), le <span
class="caps">CDN</span> accorciano il percorso di routing tra gli utenti e il
contenuto statico di un servizio, usando data center distribuiti
geograficamente che eseguono <a
href="http://varnish.projects.linpro.no/">Varnish</a> (o software equivalente)
e un server <span class="caps">DNS</span> con geolocalizzazione come <a
href="http://www.powerdns.com/">PowerDNS</a>. In questo modo, quando un client
qualsiasi cerca di risolvere un hostname, il <span class="caps">DNS</span>
risponde con l'indirizzo IP virtuale del datacenter piu' vicino, e poi serve il
contenuto dalla cache.</p>


<p>Questi sono approcci che cercano di mitigare la natura best-effort di
Internet, ma forse ci sono soluzioni migliori. Le <span class="caps">NGN</span>
puntano a essere una di queste, fornendo pipe di rete multiple dedicate a
erogare diversi tipi di traffico di rete, con le loro specifiche esigenze di
QoS. Specialmente nelle connessioni di peering tra ISP, che dovrebbero fornire
SLA per garantire una QoS globale (pur sempre best-effort :) tra le reti. QoS
pienamente garantita era ed e' assicurata <strong>solo</strong> nei walled
garden.</p>


<p>Un altro approccio per accorciare i percorsi di routing e il carico su
singoli punti della rete e' usare una <a
href="http://en.wikipedia.org/wiki/Distributed_hash_table">tabella hash
distribuita</a>, o <span class="caps">DHT</span> in breve, che implementa
un'infrastruttura distribuita decentralizzata sulla quale si possono costruire
servizi efficienti come file system distribuiti, condivisione peer-to-peer, e
in generale sistemi di distribuzione di contenuti. <a
href="http://www.bittorrent.com/">BitTorrent</a> e' un esempio di <span
class="caps">DHT</span>, come lo e' <a
href="http://en.wikipedia.org/wiki/Kademlia">Kademlia</a> usata dal popolare
software di file sharing <a href="http://emule-project.net/">eMule</a>. Un
altro esempio e' <a
href="http://tools.ietf.org/html/draft-ietf-p2psip-sip-01"><span
class="caps">RELOAD</span></a>, attualmente (ancora) in stato di draft, usato
per implementare <a
href="http://en.wikipedia.org/wiki/Session_Initiation_Protocol"><span
class="caps">SIP</span></a> peer-to-peer, e quindi un'infrastruttura VoIP
decentralizzata senza un grande nome dietro. Non mi sorprende che <span
class="caps">RELOAD</span> e <span class="caps">P2PSIP</span> non siano stati
menzionati nel talk.</p>


<p>Ovviamente ne' le NGN ne' le tecnologie <span
class="caps">P2P</span>/CDN copriranno l'intera internet in breve tempo: la
buona vecchia rete <em>galleggera'</em> su queste nuove tecnologie e su
quelle legacy (come IPv4) nei prossimi anni, perche' cambiare infrastruttura di
rete impone costi pesanti agli ISP. Ci si potrebbe chiedere se anche i content
provider dovrebbero contribuire allo sviluppo dell'infrastruttura di rete,
dato che sono loro a beneficiare di maggiore banda e minore latenza. Il prof.
Trecordi ha detto di si', <a
href="http://precursorblog.com/content/google-uses-21-times-more-bandwidth-it-pays-first-ever-research-study">Google
usa 21 volte piu' banda di quella che paga</a>. Cavolo. LaTeX non basta per
fare contenuti, signor Ph.D. <a
href="http://precursorblog.com/content/google-uses-21-times-more-bandwidth-it-pays-first-ever-research-study#comment-4558">Questo
commento</a> spiega il mio punto di vista sulla questione, ed e' stato esposto
anche da un membro del pubblico successivamente.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/bandwidth-usage-p2p.png"
alt="" /></p>


<p style="text-align:right;"><cite>Fonte: <a
href="http://www.fub.it/files/Slide_Trecordi_14_05_09.pdf">slide di
Trecordi</a></cite></p>


<p>Qualunque infrastruttura di rete adotteremo in futuro, non possiamo
prescindere da un fatto nudo e crudo: solo una minoranza degli utenti consumera'
la maggioranza della banda... come e' successo con Napster nel 2000, quando il
software di <a href="http://en.wikipedia.org/wiki/Shawn_Fanning's">Shawn
Fanning</a> si dice consumasse <a
href="http://en.wikipedia.org/wiki/Napster#cite_ref-2">l'80% della banda
esterna aggregata</a> del suo <a
href="http://en.wikipedia.org/wiki/Northeastern_University">college</a>.
Considerando questo scenario, il relatore ha sostenuto che e' ragionevole per
gli ISP mettere limiti su servizi specifici (file sharing uber alles) per
limitare il modello &#8220;all you can eat&#8221;, perche' i pochi utenti che
fanno un uso massiccio potrebbero effettivamente impattare quelli che usano meno
risorse. Ho opinioni contrastanti su questo, perche' gli ISP troppo spesso
superano il limite... e limiti ragionevoli possono troppo facilmente diventare
<strong>inaccettabili</strong>.</p>


<p>Poi il professore ha parlato di <a
href="http://en.wikipedia.org/wiki/Proactive_network_Provider_Participation_for_P2P"><span
class="caps">P4P</span></a> come possibile fattore di mitigazione della
congestione di rete. <span class="caps">P4P</span> significa che gli ISP
collaborano con gli implementatori di client BitTorrent per sviluppare versioni
personalizzate che <em>ottimizzino</em> le connessioni P2P tra i clienti. In
cosa consiste questa <em>ottimizzazione</em>? In breve, nel non favorire i
client piu' veloci, ma quelli piu' <em>vicini</em>, in termini di hop di
routing. Questo avviene tramite un iTracker dedicato configurato dall'<span
class="caps">ISP</span> (ahi!) che contiene informazioni aggiuntive sulla
posizione fisica dei client, e puo' cosi' indirizzare le connessioni <span
class="caps">P2P</span> verso quelli piu' vicini.</p>


<p>Il <a
href="http://torrentfreak.com/uncovering-the-dark-side-of-p4p-080824/">lato
oscuro del <span class="caps">P4P</span></a>, come sottolinea Ernesto fondatore
di Torrentfreak, e' che puo' aprire un vaso di Pandora, perche' il gruppo di
lavoro <span class="caps">P4P</span> <a
href="http://www.awesomehighlighter.com/page/display/S4E2UjZZH">&quot;include
alcuni membri prominenti dell'industria dell'intrattenimento e noti lobbisti
anti-pirateria&quot;</a> (scusate ma l'evidenziatore non ha funzionato bene su
questa pagina). Non posso dire che Ernesto abbia torto, anche per dichiarazioni
come quella fatta ieri 15 maggio 2009 dal <span class="caps">CEO</span> di Sony
Pictures: <a
href="http://www.boingboing.net/2009/05/15/sony-pictures-ceo-no.html">&quot;<cite>niente
di buono e' venuto da internet, punto.</cite>&quot;</a>. Eh. Nessun
commento.</p>


<p>Poi, <span class="caps">DPI</span> (Deep Packet Inspection). Gli ISP
possono usarla? E per quali scopi? Sicurezza? Be', potrebbe funzionare,
fintanto che procedure automatiche filtrano <span class="caps">SPAM</span> e
virus dalle reti residenziali, ok... ma AT&#38;T ha usato <a
href="http://en.wikipedia.org/wiki/Narus">Narus</a> e fibra sdoppiata per <a
href="http://en.wikipedia.org/wiki/Deep_packet_inspection#United_States">identificare
e raccogliere dati di chiamate VoIP</a>, la <span class="caps">DPI</span> puo'
anche essere usata per erogare <a
href="http://www.itworld.com/internet/66943/att-sends-mixed-message-behavioral-advertising">pubblicita'
mirata</a>, e puo' essere abusata fin troppo facilmente: in Italia abbiamo
avuto il famigerato scandalo di spionaggio del <a
href="http://www.infoworld.com/t/business/telecom-italia-embroiled-in-new-espionage-scandal-999">Tiger
Team</a>, quindi abbiamo bisogno di regole precise per regolamentare queste
tecnologie potenzialmente pericolose e assicurarci che gli ISP le rispettino.
Serve una dose enorme di <strong>Fede</strong>, direi.</p>


<p style="text-align:center;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/have-faith.jpg"
alt="" /></p>


<p style="text-align:right;"><cite>Foto di <a
href="http://www.flickr.com/photos/shrued/108950211/">shrued</a></cite></p>


<h2>Tavola rotonda con i portavoce delle telco</h2>


<p>Questa era la parte davvero interessante dell'evento: vedere uomini che
rappresentano le telco parlare tra di loro di questioni legate a Internet, e
riferirsi l'un l'altro come le aziende che rappresentano. Piuttosto divertente,
considerando lo status quo piuttosto complicato qui in Italia (concessioni
governative, cavi dell'ultimo miglio di proprieta' di una sola azienda per
ragioni storiche, e cosi' via).</p>


<p>Le parti coinvolte (e i punti chiave condensati) erano:</p>


<ul> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/vodafone.png"
alt="" /><br/><a
href="http://www.linkedin.com/pub/paolo-di-domenico/5/267/95">Paolo di
Domenico</a> &#8211; <a href="http://www.vodafone.it/">Vodafone</a> &#8211;
<em>(Punteggio: 3)</em> <ul> <li>Gli utenti pesanti non dovrebbero poter
degradare l'esperienza degli altri clienti</li> <li>Non bloccheremo il traffico
su base applicativa</li> <li>Dovremmo poter gestire il carico di traffico e
mettere limiti quando siamo oltre capacita'</li> <li>La trasparenza di SLA e
TOS e' un must</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/tre.png"
alt="" /><br/>Anton Giulio Lombardi &#8211; <a
href="http://www.tre.it/">Tre</a> &#8211; <em>(Punteggio: 3)</em> <ul> <li>I
dispositivi stanno <a href="http://www.apple.com/iphone">migliorando</a> e
diventando multi-connessi (wifi, gsm, hsdpa), questo implica convergenza di
servizi che oggi sono separati (telefonia e internet)</li> <li>Frequenze: il 6
maggio 2009 in Italia e' stata votata una proposta di legge che, se approvata,
permettera' agli operatori mobili di fare un uso piu' ampio delle frequenze di
quanto sia possibile ora</li> <li>I contenuti vengono partizionati dai
produttori per ottenere piu' ricavi; i dispositivi multi-connessi che tipo di
accesso forniscono? Ad es. un PC con un modulo <span class="caps">HSDPA</span>
che tipo di accesso fornisce? Broadband? <span class="caps">UMTS</span>?
Servono regolamentazioni sensate per alleggerire il carico sugli operatori
mobili, o tutti inizieranno a usare piattaforme non compatibili. (Davvero non
ho capito il suo punto).</li> <li>Di nuovo sulle regolamentazioni: le persone
potrebbero usare i nostri cellulari (70M in Italia) per i pagamenti, ma la
legislazione non e' pronta. Inoltre, la nostra azienda trasmette la televisione
<a href="http://www.rai.it/"><span class="caps">RAI</span></a> via <span
class="caps">DVBH</span>, ma la <span class="caps">RAI</span> non trasmette da
sola. Piuttosto strano.</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/wind.png"
alt="" /><br/><a
href="http://www.key4biz.it/Who_is_who/2008/09/Mosca_Raffaele.html">Raffaele
Mosca</a> &#8211; <a href="http://www.wind.it/">Wind</a> &#8211;
<em>(Punteggio: 3)</em> <ul> <li>La neutralita' e' la base comune da cui
partire per qualsiasi ulteriore discussione. Non possiamo bloccare l'accesso a
un sito come <a href="http://www.cnn.com/"><span class="caps">CNN</span></a> o
<a href="http://english.aljazeera.net/">Al Jazeera</a> per nessun motivo</li>
<li>Potremmo definire un minimo comun denominatore in un insieme di servizi che
dia neutralita' e non necessiti di QoS. Dato che IP e' un protocollo
best-effort, nessuno dovrebbe investire in risorse di rete non usate
efficientemente (a causa del file sharing, nota del redattore).</li> <li>Alla
fine, servono regolamentazioni sane e precise, perche' in un contesto
commerciale con piu' attori ognuno cerca di tirare l'acqua al proprio mulino (e
odio questo stato di cose, nota del redattore)</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/telecom-w.png"
alt="" /><br/><a
href="http://www.key4biz.it/Who_is_who/2008/06/Nocentini_Stefano.html">Stefano
Nocentini</a> &#8211; <a href="http://www.telecomitalia.it/">Telecom Italia</a>
&#8211; <em>(Punteggio: 5, Perspicace)</em> <ul> <li>Pensate a Internet come
un'autostrada, cosi' possiamo ragionare meglio. <ul> <li>I limiti di velocita'
equivalgono ai limiti di banda, perche' puoi raggiungerli, ma non quando c'e'
un ingorgo.</li> <li>Un'autostrada e' dimensionata su un utilizzo medio, e cosi'
e' l'infrastruttura di rete: quindi l'idea di una &#8220;partenza
intelligente&#8221;, se pianifichi il viaggio nelle ore di punta, e' probabile
che verrai rallentato dagli ingorghi.</li> <li>Neutralita': ci sono leggi che
vietano ai camion l'accesso alle autostrade nei weekend &#8220;caldi&#8221;,
tranne quelli che trasportano merci deperibili. Questa e' regolamentazione
istituzionale, non dell'<span class="caps">ISP</span>.</li> <li>I costi sono
distribuiti su piu' fattori (distanza, tipo di veicolo, ecc.)</li> <li><span
class="caps">DPI</span>: recentemente le autostrade italiane hanno introdotto
<a href="http://en.wikipedia.org/wiki/SPECS_(speed_camera">autovelox a
tratta</a>), e' il parallelo perfetto con la <span class="caps">DPI</span>
sulle reti a pacchetto!</li> <li>Digital divide: non tutti i comuni sono
raggiunti da un'autostrada, proprio come le DSL (ma e' una vergogna, nota del
redattore).</li> </ul> </li> <li>Conclusione: servono regolamentazioni sensate
progettate da una tavola rotonda scientifica, e tali regolamentazioni devono
essere tenute aggiornate, perche' l'ecosistema di Internet e' in costante
evoluzione.</li> <li><em>Applauso</em>.</li> </ul> </li> <li><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/fastweb.png"
alt="" /><br/><a
href="http://www.linkedin.com/pub/roberto-scrivo/5/19b/87a">Roberto Scrivo</a>
&#8211; <a href="http://www.fastweb.it/">Fastweb</a> &#8211; <em>(Punteggio:
1)</em> <ul> <li>Servono regolamentazioni</li> <li>Soffriamo di mancanza di
competenza tecnologica</li> <li>La neutralita' non e' il problema qui, e' solo
questione di gestione</li> <li>Implementeremo le NGN quando saranno
redditizie</li> </ul></li> </ul>


<p>E infine <a
href="http://www.linkedin.com/pub/eugenio-prosperetti/0/424/6a4">Eugenio
Prosperetti</a> dell'<a
href="http://www.isimm.it/chisiamo/chisiamo.php"><span
class="caps">ISIMM</span></a> (ragazzi, sistematevi l'encoding sul sito ;) ha
fatto un riepilogo dei concetti espressi dai portavoce delle telco e ha
insistito sulla necessita' di accessibilita' di un servizio che sta diventando
uno strumento comune per lavorare. Servono il 4G, serve la fibra, e lo Stato
dovrebbe promuovere queste questioni (e non demonizzare Internet, nota del
redattore).</p>


<h2>Politica</h2>


<div style="float:right;"><img
src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2/gentiloni.jpg"
alt="" /></div>

<p><a href="http://www2.paologentiloni.it/">Paolo Gentiloni</a>, ex ministro
delle telecomunicazioni, ha detto che lo Stato non sta solo a guardare: avra'
un ruolo prominente nel futuro. Ha detto che Microsoft ha <a
href="http://www.readwriteweb.com/archives/microsoft_europe_internet_usage_will_overtake_trad.php">riportato</a>
che nel 2010 l'uso di internet superera' la TV tradizionale, e come tale il
carico di lavoro sulla Pubblica Amministrazione aumentera', anche perche' la PA
se l'e' persa (ehi, questo mi ricorda quando Ballmer di Microsoft ha dichiarato
che <a href="http://www.pcmag.com/article2/0,2817,2331369,00.asp">abbiamo
mancato internet</a>). Ha anche ricordato un <a
href="http://borsaitaliana.it.reuters.com/article/businessNews/idITMIE52C0K820090313">Rapporto
Caio</a> che promette di <a
href="http://ict.asca.it/interna.php?articolo=BANDA_LARGA__ECCO_IL_RAPPORTO_CAIO&amp;idnotizia=1085&amp;sezione=news">coprire
il 99% della popolazione con <span class="caps">DSL</span> o fibra</a> entro il
2011, se i lavori inizieranno a giugno 2009 (vedremo, nota del
redattore).</p>


<blockquote> <strong><span class="caps">AGGIORNAMENTO</span></strong>: Il
Rapporto Caio e' stato <a
href="https://www.wikileaks.org/wiki/Comparing_broadband_in_Italy_with_other_countries:_Francesco_Caio_report:_Portare_l%27Italia_verso_la_leadership_europea_nella_banda_larga:_Considerazioni_sulle_opzioni_di_politica_industriale%2C_12_Mar_2009">pubblicato
su WikiLeaks</a> il 15 maggio 2009 (grazie <a
href="http://blog.quintarelli.it/blog/2009/05/online-il-rapporto-caio.html">Quinta</a>
per la condivisione). </blockquote>

<p>E' difficile per la UE implementare pratiche di sviluppo infrastrutturale
come quelle asiatiche, dove lo Stato prende decisioni e le imprese le
eseguono... perche' in un mondo capitalista l'unica cosa che conta e' il <span
class="caps">ROI</span>. Dobbiamo trovare un equilibrio sano per tutti, e ci
stiamo lavorando.</p>


<h2>Conclusioni</h2>


<p>In breve, l'evento e' stato interessante, un po' pleonastico perche' gli
stessi argomenti sono stati ripresi piu' e piu' volte durante la giornata, ed
e' stato un inquadramento della situazione attuale (territorio inesplorato), ma
almeno ho sentito politici dire &#8220;si', internet e' importante, ha valore,
e vale la pena investirci&#8221;. Non ricordo quante volte ho detto queste
parole in passato.</p>


<p>Spero sia stata una bella lettura, e complimenti per essere arrivati fino
alla fine!</p>
