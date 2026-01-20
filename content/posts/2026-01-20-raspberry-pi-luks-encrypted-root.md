---
title: Raspberry PI 5 encrypted root with LUKS
date: 2026-01-20
tags: [linux, raspberrypi, sysadmin]
categories: [development]
---

## Preface

So I started running [home assistant](https://www.home-assistant.io/) at home
on a raspberry PI 5 machine and I just installed HAOS on an SD. I then started
growing deeply uncomfortable on storing credentials in the HA filesystem in
clear text (any obfuscation is not enough).

Considering configuring an encrypted root with HAOS is simply not possible
without forking it, and also considering that dedicating a RPI5 entirely to HAOS
is a waste of resources, I decided to add an SSD to the Pi, boot it with
raspbian and then run HAOS inside a VM.

This way, I can have an encrypted root on the main host, thus encrypting the
entire HAOS VM.

Furthermore I can now snapshot the entire HAOS VM and I have much more
flexibility in managing it. Last but not least, I can also use the remaining RPI
CPU and RAM for something else.

## Requirements

First, a big thank you [to this
post](https://rr-developer.github.io/LUKS-on-Raspberry-Pi/) that gave me the
initial pointers on how to set this up. But that 2021 post is now slightly
outdated, and many steps are no longer necessary.

- An RPI5 with debian 13 or newer
- A decent and reliable USB stick that can be fully erased
- A keyboard and monitor directly connected to the RPI

## Overview

The overall idea is:

- We prepare an initrd that contains the `resize2fs` tool that allows shrinking
  and enlarging `ext4` filesystems
- We configure the system to boot off an encrypted root that does not exist yet,
  thus forcing the system to fall into the initrd.
- While in initrd, we shrink the root filesystem to the smallest possible size
- We copy the root filesystem from the cleartext device over to the USB stick
- We create the encrypted device using LUKS
- We copy back the root filesystem from the USB stick back to the encrypted
  device
- We extend the root filesystem to the maximum size
- We configure SSH in the initrd so that you can unlock it even after you've
  deployed your raspberry pi in a location without a keyboard or screen.

Ready? Set, go!

## Preparing the initramfs

We want to tell the firmware to load an initramfs, that's a RAM disk with a
minimal Linux environment that has the necessary pieces to open an encrypted
device and unlock it - provided the user inserts the right password.

By default, [the firmware loads the
kernel_2712.img](https://www.raspberrypi.com/documentation/computers/config_txt.html#kernel)
kernel on the raspberry pi 5, as that is the optimised one.

If the
[`auto_initramfs`](https://www.raspberrypi.com/documentation/computers/config_txt.html#auto_initramfs)
option is set to `1`, then the firmware will also load the corresponding
`initramfs_2712` image in memory and pass its address to the kernel.

When creating a new initramfs, the
`/etc/initramfs/post-update.d/z50-raspi-firmware` script ensures to place a copy
of the most recent initramfs in the firmware directory, and name it as
`initramfs_2712`. So all the heavy lifting is already done for us!

### 1. Ensure the firmware loads the initrd

Ensure you have in `/boot/firmware/config.txt`:

```
auto_initramfs=1
```
but this should already be the case.

### 2. Tell the kernel to mount root from the encrypted device

Create a backup of your current `cmdline.txt`, should we need to restore it
later:

```
> sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.bak
```

Then edit `/boot/firmware/cmdline.txt` and replace any `root=XXX` setting with
`root=/dev/mapper/cryptroot`.

For example, my `cmdline.txt` looks like this:
```
console=tty1 root=/dev/mapper/cryptroot rootfstype=ext4 fsck.repair=yes rootwait
```

### 3. Install cryptsetup, initramfs tools and busybox

Run:

```
> sudo apt install cryptsetup initramfs-tools busybox
```

If some of these are already installed, that's perfectly fine!

Verify that your PI AES hardware acceleration is working as expected:

```
> cryptsetup benchmark -c aes-xts
# Tests are approximate using memory only (no storage IO).
# Algorithm |       Key |      Encryption |      Decryption
    aes-xts        256b      1736.6 MiB/s      1804.6 MiB/s
```

you should get similar values.

### 4. Configure the initramfs to include `resize2fs`

Create a new `/etc/initramfs-tools/hooks/luks_hooks` file, containing:

```
#!/bin/sh -e

case $1 in
        prereqs) echo ""; exit 0;;
esac

. /usr/share/initramfs-tools/hook-functions

copy_exec /sbin/resize2fs /sbin
```

and making it executable:

```
> sudo chmod +x /etc/initramfs-tools/hooks/luks_hooks
```

### 5. Add disk encryption kernel modules to the initramfs

Add the following lines at the bottom of `/etc/initramfs-tools/modules`:

```
aes_ce_blk
sha2_ce
dm_crypt
```

### 6. Ask the initramfs to include *most* modules

The initramfs tools try to miminize the number of modules installed in the RAM
disk, doing some fancy detection of the hardware and the needed ones. However
this may fail and you may end up with a system that just hangs in the initramfs.

So let's edit `/etc/initramfs-tools/initramfs.conf` and ensure that the
`MODULES` line reads:

```
MODULES=most
```

### 7. Regenerate the initramfs

Let's now run this command to generate the initramfs for all installed kernels:
```
> sudo update-initramfs -u
update-initramfs: Generating /boot/initrd.img-6.12.62+rpt-rpi-2712
'/boot/initrd.img-6.12.62+rpt-rpi-2712' -> '/boot/firmware/initramfs_2712'
```

Let's check we have everything we need:

```
> lsinitramfs /boot/firmware/initramfs_2712 |grep -E 'sbin/(cryptsetup|resize2fs|fdisk)'
usr/sbin/cryptsetup
usr/sbin/resize2fs
usr/sbin/fdisk
```

and:

```
> lsinitramfs /boot/firmware/initramfs_2712 |grep -E 'aes.ce.blk|sha2.ce|dm.crypt'
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/arch/arm64/crypto/aes-ce-blk.ko.xz
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/arch/arm64/crypto/sha2-ce.ko.xz
usr/lib/modules/6.12.62+rpt-rpi-2712/kernel/drivers/md/dm-crypt.ko.xz
```

It is now time to reboot and get dropped into the `(initramfs)` shell! Connect
your disposable USB stick to the pi and:

```
> sudo reboot
```

## Tweaking the root disk in the initramfs shell

After a few attempts to mount `/dev/mapper/cryptroot`, the initramfs will give
up and drop you to a shell whose prompt is just `(initramfs) `. In this shell we
have root access and we can manipulate the block devices connected to the pi.

### 1. Ensure that you can access all needed devices

We need to access both the USB stick and your root device. Let's check it by
issuing `lsblk`.

You should see a `/dev/sda` device that's your USB stick, and a `/dev/mmcblk0`
device if you are using an SD card, or a `/dev/nvme0n1` device if you're using
an NVME drive.

### 2. Ensure that we can use the encryption algorithms

Let's re-run the benchmarks:

```
(initramfs) cryptsetup benchmark -c aes-xts
# Tests are approximate using memory only (no storage IO).
# Algorithm |       Key |      Encryption |      Decryption
    aes-xts        256b      1761.5 MiB/s      1813.9 MiB/s
```

If all is good, We can now proceed with our plan: shrink the root filesystem,
copy it over to the USB stick, create a new encrypted device and move the root
filesystem back to the encrypted device.

### 3. Check the root filesystem integrity

Run:

```
e2fsck -f /dev/nvme0n1p2
```

If `e2fsck` said that the filesystem is OK, proceed to the next step! Otherwise,
if there are some serious errors, it may be best to stop and undo the changes
done so far to avoid serious data corruption. It's time to restore the
`cmdline.txt` backup we did earlier.

Use `lsblk` to find the device name of the the `512M` partition - that'd be
`/dev/mmcblk0p1` if using an SD card or `/dev/nvme0n1p1` if using an NVME drive.

Then, let's mount it, restore the former `cmdline.txt` and reboot:

```
mkdir -p /foo
mount /dev/YOURPARTITION /foo
mv /foo/cmdline.txt.bak /foo/cmdline.txt
umount /foo
reboot
```

That'll undoes the boot from the encrypted root, and the pi will boot back from
the cleartext root. Having a non-repairable filesystem is dangerous, so seek
some advice :-).

### 4. Resize the root file system to the smallest possible size

Run:

```
resize2fs -fM -p /dev/nvme0n1p2
```

That'll output something like:

```
Resizing the filesystem on /dev/nvme0n1p2 to 2345678 (4k) blocks.
```

The number of blocks (`2345678` in this example) is the number to take note of.

We're now going to extract a checksum of it, so to ensure that after we copy it
around and back no data corruption took place.

### 5. Compute the checksum of your root filesystem

Run:

```
dd bs=4k count=XXXXX if=/dev/nvme0n1p2 | sha1sum
```

and take note of the resulting checksum. Taking a picture of the screen works :)

### 6. Copy the root filesystem over to the USB stick

If your USB stick is `/dev/sda` (likely), then we can copy the shrunk root
filesystem to it with:

```
dd bs=4k count=XXXXX if=/dev/nvme0n1p2 of=/dev/sda
```

This will take some time, so please be patient and wait.

### 7. Check copy integrity

Let's now calculate the checksum of what we copied so far to the USB stick, to
ensure it was stored properly:

```
dd bs=4k count=XXXXX if=/dev/sda | sha1sum
```

This should perfectly match with the checksum we found at step 5. If this is not
the case, you should use a different USB stick. If you don't have another one,
then you can undo the changes so far by looking at step 3 in this section, and
reboot your pi.

### 8. Create the encrypted device

This is the command I settled on:

```
cryptsetup --type luks2 --cipher aes-xts-plain64 --hash sha256 -–keysize 256 luksFormat /dev/nvme0n1p2
```

The defaults nowadays are to use `argon2id` as Password-Base Key Derivation
Function, and the PI5 is fast enough to use the default 2000ms iteration time.

This command will ask for a passphrase, that's what we'll need every time the
system boots to unlock the root disk and let the system continue booting.

Ensure to choose a decently sized passphrase, and check out [this
page](https://xkcd.com/936/) if you need advice.

### 9. Copy back the root filesystem to the encrypted device

Let's open our encrypted root:

```
cryptsetup luksOpen /dev/nvme0n1p2 cryptroot
```

key in the passphrase that you inserted at step 8. This will make available a
ned `/dev/mapper/cryptroot` device node, on which we can now copy back our root
filesystem:

```
dd bs=4k count=XXXXX if=/dev/sda of=/dev/mapper/cryptroot
```

and let's calculate the checksum of the copy so to ensure that what we've copied
back matched what's on the USB stick, that we found at step 7:

```
dd bs=4k count=XXXXX if=/dev/mapper/cryptroot | sha1sum
```

if there's a mismatch, ouch - your root filesystem should still be safe on the
USB stick, but at this point this means either the USB stick is faulty or the
target storage is broken. Either case it's not pleasant, and I'd suggest to find
out who's at fault and replace it. But for now we should carry on.

### 10. Check the root filesystem and resize it back

Let's ensure the filesystem is still sane:
```
e2fsck /dev/mapper/cryptroot
```

and let's resize it back to the maximum size of the underlying device:
```
resize2fs -f /dev/mapper/sdcard
```

at this point, we can exit from the initramfs shell and the boot process will
continue normally.

```
exit
```

## Making changes permanent

So far, we'd need to open the encrypted partition every time by hand in the
initramfs shell, and that's quite uncomfortable.

Furthermore, we'd always need a keyboard and screen hooked up to the pi to
insert the password, and that's also pretty ugly.

So we now instruct the initramfs tools to attempt opening the encrypted root
automatically and wait for a user to insert the password.

We also set up an SSH server in the initramfs that allows a remote user to
connect and unlock the root device remotely.

### 1. Set up the encrypted partition in `/etc/crypttab`

Your `/etc/crypttab` should look like the following:

```
# <target name> <source device>         <key file>      <options>
cryptroot       /dev/nvme0n1p2          none            luks
```

### 2. Set up the encrypted root in `/etc/fstab`

The device for the root filesystem should be changed to the
`/dev/mapper/cryptroot` encrypted device.

It is likely that your root device would be specified with a `PARTUUID=` line.
These are displayed in `lsblk` output if you run `lsblk -o
NAME,TYPE,MOUNTPOINT,PTUUID`.

Anyway, you need to change the line for the `/` partition to:
```
/dev/mapper/cryptroot /               ext4    defaults,noatime  0       1
```

### 3. Add initramfs SSH

Let's install the necessary packages:

```
> sudo apt install dropbear-initramfs
```

This will install the necessary hooks to add the dropbear SSH daemon in the
initramfs, and generate all the host keys.

This setup only allows SSH public key authentication, so you need to add your
own SSH key to the `/etc/dropbear/initramfs/authorized_keys` file.

Then, the host keys generated for the initramfs are different from the ones in
the host. This means that your SSH client will complain every time it connects
to the SSH daemon in the initramfs as it'll see a key mismatch with the host.

So, we can convert the ones in the host to the initramfs:

```
> cd /etc/ssh
> dropbearconvert openssh dropbear ssh_host_ecdsa_key /etc/dropbear/initramfs/dropbear_ecdsa_host_key
> dropbearconvert openssh dropbear ssh_host_ed25519_key /etc/dropbear/initramfs/dropbear_ed25519_host_key
> dropbearconvert openssh dropbear ssh_host_rsa_key /etc/dropbear/initramfs/dropbear_rsa_host_key
```

and now let's generate the corresponding public keys:
```
> cd /etc/dropbear/initramfs
> dropbearkey -y -f dropbear_ecdsa_host_key | grep ^ecdsa > dropbear_ecdsa_host_key.pub
> dropbearkey -y -f dropbear_ed25519_host_key | grep ^ssh > dropbear_ed25519_host_key.pub
> dropbearkey -y -f dropbear_rsa_host_key | grep ^ssh > dropbear_rsa_host_key.pub
```

And we're good!

### 4. Regenerate the initramfs

As done previously -- however now that we've changed `crypttab` and  `fstab`,
initramfs will run all the necessary plumbing to try to open the encrypted root.

```
> sudo update-initramfs -u
update-initramfs: Generating /boot/initrd.img-6.12.62+rpt-rpi-2712
'/boot/initrd.img-6.12.62+rpt-rpi-2712' -> '/boot/firmware/initramfs_2712'
```

Given we've also added dropbear, the initramfs will also spawn the SSH daemon
when waiting for the root to be unlocked.

## Did it blend?

Of course it did! If you've made this far, congratulations! You can now enjoy
your mini Linux server with encrypted root. Upon reboot, just connect over SSH
to it, and run:

```
cryptroot-unlock
```

And after inserting your encrypted device password, the connection will close
and your server will boot.

Happy hacking!
