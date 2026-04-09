---
date: "2009-01-29T09:00:00Z"
title: "Il plugin jQuery ajax-upload-fu"
tags: [javascript, ruby, projects]
---

{{< retrospective year="2026" >}}
Questo plugin si basava su `$.browser` (rimosso in jQuery 1.9) e sul trucco dell'era Prototype di nascondere un file input sotto il cursore. I browser moderni supportano la File API, l'upload drag-and-drop, e `input.click()` funziona ovunque ormai -- niente più inseguimento del mouse.
{{< /retrospective >}}

Di recente ho scritto un [plug-in jQuery](http://gist.github.com/54441) che
permette l'upload di file via **AJAX** senza usare un pulsante file input
fisso. Raggiunge il suo scopo installando un handler OnMouseMove sugli elementi
selezionati e spostando il pulsante input sotto il cursore del mouse.

La citazione che ha ispirato questo codice e': "Se Maometto non va alla
montagna, la montagna va da Maometto", il contrario del [proverbio piu'
noto](http://en.wikipedia.org/wiki/If_the_mountain_won't_come_to_Muhammad) :).

*EDIT 2023: ATTENZIONE: questi link sono scaduti :-(*
E' stato estratto dalla codebase JavaScript dell'[applicazione Visita
CSA](http://www.visitacsa.it/), guarda il
[gist](http://gist.github.com/54441) per maggiori informazioni, e dai
un'occhiata [al codice dell'app live per un esempio di
utilizzo](http://www.visitacsa.it/javascripts/business-registration.js).

Ecco il codice sorgente:

```javascript
//  ~ JavaScript Kung-FU, with an excess chunky bacon dose! ~
// This plugin allows seamless ajax file uploads without having
// a fixed file input button. It achieves this by installing an
// OnMouseMove handler over the interested elements, and moving
// the input button under the cursor. <<If Muhammad won't go to
// the the mountain, the mountain will come to Muhammad.>> :-).
//
// This approach is needed on the majority of browser, except
// Safari, on which the coder is allowed to trigger a "click" 
// event onto an input type=file element. On other browsers,
// you can not, that's why the complicated mousemove approach
// was chosen.
//
// Either way, when the value of the input type=file changes,
// handlers are disabled, and a user-provided callback is then
// called (passed via the "upload" option). Handlers are then
// re-enabled again when the upload succeeds or fails.
//
// IE has additional problems, because, quite unexplicably,
// when submitting a form that causes a page load, the change
// event on the file input is triggered AGAIN, thus triggering
// a new file upload. To circumvent this, you can pass a "linked" 
// option, that contains the jQuery selector of the form, and
// whenever an input under this form is hovered, ajax upload
// handlers are temporarily cleared and thus the spurious form
// submission.
//
// The jquery Form plugin is a perfect companion of this one,
// because of its .ajaxSubmit method. Have a look at its home
// page: http://malsup.com/jquery/form/.
// 
// Have fun!
// - vjt@openssl.it
//
$.fn.ajaxFormUpload = function(options) {
  var positioning = { top: 0, left: 0,
    position: 'absolute', cursor: 'pointer', 'z-index': 2 };

  var form = $(options.form || '#ajax_upload');
  form.css(positioning)

  var input = form.find('input[type=file]');
  input.css($.extend(positioning, { width: '10px', opacity: 0, 'font-size':'0px' }));

  var hovering_element = null;

  var elements = $(this);

  var handler, event_;
  if ($.browser.safari) {
    event_ = 'click', handler = function() {
      hovering_element = $(this);
      input.click();
    };
  } else {
    event_ = 'mousemove', handler = function(event) {
      hovering_element = $(this);
      form.css({ left: event.pageX - 10, top: event.pageY - 5 });
    };
  }

  function enable()  { $(elements).bind(event_, handler);   }
  function disable() { $(elements).unbind(event_, handler); }

  input.change(function() {
    var element = hovering_element;
    if (!element) return;
    disable();

    options.upload(element, form);

    enable();
  });

  enable();

  if (options.linked) {
    $(document).ready(function() {
      $(options.linked).find('input').mouseover(function() { hovering_element = null; });
    });
  }
};
```

Puoi trovarlo su [github](http://gist.github.com/54441).
