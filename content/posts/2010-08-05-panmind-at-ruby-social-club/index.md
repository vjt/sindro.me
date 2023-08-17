---
date: 2010-08-05T16:00:00Z
title: Panmind spin-offs presented at Ruby Social Club Milan
tags: [open source, panmind, rails, ruby]
categories: [development]
---

On July 22nd 2010, [Mikamai](http://mikamai.com/) hosted a [Ruby Social Club in
Milan](http://blog.mikamai.com/2010/07/la-notte-del-ruby-social-club/), where
nearly 50 people attended watching five speeches about Ruby, Web development
and Startups. I was glad to be one of the speakers, and I presented a set of
Rails plugins [we](http://mind2mind.is/) spinned off from our latest (and
greatest) project: [Panmind](http://panmind.org/) (read more on [the about
page](http://panmind.org/about)) and released as Open Source on
[GitHub](http://github.com/Panmind).

The keynote is split in two parts: the first one explains **why** you should
follow the sane software engineering principle of writing modular and
interest-separated code and then **how** you could (and should) extract it from
your Rails application by decoupling configuration and then prepare for the
Open Source release, by writing documentation **AND** presenting to a Ruby
event so, **hopefully, someone else will write unit tests! :-)**

We released an [SSL helper](http://github.com/panmind/ssl_helper) plugin that
implements filters (like Rails' `ssl_requirement`) but also named route helpers:
no more `<%= url_for :protocol => 'https' %>`! You'll have something like
`plain_root_url` and `ssl_login_url` - like they were built into the framework.

Then, a [Google Analytics](http://github.com/panmind/bigbro) ultra-simple
plugin, with `<noscript>` support, a couple of test helpers and an
[embryo](http://github.com/Panmind/bigbro/blob/master/js/jquery.analytics.js)
of a JS Analytics framework - hopefully it'll evolve into a complete jQuery
plugin. Then, a [ReCaptcha](http://github.com/Panmind/recaptcha) interface,
with AJAX validation support and eventually a
[Zendesk](http://github.com/Panmind/zendesk) interface for Rails.

We released also more code on [Panmind's GitHub
account](http://github.com/Panmind), including the nifty [AJAX Navigation
Framework](http://github.com/Panmind/jquery-ajax-nav) that implements all the
boilerplate code for the ultra-fast AJAX navigation of panmind
[contents](http://panmind.org/search) and
[projects](http://panmind.org/tour/collaborate).

The keynote follows, you can download it in PDF (no [exploits, I
swear!](/posts/2010-08-04-on-the-iphone-pdf-and-kernel-exploit)) [from this
link](/posts/2010-08-05-panmind-at-ruby-social-club/Panmind_at_Ruby_Social_Club_Milano.pdf)
or view/comment it on slideshare
[here](http://www.slideshare.net/panmind/panmind-open-source-releases-presented).

Final words: check out [mikamai blog post on the Ruby Social
Club](https://blog.mikamai.com/post/129408154293/la-notte-del-ruby-social-club)
to read the other keynotes (I will, hopefully, update this post with sum-ups of
them when time permits :-)) and [say hello on
twitter](http://twitter.com/panmind) or [on GitHub](http://github.com/Panmind)
if you're interested in contributing our open source projects or [you want to
work with us](http://panmind.org/jobs).

<iframe
src="https://www.slideshare.net/slideshow/embed_code/key/4PwLzCoPaujLIl"
width="100%" height="500" frameborder="0" marginwidth="0" marginheight="0"
scrolling="no" allowfullscreen></iframe>

[PDF version](/posts/2010-08-05-panmind-at-ruby-social-club/Panmind_at_Ruby_Social_Club_Milano.pdf)
