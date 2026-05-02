---
title: '"Guess The Friend" — 48 ore di follia alla Rails Rumble'
date: 2012-10-14
tags: [rails, ruby, hackathon, facebook, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Questo gioco usava le API Facebook Graph per accedere alla lista amici, alle foto profilo e ai dati personali — nome, posizione, interessi, tutto. Sono **esattamente le stesse API** che [Cambridge Analytica](https://it.wikipedia.org/wiki/Scandalo_Facebook-Cambridge_Analytica) ha sfruttato nel 2018 per raccogliere i dati di 87 milioni di utenti Facebook a fini di profilazione politica. Noi ci abbiamo costruito un gioco da festa; loro una macchina di sorveglianza. Facebook ha chiuso queste API nel 2018 dopo lo scoppio dello scandalo. Il gioco non funziona più da allora. L'ironia è spessa — le stesse funzionalità della piattaforma che rendevano possibili i giochini social hanno anche reso possibile uno dei più grandi scandali sulla privacy nella storia della tecnologia.
{{< /retrospective >}}

Lo scorso weekend abbiamo partecipato alla [Rails Rumble](http://railsrumble.com/) 2012 — 48 ore per costruire un'app web da zero usando Ruby on Rails, nessuna preparazione consentita. Il nostro team faceva parte della community italiana [48rails](http://48rails.org/) e abbiamo costruito **Guess The Friend**: un gioco Facebook che implementa il classico [Indovina Chi?](https://it.wikipedia.org/wiki/Indovina_chi%3F) da tavolo, ma usando i tuoi *veri* amici di Facebook come personaggi.

(Sarei tornato alla Rumble [l'anno dopo](/it/posts/2013-10-20-hermes-rails-rumble-2013/) con un team diverso, a costruire [Hermes](/it/posts/2013-10-20-hermes-rails-rumble-2013/).)

<!--more-->

## Il team

Quattro persone, un weekend, zero ore di sonno:

- [Andrea Pavoni](https://github.com/andreapavoni) (@apeacox) — team lead, backend
- [Alessandro Vendruscono](https://github.com/vendruscolo) (@vendruscolo) — frontend
- [Claudio Floreani](https://github.com/ClaudioFloreani) (@ClaudioFloreani) — design
- [Marcello Barnaba](https://github.com/vjt) (@vjt) — backend, deployment

## Come funziona

Fai login con Facebook, l'app scarica la tua lista amici con foto e dati del profilo, e inizi una partita contro un altro giocatore. A ciascuno viene assegnato un "amico segreto" dalla lista amici dell'avversario. Poi a turno si fanno domande sì/no — "Questa persona vive a Milano?", "Ha la barba?" — e si eliminano i candidati finché non indovini chi è. Concetto semplice, sorprendentemente divertente quando le facce che ti fissano sono persone che conosci davvero.

## Il caos

Quarantotto ore sono tantissime e niente allo stesso tempo. Hai tempo di costruire qualcosa di vero, ma non abbastanza per farlo pulito. Solo il ballo dell'OAuth con Facebook ci ha mangiato un paio d'ore. Il deploy era Unicorn dietro nginx, pushato via Capistrano su un VPS — la demo girava su `i.sindro.me`. Il codice è esattamente quello che ti aspetti da un hackathon di 48 ore: funziona, è brutto, e nessuno ha scritto test.

Ecco un reel dall'hackathon — "la leggenda del pianista sulla keyboard" — il sottoscritto, privato del sonno e ubriaco, che scrive codice a tempo con [Windowpane](https://www.youtube.com/watch?v=O4OxrhVxCWY) degli Opeth durante la Rails Rumble:

<video controls width="100%" preload="metadata">
  <source src="/posts/2012-10-14-guess-the-friend-rails-rumble-2012/guessthefriend-reel.mp4" type="video/mp4">
</video>

Il codice è su GitHub: [andreapavoni/r12-guessthefriend](https://github.com/andreapavoni/r12-guessthefriend) (originale) e [vjt/guessthefriend](https://github.com/vjt/guessthefriend) (il mio fork). Non aspettarti codice pulito e copertura completa dei test — è un artefatto da hackathon, congelato nel tempo.
