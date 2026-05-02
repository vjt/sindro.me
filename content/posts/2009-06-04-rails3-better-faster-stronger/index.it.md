---
title: 'Rails 3: Better, Faster, Stronger'
date: 2009-06-04
tags: [rails, ruby, open-source]
---

{{< retrospective year="2026" >}}
Rails 3.0 è uscito nel 2010 e il merge con Merb è stato un successo. Oggi Rails è alla versione 8.x, ha integrato tutto quello che qui si auspicava (modularità, API stabili, engines come cittadini di prima classe) e molto di più. Lighthouse è stato dismesso, therubymine.com non esiste più, e molti dei link in questo articolo sono morti — ma le idee di fondo restano valide.
{{< /retrospective >}}

![Rails 3: Harder, Better, Faster, Stronger](/posts/2009-06-04-rails3-better-faster-stronger/rails3-harder-better-faster-stronger.png)

Tutti (o quasi) gli sviluppatori web conoscono o hanno sentito almeno parlare di [Ruby on Rails](http://www.rubyonrails.com/), un [framework full-stack](http://en.wikipedia.org/wiki/Web_application_framework) per la creazione di applicazioni web utilizzando il linguaggio di programmazione [Ruby](http://www.ruby-lang.org/).

<!--more-->

Qualora non abbiate mai sentito parlare nè di Rails, nè di web application, sulla [wikipedia italiana](http://it.wikipedia.org/w/index.php?title=Ruby_on_Rails&oldid=23455980) è presente una brevissima panoramica su di esso, in cui è impossibile non essere colpiti dalla sua Filosofia. Rails è infatti definito dall'autore [David Heinemeier Hansson](http://loudthinking.com/) "[opinionated software](http://roohit.com/800c1)", cioè un software che impone determinati approcci e workflow durante la progettazione e la stesura di un progetto, con i vantaggi e [svantaggi](http://www.martinfowler.com/bliki/EnterpriseRails.html) che questo può portare.

Altra caratteristica che ha contraddistinto le prime evoluzioni di Rails (2003-2007) è stata la mancanza di interfacce robuste per la sua estensione attraverso plug-in esterni, complice anche una controversa caratteristica di Ruby: il [monkeypatching](http://en.wikipedia.org/wiki/Monkey_patch). In Ruby le classi non sono chiuse: è possibile modificarne il funzionamento in qualsiasi punto del programma, e questo vale anche per le classi base (ad es. String, Integer, …). Ciò ha portato al proliferare di plug-in ed estensioni al framework che facevano leva su dettagli implementativi privati, la cui stabilità nel tempo non è garantita, con tutti i problemi di [manutenibilità](http://it.wikipedia.org/wiki/Manutenibilit%C3%A0) che ne derivano: chi ha seguito le prime fasi del rilascio di Rails non può non ricordare il [lungo](http://weblog.rubyonrails.org/2005/11/11/why-engines-and-components-are-not-evil-but-distracting/) [dibattito](http://rails-engines.rubyforge.org/wiki/wiki.pl?OhGodWhatHaveWeDone) che seguì dall'implementazione dei [Rails Engines](http://rails-engines.org/).

In seguito, gli engines sono stati [rivalutati](http://www.coryosborn.com/posts/railsconf-day-2-rails-engines), tanto da [venir presentati](http://assets.en.oreilly.com/1/event/24/The%20Even-Darker%20Art%20of%20Rails%20Engines%20Presentation.pdf) all'edizione 2009 di [RailsConf](http://en.oreilly.com/rails2009/), come una via funzionale per la realizzazione di componenti software riutilizzabili e completi, poichè possiedono dei Model, View, Controller, e delle Route che connettono gli URI a cui risponde l'applicazione al codice che ne implementa la logica.

Questo cambio di visione da parte di DHH è stato determinato dalla sua esperienza di trovarsi a reimplementare diverse applicazioni che sarebbero potute essere racchiuse in un engine e successivamente riutilizzate.

Simili considerazioni sono state anche espresse in proposito al forte carattere opinionated di Rails, i cui approcci imposti non riguardano solo l'utilizzo di un certo [pattern](http://c2.com/cgi/wiki?DesignPatterns), ma anche l'imposizione di uno specifico "pezzo di software" che lo implementi. Ad esempio, per accedere ad un database in Rails viene utilizzato [ActiveRecord](http://ar.rubyonrails.org/), un'implementazione del pattern di [Object-Relational Mapping](http://c2.com/cgi/wiki?ObjectRelationalMapping) che permette di avvicinare il [modello relazionale](http://en.wikipedia.org/wiki/RDBMS) dei database attualmente diffusi sul mercato al modello [object](http://en.wikipedia.org/wiki/Object_oriented) [oriented](http://c2.com/cgi/wiki?ObjectOriented) utilizzato da Ruby e pervasivamente ereditato da Rails.

## Il contesto Open Source

In un contesto open source, però, tale restrizione è vista come castrante da tanti developer. Nonostante ActiveRecord faccia bene il suo lavoro, è importante poter scegliere il componente più adatto ad un determinato scopo: è un concetto che qualsiasi sviluppatore esperto fa suo, tralasciando le inutili guerre di religione :).

La modularità, estendibilità e la presenza di un'interfaccia ragionata e soprattutto stabile sono i principi fondanti di [Merb](http://merbivore.com/), un altro framework Ruby-based per la creazione di applicazioni web database-backed, la cui headline è "Looking for a hacker framework?". Merb consiste in un piccolo core di funzionalità ben organizzate, su cui una serie di plug-in costruiscono e realizzano l'impianto completo su cui poi realizzare la propria applicazione.

Con Merb è possibile utilizzare il preferito degli ORM, template engine, mailer e testing frameworks disponibili, in quanto tutti si appoggiano al medesimo [core](http://merbivore.com/features.html). Inoltre è semplice realizzarne di nuovi per soddisfare le esigenze più disparate: è una filosofia [molto simile a quella UNIX](http://en.wikipedia.org/wiki/Unix_philosophy), in cui ogni singolo tool software implementa limitate funzionalità (ma bene), dove per risolvere problemi più complessi è sufficiente l'utilizzo in cascata di diversi tool.

Dati i numerosi vantaggi di questo approccio, completamente opposto a quello iniziale di Rails, anche un [Rated R individual](http://www.loudthinking.com/posts/39-im-an-r-rated-individual) dalle strong opinions ha deciso di cambiare idea ancora una volta, e annunciare al mondo la notizia che nessuno si aspettava di ricevere: [rails e merb](http://weblog.rubyonrails.org/2008/12/23/merb-gets-merged-into-rails-3) [diventeranno un unico progetto](http://yehudakatz.com/2008/12/23/rails-and-merb-merge/)!

Il [risultato di questo merge](http://www.internetnews.com/dev-news/article.php/3819116) si concretizzerà nella prossima major release di Rails, la 3.0, che è stata oggetto di un [consistente talk](http://merbist.com/2009/05/08/railsconf-2009/) a RailsConf 2009, e le cui caratteristiche saranno:

**Meno "opinionated"**: non più una singola "Rails Way", bensì multiple "Rails Ways", data la possibilità di scegliere tra differenti ORM (AR, Sequel, DataMapper, CouchRest, …), templating engines (ERb, HAML, Liquid, Markaby, […](http://www.hokstad.com/mini-reviews-of-19-ruby-template-engines.html)) Javascript libraries (Prototype, jQuery, MooTools, Dojo, …) e testing frameworks (Test::Unit, RSpec, Mocha, …).

**Più veloce**: il team di sviluppo di Merb è sempre stato attento alle performance, cercando di evitare la scrittura di software con troppa "magic" (e.g. abuso di method\_missing) e che seguisse la sua filosofia di modularità e circoscrizione ad di un componente ad un singolo dominio applicativo. Rails3 erediterà questi approcci al design garantendo migliori performance. In quest'ottica è avvenuto anche l'inserimento di [Metal](http://weblog.rubyonrails.org/2008/12/17/introducing-rails-metal) in Rails 2.3.

**Una public API**: Sbagliando, s'impara. Se è vero che non è possibile immaginare l'uso che un utente finale fà di un software, allo stesso modo sono molteplici e imprevedibili gli usi che uno sviluppatore può fare di un framework, e tali diventano anche evil se non gli è fornita una [API](http://en.wikipedia.org/wiki/Application_programming_interface) e delle linee guida per la sua estensione. Il lungo dibattito riguardo i Rails Engines ha fatto storia, e non è il caso di ripetere gli stessi errori.

**Più modulare** e **più agnostico**, dirette conseguenze dell'introduzione di una API, e che permettono quindi la realizzazione di applicazioni "componibili", essendo il framework non una singola torre, ma più un set di strumenti a-la [lego technic](http://en.wikipedia.org/wiki/Lego_Technic) (bei ricordi :). Una funzionalità che conferma questo approccio, già disponibile in Rails 2.3, sono i Rails templates: essi offrono una [DSL](http://en.wikipedia.org/wiki/Domain-specific_programming_language) per automatizzare l'inizializzazione di una nuova applicazione, attraverso la scrittura dei requisiti in un file .rb da passare come argomento del parametro -m al comando rails. [Questo blogpost di lifo](http://m.onkey.org/2008/12/4/rails-templates) contiene tutte le informazioni per un quickstart.

**Più evolvibile**: diretta conseguenza della maggiore modularità e di un cambio di vision. In Rails3 non ci saranno più "Vacche sacre", bensì qualsiasi aspetto del framework potrà essere soggetto a cambiamento. Non spaventatevi: a patto che la API rimanga stabile e ci sia un definito processo di deprecation per le API marcate come obsolete, per lo sviluppatore non ci sarà alcun mal di testa. Molti più ce ne sono stati in passato a causa dell'assenza di API, dove ognuno implementava come meglio credeva le feature di cui aveva bisogno.

## Live from the stage

Uno (dei tantissimi) esempi di come realizzare questo grande merge è possibile vederlo direttamente su github, nello specifico [due](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a) [commit](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1) su ActionController. Esso è stato completamente ristrutturato, e la nuova implementazione è stata riposta in una nuova directory, new\_base, nel primo commit introdotta la [Rails2Compatibility](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a#L5R5) e rimossi i [fixture template](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a#L13L5).

Successivamente, nel secondo commit, è avvenuto lo switch dalla vecchia ActionController::Base alla [nuova](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1#L6L2), inserendo anche qualche [hack temporaneo](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1#L2R4) per far sì che i test continuassero a funzionare.

Seguire un merge di questa portata operato da professionisti affermati è un ottimo esercizio, soprattutto per chi si è da poco affacciato all'ingegneria del software, e vuole imparare sul campo le best practices che portano le [big rewrite](http://chadfowler.com/2006/12/27/the-big-rewrite) al successo.

## Il futuro?

Rails3 sarà un notevole passo avanti nella storia di questo framework, che si lascerà dietro le parti più controverse della sua filosofia, e permetterà alla community di farlo evolvere in maniere prima impossibili. È auspicabile per ogni sviluppatore seguirne il suo sviluppo, poichè è anche possibile imparare processi e approcci al project management, oltre che allo sviluppo di software. La gestione del progetto rails con relative milestone è gestita attraverso [lighthouse](http://rails.lighthouseapp.com/), mentre tutto il codice sorgente è conservato su [github](http://github.com/rails/rails). Data la natura di git (e github), chiunque può, in qualsiasi momento, effettuare un fork di rails e modificarlo come più gli piace. È una possibilità che poche altre piattaforme per lo sviluppo di software opensource permettono.

Inoltre, è possibile seguire il Rails Core Team su [twitter](http://twitter.com/rails), mantenersi aggiornati sugli sviluppi ad alto livello seguendo [il blog di Ryan Daigle](http://ryandaigle.com/), seguire le discussioni attorno a Rails3 attraverso il mail-to-web gateway presente su [ruby-forum.com](http://www.ruby-forum.com/forum/3) e, ovviamente, aggiungere therubymine.com ai propri bookmark poichè su queste pagine riparleremo presto di Rails3 :).

A presto!

---

> **Nota:** Questo articolo è stato originariamente pubblicato su [therubymine.com](http://therubymine.com/2009/06/04/rails3-better-faster-stronger/), un blog collettivo italiano su Ruby e Rails che non esiste più. Lo ripubblico qui per preservarlo.
