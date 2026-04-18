---
title: "De-CAF: filing Italian taxes on foreign investments without a commercialista"
date: 2026-04-18
tags: [python, taxes, italy, foreign-investments, open-source, finance]
description: "Why I wrote decaf — a Python tool that takes broker files from Interactive Brokers and Charles Schwab and spits out everything you need to fill the Modello Redditi PF: Quadro RW, RT, RL. With three test fixtures named after three Italian audio-cult saints."
image: cover.png
featuredImage: cover.png
---

If you hold foreign investments as an Italian tax resident, you know the drill. Every spring you dump screenshots of your broker account into a Google Drive folder, send them to your [commercialista](https://it.wikipedia.org/wiki/Commercialista), and a few weeks later you get back a PDF that costs between three hundred and eight hundred euros and which you have no way of verifying because you don't speak [TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917) fluently.

I got tired of this two years ago and started writing the calculation by hand in a spreadsheet. Last winter I rewrote the spreadsheet in Python. Last week I published it on PyPI as [`decaf-tax`](https://pypi.org/project/decaf-tax/) and on [GitHub](https://github.com/vjt/decaf). The source is MIT, the tests include three synthetic fixtures named after Italian meme saints, and the README has a disclaimer that is not a joke: **this is a tool, not a commercialista** — it automates the arithmetic, it doesn't interpret case law.

<!--more-->

## What it actually does

`decaf` is two commands. `decaf fetch` pulls data from your broker and from the ECB's [daily reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), stores it in a local SQLite file, and that's it. `decaf report --year 2025` reads back from SQLite, converts USD to EUR at the ECB rate on the right date (settlement for monitoring, trade for gains — the two are different), and produces four things:

- **Quadro RW** — foreign asset monitoring plus [IVAFE](https://www.agenziaentrate.gov.it/portale/web/guest/schede/pagamenti/ivafe/ivafe-scheda-informativa): 0.2% per year on the mark-to-market value of your securities, pro-rated by holding days, plus a flat €34.20 for any cash account.
- **Quadro RT** — capital gains at 26% on stocks. Decaf trusts the broker's [FIFO P/L](https://www.investopedia.com/terms/f/fifo.asp) here; no point re-implementing cost basis when Interactive Brokers and Schwab both already track it.
- **Quadro RL** — gross interest and foreign dividends, paired with the foreign withholding actually applied. This is where you reconcile the Italian 26% against whatever the source country withheld.
- **Soglia valutaria** — the forex threshold analysis under [art. 67(1)(c-ter) TUIR](https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art67). If you sit on more than €51,645.69 in foreign currency for seven or more consecutive working days, your USD balance gets treated as a financial asset and its *currency* gains become taxable. Which brings us to the hard part.

Output: colored tables in the terminal, an Excel file with one sheet per quadro, a PDF prospectus, and a full YAML dump of the internal `TaxReport` object. The YAML is the one that matters for me — it's diff-friendly and stable across runs, which means I can commit it as a regression oracle.

## The one thing I had to compute

Brokers give you the stock FIFO for free. They don't give you the forex FIFO, because from their perspective your dollars are just the settlement currency of your account — there is no "realization event" when you convert back to euro. From the Italian tax office's perspective, on the other hand, every EUR→USD conversion is a purchase of USD lots, and every USD→EUR conversion (or wire out) is a disposal, and if you cross the threshold you owe 26% on the euro-denominated gain computed FIFO across all lots.

This is where `forex_gains.py` lives. It walks your broker events in chronological order and maintains a FIFO lot tracker for USD: dollars acquired from stock sales, dividends, and interest are purchases; dollars disposed via EUR.USD conversions and wire transfers are sales. The realized gain on each disposal is `(disposal_rate - acquisition_rate) * usd_amount`, in euros, quoted at ECB rates on the respective trade dates. If the seven-day threshold hasn't been breached for that year the tracker runs but `quadro_rt.py` ignores it. If it has, the tracker's output becomes RT lines alongside the stock gains.

I spent more time on this file than on the other nine quadro modules combined. There's no shortcut: you can't trust the broker's currency P/L (they compute it against account base currency at internal rates, which aren't the ECB's), and you can't skip it either, because the AdE does check.

## Supported brokers

Two, for now, because those are the two I use:

- **Interactive Brokers** (Ireland entity) — [Flex Query](https://www.interactivebrokers.com/en/software/am/am/reports/flex_queries.htm) XML, either fetched via the HTTPS API with a pair of tokens in `.env` or parsed from a downloaded file. Clean, structured, idempotent. If you've never set up a Flex Query before there's a twelve-screenshot walkthrough in [`doc/QUERY_SETUP.md`](https://github.com/vjt/decaf/blob/master/doc/QUERY_SETUP.md) because the IBKR portal is the IBKR portal.
- **Charles Schwab** (EAC/RSU accounts) — three files, downloaded by hand from `schwab.com`. A JSON export of the transaction history, the Year-End Summary PDF for per-lot gains, and the Annual Withholding Statement PDF for vest FMVs. The Schwab Trader API is [broken for EAC accounts](https://github.com/vjt/decaf/blob/master/doc/INTERNALS.md) — the OAuth2 flow works, the endpoints just don't return the data — so PDF parsing it is. `poppler-utils` does the heavy lifting.

There's no Fineco, no Directa, no Degiro yet. Adding one is a new `parse.py` module that builds the same internal `ParsedData` domain dataclasses; the rest of the pipeline doesn't care where the events came from. PRs welcome.

## The trio

`tests/reference/` has three synthetic fixtures. The names are not random.

- **[`magnotta/`](https://github.com/vjt/decaf/tree/master/examples/magnotta)** — the base case. IBKR only, one year, IVAFE pro-rata on a partial-year position, one losing trade, one dividend with US withholding. Named after [Mario Magnotta](https://it.wikipedia.org/wiki/Mario_Magnotta), the L'Aquila school custodian whose 1987 phone-prank tapes made him the patron saint of Italians being ruined by paperwork they never signed.
- **[`mosconi/`](https://github.com/vjt/decaf/tree/master/examples/mosconi)** — IBKR plus Schwab, two years, same ticker across both brokers, partial FIFO sale, RSU vest. Named after [Germano Mosconi](https://it.wikipedia.org/wiki/Germano_Mosconi), the Veronese TV journalist whose off-air blasphemy tapes taught an entire generation how to cope with a malfunctioning teleprompter.
- **[`mascetti/`](https://github.com/vjt/decaf/tree/master/examples/mascetti)** — the stress test. Two years, forex threshold breached both of them, FIFO across multiple USD lots, RSUs vesting across years, four different withholding rates (US 30%, UK 0%, DE 26.375%, IT 26%). Named after [Il Conte Raffaello Mascetti](https://it.wikipedia.org/wiki/Amici_miei) from *Amici Miei* — the inventor of the [supercazzola](https://en.wikipedia.org/wiki/Supercazzola), patron saint of verbal smokescreens deployed against incomprehensible authority.

Three figures who all, in their own register, captured what it feels like to deal with Italian bureaucracy: Mascetti talks his way through it, Mosconi curses his way through it, Magnotta is destroyed by it. Test-case naming is rarely this satisfying.

## Disclaimer that is not a joke

`decaf` computes numbers. A commercialista interprets law. These are different things.

If your situation is simple — one broker, no RSUs, no forex threshold, no unusual withholdings — the numbers that come out of decaf will probably match what a commercialista would charge you to produce. If your situation is complex, or if the law changes (it does, every year), or if you have doubts about whether a specific transaction is a capital gain or a redemption or a distribution, **go to a commercialista**. I do, too, for the weird years. The tool is a starting point, not an oracle, and I disclaim liability in the README, in the CLI banner, and here.

The point of writing this, and of open-sourcing it, is that the arithmetic should be commodity. You shouldn't have to pay a professional every spring just to multiply your dividends by the ECB rate on the settlement date. Spend that money on the cases where the professional's *judgement* matters.

## Where to find it

- **PyPI**: [`pip install --user decaf-tax`](https://pypi.org/project/decaf-tax/) — command is `decaf`
- **Source**: [github.com/vjt/decaf](https://github.com/vjt/decaf) — MIT, 143 tests, pre-commit hook enforcing ruff + pyright + pytest
- **Manual**: [`doc/decaf_manual.pdf`](https://cdn.jsdelivr.net/gh/vjt/decaf@v0.1.3/doc/decaf_manual.pdf) — guide plus full normative references down to the Gazzetta Ufficiale

Feedback, bug reports, and broker integrations welcome in the [issue tracker](https://github.com/vjt/decaf/issues). Tell me when the numbers don't match your commercialista's — that's the one piece of feedback I cannot get any other way.
