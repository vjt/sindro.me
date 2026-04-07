---
title: "Come ho rimpiazzato l'app Verisure con Home Assistant"
date: 2026-04-04
tags: [reverse-engineering, iot, home-assistant, python, security]
categories: [development]
description: "L'app Verisure fa schifo: lenta, piena di pubblicità, zero automazioni. L'ho rimpiazzata con un componente custom per Home Assistant."
---

L'app Verisure fa schifo. Lì, l'ho detto.

Non che l'allarme funzioni male — il pannello SDVECU è solido, i sensori
sono affidabili, l'installazione è professionale. Ma l'app. Dio santo,
l'app.

## Il problema

Apri l'app per controllare lo stato dell'allarme e ti accoglie una **pubblicità
di Verisure stessa**. Io pago fior di quattrini per il servizio e loro mi
piazzano le ads _dentro_ l'app. È il 2026 e un'azienda di sicurezza mi fa
vedere banner pubblicitari quando provo a verificare se casa mia è protetta.

Ma le ads sono il meno. I veri problemi sono:

- **Routine cieche.** Sì, l'app ha le "routine" — attiva a
  mezzanotte, disattiva alle 7. Ma non sanno dove sei. Mezzanotte
  e sei ancora in giardino? L'allarme si attiva e i sensori scattano.
  Finestra aperta? Il pannello annuncia che non riesce ad attivare,
  ma se non lo senti l'allarme resta spento. Vai in vacanza e
  dimentichi di disabilitare la routine di disattivazione mattutina?
  Allarme spento con la casa vuota. E le modifiche alle routine
  impiegano _20 minuti a propagarsi_ — "o il giorno dopo". Nel 2026.
- **Zero presenza.** L'app non sa dove sei. Non sa chi è in casa.
  Non sa se la donna delle pulizie è andata via. Nessuna automazione
  basata sulla posizione.
- **Una telecamera alla volta.** Vuoi vedere tutte le camere? Tocca,
  aspetta, torna indietro, tocca la prossima, aspetta. Nessuna vista
  d'insieme. Nessun "cattura tutto".
- **Lentezza biblica.** Richiedi un'immagine, aspetti, aspetti, forse
  arriva. A volte ricarichi l'app e riprovi. Nel 2026.
- **Nessuno storage permanente.** Le immagini catturate spariscono. Non
  c'è uno storico consultabile.
- **Nessun timestamp sulle immagini.** Catturi una foto e non sai
  _quando_ è stata scattata né _da quale camera_. Devi ricordartelo tu.
  Per un sistema di sicurezza è imbarazzante.
- **Notifiche generiche.** Una notifica uguale per tutti. Niente
  notifiche actionable, niente notifiche critiche che bypassano il
  "Non Disturbare".

Quello che volevo: il mio allarme, integrato nella mia domotica, con
automazioni intelligenti, notifiche per tutti i residenti, e una
dashboard che mostra _tutto_ in un colpo d'occhio. Senza pubblicità.

## La soluzione: Home Assistant + un componente custom

Ho scritto [ha-verisure-italy](https://github.com/vjt/ha-verisure-italy),
un componente custom per Home Assistant che parla direttamente con le
API GraphQL di Verisure Italia (`customers.verisure.it`). Rimpiazza
completamente l'app per il controllo dell'allarme e il monitoraggio
delle telecamere.

### Cosa fa

- **Controllo allarme** — attiva parziale+perimetrale ("a casa"),
  totale+perimetrale ("fuori casa"), disattiva
- **Force arm** — quando l'allarme non si attiva perché una finestra è
  aperta, un tap per forzare. O meglio: un'automazione che forza
  automaticamente quando esci di casa
- **Telecamere** — scoperte automaticamente, cattura parallela con
  overlay timestamp, pulsanti per camera singola e "cattura tutte"
- **Dashboard auto-generata** — pannello allarme, griglia telecamere,
  pulsanti di cattura, tutto populato automaticamente nella sidebar di HA

![La dashboard Verisure auto-generata](/posts/2026-04-04-verisure-italy-home-assistant/dashboard.png)

### Le automazioni che l'app non può fare

Ecco cosa gira in produzione a casa mia:

**Attiva quando l'ultimo esce.** Un sensore binario traccia chi è in
casa (GPS + WiFi via [OpenWrt presence detection](https://github.com/vjt/openwrt-ha-presence)).
Quando tutti sono fuori, l'allarme si attiva automaticamente.

**Rete di sicurezza.** Ogni 5 minuti, se nessuno è in casa e l'allarme
è spento, lo riattiva e manda una notifica. Perché la vita è complicata
e i sensori di presenza ogni tanto sbagliano.

**Force-arm automatico.** Se l'allarme non si attiva perché una finestra
è aperta, l'integrazione rileva il blocco, notifica quali zone sono
aperte, e forza l'attivazione. Un allarme attivo con eccezioni è
meglio di un allarme spento. Le routine Verisure? Il pannello annuncia il
fallimento — ma se non sei lì ad ascoltarlo, l'allarme resta spento.

![Force arm: allarme bloccato, un tap per forzare](/posts/2026-04-04-verisure-italy-home-assistant/force-arm.png)

**Arma notturno intelligente.** Non "attiva a mezzanotte" come le
routine Verisure. Attiva tra mezzanotte e le 7 solo quando rileva che
entrambi i residenti sono in casa e a riposo. Sei in giardino alle 2
di notte? L'allarme aspetta.

**Disattiva mattutino sicuro.** Si disattiva alle 7, ma _solo se
qualcuno è in casa_. Vai al mare e dimentichi? L'allarme resta attivo.
Con le routine Verisure devi ricordarti di disabilitarle — e se ti
dimentichi, aspetti 20 minuti (o un giorno) per la propagazione.

**Notifica actionable all'arrivo.** Arrivi a casa con l'allarme
attivo? Una notifica con il pulsante "Disattiva" direttamente sul
telefono. Si auto-dismette se l'allarme viene disattivato con altri
mezzi.

**Notifica di stato critica.** Se l'allarme riporta uno stato
sconosciuto, notifica critica che bypassa il "Non Disturbare" di iOS.
Questo è software di sicurezza — nessun errore può passare in
silenzio.

E tutto questo funziona via **CarPlay** — vedo lo stato dell'allarme
e ricevo le notifiche direttamente in macchina.

## Design tecnico

Questo non è un progetto weekend. È software di sicurezza: un
comportamento sbagliato = allarme disattivato = il ladro entra.
Ogni decisione ottimizza per la correttezza, non per la comodità.

### Architettura a due livelli

- **Client API** (`verisure-italy` su [PyPI](https://pypi.org/project/verisure-italy/)) —
  client GraphQL typed, modelli Pydantic per ogni request/response,
  nessun `dict`, nessun `Any`. Se la risposta non matcha: `ValidationError`.
  Crash rumoroso al boundary, tipi garantiti all'interno.
- **Integrazione HA** (`custom_components/verisure_italy/`) — alarm
  control panel, camera, bottoni, config flow con 2FA, dashboard
  auto-generata. Il nostro codice, pulito, specifico per l'Italia.

### Macchina a stati

Il pannello Verisure ha 6 stati protocollari su due assi:
interiore (OFF/PARZIALE/TOTALE) × perimetrale (OFF/ON). La macchina
a stati li enumera tutti. Uno stato sconosciuto è un errore, mai un
default. Il codice crasha rumorosamente e notifica un umano.

### Principi ingegneristici

- **Fail-secure.** Stato sconosciuto = ERRORE, mai "probabilmente
  disattivato". Timeout = mantieni lo stato precedente e notifica.
- **Parse al boundary.** JSON dall'API → modelli Pydantic al livello
  HTTP. Se il parsing fallisce, esplode lì. Dentro il codebase, i
  tipi garantiscono la correttezza.
- **Nessun default silenzioso.** Niente `.get()` con fallback su dati
  che devono esistere. Niente `= None` che nascondono degradazioni.
- **Type system rigoroso.** Pyright in strict mode, 0 errori, 14
  secondi. 165 test. Ruff per linting. `scripts/check.sh` lancia
  tutto in una botta.

### Iterazioni, non big bang

Il progetto è nato come POC: "posso parlare con le API Verisure da
Python?" Sì. Poi: "posso integrarlo in HA?" Sì. Da lì, iterazione
dopo iterazione:

1. POC funzionante
2. Integrazione HA base (arm/disarm/stato)
3. Telecamere con cattura parallela
4. Config flow con 2FA
5. Dashboard auto-generata
6. Force-arm con gestione eccezioni
7. **v0.7.0** — hardening da code review: 3 CRITICAL e 7 HIGH risolti
8. **v0.8.0** — seconda review: tutti gli HIGH e MEDIUM risolti, pyright
   clean, 165 test, boundary puliti, thread safety

Ad ogni iterazione, code review con 8 agenti paralleli (4 line-level +
4 architettura) che passano al setaccio ogni file. Niente viene
lasciato indietro.

## Installazione

L'integrazione si installa tramite [HACS](https://hacs.xyz/) (Home
Assistant Community Store) — il gestore di componenti custom della
community. Se non l'hai ancora installato,
[segui la guida ufficiale](https://www.hacs.xyz/docs/use/download/download/).

Una volta che HACS è attivo:

[![Aggiungi a HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=vjt&repository=ha-verisure-italy&category=integration)

Oppure manualmente via HACS → Custom repositories →
`https://github.com/vjt/ha-verisure-italy` → Integration.

Il client API si installa automaticamente da PyPI. Il config flow
guida il setup con supporto 2FA completo. La dashboard si genera
da sola.

> **Perché non è nel catalogo ufficiale di HA?** L'integrazione è
> giovane — la sto mettendo alla prova con i primi utenti prima di
> sottoporla per l'inclusione ufficiale. HACS è il canale giusto
> per questa fase.

## Cosa manca

- **Storage permanente delle immagini.** I building block ci sono
  (le immagini catturate sono bytes in memoria), manca il layer di
  persistenza.
- **Timeline degli eventi.** L'API espone gli eventi, ma non li
  consumiamo ancora.
- **Supporto multi-installazione.** Il codice gestisce
  un'installazione. Il guard contro i duplicati c'è, ma il multi-install
  è da implementare.

## Conclusione

L'app Verisure è una scatola chiusa con le pubblicità sopra.
Home Assistant è una piattaforma aperta dove ogni pezzo è
programmabile. Tra le due non c'è partita.

Il codice è su [GitHub](https://github.com/vjt/ha-verisure-italy),
il client API su [PyPI](https://pypi.org/project/verisure-italy/),
le automazioni d'esempio nella
[documentazione](https://github.com/vjt/ha-verisure-italy/blob/master/docs/automations.md).

Happy hacking!
