# sindro.me Layout Redesign

**Date:** 2026-04-06
**Approach:** CSS Rewrite, Keep Templates (Approach B)

## Goal

Modernize the blog layout: crisp light-first design with system-aware dark mode, responsive CSS Grid replacing the legacy Hyde/Poole flexbox, hamburger menu below 1200px, right-side TOC on wide screens. Less wasted space, especially on landscape phones.

## Layout Grid

Three responsive tiers using CSS Grid.

### Desktop (>=1200px) — Three columns

```
| Sidebar (220px) | Content (fluid, max 52rem) | TOC (200px) |
```

- Sidebar: fixed, scrolls independently, contains brand/search/nav/socials/copyright
- Content: centered in available space with `max-width: 52rem`
- TOC: sticky position, visible on single posts only, hidden on list pages
- No header bar — sidebar has the brand

### Tablet / Landscape phone (600–1199px) — Single column + hamburger

```
| Header: [hamburger] [brand] [payoff] [lang] [toggle] |
| Content (full width, padded)                          |
```

- Header bar: fixed top, hamburger icon + "sindro.me" + "feeling bold on the internet" + lang flags + dark/light toggle
- Sidebar: off-screen, slides from left on hamburger click (280px)
- TOC: inline collapsible at top of post
- Content: full width with horizontal padding

### Portrait phone (<600px) — Compact

Same as tablet but:
- Payoff text hidden from header (not enough room)
- Tighter padding
- Header: hamburger + brand + lang flags + toggle

### Breakpoints

| Range | Layout | Sidebar | TOC | Header |
|-------|--------|---------|-----|--------|
| >=1200px | 3-col grid | Visible (220px) | Right column (200px) | None |
| 600–1199px | 1-col | Hamburger slide-out | Inline collapsible | Hamburger + brand + payoff + lang + toggle |
| <600px | 1-col compact | Hamburger slide-out | Inline collapsible | Hamburger + brand + lang + toggle |

### CSS Grid structure

```css
/* Desktop: 3-column */
body {
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 220px 1fr 200px;
  height: 100vh;
}

/* Tablet/phone: 1-column + header */
@media (max-width: 1199px) {
  body {
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr;
    height: auto;
  }
}
```

## Color & Theme System

### Light mode (default)

| Role | Color |
|------|-------|
| Background | #FFFFFF |
| Sidebar bg | #F8F8F8 |
| Text | #111111 |
| Secondary text | #555555 |
| Links | #268BD2 (Solarized blue, unchanged) |
| Borders | #E5E5E5 |
| Tags / inline code bg | #F0F0F0 |
| Dates / meta | #999999 |
| Code blocks | Monokai dark (unchanged) |

### Dark mode

| Role | Color |
|------|-------|
| Background | #121212 |
| Sidebar bg | #1A1A1A |
| Text | #EEEEEE |
| Secondary text | #999999 |
| Links | #5BA3D9 (lighter blue for contrast) |
| Borders | #2A2A2A |
| Tags / inline code bg | #252525 |
| Dates / meta | #666666 |
| Code blocks | Monokai dark (unchanged) |

### Theme behavior

1. **Default:** follow `prefers-color-scheme` (system setting)
2. **Override:** user clicks toggle -> stored in `localStorage` -> persists across visits
3. **Reset:** clearing localStorage falls back to system preference
4. **No FOUC:** inline script in `<head>` applies theme class before first paint

### What stays visually

- Abril Fatface for brand/logo
- Fira Sans 300 for body text
- Solarized blue links
- Monokai code blocks

## Header & Hamburger Menu

### Header bar (shown <1200px only)

Fixed top bar containing:
- Hamburger icon (left)
- Brand "sindro.me" in Abril Fatface
- Payoff "feeling bold on the internet" (center, hidden <600px)
- Language switcher flags (right)
- Dark/light toggle (right)

### Language switcher

Bigger than current: 18px emoji, 8px x 12px padding, 8px border-radius, rounded background. Minimum 44px touch target for accessibility.

### Hamburger slide-out

- Slides from left, 280px wide
- Semi-transparent dark overlay behind (click to close)
- Close button (X) top right of panel
- Contains everything from the sidebar: search, nav, socials, copyright
- CSS transition: `transform 0.25s ease`
- `Escape` key closes
- Focus trap for accessibility
- No JS framework — toggle class on body

## Content Area & Typography

### Content width

- Max-width: 52rem (~832px), up from 44rem
- Centered in the grid's content column
- On hamburger screens (<1200px): full width with padding, no max-width cap

### Typography scale

| Element | Size | Weight | Color | Line-height |
|---------|------|--------|-------|-------------|
| Post title (h1) | 1.75rem | 700 | --text-color | 1.25 |
| Section heading (h2) | 1.375rem | 600 | --text-color | 1.3 |
| Subsection (h3) | 1.125rem | 600 | --text-color | 1.35 |
| Body text | 1rem (16px) | 300 | #333 (light) / #ddd (dark) | 1.7 |
| Secondary text | 0.875rem | 300 | #555 | 1.6 |
| Meta / dates | 0.75rem | 400 | #999 | 1.5 |
| Inline code | 85% | 400 | --code-color | inherit |

### Changes from current

- Base font stays 16px — no more jump to 20px at 48em breakpoint
- Line-height 1.5 -> 1.7 for body text
- Heading weights explicit 600/700
- Post list: border-separated entries instead of 4em gap
- Tags: pill-shaped with background color

## CSS Architecture

### Files deleted

| File | Lines | Reason |
|------|-------|--------|
| `poole.css` | 274 | Legacy reset/typography, replaced by layout.css |
| `hyde.css` | 173 | Legacy flexbox layout, replaced by layout.css |
| `poison.css` | 450 | Theme overrides, rewritten as components.css |
| `custom.css` | 228 | Mixed concerns, folded into components.css |

### Files created

| File | Purpose |
|------|---------|
| `layout.css` | CSS Grid system, 3 breakpoints, sidebar/content/TOC columns, hamburger slide-out positioning, header bar, mobile layout |
| `components.css` | Navigation, tags, post list, post meta, TOC, pagination, search, lang switcher, socials, dark/light toggle, tables, resume page, about page |

### Files kept (minor tweaks)

| File | Changes |
|------|---------|
| `fonts.css` | Unchanged |
| `codeblock.css` | Border-radius and spacing adjustments |

### Bundle

`stylesheets.html` bundles: `layout.css` + `components.css` + `fonts.css` + `codeblock.css` (minified + fingerprinted via Hugo Pipes, same as current).

## Template Changes

| File | Change |
|------|--------|
| `baseof.html` | Replace mobile-header with new header partial. Add hamburger overlay div. Update body classes for CSS Grid. |
| `head/css.html` | Update CSS variable defaults to light-first palette. Add `prefers-color-scheme` media query block for dark mode variables. |
| `head/stylesheets.html` | Replace poole+hyde+poison+custom bundle with layout+components bundle. |
| `head/scripts.html` | Update light_dark.js init to check `prefers-color-scheme` first, localStorage second. Add hamburger.js. |
| **NEW** `partials/header.html` | Responsive header bar: hamburger, brand, payoff, lang switcher, dark/light toggle. |

### JavaScript changes

| File | Change |
|------|--------|
| `light_dark.js` | Add system preference detection via `matchMedia('(prefers-color-scheme: dark)')`. Three-state logic: system / light / dark. Listen for system changes. |
| **NEW** `hamburger.js` | Menu toggle, overlay click-to-close, Escape key, focus trap. ~30 lines, no dependencies. |

Note: `light_dark.js` already syncs theme with Remark42 comments (`window.REMARK42.changeTheme()`). This integration must be preserved in the rewrite.

### Untouched

- All sidebar partials (title, menu, search, socials, copyright) — same HTML, new CSS
- All post partials (info, comments, navigation) — same HTML, new CSS
- single.html, list.html, index.html — untouched
- All shortcodes — untouched
- All content files — zero changes
- config.toml — color params still work via CSS variables
- Resume and About layouts — styling moves to components.css but HTML structure unchanged

## Migration Safety

- Old CSS files kept in `css/legacy/` until confirmed everything works
- Work in a git branch for easy rollback
- Stage and review at `vjt.sindro.me` before shipping to prod
- Test checklist: post, list, index, about, resume, 404, tags, categories, both languages, both themes, mobile/tablet/desktop
