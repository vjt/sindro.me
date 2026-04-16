---
title: "Myousica, diciotto anni dopo"
date: 2026-04-11
tags: ["myousica", "panmind", "retrospective", "music", "open-source"]
description: "Diciotto anni dopo aver iniziato a costruire Myousica, la piattaforma di musica collaborativa che era troppo in anticipo sui tempi — uno sguardo a cosa abbiamo costruito, perché non ha funzionato, e chi lo fa oggi."
image: cover.jpg
featuredImage: cover.jpg
---

Oggi è il mio compleanno, e ho deciso di aprire una capsula del tempo.

Diciotto anni fa, abbiamo iniziato a costruire [Myousica](/it/posts/2008-09-11-myousica-com-was-born-today/) — una piattaforma per creare musica collaborativamente nel browser. Registra dal microfono, carica tracce, remixa la musica degli altri, costruisci canzoni insieme a sconosciuti dall'altra parte del mondo. Abbiamo [lanciato a settembre 2008](/it/posts/2008-09-11-myousica-com-was-born-today/) dopo nove mesi di sviluppo.

Era una startup. Ha funzionato per circa cinque mesi prima di essere messa in pausa, e il codice sorgente è stato poi [rilasciato su GitHub](https://github.com/mewsic) con il nome Mewsic. Ho scritto dei dettagli tecnici in una serie di tre post: la [piattaforma Rails](/it/posts/2010-10-14-myousica-collaborative-music-remixing-platform/), l'[editor multitraccia Flash](/it/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/) e la [pipeline audio](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/). Quei post coprono l'ingegneria. Questo è sul quadro più ampio.

<!--more-->

## L'idea giusta al momento sbagliato

Il concetto di base era solido: permettere a chiunque di fare musica in un browser, in modo collaborativo. Nessun software da installare. Apri il browser, scegli una canzone, aggiungi la tua traccia di chitarra, condividi il risultato. Un musicista a Roma poteva iniziare un beat, qualcuno a Tokyo poteva aggiungere il basso, una cantante a San Paolo poteva metterci la voce sopra. Tutto nel browser.

Il problema era che nel 2008 i browser non sapevano fare niente di tutto questo nativamente.

Per catturare l'audio dal microfono serviva Flash — un front-end ActionScript nel plugin Flash Player. Per inviare quell'audio a un server serviva RTMP — un media server Java ([Red5](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/#red5-il-ponte-rtmp)) solo per ricevere l'audio e scriverlo su disco come file FLV. Per trasformare quegli FLV in MP3 riproducibili serviva una [pipeline](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/) di ffmpeg, sox e worker in background lato server. Per mostrare una forma d'onda la renderizzavi come PNG — la Canvas API non era abbastanza matura. Per riprodurre più tracce sincronizzate costruivi un [motore di riproduzione custom](/it/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/#il-sampler) in ActionScript con sincronizzazione al frame.

L'intera architettura esisteva per compensare ciò che il browser non sapeva fare. Quattro servizi separati, ~2.000 commit, mezza dozzina di tool esterni — tutto per ottenere qualcosa che la [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) avrebbe reso possibile in poche centinaia di righe di JavaScript.

## Microservizi accidentali

Un dettaglio divertente: la nostra architettura a quattro servizi — app Rails, multitraccia Flash, media server Red5, [uploader](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/) di elaborazione audio — precede il termine "microservizi." James Lewis presentò il concetto al 33rd Degree a Cracovia nel 2012, e Martin Fowler lo [rese popolare](https://martinfowler.com/articles/microservices.html) nel 2014. Noi non chiamavamo la nostra architettura in nessun modo. Avevamo semplicemente bisogno di servizi separati perché un'unica app Rails non poteva gestire la transcodifica audio, lo streaming RTMP in tempo reale e un editor multitraccia contemporaneamente.

Ma guardando indietro, era esattamente quello: servizi indipendenti che comunicano via callback HTTP, autenticazione stateless basata su token, nulla di condiviso tranne il filesystem per lo spool audio. L'uploader non sapeva nulla di utenti o canzoni — elaborava file audio e faceva [callback](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/#la-pipeline-di-encoding) all'app principale quando aveva finito. Red5 non sapeva nulla di nulla — registrava stream RTMP su disco. Ogni servizio aveva un compito solo.

Semplicemente non avevamo ancora un nome per il pattern. Per essere onesti, era un servizio in più — non esattamente un manifesto sui sistemi distribuiti. Ma è divertente che quello che consideravamo "buon senso" sarebbe diventato un intero movimento architetturale pochi anni dopo.

## Cosa esiste oggi

Apri [BandLab](https://www.bandlab.com/) nel browser adesso. Troverai un editor multitraccia completo con registrazione, strumenti virtuali, effetti, collaborazione in tempo reale, condivisione. Gratuito. Oltre sessanta milioni di utenti. Fondato nel 2015.

[Soundtrap](https://www.soundtrap.com/) è nato nel 2012, è stato acquisito da Spotify nel 2017 e rivenduto ai fondatori nel 2023. Studio musicale collaborativo nel browser. Più persone che editano lo stesso progetto in tempo reale.

[Splice](https://splice.com/) è nato nel 2013. Collaborazione cloud con version control per progetti musicali — tipo Git per sessioni DAW — più un enorme marketplace di sample royalty-free.

Fanno tutti quello che faceva Myousica. Registrare nel browser. Sovrapporre tracce. Collaborare con altri musicisti. Costruire canzoni insieme. La differenza è che hanno lanciato quando la tecnologia era pronta: la Web Audio API per l'elaborazione audio nativa, WebRTC per lo streaming in tempo reale, la MediaRecorder API per l'accesso al microfono, i Web Workers per il multithreading, e il tipo di banda che non ti costringe a scegliere tra lo streaming audio e il caricamento di una pagina web.

Noi abbiamo costruito la stessa cosa otto anni prima, e abbiamo dovuto costruirci mezzo browser per farlo.

## Cosa resta

Il codice è su [GitHub](https://github.com/mewsic). Cinque repository, dall'[app Rails](/it/posts/2010-10-14-myousica-collaborative-music-remixing-platform/) al [multitraccia ActionScript](/it/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/) alla [pipeline audio](/it/posts/2010-10-18-myousica-from-microphone-to-mp3/). Non come prodotto — come capsula del tempo. Un documento di cosa serviva per fare audio collaborativo nel browser nel 2008, prima che esistesse qualsiasi API per renderlo ragionevole.

![Pisolino da hackathon — lo stato naturale di uno sviluppatore durante il crunch](/it/posts/2026-04-11-myousica-eighteen-years-later/hackathon-nap.jpg)

Sono orgoglioso di quello che abbiamo costruito. [Vaclav Vancura](https://vancura.design/) ha progettato un [multitraccia straordinario](/it/posts/2010-10-16-myousica-multitrack-audio-mixing-in-the-browser/) in ActionScript — 7.000 righe di codice splendidamente architettato. [Andrea Franz](https://github.com/pilu) e [Giovanni Intini](https://github.com/intinig) hanno costruito le fondamenta sia dell'app principale che dell'uploader. [Fabio Grande](https://www.fabiogrande.com/) ha disegnato l'identità visiva — la UI, il logo, tutto il look and feel. E noi cinque, in ~2.000 commit, abbiamo consegnato una piattaforma musicale collaborativa che funzionava davvero. Potevi aprire un browser, registrare una traccia, e suonare con qualcuno dall'altra parte del pianeta. Nel 2008.

![La chitarra rosa di Fabio con il logo Myousica — durante le sessioni di registrazione dei contenuti audio per il sito](/it/posts/2026-04-11-myousica-eighteen-years-later/myousica-guitar.jpg)

Myousica è stato un successo commerciale? No. L'idea era giusta? Sessanta milioni di utenti BandLab dicono di sì.

Eravamo solo troppo in anticipo.
