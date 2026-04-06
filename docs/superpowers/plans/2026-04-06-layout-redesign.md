# Layout Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the legacy Hyde/Poole CSS with a modern CSS Grid layout, light-first color scheme with system-aware dark mode, hamburger menu below 1200px, and right-side TOC on wide screens.

**Architecture:** CSS rewrite (approach B) — templates stay mostly the same, CSS is rewritten from scratch. Two new CSS files (`layout.css`, `components.css`) replace four old ones (`poole.css`, `hyde.css`, `poison.css`, `custom.css`). One new partial (`header.html`), one new JS file (`hamburger.js`), and a rewritten `light_dark.js`.

**Tech Stack:** Hugo templates, CSS Grid, vanilla JS, Hugo Pipes (concat/minify/fingerprint)

**Spec:** `docs/superpowers/specs/2026-04-06-layout-redesign-design.md`

---

## File Map

### Created
- `themes/poison/assets/css/layout.css` — CSS Grid, breakpoints, responsive tiers
- `themes/poison/assets/css/components.css` — All UI components (nav, tags, post list, search, etc.)
- `themes/poison/layouts/partials/header.html` — Responsive header bar with hamburger
- `themes/poison/assets/js/hamburger.js` — Menu toggle, overlay, Escape, focus trap

### Modified
- `themes/poison/layouts/_default/baseof.html` — New structure with header + grid
- `themes/poison/layouts/partials/head/css.html` — Light-first palette + prefers-color-scheme
- `themes/poison/layouts/partials/head/stylesheets.html` — New CSS bundle
- `themes/poison/layouts/partials/head/scripts.html` — Add hamburger.js to bundle
- `themes/poison/assets/js/light_dark.js` — System preference detection
- `themes/poison/assets/css/codeblock.css` — Minor border-radius tweaks
- `themes/poison/layouts/partials/language_switcher.html` — Bigger tap targets (class update)

### Moved to legacy (safety net)
- `themes/poison/assets/css/legacy/poole.css`
- `themes/poison/assets/css/legacy/hyde.css`
- `themes/poison/assets/css/legacy/poison.css`
- `themes/poison/assets/css/legacy/custom.css`

### Untouched
- `themes/poison/assets/css/fonts.css`
- `themes/poison/layouts/partials/sidebar/sidebar.html` (and all sub-partials)
- `themes/poison/layouts/partials/post/*`
- `themes/poison/layouts/_default/single.html`
- `themes/poison/layouts/_default/list.html`
- `themes/poison/layouts/index.html`
- All shortcodes, content files, config.toml

---

### Task 1: Move old CSS to legacy and create empty new files

**Files:**
- Move: `themes/poison/assets/css/poole.css` → `themes/poison/assets/css/legacy/poole.css`
- Move: `themes/poison/assets/css/hyde.css` → `themes/poison/assets/css/legacy/hyde.css`
- Move: `themes/poison/assets/css/poison.css` → `themes/poison/assets/css/legacy/poison.css`
- Move: `themes/poison/assets/css/custom.css` → `themes/poison/assets/css/legacy/custom.css`
- Create: `themes/poison/assets/css/layout.css`
- Create: `themes/poison/assets/css/components.css`

- [ ] **Step 1: Create legacy directory and move old CSS**

```bash
cd themes/poison/assets/css
mkdir -p legacy
git mv poole.css legacy/poole.css
git mv hyde.css legacy/hyde.css
git mv poison.css legacy/poison.css
git mv custom.css legacy/custom.css
```

- [ ] **Step 2: Create empty layout.css with section headers**

Create `themes/poison/assets/css/layout.css`:
```css
/* ==========================================================================
   layout.css — CSS Grid system, breakpoints, responsive layout
   Replaces: poole.css (reset/base) + hyde.css (sidebar layout)
   ========================================================================== */

/* --- Reset & Base --- */

/* --- Grid Layout --- */

/* --- Sidebar --- */

/* --- Content --- */

/* --- TOC Column --- */

/* --- Header Bar (< 1200px) --- */

/* --- Hamburger Slide-out --- */

/* --- Responsive: Tablet (600-1199px) --- */

/* --- Responsive: Phone (< 600px) --- */
```

- [ ] **Step 3: Create empty components.css with section headers**

Create `themes/poison/assets/css/components.css`:
```css
/* ==========================================================================
   components.css — UI components
   Replaces: poison.css + custom.css
   ========================================================================== */

/* --- Typography --- */

/* --- Dark/Light Toggle --- */

/* --- Language Switcher --- */

/* --- Navigation Menu --- */

/* --- Search (Pagefind) --- */

/* --- Post Info & Meta --- */

/* --- Tags --- */

/* --- Post List (index) --- */

/* --- Entry List (archives) --- */

/* --- Pagination --- */

/* --- Table of Contents --- */

/* --- Tables --- */

/* --- Blockquotes --- */

/* --- Images --- */

/* --- Comments (Remark42) --- */

/* --- Newsletter (Listmonk) --- */

/* --- Resume Page --- */

/* --- Socials --- */

/* --- Footer / Copyright --- */

/* --- Scrollbar --- */
```

- [ ] **Step 4: Update stylesheets.html to use new files**

Modify `themes/poison/layouts/partials/head/stylesheets.html`:
```html
{{ $css_bundle := slice
    (resources.Get "css/layout.css")
    (resources.Get "css/components.css")
    (resources.Get "css/codeblock.css")
    (resources.Get "css/fonts.css")
  | resources.Concat "css/bundle.css" | minify | fingerprint }}

<link type="text/css" rel="stylesheet" href="{{ $css_bundle.RelPermalink }}">
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: move legacy CSS, scaffold new layout.css and components.css"
```

---

### Task 2: Write layout.css — Reset, Grid, and Desktop Layout

**Files:**
- Modify: `themes/poison/assets/css/layout.css`

- [ ] **Step 1: Write the reset and base styles**

Add to the `Reset & Base` section of `layout.css`:
```css
/* --- Reset & Base --- */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  font-weight: 300;
  line-height: 1.7;
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  color: var(--text-color);
  background-color: var(--bkg-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: var(--link-color);
  text-decoration: none;
}

a:hover,
a:focus {
  text-decoration: underline;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--text-color);
}

h1 { font-size: 1.75rem; font-weight: 700; }
h2 { font-size: 1.375rem; }
h3 { font-size: 1.125rem; }
h4, h5, h6 { font-size: 1rem; }

p {
  margin-top: 0;
  margin-bottom: 1rem;
}

strong { color: var(--text-color); }

ul, ol {
  margin-top: 0;
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

li { color: var(--list-color); }
li > p { color: var(--list-color); }

blockquote {
  margin: 0 0 1rem;
  padding: 0.5rem 1rem;
  border-left: 3px solid var(--link-color);
  color: var(--list-color);
}

pre {
  margin-top: 0;
  margin-bottom: 1rem;
  overflow-x: auto;
  font-size: 0.8rem;
  line-height: 1.4;
}

code {
  font-family: Menlo, Monaco, "Courier New", monospace;
  font-size: 85%;
  color: var(--code-color);
  background-color: var(--code-background-color);
  padding: 0.15em 0.3em;
  border-radius: 3px;
}

pre code {
  padding: 0;
  background-color: transparent;
  color: var(--code-block-color);
}

hr {
  border: 0;
  border-top: 1px solid var(--table-border-color);
  margin: 1.5rem 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

thead th {
  border-bottom: 2px solid var(--table-border-color);
}

th, td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid var(--table-border-color);
}

tbody tr:nth-child(odd) {
  background-color: var(--table-stripe-color);
}

/* Smooth scrolling */
html { scroll-behavior: smooth; }
```

- [ ] **Step 2: Write the CSS Grid desktop layout**

Add to the `Grid Layout` section:
```css
/* --- Grid Layout --- */
body {
  display: grid;
  grid-template-columns: 220px 1fr 200px;
  grid-template-rows: 1fr;
  min-height: 100vh;
}

/* When there's no TOC (list pages, index), content spans both columns */
body:not(.has-toc) {
  grid-template-columns: 220px 1fr;
}
```

- [ ] **Step 3: Write sidebar layout styles**

Add to the `Sidebar` section:
```css
/* --- Sidebar --- */
.sidebar {
  grid-column: 1;
  grid-row: 1;
  background-color: var(--sidebar-bg-color);
  border-right: 1px solid var(--table-border-color);
  overflow-y: auto;
  height: 100vh;
  position: sticky;
  top: 0;
}

.sidebar-sticky {
  padding: 1.5rem 1rem;
}

.sidebar .brand {
  font-family: "Abril Fatface", serif;
  font-size: 1.8em;
  font-weight: 400;
  margin: 0;
}

.sidebar .brand a {
  color: var(--sidebar-h1-color);
  text-decoration: none;
}

.sidebar .lead {
  font-size: 0.85rem;
  font-weight: 300;
  color: var(--sidebar-p-color);
  margin: 0.25rem 0 1rem;
}

.sidebar a {
  color: var(--sidebar-a-color);
}

.sidebar p,
.sidebar .footnote {
  color: var(--sidebar-p-color);
  font-size: 0.8rem;
}

.sidebar-about img {
  display: block;
  width: 150px;
  height: 150px;
  margin: 0 auto 0.5rem;
  border-radius: 50%;
  border: 3px solid var(--sidebar-img-border-color);
}

/* Scrollbar */
.sidebar::-webkit-scrollbar { width: 6px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb {
  background: rgba(128,128,128,0.3);
  border-radius: 3px;
}
```

- [ ] **Step 4: Write content area styles**

Add to the `Content` section:
```css
/* --- Content --- */
.content.container {
  grid-column: 2;
  grid-row: 1;
  overflow-y: auto;
  height: 100vh;
  padding: 2rem 2rem 2rem 2.5rem;
}

.content.container > * {
  max-width: 52rem;
}

/* Scrollbar */
.content.container::-webkit-scrollbar { width: 6px; }
.content.container::-webkit-scrollbar-track { background: transparent; }
.content.container::-webkit-scrollbar-thumb {
  background: rgba(128,128,128,0.2);
  border-radius: 3px;
}
```

- [ ] **Step 5: Write TOC column styles**

Add to the `TOC Column` section:
```css
/* --- TOC Column --- */
.article-toc {
  grid-column: 3;
  grid-row: 1;
  height: 100vh;
  overflow-y: auto;
  padding: 2rem 1rem;
  border-left: 1px solid var(--table-border-color);
  font-size: 0.8rem;
}

.article-toc .toc-wrapper {
  position: sticky;
  top: 2rem;
}

.article-toc #TableOfContents ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.article-toc #TableOfContents ul ul {
  padding-left: 1rem;
}

.article-toc #TableOfContents a {
  color: var(--list-color);
  text-decoration: none;
  display: block;
  padding: 0.25rem 0;
  line-height: 1.4;
  transition: color 0.15s;
}

.article-toc #TableOfContents a:hover {
  color: var(--link-color);
}

.article-toc #TableOfContents a.active {
  color: var(--link-color);
  font-weight: 500;
}

.article-toc .inactive a {
  opacity: 0.5;
}

/* Hide TOC column when body doesn't have it */
body:not(.has-toc) .article-toc {
  display: none;
}
```

- [ ] **Step 6: Build and verify desktop layout renders**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

Expected: Hugo builds successfully (warnings OK, errors not OK).

- [ ] **Step 7: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: layout.css — reset, CSS Grid, desktop 3-column layout"
```

---

### Task 3: Write layout.css — Header Bar, Hamburger, and Responsive

**Files:**
- Modify: `themes/poison/assets/css/layout.css`

- [ ] **Step 1: Write the header bar styles**

Add to the `Header Bar` section of `layout.css`:
```css
/* --- Header Bar (< 1200px) --- */
.site-header {
  display: none; /* Hidden on desktop */
}

/* Hide mobile-header (legacy, replaced by .site-header) */
.mobile-header {
  display: none;
}
```

- [ ] **Step 2: Write the hamburger slide-out styles**

Add to the `Hamburger Slide-out` section:
```css
/* --- Hamburger Slide-out --- */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
}

body.menu-open .sidebar-overlay {
  display: block;
}
```

- [ ] **Step 3: Write tablet/landscape responsive tier**

Add to the `Responsive: Tablet` section:
```css
/* --- Responsive: Tablet (600-1199px) --- */
@media (max-width: 1199px) {
  body {
    display: block;
    min-height: auto;
  }

  .site-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 0.6rem 1rem;
    background: var(--bkg-color);
    border-bottom: 1px solid var(--table-border-color);
  }

  .site-header .header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .site-header .hamburger-btn {
    background: none;
    border: none;
    font-size: 1.4rem;
    cursor: pointer;
    padding: 0.25rem;
    color: var(--text-color);
    line-height: 1;
  }

  .site-header .header-brand {
    font-family: "Abril Fatface", serif;
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--text-color);
    text-decoration: none;
  }

  .site-header .header-payoff {
    color: var(--date-color);
    font-size: 0.8rem;
    flex: 1;
    text-align: center;
    padding: 0 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .site-header .header-right {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-shrink: 0;
  }

  /* Sidebar becomes off-canvas */
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    border-right: 1px solid var(--table-border-color);
    overflow-y: auto;
  }

  body.menu-open .sidebar {
    transform: translateX(0);
  }

  .sidebar .sidebar-close {
    display: block;
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--sidebar-p-color);
    line-height: 1;
    padding: 0.25rem;
  }

  /* Content takes full width */
  .content.container {
    height: auto;
    overflow-y: visible;
    padding: 1.5rem;
  }

  /* TOC becomes inline */
  .article-toc {
    height: auto;
    overflow-y: visible;
    border-left: none;
    border-bottom: 1px solid var(--table-border-color);
    padding: 1rem 1.5rem;
    font-size: 0.8rem;
    margin-bottom: 1rem;
  }

  .article-toc .toc-wrapper {
    position: static;
  }

  .article-toc summary {
    cursor: pointer;
    font-weight: 500;
    color: var(--text-color);
  }
}
```

- [ ] **Step 4: Write phone responsive tier**

Add to the `Responsive: Phone` section:
```css
/* --- Responsive: Phone (< 600px) --- */
@media (max-width: 599px) {
  .site-header {
    padding: 0.5rem 0.75rem;
  }

  .site-header .header-brand {
    font-size: 1rem;
  }

  .site-header .header-payoff {
    display: none;
  }

  .content.container {
    padding: 1rem;
  }

  .content.container > * {
    max-width: 100%;
  }

  .article-toc {
    padding: 0.75rem 1rem;
  }
}
```

- [ ] **Step 5: Add the sidebar close button hidden-by-default rule**

At the end of the `Sidebar` section (before the responsive sections), add:
```css
/* Close button only shows in hamburger mode */
.sidebar .sidebar-close {
  display: none;
}
```

- [ ] **Step 6: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 7: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: layout.css — header bar, hamburger slide-out, responsive breakpoints"
```

---

### Task 4: Write components.css — Typography, Navigation, and Post Styles

**Files:**
- Modify: `themes/poison/assets/css/components.css`

- [ ] **Step 1: Write typography and dark/light toggle styles**

Add to the `Typography` and `Dark/Light Toggle` sections:
```css
/* --- Typography --- */
.post-title, .post-title a {
  color: var(--post-title-color);
  text-decoration: none;
}

.post .post-title {
  margin-bottom: 0.25rem;
}

.post-date {
  display: block;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
  color: var(--date-color);
  font-size: 0.8rem;
}

.read-more-link {
  margin: 0.5rem 0 2rem;
}

.read-more-link a {
  font-size: 0.9rem;
}

/* --- Dark/Light Toggle --- */
.light-dark {
  display: inline-flex;
}

.btn-light-dark {
  background: none;
  border: 1px solid var(--table-border-color);
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  color: var(--text-color);
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}

.btn-light-dark:hover {
  background: var(--table-stripe-color);
}

.moon, .sun {
  display: block;
  width: 1em;
  height: 1em;
}

.sun { display: none; }
body.dark-theme .moon { display: none; }
body.dark-theme .sun { display: block; }
```

- [ ] **Step 2: Write language switcher styles**

Add to the `Language Switcher` section:
```css
/* --- Language Switcher --- */
.lang-switcher {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
}

.lang-current,
.lang-link {
  font-size: 18px;
  padding: 6px 10px;
  border-radius: 6px;
  text-decoration: none;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.lang-current {
  background: var(--link-color);
  opacity: 1;
}

.lang-link {
  background: var(--table-stripe-color);
  opacity: 0.7;
  transition: opacity 0.15s;
}

.lang-link:hover {
  opacity: 1;
  text-decoration: none;
}
```

- [ ] **Step 3: Write navigation menu styles**

Add to the `Navigation Menu` section:
```css
/* --- Navigation Menu --- */
.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
}

.sidebar-nav a {
  display: block;
  padding: 0.4rem 0;
  color: var(--sidebar-a-color);
  text-decoration: none;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

.sidebar-nav a:hover {
  color: var(--link-color);
}

.sidebar-nav .sidebar-nav-heading {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sidebar-p-color);
  margin-top: 1rem;
  margin-bottom: 0.25rem;
}

.sidebar-nav .sidebar-nav-item {
  padding-left: 0.75rem;
}

.sidebar-nav .sidebar-nav-item .pre {
  font-size: 0.7rem;
  color: var(--sidebar-p-color);
}
```

- [ ] **Step 4: Write search (Pagefind) styles**

Add to the `Search (Pagefind)` section:
```css
/* --- Search (Pagefind) --- */
#search {
  margin-bottom: 1rem;
}

#search .pagefind-ui__search-input {
  background: var(--bkg-color) !important;
  color: var(--text-color) !important;
  border: 1px solid var(--table-border-color) !important;
  border-radius: 6px !important;
  font-size: 0.85rem !important;
  padding: 0.5rem 0.75rem !important;
  width: 100% !important;
}

#search .pagefind-ui__search-clear {
  color: var(--text-color) !important;
}

#search .pagefind-ui__result-link {
  color: var(--link-color) !important;
}

#search .pagefind-ui__result-excerpt {
  color: var(--list-color) !important;
}
```

- [ ] **Step 5: Write post info, tags, and post list styles**

Add to the `Post Info`, `Tags`, and `Post List` sections:
```css
/* --- Post Info & Meta --- */
.post-info .featured-image img {
  width: 100%;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.post-info .reading-time {
  color: var(--date-color);
  font-size: 0.8rem;
}

/* --- Tags --- */
.tag-link,
.tag {
  display: inline-block;
  font-size: 0.75rem;
  background: var(--table-stripe-color);
  color: var(--list-color);
  padding: 0.15rem 0.6rem;
  border-radius: 4px;
  margin: 0.15rem 0.15rem 0.15rem 0;
  text-decoration: none;
  transition: background 0.15s;
}

.tag-link:hover,
.tag:hover {
  background: var(--table-border-color);
  text-decoration: none;
}

/* --- Post List (index) --- */
.posts .post {
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--table-border-color);
}

.posts .post:last-child {
  border-bottom: none;
}
```

- [ ] **Step 6: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 7: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: components.css — typography, nav, search, tags, post list"
```

---

### Task 5: Write components.css — Entry List, Pagination, Tables, Resume, Socials

**Files:**
- Modify: `themes/poison/assets/css/components.css`

- [ ] **Step 1: Write entry list (archive pages) styles**

Add to the `Entry List` section:
```css
/* --- Entry List (archives) --- */
.entries {
  list-style: none;
  padding: 0;
}

.entries li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 0.35rem 0;
  border-bottom: 1px dotted var(--table-border-color);
}

.entries li .title {
  flex: 1;
  min-width: 0;
}

.entries li .title a {
  color: var(--text-color);
  text-decoration: none;
}

.entries li .title a:hover {
  color: var(--link-color);
}

.entries li .published {
  flex-shrink: 0;
  margin-left: 1rem;
  color: var(--date-color);
  font-size: 0.8rem;
}

.entries h3 {
  margin-top: 2rem;
  color: var(--date-color);
  font-size: 1rem;
  font-weight: 400;
}
```

- [ ] **Step 2: Write pagination styles**

Add to the `Pagination` section:
```css
/* --- Pagination --- */
.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin: 2rem 0;
  font-size: 0.9rem;
}

.pagination a,
.pagination span {
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--table-border-color);
  border-radius: 4px;
  color: var(--text-color);
  text-decoration: none;
}

.pagination a:hover {
  background: var(--table-stripe-color);
  text-decoration: none;
}

.pagination .active {
  background: var(--link-color);
  color: #fff;
  border-color: var(--link-color);
}
```

- [ ] **Step 3: Write TOC component styles**

Add to the `Table of Contents` section:
```css
/* --- Table of Contents --- */
.article-toc h4 {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--date-color);
  margin-top: 0;
  margin-bottom: 0.75rem;
}
```

- [ ] **Step 4: Write resume page styles**

Add to the `Resume Page` section:
```css
/* --- Resume Page --- */
.resume-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.resume-photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.resume-section {
  margin-bottom: 2rem;
}

.resume-section h2 {
  border-bottom: 2px solid var(--table-border-color);
  padding-bottom: 0.25rem;
}

.resume-buttons {
  display: flex;
  gap: 0.75rem;
  margin: 1rem 0;
}

.resume-buttons a {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--link-color);
  border-radius: 6px;
  font-size: 0.85rem;
  color: var(--link-color);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.resume-buttons a:hover {
  background: var(--link-color);
  color: #fff;
}

.resume-footer-images {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.resume-footer-images img {
  height: 40px;
  width: auto;
}

/* Hide duplicate headshot on desktop (already in sidebar) */
@media (min-width: 1200px) {
  .resume-photo { display: none; }
}
```

- [ ] **Step 5: Write socials and footer styles**

Add to the `Socials` and `Footer / Copyright` sections:
```css
/* --- Socials --- */
.sidebar-socials {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.sidebar-socials a {
  color: var(--sidebar-socials-color);
  transition: opacity 0.15s;
}

.sidebar-socials a:hover {
  opacity: 0.7;
}

.sidebar-socials svg {
  width: 1.2em;
  height: 1.2em;
  vertical-align: middle;
}

/* --- Footer / Copyright --- */
.sidebar .blurb {
  font-size: 0.75rem;
  color: var(--sidebar-p-color);
}

.sidebar hr {
  border-color: rgba(128, 128, 128, 0.2);
}

.sidebar .glider-container {
  margin-top: 1rem;
}

.sidebar .glider-container img {
  width: 40px;
  height: 40px;
}

/* --- Scrollbar --- */
.content.container::-webkit-scrollbar,
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.content.container::-webkit-scrollbar-track,
.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.content.container::-webkit-scrollbar-thumb,
.sidebar::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.3);
  border-radius: 3px;
}
```

- [ ] **Step 6: Write newsletter (Listmonk) styles**

Add to the `Newsletter (Listmonk)` section:
```css
/* --- Newsletter (Listmonk) --- */
.newsletter-form {
  border: 1px solid var(--table-border-color);
  border-radius: 6px;
  padding: 1.5rem;
  margin: 2rem 0;
  background: var(--table-stripe-color);
}

.newsletter-form input[type="email"] {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--table-border-color);
  border-radius: 4px;
  font-size: 0.9rem;
  width: 100%;
  max-width: 300px;
  background: var(--bkg-color);
  color: var(--text-color);
}

.newsletter-form button {
  padding: 0.5rem 1rem;
  background: var(--link-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
```

- [ ] **Step 7: Write image and blockquote styles**

Add to the `Images` and `Blockquotes` sections:
```css
/* --- Images --- */
.post img {
  border-radius: 6px;
  margin: 1rem 0;
}

/* --- Blockquotes --- */
blockquote p:last-child {
  margin-bottom: 0;
}
```

- [ ] **Step 8: Write post navigation styles**

Add before the Resume section:
```css
/* --- Post Navigation --- */
.post-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--table-border-color);
  font-size: 0.9rem;
}

.post-navigation .prev,
.post-navigation .next {
  max-width: 45%;
}

.post-navigation .label {
  font-size: 0.75rem;
  color: var(--date-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* --- Categories list on post --- */
.post-categories {
  margin-top: 1rem;
  font-size: 0.85rem;
}

/* --- Series --- */
.post-series {
  border: 1px solid var(--table-border-color);
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  background: var(--table-stripe-color);
}
```

- [ ] **Step 9: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 10: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: components.css — entries, pagination, TOC, resume, socials, newsletter"
```

---

### Task 6: Update css.html — Light-First Palette with prefers-color-scheme

**Files:**
- Modify: `themes/poison/layouts/partials/head/css.html`

- [ ] **Step 1: Rewrite css.html with light-first defaults and system dark mode**

Replace the entire contents of `themes/poison/layouts/partials/head/css.html` with:
```html
<style>
    body {
        --sidebar-bg-color: {{ with .Site.Params.sidebar_bg_color }}{{ . }}{{ else }}#F8F8F8{{ end }};
        --sidebar-img-border-color: {{ with .Site.Params.sidebar_img_border_color }}{{ . }}{{ else }}#ddd{{ end }};
        --sidebar-p-color: {{ with .Site.Params.sidebar_p_color }}{{ . }}{{ else }}#888{{ end }};
        --sidebar-h1-color: {{ with .Site.Params.sidebar_h1_color }}{{ . }}{{ else }}#111{{ end }};
        --sidebar-a-color: {{ with .Site.Params.sidebar_a_color }}{{ . }}{{ else }}#333{{ end }};
        --sidebar-socials-color: {{ with .Site.Params.sidebar_socials_color }}{{ . }}{{ else }}#555{{ end }};
        --text-color: {{ with .Site.Params.text_color }}{{ . }}{{ else }}#111{{ end }};
        --bkg-color: {{ with .Site.Params.content_bg_color }}{{ . }}{{ else }}#FFF{{ end }};
        --post-title-color: {{ with .Site.Params.post_title_color }}{{ . }}{{ else }}#111{{ end }};
        --list-color: {{ with .Site.Params.list_color }}{{ . }}{{ else }}#555{{ end }};
        --link-color: {{ with .Site.Params.link_color }}{{ . }}{{ else }}#268bd2{{ end }};
        --date-color: {{ with .Site.Params.date_color }}{{ . }}{{ else }}#999{{ end }};
        --table-border-color: {{ with .Site.Params.table_border_color }}{{ . }}{{ else }}#E5E5E5{{ end }};
        --table-stripe-color: {{ with .Site.Params.table_stripe_color }}{{ . }}{{ else }}#F9F9F9{{ end }};
        --code-color: {{ with .Site.Params.code_color }}{{ . }}{{ else }}#111{{ end }};
        --code-background-color: {{ with .Site.Params.code_background_color }}{{ . }}{{ else }}#F0F0F0{{ end }};
        --code-block-color: {{ with .Site.Params.code_block_color }}{{ . }}{{ else }}#fff{{ end }};
        --code-block-background-color: {{ with .Site.Params.code_block_background_color }}{{ . }}{{ else }}#272822{{ end }};
        --moon-sun-color: {{ with .Site.Params.moon_sun_color }}{{ . }}{{ else }}#555{{ end }};
        --moon-sun-background-color: {{ with .Site.Params.moon_sun_background_color }}{{ . }}{{ else }}#F0F0F0{{ end }};
    }
    body.dark-theme {
        --sidebar-bg-color: #1A1A1A;
        --sidebar-img-border-color: #333;
        --sidebar-p-color: #777;
        --sidebar-h1-color: #EEE;
        --sidebar-a-color: #CCC;
        --sidebar-socials-color: #AAA;
        --text-color: {{ with .Site.Params.text_color_dark }}{{ . }}{{ else }}#EEE{{ end }};
        --bkg-color: {{ with .Site.Params.content_bg_color_dark }}{{ . }}{{ else }}#121212{{ end }};
        --post-title-color: {{ with .Site.Params.post_title_color_dark }}{{ . }}{{ else }}#DBE2E9{{ end }};
        --list-color: {{ with .Site.Params.list_color_dark }}{{ . }}{{ else }}#999{{ end }};
        --link-color: {{ with .Site.Params.link_color_dark }}{{ . }}{{ else }}#5BA3D9{{ end }};
        --date-color: {{ with .Site.Params.date_color_dark }}{{ . }}{{ else }}#666{{ end }};
        --table-border-color: {{ with .Site.Params.table_border_color_dark }}{{ . }}{{ else }}#2A2A2A{{ end }};
        --table-stripe-color: {{ with .Site.Params.table_stripe_color_dark }}{{ . }}{{ else }}#1E1E1E{{ end }};
        --code-color: {{ with .Site.Params.code_color_dark }}{{ . }}{{ else }}#EEE{{ end }};
        --code-background-color: {{ with .Site.Params.code_background_color_dark }}{{ . }}{{ else }}#252525{{ end }};
        --code-block-color: {{ with .Site.Params.code_block_color_dark }}{{ . }}{{ else }}#fff{{ end }};
        --code-block-background-color: {{ with .Site.Params.code_block_background_color_dark }}{{ . }}{{ else }}#272822{{ end }};
        --moon-sun-color: #EEE;
        --moon-sun-background-color: #333;
    }
    body {
        background-color: var(--bkg-color);
    }
</style>
<!-- No-FOUC: apply dark theme before first paint -->
<script>
(function() {
    var saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.classList.add('dark-theme');
    }
})();
</script>
```

Note: The no-FOUC script is in `<head>` but uses `document.body` — this works because Hugo places `css.html` inside `<head>` which is parsed before body renders. However, `document.body` won't exist yet at parse time. We need to use `documentElement` instead:

Actually, the script should go on `<html>` or use `document.documentElement`. Let's fix:

Replace the `<script>` block with:
```html
<script>
(function() {
    var saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark-theme');
    }
})();
</script>
```

And update the CSS to also support `html.dark-theme` — actually, since this runs in `<head>`, let's keep it simple: the existing `light_dark.js` (deferred) will handle applying the class to `body`. For the no-FOUC, we set it on `<html>`:

```html
<script>
(function() {
    var saved = localStorage.getItem('theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
        document.documentElement.className += ' dark-theme';
    }
})();
</script>
```

And add this to `layout.css` reset section:
```css
/* Support dark-theme on html (no-FOUC) and body (runtime) */
html.dark-theme body,
body.dark-theme {
    /* dark-theme variables are defined in css.html */
}
```

Wait — the CSS variables are on `body.dark-theme` selector. For the no-FOUC, we need to also define them on `html.dark-theme body`. But since the variables are Hugo-templated in css.html, we should duplicate the selector there.

Add after the `body.dark-theme` block in `css.html`:
```css
html.dark-theme body {
    /* Inherit same dark overrides for no-FOUC */
    --sidebar-bg-color: #1A1A1A;
    /* ... (same dark values) */
}
```

This is getting complex. Simpler approach: put the dark variables on `body.dark-theme, html.dark-theme body` in one selector. Update the css.html accordingly.

- [ ] **Step 2: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 3: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: css.html — light-first palette, system dark mode, no-FOUC script"
```

---

### Task 7: Create header.html Partial and Update baseof.html

**Files:**
- Create: `themes/poison/layouts/partials/header.html`
- Modify: `themes/poison/layouts/_default/baseof.html`

- [ ] **Step 1: Create the header.html partial**

Create `themes/poison/layouts/partials/header.html`:
```html
<header class="site-header" data-pagefind-ignore>
    <div class="header-left">
        <button class="hamburger-btn" aria-label="{{ i18n "toggle_menu" | default "Toggle menu" }}" aria-expanded="false">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 3.5h12a.5.5 0 0 1 0 1H2a.5.5 0 0 1 0-1zm0 4h12a.5.5 0 0 1 0 1H2a.5.5 0 0 1 0-1zm0 4h12a.5.5 0 0 1 0 1H2a.5.5 0 0 1 0-1z"/>
            </svg>
        </button>
        <a href="{{ .Site.BaseURL }}" class="header-brand">{{ .Site.Params.brand }}</a>
    </div>
    <span class="header-payoff">{{ .Site.Params.description | safeHTML }}</span>
    <div class="header-right">
        {{ partial "language_switcher.html" . }}
        {{ partial "light_dark.html" . }}
    </div>
</header>
```

- [ ] **Step 2: Update baseof.html with new structure**

Replace the entire contents of `themes/poison/layouts/_default/baseof.html` with:
```html
{{ partial "head/head.html" . }}
    <body class="{{ if .Site.Params.dark_mode }}dark-theme{{ end }}{{ if and (eq .Kind "page") (not .Params.hideToc) (not .Site.Params.hideToc) }} has-toc{{ end }}">
        {{ partial "header.html" . }}
        <div class="sidebar-overlay"></div>
        <div class="wrapper">
            {{ partial "sidebar/sidebar.html" . }}
            <main class="content container">
                {{ block "main" . -}}{{- end }}
            </main>
            {{ block "sidebar" . }}{{ end }}
        </div>
    </body>
</html>
```

Key changes:
- Removed old `.mobile-header` div entirely
- Added `{{ partial "header.html" . }}` (new responsive header)
- Added `.sidebar-overlay` div for hamburger backdrop
- Added `.has-toc` class conditionally (for CSS Grid column control)
- Removed `layout-reverse` class (no longer needed — we're always sidebar-left)

- [ ] **Step 3: Add close button to sidebar partial**

Modify `themes/poison/layouts/partials/sidebar/sidebar.html` — add the close button as the first child inside `sidebar-sticky`:
```html
<aside class="sidebar" id="sidebar" data-pagefind-ignore>
    <div class="container sidebar-sticky">
        <button class="sidebar-close" aria-label="{{ i18n "close_menu" | default "Close menu" }}">&times;</button>
        <div class="sidebar-top-controls">
            {{ partial "language_switcher.html" . }}
            {{ partial "light_dark.html" . }}
        </div>
        {{ partial "sidebar/title.html" . }}
        {{ partial "sidebar/search.html" . }}
        {{ partial "sidebar/menu.html" . }}
        {{ partial "sidebar/socials.html" . }}
        {{ partial "sidebar/copyright.html" . }}
  </div>
</aside>
```

- [ ] **Step 4: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: header.html partial, updated baseof.html with CSS Grid structure"
```

---

### Task 8: Write hamburger.js and Update light_dark.js

**Files:**
- Create: `themes/poison/assets/js/hamburger.js`
- Modify: `themes/poison/assets/js/light_dark.js`
- Modify: `themes/poison/layouts/partials/head/scripts.html`

- [ ] **Step 1: Create hamburger.js**

Create `themes/poison/assets/js/hamburger.js`:
```javascript
(function() {
    var body = document.body;
    var hamburger = document.querySelector('.hamburger-btn');
    var overlay = document.querySelector('.sidebar-overlay');
    var closeBtn = document.querySelector('.sidebar-close');
    var sidebar = document.querySelector('.sidebar');

    function openMenu() {
        body.classList.add('menu-open');
        hamburger.setAttribute('aria-expanded', 'true');
        sidebar.focus();
    }

    function closeMenu() {
        body.classList.remove('menu-open');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.focus();
    }

    if (hamburger) {
        hamburger.addEventListener('click', function() {
            if (body.classList.contains('menu-open')) {
                closeMenu();
            } else {
                openMenu();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && body.classList.contains('menu-open')) {
            closeMenu();
        }
    });
})();
```

- [ ] **Step 2: Rewrite light_dark.js with system preference detection**

Replace the entire contents of `themes/poison/assets/js/light_dark.js` with:
```javascript
(function() {
    var btn = document.querySelector('.btn-light-dark');
    if (!btn) return;

    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    var saved = localStorage.getItem('theme');

    function applyTheme(theme) {
        var isDark = theme === 'dark';
        document.body.classList.toggle('dark-theme', isDark);
        document.documentElement.classList.toggle('dark-theme', isDark);

        var hasComments = document.getElementById('remark42');
        if (hasComments && window.REMARK42 && window.REMARK42.changeTheme) {
            window.REMARK42.changeTheme(isDark ? 'dark' : 'light');
        }
    }

    function getEffectiveTheme() {
        var saved = localStorage.getItem('theme');
        if (saved) return saved;
        return prefersDark.matches ? 'dark' : 'light';
    }

    // Apply on load (supplements the no-FOUC script in <head>)
    applyTheme(getEffectiveTheme());

    // Toggle button cycles: if user has override, clear it (back to system).
    // If following system, toggle to opposite.
    btn.addEventListener('click', function() {
        var current = getEffectiveTheme();
        var next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', next);
        applyTheme(next);
    });

    // Listen for system preference changes (only matters when no localStorage override)
    prefersDark.addEventListener('change', function() {
        if (!localStorage.getItem('theme')) {
            applyTheme(getEffectiveTheme());
        }
    });
})();
```

- [ ] **Step 3: Update scripts.html to include hamburger.js**

Replace the entire contents of `themes/poison/layouts/partials/head/scripts.html` with:
```html
{{/* JS bundle: light/dark + hamburger + toc + codeblock */}}
{{ $js := slice
    (resources.Get "js/light_dark.js")
    (resources.Get "js/hamburger.js")
}}

{{ if not .Site.Params.hideToc }}
    {{ $js = $js | append (resources.Get "js/toc.js") }}
{{ end }}

{{ $js = $js | append (resources.Get "js/codeblock.js") }}

{{ $js_bundle := $js | resources.Concat "js/bundle.js" | minify | fingerprint }}

<script defer type="text/javascript" src="{{ $js_bundle.RelPermalink }}"></script>

{{ if .Site.Params.plausible }}
<script defer data-domain="{{ .Site.Params.plausible_domain }}" src="{{ .Site.Params.plausible_script }}"></script>
{{ end }}

{{/* Pagefind search */}}
<link href="/pagefind/pagefind-ui.css" rel="stylesheet">
<script src="/pagefind/pagefind-ui.js"></script>
<script>
    window.addEventListener('DOMContentLoaded', (event) => {
        new PagefindUI({
            element: "#search",
            showSubResults: true,
            showImages: false,
            excerptLength: 15
        });
    });
</script>
```

- [ ] **Step 4: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
cd themes/poison && git add -A && git commit -m "feat: hamburger.js, rewritten light_dark.js with system preference detection"
```

---

### Task 9: Update codeblock.css and Language Switcher

**Files:**
- Modify: `themes/poison/assets/css/codeblock.css`
- Modify: `themes/poison/layouts/partials/language_switcher.html`

- [ ] **Step 1: Read current codeblock.css**

Read `themes/poison/assets/css/codeblock.css` to understand what needs minor tweaks.

- [ ] **Step 2: Update codeblock.css border-radius and spacing**

The syntax highlighting classes in codeblock.css are fine. Only update the container/button styles at the top of the file. Find and replace the `.code-container` and `.copy-button` rules to use consistent border-radius:

Update `.highlight pre` to have `border-radius: 6px` (from whatever the current value is).
Update `.copy-button` to have `border-radius: 4px`.

- [ ] **Step 3: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 4: Commit**

```bash
cd themes/poison && git add -A && git commit -m "fix: codeblock.css border-radius consistency"
```

---

### Task 10: Update Resume Layout Template

**Files:**
- Modify: `themes/poison/layouts/resume/resume.html`

- [ ] **Step 1: Read the current resume template**

Read `themes/poison/layouts/resume/resume.html` to understand the structure.

- [ ] **Step 2: Update the resume template**

The resume template has its own `<head>` section and doesn't use `baseof.html`. It needs to:
- Include the new `header.html` partial
- Include the `sidebar-overlay` div
- Reference the new CSS bundle (should already work since stylesheets.html was updated)
- Remove the old `.mobile-header` section if present
- Add `.has-toc` logic is not needed (resume has no TOC)

Read the file, then make targeted edits to match the pattern in the updated `baseof.html`.

- [ ] **Step 3: Also check about/about.html**

Read `themes/poison/layouts/about/about.html` — if it uses `baseof.html` (via `{{ define "main" }}`), it's already covered. If it has its own structure like resume, update it similarly.

- [ ] **Step 4: Build and verify**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
cd themes/poison && git add -A && git commit -m "fix: update resume and about templates for new layout"
```

---

### Task 11: Add i18n Strings for New UI Elements

**Files:**
- Modify: `i18n/en.yaml`
- Modify: `i18n/it.yaml`

- [ ] **Step 1: Read current i18n files**

```bash
cat i18n/en.yaml
cat i18n/it.yaml
```

- [ ] **Step 2: Add new strings**

Add to `i18n/en.yaml`:
```yaml
- id: toggle_menu
  translation: "Toggle menu"
- id: close_menu
  translation: "Close menu"
```

Add to `i18n/it.yaml`:
```yaml
- id: toggle_menu
  translation: "Apri/chiudi menu"
- id: close_menu
  translation: "Chiudi menu"
```

- [ ] **Step 3: Commit**

These are in the parent repo (not the theme submodule):
```bash
cd /home/vjt/code/sindro.me && git add i18n/ && git commit -m "feat: add i18n strings for hamburger menu"
```

---

### Task 12: Full Visual Test and Cleanup

**Files:**
- All modified files

- [ ] **Step 1: Full Hugo build**

```bash
cd /home/vjt/code/sindro.me && hugo --gc --minify 2>&1
```

Expected: clean build, no errors.

- [ ] **Step 2: Run hugo server and visually test**

```bash
hugo server -D --bind 0.0.0.0
```

Test checklist (both EN and IT, both light and dark mode):
- Homepage (post list with summaries)
- Single post (with TOC, code blocks, images, tags)
- List page (tags, categories — archive-style entries)
- About page
- Resume page
- 404 page
- Pagination
- Language switcher (click flags, verify navigation)
- Dark/light toggle (click toggle, verify persistence)
- System preference (change OS dark mode, verify blog follows)
- Desktop (>1200px): 3-column layout visible
- Tablet (600-1199px): header bar, hamburger works, sidebar slides
- Phone (<600px): compact header, no payoff, hamburger works
- Landscape phone: verify sidebar not dominating

- [ ] **Step 3: Fix any visual issues found**

Address problems iteratively. Each fix should be a small targeted change.

- [ ] **Step 4: Remove legacy CSS directory once confirmed**

```bash
cd themes/poison && rm -rf assets/css/legacy/ && git add -A && git commit -m "chore: remove legacy CSS (poole, hyde, poison, custom)"
```

- [ ] **Step 5: Commit theme submodule pointer and all parent changes**

```bash
cd /home/vjt/code/sindro.me
git add themes/poison
git commit -m "update theme: modern CSS Grid layout, light-first design, hamburger menu"
```

- [ ] **Step 6: Stage on vjt.sindro.me for review**

```bash
ssh sindrome@m42 'cd staging && git pull && ./build.sh'
```

Review at `https://vjt.sindro.me/` before shipping to prod.
