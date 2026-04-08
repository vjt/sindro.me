---
title: "Come banIP ha distrutto il throughput del mio WireGuard da febbraio"
date: 2026-04-07
tags: [openwrt, wireguard, networking, debugging, mwan3, banip]
description: "Un rate limit ICMP del firewall droppava le risposte degli health check di mwan3, facendo sembrare instabile la fibra e forzando il traffico WireGuard sul backup 5G a 2 Mbps. Per due mesi."
featuredImage: "cover.jpg"
---

**TL;DR:** Se usi OpenWrt con mwan3 (failover multi-WAN) e WireGuard, aggiungi `nohostroute=1` all'interfaccia WireGuard. Senza, netifd crea un route statico per l'endpoint WireGuard all'avvio dell'interfaccia, pinnato a qualsiasi uplink sia attivo in quel momento. Per il primo corollario della Legge di Murphy, tutto ciò che può andare storto andrà storto *nel momento peggiore possibile* — quindi il link primario sarà giù esattamente quando WireGuard parte, e il route dell'endpoint resta incollato permanentemente al backup. La tua VPN resterà incollata al backup lento mentre il link primario se ne sta lì a non fare un cazzo. Non te ne accorgerai finché non dovrai trasferire qualcosa di grosso.

Oggi ho scoperto che il mio tunnel WireGuard verso un server remoto strisciava a **2 Mbps** da inizio febbraio. Il fix ha richiesto due comandi UCI. La root cause era il flag `nohostroute` mancante — più un bonus: il mio stesso firewall sabotava i miei stessi health check, facendo sembrare la fibra abbastanza inaffidabile da impedire al sistema di auto-correggersi.

Ecco la storia forense completa, perché sono ancora incazzato e meritate di imparare dalle mie sofferenze.

Prima però, un po' di contesto su come è avvenuta questa indagine. Stavo lavorando con un assistente AI (Claude Code) che ha accesso SSH alla mia infrastruttura. Questo è possibile perché ho una base solida: autenticazione SSH a chiave ovunque, DNS interno corretto (`m42`, `golem` risolvono agli indirizzi VPN giusti), mesh WireGuard tra tutti i nodi, e l'assistente si connette tramite un `ssh-agent` che gira come servizio utente systemd. Una variabile d'ambiente e l'AI raggiunge ogni macchina della mia rete — e, cosa fondamentale, può *incrociare* i dati trovati su una macchina con quelli di un'altra. Quest'indagine mi avrebbe richiesto ore di salti tra terminali. L'AI l'ha fatta in minuti, testando ipotesi metodicamente su tre macchine simultaneamente. L'investimento in SSH, DNS e VPN fatti bene ha ripagato enormemente.

## Il sintomo

Stavo facendo rsync di archivi di log da un server FreeBSD remoto (`m42`, in colocation) al mio Raspberry Pi 5 (`nowhere`) a casa. Il trasferimento era agonizzante — circa 200 KB/s con rsync, forse 1 MB/s con tar via SSH.

Ho una fibra potente a casa. Il server remoto è su una linea da 100 Mbps. Il tunnel WireGuard tra i due passa attraverso un router OpenWrt (`golem`, un GL.iNet MT-6000 con la mia build OpenWrt) che gestisce il failover dual-WAN via mwan3. Tutto configurato correttamente. Non c'è motivo per cui sia lento.

Eppure.

## Step 1: È WireGuard il collo di bottiglia?

Il mio primo istinto è stato che la crypto WireGuard saturasse la CPU del Pi. Quindi ho testato il throughput SSH grezzo, poi installato iperf3 (che si è bloccato in installazione per un prompt debconf interattivo su un sistema headless — classico). I numeri:

```
$ iperf3 -c m42 -t 5
9.01 Mbits/sec upload

$ iperf3 -c m42 -t 5 -R
1.68 Mbits/sec download
```

Upload 9 Mbps, download 1.7 Mbps. Asimmetria enorme. Ma HTTPS dall'IP pubblico dello stesso server? 28 Mbps. Il server sta bene, internet sta bene.

## Step 2: Il rabbit hole del dual-WAN

Il mio router `golem` ha due uplink:
- **Fibra** (`eth1`, metric 10) — primaria
- **5G** (`br-lan.253`, VLAN verso un modem 5G, metric 20) — backup

mwan3 mostrava tutto ok: fibra online, 100% del traffico sulla fibra. Ma il route dell'endpoint WireGuard:

```
$ ip route show 46.38.233.77
46.38.233.77 via 192.168.253.254 dev br-lan.253 proto static metric 20
```

**Pinnato sul link 5G.** Questo route statico viene creato da netifd quando l'interfaccia WireGuard si avvia — per evitare routing loop. Viene creato una volta e mai rivisto.

## Step 3: Test su entrambi gli uplink

iperf3 diretto da golem a m42: 9 Mbps upload, 2 Mbps download. LAN tra nowhere e golem: 935 Mbps. Il collo di bottiglia era definitivamente il tunnel WG che passava per il 5G.

Il link 5G passa per CGNAT (`172.20.x.x`), 25ms di latenza. La fibra passa per un altro CGNAT (`172.17.x.x`), 3ms. Il 5G non era mai stato pensato per trasferimenti bulk.

## Step 4: Ma PERCHÉ WG era sul 5G?

La fibra avrebbe dovuto essere *down* al boot perché il 5G diventasse il default. Primo controllo: `logread` sul router. Inutile — il ring buffer contiene solo i log del giorno corrente. Ma quello che conteneva era già sospetto: pagine e pagine di fallimenti ping mwan3 sull'interfaccia fibra:

```
Check (ping) failed for target "8.8.8.8" on interface wan (eth1). Current score: 10
Check (ping) failed for target "1.1.1.1" on interface wan (eth1). Current score: 10
Check (ping) failed for target "8.8.8.8" on interface wan (eth1). Current score: 10
```

Migliaia di fallimenti. Lo score oscillava tra 9 e 10 — i singoli ping fallivano costantemente, ma abbastanza ne passavano per impedire allo score di arrivare a 0 (che dichiarerebbe l'interfaccia morta). Questo era il primo vero indizio.

Tutto il syslog di questo router viene spedito a VictoriaLogs (log storage centralizzato). Tempo di fare forensics. Prima cosa, stabilire la data:

```
$ ssh root@golem 'mwan3 status | grep wan5g'
interface wan5g is online (online 83h:06m, uptime 1485h:25m)
```

1485 ore ÷ 24 = 61.8 giorni prima del 7 aprile → **4 febbraio**. Poi ho interrogato VictoriaLogs per ogni cambio di stato di interfaccia da allora:

```
$ curl -sk 'https://victorialogs/select/logsql/query' \
  --data-urlencode 'query=tags.hostname:golem AND ("is online" OR "is offline")'
```

La timeline era schiacciante:

```
# Prima entry: i ping falliscono subito
2026-02-04T21:00  Check (ping) failed for "8.8.8.8" on wan (eth1). Score: 10
...fallimenti ogni pochi minuti per 90 minuti...

# Poi lo score arriva a zero:
2026-02-04T22:30  Interface wan (eth1) is offline

# 8.7 ORE dopo:
2026-02-05T07:13  Interface wan (eth1) is online

# Altri due lunghi down nei due giorni successivi:
2026-02-06T10:45  Interface wan (eth1) is offline
2026-02-06T14:03  Interface wan (eth1) is online              # 3.3 ore offline
2026-02-06T22:56  Interface wan (eth1) is offline
2026-02-07T12:34  Interface wan (eth1) is online              # 13.6 ore offline

# Poi silenzio per un mese. Dopo il 7 feb, solo brevi blip:
2026-03-10T15:54  Interface wan (eth1) is offline
2026-03-10T15:58  Interface wan (eth1) is online              # 4 minuti
2026-03-14T00:03  Interface wan (eth1) is offline
2026-03-14T00:04  Interface wan (eth1) is online              # 52 secondi
2026-04-03T03:35  Interface wan (eth1) is offline
2026-04-03T03:36  Interface wan (eth1) is online              # 52 secondi
2026-04-05T06:53  Interface wan (eth1) is offline
2026-04-05T06:53  Interface wan (eth1) is online              # 53 secondi
```

Nel frattempo, il link 5G mostrava decine di flap offline/online (il modem 5G si riconnette di continuo — rumoroso ma irrilevante).

Il quadro era chiaro. Nei primi tre giorni, mwan3 aveva dichiarato la fibra *morta* tre volte — per **8.7 ore**, **3.3 ore** e **13.6 ore** rispettivamente. Dopo il 7 febbraio, il pattern era cambiato: gli eventi offline erano diventati blip di meno di un minuto.

E a quel punto mi sono ricordato: a inizio febbraio avevo appena finito di configurare il [backup 5G](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) e stavo testando il failover **tirando giù la fibra manualmente** per vedere se il 5G reggeva tutta la casa. Durante quei test, avevo notato che WireGuard restava incollato al link morto, così lo riavviavo — `ifdown wg && ifup wg`. Che creava il route dell'endpoint attraverso il backup 5G, perché era quello attivo in quel momento:

```
$ ip route show 46.38.233.77
46.38.233.77 via 192.168.253.254 dev br-lan.253 proto static metric 20
```

`proto static` — impostato da netifd all'avvio dell'interfaccia WireGuard, presente sia nella tabella principale che nella table 2 (wan5g). **Mai aggiornato. Mai rivalutato.** Riportavo su la fibra, tutto sembrava a posto, il traffico scorreva normalmente. Ma il route dell'endpoint WG restava cementato sul 5G. Non avevo indagato il *perché* WireGuard restava incollato — lo riavviavo e andavo avanti. Adesso lo so: ogni riavvio ri-creava il route statico via qualsiasi gateway fosse attivo in quel momento.

E quelle 102.935 entry "Check (ping) failed" che VictoriaLogs aveva accumulato da allora? Spiegavano il resto della storia. Anche dopo che i miei test erano finiti, mwan3 vedeva fallimenti ping costanti sulla fibra, mantenendo lo score a 9-10 (appena appena online). Periodicamente, abbastanza fallimenti si allineavano per far scendere lo score a zero, e mwan3 dichiarava la fibra offline. A inizio febbraio, quei drop duravano ore perché lo score faticava a recuperare. A marzo, qualcosa nei tempi era cambiato e il recupero era rapido — ma il route WG era già cementato, e il sistema non aveva nessun meccanismo per correggerlo.

Ma aspetta — la fibra non può *davvero* avere tutta questa packet loss. Giusto?

## Step 5: Ma la fibra funziona!

```
$ ping -I eth1 -c 50 8.8.8.8
50 trasmessi, 50 ricevuti, 0% packet loss
rtt min/avg/max = 12.6/13.0/13.8 ms
```

Zero perdita. Perfetto. Allora perché i ping one-shot di mwan3 falliscono?

## Step 6: Replicare il comportamento di mwan3

Ho studiato lo script mwan3track — usa `LD_PRELOAD` con una libreria wrapper che setta `SO_BINDTODEVICE` per bindare i ping all'interfaccia giusta. Ho replicato il suo comportamento esatto con ping one-shot in un loop:

```bash
for i in $(seq 1 30); do
  ping -I eth1 -n -c 1 -W 4 8.8.8.8 > /dev/null 2>&1
  [ $? -ne 0 ] && echo "FAIL at $i"
done
```

Risultato: 4/30 fallimenti, pattern regolare ogni ~8 iterazioni. Tre varianti testate (con LD_PRELOAD, con solo `-I`, senza niente): stessi risultati. Non è il wrapper, non è il binding. È qualcosa nel fatto di fare processi separati.

## Step 7: tcpdump rivela la verità

Ho catturato i pacchetti durante i ping falliti:

```
19:56:00.406147 IP 192.168.254.1 > 8.8.8.8: ICMP echo request
19:56:00.418955 IP 8.8.8.8 > 192.168.254.1: ICMP echo reply
```

**Le risposte ARRIVANO.** Tutte quante. La rete ha zero packet loss. Qualcosa tra l'interfaccia di rete e il processo ping mangia le risposte.

## Step 8: Il colpevole — banIP ICMP flood protection

```
$ nft list ruleset | grep icmpflood
counter cnt_icmpflood { packets 8951 bytes 651072 }
meta nfproto . meta l4proto { ipv4 . icmp }
  limit rate over 25/second burst 5 packets
  counter name "cnt_icmpflood" drop
```

**8.951 pacchetti ICMP droppati** dalla protezione flood di banIP. Nella chain `pre-routing`, applicata solo all'interfaccia WAN fibra (`iifname "eth1"`).

La regola: droppa qualsiasi traffico ICMP che supera 25 pacchetti/secondo con tolleranza burst di **5 pacchetti**.

Ecco cosa succede: mwan3 traccia entrambe le WAN pingando 3 target ciascuna. Sono 6 ping per ciclo, ciascuno in un processo `ping -c 1` separato. Le risposte arrivano in burst — e quando il burst supera i 5 pacchetti nella finestra di rate, nftables droppa l'eccesso **prima che raggiunga il socket del processo ping**.

Il `ping -c 50` persistente funziona perché manda un pacchetto al secondo con un singolo socket. Il loop one-shot fallisce perché crea pattern di risposta bursty.

## La cascata completa

1. banIP droppa le risposte ICMP che arrivano in burst (by design — "flood protection")
2. Gli health check mwan3 usano ping one-shot che creano pattern bursty
3. mwan3 vede fallimenti ping costanti sulla fibra, score oscilla a 9-10
4. A un certo punto (probabilmente durante un vero micro-down della fibra), lo score è sceso a 0 e mwan3 è passato al 5G
5. Il route endpoint WireGuard è stato creato via il gateway 5G
6. La fibra è tornata, lo score mwan3 si è ripreso, il traffico normale scorreva correttamente — **ma il route statico WG è rimasto sul 5G**
7. Tutto il traffico WireGuard attraverso il tunnel: 2 Mbps invece di 70 Mbps
8. Per **due mesi** — dal boot del sistema il 4 febbraio

## Il fix

Due comandi UCI:

```bash
# 1. Impedire a banIP di droppare le risposte degli health check mwan3
uci set banip.global.ban_icmplimit=250
uci commit banip
/etc/init.d/banip restart

# 2. Impedire a netifd di creare un route statico per l'endpoint WireGuard
uci set network.wg.nohostroute=1
uci commit network
ifdown wg && ifup wg
```

Il primo comando alza il rate limit ICMP da 25/sec a 250/sec, così i ping bursty di mwan3 non raggiungono mai la soglia di drop.

Il secondo comando è il **vero fix della root cause**. Di default, netifd crea un route statico per l'IP dell'endpoint WireGuard per prevenire routing loop (se tutto il traffico passasse per la VPN, i pacchetti criptati proverebbero anche loro a passare per la VPN → loop infinito). Ma io **non** routo tutto il traffico per la VPN — solo `192.168.50.0/24`. L'IP endpoint `46.38.233.77` deve semplicemente seguire la default route, che mwan3 gestisce. Senza `nohostroute=1`, viene creato un route statico all'avvio dell'interfaccia WireGuard, pinnato a qualsiasi gateway sia attivo in quel momento. Se la fibra sta ancora inizializzando o mwan3 non l'ha ancora dichiarata online, il route va sul 5G — e ci resta per sempre.

Con `nohostroute=1`, nessun route statico. Il traffico WireGuard verso l'endpoint segue la default route. Se la fibra va giù, mwan3 switcha il default sul 5G, e WireGuard segue automaticamente. Nessun route stantio, nessun intervento manuale.

Dopo entrambi i fix:

```
$ iperf3 -c m42 -t 5 -R
[  5] 0.00-1.00  1.62 MBytes  13.6 Mbits/sec
[  5] 1.00-2.00  5.00 MBytes  41.9 Mbits/sec
[  5] 2.00-3.00  8.38 MBytes  70.3 Mbits/sec
[  5] 3.00-4.00  11.8 MBytes  98.5 Mbits/sec
[  5] 4.00-5.00  15.1 MBytes   127 Mbits/sec
```

**Da 2 Mbps a 127 Mbps.** Miglioramento di 63x.

## "Ma ti servono davvero tutti questi ping?"

Dopo il fix, mi sono chiesto: il burst di default di banIP è troppo basso, o sto pingando troppo?

Facciamo i conti. mwan3 traccia 3 target per interfaccia, `ping -c 1` ciascuno, ogni 5 secondi. Sono 3 echo reply ICMP che arrivano su eth1 entro ~20ms. Con tolleranza burst di 5 pacchetti e refill a 25/sec (un token ogni 40ms), 3 risposte in 20ms consumano 3 token mentre solo mezzo token si è rigenerato. Stretto, ma dovrebbe reggere — a malapena.

Solo che ho anche **Telegraf** sullo stesso router, che misura la latenza:

```toml
[[inputs.ping]]
  urls = ["google.com", "reddit.com", "facebook.com", "sindro.me", "8.8.8.8", "1.1.1.1"]
  method = "native"
  count = 10
  ping_interval = 0.5
  interface = "192.168.254.1"
```

Sei target, 10 ping ciascuno, ogni 0.5 secondi, bindati sulla stessa interfaccia `eth1`. Sono **60 echo reply ICMP** per ciclo di misurazione, tutti in arrivo in burst sulla WAN fibra. Con tolleranza burst di 5, banIP li massacrava.

Quindi i continui fallimenti mwan3 non erano solo per i 3 ping di mwan3 che colpivano il limite — erano i 60 ping di Telegraf che **consumavano tutti i token del burst**, senza lasciare niente per gli health check di mwan3 che arrivavano nella stessa finestra. I due sistemi competevano inconsapevolmente per lo stesso budget di 5 pacchetti burst.

Individualmente, ogni default è ragionevole:
- banIP burst 5 va bene per protezione flood ICMP
- mwan3 con 3 target di tracking è standard
- Il monitoraggio ping di Telegraf è utile per le dashboard di latenza

La combinazione è ciò che ti frega. Alzare il rate a 250/sec rende il budget burst effettivamente illimitato per traffico legittimo proteggendo comunque dai flood reali (nessuno fa ICMP legittimo a 250+ pacchetti/secondo).

## Lezioni

**Il tuo firewall può sabotare il tuo stesso monitoraggio infrastrutturale.** La protezione ICMP flood di banIP è ben intenzionata — non vuoi che attori esterni floodino la tua WAN con ICMP. Ma il rate limit non distingue tra traffico flood esterno e le risposte degli health check del tuo stesso router che arrivano in burst.

**Ping persistenti e ping one-shot si comportano diversamente sotto rate limiting.** Se il tuo monitoraggio usa `ping -c 1` in un loop (come fa mwan3), pattern di risposta bursty sono inevitabili. Un rate limiter con tolleranza burst bassa dropperà risposte anche quando il rate reale è basso.

**I route statici sono killer silenziosi.** Il route endpoint WireGuard viene creato all'avvio dell'interfaccia e mai rivalutato. Quando il gateway "giusto" cambia, il route resta. Nessun allarme, nessun log, nessuna indicazione che il traffico WireGuard passava per un link 5G a 2 Mbps invece di una fibra a 100 Mbps.

**tcpdump è l'arbitro definitivo.** Senza cattura pacchetti, avrei dato la colpa all'ISP fibra, all'overhead crypto di WireGuard, o alla CPU del Pi. I pacchetti sul filo raccontavano la storia vera: le risposte arrivavano perfettamente, e qualcosa nello stack di rete del kernel (nftables, in pre-routing) se le mangiava.

**Controlla il contatore `cnt_icmpflood` sul tuo box OpenWrt.** Se è diverso da zero e stai usando mwan3, probabilmente hai esattamente questo problema.

```bash
nft list counters | grep -A1 icmpflood
```

Prego.

## Epilogo: il mistero del 5G

Dopo il fix, ho testato WireGuard su entrambi i link:

| Percorso | Download TCP | Ritrasmissioni |
|----------|-------------|----------------|
| Raw TCP via 5G (no WG) | 273 Mbps | 2 |
| Raw UDP via 5G (no WG) | 300 Mbps | 0.18% loss |
| WireGuard via 5G | 1.7 Mbps | 26 in 5 sec |
| WireGuard via Fibra | 63 Mbps | 0 |

Il link 5G fa 300 Mbps raw. WireGuard lo trasforma in 1.7 Mbps. Un crollo di 175x. Non è un problema di porta, non è throttling, non è la CPU, non è l'MTU — li ho testati tutti.

Non so ancora perché. L'indagine è in corso. Prossimo post.
