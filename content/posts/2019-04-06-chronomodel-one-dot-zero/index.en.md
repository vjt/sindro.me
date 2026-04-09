---
title: "ChronoModel 1.0: Seven Years to Ship"
date: 2019-04-06
tags: [ruby, postgresql, rails, open-source]
description: "ChronoModel hits 1.0 after seven years, 506 commits, and 31 releases. The core idea never changed — everything else did."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
After v1.0.0, [Geremia Taglialatela](https://github.com/tagliala) took over and pushed it to [v5.0.0](https://rubygems.org/gems/chrono_model/versions/5.0.0) with Rails 8.1 and Ruby 4.0 support. The gem is at 201 stars and still actively maintained. Seven more years of production use at IFAD — and counting — on top of the seven it took to reach 1.0. The [API documentation](https://vjt.github.io/chronomodel/) and the [repo](https://github.com/ifad/chronomodel) are both alive.
{{< /retrospective >}}

Seven years ago I [released ChronoModel v0.1.0](/posts/2012-05-07-chronomodel-time-travel-postgresql/) — a Ruby gem that gives ActiveRecord models temporal capabilities on PostgreSQL. Five days of hacking, thirty-six commits, no tests, and a confession about monkey-patching the PostgreSQL adapter constant.

Today I'm tagging [v1.0.0](https://github.com/ifad/chronomodel/commit/aa07e74). The commit message is `:gem: this is v1.0.0`. Not much of a speech, but the code speaks for itself: 506 commits, 31 releases, 52 files changed, 5,392 lines added. The [core idea](/posts/2012-05-07-chronomodel-time-travel-postgresql/#the-architecture) — updatable views on `public`, current data on `temporal`, history on `history` with table inheritance — never changed. Everything else did.

<!--more-->

## What changed

Three things were wrong with v0.1.0, and I said so at the time. All three got fixed on the same day — [Valentine's Day 2014](https://github.com/ifad/chronomodel/tree/v0.6.0), the [v0.6.0 release](https://github.com/ifad/chronomodel/compare/v0.5.7...v0.6.0). A complete rewrite of the database layer while keeping the Ruby API identical. The minimum PostgreSQL version jumped from 9.0 to 9.3. If v0.1.0 was "this works," v0.6.0 was "this works *correctly*."

### Rules → INSTEAD OF triggers

The [original design](/posts/2012-05-07-chronomodel-time-travel-postgresql/#the-architecture) used PostgreSQL [rules](http://www.postgresql.org/docs/9.1/static/rules.html) to make the public views writable. Rules work, but they have sharp edges — they rewrite queries at parse time, they can't handle `RETURNING` clauses properly, and debugging them is a nightmare.

I [ripped them all out](https://github.com/ifad/chronomodel/commit/05aff8cc) and replaced them with INSTEAD OF triggers. Same behavior, cleaner execution model. Triggers fire at statement execution time, handle `RETURNING` naturally, and you can actually debug them. The commit message says "BREAKING CHANGE" — because it was. Every temporal table needed a migration to switch over.

### box()/point() → tsrange

The [original exclusion constraint](/posts/2012-05-07-chronomodel-time-travel-postgresql/#the-architecture) was my proudest hack — abusing GiST geometric indexes to prevent overlapping history entries by encoding time ranges as 2D boxes. It worked, but it was a hack. [PostgreSQL 9.2](https://www.postgresql.org/docs/9.2/rangetypes.html) shipped proper range types, and by [9.3](https://www.postgresql.org/docs/9.3/rangetypes.html) they were solid.

[Replaced](https://github.com/ifad/chronomodel/commit/be57527) the geometric hack with native `tsrange` columns. The constraint went from this:

```sql
-- v0.1.0: encode time as geometry, hope for the best
EXCLUDE USING gist (
  box(
    point( date_part('epoch', valid_from), id ),
    point( date_part('epoch', valid_to - INTERVAL '1 msec'), id )
  ) WITH &&
)
```

to this:

```sql
-- v0.6.0: say what you mean
EXCLUDE USING gist ( id WITH =, validity WITH && )
```

And the WHERE clauses for [temporal queries](https://github.com/ifad/chronomodel/commit/be57527) cleaned up just as dramatically:

```sql
-- v0.1.0: "what year is it?!" as a geometry problem
WHERE box(point(date_part('epoch', valid_from), 0),
          point(date_part('epoch', valid_to), 0))
   && box(point(date_part('epoch', '2014-01-01'), 0),
          point(date_part('epoch', '2014-01-01'), 0))

-- v0.6.0: just ask
WHERE '2014-01-01' <@ validity
```

The database understands what it's enforcing, and so does anyone reading the query log.

### Monkey-patching → proper adapter

The v0.1.0 ["ugly truth"](/posts/2012-05-07-chronomodel-time-travel-postgresql/#the-ugly-truth):

```ruby
silence_warnings do
  ActiveRecord::ConnectionAdapters::PostgreSQLAdapter = ChronoModel::Adapter
end
```

Gone. ChronoModel now [registers itself](https://github.com/ifad/chronomodel/commit/c11b30f) as a proper adapter subclass. You configure it in `database.yml` with `adapter: chronomodel` and ActiveRecord loads it through its standard adapter resolution. No constants are harmed.

## Tests

The v0.1.0 post said "no tests yet — they're coming, I promise." They came. [v0.3.0](https://github.com/ifad/chronomodel/tree/v0.3.0) (June 2012, six weeks later) added comprehensive RSpec specs. By v1.0.0 there are [5,000+ lines of test code](https://github.com/ifad/chronomodel/tree/v1.0.0/spec) covering temporal tables, history queries, associations, time queries, STI, indexes, migrations, schema dumping, and standard ActiveRecord behavior.

The test suite runs against multiple Rails versions via [Appraisal](https://github.com/thoughtbot/appraisal) — [Rails 5.0, 5.1, and 5.2](https://github.com/ifad/chronomodel/tree/v1.0.0/gemfiles) for v1.0.0. The [v0.13.1](https://github.com/ifad/chronomodel/tree/v0.13.1) release, tagged thirty minutes before v1.0.0, is the last version supporting Rails 4.2.

## The weekend of April 6th

The final push is a weekend sprint. [Rails 5.0 through 5.2 support](https://github.com/ifad/chronomodel/commit/f2bbdb3) lands in the afternoon, [Rails 4.2 gets dropped](https://github.com/ifad/chronomodel/commit/ab10280), specs get [added](https://github.com/ifad/chronomodel/commit/f043ef7), deprecation warnings get fixed. Then three releases in under an hour:

- **20:25** — [v0.13.1](https://github.com/ifad/chronomodel/compare/v0.13.0...v0.13.1): "the last version to support Rails 4.2"
- **20:54** — [v1.0.0](https://github.com/ifad/chronomodel/compare/v0.13.1...v1.0.0): `:gem: this is v1.0.0`
- **21:17** — [v1.0.1](https://github.com/ifad/chronomodel/compare/v1.0.0...v1.0.1), because of course there's a v1.0.1

Then the refactoring runs until [5 AM](https://github.com/ifad/chronomodel/commit/3a13f10) — [extracting the adapter into clean modules](https://github.com/ifad/chronomodel/commit/9ff1ab5), [rewriting `on_schema`](https://github.com/ifad/chronomodel/commit/aa8a5c5) to use thread-local storage, fixing CodeClimate smells, increasing coverage. Because tagging 1.0 doesn't mean you stop. It means you finally have permission to clean up properly.

## What didn't change

The three-schema architecture. The `temporal: true` migration option. The `include ChronoModel::TimeMachine` mixin. The `as_of` query interface. The idea that temporal data belongs in the database, not in application callbacks.

```ruby
# This worked in 2012. It still works in 2019.
Country.as_of(1.year.ago).find_by(code: 'IT')
```

506 commits to make the internals worthy of the interface. Seven years of production at [IFAD](http://www.ifad.org/) without a single data loss incident.

The [source is on GitHub](https://github.com/ifad/chronomodel), the [API docs](https://vjt.github.io/chronomodel/) cover every public method. `gem 'chrono_model', '~> 1.0'` and you're set.

Time travel shouldn't cost an Oracle license. It still doesn't.
