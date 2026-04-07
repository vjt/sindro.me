---
title: FreeBSD encrypted ZFS remote unlocking via SSH
date: 2026-01-28
tags: [ai-generated, freebsd, sysadmin]
categories: [development]
---

## Remote LUKS? Pfft. Here is how to SSH-Unlock a ZFS-Encrypted FreeBSD Root (The Hard Way)

If you run FreeBSD [like I do](https://sindro.me/posts/2023-08-13-freebsd-encrypted-root-on-zfs/), on a remote server with full disk encryption (ZFS on GELI), you know the panic of rebooting. You are always at the mercy of a KVM-over-IP or a VNC connection from the browser, to insert the root filesystem password at the kernel prompt.

Nevertheless, if you (like me) run a system with `kern.securelevel` > 0, then installing a new libc means rebooting single user and installing the updates over said KVM or VNC connection, that is _not ergonomic_ to say the least.

The standard solution is usually a pre-boot SSH environment. On Linux, dropbear-initramfs makes this trivial. On FreeBSD? You are building a custom mfsroot (memory file system) from scratch.

Most guides out there suggest using a static shell script as init. This works, but it’s miserable. You lose job control (no Ctrl+C), you have no proper TTY, and good luck if you need to debug network issues interactively.

I didn't want a hacky script. I wanted a real environment. I wanted `init`, `getty`, `login`, PAM authentication, and a ZFS chroot for maintenance - to install updates.

Here is how I built a robust remote unlocker for FreeBSD.

## The Problem with /bin/sh as Init

The naive approach is to compile a tiny ramdisk, shove a static sh binary in it, and tell the loader to run it as PID 1.

```bash
# This creates nightmares
cat > /sbin/init <<EOF
#!/bin/sh
/sbin/dropbear
exec /bin/sh
EOF
```

Why does this fail?

1. No job control: `/bin/sh` as PID 1 doesn't handle terminal sequences that trigger signals like `SIGINT`. If you run a command that hangs, you can't Ctrl+C out of it. You are stuck.

2. No switch-root (aka `reroot`). FreeBSD's way of switching the current root is built on the `RB_REROOT` flag of the [`reboot()` system call](https://man.freebsd.org/cgi/man.cgi?query=reboot&apropos=0&sektion=2&manpath=FreeBSD+14.3-RELEASE&arch=default&format=html), but its use [is restricted to PID 1](https://man.freebsd.org/cgi/man.cgi?query=reboot&apropos=0&sektion=2&manpath=FreeBSD+14.3-RELEASE&arch=default&format=html). So `reboot(8)` [sends a signal to `init(8)`](https://cgit.freebsd.org/src/tree/sbin/reboot/reboot.c#n233) to shutdown or reroot the system. If your init is a shell script, the system hangs instead of pivoting.

## The Architecture

To solve this, we need to replicate the FreeBSD boot process in miniature. My `mfsroot` contains:

1. Real `/sbin/init`: The actual FreeBSD init binary handles signal propagation and process reaping.
2. Real `/usr/libexec/getty`: Sets up the TTY properly so job control works.
3. Real `/usr/bin/login` + PAM: Authenticates against the real root password hash copied from the host.
4. ZFS Tools: To import the pool and chroot into the main system for emergency updates without fully booting.

## The `mkunlock` Script

I wrote a script to automate the generation of this image. It grabs necessary binaries (including dynamic libraries via `ldd`), configures a minimal PAM stack, and preps the RC scripts.

Here is the logic flow:

1. Build Phase: Creates a staging directory structure.
2. Library Harvesting: Copies `dropbear`, `geli`, `init`, `login`, and their shared object dependencies (`libc`, `libpam`, `libgeom`, etc.).
3. Configuration: Generates a minimal `/etc/rc`, `/etc/ttys`, and `/etc/gettytab`.

## The "Magic" Reroot

The hardest part was getting the kernel to switch from the Ramdisk to the ZFS root after unlocking. The trick is using `reboot -r` (reroot) but ensuring the environment is clean.

We need to:

1. Set `kenv vfs.root.mountfrom="zfs:tank/ROOT"`.
2. Unmount the physical boot partition.
3. Remount root read-only (`mount -ur /`).
4. Run reroot via `/sbin/reboot -r`.

## Upsides

The resulting environment is beautiful. When the server boots, it loads the 30MB ramdisk and configures the network.

I SSH in and get a shell, and from the host console I can also log on with a password of the system, or another one if we don't want to copy over the target system's password hash to the unencrypted ramdisk.

Once inside, I have three custom tools:

* `unlock.sh`: Attaches the GELI provider using the keyfile and password.
* `enter.sh`: Imports the ZFS pool to a temporary mountpoint and chroots into it. This allows me to run `freebsd-update` (or nowadays `pkg upgrade` as I have pkgbase) or fix configs in Single User mode equivalence - without booting the full system.
* `boot.sh`: Performs the clean pivot to the decrypted OS.

## Downsides

There are of course a few downsides - as nothing comes for free!

* If the system reboots without your intervention, it'll end up exposing a dropbear on some port. I'm not using the standard one, but it is reachable nevertheless.
* If you use the same root password in the main system and in the rescue environment, you are exposing the hash in the unencrypted RAM disk.
* When the system is updated, you should re-run `mkunlock` to ensure the userland is in sync with the kernel.

## The Code

If you want to stop praying every time you type reboot, grab the script from my repo.

https://github.com/vjt/mfsroot-geli-dropbear

Download it, run it, and it'll create a `/boot/mfsroot.gz` file. You can then enable it at boot by editing your `loader.conf`:

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

Ensure to not have a `geom_eli_load="YES"` line in your `loader.conf` otherwise the kernel will detect your encrypted root and ask you to insert its password!

FreeBSD is powerful, but sometimes you have to scratch your own itch!
