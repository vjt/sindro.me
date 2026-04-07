---
title: 'MetalOS talk at All Systems Go! 2025'
date: 2025-10-09
tags: [linux, sysadmin, meta]
categories: [development]
---

I presented a talk at [All Systems Go 2025](https://all-systems-go.io/), the foundational Linux userspace conference. The conference is organised mostly by the systemd team, and it's a yearly meeting for all people working on Linux systems software.

This year's theme has mostly been "containers, containers, containers" with many new features in systemd to support containerisation and as well practical experiences from people working in the field on how they're using systemd and collateral software to build container infrastructures.

![Me and Serge on stage](/posts/2025-10-09-all-systems-go/vjt-dubros-on-stage.jpg)

I presented together with my colleague [Serge Dubrouski](https://www.linkedin.com/in/serge-dubrouski-2902638/) our work in building an Operating System at Meta scale. We run an image-based operating system, but the company comes from two decades of updating the OS online, so we had to design a suitable migration strategy and set the foundation for the future.

We describe how we cut CentOS releases from upstream, the [OSS tools](https://github.com/metaincubator/antlir) we've built to create OS images, and the internal technology (MetalOS) that we came up with to build an OS that runs on millions of Linux servers.

{{< youtube PpDDdLMiPCs >}}

You can also [download the video for offline viewing](/posts/2025-10-09-all-systems-go/asg2025-332-eng-OS_as_a_Service_at_Meta_Platforms_hd.mp4).

Questions? Comments? Rant below! 🤣
