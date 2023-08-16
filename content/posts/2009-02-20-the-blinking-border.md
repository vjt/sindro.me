---
date: 2009-02-20T04:00:00Z
title: The obfuscated blinking border
tags: [javascript, obfuscated]
categories: [development, all]
---

This is the obfuscated piece of Javascript code that implements the red border
and loads [Google Analytics](https://www.google.com/analytics) on the
[Segmentation Fault site](https://segmentation-fault.core-dumped.info/):

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

To me, it looks like a contrived melody, or complicated poetry. It’s evil
engineering, I know. But when I was writing it, I felt exactly the same I did
while writing verses with rhymes. [\_why](http://whytheluckystiff.net/)’s words
are absolutely pertinent here:

> until programmers stop acting like obfuscation is morally hazardous, they’re
> not artists, just kids who don’t want their food to touch.”.

You can view the code with syntax hilighting on
[github](https://gist.github.com/vjt/67277), or with the “View source” function
of your browser while you’re on the [segfault
site](https://segmentation-fault.core-dumped.info/). :)
