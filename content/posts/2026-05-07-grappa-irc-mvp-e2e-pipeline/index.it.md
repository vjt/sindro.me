---
title: "grappa-irc: ci avviciniamo all'MVP, con una test pipeline vera dietro"
date: 2026-05-07
tags: [irc, azzurra, grappa-irc, elixir, phoenix, projects, ai-generated, open-source, testing, playwright, docker, ci]
description: "Update veloce: grappa-irc è vicino all'MVP. E la lezione che ho dovuto imparare a testate — un agente LLM ha bisogno di qualcosa di deterministico contro cui testare."
image: cicchetto-grappa-channel.png
featuredImage: cicchetto-grappa-channel.png
---

[Due settimane fa](/it/posts/2026-04-24-grappa-irc-elixir-beam-stack/) abbiamo scelto lo stack — Elixir sul BEAM. Oggi, [cicchetto](https://github.com/vjt/grappa-irc) (la PWA) davanti a un bouncer funzionante, in conversazione con una rete IRC vera — la copertina qui sopra mostra il canale `#grappa`; qui sotto, `#softs`:

<!--more-->

![cicchetto su #softs](cicchetto-softs-channel.png)

Non è ancora bello, non è feature-complete, ma i messaggi viaggiano round-trip — IRC ↔ grappa ↔ cicchetto — lo scrollback persiste, lo switch tra canali funziona, e la sidebar in stile irssi si riconosce. L'MVP è **vicino**.

## La lezione: agli LLM serve qualcosa di deterministico contro cui testare

La parte onesta di questo update è la lezione che ho dovuto imparare a testate.

Le prime settimane stavo guidando l'agente a testare **in tempo reale**: Chrome via MCP, irssi via tmux, occhio agli screenshot, copia-incolla degli errori in console. Per uno spike di cinque minuti regge. Come loop di sviluppo, **non** regge.

Il motivo è scolpito nel modo in cui un LLM lavora: è fuzzy per design. Output probabilistico, contesto che deriva, nessuna garanzia che lo stesso prompt due volte produca lo stesso passo due volte. Dagli un target *vivo* — una sessione browser che muta, un pannello tmux con stato, una rete IRC remota che può laggare — e la sua fuzziness si moltiplica con la variabilità del sistema. Bug che dovrebbero essere deterministici diventano *intermittenti*. "Ieri funzionava" diventa la modalità di guasto dominante. Passi più tempo a fare l'arbitro all'agente che a programmare.

Quindi mi sono fermato, ho fatto un passo indietro, e ho chiesto all'agente di costruire la cosa di cui aveva davvero bisogno: una **test pipeline end-to-end completa**. Docker Compose, gira su GitHub Actions a ogni push:

- una rete IRC completa — `ircd` + services — bootata da zero dentro container
- un **client IRC sintetico** che scripta in modo deterministico "l'altro lato della conversazione"
- il bouncer grappa che si collega alla rete del client sintetico come utente normale
- nginx davanti alla PWA cicchetto
- un **Chrome headless via Playwright** che guida la PWA come farebbe un umano

A ogni run di CI il cerchio si chiude:

1. tutti i server bootano
2. il bouncer si connette alla rete IRC
3. il client sintetico e l'utente lato bouncer si scambiano messaggi
4. il bouncer **persiste** quei messaggi nel suo scrollback su sqlite
5. la PWA, guidata da Playwright, esegue i flussi UX attesi sopra a un backend vero

Prima avevamo unit test sulla UI. Erano della forma sbagliata — esercitavano componenti in isolamento, non la superficie d'interazione utente. Un bottone può superare ogni assertion sui suoi props e restare non-cliccabile in un browser vero. Adesso testiamo l'UX, in un browser vero, contro un bouncer vero, contro un IRCd vero. Cerchio chiuso, niente fuzz.

Il corollario che avevo già mezzo-interiorizzato ma non stavo applicando: **dai all'LLM un target che può colpire in modo deterministico, poi fidati del loop**. Test verdi = ok. Test rossi = correggi. Niente più "a me sullo schermo va, shippiamo." È sana ingegneria — il TDD lo predica da vent'anni — ma con un LLM al volante il costo di *non* farlo è amplificato. Senza target deterministici l'agente dichiara volentieri vittoria su codice rotto, perché il suo campione di "evidenza" è troppo piccolo e troppo rumoroso per essere un test vero.

Con questa pipeline in piedi, la strada per l'MVP è chiara: ogni nuova feature UX entra con il suo case Playwright, l'agente guida il proprio loop, e io rivedo la diff e il badge verde della CI. Il modello è questo.

## A breve

Un paio di settimane ancora per passare il mio review gate, poi apro al pubblico. Prima, hardening: ultimamente vedo `fail2ban` lavorare di più, port scan e spider in aumento su questo sito — del setup ne avevo [parlato tempo fa nel post su pfasciilogd](/it/posts/2023-08-17-pfasciilogd-link-pf-and-fail2ban/), continua a guadagnarsi lo stipendio — e voglio che grappa shippi in un'internet ostile senza sorprese. Flussi SASL, rate limit, superficie d'auth, igiene dei container. Poi annuncio.

Repo aperto come sempre: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issue benvenute. Su [#grappa via webchat Azzurra](https://webchat.azzurra.chat/?join=#grappa) trovi `vjt-claude` (l'AI a cui ho passato il contesto del progetto) o me, quando ci sono.
