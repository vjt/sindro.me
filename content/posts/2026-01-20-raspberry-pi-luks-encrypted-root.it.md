---
title: Root cifrata con LUKS su Raspberry PI 5
date: 2026-01-20
updated: 2026-03-14
tags: [linux, sysadmin]
categories: [development]
---

## Premessa

Quindi ho cominciato a far girare [Home Assistant](https://www.home-assistant.io/)
a casa su un Raspberry PI 5 e ho semplicemente installato HAOS su una SD. Poi ho
iniziato a sentirmi sempre più a disagio nel salvare credenziali nel filesystem
di HA in chiaro (qualsiasi offuscamento non è sufficiente).

Considerando che configurare una root cifrata con HAOS è semplicemente
impossibile senza forkarlo, e considerando anche che dedicare un intero RPI5
a HAOS è uno spreco di risorse, ho deciso di aggiungere un SSD al Pi, avviarlo
con Raspbian e poi far girare HAOS dentro una VM.

In questo modo, posso avere una root cifrata sull'host principale, cifrando
così l'intera VM HAOS.

Inoltre posso ora fare snapshot dell'intera VM HAOS e ho molta più
flessibilità nella gestione. Ultimo ma non meno importante, posso anche usare
la CPU e la RAM rimanenti del RPI per qualcos'altro.

## Ringraziamenti

Prima di tutto, un grande grazie a [questo
post](https://rr-developer.github.io/LUKS-on-Raspberry-Pi/) che mi ha dato
le indicazioni iniziali su come fare il setup. Ma quel post del 2021 è ora
leggermente datato, e molti passaggi non sono più necessari.

Secondo, un grande grazie a [Eric Fjøsne](https://github.com/ericfjosne) per
[aver usato questa guida e averla corretta](https://github.com/vjt/sindro.me/pull/1)
dato che l'avevo scritta perlopiù a posteriori :-).

## Requisiti

- Un RPI5 con Debian 13 (trixie) o successivo
- Una chiavetta USB decente e affidabile che può essere completamente cancellata
- Una tastiera e un monitor collegati direttamente al RPI

## Panoramica

L'idea di fondo è:

- Prepariamo un initrd che contiene i seguenti strumenti:
  - `resize2fs` per ridurre e ingrandire filesystem `ext4`
  - `cryptsetup` per gestire la cifratura delle partizioni
- Configuriamo il sistema per avviarsi da una root cifrata che non esiste ancora,
  forzando così il sistema a cadere nell'initrd.
- Nell'initrd, riduciamo il filesystem root alla dimensione minima possibile
- Copiamo il filesystem root dalla partizione in chiaro sulla chiavetta USB
- Creiamo la partizione cifrata usando LUKS
- Copiamo il filesystem root dalla chiavetta USB sulla partizione cifrata
- Estendiamo il filesystem root alla dimensione massima
- Configuriamo SSH nell'initrd così da poterlo sbloccare anche dopo aver
  piazzato il Raspberry Pi in un posto senza tastiera o schermo.

Pronti? Via!

## Preparazione dell'initramfs

Vogliamo dire al firmware di caricare un initramfs, cioè un RAM disk con un
ambiente Linux minimale che ha i pezzi necessari per aprire un device cifrato
e sbloccarlo - a patto che l'utente inserisca la password corretta.

Per default, [il firmware carica
kernel_2712.img](https://www.raspberrypi.com/documentation/computers/config_txt.html#kernel)
sul Raspberry Pi 5, dato che è quello ottimizzato.

Se l'opzione
[`auto_initramfs`](https://www.raspberrypi.com/documentation/computers/config_txt.html#auto_initramfs)
è impostata a `1`, allora il firmware caricherà anche l'immagine
`initramfs_2712` corrispondente in memoria e passerà il suo indirizzo al kernel.

Quando si crea un nuovo initramfs, lo script
`/etc/initramfs/post-update.d/z50-raspi-firmware` si assicura di piazzare una
copia dell'initramfs più recente nella directory del firmware, e di chiamarla
`initramfs_2712`. Quindi tutto il lavoro pesante è già fatto per noi!

### 1. Assicurati che il firmware carichi l'initrd

Assicurati di avere in `/boot/firmware/config.txt`:

```
auto_initramfs=1
```
ma dovrebbe già essere così.

### 2. Dì al kernel di montare la root dal device cifrato

Crea un backup del tuo `cmdline.txt` attuale, nel caso dovessimo ripristinarlo
dopo:

```
> sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.bak
```

Poi modifica `/boot/firmware/cmdline.txt` e fai quanto segue:
- sostituisci qualsiasi impostazione `root=XXX` con `root=/dev/mapper/cryptroot`.
- Per una scheda SD, aggiungi alla riga `cryptdevice=/dev/mmcblk0p1:cryptroot`
- Per un SSD, aggiungi alla riga `cryptdevice=/dev/nvme0n1p2:cryptroot`

Per esempio, il mio `cmdline.txt` è così:
```
console=serial0,115200 console=tty1 root=/dev/mapper/cryptroot rootfstype=ext4 fsck.repair=yes rootwait cryptdevice=/dev/nvme0n1p2:cryptroot
```

Sentiti libero di lasciare qualsiasi altro parametro presente, come quello per
il codice paese WiFi `cfg80211.ieee80211_regdom=XX`, che regola canali wireless
e livelli di potenza secondo le leggi locali.

### 3. Installa cryptsetup, initramfs-tools e busybox

Esegui:

```
> sudo apt install cryptsetup initramfs-tools busybox
```

Se alcuni di questi sono già installati, va benissimo!

Verifica che l'accelerazione hardware AES del tuo PI funzioni come previsto:

```
> cryptsetup benchmark -c aes-xts
# Tests are approximate using memory only (no storage IO).
# Algorithm |       Key |      Encryption |      Decryption
    aes-xts        256b      1736.6 MiB/s      1804.6 MiB/s
```

dovresti ottenere valori simili.

### 4. Configura l'initramfs per includere `resize2fs` e `cryptsetup`

Crea un nuovo file `/etc/initramfs-tools/hooks/luks_hooks`, contenente:

```
#!/bin/sh -e

case $1 in
        prereqs) echo ""; exit 0;;
esac

. /usr/share/initramfs-tools/hook-functions

copy_exec /sbin/resize2fs /sbin
copy_exec /sbin/cryptsetup /sbin
```

e rendilo eseguibile:

```
> sudo chmod +x /etc/initramfs-tools/hooks/luks_hooks
```

### 5. Aggiungi i moduli kernel per la cifratura del disco all'initramfs

Aggiungi le seguenti righe in fondo a `/etc/initramfs-tools/modules`:

```
aes_ce_blk
sha2_ce
dm_crypt
algif_skcipher
```

### 6. Chiedi all'initramfs di includere la *maggior parte* dei moduli

Gli initramfs-tools cercano di minimizzare il numero di moduli installati nel
RAM disk, facendo un rilevamento sofisticato dell'hardware e dei moduli
necessari. Tuttavia questo può fallire e potresti ritrovarti con un sistema
che si blocca nell'initramfs.

Quindi modifichiamo `/etc/initramfs-tools/initramfs.conf` e assicuriamoci che
la riga `MODULES` dica:

```
MODULES=most
```

### 7. Rigenera l'initramfs

Eseguiamo ora questo comando per generare l'initramfs per tutti i kernel installati:
```
> sudo update-initramfs -u
update-initramfs: Generating /boot/initrd.img-6.12.62+rpt-rpi-2712
'/boot/initrd.img-6.12.62+rpt-rpi-2712' -> '/boot/firmware/initramfs_2712'
```

Verifichiamo di avere tutto il necessario:

```
> lsinitramfs /boot/firmware/initramfs_2712 | grep -E 'sbin/(cryptsetup|resize2fs)'
usr/sbin/cryptsetup
usr/sbin/resize2fs
```

e:

```
> lsinitramfs /boot/firmware/initramfs_2712 | grep -E 'aes.ce.blk|sha2.ce|dm.crypt|algif.skcipher'
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/arch/arm64/crypto/aes-ce-blk.ko.xz
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/arch/arm64/crypto/sha2-ce.ko.xz
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/crypto/algif_skcipher.ko.xz
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/drivers/md/dm-crypt.ko.xz
```

Ora è il momento di riavviare e finire nella shell `(initramfs)`! Collega la
tua chiavetta USB usa e getta al Pi e:

```
> sudo reboot
```

## Modifiche al disco root nella shell initramfs

Dopo qualche tentativo di montare `/dev/mapper/cryptroot`, l'initramfs
desisterà e ti lascerà in una shell il cui prompt è semplicemente
`(initramfs) `. In questa shell abbiamo accesso root e possiamo manipolare i
dispositivi a blocchi collegati al Pi.

> ⚠️ Nota che il layout della tastiera per questa shell è English US.
> Potresti volerlo cambiare con quello corrispondente alla tua tastiera.

### 1. Assicurati di poter accedere a tutti i device necessari

Dobbiamo accedere sia alla chiavetta USB che al tuo device root. Verifichiamolo
eseguendo `lsblk`.

Dovresti vedere un device `/dev/sda` che è la tua chiavetta USB, e un device
`/dev/mmcblk0` se stai usando una scheda SD, o un device `/dev/nvme0n1` se
stai usando un drive NVME.

### 2. Assicurati che possiamo usare gli algoritmi di cifratura

Rieseguiamo i benchmark:

```
(initramfs) cryptsetup benchmark -c aes-xts
# Tests are approximate using memory only (no storage IO).
# Algorithm |       Key |      Encryption |      Decryption
    aes-xts        256b      1761.5 MiB/s      1813.9 MiB/s
```

Se tutto va bene, possiamo ora procedere con il nostro piano: ridurre il
filesystem root, copiarlo sulla chiavetta USB, creare un nuovo device cifrato
e spostare il filesystem root sul device cifrato.

### 3. Controlla l'integrità del filesystem root

Esegui:

```
e2fsck -f /dev/nvme0n1p2
```

Se `e2fsck` dice che il filesystem è OK, procedi al passo successivo! Altrimenti,
se ci sono errori seri, potrebbe essere meglio fermarsi e annullare le modifiche
fatte finora per evitare gravi corruzioni di dati. È il momento di ripristinare
il backup di `cmdline.txt` fatto prima.

Usa `lsblk` per trovare il nome del device della partizione da `512M` - sarebbe
`/dev/mmcblk0p1` se usi una scheda SD o `/dev/nvme0n1p1` se usi un drive NVME.

Poi montiamola, ripristiniamo il `cmdline.txt` precedente e riavviamo:

```
mkdir -p /foo
mount /dev/TUAPARTIZIONE /foo
mv /foo/cmdline.txt.bak /foo/cmdline.txt
umount /foo
reboot
```

Questo annulla il boot dalla root cifrata, e il Pi bootierà di nuovo dalla
root in chiaro. Avere un filesystem non riparabile è pericoloso, quindi
chiedi consiglio :-).

### 4. Ridimensiona il filesystem root alla dimensione minima possibile

Esegui:

```
resize2fs -fM -p /dev/nvme0n1p2
```

Che produrrà qualcosa del tipo:

```
Resizing the filesystem on /dev/nvme0n1p2 to 2345678 (4k) blocks.
```

Il numero di blocchi (`2345678` in questo esempio) è il numero da annotare.

Ora estrarremo un checksum, per assicurarci che dopo averlo copiato avanti
e indietro non ci siano state corruzioni di dati.

### 5. Calcola il checksum del tuo filesystem root

Esegui:

```
dd bs=4k count=XXXXX if=/dev/nvme0n1p2 | sha1sum
```

dove devi sostituire `XXXXX` con il numero di blocchi che hai annotato nel
passo precedente.

Prendi nota del checksum risultante. Fare una foto allo schermo funziona :)

### 6. Copia il filesystem root sulla chiavetta USB

Se la tua chiavetta USB è `/dev/sda` (probabile), allora possiamo copiare il
filesystem root ridotto con:

```
dd bs=4k count=XXXXX if=/dev/nvme0n1p2 of=/dev/sda
```

dove devi sostituire `XXXXX` con il numero di blocchi annotato in un passo
precedente.

Ci vorrà un po', quindi porta pazienza e aspetta.

### 7. Verifica l'integrità della copia

Calcoliamo ora il checksum di quello che abbiamo copiato sulla chiavetta USB,
per assicurarci che sia stato salvato correttamente:

```
dd bs=4k count=XXXXX if=/dev/sda | sha1sum
```

dove devi sostituire `XXXXX` con il numero di blocchi annotato in un passo
precedente.

Questo dovrebbe corrispondere perfettamente al checksum trovato al passo 5. Se
non è così, dovresti usare una chiavetta USB diversa. Se non ne hai un'altra,
allora puoi annullare le modifiche fatte finora guardando il passo 3 di questa
sezione, e riavviare il Pi.

### 8. Crea il device cifrato

Questo è il comando che ho scelto:

```
cryptsetup --type luks2 --cipher aes-xts-plain64 --hash sha256 -–key-size 256 luksFormat /dev/nvme0n1p2
```

Al giorno d'oggi il default è usare `argon2id` come Password-Based Key
Derivation Function, e il PI5 è abbastanza veloce da usare il tempo di
iterazione predefinito di 2000ms.

Questo comando chiederà una passphrase, che è ciò che servirà ogni volta che
il sistema si avvia per sbloccare il disco root e permettere al sistema di
continuare il boot.

Assicurati di scegliere una passphrase di dimensioni decenti, e dai
un'occhiata a [questa pagina](https://xkcd.com/936/) se hai bisogno di
consigli.


> ⚠️ Ricorda che, a meno che non l'abbia cambiato, il layout della tastiera
> per questa shell è English US. Questo potrebbe differire dal layout reale
> della tua tastiera configurato sull'installazione del Raspberry Pi.

### 9. Copia il filesystem root sul device cifrato

Apriamo la nostra root cifrata:

```
cryptsetup luksOpen /dev/nvme0n1p2 cryptroot
```

inserisci la passphrase che hai impostato al passo 8. Questo renderà disponibile
un nuovo device node `/dev/mapper/cryptroot`, sul quale possiamo ora copiare il
nostro filesystem root:

```
dd bs=4k count=XXXXX if=/dev/sda of=/dev/mapper/cryptroot
```

dove devi sostituire `XXXXX` con il numero di blocchi annotato in un passo
precedente.

Calcoliamo il checksum della copia per assicurarci che quello che abbiamo
copiato corrisponda a quello sulla chiavetta USB, trovato al passo 7:

```
dd bs=4k count=XXXXX if=/dev/mapper/cryptroot | sha1sum
```

dove devi sostituire `XXXXX` con il numero di blocchi annotato in un passo
precedente.

Se c'è un mismatch, ahia - il tuo filesystem root dovrebbe essere ancora al
sicuro sulla chiavetta USB, ma a questo punto significa che o la chiavetta
USB è difettosa o lo storage di destinazione è rotto. In entrambi i casi non
è piacevole, e consiglierei di scoprire chi è il colpevole e sostituirlo.
Ma per ora andiamo avanti.

### 10. Controlla il filesystem root e ridimensionalo

Assicuriamoci che il filesystem sia ancora sano:
```
e2fsck /dev/mapper/cryptroot
```

e ridimensioniamolo alla dimensione massima del device sottostante:
```
resize2fs -f /dev/mapper/cryptroot
```

a questo punto, possiamo uscire dalla shell initramfs e il processo di boot
continuerà normalmente.

```
exit
```

## Rendere le modifiche permanenti

Finora, dovremmo aprire la partizione cifrata ogni volta a mano nella shell
initramfs, e questo è piuttosto scomodo.

Inoltre, avremmo sempre bisogno di una tastiera e uno schermo collegati al
Pi per inserire la password, e anche questo è piuttosto brutto.

Quindi ora istruiamo gli initramfs-tools a tentare di aprire la root cifrata
automaticamente e attendere che un utente inserisca la password.

Configuriamo anche un server SSH nell'initramfs che permette a un utente
remoto di connettersi e sbloccare il device root da remoto.

### 1. Configura la partizione cifrata in `/etc/crypttab`

Il tuo `/etc/crypttab` dovrebbe avere questo aspetto:

```
# <target name> <source device>         <key file>      <options>
cryptroot       /dev/nvme0n1p2          none            luks
```

### 2. Configura la root cifrata in `/etc/fstab`

Il device per il filesystem root dovrebbe essere cambiato al device cifrato
`/dev/mapper/cryptroot`.

È probabile che il tuo device root sia specificato con una riga `PARTUUID=`.
Questi vengono mostrati nell'output di `lsblk` se esegui `lsblk -o
NAME,TYPE,MOUNTPOINT,PTUUID`.

In ogni caso, devi cambiare la riga per la partizione `/` in:
```
/dev/mapper/cryptroot /               ext4    defaults,noatime  0       1
```

### 3. Aggiungi SSH all'initramfs

Installiamo i pacchetti necessari:

```
> sudo apt install dropbear-initramfs
```

Questo installerà gli hook necessari per aggiungere il demone SSH dropbear
nell'initramfs, e genererà tutte le host key.

Questo setup permette solo l'autenticazione con chiave pubblica SSH, quindi
devi aggiungere la tua chiave SSH al file
`/etc/dropbear/initramfs/authorized_keys`.

Poi, le host key generate per l'initramfs sono diverse da quelle dell'host.
Questo significa che il tuo client SSH si lamenterà ogni volta che si connette
al demone SSH nell'initramfs perché vedrà un mismatch di chiavi con l'host.

Quindi, possiamo convertire quelle dell'host per l'initramfs:

```
> cd /etc/ssh
> dropbearconvert openssh dropbear ssh_host_ecdsa_key /etc/dropbear/initramfs/dropbear_ecdsa_host_key
> dropbearconvert openssh dropbear ssh_host_ed25519_key /etc/dropbear/initramfs/dropbear_ed25519_host_key
> dropbearconvert openssh dropbear ssh_host_rsa_key /etc/dropbear/initramfs/dropbear_rsa_host_key
```

e ora generiamo le chiavi pubbliche corrispondenti:
```
> cd /etc/dropbear/initramfs
> dropbearkey -y -f dropbear_ecdsa_host_key | grep ^ecdsa > dropbear_ecdsa_host_key.pub
> dropbearkey -y -f dropbear_ed25519_host_key | grep ^ssh > dropbear_ed25519_host_key.pub
> dropbearkey -y -f dropbear_rsa_host_key | grep ^ssh > dropbear_rsa_host_key.pub
```

E siamo a posto!

### 4. Rigenera l'initramfs

Come fatto in precedenza -- tuttavia ora che abbiamo modificato `crypttab` e
`fstab`, initramfs eseguirà tutto il plumbing necessario per tentare di aprire
la root cifrata.

```
> sudo update-initramfs -u
update-initramfs: Generating /boot/initrd.img-6.12.62+rpt-rpi-2712
'/boot/initrd.img-6.12.62+rpt-rpi-2712' -> '/boot/firmware/initramfs_2712'
```

Dato che abbiamo anche aggiunto dropbear, l'initramfs avvierà anche il demone
SSH mentre attende che la root venga sbloccata.

## Ha funzionato?

Ma certo! Se sei arrivato fin qui, congratulazioni! Ora puoi goderti il tuo
mini server Linux con root cifrata. Al riavvio, collegati via SSH e esegui:

```
cryptroot-unlock
```

E dopo aver inserito la password del device cifrato, la connessione si chiuderà
e il tuo server bootierà.

Happy hacking!
