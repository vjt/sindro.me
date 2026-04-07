---
date: 2008-11-12T21:00:00Z
title: Far funzionare davvero(tm) il CCacheServer Kerberos Ticket su OSX
tags: [apple, security, macos]
categories: [development]
---

Se ti stai chiedendo **perché** il demone `CCacheServer`, che tiene in memoria
i ticket Kerberos ottenuti tramite `kinit(1)`, NON parte... è a causa di un
bug **strano** riguardante il `LimitLoadToSessionType` specificato nel .plist
dell'agent, che si trova in
`/System/Library/LaunchAgents/edu.mit.kerberos.CCacheServer.plist` sui sistemi
OSX 10.5.

Devi semplicemente commentare queste due righe:

```plaintext
<key>LimitLoadToSessionType</key>
<string>Background</string>
```

E poi o fai
```
launchctl load /System/Library/LaunchAgents/edu.mit.kerberos.CCacheServer.plist
```
oppure riavvii il sistema ;).

CCacheServer verrà poi istanziato quando fai un kinit:

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

Il bug è strano perché la chiave `LimitLoadToSessionType` dovrebbe in realtà
istruire launchd ad avviare automaticamente il demone e farlo girare una volta
per [ogni utente
loggato](http://developer.apple.com/technotes/tn2005/tn2083.html#TABLAUNCHAGENTSUBTYPES),
quando kinit ne richiede i servizi. Ma se la chiave è impostata nel `.plist`,
un launchctl load su di esso fallisce con "nothing found to load". Assurdo!
