---
title: '"Guess The Friend" — 48 hours of Rails Rumble madness'
date: 2012-10-14
tags: [rails, ruby, hackathon, facebook]
---

{{< retrospective year="2026" >}}
This game used the Facebook Graph API to access your friends list, profile photos, and personal details — name, location, interests, the works. These are **exactly the same APIs** that [Cambridge Analytica](https://en.wikipedia.org/wiki/Facebook%E2%80%93Cambridge_Analytica_data_scandal) exploited in 2018 to harvest data from 87 million Facebook users for political profiling. We built a fun party game; they built a surveillance machine. Facebook shut down these APIs in 2018 after the scandal broke. The game hasn't worked since. The irony is thick — the same platform features that made silly social games possible also enabled one of the biggest privacy scandals in tech history.
{{< /retrospective >}}

Last weekend we competed in [Rails Rumble](http://railsrumble.com/) 2012 — 48 hours to build a web app from scratch using Ruby on Rails, no preparation allowed. Our team was part of the Italian [48rails](http://48rails.org/) community, and we built **Guess The Friend**: a Facebook game that implements the classic [Guess Who?](https://en.wikipedia.org/wiki/Guess_Who%3F) board game, but using your *real* Facebook friends as characters.

<!--more-->

## The team

Four people, one weekend, zero sleep:

- [Andrea Pavoni](https://github.com/andreapavoni) (@apeacox) — team lead, backend
- [Alessandro Vendruscono](https://github.com/vendruscolo) (@vendruscolo) — frontend
- [Claudio Floreani](https://github.com/ClaudioFloreani) (@ClaudioFloreani) — design
- [Marcello Barnaba](https://github.com/vjt) (@vjt) — backend, deployment

## How it works

You log in with Facebook, the app pulls your friends list with their photos and profile data, and you start a match against another player. Each of you gets assigned a "secret friend" from the other player's friend list. Then you take turns asking yes/no questions — "Does this person live in Milan?", "Do they have a beard?" — and eliminate candidates until you guess who it is. Simple concept, surprisingly fun when the faces staring back at you are people you actually know.

## The chaos

Forty-eight hours is both a lot and nothing. You have time to build something real, but not enough to make it clean. The Facebook OAuth dance alone ate a few hours. Deployment was Unicorn behind nginx, pushed via Capistrano to a VPS — the demo ran at `i.sindro.me`. The code is exactly what you'd expect from a 48-hour hackathon: it works, it's ugly, and nobody wrote tests.

Here's a quick video of the game in action:

<video controls width="100%" preload="metadata">
  <source src="/posts/2012-10-14-guess-the-friend-rails-rumble-2012/guessthefriend-reel.mp4" type="video/mp4">
</video>

The code is on GitHub: [andreapavoni/r12-guessthefriend](https://github.com/andreapavoni/r12-guessthefriend) (original) and [vjt/guessthefriend](https://github.com/vjt/guessthefriend) (my fork). Don't expect clean code and full coverage — it's a hackathon artifact, frozen in time.
