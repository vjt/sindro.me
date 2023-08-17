---
date: 2008-11-12T21:00:00Z
title: Making the CCacheServer Kerberos Ticket server actually Work(tm) on OSX
tags: [apple, kerberos, macos, ticket]
categories: [development]
---

If you're wondering **why** the `CCacheServer` daemon, that caches in memory
Kerberos tickets obtained via `kinit(1)` is NOT starting .. that's because of a
**strange** bug regarding the `LimitLoadToSessionType` specified into the agent
.plist, located into
`/System/Library/LaunchAgents/edu.mit.kerberos.CCacheServer.plist` on OSX 10.5
systems.

You simply have to comment out these two lines:

```plaintext
<key>LimitLoadToSessionType</key>
<string>Background</string>
```

And either
```
launchctl load /System/Library/LaunchAgents/edu.mit.kerberos.CCacheServer.plist
```
or reboot your system ;).

CCacheServer will then be instantiated when you do a kinit:

```
$ kinit
Please enter the password for vjt@DOMAIN.LOCAL:

$ klist
Kerberos 5 ticket cache: 'API:Initial default ccache'
Default principal: vjt@DOMAIN.LOCAL

Valid Starting     Expires            Service Principal
11/12/08 20:59:35  11/13/08 06:59:14  krbtgt/DOMAIN.LOCAL@DOMAIN.LOCAL
    renew until 11/19/08 20:59:35
```

The bug is strange because the `LimitLoadToSessionType` key actually should
instruct launchd to automatically start up the daemon and run it once for
[every logged in
user](http://developer.apple.com/technotes/tn2005/tn2083.html#TABLAUNCHAGENTSUBTYPES),
when kinit asks its services. But, if the key is set in the `.plist`, a
launchctl load on it fails with "nothing found to load". Weird!
