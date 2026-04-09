---
title: "Taking Back Your Network Stack from Cisco AnyConnect"
date: 2014-04-20
tags: [networking, macos, security, open-source]
image: cover.jpg
featuredImage: cover.jpg
description: "Cisco AnyConnect hijacks your entire network stack. Here is how I replaced it with OpenConnect, split tunneling, and split DNS on macOS."
---

{{< retrospective year="2026" >}}
Twelve years later, AnyConnect rebranded to "Cisco Secure Client" but the philosophy is identical: total control, zero transparency. The industry has largely moved on — Tailscale, WireGuard, and Cloudflare WARP have made split tunneling the default. macOS replaced kexts with the NetworkExtension framework, and `scutil` tricks require more care. But OpenConnect still works, the protocol hasn't changed, and the [scripts are still on GitHub](https://github.com/vjt/openconnect-macos).
{{< /retrospective >}}

Cisco AnyConnect is the kind of software that makes you question whether the
people who wrote it have ever actually used a computer outside of a corporate
cubicle. You install it, you connect to the VPN, and suddenly *all* your traffic
is being funneled through your employer's network. Your personal browsing, your
Spotify, your SSH sessions to your own servers -- everything. And there is no
setting to change it. It is by design. The sysadmins at HQ decided what is best
for you, and what is best for you is a full tunnel with zero user control.

<!--more-->

## The problem

AnyConnect installs a kernel extension (yes, a kext) and a persistent daemon
that takes ownership of your routing table the moment you connect. It sets
itself as the default gateway for *everything*, ignoring any routes you had
before. It also hijacks DNS, pointing all resolution through the corporate
servers. You cannot even resolve your home NAS by hostname anymore.

The official Cisco answer to "can I do split tunneling?" is "ask your
administrator." Great.

## The fix: OpenConnect + split tunnel + split DNS

[OpenConnect](https://www.infradead.org/openconnect/) is an open-source client
that speaks the AnyConnect protocol. It connects to the same VPN gateway, but
it gives *you* control over what happens after the tunnel is up.

I wrote a set of scripts --
[openconnect-macos](https://github.com/vjt/openconnect-macos) -- that replace
the entire AnyConnect client with three files:

- **`vpn.conf`** -- OpenConnect connection config, plus a list of
  `INTERNAL_ROUTES` that should go through the VPN:

  ```bash
  INTERNAL_ROUTES="10.0.0.0/8 172.16.0.0/12 192.168.0.0/16"
  ```

- **`net.macos.sh`** -- a custom `vpnc-script` that only routes the specified
  subnets through the tunnel, and sets up split DNS via macOS `scutil`:

  ```bash
  # Register corporate domains for split DNS resolution
  scutil <<EOF
  d.init
  d.add SupplementalMatchDomains * corp.example.com internal.example.com
  d.add ServerAddresses * 10.0.0.53
  set State:/Network/Service/org.openconnect/DNS
  EOF
  ```

  Only queries for `corp.example.com` go to the corporate DNS. Everything else
  hits your normal resolver. No more leaking your browsing habits to the
  corporate proxy.

- **`vpn.sh`** -- the runner script, configured for passwordless `sudo` via a
  sudoers entry.

The result: corporate resources are reachable, everything else takes its normal
path. Your Spotify keeps streaming. Your SSH sessions stay alive. Your packets,
your rules.

It works on Linux too, with a slightly different network script.

**Fair warning:** employers force full-tunnel VPNs for a reason — it's part of their security posture. By bypassing it, you may be violating your company's security policy, your employment contract, or both. You are responsible for your own actions. I am absolutely, categorically not responsible if you get fired, audited, or escorted out of the building by IT security. You've been warned.

The code: [github.com/vjt/openconnect-macos](https://github.com/vjt/openconnect-macos)
