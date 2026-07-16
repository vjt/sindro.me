---
title: "GL-X3000 r6: allinearsi a monte senza rompere il modem"
date: 2026-07-16
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "Rebase della mia immagine GL-X3000 su 155 commit più recenti di OpenWrt 25.12, l'unica trappola di build che mi ha morso, e come ho flashato un uplink 5G vivo dimostrando che la radio non è regredita."
---

**TL;DR:** ho ricostruito Jeeves — [il mio uplink 5G di backup su GL-iNet
GL-X3000](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/) — sulla
versione più recente di OpenWrt 25.12, portando il kernel da 6.12.85 a
6.12.94. I miei 20 commit di abilitazione hardware si sono riapplicati puliti
su 155 commit di upstream. Una trappola di build mi è costata una
ricostruzione. Poi ho flashato il router-modem in funzione e ho controllato
la telemetria per confermare che la parte 5G fosse tornata esattamente
com'era. L'immagine è `jeeves-r6`, sulla
[pagina delle release](https://github.com/vjt/openwrt-glinet-x3000/releases).

<!--more-->

## Perché ricostruire

La [migrazione di aprile](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
ha portato Jeeves su OpenWrt 25.12 vanilla con il modem Quectel RM520N-GL
pienamente funzionante. Da allora l'upstream si è mosso: 155 commit, un salto
di nove point-release del kernel (6.12.85 → 6.12.94) e il solito ricambio di
fix di sicurezza e aggiornamenti di pacchetti. Niente di tutto ciò cambia
*cosa fa* Jeeves — è pura igiene. Ma l'igiene su un dispositivo con due patch
di kernel fuori dall'albero non è mai del tutto gratis.

Il mio stack sono 20 commit sopra l'upstream. Due sono patch di kernel, e
sono quelle che sorveglio a ogni rebase:

- una insegna al driver MHI PCI generico a rivendicare l'RM520N-GL tramite il
  suo subvendor ID Qualcomm, così che il modem si agganci del tutto;
- una disabilita il power management runtime del PCIe su questa scheda. Senza,
  la porta sospende il modem in D3hot e il link MHI muore in una cascata di
  completion-timeout / AER da cui si esce solo con un reboot completo.

Se perdo la seconda, il modem va in crash come faceva prima che trovassi la
soluzione. Quindi la regola del rebase è semplice: quelle due devono
sopravvivere, intatte, o la build non parte. Stavolta si sono riapplicate
senza conflitti — ma ho anche
[aperto una issue per portarle a monte](https://github.com/vjt/openwrt-glinet-x3000/issues/6),
perché la soluzione corretta a lungo termine è non portarsele dietro affatto.

## L'unica trappola di build: una cache di configure stantia

La prima build è fallita. Non nel mio codice — in `vim`, tra tutti.

L'upstream aveva cambiato i flag del compilatore per il target (avevano
aggiunto `-Wl,-z,max-page-size=4096` ai `CFLAGS`/`LDFLAGS` globali). La
maggior parte dei pacchetti OpenWrt rilancia `configure` da zero a ogni
build, quindi non se ne accorge. Ma `vim` si tiene il suo `config.cache` di
autotools tra una build e l'altra, e quando i flag sono cambiati sotto,
`configure` si è rifiutato di proseguire:

```
configure: error: changes in the environment can compromise the build
configure: error: run 'make distclean' and/or 'rm auto/config.cache'
```

Il mio container di build aveva una `build_dir` rimasta dall'era di r5, e la
cache stantia era lì. La soluzione è un `make clean` che ripulisce la
`build_dir` del target e costringe ogni pacchetto a riconfigurarsi con i nuovi
flag — la toolchain resta, quindi costa tempo ma non una ricostruzione da
zero. Se fai un rebase attraverso un cambio di flag e ti ritrovi un singolo
pacchetto che fallisce al `configure` con quel messaggio, ecco perché. Non
metterti a cercare tra le tue patch; pulisci l'albero.

## Flashare un uplink vivo senza perderlo

Jeeves è un gateway di *backup*, non quello principale, ed ero sul posto —
che è l'unico motivo per cui l'ho flashato da remoto. Scrivere il firmware
riavvia il dispositivo, e se il modem non fosse tornato avrei avuto bisogno di
un recupero fisico. La sequenza che ho usato, in ordine:

1. Tirare giù un backup completo della config **dal** dispositivo per primo,
   così che un reflash a r5 possa ripristinare lo stato.
2. `sysupgrade --test` dell'immagine sul dispositivo, per confermare metadati
   e compatibilità della scheda prima di toccare la flash.
3. Flashare con un comando SSH **sincrono** — non in background/staccato.
   `sysupgrade` passa la scrittura vera a un secondo stage via ubus, e se
   stacchi la sessione quella chiamata diventa silenziosamente un no-op e non
   viene scritto nulla. Lascia che la connessione si blocchi; cade al reboot,
   ed è normale.
4. Mantenere la config nell'upgrade (stessa linea di config), poi aspettare e
   guardare.

È tornato su in circa settanta secondi.

## La radio è sopravvissuta?

Questa è la parte che conta davvero. Un salto di kernel tocca ogni driver del
modem — MHI, il percorso di controllo MBIM, l'USB — e l'unico modo onesto per
sapere che non ha fatto regredire la radio è guardare i numeri, non il log di
boot.

Il modem si è ri-enumerato su PCIe/MHI in modo pulito, e `dmesg` mostrava il
link PCIe che saliva **senza cascata AER** — la patch sul runtime-PM che si
guadagna il posto attraverso il salto di kernel. ModemManager aveva il modem
`connected` su LTE+5G-NSA entro una decina di secondi dall'avvio.

Poi ho confrontato la telemetria prima e dopo il flash. Il mio watchdog e i
collector di segnale spingono su VictoriaMetrics, quindi ho RSRP e SINR per
singola portante e una gauge di verità su "NR agganciato". La parte 5G — la
portante n78 NSA, che è tutto il senso di questa scatola — era
**statisticamente identica** attraverso il flash: RSRP intorno ai −95 dBm,
SINR intorno agli 11.8 dB, NR agganciato il 100% del tempo sia prima che dopo.

Una cosa mi ha quasi ingannato. La finestra post-flash mostrava per un attimo
*più* carrier aggregation LTE di quella pre-flash, il che sembra un
miglioramento. Non lo è — ho controllato una settimana di storia e il
campione pre-flash era semplicemente capitato in un momento a portante
singola, mentre il dispositivo normalmente aggrega da una a tre portanti LTE a
seconda di cosa la rete decide di darmi. La profondità di carrier aggregation
è guidata dalla rete, non dal firmware. Il verdetto onesto è *nessun
cambiamento*, che per un puro allineamento a monte è esattamente il risultato
che vuoi.

Per restare onesto, ho schedulato un follow-up che rilancia lo stesso
confronto su una finestra intera e omogenea di 24 ore, una volta che r6 avrà
una giornata di dati alle spalle — un controllo di 35 minuti subito dopo un
reboot non è un verdetto sulla radio.

## Cosa si è portato dietro

Poiché i miei feed di pacchetti custom seguono i rispettivi branch principali,
alcuni dei miei strumenti sono avanzati con la ricostruzione — in particolare
[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools) è passato da
1.4.0 a 1.6.0, tirandosi dietro il generatore di dashboard Grafana e il lavoro
sulle statistiche di questo ciclo. È una scelta deliberata: voglio il mio
codice aggiornato a ogni build, anche quando l'upstream stesso non si è mosso.

`jeeves-r6` è sulla
[pagina delle release](https://github.com/vjt/openwrt-glinet-x3000/releases)
se hai la stessa scatola. Come sempre: è un uplink di backup, flasha di
conseguenza, e tieni da parte l'immagine r5 per il recupero.
