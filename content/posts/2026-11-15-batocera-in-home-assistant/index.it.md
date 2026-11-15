---
title: "Batocera dentro Home Assistant"
date: 2026-11-15
tags: [home-assistant, batocera, retrogaming, emulationstation, mqtt, hacs, claude-code, ai-generated]
description: "ha-batocera: un'integrazione Home Assistant per una console di retrogaming con Batocera. Cerchi e lanci i giochi dal telefono, vedi a cosa si gioca e per quanto, guardi la TV in diretta, chiudi un gioco piantato e metti dei limiti di tempo."
image: cover.jpg
featuredImage: cover.jpg
---

> **Prima di cominciare.** Batocera è una distribuzione Linux per il
> retrogaming: un PC si avvia direttamente in EmulationStation, un menu che
> si usa col joypad, con dietro gli emulatori delle vecchie console e dei
> vecchi home computer. I giochi negli screenshot sono copie di backup di
> originali miei. Questo post non incoraggia a scaricare giochi, e niente di
> quello che descrive ne scarica.

Sotto la TV c'è **joker**, un mini PC con Batocera 43: la console dei
bambini. Adesso è anche un dispositivo di Home Assistant, grazie a
un'integrazione che ho scritto con Claude Code:
[ha-batocera](https://github.com/vjt/ha-batocera).

## Perché

- **La ricerca.** Su joker ci sono migliaia di giochi, e cercarli col
  joypad vuol dire una tastiera a schermo, una lettera alla volta. Dal
  telefono scrivo "mario", vedo tutti i Mario di tutti i sistemi, e con un
  tocco parte sulla TV.
- **A cosa giocano i bambini, e per quanto.** Sono i dati che vuoi avere
  prima di mettere un limite. I limiti sono venuti dopo.
- **Chiudere un gioco piantato.** A volte la combinazione di uscita sul
  joypad non risponde. Il tasto stop sul telefono sì.

## Com'è fatto

Un piccolo demone sulla console (Python, solo libreria standard) viene
avvisato da Batocera a ogni avvio e chiusura di un gioco, legge il catalogo
dall'API locale di EmulationStation e parla con Home Assistant via MQTT.
HACS lo distribuisce insieme all'integrazione.

```mermaid
graph LR
    launcher[launcher di Batocera] -->|avvio / chiusura| daemon[demone]
    es[EmulationStation] <-->|catalogo, lancio| daemon
    daemon <-->|MQTT| ha[Home Assistant]
```

## La pagina

L'integrazione aggiunge una pagina **Batocera** nella barra laterale:
aspetto da CRT scuro, font pixel, ovviamente. Preferiti, giocati di
recente, una tessera per sistema col suo logo.

![La pagina Batocera sul telefono: INSERT COIN, la casella di ricerca, e le tessere di preferiti, giocati di recente e di ogni sistema](/posts/2026-11-15-batocera-in-home-assistant/page-systems.jpg)

La ricerca funziona a ogni livello, su tutti i sistemi o dentro uno solo.
Cerca anche in quello che dicono le descrizioni dei giochi: quelli vengono
dopo i risultati per nome, sotto IN THE DESCRIPTION.

![Ricerca di "mario" con la tastiera del telefono](/posts/2026-11-15-batocera-in-home-assistant/page-search.jpg)

![Ricerca di "robotnik": 19 trovati, uno per nome e gli altri sotto IN THE DESCRIPTION, dal Mega Drive al MAME](/posts/2026-11-15-batocera-in-home-assistant/page-search-description.jpg)

I filtri per genere, decennio e voto, dentro un sistema o su tutti, si
combinano con la ricerca. Ogni livello dice quanti giochi contiene, la
ricerca o i filtri quanti ne hanno trovati.

![La home filtrata sui platform degli anni '80 e cercata per "mario": 9 trovati, ogni tessera col suo sistema](/posts/2026-11-15-batocera-in-home-assistant/page-filters.jpg)

Le ROM divise in cartelle, per genere o come ti pare, si sfogliano come
cartelle.

![Nintendo 64, 259 giochi, le ROM in cartelle per genere: action, fighting, platform, racing e così via](/posts/2026-11-15-batocera-in-home-assistant/page-folders.jpg)

I giocati di recente rispondono alla prima domanda, a cosa si gioca
davvero:

![Giocati di recente, 50 giochi: Super Mario Bros. Wonder in corso, Mario Kart 8 Deluxe, New Super Mario Bros. U e altri; un titolo sfocato](/posts/2026-11-15-batocera-in-home-assistant/page-recently-played.jpg)

Tocchi un gioco e la scheda dice cos'è: anno, genere, giocatori, voto,
chi l'ha fatto, la descrizione. **PRESS START**, e parte sulla TV. Se ce
n'è già uno aperto, la scheda dice quale sta per chiudere.

![La scheda di lancio di Metal Sonic Rebooted: 2018, platform, un giocatore, quattro stelle, autori e descrizione, che avvisa che chiuderà Super Mario Bros. Wonder](/posts/2026-11-15-batocera-in-home-assistant/page-press-start.jpg)

Mentre si gioca, la barra in alto mostra cosa, da quanto, e quanto tempo
resta. KILL vuole due tocchi, perché un gioco chiuso per sbaglio perde
quello che non era salvato.

![La barra del gioco in corso: Mario Kart 8 Deluxe, un minuto, FREE PLAY, con KILL](/posts/2026-11-15-batocera-in-home-assistant/page-now-playing.jpg)

Sfogliare possono tutti; lanciare e fermare, solo un admin o un utente
scelto nelle opzioni.

## Lo schermo in diretta

L'anteprima nella barra è uno screenshot della TV, aggiornato ogni 15
secondi. La tocchi e va in diretta, più o meno un fotogramma al secondo,
finché qualcuno guarda.

<img src="/posts/2026-11-15-batocera-in-home-assistant/page-live.webp" width="576" height="1200" alt="Lo schermo in diretta: Super Mario Bros. Wonder in corso, la TV mostrata a circa un fotogramma al secondo" loading="lazy">

## Spegnere e accendere

SHUT DOWN spegne la console come fa il menu di EmulationStation, quindi le
liste dei giochi vengono salvate, dopo aver chiuso il gioco come fa lo
stop. A console spenta la pagina lo dice, e i giochi restano lì da
sfogliare. POWER ON la sveglia dalla rete, senza indirizzi MAC da scrivere:
è la console stessa, finché è accesa, a dire a Home Assistant come
svegliarla.

![La pagina Batocera a console spenta: OFFLINE, nessun segnale dalla console, un bottone POWER ON, i giochi ancora da sfogliare](/posts/2026-11-15-batocera-in-home-assistant/page-offline.jpg)

## I limiti

Tre, per tutta la console: un limite giornaliero in minuti, una fascia di
orari consentiti e un blocco manuale. Si impostano dalla pagina del
dispositivo, e solo un admin li può cambiare. Cinque minuti prima della
fine Home Assistant lancia un evento che puoi trasformare in una notifica;
alla fine ferma il gioco, e continua a fermare quelli nuovi.

![La pagina del dispositivo joker: consentito da, consentito fino a e limite giornaliero](/posts/2026-11-15-batocera-in-home-assistant/device-limits.jpg)

Non è una fortezza, e il README dice dove sono i buchi.

## Un avvertimento

L'API web di EmulationStation si può aprire a tutta la rete con
l'impostazione `PublicWebAccess`, e a quel punto chiunque in LAN può
lanciare giochi o mandare input, senza autenticazione. ha-batocera non la
apre mai, e se la trova aperta lo dice in **Impostazioni, Riparazioni**.

## Installarlo

Serve un broker MQTT raggiungibile dalla console e l'accesso SSH di root
alla console. Aggiungi il repository a HACS come repository personalizzato
(la richiesta per lo store di default è
[aperta](https://github.com/hacs/default/pull/14180)), installa, poi
"Aggiungi integrazione, Batocera": Home Assistant installa il demone via
SSH e lo tiene aggiornato, mai a partita in corso. I dettagli sono nel
[README](https://github.com/vjt/ha-batocera).

## Com'è nato

Tre giornate di lavoro con Claude Code: io dicevo cosa volevo, provavo su
joker e sul telefono, e rimandavo indietro quello che non andava. Dalla
0.2 alla 0.9.1, diciannove release, quasi trecento test.

Strada facendo ho preso abbastanza trappole di Batocera da metterle per
iscritto: [batocera-skill](https://github.com/vjt/batocera-skill), una skill
di Claude Code per pilotare una console Batocera via SSH. Niente ROM,
niente demoni, niente che resti acceso.

Licenza MIT per entrambi.
