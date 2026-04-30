#!/usr/bin/env python3
"""
Purge all fingerprinted static assets from Cloudflare cache.

Walks the build directory for fonts, the Hugo-fingerprinted JS bundle,
and Hugo image-processing outputs (`*_hu_<hash>.<ext>`), then POSTs the
URL list to Cloudflare's purge_cache endpoint.

Use this when the response *headers* on stable URLs change at the
origin (e.g. Cache-Control max-age was bumped) — `cf-purge.py` only
diffs HTML/XML and won't notice header-only changes on static assets.
For routine deploys where content changes ride a new fingerprinted
URL, this script is unnecessary.

Defaults read from environment (sourced via .env):
  HUGO_BASEURL → --base
  CF_ZONE_ID   → --zone-id

Typical invocation from the prod checkout:
  . ./.env && python scripts/cf-purge-static.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cf import DEFAULT_BATCH_SIZE, load_token, purge_urls

# Mirrors the nginx location blocks in /usr/local/etc/nginx/sites/sindro.me
# that grant max-age=1y, immutable.
HU_FINGERPRINT = re.compile(r"_hu_[a-f0-9]+\.(webp|jpg|jpeg|png|gif)$", re.IGNORECASE)


def collect_static(root: Path) -> list[str]:
    rels: set[str] = set()
    for p in root.glob("fonts/*.woff2"):
        rels.add(p.relative_to(root).as_posix())
    for p in root.glob("js/bundle.*.js"):
        rels.add(p.relative_to(root).as_posix())
    for p in root.rglob("*"):
        if p.is_file() and HU_FINGERPRINT.search(p.name):
            rels.add(p.relative_to(root).as_posix())
    return sorted(rels)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--new-dir", type=Path, default=Path("public"),
                    help="Build directory to scan (default: public)")
    ap.add_argument("--base", default=os.environ.get("HUGO_BASEURL"),
                    help="Apex base URL (default: $HUGO_BASEURL from .env)")
    ap.add_argument("--zone-id", default=os.environ.get("CF_ZONE_ID"),
                    help="Cloudflare zone ID (default: $CF_ZONE_ID from .env)")
    ap.add_argument("--token-file", default=os.path.expanduser(
                        "~/.config/cloudflare/purge-token"),
                    help="Path to file containing CF API token")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print URLs to purge, do not call CF API")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    args = ap.parse_args()

    if not args.base:
        raise SystemExit("--base not given and HUGO_BASEURL not set; source .env first")
    if not args.zone_id:
        raise SystemExit("--zone-id not given and CF_ZONE_ID not set; source .env first")
    if not args.new_dir.is_dir():
        raise SystemExit(f"--new-dir does not exist: {args.new_dir}")

    base = args.base.rstrip("/")
    rels = collect_static(args.new_dir)
    urls = [f"{base}/{rel}" for rel in rels]

    if not urls:
        print("cf-purge-static: no fingerprinted assets found", file=sys.stderr)
        return 0

    print(f"cf-purge-static: {len(urls)} URL(s)", file=sys.stderr)
    if args.dry_run:
        for u in urls:
            print(f"  {u}", file=sys.stderr)
        return 0

    token = load_token(args.token_file)
    purge_urls(args.zone_id, token, urls, args.batch_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
