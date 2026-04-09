---
title: "data-confirm-modal: quando un utente ha fatto troppi danni"
date: 2013-07-02
tags: [ruby, rails, javascript, open-source]
description: "Un utente all'IFAD ha fatto troppi danni perche' il confirm() del browser non era abbastanza esplicito. Cosi' ho estratto un rimpiazzo con modal Bootstrap in una gem. 116 righe di JavaScript."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Questa piccola gem e' cresciuta fino a 268 stelle e 112 fork, con 32 contributori in 7 anni. Ha imparato [Bootstrap 3, poi 4 con auto-detection](https://github.com/ifad/data-confirm-modal/blob/v1.6.0/vendor/assets/javascripts/data-confirm-modal.js#L12-L33) (v1.6.0), ha ottenuto una [modalita' non-Rails](https://github.com/ifad/data-confirm-modal?tab=readme-ov-file#without-rails-with-data-attributes-example-b3-example-b4) con callback `dataConfirmModal.confirm()` (v1.2.0), un [pacchetto npm](https://www.npmjs.com/package/data-confirm-modal) che fa ancora 3.700 download a settimana (v1.6.2), e ha continuato a funzionare con ogni versione di Rails fino alla 6.0. Il concetto e' diventato talmente mainstream che ogni framework UI oggi ha il suo componente di conferma. Il [repo](https://github.com/ifad/data-confirm-modal) e' ancora online.
{{< /retrospective >}}

Un utente all'[IFAD](http://www.ifad.org/) ha fatto troppi danni la settimana scorsa.

Non intenzionalmente — ha semplicemente cliccato attraverso una catena di azioni distruttive, liquidando allegramente i dialog `confirm()` del browser senza leggerli. Perche' nessuno li legge. Sono brutti dialog di sistema grigi che si confondono con il flusso di lavoro. Clicca OK, clicca OK, clicca OK — e improvvisamente meta' dei dati e' sparita.

Cosi' l'ho sistemato. E poi ho estratto la fix in una gem, perche' questo problema non e' specifico della nostra applicazione. Oggi rilascio [data-confirm-modal](https://github.com/ifad/data-confirm-modal) — 116 righe di JavaScript che sostituiscono il `confirm()` integrato di Rails con un [modal Bootstrap](https://getbootstrap.com/2.3.2/javascript.html#modals).

<!--more-->

## La fix

Il concetto e' semplicissimo: qualsiasi link Rails con `data-confirm` gia' attiva una conferma del browser. La mia gem intercetta quell'evento e mostra un modal Bootstrap vero e proprio. Il titolo di default e' **"Are you ABSOLUTELY sure?"** — perche' a quanto pare dovevamo urlare di piu'.

Sostituzione drop-in. Zero modifiche al codice esistente. Aggiungi la gem, fai require del JS, e ogni `link_to "Delete", @thing, confirm: "This will destroy everything"` adesso mostra un modal vero con un titolo, un body, e due pulsanti chiaramente etichettati.

```ruby
# Gemfile
gem 'data-confirm-modal', github: 'ifad/data-confirm-modal'
```

```javascript
// application.js
//= require data-confirm-modal
```

Fatto.

## Il trucco del data-verify

Ecco la feature di cui vado piu' fiero. Sai come GitHub ti fa digitare il nome del repository prima di poterlo cancellare? Stessa idea:

```erb
<%= link_to "Delete project", project_path(@project),
  method: :delete,
  data: {
    confirm: "Questo eliminera' permanentemente il progetto e tutti i suoi dati.",
    verify: "DELETE",
    commit: "Ho capito, cancellalo"
  } %>
```

Il pulsante di conferma resta **disabilitato** finche' l'utente non digita esattamente "DELETE" nel campo di input. Niente piu' click da memoria muscolare attraverso azioni distruttive. Se vuoi distruggere qualcosa, devi dimostrare che lo vuoi davvero.

## Come funziona

La parte interessante e' l'[integrazione con Rails UJS](https://github.com/ifad/data-confirm-modal/blob/09eca28/vendor/assets/javascripts/data-confirm-modal.js#L88-L108). Quando un link `data-confirm` viene cliccato, Rails lancia un evento `confirm` e controlla `$.rails.confirm()` per decidere se procedere. Il mio codice fa un monkey-patch temporaneo di quella funzione:

```javascript
$(document).delegate('a[data-confirm]', 'confirm', function (e) {
  var element = $(this), modal = getModal(element);
  var confirmed = modal.data('confirmed');

  if (!confirmed && !modal.is(':visible')) {
    modal.modal('show');

    // Sostituisci temporaneamente la funzione confirm di Rails
    var confirm = $.rails.confirm;
    $.rails.confirm = function () { return modal.data('confirmed'); }
    modal.on('hide', function () { $.rails.confirm = confirm; });
  }

  return confirmed;
});
```

Mostra il modal, scambia la funzione confirm, ripristinala alla chiusura. Quando l'utente clicca il pulsante di conferma nel modal, `modal.data('confirmed')` diventa `true`, il click originale viene ri-attivato, e questa volta `$.rails.confirm` restituisce `true`. Pulito, minimale, nessuna dipendenza da jQuery UI.

## Il danno che ha scatenato tutto

L'incidente vero e proprio all'IFAD ha coinvolto un utente che gestiva dati di progetto nelle nostre applicazioni interne. Il dialog `confirm()` del browser era diventato invisibile per lui — solo un altro ostacolo da superare con un click. I dati che ha cancellato hanno richiesto uno sforzo significativo per essere recuperati.

La fix nella nostra applicazione e' stata immediata: sostituire `confirm()` con un modal che esige attenzione. L'estrazione in una gem ha richiesto tre commit e sei minuti. A volte il miglior open source nasce dai peggiori incidenti in produzione.

[Sorgente su GitHub](https://github.com/ifad/data-confirm-modal). [Provalo su JSFiddle](https://jsfiddle.net/zpu4u6mh/). PR benvenute — specialmente se anche voi siete stati scottati dal `confirm()`.
