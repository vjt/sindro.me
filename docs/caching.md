# Caching strategy

How sindro.me caches content across origin → Cloudflare edge → browser, why
the TTLs are what they are, and how `cf-purge.py` / `cf-purge-static.py` keep
the edge honest.

## TL;DR

```
Browser  ──── 1h ────►  Cloudflare edge  ──── 1d ────►  Origin (m42 nginx)
```

- **Edge TTL**: 1d. Long because edge is purgeable.
- **Browser TTL**: 1h. Short because browsers are not purgeable.
- **Override mode**: `override_origin` on both, so the CF Cache Rule is the
  single source of truth — origin nginx headers don't decide TTLs.
- **Surgical purge** runs after every prod deploy via `build.sh`, diffing the
  new build against the previous one and purging only changed URLs.

## Architecture

```
                     ┌──────────────────────────┐
   GET sindro.me/   │    Cloudflare edge       │
   ─────────────►   │  Cache Rule applies      │
                     │  edge_ttl=86400          │
                     │  browser_ttl=3600        │
                     └──────────┬───────────────┘
                                │ cache MISS or expired
                                ▼
                     ┌──────────────────────────┐
                     │   m42 nginx (origin)     │
                     │   serves Hugo public/    │
                     └──────────────────────────┘
```

- **m42** runs FreeBSD, nginx, Hugo. Two checkouts: `staging` (vjt.sindro.me)
  and `prod` (sindro.me). Both rebuild via `build.sh`.
- **Cloudflare** sits in front of `sindro.me` and `www.sindro.me`. Free tier.
- **Browsers** see whatever Cache Rule + origin negotiate.

Sibling subdomains have their own rules:

| Host                | Caching policy |
|---------------------|----------------|
| `sindro.me`, `www.` | Edge 1d, browser 1h (this doc) |
| `vjt.sindro.me`     | Staging — bypass everything |
| `remark.sindro.me`  | See "Remark42 rules" below |
| `noema.sindro.me`   | Untouched |

## Why edge long, browser short

The asymmetry isn't arbitrary — it follows from one fact:

> **Edge cache is purgeable. Browser cache is not.**

Once a browser caches a response, only its own TTL or a hard reload evicts it.
We can't reach into a returner's browser to fix a typo. So browser TTL must be
short enough that "I just fixed a typo" doesn't haunt readers for hours.

The edge is the opposite: a single API call evicts any URL within seconds.
That makes long edge TTLs safe — staleness is bounded by purge reliability,
not by the TTL ceiling.

So:

- **Browser 1h** — small enough that post-edit staleness is bounded, large
  enough that a returner navigating the site for ten minutes hits cache.
- **Edge 1d** — large enough that cache hit ratio approaches 1, small enough
  that a missed purge auto-heals within a day.

If you flip this (browser long, edge short), you get the worst of both:
returners stuck on stale content for ages and origin egress every hour for
every URL. Don't.

## Why `override_origin` (and not "respect origin Cache-Control")

Cloudflare's free tier doesn't cache HTML by default. Without an explicit
Cache Rule with `cache: true`, the edge skips HTML regardless of what origin
sends in `Cache-Control`. So we need a rule just to enable HTML caching.

Once we have a rule, `override_origin` mode lets edge TTL and browser TTL
diverge:

- `edge_ttl.mode = override_origin` → edge caches for `default` seconds, no
  matter what origin says.
- `browser_ttl.mode = override_origin` → CF rewrites the `Cache-Control`
  header sent to the browser to `max-age=<default>`.

A single `Cache-Control: max-age=N` at origin can't express "edge caches for
1d, browser for 1h". Cloudflare's rule can. That's the whole point.

If we *didn't* override:

- Origin sends `Cache-Control: public, max-age=14400` (4h, current nginx).
- Edge caches for some default (usually short for HTML on free tier).
- Browser caches for 4h.

That's strictly worse than the override pattern: edge undercaches, browser
overcaches.

## The Cache Rule

Zone: `0bd5bbe88a4795becad7618372827bb6`. Phase:
`http_request_cache_settings`. Rule ID: `28b5435411974ec5922ed575ba13b361`.

```json
{
  "description": "sindro.me + www — edge 1d, browser 1h",
  "expression": "(http.host in {\"sindro.me\" \"www.sindro.me\"})",
  "action": "set_cache_settings",
  "action_parameters": {
    "cache": true,
    "edge_ttl":    { "default": 86400, "mode": "override_origin" },
    "browser_ttl": { "default": 3600,  "mode": "override_origin" }
  }
}
```

To inspect or update, use the Cloudflare API directly with the `admin-token`
in `~/.config/cloudflare/admin-token` (Zone Cache Settings: Write scope).

## Remark42 rules

The `remark.sindro.me` host has separate rules in the same ruleset, summarized
here for completeness:

| Match                                                | Action |
|------------------------------------------------------|--------|
| `POST/PUT/DELETE/PATCH /api/v1/*`                    | bypass cache |
| `GET /api/v1/find` `/api/v1/last` `/api/v1/info`     | edge+browser 30s |
| `/web/*`, `/embed.js`, `/counter.js`                 | edge 1d, browser 1h |
| `/web/remark.css`                                    | bypass (per-site CSS via `Vary: Referer`) |
| `/web/iframe.html`                                   | bypass (per-URI Referrer-Policy + Cache-Control overrides at origin) |

## Purge strategy

### `cf-purge.py` — surgical, runs after every prod deploy

Hashes the new `public/` against the old `public_old_<pid>/` (kept around by
`build.sh`'s atomic-swap), diffs, and purges only changed URLs.

**Tracked file types:**

- **Text**: `.html`, `.xml` (posts, indexes, tag pages, sitemap, RSS, atom).
- **Binary** (non-fingerprinted): `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`,
  `.svg`, `.ico`, `.pdf`, `.asc`, `.pub`, `.txt`, `.mp3`.

**Skipped:**

- **Hugo-fingerprinted** assets: `*_hu_<hash>.{webp,jpg,…}`,
  `js/bundle.<hash>.js`, `fonts/*.woff2`. These ride a new URL when content
  changes, so the old URL has no live cache entry to purge — it just becomes
  an orphan.
- **Videos** (`.mp4`, LFS-tracked): big, ~never edited in place, hashing them
  is expensive for zero benefit.

**Scope**: filtered to the apex hostname only (sibling subdomains untouched).

**First-run behavior**: with no old manifest, emits the full URL list. CF
treats unknown URLs as no-ops, so this is safe and idempotent.

**Failure mode**: raises on CF API errors, which fails `build.sh`. You notice.
With edge TTL 1d, a missed purge means up to 24h of stale content — that's
the upper bound, and it's loud.

### `cf-purge-static.py` — header-policy changes

The orthogonal case: response *headers* change on stable fingerprinted URLs.
Example: nginx Cache-Control was bumped, or `immutable` was added/removed.

`cf-purge.py` won't notice — content hash is unchanged, only headers shifted.
`cf-purge-static.py` walks the build dir and force-purges every fingerprinted
URL family (`fonts/*.woff2`, `js/bundle.*.js`, `*_hu_<hash>.*`), causing edge
to re-fetch with the new headers.

Run only when header policy changes. Routine deploys don't need it.

## Why hash-based diff and not git history?

Source-to-output is a graph, not a 1:1 mapping. A single source change can
fan out:

- Editing `content/posts/foo/index.en.md` → `/posts/foo/`, `/posts/`, `/`,
  every `/tags/X/` for each tag, `/index.xml`, `/sitemap.xml`, language nav,
  Pagefind index.
- Bumping the theme submodule → potentially every page.
- `config.toml` or `i18n/*.yaml` → wide blast radius.
- Shortcode change → every caller.

There's also build-time variance with no git diff at all:
`{{< years-since >}}` and `{{< age >}}` shortcodes change output yearly.
`lastmod`, paginator, Pagefind index drift without commits.

Git-based purge would also need state bookkeeping (last-deployed commit) and
fail-safe handling for partial deploys.

Hash-based diff is dumb but correct: it sees what actually changed at the
wire, regardless of cause. Sub-second on m42 (text + ~290 binaries, mp4
excluded). Self-healing.

## Operational notes

### When you change something

| Change                          | What to do |
|---------------------------------|------------|
| Edit a post, add a post, etc.   | `build.sh` runs `cf-purge.py` automatically. Done. |
| Replace an image at the same URL | `cf-purge.py` now handles this since binary diffing was added. Done. |
| Bump nginx Cache-Control on `/static/`  | `cf-purge-static.py` once. |
| Theme change touching layouts   | `build.sh` runs `cf-purge.py`. Diff catches everything. |
| Cache Rule itself                | Edit via CF dashboard or API. No purge needed — TTLs apply on next miss. |

### Monitoring

- `cf-cache-status` header: `HIT` / `MISS` / `EXPIRED` / `BYPASS`. Sanity check
  with `curl -sI https://sindro.me/`.
- Cloudflare dashboard → Caching → Overview: hit ratio should be high (>90%)
  for the apex.
- A 24h drop in hit ratio after a deploy = `cf-purge.py` over-purged. Likely
  cause: a build emitted spurious diffs (e.g., a non-deterministic Hugo build).

### Manual purge

If something is wrong and you need to nuke the apex cache:

```bash
TOKEN=$(cat ~/.config/cloudflare/admin-token)
ZONE=0bd5bbe88a4795becad7618372827bb6
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/purge_cache"
```

Last resort. Dumps every cache entry in the zone, including `remark.` and
`vjt.`. Cold-start hits origin hard for a few minutes after.

## Future considerations

- **Stale-while-revalidate**: CF supports `serve_stale` config in cache rules.
  Could be useful if origin egress becomes a concern. Currently not enabled.
- **Tiered caching**: free tier doesn't get it. Paid plans serve more requests
  from regional caches before falling back to origin.
- **Cache-Tag headers**: Enterprise feature. Would let us purge by tag (e.g.,
  "all pages tagged `ruby`") instead of by URL list. Overkill for this site.
