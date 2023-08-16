---
date: 2009-01-29T19:00:00Z
title: "A permalink_fu improvement: allow modification of permalinks and send HTTP redirects on-the-fly"
tags: [permalink, plugin, projects, rails, ruby]
categories: [development, all]
---

Another spin-off from the [www.visitacsa.it](http://www.visitacsa.it/) website:
a [permalink_fu](http://github.com/technoweenie/permalink_fu/tree/master)
improvement that allows **dynamic permalinks**. I know it is an
[oxymoron](http://en.wikipedia.org/wiki/Oxymoron), because permalinks should be
.. well .. permanent! And because [search
engines](http://www.searchlores.org/main.htm) index them, they should never
change. But what happens when you publish *something*, your permalink is
generated with permalink_fu using the *title* of your post, and after a couple
of days you want to change the title, and the permalink under which the post is
accessible as well?

Following the
[specification](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html), your
app should send out a *301 moved permanently* HTTP status when accessing the
old permalink and redirect the client to the new Uniform Resource Locator.
That's quite the same thing what my modification to *permalink_fu* does:
whenever your post attributes are changed, the former and new permalinks are
saved to the database, and you can enable your controller to generate *302
moved temporarily* redirects when needed. In other words, it checks whether the
requested URL is an old permalink, and automagically redirects the client to
the new one.

Everything is done behind the scenes, and the plugin has also got nifty rake
tasks to set up the Redirect model and associated migrations. And you can
change its name, of course! :)

The *302* code was chosen because the *301 permanent* status code [has quite
disruptive effects on search
engines](http://www.google.com/support/webmasters/bin/answer.py?hl=en&amp;answer=40132),
but more discussion is welcome.

Have a look over [my repository at
github](http://github.com/vjt/permalink_fu/tree/master), read the
[README](http://github.com/vjt/permalink_fu/blob/b8d979f28c9795389cc65e9670a3529f805618dc/README)
that contains the documentation of the added features, and check out the code!

