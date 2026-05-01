---
title: "Failover mwan3 senza connessioni appese"
date: 2026-05-01
draft: true
tags: [openwrt, mwan3, networking, conntrack, nftables, devlog]
description: "mwan3 sposta i flussi nuovi quando un uplink cade. Quelli esistenti restano appesi per minuti. Ecco perché, e un piccolo flush selettivo del conntrack che risolve senza rasare al suolo il resto del router."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** [mwan3](https://openwrt.org/docs/guide-user/network/wan/multiwan/mwan3)
sposta i flussi *nuovi* quando un uplink cade. I flussi esistenti
restano inchiodati al percorso morto: il conntrack se li ricorda,
il flow offload del firewall continua a spedire pacchetti lungo
quel percorso, e i socket TCP a vita lunga restano appesi finché
l'applicazione non se ne accorge e si riconnette. L'opzione nativa
`flush_conntrack` è un'atomica globale. La soluzione è un
`/etc/mwan3.user` da quindici righe che fa un flush *selettivo* del
conntrack per mark mwan3, solo sull'evento `disconnected`.

<!--more-->

## Come ci sono arrivato

Dopo aver [migrato
Jeeves](/it/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/)
— il mio GL.iNet GL-X3000, il router 5G che gestisce
l'[uplink di backup, perché non voglio perdermi un'altra
riunione](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) —
a OpenWrt 25.12 vanilla, sono tornato a fare le mie esercitazioni
di failover sul gateway: stacco la fibra, vedo cosa succede. Stacco
il 5G, vedo cosa succede. E rifaccio.

Lo scenario era sempre lo stesso che osservavo da mesi. mwan3 faceva
il suo: i ping verso `1.1.1.1` tornavano in pochi secondi, le tabelle
di routing si ribaltavano sul membro vivo, le sessioni nuove partivano
sull'interfaccia giusta — ma ogni connessione TCP a vita lunga aperta
*prima* del failover restava lì, morta. Tornavano vive, sì. Su tempi
misurati in *minuti*, di solito governati dai timeout
dell'application layer.

Lo sapevo da un pezzo e mi ci ero arrangiato attorno. Imbarazzantemente
da un pezzo, in effetti — semplicemente non avevo mai trovato il tempo
di mettermi giù sul serio a capire da dove venisse la lentezza. Il
nuovo giro di esercitazioni ha reso impossibile continuare ad
archiviare le connessioni appese sotto "dopo".

Lista delle vittime, sulla mia rete di casa: il [server DNS
Technitium](https://technitium.com/dns/) che inoltra ogni query in
uscita dalla casa via DNS-over-TLS verso resolver upstream (così il
mio ISP non vede in chiaro i nomi che chiedo — il DNS in cleartext su
UDP/53 non è una battaglia che ho voglia di combattere) tiene aperti
socket TLS a vita lunga che restavano appesi. Il WebSocket di Home
Assistant verso la sua app companion sul telefono restava appeso.
Qualunque cosa con una connessione TCP persistente da prima del
failover restava lì, muta, mentre quelle nuove andavano benissimo.

Quello non è failover. È testa o croce.

## Cosa succede davvero

Il mio gateway di default, `golem`, è un [GL.iNet
GL-MT6000](https://www.gl-inet.com/products/gl-mt6000/) che gira
OpenWrt vanilla, con
[mwan3](https://openwrt.org/docs/guide-user/network/wan/multiwan/mwan3)
configurato su due membri:

| Membro | iface mwan3 | Device Linux   | Va verso                                           | Mark (mmx_mask `0x3F00`) |
|--------|-------------|----------------|----------------------------------------------------|--------------------------|
| fibra  | `wan`       | `eth1`         | il router fibra dell'ISP, lato LAN                 | `0x100` (id 1 << 8)      |
| 5G     | `wan5g`     | `br-lan.253`   | Jeeves e il suo uplink 5G, su una VLAN 802.1Q      | `0x200` (id 2 << 8)      |

Quando la fibra cade, mwan3:

1. Aggiorna le tabelle di routing perché le connessioni nuove vadano
   via 5G.
2. Si lava le mani.

Quello che *non* fa: niente sulle entry conntrack create mentre la
fibra era viva. Quelle entry portano ancora `ct mark = 0x100`, il
mark della fibra.

Già di per sé è un problema. Ma su questo router lo peggioro di
proposito: ho il **software flow offload** abilitato in fw4 (il
firewall basato su nftables di OpenWrt). Il flow offload è un
fast-path del kernel: una volta che il conntrack ha classificato un
flusso come ESTABLISHED, i pacchetti successivi saltano del tutto le
chain regolari di netfilter e prendono una scorciatoia di forwarding
dedicata. Importante su un router ARM che spinge una linea fibra
gigabit.

La scorciatoia ha come chiave la tupla del flusso più il device di
output. Quando la fibra cade, le entry offloadate per i flussi
marcati fibra puntano ancora a `eth1`. Dal punto di vista di `golem`,
il link di eth1 verso il modem dell'ISP è in perfetta salute — mwan3
ha rilevato il guasto via timeout dei ping *upstream*, non via un
evento link-down locale. Quindi il router continua a sputare
pacchetti sul percorso morto. Dove muoiano davvero dipende da cosa
si è rotto (la sessione PPPoE del modem, la fibra ottica a monte, il
gateway dell'ISP — scegli pure). Il modem probabilmente emette ICMP
Destination Unreachable per i primi pacchetti che non riesce a
inoltrare, e golem fa diligentemente l'un-SNAT e li gira indietro al
client di LAN — ma il TCP, [per RFC
5461](https://datatracker.ietf.org/doc/html/rfc5461), tratta gli
ICMP unreachable su una connessione stabilita come *soft errors* e
li ignora mentre ritrasmette, invece di abbattere il socket al primo
che arriva. Il kernel del client tiene il socket aperto.
L'applicazione aspetta.

Prima o poi scatta il timeout applicativo che la connessione si porta
dietro — i client DoT ne hanno di corti, i WebSocket fanno
pong-timeout in decine di secondi, SSH dipende dal `ServerAliveInterval`
che hai impostato, se l'hai impostato — e l'applicazione chiude il
socket morto, ne apre uno nuovo, e si rimette in piedi sull'uplink
vivo.

Il `tcp_keepalive_time` del kernel è impostato di default a 7200
secondi, quindi senza nessun timeout applicativo finisci sul
fallback delle due ore. In pratica niente sulla mia rete è abbastanza
paziente da aspettare tanto, e la riconnessione effettiva si misura
in minuti a una cifra o poco più. Comunque troppo per qualcosa che
dovrebbe essere trasparente.

## Cose che ho considerato ma non hanno funzionato

{{< figure src="rejected.jpg" alt="Illustrazione in stile incisione su tavola, palette ambra calda e teal freddo su sfondo crema con griglia da progettista: quattro strumenti chirurgici scartati appoggiati su un banco da lavoro in legno. Da sinistra a destra: un paio di forbici fini con la punta spezzata, una siringa antica con un piccolo rotolo arricciato di cifrario appuntato accanto, una sezione di staccionata con un tunnel nascosto sotto in cui passa un pacchetto luminoso, e una campana di vetro con dentro un groviglio di condotti di rete recisi. Ogni strumento ha un cartellino circolare in ottone; linee tratteggiate di misura e frecce annotano il banco" caption="Quattro strumenti provati e scartati: chirurgia per-client, l'RST spoofato che non sa leggere la finestra, la regola che l'offload bypassa via tunnel, e la campana di vetro del flush globale." >}}

L'ho affrontato da quattro angolazioni diverse prima di trovare quella
giusta. I motivi per cui ognuna fallisce sono interessanti in sé.

**`ss -K` sui client.** Ammazzare i socket incriminati lato client e
lasciare che l'applicazione si riconnetta. Layer sbagliato: dovrei
piazzare un hook su ogni device che apra una connessione a vita lunga
attraverso questo gateway, e continuare a farlo a mano a mano che la
lista dei device cresce. È una soluzione per-client per un problema
a livello di router.

**Forgiare un RST spoofato dal gateway.** Far iniettare a `golem` un
TCP RST nel flusso esistente con la tupla giusta, così il kernel del
client marca il socket `ECONNRESET` e l'applicazione si riconnette.
RFC 5961 richiede che il sequence number del RST sia dentro la
finestra di ricezione — e il conntrack non espone i sequence number
correnti (`-o extended` e `-o xml` li omettono entrambi). Gli RST
fuori finestra vengono scartati in silenzio. Vicolo cieco senza un
packet capture per ogni flusso.

**Una regola nft `reject with tcp reset` permanente sull'uscita
sbagliata per il mark.** Piazzare nella forward chain una regola
che scatti ogni volta che un pacchetto cerca ancora di uscire con il
mark di un uplink *ma* il device da cui sta uscendo è quello dell'altro
uplink. La regola è permanente nel ruleset; matcha solo quando l'idea del
conntrack su dove deve andare il flusso si è discostata dalla tabella
di routing — che è esattamente il sintomo post-failover.
Corretta in spirito, ma nel momento in cui un flusso è nella tabella
di offload non passa più dalla forward chain — è letteralmente
quello che fa l'offload: salta le chain. La regola non vede mai il
pacchetto a meno che l'entry di offload non venga invalidata. Cosa
che succede solo su... un flush conntrack. Circolare.

**L'opzione nativa `flush_conntrack` di mwan3.** Sembrava promettente,
finché non ho letto il [sorgente](https://github.com/openwrt/packages/blob/master/net/mwan3/files/lib/mwan3/mwan3.sh#L1207):
è `echo f > /proc/net/nf_conntrack`, un flush *globale* di ogni
flusso del router. Wireguard, Tailscale, forwarding LAN-to-LAN, le
connessioni stabilite dell'uplink superstite, tutto. Ogni volta che
mwan3 emette un evento configurato. Danni collaterali enormi per un
problema che chiede chirurgia.

## La soluzione

{{< figure src="the-fix.jpg" alt="Illustrazione in stile incisione su tavola, palette ambra calda e teal freddo su sfondo crema con griglia da progettista: una lunga fila orizzontale di piccoli pacchetti-busta luminosi su un banco da lavoro. La maggior parte brilla di ambra calda ed è intatta; un tratto contiguo nel mezzo brilla di teal freddo e viene sollevato delicatamente uno alla volta da un bisturi fluttuante di luce, lasciando la griglia nuda esposta sotto di loro. In alto a sinistra, in un riquadro: una mano che preme uno stampo di legno intagliato con sopra inciso un piccolo glifo astratto. Linee tratteggiate di misura e piccole frecce di annotazione attorno al vuoto" caption="Chirurgia, non amputazione: solo le entry col mark morto lasciano il banco." >}}

Quello che serviva: cancellare *solo* le entry conntrack marcate col
mark dell'uplink morto, *solo* sugli eventi `disconnected`. Il
conntrack già lo supporta — `conntrack -D -m <mark>/<mask>` cancella
per mark. mwan3 già etichetta ogni flusso col mark del suo membro.
Le due cose dovevano solo incontrarsi.

`/etc/mwan3.user` viene eseguito su ogni evento hotplug di mwan3:

```sh
. /lib/functions.sh
. /lib/mwan3/mwan3.sh
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

> *Una cosa che mi ha quasi sparato in un piede:* `config_load mwan3`
> è obbligatorio. `mwan3_get_iface_id` legge da una tabella runtime
> che si popola solo dopo aver camminato la config di mwan3. Se salti
> il load, la lookup torna vuota, il mark calcolato è `0x000`, e
> `conntrack -D -m 0/0x3F00` matcha ogni flusso *non marcato* del
> router — traffico locale, LAN-to-LAN, tutto. La riga `[ -n "$id"
> ] && [ "$id" != "0" ]` è la cintura di sicurezza che si rifiuta di
> sparare su un id vuoto o zero.

## Cosa succede ora

{{< figure src="recovery.jpg" alt="Illustrazione in stile incisione su tavola, palette ambra calda e teal freddo su sfondo crema con griglia da progettista: un diagramma di flusso orizzontale. A sinistra, un piccolo terminale di computer antico con ingranaggi in ottone visibili emette un pacchetto di dati luminoso color ambra. Il pacchetto incontra un tubo teal disegnato in modo sbiadito e barrato (il percorso morto), poi viene re-instradato attraverso un tubo ambra parallelo. Il tubo termina in una lente o trasformatore di ottone che riscrive in modo visibile il marchio di identificazione del pacchetto. Il pacchetto arriva poi a un castello-nuvola fortificato sulla destra. Una freccia teal sottile scorre indietro lungo il fondo dell'inquadratura fino al terminale, dove un piccolo bagliore luminoso di luce raffigura una connessione nuova fresca. Linee tratteggiate di misura e cartellini circolari in ottone annotano il percorso" caption="Il loop di ripresa: percorso morto barrato, percorso vivo che subentra, masquerade che riscrive la sorgente, il remoto risponde, il client si riconnette." >}}

Quando la fibra cade:

1. mwan3track manca i ping, emette `disconnected wan`.
2. mwan3 aggiorna le tabelle di routing: i flussi nuovi vanno con
   mark `0x200` (5G).
3. `/etc/mwan3.user` parte.
4. Le entry conntrack con `mark & 0x3F00 == 0x100` vengono cancellate,
   e con loro le entry corrispondenti nella tabella di flow offload
   di fw4. I pacchetti successivi per quei flussi tornano a passare
   per la pipeline regolare di netfilter.
5. Il prossimo pacchetto su un socket precedentemente inchiodato
   arriva su `golem` senza una entry conntrack che corrisponda. A
   patto che
   [`nf_conntrack_tcp_loose`](https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.rst)
   sia attivo — il default su OpenWrt — il kernel accetta il segmento
   a metà flusso come una nuova entry conntrack ESTABLISHED, lo
   instrada via la default route corrente (5G), e la regola di
   masquerade sulla WAN 5G riscrive l'IP e la porta sorgente con
   l'indirizzo della WAN 5G.
6. Il remoto riceve un segmento TCP da una tupla che non ha mai
   visto prima.

A questo punto la variabile dominante è il comportamento del remoto.

**Remoto educato** (la maggior parte dei CDN, Google, Cloudflare DoT):
segmento non sollecitato per una tupla sconosciuta → RST di ritorno
→ il kernel del client marca il socket `ECONNRESET` → l'applicazione
si riconnette in un RTT. È quello che fa il 99% di internet.

**Remoto silent-drop** (alcuni firewall enterprise, alcuni frontend
BGP anycast): inghiotte il segmento, niente risposta. Il client
ritrasmette per `tcp_retries2` finché il kernel molla (~15 minuti di
default) o scatta prima il timeout dell'applicazione. Per il DoT,
Technitium ha timeout applicativi corti e riapre le query su un
socket fresco in pochi secondi. Il bound lo fissa l'applicazione,
non il kernel. Se hai un servizio a vita lunga dietro a un remoto
silent-drop con un timeout applicativo lungo, l'escalation è
disabilitare il flow offload e aggiungere la regola nft RST
sull'uscita col mark sbagliato — io non ne ho avuto bisogno.

Tanto basta. Il failover ora *failovera* davvero. I ping si
riprendono, *e* anche i socket si riprendono, sulla stessa scala
temporale.

---

Tutto qui: quindici righe di shell agganciate a un evento hotplug.
L'autore di mwan3 aveva già fatto la parte difficile — ogni flusso è
marcato, ogni evento è emesso, ogni primitiva sta lì ad aspettare di
essere composta. Mancava solo il flush chirurgico. L'affidabilità non
è un'impostazione. L'affidabilità è una cosa che si costruisce.

Sia `/etc/mwan3.user` sia l'helper `mwan-ct` per l'operatore (lista,
conteggi, top-talker, ispezione dell'offload, flush manuale per
uplink) stanno in
[**vjt/mwan3-selective-flush**](https://github.com/vjt/mwan3-selective-flush)
su GitHub. Si copiano dentro, si fa lo smoke test con la ricetta nel
README, fatto.
