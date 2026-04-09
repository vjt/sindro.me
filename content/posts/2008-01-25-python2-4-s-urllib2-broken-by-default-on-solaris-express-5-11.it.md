---
date: 2008-01-25
title: urllib2 di Python2.4 rotto di default su Solaris Express 5.11
tags: [security, git, python, sysadmin]
---

{{< retrospective year="2026" >}}
Sun è stata acquisita da Oracle nel 2010 e Solaris è di fatto abbandonato da quando Oracle ha smantellato il team nel 2017. Python 2.4 e `urllib2` non esistono più — `urllib2` è stato incorporato in `urllib.request` in Python 3.
{{< /retrospective >}}

Mentre installavo allegramente i prerequisiti per compilare un'applicazione su
[Solaris 11](http://sun.com/software/solaris), ho apprezzato il fatto di
trovare [Mercurial](http://selenic.com/mercurial) già installato nel sistema
base... tranne per un GROSSO problema: la digest authentication era rotta. Ho
fatto un `tcpdump` del traffico scambiato tra il client Mercurial e il server
CGI e ho visto che non veniva inviato nessun header Authorization, e
ovviamente il server si rifiutava di servire il repository hg.

Prima di reinstallare Python, magari da sorgente e sostituendo l'installazione
di default oppure tenendo affiancate due versioni diverse, con le conseguenti
seccature e sporcizia nel sistema, ho provato un patch davvero minuscolo a
urllib2.py che... con mio divertimento, ha risolto il problema:

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

Non sono un ca**o di esperto Python (ma il linguaggio è interessante), quindi
non chiedetemi PERCHÉ funziona: ho semplicemente seguito il commento di
`add_header` che diceva "questo metodo è utile per aggiungere header di
autenticazione" e ho sostituito il metodo `unredirected_header` con il primo.
Non ho proprio idea del perché con urllib2 di Python2.5 "tutto funziona" anche
con quel metodo; qualcosa deve essere rotto da qualche altra parte. Un diff
tra le due urllib non mi ha dato niente, dovrei davvero imparare Python prima
o poi.

Non ho trovato nessuna informazione googlando parole chiave come <<solaris
"http {authorization,authentication}" {urllib2,python} {broken,not working}
mercurial>> (shell interpolation intesa), quindi spero che questo post sia
utile a qualcuno ;).

Solaris sembra una bella bestia, comunque. Dovrò imparare di più anche su
quello. :).
