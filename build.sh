#!/bin/sh
# Build script for Hugo + Pagefind + Resume PDF

set -e

VENV="$(dirname "$(realpath "$0")")/../.venv"

# Source .env for HUGO_BASEURL and other overrides
[ -f .env ] && . ./.env

rm -rf public

echo "Building Hugo site..."
hugo "$@"

echo "Indexing with Pagefind..."
npx -y pagefind --site public \
  --glob "{posts,about,deletion,privacy,tos,resume,it/posts,it/about,it/deletion,it/privacy,it/tos,it/resume}/**/*.html"

if [ -x "$VENV/bin/python" ]; then
  echo "Generating resume PDFs..."
  "$VENV/bin/python" scripts/resume-pdf.py
fi

echo "Build complete!"
