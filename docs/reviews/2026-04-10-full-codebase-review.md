# Full Codebase Review: sindro.me + sindrome theme

**Date:** 2026-04-10
**Reviewer:** Claude Opus 4.6 (5 parallel agents)
**Scope:** config, build scripts, theme layouts, CSS/JS assets, i18n, content, deprecated patterns

---

## Status

- [x] Dead CSS / legacy cleanup (shipped 2026-04-10)
- [x] Resume layout duplicates baseof.html (shipped 2026-04-10)
- [x] Hugo deprecations (.Scratch, .Page.Store — shipped 2026-04-10; Pager .URL not available in v0.154)
- [x] HTML deprecations (align, a name, language attr — shipped 2026-04-10)
- [ ] Theme reusability (hardcoded sindro.me values)
- [ ] Pagefind migration to Component UI
- [x] JS fixes (toc.js globals, boot-splash storage mismatch — shipped 2026-04-10)
- [x] Config cleanup (dead category taxonomy, Italian description — shipped 2026-04-10)
- [x] Content fixes (banip featuredImage path — shipped 2026-04-10)
- [ ] Minor cleanups (dead i18n keys, inline styles, etc.)

---

## CRITICAL (5)

| # | Area | File | Issue | Status |
|---|------|------|-------|--------|
| 1 | Layouts | `resume/resume.html` | **Duplicates entire `baseof.html` scaffold** instead of using `{{ define "main" }}`. Any change to baseof requires a parallel change here. | FIXED |
| 2 | CSS | `assets/css/legacy/` | **1145 lines of dead CSS** -- poole.css, hyde.css, poison.css, custom.css not loaded by `stylesheets.html`. | FIXED |
| 3 | CSS | `components.css` vs templates | **Class name mismatch between new CSS and old HTML.** CSS targets `.sidebar-nav-heading`, `.sidebar-nav-item`, `.sidebar-socials`, `.newsletter-form`, `.resume-buttons` -- but templates use `.heading`, `.bullet`, `.social`, `.newsletters`, `.resume-download`. Investigation showed elements look fine via generic/inherited styles; dead CSS removed. | FIXED |
| 4 | Pagefind | `head/scripts.html:24-35` | **Legacy Pagefind UI** (`pagefind-ui.js` / `PagefindUI` constructor) deprecated since v1.5.0. Should migrate to Component UI (`pagefind-modular-ui.js`). | |
| 5 | CSS | `fonts.css:37-72` | **PT Sans loaded but never used.** Four `@font-face` declarations for a font referenced by zero CSS rules. Also removed `.woff` fallbacks and `local('')` hack. | FIXED |

## IMPORTANT (18)

| # | Area | File:Line | Issue |
|---|------|-----------|-------|
| 6 | Theme reuse | `resume.html`, `about.html` | Hardcoded `/vjt.jpg`, `"Marcello Barnaba"`, PDF paths, post URLs -- should use `.Site.Params` |
| 7 | Theme reuse | `boot-splash.html:3`, `boot-splash.js:23,31` | Hardcoded `sindro.me` brand and hostname |
| 8 | Theme reuse | `scripts.html:17` | Hardcoded `sindro.me` and GitHub URL in console easter egg |
| 9 | Hugo deprecated | `head/meta.html` (22 sites) | `.Scratch.Set`/`.Get`/`.Add` -- use `newScratch` or local `$variables` |
| 10 | Hugo deprecated | `index.html:43-63`, `pagination.html:8-19` | Pager `.URL` deprecated -- use `.PageURL` |
| 11 | Hugo deprecated | `mermaid.html`, `plantuml.html` | `.Page.Scratch` deprecated |
| 12 | HTML deprecated | `light_dark.html:1` | `align="right"` -- use CSS |
| 13 | HTML deprecated | `comments.html:2` | `<a name="comments">` -- use `id=` instead |
| 14 | HTML deprecated | `plantuml.html:8` | `language="javascript"` attribute |
| 15 | Config | `config.toml:40` | `category = 'categories'` declared but never used, generates empty taxonomy pages |
| 16 | Config | `config.toml:69` | Italian `description` is English ("feeling bold on the internet") |
| 17 | JS bug | `toc.js:23` | `nav_ref` assigned without `let`/`const` -- implicit global |
| 18 | JS bug | `boot-splash.js` vs `baseof.html:4` | `localStorage` in JS vs `sessionStorage` in inline script -- splash DOM flashes on every navigation |
| 19 | Duplication | `index.html:29-68` | Desktop TOC and mobile TOC are ~38 lines of copy-paste |
| 20 | Duplication | `layout.css:207-235` + `components.css:743-757` | Identical scrollbar rules in both files -- FIXED (removed from components.css) |
| 21 | Scripts | `resume-pdf.py:137,147` | Hardcoded `sindro.me` URL -- ignores configurable `baseURL` |
| 22 | Scripts | `resume-pdf.py:97-102` | Locale hack: `text.replace(" months", " mesi")` -- fragile string replacement |
| 23 | Content | `banip-icmp-mwan3` posts | Absolute `featuredImage` path instead of relative `cover.jpg` -- breaks Hugo resource pipeline |

## SUGGESTIONS (15)

| # | Area | Issue |
|---|------|-------|
| 24 | Config | `dark_mode = true` is vestigial -- JS overrides it immediately |
| 25 | Config | Reinvented menu system (custom params array instead of Hugo's built-in `[menu]`) |
| 26 | i18n | Dead keys: `mins_read` and `about` |
| 27 | HTML | `list.html:7` -- `<h3>` directly inside `<ul>` (invalid), plus inline `style=` |
| 28 | HTML | `head.html:2` -- XHTML `xmlns` and `xml:lang` unnecessary in HTML5 |
| 29 | HTML | `head.html:7` -- `http-equiv="content-type"` legacy form |
| 30 | HTML | `plantuml.html:12-13` -- duplicate `id` attribute on span and img |
| 31 | CSS | `fonts.css` -- `local('')` hack and `.woff` fallbacks unnecessary -- FIXED |
| 32 | CSS | `components.css:390` -- `::-webkit-details-marker` redundant (already `list-style: none`) |
| 33 | CSS | `codeblock.css:60-126` -- syntax highlighting colors have no dark mode support |
| 34 | CSS | `layout.css:14,136` and `layout.css:22,139` -- duplicate `html` and `body` selector blocks |
| 35 | JS | `toc.js` not wrapped in IIFE (unlike all other JS files) |
| 36 | JS | `codeblock.js` -- clipboard API fails silently on non-HTTPS |
| 37 | Build | `build.sh:18` -- Pagefind glob lists every section twice (EN + IT) |
| 38 | Shortcode | `retrospective.html:4` -- hardcoded `"2026"` default year |

## The Big Picture

The codebase has two layers of debt:

1. **The CSS rewrite was half-finished.** New CSS files (`layout.css`, `components.css`) were written with new class names, but the HTML templates still used the old Poison-era class names. The legacy CSS directory was correctly removed from the bundle, but the template-to-CSS contract was never updated. Investigation showed elements render fine via generic/inherited styles -- the speculative CSS selectors were dead code and have been removed.

2. **Theme reusability is a fiction.** Despite being published on GitHub as a reusable theme, there are ~15 hardcoded references to `sindro.me`, `vjt.jpg`, specific post URLs, Italian-specific strings outside i18n, and site-specific boot splash messages. The theme works for exactly one site.

The Hugo deprecations (.Scratch, Pager .URL) and HTML deprecations (align, name) are straightforward find-and-replace fixes. The Pagefind migration is a medium effort. The resume layout refactor (extending baseof instead of duplicating it) is the highest-impact structural fix remaining.

### Additional deprecation notes

- **Pagefind**: `pagefind-ui.js`/`pagefind-ui.css` and `PagefindUI` constructor are deprecated in favor of Component UI (`pagefind-modular-ui.js`). All `pagefind-ui__*` CSS selectors will need updating.
- **Hugo**: `.Scratch` deprecated in favor of `newScratch`; Pager `.URL` deprecated in favor of `.PageURL`; `.Page.Scratch` in shortcodes deprecated.
- **HTML5**: `<a name="">` obsolete (use `id=`); `align=""` attribute deprecated; `language="javascript"` deprecated; `xmlns`/`xml:lang` unnecessary; `http-equiv="content-type"` legacy form.
- **CSS**: `::-webkit-details-marker` redundant when `list-style: none` is set; `-ms-text-size-adjust` dead (IE Mobile); `word-wrap` is legacy name for `overflow-wrap`.
- **JS**: `toc.js` leaks globals (`nav_ref` undeclared, `activeElement` in module scope); `boot-splash.js` uses `localStorage` but `baseof.html` checks `sessionStorage`.
