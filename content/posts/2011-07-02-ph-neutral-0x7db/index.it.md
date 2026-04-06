---
title: PH-Neutral 0x7db
date: 2011-07-02T17:00:00
tags: [conference, hack, security]
categories: [development]
---

<p>&#8220;<strong>If it is good, they stop making it</strong>&#8221;, il
payoff stampato sui laccetti della conferenza, distribuiti a ogni partecipante,
insieme a un badge über-l33t personalizzato con il nostro nickname e l'hash
della chiave.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/phneutral-badge.jpg" alt="" /></p>


<p>Essendo la mia prima esperienza a una conferenza di sicurezza internazionale
(sono stato solo al camp ccc2k+7), ed essendo un outsider di ph dato che non
avevo mai partecipato alle edizioni precedenti, il keynote di apertura tenuto da
<a href="http://twitter.com/41414141">FX</a>, staffer e frontman, è stato
illuminante: &#8220;you ought to be here!&#8221;, ha urlato indicando il palco,
indossando una camicia bianca col logo Phenoelit stampato su entrambe le
maniche.</p>


<p><a name="continue"></a></p>


<p>&#8220;Questa conferenza non è mai iniziata in orario&#8221;, ha continuato,
&#8220;quindi non c'era motivo di farlo per quest'ultima&#8221;. Il programma è
lineare: festa, il giorno dopo talk dalle 12:00 alle 19:30, poi festa, e
l'ultimo giorno talk dalle 12:00 alle 17:30. Decisamente un setup che si sposa
bene con l'alcol disponibile :-D.</p>


<p>Subito dopo, un altro speaker ci ha informato che le chiavi di accesso wifi
ricevute alla registrazione ci permettono di usare una bestia con 6 AP/3
repeater pilotata da un box OpenBSD — vogliono che il pubblico la hacki perché,
beh, &#8220;you are the Worst Case Scenario.&#8221; :-)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/ap-tree.jpg" alt="" /></p>


<p>Poi è stato presentato il divertente video Hacker Hacker:</p>


<p style="text-align:center;"><iframe width="100%" height="400"
src="https://www.youtube.com/embed/IZYQILfxHiw" frameborder="0"
allowfullscreen="yay"></iframe></p>


<p style="text-align:center;">:-D</p>


<p>Dopo una prima serata fiacca e non troppo entusiasmante (per la stanchezza),
vedremo cosa porta il giorno dopo.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/funny-nhaima.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/sj.html">Sniffjoke &#8211; un
toolkit per eludere gli sniffer</a></h2>


<p>Gli sniffer ad alta capacità usati nelle grandi aziende e sui gateway di
frontiera nazionali che raccolgono traffico generato dagli utenti per trovare
pattern potenzialmente &#8220;criminali&#8221; sono oggi generalmente disponibili
per larghezze di banda fino a 10Gbps, e presto ci saranno appliance che
elaboreranno flussi da 100Gbps. Sniffjoke, di <a
href="http://twitter.com/sniffjoke">vecna</a> e <a
href="http://www.evilaliv3.org/">evilaliv3</a>, è uno strumento che può
iniettare nelle connessioni <span class="caps">TCP</span> pacchetti estranei che
ingannano lo sniffer intercettante ma senza effetti significativi sul
destinatario. Questi pacchetti, per esempio, fanno credere allo sniffer che la
connessione sia stata resettata anche se non è vero — iniettando un <span
class="caps">RST</span> con checksum errato o un pacchetto con <span
class="caps">TTL</span> inferiore di 1 rispetto al conteggio degli hop — oppure
cercano di consumare la sua potenza di calcolo usando interpretazioni
vendor-specific note del <span class="caps">TCP RFC</span>. Dettagli: <a
href="http://delirandom.net/sniffjoke/">sito web</a>, <a
href="http://www.slideshare.net/diocanaglia/sniffjoke-04">slide</a>, <a
href="http://www.wireshark.org/lists/wireshark-dev/200904/msg00343.html">thread
su Wireshark</a>.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/dante-poirot.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/wlan.html">Storie horror dei
router <span class="caps">WLAN</span></a></h2>


<p>Vi siete mai chiesti cosa succede quando la password della rete wireless è
direttamente legata al <span class="caps">MAC</span> address del dispositivo, da
cui può essere dedotta perché fa parte dell'ESSID? Storie dell'orrore, come ci
hanno mostrato un ricercatore austriaco (<a
href="http://twitter.com/sviehb">ViBi</a>) e uno tedesco (<a
href="http://twitter.com/5m7x">5M7X</a>). Molti operatori che vendono
apparecchiature wifi le spediscono con vulnerabilità simili, come ci mostrano
anche mayhem e cyrax in <a
href="http://www.video.mediaset.it/video/iene/puntata/227136/viviani-haker-e-wifi.html">questo
video</a> (solo in italiano).</p>


<p>Stiamo parlando di una tecnologia il cui potenziale non è massimizzato, e che
di conseguenza porta a misure di sicurezza difettose, a causa di cattiva
ingegneria e istruzioni fuorvianti: alcuni manuali di apparecchiature wifi
raccomandano addirittura all'utente di non toccare mai la configurazione e
lasciare le password di default. Geniale. Altri esempi di cattiva ingegneria
includono l'usare gli ultimi 4 byte del <span class="caps">MAC</span> address
ethernet interno come chiave di rete e poi trasmettere quel <span
class="caps">MAC</span> tramite un pacchetto multicast inviato a 224.0.1.0 (<a
href="http://www.samsung.com/global/business/telecommunication/productInfo.do?ctgry_group=14&amp;ctgry_type=32&amp;b2b_prd_id=217">Samsung
<span class="caps">G3200</span></a> / <span class="caps">G2210</span> / <span
class="caps">G3220</span>).</p>


<p>Altre aziende, come la Synchron che produce l'<a
href="http://dsl.vodafone.de/hilfe/index.php?aktion=anzeigen&amp;rubrik=004&amp;id=269">easybox</a>,
hanno un metodo brevettato per fornire un sistema di riconoscimento della chiave,
con corrispondenza diretta tra il MAC e il seed della chiave. E alla fine, ci
sono persino aziende che vendono i loro dispositivi con il <span
class="caps">SSHD</span> di gestione aperto sull'interfaccia esterna, e che
basano la chiave di rete interamente sul <span class="caps">MAC</span>
interno. Aggiungici le password di default e hai il quadro completo.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/wifi-armory.jpg" alt="" /></p>


<p>Se vuoi saperne di più, dovresti procurarti un po' di <a
href="http://net-wifi.it/">armamentario</a> e o fare reverse engineering degli
algoritmi da solo, oppure partecipare a conferenze di sicurezza e chiedere le
slide ai ricercatori :-). Quando l'industria sarà pronta, tutti i dettagli
verranno rivelati.</p>


<h2>Hacking <span class="caps">TETRA</span></h2>


<p>Tenuto da Harald Welte (<a href="http://twitter.com/laf0rge">@laf0rge</a>),
membro del crew <a href="http://gnumonks.de/">gnumonks.de</a>, il talk ha
descritto una tecnologia di radiocomunicazione terrestre simile al <span
class="caps">GSM</span> ma che opera su frequenze più basse dello spettro,
ottenendo così una copertura più ampia con meno ripetitori. <span
class="caps">TETRA</span> impiega metodi per autenticare e crittografare le
comunicazioni, ha un canale di segnalazione su cui vengono scambiati messaggi
di 140 caratteri e identifica ogni utente sulla rete usando la corrispondenza
tra il numero dell'abbonato e quello del terminale.</p>


<p><a href="http://en.wikipedia.org/wiki/TETRA"><span
class="caps">TETRA</span></a> è ampiamente diffuso nel mondo come mezzo di
comunicazione per trasporto pubblico, sicurezza pubblica, vigili del fuoco, ecc.
È una tecnologia adatta a questi usi, ma laforge ci ha giustamente ricordato che
anche se gli strumenti ci permettono di implementare reti sicure, spesso
l'implementazione di tali strumenti è inefficace e soggetta a rottura.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/laf0rge.jpg" alt="" /></p>


<p>Ci ha mostrato come funziona la segnalazione sulla rete. Ha iniziato
mostrandoci dump di pacchetti in Wireshark, grazie a hacker cinesi che hanno
scritto i dissector. È anche riuscito ad associarsi a una rete TETRA usata dalla
<span class="caps">BVG</span>, il sistema di trasporto pubblico tedesco, e ad
ascoltare una chiamata tra la centrale e tutti i macchinisti: la centrale
chiedeva ai macchinisti di premere un pulsante contemporaneamente. Sì, signore:
nel 21° secolo serve ancora gente per farlo. Fantastico. Se vuoi costruire il
tuo, dovresti prima imparare come funzionano le radiocomunicazioni, comprarti un
dongle <a href="http://www.funcubedongle.com/">FUNcube</a> e dare un'occhiata al
progetto <a href="http://osmocomtetra/">OsmocomTETRA</a>. Un'introduzione è
disponibile su <a
href="http://www.h-online.com/security/news/item/TETRA-digital-radio-now-for-everyone-1254088.html">heise.de</a>.</p>


<h2>Printer Hacking</h2>


<p>Trova una vulnerabilità in un'interfaccia di gestione stampante, scrivi un'applet
Java che la sfrutta, definisci degli hook per pilotarla da Javascript, e il tuo
scanner di vulnerabilità stampanti via web è fatto!</p>


<p>Mi sono perso la prima parte del talk, quindi non ho i dettagli, ma come mi
ha detto lo speaker dopo quando gli ho chiesto come il tutto si incastrasse,
&#8220;è tutto scritto!&#8221; quindi basta <span class="caps">RTFM</span> <a
href="http://andreicostin.com/papers/Conf -
EuSecWest2010_AndreiCostin_HackingPrintersForFunAndProfit_full.pdf">qui</a>
:)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/naif-sleeping.jpg" alt="" /></p>


<h2><a href="http://ph-neutral.darklab.org/talks/chip_and_pin.html">Chip &#38;
<span class="caps">PIN</span> è definitivamente rotto</a></h2>


<p>Proseguendo nella lista delle tecnologie mal implementate, al giorno d'oggi le
carte di credito/debito sono vulnerabili a un classico attacco di downgrade
quando si tratta di validare il <span class="caps">PIN</span>. Ci sono diversi
tipi di chip, alcuni che permettono solo l'autenticazione in chiaro tra il <span
class="caps">POS</span> e il chip, altri che impiegano un meccanismo di
challenge-response, e quasi tutti permettono la validazione del <span
class="caps">PIN</span> online con la banca.</p>


<p>In ogni caso, la <span class="caps">SIM</span> espone un'interfaccia ai
lettori di carte, che può essere interrogata e la cui comunicazione può essere
intercettata da un dispositivo interposto. Dato che le carte devono essere
retrocompatibili con i POS esistenti e viceversa, un tale dispositivo è in grado
di alterare le capacità pubblicizzate dalla carta e forzare il <span
class="caps">POS</span> a usare l'autenticazione in chiaro, per poi
intercettare il PIN mentre l'utente lo digita.</p>


<p>Uno skimmer del genere è un dispositivo 4&#215;4cm, che può essere installato
<strong>dentro</strong> un <code>POS</code> o un <code>ATM</code>, passando
quindi potenzialmente inosservato per un lungo periodo. E anche se ci sono
assicurazioni che ti coprono contro queste frodi, se sei un viaggiatore
frequente, puoi avere vita dura a dimostrare di essere stato vittima, sia perché
numero di carta e PIN corrispondono, sia perché questa è ormai considerata una
tecnologia &#8220;sicura&#8221; che non può essere violata.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/inversepath.jpg" alt="" /></p>


<p>Grazie ad Andrea Barisani e Davide Bianco per averci informato sulla falla di
downgrade. Se vuoi saperne di più, ecco le loro slide pubblicate sul sito della
loro azienda, <a href="http://inversepath.com/">inversepath.com</a>.</p>


<h2><a href="http://ph-neutral.darklab.org/talks/freebsd.html">Exploitation del
kernel FreeBSD</a></h2>


<p>Col passare degli anni, lo stack smashing è ancora vivo e potente, come <a
href="http://twitter.com/_argp">argp</a> ha spiegato durante il suo talk. <a
href="http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2008-3531"><span
class="caps">CVE</span>-2008-3531</a> è una vulnerabilità nota del kernel
FreeBSD che permette l'esecuzione di codice nello spazio kernel, mentre l'<span
class="caps">UMA</span> — l'allocatore di memoria di FreeBSD — <a
href="http://www.phrack.org/issues.html?issue=66&amp;id=8#article">ha falle
note anch'esso</a>.</p>


<p>Senza entrare in dettagli più profondi, il problema principale qui è
l'approccio &#8220;se funziona non toccarlo&#8221; adottato da molti
amministratori di sistema quando si tratta di macchine in produzione: di
conseguenza, non vengono aggiornate per anni. Forse oggi non è rotto (ammesso
che lo sia mai, eh, 0dayz?) ma lo sarà domani, e te la prenderai in quel posto
se non ti tieni aggiornato. <span class="caps">PAROLA</span>.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/argp.jpg" alt="" /></p>


<h2>Progressi nell'evasione di <span class="caps">ASLR</span> su Win32</h2>


<p>Quando penso ai prodotti Microsoft, ho sempre la sensazione che non siano
costruiti per essere usati dalle persone, perché mi sembra che i programmatori
che li scrivono non si preoccupino mai di usarli in prima persona. <a
href="http://en.wikipedia.org/wiki/Eating_your_own_dog_food">Non mangiano il
proprio cibo per cani</a>. Provate ad usare i developer tools di IE e
capirete.</p>


<p>Il loro software è scritto per il business, deve soddisfare qualche requisito
di ordine superiore concordato da qualche manager a caso 7 livelli più su nella
gerarchia, e molto spesso fallisce nell'implementarli correttamente. Così, come
<a href="http://twitter.com/not_me">JF</a> ha fatto notare durante il talk
&#8220;Microsoft ha speso un sacco di soldi per risolvere il problema
dell'exploitation, ma ha solo creato più problemi&#8221;. Word, dword e
qword! :-)</p>


<p>L'<a href="http://en.wikipedia.org/wiki/ASLR"><span
class="caps">ASLR</span></a> è un fattore di mitigazione per gli exploit che
assumono che l'indirizzo di ritorno del codice vulnerabile si trovi a un
indirizzo noto in memoria. Queste locazioni vengono usate per calcolare dove
scrivere lo shellcode per innescare la sua esecuzione dopo l'exploitation. Se
l'indirizzo di ritorno viene randomizzato (da qui Address Space Layout
Randomization), allora l'exploit farà semplicemente crashare il software
vulnerabile facendogli riferire un indirizzo fuori dal suo spazio.</p>


<p>Il problema è che, per qualche oscuro effetto collaterale, per ogni 16 thread
creati, se il loro indirizzo base è pari (<code>0x02xxxxxx</code>,
<code>0x04xxxxxx</code>), 13 di essi finiranno per essere basati a una locazione
nota, rendendo così l'<span class="caps">ASLR</span> inefficace e bypassato.
<strong><span class="caps">PWN</span></strong>!</p>


<p>Guardate le slide di JF <a
href="/posts/2011-07-02-ph-neutral-0x7db/Advances_in_Win32_ASLR_Evasion.pdf">qui</a>
&#8211; grazie per la condivisione <a href="http://twitter.com/not_me">@not_me</a>!</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/jf.jpg" alt="" /></p>


<p>JF si è scusato almeno 4 volte prima di finire per chiudere il portatile e
concludere la presentazione con vodka e gin, perché diceva di non aver fatto un
buon lavoro nello spiegare ma, come gli ho detto anche dopo, è stato più che
efficace: non è per niente facile capire come tutti gli effetti collaterali
giocano insieme. Solo lui che era su questa roba da mesi era in grado di vedere
i pattern negli indirizzi e portare a termine una exploitation di successo di un
processo protetto da <span class="caps">ASLR</span>. Illuminante!</p>


<h2><a href="http://ph-neutral.darklab.org/talks/lfh.html">Exploitation moderna
dell'heap usando il low-fragmentation heap</a></h2>


<p>Non sono un tipo da memory management e non ho capito la maggior parte dei
concetti del talk, ma il suo abstract è molto esplicativo:</p>


<blockquote> <p><em>La gestione della memoria heap è maturata nel tempo, ma con
nuovo codice complesso arrivano nuove opportunità di exploitation. Questa
presentazione si concentrerà sulla comprensione del Low Fragmentation heap su
Windows 7 (32-bit). Dopo aver posto le basi dei concetti integrali, nuove
tecniche di exploitation verranno discusse approfonditamente. Infine, useremo
questa nuova conoscenza per sfruttare vulnerabilità <strong>presuntamente</strong>
non-exploitabili. In particolare copriremo un caso di studio che mostra come
creare un exploit per il <strong>denial of service</strong> di <span
class="caps">IIS FTP 7</span>.5 (<a
href="http://blogs.technet.com/b/srd/archive/2010/12/22/assessing-an-iis-ftp-7-5">http://blogs.technet.com/b/srd/archive/2010/12/22/assessing-an-iis-ftp-7-5-=
unauthenticated-denial-of-service-vulnerability.aspx</a>-=
unauthenticated-denial-of-service-vulnerability.aspx), risultante nel pieno
controllo di <span class="caps">EIP</span>.</em></p> </blockquote>


<p>La cosa interessante è che per usare un sottosistema di ottimizzazione
dell'allocazione di memoria per fare quello che vuoi, devi mescolare e combinare
7 diverse primitive di attacco, capire a fondo come vengono fatte le allocazioni
di blocchi e come interagiscono con la <span class="caps">CPU</span> host. Oltre
a combattere con tutti gli effetti collaterali per scrivere nel program counter
l'indirizzo che vuoi eseguire. "@You say <span class="caps">JMP</span>, we say
what addr@", come diceva correttamente una maglietta davanti a me. :-)</p>


<p>Per quanto incredibilmente complicato possa sembrare, <a
href="http://twitter.com/nudehaberdasher">Chris Valasek</a> è riuscito a
trovare, exploitare e spiegare le vulnerabilità, con un esercizio mentale che è
tanto brillante quanto ispirazionale: scava sempre più a fondo, e sarai in grado
di raggiungere qualsiasi obiettivo.</p>


<p><a
href="https://prezi.com/secure/73006c52fbfde4eddf935b5e09103df23580c39d/">Qui
le slide di Chris</a>, ma purtroppo dovrete abilitare Flash.</p>


<h2>Exploiting the Hard-Working <span class="caps">DWARF</span>: Trojan senza
codice eseguibile nativo</h2>


<p>Avreste mai immaginato che in ogni binario compilato con <span
class="caps">GCC</span> possa annidarsi un sottosistema completo di macchina
virtuale, che viene invocato ad ogni call/ret e ha la capacità di leggere e
scrivere l'heap e ogni registro della CPU? Ebbene sì, e si chiama <span
class="caps">DWARF</span>, una strumentazione di debug usata da <span
class="caps">GDB</span> per aiutare lo sviluppatore a fare debug del
proprio software.</p>


<p><em>"È una storia di <a href="http://en.wikipedia.org/wiki/DWARF"><span
class="caps">DWARF</span></a> e <a
href="http://en.wikipedia.org/wiki/Executable_and_Linkable_Format"><span
class="caps">ELF</span></a>..."</em> LOL! :-D.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/dwarf.jpg" alt="" /></p>


<p>La cosa interessante è anche che il codice <span class="caps">DWARF</span>
non viene considerato dagli strumenti di analisi come parte del codice oggetto
di un binario, rendendolo così un vettore di iniezione per attaccare trojan a un
binario. Inoltre, <span class="caps">DWARF</span> è indipendente dalla
piattaforma e dall'architettura, essendo una macchina a stati finiti a sé
stante: un trojan basato su <span class="caps">DWARF</span> può essere usato su
piattaforme multiple e attaccato a qualsiasi binario <span
class="caps">ELF</span>.</p>


<p>Se il codice <span class="caps">DWARF</span> è presente, viene eseguito per
ogni funzione chiamata e ad ogni return, mentre lo stack viene srotolato, e sì
puoi leggere e scrivere la <span class="caps">CPU</span> e l'heap. Bello. Per
tutti i dettagli, date un'occhiata al <a
href="http://ph-neutral.darklab.org/talks/tr2011-680.pdf">whitepaper</a>.</p>


<p>Qui vediamo un esempio di hobbyismo e cattiva gestione del progetto lato <span
class="caps">GCC</span> — senza offesa ovviamente — ma un sottosistema così
elaborato e complesso finisce per essere disponibile nella stragrande maggioranza
dei sistemi operativi, diventando potenzialmente un vettore di infezione.</p>


<p>Deduco questo perché <span class="caps">DWARF</span> è un pezzo di codice
oscuro, non documentato, frutto di cargo cult, scritto perché in qualche modo
oggi e domani gli sviluppatori di <span class="caps">GDB</span> avevano bisogno
di strumentazioni, e gli sviluppatori di <span class="caps">GCC</span> hanno
costruito uno strumento eccessivamente potente per supportarli, ma detto
strumento può poi essere abusato e nessuno sa veramente come funzionano le prime
release — a meno che non si spulcino post a caso sulla mailing list di <span
class="caps">GCC</span>. Le release più recenti sono abbastanza
documentate, <a href="http://dwarfstd.org/Download.php">comunque</a>.</p>


<p>La cosa divertente è che credo che per supportare <span class="caps">GDB</span>,
anche l'<a href="http://llvm.org/">infrastruttura del compilatore <span
class="caps">LLVM</span></a>, costruita con un design pulito da zero, usa <span
class="caps">DWARF</span>! Detto ciò, la morale della storia è che gli hack
sporchi di oggi ti chiameranno per guai domani — o il giorno dopo.</p>


<h2>Festa! (<a href="http://82.94.215.218/download/ph-neutral/0x7db/DJ/">Musica
qui</a>)</h2>


<blockquote> <p>- &#8220;ehi amico, sei tu il tizio dietro il box OpenBSD che fa
da host AP per la rete wifi del ph?&#8221;<br/> - &#8220;sì, sono
io&#8221;<br/> - &#8220;posso chiederti una shell di root?&#8221;<br/> -
&#8220;vuoi... <span class="caps">COSA</span>?&#8221;<br/> - &#8220;sì, sai,
vorrei dare un <code>ifconfig</code>, <code>brconfig</code>,
<code>pfctl -s</code>, <code>ls -lrt /etc | tail</code>, roba così
&#8211; solo per vedere come funziona il tutto :)&#8221;</p> </blockquote>


<p>Kudos al panda OpenBSD, che non mi ha dato la shell, ma mi ha illustrato come
funziona il "cluster" di access point dorepanda, creando una rete che copre
tutti gli spettri 802.11b/g e n. Bilancia i client tra gli AP, usa la
crittografia per verificare l'identità dell'AP e cerca di prevenire
l'eavesdropping.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/party1.jpg" alt="" /></p>


<blockquote> <p>- &#8220;amico, sei davvero una barba grigia a una conferenza di
sicurezza!&#8221;<br/> - &#8221;... e quindi?!&#8221;</p> </blockquote>


<p>... e poi parli con un <span class="caps">DBA</span> con 20 anni di esperienza
che ti dice &#8220;<em>Oracle è difettoso by design</em>&#8221; e chiacchieri
con lui di come lo scenario della sicurezza è cambiato nel corso degli
anni.</p>


<blockquote> <p>- &#8220;non è cambiato veramente niente, è solo diventato più
complicato lungo la strada&#8221;<br/> - &#8220;vuoi dire che il punto è sempre
che devi piazzare del shellcode in memoria e poi trovare un modo per
eseguirlo?&#8221;<br/> - &#8220;esattamente — puoi avere un NX bit, <span
class="caps">ASLR</span> e canary, ma c'è sempre un modo per
aggirarli.&#8221;</p> </blockquote>


<p>Un buon <a href="http://signalos.org/">amico sysadmin</a> mi ha detto
qualcosa di simile, nei termini di &#8220;finché leggo abbastanza documentazione,
sono in grado di configurare e deployare qualsiasi sistema. Niente più
sfide.&#8221;</p>


<p>Per me, conferenze come questa ti fanno riflettere, pensare e attivare
circuiti mentali che stimolano la tua passione: vedi esseri umani brillanti che
risolvono problemi intricati, che si addentrano nei dettagli e che imparano
cose nuove nel processo. Esseri umani il cui modello del mondo include sequenze
di interazioni che avvengono dentro la macchina. Come un netadmin esperto
riconosce i numeri AS dai netblock, un kernel hacker impara a riconoscere
porzioni dello spazio di indirizzamento: letteralmente respira dentro il sistema
operativo.</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/party2.jpg" alt="" /></p>


<p>Mi stupisce come ho trovato forti corrispondenze con la <a
href="http://www.amazon.com/Intelligence-Jeff-Hawkins/dp/0805074562">teoria
dell'intelligenza</a> di Jeff Hawkins (<a
href="http://www.ted.com/talks/jeff_hawkins_on_how_brain_science_will_change_computing.html">video
<span class="caps">TED</span></a>) nelle menti degli hacker. Ho parlato degli
<a href="http://numenta.com/htm-overview/htm-algorithms.php">HTM</a> <a
href="http://numenta.com/htm-overview/education.php">paper</a> con le persone
che ho incontrato, e sono rimasto sorpreso che nessuno di loro conoscesse una
tecnologia volta a costruire macchine intelligenti reimplementando l'algoritmo
corticale del cervello umano in silicio. Per esempio, i talk di Chris Valasek e
JF dimostrano le basi dell'expertise: più input ricevi da un contesto, più il
tuo cervello sarà in grado di vedere pattern più profondi e complicati, perché
vengono spostati più in basso nella gerarchia corticale, il cui compito è
riconoscere i dettagli — come loro hanno fatto con l'<span
class="caps">ASLR</span> e il low-fragmentation heap.</p>


<blockquote> <p>- &#8220;signore, lei è l'unico che indossa una cravatta in
questa sala&#8221;<br/> - &#8221;...&#8221;<br/> - &#8220;quindi deve
sicuramente lavorare per Microsoft!&#8221;<br/> - &#8220;ehm, no...&#8221;<br/>
- &#8220;ah, ok allora la mia ipotesi era sbagliata. scusi il disturbo!
:D&#8221;<br/></p> </blockquote>


<p>Alle 5:15, è meglio andare a letto, in attesa del prossimo buongiorno!</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/morning.jpg" alt="" /></p>


<h2>Giorno 3 &#8211; <a href="http://ph-neutral.darklab.org/talks/newav.html"
title="tramite addestramento del linguaggio naturale">98% di rilevamento virus
Zero-Day</a></h2>


<p>Dopo una festa del genere, sia il talk sull'<a
href="http://ph-neutral.darklab.org/talks/jes.html">ingegneria sociale</a> che
quello su <a
href="http://www.slideshare.net/nbrito01/phneutral-0x7db-exploit-next-generation">Exploit
Next Generation++</a> erano un po' nebulosi, non sono nemmeno riuscito a
riconoscere il linguaggio del codice sorgente di Metasploit (ehm). :-)</p>


<p>Poi shirtie (<a href="http://twitter.com/skjortan">@skjortan</a>) è salito sul
palco e ha illustrato come si può usare un classificatore <a
href="http://en.wikipedia.org/wiki/Bayesian_classifier">bayesiano</a> / <a
href="http://en.wikipedia.org/wiki/Maximum_entropy_classifier"><span
class="caps">MAXENT</span></a> per identificare malware sconosciuto,
0-day.</p>


<p>Esattamente come un filtro anti-spam cattura lo spam analizzando prima un
training set, identificando i pattern ricorrenti e poi confrontandoli con dati
nuovi, anche il malware come lo spam ha caratteristiche tipiche che possono
essere usate per trovarlo. Per esempio, la presenza di un riferimento all'API
<code>CreateProcess</code> o l'assenza di quella <code>&lt;a
href="http://en.wikipedia.org/wiki/Pentium_FDIV_bug"&gt;_check_fdiv&lt;/a&gt;</code>,
oppure se il binario è <a href="http://upx.sourceforge.net/">compresso con <span
class="caps">UPX</span></a> o meno.</p>


<p>La tecnologia sembra efficace, non è un sostituto di un AV basato su firme
bensì un'integrazione, perché è soggetta a falsi positivi, ma è l'unica che
identifica malware sconosciuto, 0-day — quello per cui non esistono
firme.</p>


<h2><span class="caps">XSLT</span> offensivo</h2>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/xslt.jpg" alt="" /></p>


<p><code>XSLT</code> è un linguaggio usato per trasformare documenti <span
class="caps">XML</span> in un'altra forma, ed è un linguaggio Turing-completo
eseguito nel contesto del server o del client. Viene usato sia dai sistemi di
content management che nelle applicazioni client-side, l'esempio più prominente
essendo l'indice di un repository Subversion.</p>


<p>Poiché <code>XSLT</code> è un linguaggio di programmazione (funzionale),
offre mezzi per leggere e scrivere file e per eseguire codice. Se l'input
dell'utente non è sanitizzato e/o il motore <span class="caps">XSLT</span> è
esposto, può essere usato per pwnare una macchina. Ovviamente, le funzionalità
abusabili possono essere disabilitate se non servono, o in alternativa
incapsulate con un'<span class="caps">API</span> sicura se servono. Date
un'occhiata alle slide di <a
href="http://twitter.com/Agarri_FR">Nicolas Gregoire</a> <a
href="http://prezi.com/y_fuybfudgnd/offensive-xslt/">qui</a>. Utenti Liferay,
<a href="http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-1571">siete
avvisati</a> :-)</p>


<p style="text-align:center;"><img src="/posts/2011-07-02-ph-neutral-0x7db/an0nym0us.jpg" alt="" /></p>


<h2>Parole finali</h2>


<p>Grazie <a href="http://twitter.com/nhaima">@nhaima</a> per avermi parlato
della conferenza e avermi permesso di avere un accredito (grazie nobody :)</p>


<p>Grazie <a href="http://twitter.com/techdoer">@techdoer</a> per l'editing del
post — si spera che questo sia il mio primo senza errori grammaticali :-D</p>


<p>Grazie <a href="http://twitter.com/phonoelit">@phenoelit</a> e <a
href="http://twitter.com/41414141">@41414141</a> per aver organizzato la festa
(siete i migliori), e a tutti quelli che c'erano. Spero di vedervi presto sul
palco :). Yay!</p>
