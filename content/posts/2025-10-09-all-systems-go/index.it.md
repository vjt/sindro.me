---
title: 'Talk su MetalOS ad All Systems Go! 2025'
date: 2025-10-09
tags: [linux, sysadmin, meta, events]
image: vjt-dubros-on-stage.jpg
featuredImage: vjt-dubros-on-stage.jpg
---

<img src="/posts/2025-10-09-all-systems-go/metalos-logo.png" alt="Logo MetalOS" style="float:right;max-width:150px;margin:0 0 1rem 1rem">

Ho presentato un talk ad [All Systems Go 2025](https://all-systems-go.io/), la conferenza fondamentale sullo userspace Linux. La conferenza è organizzata principalmente dal team di systemd, ed è un punto d'incontro annuale per tutti quelli che lavorano su software di sistema Linux.

Il tema di quest'anno è stato prevalentemente "container, container, container", con molte nuove funzionalità in systemd per supportare la containerizzazione e anche esperienze pratiche da persone che lavorano sul campo su come usano systemd e software collaterali per costruire infrastrutture a container.

Ho presentato insieme al mio collega [Serge Dubrouski](https://www.linkedin.com/in/serge-dubrouski-2902638/) il nostro lavoro nella costruzione di un sistema operativo alla scala di Meta. Gestiamo un sistema operativo basato su immagini, ma l'azienda viene da due decenni di aggiornamenti del SO online, quindi abbiamo dovuto progettare una strategia di migrazione adeguata e gettare le fondamenta per il futuro.

Descriviamo come prepariamo le release CentOS dall'upstream, gli [strumenti OSS](https://github.com/facebookincubator/antlir) che abbiamo costruito per creare le immagini del SO, e la tecnologia interna (MetalOS) che abbiamo ideato per costruire un SO che gira su milioni di server Linux.

Il logo: è metal perché MetalOS gira su bare metal, e le corna sono un riferimento ad [Antlir](https://facebookincubator.github.io/antlir/docs/intro) — **AN**o**T**her **L**inux **I**mage builde**R** — il build system open-source che usiamo per produrre le immagini del SO.

{{< youtube PpDDdLMiPCs >}}

Puoi anche [scaricare il video per la visione offline](/posts/2025-10-09-all-systems-go/asg2025-332-eng-OS_as_a_Service_at_Meta_Platforms_hd.mp4).

Domande? Commenti? Sfogate qui sotto! 🤣
