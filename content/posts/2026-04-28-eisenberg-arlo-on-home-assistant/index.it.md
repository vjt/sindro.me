---
title: "Eisenberg: telecamere Arlo su Home Assistant, fatto bene"
date: 2026-04-28
tags: [home-assistant, arlo, hacs, mqtt, python, devlog]
description: "Una integration Home Assistant per le telecamere Arlo: piccola, tipata, event-driven. Push una volta, poi silenzio per 14 giorni. Niente IMAP, niente Cloudflare bypass, niente roulette del rate-limit."
image: cover.jpg
featuredImage: cover.jpg
---

Configurare una telecamera Arlo su Home Assistant dovrebbe avere questo aspetto:

1. Installi l'integration da HACS.
2. Inserisci email e password Arlo.
3. Il telefono vibra. Tocchi **Approva** nell'app Arlo.
4. Clicchi **Submit** in Home Assistant.
5. Sei dentro.

<!--more-->

Questo è tutto il flow. Niente setup IMAP, niente dialog dove incollare codici 2FA, niente schermata con uno spinner che va in timeout, niente sorpresa "rate-limited, riprova fra due ore". È lo stesso flow trusted-browser che `my.arlo.com` esegue nel tuo laptop — l'integration semplicemente fa passare una push sul tuo telefono, cattura il cookie di trust valido 14 giorni, e poi sta zitta.

Quella push servirà di nuovo solo quando il cookie scade. L'integration lo persiste fra restart e lo riusa a ogni risveglio. Nel caso comune, ti autentichi una volta e poi non vedi più dialog di auth.

Il progetto vive su [github.com/vjt/ha-eisenberg](https://github.com/vjt/ha-eisenberg). L'ho chiamato Eisenberg in onore di Arlo Eisenberg, lo skater. Il nome è un atto di debolezza. Andiamo avanti.

## Cosa ti porti a casa

- **Una camera entity** con snapshot on-demand, thumbnail dei motion event, e streaming live RTSPS. Lag sotto il secondo in HLS. La tile sulla dashboard tiene un'immagine anche quando la camera è disarmata (Arlo rifiuta gli snapshot cloud in standby), salvando l'ultimo frame buono su disco.
- **Binary sensor di movimento**, sia quello generico sia i sensor AI con classificazione person / vehicle / animal che si auto-resettano.
- **Una select per la security mode** — `armAway`, `armHome`, `standby` — pilotabile da qualsiasi automation. Lo agganci al tuo alarm panel, allo stato di `person.*`, a uno schedule orario, a quello che vuoi.
- **Uno switch sirena**, **sensori batteria e segnale**, **connettività della base station**.
- **Un servizio `eisenberg.snapshot`** per pulsanti dashboard o automation triggerate dal motion. Fallisce ad alta voce se la camera è in standby invece di fare un no-op silenzioso, perché quella è il tipo di cosa che debuggi solo all'1 di notte.
- **Archiviazione opzionale a rotazione** di clip motion, thumbnail e keyframe degli stream in una location `media_dirs`, con retention configurabile (default 14 giorni).

Ogni motion event spara anche un evento `eisenberg_media` sul bus di HA con le AI category, content URL, thumbnail URL, durata, timestamp. Ci agganci automation a piacere.

## Sotto il cofano (in breve)

L'integration è event-driven. Non c'è un polling loop. Il firehose MQTT di Arlo trasporta ogni cambio di stato — motion, classificazione AI, URL degli snapshot, cambio mode, heartbeat della base station — e un singolo coordinator distribuisce quei dati agli entity nel momento esatto in cui arrivano. REST viene usato solo per i comandi (start stream, set mode, fire snapshot) e la device discovery iniziale.

La libreria client è un package PyPI tipato basato su `aiohttp` + `asyncio` ([`pyeisenberg`](https://pypi.org/project/pyeisenberg/)). MQTT 3.1.1 è implementato da zero sopra la stessa sessione WebSocket — nessun secondo stack TCP da tenere in vita. Ogni payload API e MQTT atterra in un model Pydantic, così le shape sconosciute fanno rumore in development invece di passare in silenzio. Quella disciplina ha fatto saltare fuori tre tipi di evento che Arlo aveva iniziato a emettere senza dirlo a nessuno e sarebbero rimasti invisibili.

Per i curiosi: niente bypass di Cloudflare, niente rituali di User-Agent spoofing oltre all'unico punto in cui Arlo gate-keepa l'RTSP su una UA mobile, niente scraping IMAP per i codici 2FA. Tutto il progetto è abbastanza piccolo da leggerselo in un pomeriggio, ed era esattamente il punto.

## Testato su, limiti

Costruita e usata su un **Arlo Essential XL HD** (batteria + solare, WiFi, cloud-only). Altri modelli Arlo che condividono le stesse shape v3 automation + MQTT dovrebbero funzionare — apri una issue se il tuo non lo fa. Tutte le Arlo sono cloud-only by design dell'hardware; questa integration non può aggiustarlo, può solo far sembrare il path cloud locale.

## Come prenderla

```
HACS → Custom repositories → https://github.com/vjt/ha-eisenberg
```

Oppure clicca il badge **Open in HACS** sul README — fa un deep-link nella tua istanza col repo precompilato. Sorgente MIT. La libreria client è `pyeisenberg` su PyPI. Tutto ti sta in testa.
