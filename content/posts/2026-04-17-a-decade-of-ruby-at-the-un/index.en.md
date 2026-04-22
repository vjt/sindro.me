---
title: "A decade of Ruby at the UN"
date: 2026-04-17
tags: [ruby, rails, ifad, retrospective, open-source, panmind]
description: "How IFAD ended up running production Ruby apps since 2008, and what I built there."
image: cover.jpg
featuredImage: cover.jpg
draft: true
---

IFAD runs on a lot of things — PeopleSoft, Oracle, SharePoint, plus a Sybase from the year 2000 that, when I arrived, held a surprising amount of institutional memory. It also runs on Ruby — that's why I was there.

I walked into the Rome offices in the spring of 2011 as a consultant on an agile team that didn't look or act like the rest of the place. The rest of the place was an intergovernmental agency: careful, deliberate, dependent on external vendors, tied to procurement cycles and risk frameworks, understandably slow. Our team was five or six people who shipped software. We didn't replace the enterprise side — we complemented it. When something needed to be done now, and done well, and owned by people inside the building, we got the call.

The person who had made that call possible, years before I arrived, was [Amedeo Paglione](https://www.linkedin.com/in/amedeo-paglione-72a83825/).

<!--more-->

## Why Ruby was already there

Around 2008, well before me, Amedeo was building internal tools at IFAD in Ruby on Rails. The story that got passed down — and that I verified over the next decade — is that he shipped things faster than every contractor the organization had on retainer. Someone inside IFAD noticed. Then someone else noticed. By the time I turned up, Rails was not a rebellion; it was earned territory. You don't argue with the team that ships.

That's the culture I walked into. Ruby wasn't there because anyone made an executive decision to adopt it. It was there because a handful of people had quietly demonstrated, over and over, that they could turn a requirement into working software in the time it took a vendor to write a statement of work.

Amedeo is a visionary, and he thinks in decades. I've written about him in posts about [ChronoModel](/posts/2012-05-07-chronomodel-time-travel-postgresql/) and [Hermes](/posts/2013-10-20-hermes-rails-rumble-2013/), and I'll keep doing it, because almost everything I'm about to describe started with a conversation with him.

## How I got there

In July 2010 I was at [Panmind](/posts/2026-04-12-panmind-ahead-of-its-time/) in Rome, and at a [Ruby Social Club meetup in Milan](/posts/2010-08-05-panmind-at-ruby-social-club/) to present a set of open source plugins we'd been extracting from our product. The plugins weren't revolutionary — an SSL helper, a Google Analytics wrapper, a ReCaptcha interface, a jQuery-driven AJAX navigation layer — but they were careful, documented, tested, and we'd put them on GitHub because they'd been useful to us and might be useful to other people.

In the audience that night was [Simone Carletti](https://github.com/weppos), who worked at IFAD at the time. He listened to a Panmind engineer talk about the plugins he'd written and the decisions behind them, and a few months later asked whether I might be interested in a new opportunity. By the spring of 2011 I was in Rome, on Amedeo's team, writing the members platform.

This is the part I'd like the younger engineer reading this to take seriously: I got that job because I'd been sharing my work publicly. The plugins weren't a marketing exercise — they were the byproduct of real engineering we'd chosen to publish because it felt like the right thing to do. But they had a side effect, which is that they let someone who could only evaluate me from a distance actually evaluate me. Simone could tell, from the commits and the talk, that I could write the code *and* talk about it. That was enough signal to start a conversation.

Share your work. It gives other people a way to find you that a CV never will.

## First assignment: the Member States Platform

My first piece of work was a Rails application that would become, and still is, [webapps.ifad.org/members](https://webapps.ifad.org/members). It's a platform for IFAD's [Member States](https://webapps.ifad.org/members/member-states) — 180 countries as of today that fund the agency and sit on its governing bodies — to see meeting papers, track sessions of the Governing Council and Executive Board, and receive notifications about documents relevant to their seats. The public landing page is the news section. The interesting part sits behind a login.

It looked simple. It wasn't.

### The authorization problem

{{< figure src="authz-matrix.jpg" alt="An ornate leather-bound ledger open on a wooden desk, three woven ribbons of parchment forming a three-dimensional lattice across the pages, lit by a warm brass lamp" >}}

The platform's access rules are a three-dimensional matrix with exceptions on every face. What a given person can see depends on:

- Their role in their country's delegation (head of delegation, alternate, observer, technical expert, and so on).
- Their country's role with IFAD (which List it belongs to, whether it sits on the Executive Board this cycle, whether it's a full member or a special-status attendee).
- Their role in the specific meeting (a country can send a different person to each session, with different privileges).

On top of that, every meeting has its own rules. And on top of *those* rules, there are per-meeting overrides for specific delegations — the kind of carve-out that an intergovernmental agency generates naturally, meeting after meeting. That set of rules drove two things: who could see which documents, and who got the e-mail when a new document was published.

The whole thing was implemented inside the database. A base view encoded the full matrix — person × country × meeting × role-in-meeting — and a hierarchy of additional views layered per-meeting overrides on top. The override views hard-coded the meeting IDs they applied to; a smell anywhere else, but fine here, because a meeting ID — once assigned to a Governing Council or Executive Board session — never changes. Rails queried the views and stayed out of the way. The authorization logic lived where the data lived, which is where it should live. It was fast.

Whatever Ruby-side checks remained on top, I wrote in-line. [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) would eventually be the right place for them, but in 2011 Eaco didn't exist.

### The other half: documents in four languages

The rest of the platform was document distribution in IFAD's four official languages (Arabic, English, French, Spanish). Documents were authored by the Office of the Secretary and published through the platform to delegates; each release triggered notifications, filtered through the authorization matrix above, in the recipient's preferred language.

The descriptions and excerpts that framed each document came in through a WYSIWYG editor, and most of them started their life in Word. Word's HTML is full of junk — inline styles, Office namespaces, `mso-*` attributes, structural noise that looks fine in the editor and looks wrong everywhere else. The work lived on both sides of the pipeline: configuring the editor to normalize its output on the way to the server, and writing sanitization on the backend to strip whatever got through anyway. I iterated on both until pasting from Word produced clean, structured HTML downstream.

The harder part was the workflow and observability around publishing. The Office of the Secretary was responsible for releasing documents and notifying the delegations, and they needed the tools that match that responsibility: drafts they could circulate internally before going live, previews of both the documents and the notification emails each set of recipients would receive, and a way to see — after the fact — who was notified of what.

Then there was batching. You don't want to send ten separate emails to a delegation on a busy publishing day. I built a queueing mechanism that collected notifications as documents went live, waited for a configurable window, and sent them out as digests. Each delegate could choose their own frequency. The design came straight out of years on Linux mailing lists, where the digest option had long been the civilized way to subscribe to a high-volume list.

None of this was novel on its own. Making it hang together coherently, across four languages and a meeting calendar that never paused, was the work.

### The award

{{< figure src="award.jpg" alt="Classical still life: bronze laurel wreath, sealed parchment scroll, and brass plaque resting on a deep crimson velvet cushion on a carved wooden surface, with a gilded picture frame and an oil lamp in the palazzo background" >}}

In December 2011 the platform won [IFAD's Outstanding Project/Initiative award](https://ifad-un.blogspot.com/2011/12/celebrating-27-extraordinary-colleagues.html). The citation went to Amedeo and the three cross-departmental staff who had conceived it, sponsored it, and championed it across silos: Shamela Brown, Victoria Chiartano, and Paola de Leva. Consultants don't qualify for those awards, so my name isn't on the citation. Fair enough — they did the harder job. I got to write the code.

Victoria was my business focal point for the duration of the build. She translated two decades of how IFAD actually runs its governing-body cycles into requirements I could build against, and pushed back when my engineering instincts ran ahead of the business reality. Members is what it is because the engineering and the business analysis were done together, by people who respected each other and argued productively when they disagreed. That combination — good engineering alongside good business competence — is rarer than either alone.

## The Sybase underneath

The Member States Platform was new code, but it didn't live alone. It pulled its people, countries, meetings, sessions, and roles from a back-office system that had been at IFAD long before me: a Java application built around the year 2000, running on top of a Sybase database. The system had a name too — **CIAO**, for *Contact Information Available Online*, which also happens to be the Italian word for hello and goodbye. A back-office at a Rome-based UN agency ought to greet you in Italian; whoever named it in 2000 got that right.

The Java app was adequate for its original purpose, which was to act as an internal registry of people, countries, and events: forms for creating them, screens for editing them, reports for auditing them. Andrea De Baggis, who wrote it in the early 2000s, did a professional job with the tools of the time.

The problem was the data model. It had been implemented using the [entity-attribute-value](https://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model) pattern: one big table holding every attribute of every entity as a row. An entity was a bag of rows; a query for "the list of Heads of Delegation for Governing Council 36 whose country is a List A member" was ten joins and, on a warm day, ten minutes.

That data was the canonical source for more than the back-office. Every Rails app on Amedeo's team that needed to know what a country was, or what role a person held in a meeting, needed it. We reached into the Sybase from our side, with a driver that felt older than some of our code, and made it work. It worked. It was also the most persistent source of pain on the team for years — the authorization views I'd written lived on top of it, and they were only as fast as the substrate they queried.

Amedeo had had the plan from the start. Replacing the legacy back-office was a planned programme with phases, and the Members Platform was the first of them — a visible, self-contained project that would, in retrospect, also serve as a test-bed to demonstrate the agile team could deliver something of that scope inside IFAD's constraints. Once Members was in production, I moved on to the next phase: the back-office itself.

## Rewriting the back-office in Rails

The plan was boring and correct. Stand up a Rails application with a normalized schema, migrate the EAV-encoded data into it one entity type at a time, expose a JSON API, and — when the new system reached parity — retire the Sybase-driven CIAO and let the Rails one take over the name.

Normalization was the easy part. Sybase would give up its data if you were patient with it. I wrote importers, ran them against snapshots, wrote more importers, compared row counts until they matched, and promoted the new schema when they did. The primary keys came across too — every country, meeting, person, and role kept the ID it had held in the EAV database — so anything already holding a reference, inside or outside IFAD, kept resolving through the cut-over. The canonical list of countries, meetings, and people moved to the new system, where a query for the Heads of Delegation took milliseconds instead of minutes.

The harder part was the API. The Members Platform had to switch from reading Sybase to reading the new JSON endpoints — and it had to keep working throughout. The cut-over, predictably, did not land on the first try. That's a story for a post about migrations; it isn't this post.

What's relevant here is what I built on the consuming side, because it became a gem. Rails in 2011–2013 gave you [ActiveResource](https://github.com/rails/activeresource) for consuming JSON APIs, and ActiveResource was too magic, too slow, and too eager to pretend that a remote call was a local method call. I wanted something that looked familiar on the surface — so the rest of the team wouldn't have to learn a new API — but that was honest about network boundaries underneath, and faster in the common case. That gem became [Hawk](https://github.com/ifad/hawk). The idea was a thin, non-magic client layered on top of [Typhoeus](https://github.com/typhoeus/typhoeus) and [Ethon](https://github.com/typhoeus/ethon) — libcurl under the hood — with explicit batching and connection reuse.

Hawk is also still missing its documentation. The usage section in the README has been a `TODO` since my first commit. Lesson: if the docs aren't there on day one, they never arrive, and the project drifts toward NIH — the next person who needs what your gem does finds it easier to write their own than to reverse-engineer yours.

## Reticulum: the graph

{{< figure src="reticulum.jpg" alt="An antique parchment chart on a candlelit table showing a constellation-like network of glowing golden nodes connected by luminous threads with visible loops, a brass astrolabe to the left and a quill in an inkwell to the right" >}}

Hawk and the JSON back-office were, individually, unremarkable pieces of engineering — a client, a server, an API. What made them matter was that Amedeo was already three steps ahead.

His vision, which he had been articulating since before I arrived, was that every system at IFAD holding canonical data should expose it as an HTTP JSON API, and every application that needed that data should consume it over the wire instead of keeping its own copy. Single source of truth per domain. No duplicate country lists, no out-of-sync people databases, no reconciliation scripts that mostly worked. An enterprise service bus, except without the commercial bus product — just HTTP, JSON, and a set of disciplined services.

Internally we called it Reticulum, and it was modeled as a graph — resources linked to other resources, cycles allowed. A country pointed to its Lists; a List pointed back at its members; a meeting pointed at its Governing Body and at the people holding roles in it. Walk the graph in either direction; navigation and dependencies fell out of the same structure.

This sounds ordinary today. In 2012, inside a UN agency, with an enterprise side still wiring systems together through nightly batch files and shared database links, it was ambitious, and it was correct. We built it. Every Rails app on the team eventually spoke the same set of APIs. New apps came up in weeks instead of months, because the hard part — *where is the authoritative list of X* — had been answered once, and the answer was always "call this endpoint."

The agile team didn't replace the enterprise side of IFAD; we weren't trying to. The enterprise side — vendors, procurement, risk frameworks, audit requirements — was solving a different problem on a different clock. What our team did, what Amedeo's model let us do, was run a fast lane beside it. The two lanes spoke JSON to each other when they needed to. Nobody's timeline had to match anybody else's.

## Three around a table

By around 2013 the agile side of IFAD's IT had crystallized into a small group. Amedeo led it. [Lleïr Borràs Metje](https://github.com/lleirborras) joined at about that time as a lead engineer, and from then on he, Amedeo, and I were the core. I wouldn't have shipped half of what I shipped without Lleïr. When a feature needed to land fast, we'd run an internal hackathon — the three of us in a room for a day or two — and ship it end-to-end into one of our tools. One visionary, two engineers who trusted each other, and a team small enough to fit around a table. That's the practical shape of everything Reticulum made possible.

Not everything the three of us did on the agile team is worth a standalone post. A large chunk of those years was infrastructure work nobody writes conference talks about: Ansible playbooks that rolled out Rails apps, server bootstrap, deployment plumbing, monitoring, backup jobs, the ten thousand small things that sit between a git commit and production.

That work isn't exciting in the telling, but it's where the team's credibility came from. When a new Rails app could be provisioned, deployed, and monitored in an afternoon — because the infrastructure was already scripted and already tested — Amedeo's *ship fast, ship right* wasn't a slogan, it was a fact about our tooling.

## Crossing over: tech lead on IBM territory

{{< figure src="crossing-over.jpg" alt="A long arcaded marble corridor in a Roman palazzo, a wood-and-books workspace glimpsed through an open doorway on the left, a single figure in dark attire walking with a satchel toward the formal wing ahead, late afternoon light slanting through clerestory windows" >}}

After several years on the agile team, I crossed into the enterprise side of IFAD's IT as tech lead on a large finance project built on IBM technology. I won't say much about the project itself — most of the work sits under the kind of constraints where "can't say much" is the right answer.

I reported to [Simone Giorgi](https://www.linkedin.com/in/simone-giorgi-2a811a/), with [Thomas Bousios](https://www.linkedin.com/in/thomas-bousios-b49760/) one level up as the director of the area. They picked me because years of shipping on the agile side had earned it. Knowing both sides — software engineering and the infrastructure it runs on — was what the role needed. Thomas was also the director who stood up IFAD's first CISO office and drove the security programme across the estate — enterprise 2FA, network segmentation, service-account discipline. On paper we were an unlikely pairing: him enterprise-oriented, me DIY; in practice it worked, and worked remarkably well — that pairing is what let me ship [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) and the [OneSpan integration](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/).

The stack was different: IBM-based, under governance that runs on slower cycles, more risk scaffolding, narrower room to improvise. Different sport, same game. I brought the agile team's engineering rigor — reviewable code, reproducible deployments, real tests — into a programme that hadn't always demanded them, and got back, from Simone and Thomas, a real education in operating inside tighter governance without losing speed. I owe both of them a debt.

The business analyst on the project was [Michelle Lockwood](https://www.linkedin.com/in/michelle-lockwood-8929a55/), and Michelle was instrumental to its outcome — the same way Victoria and Shamela had been instrumental on Members.

On the IBM side, the vendor's project manager was [Eugenio Catello](https://www.linkedin.com/in/eugenio-catello/). We disagreed often in the early months — different priorities, different clocks, different definitions of done — and the working relationship got steadily better as the programme advanced. What looked like friction early on was two sides calibrating to each other's constraints.

### WebSphere and ISAM

I worked with **WebSphere Application Server** — a piece of Java infrastructure of a very specific era, with its own deployment model, its own tooling, and its own preferred way of doing things. I wrote [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) to bring WebSphere deployment into the same Git-driven, reviewable, idempotent workflow the agile team had taken for granted on Rails. It took a while, because WebSphere does not like being automated.

I also worked with **IBM Security Access Manager** (ISAM), an enterprise authentication gateway from the same family of products. I wrote [omniauth-ibmisam](https://github.com/vjt/omniauth-ibmisam) to let Rails apps accept ISAM-authenticated sessions without pretending to speak the rest of the ISAM ecosystem. That gem is short, unglamorous, and does exactly one useful thing — which is how I like gems.

A large share of the work was integration across the IBM and Oracle sides of IFAD's stack: the kind nobody writes conference talks about, but that keeps organizations running. If you ever have to connect two enterprise products whose vendors swear they were designed to work together — they weren't, they never have been, they never will be — you want Simone and Michelle in the room.

### The log cluster

{{< figure src="log-cluster.jpg" alt="Interior of a grand Italian palazzo archive hall at night, a large open leather-bound codex on a carved marble pedestal at the center, parchment ribbons flowing toward it from smaller scribe desks arranged along the walls, each desk lit by its own brass lamp" >}}

The piece I'm proudest of from those years is the central log aggregation platform. We built it on hardware that would otherwise have gone to waste. Google had retired the Google Search Appliance product line and IFAD's contract had expired; four of those yellow boxes were sitting spare at UNICC. I knew them well — I'd spent time earlier configuring the GSA to index internal content, wrangling regex after regex and never being entirely satisfied with what came out the other end. Amedeo already had his Finder project in the pipeline to replace it, but that's another story. What mattered here was that the hardware was still good: SMART-clean disks in order, RAID10 across 2.5-inch SATA, overbuilt by Google to sustain far more load than it had ever seen at IFAD, underutilized for years. For an Elasticsearch cluster it was, on paper, a perfect fit — machines designed to push through indexing and search workloads already. I asked UNICC to ship them to Rome, and they did. Google's BIOS was locked, and the unlock was a fully documented, supported procedure — once applied, the hardware was ours.

{{< figure src="gsa-servers.jpg" alt="Four yellow Google Search Appliance servers stacked in a rack, each chassis embossed with the Google logo and perforated with the appliance's trademark pattern of round vents; orange fibre cabling visible behind them" >}}

The work landed with two engineers who reported to me: [Riccardo Massullo](https://github.com/riccardomassullo) and [Gian Piero Carrubba](https://github.com/gpiero). They wrote the OS automation that brought the appliances up reproducibly, and the three of us layered Elasticsearch, Kibana, and APM on top under an enterprise license. The cluster collected logs from both sides of IFAD's IT — the Ruby stack on the agile side, the IBM stack on the enterprise side. IBM application servers are noisy; they write fat stack traces ten directories deep across multiple log files, in formats that were never meant to be machine-read twice. We wrote Filebeat configurations that tailed everything and a large Logstash pipeline that parsed it properly — handling multiline records, enriching events with GeoIP and AS-number lookups, and normalizing fields across sources so a Rails request could be cross-checked against the WebSphere call it triggered without translating between two schemas.

What made the cluster useful was less the technology than the audience. IBM shipped its own dashboards for ISAM and WebSphere; they were competent, and they were product-centric — designed to tell you about the product, not about your project. Ours was project-centric. Developers used it to diagnose malfunctioning code across the stack. Sysadmins used it to assess operational status at a glance. Business analysts used it to see how people were actually using the platforms. Security, under CISO [Guillaume Farret](https://www.linkedin.com/in/guillaume-farret/), used it to build alerts on suspicious patterns. One cluster, four audiences, one consistent schema. At its peak the cluster held around 10 TiB of indexed data across roughly two years of retention, with separate rollover policies tuned per data type.

Logs weren't the only telemetry we piped in. IFAD's firewalls and switches had built-in NetFlow exporters that pushed records directly at Logstash, which parsed them into Elasticsearch as they came through. The application servers didn't have that. [Octoflow](https://github.com/ifad/octoflow) was the small Python service Riccardo and I built on top of [nprobe](https://www.ntop.org/products/netflow/nprobe/) to close the gap — a collector/filter/exporter running alongside each app server, generating flow records from its own traffic and shipping them into the same pipeline. The schema followed the [ElastiFlow](https://www.elastiflow.com/) conventions, which gave the security side ready-made Kibana dashboards and a vocabulary the industry already spoke. A web request reaching a WebSphere application server could be paired with the actual packet flows that had carried it.

The cluster ran on the repurposed appliances for years. As the production infrastructure matured, it slowly migrated onto VMs — not because the hardware was failing, but because the operational model around it had moved on. Elasticsearch itself got worse over time, too: each major version a little more bloated, a little less friendly to the sysadmin running it. But that's another story.

## Leaving, 2021

In late 2021 I took an offer from Meta and moved to Dublin. Ten years at IFAD ended in the usual way: a box carried down the stairs of the Rome office, and a lot of handover documents in my laptop. The Rails apps kept running. The APIs kept answering. The enterprise side kept its own clock. None of that needed me anymore, which is how it ought to be.

## What persists

{{< figure src="what-persists.jpg" alt="View from inside an Italian palazzo through an open arched window onto Roman rooftops at dawn, a distant dome silhouette on the horizon, an open leather-bound ledger and a sprig of ivy on the stone sill, an unlit brass lamp beside them, a dim wooden desk visible in the shadow to the left" >}}

[webapps.ifad.org/members](https://webapps.ifad.org/members) is still the URL. The document pages still come in four languages. The [Governing Council documents page](https://webapps.ifad.org/members/gc/49) looks the way it looked the day we shipped it — each news entry still prefixed with the <u>"New Documents Online!"</u> that Victoria used to write by hand in the emails she sent to delegates before the platform existed. Members replaced the manual mails. It did not replace the phrasing.

[ChronoModel](https://github.com/ifad/chronomodel) still gets updates on GitHub; I wrote [a standalone post](/posts/2012-05-07-chronomodel-time-travel-postgresql/) about it and [its 1.0 release](/posts/2019-04-06-chronomodel-one-dot-zero/). [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) still gets updates too. [data-confirm-modal](/posts/2013-07-02-data-confirm-modal/) has, somehow, been [downloaded millions of times](https://rubygems.org/gems/data-confirm-modal). [Geremia Taglialatela](https://github.com/tagliala) — the colleague who inherited Colore when I left — has put 354 commits into the [Heathen / Colore document pipeline](/posts/2016-01-15-document-pipeline-heathen-colore/) since. You leave a place, and the work you did stays there, and the people who come after you make it better than you could.

Amedeo's vision is still the shape of the agile side of IFAD's stack. Small services, clear APIs, single sources of truth, agile team complementing the enterprise machine. It survived a decade.

What I took away from those ten years — more than any of the code — is this: when a place decides to trust a team, protect it, and let it ship, and when that team is led by someone who actually thinks about the organization and not about themselves, you get an extraordinary amount of software out of a very small group of people, over a very long time. That combination is rarer than it should be. And I didn't walk into it by accident — I walked into it because I'd been publishing what I built, and the right person had noticed. That's still the best advice I have for anyone starting out.
