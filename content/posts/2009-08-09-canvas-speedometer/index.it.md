---
title: "Canvas Speedometer: un tachimetro HTML5 in un mondo Flash"
date: 2009-08-09
tags: [javascript, html5, open-source]
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
HTML5 Canvas ha vinto. Flash è stato ufficialmente ucciso da Adobe a dicembre 2020. Questo tachimetrino si renderizza ancora perfettamente su qualsiasi browser moderno — ma nessuno si mette più a disegnare widget gauge a mano. D3.js, Chart.js, o anche solo CSS possono farlo con una frazione dello sforzo. Eppure, 52 stelle e 17 fork su GitHub: niente male per un progetto da weekend del 2009. E il mio amico che ha scritto il codice originale? Era praticamente Claude prima che Claude esistesse — sfornava codice di produzione a velocità macchina mentre il resto di noi stava ancora leggendo la documentazione.
{{< /retrospective >}}

L'elemento `<canvas>` è la novità del momento. Safari e Firefox lo supportano, Chrome è appena uscito, e Internet Explorer... vabbè, di Internet Explorer non parliamo. Flash è lo standard de facto per qualsiasi cosa grafica sul web. Un mio amico — uno degli ingegneri più brillanti che conosca, il tipo che implementa un filesystem in una notte e un kernel in una settimana — mi passa un widget tachimetro che ha scritto come codice di pubblico dominio. Figo, ma un po' grezzo. Quindi lo prendo, rifattorizzo tutto in JavaScript object-oriented come si deve, aggiungo il supporto ai temi, risolvo i quirk di Firefox, e scrivo la documentazione.

<!--more-->

## Cinque layer di profondità

La sua intuizione chiave è la performance. Ridisegnare un intero tachimetro ad ogni frame è uno spreco — la cornice, le tacche, i numeri non cambiano mai. Lui impila **cinque canvas separati** uno sopra l'altro: sfondo, indicatori, arco di soglia, lancetta e overlay lucido. Quando il valore cambia, si ridisegna solo il layer della lancetta. Tutto il resto resta fermo. Io lo guardo e penso: geniale.

## La mia parte: impacchettare il motore

Quello che faccio io è rilavorare il tutto per il riuso. Estendo il `CanvasRenderingContext2D` con metodi helper come `fillEllipse()`, `fillPolygon()` e `strokeBoxedArc()`, aggiungo una struttura object-oriented come si deve, il supporto ai temi, e rendo il tachimetro completamente configurabile: valori min/max, angoli di inizio/fine, spaziatura delle tacche, soglia colore e un overlay lucido attivabile.

Il vero dolore è la compatibilità cross-browser. Firefox ha le sue API non-standard per il rendering del testo (`mozPathText` e compagnia bella) che devo polyfillare. E per IE? La libreria `excanvas` di Microsoft traduce le chiamate Canvas in VML — un linguaggio di markup vettoriale presente in IE fin dalla versione 5. Funziona. A malapena.

## Provalo

Il [canvas-speedometer](https://github.com/vjt/canvas-speedometer) è su GitHub. Crediti all'autore originale (preferisce restare anonimo) che ha scritto il codice iniziale — io l'ho solo ripulito, reso manutenibile e portato più avanti. Dimostra che HTML5 può offrire grafica ricca e interattiva senza plugin — niente Flash, niente applet Java, niente generazione di immagini lato server. Solo JavaScript e un tag `<canvas>`. Secondo me questo è il futuro.
