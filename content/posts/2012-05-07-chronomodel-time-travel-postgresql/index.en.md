---
title: "ChronoModel: Time Travel for PostgreSQL"
date: 2012-05-07
tags: [ruby, postgresql, rails, open-source, ifad]
description: "I just shipped a Ruby gem that implements Oracle's Flashback Queries on PostgreSQL using views, rules, and table inheritance. Five days from first commit to release."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
ChronoModel is still alive — 14 years, 41 releases, 201 stars. The rules got replaced by INSTEAD OF triggers in [v0.6](https://github.com/ifad/chronomodel/tree/v0.6.0) (2014), the `box()`/`point()` hack by proper `tsrange` columns, and the monkey-patching by a proper adapter registration. [Geremia Taglialatela](https://github.com/tagliala) took over maintenance in 2020 and pushed it to [v5.0.0](https://rubygems.org/gems/chrono_model/versions/5.0.0) with Rails 8.1 and Ruby 4.0 support. The core idea — updatable views on `public`, current data on `temporal`, history on `history` with table inheritance — never changed. The [repo](https://github.com/ifad/chronomodel) is healthy and actively maintained.
{{< /retrospective >}}

**Update, April 2019:** [ChronoModel reached 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/) — seven years, 506 commits, and 31 releases later.

We're building a CRM at [IFAD](http://www.ifad.org/) — a UN specialized agency in Rome — and one of the hard requirements is temporal data. We need to know what a record looked like at any point in the past. What was this project's budget on March 15th? When did this beneficiary's address change? Who approved what, and what did the record look like at the time?

I'd been prototyping a PostgreSQL schema approach for this — views, rules, table inheritance — and it worked. Then [Amedeo](https://github.com/amedeo), my boss, looked at it and said: "This shouldn't live inside the CRM. Make it a reusable framework."

He was right. The temporal pattern has nothing to do with CRM logic. It belongs in a gem.

So I had five days of uninterrupted focus, and today I'm releasing [ChronoModel](https://github.com/ifad/chronomodel) — an ActiveRecord extension that gives your models full temporal capabilities on PostgreSQL. What Oracle sells as [Flashback Queries](http://docs.oracle.com/cd/B28359_01/appdev.111/b28424/adfns_flashback.htm) and charges enterprise money for, we can do with standard SQL on Postgres 9.0+.

<!--more-->

## The idea

The textbook answer to temporal data is a [Slowly Changing Dimension Type 2](http://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2) — you keep a history of every row with validity timestamps, and query against them. Every enterprise database vendor has a proprietary solution. PostgreSQL doesn't. But PostgreSQL gives you all the building blocks — views, rules, table inheritance, GiST indexes — and nobody had assembled them into a Rails-friendly package. Until now.

My bet was to make it **completely transparent** to the application. No schema changes in your models, no special save methods, no history tables to manage by hand. You add `temporal: true` to your migration and `include ChronoModel::TimeMachine` in your model, and everything else happens behind the scenes. Your existing code doesn't change — it just gains the ability to look into the past.

The critical insight is that all of this happens **in the database**, not in the application layer. PostgreSQL rules intercept every write and atomically maintain the history. There's no "forget to call `save_with_history!`" bug. There's no race condition between writing the current row and the history entry. Referential integrity is guaranteed by the database itself — if the transaction commits, the history is consistent. Period.

That transparency is also the riskiest part of the design, because making it invisible to ActiveRecord means getting *very* intimate with ActiveRecord's internals. More on that later.

## The architecture

ChronoModel uses three PostgreSQL schemas working together:

- **`temporal`** — holds the real "current" tables
- **`history`** — holds history tables that **inherit** from the temporal ones, adding `valid_from`, `valid_to`, and `recorded_at` columns
- **`public`** — holds **updatable views** that your application sees as regular tables

Your Rails models point at the views in `public`. They look and behave exactly like normal tables. Behind the scenes, PostgreSQL [rules](http://www.postgresql.org/docs/9.1/static/rules.html) on those views intercept every INSERT, UPDATE, and DELETE and route them to the right places:

- **INSERT**: creates a row in `temporal` (current data) and a row in `history` (with `valid_from = now()`)
- **UPDATE**: closes the current history entry (sets `valid_to = now()`), opens a new one, and updates the temporal table
- **DELETE**: closes the history entry and removes the temporal row

The beautiful part is that your application code doesn't change at all. Queries hit the `public` views, which show current data from `temporal`. History accumulates silently in `history`.

Here's the complete SQL structure for a `countries` table (from the [full schema reference](https://github.com/ifad/chronomodel/blob/v0.1.0/README.sql)):

```sql
create schema temporal;  -- current data lives here
create schema history;   -- historical data lives here

-- The real table, in the temporal schema
create table temporal.countries (
  id   serial primary key,
  name varchar
);

-- The history table INHERITS from the temporal one — so it has
-- all the same columns, plus validity tracking fields.
-- No schema duplication, no column drift.
create table history.countries (
  hid         serial primary key,
  valid_from  timestamp not null,
  valid_to    timestamp not null default '9999-12-31',
  recorded_at timestamp not null default now(),

  constraint from_before_to check (valid_from < valid_to),

  constraint overlapping_times exclude using gist (
    box(
      point( extract( epoch from valid_from), id ),
      point( extract( epoch from valid_to - interval '1 millisecond'), id )
    ) with &&
  )
) inherits ( temporal.countries );

-- What the application sees: a plain view over current data
create view public.countries as select * from only temporal.countries;
```

Three things to notice:

1. **`inherits ( temporal.countries )`** — the history table inherits the schema from the current table. Add a column to `temporal.countries`, it automatically appears in `history.countries`. No migration drift, ever.

2. **`select * from only temporal.countries`** — the `ONLY` keyword is crucial. Without it, PostgreSQL's inheritance means the view would return rows from both the temporal *and* the history table. `ONLY` restricts it to the current data.

3. **The exclusion constraint** — I abuse GiST geometric indexes to prevent overlapping history entries for the same record. Each validity period becomes a **box** in 2D space (time axis × record ID). Two boxes overlap (`&&`) only if they share the same ID and an overlapping time range. If anyone tries to insert a contradictory history entry, PostgreSQL rejects it at the constraint level. Bulletproof temporal integrity using spatial indexes. I'm unreasonably proud of this hack.

Then the rules make the view writable. Here's UPDATE (the most interesting one):

```sql
create rule countries_upd as on update to countries do instead (
  -- Close the current history entry
  update history.countries
    set   valid_to = now()
    where id       = old.id and valid_to = '9999-12-31';

  -- Open a new history entry with the updated data
  insert into history.countries ( id, name, valid_from )
  values ( old.id, new.name, now() );

  -- Update the current table
  update only temporal.countries
    set name = new.name
    where id = old.id
);
```

One rule, three operations, one transaction. The `'9999-12-31'` sentinel marks the currently-valid entry. The gem generates all of this — the schemas, the tables with inheritance, the view, the rules, the indexes, the constraints — from a single `temporal: true` option. You never write this SQL by hand.

## The Rails integration

Getting this to work transparently with ActiveRecord required... creativity. The adapter subclasses `PostgreSQLAdapter` and overrides every DDL method — `create_table`, `drop_table`, `rename_table`, `add_column`, `rename_column`, `change_column`, `remove_column`, `add_index`, `remove_index`, and more. All of them check if the table is temporal and route operations to both schemas accordingly.

From your migration, it's one option:

```ruby
create_table :countries, temporal: true do |t|
  t.string :name
  t.string :code
  t.timestamps
end
```

That single `temporal: true` creates the temporal table, the history table with inheritance, the public view, all the rules, the GiST index, and the exclusion constraint. Drop-in.

Then in your model:

```ruby
class Country < ActiveRecord::Base
  include ChronoModel::TimeMachine
end
```

And you get time travel:

```ruby
# Current data — works exactly like before
Country.where(code: 'IT')

# What did Italy look like on January 1st 2010?
Country.as_of(Time.utc(2010, 1, 1)).find_by(code: 'IT')

# Full history of a record
italy = Country.find_by(code: 'IT')
italy.history  # => all versions, with valid_from/valid_to

# Temporal associations propagate automatically
italy.as_of(1.year.ago).projects  # also loaded as-of that date
```

I also [added CTE support](https://github.com/ifad/chronomodel/blob/v0.1.0/lib/chrono_model/patches.rb#L39-L62) (Common Table Expressions) to ActiveRecord's query builder, because Rails 3 doesn't have `WITH` clauses and the `as_of` queries need them. That required [patching Arel's PostgreSQL visitor](https://github.com/ifad/chronomodel/blob/v0.1.0/lib/chrono_model/patches.rb#L64-L78) to emit the correct SQL.

## The ugly truth

Let me be honest about the hack that makes this work. To inject the adapter, I do this:

```ruby
silence_warnings do
  ActiveRecord::ConnectionAdapters::PostgreSQLAdapter = ChronoModel::Adapter
end
```

Yes, I replace the entire PostgreSQL adapter constant. And I patch `ActiveRecord::Associations::Association` to propagate the `as_of_time` across temporal associations.

It works. It's ugly. It'll need to be cleaned up before this thing sees a 1.0. But it works, and it works transparently — your existing code doesn't change.

## Five days

Thirty-six commits from the initial README to this release. No tests yet — they're coming, I promise. The SQL is solid (I've been testing the schema approach manually for weeks before writing the gem), but the Ruby side needs proper specs.

If you work with PostgreSQL and Rails and you've ever needed historical queries, audit trails, or temporal reporting: `gem install chrono_model` and try it. The [source is on GitHub](https://github.com/ifad/chronomodel), and the [API documentation](https://vjt.github.io/chronomodel/) covers every public method. Issues, PRs, and complaints welcome.

Time travel shouldn't cost an Oracle license.


---

**Open source from the IFAD years:** **ChronoModel (2012)** • [data-confirm-modal](/posts/2013-07-02-data-confirm-modal/) (2013) • [Hermes](/posts/2013-10-20-hermes-rails-rumble-2013/) (2013) • [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • [TM → Pontoon](/posts/2018-02-14-translation-memory-pontoon/) (2018) • [ChronoModel 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • [OneSpan 2FA](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/) (2020) • [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) (2026)
