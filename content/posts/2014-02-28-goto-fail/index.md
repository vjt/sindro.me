---
date: 2014-02-28T03:00:00
title: goto fail;
tags: [apple, fail]
---

## In its own words:

{{< figure alt="goto fail diff" src="/posts/2014-02-28-goto-fail/goto-fail.png" >}}

Sources:
[55179.13.c](http://opensource.apple.com/source/Security/Security-55179.13/libsecurity_ssl/lib/sslKeyExchange.c?txt),
[55471.c](http://opensource.apple.com/source/Security/Security-55471/libsecurity_ssl/lib/sslKeyExchange.c?txt)

Source code differences between two consecutive versions of the
Security.framework, a MacOS/iOS component. The seemingly innocuous extra goto
fail; is the cause of a [severe security flaw in most Apple
products](http://nakedsecurity.sophos.com/2014/02/24/anatomy-of-a-goto-fail-apples-ssl-bug-explained-plus-an-unofficial-patch/).
