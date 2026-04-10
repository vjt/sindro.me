---
date: 2010-08-05T16:00:00Z
title: Gli spin-off di Panmind presentati al Ruby Social Club Milano
tags: [open-source, projects, rails, ruby, events]
---

{{< retrospective year="2026" >}}
Panmind non esiste più. Le repo GitHub esistono ancora come reperti storici, ma l'ecosistema di plugin Rails descritto qui è stato sostituito da gem e engine da un pezzo.
{{< /retrospective >}}

Il 22 luglio 2010, [Mikamai](http://mikamai.com/) ha ospitato un [Ruby Social
Club a Milano](http://blog.mikamai.com/2010/07/la-notte-del-ruby-social-club/),
dove circa 50 persone hanno assistito a cinque talk su Ruby, sviluppo web e
startup. Sono stato contento di essere uno degli speaker, e ho presentato un
insieme di plugin Rails che [noi](http://mind2mind.is/) abbiamo estratto dal
nostro ultimo (e più grande) progetto:
[Panmind](http://panmind.org/) (leggi di più nella [pagina
about](http://panmind.org/about)), rilasciati come Open Source su
[GitHub](http://github.com/Panmind).

La presentazione è divisa in due parti: la prima spiega **perché** dovresti
seguire il sano principio di ingegneria del software di scrivere codice modulare
e a responsabilità separate, e poi **come** potresti (e dovresti) estrarlo dalla
tua applicazione Rails disaccoppiando la configurazione e preparando il rilascio
Open Source, scrivendo documentazione **E** presentando a un evento Ruby così,
**si spera, qualcun altro scriverà i test unitari! :-)**

Abbiamo rilasciato un plugin [SSL helper](http://github.com/panmind/ssl_helper)
che implementa dei filtri (come `ssl_requirement` di Rails) ma anche degli
helper per le named route: basta con `<%= url_for :protocol => 'https' %>`!
Avrai qualcosa come `plain_root_url` e `ssl_login_url` — come se fossero
integrati nel framework.

Poi, un plugin semplicissimo per [Google
Analytics](http://github.com/panmind/bigbro), con supporto `<noscript>`, un
paio di helper per i test e un
[embrione](http://github.com/Panmind/bigbro/blob/master/js/jquery.analytics.js)
di framework JS per Analytics — si spera che evolva in un plugin jQuery
completo. Poi, un'interfaccia
[ReCaptcha](http://github.com/Panmind/recaptcha), con supporto alla validazione
AJAX, e infine un'interfaccia [Zendesk](http://github.com/Panmind/zendesk)
per Rails.

Abbiamo rilasciato anche altro codice sull'[account GitHub di
Panmind](http://github.com/Panmind), incluso il bel [AJAX Navigation
Framework](http://github.com/Panmind/jquery-ajax-nav) che implementa tutto il
codice boilerplate per la navigazione AJAX ultra-veloce dei
[contenuti](http://panmind.org/search) e dei
[progetti](http://panmind.org/tour/collaborate) di Panmind.

La presentazione segue: puoi scaricarla in PDF (nessun [exploit, lo
giuro!](/posts/2010-08-04-on-the-iphone-pdf-and-kernel-exploit)) [da questo
link](/posts/2010-08-05-panmind-at-ruby-social-club/Panmind_at_Ruby_Social_Club_Milano.pdf)
Ultime parole: dai un'occhiata al [post sul blog di Mikamai sul Ruby Social
Club](https://blog.mikamai.com/post/129408154293/la-notte-del-ruby-social-club)
per leggere le altre presentazioni (spero di aggiornare questo post con dei
riassunti quando avrò tempo :-)) e [salutaci su
Twitter](http://twitter.com/panmind) o [su GitHub](http://github.com/Panmind)
se ti interessa contribuire ai nostri progetti open source o se [vuoi lavorare
con noi](http://panmind.org/jobs).

<object data="/posts/2010-08-05-panmind-at-ruby-social-club/Panmind_at_Ruby_Social_Club_Milano.pdf" type="application/pdf" width="100%" height="600">
  <p><a href="/posts/2010-08-05-panmind-at-ruby-social-club/Panmind_at_Ruby_Social_Club_Milano.pdf">Scarica la presentazione (PDF)</a></p>
</object>
