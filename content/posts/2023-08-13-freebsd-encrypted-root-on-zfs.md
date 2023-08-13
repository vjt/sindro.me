---
title: FreeBSD encrypted root on ZFS
date: 2023-08-13
tags: [freebsd, sysadmin]
---

## Preface

In 2023, I still run my own mailserver. Yes, because I like to keep control of
(at least part) my own digital life, and I enjoy having multiple domain names
on which I have stuff on. However, I was paying 30€/month to AWS to get in
exchange 2 cores, 2GiBs of RAM and 40G of disk, barely sufficient to run
IMAP+SMTP+MySQL+Clamd, let alone any form of spam protection or full-text
search on email bodies.

So, I was paying a lot of money to run a shitty service, and I even though
about shutting everything off and move my mail and my web sites onto some
form of fully hosted service.

## I still want to do it

Say what, to host four domains with just some email redirects plus the web
sites I run, I would have spent more I was paying to also cripple me to
some service vendor and their politics.

So, I wanted to run FreeBSD and I started scouting on the [ISPs
page](https://www.freebsd.org/commercial/isp/) until I decided to review
[Hetzner](https://www.hetzner.com/cloud) and
[netcup](https://www.netcup.eu/vserver/vps.php), that both offer aggressive
pricing and a old fashioned VPS and little more.

## Settling on a vendor

Eventually, I settled on a netcup VPS 1000 that gives me, for 1/3 of the price
I was paying to AWS, 4 times the resources: 6 cores, 8GiB of RAM, 160GiB of
RAID10 SSD and an uncrippled, completely totally free FreeBSD installation.

However, the base image that Netcup provides has some limitations:

- It runs on UFS
- It is lacking a swap partition
- It has no encryption

## Making a plan

As I was already into the configuration stage and I didn't want to restart
from scratch (this is an old-fashioned server, manually managed, no automation)
I decided to:

* Spin up temporary servers on hetzner to experiment
* Peruse for the incantation required to have a full disk encryption bootable
  machine
* Copy over the / from the netcup server to hetzner and see whether it boots
* Rinse and repeat
* Once the incantation is stable:
  * Boot a hetzner target server to temporarily hold all the data
  * Reboot the netcup source server from a CD so to rsync over all the data to hetzner
  * Scratch the netcup server disk and recreate all the partitions and filesystems
    the way I like
  * Rsync all data back from hetzner to netcup and reboot

## Executing it

Turns out, it actually works. I started using the FreeBSD installation CD, to
then realise I didn't need the installer at all, because I already had a live
system I was migrating, so I ended up using [mfsbsd](https://mfsbsd.vx.sk/)
to both spin up the target server, and as well to boot the source server when
it was time to copy everything back and forth.

Starting from [this freebsd forum
thread](https://forums.freebsd.org/threads/howto-freebsd-10-1-amd64-uefi-boot-with-encrypted-zfs-root-using-geli.51393/)
and [this wiki page for zfs
boot](https://wiki.freebsd.org/RootOnZFS/GPTZFSBoot) I ended up cooking the
following incantation:

### Reboot from ramdisk and copy over the data to the temp server

This configures the network, updates rsync to the latest version, mounts the
current filesystem in /mnt and rsyncs everything over to a temporary storage
location

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

### Create the partitions

Here we create a boot partition holding the `gptboot` executable, whose
responsibility is to load and execute the freebsd loader from the clear
text `/boot` partition.

Then we create a `swap` partition and eventually a `zfs` partition that
will contain our ZFS pool.

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

### Create `/boot` and the encrypted root device

Here we create a UFS filesystem for the unencrypted `/boot` partition
that'll hold the kernel and loader, and part of the encryption key used
to encrypt the root. That key alone is not sufficient to gain access to
the filesystem, as also an additional passphrase is needed.

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

### Create ZFS pool

This is my layout, that I mostly use to limit executability of paths that
should not be executable, and also for ease of snapshotting separate parts of
the filesystem that need different retention strategies

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

Eventually, mount the unencrypted UFS boot partition below the ZFS fs
hierarchy,

```bash
umount /dev/vtbd0p2
mkdir /mnt/ufsboot
mount /dev/vtbd0p2 /mnt/ufsboot
```

### Copy everything back!

Now it's time to get back the stuff from the temporary location it was placed to,
and write it onto the new shiny ZFS pool on the GELI-encrypted root:

```bash
rsync --archive --recursive --times --executability --hard-links \
  --links --perms --compress root@m17.openssl.it:/mnt/ /mnt

mv /mnt/boot/* /mnt/ufsboot/boot
rm -rf /mnt/boot
ln -s ufsboot/boot /mnt
```

We use a symlink to point `/boot` to `/ufsboot/boot`, so the system will behave
as if `/boot` was a normal directory in `/`. It's required to keep a `/boot`
subdir in the `boot` partition because plenty of loader code depends on
hardcoded `/boot` paths.

### What's left

`/etc/fstab`, with encrypted swap of course:

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

## Did it blend?

Yes of course it did! And it's happily working since :-)

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
