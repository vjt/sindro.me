---
date: 2011-07-07T14:00:00Z
title: Fare il bind della porta 80/TCP come non-root sul server di sviluppo
tags: [linux, ruby]
---

![Neo Tux](/posts/2011-07-07-binding-port-80-for-your-development-application-server/neo-tux.png)

Quindi hai una VM Linux che usi per lo sviluppo, perché vuoi replicare
l'ambiente di produzione il più fedelmente possibile. Hai molte applicazioni da
gestire, devono girare tutte contemporaneamente perché sono dei bei web service
REST JSON.

Sei stanchissimo di ricordarti quale hai messo sulla porta `8081`, e i tuoi file
di configurazione stanno diventando un vero casino. Quindi configuri degli alias
per gli indirizzi IP sull'interfaccia di rete e decidi di assegnare persino dei
nomi host — `/etc/hosts` va benissimo — per ogni applicazione.

Poi, in una configurazione del genere, perché dovresti ancora farle girare su
porte superiori a `1024`? Non sarebbe fantastico digitare il nome
dell'applicazione nella barra degli indirizzi del browser? Sì che lo sarebbe, ma
è meglio non farle girare come `root`, comunque.

La soluzione sono le [Linux
capabilities](http://www.kernel.org/doc/man-pages/online/pages/man7/capabilities.7.html)
(vedi anche [qui](http://www.friedhoff.org/posixfilecaps.html)). Quella che ci
interessa è `cap_net_bind_service`: dà a un processo il diritto di fare il bind
su porte well-known (< 1024). Se usi un linguaggio interpretato, ovviamente
dovrai aggiungere la capability all'interprete stesso. Ecco perché c'è
**sviluppo** nel titolo di questo articolo — non dovresti configurare questo su
un server di produzione, se non sai cosa stai facendo.

Un'ultima stranezza: se ti capita di fare `dlopen()` su shared object che
linkano dinamicamente verso librerie fuori dai path canonici, non puoi caricarli
tramite `LD_LIBRARY_PATH` (ad es. il `SYBASE.sh`) perché viene ignorato per i
processi con `setcap`. Meglio spostare i path delle librerie in uno snippet
dentro `/etc/ld.so.conf.d`.

## tl;dr

Assumendo che tu sia l'ultimo e più grande sviluppatore Rails, dovresti
diventare root — o usare sudo, come preferisci — e

```shell
# SEI SULLA TUA MACCHINA DI SVILUPPO
setcap cap_net_bind_service+ep `which ruby`
```

Profit:

```shell
thin start -a yourapp -p 80
>> Using rack adapter
>> Thin web server (v1.2.11 codename Bat-Shit Crazy)
>> Maximum connections set to 1024
>> Listening on yourapp:80, CTRL+C to stop
...
```
