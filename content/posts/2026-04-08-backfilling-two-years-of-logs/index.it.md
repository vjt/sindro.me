---
title: "Backfill di due anni di log: observability enterprise-grade su un Raspberry Pi"
date: 2026-04-08
tags: [ai-generated, sysadmin, observability, projects]
description: "Come ho riprocessato 25 milioni di entry di log attraverso una pipeline completa di enrichment — GeoIP, ASN, reverse DNS — su un Raspberry Pi 5, con Claude a scrivere il codice."
---

![BSD daemon con la telemetria che fluisce attraverso una pipeline di enrichment verso VictoriaLogs](/posts/2026-04-08-backfilling-two-years-of-logs/cover.jpg)

Ho un server FreeBSD che si chiama m42 e gira da anni. Gestisce email (Postfix + Dovecot + Rspamd), web (nginx con una dozzina di vhost), firewall (pf), e tutti i soliti servizi. Genera migliaia di entry di log al giorno su quattro formati distinti: BSD syslog, fail2ban, pf packet filter, e nginx access/error.

Ho anche scritto [pfasciilogd](/posts/2023-08-17-pfasciilogd-link-pf-and-fail2ban/) nel 2023 per convertire i log binari di pf in testo ASCII così che fail2ban potesse parsarli — un pezzo fondamentale che oggi alimenta di telemetria strutturata del firewall l'intera pipeline.

Ho anche due anni di backup mensili conservati in snapshot [restic](https://restic.net/). Circa 25 milioni di righe di log, lì ferme. Una miniera di telemetria di sicurezza, pattern di traffico, e dati sugli attacchi — completamente non indicizzata e non ricercabile.

Ho costruito uno stack completo di observability su un Raspberry Pi 5 a casa — [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) per lo storage, [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) per il processing, [Grafana](https://grafana.com/) per la visualizzazione — e poi ho fatto il backfill di ognuna di quei 25 milioni di entry attraverso la stessa identica pipeline che processa i dati live. Con enrichment completo: geolocalizzazione GeoIP, identificazione ASN, e risoluzione DNS inversa per ogni indirizzo IP.

Questo è log management di livello enterprise. Che gira su un single-board computer da 80€. Nel mio salotto.

## Perché i backfill sono difficili (e di solito vengono saltati)

Siamo onesti: nessuno fa i backfill. Sono i broccoli del lavoro operativo. Sai che dovresti, ma il rapporto sforzo/beneficio sembra pessimo.

Il problema è che un backfill non è semplicemente "carica i vecchi dati." La tua pipeline si è evoluta. Le regole di parsing che hai scritto sei mesi fa non corrispondono ai processori di oggi. L'enrichment che hai aggiunto la settimana scorsa non esiste nei tuoi vecchi script di backfill. Ti ritrovi con due classi di dati: entry live ricche e entry storiche impoverite.

L'approccio ingenuo — scrivere script Python che replicano la logica della pipeline — funziona inizialmente. L'ho fatto. Due volte. Produceva dati che sembravano corretti ma erano sottilmente sbagliati: nomi di campi diversi, enrichment mancanti, comportamento di parsing differente. Ogni volta che aggiungevo un nuovo processore alla pipeline live, gli script di backfill si allontanavano ulteriormente dalla realtà.

## L'intuizione architetturale: replay, non riscrittura

La soluzione era imbarazzantemente semplice: **smettere di duplicare la pipeline in Python e semplicemente rieseguire i log grezzi attraverso quella vera.**

La pipeline live funziona così:

```
m42 (syslog-ng) → TCP:514 → Telegraf → Starlark → GeoIP → Reverse DNS → VictoriaLogs
```

syslog-ng su m42 avvolge ogni riga di log in un envelope [RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424) e la spedisce via TCP con un buffer affidabile su disco. Telegraf la riceve e la passa attraverso una catena di processori:

1. **Processori Starlark** (ordine 1) — quattro script separati che estraggono campi strutturati da ogni tipo di log: le regole del firewall pf vengono parsate in azione/direzione/IP/porte/protocollo, le entry fail2ban ottengono jail/azione/IP, nginx ottiene vhost/tipo/IP client, postfix ottiene ID coda e indirizzi email
2. **Enricher GeoIP** (ordine 2) — un binario Go custom che gira come processore execd, mappa ogni IP pubblico a paese, città, coordinate, ASN e organizzazione usando i database GeoLite2 di MaxMind
3. **Reverse DNS** (ordine 3) — lookup PTR per ogni IP estratto, risolti attraverso un server DNS [Technitium](https://technitium.com/dns/) locale con caching aggressivo

Lo script di backfill è diventato un **log replayer**: legge i file grezzi, avvolge ogni riga in un envelope RFC 5424 con il timestamp e i metadati corretti, e lo invia a Telegraf via TCP. Tutto qui. Zero parsing del contenuto. Lo script è passato da ~700 righe di Python (con librerie GeoIP, estrattori regex, posting HTTP) a ~350 righe che non fanno altro che costruire envelope e inviare via TCP.

```python
def rfc5424(pri: int, ts: str, appname: str, procid: str, msg: str) -> str:
    return f"<{pri}>1 {ts} {HOSTNAME} {appname} {procid} - - {msg}"

def send_rfc5424(sock: socket.socket, msg: str) -> None:
    encoded = msg.encode("utf-8")
    frame = f"{len(encoded)} ".encode("ascii") + encoded
    sock.sendall(frame)
```

Il backpressure TCP gestisce il controllo di flusso — quando Telegraf non riesce a stare al passo (soprattutto per i lookup DNS), il send TCP si blocca. Nessuna perdita di dati, nessuna complessità di buffering, nessuna logica di rate limiting. Il protocollo fa il lavoro.

## La pipeline di enrichment

Ecco come appare una singola entry del firewall pf dopo il processing completo:

```
Riga di log grezza:
  2024-05-29T22:00:08.006704+02:00 rule 1/0(match): block in on vtnet0:
  141.98.7.190.56034 > 46.38.233.77.8728: Flags [S]

Dopo l'enrichment:
  pf_action     = block
  pf_direction  = in
  pf_interface  = vtnet0
  pf_proto      = tcp
  pf_src_ip     = 141.98.7.190
  pf_src_port   = 56034
  pf_dst_ip     = 46.38.233.77
  pf_dst_port   = 8728
  geo_country   = DE
  geo_city      = Frankfurt am Main
  asn           = AS215439
  as_org        = Play2go International Limited
```

Ogni tipo di log riceve questo trattamento. Una entry postfix ottiene `mail_client_ip`, `mail_client_host` (reverse DNS), geolocalizzazione e ASN per il server di posta che si connette. Una entry fail2ban ottiene `f2b_jail`, `f2b_action`, `f2b_ip` con geo e DNS completi. Una entry nginx ottiene `vhost`, `client_ip`, `client_host`, e geo. Tutto ricercabile, filtrabile e visualizzabile in Grafana.

I processori Starlark gestiscono sia IPv4 che IPv6 nativamente — m42 è dual-stack, e una quantità sorprendente di traffico (specialmente tentativi di brute-force SSH) arriva su IPv6.

## Cosa ha reso possibile tutto questo

Questo progetto non esisterebbe senza l'assistenza dell'AI. Non avrei avuto il tempo di costruire sia una pipeline di enrichment robusta SIA un sistema completo di backfill. Uno o l'altro, forse. Entrambi? Impossibile.

Ma — e questo è il punto cruciale — **l'AI non ha costruito questo dal nulla.** Il motivo per cui Claude è stato così efficace è che l'infrastruttura era già pulita:

- **Snapshot restic** — due anni di backup mensili del server, strutturati in modo consistente, pronti per essere letti
- **Docker con networking macvlan** — ogni servizio ha il proprio IP su una VLAN dedicata, isolamento pulito
- **Telegraf già funzionante** — la pipeline dei processori (input, processori, output) era già strutturata e documentata
- **VictoriaLogs già in ingestion** — i log live fluivano, lo schema era collaudato
- **Un CLAUDE.md ben mantenuto** — principi di ingegneria che hanno tenuto l'AI focalizzata: "leggi prima di scrivere," "correggi le cause radice non i sintomi," "non inventare mai spiegazioni"

L'infrastruttura pulita si compone. Ogni scorciatoia che non hai preso, ogni backup che hai configurato, ogni pezzo di documentazione che hai scritto — tutto diventa leva quando hai bisogno di costruire qualcosa di ambizioso sopra. L'AI amplifica quello che c'è già. Se le fondamenta sono solide, l'amplificazione è straordinaria. Se le fondamenta sono caos, l'AI amplifica il caos più velocemente.

## Una nota sull'iterazione

Ecco cosa farei diversamente: **dedicare ancora più tempo alla progettazione prima di scrivere codice.**

È incredibilmente facile ottenere da Claude un proof of concept funzionante. Descrivi quello che vuoi, e 30 secondi dopo hai codice che gira. La scarica di dopamina è reale. Ma per task come il backfill — dove l'esecuzione richiede ore e non puoi facilmente annullare — un design sbagliato significa rifare l'intera esecuzione. Più volte.

Ho attraversato diverse iterazioni di questo backfill. Ogni volta scoprivo qualcosa che la pipeline gestiva ma che gli script di backfill no — supporto IPv6, reverse DNS, un processore Starlark che avevo dimenticato. Ogni ripetizione significava: cancellare 25 milioni di entry, aspettare, rieseguire per 8+ ore, verificare.

La lezione: il costo di un'ora in più di progettazione è triviale rispetto a un backfill di 8 ore che devi buttare via. Fai il tuo brainstorming. Audita campo per campo. Confronta le entry live con quello che produce il tuo strumento. Poi — e solo poi — schiaccia il grilletto.

## I numeri

- **25 milioni di entry** su quattro formati di log (BSD syslog, fail2ban, pf, nginx)
- **Due anni** di snapshot restic (2024-05 fino a 2026-04)
- **~350 righe di Python** per lo script di replay (dalle ~700 righe che duplicavano la logica della pipeline)
- **Quattro processori Starlark**, un enricher GeoIP in Go, un resolver reverse DNS
- **~8 ore** per rieseguire tutto attraverso la pipeline completa
- Gira su un **Raspberry Pi 5** (4 core, 16GB RAM, NVMe) nel mio salotto

Il Pi ha raggiunto un load average di 19 su 4 core durante il backfill — lavorava duro, ma ha retto. La pipeline live ha continuato a girare in parallelo per tutta la durata. Nessuna entry persa, nessun servizio interrotto.

## Provalo a casa

L'intero stack è aperto e riproducibile:

- [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) — storage di log gratuito, singolo binario, con LogsQL
- [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) — processore di metriche e log basato su plugin
- [Grafana](https://grafana.com/) — dashboard e alerting
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — database di geolocalizzazione IP gratuiti
- [restic](https://restic.net/) — backup crittografati e deduplicati
- [syslog-ng](https://www.syslog-ng.com/) — trasporto log affidabile con buffering su disco
- [Claude Code](https://claude.ai/code) — l'AI che ha reso fattibile costruire tutto questo nel tempo che avevo

Se hai backup di server in giro, i tuoi log storici sono lì dentro. E se hai una pipeline che processa dati live, hai già tutto quello che ti serve per arricchirli. Non scrivere un tool di backfill separato — riesegui attraverso quello vero.

I tuoi dati passati meritano lo stesso trattamento dei tuoi dati live. È tutto segnale.
