---
title: "Compilare pacchetti OpenWrt con VM cloud usa-e-getta e un bot Telegram"
date: 2026-03-28
tags: [openwrt, docker, python, networking]
description: "Un sistema basato su Docker che fa polling dei repo git, lancia VM Hetzner effimere per compilare pacchetti OpenWrt cross-architettura, e mette tutto dietro un bot Telegram. Ciclo completo: ~2 minuti, ~0,001 EUR a build."
---

Mantengo un mucchio di pacchetti OpenWrt custom su quattro architetture: MediaTek Filogic (aarch64), Raspberry Pi 2 (ARM), Ramips MT7621 (MIPS) e Atheros ath79 (MIPS). L'SDK di OpenWrt gira solo su x86_64. Non ho un build server dedicato. E non ne voglio uno -- una macchina che sta lì a far niente il 99,9% del tempo solo per compilare file `.ipk` ogni qualche giorno è un'offesa al mio senso di allocazione delle risorse.

Quindi ho costruito [openwrt-builder](https://github.com/vjt/openwrt-builder): un sistema che fa polling dei miei repo per le modifiche, lancia una VM Hetzner usa-e-getta quando deve compilare, builda i pacchetti, li riporta indietro, e distrugge il server. Il tutto controllato via Telegram.

<!--more-->

## L'architettura

Due container Docker, un `docker-compose.yml`:

1. **nginx** -- serve il feed dei pacchetti. I router OpenWrt puntano la loro config `opkg` qui, scaricano i file `.ipk` come da qualsiasi feed ufficiale.
2. **builder** -- un servizio Python che fa tre cose: gestisce il bot Telegram, fa polling dei repo git a intervalli regolari, e orchestra le build.

Quando un repo cambia (o premi `/rebuild` su Telegram), il builder capisce cosa fare. Ogni pacchetto dichiara il suo metodo di build -- compilazione SDK, script shell, `opkg-build`, o skip -- e il builder fa il dispatch di conseguenza.

Per tutto ciò che richiede l'SDK di OpenWrt, lancia un Hetzner CX23 (2 vCPU, 4 GB RAM), si collega in SSH, scarica l'SDK, compila il pacchetto, fa SCP del `.ipk` risultante, e distrugge il server. L'intero ciclo -- creazione, build, trasferimento, distruzione -- dura circa due minuti.

## Il costo di non avere un build server

Un CX23 costa 0,0066 EUR/ora. Una build dura ~2 minuti. Fa circa **0,001 EUR a build**. Potrei fare mille build al mese per un euro. Confrontalo con anche il VPS always-on più economico a 4 EUR/mese per una macchina che builda forse due volte a settimana. Non c'è proprio partita.

L'API di Hetzner rende tutto indolore. Crei un server con una chiave SSH, aspetti che booti, esegui comandi via SSH, tiri giù gli artefatti, cancelli il server. Nessuno stato da gestire, nessuna patch di sicurezza da applicare, nessun disco che si riempie di vecchi SDK.

## Telegram come control plane

Il bot è volutamente semplice:

- `/status` -- cosa sta girando, cosa è in coda
- `/list` -- tutti i pacchetti tracciati e la loro ultima build
- `/rebuild <pacchetto>` -- forza una rebuild adesso
- `/logs` -- tail dell'output di build recente

Gestisco la rete di casa dal telefono metà del tempo. Avere il sistema di build nella stessa chat Telegram dove ricevo gli alert dai router è naturale. Pusha un commit, ricevi una notifica che la build è partita, un'altra quando è finita. Se qualcosa si rompe, i log sono lì.

## Build multi-target

Il builder gestisce quattro target OpenWrt out of the box. Ogni target ha il suo URL SDK, la sua directory di output nel feed, e il suo set di pacchetti. Quando un pacchetto supporta più target, il builder lo compila una volta per target -- stesso sorgente, SDK diverso, `.ipk` diverso. Il feed è organizzato per target, così ogni router scarica solo i pacchetti per la propria architettura.

L'auto-detection fa il resto: se un repo ha un `Makefile` con struttura da SDK OpenWrt, si fa una build SDK. Se ha un `build.sh`, si esegue quello. Se sono solo file dati, `opkg-build` li impacchetta. Nessuna configurazione per pacchetto, a parte un hint di una riga.

## Lo stack

Python con `python-telegram-bot` (async), API Hetzner Cloud, rsync/SCP per i trasferimenti, Docker Compose per tenere tutto insieme. Il tutto sono circa 1500 righe di Python e gira sullo stesso Raspberry Pi 5 che ospita il resto della mia infrastruttura domestica.

Sorgente: [github.com/vjt/openwrt-builder](https://github.com/vjt/openwrt-builder)
