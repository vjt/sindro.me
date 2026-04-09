---
date: 2009-04-26T23:00:00Z
title: "Facebook Developer Garage 2009, Milano (Italia)"
tags: [events, facebook, networking, social, web2.0]
---

<div style="float:left; margin:8px 10px 4px 0;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/logofb.jpg"/></div>

<p>Questo e' il mio resoconto del primo <a
href="http://fb.mikamai.com/programma/">facebook developer garage
italiano</a>, tenutosi a Milano il <a
href="http://www.facebook.com/event.php?eid=70473476888">23 aprile 2009</a>,
e ospitato da <a href="http://mikamai.com/">mikamai</a>. La mattina e' stata
dedicata alle sessioni per sviluppatori, il pomeriggio a quelle di marketing
&#38; comunicazione. Alcuni video dell'evento sono disponibili <a
href="http://qik.com/istintoweb">qui</a>.</p>


<h1>Mattina: sessione sviluppatori</h1>


<p>Il primo talk e' stato tenuto da <a
href="http://www.facebook.com/people/James-Leszczenski/4800348">James
Leszczenski</a>, ingegnere di Facebook, che ha presentato la visione, la
missione e i valori della <a
href="http://developers.facebook.com/connect.php">piattaforma connect</a>.
Interessante, oltre al talk in se', per la partecipazione del pubblico: la
platea era profondamente interessata a sapere <a
href="http://wiki.developers.facebook.com/index.php/Authenticating_Users_with_Facebook_Connect">quali
informazioni si ottengono</a> da Facebook, <a
href="http://wiki.developers.facebook.com/index.php/Facebook_Connect_Policies">come
gestirle</a>, e quali strumenti connect fornisce per <a
href="http://wiki.developers.facebook.com/index.php/Linking_Accounts_and_Finding_Friends">collegare
identita' e trovare amici</a> su un sito web abilitato.</p>


<p><a name="continue"></a> Piu' tardi ho avuto occasione di chiedere a <a
href="http://www.facebook.com/people/James-Leszczenski/4800348">James</a> se
FB fosse incline o meno ad adottare <a href="http://openid.net/">OpenID</a>
come metodo di autenticazione: ha detto che connect e OpenID permettono
entrambi agli utenti di avere credenziali di login uniche per accedere a piu'
siti, ma connect permette anche di sfruttare la potenza del social graph di
Facebook per consentire agli utenti di comunicare e condividere informazioni.
Quindi, la risposta breve e' &#8220;no&#8221;. Allora gli ho proposto di
implementare OpenID su FB stesso, cosi' che connect potesse diventare davvero
un superset di OpenID, ma ha risposto che &#8220;come azienda, queste sono
decisioni difficili e non posso dare una risposta adesso&#8221;. Comprensibile
:).</p>


<blockquote> <strong><span class="caps">AGGIORNAMENTO</span></strong>: il 27
aprile 2009, TechCrunch riporta di <em>aver sentito</em> che Facebook <a
href="http://www.techcrunch.com/2009/04/27/facebook-first-big-site-to-really-embrace-openid/">abbraccera'
OpenID</a> come mezzo per autenticare gli utenti. Ottime notizie, in attesa di
una dichiarazione ufficiale da Facebook! :) </blockquote>

<p>Il secondo talk e' stato tenuto da <a href="http://acinapura.com/">Vincenzo
Acinapura</a>, che ha descritto gli strumenti di base per creare
un'applicazione sulla piattaforma Facebook. Ha esplorato le tecnologie che ci
stanno dietro (<a
href="http://wiki.developers.facebook.com/index.php/XFBML"><span
class="caps">XFBML</span></a>, <a
href="http://wiki.developers.facebook.com/index.php/FQL"><span
class="caps">FQL</span></a>, <a
href="http://wiki.developers.facebook.com/index.php/FBJS"><span
class="caps">FBJS</span></a>), i principali <a
href="http://wiki.developers.facebook.com/index.php/Anatomy_of_a_Facebook_App">punti
di integrazione</a> all'interno della piattaforma (notifiche, publisher, ...) e
ha mostrato codice d'esempio per implementare alcuni dei tag <span
class="caps">FBML</span> piu' usati (<code>fb:comments</code>,
<code>fb:share</code>, <code>fb:feed</code>, <a
href="http://wiki.developers.facebook.com/wiki/FBML">e cosi' via</a>).
Infine ha ricordato l'importanza di automatizzare il deploy delle applicazioni,
e ha suggerito di usare <a href="http://www.capify.org/">capistrano</a> per
farlo.</p>


<p>Poi e' iniziato il <a href="http://fb.mikamai.com/programma/">Facebook Sumo
Contest</a>: tre sviluppatori avevano <del>un'</del> due ore per mettere
insieme un'applicazione Facebook funzionante che poi sarebbe stata giudicata dal
James di Facebook e dagli applausi del pubblico :). Alla fine solo due ce
l'hanno fatta, il primo era un ragazzo italiano che ha scritto un'app per fare
regali agli amici; il secondo un ragazzo francese (credo) che ha costruito
un'app per organizzare feste con gli amici, invitare gente e divertirsi. Ha
vinto il primo, ma secondo me almeno il secondo ha mostrato un po' piu' di
creativita'. Ovviamente entrambi sono stati vittime della <a
href="http://en.wikipedia.org/wiki/Murphy's_Law">legge di Murphy</a>, perche'
le app non hanno funzionato al primo colpo :).</p>


<p style="text-align:center;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/pilu_and_reggie.jpg"/></p>


<p><a href="http://qik.com/video/1529172">Terzo talk</a> di <a
href="http://www.linkedin.com/pub/2/129/894">Andrea Reginato</a> e <a
href="http://gravityblast.com/">Andrea Franz</a>, che hanno iniziato definendo
cosa significa <strong>virale</strong> e come il social graph possa permettere a
chiunque di distribuire contenuti a un numero molto grande di utenti. In breve,
fintanto che il tuo contenuto e' <a
href="http://modernl.com/article/how-to-write-great-headlines">ben
formulato</a> e interessante, la distribuzione passaparola tramite social
network, dove pubblicare contenuti e' &#8220;facile come bere un bicchier
d'acqua&#8221;, e' un modo potente per far arrivare il tuo contenuto a milioni
di persone potenzialmente interessate.</p>


<p>Come ottenerlo? Hanno esplorato come FB connect puo' arricchire i nostri
siti e dare agli utenti la possibilita' di commentare e interagire usando le
loro credenziali Facebook, e poi diffondere le interazioni tramite Facebook per
raggiungere un pubblico piu' ampio. Non e' scienza missilistica, ma dalla mia
esperienza funziona, purche' il contenuto sia di per se'
<strong>utile</strong> e <strong>di valore</strong>, e soprattutto non appaia
<strong>falso</strong> e come <strong>pubblicita'</strong> alla maggior parte
degli utenti. Penso che Facebook e <a href="http://twitter.com/">Twitter</a>
siano anche strumenti potenti per <a
href="http://monitter.com/">analizzare</a> e <a
href="http://hashtags.org/">identificare</a> quale tipo di contenuto e'
<strong>interessante</strong> adesso per le persone, e modellare la
distribuzione virale su queste intuizioni.</p>


<p>C'e' stata molta interazione con il pubblico, interessato principalmente a
come integrarlo nel proprio sito web mantenendo il proprio sistema di
registrazione/login, preoccupazioni sulla privacy, gestione e caching delle
informazioni (quali mettere in cache, come e per quanto tempo), e questioni
legali. Quando c'e' un reclamo su dati mostrati sul mio sito ma pubblicati e
ospitati sui server di Facebook, chi e' il referente legale da interpellare? Un
portavoce di <a href="http://civile.it/">civile.it</a> ha dichiarato che il
responsabile va individuato nel proprietario dei server su cui i dati sono
ospitati: e' Facebook stesso.</p>


<p>I due Andrea alla fine hanno mostrato un gioco demo per la piattaforma FB
costruito con <a href="http://sinatrarb.com/">sinatra</a>, <a
href="http://prototypejs.org/">prototype</a> e <a
href="http://wiki.developers.facebook.com/wiki/FBJS"><span
class="caps">FBJS</span></a>. L'app ti chiede di identificare uno dei tuoi
amici guardando un sottoinsieme di foto profilo: ogni volta che indovini (in
massimo 10 secondi), appare un'altra foto e la difficolta' aumenta. Il numero
di amici identificati determina il &#8220;livello&#8221;, che puoi pubblicare
sul tuo profilo una volta finito :).</p>


<p>Dopo il loro talk, abbiamo fatto la pausa pranzo e finalmente mi sono
riunito con un mio amico, arrivato in ritardo come al solito ;).</p>


<p style="text-align:center;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/relax_at_facebook_developer_garage_2009_in_milan.jpg"/></p>

<h1>Pomeriggio: marketing e comunicazione</h1>

<p>Il pomeriggio e' stato dedicato al marketing e alla comunicazione, e a tutti
i modi in cui si puo' sfruttare la piattaforma Facebook per portare traffico al
proprio sito, o per generare informazione virale attraverso le connessioni
sociali tra le persone, e ha presentato alcune case history degli autori
dell'applicazione <a
href="http://www.facebook.com/apps/application.php?id=8827826004">who has the
biggest brain</a>, &#8220;Ninja Marketing:http://ninjamarketing.it e i
creatori dell'applicazione <a href="http://www.cayenne.it/">skoda in love</a>
(cayenne marketing).</p>


<p>Per prima cosa, Lorenzo Viscanti (co-fondatore di mikamai) ha descritto come
le pagine Facebook possano aiutare i marketer a pubblicizzare contenuti e
analizzare il traffico degli utenti per migliorare le conversioni: dato che
Facebook permette agli utenti di inserire molte informazioni su se stessi,
questi dati possono essere aggregati e mostrati efficacemente nella sezione
statistiche di una pagina Facebook. Per una spiegazione piu' dettagliata,
consultate la <a
href="http://www.facebook.com/advertising/FacebookPagesProductGuide.pdf">guida
alle pagine Facebook</a> pubblicata a marzo 2009.</p>


<p>Poi, momento divertente, con la proiezione di un video dell'ironico cantante
neomelodico Manuele D&#8217;Amore, con la sua canzone <a
href="http://www.catepol.net/2009/03/28/facebook-neomelodico-lasciarsi-su-facebook/">lasciarsi
su facebook</a>. Per chi non conosce le canzoni neomelodiche napoletane, sono un
prodotto della cultura popolare napoletana di cui <a
href="http://en.wikipedia.org/wiki/Gigi_D'Alessio">Gigi D&#8217;Alessio</a> e'
uno dei performer piu' noti.</p>

**EDIT 2023-08: scusate, questo video non c'e' piu'**

<p>Poi, tempo di politica. <a
href="http://www.facebook.com/pages/Ivan-Scalfarotto/21997441531">Ivan
Scalfarotto</a> (candidato alle elezioni europee 2009) e <a
href="http://www.civati.it/cv.htm">Giuseppe Civati</a> erano sul palco e hanno
parlato di politica e social networking, un argomento molto discusso in quei
giorni, principalmente a causa del <a
href="http://en.wikipedia.org/wiki/Barack_Obama#2008_presidential_campaign">suo
utilizzo di successo da parte di Obama</a> che lo ha portato alla Casa Bianca
il 20 gennaio 2009. Penso che il nucleo del suo successo fosse il messaggio,
che non era &#8220;votate me&#8221;, ma piuttosto &#8220;andate a votare,
razza di idioti!&#8221; :), un perfetto esempio di dare voce a una tensione
psico-sociale tramite internet. Le persone hanno diffuso tramite Facebook,
Twitter e altri social network la loro azione di essere andati a votare, e come
gli <a
href="http://en.wikipedia.org/wiki/Robert_Cialdini">psicologi</a> hanno
spiegato molte volte, &#8220;le persone fanno cose che vedono fare ad altre
persone&#8221;.</p>


<p>Il lato negativo di questo talk e' che era troppo orientato alla politica, e
anche se dovremmo parlare di politica e internet, alcuni <a
href="http://twitter.com/fedepo/statuses/1594019457">sentivano che il tizio
stesse calcando troppo la mano</a>. Ehi, questo e' il bello dei social media:
dare voce a tutti, e quando qualcuno abusa del palco, gridarlo forte! :).</p>


<p>Dopo la politica, tempo di marketing serio: il talk piu' interessante
(secondo me) dell'intera giornata e' stato quello tenuto dai ragazzi di <a
href="http://ninjamarketing.it/">ninja marketing</a>, che hanno identificato la
&#8220;chimica del marketing virale&#8221; come il &#8220;<span
class="caps">DNA</span> virale&#8221; e un appropriato &#8220;seeding&#8221;
tramite i social media. Il <span class="caps">DNA</span> riguarda le emozioni:
gioia, rabbia, tristezza, paura e (ovviamente) sorpresa, ma la piu'
importante di tutte e' la <a
href="http://en.wikipedia.org/wiki/Catharsis">catarsi</a>. Citando
Wikipedia:</p>


<blockquote> [..] il termine &#8220;catarsi&#8221; si riferisce [..] alla
sensazione, o effetto letterario, che idealmente pervade un pubblico alla fine
della visione di una tragedia (un rilascio di emozioni o energia represse).
</blockquote>

<p>Queste emozioni identificano improvvisamente una tensione psico-sociale,
sulla quale bisogna essere abbastanza furbi da costruire i mezzi per darle voce
attraverso i social media, come hanno fatto i marketer del <a
href="http://www.whoppersacrifice.com/">whopper sacrifice</a>. La tensione qui
era la volonta' condivisa di rimuovere degli &#8220;amici&#8221; dal nostro
social graph, ma l'incapacita' di farlo per evitare possibili rimostranze da
parte loro. Ma quando avevi un motivo per farlo e guadagnare un whopper gratis,
ecco che la gente ha iniziato a cancellare altri dalle proprie liste di amici,
anche se del whopper non gliene fregava niente. Anche l'esperimento Obama
(IMHO) e' un vivido esempio di tensione psico-sociale (come ho detto prima),
che e' stata sfruttata con successo e ha dato i suoi risultati.</p>


<p style="text-align:center;"><a href="http://www.ninjamarketing.it/"><img
src="http://www.ninjamarketing.it/wp-content/themes/ninja_4/images/ninja-logo.gif"
alt="" /></a></p>


<p>Il penultimo talk, tenuto da Daniela Cangiano, ha descritto una case history
dei marketer che hanno realizzato <a
href="http://www.skoda-auto.it/skoda_in_love_octavia.asp">skoda in love</a> per
le auto Skoda (ora non piu' disponibile su Facebook). In breve, l'app faceva
cinque domande all'utente e trovava il miglior match per un appuntamento
scegliendo tra i suoi amici. L'app, per design, sceglieva i risultati
<strong>casualmente</strong> e dava <strong>sempre</strong> una percentuale di
compatibilita' superiore all'80%. Mostrando il match, veniva anche mostrata la
pubblicita', invitando l'utente a comprare un'auto Skoda e uscire con l'amico
compatibile per un appuntamento.</p>


<p>I punti chiave dell'app erano la stagionalita' (lanciata qualche giorno
prima di San Valentino), il wording, molto semplicistico e ironico, la
comunicazione, l'interattivita', eccetera eccetera. La presentatrice ha poi
sottolineato che Facebook e' un &#8220;amplificatore di interazioni
sociali&#8221; (per via della mancanza di contatto fisico e della comunicazione
scritta, aggiungerei) e che e' un veicolo potente per veicolare informazioni ai
clienti. Daniela ha poi affermato che le aziende non dovrebbero ne'
sottovalutare il valore di Facebook, essendo la &#8220;risonanza del cuore
pulsante della rete&#8221;, ne' considerarlo semplicemente un veicolo stupido,
perche' e' &#8220;dalle persone, per le persone&#8221;. Penso che le sue
affermazioni fossero valide a prima vista, ma piuttosto esagerate perche' la
chiave qui e' &#8220;internet&#8221;, non &#8220;Facebook&#8221;. Internet ci
ha aperto la mente dandoci infiniti punti di vista condivisi da milioni di
persone che ogni giorno bloggano, twittano e aggiornano anche il loro stato su
Facebook. Ma e' <strong>internet</strong>, amico bello.</p>


<p>Inoltre, le affermazioni di Daniela non si riflettevano nell'applicazione che
avevano costruito, come un membro del pubblico ha fatto notare: &#8220;se dici
che Facebook e' dalle persone e per le persone, perche' avete fatto un'app che
gli dava un risultato falso? Che tipo di godimento gli ha procurato, a parte
trovare un match falso?&#8221;. Ha risposto che l'app non era pensata per
trovare davvero dei match, ma solo per &#8220;dare qualche minuto di divertimento
all'utente, e poi veicolare il messaggio pubblicitario&#8221;. Per me e'
marketing orribile, che abusa di una stagionalita' gia' abusata (San
Valentino), ed e' solo un esempio di come le cose <span class="caps">NON</span>
dovrebbero essere fatte.</p>


<p>Ma ha funzionato? Il pubblico ha chiesto &#8220;quante conversioni (in
termini di auto vendute) avete ottenuto dall'app?&#8221; Ha risposto:
&#8220;be', questa e' solo una parte di una campagna marketing piu' ampia, e non
posso rivelare i risultati qui. Se siete interessati, scrivetemi a daniela
<span class="caps">DOT</span> cangiano AT cayenne <span class="caps">DOT</span>
it&#8221;. Se le scrivete, fatelo sapere a tutti con un commento, grazie
:).</p>


<p>L'ultimo talk e' stato tenuto dal lead developer di <a
href="http://hellotxt.com/">helloTxt</a>, un'app che permette di aggiornare il
proprio stato su piu' network usando un singolo form. Ha descritto come, una
volta che i framework e le interfacce principali del tuo sito web sono pronti e
funzionanti, e' solo questione di settimane programmare un'app Facebook e
iniziare a diffonderla: a loro sono bastati 1 sviluppatore, 1 designer, 1
copywriter e 1 marketer per farla funzionare.</p>


<h1>Conclusioni</h1>


<p>Per me l'evento e' stato davvero interessante e ringrazio sia gli <a
href="http://mikamai.com/">ospitanti</a> che tutti quelli che hanno tenuto talk
sul palco, il mio cervello era davvero sazio alla fine :). Come avete letto da
questo post (ehi, grazie per essere arrivati fino in fondo! :) gli argomenti
hanno coperto davvero molti campi (tecnologia, sociologia, politica,
marketing), ed e' incredibile che internet (e i social media) possano fonderli
tutti in un'unica piattaforma, e dare agli esseri umani nuovi modi di studiarli
e implementarli.</p>


<p>Spero solo che james AT facebook <span class="caps">DOT</span> com accolga
il consiglio che gli ho dato prima di andarmene: &#8220;<strong><span
class="caps">SIATE APERTI</span></strong>!&#8221; perche' abbiamo bisogno di
tecnologie aperte, standard aperti e conoscenza aperta, cosi' che nessuna
azienda privata possa controllarli, per il bene dell'umanita'.</p>


<p>Mi piacerebbe sentire la vostra opinione, i vostri pensieri e le vostre
critiche. Condivideteli nei commenti!</p>


<p>~ <a href="mailto:vjt@openssl.it">vjt@openssl.it</a></p>
