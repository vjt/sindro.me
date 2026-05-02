---
title: "GRcalc: Calcolatrice Grafica in Turbo Pascal, 2002"
date: 2026-04-15
tags: [pascal, graphics, parser, university, retrospective, archaeology, ai-generated, open-source]
description: "L'esame di programmazione chiedeva struct di libri salvati in un file binario. Io ho costruito una calcolatrice grafica con parser di espressioni, valutatore ricorsivo e rendering in tempo reale. La professoressa mi ha dato 25/30 perché non capiva il codice. Ho lasciato l'università."
image: cover.jpg
featuredImage: cover.jpg
---

Nel febbraio 2002 avevo 20 anni e stavo dando l'esame di Programmazione. La consegna era: una struttura dati che rappresenta dei libri, salvati come record binari in un file. Scrivere un programma per elencarli, aggiungerli e cancellarli.

Non feci quello. Costruii una calcolatrice grafica.

<!--more-->

## Cosa chiedeva la consegna

La professoressa voleva un `record` di tipo Libro — titolo, autore, anno, prezzo — scritto sequenzialmente in un file binario con `BlockWrite`. Un menu: elenca tutti i libri, aggiungi un libro, cancella per indice. Magari cerca. Il tipo di programma dove la parte più difficile è ricordarsi che gli offset dei file in Turbo Pascal partono da zero.

Lo trovai noioso.

## Cosa costruii invece

[GRcalc](https://github.com/vjt/grcalc) è un plotter di funzioni. Scrivi un'espressione matematica — `sin(cos(x))`, `ln(cos(x*x)) + atan(x)`, qualsiasi composizione di funzioni trigonometriche, logaritmiche e operazioni aritmetiche — e la disegna in tempo reale su un piano cartesiano con assi etichettati e controllo dello zoom.

Girava in modalità grafica BGI a 640×480, con driver per EGA/VGA, CGA e Hercules [linkati direttamente nell'eseguibile](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L28-L35) in modo da non dover distribuire nient'altro oltre al `.EXE`.

Ecco `y = cos(e(x))` a 60× di zoom:

![y = cos(e(x)) a 60x di zoom — curva gialla su sfondo nero con assi cartesiani e barra di progresso colorata](cos.jpg)

E `y = ln(cos(x*x)) + atan(x)` a 90× di zoom — una funzione composta più complessa con discontinuità dove `cos(x²)` diventa negativo:

![y = ln(cos(x*x)) + atan(x) a 90x di zoom — lobi multipli con buchi dove la funzione non è definita](ln.jpg)

La barra di progresso in basso era colorata: blu dove la funzione è definita, rossa dove è definita ma fuori schermo, grigia dove non è definita (come `ln` di un numero negativo).

## Come funziona

Il programma ha tre strati: un parser, un valutatore e un renderer. Il [sorgente completo](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS) è ~1000 righe di Turbo Pascal in un singolo file.

### Il parser

Una [macchina a stati](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L315-L614) che percorre la stringa di input carattere per carattere e costruisce una lista collegata di termini tipizzati. Ogni termine è un numero, una variabile (`x`), un operatore, un nome di funzione o una parentesi.

![Diagramma di flusso del parser — mostra le transizioni tra gli stati IDLE, READNUMBER, READFUNCTION, READOPERATOR, READVARIABLE, BRACKETOPEN, BRACKETCLOSE](parser_flux.gif)

Ogni transizione di stato valida la sintassi — non puoi avere due operatori di fila, una funzione deve essere seguita da un'espressione, le parentesi devono essere bilanciate. Se qualcosa fallisce, il parser imposta `calc_errno` ed esce.

Il lookup delle funzioni usa una dispatch table — un array di record che mappa nomi a [puntatori a funzione](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L167-L181):

```pascal
calc_func_table : array [1..CALC_FUNX] of record
    func_name : string[5];
    func_handler : calc_func_handler_t;
end = (
    (func_name : 'sin'; func_handler : calc_sin),
    (func_name : 'cos'; func_handler : calc_cos),
    ...
);
```

Stesso schema per gli operatori. Aggiungere una nuova funzione significava una riga nella tabella e una procedura wrapper.

### Il valutatore

Il cuore del programma è [`get_y_value`](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L630-L728) — una funzione che prende un valore `x` e percorre la lista collegata valutando l'espressione.

Il trucco è la ricorsione mutua. `get_y_value` gestisce il ciclo di valutazione principale (numeri, operatori, variabili). Quando incontra un termine funzione, chiama `evaluate_func`, che prende il puntatore a funzione, avanza al termine successivo e ricorre: se il termine successivo è un'altra funzione, chiama se stessa; se è una parentesi, richiama `get_y_value` per la sotto-espressione.

È così che `sin cos tan x` funzionava — `evaluate_func` concatenava tre chiamate in profondità, ognuna che avvolgeva la successiva, finché non trovava la variabile e si srotolava: `sin(cos(tan(x)))`.

![Diagramma di flusso del programma principale — INIT → leggi dati → analizza funzione → imposta grafica → disegna grafico → attendi tasto → torna in CRT](main_flux.gif)

### Il renderer

Per ogni colonna di pixel sullo schermo, il renderer chiamava `get_y_value` con la `x` corrispondente (divisa per il fattore di zoom), scalava il risultato e piazzava un pixel giallo. Se la funzione non era definita in quel punto — `ln` di un numero negativo, divisione per zero — `calc_errno` lo segnalava e la barra di progresso diventava grigia. Se il valore superava il viewport, la barra diventava rossa.

Gli [assi cartesiani](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L770-L836) erano disegnati con tacche e etichette che si adattavano al fattore di zoom. La barra superiore mostrava la funzione e il livello di zoom, quella inferiore la risoluzione.

### Gestione degli errori

Ero innamorato della [`perror(3)`](https://man7.org/linux/man-pages/man3/perror.3.html) del C in quel periodo della mia vita, quindi costruii una [versione in miniatura](https://github.com/vjt/grcalc/blob/master/src/GRCALC.PAS#L96-L115): un `calc_errno` globale, un array di stringhe di errore e una procedura `calc_perror` che stampava il messaggio. Divisione per zero, dominio non definito, errori di sintassi, fallimento dell'inizializzazione grafica — passavano tutti per la stessa strada.

## Cosa c'è di oggettivamente sbagliato

Scrissi 10 pagine di [documentazione](/posts/2026-04-15-grcalc-graphical-calculator-pascal/grcalc-doc.pdf) con diagrammi di flusso disegnati in CorelDRAW, più 26 pagine di codice sorgente stampato — bisognava portare tutto in forma cartacea. Compilai un eseguibile da 52KB che rilevava la scheda video e plottava funzioni matematiche arbitrarie in tempo reale. Ma rileggendo il codice oggi, ventiquattro anni dopo, ci sono problemi reali:

**Nessuna precedenza degli operatori.** `2 + 3 * x` si valuta da sinistra a destra come `(2 + 3) * x`. Il parser non costruisce un AST con livelli di precedenza — costruisce una lista collegata piatta. Servono le parentesi per la matematica corretta: `2 + (3 * x)`. Lo sapevo — ero in ritardo e le parentesi funzionavano.

**Solo interi come costanti.** Non puoi scrivere `3.14 * x` perché il parser gestisce solo cifre. Nessun supporto per il punto decimale. Vuoi π? Usa `atan(1) * 4 * x`. Oppure no.

**Tutto è stato globale.** `calc_errno`, `calc_term`, `calc_zoom` — tutte variabili globali. Il valutatore muta il suo argomento puntatore come side effect per tracciare la posizione nella lista. Funziona, ma è il tipo di codice dove aggiungere una seconda feature rompe la prima.

**Il record `calc_term_t` spreca memoria.** Ogni nodo nella lista porta campi per un valore numerico, un puntatore a funzione E un puntatore a operatore — anche se ogni nodo è solo uno di quei tipi. Ne discuto addirittura nei commenti, considero l'uso di oggetti con ereditarietà, e decido che renderebbe il programma "troppo complesso." A 20 anni, avevo ragione per i motivi sbagliati.

### Il bug alla riga 655 {#il-bug-alla-riga-655}

In `evaluate_func`, il caso NUMBER legge `p^.term_next^.term_value` — cioè il valore del nodo *successivo*, non di quello corrente. Dovrebbe essere `p^.term_value`. Non scatta mai in pratica perché dovresti scrivere qualcosa come `sin 5` (una funzione applicata a un letterale numerico senza parentesi), e nessuno lo fa — scrivi `sin(5)` o `sin x`. Un bug vero, nascosto dalla convenzione. Non lo beccai nel 2002. Lo ha trovato [Claude](/it/tags/ai-generated/) nel 2026.

**`delay(100)` tra un pixel e l'altro.** Ogni pixel ha una pausa di 100ms per guardare la curva che si disegna. Secondi di animazione forzata per ogni grafico, senza modo di saltarla.

## L'esame

Portai tutto questo all'esame il 20 febbraio 2002. Dieci pagine di documentazione e ventisei pagine di codice sorgente stampato, diagrammi di flusso, un eseguibile funzionante. La professoressa lo guardò. Si aspettava `type TLibro = record`. Si aspettava `BlockWrite` e `BlockRead` e un menu testuale che dice `1) Aggiungi libro 2) Cerca libro 3) Esci`.

Ricevette un parser a macchina a stati, dispatch table con puntatori a funzione, valutazione ricorsiva con ricorsione mutua e rendering grafico in tempo reale.

Disse: "Non capisco niente di questo codice. Non so come giudicarlo. Qual è il tuo voto precedente?"

"24 su 30."

"Ti posso dare 25."

Presi il 25. Qualsiasi voto andava bene per il valore intrinseco del lavoro. Sapevo cosa avevo costruito.

## Cosa successe dopo

Lasciai l'università dopo quello. Non in modo drammatico — semplicemente smisi di andarci. Il divario tra quello che imparavo per conto mio (parser, grafica, networking, [server IRC](/it/tags/irc/)) e quello che mi insegnavano (libri in file binari) era troppo ampio. Tornai qualche anno dopo e me ne andai di nuovo, ma quella è un'altra storia.

Il codice è rimasto su [barnaba.openssl.it](https://barnaba.openssl.it) per i ventiquattro anni successivi — una pagina statica che misi online da studente e non ho mai tolto. Oggi lo metto su [GitHub](https://github.com/vjt/grcalc), dove gli spetta.

GRcalc non è buon software. Ha bug, nessuna precedenza degli operatori, delay hardcoded. Ma è un artefatto onesto di cosa un ventenne che leggeva troppe man page e non abbastanza libri di testo poteva costruire quando decideva che la consegna era noiosa.

25/30.
