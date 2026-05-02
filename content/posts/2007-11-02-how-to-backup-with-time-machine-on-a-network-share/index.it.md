---
title: Come fare il backup con Time Machine su una condivisione di rete
author: Marcello Barnaba
date: 2007-11-02
tags: [apple, backup, linux, networking, macos]
---

{{< retrospective year="2026" >}}
Apple ha aggiunto il supporto nativo a Time Machine via SMB in macOS High Sierra (2017) e ha deprecato AFP in Big Sur (2020). Oggi qualsiasi NAS con una semplice condivisione Samba funziona senza problemi — niente Netatalk, Avahi o marker file. Il Time Capsule è stato dismesso nel 2018.
{{< /retrospective >}}

*Ingredienti*: Debian, Netatalk, Avahi, un po' di trucchetti.

## Passo 1: Ricompilare Netatalk con supporto SSL

Ricompila Netatalk con il [supporto SSL](http://www.blackmac.de/archives/58-Make-Netatalk-talk-to-Leopard-Mac-OS-X-10.5.html#extended).

Puoi tranquillamente ignorare la roba del ".passwd", perché afpd usa PAM per l'autenticazione degli utenti.

Suggerimento: Disabilita i gestori del protocollo atalk in `/etc/default/netatalk` per un avvio più veloce:

```
# Set which daemons to run (papd is dependent upon atalkd):
ATALKD_RUN=no        # appletalk protocol
PAPD_RUN=no          # printer sharing daemon (printers are soooo '90s)
CNID_METAD_RUN=yes   # don't remember but is needed, rtfm!
AFPD_RUN=yes         # you will always need this
TIMELORD_RUN=no      # my time lord's name is <a href="http://openntpd.org">openntpd</a>
A2BOOT_RUN=no        # boot? nah! :P
```

## Passo 2: Crea una condivisione per i dati di backup di Time Machine, aggiungendo ad es.

```
# path         name           perms     charset
/some/where/tm "Time Machine" allow:vjt volcharset:"UTF8" 
```

in `/etc/netatalk/AppleVolumes.default`.

## Passo 3: Fai comparire il server AFPD nel Finder

Scarica il file di servizio avahi, mettilo in `/etc/avahi/services` e ricarica avahi con `/etc/init.d/avahi-daemon reload` (*scusate, i link originali sono rotti*).

## Passo 4: Configura il backup di Time Machine

Ti servono due file sulla condivisione di rete AFP: .com.apple.timemachine.supported e un dot-file che prende il nome dal MAC address della tua en0. Per crearlo, il modo più semplice è collegare un disco USB/Firewire, rinominarlo con il nome della condivisione di rete desiderata (specificata nel file AppleVolumes) e abilitare Time Machine su di esso.

Poi, copia il file .00... dal disco esterno nella tua home directory, espelli il disco, monta la condivisione di rete dal Finder e copia il file lì.

Infine, fai un touch di `.com.apple.timemachine.supported` sulla condivisione di rete e riapri le preferenze di Time Machine: la dimensione del tuo volume di backup dovrebbe essere uguale alla dimensione della condivisione di rete :).

Non puoi copiare entrambi i file ad es. via scp e aspettarti che funzioni: afpd ignora i dot-file nelle directory condivise, e i dot-file creati dalla macchina client appaiono così:

```
-rw-r--r--  1 vjt  16 2007-11-02 15:50 :2e000855f00f00
-rw-r--r--  1 root  0 2007-11-02 15:19 :2ecom.apple.timemachine.supported
```

perché afpd ha bisogno del dot-namespace:

```
drwxr-xr-x  2 vjt 40 2007-11-02 16:02 .AppleDB/
drwxr-xr-x  2 vjt  8 2007-11-02 16:02 .AppleDesktop/
```

Funziona:

![Time Machine in fase di backup](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/tm-backing-up.png)


Ovviamente con un po' di cache trashing:

![Cache Trashing](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/tm-fscache-destroy-after-backup.png)

Divertitevi!

PS: Si possono usare anche condivisioni SMB, dato che la storia degli hard link alle directory è contenuta in un file .sparsebundle creato sulla condivisione di rete. Una condivisione AFP ha il vantaggio aggiuntivo di essere indicizzabile da Spotlight, per non parlare del fatto che il tuo server Linux apparirà nel Finder come un fiammante Mac:

![fiammante mac](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/shiny-mac-icon.png)

e non come un PC Windows crashato:

![pc crashato](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/crashed-pc-icon.png)

:)
