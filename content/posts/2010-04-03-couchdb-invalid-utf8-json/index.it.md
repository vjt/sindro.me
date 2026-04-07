---
title: "CouchDB 0.11 Invalid UTF-8 JSON: Risolto"
date: 2010-04-03T19:00:00Z
tags: [erlang, projects]
categories: [development]
---

![CouchDB logo](/posts/2010-04-03-couchdb-invalid-utf8-json/couchdb.png)

Se il tuo CouchDB 0.11 ti spara l'errore "Invalid UTF-8 JSON" ad **ogni** POST
o PUT che gli mandi, assicurati che nella tua
`$prefix/usr/lib/couchdb/erlang/lib` non ci siano residui di installazioni
precedenti.

Sul server di sviluppo [nostro](http://exelab.eu/), ho trovato due directory
("couch-0.10" e "mochiweb-r97") dalla vecchia installazione 0.10 che causavano
il problema.

Questo vale se hai aggiornato da sorgenti, come probabilmente hai fatto, perché
ad aprile 2010 non è che ci fossero tutti questi pacchetti di CouchDB 0.11 :-).

Un grazie enorme a [@couchdb](http://twitter.com/couchdb) per [avermi indicato
la direzione giusta](http://twitter.com/CouchDB/status/11495632471) dopo [aver
letto una segnalazione sulla mailing list
dev](http://mail-archives.apache.org/mod_mbox/couchdb-dev/201002.mbox/%3c112036548.3241265012630999.JavaMail.jira@brutus.apache.org%3e)
— ma non volevo fare "rimuovi e reinstalla" perché mi piace capire cosa sta
succedendo ;-).

<small>Nota a margine: che sia la fine dell'Hiatus? Spero di sì ;-p</small>
