---
title: "Riprendere il controllo della rete da Cisco AnyConnect"
date: 2014-04-20
tags: [networking, macos, security, open-source]
image: cover.jpg
featuredImage: cover.jpg
description: "Cisco AnyConnect sequestra l'intero stack di rete. Ecco come l'ho sostituito con OpenConnect, split tunneling e split DNS su macOS."
---

{{< retrospective year="2026" >}}
Dodici anni dopo, AnyConnect si è rinominato "Cisco Secure Client" ma la filosofia è identica: controllo totale, trasparenza zero. L'industria è andata avanti — Tailscale, WireGuard e Cloudflare WARP hanno reso lo split tunneling il default. macOS ha rimpiazzato i kext con il framework NetworkExtension, e i trucchi con `scutil` richiedono più attenzione. Ma OpenConnect funziona ancora, il protocollo non è cambiato, e gli [script sono ancora su GitHub](https://github.com/vjt/openconnect-macos).
{{< /retrospective >}}

Cisco AnyConnect è il tipo di software che ti fa dubitare che chi l'ha scritto
abbia mai usato un computer fuori da un cubicolo aziendale. Lo installi, ti
connetti alla VPN, e improvvisamente *tutto* il tuo traffico viene incanalato
attraverso la rete del datore di lavoro. La navigazione personale, Spotify, le
sessioni SSH verso i tuoi server -- tutto. E non c'è un'impostazione per
cambiarlo. È by design. I sysadmin della sede centrale hanno deciso cosa è
meglio per te, e cosa è meglio per te è un tunnel completo con zero controllo
utente.

<!--more-->

## Il problema

AnyConnect installa una kernel extension (sì, un kext) e un demone persistente
che si impossessa della tua tabella di routing nel momento in cui ti connetti.
Si imposta come default gateway per *tutto*, ignorando qualsiasi rotta
preesistente. Sequestra anche il DNS, puntando tutta la risoluzione attraverso i
server aziendali. Non riesci nemmeno più a risolvere il tuo NAS di casa per
hostname.

La risposta ufficiale Cisco a "posso fare split tunneling?" è "chiedi al tuo
amministratore." Fantastico.

## La soluzione: OpenConnect + split tunnel + split DNS

[OpenConnect](https://www.infradead.org/openconnect/) è un client open-source
che parla il protocollo AnyConnect. Si connette allo stesso gateway VPN, ma dà
a *te* il controllo su cosa succede dopo che il tunnel è attivo.

Ho scritto un set di script --
[openconnect-macos](https://github.com/vjt/openconnect-macos) -- che
sostituiscono l'intero client AnyConnect con tre file:

- **`vpn.conf`** -- configurazione della connessione OpenConnect, più una lista
  di `INTERNAL_ROUTES` che devono passare per la VPN:

  ```bash
  INTERNAL_ROUTES="10.0.0.0/8 172.16.0.0/12 192.168.0.0/16"
  ```

- **`net.macos.sh`** -- un `vpnc-script` custom che instrada solo le subnet
  specificate attraverso il tunnel, e configura lo split DNS tramite `scutil` di
  macOS:

  ```bash
  # Registra i domini aziendali per la risoluzione DNS separata
  scutil <<EOF
  d.init
  d.add SupplementalMatchDomains * corp.example.com internal.example.com
  d.add ServerAddresses * 10.0.0.53
  set State:/Network/Service/org.openconnect/DNS
  EOF
  ```

  Solo le query per `corp.example.com` vanno al DNS aziendale. Tutto il resto
  va al tuo resolver normale. Niente più browsing leakato al proxy aziendale.

- **`vpn.sh`** -- lo script runner, configurato per `sudo` senza password
  tramite una entry in sudoers.

Il risultato: le risorse aziendali sono raggiungibili, tutto il resto prende il
suo percorso normale. Spotify continua a streammare. Le sessioni SSH restano
attive. I tuoi pacchetti, le tue regole.

Funziona anche su Linux, con uno script di rete leggermente diverso.

**Avvertenza:** i datori di lavoro impongono VPN full-tunnel per un motivo — fa parte della loro postura di sicurezza. Bypassandola, potresti violare la policy di sicurezza aziendale, il tuo contratto di lavoro, o entrambi. Sei responsabile delle tue azioni. Io non sono assolutamente, categoricamente responsabile se ti licenziano, ti auditano, o ti scortano fuori dall'edificio la sicurezza IT. Sei stato avvisato.

Il codice: [github.com/vjt/openconnect-macos](https://github.com/vjt/openconnect-macos)
