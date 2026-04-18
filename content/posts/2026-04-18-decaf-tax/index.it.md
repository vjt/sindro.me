---
title: "De-CAF: fare la dichiarazione su investimenti esteri senza commercialista"
date: 2026-04-18
tags: [python, tasse, italia, investimenti-esteri, open-source, finanza]
description: "Perché ho scritto decaf — un tool Python che prende i file di Interactive Brokers e Charles Schwab e sputa fuori tutto quello che serve per compilare il Modello Redditi PF: Quadro RW, RT, RL. Con tre fixture di test intitolate a tre santi patroni dell'audio-cult italiano."
image: cover.png
featuredImage: cover.png
---

Se sei residente fiscale in Italia e hai investimenti all'estero, la scena la conosci. Ogni primavera carichi gli screenshot del conto del broker in una cartella Drive, li mandi al [commercialista](https://it.wikipedia.org/wiki/Commercialista), e qualche settimana dopo ti torna indietro un PDF che costa tra i trecento e gli ottocento euro e che non hai modo di verificare perché non mastichi il [TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917) fluente.

Due anni fa mi sono stancato e ho cominciato a rifare i conti a mano in un foglio di calcolo. L'inverno scorso ho riscritto il foglio in Python. La settimana scorsa l'ho pubblicato su PyPI come [`decaf-tax`](https://pypi.org/project/decaf-tax/) e su [GitHub](https://github.com/vjt/decaf). Licenza MIT, i test includono tre fixture sintetiche intitolate a tre santi patroni del meme italiano, e il README ha un disclaimer che non è uno scherzo: **è uno strumento, non un commercialista** — automatizza l'aritmetica, non interpreta la giurisprudenza.

<!--more-->

## Cosa fa, in concreto

`decaf` sono due comandi. `decaf fetch` scarica i dati dal broker e i tassi di riferimento giornalieri [della BCE](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), li deposita in un file SQLite locale, e stop. `decaf report --year 2025` rilegge dal SQLite, converte USD in EUR al cambio BCE della data giusta (regolamento per il monitoraggio, operazione per le plusvalenze — sono due date diverse), e produce quattro cose:

- **Quadro RW** — monitoraggio attività estere più [IVAFE](https://www.agenziaentrate.gov.it/portale/web/guest/schede/pagamenti/ivafe/ivafe-scheda-informativa): 0.2% annuo sul valore di mercato dei titoli, pro-rata per giorni di detenzione, più €34.20 fissi per ogni conto di liquidità.
- **Quadro RT** — plusvalenze al 26% sui titoli. Qui decaf si fida del [FIFO del broker](https://www.investopedia.com/terms/f/fifo.asp); non ha senso reimplementare il cost basis quando IBKR e Schwab lo tracciano già.
- **Quadro RL** — interessi e dividendi esteri lordi, abbinati alla ritenuta effettivamente applicata alla fonte. È qui che riconcili il 26% italiano con qualunque ritenuta abbia trattenuto il paese estero.
- **Soglia valutaria** — l'analisi ex [art. 67(1)(c-ter) TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67). Se stai sopra €51.645,69 in valuta estera per sette o più giorni lavorativi consecutivi, il tuo saldo in USD diventa un'attività finanziaria a tutti gli effetti e le sue plusvalenze *valutarie* diventano imponibili. Il che ci porta alla parte rognosa.

Output: tabelle colorate nel terminale, un file Excel con un foglio per quadro, un PDF con il prospetto, e un dump YAML completo del `TaxReport` interno. Lo YAML per me è quello che conta davvero — è diffabile e stabile tra run, e quindi posso committarlo come oracolo di regressione.

## L'unica cosa che ho dovuto calcolare

I broker ti danno il FIFO titoli gratis. Il FIFO sulla valuta non te lo danno, perché per loro i dollari sono solo la valuta di regolamento del conto — non c'è nessun "evento realizzativo" quando torni all'euro. Dal punto di vista dell'AdE invece ogni conversione EUR→USD è un acquisto di lotti USD, ogni conversione USD→EUR (o bonifico in uscita) è una cessione, e se hai sforato la soglia paghi il 26% sulla plusvalenza in euro calcolata FIFO su tutti i lotti.

È qui che vive `forex_gains.py`. Scorre gli eventi del broker in ordine cronologico e mantiene un tracker FIFO per i dollari: quelli acquisiti da vendite di titoli, dividendi e interessi sono acquisti; quelli ceduti via EUR.USD e bonifici sono vendite. La plusvalenza realizzata su ogni cessione è `(tasso_cessione - tasso_acquisto) * importo_usd`, in euro, al cambio BCE delle rispettive date. Se la soglia non è stata superata nell'anno il tracker gira ma `quadro_rt.py` lo ignora. Se è stata superata, il suo output diventa righe RT affianco alle plusvalenze titoli.

Su questo file ho speso più tempo che sugli altri nove moduli quadro messi insieme. Non c'è scorciatoia: non ti puoi fidare del P/L valutario del broker (lo calcolano contro la valuta base del conto con tassi interni, che non sono i BCE), e non lo puoi saltare, perché l'AdE controlla.

## Broker supportati

Due, per ora, perché sono i due che uso:

- **Interactive Brokers** (entity irlandese) — [Flex Query](https://www.interactivebrokers.com/en/software/am/am/reports/flex_queries.htm) XML, scaricato via API HTTPS con due token in `.env` o parsato da file già esportato. Pulito, strutturato, idempotente. Se una Flex Query non l'hai mai configurata c'è una guida con dodici screenshot in [`doc/QUERY_SETUP.md`](https://github.com/vjt/decaf/blob/master/doc/QUERY_SETUP.md), perché il portale IBKR è il portale IBKR.
- **Charles Schwab** (conti EAC/RSU) — tre file, scaricati a mano da `schwab.com`. Un export JSON delle transazioni, il PDF del Year-End Summary per le plusvalenze per lotto, e il PDF dell'Annual Withholding Statement per i fair-market-value ai vest. La Trader API di Schwab [è rotta per i conti EAC](https://github.com/vjt/decaf/blob/master/doc/INTERNALS.md) — l'OAuth2 gira, ma gli endpoint non restituiscono i dati — quindi si parsa il PDF. Il lavoro pesante lo fa `poppler-utils`.

Fineco no, Directa no, Degiro no, ancora. Aggiungere un broker significa un nuovo modulo `parse.py` che costruisca gli stessi `ParsedData` interni; al resto della pipeline non importa da dove arrivano gli eventi. PR benvenute.

## Il trittico

In `tests/reference/` ci sono tre fixture sintetiche. I nomi non sono casuali.

- **[`magnotta/`](https://github.com/vjt/decaf/tree/master/examples/magnotta)** — il caso base. Solo IBKR, un anno, IVAFE pro-rata su una posizione parziale, un trade in perdita, un dividendo con ritenuta US. Come [Mario Magnotta](https://it.wikipedia.org/wiki/Mario_Magnotta), il bidello aquilano i cui nastri delle beffe telefoniche del 1987 lo hanno consacrato santo patrono degli italiani rovinati da carte che non hanno mai firmato.
- **[`mosconi/`](https://github.com/vjt/decaf/tree/master/examples/mosconi)** — IBKR più Schwab, due anni, stesso ticker su entrambi, vendita FIFO parziale, vesting RSU. Come [Germano Mosconi](https://it.wikipedia.org/wiki/Germano_Mosconi), il giornalista veronese le cui bestemmie off-air hanno insegnato a un'intera generazione come affrontare un gobbo che non funziona.
- **[`mascetti/`](https://github.com/vjt/decaf/tree/master/examples/mascetti)** — lo stress test. Due anni, soglia valutaria superata entrambi, FIFO su lotti USD multipli, RSU che vestano su più anni, quattro ritenute diverse (US 30%, UK 0%, DE 26.375%, IT 26%). Come [Il Conte Raffaello Mascetti](https://it.wikipedia.org/wiki/Amici_miei) di *Amici Miei* — l'inventore della [supercazzola](https://it.wikipedia.org/wiki/Supercazzola), santo patrono delle cortine verbali spiegate contro autorità incomprensibili.

Tre figure che, ciascuna a suo modo, hanno fissato che cosa si prova davanti alla burocrazia italiana: Mascetti ci parla sopra, Mosconi ci bestemmia sopra, Magnotta ne viene distrutto. Raramente ho avuto tanta soddisfazione nell'intitolare dei test.

## Disclaimer che non è uno scherzo

`decaf` calcola numeri. Il commercialista interpreta la legge. Sono due cose diverse.

Se la tua situazione è semplice — un broker, niente RSU, niente soglia valutaria, niente ritenute anomale — i numeri che escono da decaf probabilmente coincidono con quelli per cui un commercialista si farebbe pagare. Se la tua situazione è complessa, o se la legge cambia (e cambia, ogni anno), o se hai dubbi sul fatto che una specifica transazione sia una plusvalenza, un rimborso o una distribuzione, **vai dal commercialista**. Ci vado anch'io, per gli anni strani. Il tool è un punto di partenza, non un oracolo, e scrivo il disclaimer nel README, nel banner della CLI e qui.

Il senso di scriverlo, e di liberarne il codice, è che l'aritmetica dovrebbe essere commodity. Non dovresti dover pagare un professionista ogni primavera solo per moltiplicare i dividendi per il cambio BCE alla data di regolamento. Quei soldi tienili per i casi in cui a contare è il *giudizio* del professionista.

## Dove trovarlo

- **PyPI**: [`pip install --user decaf-tax`](https://pypi.org/project/decaf-tax/) — il comando è `decaf`
- **Sorgenti**: [github.com/vjt/decaf](https://github.com/vjt/decaf) — MIT, 143 test, pre-commit hook con ruff + pyright + pytest
- **Manuale**: [`doc/decaf_manual.pdf`](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.1.3/doc/decaf_manual.pdf) — guida più riferimenti normativi fino alla Gazzetta Ufficiale

Feedback, bug report e integrazioni broker nuove sono benvenute negli [issue](https://github.com/vjt/decaf/issues). Scrivimi quando i numeri non tornano con quelli del tuo commercialista — è l'unico feedback che non posso procurarmi in nessun altro modo.
