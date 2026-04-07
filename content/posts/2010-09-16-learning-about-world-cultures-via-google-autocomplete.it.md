---
date: 2010-09-16T20:00:00Z
title: Scoprire le culture del mondo tramite l'autocompletamento di Google
tags: [funny, networking]
---

Per curiosità, stavo guardando come un browser interagisce col backend di Google
Instant. Mentre osservavo gli scambi HTTP con Firebug, prima mi sono chiesto
perché codificano HTML e JS con sequenze di escape `\xYY`, poi perché le
stessissime funzioni JS vengono mandate avanti e indietro ad ogni richiesta, e
poi mi sono imbattuto nel servizio JSONp `google.com/s?q=QUERY`.

Dagli una query, e ti restituirà le frasi suggerite correlate che vengono usate
per costruire il menu sotto la barra di ricerca quando usi i suggerimenti e/o
Instant (non ho scavato troppo in tutti gli altri parametri).

Ad ogni modo, la cosa interessante è che, ovviamente, i suggerimenti sono
personalizzati per paese. Per mostrare le differenze in modo esplicito,
chiediamo al servizio la query più semplice possibile, `a`:

Per l'Italia otterrai:

```
$ curl http://www.google.it/s?q=a
window.google.ac.h(["a",[["ansa","","0"],
["alice","","1"],["alitalia","","2"],["alice mail","","3"],
["apple","","4"],["agenzia delle entrate","","5"],
["audi","","6"],["aci","","7"],["autoscout","","8"],
["atm","","9"]],"","","","","",{}])
```

hmm, togliamo il JSONp e i parametri:

```
$ curl -s http://www.google.it/s?q=a | ruby -rjson -ne 'puts JSON($_[19..-2])[1].map(&:first).join(", ")'            
ansa, alice, alitalia, alice mail, apple, agenzia delle entrate, audi, aci, autoscout, atm
```

Per gli USA otterrai:

```
amazon, aol, att, apple, american airlines, abc, ask.com, amtrak, addicting games, aim
```

Regno Unito:

```
argos, amazon, asda, asos, autotrader, aa route planner, aol, apple, amazon uk, aqa
```

Irlanda:

```
aer lingus, aib, argos, amazon.co.uk, argos.ie, asos, aa route planner, amazon, aldi, aib internet banking
```

Infine, perché ci sono stato di recente ed è stata un'esperienza profonda, Cuba:

```
asus, antonio maceo, amor, amigos, ain, antivirus, avira, alba, aduana, as
```

Sono sicuro che @nhaima sta sorridendo nel vedere queste parole, perché caspita,
laggiù cercano davvero un sacco software antivirus (avira è uno di quelli)
perché è un mondo senza Internet, quindi senza software libero: sei condannato
a usare roba Windows, e hai quello per cui paghi. Antonio Maceo è stato un eroe
della rivoluzione del XIX secolo, ed è nel cuore del popolo cubano. Amor,
Amigos! :-)

Ad ogni modo, sembra che query semplici come questa diano davvero uno spaccato
di ciò che una popolazione pensa e/o di cui ha bisogno, perché sono sicuramente
generate dai trend di ricerca, quindi sono le "parole più cercate". Sto
scoprendo l'acqua calda? Forse, ma è stato divertente riscoprirlo. Assicurati
solo di non bombardare il servizio /s con troppe richieste, perché saranno
comunque gestite dallo stesso cluster di macchine, e quindi verrai bannato presto
(io lo sono stato :-p).
