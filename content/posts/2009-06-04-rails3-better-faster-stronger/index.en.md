---
title: 'Rails 3: Better, Faster, Stronger'
date: 2009-06-04
tags: [rails, ruby]
---

{{< retrospective year="2026" >}}
Rails 3.0 shipped in 2010 and the Merb merge was a success. Today Rails is at version 8.x, having integrated everything envisioned here (modularity, stable APIs, engines as first-class citizens) and much more. Lighthouse is gone, therubymine.com no longer exists, and many links in this article are dead — but the core ideas still hold.
{{< /retrospective >}}

![Rails 3: Harder, Better, Faster, Stronger](/posts/2009-06-04-rails3-better-faster-stronger/rails3-harder-better-faster-stronger.png)

Almost every web developer knows or has at least heard of [Ruby on Rails](http://www.rubyonrails.com/), a [full-stack framework](http://en.wikipedia.org/wiki/Web_application_framework) for building web applications using the [Ruby](http://www.ruby-lang.org/) programming language.

<!--more-->

If you've never heard of Rails or web applications, there's a brief overview on [Wikipedia](http://en.wikipedia.org/wiki/Ruby_on_Rails), where it's impossible not to be struck by its Philosophy. Rails is defined by its author [David Heinemeier Hansson](http://loudthinking.com/) as "[opinionated software](http://roohit.com/800c1)" — software that imposes certain approaches and workflows during the design and development of a project, with all the advantages and [disadvantages](http://www.martinfowler.com/bliki/EnterpriseRails.html) that entails.

Another characteristic that marked the early evolution of Rails (2003-2007) was the lack of robust interfaces for extending it through external plug-ins, partly enabled by a controversial Ruby feature: [monkeypatching](http://en.wikipedia.org/wiki/Monkey_patch). In Ruby, classes are never closed: you can modify their behavior at any point in the program, and this applies to core classes too (e.g. String, Integer, ...). This led to a proliferation of plug-ins and framework extensions that relied on private implementation details whose stability over time was never guaranteed, with all the [maintainability](http://en.wikipedia.org/wiki/Maintainability) problems that follow: anyone who followed the early Rails releases cannot forget the [lengthy](http://weblog.rubyonrails.org/2005/11/11/why-engines-and-components-are-not-evil-but-distracting/) [debate](http://rails-engines.rubyforge.org/wiki/wiki.pl?OhGodWhatHaveWeDone) that arose from the implementation of [Rails Engines](http://rails-engines.org/).

Later, engines were [rehabilitated](http://www.coryosborn.com/posts/railsconf-day-2-rails-engines), even being [presented](http://assets.en.oreilly.com/1/event/24/The%20Even-Darker%20Art%20of%20Rails%20Engines%20Presentation.pdf) at the 2009 edition of [RailsConf](http://en.oreilly.com/rails2009/) as a viable path for building reusable, complete software components — since they include Models, Views, Controllers, and Routes that connect the URIs an application responds to with the code implementing its logic.

This change of vision on DHH's part was driven by his experience of having to reimplement several applications that could have been encapsulated in an engine and subsequently reused.

Similar considerations were also expressed regarding Rails' strong opinionated character, whose imposed approaches don't just concern the use of a certain [pattern](http://c2.com/cgi/wiki?DesignPatterns), but also the imposition of a specific "piece of software" implementing it. For example, to access a database in Rails you use [ActiveRecord](http://ar.rubyonrails.org/), an implementation of the [Object-Relational Mapping](http://c2.com/cgi/wiki?ObjectRelationalMapping) pattern that bridges the [relational model](http://en.wikipedia.org/wiki/RDBMS) of currently widespread databases with the [object](http://en.wikipedia.org/wiki/Object_oriented) [oriented](http://c2.com/cgi/wiki?ObjectOriented) model used by Ruby and pervasively inherited by Rails.

## The Open Source context

In an open source context, however, such a restriction is seen as stifling by many developers. While ActiveRecord does its job well, it's important to be able to choose the component best suited to a given purpose: it's a concept that any experienced developer embraces, setting aside pointless religious wars :).

Modularity, extensibility, and the presence of a well-designed and above all stable interface are the founding principles of [Merb](http://merbivore.com/), another Ruby-based framework for building database-backed web applications, whose tagline is "Looking for a hacker framework?". Merb consists of a small, well-organized core of functionality, on top of which a series of plug-ins build and realize the complete scaffolding on which you then develop your application.

With Merb you can use your preferred ORM, template engine, mailer, and testing frameworks, since they all rely on the same [core](http://merbivore.com/features.html). Moreover, it's straightforward to build new ones to satisfy the most disparate needs: it's a philosophy [very similar to the UNIX one](http://en.wikipedia.org/wiki/Unix_philosophy), where each individual software tool implements limited functionality (but does it well), and solving more complex problems requires chaining different tools together.

Given the numerous advantages of this approach — completely opposite to Rails' initial one — even a [Rated R individual](http://www.loudthinking.com/posts/39-im-an-r-rated-individual) with strong opinions decided to change his mind once again, and announce to the world the news nobody expected: [Rails and Merb](http://weblog.rubyonrails.org/2008/12/23/merb-gets-merged-into-rails-3) [would become a single project](http://yehudakatz.com/2008/12/23/rails-and-merb-merge/)!

The [result of this merge](http://www.internetnews.com/dev-news/article.php/3819116) would materialize in the next major release of Rails, version 3.0, which was the subject of a [substantial talk](http://merbist.com/2009/05/08/railsconf-2009/) at RailsConf 2009, and whose features would be:

**Less "opinionated"**: no longer a single "Rails Way" but multiple "Rails Ways", given the ability to choose between different ORMs (AR, Sequel, DataMapper, CouchRest, ...), templating engines (ERb, HAML, Liquid, Markaby, [...](http://www.hokstad.com/mini-reviews-of-19-ruby-template-engines.html)), Javascript libraries (Prototype, jQuery, MooTools, Dojo, ...) and testing frameworks (Test::Unit, RSpec, Mocha, ...).

**Faster**: the Merb development team was always attentive to performance, striving to avoid writing software with too much "magic" (e.g. abuse of method\_missing) and to follow its philosophy of modularity and confining a component to a single application domain. Rails 3 would inherit these design approaches, ensuring better performance. In this vein, [Metal](http://weblog.rubyonrails.org/2008/12/17/introducing-rails-metal) was introduced in Rails 2.3.

**A public API**: you learn by making mistakes. If it's true that you can't predict how an end user will use software, the ways a developer can use a framework are equally multiple and unpredictable — and they become evil if they're not provided with an [API](http://en.wikipedia.org/wiki/Application_programming_interface) and guidelines for extension. The long debate around Rails Engines made history, and there was no point in repeating the same mistakes.

**More modular** and **more agnostic**, direct consequences of introducing an API, enabling the creation of "composable" applications — the framework being not a single tower, but rather a set of tools a-la [Lego Technic](http://en.wikipedia.org/wiki/Lego_Technic) (fond memories :). A feature confirming this approach, already available in Rails 2.3, was Rails templates: they offered a [DSL](http://en.wikipedia.org/wiki/Domain-specific_programming_language) for automating the initialization of a new application, by writing requirements in a .rb file to be passed as an argument to the -m parameter of the rails command. [This blog post by lifo](http://m.onkey.org/2008/12/4/rails-templates) contains everything you need for a quickstart.

**More evolvable**: a direct consequence of greater modularity and a change of vision. In Rails 3 there would be no more "Sacred Cows" — any aspect of the framework could be subject to change. Don't be alarmed: as long as the API remains stable and there's a defined deprecation process for APIs marked as obsolete, developers would have no headaches. There were far more headaches in the past due to the absence of an API, where everyone implemented the features they needed however they saw fit.

## Live from the stage

One (of the very many) examples of how this grand merge was being carried out can be seen directly on GitHub — specifically, [two](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a) [commits](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1) on ActionController. It was completely restructured, and the new implementation was placed in a new directory, new\_base. In the first commit, [Rails2Compatibility](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a#L5R5) was introduced and the [fixture templates](http://github.com/rails/rails/commit/8a4e77b4200946ba4ed42fe5927a7400a846063a#L13L5) were removed.

Subsequently, in the second commit, the switch from the old ActionController::Base to the [new one](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1#L6L2) took place, also inserting some [temporary hacks](http://github.com/rails/rails/commit/e046f36824fcc164c284a13524c6b4153010a4e1#L2R4) to keep the tests passing.

Following a merge of this magnitude carried out by established professionals is an excellent exercise, especially for those who have recently entered software engineering and want to learn firsthand the best practices that lead [big rewrites](http://chadfowler.com/2006/12/27/the-big-rewrite) to success.

## The future?

Rails 3 would be a remarkable leap forward in the history of this framework, leaving behind the most controversial parts of its philosophy and enabling the community to evolve it in ways previously impossible. It's advisable for every developer to follow its development, since there's also much to learn about project management processes and approaches, beyond software development itself. The Rails project management with its milestones was handled through [Lighthouse](http://rails.lighthouseapp.com/), while all the source code was hosted on [GitHub](http://github.com/rails/rails). Given the nature of git (and GitHub), anyone can, at any time, fork Rails and modify it as they please. It's a possibility that few other platforms for open source software development offer.

Additionally, you could follow the Rails Core Team on [Twitter](http://twitter.com/rails), stay updated on high-level developments by following [Ryan Daigle's blog](http://ryandaigle.com/), follow discussions around Rails 3 through the mail-to-web gateway on [ruby-forum.com](http://www.ruby-forum.com/forum/3) and, of course, bookmark therubymine.com since we'd be talking about Rails 3 again soon on these pages :).

See you soon!

---

> **Note:** This article was originally published on [therubymine.com](http://therubymine.com/2009/06/04/rails3-better-faster-stronger/), an Italian collective blog about Ruby and Rails that no longer exists. I'm republishing it here to preserve it.
