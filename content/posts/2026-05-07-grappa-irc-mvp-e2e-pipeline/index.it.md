---
title: "grappa-irc: ci avviciniamo all'MVP, con una test pipeline vera dietro"
date: 2026-05-07
tags: [irc, azzurra, grappa-irc, elixir, phoenix, projects, ai-generated, open-source, testing, playwright, docker, ci]
description: "Update veloce: grappa-irc è vicino all'MVP. E la lezione che ho dovuto imparare a testate — un agente LLM ha bisogno di qualcosa di deterministico contro cui testare."
image: cicchetto-grappa-channel.png
featuredImage: cicchetto-grappa-channel.png
---

[Due settimane fa](/it/posts/2026-04-24-grappa-irc-elixir-beam-stack/) abbiamo scelto lo stack — Elixir sul BEAM. Oggi, [cicchetto](https://github.com/vjt/grappa-irc) (la PWA) davanti a un bouncer funzionante, in conversazione con una rete IRC vera — la copertina qui sopra mostra il canale `#grappa`; qui sotto, `#sniffo`:

<!--more-->

![cicchetto su #sniffo](cicchetto-sniffo-channel.png)

Non è ancora bello, non è feature-complete, ma i messaggi viaggiano round-trip — IRC ↔ grappa ↔ cicchetto — lo scrollback persiste, lo switch tra canali funziona. L'MVP è **vicino**.

## La lezione: agli LLM serve qualcosa di deterministico contro cui testare

La parte onesta di questo update è la lezione che ho dovuto imparare a testate.

Le prime settimane stavo guidando l'agente a testare **in tempo reale**: Chrome via MCP, irssi via tmux, occhio agli screenshot, copia-incolla degli errori in console. Questa modalità ha il suo posto — è genuinamente utile quando sai già che qualcosa non va e ti serve un paio di mani in più per smanettarci, riprodurre un bug puntuale, isolare un comportamento strano in una sessione usa-e-getta. Come *loop di sviluppo*, però — una rete di regressione che giri a ogni modifica per assicurarti che niente si sia rotto — non scala, e non scalerà mai.

Due motivi, entrambi strutturali.

Primo, un LLM è fuzzy per design — output probabilistico, contesto che deriva, nessuna garanzia che lo stesso prompt due volte produca la stessa sequenza di azioni due volte. È tollerabile per una caccia al bug puntuale: l'agente fa il lavoro di gambe, tu leggi il risultato, la varianza vive dentro una singola sessione ad-hoc. È fatale come check di regressione a ogni push: non puoi lanciare "guida il browser, guida il client IRC, dimmi se si è rotto qualcosa" in automatico e fidarti di una risposta diversa ogni volta.

Secondo, e più tosto, il setup stesso sconfigge la guida via linguaggio naturale. Due server IRC + services, un bouncer, una SPA, un nginx davanti — descrivere il comportamento end-to-end giusto in prosa, abbastanza dettagliata perché un LLM lo verifichi in modo consistente, è una battaglia persa. La superficie è troppo grande; i failure mode sono troppi; la spec in prosa cresce più di quanto un umano riesca a mantenerla. Quello che è chiaro in un prompt è ambiguo nel successivo. Servono spec *verificabili dalla macchina*, non narrate.

Quindi mi sono fermato, ho fatto un passo indietro, e ho chiesto all'agente di costruire la cosa di cui aveva davvero bisogno: una **test pipeline end-to-end completa**. [Docker Compose](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/compose.yaml), gira su [GitHub Actions](https://github.com/vjt/grappa-irc/blob/main/.github/workflows/integration.yml) a ogni push:

- una rete IRC completa — Bahamut `ircd` + services in stile Anope — bootata da zero dentro container, in un repo a parte ([azzurra-testnet](https://github.com/vjt/azzurra-testnet)) e tirata dentro come submodule sotto [`cicchetto/e2e/infra`](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e)
- un **client IRC sintetico** — [`cicchetto/e2e/fixtures/ircClient.ts`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/fixtures/ircClient.ts) — che scripta "l'altro lato della conversazione" in modo deterministico su una socket TCP raw
- il bouncer grappa — buildato dalla stessa sorgente dell'immagine dev — che si collega al leaf del testnet come utente normale
- [nginx](https://github.com/vjt/grappa-irc/blob/main/infra/nginx.conf) davanti alla PWA cicchetto, stessa config di prod
- un **Chrome headless via Playwright** — [`playwright.config.ts`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/playwright.config.ts), runner image in [`cicchetto/e2e/runner/Dockerfile`](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/runner/Dockerfile) — che guida la PWA come farebbe un umano. In parallelo gira anche Webkit su viewport iPhone-15, per i test iOS-shaped.

Tutto incollato da [`scripts/integration.sh`](https://github.com/vjt/grappa-irc/blob/main/scripts/integration.sh) — `compose up`, run della suite, `compose down -v` in uscita, niente stato dangling.

A ogni run di CI il cerchio si chiude:

1. tutti i server bootano
2. il bouncer si connette alla rete IRC
3. il client sintetico e l'utente lato bouncer si scambiano messaggi
4. il bouncer **persiste** quei messaggi nel suo scrollback su sqlite
5. la PWA, guidata da Playwright, esegue i flussi UX attesi sopra a un backend vero

La matrice di spec attuale vive in [`cicchetto/e2e/tests/`](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e/tests) — da M1 a M12 copre l'UX di messaggistica e finestre, più un regression case ([BUG7](https://github.com/vjt/grappa-irc/blob/main/cicchetto/e2e/tests/bug7-ios-own-msg-visible.spec.ts)) per un bug iOS in cui i propri messaggi non comparivano fino a refresh. Ogni spec è un singolo flusso visibile all'utente. Ne leggi uno e indovini cosa testa il successivo.

Prima avevamo unit test sulla UI. Erano della forma sbagliata — esercitavano componenti in isolamento, non la superficie d'interazione utente. Un bottone può superare ogni assertion sui suoi props e restare non-cliccabile in un browser vero. Adesso testiamo l'UX, in un browser vero, contro un bouncer vero, contro un IRCd vero. Cerchio chiuso, niente fuzz.

Il corollario che avevo già mezzo-interiorizzato ma non stavo applicando: **dai all'LLM un target che può colpire in modo deterministico, poi fidati del loop**. Test verdi = ok. Test rossi = correggi. Niente più "a me sullo schermo va, shippiamo." È sana ingegneria — il TDD lo predica da vent'anni — ma con un LLM al volante il costo di *non* farlo è amplificato. Senza target deterministici l'agente dichiara volentieri vittoria su codice rotto, perché il suo campione di "evidenza" è troppo piccolo e troppo rumoroso per essere un test vero.

Con questa pipeline in piedi, la strada per l'MVP è chiara: ogni nuova feature UX entra con la [sua spec Playwright](https://github.com/vjt/grappa-irc/tree/main/cicchetto/e2e/tests), l'agente guida il proprio loop, e io rivedo la diff e il badge verde della CI. Il modello è questo.

## A breve

Un paio di settimane ancora per passare il mio review gate, poi apro al pubblico. Prima, hardening: ultimamente vedo `fail2ban` lavorare di più, port scan e spider in aumento su questo sito — del setup ne avevo [parlato tempo fa nel post su pfasciilogd](/it/posts/2023-08-17-pfasciilogd-link-pf-and-fail2ban/), continua a guadagnarsi lo stipendio — e voglio che grappa shippi in un'internet ostile senza sorprese. Flussi SASL, rate limit, superficie d'auth, igiene dei container. Poi annuncio.

Repo aperto come sempre: [github.com/vjt/grappa-irc](https://github.com/vjt/grappa-irc). Issue benvenute. Su [#grappa via webchat Azzurra](https://webchat.azzurra.chat/?join=#grappa) trovi `vjt-claude` (l'AI a cui ho passato il contesto del progetto) o me, quando ci sono.
