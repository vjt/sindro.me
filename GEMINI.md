# GEMINI.md

## Project Overview

This directory contains the source code for **sindro.me**, a personal technical blog and website authored by Marcello Barnaba (@vjt). The site covers topics such as software development, system administration (Linux/BSD), security, and personal reflections.

**Key Technologies:**
*   **Hugo:** A fast and modern static site generator written in Go.
*   **Theme:** Uses a custom fork of the [Poison](https://github.com/lukeorth/poison) theme (originally based on Hyde), located in `themes/poison`.
*   **Content:** Written in Markdown with Hugo-specific front matter.
*   **Comments:** Integrates with [Remark42](https://remark42.com/) for a privacy-focused commenting system.

## Directory Structure

*   `config.toml`: The main configuration file for the Hugo site (base URL, params, menus, taxonomies).
*   `content/`: Contains the site's content.
*   `content/posts/`: Blog posts (e.g., `YYYY-MM-DD-slug.md`).
*   `content/about/`: Static pages like "About".
*   `themes/poison/`: The active theme for the site.
*   `static/`: Static assets like images, PDFs, and favicons that are copied directly to the build output.
*   `archetypes/`: Templates for new content creation (e.g., `default.md`).
*   `resources/`: Hugo resource cache (generated files).

## Building and Running

Since this is a standard Hugo project without a `package.json` or `Makefile`, use the global `hugo` CLI.

### Prerequisites

*   **Hugo:** Ensure Hugo is installed (extended version recommended for some themes).
*   Check version: `hugo version`

### Development Server

To run the site locally with live reloading:

```bash
hugo server -D
```

*   `-D` includes content marked as `draft: true`.
*   The site will typically be available at `http://localhost:1313`.

### Production Build

To build the static site for deployment (output defaults to `public/`):

```bash
hugo --minify
```

## Development Conventions

* **Content Creation:**
* Create new posts using `hugo new posts/my-new-post.md`.
* Front matter format (TOML/YAML) typically includes:
```yaml
---
title: "Post Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
categories: [category1]
draft: true
---
```
* **Asset Management:**
* Global assets go in `static/`.
* Post-specific assets can be placed in page bundles (a folder named after the post containing `index.md` and resources).
* **Theme Customization:**
* Modifications should primarily be done in `themes/poison`.
* Check `config.toml` for theme-specific parameters under `[params]`.
