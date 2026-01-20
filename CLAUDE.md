# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the source code for **sindro.me**, a personal technical blog by Marcello Barnaba (@vjt). The site is a static website generated using Hugo with a custom fork of the Poison theme.

**Technology Stack:**
- Hugo v0.154.5+extended (static site generator)
- Custom fork of the Poison theme (originally based on Hyde)
- Remark42 for privacy-focused commenting system
- Markdown with YAML/TOML front matter for content

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
hugo --minify
```
- Generates optimized static site in `public/` directory
- Use `--minify` for production deployment

### Content Creation
```bash
hugo new posts/YYYY-MM-DD-slug-title.md
```
- Creates new post with proper front matter from archetype template
- Posts use date-prefixed naming: `YYYY-MM-DD-slug.md`

## Architecture and Structure

### Content Organization

Posts can be organized in two ways:
1. **Single file posts**: `content/posts/YYYY-MM-DD-slug.md`
2. **Page bundles**: `content/posts/YYYY-MM-DD-slug/index.md` (for posts with images/assets)

The site uses both approaches. Page bundles are preferred when a post has associated media files.

### Configuration Hierarchy

The site configuration is split between:
- `config.toml`: Main site configuration (baseURL, params, menus, social links, taxonomies)
- `themes/poison/`: Theme customizations and layouts

The Poison theme is a Git submodule tracking a custom fork at `https://github.com/vjt/poison`.

### Front Matter Format

Posts use YAML front matter:
```yaml
---
title: "Post Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
categories: [category1]
draft: true  # Remove or set to false when ready to publish
---
```

### Static Assets

- `static/`: Root-level static files (favicon, images, PDFs) copied directly to site root
- Page bundle assets: Place images alongside `index.md` in post directories

### Theme Customization

The Poison theme lives in `themes/poison/` and includes:
- `layouts/`: Template overrides
- `assets/`: CSS/JS source files
- `static/`: Theme-specific static assets

Theme parameters are configured in the main `config.toml` under `[params]`, including:
- Dark mode settings (`dark_mode = true`)
- Remark42 comment integration
- Social media links
- Custom menu structure

### Taxonomies

The site uses Hugo's taxonomy system:
- **Categories**: Broad content classification
- **Tags**: Granular topic tagging
- **Series**: Multi-part article groupings

These are defined in `config.toml` under `[taxonomies]`.

## Important Notes

- The theme is a Git submodule; modifications to the theme should be committed in the submodule repository
- Hugo extended version is required (already installed: v0.154.5+extended)
- The site uses unsafe HTML rendering (`markup.goldmark.renderer.unsafe = true`) to allow raw HTML in Markdown
- Base URL is `https://vjt.sindro.me/` in production
