#!/usr/bin/env python3
"""
Purge Cloudflare cache for content that changed in this build.

Compares two build directories by SHA-256 hashing HTML/XML output and
non-fingerprinted binary assets (images, PDFs, audio, text), emits the
set of URLs whose content changed (or was deleted), and POSTs the URL
list to Cloudflare's purge_cache endpoint.

Hugo-fingerprinted assets (e.g. *_hu_<hash>.webp, js/bundle.<hash>.js,
fonts/*.woff2) are skipped: their URLs change with content, so old
cache entries become orphans rather than stale. Use cf-purge-static.py
when only response headers change on those stable URLs.

Videos (.mp4, LFS-tracked) are skipped: they rarely change in place
and hashing them is expensive.

Scope is restricted to the apex hostname (e.g. https://sindro.me/),
leaving sibling subdomains (remark., noema., vjt.) cache untouched.

When invoked without --old-dir (first run, missing manifest), emits the
full URL list from the new build — CF treats unknown URLs as no-ops, so
this is safe and idempotent.

Defaults read from environment (sourced via .env):
  HUGO_BASEURL → --base
  CF_ZONE_ID   → --zone-id

So from the prod checkout, this is enough:
  . ./.env && python scripts/cf-purge.py
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cf import DEFAULT_BATCH_SIZE, load_token, purge_urls

TEXT_EXTS = {".html", ".xml"}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
               ".ico", ".pdf", ".asc", ".pub", ".txt", ".mp3"}
TRACKED_EXTS = TEXT_EXTS | BINARY_EXTS

# Hugo-fingerprinted URLs change with content, so the old URL becomes
# an orphan rather than stale — no purge needed. Header-only changes
# on these stable-URL families are handled by cf-purge-static.py.
HU_FINGERPRINT = re.compile(r"_hu_[a-f0-9]+\.(webp|jpg|jpeg|png|gif)$", re.IGNORECASE)
JS_FINGERPRINT = re.compile(r"^js/bundle\.[a-f0-9]+\.js$")
FONT_FINGERPRINT = re.compile(r"^fonts/.+\.woff2$")


def is_fingerprinted(rel: str) -> bool:
    return bool(HU_FINGERPRINT.search(rel)
                or JS_FINGERPRINT.match(rel)
                or FONT_FINGERPRINT.match(rel))


def hash_tree(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TRACKED_EXTS:
            continue
        rel = path.relative_to(root).as_posix()
        if is_fingerprinted(rel):
            continue
        manifest[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return manifest


def changed_paths(old: dict[str, str], new: dict[str, str]) -> set[str]:
    out: set[str] = set()
    for rel, h in new.items():
        if old.get(rel) != h:
            out.add(rel)
    for rel in old:
        if rel not in new:
            out.add(rel)
    return out


def path_to_url(rel: str, base: str) -> str:
    base = base.rstrip("/")
    rel = rel.replace(os.sep, "/")
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{base}/{rel}" if rel else f"{base}/"


def filter_apex(urls: Iterable[str], base: str) -> list[str]:
    base = base.rstrip("/") + "/"
    return sorted(u for u in urls if u.startswith(base) or u == base.rstrip("/"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--new-dir", type=Path, default=Path("public"),
                    help="Build directory just produced (default: public)")
    ap.add_argument("--old-dir", type=Path,
                    help="Previous build directory (e.g. public_old_$$/) for diff")
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

    new = hash_tree(args.new_dir)
    if args.old_dir and args.old_dir.is_dir():
        old = hash_tree(args.old_dir)
        rels = changed_paths(old, new)
        mode = f"diff (old={args.old_dir}, new={args.new_dir})"
    else:
        rels = set(new.keys())
        mode = f"full (new={args.new_dir}, no old manifest)"

    urls = filter_apex(
        (path_to_url(r, args.base) for r in rels),
        args.base,
    )

    if not urls:
        print(f"cf-purge: {mode}: no URLs to purge", file=sys.stderr)
        return 0

    print(f"cf-purge: {mode}: {len(urls)} URL(s)", file=sys.stderr)
    for u in urls:
        print(f"  {u}", file=sys.stderr)

    if args.dry_run:
        return 0

    token = load_token(args.token_file)
    purge_urls(args.zone_id, token, urls, args.batch_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
