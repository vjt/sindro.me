---
title: Sblocco remoto via SSH di ZFS cifrato su FreeBSD
date: 2026-01-28
tags: [freebsd, sysadmin]
categories: [development]
---

## LUKS remoto? Pfft. Ecco come sbloccare via SSH una root ZFS cifrata su FreeBSD (nel modo difficile)

Se usi FreeBSD [come me](https://sindro.me/posts/2023-08-13-freebsd-encrypted-root-on-zfs/), su un server remoto con cifratura completa del disco (ZFS su GELI), conosci il panico del riavvio. Sei sempre alla mercé di un KVM-over-IP o di una connessione VNC dal browser, per inserire la password del filesystem root al prompt del kernel.

Inoltre, se (come me) fai girare un sistema con `kern.securelevel` > 0, allora installare una nuova libc significa riavviare in single user e installare gli aggiornamenti tramite la suddetta connessione KVM o VNC, che _non è ergonomica_ per usare un eufemismo.

La soluzione standard è di solito un ambiente SSH pre-boot. Su Linux, dropbear-initramfs rende la cosa banale. Su FreeBSD? Devi costruirti un mfsroot (memory file system) custom da zero.

La maggior parte delle guide suggerisce di usare un semplice shell script come init. Funziona, ma è misero. Perdi il job control (niente Ctrl+C), non hai un TTY decente, e in bocca al lupo se devi fare debug dei problemi di rete in modo interattivo.

Non volevo un hack raffazzonato. Volevo un ambiente vero. Volevo `init`, `getty`, `login`, autenticazione PAM, e un chroot ZFS per la manutenzione -- per installare aggiornamenti.

Ecco come ho costruito un unlocker remoto robusto per FreeBSD.

## Il problema con /bin/sh come Init

L'approccio ingenuo è compilare un ramdisk minuscolo, ficcarci dentro un binario sh statico, e dire al loader di eseguirlo come PID 1.

```bash
# Questo crea incubi
cat > /sbin/init <<EOF
#!/bin/sh
/sbin/dropbear
exec /bin/sh
EOF
```

Perché fallisce?

1. Niente job control: `/bin/sh` come PID 1 non gestisce le sequenze del terminale che scatenano segnali come `SIGINT`. Se esegui un comando che si blocca, non puoi fare Ctrl+C. Sei incastrato.

2. Niente switch-root (aka `reroot`). Il modo di FreeBSD per cambiare la root corrente è basato sul flag `RB_REROOT` della [system call `reboot()`](https://man.freebsd.org/cgi/man.cgi?query=reboot&apropos=0&sektion=2&manpath=FreeBSD+14.3-RELEASE&arch=default&format=html), ma il suo uso [è limitato a PID 1](https://man.freebsd.org/cgi/man.cgi?query=reboot&apropos=0&sektion=2&manpath=FreeBSD+14.3-RELEASE&arch=default&format=html). Quindi `reboot(8)` [manda un segnale a `init(8)`](https://cgit.freebsd.org/src/tree/sbin/reboot/reboot.c#n233) per fare shutdown o reroot del sistema. Se il tuo init è uno shell script, il sistema si blocca invece di fare il pivot.

## L'architettura

Per risolvere questo, dobbiamo replicare il processo di boot di FreeBSD in miniatura. Il mio `mfsroot` contiene:

1. `/sbin/init` vero: il vero binario init di FreeBSD gestisce la propagazione dei segnali e il reaping dei processi.
2. `/usr/libexec/getty` vero: configura il TTY correttamente così il job control funziona.
3. `/usr/bin/login` vero + PAM: si autentica contro il vero hash della password di root copiato dall'host.
4. Strumenti ZFS: per importare il pool e fare chroot nel sistema principale per aggiornamenti d'emergenza senza boot completo.

## Lo script `mkunlock`

Ho scritto uno script per automatizzare la generazione di questa immagine. Prende i binari necessari (incluse le librerie dinamiche via `ldd`), configura uno stack PAM minimale, e prepara gli script RC.

Ecco il flusso logico:

1. Fase di build: crea una struttura di directory di staging.
2. Raccolta librerie: copia `dropbear`, `geli`, `init`, `login`, e le loro dipendenze di shared object (`libc`, `libpam`, `libgeom`, ecc.).
3. Configurazione: genera un `/etc/rc`, `/etc/ttys`, e `/etc/gettytab` minimali.

## Il reroot "magico"

La parte più difficile è stata far sì che il kernel passi dal ramdisk alla root ZFS dopo lo sblocco. Il trucco è usare `reboot -r` (reroot) ma assicurandosi che l'ambiente sia pulito.

Bisogna:

1. Impostare `kenv vfs.root.mountfrom="zfs:tank/ROOT"`.
2. Smontare la partizione di boot fisica.
3. Rimontare root in sola lettura (`mount -ur /`).
4. Eseguire reroot via `/sbin/reboot -r`.

## Vantaggi

L'ambiente risultante è bellissimo. Quando il server boota, carica il ramdisk da 30MB e configura la rete.

Mi collego via SSH e ottengo una shell, e dalla console dell'host posso anche fare login con la password del sistema, o un'altra se non vogliamo copiare l'hash della password del sistema target nel ramdisk non cifrato.

Una volta dentro, ho tre strumenti custom:

* `unlock.sh`: collega il provider GELI usando il keyfile e la password.
* `enter.sh`: importa il pool ZFS su un mountpoint temporaneo e fa chroot al suo interno. Questo mi permette di eseguire `freebsd-update` (o al giorno d'oggi `pkg upgrade` dato che uso pkgbase) o sistemare le config in un equivalente della modalità Single User - senza avviare il sistema completo.
* `boot.sh`: esegue il pivot pulito verso il SO decifrato.

## Svantaggi

Ci sono ovviamente alcuni svantaggi - niente è gratis!

* Se il sistema si riavvia senza il tuo intervento, finirà per esporre un dropbear su qualche porta. Non uso quella standard, ma è raggiungibile comunque.
* Se usi la stessa password di root nel sistema principale e nell'ambiente di rescue, stai esponendo l'hash nel RAM disk non cifrato.
* Quando il sistema viene aggiornato, dovresti rieseguire `mkunlock` per assicurarti che lo userland sia in sync con il kernel.

## Il codice

Se vuoi smettere di pregare ogni volta che scrivi reboot, prendi lo script dal mio repo.

https://github.com/vjt/mfsroot-geli-dropbear

Scaricalo, eseguilo, e creerà un file `/boot/mfsroot.gz`. Puoi poi abilitarlo al boot modificando il tuo `loader.conf`:

```sh
# Load modules
geom_md_load="YES"
zfs_load="YES"

# Load initrd
mfs_load="YES"
mfs_type="md_image"
mfs_name="/boot/mfsroot"

vfs.root.mountfrom="ufs:/dev/md0"
```

Assicurati di non avere una riga `geom_eli_load="YES"` nel tuo `loader.conf` altrimenti il kernel rileverà la tua root cifrata e ti chiederà di inserire la password!

FreeBSD è potente, ma a volte devi grattarti il prurito da solo!
