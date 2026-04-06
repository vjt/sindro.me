---
title: How to Backup with Time Machine on a Network Share
author: Marcello Barnaba
date: 2007-11-02
tags: [apple, backup, debian, netatalk]
categories: [development]
---

*Ingredients*: Debian, Netatalk, Avahi, some trickery.

## Step 1: Recompile Netatalk with SSL Support

Recompile Netatalk with [SSL Support](http://www.blackmac.de/archives/58-Make-Netatalk-talk-to-Leopard-Mac-OS-X-10.5.html#extended).

You can safely ignore the ".passwd" stuff, because afpd uses PAM for user authentication.

Hint: Disable the atalk protocol handlers in `/etc/default/netatalk` for a faster startup:

```
# Set which daemons to run (papd is dependent upon atalkd):
ATALKD_RUN=no        # appletalk protocol
PAPD_RUN=no          # printer sharing daemon (printers are soooo '90s)
CNID_METAD_RUN=yes   # don't remember but is needed, rtfm!
AFPD_RUN=yes         # you will always need this
TIMELORD_RUN=no      # my time lord's name is <a href="http://openntpd.org">openntpd</a>
A2BOOT_RUN=no        # boot? nah! :P
```

## Step 2: Create a share for time machine backup data, by adding e.g.

```
# path         name           perms     charset
/some/where/tm "Time Machine" allow:vjt volcharset:"UTF8" 
```

into `/etc/netatalk/AppleVolumes.default`.

## Step 3: Let the AFPD server show up in finder

Download the avahi service file, put it into `/etc/avahi/services` and reload avahi with `/etc/init.d/avahi-daemon reload` (*sorry, original links are broken*).

## Step 4: Set Up Time Machine Backup

You need two files on your afp network share: .com.apple.timemachine.supported and a dot-file named with your en0 MAC address. To create it, the easier way is to attach an USB/Firewire disk, rename it with the name of the intended network share (specified into the AppleVolumes file) and enable time machine on it.

Then, copy over the .00… file on the external disk into your home dir, eject the disk, mount the network share from the finder and copy the file there.

Finally, touch `.com.apple.timemachine.supported` onto the network share, and re-open time machine preferences: the size of your backup volume should be equal to the network share size :).

You cannot copy both files e.g. via scp and expect it to work: afpd ignores dot-files in shared directories, and dot-files created on the client machine appear as such:

```
-rw-r--r--  1 vjt  16 2007-11-02 15:50 :2e000855f00f00
-rw-r--r--  1 root  0 2007-11-02 15:19 :2ecom.apple.timemachine.supported
```

because afpd needs the dot-namespace:

```
drwxr-xr-x  2 vjt 40 2007-11-02 16:02 .AppleDB/
drwxr-xr-x  2 vjt  8 2007-11-02 16:02 .AppleDesktop/
```

It works:

![Time machine backing up](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/tm-backing-up.png)


Of course with a bit of cache trashing:

![Cache Trashing](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/tm-fscache-destroy-after-backup.png)

Have fun!

PS: You can use SMB shares too, as the hard link to directories stuff is
embedded into a .sparsebundle file created on the network share. An AFP share
has the added benefit of being indexable by spotlight, not to mention that your
Linux server will appear in the finder as a shiny Mac:

![shiny mac](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/shiny-mac-icon.png)

and not as a crashed windows pc:

![crashed pc](/posts/2007-11-02-how-to-backup-with-time-machine-on-a-network-share/crashed-pc-icon.png)

:)
