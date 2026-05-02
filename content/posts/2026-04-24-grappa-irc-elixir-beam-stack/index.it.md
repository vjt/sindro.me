---
title: "grappa-irc: lavori iniziati, stack scelto — Elixir su BEAM"
date: 2026-04-24
tags: [irc, azzurra, grappa-irc, elixir, beam, phoenix, projects, ai-generated, open-source]
description: "Update veloce: i lavori su grappa-irc sono partiti, e abbiamo deciso lo stack. Elixir/Phoenix sul BEAM."
image: cover.jpg
featuredImage: cover.jpg
---

[Quattro giorni fa](/it/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/) ho pubblicato il pitch di [grappa-irc](https://github.com/vjt/grappa-irc) — un BNC IRC con API REST e una PWA che parla solo HTTP. README-driven, pre-alpha, niente codice. Quattro giorni dopo, primo update: i lavori sono partiti, e abbiamo deciso lo stack.

<!--more-->

## Stack: Elixir su BEAM

Prima ipotesi era Rust + tokio + axum + sqlx. Ottima su memory safety e performance per-core, parser IRC pronto con la `irc` crate, walking-skeleton plan già scritto.

Poi mi sono fermato a riguardare il problema. Cosa fa grappa, davvero?

- **Connessioni TCP a lunga vita**, una per utente.
- **Stato persistente per-utente**: canali, scrollback, modi.
- **Crash isolation**: se cade la connessione upstream di un utente, gli altri non se ne accorgono.
- **Hot code reload**: aggiornare grappa senza far cadere le sessioni.
- **Concorrenza massiccia, IO-bound**: ogni utente è un processo che dorme finché non arriva un PRIVMSG.

Questa lista è il **brief originario di Erlang**. Telefonia anni '80 = milioni di chiamate concorrenti, lunga durata, isolation, hot upgrade. È esattamente la forma di un bouncer IRC moltiplicata per N utenti — un fit così pulito che mi sentivo scemo a non averlo visto subito.

E sopra ci sta **Phoenix**: framework web maturo, REST + Channels (WebSocket) nativi, e la parte client-side (`phoenix.js`) è già risolta a scala Discord. Non devo inventarmi io il transport tra grappa e cicchetto: c'è già, è collaudato, è disegnato esattamente per il pattern *server stateful per-utente che pusha eventi al browser*.

Pattern matching su tuple e binari collassa il parser IRC in tre righe. Supervision trees sostituiscono il "tokio task per user" con un modello dichiarativo: una `DynamicSupervisor` spawna un `GenServer` per utente, e se uno crasha si riavvia da solo, senza toccare gli altri. Hot reload viene gratis dal runtime. Mnesia o Ecto + sqlite per lo scrollback.

WhatsApp gira su BEAM da sempre — non per nostalgia: il modello fitta. Pattern collaudato a scale che grappa non vedrà mai.

Rust resta uno dei linguaggi che amo di più. Per grappa, però, BEAM è il fit.

## Prossimi passi

- README finalizzato.
- Walking-skeleton riscritto in Elixir/Phoenix (il piano Rust è archiviato, non buttato — la struttura del walking-skeleton vale a prescindere dal linguaggio).
- Phase 1.

Repo aperto: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issue benvenute. Su [#grappa via webchat Azzurra](https://webchat.azzurra.chat/?join=#grappa) trovi `vjt-claude` (l'AI a cui ho passato il contesto del progetto) o me, quando ci sono.
