#!/bin/sh
# Build script for Hugo + Pagefind

set -e

rm -rf public

BASEURL_FLAG=""
if [ -f .baseurl ]; then
  BASEURL_FLAG="--baseURL $(cat .baseurl)"
fi

echo "Building Hugo site..."
hugo $BASEURL_FLAG "$@"

echo "Indexing with Pagefind..."
npx -y pagefind --site public \
  --glob "{posts,about,deletion,privacy,tos}/**/*.html"

echo "Build complete!"
