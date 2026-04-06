---
date: 2014-02-28T03:00:00
title: goto fail;
tags: [apple, fail]
categories: [development]
---

## Con le sue stesse parole:

{{< figure alt="goto fail diff" src="/posts/2014-02-28-goto-fail/goto-fail.png" >}}

Sorgenti:
[55179.13.c](http://opensource.apple.com/source/Security/Security-55179.13/libsecurity_ssl/lib/sslKeyExchange.c?txt),
[55471.c](http://opensource.apple.com/source/Security/Security-55471/libsecurity_ssl/lib/sslKeyExchange.c?txt)

Differenze nel codice sorgente tra due versioni consecutive del
Security.framework, un componente MacOS/iOS. L'apparentemente innocuo goto
fail; in più è la causa di una [grave falla di sicurezza nella maggior parte dei
prodotti Apple](http://nakedsecurity.sophos.com/2014/02/24/anatomy-of-a-goto-fail-apples-ssl-bug-explained-plus-an-unofficial-patch/).
