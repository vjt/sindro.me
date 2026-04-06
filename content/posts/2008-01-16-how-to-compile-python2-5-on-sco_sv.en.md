---
date: 2008-01-16
tags: [compile, openserver, python, sco]
title: How to compile python2.5 on SCO_SV
categories: [development]
---

- You must have PTH installed, and maybe other libs.
- This was tested on `SCO_SV os507 3.2 5.0.7 i386`

If you have UDK, run:

```sh
$ CFLAGS='-I/usr/local/include -belf' LDFLAGS='-L/usr/local/lib' \
  ./configure --with-threads --with-pth --disable-shared --disable-ipv6
```

- Add `/usr/local/include` to `BASECFLAGS` in `Makefile` (autocrap sucks).
- Patch `Modules/ctypes/_ctypes_test.c` by putting an `#ifdef HAVE_LONG_LONG` around functions that use `PY_LONG_LONG` (hints: lines `384` and `318`).
- Patch `Objects/longobject.c` and on line `817` put the `IS_LITTLE_ENDIAN` macro before the `#ifdef HAVE_LONG_LONG` block, and put `_PyLong_FromSsize_t` and `_PyLong_FromSize_t` after the `HAVE_LONG_LONG` block.

If you have GCC, run:

```sh
$ CFLAGS='-I/usr/local/include' LDFLAGS='-L/usr/local/lib'            \
  ./configure --with-threads --with-pth --disable-shared --disable-ipv6
```

Either with UDK or GCC:

- Edit `pyconfig.h` and comment out the `socklen_t` define
- Edit `Modules/socketmodule.c` and on line 226 add `|| defined(SCO5)` in order to define `INET_ADDRSTRLEN`.
- Run `make` (or `gmake` if you wish)
- You will be left without `_curses.so`, `_curses_panel.so`, `_locale.so` and `readline.so` if using GCC and also `pyexpat`, `elementtree` and `sha512` if using UDK.


```
      __   ____  __ __  ____     __
      \ \ / /  \/  |  \/  \ \   / /
       \ V /| |\/| | |\/| |\ \ / / 
        | | | |  | | |  | | \ V /_ 
        |_| |_|  |_|_|  |_|  \_/(_)

```

```sh
[vjt@os507 ~/Python-2.5.1-vjt] $ python
Python 2.5.1 (r251:31337, Sep 13 2007, 22:40:33) 
[GCC 4.2.1] on sco_sv3
Type "help", "copyright", "credits" or "license" for more information.
>>> import socket
>>> 
```

```sh
[vjt@os507 ~] $ hg clone http://code.wuhrer.thc/hg/Antani
destination directory: Antani
http authorization required
```

!! YAY! :D
