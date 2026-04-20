#!/bin/sh
# Lint Italian post markdown for broken bundle references.
#
# Two classes of bugs, both surfaced by commit da0df03:
#
#   1. Absolute links with /it/ prefix pointing at bundle assets.
#      Page bundles publish only under /posts/slug/ (not duplicated per
#      language), so /it/posts/slug/file.ext 404s.
#
#   2. Relative links to non-image bundle files in .it.md. Hugo's image
#      render hook rewrites ![](name.ext) to absolute bundle paths, but
#      plain <a href> passes through. Browser resolves against page URL,
#      so on /it/posts/slug/ a bare name.pdf becomes /it/posts/slug/name.pdf
#      and 404s.
#
# Exit 1 on any violation with file:line context.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0

# (1) /it/ prefix on links ending in a file extension (bundle assets).
# Page bundles publish only under /posts/slug/ (language-neutral), so
# /it/posts/slug/file.ext 404s. Page links /it/posts/slug/ are fine —
# those go to the Italian rendering of the post.
bad_abs=$(grep -rn -E '\]\(/it/[^)]+\.\w+\)' content --include='*.md' || true)
if [ -n "$bad_abs" ]; then
  echo "ERROR: /it/ prefix on bundle asset — bundles are language-neutral, use /posts/slug/file.ext:"
  echo "$bad_abs"
  fail=1
fi

# (2) Relative bundle-file links in .it.md. Plain <a> form only —
# ![alt](...) is handled by Hugo's image render hook and resolves fine.
# (^|[^!]) before [ excludes the image form; [^]]* inside [] allows
# any alt/link text without nested brackets.
bad_rel=$(grep -rn -E '(^|[^!])\[[^]]*\]\([A-Za-z0-9_-][A-Za-z0-9._-]*\.\w+\)' content --include='*.it.md' || true)
if [ -n "$bad_rel" ]; then
  echo "ERROR: relative non-image link in .it.md — use absolute /posts/slug/file.ext (Hugo only rewrites ![](), not [](): browser resolves against /it/... and 404s):"
  echo "$bad_rel"
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "IT link check OK."
