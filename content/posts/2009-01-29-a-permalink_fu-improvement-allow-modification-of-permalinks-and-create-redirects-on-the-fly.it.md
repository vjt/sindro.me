---
date: 2009-01-29T19:00:00Z
title: "Un miglioramento a permalink_fu: permettere la modifica dei permalink e inviare redirect HTTP al volo"
tags: [permalink, plugin, projects, rails, ruby]
categories: [development]
---

Un altro spin-off dal sito [www.visitacsa.it](http://www.visitacsa.it/): un
miglioramento a
[permalink_fu](http://github.com/technoweenie/permalink_fu/tree/master) che
permette **permalink dinamici**. Lo so che è un
[ossimoro](http://en.wikipedia.org/wiki/Oxymoron), perché i permalink dovrebbero
essere... beh... permanenti! E siccome i [motori di
ricerca](http://www.searchlores.org/main.htm) li indicizzano, non dovrebbero
mai cambiare. Ma cosa succede quando pubblichi *qualcosa*, il tuo permalink
viene generato con permalink_fu usando il *titolo* del tuo post, e dopo un
paio di giorni vuoi cambiare il titolo, e anche il permalink sotto il quale il
post è accessibile?

Seguendo la
[specifica](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html), la tua
applicazione dovrebbe inviare uno status HTTP *301 moved permanently* quando si
accede al vecchio permalink e fare redirect del client verso il nuovo Uniform
Resource Locator. Questo è più o meno quello che fa la mia modifica a
*permalink_fu*: ogni volta che gli attributi del tuo post vengono modificati, il
permalink precedente e quello nuovo vengono salvati nel database, e puoi
abilitare il tuo controller a generare redirect *302 moved temporarily* quando
necessario. In altre parole, controlla se l'URL richiesto è un vecchio
permalink e reindirizza automagicamente il client verso quello nuovo.

Tutto avviene dietro le quinte, e il plugin ha anche dei comodi task rake per
impostare il model Redirect e le migration associate. E puoi anche cambiarne
il nome, ovviamente! :)

Il codice *302* è stato scelto perché lo status code *301 permanent* [ha
effetti piuttosto dirompenti sui motori di
ricerca](http://www.google.com/support/webmasters/bin/answer.py?hl=en&amp;answer=40132),
ma ulteriori discussioni sono benvenute.

Dai un'occhiata al [mio repository su
GitHub](http://github.com/vjt/permalink_fu/tree/master), leggi il
[README](http://github.com/vjt/permalink_fu/blob/b8d979f28c9795389cc65e9670a3529f805618dc/README)
che contiene la documentazione delle funzionalità aggiunte, e guarda il codice!
