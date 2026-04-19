---
title: "De-CAF: filing Italian taxes on foreign investments, without a commercialista"
date: 2026-04-18
tags: [python, taxes, italy, foreign-investments, open-source, finance]
description: "Why I wrote decaf — a Python tool that takes broker files from Interactive Brokers and Charles Schwab and spits out everything you need to fill the Modello Redditi PF: Quadro RW, RT, RL. With three test fixtures named after three Italian audio-cult saints."
image: cover.png
featuredImage: cover.png
draft: true
---

If you hold foreign investments as an Italian tax resident, you know the drill. Every spring you bundle a stack of PDFs and broker exports, send them to your [commercialista](https://it.wikipedia.org/wiki/Commercialista), and a few weeks later you get back a PDF that costs between three hundred and eight hundred euros and which you have no way of verifying because you don't speak [TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917) fluently.

A project like decaf, until recently, wouldn't have been an evenings-and-weekends project: reading the TUIR, Agenzia delle Entrate circolari, and interpello responses isn't my job, and doing it with enough precision to bet a tax filing on it takes months. With an [LLM](https://www.anthropic.com/claude/opus) that chews through the legislation alongside me and keeps me honest, it became feasible. The result is [`decaf-tax`](https://pypi.org/project/decaf-tax/) on PyPI and [github.com/vjt/decaf](https://github.com/vjt/decaf) on GitHub, MIT-licensed. With a test suite built specifically to keep me from fudging numbers: synthetic cases with their expected outputs stored next to them, plus three years of my own real filing — the one validated by the commercialista — used as an ongoing reference. I'll unroll the technical details below.

<!--more-->

## What it actually does

`decaf` is two commands. `decaf load` pulls data from each of your brokers and normalizes it into a single broker-agnostic shape: trades, dividends, interest, wires, currency conversions, RSU vests — all deposited into a local database as events on a single timeline. That's the piece that makes the rest tractable: once every broker's flows live on the same timeline, the filing becomes an aggregation problem, not a correlate-across-spreadsheets problem — including the things that have to be computed *across* brokers, like currency gains. `decaf report --year 2025` reads back from the database, converts USD to EUR at the ECB rate on the right date (settlement for monitoring, trade for gains — those are two different dates), and produces a report.

The report comes out in several formats: colored tables in the terminal, [an Excel file](/posts/2026-04-18-decaf-tax/decaf_2025.xlsx) with one sheet per quadro, [a PDF prospectus](/posts/2026-04-18-decaf-tax/decaf_2025.pdf), and a plain-text file with the full dump. That last one is the one that matters to me: it's the reference I use to be sure that, when I change the code, the numbers don't silently drift — it's how I notice immediately if I've broken some calculation path.

As for what's in it, decaf produces four things:

- **Quadro RW** — foreign-asset monitoring plus [IVAFE](https://www.agenziaentrate.gov.it/portale/schede/pagamenti/imposta-valore-att-estero-ivafe/base-imponibile-e-aliquote-scheda-ivafe): 0.2% per year on the mark-to-market value of your securities and on broker cash balances, pro-rated by holding days. Decaf does not handle foreign bank accounts (Revolut, Wise, N26 and the like): those carry a flat €34.20 per year, and you declare them by hand. Code in [`quadro_rw.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rw.py).
- **Quadro RT** — 26% capital gains on securities. Decaf trusts the broker's cost-basis determination: the broker tracks every lot (acquisition date, price, quantity) and on each sale records which lot you disposed of and its actual cost basis — you pick it via Tax Optimizer on Schwab or the matching method in IBKR account settings. This is exactly the method [AdE circolare 165/E of 24/06/1998, §2.3.2](https://def.finanze.it/DocTribFrontend/getPrassiDetail.do?id=%7B223C9DB9-C064-4DDA-84B2-819A66817892%7D) prescribes for partecipazioni: taxable base = *sale proceeds − actual acquisition cost of the lot sold*. No FIFO/LIFO presumption, no recomputation. On the FX side decaf applies [art. 9 c. 2 TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art9) literally: each closed lot is converted to EUR using **two** distinct ECB rates — the cost at the rate on the *lot's acquisition date*, the proceeds at the rate on the *sale's settlement date* — and the gain is the difference of the two. On multi-year lots, using a single rate (the usual shortcut) can move the taxable base by several percent relative to what the statute actually says. Code in [`quadro_rt.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rt.py).
- **Quadro RL** — gross foreign interest and dividends, paired with the withholding actually applied at source. This is where you reconcile the Italian 26% against whatever the source country withheld. Code in [`quadro_rl.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rl.py).
- **Soglia valutaria** — the forex threshold analysis under [art. 67(1)(c-ter) TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67). If you sit on more than €51,645.69 in foreign currency for seven or more consecutive working days, your USD balance becomes a financial asset in its own right, and its *currency* gains become taxable. Which brings us to the hard part.

## The one thing brokers weren't giving me

Brokers give you the stock gain ready-made. They don't give you the currency gain, because from their perspective your dollars are just the settlement currency of your account — there's no "realization event" when you go back to euros. From the AdE's perspective, on the other hand, every EUR→USD conversion is a purchase of USD lots, every USD→EUR (or outbound wire) is a disposal, and if you've crossed the threshold you owe 26% on the euro-denominated gain. How to compute it is set by [art. 67 c. 1-bis TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67) ("those acquired most recently are considered disposed first" — LIFO, *last-in first-out*) and [AdE ruling 204/2023](https://www.agenziaentrate.gov.it/portale/documents/20143/5297297/Risposta+n.+204+del+2023.pdf) ("computed analytically and separately, for each account" — no commingling between broker accounts, each keeps its own lot queue).

That's where [`forex_gains.py`](https://github.com/vjt/decaf/blob/master/src/decaf/forex_gains.py) lives. It walks broker events in chronological order and keeps a LIFO tracker *per account*: dollars acquired from stock sales, dividends and interest on an account are purchases of that account; those disposed via EUR.USD conversions and wires from the same account are sales of that account, matched first against the most-recently-acquired lot. One subtlety worth covering: a same-currency transfer between two broker accounts belonging to the same person isn't a disposal under [AdE ruling 60/E of 2024-12-09](https://www.agenziaentrate.gov.it/portale/documents/20143/6475876/Risoluzione+60E+del+09+12+2024.pdf), so from v0.3.0 decaf auto-matches cross-broker wires (same currency, same amount within 0.01 USD, settle date within ±3 business days, distinct accounts owned by the same person): the USD lots migrate from the source account's queue into the destination account's queue preserving original acquisition date and ECB rate, and no artificial gain is booked on the transfer. The realized gain on each *actual* disposal is

```
gain_eur = usd_amount × (1/ecb_rate_disposal − 1/ecb_rate_acquisition)
```

— the formula lives in [`forex_gains.py#L11`](https://github.com/vjt/decaf/blob/master/src/decaf/forex_gains.py#L11). The rate inversion matters: the ECB publishes the rate as USD per EUR, but what we need here is euros per disposed dollar. If the threshold wasn't crossed for that year the tracker runs but [`quadro_rt.py`](https://github.com/vjt/decaf/blob/master/src/decaf/quadro_rt.py) ignores it. If it was crossed, its output becomes RT lines alongside the stock gains.

I spent more time on this file than on the other nine quadro modules combined. There's no shortcut: you can't trust the broker's currency P/L (they compute it against account base currency at internal rates, which aren't the ECB's), and you can't skip it either, because the AdE does check.

## Supported brokers

Two, for now, because those are the two I use:

- **Interactive Brokers** (Ireland entity) — [Flex Query](https://www.ibkrguides.com/orgportal/performanceandstatements/flex.htm) XML, downloaded by hand from the IBKR portal, or pulled automatically if you know how to generate a Flex Query token and drop it in `.env`. Clean, structured, idempotent. If you've never set up a Flex Query, there's a twelve-screenshot walkthrough in [`doc/QUERY_SETUP.md`](https://github.com/vjt/decaf/blob/master/doc/QUERY_SETUP.md), because the IBKR portal is the IBKR portal. Parser in [`parse.py`](https://github.com/vjt/decaf/blob/master/src/decaf/parse.py).

- **Charles Schwab** (EAC — *Equity Award Center*, the accounts Schwab assigns to employees who receive RSUs or stock options from their employer) — three files, downloaded by hand from `schwab.com`: a JSON export of the transactions, the Year-End Summary PDF for per-lot gains, and the Annual Withholding Statement PDF for vest fair-market-values.

  Why three files and not an API? Because I registered with Schwab's developer portal, waited for account approval, registered an app, ran the OAuth2 flow — all fine — and then the endpoints came back empty. The [Trader API doesn't support EAC accounts](https://github.com/vjt/decaf/blob/master/doc/INTERNALS.md#schwab-integration), and Schwab's other APIs don't expose the tax information that matters (per-lot cost basis, per-jurisdiction vest FMVs): those only live in the annual PDFs. So, PDF parsing it is. `poppler-utils` does the heavy lifting. Orchestrator in [`schwab_parse.py`](https://github.com/vjt/decaf/blob/master/src/decaf/schwab_parse.py).

Fineco, Directa and Degiro aren't there yet. Degiro is the obvious candidate: it's regime dichiarativo by default, you file RW and RT yourself. Fineco and Directa default to regime amministrato — they act as withholding agent, they compute the taxes for you, and RW is actually exempted — so decaf only helps you there if you've specifically opted into regime dichiarativo. Adding a broker means a new parser module that builds the same internal `ParsedData`; the rest of the pipeline doesn't care where the events came from. PRs welcome.

## The trio

Tax arithmetic is a domain where getting one number wrong means writing the wrong thing on the Modello Redditi. So decaf has a test infrastructure built to keep me from trusting muscle memory.

The anchor is my own real filing. For three years running (2022, 2023, 2024) I reconciled decaf's numbers against those the commercialista signed off on, line by line; those three filings — which stay on my disks, not public — are the first smoke test and I re-run them on every code change, with any unexplained drift putting the change back into review. "Matched", though, needs a qualifier: up through v0.2.0 the numbers agreed to the cent, but v0.3.1 rolled out the per-lot EUR conversion prescribed by art. 9 c. 2 TUIR (cost at the ECB rate on the lot's acquisition date, proceeds at the ECB rate on the sale's settlement date), and that shifts the taxable base by 2–3% relative to the single-rate shortcut the commercialista — like nearly everyone — had applied. The tax delta on my scenarios runs about fifty to sixty euros per year: small, in the taxpayer's favor, and — more importantly — what the statute actually says. That decaf now diverges from the commercialista in a *documented and defensible* way — citing the same TUIR article — feels more like validation than a bug.

From that validated base I derived three [synthetic cases](https://github.com/vjt/decaf/tree/master/examples): fake data, built to exercise the same logic without exposing my real numbers. They live alongside the code, and each one ships with its **expected report** next to it: when I change something and re-run decaf, comparing the new output to the expected report is immediate, and any difference jumps out. On top of that, three automatic checks run on every test pass: the report matches the expected one exactly, each quadro's row count stays stable, and every Quadro RL row satisfies `net = gross − withholding`. Code in [`tests/test_e2e.py`](https://github.com/vjt/decaf/blob/master/tests/test_e2e.py).

Want to try it on your own numbers? [`doc/BACKTEST.md`](https://github.com/vjt/decaf/blob/master/doc/BACKTEST.md) walks you through feeding decaf your past filing and comparing the output against whatever your commercialista came back with — *try before you buy*, satisfaction guaranteed or your money back.

The three public synthetic cases cover three levels of increasing complexity:

- **[`magnotta/`](https://github.com/vjt/decaf/tree/master/examples/magnotta)** — the base case. IBKR only, one year, IVAFE pro-rata on a partial-year position, a losing trade of 480,000 old lire, one dividend with US withholding.
- **[`mosconi/`](https://github.com/vjt/decaf/tree/master/examples/mosconi)** — IBKR plus Schwab, two years, the same ticker on both, partial sale across multiple lots, RSU vesting.
- **[`mascetti/`](https://github.com/vjt/decaf/tree/master/examples/mascetti)** — the stress test. Two years, forex threshold breached in both, per-account LIFO across multiple USD lots, RSUs vesting across years, four different withholding rates (US 30%, UK 0%, DE 26.375%, IT 26%).

The names are not random. In order:

- [Mario Magnotta](https://it.wikipedia.org/wiki/Mario_Magnotta), the L'Aquila school custodian whose 1987 phone-prank tapes made him the patron saint of Italians being ruined by paperwork they never signed.
- [Germano Mosconi](https://it.wikipedia.org/wiki/Germano_Mosconi), the Veronese TV journalist whose off-air blasphemy tapes taught an entire generation how to cope with a malfunctioning teleprompter.
- [Il Conte Raffaello Mascetti](https://it.wikipedia.org/wiki/Amici_miei) from *Amici Miei* — the inventor of the [supercazzola](https://youtu.be/9-1T3sTk1Ng), patron saint of verbal smokescreens deployed against incomprehensible authority.

Three figures who, each in their own register, captured what it feels like to deal with Italian bureaucracy: Mascetti talks his way through it, Mosconi curses his way through it, Magnotta is destroyed by it. Test-case naming is rarely this satisfying.

## Disclaimer that is not a joke

`decaf` **interprets the law**. The arithmetic is the easy part; the interpretation — which transaction goes into which quadro, which date to use, which FX rate, which threshold — is the work I did together with [Claude Opus 4.7](https://www.anthropic.com/claude/opus), reading TUIR, Agenzia delle Entrate circolari, and interpello responses. The full normative references, with Gazzetta Ufficiale links, live in [`doc/NORMATIVA.md`](https://github.com/vjt/decaf/blob/master/doc/NORMATIVA.md), and the operational filing guide is in [`doc/GUIDA_FISCALE.md`](https://github.com/vjt/decaf/blob/master/doc/GUIDA_FISCALE.md) — both bundled into the [manual PDF](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.3.2/doc/decaf_manual.pdf) if you'd rather download everything in one file. I back-tested it against my own filings from 2022 to 2024, reconciling every number with the commercialista's.

But: my scenarios aren't that complicated. The software handles cases more complex than anything I've been able to verify against a real signed filing — multi-year RSUs across multiple brokers, forex threshold, per-account LIFO across dozens of currency lots, four withholding jurisdictions — and those cases have their own dedicated synthetic fixtures, but no back-test against a signed return. One specific caveat worth flagging: for assets held in states with privileged tax regimes (so-called *black-list* countries), the IVAFE rate rises to 0.4% starting in 2024, and decaf doesn't detect that automatically yet — if you have black-list exposure, adjust by hand. Your mileage may vary: if the law changes (and it does, every year), or if you have an edge case outside the synthetic fixtures, **use at your own risk**. For the weird years, go to a commercialista anyway. I do.

The point of writing this, and of open-sourcing it, is that the arithmetic should be commodity. You shouldn't have to pay a professional every spring just to multiply your dividends by the ECB rate on the settlement date. Save that money for the cases where the professional's *judgement* is what matters.

## Where to find it

- **PyPI**: [`pip install --user decaf-tax`](https://pypi.org/project/decaf-tax/) — command is `decaf`
- **Source**: [github.com/vjt/decaf](https://github.com/vjt/decaf) — MIT, 156 tests, pre-commit hook enforcing ruff + pyright + pytest
- **Manual**: [`doc/decaf_manual.pdf`](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.3.2/doc/decaf_manual.pdf) — guide plus full normative references down to the Gazzetta Ufficiale

Feedback, bug reports, and new broker integrations welcome in the [issue tracker](https://github.com/vjt/decaf/issues). Tell me when the numbers don't match your commercialista's — that's the one piece of feedback I can't get any other way.

Happy filing — for what little that's worth.
