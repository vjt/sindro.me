---
title: "Come ho usato Claude per rifare completamente il blog in due giorni"
date: 2026-04-07
tags: [ai-generated, projects, sysadmin]
categories: [development]
description: "Un post meta sull'uso di Claude Code per tradurre 69 articoli, ridisegnare il layout da zero e aggiungere un easter egg con la sequenza di boot — tutto in 48 ore di iterazione continua."
---

È come avere un ingegnere incredibilmente veloce, competente e preciso seduto accanto a te — uno che ti lascia davvero fluire creativamente senza freni. Dici "e se facessimo..." e trenta secondi dopo hai un prototipo funzionante davanti agli occhi. Dici "no, più così" e ha già finito prima che tu abbia spiegato il perché.

È questa la sensazione che ho avuto lavorando con [Claude Code](https://claude.ai/code) negli ultimi due giorni. Ho rifatto completamente questo blog — tradotto tutti e 69 gli articoli in italiano, ridisegnato il layout da zero, aggiunto un easter egg nerd con la sequenza di boot del kernel, ripulito anni di tag accumulati, e iterato su decine di decisioni di design. Tutto tracciato in git, tutto verificabile, tutto live.

Ecco il mio grafico di contribuzione su GitHub, per dimostrare che non sto esagerando:

![Attività GitHub con una valanga di commit](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/github-activity.png)

Quel muro verde sono 40 giorni di lavoro con Claude su un sacco di progetti — [integrazioni domotiche](/it/posts/2026-04-04-verisure-italy-home-assistant/), [strumenti di rete per OpenWrt](/it/posts/2026-04-03-wifi-dethrash-openwrt-mesh-analyzer/), [rilevamento presenza WiFi](/it/posts/2026-02-15-wifi-presence-detection-home-assistant/), [tooling per modem 5G](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/), e questo redesign del blog. Solo gli ultimi due giorni coprono una fetta ridicola del totale.

## Il punto di partenza

Questo blog esiste dal 2007, ma la versione Hugo risale al 2023 quando ho migrato da WordPress. Usava il [tema Poison](https://github.com/vjt/poison) — un fork di Hyde/Poole — con sidebar scura, solo in inglese, e un layout che urlava "il 2015 chiama, vuole il suo CSS indietro."

![Il vecchio layout — sidebar scura, solo inglese, CSS Hyde/Poole](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/old-layout-desktop.png)

Funzionava. Ma si sentiva datato. La sidebar era troppo larga su mobile, l'area di contenuto troppo stretta su desktop, e il tutto era solo in inglese nonostante io sia italiano e abbia un pubblico in entrambe le lingue.

## Fase 1: Diventare bilingue

La prima grande mossa è stata tradurre tutti e 69 gli articoli dall'inglese all'italiano. Il che ha implicato:

- Configurare l'infrastruttura multilingue di Hugo (`config.toml` con i blocchi `[languages.en]` e `[languages.it]`)
- Rinominare ogni file di contenuto da `post.md` a `post.en.md` e creare le controparti `post.it.md`
- Aggiungere `i18n/en.yaml` e `i18n/it.yaml` per le stringhe dell'interfaccia
- Costruire un selettore di lingua con i pulsanti a emoji bandiera
- Configurare nginx per rilevare gli header `Accept-Language` e fare il redirect di conseguenza

Claude ha gestito le traduzioni con buona qualità — non perfette, ma più che sufficienti per un blog tecnico dove il gergo resta comunque in inglese. Il tono conversazionale in italiano usa il "tu" informale, che si adatta bene al mio stile di scrittura.

![Dopo l'i18n — stesso layout scuro, ma ora bilingue con il selettore di lingua](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/i18n-layout-desktop.png)

Nota il selettore con le bandiere nell'angolo in alto a sinistra della sidebar. Stesso layout scuro, ma ora il sito funziona in entrambe le lingue.

## Fase 2: Il redesign del layout

È qui che ci si è divertiti. Volevo qualcosa di moderno, funzionale, e che sprecasse meno spazio sullo schermo. Il processo è andato così:

### Brainstorming con un compagno visivo

Claude Code ha un sistema di plugin chiamato [Superpowers](https://github.com/anthropics/claude-code) che include una skill di brainstorming con un **visual companion** — un server web locale che renderizza mockup nel browser mentre discuti le opzioni di design dal terminale.

![Il visual companion del brainstorming che mostra le direzioni di layout](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/brainstorm-companion.png)

Ed è qui che la cosa diventa meta: Claude gira su un Raspberry Pi 5 (il mio server di casa), ma il browser è sul mio laptop. La connessione è un reverse tunnel SSH:

```bash
# Sul mio laptop — tunnel della porta di debug di Chrome verso il Pi
ssh -R 9222:localhost:9222 vjt@nowhere
```

Claude usa il [Chrome DevTools MCP](https://github.com/anthropics/mcp-servers) (Model Context Protocol) per pilotare il browser da remoto — naviga le pagine, fa screenshot, ispeziona gli elementi, valuta JavaScript. Riesce letteralmente a vedere com'è il sito e a debuggare i problemi CSS leggendo gli stili computati.

Il brainstorming in sé è stato collaborativo:
1. Ho detto "voglio qualcosa di più moderno, più funzionale, con meno spazio sprecato"
2. Claude mi ha mostrato tre direzioni visive nel browser — ho scelto "Crisp Light"
3. Abbiamo esplorato le opzioni di layout — ho scelto CSS Grid con hamburger sotto i 1200px
4. Ogni sezione del design veniva presentata e approvata prima di passare alla successiva
5. Una specifica formale è stata scritta e committata su git

### Dalla specifica all'implementazione

Il piano di implementazione aveva 12 task. Claude ha inviato subagent in parallelo — ognuno con un task specifico (scrivi `layout.css`, scrivi `components.css`, crea il partial dell'header, ecc.), lo implementava, committava e riportava indietro. Un revisore della specifica verificava ogni task rispetto al design, poi un revisore della qualità del codice controllava l'implementazione.

Le modifiche principali:
- **CSS Grid** ha sostituito il vecchio layout flexbox di Hyde/Poole
- **Desktop a tre colonne**: sidebar (220px) | contenuto (fluido) | table of contents (200px)
- **Menu hamburger** sotto i 1200px con sidebar a scorrimento laterale
- **Design light-first** con dark mode adattiva al sistema (`prefers-color-scheme`)
- **Script anti-FOUC** — un `<script>` inline nel `<head>` applica il tema scuro prima del primo render
- Larghezza massima dei contenuti allargata da 44rem a 52rem
- Tag ridisegnati come pill badge
- Navigazione tra post come card con bordo
- Header degli articoli in stile giornale

### Il ciclo di iterazione

Quello che ha davvero fatto funzionare tutto è stata la velocità di iterazione. Il ciclo era questo:

1. Segnalavo un problema ("le categorie sono testo semplice, non pill")
2. Claude correggeva il CSS, committava sul submodule del tema, pushava su GitHub
3. Poi SSH al server di build, pull, build e deploy in staging
4. Controllavo il risultato sul telefono/laptop
5. Si ricomincia

Ogni ciclo durava circa 60 secondi. In due ore abbiamo fatto decine di ritocchi visivi — correzioni al contrasto, dimensioni dei font, aggiustamenti di spaziatura, discussioni float vs. flex, posizionamento del TOC. Il tipo di rifinitura che normalmente richiede giorni di avanti e indietro.

## Il risultato

![Nuovo layout — chiaro, pulito, CSS Grid, responsive](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/new-layout-desktop.png)

Pulito. Light-first con dark mode di sistema. Tre colonne su desktop, hamburger su tablet/telefono. Il contenuto ha finalmente spazio per respirare, i blocchi di codice non richiedono scroll orizzontale, e il TOC sta dove ti aspetti che stia.

![Layout mobile con menu hamburger](/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/new-layout-mobile.png)

Su mobile: header compatto con brand + selettore di lingua, TOC collassabile, e la sidebar scorre fuori quando tocchi l'hamburger. Niente più scroll infinito oltre una sidebar gigante per arrivare al contenuto.

## L'easter egg

Perché cos'è il blog di un sysadmin senza un easter egg nerd? Alla prima visita ti appare una sequenza di boot del kernel Linux:

```
[    0.000000] Linux version 6.12.75+rpt-rpi-2712 (vjt@openssl.it) (gcc 12.2.0)
[    0.031201] CPU: ARMv8 Cortex-A76 [410fd083] revision 3 (ARMv8), cr=30c5383d
[    0.068442] Machine model: Raspberry Pi 5 Model B Rev 1.0
...
[    0.831002] hugo[1337]: Total in 91 ms
[    0.900000] init: blog ready. feeling bold on the internet.
```

Dura 3 secondi, poi sfuma per rivelare il blog. Usa `sessionStorage` così parte una sola volta per sessione browser — niente consumo di batteria, niente rompiscatole alle visite successive. Solo un momento "benvenuto nel mio mondo" una tantum.

## La pulizia dei tag

Già che c'eravamo, abbiamo passato in rassegna tutti i tag del blog. Da ~130 tag (molti con un solo articolo) a 33 puliti. Uniti i duplicati (`bsd`/`freebsd`/`openbsd` → `freebsd`), rimossi quelli inutili (`wallpaper`, `skating`, `siamese`), e aggiunti nuovi tag significativi (`iot`, `reverse-engineering`, `ai-generated`).

## Il setup

Per i curiosi, ecco come funziona il tutto:

- **Claude Code** gira su un Raspberry Pi 5 (`nowhere`) via SSH
- **Chrome** gira sul mio MacBook con il remote debugging abilitato (`--remote-debugging-port=9222`)
- Un **SSH reverse tunnel** (`ssh -R 9222:localhost:9222`) permette a Claude sul Pi di parlare con Chrome sul mio laptop
- Claude usa il **Chrome DevTools MCP** per navigare, fare screenshot, ispezionare e valutare script nel browser
- Il blog si builda su un **server FreeBSD** (`m42`) — Claude fa SSH lì per fare pull, build e deploy
- **Staging** su `vjt.sindro.me`, **prod** su `sindro.me` — entrambi con un semplice `git pull && ./build.sh`

È una macchina di Rube Goldberg meravigliosamente ridicola fatta di tunnel SSH, protocolli MCP e submodule git. Ma funziona, e funziona *veloce*.

## Cosa ho imparato

Lo sviluppo assistito dall'AI non riguarda il far scrivere codice all'AI al posto tuo. Riguarda l'avere un pair programmer straordinariamente capace che non si stanca mai, non perde mai il filo (be', quasi mai), e riesce a eseguire a una velocità che ti permette di concentrarti interamente su *cosa* vuoi, non su *come* arrivarci.

Il ciclo di iterazione continua — proposta, brainstorming, POC, implementazione completa, review, bugfix — si sentiva naturale. Come avere una conversazione che per caso produce software funzionante. La mia creatività era il collo di bottiglia, non l'esecuzione.

Due giorni. 69 traduzioni. Redesign completo del layout. Easter egg con la sequenza di boot. Pulizia dei tag. Questo articolo. E Claude ha pure fatto da solo gli screenshot per il post che stai leggendo.

Feeling bold on the internet, indeed.
