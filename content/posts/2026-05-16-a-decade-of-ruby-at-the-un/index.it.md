---
title: "Il mio decennio di Ruby all'ONU"
date: 2026-05-16
tags: [ruby, rails, ifad, retrospettiva, open-source, panmind, ai-generated]
description: "Come IFAD è finito a far girare applicazioni Ruby in produzione dal 2008, e cosa ci ho costruito sopra."
image: cover.jpg
featuredImage: cover.jpg
draft: true
---

IFAD gira su tante cose — PeopleSoft, Oracle, SharePoint, più un Sybase del 2000 che, quando sono arrivato, custodiva una sorprendente quantità di memoria istituzionale. Gira anche su Ruby — ed è per quello che ero lì.

Sono entrato negli uffici di Roma nella primavera del 2011 come consulente in un team agile che non aveva l'aspetto né il comportamento del resto del posto. Il resto del posto era un'agenzia intergovernativa, con cicli di procurement, rapporti con i vendor e framework di rischio appropriati alla sua scala e al suo mandato. Il nostro team era cinque o sei persone che rilasciavano software. Non sostituivamo l'enterprise side — lo complementavamo. Quando qualcosa richiedeva un team interno che lavorasse su tempi brevi, la chiamata arrivava a noi.

La persona che aveva reso possibile quella chiamata, anni prima del mio arrivo, era [Amedeo Paglione](https://www.linkedin.com/in/amedeo-paglione-72a83825/).

<!--more-->

## Perché Ruby era già lì

Intorno al 2008, molto prima di me, Amedeo costruiva strumenti interni in IFAD con Ruby on Rails. La storia che si è tramandata — e che ho verificato nel decennio successivo — è che il suo stack permetteva a IFAD di chiudere requisiti con tempi di ciclo che l'organizzazione non aveva mai visto prima. Qualcuno dentro IFAD se ne accorse. Poi se ne accorse qualcun altro. Quando sono arrivato io, Rails si era guadagnato il suo posto nello stack. Col team che rilascia, non si discute.

È questa la cultura in cui sono entrato. Il posto di Ruby in IFAD non era il risultato di una decisione di piattaforma calata dall'alto — era il risultato di un'adozione dal basso che l'organizzazione aveva riconosciuto e supportato. Una manciata di persone aveva dimostrato in silenzio, una volta dopo l'altra, di saper trasformare un requisito in software funzionante nel tempo che un vendor ci metteva a scrivere uno statement of work.

Amedeo è un visionario, e pensa per decenni. Ho scritto di lui nei post su [ChronoModel](/posts/2012-05-07-chronomodel-time-travel-postgresql/) e [Hermes](/posts/2013-10-20-hermes-rails-rumble-2013/), e continuerò a farlo, perché quasi tutto quello che sto per descrivere è iniziato con una conversazione con lui.

## Come ci sono arrivato

Nel luglio 2010 ero a [Panmind](/posts/2026-04-12-panmind-ahead-of-its-time/) a Roma, e a un [meetup del Ruby Social Club a Milano](/posts/2010-08-05-panmind-at-ruby-social-club/) per presentare una serie di plugin open source che stavamo estraendo dal nostro prodotto. I plugin non erano rivoluzionari — un helper SSL, un wrapper per Google Analytics, un'interfaccia ReCaptcha, un layer di navigazione AJAX guidato da jQuery — ma erano fatti con cura, documentati, testati, e li avevamo messi su GitHub perché ci erano stati utili e potevano esserlo per altri.

In platea quella sera c'era [Simone Carletti](https://github.com/weppos), che all'epoca lavorava in IFAD. Ha ascoltato un ingegnere di Panmind raccontare i plugin che aveva scritto e le scelte dietro a quel codice, e qualche mese dopo mi ha chiesto se mi potesse interessare una nuova opportunità. Nella primavera del 2011 ero a Roma, nel team di Amedeo, a scrivere il members platform.

Questa è la parte che vorrei che l'ingegnere più giovane che mi sta leggendo prendesse sul serio: ho avuto quel lavoro perché stavo condividendo pubblicamente il mio lavoro. I plugin non erano un esercizio di marketing — erano il sottoprodotto di vera ingegneria che avevamo scelto di pubblicare perché ci sembrava la cosa giusta. Ma avevano un effetto collaterale: hanno permesso a qualcuno che poteva valutarmi solo a distanza di valutarmi davvero. Simone poteva capire, dai commit e dal talk, che sapevo scrivere il codice *e* parlarne. Quel segnale è bastato per iniziare una conversazione.

Condividi il tuo lavoro. Dà alle altre persone un modo di trovarti che un CV non darà mai.

## Primo incarico: la Member States Platform

Il mio primo pezzo di lavoro è stato un'applicazione Rails che sarebbe diventata, e che è ancora, [webapps.ifad.org/members](https://webapps.ifad.org/members). È una piattaforma per gli [Stati Membri](https://webapps.ifad.org/members/member-states) di IFAD — 180 Paesi ad oggi che finanziano l'agenzia e siedono nei suoi organi di governo — per consultare i documenti delle riunioni, seguire le sessioni del Governing Council e dell'Executive Board, e ricevere notifiche sui documenti rilevanti per i loro seggi. La landing pubblica è la sezione news. La parte interessante sta dietro un login.

Sembrava semplice. Non lo era.

### Il problema dell'autorizzazione

{{< figure src="authz-matrix.jpg" alt="Un registro rilegato in pelle ornato, aperto su una scrivania di legno, tre nastri intrecciati di pergamena che formano un reticolo tridimensionale attraverso le pagine, illuminati da una calda lampada in ottone" >}}

Le regole di accesso della piattaforma sono una matrice tridimensionale con eccezioni su ogni faccia. Cosa può vedere una data persona dipende da:

- Il suo ruolo nella delegazione del proprio Paese (head of delegation, alternate, observer, technical expert, e così via).
- Il ruolo del suo Paese in IFAD (a quale Lista appartiene, se siede nell'Executive Board in questo ciclo, se è membro a pieno titolo o partecipante con status speciale).
- Il suo ruolo nella riunione specifica (un Paese può mandare una persona diversa a ogni sessione, con privilegi diversi).

A questo si aggiunge che ogni riunione ha le sue regole. E sopra a *quelle* regole, ci sono override per singolo meeting su delegazioni specifiche — il tipo di eccezione che un'agenzia intergovernativa genera naturalmente, riunione dopo riunione. Quell'insieme di regole guidava due cose: chi poteva vedere quali documenti, e chi riceveva l'e-mail quando veniva pubblicato un nuovo documento.

Il tutto era implementato dentro il database. Una view base codificava la matrice completa — persona × Paese × riunione × ruolo-nella-riunione — e una gerarchia di view aggiuntive ci sovrapponeva gli override per singolo meeting. Le view di override avevano gli ID di riunione hard-coded; un code smell ovunque altrove, ma qui andava bene, perché un meeting ID — una volta assegnato a una sessione del Governing Council o dell'Executive Board — non cambia mai più. Rails interrogava le view e stava fuori dai piedi. La logica di autorizzazione viveva dove vivevano i dati, che è dove deve vivere. Ed era veloce.

Qualunque check lato Ruby fosse rimasto sopra, lo scrivevo in-line. [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) sarebbe stato, col tempo, il posto giusto per quei controlli, ma nel 2011 Eaco non esisteva.

### L'altra metà: documenti in quattro lingue

Il resto della piattaforma era distribuzione di documenti nelle quattro lingue ufficiali di IFAD (arabo, inglese, francese, spagnolo). I documenti venivano redatti dall'Office of the Secretary e pubblicati attraverso la piattaforma ai delegati; ogni rilascio innescava notifiche, filtrate attraverso la matrice di autorizzazione di cui sopra, nella lingua preferita del destinatario.

Le descrizioni e gli excerpt che incorniciavano ciascun documento arrivavano da un editor WYSIWYG, e la maggior parte iniziava la propria vita in Word. L'HTML di Word è pieno di spazzatura — stili inline, namespace Office, attributi `mso-*`, rumore strutturale che nell'editor sembra a posto ma ovunque altrove è sbagliato. Il lavoro viveva su entrambi i lati della pipeline: configurare l'editor perché normalizzasse l'output prima di mandarlo al server, e scrivere la sanitizzazione sul backend per rimuovere quello che passava comunque. Ho iterato su entrambi finché incollare da Word non produceva HTML pulito e strutturato a valle.

La parte più difficile era il workflow e l'osservabilità intorno alla pubblicazione. L'Office of the Secretary era responsabile del rilascio dei documenti e delle notifiche alle delegazioni, e aveva bisogno degli strumenti che corrispondono a quella responsabilità: bozze da poter far circolare internamente prima del go-live, anteprime sia dei documenti sia delle email di notifica che ciascun gruppo di destinatari avrebbe ricevuto, e un modo per vedere — a posteriori — chi era stato notificato di cosa.

Poi c'era il batching. Non vuoi mandare dieci email separate a una delegazione in un giorno di pubblicazioni intense. Ho costruito un meccanismo di coda che collezionava le notifiche man mano che i documenti andavano live, aspettava una finestra configurabile, e le spediva come digest. Ogni delegato poteva scegliere la propria frequenza. Il design veniva dritto dagli anni passati sulle mailing list Linux, dove l'opzione digest era da tempo il modo civile di iscriversi a una lista ad alto volume.

Niente di tutto questo era nuovo di per sé. Tenerlo insieme in maniera coerente, su quattro lingue e un calendario di riunioni che non si fermava mai, era il lavoro.

### Il premio

{{< figure src="award.jpg" alt="Natura morta classica: corona di alloro in bronzo, pergamena sigillata e targa in ottone poggiate su un cuscino di velluto cremisi profondo su una superficie di legno intagliato, con una cornice dorata e una lampada a olio sullo sfondo del palazzo" >}}

A dicembre 2011 la piattaforma vinse l'[Outstanding Project/Initiative award di IFAD](https://ifad-un.blogspot.com/2011/12/celebrating-27-extraordinary-colleagues.html). Il riconoscimento andò ad Amedeo e alle tre persone cross-dipartimento che l'avevano concepita, sponsorizzata e portata avanti tra i silos: Shamela Brown, Victoria Chiartano e Paola de Leva. I consulenti non sono eleggibili per quei premi, quindi il mio nome non è sulla citazione. Giusto così — il loro lavoro è stato più duro. A me è toccato scrivere il codice.

Victoria è stata il mio business focal point per tutta la durata della realizzazione. Ha tradotto due decenni di come IFAD gestisce davvero i cicli dei suoi organi di governo in requisiti su cui potevo costruire, e mi rispondeva picche quando i miei istinti ingegneristici correvano avanti rispetto alla realtà del business. Members è quello che è perché l'ingegneria e la business analysis sono state fatte insieme, da persone che si rispettavano e discutevano in modo produttivo quando non erano d'accordo. Quella combinazione — buona ingegneria a fianco di buona competenza di business — è più rara di entrambe prese singolarmente.

## Il Sybase sotto

La Member States Platform era codice nuovo, ma non viveva da sola. Pescava persone, Paesi, riunioni, sessioni e ruoli da un sistema di back-office che era in IFAD da molto prima di me: un'applicazione Java costruita intorno all'anno 2000, in cima a un database Sybase. Il sistema aveva anche un nome — **CIAO**, per *Contact Information Available Online*, che guarda caso è anche la parola italiana per il saluto in entrata e in uscita. Un back-office in un'agenzia ONU con sede a Roma deve salutarti in italiano; chi lo battezzò nel 2000 ci prese.

L'app Java era adeguata al suo scopo originale, che era fare da registro interno di persone, Paesi ed eventi: form per crearli, schermate per modificarli, report per fare audit. Andrea De Baggis, che la scrisse nei primi anni 2000, fece un lavoro professionale con gli strumenti dell'epoca.

Il problema era il data model. Era stato implementato col pattern [entity-attribute-value](https://it.wikipedia.org/wiki/Entity-attribute-value_model): una grossa tabella che conteneva ogni attributo di ogni entità come riga. Un'entità era un sacchetto di righe; una query per "la lista degli Head of Delegation per il Governing Council 36 il cui Paese è membro di List A" erano dieci join e, in una giornata calda, dieci minuti.

Quei dati erano la sorgente canonica per molto più del back-office. Ogni app Rails del team di Amedeo che avesse bisogno di sapere cos'era un Paese, o che ruolo aveva una persona in una riunione, ne aveva bisogno. Allungavamo le mani dentro il Sybase dal nostro lato, con un driver che sembrava più vecchio di parte del nostro codice, e lo facevamo funzionare. Funzionava. Era anche la fonte di dolore più persistente nel team per anni — le view di autorizzazione che avevo scritto vivevano sopra, ed erano veloci tanto quanto il substrato che interrogavano.

Amedeo aveva il piano dall'inizio. Sostituire il back-office legacy era un programma pianificato a fasi, e la Members Platform era la prima — un progetto visibile e autonomo che, col senno di poi, sarebbe servito anche come banco di prova per dimostrare che il team agile poteva consegnare qualcosa di quella portata dentro i vincoli di IFAD. Una volta che Members era in produzione, sono passato alla fase successiva: il back-office stesso.

## Riscrivere il back-office in Rails

Il piano era noioso e corretto. Tirare su un'applicazione Rails con uno schema normalizzato, migrare i dati codificati in EAV un tipo di entità alla volta, esporre una JSON API, e — quando il nuovo sistema avesse raggiunto la parità — ritirare il CIAO basato su Sybase e lasciare che fosse quello in Rails a prendersi il nome.

La normalizzazione era la parte facile. Sybase cedeva i suoi dati se avevi pazienza. Ho scritto importer, li ho fatti girare su snapshot, ho scritto altri importer, ho confrontato i conteggi delle righe finché non combaciavano, e ho promosso il nuovo schema quando combaciavano. Anche le primary key sono passate — ogni Paese, riunione, persona e ruolo ha conservato l'ID che aveva nel database EAV — così qualunque cosa avesse già un riferimento, dentro o fuori IFAD, continuava a risolvere attraverso il cut-over. La lista canonica di Paesi, riunioni e persone si è spostata sul nuovo sistema, dove una query per gli Head of Delegation impiegava millisecondi invece di minuti.

La parte più difficile era l'API. La Members Platform doveva passare dal leggere Sybase al leggere i nuovi endpoint JSON — e doveva continuare a funzionare nel frattempo. Il cut-over, com'era prevedibile, non è andato al primo colpo. Quella è una storia per un post sulle migrazioni; non è questo post.

Quel che è rilevante qui è cosa ho costruito sul lato consuming, perché è diventato una gemma. Rails nel 2011–2013 ti dava [ActiveResource](https://github.com/rails/activeresource) per consumare JSON API, e ActiveResource era troppo magica, troppo lenta, e troppo desiderosa di fingere che una chiamata remota fosse una chiamata di metodo locale. Volevo qualcosa che sembrasse familiare in superficie — così che il resto del team non dovesse imparare un'API nuova — ma che fosse onesto sui confini di rete sotto, e più veloce nel caso comune. Quella gemma è diventata [Hawk](https://github.com/ifad/hawk). L'idea era un client sottile e non-magico costruito sopra [Typhoeus](https://github.com/typhoeus/typhoeus) ed [Ethon](https://github.com/typhoeus/ethon) — libcurl sotto il cofano — con batching esplicito e riuso delle connessioni.

Anche Hawk è ancora senza documentazione. La sezione usage del README è un `TODO` dal mio primo commit. Lezione: se la documentazione non c'è dal giorno uno, non arriva mai, e il progetto deriva verso il NIH — la prossima persona che ha bisogno di quel che fa la tua gemma trova più facile scriversene una propria che fare reverse engineering della tua.

## Reticulum: il grafo

{{< figure src="reticulum.jpg" alt="Una carta antica di pergamena su un tavolo illuminato da candele che mostra una rete simile a una costellazione di nodi dorati luminosi connessi da fili luminosi con loop visibili, un astrolabio in ottone a sinistra e una penna d'oca in un calamaio a destra" >}}

Hawk e il back-office JSON erano, presi singolarmente, pezzi di ingegneria non straordinari — un client, un server, un'API. Quel che li rendeva importanti era che Amedeo era già tre passi avanti.

La sua visione, che articolava da prima del mio arrivo, era che ogni sistema in IFAD che custodisse dati canonici dovesse esporli come HTTP JSON API, e ogni applicazione che avesse bisogno di quei dati dovesse consumarli over the wire invece di tenersene una copia. Single source of truth per dominio. Niente liste di Paesi duplicate, niente database di persone fuori sincrono, niente script di riconciliazione che funzionavano *quasi* sempre. Un enterprise service bus, ma senza il prodotto commerciale di bus — solo HTTP, JSON, e un insieme di servizi disciplinati.

Internamente lo chiamavamo Reticulum, ed era modellato come un grafo — risorse che linkavano altre risorse, cicli permessi. Un Paese puntava alle sue Liste; una Lista puntava indietro ai suoi membri; una riunione puntava al suo Governing Body e alle persone che vi rivestivano ruoli. Il grafo si percorreva in entrambe le direzioni; navigazione e dipendenze cadevano fuori dalla stessa struttura.

Oggi suona ordinario. Nel 2012, dentro un'agenzia ONU, con un enterprise side che ancora cuciva insieme sistemi tramite batch notturni e database link condivisi, era ambizioso, ed era corretto. L'abbiamo costruito. Ogni app Rails del team alla fine parlava lo stesso set di API. Le app nuove venivano su in settimane invece che mesi, perché alla parte difficile — *dov'è la lista autoritativa di X* — era stata data risposta una volta sola, e la risposta era sempre "chiama questo endpoint".

Il team agile non sostituiva l'enterprise side di IFAD; non era quello che provavamo a fare. L'enterprise side — vendor, procurement, framework di rischio, requisiti di audit — risolveva un problema diverso su un orologio diverso. Quello che il nostro team faceva, quello che il modello di Amedeo ci consentiva di fare, era far girare una corsia veloce a fianco. Le due corsie si parlavano in JSON quando serviva. Nessuna timeline doveva combaciare con quella di qualcun altro.

## Tre intorno a un tavolo

Verso il 2013 il lato agile dell'IT di IFAD si era cristallizzato in un piccolo gruppo. Lo guidava Amedeo. [Lleïr Borràs Metje](https://github.com/lleirborras) si è unito più o meno in quel periodo come lead engineer, e da allora in poi io, lui e Amedeo eravamo il nucleo. Non avrei rilasciato metà di quello che ho rilasciato senza Lleïr. Quando una feature doveva atterrare in fretta, ci facevamo un hackathon interno — noi tre in una stanza per uno o due giorni — e la spedivamo end-to-end in uno dei nostri strumenti. Un visionario, due ingegneri che si fidavano l'uno dell'altro, e un team abbastanza piccolo da stare intorno a un tavolo. Questa è la forma pratica di tutto ciò che Reticulum ha reso possibile.

Non tutto quello che noi tre abbiamo fatto sul team agile vale un post a sé. Una grossa fetta di quegli anni è stata lavoro di infrastruttura su cui nessuno scrive talk per le conferenze: playbook Ansible che rilasciavano app Rails, bootstrap dei server, deployment plumbing, monitoring, job di backup, le diecimila piccole cose che stanno tra un git commit e la produzione.

Quel lavoro non è entusiasmante da raccontare, ma è da lì che veniva la credibilità del team. Quando una nuova app Rails poteva essere provisionata, deployata e monitorata in un pomeriggio — perché l'infrastruttura era già scriptata e già testata — il *ship fast, ship right* di Amedeo non era uno slogan, era un dato di fatto sul nostro tooling.

## Crossing over: tech lead in territorio IBM

{{< figure src="crossing-over.jpg" alt="Un lungo corridoio marmoreo arcato in un palazzo romano, uno spazio di lavoro di legno e libri intravisto attraverso una porta aperta sulla sinistra, una singola figura in abito scuro che cammina con una borsa verso l'ala formale davanti, luce tardo-pomeridiana che entra obliqua dalle finestre a lucernario" >}}

Dopo diversi anni nel team agile, sono passato all'enterprise side dell'IT di IFAD come tech lead su un grosso progetto finance costruito su tecnologia IBM. Non dirò molto del progetto in sé — la maggior parte del lavoro vive sotto il tipo di vincoli per cui "non posso dire molto" è la risposta giusta.

Riportavo a [Simone Giorgi](https://www.linkedin.com/in/simone-giorgi-2a811a/), con [Thomas Bousios](https://www.linkedin.com/in/thomas-bousios-b49760/) un livello sopra come director dell'area. Mi hanno scelto perché anni di delivery sul lato agile se l'erano guadagnati. Conoscere entrambi i lati — software engineering e l'infrastruttura su cui gira — era ciò che il ruolo richiedeva. Thomas è anche il director che ha tirato su il primo ufficio CISO di IFAD e ha guidato il programma di sicurezza su tutto il perimetro — 2FA enterprise, segmentazione di rete, disciplina sugli account di servizio. Sulla carta eravamo una coppia improbabile: lui enterprise-focused, io engineering-led; nella pratica funzionava, e funzionava notevolmente bene — è quell'accoppiata che mi ha permesso di rilasciare [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) e l'[integrazione con OneSpan](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/).

Lo stack era diverso: basato su IBM, sotto una governance più stretta che gira su cicli più lenti, più impalcatura di rischio, meno spazio per improvvisare. Sport diverso, stesso gioco. Ho portato il rigore ingegneristico del team agile — codice rivedibile, deployment riproducibili, test veri — in un programma in cui stavano diventando sempre più importanti, e in cambio, da Simone e Thomas, ho ricevuto una vera educazione su come operare dentro una governance più stretta senza perdere velocità. Sono in debito con entrambi.

La business analyst sul progetto era [Michelle Lockwood](https://www.linkedin.com/in/michelle-lockwood-8929a55/), e Michelle è stata determinante per il risultato — nello stesso modo in cui Victoria e Shamela lo erano state su Members.

Sul lato IBM, il project manager del vendor era [Eugenio Catello](https://www.linkedin.com/in/eugenio-catello/). Nei primi mesi capitava spesso che fossimo in disaccordo — priorità diverse, orologi diversi, definizioni di *done* diverse — e il rapporto di lavoro è migliorato costantemente man mano che il programma avanzava. Quella che all'inizio sembrava frizione erano i due lati che si calibravano sui vincoli reciproci.

### WebSphere e ISAM

Ho lavorato con **WebSphere Application Server** — un pezzo di infrastruttura Java di un'era molto specifica, col suo modello di deployment, il suo tooling e il suo modo preferito di fare le cose. Ho scritto [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) per portare il deployment di WebSphere nello stesso workflow Git-driven, rivedibile e idempotente che il team agile dava per scontato su Rails. Ci è voluto un po', perché a WebSphere non piace essere automatizzato.

Ho lavorato anche con **IBM Security Access Manager** (ISAM), un gateway di autenticazione enterprise della stessa famiglia di prodotti. Ho scritto [omniauth-ibmisam](https://github.com/vjt/omniauth-ibmisam) per permettere alle app Rails di accettare sessioni autenticate via ISAM senza dover fingere di parlare il resto dell'ecosistema ISAM. Quella gemma è corta, poco glamour, e fa esattamente una cosa utile — che è il modo in cui mi piacciono le gemme.

Una grossa fetta del lavoro era integrazione tra il lato IBM e il lato Oracle dello stack di IFAD: il genere di lavoro su cui nessuno scrive talk per le conferenze, ma che tiene in piedi le organizzazioni. Se mai ti capitasse di dover connettere due prodotti enterprise i cui vendor giurano che sono stati progettati per lavorare insieme — non lo sono, non lo sono mai stati, non lo saranno mai — vuoi Simone e Michelle nella stanza.

### Il log cluster

{{< figure src="log-cluster.jpg" alt="Interno di una grande sala d'archivio di palazzo italiano di notte, un grande codice rilegato in pelle aperto su un piedistallo in marmo intagliato al centro, nastri di pergamena che fluiscono verso di esso da scrivanie più piccole disposte lungo le pareti, ciascuna scrivania illuminata dalla propria lampada in ottone" >}}

Il pezzo di cui sono più orgoglioso di quegli anni è la piattaforma centrale di aggregazione dei log. L'abbiamo costruita su hardware che altrimenti sarebbe finito in discarica. Google aveva ritirato la linea di prodotto Google Search Appliance e il contratto di IFAD era scaduto; quattro di quelle scatole gialle stavano ferme presso UNICC. Le conoscevo bene — avevo passato tempo in precedenza a configurare la GSA per indicizzare contenuti interni, lottando con una regex dopo l'altra e non essendo mai del tutto soddisfatto di quello che usciva dall'altra parte. Amedeo aveva già il suo progetto Finder in pipeline per sostituirla, ma quella è un'altra storia. Quel che contava qui era che l'hardware era ancora buono: dischi SMART-clean in ordine, RAID10 su SATA da 2,5", sovradimensionato da Google per reggere molto più carico di quanto ne avesse mai visto in IFAD, sottoutilizzato per anni. Per un cluster Elasticsearch era, sulla carta, una calzata perfetta — macchine già progettate per spingere su workload di indicizzazione e ricerca. Ho chiesto a UNICC di spedirli a Roma, e l'hanno fatto. Il BIOS Google era bloccato, e lo sblocco era una procedura completamente documentata e supportata — una volta applicata, l'hardware era nostro.

{{< figure src="gsa-servers.jpg" alt="Quattro server gialli Google Search Appliance impilati in un rack, ogni chassis con il logo Google in rilievo e bucherellato col pattern caratteristico delle ventole rotonde dell'appliance; cavi in fibra arancione visibili dietro" >}}

Il lavoro è atterrato su due ingegneri che riportavano a me: [Riccardo Massullo](https://github.com/riccardomassullo) e [Gian Piero Carrubba](https://github.com/gpiero). Hanno scritto l'automazione dell'OS che tirava su gli appliance in modo riproducibile, e noi tre ci abbiamo sovrapposto Elasticsearch, Kibana e APM sotto licenza enterprise. Il cluster raccoglieva log da entrambi i lati dell'IT di IFAD — lo stack Ruby sul lato agile, lo stack IBM sull'enterprise side. Gli application server IBM sono rumorosi; scrivono grossi stack trace profondi dieci livelli su molteplici file di log, in formati che non sono mai stati pensati per essere letti due volte da una macchina. Abbiamo scritto configurazioni Filebeat che tailavano tutto e una grossa pipeline Logstash che li parsava come si deve — gestendo record multilinea, arricchendo gli eventi con lookup GeoIP e AS-number, e normalizzando i campi tra le sorgenti così che una request Rails potesse essere incrociata con la chiamata WebSphere che l'aveva innescata senza dover tradurre tra due schemi.

Quel che rendeva utile il cluster era meno la tecnologia e più l'audience. IBM forniva le sue dashboard per ISAM e WebSphere; erano competenti, ed erano product-centric — progettate per raccontarti del prodotto, non del tuo progetto. Le nostre erano project-centric. Gli sviluppatori le usavano per diagnosticare codice malfunzionante in tutto lo stack. I sysadmin per valutare lo stato operativo a colpo d'occhio. I business analyst per vedere come la gente usava davvero le piattaforme. La Security, sotto il CISO [Guillaume Farret](https://www.linkedin.com/in/guillaume-farret/), per costruire alert su pattern sospetti. Un cluster, quattro audience, uno schema coerente. Al picco il cluster conteneva circa 10 TiB di dati indicizzati su all'incirca due anni di retention, con policy di rollover separate calibrate per ciascun tipo di dato.

I log non erano l'unica telemetria che vi facevamo confluire. I firewall e gli switch di IFAD avevano exporter NetFlow built-in che spingevano i record direttamente a Logstash, che li parsava in Elasticsearch man mano che arrivavano. Gli application server quello non ce l'avevano. [Octoflow](https://github.com/ifad/octoflow) era il piccolo servizio Python che io e Riccardo abbiamo costruito sopra [nprobe](https://www.ntop.org/products/netflow/nprobe/) per chiudere il gap — un collector/filter/exporter che girava a fianco di ciascun app server, generando record di flow dal suo stesso traffico e spedendoli nella stessa pipeline. Lo schema seguiva le convenzioni di [ElastiFlow](https://www.elastiflow.com/), che dava alla parte security dashboard Kibana già pronte e un vocabolario che l'industria già parlava. Una request web che arrivava a un application server WebSphere poteva essere accoppiata con i pacchetti veri che l'avevano trasportata.

Il cluster ha girato sugli appliance ripurposati per anni. Man mano che l'infrastruttura di produzione maturava, è migrato lentamente su VM — non perché l'hardware stesse cedendo, ma perché il modello operativo intorno era andato avanti. Anche Elasticsearch è peggiorato col tempo: ogni major version un po' più gonfia, un po' meno amichevole al sysadmin che la fa girare. Ma quella è un'altra storia.

## Partire, 2021

A fine 2021 ho accettato un'offerta da Meta e mi sono trasferito a Dublino. Dieci anni in IFAD sono finiti nel modo solito: una scatola portata giù per le scale dell'ufficio di Roma, e un mucchio di documenti di handover nel mio laptop. Le app Rails hanno continuato a girare. Le API hanno continuato a rispondere. L'enterprise side ha tenuto il suo orologio. Niente di tutto ciò aveva più bisogno di me, ed è così che deve essere.

## Quel che resta

{{< figure src="what-persists.jpg" alt="Vista dall'interno di un palazzo italiano attraverso una finestra arcata aperta sui tetti romani all'alba, la sagoma distante di una cupola all'orizzonte, un registro rilegato in pelle aperto e un rametto di edera sul davanzale di pietra, una lampada in ottone spenta accanto, una scrivania di legno fioca visibile nell'ombra a sinistra" >}}

[webapps.ifad.org/members](https://webapps.ifad.org/members) è ancora l'URL. Le pagine dei documenti escono ancora in quattro lingue. La [pagina dei documenti del Governing Council](https://webapps.ifad.org/members/gc/49) ha lo stesso aspetto che aveva il giorno in cui l'abbiamo rilasciata — ogni voce di news ancora prefissata col <u>"New Documents Online!"</u> che Victoria scriveva a mano nelle email che mandava ai delegati prima che la piattaforma esistesse. Members ha sostituito le email manuali. Non ha sostituito il fraseggio.

[ChronoModel](https://github.com/ifad/chronomodel) riceve ancora aggiornamenti su GitHub; ne ho scritto in [un post a sé](/posts/2012-05-07-chronomodel-time-travel-postgresql/) e nel [suo rilascio 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/). Anche [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) riceve ancora aggiornamenti. [data-confirm-modal](/posts/2013-07-02-data-confirm-modal/) è stato, chissà come, [scaricato milioni di volte](https://rubygems.org/gems/data-confirm-modal). [Geremia Taglialatela](https://github.com/tagliala) — il collega che ha ereditato Colore quando me ne sono andato — da allora ha messo 354 commit nella [pipeline documentale Heathen / Colore](/posts/2016-01-15-document-pipeline-heathen-colore/). Lasci un posto, e il lavoro che hai fatto resta lì, e le persone che vengono dopo di te lo rendono migliore di quanto avresti potuto tu.

La visione di Amedeo è ancora la forma del lato agile dello stack di IFAD. Servizi piccoli, API chiare, single source of truth, team agile che complementa la macchina enterprise. È sopravvissuta un decennio.

Quel che mi sono portato via da quei dieci anni — più di qualunque pezzo di codice — è questo: quando un posto decide di fidarsi di un team, di proteggerlo, e di lasciarlo rilasciare, e quando quel team è guidato da qualcuno che pensa davvero all'organizzazione e non a sé stesso, ottieni una quantità straordinaria di software da un gruppo molto piccolo di persone, e per molto tempo. Quella combinazione è più rara di quanto dovrebbe essere. E non ci sono entrato per caso — ci sono entrato perché pubblicavo quel che costruivo, e la persona giusta se ne era accorta. Resta il miglior consiglio che ho per chiunque stia iniziando.
