---
title: "Myousica, sixteen years later"
date: 2024-09-11
tags: ["myousica", "mewsic", "retrospective", "music", "open-source"]
description: "Sixteen years after launching Myousica, the collaborative music platform that was too early for its own good — a look back at what we built, why it didn't work, and who's doing it now."
image: cover.jpg
featuredImage: cover.jpg
---

Sixteen years ago today, we launched [Myousica](/posts/2008-09-11-myousica-com-was-born-today/) — a platform for collaborative music creation in the browser. Record from your microphone, upload tracks, remix other people's music, build songs together with strangers across the internet. In 2008.

It was a startup. It ran for about five months before being paused, and the source code was eventually [released on GitHub](https://github.com/mewsic) under the name Mewsic. I wrote about the technical details in a three-part series: the [Rails platform](/posts/2010-10-14-myousica-collaborative-music-remixing-platform/), the [Flash multitrack editor](/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/), and the [audio pipeline](/posts/2010-10-18-myousica-from-microphone-to-mp3/). Those posts cover the engineering. This one is about the bigger picture.

## The right idea at the wrong time

The core concept was solid: let anyone make music in a web browser, collaboratively. No software to install. Open your browser, pick a song, add your guitar track, share the result. A musician in Rome could start a beat, someone in Tokyo could add bass, a singer in São Paulo could lay down vocals on top. All in the browser.

The problem was that in 2008, browsers couldn't do any of this natively.

To capture audio from a microphone, you needed Flash — an ActionScript front-end running in the Flash Player plugin. To stream that audio to a server, you needed RTMP — a Java media server ([Red5](https://github.com/mewsic/mewsic-red5)) just to receive the audio and write it to disk as FLV files. To turn those FLV files into playable MP3s, you needed a [pipeline](/posts/2010-10-18-myousica-from-microphone-to-mp3/) of ffmpeg, sox, and background workers on the server side. To display a waveform, you rendered it as a PNG — the Canvas API wasn't mature enough. To play back multiple tracks in sync, you built a [custom playback engine](/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/#the-sampler) in ActionScript with frame-accurate timing.

The entire architecture existed to compensate for what the browser couldn't do. Four separate services, ~2,000 commits, half a dozen external tools — all to achieve something that the [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) would later make possible in a few hundred lines of JavaScript.

## Accidental microservices

Here's a fun detail: our four-service architecture — Rails app, Flash multitrack, Red5 media server, audio processing [uploader](https://github.com/mewsic/mewsic-uploader) — predates the term "microservices." James Lewis presented the concept at 33rd Degree in Kraków in 2012, and Martin Fowler [popularized it](https://martinfowler.com/articles/microservices.html) in 2014. We didn't call our architecture anything. We just needed separate services because one Rails app couldn't handle audio transcoding, real-time RTMP streaming, and a multitrack editor at the same time.

But looking back, that's what it was: independent services communicating via HTTP callbacks, stateless token-based authentication between them, shared nothing except the filesystem for audio spools. The uploader didn't know about users or songs — it just processed audio files and [called back](/posts/2010-10-18-myousica-from-microphone-to-mp3/#the-encoding-pipeline) to the main app when done. Red5 didn't know about anything — it just recorded RTMP streams to disk. Each service had one job.

We just didn't have a name for the pattern yet. To be fair, it was one extra service — not exactly a distributed system manifesto. But it's amusing that what we considered "just common sense" would become a whole architecture movement a few years later.

## What exists today

Open [BandLab](https://www.bandlab.com/) in your browser right now. You'll find a full multitrack editor with recording, virtual instruments, effects, real-time collaboration, sharing. Free. Over sixty million users. Founded in 2015.

[Soundtrap](https://www.soundtrap.com/) launched in 2012, was acquired by Spotify in 2017, and sold back to its founders in 2023. Browser-based collaborative music studio. Multiple people editing the same project in real time.

[Splice](https://splice.com/) launched in 2013. Cloud-based collaboration with version control for music projects — like Git for DAW sessions — plus a massive royalty-free sample marketplace.

They all do what Myousica did. Record in the browser. Layer tracks. Collaborate with other musicians. Build songs together. The difference is that they launched when the technology was ready: the Web Audio API for native audio processing, WebRTC for real-time streaming, the MediaRecorder API for microphone access, Web Workers for multithreading, and the kind of bandwidth that doesn't make you choose between streaming audio and loading a webpage.

We built the same thing six years earlier, and we had to build half the browser to do it.

## What remains

The code is on [GitHub](https://github.com/mewsic). Five repositories, from the [Rails app](https://github.com/mewsic/mewsic) to the [ActionScript multitrack](https://github.com/mewsic/mewsic-multitrack) to the [Red5 configuration](https://github.com/mewsic/mewsic-red5). Not as a product — as a time capsule. A record of what it took to do browser-based collaborative audio in 2008, before any of the APIs existed to make it reasonable.

I'm proud of what we built. [Vaclav Vancura](https://vancura.design/) designed an [extraordinary multitrack editor](/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/) in ActionScript — 7,000 lines of impeccable code that I never once had to debug. [Andrea Franz](https://github.com/pilu) built the uploader foundation. And the five of us, across ~2,000 commits, shipped a collaborative music platform that actually worked. You could open a browser, record a track, and jam with someone on the other side of the planet. In 2008.

Was Myousica a commercial success? No. Was the idea right? Sixty million BandLab users say so.

We were just too early.
