---
date: 2009-02-20T04:00:00Z
title: Il bordo lampeggiante offuscato
tags: [javascript, obfuscated]
categories: [development]
---

Questo e' il pezzo di codice Javascript offuscato che implementa il bordo rosso
e carica [Google Analytics](https://www.google.com/analytics) sul [sito
Segmentation Fault](https://segmentation-fault.core-dumped.info/):

```javascript
var theLoadSequenceToRunAfterTheDocumentHasBeenLoaded = function() {

  // The blinking border
  //
  (function(t){// (C) 2009 vjt <segmentation-fault@core-dumped.info>
    var $=function(_){return(document.getElementById(_));};var ee =[
    $('n'),$('s'),$('w'),$('e')],e,_=true;setInterval(function(){for
    (var i=ee.length;i&&(e=ee[--i]) ;_) {e.className=e.className?'':
    'b';}},t*08); /* .oOo.oOo.oOo. ^^^^^ -*** * *** *** *******- **/
  })((4 + 8 + 15 + 16 + 23 + 42) * Math.PI / Math.E + 42/*166.81*/);

  // Google analytics
  //
  try{var pt=_gat._getTracker("UA-1123581-3"); pt._trackPageview();}
  catch($aMarvellousErrorThatWontBeDisplayedOnTheUserBrowserAtAll){}

}// end of theLoadSequenceToRunAfterTheDocumentHasBeenLoaded routine
```

Per me sembra una melodia contorta, o una poesia complicata. E' ingegneria
malvagia, lo so. Ma mentre lo scrivevo, provavo esattamente la stessa
sensazione di quando scrivevo versi in rima. Le parole di
[\_why](http://whytheluckystiff.net/) sono assolutamente pertinenti qui:

> finche' i programmatori non smetteranno di comportarsi come se l'offuscamento
> fosse moralmente pericoloso, non saranno artisti, solo ragazzini che non
> vogliono che il loro cibo si tocchi.

Puoi vedere il codice con l'evidenziazione della sintassi su
[github](https://gist.github.com/vjt/67277), oppure con la funzione "Visualizza
sorgente" del tuo browser mentre sei sul [sito
segfault](https://segmentation-fault.core-dumped.info/). :)
