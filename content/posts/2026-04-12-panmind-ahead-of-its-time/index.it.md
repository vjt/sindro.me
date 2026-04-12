---
title: "Lo Stack Panmind: Architettura da 2020 Costruita nel 2010"
date: 2026-04-12
tags: [panmind, javascript, erlang, ruby, rails, architecture, open-source]
description: "Come una piccola startup italiana ha costruito un framework SPA, una pipeline di analytics event-driven e la condivisione di sessioni tra linguaggi diversi — anni prima che diventassero mainstream."
image: cover.jpg
featuredImage: cover.jpg
---

Nel 2009, un piccolo team a Roma iniziava a costruire [Panmind](https://github.com/Panmind), una piattaforma collaborativa per condividere e organizzare la conoscenza. L'azienda era [Mind2Mind S.r.L.](http://mind2mind.is/), fondata da Emanuele Caronia.

Panmind di per sé non è sopravvissuto. Ma lo stack che abbiamo costruito ha fatto qualcosa di interessante: ha anticipato pattern architetturali che non sarebbero diventati mainstream per cinque o dieci anni. Stavamo costruendo single-page application prima che esistesse il termine, streaming analytics prima di Segment, e condividendo sessioni tra linguaggi diversi prima dei JWT.

Ho [presentato alcuni dei nostri spin-off open source](/it/posts/2010-08-05-panmind-at-ruby-social-club/) al Ruby Social Club di Milano nel 2010, ma quel post toccava solo la superficie — era una carrellata veloce di plugin Rails. Questa è la storia più approfondita: tre tecnologie, tre problemi risolti troppo presto, e come le stesse idee si sono ripresentate in ogni major framework che è venuto dopo.

## Atto 1: jquery-ajax-nav — SPA Prima delle SPA

![Routing basato su hash in un browser vintage — polling dei cambiamenti, iframe nascosti per IE, il fragment URL come unica parte programmabile della barra degli indirizzi](/posts/2026-04-12-panmind-ahead-of-its-time/act1-ajax-nav.jpg)

Panmind doveva essere veloce. Cliccare un link non doveva ricaricare l'intera pagina — doveva sostituire solo l'area dei contenuti, istantaneamente. Nel 2023 avresti usato React, o Turbo, o HTMX. Nel 2009, nessuno di questi esisteva. Non c'era la History API. Non c'era `pushState`. Il fragment dell'URL — la parte dopo `#` — era l'unica porzione dell'URL che potevi modificare senza innescare un reload della pagina. Quindi abbiamo usato quello.

[jquery-ajax-nav](https://github.com/vjt/jquery-ajax-nav) era un framework jQuery da 14 plugin che trasformava una tradizionale app Rails server-rendered in qualcosa che si comportava come una single-page application. 206 commit, estratto dalla codebase di produzione di Panmind, testato su tutto, da IE6 a Chrome.

### Il problema dell'encoding degli hash

I fragment degli URL non possono contenere query string. I caratteri `?` e `&` hanno significati speciali negli URL, e i browser li gestiscono in modo inconsistente dentro i fragment. Quindi abbiamo inventato un encoding custom:

```javascript
// jquery.location.js — encoding custom per gli anchor
//
// Dato che la sintassi tradizionale delle query string (?foo=bar&baz=42)
// non può essere usata negli anchor, questo plugin implementa una sintassi
// custom, dove ':' mappa a '?' e ';' mappa a '&'.
//
// Esempio: /search?q=hello&page=2 → #search:q=hello;page=2

this.encodeAnchor = function (href) {
  if (!/^[\/#]/.test (href))
    href = '/' + (href || '');

  return decodeURIComponent (href)
           .replace (/[?&\/]+$/, '') // Trim the tail
           .replace (/^\//, '#')     // Replace the leading / with '#'
           .replace (/\?/,  ':')     // Replace '?' with ':'
           .replace (/\&/g, ';')     // Replace '&' with ';'
};
```

Un paio di regex, e all'improvviso potevi memorizzare path completi con parametri dentro un fragment URL. Oggi React Router e Vue Router hanno una "hash mode" che fa essenzialmente la stessa cosa — esiste per ambienti dove non puoi configurare il routing lato server, che nel 2009 era *qualsiasi* ambiente.

### Rilevare la navigazione senza eventi

Ecco il punto sul 2009: i browser non emettevano eventi quando l'hash cambiava. L'evento `hashchange` era ancora in fase di rollout (IE8 ce l'aveva, Firefox e Chrome non ancora, Safari sicuramente no). La History API con `popstate` non sarebbe arrivata fino al 2011-2012. Quindi come fai a rilevare quando l'utente clicca il tasto indietro?

Fai polling. Ogni 100 millisecondi.

```javascript
// jquery.history.js — il cuore del routing basato su hash nel 2009

init: function (callback) {
  _callback = callback;
  _current  = '#';

  // IE < 8 ha bisogno di un iframe nascosto per le history entry
  if ($.browser.msie && ($.browser.version < 8 || document.documentMode < 8))
    _iframe.init ();

  setInterval (function () {
    var hash;

    if (_iframe.inited)
      hash = _iframe.get ();
    else
      hash = location.hash || '#';

    hash = normalize (hash);

    if (!changed (hash))
      return;

    $.history.save (hash, false);
    invoke ();
  }, 100);
},
```

Un `setInterval` che gira dieci volte al secondo, controllando se `location.hash` è cambiato. Brutale? Sì. L'unico modo? Anche. E funzionava perfettamente — la callback viene invocata, il contenuto si carica via AJAX, e l'utente non si accorge di nulla.

Ma la vera follia era IE. Internet Explorer 6 e 7 avevano un bug *affascinante*: cambiare `location.hash` via JavaScript non creava una nuova history entry. Il tasto indietro semplicemente non funzionava. Il workaround era creare un iframe nascosto e scrivere l'hash nel body del suo documento — perché scrivere in un iframe *creava* history entry:

```javascript
// L'hack dell'iframe per IE — scrivere in un iframe nascosto per creare
// history entry, perché IE non lo faceva per i cambiamenti di hash

var _iframe = {
  // ...
  write: function (hash) {
    var doc = this.element.contentWindow.document;
    doc.open();
    doc.write('<html><body>' + hash + '</body></html>');
    doc.close();
  }
};
```

Hai letto bene. Scrivevamo `<html><body>#search:q=hello</body></html>` in un iframe nascosto per far funzionare il tasto indietro su IE. Questo è il genere di cose che ti fa apprezzare la History API.

### Eventi del ciclo di vita

![Il ciclo di vita della pagina come palcoscenico teatrale — vecchi contenuti smontati a sinistra, nuovi contenuti assemblati a destra, un direttore d'orchestra che guida la transizione](/posts/2026-04-12-panmind-ahead-of-its-time/lifecycle-events.jpg)

Il framework di navigazione aveva un ciclo di vita degli eventi completo. Quando il contenuto stava per essere sostituito, un evento `nav:unloading` scattava — così potevi disattivare timer, rimuovere event handler, fare pulizia. Quando arrivava nuovo contenuto, `nav:loaded` scattava — così potevi inizializzare widget, agganciare eventi, preparare la nuova pagina.

```javascript
// jquery.ajax-nav.js — registrazione degli eventi del ciclo di vita

// Eseguito UNA SOLA VOLTA al primo caricamento
$.fn.ajaxInit = function (fn) {
  return $(document).one ('nav:loaded', fn);
};

// Eseguito OGNI VOLTA che il contenuto si carica
$.fn.ajaxReady = function (fn) {
  return $(document).bind ('nav:loaded', fn);
};

// Eseguito OGNI VOLTA che il contenuto sta per essere scaricato
$.fn.ajaxUnload = function (fn) {
  return $(document).bind ('nav:unloading', fn);
};
```

Se ti sembra familiare, dovrebbe. Turbolinks (2012) introdusse `turbolinks:load`. Turbo (2021) ha `turbo:before-render` e `turbo:load`. Sono lo stesso concetto — la stessa *esigenza* — formalizzato tre e dodici anni dopo rispettivamente.

### Hijacking di link e form

Qualsiasi link con classe `nav` veniva intercettato al click. Invece di un page load completo, il framework recuperava il contenuto via AJAX e lo inseriva nel container:

```javascript
// Intercettare i click sui link di navigazione
$.fn.navLink = function (options) {
  options = __validateOptions (options, this);

  var listener = function (event) {
    var link = $(this);
    var args = $.clone (options);

    if (!args.href)
      args.href = link.attr ('href');

    $.navLoadContent (link, args);
    return false;
  };

  if (options.live)
    $(this).live ('click', listener);
  else
    $(this).click (listener);

  return this;
};
```

I form ricevevano lo stesso trattamento con `.navForm()` — i form GET venivano serializzati in query string, i POST inviavano i dati nel body. E c'era una convenzione astuta — qualcuno direbbe abusiva — per i redirect AJAX. Non potevamo usare nessun codice 3xx perché IE seguiva ciecamente i redirect sulle richieste XHR, ingoiando la risposta prima che il nostro JavaScript potesse intercettarla. Quindi abbiamo dirottato HTTP 202 (Accepted): il server rispondeva 202 con il path del redirect nel body, e il nostro codice client lo seguiva manualmente:

```javascript
// HTTP 202 = redirect AJAX: il body della risposta contiene il path da seguire
if (xhr.status == 202) {
  options.href   = response;
  options.method = 'get';
  options.params = null;
  $.navLoadContent (loader, options);
  return;
}
```

L'helper Rails corrispondente era semplicissimo:

```ruby
def ajax_redirect_to(path)
  if request.xhr?
    render :text => path, :status => 202
  else
    redirect_to path
  end
end
```

La convenzione di redirect di Turbo (303 See Other) è l'equivalente moderno. HTMX ha `HX-Redirect`. Stesso problema, stessa soluzione, diverso codice HTTP.

### Il cookie di ottimizzazione

Uno dei miei trick preferiti nella codebase. Quando il framework hijackava un URL profondo come `/projects/1/writeboards/42` in `/projects/1#writeboards/42`, impostava un cookie di 1 secondo chiamato `nha`:

```javascript
// Imposta un cookie per dire al backend di renderizzare uno spinner
// ("nha" sta per NavHijAck)
$.navHijackRedirect = function (base, anchor) {
  var expire = new Date((+new Date) + 1000).toGMTString ();
  document.cookie = 'nha=1; path="' + base + '"; expires=' + expire;
  $.location.set (base + $.location.encodeAnchor (anchor));
};
```

Il backend Rails controllava questo cookie e, se presente, renderizzava solo uno spinner di caricamento invece della pagina completa — perché il JavaScript avrebbe immediatamente lanciato una richiesta AJAX per il contenuto reale. Un'ottimizzazione artigianale che risparmiava un intero render lato server ad ogni navigazione hijackata. Oggi i framework gestiscono questo automaticamente con skeleton screen e streaming HTML.

### Comportamenti dichiarativi via attributi HTML

![L'HTML come burattinaio — tag di attributi su fili che controllano elementi UI Web 2.0 sottostanti](/posts/2026-04-12-panmind-ahead-of-its-time/declarative-html.jpg)

Oltre al framework di navigazione, abbiamo costruito un'intera [libreria di behaviour](https://github.com/vjt/jquery-ajax-nav/blob/master/jquery.behaviours.js) che collegava le interazioni UI in modo dichiarativo tramite attributi HTML — nello specifico, abusando dell'attributo `rel`. Un toggler, un tabber, un cycler, un deleter, un rollover — ciascuno era una classe CSS che attivava un handler jQuery `.live()`, e l'attributo `rel` puntava all'elemento target:

```html
<!-- Toggler: click per mostrare/nascondere #milestone_42 -->
<a class="toggler slider" rel="#milestone_42">Edit</a>

<!-- Tabber: ogni tab punta al suo pannello di contenuto -->
<ul class="tabber fader" rel=".newElement">
  <li class="active"><a href="#" rel="#newPost">New Post</a></li>
  <li><a href="#" rel="#newLink">New Link</a></li>
</ul>

<!-- Cycler: slide auto-rotanti, intervallo del timer in rev(!) -->
<div class="cycler timer" rel="#slides" rev="5000"></div>
```

Avevamo persino `hierarchyFind()`, una funzione custom di attraversamento del DOM che parsava un mini-linguaggio dentro `rel`. La sintassi `>#todo .uploader` significava "trova un genitore il cui ID inizia con 'todo', poi cerca al suo interno un elemento con classe 'uploader'" — essenzialmente `element.closest('[id^="todo"]').querySelector('.uploader')`, solo che `closest()` non sarebbe esistito nei browser fino al 2015-2016.

Il pattern — dichiarare comportamenti e target negli attributi HTML invece di scrivere JavaScript — è esattamente quello che fa HTMX oggi con `hx-target`, `hx-swap` e `hx-trigger`. È quello che fa Stimulus con `data-controller` e `data-target`. È quello che fa Alpine.js con `@click` e `x-show`. Noi scrivevamo `rel="#milestone_42"` nel 2009; oggi scriveresti `hx-target="#milestone_42"`. La semantica si è spostata da `rel` agli attributi `data-*` (che HTML5 ha formalizzato esattamente per questo scopo), ma l'idea — l'HTML come fonte di verità per il comportamento della UI — è la stessa.

### I paralleli

| jquery-ajax-nav (2009) | Cosa è venuto dopo |
|---|---|
| Hash polling ogni 100ms | Evento `hashchange` (IE8+), poi `popstate` + History API (2011) |
| Encoding `#/path:query=param` | React Router hash mode, Vue Router hash mode |
| `nav:unloading` / `nav:loaded` | Turbolinks `turbolinks:load` (2012), Turbo `turbo:before-render` (2021) |
| `.navLink()` hijacking dei click | Turbo Drive auto-hijacking di tutti i tag `<a>` |
| `.navForm()` hijacking dei submit | HTMX `hx-post` (2020), intercettazione `<form>` di Turbo |
| HTTP 202 body = path di redirect | Convenzione redirect 303 di Turbo |
| Sostituzione DOM con `.html()` | Virtual DOM diffing (React 2013), morphdom (Turbo 2021) |
| Progressive enhancement — funziona senza JS | La maggior parte delle SPA moderne richiede JS. Solo Turbo mantiene questo. |

L'ultima riga è quella che conta. jquery-ajax-nav era costruito sopra HTML puro. Ogni link funzionava senza JavaScript — semplicemente ottenevi reload completi invece di AJAX. Il framework era un *enhancement*, non un requisito. La maggior parte delle SPA moderne non può dire altrettanto. Turbo Drive, che ha raggiunto la maturità solo nel 2021, è il successore spirituale più vicino — e segue esattamente la stessa filosofia.

## Atto 2: usage_tracker — Analytics Event-Driven Prima di Segment

![Una pipeline dati steampunk — server rack Ruby con gemme luminose, una turbina EventMachine che cattura pacchetti UDP, e pile di documenti CouchDB ordinati da braccia robotiche](/posts/2026-04-12-panmind-ahead-of-its-time/act2-usage-tracker.jpg)

Con la navigazione AJAX in piedi, le analytics tradizionali non bastavano più. I log del server mostravano un page load iniziale seguito da un flusso di richieste XHR, senza modo di ricostruire il percorso di navigazione effettivo dell'utente. Google Analytics *poteva* tracciare le navigazioni AJAX se chiamavi manualmente `_trackPageview()` dopo ogni swap di contenuto — e lo facevamo, tramite il nostro plugin [bigbro](https://github.com/vjt/bigbro). Ma il modello a pageview di GA non poteva darci quello che ci serviva davvero: durate delle richieste, XHR vs page load completi, pattern di traffico per area, comportamento per utente. Ci serviva la nostra pipeline di analytics.

Così abbiamo costruito [usage_tracker](https://github.com/vjt/usage_tracker): un sistema di analytics a tre componenti che catturava ogni richiesta, la trasportava in modo asincrono, la memorizzava in un database documentale e calcolava aggregazioni via map-reduce. Nel 2010.

### Il middleware Rack

Il primo componente era un middleware Rack che wrappava ogni richiesta Rails, ne misurava la durata e ne estraeva i metadati:

```ruby
# usage_tracker/middleware.rb — strumentazione delle richieste

def call(env)
  req_start = Time.now.to_f
  response  = @app.call env
  req_end   = Time.now.to_f

  data = {
    :user_id  => env['rack.session'][:user_id],
    :duration => ((req_end - req_start) * 1000).to_i,
    :backend  => @@backend,
    :xhr      => env['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest',
    :context  => env[Context.key],
    :env      => {},
    :status   => response[0]
  }

  @@headers.each {|key| data[:env][key.downcase] = env[key] unless env[key].blank?}

  self.class.track(data.to_json)

  return response
end
```

Quel flag `:xhr` è il collegamento cruciale con l'Atto 1 — ci diceva se una richiesta veniva da un page load completo o dallo swap di contenuto AJAX di jquery-ajax-nav. Il sistema di analytics era *progettato* per capire il framework di navigazione.

I dati venivano spediti via UDP, fire-and-forget:

```ruby
def track(data)
  Timeout.timeout(1) do
    UDPSocket.open do |sock|
      sock.connect(@@host, @@port.to_i)
      sock.write_nonblock(data << "\n")
    end
  end
rescue Timeout::Error, Errno::EWOULDBLOCK, Errno::EAGAIN, Errno::EINTR
  UsageTracker.log "Cannot track data: #{$!.message}"
end
```

Non-blocking, timeout di 1 secondo, errori loggati silenziosamente. Il `write_nonblock` di per sé non blocca, ma `UDPSocket.open` e `connect` *potrebbero* — risoluzione DNS, allocazione socket, buffer del kernel. Il `Timeout.timeout(1)` avvolge l'intera operazione come rete di sicurezza: se qualcosa nella macchina dei socket a livello OS si blocca, usciamo dopo un secondo invece di bloccare la richiesta Rails. Codice difensivo. La pipeline di analytics non rallentava *mai* una richiesta utente. Meglio perdere un data point che aggiungere latenza. È esattamente la filosofia dietro [StatsD](https://github.com/statsd/statsd), che Etsy avrebbe rilasciato in open source un anno dopo nel 2011, e che è diventato la base della telemetria applicativa moderna.

### Il reactor EventMachine

In ricezione, un daemon [EventMachine](https://github.com/eventmachine/eventmachine) ascoltava su un socket UDP, parsava il JSON in arrivo, lo validava e lo memorizzava in CouchDB:

```ruby
# usage_tracker/reactor.rb — raccolta dati event-driven

module UsageTracker
  module Reactor
    def receive_data(data)
      doc = parse(data)
      if doc && check(doc)
        store(doc)
      end
    end

    private
      def store(doc)
        tries = 0
        begin
          doc['_id'] = make_id
          UsageTracker.database.save_doc(doc)
        rescue RestClient::Conflict => e
          if (tries += 1) < 10
            retry
          end
        end
      end

      # Timestamp come _id: ordinamento cronologico automatico
      # Cifra casuale: evita conflitti tra server multipli
      def make_id
        Time.now.to_f.to_s.ljust(16, '0') + rand(10).to_s
      end
  end

  EventMachine.run do
    host, port = UsageTracker.settings.host, UsageTracker.settings.port
    EventMachine.open_datagram_socket host, port, Reactor
    log "Listening on #{host}:#{port} UDP"
  end
end
```

I document ID basati su timestamp erano furbi — CouchDB ordina per `_id` di default, quindi i documenti erano automaticamente in ordine cronologico. La cifra casuale alla fine gestiva il caso limite di server multipli che generavano eventi nello stesso millisecondo.

### Le view map-reduce di CouchDB

![Un laboratorio artigiano — documenti sparsi su un tavolo, lenti d'ingrandimento su bracci articolati che estraggono pattern, pile ordinate di risultati](/posts/2026-04-12-panmind-ahead-of-its-time/map-reduce.jpg)

Le query di analytics erano definite come view map-reduce CouchDB in un file YAML — con templating ERB per evitare duplicazioni nel JavaScript:

```yaml
# config/views.yml — analytics calcolate via map-reduce
<%
  _AREAS_RE = '\/(' << %w( inbox res projects users account publish search ).join('|') << ')'

  _GET_AREA = %(
    var match = doc.env.path_info.match (/#{_AREAS_RE}/);
    var area  = match ? match[1] : 'other';
  ).gsub(/\s+/x, ' ').strip
%>

average_duration_of_path:
  map: |
    function (doc) {
      if (doc.duration)
        emit (doc.env.path_info, doc.duration);
    }
  reduce: |
    function (keys, values){
      return Math.round (sum (values) / values.length);
    }

area_count:
  map: |
    function (doc) {
      if (doc.env) {
        <%= _GET_AREA %>
        emit (area, 1);
      }
    }
  reduce: |
    function (keys, values, rereduce) {
      return sum (values);
    }
```

JavaScript dentro ERB dentro YAML. Tre linguaggi in un file. È il genere di cose che ti fa storcere il naso e rispettare allo stesso tempo — brutto, pragmatico, e ha permesso di definire 13 view di analytics senza una singola riga di logica di estrazione delle aree duplicata.

### L'architettura

```
Browser → Rails → Rack Middleware → UDP → EventMachine Reactor → CouchDB → Map-Reduce
```

Ti suona familiare? È essenzialmente:

- **Rack middleware che estrae telemetria** → auto-instrumentation di OpenTelemetry
- **UDP fire-and-forget** → protocollo StatsD (Etsy, 2011)
- **Reactor EventMachine** → consumer Kafka, Fluentd, Vector
- **Map-reduce CouchDB** → aggregazioni Elasticsearch, materialized view ClickHouse
- **L'intera pipeline** → architettura [Connections](https://segment.com/) di Segment: instrument → transport → store → query

E il flag XHR — quel singolo booleano per richiesta — è quello che Google Analytics 4 chiama "single page application mode." L'abbiamo costruito perché dovevamo. Avevamo una SPA (Atto 1), e le analytics dovevano capirla. Oggi lo chiamiamo "Real User Monitoring" e paghiamo Datadog o New Relic per averlo.

## Atto 3: erlang-ruby-marshal — Sessioni Cross-Language Prima dei JWT

![Due Stele di Rosetta — Ruby incandescente in rosso, Erlang luminoso in blu — con un fiume di dati binari che scorre tra loro e un cookie HTTP spezzato sopra](/posts/2026-04-12-panmind-ahead-of-its-time/act3-erlang-marshal.jpg)

Panmind aveva un sistema di chat web. Era scritto in Erlang, costruito su [misultin](https://github.com/vjt/misultin) — un server HTTP Erlang leggero. I WebSocket non sarebbero stati standardizzati fino all'RFC 6455 di dicembre 2011, e il supporto nei browser sarebbe rimasto frammentario fino al 2013. Quindi il trasporto era XHR long-polling puro: il browser apriva una richiesta HTTP, il server Erlang la teneva aperta fino all'arrivo di un messaggio o al timeout della connessione, poi il browser si riconnetteva immediatamente. Nessun framework Comet, nessun Socket.IO, nessun livello di astrazione. Solo una richiesta che resta appesa per 30 secondi in attesa di dati.

Ma il server di chat aveva un problema: doveva sapere chi era loggato. L'applicazione Rails gestiva l'autenticazione e memorizzava le sessioni nei cookie. Le sessioni Rails sono serializzate usando il formato [Marshal](https://ruby-doc.org/core/Marshal.html) di Ruby — un protocollo binario che solo Ruby sa leggere. Non c'era un session store basato su JSON, niente JWT, niente token di autenticazione condivisi. Se volevi che un altro linguaggio leggesse una sessione Rails, dovevi insegnare a quel linguaggio a parsare la serializzazione binaria di Ruby.

Così abbiamo forkato [erlang-ruby-marshal](https://github.com/vjt/erlang-ruby-marshal) — scritto originariamente da tema per Ruby 1.8 — e lo abbiamo esteso per la compatibilità con Ruby 1.9. Ruby 1.9 aveva cambiato il modo in cui le stringhe venivano serializzate, aggiungendo metadati di encoding tramite variabili d'istanza. Il nostro fork gestiva quello.

### Insegnare a Erlang a parlare Ruby

Il cuore del parser è un bellissimo esempio del pattern matching binario di Erlang. Ogni byte nello stream Marshal identifica un tipo Ruby, e il decoder fa il dispatch di conseguenza:

```erlang
%% marshal.erl — decodifica della serializzazione binaria di Ruby in Erlang

decode_element(?TYPE_NIL,    <<D/binary>>) -> {nil, D};
decode_element(?TYPE_TRUE,   <<D/binary>>) -> {true, D};
decode_element(?TYPE_FALSE,  <<D/binary>>) -> {false, D};
decode_element(?TYPE_FIXNUM, <<S:8, D/binary>>) -> decode_fixnum(S, D);
decode_element(?TYPE_STRING, <<S:8, D/binary>>) -> decode_string(S, D);
decode_element(?TYPE_SYMBOL, <<S:8, D/binary>>) -> decode_symbol(S, D);
decode_element(?TYPE_IVAR,   <<T:8, D/binary>>) -> decode_element_with_ivars(T, D);
```

Ogni clausola matcha sul byte del tipo ed estrae i dati binari rimanenti. Il pattern matching di Erlang sui binari rende questo quasi leggibile come una specifica di protocollo — puoi vedere la struttura del formato Marshal direttamente nel codice.

L'estrazione vera e propria della sessione era gestita da `rcookie.erl`, che splittava il cookie Rails, verificava la firma HMAC-SHA e decodificava il payload:

```erlang
%% rcookie.erl — estrarre una sessione Rails da un cookie firmato

parse(Cookie) ->
    [Data, Digest] = string:tokens(decode(Cookie), "--"),
    case verify(Data, Digest) of
        false -> {error, verify_failed};
        true  -> {ok, marshal:decode(base64:decode(Data))}
    end.
```

Split al `--`, verifica del digest, base64-decode, unmarshal. Quattro righe, e ora il server di chat Erlang sa chi sei.

### Il problema che questo risolveva

Questo è il problema dell'autenticazione nei microservizi. Il Servizio A (Rails) gestisce il login. Il Servizio B (chat Erlang) ha bisogno di conoscere l'identità dell'utente. Nel 2009, gli approcci standard non esistevano ancora:

- **JWT** (draft 2010, RFC 7519 nel 2015): token language-agnostic, self-contained, firmati. Qualsiasi linguaggio può verificarli e leggerli. La soluzione *progettata* esattamente per questo problema.
- **Session store condivisi**: Redis o Memcached con serializzazione JSON. Richiede che entrambi i servizi si connettano allo stesso store.
- **OAuth2/OIDC** (2012): autenticazione basata su token con endpoint standard.

Nessuno di questi era disponibile. L'abbiamo risolto andando *più in basso* — insegnando a Erlang a parsare il protocollo binario di Ruby. È la soluzione più diretta possibile: Ruby scrive byte, Erlang legge byte, fatto. Nessun middleware, nessuna infrastruttura condivisa, nessuno standard a cui conformarsi. Solo due linguaggi che si mettono d'accordo su un wire format.

E il trasporto stesso — XHR long-polling — è quello che i WebSocket hanno sostituito, e che i Server-Sent Events (SSE) hanno formalizzato. Oggi apriresti un WebSocket con un JWT nell'header dell'handshake. Nel 2009, tenevi aperta una connessione HTTP e parsavi un cookie Ruby in Erlang.

## Essere in Anticipo Non Vuol Dire Sbagliare

Nel 2009-2011, Panmind stava facendo girare:

- Un **framework single-page app** con eventi del ciclo di vita, progressive enhancement e hijacking dei form — un pattern che Turbolinks, React, e infine Turbo e HTMX avrebbero ciascuno reinventato
- Una **pipeline di analytics asincrona event-driven** su UDP con aggregazioni map-reduce — l'architettura che StatsD, Segment e OpenTelemetry avrebbero standardizzato
- Un **server di chat Erlang** che condivideva sessioni con Rails tramite parsing di protocollo binario — il problema di autenticazione cross-service per cui i JWT sono stati progettati

Stesse idee. Era diversa. Costruite con jQuery ed EventMachine e pattern matching Erlang invece che con React e Kafka e OAuth2. Costruite da un piccolo team a Roma che cercava di rendere un prodotto veloce, capire i suoi utenti e supportare funzionalità real-time — non di essere avanti rispetto a qualcosa.

È questo il punto dell'essere in anticipo: non sai di esserlo. Stai solo risolvendo problemi con gli strumenti che hai. Il loop di hash-polling, l'UDP fire-and-forget, il parser Marshal in Erlang — nessuno di questi sembrava *visionario* al momento. Sembravano la cosa ovvia da fare. È solo dopo, quando l'industria converge sugli stessi pattern con standard appropriati e team dedicati e documentazione migliore, che realizzi che le idee erano giuste. Avevano solo bisogno che l'ecosistema le raggiungesse.

E quando l'ha fatto, Panmind non c'era più.

Niente di tutto questo è stato un lavoro solitario. Fabrizio Regini, Paolo Zaccagnini e Christian Wörner scrivevano codice al mio fianco. Edoardo Batini teneva in piedi i server. Emanuele Bertolini, Ferdinando de Meo e Chiara Santoro hanno disegnato l'interfaccia che rendeva la navigazione AJAX degna di essere costruita. Simona Forti creava i contenuti per cui gli utenti venivano. Francesca Antinori capiva cosa costruire. E Emanuele Caronia ha avuto la visione di mettere tutto insieme. Lo stack è stato un lavoro di squadra, anche se i repo mostrano solo hash di commit.

Grazie per aver letto!

**I repo:** [jquery-ajax-nav](https://github.com/vjt/jquery-ajax-nav) | [usage_tracker](https://github.com/vjt/usage_tracker) | [erlang-ruby-marshal](https://github.com/vjt/erlang-ruby-marshal) | [misultin](https://github.com/vjt/misultin) | [Tutti i repo Panmind](https://github.com/Panmind)
