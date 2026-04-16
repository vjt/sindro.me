---
title: "From Heathen to Colore: A Document Pipeline Story"
date: 2016-01-15
tags: [ruby, sinatra, nginx, c, open-source, ifad]
description: "Three years and four colleagues converting Word into PDF at IFAD. Heathen was Sinatra + Dragonfly + a content-hash dedup trick. Colore is the rewrite — directory-as-database, async workers, an nginx C module, and a v1.0 tag I just merged."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Colore is still alive at [github.com/ifad/colore](https://github.com/ifad/colore) — [Geremia Taglialatela](https://github.com/tagliala) took over after I drifted onto other things and pushed the project forward through Ruby 2.7, 3.0, 3.1, 3.2, sidekiq 6, and modern CI. He sits at [354 commits](https://github.com/ifad/colore/graphs/contributors) — three times mine. The [nginx C module](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module) Joe wrote in February 2015 is unchanged. Heathen the standalone service was eventually folded directly into Colore as a library; the [original repo](https://github.com/ifad/heathen) is archived but the code lives on inside `lib/heathen/` of Colore. Same idea, fewer moving parts.
{{< /retrospective >}}

[IFAD](http://www.ifad.org/) is a UN agency that runs on documents. Loan agreements, evaluation reports, country strategy notes, board decisions, project briefs — every web application we build sooner or later needs to take a Word file and give back a PDF, or take a scan and give back something searchable, or take an arbitrary blob and turn it into a thumbnail. Three years ago we decided to stop solving this problem one application at a time and put it behind a single service.

Today I'm merging [v1.0.0 of Colore](https://github.com/ifad/colore/commit/63d4fe0). It's the second attempt at that service, and it's the one we get to keep. This is the story of both attempts and the people who built them — because almost none of the code below is mine.

<!--more-->

## Heathen, the first attempt

[Heathen](https://github.com/ifad/heathen) starts on [December 18, 2012](https://github.com/ifad/heathen/commit/f9081b6) with a `README` from [Peter Brindisi](https://github.com/petebrindisi). The repo banner is ASCII art. The tagline is "Convert the heathens." The mission statement is one sentence: *"a service for converting pretty much anything to PDF."*

Two days later the first working version lands. Peter sketches the architecture, [Lleïr Borràs Metje](https://github.com/lleirborras) wires up the conversion backends, [Joe Blackman](https://github.com/jblackman) joins to extend the API, and I show up roughly a year later to clean up the rough edges. Final tally: [193 commits, four authors](https://github.com/ifad/heathen/graphs/contributors), almost evenly split. None of us is the lead. The project belongs to the codebase.

The stack is delightfully 2012:

- [Sinatra](http://www.sinatrarb.com/) for the HTTP layer
- [Dragonfly](https://github.com/markevans/dragonfly) for content-addressable file storage and on-the-fly processing jobs
- [Rack::Cache](https://github.com/rtomayko/rack-cache) so converted output gets memoized for free
- [Redis](https://redis.io/) to remember which content hash maps to which Dragonfly job
- LibreOffice running headless on `localhost:8100`, [`wkhtmltopdf`](https://wkhtmltopdf.org/) for HTML, [ImageMagick](https://imagemagick.org/) for images, [tesseract](https://github.com/tesseract-ocr/tesseract) for OCR, and a [forked pdfbeads](https://github.com/ifad/pdfbeads) for stitching OCR'd images into searchable PDFs

The conversion contract is unusual. You `POST /convert` with a file (or a URL) and an action. The server doesn't actually do the work. Instead, it [hashes the content with SHA-256](https://github.com/ifad/heathen/blob/master/inquisitor.rb#L42-L44), checks Redis to see if it's been seen before, and either returns the cached Dragonfly URL or stores a fresh one and returns *that*. Either way you get back a JSON document with two URLs:

```json
{
  "original":  "http://heathen/media/W1siZi....jpg",
  "converted": "http://heathen/media/W1siZi....pdf"
}
```

Hitting the `converted` URL is what triggers the actual conversion — Dragonfly deserializes the URL into a job description, runs the conversion, and Rack::Cache holds onto the result. Subsequent requests are served from the cache. Same content uploaded twice from anywhere in the organization → same URL → no work duplicated. It's a cute trick. It's also the reason every quirk of the system is downstream of Dragonfly's URL-as-state model.

The infrastructure side is the part I do contribute to. The whole stack — LibreOffice with PyUNO, ImageMagick with the right delegate libraries, tesseract with the right language packs, the patched pdfbeads — has to live somewhere. I package all of it [as RPMs on the openSUSE Build Service](https://build.opensuse.org/project/show/home:vjt:ifad), so production deployment is `zypper ar` and `zypper install`. Heathen runs under Unicorn behind nginx on openSUSE, and it just works.

In late 2013 I do my one significant code contribution: five days between Christmas Eve and the 28th refactoring the subprocess executioner. The original used backticks. Backticks don't stream stdout, don't expose stderr, and break when wkhtmltopdf decides to vomit a megabyte of warnings before producing the PDF. I [rewrite it on top of `Process.spawn` plus `ProcessBuilder` for jRuby](https://github.com/ifad/heathen/commit/a36a1e0), [switch to `Open3` for large stdout streams](https://github.com/ifad/heathen/commit/44ba0b0), [kill PDFKit](https://github.com/ifad/heathen/commit/7b128d9) in favor of calling wkhtmltopdf directly, and [handle the case](https://github.com/ifad/heathen/commit/cdf44ca) where the Java side melts down on a megabyte of stdout. It's the kind of work nobody notices unless you don't do it.

A year later Joe ships [autoheathen](https://github.com/ifad/heathen/blob/master/bin/autoheathen) — an SMTP-driven version of the same pipeline. You email a Word document to `wikilex@ifad.org`, autoheathen receives it, converts the attachments, and forwards the result. The Legal department lives inside Outlook. Outlook does not speak HTTP. Email-driven conversion is how you meet users where they are.

## Why we rewrite

By the end of 2014 we know what's wrong. Not enough to throw the system out — Heathen is in production, it works, and nobody is asking us to replace it. But enough to know we won't choose this stack again.

The Dragonfly URL-as-state idea is the central problem. The URL *is* the job description, base64-encoded into the path. That means:

- **No versioning.** A document is a content hash. Upload `contract.docx`, get back a URL. Upload a corrected `contract.docx`, get a *different* URL. Now you need somewhere outside the system to remember which one is current. Every consuming application invents its own answer.
- **Synchronous conversion.** The first GET on the converted URL is when the work happens. If LibreOffice takes 90 seconds to render a complicated DOCX, the HTTP request takes 90 seconds. We end up with timeout knobs everywhere.
- **No callbacks.** You can't tell Heathen "convert this and ping me when you're done." The model doesn't have a "done" event.
- **Cache invalidation by hand.** When pdfbeads gets a bug fix and you want existing OCR'd PDFs regenerated, you `rake heathen:cache:clear` and the world re-converts on demand. Subtle.
- **Authorization is somebody else's problem.** Anyone who can guess a URL can fetch a document. We front it with nginx ACLs and pretend.

None of these are bugs. They're the boundary of what the chosen primitives can express. The right move is a different set of primitives.

## Colore

[Joe Blackman](https://github.com/jblackman) starts the rewrite on [January 30, 2015](https://github.com/ifad/colore/commit/422323f) with a commit titled "First cut of storage." The new project is [Colore](https://github.com/ifad/colore) — Italian for "color," named after [the color wheel](https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/BYR_color_wheel.svg/480px-BYR_color_wheel.svg.png) the README sports as its logo, and because it speaks several languages: storage, versioning, conversion.

The fundamental decision is in [a refactor commit four days later](https://github.com/ifad/colore/commit/6414de6): *"Refactored document to quit messing around with metadata, instead querying the directory structure."* No database. The filesystem is the database. Documents live at:

```
storage/
  └── myapp/
      └── 12345/
          ├── metadata.json
          ├── title
          ├── current → v002
          ├── v001/
          │   ├── foo.docx
          │   ├── foo.pdf
          │   └── _author.txt
          └── v002/
              ├── foo.docx
              ├── foo.jpg
              └── _author.txt
```

`current` is a symlink. New versions are new directories. Atomically advancing `current` is a one-system-call operation. Rolling back is the reverse. Listing versions is `ls`. The structure *is* the schema, and `Document.load(base_dir, doc_key)` walks the tree to reconstruct state. Joe gets [`flock`-based concurrency](https://github.com/ifad/colore/commit/f40097d) right on day twelve so simultaneous updates to the same document don't race.

The HTTP API gets a verb-noun shape that Heathen never had:

- `PUT  /document/:app/:doc_id/:filename` — create a new document
- `POST /document/:app/:doc_id/:filename` — store a new version
- `POST /document/:app/:doc_id/:version/:filename/:action` — request a conversion
- `GET  /document/:app/:doc_id/:version/:filename` — fetch a file
- `DELETE /document/:app/:doc_id` — burn it down

Conversions go through [Sidekiq](https://sidekiq.org/) and [POST a callback when done](https://github.com/ifad/colore/commit/a3aec71). Apps get to be event-driven. Heathen, the conversion engine itself, is [vendored into Colore as a library](https://github.com/ifad/colore/tree/master/lib/heathen) — same LibreOffice/wkhtmltopdf/ImageMagick/tesseract toolbox, now without the HTTP wrapper. One service instead of two, async by default, callbacks where they belong.

`autoheathen` comes along too: Joe [ports it from the old repo](https://github.com/ifad/colore/commit/0ef1fed) on day eight. Wikilex keeps working through the cutover.

By [February 11](https://github.com/ifad/colore/commit/d9af5a3) the LICENSE is in, the [README is written](https://github.com/ifad/colore/commit/46249b3), and Colore is open source.

## The nginx C module

The piece I want to point at because it makes me happy is the [bespoke nginx module](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module) Joe writes [on February 19, 2015](https://github.com/ifad/colore/commit/f6a6465).

The problem is fanout. With one document directory per `doc_id`, a Colore deployment with millions of documents has millions of directories under one parent. Most filesystems get unhappy long before that. The fix is a hash-prefix tree: take the MD5 of `doc_id`, lop off the first two characters, and use them as an intermediate directory. Now `myapp/12345/` actually lives at `myapp/ab/12345/`, and you have 256 buckets at the top instead of one bottomless pit.

Doing this in Ruby is fine — Colore handles it itself when reading and writing. But the *real* win is serving documents directly from nginx without round-tripping through the Sinatra app. The application sees a request, checks authorization, and emits an `X-Accel-Redirect` header pointing at the storage URL. nginx intercepts the response, swaps in the file from disk, and streams it. The Ruby app handles authorization in milliseconds and never touches the bytes.

Except nginx now has to compute the MD5 prefix on its own, in C. So Joe writes a [99-line nginx C module](https://github.com/ifad/colore/blob/master/nginx/ngx_colore_module/ngx_colore_module.c) that exposes one directive:

```nginx
location /document/foobar/(?<doc_id>.+?)/(?<file>.+)$ {
    internal;
    set_colore_subdir $hash $doc_id 2;
    alias             $colore_storage/foobar/$hash/$doc_id/$file;
}
```

`set_colore_subdir $hash $doc_id 2` runs an MD5 over `$doc_id` and writes the first 2 hex characters into `$hash`. That's it. That's the whole module. The vast majority of those 99 lines are nginx boilerplate — module struct, command table, init hooks. The actual work is one MD5 call and a `memcpy`. It's the difference between "Ruby serves a 50MB PDF" and "nginx serves a 50MB PDF and Ruby never wakes up."

The [build dependency](https://github.com/ifad/colore/blob/master/nginx/ngx_colore_module/README.markdown) is the [Nginx Development Kit](https://github.com/simpl/ngx_devel_kit) — a meta-module that gives third-party modules sane primitives for declaring variable filters. With NDK in the picture, exposing a new variable computation to nginx config is just declaring a callback and a directive descriptor.

## The Rails side

The application contract is now clean enough that wiring it into Rails is a small piece of glue rather than a project. [Luca Spiller](https://github.com/lucaspiller) writes [carrierwave-colore](https://github.com/ifad/carrierwave-colore) in [October 2015](https://github.com/ifad/carrierwave-colore/commit/3416c0c) — a [CarrierWave](https://github.com/carrierwaveuploader/carrierwave) storage adapter for Colore. You add it to your Gemfile, configure a base URI and an app name, and your existing uploaders write through to Colore:

```ruby
class DocumentUploader < CarrierWave::Uploader::Base
  storage :colore

  def store_path
    "#{model.class.name}.#{model.id}"
  end
end

# elsewhere
file = document.attachment.file
file.convert('pdf')          # async; returns immediately
file.format('pdf').read      # fetch the converted blob
file.versions                # => {"v001" => ["docx", "pdf"]}
```

`convert` returns immediately and Colore handles the work in the background; an optional callback URL [gets POSTed](https://github.com/ifad/carrierwave-colore) when the conversion lands. The Rails app stays Rails-shaped. Colore is invisible from the application's perspective until it isn't.

Underneath, [colore-client](https://github.com/ifad/colore-client) — also Joe's — handles the HTTP. It's a thin REST wrapper that knows about the Colore status codes and turns errors into proper Ruby exceptions. The CarrierWave adapter just speaks colore-client.

## v1.0.0

The [v1.0.0 tag](https://github.com/ifad/colore/commit/63d4fe0) goes in this morning, January 15, 2016 — a year minus two weeks since Joe's first commit. The merge message is unceremonious: *"libreoffice text conversion and specs fixes."* Then the tag. The git log is honest about who built it: Joe and Luca on top, contributions from [Antonio Delfin Martinez](https://github.com/antoniodelfin) and [Danilo Grieco](https://github.com/danilo-g), me on the infrastructure and the bug-fix patrol.

What we have at v1.0:

- A document service that knows about versions, runs conversions asynchronously, posts callbacks, and serves files through nginx without ever touching the bytes in Ruby.
- A bespoke nginx C module that lets nginx serve the bytes directly, with the Ruby app off the hot path.
- A CarrierWave adapter that makes adoption a five-line change.
- An email-driven entry point so non-HTTP users (the Legal department, mostly) can play too.
- A migration story from Heathen — the [legacy converter](https://github.com/ifad/colore/blob/master/lib/legacy_converter.rb) reads the old Dragonfly storage and republishes documents into the Colore tree, keyed by the original content hash.

What we don't have, and never will, is a dramatic origin story. The pipeline isn't an act of singular vision. It's three years of four people taking turns on the same problem, throwing out the parts that didn't work and keeping the parts that did. The Heathens get converted either way.

## Credits

- **Heathen**: [Peter Brindisi](https://github.com/petebrindisi) (initial design and architecture, 54 commits), [Lleïr Borràs Metje](https://github.com/lleirborras) (49), me (53), [Joe Blackman](https://github.com/jblackman) (38). Source at [github.com/ifad/heathen](https://github.com/ifad/heathen).
- **Colore**: Joe Blackman (architect and primary author), with everyone else along for the ride. Source at [github.com/ifad/colore](https://github.com/ifad/colore). nginx C module at [`nginx/ngx_colore_module/`](https://github.com/ifad/colore/tree/master/nginx/ngx_colore_module).
- **carrierwave-colore**: [Luca Spiller](https://github.com/lucaspiller). Source at [github.com/ifad/carrierwave-colore](https://github.com/ifad/carrierwave-colore).
- **colore-client**: Joe Blackman. Source at [github.com/ifad/colore-client](https://github.com/ifad/colore-client).
- **autoheathen**: Joe Blackman, originally in Heathen, ported to Colore.
- **OpenSuSE RPMs**: me, at [build.opensuse.org/project/show/home:vjt:ifad](https://build.opensuse.org/project/show/home:vjt:ifad).

`gem install colore-client` and you can talk to a Colore service. `bundle install carrierwave-colore` and your Rails uploads end up versioned, converted, and served by nginx. The keys to the document kingdom are MIT-licensed.
