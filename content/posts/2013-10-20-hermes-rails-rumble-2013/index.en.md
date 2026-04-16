---
title: "Hermes: contextual help in 48 hours (Rails Rumble 2013)"
date: 2013-10-20
tags: [rails, ruby, open-source, hackathon, ifad]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
The "contextual help" space exploded into a whole product category — Intercom, Pendo, Appcues and others now do this commercially at scale. IFAD's fork lived on for years inside the agency. The Rails Rumble itself stopped running after 2015, and the era of 48-hour competition hackathons gave way to AI hackathons and startup weekends. The [repo](https://github.com/vjt/r13-hermes) is archived but still up.
{{< /retrospective >}}

The [Rails Rumble](http://railsrumble.com/) is — was — a 48-hour hackathon where teams of up to four people build a complete web app from scratch using Ruby. No prep work, no pre-written code. Just caffeine, git, and a deadline.

This year our team — [@amedeo](https://github.com/amedeo), [@liquid1982](https://github.com/liquid1982), [@maisongb](https://github.com/maisongb), and me — built **Hermes: the epic messenger service**, entry #385.

(My [previous Rumble entry](/posts/2012-10-14-guess-the-friend-rails-rumble-2012/) was *Guess The Friend* in 2012, with a different team.)

<!--more-->

## What Hermes does

The idea was simple but genuinely useful: give site owners a way to embed **contextual help** into their web applications. Think tooltips, banners, tutorials — content that appears on the right page at the right time, without hard-coding anything into the host app.

The integration was a single `<script>` tag. That JS file opened a channel back to the Hermes backend, which looked up the current URL and returned the help payload for that page. Site owners managed everything through a dashboard — no deploy needed to update a tooltip or add a walkthrough step.

## 48 hours at 48rails

We built the whole thing at [48rails](https://web.archive.org/web/2013*/48rails.com), a coworking space in Italy that was basically our home base for this kind of insanity. Two days of intense coding, questionable food choices, and zero sleep. The usual.

The app was a standard Rails stack — nothing exotic. But the piece I'm most proud of is the **element inspector** I wrote for the authoring mode. You know how browser DevTools let you hover over elements and they light up? I built that from scratch, in a hackathon, sleep-deprived, with beer. Four red overlay `<div>`s (N/S/E/W) that dynamically reposition themselves around whichever element is under your cursor using `getBoundingClientRect()` with scroll compensation. You move the mouse, the red frame follows. Click, and it walks the DOM upward computing a unique CSS selector via `id` or `nth-child`, then fires it back to the admin panel via `postMessage`. The popup closes, and boom — you've just told Hermes exactly where to attach your help tooltip. No manual CSS selector writing, no inspecting source code. Just point and click. [Look at it](https://github.com/vjt/r13-hermes/blob/master/app/assets/javascripts/hermes.js#L184) — it's rough, it's hacky, and it's one of the most satisfying things I've ever written at 3 AM.

## From hackathon to the UN

Here's the thing about Amedeo, my boss at [IFAD](https://www.ifad.org/) — a specialized agency of the United Nations. He's one of those people who spends time looking out of the window, and you think he's daydreaming, but really he's mapping business processes and real-world needs into clever designs in his head. Then he turns around and drops something brilliant on you.

Hermes was one of those moments. We weren't talking about a help system before. Nobody had a contextual help project on any roadmap. When the Rails Rumble comes around and the team needs an idea, Amedeo comes back from a little nap and says "contextual help — a script tag you drop into any web app, and it handles the rest." Out of the blue. The team loves it instantly.

That's what makes Hermes good: the idea is genuinely original, not something we've been kicking around forever. It comes from someone who understands how people actually use line-of-business applications, and who sees the gap nobody else notices. After the Rumble, we promote the project into IFAD, the repo moves to [ifad/hermes](https://github.com/ifad/hermes), and we even hire one of the team members for a period to keep developing it. It becomes a real internal tool — quick, context-aware tutorials across our web applications. Everything stays open source.

The concept is everywhere now — every SaaS product has onboarding tooltips and contextual help. When we built it, it was genuinely innovative. Sometimes the best hackathon projects come from a visionary who knows the problem cold, even when nobody else sees it yet.

The code: [github.com/vjt/r13-hermes](https://github.com/vjt/r13-hermes)


---

**Open source from the IFAD years:** [ChronoModel](/posts/2012-05-07-chronomodel-time-travel-postgresql/) (2012) • [data-confirm-modal](/posts/2013-07-02-data-confirm-modal/) (2013) • **Hermes (2013)** • [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • [TM → Pontoon](/posts/2018-02-14-translation-memory-pontoon/) (2018) • [ChronoModel 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • [OneSpan 2FA](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/) (2020) • [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) (2026)
