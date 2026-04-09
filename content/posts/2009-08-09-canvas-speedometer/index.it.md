---
title: "Canvas Speedometer: un tachimetro HTML5 quando Flash era ancora re"
date: 2009-08-09
tags: [javascript, html5, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
HTML5 Canvas ha vinto. Flash è stato ufficialmente ucciso da Adobe a dicembre 2020. Questo tachimetrino si renderizza ancora perfettamente su qualsiasi browser moderno — ma nessuno si mette più a disegnare widget gauge a mano. D3.js, Chart.js, o anche solo CSS possono farlo con una frazione dello sforzo. Eppure, 52 stelle e 17 fork su GitHub: il mio repo più stellato, e ne vado irragionevolmente fiero.
{{< /retrospective >}}

Siamo nell'estate 2009, e l'elemento `<canvas>` è la novità del momento. Safari e Firefox lo supportano, Chrome è appena uscito, e Internet Explorer... vabbè, di Internet Explorer non parliamo. Flash è lo standard de facto per qualsiasi cosa grafica sul web. Ma io volevo capire cosa potesse davvero fare questa Canvas API — e così ho costruito un tachimetro animato, a tema, completamente configurabile, tutto in JavaScript.

<!--more-->

## Cinque layer di profondità

L'intuizione chiave era la performance. Ridisegnare un intero tachimetro ad ogni frame è uno spreco — la cornice, le tacche, i numeri non cambiano mai. Quindi ho impilato **cinque canvas separati** uno sopra l'altro: sfondo, indicatori, arco di soglia, lancetta e overlay lucido. Quando il valore cambia, si ridisegna solo il layer della lancetta. Tutto il resto resta fermo. Sembra ovvio adesso; nel 2009 sembrava magia nera.

## L'API che non esisteva ancora

Canvas ti dava rettangoli, archi e curve di Bezier. Punto. Io avevo bisogno di ellissi, poligoni pieni e archi inscatolati — e quindi ho esteso il `CanvasRenderingContext2D` con metodi helper come `fillEllipse()`, `fillPolygon()` e `strokeBoxedArc()`. Il tachimetro è completamente configurabile: valori min/max, angoli di inizio/fine, spaziatura delle tacche, soglia colore e un overlay lucido attivabile che gli dà l'aspetto di uno strumento vero.

Il vero dolore era la compatibilità cross-browser. Firefox aveva le sue API non-standard per il rendering del testo (`mozPathText` e compagnia bella) che ho dovuto polyfillare. E per IE? La libreria `excanvas` di Microsoft traduceva le chiamate Canvas in VML — un linguaggio di markup vettoriale presente in IE fin dalla versione 5. Funzionava. A malapena.

## Provalo

Il [canvas-speedometer](https://github.com/vjt/canvas-speedometer) è su GitHub. Dimostra che HTML5 può offrire grafica ricca e interattiva senza plugin — niente Flash, niente applet Java, niente generazione di immagini lato server. Solo JavaScript e un tag `<canvas>`. Secondo me questo è il futuro.
