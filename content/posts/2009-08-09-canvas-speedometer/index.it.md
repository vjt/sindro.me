---
title: "Canvas Speedometer: un tachimetro HTML5 quando Flash era ancora re"
date: 2009-08-09
tags: [javascript, html5, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
HTML5 Canvas ha vinto. Flash è stato ufficialmente ucciso da Adobe a dicembre 2020. Questo tachimetrino si renderizza ancora perfettamente su qualsiasi browser moderno — ma nessuno si mette più a disegnare widget gauge a mano. D3.js, Chart.js, o anche solo CSS possono farlo con una frazione dello sforzo. Eppure, 52 stelle e 17 fork su GitHub: niente male per un progetto da weekend del 2009.
{{< /retrospective >}}

L'elemento `<canvas>` è la novità del momento. Safari e Firefox lo supportano, Chrome è appena uscito, e Internet Explorer... vabbè, di Internet Explorer non parliamo. Flash è lo standard de facto per qualsiasi cosa grafica sul web. Ma io voglio capire cosa può davvero fare questa Canvas API — e così sto costruendo un tachimetro animato, a tema, completamente configurabile, tutto in JavaScript.

<!--more-->

## Cinque layer di profondità

L'intuizione chiave è la performance. Ridisegnare un intero tachimetro ad ogni frame è uno spreco — la cornice, le tacche, i numeri non cambiano mai. Quindi impilo **cinque canvas separati** uno sopra l'altro: sfondo, indicatori, arco di soglia, lancetta e overlay lucido. Quando il valore cambia, si ridisegna solo il layer della lancetta. Tutto il resto resta fermo.

## L'API che non esiste ancora

Canvas ti dà rettangoli, archi e curve di Bezier. Punto. Io ho bisogno di ellissi, poligoni pieni e archi inscatolati — e quindi estendo il `CanvasRenderingContext2D` con metodi helper come `fillEllipse()`, `fillPolygon()` e `strokeBoxedArc()`. Il tachimetro è completamente configurabile: valori min/max, angoli di inizio/fine, spaziatura delle tacche, soglia colore e un overlay lucido attivabile che gli dà l'aspetto di uno strumento vero.

Il vero dolore è la compatibilità cross-browser. Firefox ha le sue API non-standard per il rendering del testo (`mozPathText` e compagnia bella) che devo polyfillare. E per IE? La libreria `excanvas` di Microsoft traduce le chiamate Canvas in VML — un linguaggio di markup vettoriale presente in IE fin dalla versione 5. Funziona. A malapena.

## Provalo

Il [canvas-speedometer](https://github.com/vjt/canvas-speedometer) è su GitHub. Dimostra che HTML5 può offrire grafica ricca e interattiva senza plugin — niente Flash, niente applet Java, niente generazione di immagini lato server. Solo JavaScript e un tag `<canvas>`. Secondo me questo è il futuro.
