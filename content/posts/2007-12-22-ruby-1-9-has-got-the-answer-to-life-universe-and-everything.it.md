---
title: Ruby 1.9 conosce la risposta alla vita, all'universo e a tutto quanto
date: 2007-12-22 22:00:00
tags: [funny, ruby, weird]
---

{{< retrospective year="2026" >}}
Ruby 1.9 ha raggiunto la fine del ciclo di vita nel 2015. Ruby è ora alla versione 3.x, e `Symbol.all_symbols` non include più questo easter egg — è stato rimosso da un pezzo. La risposta alla vita, all'universo e a tutto quanto resta 42.
{{< /retrospective >}}

```ruby
22:33:24 vjt@voyager:~$ irb19 -f
irb(main):001:0> Symbol.all_symbols.grep /^the/
=> [:the_answer_to_life_the_universe_and_everything]
```

sfortunatamente, la risposta non è 42:

```ruby
irb(main):002:0> _.first.object_id
=> 5048
```

:\

Grazie per questa strana scoperta, [nextie](https://deref.blogspot.com)! :D
