---
title: "5G come backup della fibra: non perdere mai più una riunione"
date: 2026-01-31
tags: [ai-generated, iot, networking, openwrt, python, sysadmin]
description: "Strumenti Python open source per modem Quectel 5G su OpenWRT. Monitoraggio del segnale in tempo reale con feedback audio per il puntamento dell'antenna. Licenza MIT."
---

![Antenna direzionale su un muro puntata verso una torre cellulare, cavo in fibra che si spezza da un lato mentre le onde 5G colmano il divario](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/cover.jpg)

Un paio di mesi fa, la fibra è andata giù. Come da primo corollario di Murphy, è successo nel momento peggiore in assoluto: subito prima di una riunione cruciale con un'azienda partner. Mi sono ritrovato a saltare freneticamente tra l'AP di un vicino lontano e l'hotspot del telefono, ma entrambi facevano schifo. Parliamo di 200ms di RTT e 15% di packet loss. Mi stavo scusando a profusione mentre il mio feed video si trasformava in uno slideshow del 1998; nessuno capiva una parola di quello che dicevo. Ho finito per spegnere il video e stare zitto. Opportunità persa. **Mai. Più.**

Così sono andato in modalità paranoica totale e ho costruito un setup di backup 5G serio.

## L'hardware

- [GL.iNet X-3000](https://www.gl-inet.com/products/gl-x3000/) con modem Quectel RM520N-GL
- [Poynting XPOL-24](https://poynting.tech/antennas/xpol-24/) antenna direzionale montata sul muro fuori dal mio ufficio

Il segnale 5G qui è inesistente, quindi ho dovuto usare l'artiglieria pesante. La Poynting è una bestia. 11 dBi di guadagno, vero MIMO 4x4, cross-polarizzata, stagna. Puntala verso la torre più vicina e all'improvviso il SINR salta da "meh" a "porco dio!".

Ma puntare un'antenna direzionale senza feedback visivo è doloroso. In pratica giri in tondo, aggiorni una web UI, bestemmi guardando il cielo.

## Il software

Ho scritto un set di strumenti per risolvere il problema: [quectel-5g-tools](https://github.com/vjt/quectel-5g-tools).

`5g-info` scarica tutto quello che il tuo modem sa in un formato leggibile:

![output di 5g-info](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/5g-info.png)

`5g-monitor` è una TUI ncurses che si aggiorna in tempo reale e -- qui viene il bello -- **emette beep in base al SINR**. Qualità del segnale più alta = più beep. Punta l'antenna, ascolta i beep, stringi i bulloni. Fatto.

![TUI di 5g-monitor](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/5g-monitor.png)

È come un metal detector, ma per il 5G.

## Note tecniche

Il modem parla comandi AT su `/dev/ttyUSB2`. Gli strumenti parsano le risposte da `AT+QENG`, `AT+QCAINFO`, e compagni per estrarre le info della cella servente, lo stato della carrier aggregation, e le celle vicine.

Tutto gira su OpenWRT. Installa le dipendenze con `opkg install python3-pyserial python3-toml python3-ncurses`, clona il repo, ed esegui `./bin/5g-monitor`. Niente compilazione, niente container, niente cazzate.

C'è anche `force-bands` se vuoi bloccare il modem su bande LTE/NR specifiche (utile quando il modem si ostina a connettersi a una torre lontana con RSRP migliore ma throughput peggiore).

## Risultato

Il mio backup 5G ora va a 300+ Mbps in download, 50+ in upload. Quando la fibra muore, il mio router fa failover automaticamente grazie a `mwan3`. Le riunioni continuano. I clienti non se ne accorgono. La pressione sanguigna resta normale.

*Aggiornamento, aprile 2026: l'X3000 nel frattempo è migrato dal firmware GL.iNet stock a OpenWrt 25.12 vanilla — la storia completa in [GL-X3000 su OpenWRT 25.12 vanilla: tutto funzionante](/it/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/). E `mwan3` si è rivelato avere una sua patologia sottile insieme a banIP — postmortem in [Come banIP ha distrutto il throughput del mio WireGuard da febbraio](/it/posts/2026-04-07-banip-icmp-mwan3/).*

Il codice è con licenza MIT e vive su [github.com/vjt/quectel-5g-tools](https://github.com/vjt/quectel-5g-tools). Le PR sono benvenute.

## Immagini

La Poynting subito dopo l'unboxing e il montaggio sul treppiede di test:

![Test Poynting](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-testing.jpg)

L'X3000 montato a parete un paio di giorni dopo il momento "porco dio!" dei 300Mbit in download durante i test

![X3000 montato a parete](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/x3000-wall-mount.jpg)

La Poynting montata a parete nel suo setup (semi) definitivo. Il mio DIY più grande di sempre -- non avevo mai trapanato il cemento stando su una scala di 2m su un terrazzo al primo piano :-D

![Poynting montata a parete](/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/xpol-24-wall-mount.jpg)

Buon divertimento!
