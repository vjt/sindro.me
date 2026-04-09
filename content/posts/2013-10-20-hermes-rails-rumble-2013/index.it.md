---
title: "Hermes: help contestuale in 48 ore (Rails Rumble 2013)"
date: 2013-10-20
tags: [rails, ruby, open-source, hackathon]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Lo spazio dell'"help contestuale" è esploso in una vera categoria di prodotto — Intercom, Pendo, Appcues e altri oggi fanno questo commercialmente su scala. Il fork dell'IFAD ha continuato a vivere per anni dentro l'agenzia. La Rails Rumble stessa ha smesso di esistere dopo il 2015, e l'era degli hackathon competitivi da 48 ore ha lasciato il posto agli AI hackathon e agli startup weekend. Il [repo](https://github.com/vjt/r13-hermes) è archiviato ma ancora online.
{{< /retrospective >}}

La [Rails Rumble](http://railsrumble.com/) è — era — un hackathon di 48 ore dove team di massimo quattro persone costruiscono un'app web completa da zero usando Ruby. Niente lavoro preparatorio, niente codice pre-scritto. Solo caffeina, git e una scadenza.

Quest'anno il nostro team — [@amedeo](https://github.com/amedeo), [@liquid1982](https://github.com/liquid1982), [@maisongb](https://github.com/maisongb) e il sottoscritto — ha costruito **Hermes: the epic messenger service**, entry #385.

<!--more-->

## Cosa fa Hermes

L'idea era semplice ma genuinamente utile: dare ai proprietari di siti web un modo per integrare dell'**help contestuale** nelle loro applicazioni. Tooltip, banner, tutorial — contenuti che appaiono sulla pagina giusta al momento giusto, senza dover hard-codare nulla nell'app host.

L'integrazione era un singolo tag `<script>`. Quel file JS apriva un canale verso il backend di Hermes, che cercava l'URL corrente e restituiva il payload di help per quella pagina. I proprietari del sito gestivano tutto da una dashboard — nessun deploy necessario per aggiornare un tooltip o aggiungere uno step di walkthrough.

## 48 ore al 48rails

Abbiamo costruito il tutto al [48rails](https://web.archive.org/web/2013*/48rails.com), uno spazio di coworking in Italia che era praticamente la nostra base per questo tipo di follie. Due giorni di coding intenso, scelte alimentari discutibili e zero sonno. Il solito.

L'app era un classico stack Rails — niente di esotico. La parte interessante era il client JS e l'architettura del canale real-time, che abbiamo fatto funzionare sorprendentemente bene per qualcosa messo insieme in un weekend.

## Dall'hackathon all'ONU

Ecco la parte che non mi aspettavo: circa un anno dopo, nel novembre 2014, l'[IFAD](https://www.ifad.org/) — un'agenzia specializzata delle Nazioni Unite — ha preso in mano il progetto e finanziato lo sviluppo successivo. Il repo si è spostato su [ifad/hermes](https://github.com/ifad/hermes) ed è diventato un vero strumento interno per integrare documentazione contestuale nelle loro piattaforme web.

Un progetto da hackathon del weekend che trova casa in un'agenzia ONU. È il genere di cosa che ti fa pensare che il modello open-source funzioni davvero — a volte il modo migliore per dimostrare un'idea è costruirla in 48 ore e metterla su GitHub.

Il codice: [github.com/vjt/r13-hermes](https://github.com/vjt/r13-hermes)
