---
title: 'pfasciilogd: link pf and fail2ban'
date: 2023-08-17
tags: [bsd, freebsd, sysadmin, security]
categories: [development]
---

## TL;DR

FreeBSD: How to block port scanners from enumerating open ports on your
server, by using fail2ban and an ASCII representation of `pf` logs.

## Preface

I use [`fail2ban`](https://fail2ban.org/) to keep away attackers and bots alike
that attempt to scan my websites or brute force my mailboxes. Fail2ban works by
scanning log files for specific patterns and keeping a count of matches per IP,
and allows the systems administrator to define what to do when that count
exceeds a defined threshold.

The patterns are indicative of malicious activity, such as attempting to guess
a mailbox password, or attempt to scan a web site space for vulnerabilities.

The action to perform is most of the time to block the offending IP address via
the machine firewall, but fail2ban supports any mechanism that you can conceive,
as long as it can be enacted by a UNIX command.

## PF and its logs

On my FreeBSD server I use the excellent [pf](https://docs.freebsd.org/en/books/handbook/firewalls/#firewalls-pf)
packet filter to policy incoming traffic and to perform traffic normalization.

The PF logging mechanism is very UNIX-y, as it provides a virtual network
interface (`pflog0`) onto which the initial bytes of packets blocked by a
rule that has the `log` specifier are forwarded, so that real-time block
logs can be inspected via a simple:

```bash
# tcpdump -eni pflog0
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on pflog0, link-type PFLOG (OpenBSD pflog file), capture size 262144 bytes
01:48:13.748353 rule 1/0(match): block in on vtnet0: 121.224.77.46.41854 > 46.38.233.77.6379: Flags [S], seq 1929621329, win 29200, options [mss 1460,sackOK,TS val 840989709 ecr 0,nop,wscale 7], length 0
01:48:15.726215 rule 1/0(match): block in on vtnet0: 192.241.235.20.37422 > 46.38.233.77.5632: UDP, length 3
01:48:17.993439 rule 1/0(match): block in on vtnet0: 145.239.244.34.54154 > 46.38.233.77.1024: Flags [S], seq 3365362952, win 1024, length 0
^C
3 packets captured
3 packets received by filter
0 packets dropped by kernel
```

These logs can be saved by `pflogd` into a `pcap` format file in
`/var/log/pflog`, that can be used for async troubleshooting and inspection, as
well using `tcpdump` or anything that can parse `pcap` files (such as
wireshark).

## Limits of binary logs

I had already configured `fail2ban` to parse `postfix`, `dovecot` and `nginx`
logs, so that if you try to brute an SMTP or IMAP passwd on my box or you try
to run something like [`nikto`](https://github.com/sullo/nikto) against my web
site you'll soon be banned by `fail2ban` and your incoming connections will be
dropped by `pf`.

However I could not ask `fail2ban` to read the binary `pflog` produced by
`pflogd`, as `fail2ban` is regex-based and only understands text input.

## Python to the rescue

I thought of a software that would:

* Start an `async` loop
* Run `tcpdump` and attach to its `stdout` and `stderr`
* Write the `stdout` and `stderr` to a file
* Trap a `HUP` and `USR1` signal and re-open the file, to aid log rotation

## Can I haz it?

Sure thing! Head over to [github](https://github.com/vjt/pfasciilogd/) and
check out [`pfasciilogd`](https://github.com/vjt/pfasciilogd/) and the
supporting `fail2ban` configuration.

I hope you find this useful.

Have fun!
