---
title: "ansible-wsadmin: Bypassare AdminConfig per Automatizzare WebSphere via JMX"
date: 2026-04-11
tags: [websphere, ibm, ansible, jython, automation, open-source]
description: "Un ORM Jython e un daemon persistente per IBM WebSphere che bypassa la famigerata API a stringhe di AdminConfig e si aggancia direttamente a ConfigService — il layer Java ben progettato che IBM ha seppellito sotto due decenni di wrapper sbagliati."
image: cover.jpg
featuredImage: cover.jpg
---

***tl;dr** — IBM WebSphere ha un'API di configurazione pulita (ConfigService) sepolta sotto un wrapper a stringhe rotto (AdminConfig). Ho costruito un layer Jython ad oggetti che si aggancia a ConfigService direttamente via JMX — semplificando la configurazione e garantendo la correttezza dei tipi tramite introspezione dei metadati — più un daemon persistente che elimina l'overhead di boot della JVM, e 55 script idempotenti che si integrano col rilevamento di cambiamenti di Ansible. [github.com/vjt/ansible-wsadmin](https://github.com/vjt/ansible-wsadmin)*

Nel 2021 ho passato sei mesi ad automatizzare l'infrastruttura WebSphere dell'[IFAD](https://www.ifad.org/) con Ansible. Lo stack era IBM WebSphere Application Server (WAS), WebSphere Portal Server (WPS) e Business Automation Workflow (BAW) — un deployment clusterizzato con Deployment Manager, nodi multipli, LDAP federato, messaging SIB, tutto quanto.

L'approccio standard per automatizzare WAS è scrivere script Jython usando `AdminConfig`, `AdminTask` e `AdminApp` — i quattro oggetti globali di scripting che IBM fornisce dentro [wsadmin](https://en.wikipedia.org/wiki/Wsadmin). Ho provato. È durato un giorno prima di iniziare a guardare cosa c'è sotto.

Quello che ho trovato ha cambiato il mio approccio all'intero progetto. Ha anche prodotto una libreria piena di idee che non ho mai avuto modo di descrivere come si deve — fino ad ora, con un piccolo aiuto da [Claude](https://claude.ai).

<!--more-->

## Cosa c'è sotto

IBM WebSphere ha un'API di configurazione pulita e ben progettata. Si chiama **ConfigService**, è un MBean JMX, e fa tutto quello che ti aspetteresti da una API Java decente: accetta oggetti tipizzati, restituisce oggetti tipizzati, e ha un'interfaccia coerente per ogni tipo di configurazione nel sistema.

`ConfigService.resolve()` restituisce `ObjectName[]`. `ConfigService.getAttributes()` restituisce un `AttributeList` — una lista di coppie `Attribute(name, value)` con tipi Java appropriati. `ConfigService.setAttributes()` accetta un `AttributeList`. `ConfigService.createConfigData()` prende un `ConfigDataId` padre, un nome di tipo e un `AttributeList` di attributi iniziali, e restituisce l'`ObjectName` del nuovo oggetto. C'è `getAttributesMetaInfo()` che restituisce i metadati completi per qualsiasi tipo di configurazione — nomi degli attributi, tipi, vincoli, se un attributo è un riferimento a un altro oggetto, se è una collezione.

È un'API onesta. Chiedi una cosa, ottieni una cosa. Le dai una cosa, fa la cosa.

Poi IBM ci ha messo sopra `AdminConfig`.

## Il problema AdminConfig

`AdminConfig` è il wrapper di scripting che IBM distribuisce come modo "ufficiale" per interagire con la configurazione di WebSphere da Jython. Prende gli oggetti tipizzati che ConfigService restituisce e li appiattisce tutti a stringhe. Ogni metodo restituisce una stringa. Ogni metodo che restituisce oggetti multipli restituisce una singola stringa con dei newline in mezzo. Fai split su `\n`, tranne quando il separatore è `\r\n`, e a volte i valori contengono spazi, e a volte i valori contengono parentesi quadre che collidono con la sintassi `[attr value]` che usa `AdminConfig.modify()`.

Ecco cosa restituisce `AdminConfig.show()` per un data source:

```
[name "MyDataSource"] [jndiName "jdbc/MyDS"] [description "The data source"]
[authDataAlias ""] [datasourceHelperClassname "com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper"]
```

Quelli non sono dati. È una stringa che assomiglia a dati. Serve un parser per estrarre qualsiasi cosa. E ogni volta che IBM aggiunge un attributo con una parentesi nel valore, il parser si rompe.

Confronta con quello che ti dà ConfigService per lo stesso oggetto: un `javax.management.AttributeList` — una vera collezione Java di coppie nome-valore con valori tipizzati. La iteri. Leggi attributi. Scrivi attributi. Nessun parsing.

La variante `invoke` di `AdminControl` ha lo stesso problema: converte tutto da e verso stringhe. Ma c'è `AdminControl.invoke_jmx()`, che lavora con oggetti Java veri. La variante `_jmx` è quella che può effettivamente chiamare i metodi di ConfigService — perché ConfigService prende parametri `AttributeList` e `ConfigDataId`, che non possono essere rappresentati come stringhe.

Quindi la via di fuga esiste. IBM semplicemente non te la indica.

![Sfondare il layer AdminConfig per trovare ConfigService — l'API pulita sepolta sotto](/posts/2026-04-11-ansible-wsadmin/miner-gem.jpg)

## Come ci sono arrivato

La [storia dei commit](https://github.com/vjt/ansible-wsadmin/commits/master/) racconta la storia meglio di me.

Ho iniziato dove iniziano tutti: parsando l'output di AdminConfig con regex. 10 marzo: [*strengthen the parser on corner cases...*](https://github.com/vjt/ansible-wsadmin/commit/d32f13c). 20 marzo: [*fix parsing of single-item lists and anonymous objects*](https://github.com/vjt/ansible-wsadmin/commit/b59c17c). Si sente la frustrazione nei messaggi dei commit — ogni fix rivelava un nuovo corner case dove il formato a stringhe di AdminConfig era ambiguo o auto-contraddittorio.

Verso il 25 marzo stavo già guardando il layer JMX: [*abstract jmx invoke and app info parsing*](https://github.com/vjt/ansible-wsadmin/commit/4886d23). Ho usato IntelliJ IDEA per decompilare il bytecode di WAS e ho tracciato come funzionava il codice interno di AdminConfig — scoprendo che internamente chiamava ConfigService e poi convertiva i risultati in stringhe. Tutto quel parsing contro cui stavo lottando ricostruiva quello che ConfigService aveva già restituito come oggetti Java appropriati.

27 marzo, ore 4 di mattina: [*wip: remove regex-based parsing, move down one layer*](https://github.com/vjt/ansible-wsadmin/commit/08d217a). Il pivot. Il vecchio parser viene degradato a [configparser.py](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/configparser.py) (ancora usato per i pochi angoli dove AdminTask è inevitabile), e nasce [activeconfig](https://github.com/vjt/ansible-wsadmin/tree/master/lib/wsadmin/lib/activeconfig): [*move legacy wrapper in configparser, implement new object-oriented activeconfig wrapper*](https://github.com/vjt/ansible-wsadmin/commit/95457ec).

48 ore dopo: [*extend activeconfig to a true object oriented ORM for configservice*](https://github.com/vjt/ansible-wsadmin/commit/f158a7e). 31 marzo: [*finalise object oriented traversal*](https://github.com/vjt/ansible-wsadmin/commit/4f8a2ae). Il parser di stringhe aveva richiesto settimane di fix incrementali. Il sostituto basato su ConfigService è costato un weekend.

Il daemon è apparso ancora prima — 14 marzo: [*EXPERIMENTAL - add wsadmin server to speed things up dramatically*](https://github.com/vjt/ansible-wsadmin/commit/35cde6f). Il giorno dopo: [*use the server for all tasks yippee*](https://github.com/vjt/ansible-wsadmin/commit/4ef110c).

## Cosa ho costruito

Ho costruito una libreria Jython che si aggancia direttamente a ConfigService tramite `AdminControl.invoke_jmx()`, e sopra a questa, un ORM in stile Active Record che fa comportare gli oggetti di configurazione WebSphere come normali oggetti Python.

Il cuore è [activeconfig](https://github.com/vjt/ansible-wsadmin/tree/master/lib/wsadmin/lib/activeconfig) — cinque file che ti danno `.find()`, `.create()`, `.update()`, `.delete()` su qualsiasi tipo di configurazione WebSphere:

```python
# Trova un cluster
cluster = activeconfig.find('ServerCluster=PortalCluster')

# Leggi un attributo — è un attributo Python, non un parsing di stringhe
print(cluster.name)

# Aggiorna attributi — la conversione di tipo avviene automaticamente
server.find('JavaVirtualMachine').update({'initialHeapSize': 2048, 'maximumHeapSize': 4096})

# Salva e sincronizza su tutti i nodi
activeconfig.save()
```

Dietro le quinte, [`find()`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/interface.py) chiama `ConfigService.resolve()` tramite il [bridge JMX](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/wsadminutil.py) per ottenere l'`ObjectName` dell'oggetto. Legge `_Websphere_Config_Data_Type` dall'ObjectName per determinare il tipo. Chiama `ConfigService.getAttributesMetaInfo()` attraverso il [layer di introspezione dei metadati](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/meta_info.py) per scoprire quali attributi esistono e quali sono i loro tipi Java. Recupera tutti gli attributi tramite `ConfigService.getAttributes()` e [li converte in tipi Python](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/meta_info.py) usando i metadati. Il risultato è un'istanza [`ConfigObject`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/ConfigObject.py) con accesso ad attributi.

Quando chiami [`.update()`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/ConfigObject.py), converte i tuoi valori Python in tipi Java (sempre [guidato dai metadati](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/meta_info.py)), costruisce un `AttributeList`, e chiama `ConfigService.setAttributes()`. Riferimenti ad altri oggetti di configurazione? Automaticamente risolti al loro `ConfigDataId`. Collezioni? Convertite in `java.util.ArrayList`. Enum? Validati contro i valori ammessi dai metadati. Non tocchi mai una stringa.

Il caricamento dinamico dei modelli in [`__init__.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/__init__.py) cerca file di modelli specializzati — [`Security.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/Security.py), [`Classloader.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/Classloader.py), [`CacheInstance.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/CacheInstance.py) — e li auto-registra. Quando fai `activeconfig.find('Security')`, ottieni un'istanza `Security` con metodi come `jaas_alias()` e `ssl_config_for()`, non un generico ConfigObject.

## Il daemon

Ogni invocazione di uno script wsadmin avvia una nuova JVM. Sono 2-3 secondi di startup prima che una singola riga del tuo script venga eseguita. Quando applichi 30 modifiche di configurazione da Ansible, è un minuto e mezzo passato a fissare messaggi di boot della JVM.

[`server.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/server.py) risolve questo problema. È un `SocketServer.TCPServer` che avvia la JVM una volta sola, importa l'intera libreria activeconfig, e poi ascolta richieste di esecuzione script su una porta TCP. Il protocollo è banale: mandi `nome_script arg1 arg2\n`, ottieni l'output, la connessione si chiude.

Il dispatcher shell ([`wsadmin-script.sh`](https://github.com/vjt/ansible-wsadmin/blob/master/sbin/wsadmin-script.sh)) controlla se il daemon è in esecuzione con `nc -z`. Se lo è, instrada attraverso il daemon. Se no, ricade su un'invocazione wsadmin diretta. Chi chiama non sa e non gli interessa quale percorso è stato preso.

Prima di ogni esecuzione di script, il daemon chiama `AdminConfig.reset()` per pulire lo stato della sessione pendente. Dopo l'esecuzione, di nuovo `reset()`. Ogni script gira in una sessione pulita. In caso di errori non recuperabili, il daemon esce e [systemd lo riavvia](https://github.com/vjt/ansible-wsadmin/blob/master/systemd/was-wsadmin.service) automaticamente.

Il daemon non ha autenticazione — è pensato per girare sull'host DMGR su una VLAN di gestione isolata. Ansible si connette via SSH e lancia `wsadmin-script.sh` come un normale comando. Il daemon è un'ottimizzazione locale trasparente di cui Ansible non è nemmeno consapevole.

## L'integrazione con Ansible

Ognuno dei [55 script di gestione](https://github.com/vjt/ansible-wsadmin#management-scripts) segue una regola: **stampa output solo quando qualcosa cambia**. Questo si mappa direttamente al modello di idempotenza di Ansible:

```yaml
- name: Ensure TLS 1.2 HIGH is configured
  command: wsadmin-script.sh set-qop sslProtocol:TLSv1.2 securityLevel:HIGH
  register: tls_setup
  changed_when: tls_setup.stdout | length > 0

- name: Install CA certificate
  command: wsadmin-script.sh add-cert signer my-ca /opt/certs/ca.crt CellDefaultTrustStore
  register: cert_install
  changed_when: cert_install.stdout | length > 0

- name: Set JVM heap
  command: wsadmin-script.sh set-jvm WebSphere_Portal initialHeapSize:2048 maximumHeapSize:4096
  register: jvm_heap
  changed_when: jvm_heap.stdout | length > 0
```

Prima esecuzione: lo script trova impostazioni diverse, le cambia, stampa cosa è cambiato — Ansible riporta "changed". Seconda esecuzione: le impostazioni corrispondono già, nessun output — Ansible riporta "ok". Nessun modulo Ansible custom, nessuna logica check mode, nessun file di stato. L'idempotenza vive negli script stessi, dove deve stare.

Gli script coprono tutto quello che mi serve: [provider JDBC e data source](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/data-source.py), [certificati SSL](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/add-cert.py) con confronto di fingerprint per evitare reimportazioni, [messaging SIB](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/queue.py), [tuning JVM](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/set-jvm.py), [deployment di applicazioni](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/app-deploy.py), [shared library](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/shared-lib.py), [mapping ruoli admin](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/map-user-to-admin.py), [configurazione BPM](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/set-bpm-url.py), e [altro](https://github.com/vjt/ansible-wsadmin#management-scripts).

## Il repo

[**github.com/vjt/ansible-wsadmin**](https://github.com/vjt/ansible-wsadmin) — licenza MIT.

Il [README](https://github.com/vjt/ansible-wsadmin#readme) ha la documentazione completa: quali API IBM vengono chiamate e dove, l'architettura dell'ORM, il protocollo del daemon, tutti i 55 script con link, esempi Ansible, e diagrammi architetturali Mermaid.

---

![Vent'anni di layer di API enterprise — ognuno più crepato del precedente](/posts/2026-04-11-ansible-wsadmin/layer-cake.jpg)

## Il problema wsadmin: una storia

Il resto di questo post è contesto. Se lavori con WebSphere — o se semplicemente ti diverte guardare un vendor enterprise rendere la vita inutilmente difficile — questo è per te.

### La timeline

**2002 — WAS 5.0: La riscrittura.** IBM [riscrive WebSphere da un codebase comune](https://en.wikipedia.org/wiki/IBM_WebSphere_Application_Server#Version_5.0). Il repository di configurazione basato su database viene sostituito da file XML, gestiti da un Deployment Manager che replica sui nodi. [wsadmin sostituisce il vecchio tool WSCP](https://en.wikipedia.org/wiki/Wsadmin). Il framework di amministrazione JMX arriva con due layer: **ConfigService** (l'MBean — oggetti Java tipizzati, interfaccia coerente) e **AdminConfig/AdminControl/AdminApp** (wrapper di scripting — tutto è stringhe). Il layer di scripting ha come target [JACL](https://en.wikipedia.org/wiki/Tcl_Java) (Tcl-in-Java), il che spiega l'ossessione per le stringhe: Tcl è un linguaggio orientato alle stringhe. Ma poi IBM aggiunge il supporto [Jython](https://www.ibm.com/docs/en/was/8.5.5?topic=concepts-using-wsadmin-scripting-jython) in WAS 5.1 (2004), e l'API a stringhe ha ancora meno senso.

**2006 — WAS 6.1: Arriva AdminTask.** Un quarto oggetto di scripting, progettato per fornire comandi "[task-oriented](https://www.ibm.com/docs/en/was/8.5.5?topic=wsadmin-using-scripting-admintask-object-scripted-administration)" di convenienza. Invece di semplificare le cose, aggiunge un altro livello di indirezione con la sua propria sintassi per gli argomenti: `AdminTask.createSIBJMSQueue('...(cells/...)', '[-name Queue -jndiName jms/Queue -busName Bus]')`. È una stringa contenente coppie chiave-valore dentro parentesi dentro una stringa. La documentazione IBM per AdminTask è centinaia di pagine di formule magiche tipo la [configurazione del session management](https://www.ibm.com/docs/en/was/8.5.5?topic=caus-configuring-applications-session-management-in-web-modules-using-scripting). La console di admin guadagna "Command Assistance" — mostra l'equivalente wsadmin delle azioni della console — il che evidenzia solo quanto siano contorti i comandi.

**2008 — WAS 7.0: Script Libraries.** IBM distribuisce [funzioni Jython pre-costruite](https://www.ibm.com/docs/en/was/8.5.5?topic=reference-jython-script-library) organizzate per categoria. Un passo nella direzione giusta, ma costruite sempre sul layer AdminConfig a stringhe. Un assaggio della nomenclatura: gli [script di aggiornamento applicazioni](https://www.ibm.com/docs/en/was/8.5.5?topic=scripting-application-update-scripts) di IBM includono `addSingleModuleFileToAnAppWithUpdateCommand`, `updateApplicationWithUpdateIgnoreOldOption`, e `addUpdateSingleModuleFileToAnAppWithUpdateCommand`. Il mio equivalente è [app-deploy.py](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/app-deploy.py) — 80 righe, gestisce sia install che update, confronta le versioni, fornisce default sensati.

### La risposta della community

La parte rivelatrice non è che la community ha costruito wrapper. È *chi* ha costruito wrapper.

**[wsadminlib.py](https://github.com/wsadminlib/wsadminlib)** — usato internamente in IBM per anni, [alla fine spostato su GitHub](https://wsadminlib.blogspot.com/2013/10/wsadminlib-now-available-at-githubcom.html) — è stato creato da sviluppatori di prodotto IBM per [fornire oltre 500 metodi con nomi intuitivi e parametri per sostituire i complessi comandi AdminConfig](https://www.slideshare.net/kelapure/wsadminlibwasug2011-01250726). Fermatevi un secondo a rifletterci: gli stessi ingegneri di IBM hanno costruito un wrapper da 500 metodi perché l'API che hanno distribuito aveva bisogno di essere sostituita. La [presentazione al WASUG 2011](https://www.slideshare.net/kelapure/wsadminlibwasug2011-01250726) di Rohit Kelapure attraversa metodo dopo metodo progettato per "nascondere la sintassi" — il modo diplomatico per dire che la sintassi non dovrebbe essere vista da esseri umani.

**[WDR](https://github.com/WDR/WDR)** (WebSphere Deployment Robot) prende un approccio diverso: [wrappa l'output di AdminConfig in oggetti Python](https://wdr.github.io/WDR/) per poter scrivere `jvm.initialHeapSize = 64` invece di `AdminConfig.modify(jvm, [['initialHeapSize', '64']])`. Il loro pitch è rendere gli script wsadmin *"more Pythonic and readable"* — sostituendo `AdminConfig.listConfigObjects('Node').splitlines()` con un iterabile diretto. Che questo debba essere un punto di vendita dice tutto sull'esperienza di base.

**[myarch.com](https://myarch.com/getting-started-wsadmin/)** documenta l'API con una franchezza che la documentazione ufficiale IBM non raggiunge mai. La loro descrizione delle strutture dati di AdminTask come [*"truly baffling"*](https://myarch.com/getting-started-wsadmin/) — "davvero sconcertanti" — e delle [*"ten thousand options"*](https://myarch.com/getting-started-wsadmin/) di AdminApp.install() cattura la frustrazione collettiva della community. Hanno costruito il loro [framework di automazione](https://myarch.com/was-automation) con un DSL dichiarativo.

Per Ansible specificamente, ci sono [amimof/ansible-websphere](https://github.com/amimof/ansible-websphere), [ebasso/ansible-ibm-websphere](https://github.com/ebasso/ansible-ibm-websphere), e [BertRaeymaekers/ansible-was](https://github.com/BertRaeymaekers/ansible-was) — tutti fanno shell out a script wsadmin costruiti sul layer AdminConfig/AdminTask.

### Il pattern

Ognuno di questi progetti — wsadminlib, WDR, myarch, i moduli Ansible — lavora *dentro* il layer wrapper AdminConfig. Rendono l'output di AdminConfig sopportabile parsando le stringhe in strutture dati, wrappando le chiamate in funzioni più amichevoli, fornendo astrazioni di livello più alto che nascondono le parentesi quadre.

**Nessuno di loro va sotto il wrapper.**

L'approccio che prendo con [ansible-wsadmin](https://github.com/vjt/ansible-wsadmin) è diverso: usare `AdminControl.invoke_jmx()` per chiamare ConfigService direttamente. Ottenere indietro oggetti Java veri. Lasciare che i metadati stessi di ConfigService guidino la conversione dei tipi. Costruire l'ORM sopra l'API reale, non sopra il wrapper.

AdminConfig ha ancora un ruolo — `save()`, `getCurrentSession()` e `reset()` sono primitive di gestione della sessione che non hanno equivalente in ConfigService. Ma per leggere e scrivere configurazione, viene completamente bypassato. Niente stringhe. Niente parsing. Niente parentesi quadre.

### Per approfondire

- [IBM: Documentazione ConfigService MBean](https://www.ibm.com/docs/en/was/8.5.5?topic=scripting-commands-adminconfig-object-using-wsadmin) — il riferimento ufficiale, che riesce a documentare AdminConfig senza menzionare che sotto c'è ConfigService
- [IBM: Classi ObjectName, Attribute e AttributeList](https://www.ibm.com/docs/en/was/8.5.5?topic=uwsaosa-objectname-attribute-attributelist-classes-using-wsadmin-scripting) — gli oggetti Java tipizzati che AdminConfig si sforza di nasconderti
- [Alvin Abad: Administering WebSphere Using JMX](https://alvinabad.wordpress.com/2009/02/15/automating-websphere-using-jmx/) — uno dei pochi articoli che mostra come bypassare wsadmin del tutto con JMX diretto
- [blog di wsadminlib](http://wsadminlib.blogspot.com/) — ingegneri IBM che documentano la propria fuga da AdminConfig
- [Documentazione WDR](https://wdr.github.io/WDR/) — wrapper "Pythonico" su AdminConfig
- [myarch.com: Getting Started with wsadmin](https://myarch.com/getting-started-wsadmin/) — l'introduzione più onesta all'API che troverai
- [myarch.com: AdminControl vs AdminConfig](https://myarch.com/admincontrol-vs-adminconfig/) — capire la divisione architetturale
