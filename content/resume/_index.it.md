---
title: "Curriculum Vitae"
type: resume
layout: resume
noComments: true
featuredImage: cover.jpg
downloads:
  - { label: "🇬🇧 PDF", url: "/resume.pdf" }
  - { label: "🇮🇹 PDF", url: "/resume-it.pdf" }
footer_images:
  - { src: "/m27-nebula.jpg", alt: "M27 Dumbbell Nebula", caption: "M27 (Dumbbell) Planetary Nebula · Foto mia" }
  - { src: "/posts/2014-02-28-il-vero-sistemista/cover.jpg", alt: "Hands repairing a car engine", link: "/it/posts/2014-02-28-il-vero-sistemista/", caption: "Il vero sistemista — e le sue auto sono i server." }
---

# Marcello Barnaba

**Production Engineer** · Roma, Italia · [vjt@openssl.it](mailto:vjt@openssl.it)

[GitHub](https://github.com/vjt) · [LinkedIn](https://linkedin.com/in/marcellobarnaba) · [Twitter](https://twitter.com/vjt) · [Blog](https://sindro.me)

---

# Profilo

Tech Lead con {{< years-since "1999-12-01" >}}+ anni di esperienza nella realizzazione di sistemi distribuiti resilienti, nella guida di team cross-funzionali e nella progettazione di infrastrutture critiche su larga scala. Generalista appassionato, mentor e contributore open source.

**Competenze principali:** Sistemi Distribuiti · Tech Leadership · CI/CD · Rust, Python · Linux Internals · Automazione Infrastrutturale · Incident Response · Security Hardening · Collaborazione Cross-funzionale

---

# Esperienza

## Meta Platforms — Production Engineer
*Dicembre 2021 – Presente · {{< years-since "2021-12-01" >}}+ anni*

**Bootstrap / MetalOS** (2023–presente) — sistema operativo bare-metal che alimenta milioni di server a livello globale. Parte dell'organizzazione Datacenter Automation; il team EMEA gestisce l'infrastruttura di net-booting.

- Dimezzato i cicli di re-provisioning dell'intera flotta, riducendo i tempi di inattività e il ricambio hardware
- Progettato e distribuito meccanismi di identificazione hardware per l'imaging iniziale del sistema operativo
- Implementato il sandboxing per generatori di configurazione ermetici
- Guidato la dismissione dei sistemi di net-booting legacy, migrando verso building block più recenti
- Negoziato compromessi tecnici tra più team per l'automazione sicura del ciclo di vita dei server

**Unprovisioning** (2021–2023) — decommissioning degli asset e cancellazione sicura prima che l'hardware lasci i locali aziendali.

- Guidato la dismissione e la migrazione dai sistemi di unprovisioning legacy
- Sviluppato e distribuito workflow di unprovisioning di nuova generazione
- Collaborato con i team DC ops per garantire la cancellazione sicura e la distruzione fisica
- Fatto da mentor a ingegneri junior su più fusi orari

## IFAD (Nazioni Unite) — Tech Lead
*Febbraio 2016 – Novembre 2021 · 5 anni*

Guidato il lato tecnico di un sistema finanziario critico per l'erogazione elettronica dei finanziamenti IFAD ai paesi mutuatari.

- Revisionato proposte tecniche, scritto documentazione, condotto colloqui e assunzioni
- Fatto da collegamento tra stakeholder interni, fornitori esterni e supplier
- Guidato l'automazione completa dell'infrastruttura ([esempio](/it/posts/2026-04-11-ansible-wsadmin/)), convincendo al suo riutilizzo nelle applicazioni line-of-business esistenti
- Supervisionato il design della sicurezza, delegando vulnerability assessment e hardening

## IFAD (Nazioni Unite) — Software Engineer & Sysadmin
*Gennaio 2011 – Gennaio 2016 · 5 anni*

- Progettato e sviluppato molteplici applicazioni LOB: DMS, CRM, workflow BPM, IAM, webcasting
- Costruito, messo in sicurezza e mantenuto ambienti dev/staging/prod per 30+ applicazioni Ruby
- Creato librerie di framework condivise, rilasciate come open source dove possibile
- Configurato DNS, routing, distribuzione software, monitoraggio e infrastruttura di alerting

## Mind2Mind — Web Developer & Sysadmin
*Settembre 2009 – Dicembre 2010*

Refactoring e architettura del front-end e back-end di [panmind.com](http://panmind.com), costruito con Ruby, Javascript ed Erlang. Costruito un [framework SPA, una pipeline di analytics event-driven e un sistema di sessioni cross-language](/it/posts/2026-04-12-panmind-ahead-of-its-time/) che anticipavano pattern adottati dall'industria anni dopo. Progettato e messo in sicurezza l'ambiente di produzione. Evangelizzato l'open source attraverso l'estrazione di componenti e [presentazioni a conferenze](/it/posts/2010-08-05-panmind-at-ruby-social-club/).

## Lime5 — Web Developer & Sysadmin
*Febbraio 2008 – Novembre 2009*

Progettato e implementato diversi progetti: piattaforma turistica (Visita CSA), piattaforma social musicale ([Myousica](/it/posts/2026-04-11-myousica-eighteen-years-later/)) con streaming audio su Engine Yard, sistema enterprise di knowledge-sharing (Agorà).

## Softmedia — Web Developer & Sysadmin
*Dicembre 1999 – Dicembre 2007 · 8 anni*

Primo ruolo professionale. Costruito e mantenuto infrastrutture server UNIX/Windows, VPN site-to-site, sistemi di posta (Exchange, Zimbra, Postfix) e applicazioni web in PHP e Ruby on Rails.

---

# Open Source & Community

**Progetti recenti** — [github.com/vjt](https://github.com/vjt)

- **[ha-verisure-italy](https://github.com/vjt/ha-verisure-italy)** — Integrazione Home Assistant per Verisure Italia. Client API GraphQL, tipizzato con Pydantic, 165 test, pyright strict.
- **[openwrt-ha-presence](https://github.com/vjt/openwrt-ha-presence)** — Rilevamento presenza WiFi per stanza via OpenWrt e MQTT per Home Assistant.
- **[quectel-5g-tools](https://github.com/vjt/quectel-5g-tools)** — Parser e monitor per le informazioni delle celle dei modem Quectel 5G.
- **[mfsroot-geli-dropbear](https://github.com/vjt/mfsroot-geli-dropbear)** — RAM disk iniziale FreeBSD per sblocco remoto ZFS cifrato con GELI via SSH.

**Radici nella community**

- **[Antifork.ORG](https://antifork.org)** (2007–presente) — Mantengo l'infrastruttura storica e il [codice](https://github.com/antifork) di questo gruppo di hacker/amici dai primi anni 2000.
- **[Azzurra IRC Network](/it/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/)** (2002–2005) — [Forkato il server Bahamut](/it/posts/2026-04-13-bahamut-fork-azzurra-irc-ipv6-ssl/) per la più grande rete IRC italiana: IPv6, SSL, hostname cloaking. Aggiunto SSL al client irssi. [Scritto IRC services da zero](/it/posts/2026-04-14-suxserv-multithreaded-sql-irc-services/).

---

# Quotes I Live By

- *Keep looking up* — Neil DeGrasse Tyson
- *Computer science is no more about computers than astronomy is about telescopes* — Dijkstra
- *A name indicates what we seek. An address indicates where it is. A route indicates how we get there* — Jon Postel
- *Be liberal in what you accept, be conservative in what you send* — Jon Postel
