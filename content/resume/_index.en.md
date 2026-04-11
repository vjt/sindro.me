---
title: "Resume"
type: resume
layout: resume
noComments: true
featuredImage: cover.jpg
downloads:
  - { label: "🇬🇧 PDF", url: "/resume.pdf" }
  - { label: "🇮🇹 PDF", url: "/resume-it.pdf" }
footer_images:
  - { src: "/m27-nebula.jpg", alt: "M27 Dumbbell Nebula", caption: "M27 (Dumbbell) Planetary Nebula · Photo by me" }
  - { src: "/posts/2014-02-28-il-vero-sistemista/cover.jpg", alt: "Hands repairing a car engine", link: "/posts/2014-02-28-il-vero-sistemista/", caption: "The real sysadmin — and his cars are servers." }
---

# Marcello Barnaba

**Production Engineer** · Rome, Italy · [vjt@openssl.it](mailto:vjt@openssl.it)

[GitHub](https://github.com/vjt) · [LinkedIn](https://linkedin.com/in/marcellobarnaba) · [Twitter](https://twitter.com/vjt) · [Blog](https://sindro.me)

---

# Profile

Tech Lead with {{< years-since "1999-12-01" >}}+ years of experience delivering resilient distributed systems, leading cross-functional teams, and architecting critical infrastructure at scale. Passionate generalist, mentor, and open source contributor.

**Core skills:** Distributed Systems · Tech Leadership · CI/CD · Rust, Python · Linux Internals · Infrastructure Automation · Incident Response · Security Hardening · Cross-functional Collaboration

---

# Experience

## Meta Platforms — Production Engineer
*December 2021 – Present · {{< years-since "2021-12-01" >}}+ years*

**Bootstrap / MetalOS** (2023–present) — bare-metal OS powering millions of servers globally. Part of the Datacenter Automation org; EMEA team owns the net-booting infrastructure.

- Halved re-provisioning cycles across the fleet, reducing downtime and hardware churn
- Designed and rolled out hardware identification mechanisms for early OS imaging
- Implemented sandboxing for hermetic configuration generators
- Led deprecation of legacy net-booting systems, migrating to newer building blocks
- Negotiated technical trade-offs across multiple teams for secure server lifecycle automation

**Unprovisioning** (2021–2023) — asset decommissioning and secure erasure before hardware exits company premises.

- Led deprecation and migration off legacy unprovisioning systems
- Developed and rolled out next-generation unprovisioning workflows
- Worked cross-functionally with DC ops to ensure secure erasure and physical destruction
- Mentored junior engineers across multiple time zones

## IFAD (United Nations) — Tech Lead
*February 2016 – November 2021 · 5 years*

Led the technical side of a critical financial system implementing electronic disbursement of IFAD financings to borrower countries.

- Reviewed technical proposals, authored documentation, interviewed and hired engineers
- Acted as liaison between internal stakeholders, external vendors, and suppliers
- Led full infrastructure automation, persuaded its re-use across existing line-of-business applications
- Oversaw security design, delegated vulnerability assessments and hardening

## IFAD (United Nations) — Software Engineer & Sysadmin
*January 2011 – January 2016 · 5 years*

- Architected and developed multiple LOB applications: DMS, CRMs, BPM workflows, IAM, webcasting
- Built, secured and maintained dev/staging/prod environments for 30+ Ruby applications
- Established shared framework libraries, releasing as open source where possible
- Set up DNS, routing, software distribution, monitoring and alerting infrastructure

## Mind2Mind — Web Developer & Sysadmin
*September 2009 – December 2010*

Refactored and architected front-end and back-end of [panmind.com](http://panmind.com), built with Ruby, Javascript and Erlang. Designed and secured the production environment. Evangelised open source through component extraction and [conference presentations](http://www.slideshare.net/panmind).

## Lime5 — Web Developer & Sysadmin
*February 2008 – November 2009*

Designed and implemented multiple projects: tourism platform (Visita CSA), social music platform ([Myousica](/posts/2024-09-11-myousica-sixteen-years-later/)) with audio streaming on Engine Yard, enterprise knowledge-sharing system (Agorà).

## Softmedia — Web Developer & Sysadmin
*December 1999 – December 2007 · 8 years*

First professional role. Built and maintained UNIX/Windows server infrastructure, site-to-site VPNs, mail systems (Exchange, Zimbra, Postfix), and web applications in PHP and Ruby on Rails.

---

# Open Source & Community

**Recent projects** — [github.com/vjt](https://github.com/vjt)

- **[ha-verisure-italy](https://github.com/vjt/ha-verisure-italy)** — Home Assistant integration for Verisure Italy. GraphQL API client, typed with Pydantic, 165 tests, pyright strict.
- **[openwrt-ha-presence](https://github.com/vjt/openwrt-ha-presence)** — WiFi-based room presence detection for Home Assistant via OpenWrt and MQTT.
- **[quectel-5g-tools](https://github.com/vjt/quectel-5g-tools)** — Parser and monitor for Quectel 5G modems cell information.
- **[mfsroot-geli-dropbear](https://github.com/vjt/mfsroot-geli-dropbear)** — FreeBSD initial RAM disk for remote GELI-encrypted ZFS unlock over SSH.

**Community roots**

- **[Antifork.ORG](https://antifork.org)** (2007–present) — Maintaining the legacy infrastructure and [code](https://github.com/antifork) of this group of hackers/friends from the early 2000s.
- **Azzurra IRC Network** (2002–2005) — Wrote server patches for Italy's largest IRC network: IPv6, SSL, hostname cloaking. Added SSL to the irssi client.

---

# Quotes I Live By

- *Keep looking up* — Neil DeGrasse Tyson
- *Computer science is no more about computers than astronomy is about telescopes* — Dijkstra
- *A name indicates what we seek. An address indicates where it is. A route indicates how we get there* — Jon Postel
- *Be liberal in what you accept, be conservative in what you send* — Jon Postel
