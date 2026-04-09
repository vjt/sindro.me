---
title: Chuck Norris in Ruby
date: 2008-06-13T12:00:00Z
tags: [funny, ruby]
hideVintage: true
---

{{< retrospective year="2026" >}}
Context for younger readers: in the mid-2000s, "Chuck Norris facts" were an absurdly popular internet meme — an endless list of hyperbolic jokes about the actor's supposed invincibility ("Chuck Norris can divide by zero"). Naturally, someone had to implement them in Ruby. intinig's blog is gone, but the GitHub repo is still up — a `ChuckNorris` class that refuses to be instantiated ("No one initializes Chuck Norris") or subclassed. The best part: if you try, it walks `ObjectSpace` and nils every instance of your class. Roundhouse kick to the entire Ruby runtime.
{{< /retrospective >}}

[intinig](http://tempe.st/) ported
[Chuck's](https://en.uncyclopedia.co/wiki/Chuck_Norris) roundhouse kick
power to Ruby! Have a look...

[https://github.com/intinig/chuck_norris/tree/master/chuck_norris.rb](
https://github.com/intinig/chuck_norris/tree/master/chuck_norris.rb)

It's a proof-of-concept, of course :).
