---
title: "Canvas Speedometer: an HTML5 gauge when Flash was still king"
date: 2009-08-09
tags: [javascript, html5, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
HTML5 Canvas won. Flash was officially killed by Adobe in December 2020. This little speedometer still renders perfectly in every modern browser — but nobody hand-rolls gauge widgets anymore. D3.js, Chart.js, or even pure CSS can do this with a fraction of the effort. Still, 52 stars and 17 forks on GitHub: my most starred repo, and I'm unreasonably proud of it.
{{< /retrospective >}}

It's summer 2009, and the `<canvas>` element is the new shiny thing. Safari and Firefox support it, Chrome just shipped, and Internet Explorer... well, let's not talk about Internet Explorer. Flash is how you do anything graphical on the web. But I wanted to see what this Canvas API could really do — so I built a fully animated, themed speedometer gauge widget entirely in JavaScript.

<!--more-->

## Five layers deep

The key insight was performance. Redrawing an entire gauge on every frame is wasteful — the bezel, the ticks, the numbers never change. So I stacked **five separate canvas elements** on top of each other: background, dial markings, threshold arc, needle, and gloss overlay. When the value changes, only the needle layer redraws. Everything else stays put. It sounds obvious now; in 2009 it felt like black magic.

## The API that didn't exist yet

Canvas gave you rectangles, arcs, and Bezier curves. That's it. I needed ellipses, filled polygons, and boxed arcs — so I extended `CanvasRenderingContext2D` with helper methods like `fillEllipse()`, `fillPolygon()`, and `strokeBoxedArc()`. The gauge is fully configurable: min/max values, start/end angles, tick spacing, color threshold, and a toggleable glossy overlay that makes it look like a real instrument.

The real pain was cross-browser compatibility. Firefox had its own non-standard text rendering APIs (`mozPathText` and friends) that I had to polyfill. And for IE? Microsoft's own `excanvas` library translated Canvas calls to VML — a vector markup language that shipped with IE since version 5. It worked. Barely.

## Try it

The [canvas-speedometer](https://github.com/vjt/canvas-speedometer) is on GitHub. It proves that HTML5 can deliver rich, interactive graphics without plugins — no Flash, no Java applets, no server-side image generation. Just JavaScript and a `<canvas>` tag. I think this is the future.
