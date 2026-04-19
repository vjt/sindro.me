---
title: "De-CAF: la dichiarazione sugli investimenti esteri, senza commercialista"
date: 2026-04-18
tags: [python, tasse, italia, investimenti-esteri, open-source, finanza]
description: "Perché ho scritto decaf — un tool Python che prende i file di Interactive Brokers e Charles Schwab e sputa fuori tutto quello che serve per compilare il Modello Redditi PF: Quadro RW, RT, RL. Con tre fixture di test intitolate a tre santi patroni dell'audio-cult italiano."
image: cover.png
featuredImage: cover.png
draft: true
---

Se sei residente fiscale in Italia e hai investimenti all'estero, la scena la conosci. Ogni primavera prepari un pacco di PDF ed export dei conti del broker, lo mandi al [commercialista](https://it.wikipedia.org/wiki/Commercialista), e un paio di settimane dopo ti torna indietro un PDF che costa tra i trecento e gli ottocento euro e che non hai modo di verificare perché non mastichi il [TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917) fluentemente.

Un progetto come decaf, fino a poco tempo fa, non sarebbe stato un progetto serale: leggersi TUIR, circolari dell'Agenzia delle Entrate e risposte agli interpelli non è il mio mestiere, e farlo con la precisione che serve per metterci dentro una dichiarazione richiede mesi. Con un'[Intelligenza Artificiale](https://www.anthropic.com/claude/opus) che digerisce la normativa insieme a me e non mi lascia prendere scorciatoie è diventato fattibile. Il risultato è [`decaf-tax`](https://pypi.org/project/decaf-tax/) su PyPI e [github.com/vjt/decaf](https://github.com/vjt/decaf) su GitHub, licenza MIT. Con una batteria di test costruita apposta per non farmi sbagliare i numeri: casi sintetici con i risultati attesi salvati accanto, più tre anni della mia dichiarazione reale — quella validata dal commercialista — usata come metro di confronto continuo. I dettagli tecnici li srotolo più sotto.

<!--more-->

## Cosa fa, in concreto

`decaf` sono due comandi. `decaf load` raccoglie i dati da ciascuno dei tuoi broker e li normalizza in un formato unico, indipendente dal broker: operazioni, dividendi, interessi, bonifici, conversioni valuta, vesting di RSU — tutto depositato in un database locale come eventi su un'unica linea temporale. È questo il pezzo che rende il resto trattabile: una volta che i flussi sono allineati su una sola timeline, la dichiarazione diventa un problema di aggregazione, non di correlazione tra fogli Excel provenienti da posti diversi — comprese le cose che vanno calcolate a cavallo tra broker, come le plusvalenze valutarie. `decaf report --year 2025` rilegge dal database, converte USD in EUR al cambio BCE della data giusta (regolamento per il monitoraggio, operazione per le plusvalenze — sono due date diverse), e produce un report.

Il report esce in più formati: tabelle colorate sulla riga di comando, [un file Excel](/posts/2026-04-18-decaf-tax/decaf_2025.xlsx) con un foglio per quadro, [un PDF con il prospetto](/posts/2026-04-18-decaf-tax/decaf_2025.pdf), e un file testuale con il report completo. Quest'ultimo per me è quello che conta davvero: è il riferimento che uso per essere sicuro che, quando modifico il codice, i numeri non cambino da soli — è così che mi accorgo subito se ho rotto la logica di calcolo da qualche parte.

Quanto al contenuto, decaf produce quattro cose:

- **Quadro RW** — monitoraggio attività estere più [IVAFE](https://www.agenziaentrate.gov.it/portale/schede/pagamenti/imposta-valore-att-estero-ivafe/base-imponibile-e-aliquote-scheda-ivafe): 0.2% annuo sul valore di mercato dei titoli e sui saldi cash del broker, pro-rata per giorni di detenzione. Decaf non gestisce conti correnti bancari esteri (Revolut, Wise, N26 e simili): per quelli vale il fisso da €34.20 annui, e te li dichiari a mano. Codice in [`quadro_rw.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rw.py).
- **Quadro RT** — plusvalenze al 26% sui titoli. Decaf si fida della determinazione del costo fatta dal broker: il broker tiene traccia di ogni lotto (data di acquisto, prezzo, quantità) e su ogni vendita registra quale lotto hai ceduto e il suo costo effettivo — lo scegli tu tramite Tax Optimizer su Schwab o matching method nelle settings IBKR. È esattamente il metodo che la [circolare AdE 165/E del 24/06/1998, §2.3.2](https://def.finanze.it/DocTribFrontend/getPrassiDetail.do?id=%7B223C9DB9-C064-4DDA-84B2-819A66817892%7D) prescrive per le partecipazioni: base imponibile = *corrispettivo − costo effettivo d'acquisto del lotto ceduto*. Nessuna presunzione FIFO/LIFO, nessun ricalcolo. Sul cambio invece decaf applica alla lettera l'[art. 9 c. 2 TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art9): ogni lotto ceduto viene convertito in EUR con **due** tassi BCE distinti — il costo al cambio della *data di acquisto del lotto*, il corrispettivo al cambio della *data di regolamento della vendita* — e la plusvalenza è la differenza fra i due. Sui lotti pluriennali, usare un singolo tasso (la semplificazione di prassi) può spostare la base imponibile di diversi punti percentuali rispetto al dettato normativo. Codice in [`quadro_rt.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rt.py).
- **Quadro RL** — interessi e dividendi esteri lordi, abbinati alla ritenuta effettivamente applicata alla fonte. È qui che riconcili il 26% italiano con qualunque ritenuta abbia trattenuto il paese estero. Codice in [`quadro_rl.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rl.py).
- **Soglia valutaria** — l'analisi ex [art. 67(1)(c-ter) TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67). Se stai sopra €51.645,69 in valuta estera per sette o più giorni lavorativi continui, il tuo saldo in USD diventa un'attività finanziaria a tutti gli effetti e le sue plusvalenze *valutarie* diventano imponibili. Il che ci porta alla parte rognosa.

## L'unica cosa che i broker non mi davano

I broker ti danno la plusvalenza sui titoli già pronta. Sulla valuta no, perché per loro i dollari sono solo la valuta di regolamento del conto — non c'è nessun "evento realizzativo" quando torni all'euro. Dal punto di vista dell'AdE invece ogni conversione EUR→USD è un acquisto di lotti USD, ogni conversione USD→EUR (o bonifico in uscita) è una cessione, e se hai sforato la soglia paghi il 26% sulla plusvalenza in euro. Come la calcoli lo dicono l'[art. 67 c. 1-bis TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67) ("si considerano cedute per prime le valute acquisite in data più recente" — metodo LIFO, *last-in first-out*) e la [risposta AdE 204/2023](https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+204_2023.pdf/5189c15d-4fe7-f043-606b-2843bc00df74) ("analiticamente e distintamente, per ciascun conto" — niente travaso fra conti broker diversi, ciascuno ha la sua coda di lotti a sé).

È qui che vive [`forex_gains.py`](https://github.com/vjt/decaf/blob/master/src/decaf/forex_gains.py). Scorre gli eventi del broker in ordine cronologico e mantiene un tracker LIFO separato per ciascun conto: i dollari acquisiti da vendite di titoli, dividendi e interessi sul conto sono acquisti di quel conto; quelli ceduti via EUR.USD e bonifici dallo stesso conto sono vendite di quel conto, abbinati prima al lotto più recente. Un dettaglio che volevo coprire: un giroconto in dollari fra due conti broker diversi dello stesso soggetto non integra cessione ex [risoluzione AdE 60/E del 09/12/2024](https://www.agenziaentrate.gov.it/portale/documents/20143/6581869/Ris.+n.+60+del+9+dicembre+2024+plusvalenze+art.+67+TUIR.pdf/3d6dd94c-326d-7e7c-f383-190bf5b713a5), e infatti decaf dalla v0.3.0 accoppia automaticamente i bonifici cross-broker (stessa valuta, stesso importo entro 0,01 USD, data di regolamento entro ±3 giorni lavorativi, conti distinti dello stesso soggetto): i lotti USD migrano dalla coda del conto di origine a quella del conto di destinazione preservando data di acquisto e cambio BCE originali, senza plusvalenza artificiosa sul giroconto. La plusvalenza realizzata su ogni vera cessione è

```
gain_eur = usd_amount × (1/ecb_rate_disposal − 1/ecb_rate_acquisition)
```

— la formula vive in [`forex_gains.py#L11`](https://github.com/vjt/decaf/blob/master/src/decaf/forex_gains.py#L11). L'inversione dei tassi conta: la BCE pubblica il cambio come USD per 1 EUR, e a noi invece serve l'euro per ogni dollaro disposto. Se la soglia non è stata superata nell'anno il tracker gira ma [`quadro_rt.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rt.py) lo ignora. Se è stata superata, il suo output diventa righe RT affianco alle plusvalenze titoli.

Su questo file ho speso più tempo che sugli altri nove moduli quadro messi insieme. Non c'è scorciatoia: non ti puoi fidare del P/L valutario del broker (lo calcolano contro la valuta base del conto con tassi interni, che non sono i BCE), e non lo puoi saltare, perché l'AdE controlla.

## Broker supportati

Due, per ora, perché sono i due che uso:

- **Interactive Brokers** (entity irlandese) — [Flex Query](https://www.ibkrguides.com/orgportal/performanceandstatements/flex.htm) XML, scaricato a mano dal portale IBKR, oppure tirato giù in automatico se sai generare un token Flex Query e infilarlo nel `.env`. Pulito, strutturato, idempotente. Se una Flex Query non l'hai mai configurata c'è una guida con dodici screenshot in [`doc/QUERY_SETUP.md`](https://github.com/vjt/decaf/blob/master/doc/QUERY_SETUP.md), perché il portale IBKR è il portale IBKR. Parser in [`parse.py`](https://github.com/vjt/decaf/blob/master/src/decaf/parse.py).

- **Charles Schwab** (conti EAC — *Equity Award Center*, quelli che Schwab assegna ai dipendenti che ricevono RSU o stock option dal datore di lavoro) — tre file, scaricati a mano da `schwab.com`: un export JSON delle transazioni, il PDF del Year-End Summary per le plusvalenze per lotto, e il PDF dell'Annual Withholding Statement per i fair-market-value ai vest.

  Perché tre file e non un'API? Perché mi sono registrato al portale developer di Schwab, ho aspettato l'approvazione dell'account, ho registrato un'app, ho fatto girare l'OAuth2 — tutto liscio — e poi gli endpoint sono tornati vuoti. La [Trader API non supporta i conti EAC](https://github.com/vjt/decaf/blob/master/doc/INTERNALS.md#schwab-integration), e le altre API di Schwab non espongono le informazioni fiscali che servono (cost basis per lotto, FMV ai vest per giurisdizione): quelle vivono solo nei PDF annuali. Quindi, parser PDF. Il lavoro pesante lo fa `poppler-utils`. Orchestratore in [`schwab_parse.py`](https://github.com/vjt/decaf/blob/master/src/decaf/schwab_parse.py).

Fineco, Directa e Degiro non ancora. Degiro è il candidato più ovvio: è regime dichiarativo, RW e RT te li fai tu. Fineco e Directa di default fanno da sostituto d'imposta — le tasse te le calcolano loro, l'RW è pure esonerato — quindi decaf ti serve solo se hai scelto tu il regime dichiarativo. Aggiungere un broker significa un nuovo modulo parser che costruisca gli stessi `ParsedData` interni; al resto della pipeline non importa da dove arrivano gli eventi. PR benvenute.

## Il trittico

L'aritmetica fiscale è un dominio dove sbagliare un numero vuol dire scrivere la cosa sbagliata sul Modello Redditi. Quindi decaf ha un'infrastruttura di test costruita per non farmi fidare della memoria muscolare.

Il punto di partenza è stata la mia dichiarazione reale. Per tre anni di fila (2022, 2023, 2024) ho riconciliato i numeri di decaf con quelli firmati dal commercialista, riga per riga, e quelle tre dichiarazioni — che restano sui miei dischi, non sono pubbliche — sono il primo smoke test: le rieseguo a ogni modifica del codice, e uno scostamento non spiegabile fa tornare la modifica in discussione. La parola "coincidere" però va qualificata: fino alla v0.2.0 i numeri coincidevano al centesimo, ma la v0.3.1 ha implementato la conversione in EUR per-lotto prescritta dall'art. 9 c. 2 TUIR (costo al cambio BCE della data di acquisto, corrispettivo al cambio BCE della data di regolamento), e questo sposta la plusvalenza di 2-3% rispetto alla semplificazione a un solo cambio che il commercialista — come quasi tutti — aveva usato. Il delta d'imposta sui miei scenari è nell'ordine dei cinquanta-sessanta euro all'anno: piccolo ma a favore del contribuente, e soprattutto allineato al dettato normativo. Il fatto che decaf oggi diverga dal commercialista in modo *documentato e documentabile* — citando lo stesso articolo del TUIR — mi sembra più una validazione che un problema.

Da quella base validata ho ricavato tre [casi sintetici](https://github.com/vjt/decaf/tree/master/examples): dati finti, costruiti per esercitare le stesse logiche senza esporre i miei numeri reali. Vivono assieme al codice del programma, e ognuno porta con sé il **report atteso** accanto: quando modifico qualcosa e rilancio decaf, il confronto tra il nuovo output e il report atteso è immediato, e qualunque differenza salta subito all'occhio. Oltre a questo, tre controlli automatici girano a ogni esecuzione dei test: il report coincide esattamente con quello atteso, il numero di righe di ogni quadro resta stabile, e per ogni riga del Quadro RL vale `netto = lordo − ritenuta`. Codice in [`tests/test_e2e.py`](https://github.com/vjt/decaf/blob/master/tests/test_e2e.py).

Vuoi provarlo sui tuoi numeri? In [`doc/BACKTEST.md`](https://github.com/vjt/decaf/blob/master/doc/BACKTEST.md) spiego come dare in pasto a decaf la tua dichiarazione passata e confrontare l'output con quello che ti ha tornato il commercialista — *try before you buy*, soddisfatto o rimborsato.

I tre casi sintetici pubblici coprono tre livelli di complessità crescente:

- **[`magnotta/`](https://github.com/vjt/decaf/tree/master/examples/magnotta)** — il caso base. Solo IBKR, un anno, IVAFE pro-rata su una posizione parziale, un trade in perdita da 480.000 vecchie lire, un dividendo con ritenuta US.
- **[`mosconi/`](https://github.com/vjt/decaf/tree/master/examples/mosconi)** — IBKR più Schwab, due anni, stesso ticker su entrambi, vendita parziale su più lotti, vesting RSU.
- **[`mascetti/`](https://github.com/vjt/decaf/tree/master/examples/mascetti)** — lo stress test. Due anni, soglia valutaria superata entrambi, LIFO per conto su più lotti USD, RSU che vestano su più anni, quattro ritenute diverse (US 30%, UK 0%, DE 26.375%, IT 26%).

I nomi non sono casuali. Sono, in ordine:

- [Mario Magnotta](https://it.wikipedia.org/wiki/Mario_Magnotta), il bidello aquilano i cui nastri delle beffe telefoniche del 1987 lo hanno consacrato santo patrono degli italiani rovinati da carte che non hanno mai firmato.
- [Germano Mosconi](https://it.wikipedia.org/wiki/Germano_Mosconi), il giornalista veronese le cui bestemmie off-air hanno insegnato a un'intera generazione come affrontare un gobbo che non funziona.
- [Il Conte Raffaello Mascetti](https://it.wikipedia.org/wiki/Amici_miei) di *Amici Miei* — l'inventore della [supercazzola](https://youtu.be/9-1T3sTk1Ng), santo patrono delle cortine verbali spiegate contro autorità incomprensibili.

Tre figure che, ciascuna a suo modo, hanno fissato che cosa si prova davanti alla burocrazia italiana: Mascetti ci parla sopra, Mosconi ci bestemmia sopra, Magnotta ne viene distrutto. Raramente ho avuto tanta soddisfazione nell'intitolare dei test.

## Disclaimer che non è uno scherzo

`decaf` **interpreta la legge**. L'aritmetica è la parte facile; l'interpretazione — quale transazione entra in quale quadro, quale data usare, quale cambio, quale soglia — l'abbiamo fatta io e [Claude Opus 4.7](https://www.anthropic.com/claude/opus), leggendo TUIR, circolari dell'Agenzia delle Entrate, risposte agli interpelli. I riferimenti normativi completi, con link alla Gazzetta Ufficiale, sono in [`doc/NORMATIVA.md`](https://github.com/vjt/decaf/blob/master/doc/NORMATIVA.md), e la guida operativa alla compilazione in [`doc/GUIDA_FISCALE.md`](https://github.com/vjt/decaf/blob/master/doc/GUIDA_FISCALE.md) — entrambi raccolti anche nel [manuale PDF](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.3.2/doc/decaf_manual.pdf) se preferisci scaricare tutto in un file solo. L'ho back-testata sulla mia dichiarazione dal 2022 al 2024, riconciliando ogni numero con quelli del commercialista.

Ma: i miei scenari non sono complicatissimi. Il software gestisce casi anche più complessi di quelli che ho potuto verificare con la mia dichiarazione reale — RSU multi-anno su più broker, soglia valutaria, LIFO valutario per conto su decine di lotti, quattro giurisdizioni di ritenuta — e quei casi hanno i loro casi sintetici dedicati, ma non un backtest contro una dichiarazione firmata. Un caveat specifico vale la pena citarlo: per attività detenute in Stati a regime fiscale privilegiato (i cosiddetti *black-list*) l'aliquota IVAFE sale allo 0.4% dal 2024, e decaf al momento non lo rileva automaticamente — se hai esposizione black-list, rettifichi a mano. I risultati possono variare: se la legge cambia (e cambia, ogni anno), o se hai un caso anomalo che non rientra nei casi sintetici, **usalo a tuo rischio e pericolo**. Per gli anni strani vai comunque dal commercialista. Ci vado anch'io.

Il senso di scriverlo, e di liberarne il codice, è che l'aritmetica dovrebbe essere commodity. Non dovresti dover pagare un professionista ogni primavera solo per moltiplicare i dividendi per il cambio BCE alla data di regolamento. Quei soldi tienili per i casi in cui a contare è il *giudizio* del professionista.

## Dove trovarlo

- **PyPI**: [`pip install --user decaf-tax`](https://pypi.org/project/decaf-tax/) — il comando è `decaf`
- **Sorgenti**: [github.com/vjt/decaf](https://github.com/vjt/decaf) — MIT, 156 test, pre-commit hook con ruff + pyright + pytest
- **Manuale**: [`doc/decaf_manual.pdf`](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.3.2/doc/decaf_manual.pdf) — guida più riferimenti normativi fino alla Gazzetta Ufficiale

Feedback, bug report e integrazioni broker nuove sono benvenute negli [issue](https://github.com/vjt/decaf/issues). Scrivimi quando i numeri non tornano con quelli del tuo commercialista — è l'unico feedback che non posso procurarmi in nessun altro modo.

Buone dichiarazioni — per quel poco che possono essere buone.
