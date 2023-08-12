---
title: "Remove a lightwindow trigger link after an AJAX call"
date: "2008-05-21T17:00:00Z"
tags: [javascript, lightwindow, rails, ruby]
---

Well, this is the result of 2 days of head-banging with lightwindow:

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

Call this function from your .rjs template, something like this:

```ruby
page << "myLightWindow._removeLink($('element').down('a.lightwindow'));"
```

More details to follow, when this work will be complete ;).
