"""Shared Cloudflare API helpers for cache purge scripts."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

CF_PURGE_URL = "https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache"
DEFAULT_BATCH_SIZE = 30


def load_token(token_file: str) -> str:
    return Path(token_file).expanduser().read_text().strip()


def chunked(seq: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def purge_batch(zone_id: str, token: str, urls: list[str]) -> None:
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


def purge_urls(zone_id: str, token: str, urls: list[str], batch_size: int = DEFAULT_BATCH_SIZE) -> None:
    for batch in chunked(urls, batch_size):
        purge_batch(zone_id, token, batch)
        print(f"cf-purge: purged batch of {len(batch)}", file=sys.stderr)
