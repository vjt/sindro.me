# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the source code for **sindro.me**, a personal technical blog by Marcello Barnaba (@vjt). The site is a static website generated using Hugo with a custom fork of the Poison theme.

**Technology Stack:**
- Hugo v0.154.5+extended (static site generator)
- Custom fork of the Poison theme (originally based on Hyde)
- Remark42 for privacy-focused commenting system
- Markdown with YAML front matter for content
- Git LFS for `.mp4` files
- Pagefind for search (built via `build.sh`)

## Key Commands

### Development Server
```bash
hugo server -D
```
- Starts local development server with live reload
- `-D` includes draft content
- Accessible at `http://localhost:1313` by default

### Production Build
```bash
./build.sh
```
- Runs `hugo --minify` + Pagefind indexing
- Generates optimized static site in `public/` directory

### Content Creation
```bash
hugo new posts/YYYY-MM-DD-slug-title.md
```
- Posts use date-prefixed naming: `YYYY-MM-DD-slug.md`
- For posts with images, use a page bundle: `content/posts/YYYY-MM-DD-slug/index.md`

## Architecture and Structure

### Content Organization

Posts can be organized in two ways:
1. **Single file posts**: `content/posts/YYYY-MM-DD-slug.md` — for text-only posts
2. **Page bundles**: `content/posts/YYYY-MM-DD-slug/index.md` — for posts with images/assets alongside

Page bundles are preferred when a post has associated media files. Images go in the same directory as `index.md`.

### Image References

In page bundles, reference images with the full path from the site root:
```markdown
![Alt text](/posts/YYYY-MM-DD-slug/image-name.png)
```

YouTube embeds use Hugo shortcodes:
```
{{</* youtube VIDEO_ID */>}}
```

### Configuration

- `config.toml`: Main site configuration (baseURL, params, menus, social links, taxonomies)
- `themes/poison/`: Theme customizations and layouts (Git submodule, fork at `https://github.com/vjt/poison`)
- Base URL: `https://sindro.me/`
- Dark mode enabled by default
- Remark42 comments at `remark.sindro.me`

### Front Matter Format

Posts use YAML front matter delimited by `---`:
```yaml
---
title: "Post Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
categories: [category1]
description: "Optional description for SEO/social"
---
```

Common categories: `development`, `System Administration`, `Rants`, `Open Source`, `politics`, `number-42`

### Static Assets

- `static/`: Root-level static files (favicon, author photo, GPG key, resume PDF) — copied to site root
- Page bundle assets: images placed alongside `index.md` in post directories

### Taxonomies

- **Categories**: Broad content classification
- **Tags**: Granular topic tagging
- **Series**: Multi-part article groupings

## Writing Style

Marcello's voice: conversational, technically precise, opinionated, irreverent. First-person narrative. Mixes deep technical detail with colorful language. Self-deprecating humor.

Recurring patterns:
- Opens with a personal anecdote or frustration that motivated the project
- "## The Problem" / "## The Solution" structure for technical posts
- "Never. Again." for dramatic emphasis after describing a failure
- "It's [year], and we are still..." for frustration with unsolved problems
- "Ask me how I know." after describing a non-obvious gotcha
- "Have fun!" or "Happy hacking!" as closing
- Casual asides in parentheses
- Code blocks with practical, copy-pasteable commands
- Links to GitHub repos at the end
- No unnecessary formality — profanity when warranted

## Important Notes

- The theme is a Git submodule; modifications should be committed in the submodule repository
- Hugo extended version is required (v0.154.5+extended)
- Unsafe HTML rendering is enabled (`markup.goldmark.renderer.unsafe = true`)
- The blog is deployed on a server, not built locally — Hugo is not installed on the development laptop
- Network infrastructure context is available at `~/.claude/network-setup.md`
