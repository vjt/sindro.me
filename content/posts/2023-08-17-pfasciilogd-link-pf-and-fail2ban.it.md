---
title: 'pfasciilogd: collegare pf e fail2ban'
date: 2023-08-17
tags: [freebsd, sysadmin, security]
categories: [development]
---

## TL;DR

FreeBSD: come bloccare i port scanner dall'enumerare le porte aperte sul
tuo server, usando fail2ban e una rappresentazione ASCII dei log di `pf`.

## Premessa

Uso [`fail2ban`](https://fail2ban.org/) per tenere alla larga attaccanti e bot
che tentano di scansionare i miei siti web o di forzare le mie caselle di posta.
Fail2ban funziona scansionando i file di log alla ricerca di pattern specifici e
mantenendo un conteggio delle corrispondenze per IP, e permette
all'amministratore di sistema di definire cosa fare quando quel conteggio supera
una soglia definita.

I pattern sono indicativi di attività malevola, come il tentativo di indovinare
la password di una casella di posta, o il tentativo di scansionare lo spazio di
un sito web alla ricerca di vulnerabilità.

L'azione da eseguire nella maggior parte dei casi è bloccare l'indirizzo IP
incriminato tramite il firewall della macchina, ma fail2ban supporta qualsiasi
meccanismo che tu possa concepire, purché possa essere attuato da un comando
UNIX.

## PF e i suoi log

Sul mio server FreeBSD uso l'eccellente [pf](https://docs.freebsd.org/en/books/handbook/firewalls/#firewalls-pf),
il packet filter, per gestire il traffico in entrata e per eseguire la
normalizzazione del traffico.

Il meccanismo di logging di PF è molto UNIX-iano: fornisce un'interfaccia di
rete virtuale (`pflog0`) sulla quale vengono inoltrati i primi byte dei
pacchetti bloccati da una regola con lo specificatore `log`, così che i log
dei blocchi in tempo reale possano essere ispezionati con un semplice:

```bash
# tcpdump -eni pflog0
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on pflog0, link-type PFLOG (OpenBSD pflog file), capture size 262144 bytes
01:48:13.748353 rule 1/0(match): block in on vtnet0: 121.224.77.46.41854 > 46.38.233.77.6379: Flags [S], seq 1929621329, win 29200, options [mss 1460,sackOK,TS val 840989709 ecr 0,nop,wscale 7], length 0
01:48:15.726215 rule 1/0(match): block in on vtnet0: 192.241.235.20.37422 > 46.38.233.77.5632: UDP, length 3
01:48:17.993439 rule 1/0(match): block in on vtnet0: 145.239.244.34.54154 > 46.38.233.77.1024: Flags [S], seq 3365362952, win 1024, length 0
^C
3 packets captured
3 packets received by filter
0 packets dropped by kernel
```

Questi log possono essere salvati da `pflogd` in un file formato `pcap` in
`/var/log/pflog`, che può essere usato per troubleshooting e ispezione
asincrona, sempre con `tcpdump` o qualsiasi cosa che sappia leggere file
`pcap` (come Wireshark).

## Limiti dei log binari

Avevo già configurato `fail2ban` per analizzare i log di `postfix`, `dovecot`
e `nginx`, così che se provi a forzare una password SMTP o IMAP sulla mia
macchina o provi a lanciare qualcosa come [`nikto`](https://github.com/sullo/nikto)
contro il mio sito web, verrai presto bannato da `fail2ban` e le tue
connessioni in entrata verranno droppate da `pf`.

Tuttavia non potevo chiedere a `fail2ban` di leggere il `pflog` binario
prodotto da `pflogd`, dato che `fail2ban` è basato su regex e capisce solo
input testuali.

## Python in soccorso

Ho pensato a un software che:

* Avviasse un loop `async`
* Lanciasse `tcpdump` e si agganciasse al suo `stdout` e `stderr`
* Scrivesse `stdout` e `stderr` su un file
* Intercettasse un segnale `HUP` e `USR1` e riaprisse il file, per facilitare la rotazione dei log

## Lo posso avere?

Certo che sì! Vai su [GitHub](https://github.com/vjt/pfasciilogd/) e dai
un'occhiata a [`pfasciilogd`](https://github.com/vjt/pfasciilogd/) e alla
configurazione di supporto per `fail2ban`.

Spero che ti sia utile.

Buon divertimento!
