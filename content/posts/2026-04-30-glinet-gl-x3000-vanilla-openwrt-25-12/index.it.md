---
title: "GL-X3000 su OpenWRT 25.12 vanilla: tutto funzionante"
date: 2026-04-30
tags: [openwrt, 5g, networking, glinet, quectel, modem, devlog]
description: "Diario di migrazione completo: firmware GL.iNet stock via, OpenWrt 25.12 vanilla dentro, ogni insidia documentata così non devi riscoprirla da solo."
image: cover.jpg
featuredImage: cover.jpg
---

**TL;DR:** ho migrato il mio GL-iNet GL-X3000 (Spitz AX) — Jeeves, [il
mio uplink 5G di
backup](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) —
dal firmware GL.iNet di stock (OpenWrt 21.02, kernel 5.4) a OpenWrt
25.12 vanilla (kernel 6.12.79). Il modem — un Quectel RM520N-GL su
PCIe/MHI — funziona alla perfezione. Ci sono quattro modi distinti per
incartarsi prima di arrivarci. Li ho trovati quasi tutti. Questa è la
mappa. Se vuoi un'immagine già pronta, vai dritto alla
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases) e
flasha l'ultimo `jeeves-rN` sysupgrade bin.

<!--more-->

## Perché farlo

Jeeves è il mio uplink 5G di backup. Quando la fibra cade — [e cade,
sempre nel momento
peggiore](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) —
Jeeves è quello che mi salva da una riunione persa. L'hardware è
ottimo: MediaTek MT7981B (Filogic 820), Wi-Fi 6, USB 3.0, e un modem 5G
Quectel RM520N-GL su slot M.2 collegato sia a PCIe sia a USB.

Il firmware di stock è la versione GL.iNet di OpenWrt 21.02, su kernel
5.4. Quel kernel è arrivato a fine vita a dicembre 2022. Ma l'età del
kernel non è il motivo principale per cui ho cambiato.

Il motivo principale è il **controllo**. Voglio guidare ogni singolo
aspetto di questo livello di connettività con le mie mani.

Il problema più visibile: quando il 5G cade e resta su solo l'LTE,
l'automazione di GL.iNet non prova a riportare su il 5G. Lascia
semplicemente la radio sul 4G, all'infinito. Qui da me l'LTE va sui 5
Mbit/s. Se non me ne accorgo e non intervengo a mano, il link di
backup resta fermo a 5 Mbit/s per ore prima che la radio decida da
sola di tornare al 5G. Non è accettabile per qualcosa che dovrebbe
sostituire la fibra.

Il problema più tosto è il cell locking. Il mio operatore distribuisce
il 5G-NSA (non-standalone), e nel momento in cui ho chiesto al pannello
GL.iNet di stock di bloccare una torre specifica, il modem ha smesso di
agganciarsi a *qualsiasi* tower. Sospetto che c'entri il modo in cui il
loro stack pilota la procedura di attach NSA, ma non l'ho mai provato
— a quel punto volevo già togliermi dallo stock e non avevo voglia di
mettermi a fare reverse-engineering di codice vendor. Quindi mi sono
scritto il mio sistema di locking, che parla direttamente col modem —
[`5g-lock`](https://github.com/vjt/quectel-5g-tools/blob/master/bin/5g-lock),
un wrapper sottile attorno a `AT+QNWLOCK` / `AT+QNWCFG`. Battaglia
persa: lo stack GL.iNet si accorge dei cambi AT fuori-banda e li
ripristina coi suoi tempi. Per tenere davvero in mano la radio mi
serviva un percorso AT che restasse dove l'avevo lasciato — e l'unica
strada era vanilla.

OpenWrt 25.12 vanilla porta il supporto mainline MHI/MBIM per il path
dati PCIe del modem (più sotto spiego cosa vogliono dire questi
acronimi), l'integrazione con ModemManager, il nuovo gestore di
pacchetti basato su apk, e tutto l'ecosistema attuale di pacchetti. Il
firmware GL.iNet è un fork: distribuiscono attraverso i loro repository
una serie di pacchetti aggiuntivi, ma hanno anche un loro ciclo di
release, e seguire il loro SDK da una versione all'altra è
significativamente più lavoro che seguire il vanilla. Vanilla è la cosa
vera — e mi lascia possedere ogni bit dello stack di connettività.

Un piccolo glossario per il grafico che segue — sono i quattro numeri
che ogni pipeline di telemetria cellulare traccia per ogni cella:

- **RSRP** — Reference Signal Received Power. Quanto forte arriva al
  modem il segnale della torre. Come quanto arriva forte la voce di un
  amico dall'altra parte della stanza.
- **SINR** — Signal-to-Interference-plus-Noise Ratio. Quanto è pulito
  quel segnale rispetto a tutto il resto del rumore in giro. Stesso
  amico, stessa voce, ma in una biblioteca silenziosa vs un caffè
  affollato — è il numero in dB a cambiare.
- **RSRQ** — Reference Signal Received Quality. Una vista combinata di
  segnale rispetto al carico della cella: alto quando la cella è
  scarica, scende quando è piena di utenti.
- **PCI** — Physical Cell ID. Il "nome" della torre dal punto di vista
  del modem: numero diverso = cella diversa.

{{< figure src="last-70-days-5g-telemetry.png" alt="Tre pannelli Grafana impilati — SINR, RSRP, RSRQ — su 70 giorni dal 02/20 al 04/30. Tutti e tre i pannelli mostrano vari buchi verticali multi-ora dove la serie dati manca del tutto, mescolati con la solita oscillazione giornaliera dell'interferenza" caption="Settanta giorni di telemetria del segnale 5G. I buchi nei tre pannelli sono outage veri — molti durano ore, in qualche caso coprono periodi di fallback su 4G in cui anche l'LTE era irraggiungibile e il modem non si è ripreso da solo. Con OpenWrt vanilla riesco a reagirci, invece di subirli. Se ti stai chiedendo come raccolgo questa roba, è [quectel-5g-tools](https://github.com/vjt/quectel-5g-tools) che alimenta una VictoriaMetrics interna, plottata con [questa dashboard Grafana](https://grafana.com/grafana/dashboards/24835-ultimate-isp-5g-lte-monitor-quectel-rm520-gl/)." >}}

Il GL-X3000 è supportato dalla community OpenWrt — la [pagina ufficiale
del wiki](https://openwrt.org/toh/gl.inet/gl-x3000#setup_5g_connectivity)
ti accompagna nella configurazione 5G dall'inizio alla fine. La
fregatura è che copre solo il path dati **USB** del modem, che funziona
ma riduce notevolmente la banda disponibile rispetto a quello che la
radio riesce davvero a fare — il path PCIe è significativamente più
veloce, e non volevo un collo di bottiglia proprio sul link che
dovrebbe sostituire la fibra in caduta. Il PCIe richiede una patch al
kernel (vedi sotto) e una build personalizzata. Quindi l'immagine me
la sono fatta. Non ci ho messo molto, ma c'erano un paio di passaggi
in cui la cosa giusta da fare non era ovvia, e questo è quello che ho
imparato nel processo.

## Come è fatto

Il RM520N-GL parla con l'host **sia** via PCIe **sia** via USB
contemporaneamente, attraverso una piccola sequenza di acronimi che
vale la pena chiarire subito:

- **MHI** — Modem Host Interface. Il livello di trasporto Qualcomm su
  PCIe per i modem cellulari. Scava il link PCI in canali e ci fa girare
  sopra control + data + diagnostica. Grosso modo l'equivalente degli
  endpoint USB, ma sul bus PCI.
- **MBIM** — Mobile Broadband Interface Model. Uno standard USB-IF per
  trasportare pacchetti di rete e un canale di controllo tra host e
  modem. Sul GL-X3000 viaggia sopra MHI; il kernel lo espone come
  netdev più un device a caratteri di controllo (`/dev/wwan0mbim0`).

Il firmware GL.iNet di stock usava un driver proprietario `pcie_mhi`
che esponeva i nodi `/dev/mhi_*`. OpenWrt vanilla usa il driver
upstream `mhi_pci_generic`, che espone `/dev/wwan0mbim0` (il path dati
MBIM), `/dev/wwan0at0` (porta comandi AT), e compagnia.

Il lato USB espone quattro porte seriali (`/dev/ttyUSB0`–`3`) per i
comandi AT/NMEA/DIAG, e — dopo un cambio di composizione — un'interfaccia
ADB. Più sotto torno sopra.

## Come si flasha

Il GL-X3000 sotto al cofano già fa girare OpenWrt — è esattamente per
questo che ho comprato hardware GL.iNet: volevo un dispositivo con
supporto OpenWrt di prima categoria, non un router chiuso con uno
stack vendor sopra. La [pagina del wiki OpenWrt per il
GL-X3000](https://openwrt.org/toh/gl.inet/gl-x3000) documenta la
procedura chiaramente: dai in pasto il file **sysupgrade** alla web
recovery dello U-Boot GL.iNet di stock. Non provare con il file
factory — lo U-Boot di stock valida l'header dell'immagine e lo
rifiuta con *"Something went wrong during update. Probably you have
chosen wrong file."*

La procedura: tieni premuto Reset mentre accendi, metti il PC su un IP
statico nel range `192.168.1.0/24`, apri `192.168.1.1` nel browser,
carica il sysupgrade. Circa 90 secondi. Da lì in poi, lo stesso file
sysupgrade è quello che usi anche per gli upgrade in-place.

Prima di flashare, fai un backup del bootloader di stock:

```sh
ssh root@192.168.253.254
dd if=/dev/mmcblk0boot0 of=/tmp/stock_preloader.bin
dd if=/dev/mmcblk0p4 of=/tmp/stock_uboot_fip.bin
scp root@192.168.253.254:/tmp/stock_*.bin .
```

Probabilmente non ti serviranno mai. Fallo lo stesso.

## Insidia 1: il modem ha bisogno di una patch del kernel

Il RM520N-GL venduto col GL-X3000 è la variante GLAP — sub-device PCI
ID leggermente diverso (`17cb:0308`, sub-vendor `17cb`, sub-device
**`5201`**). Il driver mainline `mhi_pci_generic` non riconosce `5201`
out of the box. Il modem non si enumera. Ti ritrovi con un `mmcli -L`
vuoto e un dmesg in cui non c'è traccia di `wwan`.

Il fix è una [patch al kernel da una
riga](https://github.com/vjt/openwrt-glinet-x3000/blob/openwrt-25.12/target/linux/generic/pending-6.12/gl-x3000-quectel-pci-id.patch)
che aggiunge il sub-device ID alla match table PCI del driver. Senza,
hai un router 5G senza 5G. La distribuisco come
`target/linux/generic/pending-6.12/gl-x3000-quectel-pci-id.patch` nel
build tree.

Non l'ho capito da solo — devo la diagnosi (e la patch stessa) a un
[thread della community
GL.iNet](https://forum.gl-inet.com/t/how-to-installing-vanilla-openwrt-on-gl-x3000/45404)
del 2024 in cui altri che facevano la stessa migrazione avevano già
sviscerato i sintomi. Tanto di cappello a chi nel thread ha individuato
per primo il sub-device `5201` mancante.

Lo stesso fix [è stato proposto in
linux-arm-msm](https://lore.kernel.org/mhi/20250729-add-rm520n-glap-support-v1-1-736ee6bbb385@fritscher.net/T/#u)
a luglio 2025 da Michael Fritscher, che è incappato nello stesso
problema. In mainline non è ancora — il maintainer ha sollevato una
domanda sul fatto che Quectel riusi i vendor ID di Qualcomm, e la
patch è in attesa di chiarimenti da parte di Quectel. Finché non
viene mergiata, l'unica strada è la patch out-of-tree.

## Insidia 2: il PCIe runtime power management ti fa crashare il modem

Questa è quella che mi è costata più tempo. Sintomi: il modem si
alza bene, ModemManager si connette, il traffico passa — e poi, **due
minuti dopo, riproducibile ogni volta**, il modem sparisce con una
cascata di errori del kernel:

```
pci 0000:01:00.0: AER: Correctable error message received
pci 0000:01:00.0: PCIe Bus Error: severity=Correctable, type=Physical Layer
pci 0000:01:00.0: MHI: channel not open
pci 0000:01:00.0: PCIe: ERROR CmpltTO
```

Per peggiorare le cose, il guasto si trascina dietro anche il resto
del bus PCI: ogni paio di secondi il kernel resetta il link, la porta
ethernet integrata si pianta mentre lo fa, e SSH si congela. Avevo
una finestra di ~un minuto di shell utilizzabile subito dopo il boot,
poi finestre da 2-3 secondi più o meno ogni 30. Debuggarlo non era
proprio comodo.

Cosa succede: il power management della porta PCIe del kernel mette la
porta in D3hot (link spento). Quando arriva del traffico, la porta si
risveglia, ma il bus MHI non si riprende mai del tutto dall'evento di
link-down. Il layer AER del PCIe inizia a loggare Completion Timeout.
Il modem ammutolisce.

Il [workaround è
brutale](https://github.com/vjt/openwrt-glinet-x3000/commit/4087faad55849b7891008482fe0d8beae81714b8):

```
pcie_port_pm=off
```

nella command line del kernel. Disabilita il power management della
porta PCIe a livello globale. Sul GL-X3000 questo significa che il
link del modem resta sempre a piena potenza. Niente più crash — ma è
un workaround, non un fix. L'interazione di fondo tra il driver MHI e
il core PM del PCIe è ancora sbagliata; spero che una versione futura
del kernel sistemi la cosa e mi permetta di togliere il flag.

Nota per i prudenti: se il modem *finisce* in questo stato bloccato,
le mitigazioni runtime non aiutano. L'unico recupero è un reboot
dell'host. Da una tempesta di CmpltTO non si esce con `rmmod` e
`modprobe`.

## Insidia 3: non rebootare il modem alla leggera

Collegato a quanto sopra: `AT+CFUN=1,1` reboota il modem. Su questo
hardware, il reboot del modem mentre il link PCIe è attivo può
incagliare la porta host PCIe nello stesso stato di errore. Il modem
fa il suo power-cycle, il link PCIe sussulta, MHI perde il sync, e ti
ritrovi nella cascata CmpltTO senza il trigger del PM.

Quindi: se devi rebootare il modem, ferma prima ModemManager, manda
`AT+CFUN=0` per spegnere la radio in modo pulito, *poi* rilancialo. O
rebootati direttamente il router — è più veloce e meno emozionante.

## Insidia 4: ModemManager si mangia le tue porte AT

Il pacchetto `modemmanager` di OpenWrt vanilla include una regola
udev/hotplug
([`/etc/hotplug.d/tty/25-modemmanager-tty`](https://github.com/openwrt/packages/blob/master/net/modemmanager/files/etc/hotplug.d/tty/25-modemmanager-tty))
che assegna a ModemManager ogni porta seriale USB che assomiglia a un
modem. Le `/dev/ttyUSB0`–`3` del RM520N-GL ci entrano tutte.
ModemManager le apre e le tiene esclusive — il che significa che la
mia toolchain AT (più sotto) non può parlare col modem mentre MM è in
esecuzione.

Il path dati del modem va su PCIe/MHI, quindi MM non *ha bisogno*
delle ttyUSB. Per il control usa `/dev/wwan0at0`. Ma la regola hotplug
non lo sa.

Il fix è una lista di esclusione e [una patch allo script
hotplug](https://github.com/vjt/openwrt-glinet-x3000/blob/openwrt-25.12/x3000/patches/0001-modemmanager-tty-honour-ignore-tty.patch):
`/etc/modemmanager/ignore-tty` elenca i nodi device da lasciare
stare, e lo `/etc/hotplug.d/tty/25-modemmanager-tty` patchato
controlla quel file prima di affidare una tty a MM. La patch si
applica pulita e fallisce rumorosamente se lo script upstream cambia.

Con questa in piedi, le `/dev/ttyUSB0`–`3` restano libere per
l'accesso AT diretto. MM usa `/dev/wwan0at0` per quello che gli serve.
Tutti contenti — e soprattutto la [mia pipeline di
telemetria](https://github.com/vjt/quectel-5g-tools) continua a
leggere le metriche di segnale dal modem senza dover litigare.

## Cosa ho effettivamente messo dentro

L'immagine finale — pubblicata come `jeeves-rN` sulla
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases) —
oltre al set di pacchetti standard di OpenWrt
25.12, contiene:

- **[`quectel-5g-tools`](https://github.com/vjt/quectel-5g-tools)** —
  una serie di strumenti Lua che ho scritto per monitorare e
  interagire con il modem Quectel. `5g-info` fa un dump completo
  dello stato, `5g-monitor` è una TUI live con visualizzazione della
  qualità del segnale e beep audio configurabili, `5g-lock` gestisce
  il band e cell locking, `quectel-at` è un wrapper a basso attrito
  per i comandi AT. C'è anche un collettore Prometheus — è quello che
  alimenta [questa dashboard
  Grafana](/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/full-5g-dashboard.jpg)
  — e
  `5g-led-bars`, un demone procd che pilota in tempo reale i quattro
  LED di segnale 5G sul pannello frontale del GL-X3000 a partire
  dall'RSRP (potenza del segnale) del 5G quando il modem è agganciato,
  o dell'LTE se il 5G è giù.
- **[`qfirehose` 1.4.17](https://github.com/vjt/qfirehose)** — il
  flasher di firmware Quectel standard. Upstream è arrivato a 1.7,
  ma ho scelto la 1.4.17 (originariamente
  [`nippynetworks/qfirehose`](https://github.com/nippynetworks/qfirehose))
  perché era la versione preconfezionata in un altro feed OpenWrt
  reputato e si era dimostrata stabile. L'ho forkato per aggiungere
  una build OpenWrt pulita, così il binario finisce direttamente
  nell'immagine — compilato e distribuito tramite il [mio
  openwrt-builder](/it/posts/2026-03-28-openwrt-builder/) come ogni
  altro pacchetto custom su questo router.
- **[`adb` + `fastboot`
  35.0.2](https://github.com/vjt/openwrt-android-tools)** — per gli
  switch di composizione USB del modem e l'accesso ADB nel SDX62.
- **[`wifi-dethrash-collector`](https://github.com/vjt/openwrt-dethrash)**
  — un collettore Prometheus che traccia i parametri Wi-Fi, gemello
  dell'[analisi del thrashing dei
  client](/it/posts/2026-04-03-wifi-dethrash-openwrt-mesh-analyzer/)
  da cui è nato.
- Un overlay rootfs con la mia CA interna e le chiavi di firma dei
  miei feed di pacchetti.
- **`telegraf-full`** — manda metriche alla mia VictoriaMetrics
  interna.

{{< figure src="signal-rabdomant.jpg" alt="Un telefono appoggiato su una borsa porta-attrezzi arancione, lo schermo mostra la TUI di 5g-monitor: operatore TIM, stato IDLE, BEEP:ON, LTE Banda 3 con PCI 427 SINR 8 dB, 5G-NSA Banda n78 con PCI 920 SINR 14 dB, breakdown completo di carrier aggregation e una lista di celle vicine, con un multitool semi-visibile a lato" caption="`5g-monitor` sul campo. PCC, SCC, celle vicine, tutto il segnale che ti serve per decidere se vale la pena salire ancora un altro gradino della scala." >}}

<video controls preload="metadata" width="100%">
  <source src="/posts/2026-04-30-glinet-gl-x3000-vanilla-openwrt-25-12/5g-monitor-beep.mp4" type="video/mp4">
</video>

Se la mia immagine precompilata non ti convince e te la vuoi
compilare da solo — più che giusto — ho automatizzato il setup. Cloni
[vjt/openwrt-glinet-x3000](https://github.com/vjt/openwrt-glinet-x3000),
lanci [`x3000/prepare.sh`](https://github.com/vjt/openwrt-glinet-x3000/blob/openwrt-25.12/x3000/prepare.sh),
e ti ritrovi un build tree funzionante pinnato a OpenWrt 25.12 con
tutte le patch del kernel applicate e tutti i pacchetti custom
collegati via `feeds.conf`. Da lì un `make` e via.

## Bonus: c'è un altro Linux dentro al modem

Visto che siamo qui: il RM520N-GL ha un suo Linux che gira dentro il
SoC baseband Qualcomm SDX62. L'accesso ADB a quel userland è
estremamente utile — log, diagnostica del firmware, `/usrdata` — ed è
bloccato di default.

Le serrature sono due. Per prima cosa, l'interfaccia USB ADB è
disabilitata nella composizione USB di default. La abiliti con un
cambio di composizione:

```sh
# Controlla la composizione corrente
quectel-at 'AT+QCFG="usbcfg"'
# +QCFG: "usbcfg",0x2C7C,0x0801,1,1,1,1,1,0,0   ← ADB off (penultimo bit)

# Tira su il bit ADB
quectel-at 'AT+QCFG="usbcfg",0x2C7C,0x0801,1,1,1,1,1,1,0'
# OK
```

Poi c'è la seconda serratura — un challenge-response su `AT+QADBKEY`:

```sh
# Step 1: prendi la challenge
quectel-at 'AT+QADBKEY?'
# +QADBKEY: 12345678

# Step 2: calcola la risposta (tool offline)
./qadbkey-unlock 12345678
# 0jXKXQwSwMxYoeg

# Step 3: invia
quectel-at 'AT+QADBKEY="0jXKXQwSwMxYoeg"'
# OK
```

La risposta non è crypto asimmetrica. Guardando le [sette righe che la
calcolano](https://github.com/vjt/qadbkey-unlock/blob/master/qadbkey-unlock2.py#L32-L38)
in `qadbkey-unlock` — il mio fork del tool originale della community
— l'algoritmo è semplice MD5-crypt: prendi la passphrase hardcoded
`SH_adb_quectel`, la salti con il valore di challenge che il modem ti
ha appena dato, lanci `crypt(3)`, e tagli 15 caratteri dall'hash. Il
"segreto" è la passphrase, estratta dal firmware Quectel a furia di
reverse engineering anni fa. Lo stato di unlock sopravvive a reboot e
upgrade del firmware del modem — finché resti su un branch di firmware
compatibile.

Una volta aperte entrambe le serrature, puoi entrare in shell sul SoC
del modem:

```
root@jeeves:~# uname -a
Linux jeeves 6.12.79 #0 SMP Tue Apr 28 15:21:30 2026 aarch64 GNU/Linux
root@jeeves:~# adb shell
/ # uname -a
Linux sdxlemur 5.4.210-perf #1 PREEMPT Fri Mar 1 06:52:45 UTC 2024 armv7l GNU/Linux
```

Una scatola a forma di router. Due SoC, due architetture, due kernel.
Quello aarch64 fa girare la rete. Quello armv7l gira dentro al modem,
e ci puoi entrare in shell.

Una nota importante, però: Quectel ha rimosso `AT+QADBKEY?` del tutto
a partire dal firmware `RM520NGLAAR_A0.301`. Compliance con la
Radio Equipment Directive (RED DA) europea — c'è un intero [thread di
discussione](https://github.com/iamromulan/cellular-modem-wiki/discussions/122)
in proposito. Una volta che flashi un firmware `≥ A0.301`, l'ADB
sparisce. Niente percorso supportato per tornare indietro.

Jeeves al momento è su `A03A03M4G` — comodamente prima del taglio
`A0.301`. Tengo una checklist obbligatoria prima di ogni aggiornamento
firmware del modem: leggo `AT+QGMR`, confronto lessicograficamente
l'identificatore di build con `A0.301`, e procedo o mi fermo.

## Epilogo: il mistero del SINR perduto

Circa due settimane prima di questa migrazione, il mio SINR sul 5G è
crollato da una baseline intorno ai 18 dB a 12 dB — nel giro di un
paio di minuti. Stesso RSRP, stessa cella, stesso beam, solo 6 dB in
più di rumore. Niente di cambiato dal mio lato. Non stavo guardando la
dashboard al momento, e non me ne sono accorto.

La cosa naturale da fare appena flashato vanilla era lanciare uno
speed test per verificare le performance. ~200 Mbps dove di solito ne
avevo ~350. *Oh no, è più lento.* Il mio primo istinto è stato
sospettare vanilla — una regressione dovuta alla migrazione appena
fatta, da qualche parte nel nuovo kernel, in MHI, o lungo il driver
path. Ma avevo qualcosa che il me-precedente non aveva: telemetria
long-term.

{{< figure src="sinr-drop.png" alt="Due pannelli Grafana impilati etichettati SINR e RSRP, dal 03/30 al 04/27. Il pannello SINR mostra una baseline intorno ai 17–18 dB fino a metà aprile, poi cala a ~11–13 dB e ci resta. Il pannello RSRP resta piatto tra -94 e -97 dBm su tutta la finestra. Entrambi mostrano vari buchi verticali in cui i dati mancano del tutto. Più serie colorate, una per PCI sulla banda n78" caption="Due mesi di SINR (sopra) e RSRP (sotto) per la cella n78 a cui mi attacco normalmente — quella col segnale più forte qui. RSRP è piatto su tutta la finestra: stesso segnale. La baseline del SINR cala a metà aprile: stesso segnale, più rumore. I buchi verticali in *entrambi* i pannelli sono outage veri — finestre lunghe ore in cui il modem ha perso del tutto la portante. Quegli outage sono l'altro motivo per cui sto facendo girare il mio firmware." >}}

Raccolgo RSRP, RSRQ, SINR, banda, PCI, e stato della carrier
aggregation tramite
[quectel-5g-tools](https://github.com/vjt/quectel-5g-tools) da gennaio,
con destinazione una VictoriaMetrics interna. La telemetria ha reso
inequivocabile che il drop di SINR era arrivato settimane prima che
toccassi il firmware. Stesso segnale (RSRP piatto), 6 dB in più di
rumore, stessa PCI, nessun handover. La migrazione non è la causa.
Non sono tornato indietro allo stock — sicurezza dai dati, non dalle
speranze.

RSRP piatto con SINR giù di 6 dB significa che il pavimento di
rumore si è alzato. Il modem riceve sempre lo stesso segnale dalla
stessa torre; sopra al segnale c'è ora significativamente più
interferenza. L'oscillazione giornaliera conservata (l'interferenza è
più bassa di notte, quando ci sono meno dispositivi attivi) ti dice
che la nuova fonte di interferenza varia col carico, non col tempo
atmosferico o con la geometria. La diagnosi: l'operatore quasi
sicuramente ha attivato una nuova cella n78 vicino. Il GL-X3000 va su
n78 (3.5 GHz TDD), la banda 5G principale in Italia e quella che si
sta densificando più aggressivamente. Niente da sistemare dal mio
lato. L'operatore ha densificato la rete. Il mio SINR è un danno
collaterale.

Naturalmente sono salito su una scala per vedere se un puntamento più
preciso dell'antenna mi facesse recuperare almeno un dB.

{{< figure src="me-ladder.jpg" alt="L'autore su una scala in piedi su un balcone, t-shirt Slackware, guarda dritto in camera. Un telefono che mostra l'output di 5g-monitor è appoggiato sul corrimano della scala accanto a lui; sullo sfondo un palazzo e qualche pianta in vaso" caption="Metodo scientifico: tieni il telefono col SINR live sul corrimano, inclini l'antenna con l'altra mano, guardi il numero." >}}

{{< figure src="me-antenna.jpg" alt="Selfie scattato dal basso — l'autore in basso a sinistra, sopra di lui l'antenna direzionale 5G montata sul muro dell'edificio, sullo sfondo campagna soleggiata e una vigna sotto un cielo limpido" caption="Funzionato. ~+1 dB di SINR dopo il ri-puntamento, ~+40 Mbps di throughput. Cinque minuti di scala ben spesi." >}}

OpenWrt vanilla mi dà finalmente la superficie che mi serve per
scrivere la logica di reconnect che quegli outage richiedono —
accorgermi del drop, aspettare che il 5G torni, ribaltare la radio in
automatico. Non l'ho ancora scritta. Ma adesso *posso*.

L'affidabilità non è un'impostazione. L'affidabilità è qualcosa che ti
costruisci. E per costruirla, ti serve il sorgente.

---

Tutto — patch del kernel, pacchetti custom, script di build, overlay
rootfs — sta in
[vjt/openwrt-glinet-x3000](https://github.com/vjt/openwrt-glinet-x3000).
Le immagini già pronte sono taggate sulla
[releases page](https://github.com/vjt/openwrt-glinet-x3000/releases)
come `jeeves-rN` — un ottimo punto di partenza se vuoi saltare il
passaggio della build.
