---
date: 2008-01-25
title: Python2.4's urllib2 broken by default on Solaris Express 5.11
tags: [authentication, digest, hg, mercurial, patch, python, solaris]
categories: [development, all]
---

While happily installing prerequisites to build an app on [Solaris
11](http://sun.com/software/solaris), i enjoyed having
[Mercurial](http://selenic.com/mercurial) already installed in the base
system.. except for a BIG issue: digest authentication was broken. I
`tcpdump`’ed the traffic exchanged between the mercurial client and the CGI
server and I saw that no Authorization header was sent, and obviously the
server refused to serve the hg repository.

Before reinstalling python, maybe from source and replacing the default
installation or having side by side two different versions, with consequent
nuisances and dirt around the system, I tried a very very small patch to
urllib2.py that… amusingly enough, fixed my problem:

```
--- urllib2.py~ Fri Jan 25 02:35:59 2008
+++ urllib2.py  Fri Jan 25 03:27:52 2008
@@ -815,7 +815,7 @@
             auth_val = 'Digest %s' % auth
             if req.headers.get(self.auth_header, None) == auth_val:
                 return None
-            req.add_unredirected_header(self.auth_header, auth_val)
+            req.add_header(self.auth_header, auth_val)
             resp = self.parent.open(req)
             return resp
```

I’m no fscking python expert (but the language is interesting), so don’t ask me
WHY it works, i simply followed the `add_header` comment that said “this method
is useful for adding authentication headers” and replaced the
`unredirected_header` method with the former. I really don’t know why with
Python2.5’s urllib2 “everything works” even with that method, something must be
broken somewhere else. A diff between the two urllibs gave me nothing, I really
should learn Python one day or another.

I also found no information by googling keywords such as <<solaris “http
{authorization,authentication}” {urllib2,python} {broken,not working}
mercurial>> (shell interpolation intended), so I hope this post will be useful
to someone ;).

Solaris looks like a nice beast, though. I’ll have to learn more about it as
well. :).
