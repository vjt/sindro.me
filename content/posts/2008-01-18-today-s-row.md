---
title: Today's row
date: 2008-01-18
tags: [bash, obfuscated, oneliner, replace, ruby, sed]
categories: [number-42, all]
---

```bash
05:01:24 vjt@voyager:~/Antani/trunk$ replace(){ sed -e "s|$1|$2|g" 
< $3 > ${3}X; mv ${3}X $3; }; egrep -r 'XP_[A-Z_]+[[:space:]]+-?[[
:digit:]]' Headers |ruby -ne "f,m=scan(/(.+):.+(XP_[\w_]+)/).first
;puts '%s %s %s' % [ f, m, 'kXP'<<m.scan(/(_[A-Z])([A-Z]+)/).map {
|a,b| a[1..1]<<b. downcase }.join ]" | while read hdr from to; do
replace $from $to $hdr; for src in `grep -rl $from Sources`; do
replace $from $to $src; done; done
```
