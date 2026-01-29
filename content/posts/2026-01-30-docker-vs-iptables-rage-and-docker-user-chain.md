---
title: "Docker vs. iptables: A Tale of Rage and the DOCKER-USER Chain"
date: 2026-01-30T00:00:00+01:00
tags: ["docker", "networking", "iptables", "linux", "sysadmin", "home-assistant"]
categories: ["System Administration", "Rants", "Open Source"]
description: "Docker's handling of iptables is a nightmare for hybrid host/VM setups. Here is why iptables-save fails, and the correct, deterministic way to fix it."
---

It is 2026, and we are still fighting with Docker’s absolute arrogance regarding Linux networking.

Here is the scenario: I run a hybrid host. On one side, I have a KVM virtual machine running **Home Assistant** (because I need full OS control and [full-disk encryption](https://sindro.me/posts/2026-01-20-raspberry-pi-luks-encrypted-root/)).
On the other, I have the usual suspect list of Docker containers — **NUT** for monitoring my shitty Lakeview (Vultech) UPS and **Technitium** for DNS and DHCP—running on the bare metal host.

It sounds simple. It should be simple.

But the moment I installed Docker, communication with my Home Assistant VM died. Just ceased to exist.

## The Problem: Docker is a Dictator

Docker, by default, treats your `iptables` rules like they are merely suggestions. When the daemon starts, it essentially clobbers the `FORWARD` chain, inserts its own logic, and sets policies that effectively isolate anything that isn't a container managed by itself.

If you have a bridge interface for a VM (like `br0` or `virbr0`), Docker’s rules often end up dropping packets destined for that VM because they don't match its internal logic for container traffic.

### The Naive Fix (and why it fails)

My first reaction—like any sysadmin who has been doing this since the early 2000s—was to fix the rules manually and then run:

```bash
iptables-save > /etc/iptables/rules.v4
```

This is a trap!

![Trap GIF](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHI5MzZoYzVwdGluYmNnMXBpYmJ2M2Y4cHB1OGVhaGlxdXRpZHpqOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ornka9rAaKRA2Rkac/giphy.gif)

If you use `iptables-persistent` (or `netfilter-persistent`) with Docker, you are entering a world of pain for two reasons:

* **Garbage Persistence**: When you run `iptables-save` while Docker is running, you aren't just saving your custom rules. You are saving Docker’s dynamic state—including rules for ephemeral `veth` interfaces and dynamic IP masquerading. When you reboot, `iptables-restore` tries to apply rules to interfaces that *do not exist yet*, causing the restore to fail or leave the firewall in an inconsistent state.

* The Race Condition: `netfilter-persistent` usually loads early in the boot process. Docker starts later. When the Docker daemon starts, it detects that the chains don't match its expectations and flushes them, effectively wiping out your carefully crafted permissions.

It is a mess of non-deterministic behavior.

## The Correct Way: `DOCKER-USER`

Deep [in the documentation](https://docs.docker.com/engine/network/firewall-iptables/), Docker admits that if you want to insert custom rules, you must use the `DOCKER-USER` chain. This chain is inserted before Docker’s rules at the top of the `FORWARD` chain.

However, Docker provides no native mechanism to manage rules in this chain persistently. They expect you to handle it. If you put them in `rc.local`, you're guessing the timing. If you use `iptables-save`, see the race condition above.

## Scratching the Itch: `docker-user-firewall`

I needed a solution that was:

1. **Clean**: No hacky shell scripts scattered in `/etc`.
2. **Atomic**: It must wipe the `DOCKER-USER` chain and reload it fresh every time.
3. **Ordered**: It must run strictly *after* Docker has finished initializing.

Since it didn't exist, I built it.

Introducing [docker-user-firewall](https://github.com/vjt/docker-user-firewall).

It is a simple, no-nonsense Debian package that installs a Systemd One-Shot service.

It utilizes `After=docker.service` and `Requires=docker.service` to ensure perfect ordering.

### How it works

The logic is brutally simple. When the service starts (post-Docker boot), it flushes the specific chain and injects your rules from a clean config file:

```
# Flush the chain to remove previous states or Docker defaults
iptables -F DOCKER-USER

# Load rules from /etc/docker-user-firewall/rules.conf
# ... (loop through config) ...

# Return control to Docker logic for anything not explicitly handled
iptables -A DOCKER-USER -j RETURN
```

### Configuration

The configuration lives in `/etc/docker/user-firewall.conf`. You define the arguments, and the tool handles the iptables command wrapping.

To fix my Home Assistant visibility, my config looks something like this:

```
# Allow traffic to pass through to the VM bridge
-i br-lan -j ACCEPT
-i br-lan -j ACCEPT
```

## Conclusion

It is frustrating that we still need to write wrapper tools for basic network persistence in 2026, but here we are. If you are running a hybrid setup and Docker is eating your packets, stop fighting `iptables-save` and enforce the correct ordering.

Grab the source here: https://github.com/vjt/docker-user-firewall
