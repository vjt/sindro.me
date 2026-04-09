---
title: "Rimuovere un link trigger di lightwindow dopo una chiamata AJAX"
date: "2008-05-21T17:00:00Z"
tags: [javascript, rails, ruby]
hideVintage: true
---

Ecco, questo è il risultato di 2 giorni di testate contro il muro con lightwindow:

`Index: public/javascripts/lightwindow.js, line 444`

```javascript
  _removeLink : function(removed) {
    // remove it from the links array
    //
    this.links = this.links.reject(function(link) {
      if (link == removed.href)
        return true;
    });
    // remove it from the gallery links array
    //
    if (gallery = this._getGalleryInfo(removed.rel)) {
      klass = gallery[0];
      name = gallery[1];
      if (this.galleries[klass] && this.galleries[klass][name]) {
        this.galleries[klass][name] = 
          this.galleries[klass][name].reject(function(link) {
            if (link == removed.href)
              return true;
          });
      }
    }
  },
```

Chiama questa funzione dal tuo template .rjs, qualcosa tipo:

```ruby
page << "myLightWindow._removeLink($('element').down('a.lightwindow'));"
```

Più dettagli a seguire, quando questo lavoro sarà completo ;).
