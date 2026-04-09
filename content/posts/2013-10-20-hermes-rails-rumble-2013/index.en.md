---
title: "Hermes: contextual help in 48 hours (Rails Rumble 2013)"
date: 2013-10-20
tags: [rails, ruby, open-source, hackathon]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
The "contextual help" space exploded into a whole product category — Intercom, Pendo, Appcues and others now do this commercially at scale. IFAD's fork lived on for years inside the agency. The Rails Rumble itself stopped running after 2015, and the era of 48-hour competition hackathons gave way to AI hackathons and startup weekends. The [repo](https://github.com/vjt/r13-hermes) is archived but still up.
{{< /retrospective >}}

The [Rails Rumble](http://railsrumble.com/) is — was — a 48-hour hackathon where teams of up to four people build a complete web app from scratch using Ruby. No prep work, no pre-written code. Just caffeine, git, and a deadline.

This year our team — [@amedeo](https://github.com/amedeo), [@liquid1982](https://github.com/liquid1982), [@maisongb](https://github.com/maisongb), and me — built **Hermes: the epic messenger service**, entry #385.

<!--more-->

## What Hermes does

The idea was simple but genuinely useful: give site owners a way to embed **contextual help** into their web applications. Think tooltips, banners, tutorials — content that appears on the right page at the right time, without hard-coding anything into the host app.

The integration was a single `<script>` tag. That JS file opened a channel back to the Hermes backend, which looked up the current URL and returned the help payload for that page. Site owners managed everything through a dashboard — no deploy needed to update a tooltip or add a walkthrough step.

## 48 hours at 48rails

We built the whole thing at [48rails](https://web.archive.org/web/2013*/48rails.com), a coworking space in Italy that was basically our home base for this kind of insanity. Two days of intense coding, questionable food choices, and zero sleep. The usual.

The app was a standard Rails stack — nothing exotic. The interesting part was the JS client, and in particular the **element inspector**: an in-page tool that lets admins pick which DOM element to attach help content to. It works by creating four red overlay `<div>`s (N/S/E/W) that frame whichever element is under the cursor, using `getBoundingClientRect()` with scroll offset compensation. On click, it walks the DOM upward computing a CSS selector via `id` or `nth-child`, then sends it back to the admin panel via `postMessage`. A crude, beautiful hack — we built our own mini browser inspector in a hackathon. The [code is here](https://github.com/vjt/r13-hermes/blob/master/app/assets/javascripts/hermes.js) if you want to see the `author` function.

## From hackathon to the UN

About a year later, in November 2014, I brought Hermes into [IFAD](https://www.ifad.org/) — a specialized agency of the United Nations, where I was working. My team there funded continued development, the repo moved to [ifad/hermes](https://github.com/ifad/hermes), and it became a real internal tool for delivering quick, context-aware tutorials across our line-of-business web applications. The concept is everywhere now — every SaaS product has onboarding tooltips and contextual help. When we built it, it was genuinely innovative.

A weekend hackathon project finding a home at a UN agency. That's the kind of thing that makes you think the open-source model actually works — sometimes the best way to prove an idea is to build it in 48 hours and put it on GitHub.

The code: [github.com/vjt/r13-hermes](https://github.com/vjt/r13-hermes)
