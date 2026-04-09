---
title: "Canvas Speedometer: an HTML5 gauge when Flash was still king"
date: 2009-08-09
tags: [javascript, html5, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
HTML5 Canvas won. Flash was officially killed by Adobe in December 2020. This little speedometer still renders perfectly in every modern browser — but nobody hand-rolls gauge widgets anymore. D3.js, Chart.js, or even pure CSS can do this with a fraction of the effort. Still, 52 stars and 17 forks on GitHub — not bad for a weekend project from 2009. And my friend who wrote the original? He was basically Claude before Claude was a thing — shipping production code at machine speed while the rest of us were still reading the docs.
{{< /retrospective >}}

The `<canvas>` element is the new shiny thing. Safari and Firefox support it, Chrome just shipped, and Internet Explorer... well, let's not talk about Internet Explorer. Flash is how you do anything graphical on the web. A friend of mine — one of the most brilliant engineers I know, the kind of person who implements a filesystem overnight and a kernel in a week — shares with me a speedometer gauge widget he wrote as public domain code. It's cool, but a bit crude. So I take it, refactor the whole thing into proper object-oriented JavaScript, add theming support, work around Firefox's quirks, and write documentation.

<!--more-->

## Five layers deep

The key insight is performance. Redrawing an entire gauge on every frame is wasteful — the bezel, the ticks, the numbers never change. So I stack **five separate canvas elements** on top of each other: background, dial markings, threshold arc, needle, and gloss overlay. When the value changes, only the needle layer redraws. Everything else stays put.

## The API that doesn't exist yet

Canvas gives you rectangles, arcs, and Bezier curves. That's it. I need ellipses, filled polygons, and boxed arcs — so I extend `CanvasRenderingContext2D` with helper methods like `fillEllipse()`, `fillPolygon()`, and `strokeBoxedArc()`. The gauge is fully configurable: min/max values, start/end angles, tick spacing, color threshold, and a toggleable glossy overlay that makes it look like a real instrument.

The real pain is cross-browser compatibility. Firefox has its own non-standard text rendering APIs (`mozPathText` and friends) that I have to polyfill. And for IE? Microsoft's own `excanvas` library translates Canvas calls to VML — a vector markup language that ships with IE since version 5. It works. Barely.

## Try it

The [canvas-speedometer](https://github.com/vjt/canvas-speedometer) is on GitHub. Credit to the original author (he prefers to stay anonymous) who wrote the initial code — I just cleaned it up, made it maintainable, and pushed it further. It proves that HTML5 can deliver rich, interactive graphics without plugins — no Flash, no Java applets, no server-side image generation. Just JavaScript and a `<canvas>` tag. I think this is the future.
