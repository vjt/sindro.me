---
title: "Da Heathen a Colore: una pipeline per i documenti"
date: 2016-01-15
tags: [ruby, sinatra, nginx, c, open-source, ifad]
description: "Tre anni e quattro colleghi a convertire Word in PDF all'IFAD. Heathen era Sinatra + Dragonfly + un trucco di dedup basato sull'hash dei contenuti. Colore è la riscrittura — directory come database, worker asincroni, un modulo C per nginx, e una v1.0 che ho appena mergiato."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Colore è ancora vivo a [github.com/ifad/colore](https://github.com/ifad/colore) — [Geremia Taglialatela](https://github.com/tagliala) ha preso in mano il progetto dopo che io mi sono spostato su altre cose, e l'ha portato avanti attraverso Ruby 2.7, 3.0, 3.1, 3.2, sidekiq 6, e CI moderna. È a [354 commit](https://github.com/ifad/colore/graphs/contributors) — tre volte i miei. Il [modulo C per nginx](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module) che Joe ha scritto a febbraio 2015 è invariato. Heathen come servizio standalone è stato alla fine assorbito direttamente dentro Colore come libreria; il [repo originale](https://github.com/ifad/heathen) è archiviato ma il codice vive dentro `lib/heathen/` di Colore. Stessa idea, meno componenti.
{{< /retrospective >}}

L'[IFAD](http://www.ifad.org/) è un'agenzia delle Nazioni Unite che gira sui documenti. Accordi di prestito, rapporti di valutazione, note strategiche per Paese, decisioni del Board, brief di progetto — ogni applicazione web che costruiamo prima o poi deve prendere un file Word e restituire un PDF, o prendere una scansione e restituire qualcosa di indicizzabile, o prendere un blob qualsiasi e farne una thumbnail. Tre anni fa abbiamo deciso di smettere di risolvere questo problema un'applicazione alla volta e di metterlo dietro un singolo servizio.

Oggi sto mergiando la [v1.0.0 di Colore](https://github.com/ifad/colore/commit/63d4fe0). È il secondo tentativo di quel servizio, ed è quello che ci teniamo. Questa è la storia di entrambi i tentativi e delle persone che li hanno costruiti — perché quasi nessuna riga del codice qui sotto è mia.

<!--more-->

## Heathen, il primo tentativo

[Heathen](https://github.com/ifad/heathen) parte il [18 dicembre 2012](https://github.com/ifad/heathen/commit/f9081b6) con un `README` di [Peter Brindisi](https://github.com/petebrindisi). Il banner del repo è in ASCII art. Lo slogan è "Convert the heathens." La mission statement è una frase: *"un servizio per convertire praticamente qualunque cosa in PDF."*

Due giorni dopo arriva la prima versione funzionante. Peter abbozza l'architettura, [Lleïr Borràs Metje](https://github.com/lleirborras) collega i backend di conversione, [Joe Blackman](https://github.com/jblackman) entra a estendere l'API, e io arrivo circa un anno dopo a smussare gli angoli vivi. Conteggio finale: [193 commit, quattro autori](https://github.com/ifad/heathen/graphs/contributors), distribuiti in modo quasi paritario. Nessuno di noi è il lead. Il progetto appartiene al codice.

Lo stack è splendidamente 2012:

- [Sinatra](http://www.sinatrarb.com/) per il livello HTTP
- [Dragonfly](https://github.com/markevans/dragonfly) per lo storage content-addressable e i job di processing al volo
- [Rack::Cache](https://github.com/rtomayko/rack-cache) cosi' l'output convertito viene memoizzato gratis
- [Redis](https://redis.io/) per ricordare quale hash dei contenuti mappa a quale job Dragonfly
- LibreOffice in headless su `localhost:8100`, [`wkhtmltopdf`](https://wkhtmltopdf.org/) per HTML, [ImageMagick](https://imagemagick.org/) per le immagini, [tesseract](https://github.com/tesseract-ocr/tesseract) per l'OCR, e un [pdfbeads forkato](https://github.com/ifad/pdfbeads) per cucire le immagini OCRizzate in PDF cercabili

Il contratto di conversione è insolito. Fai `POST /convert` con un file (o una URL) e un'azione. Il server non fa effettivamente il lavoro. Invece, [calcola l'hash SHA-256 dei contenuti](https://github.com/ifad/heathen/blob/master/inquisitor.rb#L42-L44), controlla Redis per vedere se l'ha già visto, e o restituisce la URL Dragonfly cachata o ne salva una nuova e restituisce *quella*. In ogni caso ottieni un documento JSON con due URL:

```json
{
  "original":  "http://heathen/media/W1siZi....jpg",
  "converted": "http://heathen/media/W1siZi....pdf"
}
```

Visitare la URL `converted` è ciò che innesca la conversione vera e propria — Dragonfly deserializza la URL in una descrizione di job, esegue la conversione, e Rack::Cache si tiene il risultato. Le richieste successive vengono servite dalla cache. Stesso contenuto caricato due volte da qualunque parte dell'organizzazione → stessa URL → nessun lavoro duplicato. È un trucco carino. È anche il motivo per cui ogni stranezza del sistema discende dal modello URL-come-stato di Dragonfly.

Il lato infrastruttura è la parte a cui contribuisco davvero. Tutto lo stack — LibreOffice con PyUNO, ImageMagick con le librerie delegate giuste, tesseract con i language pack giusti, il pdfbeads patchato — deve vivere da qualche parte. Lo impacchetto tutto [come RPM sull'OpenSuSE Build Service](https://build.opensuse.org/project/show/home:vjt:ifad), così il deploy in produzione è `zypper ar` e `zypper install`. Heathen gira sotto Unicorn dietro nginx su openSUSE, e funziona.

A fine 2013 faccio il mio unico contributo significativo al codice: cinque giorni tra la vigilia di Natale e il 28 dicembre a riscrivere l'executioner dei sottoprocessi. L'originale usava i backtick. I backtick non fanno streaming dello stdout, non espongono lo stderr, e si rompono quando wkhtmltopdf decide di vomitare un megabyte di warning prima di produrre il PDF. Lo [riscrivo sopra `Process.spawn` con `ProcessBuilder` per jRuby](https://github.com/ifad/heathen/commit/a36a1e0), [passo a `Open3` per stream stdout grandi](https://github.com/ifad/heathen/commit/44ba0b0), [uccido PDFKit](https://github.com/ifad/heathen/commit/7b128d9) in favore di chiamare wkhtmltopdf direttamente, e [gestisco il caso](https://github.com/ifad/heathen/commit/cdf44ca) in cui il lato Java va in tilt su un megabyte di stdout. È il tipo di lavoro che nessuno nota — a meno che tu non lo faccia.

Un anno dopo Joe rilascia [autoheathen](https://github.com/ifad/heathen/blob/master/bin/autoheathen) — una versione SMTP-driven della stessa pipeline. Mandi una email con un Word in allegato a `wikilex@ifad.org`, autoheathen la riceve, converte gli allegati, e inoltra il risultato. L'ufficio Legale vive dentro Outlook. Outlook non parla HTTP. La conversione via email è il modo in cui vai incontro agli utenti dove sono.

## Perché riscriviamo

Per fine 2014 sappiamo cosa non va. Non abbastanza da buttare via il sistema — Heathen è in produzione, funziona, e nessuno ci sta chiedendo di sostituirlo. Ma abbastanza da sapere che non sceglieremmo questo stack di nuovo.

L'idea Dragonfly URL-come-stato è il problema centrale. La URL *è* la descrizione del job, codificata in base64 nel path. Significa:

- **Niente versioning.** Un documento è un hash dei contenuti. Carichi `contratto.docx`, ottieni una URL. Carichi un `contratto.docx` corretto, ottieni una URL *diversa*. Adesso ti serve qualcosa fuori dal sistema che ricordi quale è la corrente. Ogni applicazione che lo consuma si inventa la sua risposta.
- **Conversione sincrona.** La prima GET sulla URL convertita è quando avviene il lavoro. Se LibreOffice ci mette 90 secondi a renderizzare un DOCX complicato, la richiesta HTTP ci mette 90 secondi. Finiamo con manopole di timeout dappertutto.
- **Niente callback.** Non puoi dire a Heathen "convertilo e fammi sapere quando hai finito." Il modello non ha un evento "fatto."
- **Cache invalidata a mano.** Quando pdfbeads riceve un bug fix e vuoi che i PDF OCRizzati esistenti vengano rigenerati, fai `rake heathen:cache:clear` e il mondo riconverte on-demand. Sottile.
- **L'autorizzazione è un problema di qualcun altro.** Chiunque possa indovinare una URL può scaricare un documento. Lo mettiamo davanti agli ACL di nginx e fingiamo.

Nessuno di questi è un bug. Sono il limite di ciò che le primitive scelte possono esprimere. La mossa giusta è un set diverso di primitive.

## Colore

[Joe Blackman](https://github.com/jblackman) inizia la riscrittura il [30 gennaio 2015](https://github.com/ifad/colore/commit/422323f) con un commit intitolato "First cut of storage." Il nuovo progetto è [Colore](https://github.com/ifad/colore) — perché parla diverse lingue: storage, versioning, conversione. Il README sfoggia [una ruota di colori](https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/BYR_color_wheel.svg/480px-BYR_color_wheel.svg.png) come logo.

La decisione fondamentale è in [un commit di refactor quattro giorni dopo](https://github.com/ifad/colore/commit/6414de6): *"Refactored document to quit messing around with metadata, instead querying the directory structure."* Niente database. Il filesystem è il database. I documenti vivono qui:

```
storage/
  └── myapp/
      └── 12345/
          ├── metadata.json
          ├── title
          ├── current → v002
          ├── v001/
          │   ├── foo.docx
          │   ├── foo.pdf
          │   └── _author.txt
          └── v002/
              ├── foo.docx
              ├── foo.jpg
              └── _author.txt
```

`current` è un symlink. Le nuove versioni sono nuove directory. Avanzare atomicamente `current` è un'operazione da una sola syscall. Il rollback è l'inverso. Listare le versioni è `ls`. La struttura *è* lo schema, e `Document.load(base_dir, doc_key)` cammina l'albero per ricostruire lo stato. Joe sistema la [concorrenza basata su `flock`](https://github.com/ifad/colore/commit/f40097d) al dodicesimo giorno, così update simultanei sullo stesso documento non corrono.

L'API HTTP prende una forma verbo-sostantivo che Heathen non aveva mai avuto:

- `PUT  /document/:app/:doc_id/:filename` — crea un nuovo documento
- `POST /document/:app/:doc_id/:filename` — salva una nuova versione
- `POST /document/:app/:doc_id/:version/:filename/:action` — richiedi una conversione
- `GET  /document/:app/:doc_id/:version/:filename` — leggi un file
- `DELETE /document/:app/:doc_id` — distruggi tutto

Le conversioni passano per [Sidekiq](https://sidekiq.org/) e [POSTano una callback quando hanno finito](https://github.com/ifad/colore/commit/a3aec71). Le applicazioni possono finalmente essere event-driven. Heathen, il motore di conversione vero e proprio, viene [vendoriato dentro Colore come libreria](https://github.com/ifad/colore/tree/master/lib/heathen) — stessa cassetta degli attrezzi LibreOffice/wkhtmltopdf/ImageMagick/tesseract, adesso senza il wrapper HTTP. Un servizio invece di due, asincrono di default, callback dove devono essere.

`autoheathen` viene anche lui: Joe lo [porta dal vecchio repo](https://github.com/ifad/colore/commit/0ef1fed) all'ottavo giorno. Wikilex continua a funzionare durante il cutover.

Per l'[11 febbraio](https://github.com/ifad/colore/commit/d9af5a3) la LICENSE è dentro, il [README è scritto](https://github.com/ifad/colore/commit/46249b3), e Colore è open source.

## Il modulo C per nginx

Il pezzo che voglio mostrare perché mi rende felice è il [modulo nginx su misura](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module) che Joe scrive il [19 febbraio 2015](https://github.com/ifad/colore/commit/f6a6465).

Il problema è il fanout. Con una directory documento per `doc_id`, un deployment Colore con milioni di documenti ha milioni di directory sotto un singolo parent. Quasi tutti i filesystem diventano scontenti molto prima. La soluzione è un albero a prefisso hash: prendi l'MD5 di `doc_id`, mozza i primi due caratteri, e usali come directory intermedia. Adesso `myapp/12345/` vive in realtà a `myapp/ab/12345/`, e hai 256 bucket in cima invece di un pozzo senza fondo.

Farlo in Ruby va benissimo — Colore lo gestisce da solo in lettura e scrittura. Ma la *vera* vittoria è servire i documenti direttamente da nginx senza fare il giro per la app Sinatra. L'applicazione vede una richiesta, controlla l'autorizzazione, ed emette un header `X-Accel-Redirect` che punta alla URL di storage. nginx intercetta la risposta, ci mette dentro il file dal disco, e lo streamma. La app Ruby gestisce l'autorizzazione in millisecondi e non tocca mai i byte.

Solo che adesso nginx deve calcolarsi il prefisso MD5 da solo, in C. Quindi Joe scrive un [modulo C per nginx di 99 righe](https://github.com/ifad/colore/blob/master/nginx/ngx_colore_module/ngx_colore_module.c) che espone una sola direttiva:

```nginx
location /document/foobar/(?<doc_id>.+?)/(?<file>.+)$ {
    internal;
    set_colore_subdir $hash $doc_id 2;
    alias             $colore_storage/foobar/$hash/$doc_id/$file;
}
```

`set_colore_subdir $hash $doc_id 2` esegue un MD5 su `$doc_id` e scrive i primi 2 caratteri esadecimali in `$hash`. Tutto qui. È tutto il modulo. La grande maggioranza di quelle 99 righe è boilerplate nginx — module struct, command table, init hook. Il lavoro vero è una chiamata MD5 e una `memcpy`. È la differenza tra "Ruby serve un PDF da 50MB" e "nginx serve un PDF da 50MB e Ruby non si sveglia mai."

La [dipendenza di build](https://github.com/ifad/colore/blob/master/nginx/ngx_colore_module/README.markdown) è l'[Nginx Development Kit](https://github.com/simpl/ngx_devel_kit) — un meta-modulo che dà ai moduli di terze parti primitive sane per dichiarare filtri di variabili. Con NDK in scena, esporre una nuova computazione di variabile alla config di nginx è solo dichiarare una callback e un descrittore di direttiva.

## Il lato Rails

Il contratto applicativo è ora pulito abbastanza che cablarlo a Rails è un piccolo pezzo di colla, non un progetto. [Luca Spiller](https://github.com/lucaspiller) scrive [carrierwave-colore](https://github.com/ifad/carrierwave-colore) a [ottobre 2015](https://github.com/ifad/carrierwave-colore/commit/3416c0c) — un adapter di storage [CarrierWave](https://github.com/carrierwaveuploader/carrierwave) per Colore. Lo aggiungi al Gemfile, configuri una base URI e un nome applicazione, e i tuoi uploader esistenti scrivono attraverso Colore:

```ruby
class DocumentUploader < CarrierWave::Uploader::Base
  storage :colore

  def store_path
    "#{model.class.name}.#{model.id}"
  end
end

# altrove
file = document.attachment.file
file.convert('pdf')          # asincrono; ritorna subito
file.format('pdf').read      # leggi il blob convertito
file.versions                # => {"v001" => ["docx", "pdf"]}
```

`convert` ritorna subito e Colore gestisce il lavoro in background; una URL di callback opzionale [riceve POST](https://github.com/ifad/carrierwave-colore) quando la conversione atterra. La app Rails resta forma-Rails. Colore è invisibile dal punto di vista dell'applicazione, fino a che non lo è.

Sotto, [colore-client](https://github.com/ifad/colore-client) — anche lui di Joe — gestisce l'HTTP. È un thin wrapper REST che conosce gli status code di Colore e trasforma gli errori in eccezioni Ruby vere. L'adapter CarrierWave parla solo colore-client.

## v1.0.0

Il [tag v1.0.0](https://github.com/ifad/colore/commit/63d4fe0) entra stamattina, 15 gennaio 2016 — un anno meno due settimane dal primo commit di Joe. Il messaggio di merge è senza cerimonie: *"libreoffice text conversion and specs fixes."* Poi il tag. Il git log è onesto su chi l'ha costruito: Joe e Luca in cima, contributi da [Antonio Delfin Martinez](https://github.com/antoniodelfin) e [Danilo Grieco](https://github.com/danilo-g), io sull'infrastruttura e nelle pattuglie di bug-fix.

Cosa abbiamo alla v1.0:

- Un servizio documenti che conosce le versioni, esegue conversioni in modo asincrono, posta callback, e serve i file attraverso nginx senza mai toccare i byte in Ruby.
- Un modulo C per nginx su misura che lascia nginx servire i byte direttamente, con la app Ruby fuori dal percorso caldo.
- Un adapter CarrierWave che rende l'adozione una modifica da cinque righe.
- Un punto d'ingresso email-driven così gli utenti non-HTTP (l'ufficio Legale, soprattutto) possono giocare anche loro.
- Una storia di migrazione da Heathen — il [legacy converter](https://github.com/ifad/colore/blob/master/lib/legacy_converter.rb) legge il vecchio storage Dragonfly e ripubblica i documenti dentro l'albero Colore, indicizzati sull'hash dei contenuti originale.

Quello che non abbiamo, e non avremo mai, è una storia d'origine drammatica. La pipeline non è un atto di visione singola. Sono tre anni di quattro persone che si passano il turno sullo stesso problema, buttando via le parti che non funzionavano e tenendo quelle che sì. Gli eretici vengono convertiti comunque.

## Crediti

- **Heathen**: [Peter Brindisi](https://github.com/petebrindisi) (design e architettura iniziali, 54 commit), [Lleïr Borràs Metje](https://github.com/lleirborras) (49), io (53), [Joe Blackman](https://github.com/jblackman) (38). Sorgenti su [github.com/ifad/heathen](https://github.com/ifad/heathen).
- **Colore**: Joe Blackman (architetto e autore principale), con tutti gli altri al seguito. Sorgenti su [github.com/ifad/colore](https://github.com/ifad/colore). Modulo C per nginx in [`nginx/ngx_colore_module/`](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module).
- **carrierwave-colore**: [Luca Spiller](https://github.com/lucaspiller). Sorgenti su [github.com/ifad/carrierwave-colore](https://github.com/ifad/carrierwave-colore).
- **colore-client**: Joe Blackman. Sorgenti su [github.com/ifad/colore-client](https://github.com/ifad/colore-client).
- **autoheathen**: Joe Blackman, originalmente in Heathen, portato a Colore.
- **RPM OpenSuSE**: io, su [build.opensuse.org/project/show/home:vjt:ifad](https://build.opensuse.org/project/show/home:vjt:ifad).

`gem install colore-client` e puoi parlare con un servizio Colore. `bundle install carrierwave-colore` e i tuoi upload Rails finiscono versionati, convertiti, e serviti da nginx. Le chiavi del regno dei documenti sono MIT-licensed.
