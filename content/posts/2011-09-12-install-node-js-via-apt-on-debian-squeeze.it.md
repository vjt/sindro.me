---
date: "2011-09-12T12:00:00Z"
title: "Installare node.js via APT su Debian Squeeze"
tags: [linux, javascript, sysadmin]
---

In breve: aggiungi la sorgente APT di [SID](http://www.debian.org/releases/sid/),
configura l'[APT Pinning](http://wiki.debian.org/AptPreferences) per dare
priorità ai pacchetti di `squeeze` rispetto a quelli di `SID`, ricompila il
pacchetto `nodejs` sotto `squeeze`.

- Aggiungi la **sorgente APT di SID** creando `/etc/apt/sources.list.d/sid.list`
(usa il tuo [mirror più vicino](http://www.debian.org/mirror/)):

```plaintext
deb http://ftp.us.debian.org/debian/ sid main
deb-src http://ftp.us.debian.org/debian/ sid main
```

- Configura il pinning APT creando /etc/apt/preferences.d/sid:

```
Package: *
Pin: release a=unstable
Pin-Priority: 50
```

- Installa manualmente l'ultima versione di libv8, `libv8-3.8.9.20` al momento di questo articolo:

```
apt-get install libv8-3.8.9.20
```

- Scarica i sorgenti del pacchetto nodejs, le dipendenze e compilali:

```
cd
apt-get source nodejs
apt-get build-dep nodejs
cd nodejs-*
debuild -nc -uc
```

- Se incontri errori di dipendenze di build, dovresti provare prima ad abbassare
la dipendenza in debian/control, sia in Build-Depends che in Depends, e
rieseguire `debuild`. Se la compilazione fallisce (ad es. con `undefined reference to 'ev_run'`)
la versione precedente non ha le funzioni richieste. Quindi, devi installare le
versioni aggiornate delle dipendenze necessarie (ad es. `libev4`) da sid, usando
`apt-get install nome=versione` ad es. `libev4=1:4.11-1`. Lo suggerisco perché
dovrai aggiornare manualmente i pacchetti installati da sid, quindi meno sono,
meglio è.

- Installa il pacchetto generato
```
dpkg -i nodejs_*.deb nodejs-dev*.deb
```

- Profit :-)
