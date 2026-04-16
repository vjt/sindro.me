---
title: "Hermes: help contestuale in 48 ore (Rails Rumble 2013)"
date: 2013-10-20
tags: [rails, ruby, open-source, hackathon, ifad]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Lo spazio dell'"help contestuale" è esploso in una vera categoria di prodotto — Intercom, Pendo, Appcues e altri oggi fanno questo commercialmente su scala. Il fork dell'IFAD ha continuato a vivere per anni dentro l'agenzia. La Rails Rumble stessa ha smesso di esistere dopo il 2015, e l'era degli hackathon competitivi da 48 ore ha lasciato il posto agli AI hackathon e agli startup weekend. Il [repo](https://github.com/vjt/r13-hermes) è archiviato ma ancora online.
{{< /retrospective >}}

La [Rails Rumble](http://railsrumble.com/) è — era — un hackathon di 48 ore dove team di massimo quattro persone costruiscono un'app web completa da zero usando Ruby. Niente lavoro preparatorio, niente codice pre-scritto. Solo caffeina, git e una scadenza.

Quest'anno il nostro team — [@amedeo](https://github.com/amedeo), [@liquid1982](https://github.com/liquid1982), [@maisongb](https://github.com/maisongb) e il sottoscritto — ha costruito **Hermes: the epic messenger service**, entry #385.

(La mia [precedente partecipazione alla Rumble](/it/posts/2012-10-14-guess-the-friend-rails-rumble-2012/) era stata *Guess The Friend* nel 2012, con un team diverso.)

<!--more-->

## Cosa fa Hermes

L'idea era semplice ma genuinamente utile: dare ai proprietari di siti web un modo per integrare dell'**help contestuale** nelle loro applicazioni. Tooltip, banner, tutorial — contenuti che appaiono sulla pagina giusta al momento giusto, senza dover hard-codare nulla nell'app host.

L'integrazione era un singolo tag `<script>`. Quel file JS apriva un canale verso il backend di Hermes, che cercava l'URL corrente e restituiva il payload di help per quella pagina. I proprietari del sito gestivano tutto da una dashboard — nessun deploy necessario per aggiornare un tooltip o aggiungere uno step di walkthrough.

## 48 ore al 48rails

Abbiamo costruito il tutto al [48rails](https://web.archive.org/web/2013*/48rails.com), uno spazio di coworking in Italia che era praticamente la nostra base per questo tipo di follie. Due giorni di coding intenso, scelte alimentari discutibili e zero sonno. Il solito.

L'app era un classico stack Rails — niente di esotico. Ma il pezzo di cui vado più fiero è l'**element inspector** che ho scritto per la modalità authoring. Sai come nei DevTools del browser passi il mouse sugli elementi e si illuminano? L'ho costruito da zero, in un hackathon, privato del sonno, a birra. Quattro `<div>` overlay rossi (N/S/E/W) che si riposizionano dinamicamente attorno a qualsiasi elemento sotto il cursore usando `getBoundingClientRect()` con compensazione dello scroll. Muovi il mouse, la cornice rossa segue. Click, e risale il DOM calcolando un selettore CSS unico tramite `id` o `nth-child`, poi lo spara al pannello admin via `postMessage`. Il popup si chiude, e boom — hai appena detto a Hermes esattamente dove agganciare il tooltip di aiuto. Niente selettori CSS a mano, niente ispezione del codice sorgente. Punta e clicca. [Guardalo](https://github.com/vjt/r13-hermes/blob/master/app/assets/javascripts/hermes.js#L184) — è grezzo, è hacky, ed è una delle cose più soddisfacenti che abbia mai scritto alle 3 di notte.

## Dall'hackathon all'ONU

Il bello di Amedeo, il mio capo all'[IFAD](https://www.ifad.org/) — un'agenzia specializzata delle Nazioni Unite — è che è uno di quelli che passa il tempo a guardare fuori dalla finestra, e tu pensi che stia sognando ad occhi aperti, ma in realtà sta mappando processi di business e bisogni reali in design brillanti nella sua testa. Poi si gira e ti tira fuori qualcosa di geniale.

Hermes è uno di quei momenti. Non stavamo parlando di nessun sistema di help prima. Nessuno aveva un progetto di help contestuale su nessuna roadmap. Quando arriva la Rails Rumble e al team serve un'idea, Amedeo torna da un pisolino e fa "help contestuale — un tag script che butti dentro una qualsiasi web app, e lui fa tutto il resto." Così, dal nulla. Al team piace all'istante.

È questo che rende Hermes buono: l'idea è genuinamente originale, non qualcosa che ci rigiravamo da tempo. Viene da uno che capisce come le persone usano davvero le applicazioni line-of-business, e che vede il vuoto che nessun altro nota. Dopo la Rumble, promuoviamo il progetto dentro l'IFAD, il repo si sposta su [ifad/hermes](https://github.com/ifad/hermes), e addirittura assumiamo uno dei membri del team per un periodo per continuare a svilupparlo. Diventa un vero strumento interno — tutorial rapidi e contestuali sulle nostre applicazioni web. Tutto resta open source.

Il concetto è ovunque oggi — ogni prodotto SaaS ha tooltip di onboarding e help contestuale. Quando l'abbiamo costruito noi, era genuinamente innovativo. A volte i migliori progetti da hackathon vengono da un visionario che conosce il problema a fondo, anche quando nessun altro lo vede ancora.

Il codice: [github.com/vjt/r13-hermes](https://github.com/vjt/r13-hermes)


---

**Open source dagli anni IFAD:** [ChronoModel](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/) (2012) • [data-confirm-modal](/it/posts/2013-07-02-data-confirm-modal/) (2013) • **Hermes (2013)** • [Eaco](/it/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/it/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • [TM → Pontoon](/it/posts/2018-02-14-translation-memory-pontoon/) (2018) • [ChronoModel 1.0](/it/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • [OneSpan 2FA](/it/posts/2020-09-11-integrating-onespan-2fa-with-ruby/) (2020) • [ansible-wsadmin](/it/posts/2026-04-11-ansible-wsadmin/) (2026)
