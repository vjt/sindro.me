---
title: 'MetalOS talk at All Systems Go! 2025'
date: 2025-10-09
tags: [linux, sysadmin, meta, events, open-source]
image: vjt-dubros-on-stage.jpg
featuredImage: vjt-dubros-on-stage.jpg
---

<img src="/posts/2025-10-09-all-systems-go/metalos-logo.png" alt="MetalOS logo" style="float:right;max-width:150px;margin:0 0 1rem 1rem">

I presented a talk at [All Systems Go 2025](https://all-systems-go.io/), the foundational Linux userspace conference. The conference is organised mostly by the systemd team, and it's a yearly meeting for all people working on Linux systems software.

This year's theme has mostly been "containers, containers, containers" with many new features in systemd to support containerisation as well as practical experiences from people working in the field on how they're using systemd and collateral software to build container infrastructures.

I presented together with my colleague [Serge Dubrouski](https://www.linkedin.com/in/serge-dubrouski-2902638/) our work in building an Operating System at Meta scale. We run an image-based operating system, but the company comes from two decades of updating the OS online, so we had to design a suitable migration strategy and set the foundation for the future.

We describe how we cut CentOS releases from upstream, the [OSS tools](https://github.com/facebookincubator/antlir) we've built to create OS images, and the internal technology (MetalOS) that we came up with to build an OS that runs on millions of Linux servers.

About the logo: it's metal because MetalOS runs on bare metal, and the antlers are a nod to [Antlir](https://facebookincubator.github.io/antlir/docs/intro) — **AN**o**T**her **L**inux **I**mage builde**R** — the open-source build system we use to produce the OS images.

## Slides

<a href="/posts/2025-10-09-all-systems-go/slides.pdf" class="pdf-download" style="display:inline-block;padding:0.75rem 1.25rem;border:2px solid currentColor;border-radius:4px;text-decoration:none;font-weight:bold;margin:0.5rem 0">📄 Download the slide deck (PDF, 482KB)</a>

<object data="/posts/2025-10-09-all-systems-go/slides.pdf" type="application/pdf" width="100%" height="600" style="margin:1rem 0;border:1px solid #ccc">
  <p>Your browser can't display embedded PDFs. <a href="/posts/2025-10-09-all-systems-go/slides.pdf">Download the slides here</a>.</p>
</object>

## Video

{{< youtube PpDDdLMiPCs >}}

You can also [download the video for offline viewing](/posts/2025-10-09-all-systems-go/asg2025-332-eng-OS_as_a_Service_at_Meta_Platforms_hd.mp4).

Questions? Comments? Rant below! 🤣
