---
title: "Tre bug di Telegraf e 25 milioni di righe di log"
date: 2026-04-08
tags: [ai-generated, sysadmin, observability, projects, freebsd, nginx]
description: "Come un backfill di syslog attraverso Telegraf su un Raspberry Pi ha scovato tre bug upstream — una tempesta di retry DNS, una modalità di serializzazione mancante, e un deadlock nelle pipe."
---

![BSD daemon con la telemetria che fluisce attraverso una pipeline di enrichment verso VictoriaLogs](/posts/2026-04-08-backfilling-two-years-of-logs/cover.jpg)

Ho un server FreeBSD che si chiama m42 e gira da anni. Email, web, firewall, i soliti. Due anni e mezzo di backup mensili [restic](https://restic.net/) negli snapshot — circa 25 milioni di righe syslog su quattro formati: BSD syslog, fail2ban, pf packet filter, e nginx. Una miniera d'oro di telemetria di sicurezza, completamente non indicizzata e non ricercabile.

Ho costruito uno stack di observability su un Raspberry Pi 5 a casa — [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) per lo storage, [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) per il processing, [Grafana](https://grafana.com/) per la visualizzazione — e ho deciso di fare il backfill di ognuna di quei 25 milioni di entry attraverso la stessa identica pipeline di enrichment che processa i dati live. Geolocalizzazione GeoIP, identificazione ASN, reverse DNS per ogni indirizzo IP.

Il backfill in sé era semplice. Quello che non era semplice: i tre bug che ha scovato nelle viscere di Telegraf. Il genere di bug che emerge solo sotto carico sostenuto. Il genere che nessuno incontra perché nessuno fa questa roba.

## L'architettura: replay, non riscrittura

L'approccio ingenuo è scrivere script Python che replicano la pipeline — parsare i log, arricchire con GeoIP, POST al log store. L'ho fatto. Due volte. Ogni volta gli script divergevano dalla pipeline live: nomi di campi diversi, enrichment mancanti, inconsistenze nel parsing tra Starlark e le regex Python.

La soluzione era imbarazzantemente semplice: **smettere di duplicare la pipeline e rieseguire i log grezzi attraverso quella vera.**

La pipeline live:

```
m42 (syslog-ng) → TCP:514 → Telegraf → Starlark → GeoIP → Reverse DNS → VictoriaLogs
```

Lo script di backfill è diventato un log replayer: legge i file grezzi, avvolge ogni riga in un envelope [RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424) con il timestamp corretto, la invia a Telegraf via TCP con [octet-counting framing](https://datatracker.ietf.org/doc/html/rfc6587#section-3.4.1). Fine. Zero parsing del contenuto. La pipeline di enrichment gestisce tutto in modo identico ai dati live.

```python
def send_rfc5424(sock, msg):
    encoded = msg.encode("utf-8")
    frame = f"{len(encoded)} ".encode("ascii") + encoded
    sock.sendall(frame)
```

Il backpressure TCP gestisce il controllo di flusso — quando Telegraf non riesce a stare al passo, `sendall()` si blocca. Nessuna complessità di buffering, nessuna logica di rate limiting, nessuna perdita di dati. Il protocollo fa il lavoro.

In teoria, almeno. In pratica, abbiamo trovato tre bug.

## Bug 1: La tempesta di retry DNS (negative cache del reverse_dns)

La prima cosa che è successa quando abbiamo iniziato a pompare 8.000 righe al secondo è che Telegraf si è inchiodato. Throughput zero. Ogni worker bloccato.

Il processore `reverse_dns` fa lookup PTR per ogni indirizzo IP in ogni riga di log. La maggior parte degli IP esterni — scanner bot, attaccanti brute-force, rumore casuale di internet — non ha record PTR. Il server DNS restituisce NXDOMAIN immediatamente. La risposta di Telegraf stock: **cancellare la entry dalla cache e riprovare la prossima volta.** Ogni. Singola. Volta.

Con 25 milioni di righe di log contenenti migliaia di IP unici irrisolvibili, questo crea una tempesta infinita di retry. Tutti i 200 worker DNS permanentemente saturi a ritentare IP che non si risolveranno mai. L'`Enqueue()` bloccante nel worker pool parallelo propaga il backpressure attraverso l'intera pipeline. Nulla si muove.

Il fix: **negative caching.** Quando un lookup PTR fallisce, cacheare il risultato negativo per un `negative_cache_ttl` configurabile (default 15 minuti) invece di cancellare la entry. I worker restano occupati per qualche minuto mentre la cache si riscalda, poi il throughput si stabilizza man mano che le negative cachate impediscono i retry.

```go
// Prima (stock): cancella al fallimento → retry infiniti
delete(d.cache, lookup.ip)

// Dopo (patchato): cache il risultato negativo → riprova dopo il TTL
lookup.completed = true
lookup.domains = nil
lookup.expiresAt = time.Now().Add(d.negativeTTL)
d.lockedSaveToCache(lookup)
```

L'evidenza era drammatica. L'abbiamo verificata durante il backfill campionando gli errori DNS a 30 secondi di distanza:

- **T=0**: 13 IP unici che fallivano (primi lookup, cache fredda)
- **T=30s**: **zero** fallimenti — la negative cache serviva risultati cachedsilenziosamente

Ogni nuovo IP fallisce esattamente una volta, viene cachato, e non viene più ritentato per 15 minuti. Telegraf stock martellerebbe gli stessi IP per sempre.

## Bug 2: Batching NDJSON (1000x meno richieste HTTP)

L'endpoint `/insert/jsonline` di VictoriaLogs si aspetta [JSON delimitato da newline](https://jsonlines.org/) — un oggetto JSON per riga. Il serializzatore JSON di Telegraf ha un metodo `SerializeBatch()` che wrappa le metriche in `{"metrics":[...]}`, che VictoriaLogs non capisce. Quindi ogni metrica veniva inviata come POST HTTP separato.

Con 1.000 metriche per flush (il default di `metric_batch_size`), sono 1.000 round-trip HTTP per ciclo di flush invece di uno. Su TLS. Verso localhost, ma comunque.

Abbiamo aggiunto un'opzione `json_newline_batch` — quando abilitata, `SerializeBatch()` concatena gli output individuali di `Serialize()` invece di wrapparli in un array:

```go
func (s *Serializer) SerializeBatch(metrics []telegraf.Metric) ([]byte, error) {
    if s.NewlineBatch {
        var buf []byte
        for _, m := range metrics {
            b, err := s.Serialize(m)
            if err != nil { return nil, err }
            buf = append(buf, b...)
        }
        return buf, nil
    }
    // ... logica esistente {"metrics":[...]}
}
```

Dieci righe di codice, 1000x meno richieste HTTP. Il genere di miglioramento che ti fa chiedere perché non esistesse già.

## Bug 3: Il deadlock nelle pipe (input TCP stream)

Questo era il più bastardo. Dopo aver girato liscio a 8K/s per circa cinque minuti, la pipeline si fermava silenziosamente. Nessun errore. Nessun crash. Semplicemente... throughput zero. Il backpressure TCP entrava in gioco, il sender si bloccava su `sendall()`, e tutto si congelava.

Il goroutine dump raccontava la storia. In `plugins/common/socket/stream.go`, ogni connessione TCP crea una `io.Pipe()` — il writer legge dal socket TCP, il reader alimenta il parser:

```go
reader, writer := io.Pipe()
defer writer.Close()
go onConnection(src, reader)  // ← il problema

for {
    n, err := decoder.Read(buf)
    // ...
    writer.Write(buf[:n])  // si blocca per sempre quando il reader esce
}
```

Il callback `onConnection` gira in una goroutine. Quando esce — per qualsiasi motivo — non chiude il reader della pipe. La chiamata `Write()` del writer si blocca per sempre in attesa di un reader che non consumerà mai. Il `defer writer.Close()` non scatta perché la funzione è bloccata alla `Write()`. Classico deadlock da resource leak.

Il fix è una riga:

```go
go func() {
    defer reader.Close()
    onConnection(src, reader)
}()
```

Nessuno l'ha mai incontrato perché si manifesta solo sotto input TCP ad alto volume sostenuto. Il syslog normale a 1 msg/sec non triggera mai la race — il callback `onConnection` non esce a metà stream. Servono migliaia di messaggi al secondo per minuti per incapparci.

## La pipeline di enrichment

Ecco cosa rende l'approccio replay-attraverso-Telegraf degno dello sforzo. Una singola entry del firewall pf passa da questo:

```
2024-05-29T22:00:08 rule 1/0(match): block in on vtnet0:
  141.98.7.190.56034 > 46.38.233.77.8728: Flags [S]
```

A questo:

```
pf_action     = block
pf_direction  = in
pf_src_ip     = 141.98.7.190
pf_dst_port   = 8728
pf_src_host   = (negative cachato — nessun PTR)
geo_country   = DE
geo_city      = Frankfurt am Main
asn           = AS215439
as_org        = Play2go International Limited
```

Ogni tipo di log riceve questo trattamento. Le entry Postfix ottengono geolocalizzazione del mail client e reverse DNS. Fail2ban ottiene jail/azione/IP con geo completa. Nginx ottiene vhost, IP client, e ASN. Tutto ricercabile e filtrabile in Grafana. Sia IPv4 che IPv6 — m42 è dual-stack, e una quantità sorprendente di traffico brute-force arriva su IPv6.

I processori Starlark gestiscono il parsing (quattro script, uno per formato di log). Un binario Go custom fa l'enrichment GeoIP tramite i database GeoLite2 di MaxMind. Il processore reverse DNS — ora con negative caching — fa i lookup PTR attraverso un server DNS [Technitium](https://technitium.com/dns/) locale.

## I numeri

- **25,3 milioni di entry** su quattro formati di log (BSD syslog, fail2ban, pf, nginx)
- **34 file mensili**, da luglio 2023 ad aprile 2026
- **~8.000 righe/sec** di throughput sostenuto (DNS-bound con 200 worker)
- **Zero perdita di dati** — backpressure TCP, zero drop dal buffer
- **~1 ora** di tempo totale di replay
- **Tre bug upstream** trovati e fixati
- Gira su un **Raspberry Pi 5** (4 core, 16GB RAM, NVMe) nel mio salotto

## Cosa ha reso possibile tutto questo

Questo progetto non esisterebbe senza l'assistenza dell'AI. Non avrei avuto il tempo di costruire una pipeline di enrichment robusta E debuggare tre bug nelle viscere di Telegraf E scrivere un sistema completo di backfill. Claude ha fatto il lavoro pesante sul codice mentre io prendevo le decisioni architetturali e beccavo gli errori di design.

Ma — e questo è il punto cruciale — **l'AI non ha costruito questo dal nulla.** Il motivo per cui Claude è stato così efficace è che l'infrastruttura era già pulita:

- **Snapshot restic** — due anni e mezzo di backup mensili del server, strutturati in modo consistente
- **Docker con networking macvlan** — ogni servizio ha il proprio IP su una VLAN dedicata
- **Telegraf già funzionante** — la pipeline dei processori era strutturata e documentata
- **VictoriaLogs già in ingestion** — log live che fluivano, schema collaudato
- **Un CLAUDE.md ben mantenuto** — principi di ingegneria che hanno tenuto l'AI focalizzata

L'infrastruttura pulita si compone. Ogni scorciatoia che non hai preso, ogni backup che hai configurato, ogni pezzo di documentazione che hai scritto — tutto diventa leva quando hai bisogno di costruire qualcosa di ambizioso sopra. L'AI amplifica quello che c'è già. Se le fondamenta sono solide, l'amplificazione è straordinaria.

## Una nota sull'iterazione

Ecco cosa farei diversamente: **dedicare ancora più tempo alla progettazione prima di scrivere codice.**

È incredibilmente facile ottenere da Claude un proof of concept funzionante. Descrivi quello che vuoi, e 30 secondi dopo hai codice che gira. La scarica di dopamina è reale. Ma per task come il backfill — dove l'esecuzione richiede ore e non puoi facilmente annullare — un design sbagliato significa rifare l'intera esecuzione.

Ho attraversato diverse iterazioni. Ogni volta scoprivo qualcosa che la pipeline gestiva ma che gli script di backfill no — supporto IPv6, interazione col reverse DNS, un processore Starlark che avevo dimenticato. Ogni ripetizione significava: cancellare milioni di entry, aspettare, rieseguire, verificare. L'iterazione finale — rieseguire RFC5424 grezzi attraverso la pipeline vera — è quella che avrebbe dovuto essere la prima.

Il costo di un'ora in più di progettazione è triviale rispetto a un backfill che devi buttare via.

## Provalo a casa

L'intero stack è aperto e riproducibile:

- [VictoriaLogs](https://docs.victoriametrics.com/victorialogs/) — storage di log gratuito, singolo binario, con LogsQL
- [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) — processore di metriche e log basato su plugin
- [Grafana](https://grafana.com/) — dashboard e alerting
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — database di geolocalizzazione IP gratuiti
- [restic](https://restic.net/) — backup crittografati e deduplicati
- [Claude Code](https://claude.ai/code) — l'AI che ha reso fattibile costruire tutto questo nel tempo che avevo

Se hai backup di server in giro, i tuoi log storici sono lì dentro. E se hai una pipeline che processa dati live, hai già tutto quello che ti serve per arricchirli. Non scrivere un tool di backfill separato — riesegui attraverso quello vero.

I tuoi dati passati meritano lo stesso trattamento dei tuoi dati live. È tutto segnale.
