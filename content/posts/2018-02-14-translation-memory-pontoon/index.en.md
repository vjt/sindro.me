---
title: "A Shameless Translation Memory Importer for Pontoon"
date: 2018-02-14
tags: [ruby, postgresql, i18n, open-source, ifad]
description: "We had translators trapped in a desktop CAT tool, exchanging XML files like it's 2003. I propose Mozilla Pontoon for collaborative web translation. The catch: years of legacy translation memories in four different formats need to come along for the ride."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
The repo at [github.com/ifad/translation-memory](https://github.com/ifad/translation-memory) is still public, still has no README, and the Pontoon fork it talks to remains private. [Mozilla's upstream](https://github.com/mozilla/pontoon) is open and very much alive. Whether anyone at IFAD still runs Pontoon eight years on, I honestly don't know — I built this for one project on my desk, not as a corporate workflow change. The hyphen-stripping regex did its job for the months I needed it. Then, presumably, the next Pontoon schema migration broke something. That's what happens to integrations that talk to a database directly.
{{< /retrospective >}}

[IFAD](http://www.ifad.org/) is a UN agency that operates in [English, French, Spanish, and Arabic](https://www.ifad.org/en/web/operations/languages). Every public-facing string in our Rails apps needs to exist in four languages, which means we have a translation team, which means we have a translation workflow, which on most projects involves a [desktop CAT tool](https://en.wikipedia.org/wiki/Computer-assisted_translation), files attached to emails, and translation memories shipped around as XML.

That workflow does not survive a project I'm building right now. It's a Rails web app on a tight schedule, the source strings change every week, and by the time a translator has finished a TM file and emailed it back the strings have already moved. I need translators and developers looking at the same database in real time. I pick [Mozilla Pontoon](https://pontoon.mozilla.org/) — open-source, free, adaptable, written in Django, backed by Postgres — and stand it up for my project. The catch: there is a corpus of translations from the previous tool that I want to seed Pontoon with on day one, so the translators don't start from a blank slate.

Today I start a [translation-memory](https://github.com/ifad/translation-memory) repo and write the first parser. The project is described, with all due engineering humility, as ["Parser for TMX, SDL/XLIFF and TXML files and shameless importer into Mozilla Pontoon"](https://github.com/ifad/translation-memory). The "shameless" part is doing a lot of work in that sentence.

<!--more-->

## What's a translation memory, anyway?

A translation memory (TM) is a pile of source-target pairs: *"Submit your application"* → *"Soumettez votre candidature"*, with metadata (who, when, in which document). When a translator later encounters *"Submit your application"* again, the CAT tool offers the previous translation. When they encounter *"Submit your loan application"*, it offers a fuzzy match and lets them edit. The TM is the team's institutional memory, shaped over years.

In a desktop world the TM is a file. You buy a CAT tool, you import the TM, you translate, you export the updated TM, you email it to the next person. In a web world the TM is a database — the same database that holds the active strings, with full history, with concurrent editing, with diffs and review.

We are moving from the first world to the second. To do it without losing anything, every translation we have ever done must land inside Pontoon's `base_translation` table.

## Pontoon, briefly

[Pontoon](https://pontoon.mozilla.org/) is the platform Mozilla uses to crowdsource the localisation of Firefox, MDN, and a long tail of Mozilla properties into [hundreds of languages](https://pontoon.mozilla.org/teams/). Translators get a web UI with the source string, the previous translation, suggestions from the TM, machine translation hints, and a comments thread. Reviewers approve or reject. Everything is versioned in git on the back end.

The data model is, mercifully, not complicated. A `Project` has many `Locale`s and many `Resource`s (one per source file). A `Resource` has many `Entity` rows (one per source string). Each `Entity` has many `Translation`s, one per locale, with `approved` and `rejected` flags and a `User` who wrote it.

I want to push the legacy TM into that shape, locale by locale, while a real Pontoon process keeps serving the same database to the translators on my project. That means transactions, no schema changes, no destructive operations.

## The TM zoo

The first thing I learn is that *"translation memory file"* is not one thing. The corpus I have to import lives in at least four formats:

- **[TMX](https://en.wikipedia.org/wiki/Translation_Memory_eXchange)** — the industry-standard XML format. Translation Memory eXchange. It's what every CAT tool can read and write, and therefore what every CAT tool implements with creative variations.
- **TXML** — a Wordbee-flavoured XML using `<conceptGrp>` / `<languageGrp>` / `<termGrp>` nesting. Less standard, more verbose, still XML.
- **[XLIFF](https://en.wikipedia.org/wiki/XLIFF)** — the OASIS standard for localisation interchange. We get [SDL Trados](https://en.wikipedia.org/wiki/SDL_Trados_Studio) flavour with `urn:oasis:names:tc:xliff:document:1.2` plus `http://sdl.com/FileTypes/SdlXliff/1.0` extensions. Metadata like author and dates lives in `<sdl:seg-defs>`, which means namespace-aware XPath.
- **TCSV** — a custom CSV format the in-house team agrees on for the strings that don't fit anywhere else. Six columns. Semicolons. Eventually we add a *"simple"* variant when the original is too rigid.

I write one Nokogiri parser per format — [`tmx.rb`](https://github.com/ifad/translation-memory/blob/master/tmx.rb), [`txml.rb`](https://github.com/ifad/translation-memory/blob/master/txml.rb), [`xliff.rb`](https://github.com/ifad/translation-memory/blob/master/xliff.rb), [`tcsv.rb`](https://github.com/ifad/translation-memory/blob/master/tcsv.rb) — and a small `Translation` value object that they all produce. The shape they share is in [`shared.rb`](https://github.com/ifad/translation-memory/blob/master/shared.rb):

```ruby
class Translation
  attr_accessor :language, :source, :target, :user,
                :created_at, :updated_at, :resource, :key

  def user=(user)
    # Remove DOMAIN\\
    @user = user.sub(/^.+\\/, '')
  end

  def language_code
    language.sub(/-\w+$/, '').downcase # Remove country specifier
  end
end
```

The two methods on top are not academic. The desktop tool ran on Active Directory, so every `created_by` looks like `IFAD\\m.barnaba`. And every locale arrives as `fr-FR`, `es-ES`, `ar-AE`, while Pontoon stores them as `fr`, `es`, `ar`. Both transforms happen on assignment, once, and the rest of the code stops worrying.

Each format-specific parser exposes the same `translations` method. The [TMX parser](https://github.com/ifad/translation-memory/blob/master/tmx.rb) iterates `/tmx/body/tu` and pulls the source/target `<seg>` elements out of the right `<tuv>`. The [TXML parser](https://github.com/ifad/translation-memory/blob/master/txml.rb) walks the conceptGrp tree and pairs the first language group with each of the others. The [XLIFF parser](https://github.com/ifad/translation-memory/blob/master/xliff.rb) registers the OASIS and SDL namespaces:

```ruby
class XMLObject < ::XMLObject
  def namespaces
    { oasis: 'urn:oasis:names:tc:xliff:document:1.2',
      sdl:   'http://sdl.com/FileTypes/SdlXliff/1.0'
    }
  end
end
```

…and digs author/date metadata out of `./sdl:seg-defs/sdl:seg[last()]` because the segment definition we want is, empirically, the last one. There is a `# last() HACK` comment in the source. It is correct.

Once the parser produces a `[Translation, Translation, ...]` array, the format dimension disappears. Everything from here is the same code path.

## A shameless importer

Pontoon has a perfectly reasonable JSON API for importing translations. I do not use it. The API expects strings to match exactly, processes them one at a time, and would have me writing a wrapper in Python, deploying it next to the Pontoon process, and dealing with auth and rate-limiting. I have a desk drawer full of TMs and a deadline measured in days. I also know exactly what I am doing: this is a one-shot migration tool with a fragile coupling to Pontoon's internal Postgres schema, and the moment Mozilla ships a database migration my models will go stale and the import will break. That's fine. The import only has to work *now*. I open [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb) instead.

The trick is that Pontoon is Django, Django stores everything in Postgres, the schema is published, and ActiveRecord doesn't care which framework wrote the tables. I declare the models I need with the table names Django chose:

```ruby
class Project < ActiveRecord::Base
  self.table_name = 'base_project'

  has_many :resources,       inverse_of: :project
  has_many :memories,        inverse_of: :project
  has_many :project_locales, inverse_of: :project

  has_many :entities,     through: :resources
  has_many :translations, through: :entities
  has_many :locales,      through: :project_locales

  belongs_to :latest_translation, class_name: 'Translation'
end
```

There are nine such models in the file: `Project`, `Locale`, `ProjectLocale`, `Resource`, `TranslatedResource`, `Entity`, `Translation`, `ChangedEntityLocale`, `Memory`, plus a `User` mapped to `auth_user`. They form a small mirror of Pontoon's data model that ActiveRecord can scope, join, and update. A `connect!` that reads `PGUSER`, `PGHOST`, `PGDATABASE`, `PGPASSWORD` from the environment, and we are inside the database:

```ruby
def self.connect!
  pg_env = %w( PGUSER PGHOST PGDATABASE PGPASSWORD )
  missing = pg_env.select {|k| ENV[k].blank? }
  raise "Please set #{missing.join(' and ')}" if missing.present?

  ActiveRecord::Base.logger = Logger.new($stderr)
  ActiveRecord::Base.logger.level = :info

  cheer "Connecting to #{ENV['PGHOST']}"
  ActiveRecord::Base.establish_connection(adapter: 'postgresql')
end
```

Every imported translation goes in inside a transaction, with the same callbacks Pontoon's own code triggers — `update_latest_translation_ids`, `increment_translated_string_counter`, `mark_entity_as_changed`, `create_memory` — because I rebuilt them in Ruby right next to their counterparts. From Pontoon's point of view, an external importer is indistinguishable from a translator typing very fast.

This is what *"shameless"* means in the repo description.

## Real-world translation memories are noisy

The first import run finds 30% of the strings and complains about the rest. The translators look at the report and tell me, politely, that those strings *are* in the TM, I am just looking wrong. They are right. Real-world translation memories are filthy.

A source string in the Rails app is `Submit your application`. The same string in the TM is `Submit your application.` (trailing period). Or `Submit\u00a0your application` (non-breaking space). Or `Submit your application` followed by a tab and three spaces a translator added when copy-pasting from Word. Or `"Submit your application"` with smart quotes. The eye says they are the same; `=` says they are not.

I match in three steps over three days.

**Step one — exact match.** What I started with. Embarrassing in retrospect:

```ruby
scope :by_string, ->(string) { where(string: string) }
```

**Step two — normalise whitespace.** [`da71f51`](https://github.com/ifad/translation-memory/commit/da71f51), Wednesday 28 February 2018 at 20:39 with the commit message "More aggressive string matching…":

```ruby
scope :by_string, ->(string) {
  where(%[regexp_replace(lower(trim(string)), '\\s\\s*', ' ') =
          regexp_replace(lower(trim(?)), '\\s\\s*', ' ')], string)
}
```

Lowercase, trim, collapse whitespace runs to a single space. Picks up another twenty per cent of the strings.

**Step three — give up on punctuation.** [`a7c9a02`](https://github.com/ifad/translation-memory/commit/a7c9a02), the next morning at 11:54, with the commit message ["Even more aggressive matching"](https://github.com/ifad/translation-memory/commit/a7c9a02). I delete every non-word character on both sides before comparing:

```ruby
scope :by_string, ->(string) {
  where(%[regexp_replace(lower(trim(string)), '[^\\w]+', '', 'g') =
          regexp_replace(lower(trim(?)), '[^\\w]+', '', 'g')], string)
}
```

This is the version that goes to production. The match rate jumps to 95%+. The remaining 5% are genuine source changes where the Rails string was edited but the TM still holds the older wording, and those need a human anyway.

I am very pleased with the rude regex. The translators on the project log in and find their old translations sitting in the suggestions panel. Postgres is fine. Everyone on this particular project is fine.

## bark, hmmm, cheer

Importing thousands of translations means thousands of log lines. The naive way is `puts` and a tail. The slightly less naive way I land on is colour-coded stderr plus a CSV audit log, in [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb):

```ruby
def self.bark(woof)
  ActiveRecord::Base.logger.info("\e[1;31m#{woof}\e[0;0m")  # red
end

def self.hmmm(woof)
  ActiveRecord::Base.logger.info("\e[1;33m#{woof}\e[0;0m")  # yellow
end

def self.cheer(woof)
  ActiveRecord::Base.logger.info("\e[1;32m#{woof}\e[0;0m")  # green
end
```

Red is "I could not find a target entity for this translation", yellow is "I found one but it is already translated, leaving it alone", green is "imported". Every operation also writes a row to `IMPORT-2018-02-28.184412.csv` so a human can re-read the run later and figure out exactly what happened to each string. The CSV is what gets attached to the post-import email to the translators on the project.

## The round trip

Migration is half the story. The other half is that some of the translators on this project still want to work in their desktop tool on some days — old habits, offline trains, internet that comes and goes. So [`export.rb`](https://github.com/ifad/translation-memory/blob/master/export.rb) and [`export-missing.rb`](https://github.com/ifad/translation-memory/blob/master/export-missing.rb) walk Pontoon backwards: given a project and a locale, write out the missing entities to CSV, optionally collapsing duplicate strings into one row with all the keys joined by semicolons.

```ruby
def self.export_condensed_entities(entities, output)
  entities_by_string = entities.inject({}) do |h, entity|
    string = entity.string.downcase.strip
    (h[string] ||= []).push(entity)
    h
  end

  entities_by_string.each do |string, es|
    keys = es.map {|e| [e.resource.path, e.key].join(':') }.join(';')
    output << [keys, es.first.string, '', ...]
  end

  gain = ((1 - entities_by_string.count.to_f/entities.count.to_f) * 100).round(2)
  cheer "Exported #{entities.count} entities as #{entities_by_string.count} rows (#{gain}% gain)"
end
```

The "gain" is the percentage of strings that are duplicates across resources — which on a real Rails app is depressingly high, because we name buttons "Submit" everywhere. The translator only translates *Submit* once, the importer expands it back into all `n` entities on the way home. The round trip means the translators on my project don't have to choose between Pontoon and their desktop habit on any given day.

## A long Valentine's sprint

Looking at the [commit log](https://github.com/ifad/translation-memory/commits/master/) the shape of the project becomes clear:

- **14 February 2018** — "Initial parsing of translation memory XML." First commit, [`9f50b5b`](https://github.com/ifad/translation-memory/commit/9f50b5b). I am working on it on Valentine's Day, which is appropriate for a project about *translation memory*.
- **19 February** — "Import translations as suggestions." First end-to-end import run.
- **28 February** — sixteen commits in one evening. XLIFF parser, namespace support, empty-segment handling, missing-timestamp handling, "More aggressive string matching…" at 20:39.
- **1 March** — "Even more aggressive matching" the next morning. The regex that ships.
- **5 March** — exporters for missing translations and the gain calculation.
- **15 March** — TCSV importer for the in-house format.
- **27 March** — `approve!` / `reject!` / `unapprove!` APIs, because once you have the data inside, somebody wants to bulk-approve.
- **17 October 2018** — last commit. The migration is done. The tool runs every time I get a fresh TM file from somebody on the project.

The whole arc takes three weeks of intense work and seven months of trailing maintenance. Fifty-two commits total. 1,300 lines of Ruby, of which 688 are the [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb) shameless importer.

## What I take away from this

Three things, mostly.

**Bypass the API when the API is wrong for your job.** Pontoon's import endpoint is fine for a translator pasting in a TMX file from their browser. It is not fine for migrating a corpus with format quirks, encoding quirks, whitespace quirks, and per-string fuzzy matching. The schema is right there in their git repo. Talking to it directly cuts a week of HTTP round trips out of the import time, and I get to use the same Postgres transactions Django uses.

**Domain knowledge beats clever code.** The `[^\\w]+` regex is two characters of work. What it took to discover I needed it is what the project is actually about: sitting next to a translator while they explained why a string the importer was rejecting was *obviously* the same string. The `# last() HACK` in XLIFF is the same — once you understand SDL's segmentation model, the hack is the right answer.

**Small tools for big migrations.** This is not a product. This is a [single-purpose Ruby script](https://github.com/ifad/translation-memory/blob/master/import.rb) you point at one file at a time:

```sh
ruby import.rb tmx project-slug path/to/file.tmx
```

It does one thing. It logs what it did. It writes a CSV you can mail back. When the migration is done you stop running it. The repo stays public, the README never gets written ([sorry](https://github.com/ifad/translation-memory)), and the next Pontoon schema migration eventually breaks the model layer. By then the import has done its job. That is enough for tools like this.

Pontoon, by the way, is excellent. If your team is still emailing each other XML files, [go look at it](https://pontoon.mozilla.org/).


---

**Open source from the IFAD years:** [ChronoModel](/posts/2012-05-07-chronomodel-time-travel-postgresql/) (2012) • [data-confirm-modal](/posts/2013-07-02-data-confirm-modal/) (2013) • [Hermes](/posts/2013-10-20-hermes-rails-rumble-2013/) (2013) • [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • **TM → Pontoon (2018)** • [ChronoModel 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • [OneSpan 2FA](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/) (2020) • [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) (2026)
