---
date: 2014-02-28T03:00:00
title: goto fail;
tags: [apple, funny, security, macos]
hideVintage: true
---

## In its own words:

{{< figure alt="goto fail diff" src="/posts/2014-02-28-goto-fail/goto-fail.png" >}}

Sources:
[55179.13.c](http://opensource.apple.com/source/Security/Security-55179.13/libsecurity_ssl/lib/sslKeyExchange.c?txt),
[55471.c](http://opensource.apple.com/source/Security/Security-55471/libsecurity_ssl/lib/sslKeyExchange.c?txt)

Source code differences between two consecutive versions of the
Security.framework, a macOS/iOS component. The seemingly innocuous extra `goto
fail;` — a duplicated line with no braces around the `if` body — caused the
SSL/TLS certificate verification to be silently skipped entirely. Any
certificate would be accepted as valid, making every HTTPS connection on
affected devices vulnerable to man-in-the-middle attacks. The bug
([CVE-2014-1266](https://nvd.nist.gov/vuln/detail/CVE-2014-1266)) affected iOS
6/7 and OS X Mavericks, and was patched in iOS 7.0.6 and OS X 10.9.2. It
became one of the most famous examples of why braces matter and why code review
catches what compilers don't. See [ImperialViolet's technical
analysis](https://www.imperialviolet.org/2014/02/22/applebug.html) for the
full details.
