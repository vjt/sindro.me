#!/usr/bin/env python3
"""
Purge Cloudflare cache for content that changed in this build.

Compares two build directories by SHA-256 hashing all HTML/XML output,
emits the set of URLs whose content changed (or was deleted), and POSTs
the URL list to Cloudflare's purge_cache endpoint.

Scope is restricted to the apex hostname (e.g. https://sindro.me/),
leaving sibling subdomains (remark., noema., vjt.) cache untouched.

When invoked without --old-dir (first run, missing manifest), emits the
full URL list from the new build — CF treats unknown URLs as no-ops, so
this is safe and idempotent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

CONTENT_EXTS = {".html", ".xml"}
CF_PURGE_URL = "https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache"
BATCH_SIZE = 30


def hash_tree(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in CONTENT_EXTS:
            continue
        rel = str(path.relative_to(root))
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


def chunked(seq: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def cf_purge(zone_id: str, token: str, urls: list[str]) -> None:
    body = json.dumps({"files": urls}).encode("utf-8")
    req = urllib.request.Request(
        CF_PURGE_URL.format(zone=zone_id),
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"CF purge HTTP {exc.code}: {body_text}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"CF purge network error: {exc}") from exc
    if not payload.get("success"):
        raise SystemExit(f"CF purge failed: {payload}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--new-dir", required=True, type=Path,
                    help="Build directory just produced (e.g. public/)")
    ap.add_argument("--old-dir", type=Path,
                    help="Previous build directory (e.g. public_old_$$/) for diff")
    ap.add_argument("--base", required=True,
                    help="Apex base URL (e.g. https://sindro.me)")
    ap.add_argument("--zone-id", required=True,
                    help="Cloudflare zone ID for the apex")
    ap.add_argument("--token-file", default=os.path.expanduser(
                        "~/.config/cloudflare/purge-token"),
                    help="Path to file containing CF API token")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print URLs to purge, do not call CF API")
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = ap.parse_args()

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

    token = Path(args.token_file).read_text().strip()
    for batch in chunked(urls, args.batch_size):
        cf_purge(args.zone_id, token, batch)
        print(f"cf-purge: purged batch of {len(batch)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
