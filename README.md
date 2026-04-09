<div align="center">

<img src="glider.svg" alt="Hacker Emblem" width="96">

# [sindro.me](https://sindro.me)

</div>

A bilingual (EN/IT) personal technical blog by [Marcello Barnaba](https://sindro.me/about/) ([@vjt](https://github.com/vjt)). Static site generated with [Hugo](https://gohugo.io/), using the [Sindrome theme](https://github.com/vjt/hugo-sindrome-theme).

## Live

- **Production**: [sindro.me](https://sindro.me)
- **Staging**: [vjt.sindro.me](https://vjt.sindro.me)

## What's here

- 69 bilingual posts (2007-present) on sysadmin, development, networking, home automation, and life
- Custom Hugo theme ([Sindrome](https://github.com/vjt/hugo-sindrome-theme)) with CSS Grid layout, system-aware dark mode, hamburger menu, and a Linux boot sequence easter egg
- Resume pipeline that generates web pages + PDFs from markdown
- Pagefind client-side search
- Remark42 comments with cross-language thread sharing

## How it was built

This blog was extensively revamped using [Claude Code](https://claude.ai/code). The entire process — brainstorming, design specs, implementation, review, bugfixing — is documented in the commit history and in this post:

**[How I Used Claude to Completely Revamp My Blog in Two Days](https://sindro.me/posts/2026-04-07-how-i-used-claude-to-revamp-my-blog/)**

Every commit is public. If you want to see what AI-assisted development actually looks like in practice, dig through the history.

## Stack

- **Hugo** (extended) — static site generator
- **[Sindrome](https://github.com/vjt/hugo-sindrome-theme)** — custom theme (git submodule)
- **Pagefind** — client-side search
- **WeasyPrint** — resume PDF generation
- **Remark42** — self-hosted comments
- Builds on FreeBSD, runs on nginx

## Building

```bash
./build.sh              # Full build: Hugo + Pagefind + resume PDFs
hugo server -D          # Dev server with drafts
```

## License

Content is copyright Marcello Barnaba. Theme is GPL-3.0.
