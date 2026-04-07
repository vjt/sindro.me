# CLAUDE.md

Guidance for AI assistants working with this repository.

## Project Overview

**sindro.me** — a bilingual (EN/IT) personal technical blog by Marcello Barnaba (@vjt). Static site generated with Hugo, using the Sindrome theme.

## Tech Stack

- **Hugo** (extended) — static site generator
- **Sindrome theme** — custom theme (forked from Poison/Hyde), git submodule at `themes/sindrome/` ([github.com/vjt/hugo-sindrome-theme](https://github.com/vjt/hugo-sindrome-theme))
- **Pagefind** — client-side search, built via `build.sh`
- **WeasyPrint** — generates resume PDFs from markdown at build time (Python venv at `../.venv`)
- **Remark42** — comments system (comments shared across language versions via canonical URL)
- **Git LFS** — for `.mp4` files

## Key Commands

```bash
./build.sh              # Full build: Hugo + Pagefind + resume PDFs
hugo server -D          # Dev server with drafts on localhost:1313
```

Note: Hugo is NOT installed on this machine (Raspberry Pi). Builds happen on `vjt@m42` (FreeBSD server) at `/srv/www/sindro.me/staging/` and `/srv/www/sindro.me/prod/`.

## Multilingual (i18n)

- **English** is the default language, served at `/` (no prefix)
- **Italian** is served at `/it/`
- Content files use language suffixes: `post.en.md` / `post.it.md`
- UI strings in `i18n/en.yaml` and `i18n/it.yaml`
- Language switcher (flag emojis) in sidebar and responsive header
- nginx detects `Accept-Language` header and `lang` cookie for root `/` redirect

### Creating bilingual content

```bash
# Page bundle (preferred — posts with images)
mkdir content/posts/YYYY-MM-DD-slug
# Create index.en.md and index.it.md — images are shared between languages

# Single file post (no images)
# Create posts/YYYY-MM-DD-slug.en.md and posts/YYYY-MM-DD-slug.it.md
```

## Content Structure

```
content/
├── about/_index.{en,it}.md       # About page
├── resume/_index.{en,it}.md      # Resume (dynamic ages via shortcodes)
├── privacy.{en,it}.md            # Privacy policy
├── tos.{en,it}.md                # Terms of service
├── deletion.{en,it}.md           # Data deletion info
└── posts/
    ├── YYYY-MM-DD-slug.{en,it}.md           # Single file posts
    └── YYYY-MM-DD-slug/index.{en,it}.md     # Page bundles (with images)
```

## Custom Shortcodes

- `{{</* years-since "2021-12-01" */>}}` — outputs integer years since a date
- `{{</* age "2020-08-01" */>}}` — outputs years, or months (locale-aware) if under 2 years

Used in the resume and about pages to auto-compute ages and tenures at build time.

## Resume Pipeline

The resume lives in `content/resume/_index.{en,it}.md` (markdown). Two outputs:

1. **Web page** — Hugo renders via `themes/sindrome/layouts/resume/resume.html` at `/resume/` and `/it/resume/`
2. **PDF** — `scripts/resume-pdf.py` reads the markdown, resolves shortcodes, renders via WeasyPrint

Both are generated automatically by `build.sh`. Output: `public/resume.pdf` and `public/resume-it.pdf`.

## Theme (Sindrome)

Forked from Poison/Hyde, completely rewritten CSS. Git submodule at `themes/sindrome/`. Changes must be committed in the submodule first, then the parent repo commits the updated submodule pointer.

### Layout
- **CSS Grid** — 3-column desktop (sidebar | content | TOC), hamburger below 1200px
- **Light-first** with system-aware dark mode (`prefers-color-scheme`)
- **No-FOUC** — inline script in `<head>` applies dark class before paint
- **Boot splash** — Linux kernel boot sequence on first visit (`sessionStorage`)

### Key files
- `assets/css/layout.css` — CSS Grid, breakpoints, responsive
- `assets/css/components.css` — all UI components
- `assets/js/light_dark.js` — theme toggle with system preference detection
- `assets/js/hamburger.js` — mobile menu toggle
- `assets/js/boot-splash.js` — boot sequence animation
- `layouts/partials/header.html` — responsive header bar
- `layouts/partials/boot-splash.html` — boot splash markup + inline CSS

## Configuration

- `config.toml` — site config with `[languages.en]` and `[languages.it]` blocks
- Per-language menus, descriptions, and blurbs
- `.baseurl` file (gitignored) — overrides baseURL for staging builds

## Front Matter

```yaml
---
title: "Post Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
description: "Optional SEO description"
image: optional-og-image.png
---
```

No categories — tags only.

## Writing Style

Conversational, technically precise, opinionated, irreverent. First person. Mixes deep technical detail with colorful language. Self-deprecating humor. Informal "tu" in Italian.
