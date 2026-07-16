---
title: "GL-X3000 r6: allinearsi a monte senza rompere il modem"
date: 2026-07-16
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "Rebase della mia immagine GL-X3000 su 155 commit più recenti di OpenWrt 25.12, l'unica trappola di build che mi ha morso, e come ho flashato un uplink 5G vivo dimostrando che la radio non è regredita."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** ho ricostruito Jeeves — [il mio uplink 5G di backup su GL-iNet
GL-X3000](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/) — sulla
versione più recente di OpenWrt 25.12, portando il kernel da 6.12.85 a
6.12.94. I miei 20 commit di abilitazione hardware si sono riapplicati puliti
su 155 commit di upstream. Una trappola di build mi è costata una
ricostruzione. Poi ho flashato il router in funzione e ho controllato la
telemetria per confermare che la parte 5G fosse tornata invariata. L'immagine
è `jeeves-r6`, sulla
[pagina delle release](https://github.com/vjt/openwrt-glinet-x3000/releases).

<!--more-->

## Perché ricostruire

La [migrazione di aprile](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
ha messo Jeeves su OpenWrt 25.12 vanilla con il modem Quectel RM520N-GL
pienamente funzionante. Da allora l'upstream si è mosso di 155 commit e ha
alzato il kernel da 6.12.85 a 6.12.94. Niente di ciò cambia cosa fa Jeeves —
è igiene. Ma l'igiene non è gratis quando il tuo stack porta due patch di
kernel fuori dall'albero.

Il mio ha 20 commit sopra l'upstream, e due sono quelle che sorveglio a ogni
rebase:

- una insegna al driver MHI PCI generico a rivendicare l'RM520N-GL tramite il
  suo subvendor ID Qualcomm, così che il modem si agganci del tutto;
- una disabilita il power management runtime del PCIe su questa scheda. Senza,
  la porta sospende il modem in D3hot e il link MHI muore in una cascata di
  completion-timeout / AER da cui si esce solo con un reboot.

Se perdo la seconda, il modem va in crash come prima che trovassi la
soluzione. Stavolta si sono riapplicate senza conflitti — e ho
[aperto una issue per portarle a monte](https://github.com/vjt/openwrt-glinet-x3000/issues/6),
perché la soluzione giusta a lungo termine è non portarsele dietro affatto.

## L'unica trappola di build: una cache di configure stantia

La prima build è fallita — in `vim`, non nel mio codice. L'upstream aveva
aggiunto `-Wl,-z,max-page-size=4096` ai `CFLAGS`/`LDFLAGS` del target. La
maggior parte dei pacchetti OpenWrt rilancia `configure` a ogni build e non se
ne accorge, ma `vim` si tiene il suo `config.cache` di autotools, e con i flag
cambiati sotto, `configure` si è arreso:

```
configure: error: changes in the environment can compromise the build
configure: error: run 'make distclean' and/or 'rm auto/config.cache'
```

Il mio container di build aveva ancora una `build_dir` dall'era di r5, quindi
la cache stantia era lì. Un `make clean` ripulisce la `build_dir` del target e
costringe ogni pacchetto a riconfigurarsi con i nuovi flag — la toolchain
resta, quindi costa tempo ma non una ricostruzione da zero. Se un singolo
pacchetto fallisce al `configure` con quel messaggio dopo un rebase, non
cercare tra le tue patch; pulisci l'albero.

## Flashare senza perdere la scatola

Scrivere il firmware riavvia il dispositivo, e se il modem non torna serve un
recupero fisico. La sequenza che ho usato:

1. Tirare giù un backup completo della config **dal** dispositivo per primo,
   così che un reflash all'immagine precedente possa ripristinare lo stato.
2. `sysupgrade --test` dell'immagine sul dispositivo, per verificare metadati e
   compatibilità della scheda prima di toccare la flash.
3. Flashare con un comando SSH **sincrono**, non staccato. `sysupgrade` passa
   la scrittura a un secondo stage via ubus; se stacchi la sessione quella
   chiamata diventa un no-op silenzioso. Lascia che la connessione si blocchi —
   cade al reboot, ed è normale.
4. Mantenere la config nell'upgrade, poi aspettare e guardare.

È tornato su in circa settanta secondi.

## La radio è sopravvissuta?

Un salto di kernel tocca ogni driver del modem — MHI, MBIM, USB — quindi
l'unico controllo vero sono i numeri, non il log di boot. Il modem si è
ri-enumerato su PCIe/MHI in modo pulito e `dmesg` mostrava il link salire senza
cascata AER — la patch sul runtime-PM che si guadagna il posto attraverso il
salto. ModemManager lo aveva `connected` su LTE+5G-NSA entro una decina di
secondi.

Poi ho confrontato la telemetria prima e dopo. La portante n78 NSA — tutto il
senso di questa scatola — era statisticamente identica: RSRP intorno ai −95
dBm, SINR intorno agli 11.8 dB, NR agganciato il 100% del tempo su entrambi i
lati.

Una cosa mi ha quasi ingannato: la finestra post-flash mostrava *più* carrier
aggregation LTE, il che sembra un miglioramento. Non lo è — una settimana di
storia mostrava che il campione pre-flash era capitato in un momento a portante
singola, mentre la scatola normalmente aggrega da una a tre portanti LTE a
seconda della rete. La profondità di CA è guidata dalla rete, non dal firmware.
Il verdetto onesto è nessun cambiamento — esattamente ciò che un puro
allineamento a monte dovrebbe produrre. Ho schedulato un follow-up su una
finestra intera di 24 ore per confermare; 35 minuti dopo un reboot non sono un
verdetto sulla radio.

## Cosa si è portato dietro

Poiché i miei feed custom seguono i rispettivi branch principali, alcuni dei
miei strumenti sono avanzati con la build — in particolare
[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools) è passato da
1.4.0 a 1.6.0, tirandosi dietro il generatore di dashboard Grafana e il lavoro
sulle statistiche di questo ciclo. Scelta deliberata: voglio il mio codice
aggiornato a ogni build, anche quando l'upstream non si è mosso.

`jeeves-r6` è sulla
[pagina delle release](https://github.com/vjt/openwrt-glinet-x3000/releases).
Tieni da parte l'immagine precedente per il rollback — e ragiona sulla tua
situazione prima di flashare. Io potevo prendermi il rischio del flash da
remoto perché Jeeves è il mio percorso di *backup* ed ero sul posto; se quella
scatola è l'unica cosa tra te e internet, trattala di conseguenza.
