#!/bin/sh
# Build script for Hugo + Pagefind

set -e

rm -rf public

echo "Building Hugo site..."
hugo "$@"

echo "Indexing with Pagefind..."
npx -y pagefind --site public \
  --glob "{posts,about,deletion,privacy,tos}/**/*.html"

echo "Build complete!"
