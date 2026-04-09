---
date: "2009-02-10T18:08:34Z"
title: "Come creare un mirror statico del sito opensource.org"
tags: [bash, open-source]
hideVintage: true
---

Attualmente mantengo il [mirror italiano](http://opensource.antifork.org/) del
sito web della [Open Source Initiative](http://opensource.org/), e oggi mi sono
reso conto che lo script che avevo scritto qualche mese fa non stava facendo
bene il suo lavoro... perche' i file CSS non venivano scaricati affatto,
causando un rendering del sito piuttosto sgradevole.

Per fare il mirror di opensource.org sto usando il caro vecchio [GNU
Wget](http://www.gnu.org/software/wget/) con -r --mirror e compagnia bella.
Mentre il buon vecchio **wget** scarica tutti i prerequisiti di ogni pagina
definiti nel sorgente HTML, non supporta le regole CSS @import e non scarica le
immagini referenziate nei CSS con le regole url().

Comunque, niente che non si possa risolvere con un po' di regex-fu: ecco
perche' [condivido lo script](http://gist.github.com/61474) che sto usando
attualmente per fare il mirror del sito opensource.org, sperando che generi un
nuovo mirror o qualche spunto su come fare meglio questo lavoro :).

Lo script: [`update_opensource_mirror.sh`](http://gist.github.com/61474)

Buon divertimento! :)
