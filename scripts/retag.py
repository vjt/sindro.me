#!/usr/bin/env python3
"""
Aggressive tag cleanup for sindro.me blog posts.
Merges duplicate/similar tags, removes single-use junk tags, deduplicates.
"""

import os
import re
import glob

POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "posts")

# Tag merge map: old_tag -> new_tag
MERGE_MAP = {
    "network": "networking",
    "sysadm": "sysadmin",
    "bsd": "freebsd",
    "openbsd": "freebsd",
    "netbsd": "freebsd",
    "jquery": "javascript",
    "nodejs": "javascript",
    "ajax": "javascript",
    "lightwindow": "javascript",
    "facebox": "javascript",
    "comet": "javascript",
    "shell": "bash",
    "sed": "bash",
    "oneliner": "bash",
    "iphone": "apple",
    "safari": "apple",
    "leopard": "apple",
    "notebook": "apple",
    "battery": "apple",
    "home-automation": "home-assistant",
    "verisure": "home-assistant",
    "wifi": "networking",
    "mqtt": "networking",
    "5g": "networking",
    "netatalk": "networking",
    "http": "networking",
    "ison": "networking",
    "docker": "linux",
    "iptables": "linux",
    "systemd": "linux",
    "debian": "linux",
    "xfs": "linux",
    "raspberrypi": "linux",
    "capabilities": "linux",
    "kerberos": "security",
    "cryptography": "security",
    "authentication": "security",
    "hack": "security",
    "merb": "rails",
    "capistrano": "rails",
    "neutrality": "politics",
    "economics": "politics",
    "crisis": "politics",
    "privacy": "politics",
    "opensource": "open-source",
    "open source": "open-source",
    "panmind": "projects",
    "twitter": "social",
    "community": "social",
    "entertainment": "funny",
    "gibberish": "funny",
    "fail": "funny",
    "chuck": "funny",
    "mercurial": "git",
    "hg": "git",
    "github": "git",
    "zfs": "sysadmin",
    "solaris": "sysadmin",
    "sco": "sysadmin",
    "openserver": "sysadmin",
    "recovery": "backup",
    "recover": "backup",
    "disaster recovery": "backup",
    "victoriametrics": "monitoring",
    "prometheus": "monitoring",
    "grafana": "monitoring",
    "conference": "events",
    "event": "events",
    "how-to": "howto",
    "plugin": "ruby",
    "obfuscated": "geek",
}

# Tags to remove entirely
REMOVE_TAGS = {
    "wallpaper", "windows", "microsoft", "upload", "universe", "units",
    "ticket", "suggest", "sqlite", "snow", "skating", "siamese", "fish",
    "betta", "parrot", "novel", "mirror", "mining", "maps", "management",
    "lua", "localization", "lighthouse", "permalink", "patch", "party",
    "dinner", "girls", "amsterdam", "mobile", "history", "healty", "instant",
    "brain", "cache", "compile", "control", "data", "development", "digest",
    "evolution", "extract", "audio", "couchdb", "will_paginate", "everything",
    "answer", "google", "internals",
}

TAGS_RE = re.compile(r'^(tags:\s*\[)(.*?)(\]\s*)$')


def parse_tags(tag_string):
    """Parse the inside of a tags: [...] bracket, handling both quoted and unquoted tags."""
    tags = []
    for item in tag_string.split(","):
        tag = item.strip().strip('"').strip("'").strip()
        if tag:
            tags.append(tag)
    return tags


def transform_tags(tags):
    """Apply merges, removals, and deduplication."""
    new_tags = []
    for tag in tags:
        tag_lower = tag.lower()
        # Check removal first
        if tag_lower in REMOVE_TAGS:
            continue
        # Check merge map
        if tag_lower in MERGE_MAP:
            new_tags.append(MERGE_MAP[tag_lower])
        else:
            new_tags.append(tag_lower)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for t in new_tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def process_file(filepath):
    """Process a single markdown file. Returns (old_tags, new_tags) or None if no tags line."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    changed = False
    old_tags = None
    new_tags = None

    for i, line in enumerate(lines):
        m = TAGS_RE.match(line)
        if m:
            prefix = m.group(1)  # "tags: ["
            tag_str = m.group(2)  # the tags content
            suffix = m.group(3)   # "]" possibly with trailing space

            old_tags = parse_tags(tag_str)
            new_tags = transform_tags(old_tags)

            if old_tags != new_tags:
                new_line = prefix + ", ".join(new_tags) + "]"
                lines[i] = new_line
                changed = True
            break

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return old_tags, new_tags
    elif old_tags is not None:
        return None  # tags found but unchanged
    return None  # no tags line


def main():
    # Find all .en.md and .it.md files
    patterns = [
        os.path.join(POSTS_DIR, "*.en.md"),
        os.path.join(POSTS_DIR, "*.it.md"),
        os.path.join(POSTS_DIR, "*", "index.en.md"),
        os.path.join(POSTS_DIR, "*", "index.it.md"),
    ]

    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    files.sort()

    total_files = 0
    changed_files = 0
    no_tags_files = 0

    print(f"Processing {len(files)} files in {POSTS_DIR}\n")

    for filepath in files:
        total_files += 1
        rel = os.path.relpath(filepath, os.path.dirname(POSTS_DIR))
        result = process_file(filepath)

        if result is None:
            # Either no tags or no change
            pass
        else:
            old_tags, new_tags = result
            changed_files += 1
            print(f"  {rel}")
            print(f"    OLD: [{', '.join(old_tags)}]")
            print(f"    NEW: [{', '.join(new_tags)}]")
            print()

    print(f"\nSummary:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files changed: {changed_files}")
    print(f"  Files unchanged: {total_files - changed_files}")


if __name__ == "__main__":
    main()
