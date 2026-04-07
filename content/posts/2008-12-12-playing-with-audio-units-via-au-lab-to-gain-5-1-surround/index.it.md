---
title: "Giocare con le Audio Units tramite AU Lab per ottenere il surround 5.1"
date: 2008-12-12T01:38:31Z
tags: [apple]
---

{{< figure src="/posts/2008-12-12-playing-with-audio-units-via-au-lab-to-gain-5-1-surround/au_lab_powa.jpg" alt="au lab pwnz" width="600" height="375" >}}

La sessione a destra mostra un documento aperto su un dispositivo audio aggregato tra [soundflower](http://www.cycling74.com/products/soundflower) (2 canali) e una Creative SBLive con 6 canali: il flower riceve l'input audio da iTunes e lo indirizza ai canali della scheda, usando tutti e 6 gli speaker.

Sono stati aggiunti degli effetti per migliorare l'esperienza audio (dettagli qui: [http://www.rottenbrains.com/?p=232](http://www.rottenbrains.com/?p=232)). La sessione a destra usa anche AUNetSend per streamare l'audio verso la sessione a sinistra, connessa agli speaker integrati del MacBook.

Risultato: audio stereo riprodotto su otto canali. Le Audio Units sono uno strumento davvero potente, ben scritto e ben funzionante.

[grazie a nextie per avermi detto di `AUNetSend` e `AUNetReceive`]

## AGGIORNAMENTO 19-12-2008

{{< figure src="/posts/2008-12-12-playing-with-audio-units-via-au-lab-to-gain-5-1-surround/au_lab_powa_II.jpg" alt="au lab pwnz again" width="600" height="375" >}}

Miglioramento: non c'è bisogno di usare NetSend e NetReceive per riprodurre su 8 speaker: un dispositivo aggregato composto da Soundflower 2ch, la SBLive USB a 6 canali e l'uscita Built-in è sufficiente!

Inoltre, nota il nuovo bus: è necessario perché l'effetto AUMatrixReverb aggiunto al canale centrale per migliorare la stereofonia dell'audio in realtà occupa due canali, e quindi si sovrappone a quello successivo (il LFE). Ma applicare l'effetto a un bus non presenta questo effetto collaterale.

Risultato: eccellente 7.1
