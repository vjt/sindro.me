---
title: Root cifrata su ZFS con FreeBSD
date: 2023-08-13
tags: [freebsd, sysadmin]
---

![Un server FreeBSD cifrato avvolto in scudi traslucidi, il cloud AWS che si sgretola sullo sfondo](/posts/2023-08-13-freebsd-encrypted-root-on-zfs/cover.jpg)

## Premessa

Nel 2023, gestisco ancora il mio mailserver. Sì, perché mi piace avere il
controllo (almeno in parte) della mia vita digitale, e mi piace avere
diversi nomi di dominio su cui tenere le mie cose. Tuttavia, stavo pagando
30€/mese ad AWS per avere in cambio 2 core, 2GiB di RAM e 40G di disco,
appena sufficienti per far girare IMAP+SMTP+MySQL+Clamd, figurarsi qualsiasi
forma di protezione antispam o ricerca full-text nel corpo delle email.

Insomma, stavo pagando un botto di soldi per far girare un servizio merdoso,
e avevo persino pensato di chiudere tutto e spostare la posta e i siti web
su qualche servizio completamente managed.

## Però voglio ancora farlo

Beh, per ospitare quattro domini con solo qualche redirect email più i siti
web che gestisco, avrei speso di più di quanto stavo già pagando,
incatenandomi per di più a qualche fornitore di servizi e alle sue politiche.

Quindi, volevo usare FreeBSD e ho cominciato a cercare nella [pagina degli
ISP](https://www.freebsd.org/commercial/isp/) fino a decidere di valutare
[Hetzner](https://www.hetzner.com/cloud) e
[netcup](https://www.netcup.eu/vserver/vps.php), che offrono entrambi
prezzi aggressivi e un buon vecchio VPS senza fronzoli.

## Scelta del provider

Alla fine, ho scelto un netcup VPS 1000 che mi dà, a 1/3 del prezzo
che pagavo ad AWS, 4 volte le risorse: 6 core, 8GiB di RAM, 160GiB di
SSD RAID10 e un'installazione FreeBSD completamente libera e senza
limitazioni.

Tuttavia, l'immagine base fornita da Netcup ha alcune limitazioni:

- Gira su UFS
- Non ha una partizione di swap
- Non ha cifratura

## Fare un piano

Dato che ero già in fase di configurazione e non volevo ricominciare da zero
(questo è un server vecchio stile, gestito a mano, zero automazione) ho
deciso di:

* Avviare server temporanei su Hetzner per sperimentare
* Cercare l'incantesimo necessario per avere una macchina con cifratura
  completa del disco che booti correttamente
* Copiare la / dal server netcup a Hetzner e vedere se boota
* Ripetere il processo
* Una volta che l'incantesimo è stabile:
  * Avviare un server target su Hetzner per tenere temporaneamente tutti i dati
  * Riavviare il server sorgente su netcup da un CD per fare rsync di tutti i dati su Hetzner
  * Azzerare il disco del server netcup e ricreare tutte le partizioni e i filesystem
    come piace a me
  * Rsync di tutti i dati da Hetzner a netcup e riavvio

## Esecuzione

Indovina un po', funziona davvero. Ho iniziato usando il CD di installazione
di FreeBSD, per poi rendermi conto che non avevo bisogno dell'installer perché
avevo già un sistema live da migrare, e ho finito per usare
[mfsbsd](https://mfsbsd.vx.sk/) sia per avviare il server target, sia per
avviare il server sorgente quando è stato il momento di copiare tutto
avanti e indietro.

Partendo da [questo thread sul forum di
FreeBSD](https://forums.freebsd.org/threads/howto-freebsd-10-1-amd64-uefi-boot-with-encrypted-zfs-root-using-geli.51393/)
e [questa pagina wiki per il boot
ZFS](https://wiki.freebsd.org/RootOnZFS/GPTZFSBoot) ho cucinato il seguente
incantesimo:

### Riavvio dal ramdisk e copia dei dati sul server temporaneo

Questo configura la rete, aggiorna rsync all'ultima versione, monta il
filesystem corrente in /mnt e fa rsync di tutto verso una posizione
di storage temporanea

```bash
ifconfig vtnet0 inet6 2a03:4000:2:33c::42 prefixlen 64
route -6 add default fe80::1%vtnet0
echo 'nameserver 2a03:4000:0:1::e1e6' > /etc/resolv.conf

pkg install rsync
pkg upgrade libiconv

mount /dev/vtbd0p2 /mnt

cd /mnt
rsync --archive --recursive --times --executability --hard-links \
  --links --perms --compress --exclude .sujournal --exclude .swapfile \
  --exclude .snap --exclude 'dev/*' --exclude 'srv/www/*/dev/*' \
  . root@m17.openssl.it:/mnt
```

### Creazione delle partizioni

Qui creiamo una partizione di boot che contiene l'eseguibile `gptboot`, la
cui responsabilità è caricare ed eseguire il loader di FreeBSD dalla
partizione `/boot` in chiaro.

Poi creiamo una partizione di `swap` e infine una partizione `zfs` che
conterrà il nostro pool ZFS.

```bash
gpart destroy -F vtbd0
gpart create -s GPT vtbd0

gpart add -s 472 -t freebsd-boot vtbd0
gpart bootcode -b /boot/pmbr -p /boot/gptboot -i 1 vtbd0

gpart add -s 1G -t freebsd-ufs -l boot vtbd0
gpart set -a bootme -i 2 vtbd0

gpart add -s 2G -t freebsd-swap -l swap vtbd0
gpart add -t freebsd-zfs -l root vtbd0
```

### Creazione di `/boot` e del device root cifrato

Qui creiamo un filesystem UFS per la partizione `/boot` non cifrata
che conterrà il kernel e il loader, e parte della chiave di cifratura usata
per cifrare la root. Quella chiave da sola non è sufficiente per accedere
al filesystem, perché è necessaria anche una passphrase aggiuntiva.

```bash
newfs -O 2 -U -m 8 -o space /dev/vtbd0p2
mkdir /tmp/ufsboot
mount /dev/vtbd0p2 /tmp/ufsboot
mkdir -p /tmp/ufsboot/boot/geli
dd if=/dev/random of=/tmp/ufsboot/boot/geli/vtbd0p4.key bs=64 count=1

geli init -e AES-XTS -l 256 -s 4096 -bd -K /tmp/ufsboot/boot/geli/vtbd0p4.key /dev/vtbd0p4
cp /var/backups/vtbd0p4.eli /tmp/ufsboot/boot/geli
geli attach -k /tmp/ufsboot/boot/geli/vtbd0p4.key /dev/vtbd0p4
```

### Creazione del pool ZFS

Questo è il mio layout, che uso principalmente per limitare l'eseguibilità
dei percorsi che non dovrebbero essere eseguibili, e anche per facilitare
lo snapshot di parti separate del filesystem che necessitano di strategie
di retention diverse

```bash
zpool create -R /mnt -O canmount=off -O mountpoint=none -O atime=off -O compression=lz4 tank /dev/vtbd0p4.eli
zfs create -o mountpoint=/ tank/ROOT
zfs create -o mountpoint=/tmp  -o exec=off     -o setuid=off  tank/tmp
zfs create -o canmount=off -o mountpoint=/usr                 tank/usr
zfs create                                     -o setuid=off  tank/usr/ports
zfs create -o canmount=off -o mountpoint=/var                 tank/var
zfs create                     -o exec=off     -o setuid=off  tank/var/log
zfs create -o atime=on         -o exec=off     -o setuid=off  tank/var/spool
zfs create                     -o exec=off     -o setuid=off  tank/var/tmp
zfs create -o canmount=off -o mountpoint=/srv                 tank/srv
zfs create                     -o exec=off     -o setuid=off  tank/srv/mail
zfs create                     -o exec=off     -o setuid=off  tank/srv/www
```

Infine, montiamo la partizione di boot UFS non cifrata sotto la gerarchia
del filesystem ZFS,

```bash
umount /dev/vtbd0p2
mkdir /mnt/ufsboot
mount /dev/vtbd0p2 /mnt/ufsboot
```

### Copia di tutto!

Ora è il momento di riprendere i dati dalla posizione temporanea dove erano
stati messi, e scriverli sul nuovo fiammante pool ZFS sulla root cifrata
con GELI:

```bash
rsync --archive --recursive --times --executability --hard-links \
  --links --perms --compress root@m17.openssl.it:/mnt/ /mnt

mv /mnt/boot/* /mnt/ufsboot/boot
rm -rf /mnt/boot
ln -s ufsboot/boot /mnt
```

Usiamo un symlink per puntare `/boot` a `/ufsboot/boot`, così il sistema
si comporterà come se `/boot` fosse una directory normale in `/`. È
necessario mantenere una sottodirectory `/boot` nella partizione `boot`
perché molto codice del loader dipende da percorsi `/boot` hardcoded.

### Cosa resta

`/etc/fstab`, con swap cifrata ovviamente:

```
/dev/vtbd0p2 /ufsboot ufs rw 0 1
/dev/vtbd0p3.eli none swap sw,ealgo=AES-XTS,keylen=128,sectorsize=4096 0 0
```


`/boot/loader.conf.d/geli.conf`:

```
geom_eli_load="YES"
geli_vtbd0p4_keyfile0_load="YES"
geli_vtbd0p4_keyfile0_type="vtbd0p4:geli_keyfile0"
geli_vtbd0p4_keyfile0_name="/boot/geli/vtbd0p4.key"
zfs_load="YES"
vfs.root.mountfrom="zfs:tank/ROOT"
```

`/etc/rc.conf`:

```
zfs_enable="YES"
```

## Ha funzionato?

Ma certo che sì! E gira felicemente da allora :-)

```bash
 03:44:10 root@m42:/srv/www/sindro.me/staging
 # uname -a
FreeBSD m42.openssl.it 13.2-RELEASE-p2 FreeBSD 13.2-RELEASE-p2 GENERIC amd64

 03:44:13 root@m42:/srv/www/sindro.me/staging
 # df -hT
Filesystem      Type      Size    Used   Avail Capacity  Mounted on
tank/ROOT       zfs       140G    6.7G    134G     5%    /
devfs           devfs     1.0K    1.0K      0B   100%    /dev
/dev/vtbd0p2    ufs       992M    189M    723M    21%    /ufsboot
tank/var/spool  zfs       134G    1.1M    134G     0%    /var/spool
tank/tmp        zfs       134G    220K    134G     0%    /tmp
tank/srv/mail   zfs       138G    4.8G    134G     3%    /srv/mail
tank/srv/www    zfs       136G    2.1G    134G     2%    /srv/www
tank/var/log    zfs       134G     13M    134G     0%    /var/log
tank/var/tmp    zfs       134G    224K    134G     0%    /var/tmp
tank/usr/ports  zfs       136G    2.6G    134G     2%    /usr/ports
/dev            nullfs    1.0K    1.0K      0B   100%    /srv/www/admin.openssl.it/dev
/dev            nullfs    1.0K    1.0K      0B   100%    /srv/www/mail.openssl.it/dev
/dev            nullfs    1.0K    1.0K      0B   100%    /srv/www/nhaima.org/dev
/dev            nullfs    1.0K    1.0K      0B   100%    /srv/www/spadaspa.it/dev
tank/usr/src    zfs       134G    773M    134G     1%    /usr/src
tank/usr/obj    zfs       134G     96K    134G     0%    /usr/obj
```

## E lo sblocco della root al boot?

Per i 2 anni e mezzo da quando ho scritto questo articolo sono stato alla
mercé della console VNC del VPS per inserire la password durante il boot,
il che è quanto meno scomodissimo.

Ma non più! [Ho configurato un ram disk
iniziale](https://sindro.me/posts/2026-01-28-freebsd-encrypted-zfs-remote-unlock/)
e ora posso sbloccare il VPS da remoto via SSH - senza bisogno del browser :-)
