---
date: 2008-01-16
tags: [sysadmin, python]
title: Come compilare python2.5 su SCO_SV
---

{{< retrospective year="2026" >}}
Sia Python 2.5 (EOL 2011) che SCO OpenServer sono estinti. SCO/Xinuos è fallita, e lo stesso Python 2 ha raggiunto la fine del ciclo di vita a gennaio 2020. Questo è un fossile digitale.
{{< /retrospective >}}

- Devi avere PTH installato, e forse altre librerie.
- Testato su `SCO_SV os507 3.2 5.0.7 i386`

Se hai UDK, lancia:

```sh
$ CFLAGS='-I/usr/local/include -belf' LDFLAGS='-L/usr/local/lib' \
  ./configure --with-threads --with-pth --disable-shared --disable-ipv6
```

- Aggiungi `/usr/local/include` a `BASECFLAGS` nel `Makefile` (autocrap fa schifo).
- Patcha `Modules/ctypes/_ctypes_test.c` mettendo un `#ifdef HAVE_LONG_LONG` attorno alle funzioni che usano `PY_LONG_LONG` (suggerimenti: righe `384` e `318`).
- Patcha `Objects/longobject.c` e alla riga `817` metti la macro `IS_LITTLE_ENDIAN` prima del blocco `#ifdef HAVE_LONG_LONG`, e metti `_PyLong_FromSsize_t` e `_PyLong_FromSize_t` dopo il blocco `HAVE_LONG_LONG`.

Se hai GCC, lancia:

```sh
$ CFLAGS='-I/usr/local/include' LDFLAGS='-L/usr/local/lib'            \
  ./configure --with-threads --with-pth --disable-shared --disable-ipv6
```

Sia con UDK che con GCC:

- Modifica `pyconfig.h` e commenta il define di `socklen_t`
- Modifica `Modules/socketmodule.c` e alla riga 226 aggiungi `|| defined(SCO5)` per definire `INET_ADDRSTRLEN`.
- Lancia `make` (o `gmake` se preferisci)
- Rimarrai senza `_curses.so`, `_curses_panel.so`, `_locale.so` e `readline.so` se usi GCC, e anche senza `pyexpat`, `elementtree` e `sha512` se usi UDK.


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
