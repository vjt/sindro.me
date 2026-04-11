# Panmind "Ahead of Its Time" Blog Post — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a bilingual blog post about how Panmind's 2009-2011 stack anticipated modern web architecture patterns.

**Architecture:** Three-act structure — jquery-ajax-nav (SPA before SPAs), usage_tracker (event-driven analytics before Segment), erlang-ruby-marshal (cross-language sessions before JWTs). Each act: problem, solution with code, modern parallels.

**Tech Stack:** Hugo page bundle, Markdown, code snippets from repos in `/home/vjt/code/panmind/`

**Spec:** `docs/superpowers/specs/2026-04-12-panmind-ahead-of-its-time-design.md`

---

### Task 1: Create page bundle and write the intro (EN)

**Files:**
- Create: `content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md`

- [ ] **Step 1: Create page bundle directory**

```bash
mkdir -p content/posts/2026-04-12-panmind-ahead-of-its-time
```

- [ ] **Step 2: Write front matter and intro**

Create `content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md` with:

```markdown
---
title: "The Panmind Stack: Building 2020s Architecture in 2010"
date: 2026-04-12
tags: [panmind, javascript, erlang, ruby, rails, architecture, open-source]
description: "How a small Italian startup built a single-page app framework, an event-driven analytics pipeline, and cross-language session sharing — years before any of it was mainstream."
---

[Intro section content]
```

The intro must:
- Set the scene: 2009-2011, Milan, a small team building a collaborative platform called [Panmind](https://github.com/Panmind)
- Name the full team: Marcello Barnaba, Fabrizio Regini, Paolo Zaccagnini, Christian Wörner (developers), Edoardo Batini (sysadmin), Emanuele Bertolini (designer), Simona Forti (content creator), Francesca Antinori (business analyst), Emanuele Caronia (owner/founder)
- Tease the three acts: a client-side SPA framework before the History API existed, an async analytics pipeline before Segment, and an Erlang chat server reading Rails sessions before JWTs
- Link to the existing [Ruby Social Club post](/posts/2010-08-05-panmind-at-ruby-social-club/) where these were first presented
- Tone: first-person, conversational, technically precise, opinionated. See CLAUDE.md for full voice guide.
- Do NOT use the word "journey"

- [ ] **Step 3: Commit**

```bash
git add content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md
git commit -m "Add Panmind ahead-of-its-time post: intro (EN)"
```

---

### Task 2: Write Act 1 — jquery-ajax-nav (EN)

**Files:**
- Modify: `content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md`

**Source code to reference:**
- `/home/vjt/code/panmind/jquery-ajax-nav/jquery.location.js` — hash encoding (lines 130-150)
- `/home/vjt/code/panmind/jquery-ajax-nav/jquery.history.js` — hash polling + IE iframe (lines 40-67 for polling, 138-184 for iframe)
- `/home/vjt/code/panmind/jquery-ajax-nav/jquery.ajax-nav.js` — lifecycle events (lines 573-589), link/form hijacking (lines 432-513), content loading (lines 282-423), URL hijacking with cookie (lines 691-741)

- [ ] **Step 1: Write the "SPA Before SPAs" section**

Append Act 1 to the EN post. Structure:

**Section heading:** `## Act 1: jquery-ajax-nav — SPA Before SPAs`

**The problem** (1-2 paragraphs): Panmind needed app-like speed. 2009 — no History API, no React, no Angular, no Backbone. The only way to avoid full page reloads without losing the back button was the URL hash fragment. But browsers didn't fire events on hash changes, IE didn't even create history entries for them, and query parameters couldn't go in fragments.

**Hash encoding** — show the `encodeAnchor`/`decodeAnchor` from `jquery.location.js` (lines 130-150):
```javascript
this.encodeAnchor = function (href) {
  if (!/^[\/#]/.test (href))
    href = '/' + (href || '');
  return decodeURIComponent (href)
           .replace (/[?&\/]+$/, '') // Trim the tail
           .replace (/^\//, '#')     // Replace the leading / with '#'
           .replace (/\?/,  ':')     // Replace '?' with ':'
           .replace (/\&/g, ';')     // Replace '&' with ';'
};
```
Explain the convention: `?` → `:`, `&` → `;`. So `/search?q=hello&page=2` becomes `#search:q=hello;page=2`. A custom URL scheme because the real one couldn't live in fragments.

**Hash polling + IE iframe** — show the polling loop from `jquery.history.js` (lines 40-67):
```javascript
init: function (callback) {
  _callback = callback;
  _current  = '#';

  if ($.browser.msie && ($.browser.version < 8 || document.documentMode < 8))
    _iframe.init ();

  setInterval (function () {
    var hash;
    if (_iframe.inited)
      hash = _iframe.get ();
    else
      hash = location.hash || '#';

    hash = normalize (hash);
    if (!changed (hash))
      return;

    $.history.save (hash, false);
    invoke ();
  }, 100);
},
```
Explain: polling every 100ms because there was no `hashchange` event (that came later, and `popstate` only with the History API in 2011). Then show the IE iframe hack (lines 138-184) — IE6-7 didn't create history entries when JS changed `location.hash`, so you had to write the hash into a hidden iframe's `document.body` to create a real history entry. Show the `_iframe.write` method:
```javascript
write: function (hash) {
  var doc = this.element.contentWindow.document;
  doc.open();
  doc.write('<html><body>' + hash + '</body></html>');
  doc.close();
}
```

**Lifecycle events** — show `ajaxInit`, `ajaxReady`, `ajaxUnload` from `jquery.ajax-nav.js` (lines 573-589):
```javascript
$.fn.ajaxInit = function (fn) {
  return $(document).one ('nav:loaded', fn);
};

$.fn.ajaxReady = function (fn) {
  return $(document).bind ('nav:loaded', fn);
};

$.fn.ajaxUnload = function (fn) {
  return $(document).bind ('nav:unloading', fn);
};
```
Explain the event model: `nav:unloading` fires before content loads (teardown), `nav:loaded` fires after (initialize). `ajaxInit` runs once, `ajaxReady` runs every time. This is exactly the lifecycle model that Turbolinks and Turbo adopted years later.

**Link and form hijacking** — show `.navLink()` from lines 432-456 and briefly describe `.navForm()`. Show the HTTP 202 convention from `$.navLoadContent` (lines 353-365):
```javascript
if (xhr.status == 202) {
  options.href   = response;
  options.method = 'get';
  options.params = null;
  $.navLoadContent (loader, options);
  return;
}
```
Explain: server returns 202 Accepted with a redirect path in the body → client automatically fetches it. A POST/Redirect/GET pattern for AJAX.

**URL hijacking with cookie optimization** — show `$.navHijackRedirect` from lines 691-698:
```javascript
$.navHijackRedirect = function (base, anchor) {
  var expire = new Date((+new Date) + 1000).toGMTString ();
  document.cookie = 'nha=1; path="' + base + '"; expires=' + expire;
  $.location.set (base + $.location.encodeAnchor (anchor));
};
```
Explain: when hijacking a deep URL like `/projects/1/writeboards/42` into `/projects/1#writeboards/42`, it sets a 1-second cookie (`nha` — "NavHijAck, but also the nick of the beloved one" as the source comment says). The Rails backend checks this cookie and renders just a spinner instead of the full page, because the JS will immediately fire an AJAX request for the real content. A hand-rolled optimization that modern frameworks handle automatically.

**The parallels table:**

| jquery-ajax-nav (2009) | What came later |
|---|---|
| Hash polling every 100ms | `hashchange` event (IE8+), then `popstate` + History API (2011) |
| `#/path:query=param` encoding | React Router hash mode, Vue Router hash mode |
| `nav:unloading` / `nav:loaded` | Turbolinks `turbolinks:load` (2012), Turbo `turbo:before-render` (2021) |
| `.navLink()` click hijacking | Turbo Drive auto-hijacking all `<a>` tags |
| `.navForm()` submit hijacking | HTMX `hx-post` (2020), Turbo `<form>` interception |
| HTTP 202 body = redirect path | Turbo 303 redirect convention |
| Full `.html()` DOM replacement | Virtual DOM diffing (React 2013), morphdom (Turbo 2021) |
| Works without JavaScript | Most modern SPAs require JS — only Turbo preserves this |

**Punchline** (1 paragraph): The progressive enhancement angle. jquery-ajax-nav enhanced plain HTML — every link worked without JavaScript, you just got full page reloads instead of AJAX. Most modern SPAs can't say that. Turbo Drive is the closest spiritual successor, and it took until 2021.

Link to the repo: [jquery-ajax-nav on GitHub](https://github.com/vjt/jquery-ajax-nav)

- [ ] **Step 2: Commit**

```bash
git add content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md
git commit -m "Add Act 1: jquery-ajax-nav — SPA before SPAs (EN)"
```

---

### Task 3: Write Act 2 — usage_tracker (EN)

**Files:**
- Modify: `content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md`

**Source code to reference:**
- `/home/vjt/code/panmind/usage_tracker/lib/usage_tracker/middleware.rb` — full file (94 lines)
- `/home/vjt/code/panmind/usage_tracker/lib/usage_tracker/reactor.rb` — full file (132 lines)
- `/home/vjt/code/panmind/usage_tracker/config/views.yml` — CouchDB views (140 lines)

- [ ] **Step 1: Write the "Event-Driven Analytics" section**

Append Act 2 to the EN post. Structure:

**Section heading:** `## Act 2: usage_tracker — Event-Driven Analytics Before Segment`

**The problem** (1-2 paragraphs): With AJAX navigation, traditional server logs were useless — they showed one page load followed by a bunch of XHR requests, with no way to understand user flow. Google Analytics couldn't track partial DOM updates. We needed our own analytics pipeline that understood the difference between a full page load and an AJAX navigation.

**The Rack middleware** — show the core of `middleware.rb` (lines 46-92). Highlight:
- Timing: `req_start = Time.now.to_f` → `@app.call(env)` → `req_end = Time.now.to_f`
- The XHR detection: `env['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'` — this is what ties it to Act 1
- The UDP fire-and-forget: `sock.write_nonblock(data)` with 1-second timeout — never block the request, lose data rather than slow down the user

Show the key code:
```ruby
data = {
  :user_id  => env['rack.session'][:user_id],
  :duration => ((req_end - req_start) * 1000).to_i,
  :backend  => @@backend,
  :xhr      => env['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest',
  :context  => env[Context.key],
  :env      => {},
  :status   => response[0]
}
```

And the UDP send:
```ruby
def track(data)
  Timeout.timeout(1) do
    UDPSocket.open do |sock|
      sock.connect(@@host, @@port.to_i)
      sock.write_nonblock(data << "\n")
    end
  end
rescue Timeout::Error, Errno::EWOULDBLOCK, Errno::EAGAIN, Errno::EINTR
  UsageTracker.log "Cannot track data: #{$!.message}"
end
```

**The EventMachine reactor** — show the reactor from `reactor.rb`. Highlight:
- `EventMachine.open_datagram_socket host, port, Reactor` — UDP listener
- `receive_data` → `parse` (JSON) → `check` (validate) → `store` (CouchDB)
- Timestamp-based document IDs (`Time.now.to_f.to_s.ljust(16, '0') + rand(10).to_s`) for natural chronological sorting
- Conflict retry loop for multi-server deployments

**The CouchDB views** — show 2-3 of the more interesting views from `views.yml`:
- The ERB-templated area extraction (`<%= _GET_AREA %>`) — DRY across 13 views
- `average_duration_of_path` — mean response time per URL path
- `area_count` — traffic per navigation area

**Architecture summary:**
```
Browser → Rails → Rack Middleware → UDP → EventMachine → CouchDB → Map-Reduce
```

**Modern parallels** (2-3 paragraphs):
- Rack middleware extracting telemetry = OpenTelemetry auto-instrumentation
- UDP fire-and-forget = StatsD protocol (Etsy open-sourced it in 2011, one year later)
- EventMachine reactor = Kafka consumer, Fluentd, Vector
- CouchDB map-reduce = Elasticsearch aggregations, ClickHouse materialized views
- The whole pipeline = Segment's Connections architecture (instrument → transport → store → query)
- The XHR flag = what Google Analytics 4 calls "single page application mode"

**Punchline**: The system was designed from day one to understand AJAX navigation — it was built as a companion to jquery-ajax-nav. Today we call this "Real User Monitoring" (RUM) and pay Datadog or New Relic for it.

Link to the repo: [usage_tracker on GitHub](https://github.com/vjt/usage_tracker)

- [ ] **Step 2: Commit**

```bash
git add content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md
git commit -m "Add Act 2: usage_tracker — event-driven analytics (EN)"
```

---

### Task 4: Write Act 3 + Conclusion (EN)

**Files:**
- Modify: `content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md`

**Source code to reference:**
- `/home/vjt/code/panmind/erlang-ruby-marshal/src/marshal.erl` — type dispatcher (lines 50-71), instance vars (lines 220-240), value caching (lines 288-344)
- `/home/vjt/code/panmind/erlang-ruby-marshal/src/rcookie.erl` — cookie parsing (lines 12-25)

- [ ] **Step 1: Write Act 3 — erlang-ruby-marshal**

Append Act 3 to the EN post. Structure:

**Section heading:** `## Act 3: erlang-ruby-marshal — Cross-Language Sessions Before JWTs`

**The problem** (2-3 paragraphs): Panmind had a web-based chat. The chat server was written in Erlang — probably using [misultin](https://github.com/vjt/misultin), an Erlang HTTP server also in our repos. No WebSockets yet (the spec was still in draft), no Comet framework. Just raw XHR long-polling: the browser opens a request, the server holds it until a message arrives or it times out, then the browser immediately reconnects. Simple, brutal, effective.

But the chat server needed to know who was logged in. The Rails app handled authentication and stored sessions in cookies, serialized with Ruby's Marshal format — a binary protocol that only Ruby understands. No JSON, no JWTs, no shared session store. If you wanted to read a Rails session from another language, you had to reverse-engineer Ruby's binary serialization format. So that's what we did.

Explain that tema wrote the original parser for Ruby 1.8, and we forked it for Ruby 1.9 compatibility — Ruby 1.9 changed how strings were marshaled (adding encoding metadata via instance variables).

**The code** — show the core dispatcher from `marshal.erl`:
```erlang
decode_element(?TYPE_NIL, <<D/binary>>) -> {nil, D};
decode_element(?TYPE_TRUE, <<D/binary>>) -> {true, D};
decode_element(?TYPE_FALSE, <<D/binary>>) -> {false, D};
decode_element(?TYPE_FIXNUM, <<S:8, D/binary>>) -> decode_fixnum(S, D);
decode_element(?TYPE_STRING, <<S:8, D/binary>>) -> decode_string(S, D);
decode_element(?TYPE_SYMBOL, <<S:8, D/binary>>) -> decode_symbol(S, D);
decode_element(?TYPE_IVAR, <<T:8, D/binary>>) -> decode_element_with_ivars(T, D);
```
Explain: Erlang pattern matching on binary data. Each byte identifies a Ruby type, and the decoder dispatches to the appropriate handler. The beauty of Erlang's binary pattern matching makes this almost readable as a spec.

Show the cookie parser from `rcookie.erl`:
```erlang
parse(Cookie) ->
    [Data, Digest] = string:tokens(decode(Cookie), "--"),
    case verify(Data, Digest) of
        false -> {error, verify_failed};
        true -> {ok, marshal:decode(base64:decode(Data))}
    end.
```
Explain: Split the cookie at `--`, verify the HMAC-SHA digest, base64-decode the data, unmarshal it. Now Erlang knows who the user is.

Briefly mention the Ruby 1.9 work: TYPE_LINK and TYPE_IVAR handling for string encoding metadata.

**Modern parallels** (1-2 paragraphs):
- Today: JWTs — language-agnostic, self-contained, signed tokens. Any language can verify and read them.
- Or: shared Redis/Memcached session store with JSON serialization
- Or: OAuth2/OIDC tokens validated by any service
- In 2009, none of this was standard. The problem — "how does Service B know who logged into Service A?" — is the foundational question of microservice authentication. We answered it by teaching Erlang to parse Ruby's binary format.

**The long-polling angle** (1 paragraph): And the transport itself — XHR long-polling — is what WebSockets replaced. Server-Sent Events (SSE) formalized the pattern. Today you'd use WebSockets or SSE with JWT auth. In 2009, you hand-rolled everything.

Link to the repo: [erlang-ruby-marshal on GitHub](https://github.com/vjt/erlang-ruby-marshal)

- [ ] **Step 2: Write the conclusion**

Append the conclusion. Structure:

**Section heading:** `## Being Early Isn't Being Wrong`

Tie the three acts together in 2-3 paragraphs:

Panmind in 2009-2011 was running:
- A single-page app framework with lifecycle events, progressive enhancement, and form hijacking
- An async event-driven analytics pipeline over UDP with map-reduce aggregations
- An Erlang chat server sharing sessions with Rails via binary protocol parsing

Restate the modern equivalents: Turbo/HTMX + Segment/OpenTelemetry + JWT-authenticated microservices. Same ideas, proper standards, bigger teams, better docs.

Closing reflection: being early isn't the same as being wrong. The patterns survived — hash-based routing became the History API, fire-and-forget UDP became StatsD, cross-language session sharing became JWTs. The ideas were right. They just needed the ecosystem to catch up. And by the time it did, Panmind was gone.

Credit the team one more time. Something like "None of this was a solo effort" — name them again briefly.

- [ ] **Step 3: Commit**

```bash
git add content/posts/2026-04-12-panmind-ahead-of-its-time/index.en.md
git commit -m "Add Act 3 + conclusion: erlang sessions, being early (EN)"
```

---

### Task 5: Write the Italian translation

**Files:**
- Create: `content/posts/2026-04-12-panmind-ahead-of-its-time/index.it.md`

- [ ] **Step 1: Translate the full post to Italian**

Create `index.it.md` with:
- Same front matter (translate title and description to Italian)
- Full translation of all sections
- Tone: informal "tu", conversational, technically precise. Same voice as the English but natural Italian, not translationese.
- Code snippets stay in English (they're code) — only the surrounding prose is translated
- The parallels table stays the same (technology names don't change)
- Keep all GitHub links identical

- [ ] **Step 2: Commit**

```bash
git add content/posts/2026-04-12-panmind-ahead-of-its-time/index.it.md
git commit -m "Add Italian translation of Panmind ahead-of-its-time post"
```

---

### Task 6: Push, stage, and report URL

**Files:** None (deployment only)

- [ ] **Step 1: Push to GitHub**

```bash
git push
```

- [ ] **Step 2: Deploy to staging**

```bash
ssh -A vjt@m42 'cd /srv/www/sindro.me/staging && git fetch origin && git reset --hard origin/master && git submodule update --remote && ./build.sh'
```

Note: use `git fetch + reset --hard` instead of `git pull` (LFS compatibility — see memory `feedback_staging_reset_hard.md`).

- [ ] **Step 3: Report staging URLs**

Tell the user to review at:
- EN: https://vjt.sindro.me/posts/2026-04-12-panmind-ahead-of-its-time/
- IT: https://vjt.sindro.me/it/posts/2026-04-12-panmind-ahead-of-its-time/
