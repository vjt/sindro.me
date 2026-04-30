#!/bin/sh
# Build script for Hugo + Pagefind + Resume PDF

set -e

VENV="$(dirname "$(realpath "$0")")/../.venv"

# Source .env for HUGO_BASEURL and other overrides
[ -f .env ] && . ./.env

echo "Linting Italian post bundle links..."
./scripts/check-it-links.sh

BUILD_DIR="public_build_$$"
rm -rf "$BUILD_DIR"

echo "Building Hugo site..."
hugo -d "$BUILD_DIR" "$@"

echo "Indexing with Pagefind..."
npx -y pagefind --site "$BUILD_DIR" \
  --glob "{posts,about,deletion,privacy,tos,resume,it/posts,it/about,it/deletion,it/privacy,it/tos,it/resume}/**/*.html"

if [ -x "$VENV/bin/python" ]; then
  echo "Generating resume PDFs..."
  HUGO_PUBLISHDIR="$BUILD_DIR" "$VENV/bin/python" scripts/resume-pdf.py
fi

echo "Swapping public directory..."
if [ -d public ]; then
  mv public "public_old_$$"
fi
mv "$BUILD_DIR" public

# Surgical Cloudflare cache purge for the apex hostname.
# Only runs when CF_ZONE_ID is set (prod .env has it, staging does not).
# Diffs old vs new public/ by HTML+XML hash to purge only changed URLs;
# leaves sibling subdomain caches (remark., noema., vjt.) warm.
if [ -n "${CF_ZONE_ID:-}" ]; then
  echo "Purging Cloudflare cache for changed pages..."
  if [ -x "$VENV/bin/python" ]; then
    PURGE_PY="$VENV/bin/python"
  else
    PURGE_PY="python3"
  fi
  "$PURGE_PY" scripts/cf-purge.py \
    --new-dir public \
    --old-dir "public_old_$$" \
    --base "${HUGO_BASEURL:-https://sindro.me}" \
    --zone-id "$CF_ZONE_ID"
fi

rm -rf "public_old_$$"

echo "Build complete!"
