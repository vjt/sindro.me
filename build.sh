#!/bin/sh
# Build script for Hugo + Pagefind + Resume PDF

set -e

VENV="$(dirname "$(realpath "$0")")/../.venv"

# Source .env for HUGO_BASEURL and other overrides
[ -f .env ] && . ./.env

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
rm -rf "public_old_$$"

echo "Build complete!"
