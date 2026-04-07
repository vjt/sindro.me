# CLAUDE.md

Guidance for AI assistants working with this repository.

## Project Overview

**sindro.me** — a bilingual (EN/IT) personal technical blog by Marcello Barnaba (@vjt). Static site generated with Hugo, using a custom fork of the Sindrome theme.

## Tech Stack

- **Hugo** (extended) — static site generator
- **Sindrome theme** — custom fork, git submodule at `themes/sindrome/` ([github.com/vjt/hugo-sindrome-theme](https://github.com/vjt/hugo-sindrome-theme))
- **Pagefind** — client-side search, built via `build.sh`
- **WeasyPrint** — generates resume PDFs from markdown at build time (Python venv at `../.venv`)
- **Remark42** — comments system (comments shared across language versions via canonical URL)
- **Git LFS** — for `.mp4` files

## Key Commands

```bash
./build.sh              # Full build: Hugo + Pagefind + resume PDFs
hugo server -D          # Dev server with drafts on localhost:1313
```

## Multilingual (i18n)

- **English** is the default language, served at `/` (no prefix)
- **Italian** is served at `/it/`
- Content files use language suffixes: `post.en.md` / `post.it.md`
- UI strings in `i18n/en.yaml` and `i18n/it.yaml`
- Language switcher (flag emojis) in mobile header and sidebar
- nginx detects `Accept-Language` header and `lang` cookie for root `/` redirect

### Creating bilingual content

```bash
# Single file post
hugo new posts/YYYY-MM-DD-slug.en.md
# Then create posts/YYYY-MM-DD-slug.it.md with same front matter (translated title)

# Page bundle (posts with images)
mkdir content/posts/YYYY-MM-DD-slug
# Create index.en.md and index.it.md — images are shared between languages
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

## Theme (Poison fork)

The theme is a git submodule. Changes must be committed in `themes/sindrome/` first, then the parent repo commits the updated submodule pointer.

Key customizations over upstream:
- i18n support with `{{ i18n }}` calls throughout templates
- Language switcher partial
- Resume page layout
- Pagefind search integration
- Remark42 comments with cross-language thread sharing
- KaTeX/tabs removed (dead weight)
- Dead CSS cleaned from poole.css/hyde.css

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
categories: [category1]
description: "Optional SEO description"
image: optional-og-image.png
---
```

Common categories: `development`, `System Administration`, `Rants`, `Open Source`, `politics`, `number-42`

## Writing Style

Conversational, technically precise, opinionated, irreverent. First person. Mixes deep technical detail with colorful language. Self-deprecating humor. Informal "tu" in Italian.
