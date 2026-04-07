---
date: 2009-05-16T02:00:00
title: Le basi concettuali e l'economia della neutralita' della rete [Parte 1] - 14 maggio 2009, Roma
tags: [politics, networking]
categories: [politics]
---

<p><a
href="http://www.fub.it/events/seminari/neutralitadellareteeaspettisocioeconomici">http://www.fub.it/events/seminari/neutralitadellareteeaspettisocioeconomici</a></p>


<p><a href="http://www.nnsquad.it/">http://www.nnsquad.it/</a></p>


<h2>Neutralita' &#8211; <em>&#8220;L'economia si sta dematerializzando&#8221;</em></h2>


<p>Sollecitato da un messaggio Facebook inviato il 6 maggio 2009 a tutti i
membri del gruppo <a
href="http://www.facebook.com/group.php?gid=56353912528">nnsquad.it &#8211; per
un Internet neutrale</a>, mi sono imbattuto in questo evento interessante a cui
ho avuto l'occasione di partecipare, tenutosi nel <a
href="http://en.wikipedia.org/wiki/Palazzo_Pallavicini-Rospigliosi">seicentesco
palazzo Rospigliosi</a> nel cuore di <a
href="http://en.wikipedia.org/wiki/Rome">Roma</a>.</p>


<p style="text-align:center;"><img src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-rome/IMG_0261.jpg" alt="" /></p>


<p style="text-align:right;"><em>Nella foto: <a
href="http://kennethrcarter.com/vita/">Kenneth Carter</a> e <a
href="http://blog.quintarelli.it/">Stefano Quintarelli</a></em></p>


<p><a name="continue"></a> La premessa era promettente: tecnici, dottori di
ricerca, portavoce delle telco e politici che parlano di internet, della sua
liberta' innata, e di come conciliarla in una societa' dove le misure di
sicurezza <a href="http://sniffo.org/node/22">aumentano costantemente</a>, e
come tali contrastano con un mondo virtuale senza barriere di sorta. Inoltre,
e' un'arena virtuale in cui tutto puo' essere gratuito, <a
href="http://thepiratebay.org/">non solo le informazioni</a>, e le persone ci
si stanno abituando.</p>


<p>Il primo intervento e' stato tenuto dal prof. <a
href="http://kennethrcarter.com/vita/">Kenneth Carter</a>, direttamente dalla
Columbia University, e ha fatto da ampia introduzione alle tematiche esplorate
(e talvolta ripetute) durante la giornata. In breve, la grande domanda e': gli
ISP possono offrire diversi gradi di performance su diversi siti (o far pagare
per performance migliori), permettere/bloccare/sovraccaricare l'accesso a certi
siti o da certi dispositivi?</p>


<p>Filtrare l'accesso ai servizi di rete e' una pratica comune su internet,
come lo e' filtrare i contenuti, e non necessariamente cattiva: pensate ai
filtri antispam per prevenire <span class="caps">UCE</span> e ai filtri dei
<span class="caps">NAP</span> per prevenire e mitigare attacchi <span
class="caps">DDOS</span>, o ai sistemi antivirus/IDS. Anche i piani di
servizio differenziati, dove ottieni latenza piu' bassa o maggiore banda in
upload pagando di piu', sono accettabili, perche' la &#8220;qualita' del
servizio&#8221; non e' un valore assoluto: dipende dal tipo di servizi che
l'utente usa. E nella maggior parte dei casi, l'utente non coglie (e nemmeno
ha bisogno di cogliere) i concetti che ci stanno dietro.</p>


<p>Ma cosa succede quando l'<span class="caps">ISP</span> supera il limite e
inizia a bloccarti il software <span class="caps">VPN</span>, o il tuo <a
href="http://www.nexlab.it/index.php/2007/05/03/fastweb-e-voip-sip-come-dicevano-una-volta-vorrete-dirlo-a-tutti-no">centralino
<span class="caps">VoIP</span></a>, o ti mette in una grande rete metropolitana
rendendo le tue macchine inaccessibili da internet, e facendoti pagare <a
href="http://aziende.fastweb.it/offerta/micro_imprese/ser_opzint_ip.html">un
sacco di soldi</a> per comprare un indirizzo IP pubblico (e per 10 giorni al
massimo)? Ok, la carenza di indirizzi IPv4 e' in arrivo, ma ce ne sono ancora
tanti disponibili, e usare sottoreti <span class="caps">IPTV</span> legacy per
indirizzare i clienti residenziali non e' una soluzione intelligente a lungo
termine.</p>


<p>Le <a href="http://en.wikipedia.org/wiki/Next_Generation_Networking">reti di
nuova generazione</a> puntano a risolvere i problemi di indirizzamento tramite
IPv6 e i suoi indirizzi di rete a 128 bit, e quelli di banda/latenza tramite
pipe (in fibra) separate, tutte dedicate a diversi tipi di dati, ad es.
VoIP/IPTV: questo e' quello che verra' chiamato &#8220;IP
frazionato&#8221;.</p>


<p style="text-align:center;"><img src="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-rome/ngn-pipes.png" alt="" /></p>


<p>Fintanto che la concorrenza rimane in piedi, applicare sovrapprezzi per QoS
e banda garantite su certi servizi e' una pratica che puo' effettivamente
migliorare l'esperienza utente: i gamer hanno aspettative completamente diverse
da chi usa solo l'&#8220;e-mail&#8221;, e i primi pagheranno volentieri di piu'
per DSL Fast-path per distruggere i propri amici, mentre i geek si godono un
indirizzo IP statico per raggiungere il loro server a casa quando sono in
giro. Partizionare le risorse su richiesta dell'utente puo' farne un uso piu'
redditizio ed efficiente, purche' sia fatto in modo intelligente e
<strong>trasparente</strong> per gli utenti. Quando la trasparenza viene meno,
si ottiene il contraccolpo che <a
href="http://en.wikipedia.org/wiki/Comcast#Network_neutrality">Comcast ha
ricevuto quando ha iniziato a bloccare il software di file sharing</a>. Anche
in Italia un <a href="http://www.tele2.it/">provider noto per le sue telefonate
moleste ai potenziali clienti</a> attualmente implementa <a
href="http://www.linkedin.com/pub/dir/samuele/fogagnolo">filtraggio a livello
7</a> per bloccare il file sharing e &#8220;sovraccaricare&#8221; la sua banda
limitata, dando cosi' un servizio scadente ai propri utenti.</p>


<p>Il punto chiave, secondo me, riguarda la mancanza di competenza
tecnologica: nessuno qui capisce niente di un mezzo (e della sua
infrastruttura) che sta diventando, piu' velocemente di qualsiasi cosa nella
storia, enormemente rilevante nella vita quotidiana.</p>


<p>Saggiamente, il prof. Carter ha identificato le questioni di neutralita'
come il <a
href="http://en.wikipedia.org/wiki/Blind_Men_and_an_Elephant">classico
problema dell'elefante e dei ciechi</a>: ogni lato del problema puo' essere
affrontato da una prospettiva completamente diversa, portando ad analisi e
possibili soluzioni completamente diverse. Ha fatto distinzioni tra conflitti
verticali (ISP vs. utente), orizzontali (utente vs. utente / <span
class="caps">ISP</span> vs. <span class="caps">ISP</span>) e diagonali
(utente sull'<span class="caps">ISP A</span> impatta sull'<span
class="caps">ISP B</span>, e cosi' via).</p>


<p>Applauso per il prof. Carter, che lascia il palco a <a
href="http://blog.quintarelli.it/">Stefano Quintarelli</a> di <a
href="http://www.nnsquad.it/">nnsquad.it</a>. Ha identificato nella <a
href="http://www.fub.it/files/Slide_Quintarelli_14_05_09.pdf">sua
presentazione</a> cinque punti chiave su cui costruire un &laquo;Internet
neutrale senza restrizioni assurde&raquo;:</p>


<ul> <li>Trasparenza: l'<span class="caps">ISP</span> deve fornire al cliente
dichiarazioni precise sulle sue politiche di regolazione/filtraggio del
traffico;</li> <li>Libera scelta: ogni volta che l'<span
class="caps">ISP</span> cambia le sue regole, l'utente deve avere il diritto
di essere informato e di mantenere quelle precedenti a cui si era
abbonato;</li> <li>Privacy: l'<span class="caps">ISP</span> non puo'
discriminare il traffico guardando il contenuto dei pacchetti;</li> <li>Gli ISP
non possono discriminare il traffico su base individuale</li> <li>Ogni volta
che un <span class="caps">ISP</span> applica discriminazione del traffico
prevista nel contratto utente, lo stesso trattamento deve essere applicato al
traffico proveniente da altre reti. Non applicare questo principio e' un
esempio del conflitto diagonale esposto dal prof. Carter.</li> </ul>


<p>Inoltre, come spesso accade nelle grandi aziende, l'innovazione tecnologica
viene bloccata da ROI possibilmente incerti: Stefano ha parlato di un progetto
di <a href="http://en.wikipedia.org/wiki/Mesh_network">rete <span
class="caps">MESH</span></a> <a
href="http://www.assisiwireless.com/tecnologia.html">ad Assisi</a>, dove una
rete wireless auto-rigenerante ha una banda aggregata pari alla somma delle
bande dei nodi. Le grandi aziende hanno tecnologie standard e grandi
infrastrutture, ma questo non significa che piccole aziende guidate da
visionari non possano competere con loro. E qui inizia il prossimo argomento,
con un intervento tenuto da <a
href="http://www.fub.it/files/Slide_Menaglia_14_05_09.pdf">Franco Menaglia
della fondazione Bordoni</a></p>


<h2>Economia</h2>


<p>La <a href="http://www.fub.it/">fondazione Bordoni</a> `acts_as_consultant`
per la pubblica amministrazione italiana in materia di <span
class="caps">ICT</span>. Il dott. Menaglia riconosce che e' un dibattito molto
complicato e attuale, principalmente perche' non e' un semplice scambio di
opinioni tra tecnologia e mercato, ma perche' da questa questione dipendono
investimenti di milioni di euro pubblici. Senza dimenticare che l'<span
class="caps">ICT</span> e' una delle chiavi principali dello sviluppo UE, che
avviene tramite applicazioni e servizi innovativi.</p>


<p>&#8220;La neutralita' non puo' prescindere dallo sviluppo economico&#8221;,
afferma, e per chiedere agli utenti di pagare di piu' per avere servizi
migliori, gli utenti devono effettivamente <strong>percepire</strong> che la
qualita' del servizio e' migliorata, e per erogare piu' dati rapidamente serve
un'infrastruttura piu' potente. Chi la paga? Gli ISP di sicuro, ma anche i
content provider potrebbero fare la loro parte (ad es. Google).</p>


<p>La chiave qui e' tutta sui business model: la pubblicita' sta morendo, e non
per colpa di AdBlock Plus, ma perche' i modelli comportamentali sono cambiati,
e secondo me <span class="caps">SPAM</span> e phishing giocano un ruolo
importante nel far sentire l'utente a disagio e riluttante ad accettare offerte
su un qualche sito internet a caso. Quindi dobbiamo trovare business model piu'
redditizi ed efficienti, pensando a internet come un ecosistema, cercando di
non spingere solo sulla propria azienda, e migliorando sia la competitivita'
che l'innovazione attraverso l'interoperabilita'.</p>


<p>In breve, non c'era molto contenuto ne' nella presentazione ne' nella
discussione, perche', come ha dichiarato l'<a
href="http://en.wikipedia.org/wiki/Eric_E._Schmidt">AD di Google</a>
commentando il report Q1 2009 nel contesto della crisi finanziaria mondiale, <a
href="http://awurl.com/FgYWkh9Ey#first_awesome_highlight">siamo in un
territorio inesplorato</a>. Penso che le persone intelligenti vinceranno alla
fine, perche' inventeranno il servizio di nuova generazione che non ha bisogno
ne' di bassa latenza ne' di alta banda e sara' estremamente utile ai propri
utenti. Qualcosa capace di raggiungere <a href="http://facebook.com/">200
milioni di utenti in pochi anni</a> (e oltre) ed essere anche redditizio, senza
ricorrere alla pubblicita'.</p>


<p>Nella seconda parte di questo articolo, riassumero' la sessione
pomeridiana: e' iniziata con l'interessante intervento tecnico sulle reti di
nuova generazione di <a
href="http://www.fub.it/files/Slide_Trecordi_14_05_09.pdf">Vittorio
Trecordi</a> e la discussione aperta con cinque portavoce delle telco (<a
href="http://telecomitalia.it/">Telecom</a>, <a
href="http://www.tre.it/">Tre</a>, <a href="http://vodafone.it/">Vodafone</a>,
<a href="http://www.fastweb.it/">Fastweb</a> e <a
href="http://www.wind.it/">Wind</a>).</p>


<p>Restate sintonizzati.</p>


<blockquote> <strong><span class="caps">AGGIORNAMENTO</span></strong> 17 maggio
2009: la seconda parte e' disponibile: <a
href="/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2">https://sindro.me/posts/2009-05-16-the-conceptual-foundations-and-the-economics-network-neutrality-part-2</a>
</blockquote>
