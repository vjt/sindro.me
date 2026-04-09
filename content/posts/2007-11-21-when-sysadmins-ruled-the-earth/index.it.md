---
title: "Quando i sysadmin governavano la Terra"
author: Marcello Barnaba
date: 2007-11-21
tags: [geek, networking]
image: cover.jpg
featuredImage: cover.jpg
hideVintage: true
---

Un romanzo davvero, davvero, davvero **NERD** di [Cory Doctorow](https://craphound.com/)
che racconta di un gruppo di sysadmin che lottano per tenere in piedi la cara
vecchia Rete dopo un evento catastrofico che ha messo il mondo intero in
ginocchio. Combattono con scorte limitate di energia e cibo e comunicano via
Usenet... usando la *buona vecchia gerarchia alt.*

Voto: 10+ per la cosa più geek che abbia mai letto. Vale davvero l'ora
necessaria per leggerlo tutto.

<!--more-->

---

> **Nota:** Il testo completo di questo racconto è riprodotto qui sotto, tradotto in italiano dall'[originale inglese](/posts/2007-11-21-when-sysadmins-ruled-the-earth/). Era originariamente pubblicato su [Jim Baen's Universe, Vol 1 Num 2, agosto 2006](https://web.archive.org/web/20110216142848/http://baens-universe.com/articles/when_sysadmins_ruled_the_earth). La rivista non esiste più — sopravvive solo la copia del Web Archive. Ho voluto preservarlo qui perché è uno dei migliori racconti di narrativa geek mai scritti. Tutti i diritti appartengono a [Cory Doctorow](https://craphound.com/); il racconto è rilasciato sotto licenza [Creative Commons BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/2.5/).

---

*Illustrazioni di Rob Dumuhosky*

![La CN Tower crolla su Toronto](/posts/2007-11-21-when-sysadmins-ruled-the-earth/sysadmins-opening.jpg)

Quando il telefono speciale di Felix suonò alle due di notte, Kelly si girò dall'altra parte e gli mollò un pugno sulla spalla sibilando: «Perché cazzo non l'hai spento prima di andare a letto?»

«Perché sono di reperibilità» disse lui.

«Non sei mica un cazzo di dottore» disse lei, tirandogli un calcio mentre si sedeva sul bordo del letto e si infilava i pantaloni che aveva lasciato sul pavimento prima di coricarsi. «Sei un maledetto amministratore di sistema.»

«È il mio lavoro» disse lui.

«Ti sfruttano come un somaro» disse lei. «Lo sai che ho ragione. Porca miseria, adesso sei un padre, non puoi scappare via nel cuore della notte ogni volta che a qualcuno va giù la scorta di porno. Non rispondere a quel telefono.»

Sapeva che aveva ragione. Rispose al telefono.

«Router principale non risponde. BGP non risponde.» Alla voce meccanica del sistema di monitoraggio non importava niente se la mandavi a fanculo, così lo fece, e si sentì un po' meglio.

«Magari riesco a sistemarlo da qui» disse. Poteva collegarsi all'UPS della gabbia e riavviare i router. L'UPS era in un netblock diverso, con i propri router indipendenti collegati a gruppi di continuità dedicati.

Kelly ora era seduta sul letto, una sagoma indistinta contro la testiera. «In cinque anni di matrimonio, non sei mai riuscito a sistemare niente da qui.» Stavolta si sbagliava — sistemava roba da casa in continuazione, ma lo faceva con discrezione e senza farne una questione, così lei non se ne ricordava. E aveva anche ragione — i log dimostravano che dopo l'una di notte, niente poteva mai essere sistemato senza andare fino alla gabbia. Legge dell'Infinita Perversità Universale — alias Legge di Felix.

Cinque minuti dopo Felix era al volante. Non era riuscito a sistemarlo da casa. Anche il netblock del router indipendente era offline. L'ultima volta che era successo, un coglione di operaio edile aveva infilato una trencher nel condotto principale del data center e Felix si era unito a un plotone di cinquanta sysadmin infuriati che per una settimana erano rimasti in cima alla buca risultante, urlando insulti ai poveracci che lavoravano 24 ore su 24 per rigiuntare diecimila cavi.

Il telefono suonò altre due volte in macchina e lui lo lasciò sovrapporsi allo stereo, facendo uscire i rapporti meccanici di stato dalle casse grosse e profonde — altra infrastruttura di rete critica offline. Poi chiamò Kelly.

«Ciao» disse lui.

«Non fare quella voce da cane bastonato, la sento la voce da cane bastonato.»

Sorrise suo malgrado. «OK, niente cane bastonato.»

«Ti amo, Felix» disse lei.

«Io sono completamente pazzo di te, Kelly. Torna a dormire.»

«2.0 è sveglio» disse lei. Il bambino era stato Beta Test quando era nel suo ventre, e quando le si erano rotte le acque, lui aveva ricevuto la chiamata ed era schizzato fuori dall'ufficio gridando: «La Gold Master è appena uscita!» Avevano cominciato a chiamarlo 2.0 prima ancora che finisse il suo primo vagito. «Questo piccolo bastardo è nato per ciucciare la tetta.»

«Mi dispiace di averti svegliata» disse lui. Era quasi al data center. Niente traffico alle 2 di notte. Rallentò e accostò prima dell'ingresso del garage. Non voleva perdere la chiamata di Kelly sottoterra.

«Non mi hai svegliata tu» disse lei. «Sei lì da sette anni. Hai tre junior che riportano a te. Dagli il telefono. Hai pagato i tuoi debiti.»

«Non mi piace chiedere ai miei sottoposti di fare qualcosa che non farei io» disse lui.

«L'hai già fatto» disse lei. «Per favore? Odio svegliarmi sola di notte. Mi manchi di più la notte.»

«Kelly—»

«Non sono più arrabbiata. Mi manchi e basta. Tu mi fai fare bei sogni.»

«OK» disse lui.

«Così semplice?»

«Esattamente. Così semplice. Non posso permettere che tu faccia brutti sogni, e ho pagato i miei debiti. D'ora in poi, accetterò la reperibilità notturna solo per coprire le feste.»

Lei rise. «I sysadmin non vanno in ferie.»

«Questo sì» disse lui. «Promesso.»

«Sei meraviglioso» disse lei. «Oh, che schifo. 2.0 ha appena fatto un core dump su tutta la mia vestaglia.»

«Questo è il mio ragazzo» disse lui.

«Oh, se lo è» disse lei. Riattaccò, e lui guidò la macchina nel parcheggio del data center, strisciando il badge e sollevando a forza una palpebra assonnata per far dare un'occhiata al suo bulbo oculare privato del sonno dallo scanner retinico.

Si fermò alla macchinetta per prendere una barretta energetica guaranà/modafinil e una tazza di caffè-robot letale in un bicchiere da clean room anti-rovesciamento. Divorò la barretta e sorseggiò il caffè, poi lasciò che la porta interna gli leggesse la geometria della mano e lo valutasse per un momento. La porta sospirò aprendosi e il carico di aria a pressione positiva dell'airlock gli soffiò addosso mentre passava finalmente nel sancta sanctorum.

Era il delirio. Le gabbie erano progettate per far manovrare due o tre sysadmin alla volta. Ogni altro centimetro di spazio cubico era occupato da rack ronzanti di server, router e dischi. Stipati tra di essi c'erano non meno di altri venti sysadmin. Era una vera convention di magliette nere con slogan incomprensibili, pance che debordavano dalle cinture cariche di telefoni e multi-tool.

Di solito nella gabbia si gelava, ma tutti quei corpi stavano surriscaldando il piccolo spazio chiuso. Cinque o sei alzarono lo sguardo con una smorfia quando entrò. Due lo salutarono per nome. Si fece largo con la pancia tra la ressa e le gabbie, verso i rack Ardent in fondo alla stanza.

«Felix.» Era Van, che quella notte non era di reperibilità.

«Che ci fai qui?» chiese. «Non c'è bisogno che domani siamo distrutti tutti e due.»

«Come? Oh. Il mio server personale è laggiù. È andato giù verso l'1:30 e mi ha svegliato il process-monitor. Avrei dovuto chiamarti e dirti che stavo scendendo — ti avrei risparmiato il viaggio.»

Il server di Felix — un box che condivideva con cinque amici — era in un rack un piano sotto. Si chiese se fosse offline anche quello.

«Che succede?»

«Attacco flashworm massiccio. Un qualche stronzo con un exploit zero-day ha messo ogni box Windows sulla rete a fare probe Monte Carlo su ogni blocco IP, compreso IPv6. I grossi Cisco hanno tutti interfacce amministrative su v6, e vanno tutti in crash se ricevono più di dieci probe simultanee, il che significa che praticamente ogni punto di interscambio è andato giù. Anche il DNS è impazzito — come se qualcuno avesse avvelenato il zone transfer la scorsa notte. Oh, e c'è una componente email e IM che manda messaggi molto realistici a tutti nella tua rubrica, vomitando dialoghi tipo Eliza che si agganciano alle tue email e messaggi loggati per farti aprire un trojan.»

«Gesù.»

«Già.» Van era un sysadmin di tipo due, più di un metro e novanta, coda di cavallo lunga, pomo d'Adamo ballonzolante. Sul suo petto a griglia per toast, la maglietta diceva CHOOSE YOUR WEAPON e mostrava una fila di dadi poliedrici da GDR.

Felix era un admin di tipo uno, con una settantina o ottantina di chili extra tutti intorno alla vita, e una barba curata ma folta che portava sopra i suoi doppi menti. La sua maglietta diceva HELLO CTHULHU e mostrava un Cthulhu carino, senza bocca, in stile Hello Kitty. Si conoscevano da quindici anni, essendosi incontrati su Usenet, poi di persona alle bevute della Toronto Freenet, a una o due convention di Star Trek, e alla fine Felix aveva assunto Van per lavorare sotto di lui alla Ardent. Van era affidabile e metodico. Formatosi come ingegnere elettronico, teneva una processione di quaderni a spirale pieni di dettagli su ogni singolo passo che avesse mai compiuto, con data e ora.

«Stavolta non è nemmeno un PEBKAC» disse Van. Problem Exists Between Keyboard And Chair — il problema sta tra la tastiera e la sedia. I trojan via email rientravano in quella categoria — se la gente fosse stata abbastanza sveglia da non aprire allegati sospetti, i trojan via email sarebbero un ricordo del passato. Ma i worm che divoravano i router Cisco non erano un problema degli utenti decerebrati — erano colpa di ingegneri incompetenti.

«No, è colpa di Microsoft» disse Felix. «Ogni volta che mi trovo al lavoro alle 2 di notte, o è un PEBKAC o è Microsloth.»

****

Finirono per staccare quei maledetti router da Internet. Non Felix, ovviamente, anche se gli prudevano le mani di farlo e riavviarli dopo aver disabilitato le interfacce IPv6. Lo fecero un paio di Bastard Operator From Hell con i controcazzi che dovevano girare due chiavi contemporaneamente per accedere alla loro gabbia — come le guardie in un silo Minuteman. Il 95 percento del traffico a lunga distanza del Canada passava da questo edificio. Aveva una sicurezza migliore della maggior parte dei silo Minuteman.

Felix e Van rimisero online i box Ardent uno alla volta. Venivano bombardati da probe del worm — rimettere i router online esponeva le gabbie a valle all'attacco. Ogni box su Internet stava affogando nei worm, o generava attacchi worm, o entrambe le cose. Felix riuscì a raggiungere il NIST e Bugtraq dopo un centinaio di timeout, e a scaricare alcune patch del kernel che avrebbero dovuto ridurre il carico che i worm mettevano sulle macchine a lui affidate. Erano le 10 del mattino, e aveva una fame da sbranare un orso morto dal culo, ma ricompilò i kernel e rimise le macchine online. Le dita lunghe di Van volavano sulla tastiera amministrativa, la lingua di fuori mentre controllava le statistiche di carico su ciascuna.

«Avevo duecento giorni di uptime su Greedo» disse Van. Greedo era il server più vecchio del rack, dai tempi in cui davano ai box nomi di personaggi di Star Wars. Ora erano tutti nominati come i Puffi, e stavano finendo i Puffi e avevano cominciato coi personaggi di McDonaldland, a partire dal laptop di Van, Mayor McCheese.

«Greedo risorgerà» disse Felix. «Io ho un 486 al piano di sotto con più di cinque anni di uptime. Mi spezzerà il cuore riavviarlo.»

«E che cazzo di uso fai di un 486?»

«Nessuno. Ma chi spegne una macchina con cinque anni di uptime? È come praticare l'eutanasia a tua nonna.»

«Voglio mangiare» disse Van.

«Facciamo così» disse Felix. «Tiriamo su il tuo box, poi il mio, poi ti porto al Lakeview Lunch per le pizze della colazione e ti prendi il resto della giornata libero.»

«Affare fatto» disse Van. «Amico, sei troppo buono con noi sottoposti. Dovresti tenerci in una fossa e picchiarci come tutti gli altri capi. È tutto quello che meritiamo.»

****

«È il tuo telefono» disse Van. Felix si estrasse dalle viscere del 486, che aveva rifiutato categoricamente di accendersi. Aveva rimediato un alimentatore di scorta da dei tizi che gestivano un'operazione di spam e stava cercando di montarlo. Si fece passare il telefono da Van, che gli era caduto dalla cintura mentre si contorceva per raggiungere il retro della macchina.

«Hey, Kel» disse. C'era uno strano rumore di singhiozzi in sottofondo. Interferenze, forse? 2.0 che sguazzava nel bagnetto? «Kelly?»

La linea cadde. Provò a richiamare, ma non ottenne nulla — né squillo né segreteria. Il telefono alla fine andò in timeout e disse ERRORE DI RETE.

«Accidenti» disse, pacato. Agganciò il telefono alla cintura. Kelly voleva sapere quando tornava a casa, o voleva che passasse a prendere qualcosa per la famiglia. Avrebbe lasciato un messaggio in segreteria.

Stava testando l'alimentatore quando il telefono suonò di nuovo. Lo afferrò al volo e rispose. «Kelly, hey, che succede?» Si sforzò di tenere ogni traccia di irritazione fuori dalla voce. Si sentiva in colpa: tecnicamente parlando, aveva adempiuto ai suoi obblighi verso la Ardent Financial LLC nel momento in cui i server Ardent erano tornati online. Le ultime tre ore erano state puramente personali — anche se aveva intenzione di fatturarle all'azienda.

C'erano singhiozzi sulla linea.

«Kelly?» Sentì il sangue defluirgli dal viso e le dita dei piedi diventare insensibili.

«Felix» disse lei, a malapena comprensibile attraverso i singhiozzi. «È morto, oh Gesù, è morto.»

«Chi? Chi, Kelly?»

«Will» disse lei.

Will? pensò. Chi cazzo è — Cadde in ginocchio. William era il nome che avevano scritto sul certificato di nascita, anche se l'avevano sempre chiamato 2.0. Felix emise un suono angosciato, come un latrato malato.

«Sto male» disse lei, «non riesco neanche più a stare in piedi. Oh, Felix. Ti amo così tanto.»

«Kelly? Che sta succedendo?»

«Tutti, tutti quanti—» disse lei. «Sono rimasti solo due canali in TV. Cristo, Felix, dalla finestra sembra l'alba dei morti viventi—» La sentì vomitare. Il telefono cominciò a spezzettarsi, rimandando i suoni del vomito come un echoplex.

«Resta lì, Kelly» gridò mentre la linea cadeva. Compose il 911, ma il telefono andò di nuovo in ERRORE DI RETE appena premette INVIO.

Prese Mayor McCheese da Van, lo collegò al cavo di rete del 486, lanciò Firefox dalla riga di comando e googlò il sito della Polizia Metropolitana. Velocemente, ma senza panico, cercò un modulo di contatto online. Felix non perdeva mai la testa. Risolveva problemi, e andare nel panico non risolveva problemi.

Trovò un modulo online e scrisse i dettagli della conversazione con Kelly come se stesse compilando un bug report, le dita veloci, la descrizione completa, e poi premette INVIA.

Van aveva letto alle sue spalle. «Felix—» cominciò.

«Dio» disse Felix. Era seduto sul pavimento della gabbia e lentamente si tirò in piedi. Van prese il laptop e provò alcuni siti di notizie, ma andavano tutti in timeout. Impossibile dire se fosse perché stava succedendo qualcosa di terribile o perché la rete zoppicava sotto il superworm.

«Devo andare a casa» disse Felix.

«Ti porto io» disse Van. «Tu continua a chiamare tua moglie.»

Si diressero verso gli ascensori. Una delle poche finestre dell'edificio era lì, un oblò spesso e schermato. Ci sbirciarono dentro aspettando l'ascensore. Non molto traffico per un mercoledì. C'erano più macchine della polizia del solito?

«Oh mio Dio—» Van indicò.

La CN Tower, un gigantesco ago bianco ed elefantiaco di edificio, incombeva a est di loro. Era storta, come un ramo piantato nella sabbia bagnata. Si stava muovendo? Sì. Stava inclinandosi, lentamente, ma acquistando velocità, cadendo verso nordest in direzione del distretto finanziario. In un secondo, superò il punto di non ritorno e si schiantò. Sentirono l'onda d'urto, poi il boato, l'intero edificio che oscillava per l'impatto. Una nuvola di polvere si levò dalle macerie, e ci furono altri tuoni quando la struttura autoportante più alta del mondo sfondò un edificio dopo l'altro.

«Il Broadcast Centre sta crollando» disse Van. E infatti — l'imponente edificio della CBC stava collassando al rallentatore. La gente correva in ogni direzione, veniva schiacciata dai calcinacci. Visto attraverso l'oblò, era come guardare un effetto in CGI scaricato da un sito di file-sharing.

I sysadmin si stavano ammassando intorno a loro adesso, spingendosi per vedere la distruzione.

«Che è successo?» chiese uno di loro.

«La CN Tower è caduta» disse Felix. Sembrava lontano alle sue stesse orecchie.

«È stato il virus?»

«Il worm? Cosa?» Felix mise a fuoco il tizio, che era un giovane admin con solo un po' di ciccia da tipo due intorno alla vita.

«Non il worm» disse il tizio. «Ho ricevuto un'email che dice che tutta la città è in quarantena per un virus. Un'arma biologica, dicono.» Porse a Felix il suo Blackberry.

Felix era così preso dal rapporto — apparentemente inoltrato da Health Canada — che non si accorse nemmeno che tutte le luci si erano spente. Poi se ne accorse, e premette il Blackberry nella mano del proprietario, e lasciò uscire un singolo singhiozzo.

****

I generatori si attivarono un minuto dopo. I sysadmin si precipitarono in massa verso le scale. Felix afferrò Van per il braccio, tirandolo indietro.

«Forse dovremmo aspettare qui nella gabbia» disse.

«E Kelly?» disse Van.

Felix sentì lo stomaco rivoltarsi. «Dobbiamo entrare nella gabbia, adesso.» La gabbia aveva filtri d'aria a microparticelle.

Corsero di sopra alla gabbia grande. Felix aprì la porta e poi la lasciò sigillarsi alle sue spalle con un sibilo.

«Felix, devi andare a casa—»

«È un'arma biologica» disse Felix. «Superbatterio. Qui dentro staremo bene, credo, finché i filtri reggono.»

«Cosa?»

«Collegati su IRC» disse.

Lo fecero. Van aveva Mayor McCheese e Felix usò Smurfette. Saltarono tra i canali di chat finché non ne trovarono uno con qualche nick familiare.

> il pentagono non c'è più/la casa bianca anche

> IL MIO VICINO VOMITA SANGUE DAL BALCONE A SAN DIEGO

> Qualcuno ha buttato giù il Gherkin. I banchieri fuggono dalla City come topi.

> Ho sentito che il Ginza è in fiamme

Felix digitò: Sono a Toronto. Abbiamo appena visto cadere la CN Tower. Ho sentito di armi biologiche, qualcosa di molto rapido.

Van lesse e disse: «Non sai quanto sia rapido, Felix. Magari siamo stati tutti esposti tre giorni fa.»

Felix chiuse gli occhi. «Se fosse così, credo che avremmo già dei sintomi.»

> Sembra che un EMP abbia messo fuori uso Hong Kong e forse Parigi—le immagini satellitari in tempo reale le mostrano completamente buie, e tutti i netblock là non stanno routando

> Sei a Toronto?

Era un nick sconosciuto.

> Sì—su Front Street

> mia sorella è alla UofT e nn riesco a raggiungerla—puoi chiamarla?

> Niente servizio telefonico

Felix digitò, fissando PROBLEMI DI RETE.

«Ho un soft phone su Mayor McCheese» disse Van, lanciando la sua app voice-over-IP. «Me ne sono appena ricordato.»

Felix prese il laptop e compose il numero di casa. Squillò una volta, poi ci fu un suono piatto e stridulo come una sirena dell'ambulanza in un film italiano.

> Niente servizio telefonico

Felix digitò di nuovo.

Alzò lo sguardo verso Van, e vide che le sue spalle magre tremavano. Van disse: «Porco dio. Il mondo sta finendo.»

****

Felix si staccò da IRC un'ora dopo. Atlanta era bruciata. Manhattan era calda — abbastanza radioattiva da mandare in tilt le webcam che guardavano su Lincoln Plaza. Tutti davano la colpa all'Islam finché non divenne chiaro che la Mecca era un cratere fumante e la famiglia reale saudita era stata impiccata davanti ai propri palazzi.

Le mani gli tremavano, e Van piangeva in silenzio nell'angolo più lontano della gabbia. Provò a chiamare casa di nuovo, e poi la polizia. Non funzionò meglio delle ultime 20 volte.

Si collegò in SSH al suo box al piano di sotto e controllò la posta. Spam, spam, spam. Altro spam. Messaggi automatici. Eccolo — un messaggio urgente dal sistema di intrusion detection nella gabbia Ardent.

Lo aprì e lesse rapidamente. Qualcuno stava sondando i suoi router in modo rozzo e ripetuto. Non corrispondeva alla firma di un worm, neanche. Seguì il traceroute e scoprì che l'attacco proveniva dallo stesso edificio, un sistema in una gabbia un piano sotto.

Aveva delle procedure per questo. Fece un portscan sull'attaccante e trovò che la porta 1337 era aperta — 1337 stava per "leet" o "elite" nel codice di sostituzione numeri/lettere degli hacker. Era il tipo di porta che un worm lasciava aperta per infilarsi dentro e fuori. Googlò gli exploit noti che lasciavano un listener sulla porta 1337, restrinse la ricerca in base al sistema operativo del server compromesso, e poi lo trovò.

Era un worm antico, uno per cui ogni box avrebbe dovuto avere la patch da anni. Non importava. Aveva il client per quel worm, e lo usò per crearsi un account root sul box, su cui poi si collegò, e si guardò intorno.

C'era un altro utente connesso, "scaredy", e controllò il monitor dei processi e vide che scaredy aveva generato le centinaia di processi che stavano sondando lui e parecchi altri box.

Aprì una chat:

> Smettila di sondare il mio server

Si aspettava spavalderia, sensi di colpa, negazione. Rimase sorpreso.

> Sei nel data center di Front Street?

> Sì

> Cristo credevo di essere l'ultimo vivo. Sono al quarto piano. Credo ci sia un attacco con armi biologiche fuori. Non voglio uscire dalla clean room.

Felix soffiò fuori un respiro.

> Mi stavi sondando per farmi risalire a te?

> Sì

> È stato intelligente

Bastardo furbo.

> Sono al sesto piano, con me ce n'è un altro.

> Cosa sai?

Felix incollò il log IRC e aspettò che l'altro tizio lo digerisse. Van si alzò e cominciò a camminare avanti e indietro. Aveva gli occhi vitrei.

«Van? Amico?»

«Devo pisciare» disse.

«Niente aprire la porta» disse Felix. «Ho visto una bottiglia vuota di Mountain Dew nel cestino laggiù.»

«Giusto» disse Van. Camminò come uno zombie fino al cestino e tirò fuori il bottiglione vuoto. Si girò di spalle.

> Sono Felix

> Will

Lo stomaco di Felix fece una lenta capriola mentre pensava a 2.0.

«Felix, credo di dover uscire fuori» disse Van. Si stava muovendo verso la porta dell'airlock. Felix mollò la tastiera e si alzò a fatica e corse a capofitto verso Van, placcandolo prima che raggiungesse la porta.

«Van» disse, guardando negli occhi vitrei e sfocati del suo amico. «Guardami, Van.»

«Devo andare» disse Van. «Devo andare a casa a dare da mangiare ai gatti.»

«C'è qualcosa là fuori, qualcosa che agisce velocemente ed è letale. Magari verrà spazzato via dal vento. Magari è già andato. Ma noi restiamo qui seduti finché non ne siamo sicuri o finché non avremo altra scelta. Siediti, Van. Siediti.»

«Ho freddo, Felix.»

Si gelava. Le braccia di Felix avevano la pelle d'oca e i suoi piedi sembravano blocchi di ghiaccio.

«Siediti contro i server, vicino alle ventole. Prendi il calore dello scarico.» Trovò un rack e si accoccolò contro.

> Ci sei?

> Ancora qui—sto risolvendo un po' di logistica

> Quanto tempo prima di poter uscire?

> Non ne ho idea

Nessuno scrisse più niente per un bel po'.

****

Felix dovette usare la bottiglia di Mountain Dew due volte. Poi Van la usò di nuovo. Felix provò a chiamare Kelly ancora una volta. Il sito della Polizia Metropolitana era giù.

Alla fine, si lasciò scivolare contro i server e avvolse le braccia intorno alle ginocchia e pianse come un bambino.

Dopo un minuto, Van venne a sedersi accanto a lui, con il braccio intorno alla spalla di Felix.

«Sono morti, Van» disse Felix. «Kelly e il mio fi— figlio. La mia famiglia non c'è più.»

«Non lo sai per certo» disse Van.

«Ne sono abbastanza sicuro» disse Felix. «Cristo, è finito tutto, vero?»

«Resistiamo ancora qualche ora e poi usciamo. Le cose dovrebbero tornare alla normalità presto. I pompieri sistemeranno tutto. Mobiliteranno l'esercito. Andrà tutto bene.»

Le costole di Felix gli facevano male. Non piangeva da — Da quando era nato 2.0. Strinse le ginocchia più forte.

Poi le porte si aprirono.

I due sysadmin che entrarono avevano gli occhi spiritati. Uno aveva una maglietta che diceva TALK NERDY TO ME e l'altro portava una maglietta della Electronic Frontiers Canada.

«Venite» disse TALK NERDY. «Ci stiamo riunendo tutti all'ultimo piano. Prendete le scale.»

Felix si accorse che stava trattenendo il respiro.

«Se c'è un agente biologico nell'edificio, siamo tutti infettati» disse TALK NERDY. «Muovetevi, vi raggiungiamo lassù.»

«Ce n'è uno al sesto piano» disse Felix, mentre si alzava in piedi.

«Will, sì, l'abbiamo preso. È già su.»

TALK NERDY era uno dei Bastard Operator From Hell che aveva staccato i grossi router. Felix e Van salirono le scale lentamente, i loro passi che echeggiavano nella tromba deserta. Dopo l'aria gelida della gabbia, la tromba delle scale sembrava una sauna.

C'era una mensa all'ultimo piano, con bagni funzionanti, acqua, caffè e cibo dalle macchinette. C'era una fila a disagio di sysadmin davanti a ciascuno. Nessuno incrociava lo sguardo di nessun altro. Felix si chiese quale fosse Will e poi si mise in fila alla macchinetta.

Prese un paio di barrette energetiche e un bicchierone enorme di caffè alla vaniglia prima di finire gli spiccioli. Van aveva conquistato un po' di spazio al tavolo e Felix posò la roba davanti a lui e si mise in fila per il bagno. «Tienimi qualcosa» disse, lanciando una barretta energetica davanti a Van.

Quando furono tutti sistemati, completamente svuotati e rifocillati, TALK NERDY e il suo amico erano tornati di nuovo. Sgombrarono il registratore di cassa in fondo all'area preparazione cibo e TALK NERDY ci salì sopra. Lentamente la conversazione si spense.

«Sono Uri Popovich, questo è Diego Rosenbaum. Grazie a tutti per essere saliti. Ecco cosa sappiamo per certo: l'edificio è sui generatori da tre ore ormai. L'osservazione visiva indica che siamo l'unico edificio nel centro di Toronto con corrente funzionante — che dovrebbe durare per altri tre giorni. C'è un agente biologico di origine sconosciuta in libertà oltre le nostre porte. Uccide velocemente, in poche ore, ed è aerodisperso. Lo prendi respirando aria cattiva. Nessuno ha aperto nessuna delle porte esterne di questo edificio dalle cinque di stamattina. Nessuno aprirà le porte finché non darò io il via libera.

«Gli attacchi alle principali città di tutto il mondo hanno lasciato i soccorritori nel caos. Gli attacchi sono elettronici, biologici, nucleari e con esplosivi convenzionali, e sono molto diffusi. Sono un ingegnere della sicurezza, e da dove vengo io, attacchi raggruppati in questo modo sono di solito considerati opportunistici: il gruppo B fa saltare un ponte perché sono tutti impegnati a gestire l'evento della bomba sporca del gruppo A. È intelligente. Una cellula di Aum Shin Rikyo a Seoul ha gasato la metropolitana verso le 2 di notte ora orientale — è il primo evento che riusciamo a localizzare, quindi potrebbe essere stato l'Arciduca che ha spezzato la schiena al cammello. Siamo abbastanza sicuri che Aum Shin Rikyo non possa essere dietro questo tipo di caos: non hanno precedenti di infowar e non hanno mai dimostrato il tipo di acume organizzativo necessario per colpire così tanti obiettivi contemporaneamente. In pratica, non sono abbastanza intelligenti.

«Ci barrichiamo qui per un futuro prevedibile, almeno finché l'arma biologica non sarà stata identificata e dispersa. Presidieremo i rack e terremo le reti in piedi. Questa è infrastruttura critica, ed è il nostro lavoro assicurarci che abbia cinque 9 di uptime. In tempi di emergenza nazionale, la nostra responsabilità di farlo raddoppia.»

Un sysadmin alzò la mano. Era molto audace, con una ring-tee verde dell'Incredibile Hulk, e stava all'estremo giovane della scala.

«Chi è morto e ti ha fatto re?»

«Ho i controlli del sistema di sicurezza principale, le chiavi di ogni gabbia, e i codici per le porte esterne — che sono tutte chiuse a chiave adesso, tra l'altro. Sono quello che ha radunato tutti qui per primo e ha convocato la riunione. Non mi importa se qualcun altro vuole questo lavoro, è un lavoro di merda. Ma qualcuno deve farlo.»

«Hai ragione» disse il ragazzino. «E io so farlo bene quanto te. Mi chiamo Will Sario.»

Popovich guardò il ragazzino dall'alto in basso. «Beh, se mi lasci finire di parlare, magari ti passo le cose quando ho finito.»

«Prego, finisci pure.» Sario gli voltò le spalle e andò alla finestra. La fissò intensamente. Lo sguardo di Felix ne fu attratto, e vide che diverse colonne di fumo oleoso si levavano dalla città.

Lo slancio di Popovich era rotto. «Quindi questo è quello che faremo» disse.

Il ragazzino si guardò intorno dopo un momento di silenzio che si protrasse. «Oh, è il mio turno adesso?»

Ci fu una risata di buon umore generale.

«Ecco cosa penso io: il mondo sta andando a puttane. Ci sono attacchi coordinati su ogni singolo pezzo di infrastruttura critica. C'è un solo modo in cui quegli attacchi possono essere così ben coordinati: via Internet. Anche se accettate la tesi che gli attacchi siano tutti opportunistici, dobbiamo chiederci come un attacco opportunistico possa essere organizzato in pochi minuti: Internet.»

«Quindi pensi che dovremmo spegnere Internet?» Popovich rise un po', ma smise quando Sario non disse nulla.

«Abbiamo visto un attacco ieri notte che ha quasi ammazzato Internet. Un po' di DoS sui router critici, un po' di magia col DNS, e giù che va come la figlia del parroco. I poliziotti e i militari sono un branco di luseroni tecnofobici, non si affidano quasi per niente alla rete. Se tiriamo giù Internet, svantaggiamo in modo sproporzionato gli attaccanti, causando solo un inconveniente ai difensori. Quando sarà il momento, la ricostruiremo.»

«Mi stai prendendo per il culo» disse Popovich. La mascella gli pendeva letteralmente.

«È logico» disse Sario. «Molta gente non riesce a gestire la logica quando detta decisioni difficili. È un problema della gente, non della logica.»

Ci fu un brusio di conversazione che si trasformò rapidamente in un boato.

![Illustrazione](/posts/2007-11-21-when-sysadmins-ruled-the-earth/sysadmins-spot.jpg)

«ZITTI!» urlò Popovich. La conversazione calò di un Watt. Popovich urlò di nuovo, battendo il piede sul bancone. Alla fine ci fu una parvenza di ordine. «Uno alla volta» disse. Era rosso in faccia, con le mani in tasca.

Un sysadmin era per restare. Un altro per andarsene. Dovevano nascondersi nelle gabbie. Dovevano inventariare le scorte e nominare un furiere. Dovevano uscire e trovare la polizia, o fare volontariato negli ospedali. Dovevano nominare dei difensori per tenere sicuro l'ingresso.

Felix scoprì con sorpresa di avere la mano alzata. Popovich gli diede la parola.

«Mi chiamo Felix Tremont» disse, salendo su uno dei tavoli, tirando fuori il suo PDA. «Voglio leggervi una cosa.

«"Governi del Mondo Industriale, voi stanchi giganti di carne e acciaio, io vengo dal Cyberspazio, la nuova dimora della Mente. A nome del futuro, chiedo a voi del passato di lasciarci in pace. Non siete benvenuti tra noi. Non avete sovranità dove noi ci raduniamo.

«"Non abbiamo un governo eletto, né è probabile che ne avremo uno, quindi mi rivolgo a voi senza maggiore autorità di quella con cui la libertà stessa ha sempre parlato. Dichiaro lo spazio sociale globale che stiamo costruendo naturalmente indipendente dalle tirannie che cercate di imporci. Non avete alcun diritto morale di governarci né possedete alcun metodo di coercizione che abbiamo vera ragione di temere.

«"I governi derivano i loro giusti poteri dal consenso dei governati. Voi non avete né sollecitato né ricevuto il nostro. Non vi abbiamo invitato. Non ci conoscete, né conoscete il nostro mondo. Il Cyberspazio non si trova entro i vostri confini. Non pensate di poterlo costruire, come fosse un'opera pubblica. Non potete. È un atto della natura e cresce da sé attraverso le nostre azioni collettive."

«Questa è la Dichiarazione di Indipendenza del Cyberspazio. È stata scritta 12 anni fa. Pensavo fosse una delle cose più belle che avessi mai letto. Volevo che mio figlio crescesse in un mondo dove il cyberspazio fosse libero — e dove quella libertà contagiasse il mondo reale, così che anche il meatspace diventasse più libero.»

Deglutì a fatica e si strofinò gli occhi col dorso della mano. Van gli diede goffamente una pacca sulla scarpa.

«Il mio bellissimo figlio e la mia bellissima moglie sono morti oggi. Milioni di altri, anche. La città è letteralmente in fiamme. Intere città sono scomparse dalla mappa.»

Tirò su un singhiozzo e lo ringoiò di nuovo.

«In tutto il mondo, persone come noi sono riunite in edifici come questo. Stavano cercando di riprendersi dal worm di ieri notte quando il disastro ha colpito. Abbiamo energia indipendente. Cibo. Acqua.

«Abbiamo la rete, che i cattivi usano così bene e che i buoni non hanno mai capito come sfruttare.

«Abbiamo un amore condiviso per la libertà che viene dal prendersi cura della rete. Siamo responsabili del più importante strumento organizzativo e governativo che il mondo abbia mai visto. Siamo la cosa più vicina a un governo che il mondo abbia in questo momento. Ginevra è un cratere. L'East River è in fiamme e l'ONU è stata evacuata.

«La Repubblica Distribuita del Cyberspazio ha superato questa tempesta praticamente illesa. Siamo i custodi di una macchina immortale, mostruosa, meravigliosa, una con il potenziale di ricostruire un mondo migliore.

«Non ho nient'altro per cui vivere se non questo.»

C'erano lacrime negli occhi di Van. Non era l'unico. Non lo applaudirono, ma fecero qualcosa di meglio. Mantennero un silenzio rispettoso, totale, per secondi che si protrassero in un minuto.

«Come lo facciamo?» disse Popovich, senza una traccia di sarcasmo.

****

I newsgroup si stavano riempiendo velocemente. Li avevano annunciati su news.admin.net-abuse.email, dove bazzicavano tutti i combattenti anti-spam, e dove c'era una cultura stretta di cameratismo di fronte all'attacco totale.

Il nuovo gruppo era alt.november5-disaster.recovery, con .recovery.governance, .recovery.finance, .recovery.logistics e .recovery.defense che pendevano da esso. Benedetta la lanosa gerarchia alt. e tutti quelli che ci navigano.

I sysadmin saltarono fuori dal nulla. Il Googleplex era online, con la tenace Queen Kong che comandava una banda di sgherri in rollerblades che sfrecciavano attraverso il gigantesco data center sostituendo box morti e premendo pulsanti di riavvio. L'Internet Archive era offline al Presidio, ma il mirror ad Amsterdam era attivo e avevano rediretto il DNS così che a malapena notavi la differenza. Amazon era giù. Paypal era su. Blogger, Typepad e Livejournal erano tutti su, e si riempivano di milioni di post di sopravvissuti spaventati che si stringevano insieme per un calore elettronico.

Gli stream di foto su Flickr erano orribili. Felix dovette disiscriversi dopo aver beccato una foto di una donna e un bambino, morti in una cucina, contorti in un geroglifico agonizzante dall'agente biologico. Non assomigliavano a Kelly e 2.0, ma non era necessario. Cominciò a tremare e non riuscì a smettere.

Wikipedia era su, ma zoppicava sotto il carico. Lo spam continuava a riversarsi come se niente fosse cambiato. I worm vagavano per la rete.

.recovery.logistics era dove si concentrava la maggior parte dell'azione.

> Possiamo usare il meccanismo di voto dei newsgroup per tenere

> elezioni regionali

Felix sapeva che avrebbe funzionato. I voti dei newsgroup Usenet funzionavano da più di vent'anni senza intoppi sostanziali.

> Eleggeremo rappresentanti regionali e loro sceglieranno un Primo

> Ministro.

Gli americani insistevano per Presidente, cosa che a Felix non piaceva. Sembrava troppo di parte. Il suo futuro non sarebbe stato il futuro americano. Il futuro americano era saltato in aria con la Casa Bianca. Lui stava costruendo una tenda più grande di così.

C'erano sysadmin francesi online da France Telecom. Il data center dell'EBU era stato risparmiato dagli attacchi che avevano martellato Ginevra, ed era pieno di tedeschi ironici il cui inglese era migliore di quello di Felix. Andavano d'accordo con i resti della squadra della BBC a Canary Wharf.

Parlavano un inglese poliglotta in .recovery.logistics, e Felix aveva lo slancio dalla sua parte. Alcuni admin stavano raffreddando le inevitabili flammewar stupide con la pratica di lunghi anni. Altri contribuivano con suggerimenti utili.

Sorprendentemente pochi pensavano che Felix fosse fuori di testa.

> Penso che dovremmo tenere le elezioni il prima possibile. Domani

> al massimo. Non possiamo governare con giustizia senza il consenso

> dei governati.

In pochi secondi la risposta atterrò nella sua casella.

> Non puoi essere serio. Consenso dei governati? Se non mi sbaglio,

> la maggior parte delle persone che proponi di governare sta vomitando

> le budella, nascosta sotto la scrivania, o vagando in stato di shock

> per le strade della città. Quando votano LORO?

Felix dovette ammettere che aveva un punto. Queen Kong era acuta. Poche donne sysadmin, e questa era una vera tragedia. Donne come Queen Kong erano troppo brave per essere escluse dal campo. Avrebbe dovuto trovare una soluzione per bilanciare le donne nel suo nuovo governo. Richiedere che ogni regione eleggesse una donna e un uomo?

Si gettò felicemente nella discussione con lei. Le elezioni sarebbero state il giorno dopo; ci avrebbe pensato lui.

****

«Primo Ministro del Cyberspazio? Perché non chiamarti il Gran Puffo della Rete Dati Globale? È più dignitoso, suona più figo e ti porterà altrettanto lontano.» Will aveva il posto letto accanto a lui, su nella mensa, con Van dall'altro lato. La stanza puzzava come un cesso: venticinque sysadmin che non si lavavano da almeno un giorno tutti ammassati nella stessa stanza. Per alcuni di loro, era passato molto, molto più di un giorno.

«Stai zitto, Will» disse Van. «Tu volevi provare a buttare giù Internet.»

«Correzione: io voglio buttare giù Internet. Tempo presente.»

Felix socchiuse un occhio. Era così stanco che era come sollevare pesi.

«Senti, Sario — se non ti piace la mia piattaforma, presentane una tua. C'è un sacco di gente che pensa che io dica stronzate e la rispetto per questo, visto che si candida contro di me o appoggia qualcuno che lo fa. Questa è la tua scelta. Quello che non è nel menu è rompere le palle e lamentarsi. Ora si dorme, o alzati e posta la tua piattaforma.»

Sario si tirò su lentamente, srotolando la giacca che aveva usato come cuscino e indossandola. «Andate a fanculo, me ne vado.»

«Pensavo non se ne andasse più» disse Felix e si girò dall'altra parte, restando sveglio a lungo, pensando alle elezioni.

C'erano altre persone in corsa. Alcuni non erano nemmeno sysadmin. Un Senatore americano in ritiro nella sua residenza estiva nel Wyoming aveva un generatore e un telefono satellitare. In qualche modo aveva trovato il newsgroup giusto e si era buttato nella mischia. Alcuni hacker anarchici in Italia bombardavano il gruppo tutta la notte, postando proclami in inglese stentato sulla bancarotta politica della "governance" nel nuovo mondo. Felix guardò il loro netblock e determinò che probabilmente erano barricati in un piccolo istituto di Interaction Design vicino a Torino. L'Italia era stata colpita molto duramente, ma fuori nella piccola città, questa cellula di anarchici aveva preso residenza.

Un numero sorprendente di candidati aveva come piattaforma lo spegnimento di Internet. Felix aveva i suoi dubbi sul fatto che fosse anche possibile, ma pensava di capire l'impulso di finire l'opera insieme al mondo. Perché no? Da ogni indicazione, sembrava che l'opera fino a quel momento fosse stata una cascata di disastri, attacchi e opportunismo, il tutto sommandosi in un Götterdämmerung. Un attacco terroristico qui, una controffensiva letale là da parte di un governo che aveva reagito in modo eccessivo... Nel giro di poco, avevano fatto piazza pulita del mondo.

Si addormentò pensando alla logistica dello spegnimento di Internet, e fece brutti sogni in cui era l'unico difensore della rete.

Si svegliò con un suono secco e pruriginoso. Si girò e vide che Van era seduto, la giacca appallottolata in grembo, a grattarsi vigorosamente le braccia magre. Erano diventate del colore della carne in scatola, con un aspetto squamoso. Nella luce che filtrava dalle finestre della mensa, pagliuzze di pelle fluttuavano e danzavano in grandi nuvole.

«Che stai facendo?» Felix si tirò su. Guardare le unghie di Van che gli laceravano la pelle gli fece venire prurito per simpatia. Erano tre giorni che non si lavava i capelli e a volte il cuoio capelluto gli dava la sensazione che ci fossero piccoli insetti a depositare uova tra i suoi capelli. La sera prima si era sistemato gli occhiali e aveva toccato il retro delle orecchie; il dito era tornato lucido di sebo denso. Gli venivano punti neri dietro le orecchie quando non si faceva la doccia per un paio di giorni, e a volte foruncoli giganteschi e profondi che Kelly alla fine scoppiava con malato piacere.

«Mi gratto» disse Van. Si mise a lavorare sulla testa, mandando una nuvola di forfora nell'aria, là a unirsi alle croste che aveva già eliminato dalle estremità. «Cristo, mi prude dappertutto.»

Felix prese Mayor McCheese dallo zaino di Van e lo collegò a uno dei cavi Ethernet che serpeggiavano su tutto il pavimento. Googlò tutto quello che gli venne in mente che potesse essere correlato. "Prurito" diede 40.600.000 risultati. Provò query composte e ottenne risultati leggermente più pertinenti.

«Credo sia eczema da stress» disse Felix, alla fine.

«Io non ho l'eczema» disse Van.

Felix gli mostrò alcune foto crude di pelle rossa e arrabbiata ricoperta di scaglie bianche. «Eczema da stress» disse, leggendo la didascalia.

Van si esaminò le braccia. «Ho l'eczema» disse.

«Dice di tenerla idratata e di provare la crema al cortisone. Potresti provare il kit di pronto soccorso nei bagni del secondo piano. Mi pare di averne vista un po' là.» Come tutti i sysadmin, Felix aveva dato una frugata in giro per gli uffici, i bagni, la cucina e i ripostigli, mettendo da parte un rotolo di carta igienica nella sua borsa a tracolla insieme a tre o quattro barrette energetiche. Condividevano il cibo nella mensa per tacito accordo, ogni sysadmin che sorvegliava gli altri alla ricerca di segni di ingordigia e accaparramento. Tutti erano convinti che ci fossero ingordigia e accaparramento al di fuori della vista, perché tutti ne erano colpevoli in prima persona quando nessun altro guardava.

Van si alzò e quando la sua faccia entrò nella luce, Felix vide quanto aveva gli occhi gonfi. «Posterò sulla mailing list per degli antistaminici» disse Felix. C'erano state quattro mailing list e tre wiki per i sopravvissuti nell'edificio poche ore dopo la chiusura della prima riunione, e nei giorni seguenti si erano stabilizzati su una sola. Felix era ancora su una piccola mailing list con cinque dei suoi amici più fidati, due dei quali erano intrappolati in gabbie in altri paesi. Sospettava che il resto dei sysadmin stesse facendo lo stesso.

Van si allontanò barcollando. «Buona fortuna per le elezioni» disse, dando una pacca sulla spalla a Felix.

Felix si alzò e camminò avanti e indietro, fermandosi a guardare attraverso le finestre sporche. Gli incendi bruciavano ancora a Toronto, più di prima. Aveva provato a cercare mailing list o blog su cui i torontoniani stavano postando, ma gli unici che aveva trovato erano gestiti da altri geek in altri data center. Era possibile — anzi probabile — che ci fossero sopravvissuti là fuori che avevano priorità più urgenti che postare su Internet. Il telefono di casa funzionava ancora circa metà delle volte ma aveva smesso di chiamarlo dopo il secondo giorno, quando sentire la voce di Kelly sulla segreteria per la cinquantesima volta lo aveva fatto piangere nel mezzo di una riunione di pianificazione. Non era l'unico.

Giorno delle elezioni. Tempo di affrontare la musica.

> Sei nervoso?

> No,

digitò Felix.

> Non mi importa granché se vinco, a essere onesto. Sono solo contento che lo stiamo facendo. L'alternativa era stare seduti con le dita nel culo, aspettando che qualcuno desse di matto e aprisse la porta.

Il cursore restò fermo. Queen Kong aveva una latenza molto alta mentre dirigeva la sua banda di Googloidi per il Googleplex, facendo tutto il possibile per tenere online il suo data center. Tre delle gabbie offshore erano andate offline e due dei sei link di rete ridondanti erano bruciati. Per fortuna le query al secondo erano molto calate.

> C'è ancora la Cina

scrisse. Queen Kong aveva una grande lavagna con una mappa del mondo colorata in query-Google-al-secondo, e ci sapeva fare, mostrando il calo nel tempo con grafici colorati. Aveva caricato un sacco di video che mostravano come la peste e le bombe avevano spazzato il mondo: l'impennata iniziale di query di persone che volevano sapere cosa stava succedendo, poi il cupo e precipitoso crollo quando le piaghe avevano preso il sopravvento.

> La Cina è ancora al novanta percento circa del nominale.

Felix scosse la testa.

> Non puoi pensare che siano responsabili loro

> No

scrisse, ma poi cominciò a digitare qualcosa e si fermò.

> No certo che no. Credo all'Ipotesi Popovich. Ogni stronzo nel mondo usa gli altri stronzi come copertura. Ma la Cina li ha messi a tacere più duramente e velocemente di chiunque altro. Forse abbiamo finalmente trovato un uso per gli stati totalitari.

Felix non poté resistere. Scrisse:

> Sei fortunata che il tuo capo non possa vederti scrivere questo. Voi eravate partecipanti piuttosto entusiasti del Grande Firewall della Cina.

> Non è stata un'idea mia

scrisse.

> E il mio capo è morto. Sono probabilmente tutti morti. Tutta la Bay Area è stata colpita duramente, e poi c'è stato il terremoto.

Avevano guardato il flusso dati automatico dell'USGS dal 6.9 che aveva devastato la California settentrionale da Gilroy a Sebastopol. Le webcam del SoMa rivelavano la portata dei danni — esplosioni di condutture del gas, edifici retrofittati sismicamente che si accartocciavano come pile di costruzioni di bambini dopo un bel calcio. Il Googleplex, che galleggiava su una serie di gigantesche molle d'acciaio, aveva tremato come un piatto di gelatina, ma i rack erano rimasti al loro posto e il danno peggiore era stato un brutto livido all'occhio di un sysadmin che si era preso in faccia una crimpatrice volante.

> Scusa. Me n'ero dimenticato.

> Va bene. Abbiamo perso tutti qualcuno, no?

> Sì. Sì. Comunque, non sono preoccupato per le elezioni. Chiunque vinca, almeno stiamo FACENDO qualcosa

> Non se votano per uno dei fottistronzi

Fottistronzo era l'epiteto che alcuni sysadmin usavano per descrivere la fazione che voleva spegnere Internet. Queen Kong l'aveva coniato — apparentemente era nato come termine generico per descrivere i manager IT incompetenti che aveva masticato e sputato durante la sua carriera.

> Non lo faranno. Sono solo stanchi e tristi. Il tuo endorsement farà la differenza

I Googloidi erano uno dei blocchi più grandi e potenti rimasti, insieme agli equipaggi dei link satellitari e ai rimanenti equipaggi dei cavi transoceanici. L'endorsement di Queen Kong era stato una sorpresa e lui le aveva mandato un'email a cui lei aveva risposto laconicamente: "non possono comandare i fottistronzi."

> gtg

scrisse e poi la sua connessione cadde. Aprì un browser e caricò google.com. Il browser andò in timeout. Ricaricò, e poi ancora, e poi la pagina di Google tornò su. Qualunque cosa avesse colpito il posto di Queen Kong — mancanza di corrente, worm, un altro terremoto — l'aveva sistemata. Sbuffò una risata quando vide che avevano sostituito le O nel logo di Google con piccoli pianeti Terra con funghi atomici che si levavano da essi.

****

«Hai qualcosa da mangiare?» gli disse Van. Era metà pomeriggio, non che il tempo passasse particolarmente nel data center. Felix si frugò le tasche. Avevano messo un furiere al comando, ma non prima che tutti avessero arraffato del cibo dalle macchinette. Lui aveva avuto una dozzina di barrette energetiche e qualche mela. Aveva preso un paio di panini ma aveva saggiamente mangiato quelli per primi prima che diventassero stantii.

«Una barretta energetica rimasta» disse. Aveva notato una certa rilassatezza nella cintura quella mattina e per un attimo se n'era compiaciuto. Poi si era ricordato delle prese in giro di Kelly sul suo peso e aveva pianto un po'. Poi aveva mangiato due barrette energetiche, lasciandogliene una sola.

«Oh» disse Van. La sua faccia era più scavata che mai, le spalle che cadevano verso il suo petto a griglia per toast.

«Tieni» disse Felix. «Vota Felix.»

Van prese la barretta energetica e poi la posò sul tavolo. «OK, vorrei ridartela e dire, "No, non potrei," ma ho una fame del cazzo, quindi la prendo e la mangio, OK?»

«Per me va benissimo» disse Felix. «Buon appetito.»

«Come vanno le elezioni?» disse Van, dopo aver leccato pulito l'involucro.

«Boh» disse Felix. «Non ho controllato da un po'.» Stava vincendo con un margine sottile qualche ora prima. Non avere il suo laptop era un grosso handicap per queste cose. Su nelle gabbie, ce n'erano una dozzina come lui, poveri bastardi che il Giorno X erano usciti di casa senza pensare di portarsi qualcosa con il WiFi.

«Ti faranno a pezzi» disse Sario, sedendosi accanto a loro. Era diventato famoso nel centro per non dormire mai, per origliare, per attaccare briga dal vivo con la foga sventata di una flamewar su Usenet. «Il vincitore sarà qualcuno che capisce un paio di fatti fondamentali.» Alzò un pugno, poi elencò i punti alzando un dito alla volta. «Punto: I terroristi stanno usando Internet per distruggere il mondo, e noi dobbiamo distruggere Internet per primi. Punto: Anche se mi sbaglio, l'intera faccenda è una barzelletta. Finiremo il combustibile per i generatori abbastanza presto. Punto: O se non succede, sarà perché il vecchio mondo sarà tornato in funzione, e non gliene fregherà un cazzo del tuo nuovo mondo. Punto: Finiremo il cibo prima di finire le cose su cui litigare o i motivi per non uscire. Abbiamo la possibilità di fare qualcosa per aiutare il mondo a riprendersi: possiamo ammazzare la rete e toglierla come strumento ai cattivi. Oppure possiamo spostare qualche altra sedia a sdraio sulla tolda del tuo Titanic personale in nome di qualche dolce sogno su un "cyberspazio indipendente."»

Il fatto era che Sario aveva ragione. Avrebbero finito il combustibile in due giorni — l'energia intermittente dalla rete elettrica aveva allungato la vita dei generatori. E se accettavi la sua ipotesi che Internet venisse usata principalmente come strumento per organizzare altro caos, spegnerla sarebbe stata la cosa giusta da fare.

Ma il figlio di Felix e sua moglie erano morti. Non voleva ricostruire il vecchio mondo. Ne voleva uno nuovo. Il vecchio mondo era uno che non aveva più posto per lui. Non più.

Van si grattò la pelle viva e desquamata. Sbuffi di forfora e croste volteggiavano nell'aria viziata e unta. Sario arricciò un labbro verso di lui. «Fa schifo. Stiamo respirando aria riciclata, lo sai. Qualunque lebbra ti stia mangiando, aerosolizzarla nel sistema di areazione è piuttosto antisociale.»

«Sei tu l'autorità mondiale sull'antisocialità, Sario» disse Van. «Vattene o ti ammazzo col multi-tool.» Smise di grattarsi e si accarezzò le pinze multiuso al fianco come un pistolero.

«Sì, sono antisociale. Ho la sindrome di Asperger e non prendo medicine da quattro giorni. Tu che cazzo di scusa hai?»

Van si grattò ancora. «Mi dispiace» disse. «Non lo sapevo.»

Sario scoppiò a ridere. «Oh, sei impagabile. Scommetto che tre quarti di questo gruppo è borderline autistico. Io sono solo uno stronzo. Ma sono uno stronzo che non ha paura di dire la verità, e questo mi rende migliore di te, coglione.»

«Fottistronzo» disse Felix, «vaffanculo.»

****

Avevano meno di un giorno di combustibile quando Felix fu eletto primo Primo Ministro del Cyberspazio. Il primo scrutinio fu invalidato da un bot che aveva spammato il processo di voto e persero un giorno cruciale mentre contavano i voti una seconda volta.

Ma a quel punto, cominciava tutto a sembrare più una barzelletta. Metà dei data center erano andati al buio. Le mappe delle query Google di Queen Kong erano sempre più cupe man mano che più parti del mondo andavano offline, anche se lei manteneva una classifica delle nuove query in crescita — principalmente legate a salute, riparo, igiene e autodifesa.

Il carico dei worm rallentava. La corrente stava saltando a molti utenti domestici di PC, e restava giù, così i loro PC compromessi si spegnevano. Le dorsali erano ancora accese e lampeggianti, ma i messaggi da quei data center erano sempre più disperati. Felix non mangiava da un giorno e nemmeno nessuno in una stazione satellitare o in una testa di ponte transoceanica.

Anche l'acqua stava finendo.

Popovich e Rosenbaum vennero a prenderlo prima che potesse fare altro che rispondere a qualche messaggio di congratulazioni e postare un discorso di accettazione preconfezionato sui newsgroup.

«Apriamo le porte» disse Popovich. Come tutti loro, aveva perso peso ed era diventato trasandato e unto. Il suo odore corporeo era come una nuvola che proveniva dai sacchi della spazzatura dietro una pescheria in una giornata di sole. Felix era piuttosto sicuro di non avere un odore migliore.

«Fate una ricognizione? Cercate altro combustibile? Possiamo organizzare un gruppo di lavoro — ottima idea.»

Rosenbaum scosse la testa tristemente. «Andiamo a cercare le nostre famiglie. Qualunque cosa ci sia là fuori, si è esaurita. O no. In entrambi i casi, non c'è futuro qui dentro.»

«E la manutenzione della rete?» disse Felix, anche se sapeva le risposte. «Chi terrà su i router?»

«Ti daremo le password di root di tutto» disse Popovich. Le mani gli tremavano e gli occhi erano velati. Come molti dei fumatori bloccati nel data center, aveva smesso di colpo quella settimana. I prodotti con caffeina erano finiti due giorni prima, tra l'altro. I fumatori la passavano dura.

«E io resto qui e tengo tutto online?»

«Tu e chiunque altro a cui importi ancora.»

Felix sapeva di aver sprecato la sua opportunità. L'elezione era sembrata nobile e coraggiosa, ma col senno di poi era stata solo una scusa per litigare quando avrebbero dovuto capire cosa fare dopo. Il problema era che non c'era niente da fare dopo.

«Non posso costringervi a restare» disse.

«Già, non puoi.» Popovich girò sui tacchi e se ne andò. Rosenbaum lo guardò andare, poi strinse la spalla di Felix e la serrò.

«Grazie, Felix. Era un bellissimo sogno. Lo è ancora. Magari troveremo qualcosa da mangiare e del combustibile e torneremo.»

Rosenbaum aveva una sorella con cui era stato in contatto via IM nei primi giorni dopo lo scoppio della crisi. Poi aveva smesso di rispondere. I sysadmin erano divisi tra quelli che avevano avuto la possibilità di dire addio e quelli che non l'avevano avuta. Ognuno era convinto che l'altra categoria stesse meglio.

Postarono la notizia sul newsgroup interno — erano pur sempre geek, dopotutto, e c'era un piccolo picchetto d'onore al piano terra, geek che li guardarono passare verso le doppie porte. Azionarono le tastiere e le saracinesche d'acciaio si alzarono, poi il primo set di porte si aprì. Entrarono nel vestibolo e si tirarono dietro le porte. Le porte esterne si aprirono. Fuori c'era un sole molto luminoso, e a parte quanto fosse tutto vuoto, sembrava molto normale. Da spezzare il cuore.

I due fecero un passo esitante fuori nel mondo. Poi un altro. Si girarono per salutare le masse riunite. Poi entrambi si aggrapparono la gola e cominciarono a tremare e contorcersi, accasciandosi in un mucchio a terra.

«Meeeee—!» fu tutto quello che Felix riuscì a tirare fuori prima che entrambi si spolverassero e si alzassero in piedi, ridendo così forte da tenersi i fianchi. Salutarono un'altra volta e girarono sui tacchi.

«Amico, quei due sono malati» disse Van. Si grattò le braccia, che avevano lunghi graffi sanguinanti. I suoi vestiti erano così coperti di croste da sembrare spolverati di zucchero a velo.

«Io l'ho trovato divertente» disse Felix.

«Cristo che fame» disse Van, come conversazione.

«Per tua fortuna, abbiamo tutti i pacchetti che possiamo mangiare» disse Felix.

«Sei troppo buono con noi sottoposti, Signor Presidente» disse Van.

«Primo Ministro» disse. «E tu non sei un sottoposto, sei il Vice Primo Ministro. Il mio addetto al taglio dei nastri e alla distribuzione di assegni premio giganti.»

Sollevò il morale di entrambi. Guardare Popovich e Rosenbaum andarsene, li sollevò. Felix seppe allora che se ne sarebbero andati tutti presto.

Era stato predeterminato dalla scorta di combustibile, ma chi voleva aspettare che il combustibile finisse, comunque?

****

> stamattina metà dei miei se ne sono andati

scrisse Queen Kong. Google reggeva piuttosto bene comunque, ovviamente. Il carico sui server era molto più leggero di quanto fosse dai tempi in cui Google stava su un mucchio di PC assemblati a mano sotto una scrivania a Stanford.

> noi siamo scesi a un quarto

scrisse Felix. Era passato solo un giorno da quando Popovich e Rosenbaum se n'erano andati, ma il traffico sui newsgroup era calato quasi a zero. Lui e Van non avevano avuto molto tempo per giocare alla Repubblica del Cyberspazio. Erano stati troppo occupati a imparare i sistemi che Popovich gli aveva passato, i router grossi grossi che continuavano a funzionare come principale punto di interscambio per tutte le dorsali di rete del Canada.

Comunque, ogni tanto qualcuno postava ancora sui newsgroup, generalmente per dire addio. Le vecchie flammewar su chi sarebbe stato PM, o se avrebbero spento la rete, o chi prendeva troppo cibo — tutto sparito.

Ricaricò il newsgroup. C'era un messaggio tipico.

> Processi impazziti su Solaris TK

>

> Ehm, ciao. Sono solo un MCSE leggero ma sono l'unico sveglio qui e quattro dei DSLAM sono appena andati giù. Sembra che ci sia del codice di fatturazione custom che sta cercando di calcolare quanto addebitare ai nostri clienti aziendali e ha generato diecimila thread e sta mangiando tutto lo swap. Vorrei solo killarlo ma non ci riesco. C'è qualche invocazione magica che devo fare per far fuori questa roba dalla maledetta scatola weenix? Cioè, non è che qualcuno dei nostri clienti ci pagherà mai più. Chiederei al tizio che ha scritto questo codice, ma è praticamente morto per quanto ne sappiamo.

Ricaricò. C'era una risposta. Era breve, autorevole e utile — esattamente il tipo di cosa che non vedevi quasi mai in un newsgroup di alto livello quando un novellino postava una domanda stupida. L'apocalisse aveva risvegliato lo spirito di paziente disponibilità nella comunità mondiale dei sysop.

Van gli lesse alle spalle. «Porca puttana, chi l'avrebbe detto?»

Guardò il messaggio di nuovo. Era di Will Sario.

Passò alla sua finestra di chat.

> sario pensavo che volessi la rete morta perché stai aiutando gli mcse a sistemare i loro box?

>  Beh Signor PM, forse non sopporto di vedere un computer soffrire nelle mani di un dilettante.

Passò al canale con Queen Kong.

> Quanto?

> Da quando ho dormito? Due giorni. Prima che finiamo il combustibile? Tre giorni. Da quando abbiamo finito il cibo? Due giorni.

> Gesù. Non ho dormito neanch'io la scorsa notte. Siamo un po' a corto di personale qui.

> asl? Sono monica e vivo a pasadena e sono annoiata coi compiti. Vuoi scaricare la mia foto???

I bot trojan erano ovunque su IRC in quei giorni, saltando su ogni canale che avesse un po' di traffico. A volte ne beccavi cinque o sei che flirtavano tra di loro. Era piuttosto surreale guardare un malware che cercava di convincere un'altra istanza di se stesso a scaricare un trojan.

Kickarono entrambi il bot dal canale contemporaneamente. Ormai aveva uno script per quello. Lo spam non era calato nemmeno un po'.

> Come mai lo spam non cala? Metà dei maledetti data center sono andati al buio

Queen Kong fece una lunga pausa prima di scrivere. Come era diventato automatico quando aveva latenza alta, lui ricaricò la homepage di Google. Effettivamente, era giù.

> Sario, hai qualcosa da mangiare?

> Non ti mancheranno un paio di pasti in più, Vostra Eccellenza

Van era tornato su Mayor McCheese ma era nello stesso canale.

«Che stronzo. Però stai diventando un figurino, amico.»

Van non aveva un bell'aspetto. Sembrava che lo potessi buttare giù con un soffio e aveva un tono catarroso e debole nel parlare.

> hey kong tutto ok?

> tutto bene ho solo dovuto andare a prendere a calci qualcuno

«Come va il traffico, Van?»

«Giù del 25 percento da stamattina» disse. C'erano un mucchio di nodi le cui connessioni passavano attraverso di loro. Presumibilmente la maggior parte erano clienti residenziali o commerciali in posti dove la corrente era ancora accesa e le centrali telefoniche erano ancora vive.

Ogni tanto, Felix intercettava le connessioni per vedere se riusciva a trovare qualcuno con notizie dal mondo esterno. Quasi tutto era traffico automatizzato, però: backup di rete, aggiornamenti di stato. Spam. Un sacco di spam.

> Lo spam è ancora su perché i servizi che bloccano lo spam stanno cedendo più velocemente dei servizi che lo creano. Tutta la roba anti-worm è centralizzata in un paio di posti. La roba cattiva è su un milione di computer zombie. Se solo gli utenti decerebrati avessero avuto il buon senso di spegnere i loro PC prima di stramazzare o fuggire

> al ritmo a cui andiamo entro cena routeremo solo spam

Van si schiarì la gola, un suono doloroso. «A proposito» disse. «Credo che succederà prima. Felix, non credo che qualcuno si accorgerebbe se ce ne andassimo via da qui.»

Felix lo guardò, la pelle color carne in scatola striata di lunghi graffi arrabbiati. Le dita gli tremavano.

«Bevi abbastanza acqua?»

Van annuì. «Tutto il fottuto giorno, ogni dieci secondi. Qualunque cosa per tenermi la pancia piena.» Indicò una bottiglia di Pepsi Max riempita d'acqua accanto a lui.

«Facciamo una riunione» disse.

****

Erano stati quarantatré il Giorno D. Adesso erano quindici. Sei avevano risposto alla convocazione della riunione semplicemente andando via. Tutti sapevano senza bisogno che glielo dicessero di cosa trattava la riunione.

«Quindi è così, lasciate che vada tutto a pezzi?» Sario era l'unico con l'energia sufficiente per arrabbiarsi come si deve. Sarebbe andato alla tomba arrabbiato. Le vene del collo e della fronte gli pulsavano di rabbia. I pugni gli tremavano di rabbia. Tutti gli altri geek abbassarono lo sguardo sui loro schermi alla sua vista, alzando gli occhi all'unisono per una volta sulla discussione, senza tenere un occhio su un log di chat o un log di servizio.

«Sario, mi stai prendendo per il culo» disse Felix. «Tu volevi staccare la maledetta spina!»

«Volevo che fosse pulito» gridò. «Non volevo che sanguinasse e stramazzasse in piccoli rantoli e conati per l'eternità. Volevo che fosse un atto di volontà della comunità globale dei suoi custodi. Volevo che fosse un atto affermativo di mani umane. Non l'entropia e il codice di merda e i worm che vincono. Fanculo, è esattamente quello che è successo là fuori.»

Su nella mensa dell'ultimo piano, c'erano finestre tutt'intorno, rinforzate e che deviavano la luce, e per consuetudine erano tutte con le tende abbassate. Adesso Sario corse per la stanza, tirando su le tende. Come diavolo fa ad avere l'energia per correre? si chiese Felix. Lui riusciva a malapena a salire le scale fino alla sala riunioni.

La luce cruda del giorno irruppe dentro. Era una bella giornata di sole là fuori, ma ovunque guardassi attraverso quella vista imponente sullo skyline di Toronto, c'erano colonne di fumo che salivano. La torre TD, un gigantesco mattone di vetro modernista nero, vomitava fiamme verso il cielo. «Sta andando tutto a pezzi, come va sempre tutto a pezzi.

«Ascoltate, ascoltate. Se lasciamo la rete a morire lentamente, parti di essa resteranno online per mesi. Forse anni. E cosa ci girerà sopra? Malware. Worm. Spam. Processi di sistema. Zone transfer. Le cose che usiamo si degradano e richiedono manutenzione costante. Le cose che abbandoniamo non vengono usate e durano per sempre. Lasceremo la rete come una fossa di calce piena di rifiuti industriali. Questa sarà la nostra cazzo di eredità — l'eredità di ogni tasto che tu e io e chiunque, ovunque, abbia mai premuto. Capite? La lasceremo a morire lentamente come un cane ferito, invece di darle un colpo pulito alla testa.»

Van si grattò le guance, poi Felix vide che si stava asciugando le lacrime.

«Sario, non hai torto, ma non hai nemmeno ragione» disse. «Lasciarla su a zoppicare è giusto. Zoppicheremo tutti per molto tempo, e magari sarà utile a qualcuno. Se c'è anche un solo pacchetto che viene routato da un qualsiasi utente a un qualsiasi altro utente, ovunque nel mondo, sta facendo il suo lavoro.»

«Se vuoi una morte pulita, puoi farlo» disse Felix. «Sono il PM e dico che si può. Vi do root. A tutti voi.» Si girò verso la lavagna dove i lavoranti della mensa una volta scarabocchiavano le specialità del giorno. Ora era coperta di resti di accesi dibattiti tecnici in cui i sysadmin si erano impegnati nei giorni dal giorno.

Pulì una zona con la manica e cominciò a scrivere password lunghe e complicate, alfanumeriche e condite di punteggiatura. Felix aveva il dono di ricordare quel tipo di password. Dubitava che gli sarebbe mai più servito granché.

****

> ce ne andiamo, kong. Il combustibile è quasi finito comunque

> già beh è giusto allora. è stato un onore, signor primo ministro

> starai bene?

> ho requisito un giovane sysadmin per soddisfare le mie esigenze femminili e abbiamo trovato un'altra scorta di cibo che ci basterà un paio di settimane ora che siamo scesi a quindici admin—sto alla grande amico

> sei incredibile, Queen Kong, davvero. Però non fare l'eroina. Quando devi andare vai. Deve esserci qualcosa là fuori

> stai attento felix, davvero—ah ti ho detto che le query sono aumentate in Romania? forse si stanno rimettendo in piedi

> davvero?

> sì, davvero. siamo duri a morire—come gli scarafaggi del cazzo

La sua connessione cadde. Passò a Firefox e ricaricò Google e era giù. Ricaricò e ricaricò e ricaricò, ma non tornò su. Chiuse gli occhi e ascoltò Van grattarsi le gambe e poi lo sentì digitare qualcosa.

«Sono tornati su» disse.

Felix soffiò fuori un respiro. Mandò il messaggio al newsgroup, uno che aveva rimaneggiato cinque volte prima di decidere: "Prendetevi cura di questo posto, OK? Torneremo, un giorno."

Se ne andavano tutti tranne Sario. Sario non se ne sarebbe andato. Ma scese a salutarli.

I sysadmin si radunarono nell'atrio e Felix fece alzare la porta di sicurezza, e la luce irruppe dentro.

Sario tese la mano.

«Buona fortuna» disse.

«Anche a te» disse Felix. Aveva una presa salda, Sario, più forte di quanto avesse diritto di essere. «Forse avevi ragione» disse.

«Forse» disse.

«Staccherai la spina?»

Sario alzò lo sguardo al controsoffitto, come se potesse vedere attraverso i pavimenti rinforzati i rack ronzanti sopra di loro. «Chi lo sa?» disse alla fine.

Van si grattò e un turbinio di pagliuzze bianche danzò nella luce del sole.

«Andiamo a trovarti una farmacia» disse Felix. Camminò verso la porta e gli altri sysadmin lo seguirono.

Aspettarono che le porte interne si chiudessero dietro di loro e poi Felix aprì le porte esterne. L'aria aveva l'odore e il sapore dell'erba tagliata, delle prime gocce di pioggia, del lago e del cielo, dell'esterno e del mondo, un vecchio amico di cui non si avevano notizie da un'eternità.

«Ciao, Felix» dissero gli altri sysadmin. Si stavano disperdendo mentre lui restava inchiodato in cima alla breve scalinata di cemento. La luce gli feriva gli occhi e li faceva lacrimare.

«Credo che ci sia una farmacia su King Street» disse a Van. «Spacchiamo una vetrina e ti prendiamo del cortisone, OK?»

«Tu sei il Primo Ministro» disse Van. «Fai strada.»

****

![Illustrazione](/posts/2007-11-21-when-sysadmins-ruled-the-earth/sysadmins-end.jpg)

Non videro un'anima viva nei quindici minuti di cammino. Non si sentiva un solo suono a parte qualche verso di uccelli e qualche gemito lontano, e il vento nei cavi elettrici sopra le loro teste. Era come camminare sulla superficie della luna.

«Scommetto che hanno le barrette di cioccolato alla farmacia» disse Van.

Lo stomaco di Felix si contrasse. Cibo. «Wow» disse, con la bocca piena di saliva.

Passarono davanti a una piccola utilitaria e sul sedile anteriore c'era il corpo essiccato di una donna che teneva il corpo essiccato di un bambino, e la bocca gli si riempì di bile acida, anche se l'odore era debole attraverso i finestrini chiusi.

Non aveva pensato a Kelly o a 2.0 da giorni. Cadde in ginocchio e vomitò di nuovo. Qui fuori nel mondo reale, la sua famiglia era morta. Tutti quelli che conosceva erano morti. Voleva solo sdraiarsi sul marciapiede e aspettare di morire anche lui.

Le mani ruvide di Van gli scivolarono sotto le ascelle e lo tirarono debolmente. «Non adesso» disse. «Quando saremo al sicuro dentro da qualche parte e avremo mangiato qualcosa, allora e solo allora potrai fare questo, ma non adesso. Mi capisci, Felix? Adesso cazzo no.»

La bestemmia gli arrivò. Si alzò in piedi. Le ginocchia gli tremavano.

«Solo un altro isolato» disse Van, e passò il braccio di Felix intorno alle sue spalle e lo condusse avanti.

«Grazie, Van. Mi dispiace.»

«Figurati» disse. «Hai bisogno di una doccia, urgente. Senza offesa.»

«Nessuna offesa.»

La farmacia aveva una saracinesca di sicurezza metallica, ma era stata strappata via dalle vetrine, che erano state rudemente sfondate. Felix e Van si infilarono nel varco ed entrarono nella farmacia buia. Qualche espositore era stato rovesciato, ma a parte quello, sembrava a posto. Vicino alle casse, Felix individuò i rack di barrette di cioccolato nello stesso istante in cui li vide Van, e si precipitarono e ne afferrarono una manciata ciascuno, rimpinzandosi.

«Voi due mangiate come porci.»

Si girarono entrambi di scatto alla voce della donna. Teneva un'ascia da pompiere che era quasi grande quanto lei. Portava un camice e scarpe comode.

«Prendete quello che vi serve e andate, OK? Non c'è motivo di avere problemi.» Aveva il mento a punta e lo sguardo acuto. Dimostrava una quarantina d'anni. Non assomigliava per niente a Kelly, il che era un bene, perché Felix sentiva già il bisogno di correre ad abbracciarla così com'era. Un'altra persona viva!

«Lei è un medico?» disse Felix. Sotto il camice portava un completo da infermiera, vide.

«Ve ne andate?» Brandì l'ascia.

Felix alzò le mani. «Seriamente, è un medico? Una farmacista?»

«Ero un'infermiera, dieci anni fa. Ora faccio soprattutto la web designer.»

«Mi prende in giro» disse Felix.

«Non hai mai conosciuto una ragazza che ne capiva di computer?»

«In realtà, un'amica mia che gestisce il data center di Google è una ragazza. Una donna, intendo.»

«Mi prende in giro» disse lei. «Una donna gestiva il data center di Google?»

«Gestisce» disse Felix. «È ancora online.»

«Ma va» disse lei. Abbassò l'ascia.

«Giuro. Ha della crema al cortisone? Posso raccontarle la storia. Mi chiamo Felix e questo è Van, che ha bisogno di tutti gli antistaminici che riesce a dargli.»

«Che riesco a dargli? Felix vecchio mio, ho abbastanza roba qui per cento anni. Questa roba scadrà molto prima di finire. Ma mi stai dicendo che la rete è ancora su?»

«È ancora su» disse. «Più o meno. È quello che abbiamo fatto tutta la settimana. Tenerla online. Potrebbe non durare molto più a lungo, però.»

«No» disse lei. «Immagino di no.» Posò l'ascia. «Hai qualcosa da scambiare? Non mi serve molto, ma ho cercato di tenermi su il morale barattando con i vicini. È come giocare a Civilization.»

«Ha dei vicini?»

«Almeno dieci» disse lei. «La gente del ristorante di fronte fa una zuppa niente male, anche se la maggior parte della verdura è in scatola. Però mi hanno svuotato lo Sterno.»

«Ha dei vicini e fa baratto con loro?»

«Beh, più o meno. Sarebbe piuttosto solitario senza di loro. Ho curato quel che potevo di raffreddori e acciacchi. Rimesso a posto un osso — frattura al polso. Senti, volete del pane bianco e burro d'arachidi? Ne ho una montagna. Il tuo amico sembra aver bisogno di un pasto.»

«Sì per favore» disse Van. «Non abbiamo niente da scambiare, ma siamo entrambi maniaci del lavoro disposti a imparare un mestiere. Le servono degli assistenti?»

«Non proprio.» Fece ruotare l'ascia sulla testa. «Ma un po' di compagnia non mi dispiacerebbe.»

Mangiarono i panini e poi della zuppa. La gente del ristorante gliela portò e fece le presentazioni, anche se Felix vide i loro nasi arricciarsi e appurò che c'era un impianto idraulico funzionante nel retro. Van entrò a farsi un bagno di spugna e poi lo seguì.

«Nessuno di noi sa cosa fare» disse la donna. Si chiamava Rosa, e aveva trovato loro una bottiglia di vino e dei bicchieri di plastica usa e getta dal reparto casalinghi. «Pensavo che avremmo avuto elicotteri o carri armati o anche saccheggiatori, ma c'è solo silenzio.»

«Tu mi sembri essere stata piuttosto silenziosa» disse Felix.

«Non volevo attirare il tipo sbagliato di attenzione.»

«Hai mai pensato che magari c'è un sacco di gente là fuori che sta facendo la stessa cosa? Magari se ci mettiamo tutti insieme troviamo qualcosa da fare.»

«O magari ci tagliano la gola» disse lei.

Van annuì. «Ha un punto.»

Felix era in piedi. «No, non possiamo pensarla così. Signora, siamo a un punto cruciale qui. Possiamo andare a fondo per negligenza, rintanandoci nei nostri buchi, oppure possiamo provare a costruire qualcosa di meglio.»

«Meglio?» Fece un verso scettico.

«OK, non meglio. Qualcosa, però. Costruire qualcosa di nuovo è meglio che lasciare tutto svanire. Cristo, cosa farai quando avrai letto tutte le riviste e mangiato tutte le patatine qui dentro?»

Rosa scosse la testa. «Belle parole» disse. «Ma che diavolo facciamo, concretamente?»

«Qualcosa» disse Felix. «Faremo qualcosa. Qualcosa è meglio di niente. Prenderemo questo pezzo di mondo dove la gente si parla, e lo espanderemo. Troveremo tutti quelli che possiamo e ci prenderemo cura di loro e loro si prenderanno cura di noi. Probabilmente faremo casino. Probabilmente falliremo. Ma preferisco fallire che arrendermi.»

Van rise. «Felix, sei più matto di Sario, lo sai?»

«Andremo a trascinarlo fuori, prima cosa domattina. Anche lui farà parte di tutto questo. Tutti lo faranno. Al diavolo la fine del mondo. Il mondo non finisce. Gli esseri umani non sono il tipo di cose che hanno una fine.»

Rosa scosse di nuovo la testa, ma adesso sorrideva un po'. «E tu sarai cosa, il Papa-Imperatore del Mondo?»

«Preferisce Primo Ministro» disse Van in un sussurro teatrale. Gli antistaminici avevano fatto miracoli sulla sua pelle, che era passata da un rosso furioso a un rosa tenue.

«Vuoi fare il Ministro della Sanità, Rosa?» disse.

«Ragazzi» disse lei. «State giocando. E questa. Vi aiuterò come posso, a patto che non mi chiediate mai di chiamarvi Primo Ministro e non mi chiamiate mai Ministro della Sanità.»

«Affare fatto» disse lui.

Van riempì i loro bicchieri, capovolgendo la bottiglia di vino per tirar fuori le ultime gocce.

Alzarono i bicchieri. «Al mondo» disse Felix. «All'umanità.» Ci pensò un attimo. «Alla ricostruzione.»

«A qualunque cosa» disse Van.

«A qualunque cosa» disse Felix. «A tutto.»

«A tutto» disse Rosa.

Bevvero. Voleva andare a vedere la casa — vedere Kelly e 2.0, anche se lo stomaco gli si rivoltava al pensiero di cosa avrebbe potuto trovare. Ma il giorno dopo, cominciarono a ricostruire. E mesi dopo, ricominciarono da capo, quando i disaccordi frantumarono il fragile gruppetto che avevano messo insieme. E un anno dopo, ricominciarono da capo ancora. E cinque anni dopo, ricominciarono di nuovo.

Passarono quasi sei mesi prima che tornasse a casa. Van lo accompagnò, pedalando dietro di lui sulle biciclette che usavano per spostarsi in città. Più andavano a nord, più si faceva forte l'odore di legno bruciato. C'erano un sacco di case bruciate. A volte i saccheggiatori bruciavano le case che avevano depredato, ma più spesso era solo la natura, il tipo di incendi che si verificano nelle foreste e sulle montagne. C'erano sei isolati soffocanti e bruciati dove ogni casa era bruciata prima di arrivare a casa.

Ma il vecchio quartiere residenziale di Felix era ancora in piedi, un'oasi di edifici inquietantemente incontaminati che sembravano come se i loro proprietari un po' negligenti fossero semplicemente usciti a comprare della vernice e lame nuove per il tosaerba per rimettere in sesto le loro vecchie case.

Era peggio, in qualche modo. Scese dalla bici all'ingresso del quartiere e camminarono con le bici in silenzio, ascoltando il sussurro del vento tra gli alberi. L'inverno stava arrivando tardi quell'anno, ma stava arrivando, e mentre il sudore si asciugava nel vento, Felix cominciò a tremare.

Non aveva più le chiavi. Erano al data center, mesi e mondi lontano. Provò la maniglia della porta, ma non girava. Spinse con la spalla e la porta si staccò dallo stipite bagnato e marcio con un forte rumore di legno che si spezza. La casa stava marcendo dall'interno.

La porta fece splash quando atterrò. La casa era piena di acqua stagnante, dieci centimetri di acqua puzzolente coperta di lenticchie d'acqua nel soggiorno. Ci sguazzò dentro con cautela, sentendo le assi del pavimento cedere come spugne sotto ogni passo.

Su per le scale, con il naso pieno di quel terribile tanfo verde di muffa. In camera da letto, i mobili familiari come un amico d'infanzia.

Kelly era nel letto con 2.0. Dal modo in cui giacevano, era chiaro che non se n'erano andati facilmente — erano piegati in due, Kelly raggomitolata intorno a 2.0. La pelle era gonfia, rendendoli quasi irriconoscibili. L'odore — Dio, l'odore.

La testa di Felix girò. Pensò che sarebbe caduto e si aggrappò al cassettone. Un'emozione che non riusciva a nominare — rabbia, ira, dolore? — lo fece respirare forte, boccheggiare come se stesse annegando.

E poi era finita. Il mondo era finito. Kelly e 2.0 — finiti. E lui aveva un lavoro da fare. Piegò la coperta sopra di loro — Van lo aiutò, solennemente. Andarono nel giardino davanti e fecero i turni a scavare, usando la pala del garage che Kelly usava per il giardinaggio. Avevano molta esperienza a scavare tombe ormai. Molta esperienza a maneggiare i morti. Scavarono, e cani diffidenti li osservavano dall'erba alta dei prati vicini, ma erano anche bravi a scacciare i cani con pietre ben lanciate.

Quando la tomba fu scavata, deposero la moglie e il figlio di Felix. Felix cercò delle parole da dire sul tumulo, ma non ne vennero. Aveva scavato così tante tombe per le mogli di così tanti uomini e i mariti di così tante donne e così tanti bambini — le parole erano finite da tempo.

Felix scavò fossati e recuperò lattine e seppellì i morti. Piantò e raccolse. Aggiustò qualche macchina e imparò a fare il biodiesel. Alla fine finì in un data center per un piccolo governo — i piccoli governi andavano e venivano, ma questo era abbastanza furbo da voler tenere dei registri e aveva bisogno di qualcuno che facesse funzionare tutto, e Van andò con lui.

Passavano molto tempo nelle chat room e a volte si imbattevano in vecchi amici dello strano periodo in cui avevano gestito la Repubblica Distribuita del Cyberspazio, geek che insistevano a chiamarlo PM, anche se nel mondo reale nessuno lo chiamava più così.

Non era una bella vita, la maggior parte del tempo. Le ferite di Felix non guarirono mai, e nemmeno quelle della maggior parte degli altri. C'erano malattie persistenti e improvvise. Tragedia su tragedia.

Ma a Felix piaceva il suo data center. Lì nel ronzio dei rack, non si sentiva mai come se fossero i primi giorni di una nazione migliore, ma non si sentiva mai nemmeno come se fossero gli ultimi.

> vai a letto, felix

> presto, kong, presto—ho quasi fatto partire questo backup

> sei un tossico, amico.

> senti chi parla

Ricaricò la homepage di Google. Queen Kong la teneva online da un paio d'anni ormai. Le O in Google cambiavano continuamente, ogni volta che le veniva l'ispirazione. Oggi erano piccoli globi a fumetti, uno sorridente e l'altro accigliato.

La guardò a lungo e tornò in un terminale a controllare il suo backup. Girava pulito, per una volta. I registri del piccolo governo erano al sicuro.

> ok buonanotte

> stammi bene

Van lo salutò con la mano mentre si trascinava verso la porta, stirandosi la schiena con una lunga serie di scrocchi.

«Dormi bene, capo» disse.

«Non restare qui tutta la notte di nuovo» disse Felix. «Anche tu hai bisogno di dormire.»

«Sei troppo buono con noi sottoposti» disse Van, e tornò a digitare.

Felix andò alla porta e uscì nella notte. Dietro di lui, il generatore a biodiesel ronzava e produceva i suoi fumi acri. C'era la luna del raccolto, che lui adorava. Domani sarebbe tornato a riparare un altro computer e a combattere l'entropia ancora una volta. E perché no?

Era quello che faceva. Era un sysadmin.
