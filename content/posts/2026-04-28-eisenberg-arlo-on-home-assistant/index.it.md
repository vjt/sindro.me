---
title: "Eisenberg: telecamere Arlo su Home Assistant, fatto bene"
date: 2026-04-28
tags: [home-assistant, arlo, hacs, mqtt, python, devlog]
description: "Una integration Home Assistant per le telecamere Arlo: piccola, tipata, event-driven. Push una volta, poi silenzio per 14 giorni."
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

Questo è tutto il flow. È lo stesso flow trusted-browser che `my.arlo.com` esegue nel tuo laptop — l'integration fa passare una push sul tuo telefono, cattura il cookie di trust che Arlo emette (valido 14 giorni), e poi sta zitta.

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

## Come funziona

L'integration è event-driven. Non c'è un polling loop. Arlo pubblica i propri cambi di stato — motion, classificazione AI, URL degli snapshot, cambio mode, heartbeat della base station — su un firehose MQTT, e un singolo coordinator distribuisce quei dati agli entity nel momento esatto in cui arrivano. REST viene usato solo per le cose che richiedono davvero un request/response: avviare uno stream, settare una mode, scattare uno snapshot, la device discovery iniziale.

### Auth

Il primo login fa l'handshake completo: `POST /api/auth` con la password (codificata base64) restituisce un token a vita breve. Quel token guida poi `POST /api/getFactorId` per chiedere ad Arlo se questo browser è già trusted. Se lo è, `POST /api/startAuth` chiude in silenzio e sei autenticato. Se non lo è, parte una push — una sola — che l'utente approva sul telefono, e un singolo `POST /api/finishAuth` conferma. La risposta di Arlo include un cookie di trust valido 14 giorni che noi persistiamo nel config entry di Home Assistant. Ogni restart successivo riusa quel cookie e il login si chiude in silenzio in tre round trip.

Punto cruciale: il flow form-driven fa una sola HTTP call per ogni click dell'utente sul dialog HA. Non c'è un task in background che martella `finishAuth` mentre l'utente cerca il telefono — Arlo rate-limita quell'endpoint pesantemente, e un retry loop stretto è il modo più veloce per lockarti fuori per ore.

Il token scade dopo circa due ore; il coordinator controlla ogni 30 minuti e refresha in silenzio al sessantesimo minuto, che lascia un margine comodo verso la scadenza.

### MQTT

Il firehose di eventi di Arlo è MQTT 3.1.1 puro su WebSocket. L'integration implementa quel protocollo direttamente sopra la stessa sessione `aiohttp` WebSocket usata per REST — nessun secondo stack TCP, nessuna libreria separata da tenere viva tra una riconnessione e l'altra. Il codec MQTT è un modulo piccolo che gestisce il packet framing per la mezza dozzina di control packet che servono (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ) e ignora tutto il resto.

Ogni topic sottoscritto ha un handler tipato. Lo stato delle camere arriva su `cameras/+/is`, i motion event su `feed/live`, gli URL degli snapshot su `fullFrameSnapshotAvailable`, i cambi di mode su `automation/activeMode/is`, e così via. Il coordinator instrada ogni frame al giusto handler, parsa il payload in un model Pydantic, e aggiorna lo stato delle entity. Se un payload non matcha la shape attesa, viene loggato a WARNING — quella disciplina ha fatto saltare fuori tre tipi di evento che Arlo aveva iniziato a emettere senza dirlo a nessuno.

### Streaming

Arlo serve gli stream live su RTSP-su-porta-443-con-TLS, che tecnicamente è RTSPS. L'API ti dice `rtsp://`. Non crederci: riscrivi l'URL in `rtsps://` prima di passarlo allo stream worker di Home Assistant, e forza il transport TCP (UDP non può attraversare TLS). Poi aggiungi tre flag a ffmpeg — `fflags=nobuffer`, `flags=low_delay`, `use_wallclock_as_timestamps` — e il lag HLS scende da ~30 secondi a meno di uno. Verificato.

Lo User-Agent del browser ottiene RTSP dall'endpoint `startStream` di Arlo. Una UA mobile ottiene DASH al posto, che è più difficile da piegare allo stream component di HA, quindi l'integration manda una UA Chrome per tutto tranne che per questa singola call.

### Set della mode

L'arming della camera vive nell'API v3 location automation di Arlo: `PUT /hmsweb/automation/v3/activeMode?locationId=…&revision=N` col body `{"mode": "armAway"}`. Il counter `revision` è il token di concurrency ottimistica — incrementalo a ogni read, riportalo a ogni write. Se un client parallelo (l'app mobile Arlo, una automation) ha incrementato il counter a nostra insaputa, il PUT fallisce; rifettiamo la revision viva e riproviamo una volta.

### Persistenza dell'immagine

La tile dashboard si svuoterebbe altrimenti ogni volta che la camera viene disarmata (niente live snapshot) o a ogni restart (niente cache in-memory). Entrambi i problemi si risolvono allo stesso modo: ogni snapshot, thumbnail di motion, o keyframe di fine stream va sia nella cache in-memory sia su disco sotto la location `media_dirs` configurata. Al boot, il coordinator fa scan di quella location per l'immagine più recente per camera e seeda la cache da disco. Una retention prune (configurabile, default 14 giorni) spazza i file vecchi a ogni health-check tick.

## Perché l'ho costruito

Ho una sola telecamera Arlo. È cloud-only by design e su quello non potevo farci nulla, ma volevo che la parte *fra il mio Home Assistant e il cloud Arlo* fosse abbastanza piccola da poterla leggere da cima a fondo. `asyncio` nativo, tipi a ogni boundary, niente trucchetti di scraping, nessuna libreria che non volevo ereditare. Circa 1500 righe di Python fra integration e libreria client, tutto su PyPI sotto licenza MIT, e quello era esattamente il punto.

## Come prenderla

```
HACS → Custom repositories → https://github.com/vjt/ha-eisenberg
```

Oppure clicca il badge **Open in HACS** sul README — fa un deep-link nella tua istanza col repo precompilato. Sorgente MIT. La libreria client è `pyeisenberg` su PyPI.
