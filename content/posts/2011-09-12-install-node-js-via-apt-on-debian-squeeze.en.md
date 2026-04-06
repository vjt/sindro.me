---
date: "2011-09-12T12:00:00Z"
title: "Install node.js via APT on Debian Squeeze"
tags: [debian, nodejs, sysadm]
categories: [development]
---

Abstract: add [SID](http://www.debian.org/releases/sid/) APT source, configure
[APT Pinning](http://wiki.debian.org/AptPreferences) to give `squeeze` packages
priority over `SID` ones, rebuild the `nodejs` package under `squeeze`.

- Add **SID APT** source by creating `/etc/apt/sources.list.d/sid.list` (use
your [nearest mirror](http://www.debian.org/mirror/)):

```plaintext
deb http://ftp.us.debian.org/debian/ sid main
deb-src http://ftp.us.debian.org/debian/ sid main
```

- Configure APT pinning by creating /etc/apt/preferences.d/sid:

```
Package: *
Pin: release a=unstable
Pin-Priority: 50
```

- Install the latest version of libv8 manually, `libv8-3.8.9.20` at the time of writing this:

```
apt-get install libv8-3.8.9.20
```

- Download the nodejs package sources, dependencies and build them:

```
cd
apt-get source nodejs
apt-get build-dep nodejs
cd nodejs-*
debuild -nc -uc
```

- If you encounter build-dependency errors, you should try first to lower the
dependency in debian/control, both in Build-Depends and in Depends and re-run
`debuild`. If the build fails (e.g. with `undefined reference to 'ev_run'`) the
previous version is missing required functions. So, you must install the
updated versions of the required dependencies (e.g. `libev4`) from sid, using
`apt-get install name=version` e.g. `libev4=1:4.11-1`. I suggest this because
you’ll have to manually update packages installed from sid, so the lesser, the
best.

- Install the generated package
```
dpkg -i nodejs_*.deb nodejs-dev*.deb
```

- Profit :-)
