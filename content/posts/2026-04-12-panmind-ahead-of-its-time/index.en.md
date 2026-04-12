---
title: "The Panmind Stack: Building 2020s Architecture in 2010"
date: 2026-04-12
tags: [panmind, javascript, erlang, ruby, rails, architecture, open-source]
description: "How a small Italian startup built a single-page app framework, an event-driven analytics pipeline, and cross-language session sharing — years before any of it was mainstream."
image: cover.jpg
featuredImage: cover.jpg
---

In 2009, a small team in Rome started building [Panmind](https://github.com/Panmind), a collaborative platform for sharing and organizing knowledge. The company was [Mind2Mind S.r.L.](http://mind2mind.is/), founded by Emanuele Caronia.

Panmind itself didn't survive. But the stack we built for it did something interesting: it anticipated architectural patterns that wouldn't become mainstream for five to ten years. We were building single-page applications before the term existed, streaming analytics before Segment, and sharing sessions across languages before JWTs.

I [presented some of our open-source spin-offs](/posts/2010-08-05-panmind-at-ruby-social-club/) at the Ruby Social Club in Milan in 2010, but that post only scratched the surface — it was a quick rundown of Rails plugins. This is the deeper story: three technologies, three problems solved too early, and how the same ideas showed up in every major framework that followed.

## Act 1: jquery-ajax-nav — SPA Before SPAs

![Hash-based routing in a vintage browser — polling for changes, hidden iframes for IE, the URL fragment as the only programmable piece of the address bar](/posts/2026-04-12-panmind-ahead-of-its-time/act1-ajax-nav.jpg)

Panmind needed to feel fast. Clicking a link shouldn't reload the entire page — it should swap just the content area, instantly. In 2023 you'd reach for React, or Turbo, or HTMX. In 2009, none of those existed. There was no History API. There was no `pushState`. The URL hash fragment — the bit after `#` — was the only part of the URL you could change without triggering a page reload. So that's what we used.

[jquery-ajax-nav](https://github.com/vjt/jquery-ajax-nav) was a 14-plugin jQuery framework that turned a traditional server-rendered Rails app into something that behaved like a single-page application. 206 commits, extracted from the Panmind production codebase, battle-tested across IE6 through Chrome.

### The hash encoding problem

URL fragments can't contain query strings. The `?` and `&` characters have special meaning in URLs, and browsers handle them inconsistently inside fragments. So we invented a custom encoding:

```javascript
// jquery.location.js — custom anchor encoding
//
// Because traditional query string syntax (?foo=bar&baz=42)
// cannot be used in anchors, this plug-in implements a custom
// syntax, where ':' maps to '?' and ';' maps to '&'.
//
// Example: /search?q=hello&page=2 → #search:q=hello;page=2

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

A handful of regex replacements, and suddenly you could store full request paths with parameters inside a URL fragment. Today, React Router and Vue Router have a "hash mode" that does essentially the same thing — it exists for environments where you can't configure server-side routing, which in 2009 was *every* environment.

### Detecting navigation without events

Here's the thing about 2009: browsers didn't fire events when the hash changed. The `hashchange` event was still rolling out (IE8 had it, Firefox and Chrome didn't yet, Safari definitely didn't). The History API with `popstate` wouldn't land until 2011-2012. So how do you detect when the user clicks the back button?

You poll. Every 100 milliseconds.

```javascript
// jquery.history.js — the core of hash-based routing in 2009

init: function (callback) {
  _callback = callback;
  _current  = '#';

  // IE < 8 needs a hidden iframe for history entries
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

A `setInterval` running ten times per second, checking if `location.hash` has changed. Brutal? Yes. The only way? Also yes. And it worked perfectly — the callback fires, the content loads via AJAX, and the user never notices they're being polled.

But the real insanity was IE. Internet Explorer 6 and 7 had a *fascinating* bug: changing `location.hash` via JavaScript didn't create a new history entry. The back button simply wouldn't work. The workaround was to create a hidden iframe and write the hash into its document body — because writing to an iframe *did* create history entries:

```javascript
// The IE iframe hack — writing to a hidden iframe to create
// history entries, because IE didn't do it for hash changes

var _iframe = {
  // ...
  write: function (hash) {
    var doc = this.element.contentWindow.document;
    doc.open();
    doc.write('<html><body>' + hash + '</body></html>');
    doc.close();
  }
};
```

You read that right. We were writing `<html><body>#search:q=hello</body></html>` into a hidden iframe to make the back button work in IE. This is the kind of thing that makes you appreciate the History API.

### Lifecycle events

![The page lifecycle as a theatrical stage — old content being torn down on the left, new content assembled on the right, a conductor orchestrating the transition](/posts/2026-04-12-panmind-ahead-of-its-time/lifecycle-events.jpg)

The navigation framework had a proper event lifecycle. When content was about to be swapped, a `nav:unloading` event fired — so you could tear down timers, unbind event handlers, clean up. When new content arrived, `nav:loaded` fired — so you could initialize widgets, bind events, set up the new page.

```javascript
// jquery.ajax-nav.js — lifecycle event registration

// Runs ONCE on first load
$.fn.ajaxInit = function (fn) {
  return $(document).one ('nav:loaded', fn);
};

// Runs EVERY time content loads
$.fn.ajaxReady = function (fn) {
  return $(document).bind ('nav:loaded', fn);
};

// Runs EVERY time content is about to unload
$.fn.ajaxUnload = function (fn) {
  return $(document).bind ('nav:unloading', fn);
};
```

If this looks familiar, it should. Turbolinks (2012) introduced `turbolinks:load`. Turbo (2021) has `turbo:before-render` and `turbo:load`. They're the same concept — the same *need* — formalized three and twelve years later respectively.

### Link and form hijacking

Any link with class `nav` got its click intercepted. Instead of a full page load, the framework fetched the content via AJAX and swapped it into the container:

```javascript
// Intercept clicks on navigation links
$.fn.navLink = function (options) {
  options = __validateOptions (options, this);

  var listener = function (event) {
    var link = $(this);
    var args = $.clone (options);

    if (!args.href)
      args.href = link.attr ('href');

    $.navLoadContent (link, args);
    return false;
  };

  if (options.live)
    $(this).live ('click', listener);
  else
    $(this).click (listener);

  return this;
};
```

Forms got the same treatment with `.navForm()` — GET forms serialized to query strings, POST forms sent data in the body. And there was a clever — some might say abusive — convention for AJAX redirects. We couldn't use any 3xx status code because IE would blindly follow redirects on XHR requests, swallowing the redirect response before our JavaScript could intercept it. So we hijacked HTTP 202 (Accepted): the server returned 202 with the redirect path in the response body, and our client code followed it manually:

```javascript
// HTTP 202 = AJAX redirect: response body contains the path to follow
if (xhr.status == 202) {
  options.href   = response;
  options.method = 'get';
  options.params = null;
  $.navLoadContent (loader, options);
  return;
}
```

The corresponding Rails helper was dead simple:

```ruby
def ajax_redirect_to(path)
  if request.xhr?
    render :text => path, :status => 202
  else
    redirect_to path
  end
end
```

Turbo's redirect convention (303 See Other) is the modern equivalent. HTMX has `HX-Redirect`. Same problem, same solution, different HTTP status code.

### The optimization cookie

One of my favorite tricks in the codebase. When the framework hijacked a deep URL like `/projects/1/writeboards/42` into `/projects/1#writeboards/42`, it set a 1-second cookie called `nha`:

```javascript
// Set a cookie to tell the backend to render a spinner
// ("nha" stands for NavHijAck)
$.navHijackRedirect = function (base, anchor) {
  var expire = new Date((+new Date) + 1000).toGMTString ();
  document.cookie = 'nha=1; path="' + base + '"; expires=' + expire;
  $.location.set (base + $.location.encodeAnchor (anchor));
};
```

The Rails backend checked this cookie and, if set, rendered just a loading spinner instead of the full page — because the JavaScript would immediately fire an AJAX request for the actual content. A hand-rolled loading optimization that saved a full server-side render on every hijacked navigation. Today, frameworks handle this automatically with skeleton screens and streaming HTML.

### Declarative behaviors via HTML attributes

![HTML as puppeteer — attribute tags on strings controlling Web 2.0 UI elements below](/posts/2026-04-12-panmind-ahead-of-its-time/declarative-html.jpg)

Beyond the navigation framework, we built an entire [behaviours library](https://github.com/vjt/jquery-ajax-nav/blob/master/jquery.behaviours.js) that wired up UI interactions declaratively through HTML attributes — specifically, by abusing the `rel` attribute. A toggler, a tabber, a cycler, a deleter, a rollover — each one was a CSS class that activated a jQuery `.live()` handler, and the `rel` attribute pointed at the target element:

```html
<!-- Toggler: click to show/hide #milestone_42 -->
<a class="toggler slider" rel="#milestone_42">Edit</a>

<!-- Tabber: each tab points at its content panel -->
<ul class="tabber fader" rel=".newElement">
  <li class="active"><a href="#" rel="#newPost">New Post</a></li>
  <li><a href="#" rel="#newLink">New Link</a></li>
</ul>

<!-- Cycler: auto-rotating slides, timer interval in rev(!) -->
<div class="cycler timer" rel="#slides" rev="5000"></div>
```

We even had `hierarchyFind()`, a custom DOM traversal function that parsed a mini-language inside `rel`. The syntax `>#todo .uploader` meant "find a parent whose ID starts with 'todo', then search inside it for an element with class 'uploader'" — essentially `element.closest('[id^="todo"]').querySelector('.uploader')`, except `closest()` wouldn't exist in browsers until 2015-2016.

The pattern — declaring behavior and targets in HTML attributes instead of writing JavaScript — is exactly what HTMX does today with `hx-target`, `hx-swap`, and `hx-trigger`. It's what Stimulus does with `data-controller` and `data-target`. It's what Alpine.js does with `@click` and `x-show`. We were writing `rel="#milestone_42"` in 2009; today you'd write `hx-target="#milestone_42"`. The semantics moved from `rel` to `data-*` attributes (which HTML5 formalized for exactly this purpose), but the idea — HTML as the source of truth for UI behavior — is the same.

### The parallels

| jquery-ajax-nav (2009) | What came later |
|---|---|
| Hash polling every 100ms | `hashchange` event (IE8+), then `popstate` + History API (2011) |
| `#/path:query=param` encoding | React Router hash mode, Vue Router hash mode |
| `nav:unloading` / `nav:loaded` | Turbolinks `turbolinks:load` (2012), Turbo `turbo:before-render` (2021) |
| `.navLink()` click hijacking | Turbo Drive auto-hijacking all `<a>` tags |
| `.navForm()` submit hijacking | HTMX `hx-post` (2020), Turbo `<form>` interception |
| HTTP 202 body = redirect path | Turbo 303 redirect convention |
| Full `.html()` DOM replacement | Virtual DOM diffing (React 2013), morphdom (Turbo 2021) |
| Progressive enhancement — works without JS | Most modern SPAs require JS. Only Turbo preserves this. |

That last row is the kicker. jquery-ajax-nav was built on top of plain HTML. Every link worked without JavaScript — you just got full page reloads instead of AJAX. The framework was an *enhancement*, not a requirement. Most modern SPAs can't say that. Turbo Drive, which took until 2021 to reach maturity, is the closest spiritual successor — and it follows the exact same philosophy.

## Act 2: usage_tracker — Event-Driven Analytics Before Segment

![A steampunk data pipeline — Ruby server rack with glowing gems, an EventMachine turbine catching UDP packets, and CouchDB document stacks being sorted by robotic arms](/posts/2026-04-12-panmind-ahead-of-its-time/act2-usage-tracker.jpg)

With AJAX navigation in place, traditional analytics were insufficient. Server logs showed one initial page load followed by a stream of XHR requests, with no way to reconstruct the user's actual navigation path. Google Analytics *could* track AJAX navigations if you manually called `_trackPageview()` after each content swap — and we did, via our [bigbro](https://github.com/vjt/bigbro) plugin. But GA's pageview model couldn't tell us what we actually needed: request durations, XHR vs full page loads, per-area traffic patterns, per-user behavior. We needed our own analytics pipeline.

So we built [usage_tracker](https://github.com/vjt/usage_tracker): a three-component analytics system that captured every request, transported it asynchronously, stored it in a document database, and computed aggregations via map-reduce. In 2010.

### The Rack middleware

The first component was a Rack middleware that wrapped every Rails request, measured its duration, and extracted metadata:

```ruby
# usage_tracker/middleware.rb — request instrumentation

def call(env)
  req_start = Time.now.to_f
  response  = @app.call env
  req_end   = Time.now.to_f

  data = {
    :user_id  => env['rack.session'][:user_id],
    :duration => ((req_end - req_start) * 1000).to_i,
    :backend  => @@backend,
    :xhr      => env['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest',
    :context  => env[Context.key],
    :env      => {},
    :status   => response[0]
  }

  @@headers.each {|key| data[:env][key.downcase] = env[key] unless env[key].blank?}

  self.class.track(data.to_json)

  return response
end
```

That `:xhr` flag is the crucial link to Act 1 — it told us whether a request came from a full page load or from jquery-ajax-nav's AJAX content swap. The analytics system was *designed* to understand the navigation framework.

The data was shipped via UDP, fire-and-forget:

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

Non-blocking, 1-second timeout, errors silently logged. The `write_nonblock` itself won't block, but the `UDPSocket.open` and `connect` calls *could* — DNS resolution, socket allocation, kernel buffers. The `Timeout.timeout(1)` wraps the entire operation as a safety net: if anything in the OS-level socket machinery hangs, we bail after one second rather than blocking the Rails request. Defensive coding. The analytics pipeline *never* slowed down a user request. Lose a data point rather than add latency. This is exactly the philosophy behind [StatsD](https://github.com/statsd/statsd), which Etsy would open-source a year later in 2011, and which became the foundation of modern application telemetry.

### The EventMachine reactor

On the receiving end, an [EventMachine](https://github.com/eventmachine/eventmachine) daemon listened on a UDP socket, parsed incoming JSON, validated it, and stored it in CouchDB:

```ruby
# usage_tracker/reactor.rb — event-driven data collection

module UsageTracker
  module Reactor
    def receive_data(data)
      doc = parse(data)
      if doc && check(doc)
        store(doc)
      end
    end

    private
      def store(doc)
        tries = 0
        begin
          doc['_id'] = make_id
          UsageTracker.database.save_doc(doc)
        rescue RestClient::Conflict => e
          if (tries += 1) < 10
            retry
          end
        end
      end

      # Timestamp as _id: natural chronological sorting
      # Random digit: avoid conflicts across multiple servers
      def make_id
        Time.now.to_f.to_s.ljust(16, '0') + rand(10).to_s
      end
  end

  EventMachine.run do
    host, port = UsageTracker.settings.host, UsageTracker.settings.port
    EventMachine.open_datagram_socket host, port, Reactor
    log "Listening on #{host}:#{port} UDP"
  end
end
```

The timestamp-based document IDs were clever — CouchDB sorts by `_id` by default, so documents were automatically in chronological order. The random digit at the end handled the edge case of multiple application servers generating events at the same millisecond.

### CouchDB map-reduce views

![A craftsman's workshop — documents spread across a desk, magnifying glasses on articulated arms extracting patterns, sorted stacks of results](/posts/2026-04-12-panmind-ahead-of-its-time/map-reduce.jpg)

The analytics queries were defined as CouchDB map-reduce views in a YAML file — with ERB templating to DRY up the JavaScript:

```yaml
# config/views.yml — analytics computed via map-reduce
<%
  _AREAS_RE = '\/(' << %w( inbox res projects users account publish search ).join('|') << ')'

  _GET_AREA = %(
    var match = doc.env.path_info.match (/#{_AREAS_RE}/);
    var area  = match ? match[1] : 'other';
  ).gsub(/\s+/x, ' ').strip
%>

average_duration_of_path:
  map: |
    function (doc) {
      if (doc.duration)
        emit (doc.env.path_info, doc.duration);
    }
  reduce: |
    function (keys, values){
      return Math.round (sum (values) / values.length);
    }

area_count:
  map: |
    function (doc) {
      if (doc.env) {
        <%= _GET_AREA %>
        emit (area, 1);
      }
    }
  reduce: |
    function (keys, values, rereduce) {
      return sum (values);
    }
```

ERB-templated JavaScript inside YAML. Three languages in one file. It's the kind of thing that makes you wince and respect at the same time — ugly, pragmatic, and it got 13 analytics views defined without a single line of duplicated area-extraction logic.

### The architecture

```
Browser → Rails → Rack Middleware → UDP → EventMachine Reactor → CouchDB → Map-Reduce
```

Sound familiar? This is essentially:

- **Rack middleware extracting telemetry** → OpenTelemetry auto-instrumentation
- **UDP fire-and-forget** → StatsD (Etsy, 2011)
- **EventMachine reactor** → Kafka consumers, Fluentd, Vector
- **CouchDB map-reduce** → Elasticsearch aggregations, ClickHouse materialized views
- **The whole pipeline** → [Segment](https://segment.com/)'s Connections architecture: instrument → transport → store → query

And the XHR flag — that one boolean per request — is what Google Analytics 4 calls "single page application mode." We built it because we had to. We had a SPA (Act 1), and the analytics needed to understand it. Today we call this "Real User Monitoring" and pay Datadog or New Relic for it.

## Act 3: erlang-ruby-marshal — Cross-Language Sessions Before JWTs

![Two Rosetta Stones — Ruby glowing red, Erlang glowing blue — with a river of binary data flowing between them and a cracked HTTP cookie above](/posts/2026-04-12-panmind-ahead-of-its-time/act3-erlang-marshal.jpg)

Panmind had a web-based chat system. It was written in Erlang, built on [misultin](https://github.com/vjt/misultin) — a lightweight Erlang HTTP server. WebSockets wouldn't be standardized until RFC 6455 in December 2011, and browser support was spotty until 2013. So the transport was raw XHR long-polling: the browser opened an HTTP request, the Erlang server held it open until a message arrived or the connection timed out, then the browser immediately reconnected. No Comet framework, no Socket.IO, no abstraction layer. Just a request that hangs for 30 seconds waiting for data.

But the chat server had a problem: it needed to know who was logged in. The Rails application handled authentication and stored sessions in cookies. Rails sessions are serialized using Ruby's [Marshal format](https://ruby-doc.org/core/Marshal.html) — a binary protocol that only Ruby can read. There was no JSON-based session store, no JWTs, no shared authentication tokens. If you wanted another language to read a Rails session, you had to teach that language to parse Ruby's binary serialization.

So we forked [erlang-ruby-marshal](https://github.com/vjt/erlang-ruby-marshal) — originally written by tema for Ruby 1.8 — and extended it for Ruby 1.9 compatibility. Ruby 1.9 changed how strings were marshaled, adding encoding metadata via instance variables. Our fork handled that.

### Teaching Erlang to speak Ruby

The core of the parser is a beautiful example of Erlang's binary pattern matching. Each byte in the Marshal stream identifies a Ruby type, and the decoder dispatches accordingly:

```erlang
%% marshal.erl — decoding Ruby's binary serialization in Erlang

decode_element(?TYPE_NIL,    <<D/binary>>) -> {nil, D};
decode_element(?TYPE_TRUE,   <<D/binary>>) -> {true, D};
decode_element(?TYPE_FALSE,  <<D/binary>>) -> {false, D};
decode_element(?TYPE_FIXNUM, <<S:8, D/binary>>) -> decode_fixnum(S, D);
decode_element(?TYPE_STRING, <<S:8, D/binary>>) -> decode_string(S, D);
decode_element(?TYPE_SYMBOL, <<S:8, D/binary>>) -> decode_symbol(S, D);
decode_element(?TYPE_IVAR,   <<T:8, D/binary>>) -> decode_element_with_ivars(T, D);
```

Each clause matches on the type byte and extracts the remaining binary data. Erlang's pattern matching on binaries makes this almost readable as a protocol specification — you can see the Marshal format structure directly in the code.

The actual session extraction was handled by `rcookie.erl`, which split the Rails cookie, verified the HMAC-SHA signature, and decoded the payload:

```erlang
%% rcookie.erl — extracting a Rails session from a signed cookie

parse(Cookie) ->
    [Data, Digest] = string:tokens(decode(Cookie), "--"),
    case verify(Data, Digest) of
        false -> {error, verify_failed};
        true  -> {ok, marshal:decode(base64:decode(Data))}
    end.
```

Split at `--`, verify the digest, base64-decode, unmarshal. Four lines, and now the Erlang chat server knows who you are.

### The problem this solved

This is the microservice authentication problem. Service A (Rails) handles login. Service B (Erlang chat) needs to know the user's identity. In 2009, the standard approaches didn't exist yet:

- **JWTs** (2010 draft, 2015 RFC 7519): language-agnostic, self-contained, signed tokens. Any language can verify and read them. The *designed* solution to exactly this problem.
- **Shared session stores**: Redis or Memcached with JSON serialization. Requires both services to connect to the same store.
- **OAuth2/OIDC** (2012): token-based authentication with standard endpoints.

None of those were available. We solved it by going *lower* — teaching Erlang to parse Ruby's binary protocol. It's the most direct possible solution: Ruby writes bytes, Erlang reads bytes, done. No middleware, no shared infrastructure, no standard to comply with. Just two languages agreeing on a wire format.

And the transport itself — XHR long-polling — is what WebSockets replaced, and what Server-Sent Events (SSE) formalized. Today you'd open a WebSocket with a JWT in the handshake header. In 2009, you held an HTTP connection open and parsed a Ruby cookie in Erlang.

## Being Early Isn't Being Wrong

In 2009-2011, Panmind was running:

- A **single-page app framework** with lifecycle events, progressive enhancement, and form hijacking — a pattern that Turbolinks, React, and eventually Turbo and HTMX would each reinvent
- An **async event-driven analytics pipeline** over UDP with map-reduce aggregations — the architecture that StatsD, Segment, and OpenTelemetry would standardize
- An **Erlang chat server** sharing sessions with Rails via binary protocol parsing — the cross-service authentication problem that JWTs were designed to solve

Same ideas. Different era. Built with jQuery and EventMachine and Erlang pattern matching instead of React and Kafka and OAuth2. Built by a small team in Rome that was trying to make a product feel fast, understand its users, and support real-time features — not trying to be ahead of anything.

That's the thing about being early: you don't know you're early. You're just solving problems with the tools you have. The hash-polling loop, the UDP fire-and-forget, the Erlang Marshal parser — none of these felt *visionary* at the time. They felt like the obvious thing to do. It's only later, when the industry converges on the same patterns with proper standards and dedicated teams and better documentation, that you realize the ideas were right. They just needed the ecosystem to catch up.

And by the time it did, Panmind was gone.

None of this was a solo effort. Fabrizio Regini, Paolo Zaccagnini, and Christian Wörner wrote code alongside me. Edoardo Batini kept the servers running. Emanuele Bertolini, Ferdinando de Meo, and Chiara Santoro designed the interface that made the AJAX navigation worth building. Simona Forti created the content that users came for. Francesca Antinori figured out what to build in the first place. And Emanuele Caronia had the vision to put it all together. The stack was a team effort, even if the repos only show commit hashes.

Thanks for reading!

**The repos:** [jquery-ajax-nav](https://github.com/vjt/jquery-ajax-nav) | [usage_tracker](https://github.com/vjt/usage_tracker) | [erlang-ruby-marshal](https://github.com/vjt/erlang-ruby-marshal) | [misultin](https://github.com/vjt/misultin) | [All Panmind repos](https://github.com/Panmind)
