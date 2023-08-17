---
date: 2011-07-07T14:00:00Z
title: Binding 80/TCP as non-root on your development server
tags: [capabilities, linux, ruby]
categories: [development]
---

![Neo Tux](/posts/2011-07-07-binding-port-80-for-your-development-application-server/neo-tux.png)

So you have a Linux VM you use for development, because you want to mirror the
production environment as closely as possible. You have many applications to
deal with, they have to be running at the same time because they are nifty REST
JSON web services.

You are very tired to remember which one you put on port `8081`, and your
configuration files slowly become a real mess. So you set up IP address aliases
in for the network interface and decide to assign even host names –
`/etc/hosts` is just fine – for each app.

Then, in such a setup, why would you still need to run them on ports higher
than `1024`? Wouldn't be just great to type the application name in the browser
address bar? Indeed it is, but it's better to not run them as `root`, anyway.

The solution are [Linux
capabilities](http://www.kernel.org/doc/man-pages/online/pages/man7/capabilities.7.html)
(see also [here](http://www.friedhoff.org/posixfilecaps.html)). The one that
interests us is `cap_net_bind_service`: it gives a process the right to bind
well-known ports (< 1024). If you use an interpreted language, of course you'll
have to add the capability to the interpreter itself. That's why there's
**development** in the title of this article – you should not set this up on a
production server, if you don't know what you are doing.

One final quirk: if you happen to `dlopen()` shared objects that dynamically
link towards libraries outside the canonical paths, you cannot load them via
`LD_LIBRARY_PATH` (e.g. the `SYBASE.sh`) as it is ignored for `setcap`-ped
processes. You should better move the library paths into an `/etc/ld.so.conf.d`
snippet.

## tl;dr

Assuming you are the latest and greatest rails developer, you should become
root – or use sudo, as you wish – and

```shell
# YOU ARE ON YOUR DEVELOPMENT MACHINE
setcap cap_net_bind_service+ep `which ruby`
```

Profit:

```shell
thin start -a yourapp -p 80
>> Using rack adapter
>> Thin web server (v1.2.11 codename Bat-Shit Crazy)
>> Maximum connections set to 1024
>> Listening on yourapp:80, CTRL+C to stop
...
```
