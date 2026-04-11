---
title: "ansible-wsadmin: Automating WebSphere by Skipping IBM's Own Wrappers"
date: 2021-05-26
tags: [websphere, ibm, ansible, jython, automation, open-source]
description: "A Jython ORM and persistent daemon for IBM WebSphere that bypasses the infamous AdminConfig string API and hooks directly into ConfigService — the well-designed Java layer that IBM buried under 18 years of bad wrappers."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Five years later, I'm open-sourcing this as [ansible-wsadmin](https://github.com/vjt/ansible-wsadmin). It spent all this time in my drive — nobody at IFAD used it after I left, and it's too useful to rot. The repo contains the full history from the development sprint documented below, with internal references scrubbed.
{{< /retrospective >}}

I'm automating the [IFAD](https://www.ifad.org/) WebSphere infrastructure with Ansible. The stack is IBM WebSphere Application Server (WAS), WebSphere Portal Server (WPS), and Business Automation Workflow (BAW) — a clustered deployment with a Deployment Manager, multiple nodes, federated LDAP, SIB messaging, the works.

The standard approach to automating WAS is to write Jython scripts using `AdminConfig`, `AdminTask`, and `AdminApp` — the four global scripting objects that IBM provides inside [wsadmin](https://en.wikipedia.org/wiki/Wsadmin). I tried that. It lasted about a day before I started looking at what's underneath.

What I found changed how I approached the entire project.

<!--more-->

## What's underneath

IBM WebSphere has a clean, well-designed configuration API. It's called **ConfigService**, it's a JMX MBean, and it does everything you'd expect from a proper Java API: it takes typed objects, returns typed objects, and has a consistent interface for every configuration type in the system.

`ConfigService.resolve()` returns `ObjectName[]`. `ConfigService.getAttributes()` returns an `AttributeList` — a list of `Attribute(name, value)` pairs with proper Java types. `ConfigService.setAttributes()` takes an `AttributeList`. `ConfigService.createConfigData()` takes a parent `ConfigDataId`, a type name, and an `AttributeList` of initial attributes, and returns the new object's `ObjectName`. There's `getAttributesMetaInfo()` that returns the full metadata for any configuration type — attribute names, types, constraints, whether an attribute is a reference to another object, whether it's a collection.

It's an honest API. You ask for a thing, you get a thing. You give it a thing, it does the thing.

Then IBM covered it with `AdminConfig`.

## The AdminConfig problem

`AdminConfig` is the scripting wrapper that IBM ships as the "official" way to interact with WebSphere configuration from Jython. It takes the typed objects that ConfigService returns and flattens them all to strings. Every method returns a string. Every method that returns multiple objects returns a single string with newlines between them. You split on `\n`, except sometimes the line separator is `\r\n`, and sometimes values contain spaces, and sometimes values contain square brackets which collide with the `[attr value]` syntax that `AdminConfig.modify()` uses.

Here's what `AdminConfig.show()` returns for a data source:

```
[name "MyDataSource"] [jndiName "jdbc/MyDS"] [description "The data source"]
[authDataAlias ""] [datasourceHelperClassname "com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper"]
```

That's not data. That's a string that looks like data. You need a parser to extract anything from it. And every time IBM adds an attribute with a bracket in the value, the parser breaks.

Compare what ConfigService gives you for the same object: a `javax.management.AttributeList` — a proper Java collection of name-value pairs with typed values. You iterate it. You read attributes. You write attributes. No parsing.

The `invoke` variant of `AdminControl` has the same problem: it converts everything to and from strings. But there's `AdminControl.invoke_jmx()`, which works with actual Java objects. The `_jmx` variant is the one that can actually call ConfigService methods — because ConfigService takes `AttributeList` and `ConfigDataId` parameters, which can't be represented as strings.

So the escape hatch exists. IBM just doesn't point you at it.

## What I built

I built a Jython library that hooks directly into ConfigService via `AdminControl.invoke_jmx()`, and on top of that, an Active Record-style ORM that makes WebSphere configuration objects behave like regular Python objects.

The core is [activeconfig](https://github.com/vjt/ansible-wsadmin/tree/master/lib/wsadmin/lib/activeconfig) — five files that give you `.find()`, `.create()`, `.update()`, `.delete()` on any WebSphere configuration type:

```python
# Find a cluster
cluster = activeconfig.find('ServerCluster=PortalCluster')

# Read an attribute — it's a Python attribute, not a string parse
print(cluster.name)

# Update attributes — type conversion happens automatically
server.find('JavaVirtualMachine').update({'initialHeapSize': 2048, 'maximumHeapSize': 4096})

# Save and sync to all nodes
activeconfig.save()
```

Under the hood, `find()` calls `ConfigService.resolve()` to get the object's `ObjectName`. It reads `_Websphere_Config_Data_Type` from the ObjectName to determine the type. It calls `ConfigService.getAttributesMetaInfo()` to learn what attributes exist and what their Java types are. It fetches all attributes via `ConfigService.getAttributes()` and converts them to Python types using the metadata. The result is a [`ConfigObject`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/ConfigObject.py) instance with attribute access.

When you call `.update()`, it converts your Python values back to Java types (again, driven by metadata), builds an `AttributeList`, and calls `ConfigService.setAttributes()`. References to other config objects? Automatically resolved to their `ConfigDataId`. Collections? Converted to `java.util.ArrayList`. Enums? Validated against the allowed values from the metadata. You never touch a string.

The dynamic model loading in [`__init__.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/__init__.py) scans for specialized model files — [`Security.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/Security.py), [`Classloader.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/Classloader.py), [`CacheInstance.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/lib/activeconfig/CacheInstance.py) — and auto-registers them. When you `activeconfig.find('Security')`, you get a `Security` instance with methods like `jaas_alias()` and `ssl_config_for()`, not a generic ConfigObject.

## The daemon

Every wsadmin script invocation boots a fresh JVM. That's 2-3 seconds of startup before a single line of your script runs. When you're applying 30 configuration changes from Ansible, that's a minute and a half of staring at JVM boot messages.

[`server.py`](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/server.py) solves this. It's a `SocketServer.TCPServer` that boots the JVM once, imports the entire activeconfig library, and then listens for script execution requests on a TCP port. The protocol is trivial: send `script_name arg1 arg2\n`, get the output back, connection closes.

The shell dispatcher ([`wsadmin-script.sh`](https://github.com/vjt/ansible-wsadmin/blob/master/sbin/wsadmin-script.sh)) checks if the daemon is running with `nc -z`. If it is, it routes through the daemon. If not, it falls back to a direct wsadmin invocation. The caller doesn't know or care which path was taken.

Before each script execution, the daemon calls `AdminConfig.reset()` to clear pending session state. After execution, `reset()` again. Each script runs in a clean session. On unrecoverable errors, the daemon exits and [systemd restarts it](https://github.com/vjt/ansible-wsadmin/blob/master/systemd/was-wsadmin.service) automatically.

The daemon has no authentication — it's meant to run on the DMGR host on an airgapped management VLAN. Ansible connects via SSH and runs `wsadmin-script.sh` as a regular command. The daemon is a transparent localhost optimization that Ansible isn't even aware of.

## The Ansible integration

Each of the [55 management scripts](https://github.com/vjt/ansible-wsadmin) follows one rule: **print output only when something changes**. This maps directly to Ansible's idempotency model:

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

First run: the script finds settings that differ, changes them, prints what changed — Ansible reports "changed". Second run: settings already match, no output — Ansible reports "ok". No custom Ansible modules, no check mode logic, no state files. The idempotency lives in the scripts themselves, where it belongs.

The scripts cover everything I need: [JDBC providers and data sources](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/data-source.py), [SSL certificates](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/add-cert.py) with fingerprint comparison to avoid reimporting, [SIB messaging](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/queue.py), [JVM tuning](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/set-jvm.py), [application deployment](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/app-deploy.py), [shared libraries](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/shared-lib.py), [admin role mapping](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/map-user-to-admin.py), [BPM configuration](https://github.com/vjt/ansible-wsadmin/blob/master/lib/wsadmin/bin/set-bpm-url.py), and [more](https://github.com/vjt/ansible-wsadmin#management-scripts).

## The repo

[**github.com/vjt/ansible-wsadmin**](https://github.com/vjt/ansible-wsadmin) — MIT licensed.

The [README](https://github.com/vjt/ansible-wsadmin#readme) has full documentation: which IBM APIs are called and where, the ORM architecture, the daemon protocol, all 55 scripts with links, Ansible examples, and Mermaid architecture diagrams.

---

## The wsadmin problem: a history

The rest of this post is context. If you work with WebSphere — or if you just enjoy watching an enterprise vendor make life unnecessarily difficult — this is for you.

### The timeline

**2003 — WAS 5.0: The rewrite.** IBM rewrites WebSphere from scratch. Configuration moves from a database to XML files. The JMX-based admin framework ships with two layers: **ConfigService** (the MBean — typed Java objects, consistent interface) and **AdminConfig/AdminControl/AdminApp** (scripting wrappers — everything is strings). The scripting layer targets [JACL](https://en.wikipedia.org/wiki/Tcl_Java) (Tcl-in-Java), which explains the string obsession: Tcl is a string-oriented language. But then they add Jython support in WAS 5.1 (2004), and the string API makes even less sense.

**2006 — WAS 6.1: AdminTask arrives.** A fourth scripting object, designed to provide "task-oriented" convenience commands. Instead of making things simpler, it adds another layer of indirection with its own argument syntax: `AdminTask.createSIBJMSQueue('...(cells/...)', '[-name Queue -jndiName jms/Queue -busName Bus]')`. That's a string containing key-value pairs inside brackets inside a string. IBM's documentation for AdminTask is hundreds of pages of these incantations.

**2008 — WAS 7.0: Script Libraries.** IBM ships pre-built Jython functions organized by category. A step in the right direction, but still built on the string-parsing AdminConfig layer underneath.

### The community response

The telling part isn't that the community built wrappers. It's *who* built wrappers.

**[wsadminlib.py](https://github.com/wsadminlib/wsadminlib)** (2006, published 2010) was created by **two IBM product developers** who, in their own words, *"were having trouble understanding the native wsadmin syntax."* IBM's own engineers couldn't use their own API. The library grew to 500+ methods with contributions from 30+ IBM engineers worldwide. Their [WASUG 2011 presentation](https://www.slideshare.net/kelapure/wsadminlibwasug2011-01250726) is a masterclass in diplomatic criticism of your own employer's product: function after function that "hides the underlying nonsense" (paraphrasing, but barely).

**[WDR](https://github.com/WDR/WDR)** (WebSphere Deployment Robot) takes a different approach: it wraps AdminConfig output in Python objects so you can do property access instead of string parsing. Their pitch: *"Lists must be treated as lists, no more splitline()."* That this needs to be a selling point says everything about the baseline experience.

**[myarch.com](https://myarch.com/getting-started-wsadmin/)** documents the API with a candor that IBM's official docs never achieve. Their description of AdminTask's data structures as *"truly baffling"* and AdminApp.install()'s *"ten thousand options"* captures the community's collective frustration. They built their own [automation framework](https://myarch.com/was-automation) with a declarative DSL on top.

For Ansible specifically, there are [amimof/ansible-websphere](https://github.com/amimof/ansible-websphere), [ebasso/ansible-ibm-websphere](https://github.com/ebasso/ansible-ibm-websphere), and [BertRaeymaekers/ansible-was](https://github.com/BertRaeymaekers/ansible-was) — all shelling out to wsadmin scripts built on the AdminConfig/AdminTask layer.

### The pattern

Every one of these projects — wsadminlib, WDR, myarch, the Ansible modules — works *within* the AdminConfig wrapper layer. They make AdminConfig's output bearable by parsing the strings into data structures, by wrapping the calls in friendlier functions, by providing higher-level abstractions that hide the square brackets.

None of them go below the wrapper.

The approach I take with [ansible-wsadmin](https://github.com/vjt/ansible-wsadmin) is different: use `AdminControl.invoke_jmx()` to call ConfigService directly. Get back proper Java objects. Let ConfigService's own metadata drive the type conversion. Build the ORM on top of the real API, not on top of the wrapper.

AdminConfig still has a role — `save()`, `getCurrentSession()`, and `reset()` are session management primitives with no ConfigService equivalent. But for reading and writing configuration, it's bypassed entirely. No strings. No parsing. No square brackets.

### Further reading

- [IBM: ConfigService MBean documentation](https://www.ibm.com/docs/en/was/8.5.5?topic=scripting-commands-adminconfig-object-using-wsadmin) — the official reference, which somehow manages to document AdminConfig without mentioning that ConfigService exists underneath
- [IBM: ObjectName, Attribute, and AttributeList classes](https://www.ibm.com/docs/en/was/8.5.5?topic=uwsaosa-objectname-attribute-attributelist-classes-using-wsadmin-scripting) — the typed Java objects that AdminConfig goes out of its way to hide from you
- [Alvin Abad: Administering WebSphere Using JMX](https://alvinabad.wordpress.com/2009/02/15/automating-websphere-using-jmx/) — one of the few articles that shows how to bypass wsadmin entirely with direct JMX
- [wsadminlib blog](http://wsadminlib.blogspot.com/) — IBM engineers documenting their own escape from AdminConfig
- [WDR documentation](https://wdr.github.io/WDR/) — "Pythonic" wrapper over AdminConfig
- [myarch.com: Getting Started with wsadmin](https://myarch.com/getting-started-wsadmin/) — the most honest introduction to the API you'll find
- [myarch.com: AdminControl vs AdminConfig](https://myarch.com/admincontrol-vs-adminconfig/) — understanding the architectural split
