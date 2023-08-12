---
title: "10.5.2 Odissey: a small journey in Mac OS X services and components"
date: 2008-02-15
tags: [apple, disaster recovery, internals, macos]
---


Well, I'm really happy with OSX 10.5.2. Even I'm not the one that blamed Apple
for the translucent menu bar that everyone dislikes.. well, I like it. I don't
care about the TM menu bar tool, because I haven't bought (yet) the nifty Time
Capsule, I like the spinner in the Airport menu and, most of all, I really like
the updates to the `BluetoothSCOAudioDriver.kext` that drives my bluetooth
headset.

Spotlight also feels faster and faster on every upgrade, and I'm a heavy
spotlight user, so this makes me really happy. Thanks Apple engineers!

Back to the topic: why odissey? Because as per [my battery
hints](../2008-01-31-how-to-keep-your-apple-notebook-battery-healthy/), I managed
to make my MacBook2,1 SHUT DOWN while at 74% of the "Writing files" phase of
the combo update... resulting in a completely broken system, as every geek
could imagine :). Apple updated some libraries, and upon reboot simply nothing
worked, and the darwin console was filled with **lots** of error messages.

The standard apple fanb^Wuser would have simply archived and installed his
system, but hey, I'm a proud geek! I know from experience that disaster
recovery situations are the best ones to learn something about an operating
system, because you have to help the system boot up, bringing services up by
hand, and find some way to re-apply the combo update without using the easy
Aqua interface.

Luckily enough, on OSX every GUI has its CLI counterpart, following the best
"UNIX guidelines" of interest separation and well designed architecture.
Furthermore, OSX takes this approach one step further, following the best
software engineering principles, where functionalities are implemented in
Frameworks and both the GUI and CLI interfaces use it. Well done!

The odissey started with a `CMD-S` to boot in single user mode, a `/sbin/fsck
-fy`, and a `/sbin/mount -uw /` to get a writable root. I started directly with
a `hdiutil attach -noverify -verbose -mount required
/Users/vjt/Downloads/MacOSXUpdCombo10.5.2.dmg` in order to mount the update
disk image, but it failed because the `diskarbitrationd` daemon wasn't running.

So, I fired up `launchctl` and issued `load
/System/Librar/LaunchDaemons/com.apple.diskarbitrationd.plist`, when I
discovered that it needed both the `configd` daemon and the `notifyd` daemon,
so I loaded them up both via launchctl and.. **YAY**! The disk image was
correctly mounted in `/Volumes/Mac OS X Update Combined`!

Here things started to complicate a bit, because an easy task like issuing
`installer -package MacOSXUpdCombo10.5.2.pkg -target /` failed with

> `NSInvalidArgumentException in [IFRunnerProxy
> requestKeyForRights:askUser:] unrecognized selector sent to instance
> 0x79ac50.`

Well, here the Objective-C method was pretty self-explaining, the installer was
trying to ask the user permission to install the package. That's quite strange,
because I was running the `installer` command as root, so no request should
have been asked.

 I started scratching my head, and thought about the `DirectoryServices`, maybe
because they were unavailable "something wrong"(tm) was happening?

OK, let's try injecting the `com.apple.DirectoryServices` property list into
`launchd`.. it didn't work and `dyld` spit out this enlightening error message:

> `com.apple.DirectoryServices[11980]: dyld: lazy symbol binding failed: Symbol
> not found: _res_interrupt_requests_enable voyager
> com.apple.DirectoryServices[11980]: Referenced from:
> /usr/sbin/DirectoryService com.apple.DirectoryServices[11980]: Expected in:
> /usr/lib/libresolv.9.dylib`

**ARGH**! Something has changed into libresolv! I was having 10.5.1's
DirectoryServices.. with 10.5.2's libresolv! Gotta restore the old version to
make DS run. I first tried with a raw `netcat` network copy from another 10.5.1
box, but with my surprise the three-way handshake wasn't completed between the
two endpoints so no data could be transferred. Phew.

But luckily, because I already brought up the `diskarbitration` daemon, I could
easily put the library on an **USB** storage device, plug it in and have it
mounted in /Volumes. It did work and Directory Services were up&#38;running..
but still the same ugly `NSInvalidArgumentException` error when launching the
`installer` utility. Sigh. :(

At this point, I gave up because my journey had been interesting enough and I
had a really more comfortable way to fix up my problem: a **USB**-attached hard
disk with a vanilla Leopard installation, from which I could boot up my
MacBook, double click the disk image from the Finder and lazily launch an
`installer -target /Volumes/disk0 -package /Volumes/Mac OS X Update
Combined/MacOSXUpdCombo10.5.2.pkg` to re-run all the upgrade procedures that
would fix my Leopard installation. So I followed this path, because I had some
work to do and could not persevere in my geeky journey with the Darwin console,
even if it had been really entertaining. :)

After the installer completed its job, I rebooted and a shiny new 10.5.2
greeted me with the usual Mac **OS X** login window that on my box sports the
"All your base are belong to us" slogan ;).

Hope you enjoyed this journey as I did, and if you're a Linux fanb^Wuser don't
underestimate the cleanliness and cleverness of Mac **OS X** that every Apple
geek tries to share with you!
