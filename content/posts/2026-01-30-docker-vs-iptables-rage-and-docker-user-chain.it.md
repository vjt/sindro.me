---
title: "Docker vs. iptables: una storia di rabbia e la chain DOCKER-USER"
date: 2026-01-30T00:00:00+01:00
tags: [ai-generated, linux, networking, sysadmin, home-assistant]
categories: ["System Administration", "Rants", "Open Source"]
description: "La gestione di iptables da parte di Docker è un incubo per i setup ibridi host/VM. Ecco perché iptables-save fallisce, e il modo corretto e deterministico per risolvere."
---

Siamo nel 2026, e stiamo ancora lottando con l'arroganza assoluta di Docker riguardo al networking Linux.

Ecco lo scenario: faccio girare un host ibrido. Da un lato, ho una macchina virtuale KVM che fa girare **Home Assistant** (perché ho bisogno del controllo completo del SO e della [cifratura del disco](https://sindro.me/posts/2026-01-20-raspberry-pi-luks-encrypted-root/)).
Dall'altro, ho la solita lista di container Docker -- **NUT** per monitorare il mio UPS Lakeview (Vultech) di merda e **Technitium** per DNS e DHCP -- in esecuzione direttamente sull'host.

Sembra semplice. Dovrebbe essere semplice.

Ma nel momento in cui ho installato Docker, la comunicazione con la mia VM Home Assistant è morta. Semplicemente cessata di esistere.

## Il problema: Docker è un dittatore

Docker, per default, tratta le tue regole `iptables` come se fossero semplici suggerimenti. Quando il demone si avvia, sostanzialmente sovrascrive la chain `FORWARD`, inserisce la sua logica, e imposta policy che isolano efficacemente qualsiasi cosa non sia un container gestito da Docker stesso.

Se hai un'interfaccia bridge per una VM (come `br0` o `virbr0`), le regole di Docker spesso finiscono per droppare i pacchetti destinati a quella VM perché non corrispondono alla sua logica interna per il traffico dei container.

### La soluzione ingenua (e perché fallisce)

La mia prima reazione -- come qualsiasi sysadmin che fa questo lavoro dai primi anni 2000 -- è stata sistemare le regole a mano e poi eseguire:

```bash
iptables-save > /etc/iptables/rules.v4
```

Questa è una trappola!

![Trap GIF](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHI5MzZoYzVwdGluYmNnMXBpYmJ2M2Y4cHB1OGVhaGlxdXRpZHpqOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ornka9rAaKRA2Rkac/giphy.gif)

Se usi `iptables-persistent` (o `netfilter-persistent`) con Docker, stai entrando in un mondo di dolore per due motivi:

* **Persistenza della spazzatura**: quando esegui `iptables-save` mentre Docker è in esecuzione, non stai salvando solo le tue regole custom. Stai salvando lo stato dinamico di Docker -- incluse le regole per le interfacce `veth` effimere e il masquerading dinamico degli IP. Quando riavvii, `iptables-restore` prova ad applicare regole a interfacce che *non esistono ancora*, causando il fallimento del restore o lasciando il firewall in uno stato inconsistente.

* **La race condition**: `netfilter-persistent` di solito si carica presto nel processo di boot. Docker parte dopo. Quando il demone Docker si avvia, rileva che le chain non corrispondono alle sue aspettative e le svuota, cancellando di fatto i tuoi permessi preparati con cura.

È un casino di comportamento non deterministico.

## Il modo corretto: `DOCKER-USER`

Nelle profondità [della documentazione](https://docs.docker.com/engine/network/firewall-iptables/), Docker ammette che se vuoi inserire regole custom, devi usare la chain `DOCKER-USER`. Questa chain viene inserita prima delle regole di Docker in cima alla chain `FORWARD`.

Tuttavia, Docker non fornisce alcun meccanismo nativo per gestire le regole in questa chain in modo persistente. Si aspettano che te la cavi tu. Se le metti in `rc.local`, stai tirando a indovinare il timing. Se usi `iptables-save`, vedi la race condition sopra.

## Grattarsi il prurito: `docker-user-firewall`

Mi serviva una soluzione che fosse:

1. **Pulita**: niente script shell raffazzonati sparsi in `/etc`.
2. **Atomica**: deve svuotare la chain `DOCKER-USER` e ricaricarla da zero ogni volta.
3. **Ordinata**: deve girare rigorosamente *dopo* che Docker ha finito l'inizializzazione.

Dato che non esisteva, l'ho costruita.

Vi presento [docker-user-firewall](https://github.com/vjt/docker-user-firewall).

È un semplice pacchetto Debian senza fronzoli che installa un servizio Systemd One-Shot.

Utilizza `After=docker.service` e `Requires=docker.service` per garantire l'ordine perfetto.

### Come funziona

La logica è brutalmente semplice. Quando il servizio si avvia (dopo il boot di Docker), svuota la chain specifica e inietta le tue regole da un file di configurazione pulito:

```
# Flush the chain to remove previous states or Docker defaults
iptables -F DOCKER-USER

# Load rules from /etc/docker-user-firewall/rules.conf
# ... (loop through config) ...

# Return control to Docker logic for anything not explicitly handled
iptables -A DOCKER-USER -j RETURN
```

### Configurazione

La configurazione vive in `/etc/docker/user-firewall.conf`. Definisci gli argomenti, e lo strumento si occupa del wrapping del comando iptables.

Per risolvere la visibilità della mia Home Assistant, la mia config è più o meno così:

```
# Allow traffic to pass through to the VM bridge
-i br-lan -j ACCEPT
-i br-lan -j ACCEPT
```

## Conclusione

È frustrante che nel 2026 dobbiamo ancora scrivere wrapper per la persistenza base del networking, ma è così. Se stai facendo girare un setup ibrido e Docker ti sta mangiando i pacchetti, smettila di lottare con `iptables-save` e imponi l'ordine corretto.

Prendi il sorgente qui: https://github.com/vjt/docker-user-firewall
