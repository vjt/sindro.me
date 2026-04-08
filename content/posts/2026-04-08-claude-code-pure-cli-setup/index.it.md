---
title: "Il mio setup Claude Code: pura CLI, puro Unix, zero IDE"
date: 2026-04-08
tags: [ai-generated, projects, sysadmin, cli]
description: "Come faccio girare Claude Code su un Raspberry Pi dentro tmux, faccio roaming delle sessioni dal telefono al laptop via SSH, e ho fatto 5000 commit in 30 giorni senza toccare un IDE."
---

![Sto scrivendo questo stesso post dal telefono via SSH — screenshot di Termius su iOS connesso a Claude Code dentro tmux](/posts/2026-04-08-claude-code-pure-cli-setup/phone-screenshot.png)

Questo sono io che scrivo questo post. Dal telefono. Via SSH. Dalla vasca da bagno, probabilmente.

Claude Code è un tool CLI. Gira in un terminale. E tanto mi bastava.

<!--more-->

## Il setup

Ho un [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) con Debian Trixie a casa. Si chiama `nowhere` (lunga storia). Claude Code gira lì, dentro [tmux](https://github.com/tmux/tmux), 24/7. Lo raggiungo da qualsiasi dispositivo — telefono, tablet, laptop — con un SSH e un reattach:

```
ssh nowhere
tmux -u at
```

Tutto qui. Due comandi e sono esattamente dove ho lasciato. Il flag `-u` abilita il supporto Unicode (emoji nelle status line, caratteri box-drawing), e `at` è abbreviazione di `attach -t 0`. La sessione persiste attraverso disconnessioni, riavvii dei dispositivi client, cambi di rete — tutto. Posso iniziare un task sul laptop, continuarlo dal telefono mentre porto fuori il cane, e finirlo sul tablet dal divano.

Roaming totale delle sessioni tra dispositivi. Zero stato perso. Mai.

## La filosofia Unix, viva e vegeta

Ecco lo stack, dal basso verso l'alto:

- **Debian Trixie** (aarch64) — perché ho un tatuaggio Debian sul braccio e a questo punto è un impegno
- **Unit systemd utente** per `ssh-agent` — parte al login, attivata via socket, `SSH_AUTH_SOCK` prevedibile a `/run/user/1000/openssh_agent`
- **tmux** — multiplexer, persistenza della sessione, scrollback, copia-incolla, gestione finestre
- **Claude Code** — l'AI che fa il lavoro vero
- **SSH** — il trasporto universale

Niente Docker. Niente Kubernetes. Niente tunnel remoti di VS Code. Niente IDE cloud. Niente Electron. Solo Unix.

### Il trucco dell'SSH agent

L'agent è gestito da systemd e il path del socket è hardcodato in `.bashrc`:

```bash
export SSH_AUTH_SOCK="${XDG_RUNTIME_DIR}/openssh_agent"
```

Questo significa che Claude Code — che gira dentro tmux, dentro una shell — ha automaticamente accesso alle mie chiavi SSH. Può fare `git push`, `ssh` sui miei server, deploy su staging e produzione, tutto senza agent forwarding. Le chiavi stanno sul Pi, l'agent è sempre in esecuzione, e ogni shell (inclusa quella di Claude) eredita il path del socket.

Nessun flag `-A` necessario dal lato client. Nessun rischio di sicurezza da agent forwarding. Il Pi _è_ l'agent.

### tmux: il vero IDE

Il mio tmux usa `Ctrl-F` come prefix key (scusa, `find`, sei morto per me) e tengo finestre multiple con etichette descrittive:

```
0:sysadm  1:gastone  2:sindrome  3:gastone-logs
```

Ogni finestra è un progetto. Ogni progetto ha Claude Code in esecuzione. Posso saltare tra una e l'altra con `^F 0`, `^F 1`, ecc. Pane split per log, htop, o una shell parallela quando serve.

Le killer feature per questo workflow:

- **Scrollback** — `Shift-PageUp` entra in copy mode. Posso scorrere migliaia di righe di output di Claude, log del terminale, output dei build. `history-limit` settato a 10.000 righe.
- **Copia-incolla** — il copy mode nativo di tmux con keybinding vi. Seleziona, yank, paste. Nessun mouse necessario (anche se il mouse mode è attivo per lo scroll pigro occasionale).
- **Sync dei pane** — `^F Ctrl-Y` attiva/disattiva l'input sincronizzato su tutti i pane. Utile per mandare lo stesso comando su viste split.

### WireGuard: mobilità seamless

Ho una VPN WireGuard configurata come on-demand su tutti i miei dispositivi. Quando sono sul WiFi di casa, il traffico va diretto sulla LAN. Quando esco, WireGuard si attiva automaticamente e mi tunnella a casa. La transizione è invisibile — la connessione SSH non cade nemmeno.

Il mio `~/.ssh/config` sul laptop e le connessioni salvate in Termius usano entrambi l'IP LAN locale del Pi. WireGuard gestisce il routing indipendentemente da dove mi trovo fisicamente. Stesso IP, stessa connessione, che sia in salotto o al bar.

## Il setup da telefono

Su iOS uso [Termius](https://termius.com/) (versione free). Connessione salvata a `nowhere`, chiave SSH importata, fatto. Il trucco fondamentale: ho mappato `Ctrl-F` (il mio prefix tmux) su un pulsante sopra la tastiera. Questo mi dà il controllo completo di tmux dal telefono — cambiare finestre, splittare pane, entrare in copy mode, tutto.

Il telefono è sorprendentemente usabile per questo workflow. Non _scrivo_ codice da lì (quello lo fa Claude), ma posso rivedere diff, approvare tool call, leggere output dei build, controllare staging, e dare istruzioni a Claude. Che è il 90% di quello che faccio comunque.

## I risultati

Negli ultimi 30 giorni, ho fatto più di **5.000 commit** su una dozzina di progetti — tutto da questo setup:

- [Rifatto completamente questo blog](/it/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/) — tradotti 69 post, ridisegnato il layout, aggiunto l'Easter egg della sequenza di boot. Nessun IDE, nessun Figma, nessun tool di design. Solo Claude Code e il live preview di [Superpowers](https://github.com/anthropics/claude-code) per il lavoro visuale.
- Scritto un [componente custom per Home Assistant](/it/posts/2026-04-04-verisure-italy-home-assistant/) per Verisure Italy — reverse-engineered le loro API GraphQL, scritto l'intero componente Python, pubblicato su PyPI.
- Creato [WiFi Dethrash](/it/posts/2026-04-03-wifi-dethrash-openwrt-mesh-analyzer/), un analizzatore di reti mesh per OpenWrt.
- Scritto un [sistema di rilevamento presenza WiFi](/it/posts/2026-02-15-wifi-presence-detection-home-assistant/) per Home Assistant.
- Costruito [tool per modem 5G](/it/posts/2026-01-31-quectel-5g-modem-tools-for-openwrt/) per OpenWrt.
- [Riprocessato due anni di log](/it/posts/2026-04-08-backfilling-two-years-of-logs/) attraverso una pipeline di enrichment completa.

Ogni singolo progetto fatto dal terminale. CSS, Python, Go, Lua, shell script, template Hugo, config nginx, unit systemd, codice di networking kernel-adjacent. L'intero stack, dall'alto al basso, da riga di comando.

## Perché funziona

L'intuizione è che Claude Code non ha bisogno di un IDE perché _è_ l'IDE. Legge file, li modifica, lancia test, controlla l'output dei build, itera. Il terminale è il suo habitat naturale. Aggiungere un layer grafico sopra non aiuta — si mette in mezzo.

E tmux è il compagno perfetto perché ti dà tutto quello che il concetto di "workspace" di un IDE moderno offre — sessioni persistenti, contesti multipli, cronologia ricercabile, layout dei pane — senza nessun bloat.

Ho iniziato a programmare su un 486 negli anni '90 con Turbo Pascal e un terminale 80x25. Poi l'industria ha speso 25 anni a convincermi che avevo bisogno di GUI, mouse, IDE, debugger visuali, tool di deploy point-and-click. Adesso l'AI mi riporta a un terminale, una tastiera, e la capacità di descrivere quello che voglio in linguaggio naturale.

Ho chiuso il cerchio, e non sono mai stato più felice a giocare con i computer.
