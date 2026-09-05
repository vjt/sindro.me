---
title: "Il forum di Azzurra, tirato fuori dalla Wayback Machine"
date: 2026-09-05
tags: [irc, azzurra, wayback-machine, archeologia-digitale, python, sqlite, open-source]
description: "forum.azzurra.org è morto da anni. La Wayback Machine ne aveva ancora quasi tutto: 159484 post dal 2001 al 2016, oggi di nuovo leggibili e cercabili."
image: cover.jpg
featuredImage: cover.jpg
---

`forum.azzurra.org` è stato per quindici anni il posto dove la rete IRC italiana litigava
con calma. Poi è morto, come muoiono i forum: non con un annuncio, ma con un dominio che
smette di risolvere. Della Wayback Machine ci si ricorda sempre troppo tardi — stavolta no.

<!--more-->

> 🍸 *Sei capitato qui per caso? Questo è il racconto di come ho recuperato quindici anni di
> forum di una rete IRC. Se ti stai chiedendo perché uno nel 2026 si metta a fare
> archeologia di IRC, la risposta lunga è [qui](/it/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/),
> e quella corta è che IRC funziona ancora: **[clicca qui e torna nel 1995 →](https://grappa.chat/it/)** —
> scegli un nome, entri in una stanza, e sei dentro. Niente app, niente account.*

Il risultato è online e si legge senza registrarsi a niente:
**<https://vjt.github.io/azzurra-forum-archive/>** — il vecchio indirizzo
`sindro.me/t/forum-azzurra/` reindirizza lì, link profondi compresi. Il codice, gli
snapshot grezzi e tutto quello che serve per rifarlo stanno su GitHub:
**<https://github.com/vjt/azzurra-forum-archive>**.

Numeri, perché senza numeri è aria fritta: **114 forum, 7070 discussioni, 159484 post**,
dal 28 giugno 2001 al 29 luglio 2016. Ricerca full-text lato client, una pagina per
discussione, HTML statico che si scarica con `wget -r` e sopravvive a me.

## Perché

Perché è archeologia digitale, e tirare fuori roba morta per rimetterla in circolo è uno
dei mestieri più belli che ci siano. Su `web.archive.org` quel forum c'è ancora, in teoria:
in pratica ogni pagina è una richiesta a una macchina che regge la memoria di tutto il web
con le donazioni, e ci mette mezzo minuto a servirti una discussione del 2004. Qui ci
mettono qualche millisecondo, perché sono pagine già pronte.

Non è una critica all'Archive, è il contrario. Senza di loro questa roba non esisteva più:
il dominio è scaduto, il database è finito dove finiscono i database, nessuno aveva un
backup. Loro l'avevano fotografata per quindici anni senza che nessuno glielo chiedesse.
Io gli mando [10 dollari al mese](https://archive.org/donate) e continuerò a mandarglieli;
se ti è mai capitato di ritrovare grazie a loro qualcosa che davi per perso, valuta di fare
altrettanto. La storia di internet non si conserva da sola: se ne va in silenzio, un
dominio alla volta, e te ne accorgi il giorno che la cerchi.

E se c'eri, il pezzo divertente è
[la ricerca](https://vjt.github.io/azzurra-forum-archive/cerca/): cerca il tuo nick e
rileggiti com'eri vent'anni fa. Non sempre è una bella scoperta.

## Come è stato fatto

Da qui in poi è roba tecnica. Se non ti interessa, hai già il link che conta:
[vai a leggerti il forum](https://vjt.github.io/azzurra-forum-archive/), che è il motivo
per cui l'ho fatto.

Premessa, perché mi sembra scorretto non dirla: **il codice di questo archivio è
interamente generato da un LLM**. Ho descritto quello che volevo a Claude in una sessione
lunga — l'importatore, il merge, il renderer, gli script di download e anche questo post
sono usciti da lì. Io ho dato le istruzioni, ho letto quello che tornava, ho detto dove
sbagliava e ho deciso cosa tenere. Il mestiere non è sparito, si è spostato: la parte
noiosa la fa la macchina, sapere cosa si vuole e accorgersi quando il risultato è una
sciocchezza no.

L'architettura sta in una riga. Si chiede l'indice all'Archive, si scarica la lista degli
URL, si prendono **uno alla volta**, si parsano, si buttano in SQLite, e da SQLite si
generano le pagine statiche.

Il primo passo è l'indice CDX: `web.archive.org/cdx/search/cdx?url=forum.azzurra.org*`,
venti pagine di risultati, filtrate a `statuscode:200`, e **senza `collapse=urlkey`** —
quello collassato tiene un solo snapshot per URL, e se proprio quello l'Archive lo serve
vuoto non hai un ripiego. Vengono fuori timestamp, URL originale, mimetype e digest per
ogni scatto di ogni pagina: da lì si estrae, per ogni discussione, la lista degli snapshot
buoni in ordine di preferenza.

Il secondo è lo scaricamento, e va fatto in serie. Ogni URL si prende nella forma
`web/<timestamp>id_/<url>`: il suffisso `id_` restituisce i byte originali del 2004, senza
la barra di navigazione che l'Archive inietta. Tre secondi di pausa fra una richiesta e
l'altra, e dopo cinque fallimenti di fila due minuti di raffreddamento, perché a quel punto
non è un errore tuo: è l'Archive che ha chiuso la porta. Se lo script si ferma lo rilanci e
riprende da dov'era, perché un file già su disco non lo riscarica: con una lista da
diecimila pagine e una rete che si stufa, è la differenza fra finire e ricominciare.

Il terzo è il parsing, in tre passate e non una. Il forum ha cambiato software due volte —
phpBB 1.4.0, poi phpBB 2.0.x, poi vBulletin — e la Wayback Machine ha fotografato tutte e
tre le epoche, con tutte le skin che si sono succedute: cinque markup diversi per lo stesso
contenuto, ISO-8859-1, spesso tagliati a metà. Prima si importano gli 8834 snapshot
vBulletin nelle tabelle vere (`forums`, `threads`, `posts`, più l'indice FTS5), poi le 1604
pagine del vecchio board in tabelle di appoggio a parte, e solo alla fine un terzo script
fonde le seconde nelle prime. Il database non è un formato d'archivio, è un indice di
lavoro: si butta e si rifà in tre minuti.

L'ultimo passo legge SQLite e sputa HTML: una pagina per discussione, una per sezione, più
l'indice full-text lato client. Nessun database in produzione, nessun processo da tenere
vivo, niente che possa cadere alle tre di notte.

## Dove si inciampa

**Scaricare in parallelo non funziona, e non te lo dice.** Il primo giro lanciava i batch
in parallelo e rispondeva `HTTP 200` per tutto. Circa 2360 di quei 200 avevano il corpo di
lunghezza zero: è così che l'Archive rifiuta, senza dichiararlo. `curl` esce con `rc=0`,
tu leggi "successo" e ti porti a casa file vuoti. In serie, con tre secondi di pausa e
un raffreddamento lungo, la stessa lista ha reso il 100%. Un errore onesto vale mille volte
un successo finto.

**Parsare con severità butta via dati che ci sono.** Pretendere i delimitatori HTML
"giusti" azzerava 1939 discussioni perfettamente leggibili in una skin più vecchia;
pretendere il `</div>` di chiusura buttava via ogni snapshot che l'Archive aveva tagliato a
metà corpo. Due correzioni da due caratteri di regex, ~16000 post recuperati. Oggi il
parser accetta un corpo che finisce a EOF e lo marca `truncated = 1` — sono 771. Mezzo post
del 2001 vale più di nessun post.

**Il vecchio board non è un secondo forum, è lo stesso.** vBulletin si era già portato
dietro parte del contenuto phpBB, quindi il mirror non si accoda: si fonde, con dedup. E il
dedup non può guardare l'orologio, perché fra i due corpus c'è un'ora di scarto (il cambio
d'ora attorno alla migrazione) e due post dello stesso utente a due minuti di distanza sono
due post veri. La chiave che regge è il **corpo**: contenimento di token ≥ 0.8 e Jaccard
≥ 0.5, dentro 180 secondi da uno degli scarti 0/±1h, con lo scarto **misurato sul doppione
più vicino** e non deciso una volta per tutto il thread. Risultato: 8686 post nel mirror,
5286 davvero nuovi.

**La posizione nella pagina scaricata non è la posizione nel forum.** 144 discussioni si
leggevano fuori ordine, e nessuna per colpa del parser: la pagina del vecchio board tiene
dieci post e non quindici, vBulletin scrive l'ora nel formato di chi guardava (460 date
erano `01:21 PM`, e buttare via il marcatore le spostava di dodici ore), e uno snapshot
preso mesi dopo un altro non concorda sulle posizioni perché in mezzo qualcuno ha
cancellato un post. Dove il board ha lasciato un id, l'ordine è quello dell'id. Otto
discussioni su 7070 restano con un salto all'indietro: lì l'orologio mente e gli id no.

Il resto è un `Makefile`: `make db` ricostruisce il database SQLite da zero in tre minuti,
`make site` sputa 6634 pagine statiche in venticinque secondi, `make search` ci mette
sopra l'indice. Il database è sacrificabile e infatti non sta nel repository — `pages/` è
il contrario, e dodici discussioni sono comunque perse per sempre: ogni snapshot che
l'Archive elenca per loro torna vuoto.

Quello che resta è di chi l'ha scritto. Se sei l'autore di un messaggio e lo rivuoi via, si
apre una issue e sparisce.

Il forum sta qui: **<https://vjt.github.io/azzurra-forum-archive/>**. Il codice, se ti
serve per rifare la stessa cosa con un altro forum morto, sta
[su GitHub](https://github.com/vjt/azzurra-forum-archive).

> 🍸 *Azzurra c'è ancora, e IRC pure. Se ti è venuta voglia di vedere com'è oggi:
> **[grappa.chat](https://grappa.chat/it/)** — scegli un nome, clicca su una stanza, e sei
> nel 1995 senza installare niente. Il perché di tutto questo l'ho scritto
> [qui](/it/posts/2026-04-20-grappa-irc-reinventing-irc-for-2026/).*
