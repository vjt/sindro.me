---
title: "Failover mwan3 senza connessioni appese"
date: 2026-05-01
draft: true
tags: [openwrt, mwan3, networking, conntrack, nftables, devlog]
description: "mwan3 sposta i flussi nuovi quando un uplink cade. Quelli esistenti restano appesi fino a due ore. Ecco perché, e un piccolo flush selettivo del conntrack che risolve senza rasare al suolo il resto del router."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** mwan3 sposta i flussi *nuovi* quando un uplink cade. Quelli
esistenti restano inchiodati al mark morto — il conntrack ricorda, il
flow offload di fw4 continua felice a spedire pacchetti giù da un tubo
chiuso, e i socket TCP a vita lunga restano appesi finché non scatta
`tcp_keepalive_time` (di default: due ore). L'opzione nativa
`flush_conntrack` di mwan3 è un'atomica globale. La soluzione è un
`/etc/mwan3.user` da quindici righe che fa un flush *selettivo* del
conntrack per mark mwan3, solo sull'evento `disconnected`.

<!--more-->

## Come ci sono arrivato

Dopo aver [migrato Jeeves su OpenWrt 25.12
vanilla](/it/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
ho deciso di fare una cosa che rimandavo da tempo imbarazzante: testare
sul serio il failover end-to-end sul gateway. Stacco la fibra, vedo
cosa succede. Stacco il 5G, vedo cosa succede. E rifaccio.

mwan3 ha fatto il suo: i ping verso `1.1.1.1` tornavano in pochi
secondi, le tabelle di routing si ribaltavano sul membro vivo, le
sessioni nuove partivano sull'interfaccia giusta. Sembrava ottimo.

Quello che ottimo non era: i miei socket DoT di Technitium verso i
resolver upstream erano appesi. Le sessioni SSH attraverso il gateway
erano appese. Il WebSocket di HA appeso. Qualunque cosa con una
connessione TCP a vita lunga aperta *prima* del failover restava lì,
morta, mentre quelle nuove funzionavano. Tornavano vive, sì — ma su
un timer da minuti-fino-a-ore, non da secondi.

Quello non è failover. È una monetina che tiri.

## Cosa succede davvero

`golem` gira mwan3 con due membri:

| Membro | Iface     | Device         | Mark (mmx_mask `0x3F00`) |
|--------|-----------|----------------|--------------------------|
| fibra  | `wan`     | `eth1`         | `0x100` (id 1 << 8)      |
| 5G     | `wan5g`   | `br-lan.253`   | `0x200` (id 2 << 8)      |

Quando la fibra cade, mwan3:

1. Aggiorna le tabelle di routing perché le connessioni nuove vadano
   via 5G.
2. Si lava le mani.

Quello che *non* fa: niente sulle entry conntrack create mentre la
fibra era viva. Quelle entry portano ancora `ct mark = 0x100`. La
flow offload table di fw4 — `hook ingress priority filter`, dispositivi
inclusi `eth1` — sta ancora felicemente offloadando quei flussi su
`eth1`. I pacchetti arrivano sul device morto e droppano in L2.

Il TCP del client non lo sa. Per il kernel, il socket è sano. Niente
RST, niente ICMP unreachable, nessun segnale. Il send buffer si
riempie. Prima o poi `tcp_keepalive_time` scatta, il kernel se ne
accorge, il socket muore. Con il default di **7200 secondi** sono
due ore.

Si può accorciare il keepalive globalmente, ma è rischioso e generico
— e non risolve il problema vero, che è che il conntrack è sbagliato.

## Cose che ho provato e non hanno funzionato

Ci sono arrivato da quattro angoli prima di trovare quello giusto.
Nessuno funzionava, e i motivi sono interessanti.

**`ss -K` sul client.** L'idea: ammazzare i socket incriminati lato
client e lasciare che l'app si riconnetta. Pulito. Non funziona su
`nowhere`, il Pi 5 che ospita la maggior parte di quei socket, perché
il kernel `rpt-rpi-2712` è compilato senza
`CONFIG_INET_DIAG_DESTROY`. `ss -K` ritorna 0 e non fa niente. No-op
silenzioso. Ho una nota in memoria per il me futuro.

**Forgiare un RST spoofato dal gateway.** L'idea: far iniettare a
`golem` un TCP RST nel flusso esistente con la tupla giusta, così il
kernel del client marca il socket `ECONNRESET` e l'app si riconnette.
Non si può, perché RFC 5961 richiede che il sequence number del RST
sia dentro la receive window — e il conntrack non espone i sequence
number correnti. Né `conntrack -L -o extended` né `-o xml` li
mostrano. I RST fuori finestra vengono scartati in silenzio.

**Regola nft permanente `reject with tcp reset` sul mark morto.**
L'idea: piazzare una regola di forwarding che spari un TCP reset per
qualunque pacchetto cerchi ancora di uscire col mark dell'uplink
morto. Bypassata dal flow offload di fw4. I pacchetti offloadati
saltano del tutto la chain `forward` — è letteralmente quello che fa
l'offload. La regola non scatta finché l'entry di offload non viene
invalidata. Cosa che succede solo su... un flush conntrack.

**L'opzione nativa `flush_conntrack` di mwan3.** Sembrava promettente
finché non ho letto il sorgente. È implementata come `echo f >
/proc/net/nf_conntrack`: flush *globale*. Tutti i flussi del router.
Wireguard, Tailscale, forwarding LAN-to-LAN, le connessioni stabilite
sull'uplink superstite, tutto. Ogni volta che mwan3 emette un evento
tracciato. Danni collaterali enormi per un problema che chiede
chirurgia.

## La soluzione

Quello che serviva: cancellare *solo* le entry conntrack marcate col
mark dell'uplink morto, *solo* sugli eventi `disconnected`. Il
conntrack già lo supporta — `conntrack -D -m <mark>/<mask>` cancella
per mark. mwan3 già etichetta ogni flusso col mark del suo membro. Le
due cose dovevano solo incontrarsi.

`/etc/mwan3.user` viene eseguito su ogni evento hotplug di mwan3:

```sh
. /usr/share/libubox/jshn.sh
. /lib/functions.sh
. /usr/share/mwan3/common.sh

config_load mwan3

flush_dead_uplink() {
    local id mark
    mwan3_get_iface_id id "$1"
    [ -n "$id" ] && [ "$id" != "0" ] || return 0
    mark=$((id << 8))
    conntrack -D -m "${mark}/0x3F00" 2>/dev/null
    logger -t mwan3-flush "selective conntrack flush iface=$1 mark=$(printf 0x%x $mark)"
}

case "$ACTION" in
    disconnected) flush_dead_uplink "$INTERFACE" ;;
esac
```

Due dettagli non ovvi.

`config_load mwan3` è obbligatorio. `mwan3_get_iface_id` legge da
`mwan3_iface_tbl`, che si popola camminando la config di mwan3. Senza
il load, la lookup torna vuota, il mark è `0x000`, e
`conntrack -D -m 0/0x3F00` matcha ogni flusso non marcato del router
— traffico locale, tutto quanto. L'ho beccato a mano prima del
deploy. La guard sull'id vuoto è la cintura di sicurezza.

Le `local` stanno dentro a una funzione perché
`/etc/hotplug.d/iface/16-mwan3-user` invoca lo script tramite
`env -i ACTION=… INTERFACE=… DEVICE=… /etc/mwan3.user` sotto ash
puro — che `local` al top level non lo accetta.

## Cosa succede ora

Quando la fibra cade:

1. mwan3track manca i ping, emette `disconnected wan`.
2. mwan3 aggiorna il routing: i flussi nuovi vanno con mark `0x200`
   (5G).
3. `/etc/mwan3.user` parte.
4. Le entry conntrack con `mark & 0x3F00 == 0x100` vengono cancellate,
   e con loro le entry corrispondenti nella flowtable di fw4.
5. Il prossimo pacchetto su un socket precedentemente inchiodato
   arriva su `golem` senza match conntrack → il kernel forwarda via
   default route corrente (5G), crea una entry conntrack fresca con
   `mark=0x200`, lo SNAT scambia l'IP sorgente da quello WAN della
   fibra a quello del 5G.
6. Il remoto vede un segmento TCP da una tupla nuova.

Il comportamento del remoto è ora la variabile dominante.

**Remoto educato** (la maggior parte dei CDN, Google, Cloudflare DoT):
segmento non sollecitato → RST di ritorno → kernel del client marca il
socket `ECONNRESET` → l'applicazione si riconnette in un RTT. È quello
che fa il 99% di internet.

**Remoto silent-drop** (alcuni firewall enterprise, alcuni frontend
BGP anycast): inghiotte il segmento, niente risposta. Il client
ritrasmette per `tcp_retries2` finché il kernel molla (~15 minuti di
default) o scade il timeout dell'applicazione. Per il DoT in
particolare, Technitium ha timeout applicativi corti e riapre i query
su un socket fresco in pochi secondi. Il bound lo decide
l'applicazione, non il kernel.

Basta così. Il failover ora *failovera* davvero. I ping si riprendono,
*e* anche i socket, sulla stessa scala temporale.

## Se il silent-drop diventa un problema

Per me non lo è. Se mai dovesse diventarlo, il piano di escalation:

1. Disabilitare il TCP flow offload sul gateway. Allora il forwarding
   passa *davvero* per `forward`, e una regola nft permanente `reject
   with tcp reset` sui pacchetti che escono dal device sbagliato per
   il loro mark scatta sul primo segmento di ogni flusso zombie. Costo
   CPU per pacchetto in salita; profilare prima/dopo.
2. "Force reload" applicativo per i pochi superstiti. Fuori scope.

## Come verificare

`golem` spedisce i log al rsyslog di `nowhere` → Telegraf →
VictoriaLogs. Tail live:

```sh
ssh root@golem 'logread -f | grep mwan3-flush'
```

Oppure query diretta su VictoriaLogs:

```sh
curl -sk 'https://victoria.bad.ass/select/logsql/query' \
  --data-urlencode 'query=_stream:{tags.hostname="golem"} mwan3-flush' \
  --data-urlencode 'start=-1d' | jq .
```

Test manuale (cancella conntrack vero — fallo solo su un router che
ti puoi permettere di fare singhiozzare per un attimo):

```sh
ACTION=disconnected INTERFACE=wan /etc/mwan3.user
```

Aspettati una singola riga di log. Aspettati `conntrack -L |
grep -c 'mark=256'` che va a circa zero — `256` decimale è `0x100`
esadecimale, il mark della fibra.

---

Tutto qui: quindici righe di shell agganciate a un evento hotplug.
L'autore di mwan3 aveva già fatto la parte difficile — ogni flusso è
marcato, ogni evento è emesso, ogni primitiva sta lì ad aspettare di
essere composta. Mancava solo il flush chirurgico. L'affidabilità non
è una setting. L'affidabilità è una cosa che si costruisce.
