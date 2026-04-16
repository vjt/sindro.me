# Tag Cloud — Fancier Classic Cloud with Filter

**Date:** 2026-04-16
**Target:** `themes/sindrome/` (submodule)
**Status:** Design approved

## Goal

Replace the flat, unstyled tag cloud on `/tags/` (and `/it/tags/`) with a classic
Web 2.0-era alphabetical cloud that is:

- **Fancier** — sqrt-scaled size, opacity ramp, font weight ramp, staggered
  fade-in animation, hover lift.
- **Useful on mobile** — finger-friendly tap targets, sticky filter input, no
  iOS zoom on focus, responsive to narrow viewports.
- **Browseable** — instant text filter and a sort toggle (A–Z default, swap to
  count).

Keep the alphabetical default because that is the "classic" tag cloud aesthetic
(del.icio.us / Flickr origin) — big and small tags mixed naturally.

## Non-goals

- No 3D / three.js / canvas.
- No co-occurrence graph, no related-tag suggestions.
- No tag-page redesign (individual tag pages stay as-is).
- No server-side rendering of filter state; filter is JS-only.

## Architecture

Single Hugo template change + one new CSS block + one small vanilla JS file.

```
themes/sindrome/
├── layouts/_default/terms.html          ← modified
├── assets/css/components.css            ← modified (.tag-cloud section)
└── assets/js/tag-cloud.js               ← NEW
i18n/
├── en.yaml                              ← add 3 strings
└── it.yaml                              ← add 3 strings
```

## Template (`layouts/_default/terms.html`)

Replace the current simple loop with:

1. Compute `$largest` and `$smallest` counts.
2. Emit a sticky filter bar:
   - `<input type="search" class="tag-filter-input">` with i18n placeholder.
   - `<button class="tag-sort-btn" data-mode="alpha">` with i18n label.
3. Emit `<div class="tag-cloud">` sorted **alphabetically** (Hugo template sort).
4. For each term emit:
   ```html
   <a href="{{ .Page.RelPermalink }}"
      class="tag-cloud-item"
      data-name="{{ lower .Page.Title }}"
      data-count="{{ $count }}"
      style="font-size:{{ $size }}rem;font-weight:{{ $weight }};opacity:{{ $opacity }};--anim-delay:{{ $i }};">
     {{ .Page.Title }}<sup>{{ $count }}</sup>
   </a>
   ```
   where:
   - `$t = sqrt((count - min) / (max - min))` clamped to `[0, 1]`.
   - `$size = 0.75 + $t * 1.45` (range 0.75rem → 2.20rem).
   - `$opacity = 0.55 + $t * 0.45` (range 0.55 → 1.00).
   - `$weight = 400 + round(raw_t * 3) * 100` (400 / 500 / 600 / 700 stepped).
5. Emit empty-state `<p class="tag-cloud-empty" hidden>` (i18n).
6. Load `tag-cloud.js` at end (via Hugo `resources.Get | minify | fingerprint`).
7. Wrap whole thing in `<div data-pagefind-ignore>`.

All math done in Hugo templating with `math.Sqrt`, `math.Round`, etc. — no
client-side layout computation.

## CSS (`assets/css/components.css`, `.tag-cloud` section)

Replace the existing `.tag-cloud` / `.tag-cloud-item` / `:hover` / `sup` block
with:

- `.tag-filter-bar` — sticky, flex row, bg matches page, border-bottom.
  Respects responsive header on mobile (top offset via media queries if needed).
- `.tag-filter-input` — `font-size: 16px` (prevents iOS zoom), flex: 1,
  rounded, focus ring uses `--link-color`.
- `.tag-sort-btn` — `min-height: 44px`, rounded pill, hover brightens border.
- `.tag-cloud` — `flex-wrap`, `align-items: baseline`, gap tuned for density
  without feeling cramped.
- `.tag-cloud-item`:
  - Padding `0.15rem 0.35rem` (enlarges tap target).
  - `color: var(--link-color)`.
  - `transition: transform 0.15s, opacity 0.15s`.
  - `animation: tagFadeIn 0.4s both`.
  - `animation-delay: calc(var(--anim-delay) * 12ms)`.
  - `:hover` — `transform: translateY(-2px)`, underline.
  - `[hidden]` — `display: none` (removes from flex layout, so remaining tags reflow).
- `.tag-cloud-item sup` — small, muted, vertical-align super.
- `.tag-cloud-empty` — centered, muted, padded.
- `@keyframes tagFadeIn` — animates `transform` only
  (`from { transform: translateY(4px) } to { transform: translateY(0) }`).
  Opacity is set by inline style from the template and is not animated, so
  the per-tag opacity ramp survives the animation and any subsequent filter
  show/hide. A short `opacity` transition on the item class handles
  hover/filter smoothness.

## JS (`assets/js/tag-cloud.js`)

Vanilla, ~1KB, no deps. Runs only if `.tag-cloud` present on the page.

```js
(function() {
  const cloud = document.querySelector('.tag-cloud');
  if (!cloud) return;
  const filter = document.querySelector('.tag-filter-input');
  const sortBtn = document.querySelector('.tag-sort-btn');
  const empty = document.querySelector('.tag-cloud-empty');
  const items = Array.from(cloud.querySelectorAll('.tag-cloud-item'));

  // Filter — case-insensitive substring on data-name.
  filter.addEventListener('input', () => {
    const q = filter.value.trim().toLowerCase();
    let shown = 0;
    items.forEach(el => {
      const match = el.dataset.name.includes(q);
      el.hidden = !match;
      if (match) shown++;
    });
    empty.hidden = shown !== 0;
  });

  // Sort toggle — alpha ↔ count.
  // Read localized labels from data attrs on the button (set by template).
  sortBtn.addEventListener('click', () => {
    const mode = sortBtn.dataset.mode === 'alpha' ? 'count' : 'alpha';
    sortBtn.dataset.mode = mode;
    sortBtn.textContent = sortBtn.dataset['label' + (mode === 'alpha' ? 'Alpha' : 'Count')];
    const sorted = items.slice().sort((a, b) =>
      mode === 'alpha'
        ? a.dataset.name.localeCompare(b.dataset.name)
        : parseInt(b.dataset.count) - parseInt(a.dataset.count)
    );
    sorted.forEach(el => cloud.appendChild(el));
  });
})();
```

Button carries both labels in data attrs so JS can swap text without fetching i18n:

```html
<button class="tag-sort-btn"
        data-mode="alpha"
        data-label-alpha="{{ i18n "sort_alpha" }}"
        data-label-count="{{ i18n "sort_count" }}">
  {{ i18n "sort_alpha" }}
</button>
```

## i18n

`i18n/en.yaml`:
```yaml
- id: tag_filter_placeholder
  translation: "Filter tags…"
- id: sort_alpha
  translation: "Sort: A–Z"
- id: sort_count
  translation: "Sort: by count"
- id: tag_cloud_empty
  translation: "No tags match."
```

`i18n/it.yaml`:
```yaml
- id: tag_filter_placeholder
  translation: "Filtra i tag…"
- id: sort_alpha
  translation: "Ordina: A–Z"
- id: sort_count
  translation: "Ordina: per numero"
- id: tag_cloud_empty
  translation: "Nessun tag corrisponde."
```

## Fallback (no-JS)

- Filter bar still renders but is inert. Acceptable: no-JS user sees the full
  alphabetical cloud and can Ctrl-F to find a tag.
- Alternative: hide filter bar entirely with `<noscript><style>.tag-filter-bar{display:none}</style></noscript>`.
- Go with the `<noscript>` hide — cleaner; no visible controls that don't work.

## Mobile specifics

- Filter input `font-size: 16px` (blocks iOS zoom-on-focus).
- Sort button `min-height: 44px` (Apple HIG tap target).
- Tag item padding `0.15rem 0.35rem` on existing font size gives an acceptable
  tap area even for the smallest tags.
- Filter bar sticky at top of scroll container — respects any responsive header
  already in the theme (no custom top offset unless observed broken in testing).
- Gap `0.25rem 0.65rem` is tight enough on phones to avoid a sparse look with
  small tags.

## Build / bundle

- JS via `resources.Get "js/tag-cloud.js" | minify | fingerprint`.
- Emit with `defer`.
- Only emitted by `terms.html` — not on every page.
- Pagefind: the whole cloud is wrapped in `data-pagefind-ignore` so tags do
  not pollute the search index.

## Testing plan (manual)

- Build locally on m42 via `build.sh`, view on staging.
- Desktop: `/tags/` and `/it/tags/` — filter, sort, hover, dark/light mode.
- Mobile: Chrome devtools emulate iPhone — no zoom on input focus, tap targets
  finger-reachable, filter sticky survives scroll.
- no-JS: disable JS in devtools, confirm filter bar hidden, cloud renders
  alphabetical with full sizing/opacity.

## Risks / open questions

- **Animation on filter reflow** — when items are hidden, the staggered
  fade-in uses original indices, which is fine (animation only runs once on
  page load). No re-animation on filter.
- **Sticky filter under responsive header** — the theme has a responsive
  header below 1200px. Need to check if `top: 0` conflicts or needs
  `top: <header-height>`. Resolve during implementation by inspecting the
  layout in devtools; add a media-query top offset only if broken.
- **`data-name` case and Unicode** — use `lower` in Hugo and `.toLowerCase()`
  in JS. Italian tags with accents (if any) will match by raw substring; acceptable.
- **Submodule commit dance** — per repo conventions, all changes inside
  `themes/sindrome/` commit in the submodule first, then the parent repo
  bumps the submodule pointer.

## Out of scope (for later, if desired)

- Co-occurrence graph / related-tag hints.
- URL-persisted filter state (`?q=ruby`).
- Per-language tag separation (currently shared across `/tags/` and `/it/tags/`).
