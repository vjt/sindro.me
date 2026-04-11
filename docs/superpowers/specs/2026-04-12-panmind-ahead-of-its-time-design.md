# Design: "The Panmind Stack: Building 2020s Architecture in 2010"

## Meta

- **Date:** 2026-04-12
- **Slug:** `2026-04-12-panmind-ahead-of-its-time`
- **Tags:** `[panmind, javascript, erlang, ruby, rails, architecture, open-source]`
- **Format:** Page bundle at `content/posts/2026-04-12-panmind-ahead-of-its-time/`
- **Languages:** EN + IT
- **Tone:** Conversational, technically precise, opinionated, first-person. "Tu" in Italian.

## Post Structure

### Intro

Set the scene: 2009-2011, a small team in Italy built Panmind, a collaborative platform. The stack they built anticipated patterns that wouldn't become mainstream for 5-10 years. Three acts, three technologies.

**The team:** Marcello Barnaba, Fabrizio Regini, Paolo Zaccagnini, Christian Worner (developers), Edoardo Batini (sysadmin), Emanuele Bertolini (designer), Simona Forti (content creator), Francesca Antinori (business analyst), Emanuele Caronia (owner/founder).

Link back to the existing [Ruby Social Club post](/posts/2010-08-05-panmind-at-ruby-social-club/) for context.

### Act 1: jquery-ajax-nav — SPA Before SPAs

**Problem:** App-like navigation without full page reloads. No History API, no React, no Angular, no Backbone (2009).

**Code examples to include:**

1. Hash encoding convention from `jquery.location.js` — `?` becomes `:`, `&` becomes `;` to store query params in URL fragments:
   - Show `encodeAnchor` / `decodeAnchor` functions
   - Explain *why*: URL fragments can't contain `?`, so you need a custom encoding

2. 100ms hash polling + IE iframe hack from `jquery.history.js`:
   - The `setInterval` polling loop checking `location.hash`
   - The hidden iframe trick for IE6-7 (which didn't create history entries for hash changes)
   - Contrast with modern `window.addEventListener('popstate', ...)`

3. Lifecycle events from `jquery.ajax-nav.js`:
   - `nav:unloading` / `nav:loaded` event system
   - `ajaxInit()` / `ajaxReady()` / `ajaxUnload()` callbacks
   - Compare to Turbo's `turbo:before-render` / `turbo:load`

4. Link and form hijacking:
   - `.navLink()` intercepting clicks on `.nav` links
   - `.navForm()` intercepting form submissions
   - HTTP 202 convention for server-side AJAX redirects
   - Compare to Turbo Drive auto-hijacking and HTMX `hx-post`

**Parallels table:**

| jquery-ajax-nav (2009) | Modern equivalent |
|---|---|
| Hash polling + IE iframe | History API + `popstate` event |
| `#/path:query=param` encoding | React Router, Vue Router hash mode |
| `nav:unloading` / `nav:loaded` | Turbo `turbo:before-render` / `turbo:load` |
| `.navLink()` hijacking | Turbo Drive auto-hijacking |
| `.navForm()` form interception | HTMX `hx-post`, Turbo forms |
| HTTP 202 body = redirect path | Turbo 303 redirect |
| Full `.html()` replacement | Virtual DOM (React), morphdom (Turbo) |
| Progressive enhancement (works without JS) | Most modern SPAs require JS |

**Punchline:** Progressive enhancement — it worked without JavaScript. Most modern SPAs can't say that.

**Repos:** [jquery-ajax-nav](https://github.com/vjt/jquery-ajax-nav)

### Act 2: usage_tracker — Event-Driven Analytics Before Segment

**Problem:** Understanding user behavior in an AJAX-driven UI. Server logs can't distinguish XHR from full page loads. Google Analytics can't track partial DOM updates. You need your own analytics pipeline.

**Code examples to include:**

1. Rack middleware from `lib/usage_tracker/middleware.rb`:
   - Request metadata extraction: duration, XHR flag, user agent, path, method, status
   - UDP non-blocking send with `write_nonblock` — fire-and-forget, never block the request
   - 1-second timeout, errors logged but not fatal

2. EventMachine reactor from `lib/usage_tracker/reactor.rb`:
   - UDP datagram listener on port 5985
   - JSON parse → validate → CouchDB store
   - Timestamp-based document IDs for natural sorting
   - Conflict retry loop (up to 10 retries) for multi-server setups

3. CouchDB map-reduce views from `config/views.yml`:
   - ERB-templated JavaScript view functions (DRY across 13 views)
   - Area extraction from URL paths (inbox, projects, users, etc.)
   - Average duration per path, per area
   - Per-user activity tracking

**Architecture (text diagram):**
```
Rails Request → Rack Middleware → UDP → EventMachine Reactor → CouchDB → Map-Reduce Views
```

**Modern parallels:**
- Rack middleware extracting telemetry = OpenTelemetry instrumentation
- UDP fire-and-forget = StatsD protocol (Etsy, 2011)
- EventMachine reactor = Kafka consumer / Fluentd
- CouchDB map-reduce = Elasticsearch aggregations / ClickHouse queries
- The whole pipeline = Segment (instrument → transport → store → query)

**Punchline:** The XHR flag tied it directly to Act 1 — the analytics system was designed to understand AJAX navigation. The two were built as a unit. Today this is called "Real User Monitoring" (RUM).

**Repos:** [usage_tracker](https://github.com/vjt/usage_tracker)

### Act 3: erlang-ruby-marshal — Cross-Language Sessions Before JWTs

**Problem:** Panmind had an Erlang-based chat server using raw XHR long-polling (request hangs until a message arrives, then reconnects — before WebSockets were usable, before Comet was formalized). The chat server needed to know who the logged-in user was. Rails sessions are serialized with Ruby's Marshal format. How do you read a Rails session cookie from Erlang?

**Code examples to include:**

1. The Erlang module parsing Ruby Marshal binary format:
   - Atoms, symbols, instance variables, object links
   - Rails Flash data decoding
   - Session hash extraction

2. The Ruby 1.9 compatibility fork:
   - tema wrote the original for Ruby 1.8
   - Panmind's fork (vjt's contribution) added Ruby 1.9 string encoding support

**Context on the chat server:**
- Built on misultin (Erlang HTTP server, also in the Panmind repos)
- Long-polling: raw XHR that times out and reissues, no Comet framework
- Needed authenticated sessions to know who was chatting
- This is the same problem WebSocket auth solves today

**Modern parallels:**
- Today: JWTs — language-agnostic, self-contained, signed tokens
- Or: shared Redis session store with JSON/protobuf serialization
- Or: OAuth2 tokens validated by any service
- In 2009: none of that was standard. You solved "microservice auth" by teaching Erlang to speak Ruby's binary format.

**Punchline:** This is literally the session-sharing problem that drove JWT adoption. Solved at the binary protocol level because there was no abstraction layer yet.

**Repos:** [erlang-ruby-marshal](https://github.com/vjt/erlang-ruby-marshal)

### Conclusion

Tie the three acts together: Panmind in 2009-2011 was running:
- A single-page app framework with lifecycle events (→ Turbo, HTMX, React)
- An async event-driven analytics pipeline over UDP (→ Segment, OpenTelemetry, StatsD)
- An Erlang chat server sharing sessions with Rails via binary protocol parsing (→ JWTs, microservice auth)

This is essentially what a modern stack looks like — just built five years too early, with duct tape instead of standards.

Closing reflection: being early isn't the same as being wrong. The ideas survived — they just needed the ecosystem to catch up.

Credit the full team. Link to all GitHub repos.

## Code Sources

All code snippets come from repos in `/home/vjt/code/panmind/`:
- `jquery-ajax-nav/jquery.location.js` — hash encoding
- `jquery-ajax-nav/jquery.history.js` — hash polling + IE iframe
- `jquery-ajax-nav/jquery.ajax-nav.js` — lifecycle events, hijacking
- `usage_tracker/lib/usage_tracker/middleware.rb` — Rack middleware
- `usage_tracker/lib/usage_tracker/reactor.rb` — EventMachine reactor
- `usage_tracker/config/views.yml` — CouchDB views
- `erlang-ruby-marshal/src/*.erl` — Marshal parser

## Non-Goals

- Not covering every Panmind repo — just these three as the "ahead of time" trio
- Not a tutorial — architecture + code examples, not step-by-step howto
- Not rewriting the Ruby Social Club post — this is a separate, deeper piece
- Not covering the skipped repos (capybara-webkit, dotlocal, etc.)
