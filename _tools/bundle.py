#!/usr/bin/env python3
"""
bundle.py — Re-embed referenced assets into a self-contained HTML file.

Run before sending to a client. Reads relative src/url() references,
encodes them as base64 data URIs, outputs a single self-contained file.

Usage:
    python3 bundle.py path/to/your-source.html
"""

from __future__ import annotations

import sys
import re
import base64
import mimetypes
from pathlib import Path

MIME_FALLBACK = {
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 bundle.py path/to/your-source.html")
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()
    if not html_path.exists():
        print(f"Error: {html_path} not found")
        sys.exit(1)

    base_dir = html_path.parent
    html = html_path.read_text(encoding="utf-8")

    stats = {"embedded": 0, "skipped": 0, "cached": 0}
    cache = {}

    def to_data_uri(relpath):
        if relpath in cache:
            stats["cached"] += 1
            return cache[relpath]

        asset = (base_dir / relpath).resolve()
        if not asset.exists() or not asset.is_file():
            print(f"  Skipped (not found): {relpath}")
            stats["skipped"] += 1
            return None

        mime, _ = mimetypes.guess_type(str(asset))
        if mime is None:
            mime = MIME_FALLBACK.get(asset.suffix.lower(), "application/octet-stream")

        b64 = base64.b64encode(asset.read_bytes()).decode("ascii")
        uri = f"data:{mime};base64,{b64}"
        cache[relpath] = uri
        stats["embedded"] += 1
        size_kb = asset.stat().st_size // 1024
        print(f"  Embedded {relpath} ({size_kb} KB)")
        return uri

    def is_relative(path):
        path = path.strip()
        return not (
            path.startswith("data:")
            or path.startswith("http://")
            or path.startswith("https://")
            or path.startswith("//")
            or path.startswith("#")
            or path.startswith("mailto:")
        )

    # 1. HTML attribute: src="..."
    def replace_attr(match):
        prefix, quote, path, _ = match.groups()
        if not is_relative(path):
            return match.group(0)
        uri = to_data_uri(path)
        if uri is None:
            return match.group(0)
        return f'{prefix}{quote}{uri}{quote}'

    html = re.sub(r'''(src=)(["'])([^"']+)(\2)''', replace_attr, html)

    # 2. HTML attribute: href="..." (only binary asset extensions)
    def replace_href(match):
        prefix, quote, path, _ = match.groups()
        if not is_relative(path):
            return match.group(0)
        ext = Path(path).suffix.lower()
        if ext not in MIME_FALLBACK and ext not in (".css", ".ico"):
            return match.group(0)
        uri = to_data_uri(path)
        if uri is None:
            return match.group(0)
        return f'{prefix}{quote}{uri}{quote}'

    html = re.sub(r'''(href=)(["'])([^"']+)(\2)''', replace_href, html)

    # 3. JS object property: src: "..." or href: "..."
    # (React.createElement props, etc.)
    def replace_js_prop(match):
        prefix, quote, path, _ = match.groups()
        if not is_relative(path):
            return match.group(0)
        uri = to_data_uri(path)
        if uri is None:
            return match.group(0)
        return f'{prefix}{quote}{uri}{quote}'

    html = re.sub(r'''((?:src|href):\s*)(["'])([^"']+)(\2)''', replace_js_prop, html)

    # 4. CSS url(...) - quoted or unquoted
    def replace_url(match):
        full = match.group(0)
        inner = match.group(1).strip().strip('"').strip("'")
        if not is_relative(inner):
            return full
        uri = to_data_uri(inner)
        if uri is None:
            return full
        return f'url("{uri}")'

    html = re.sub(r'''url\(\s*([^)]+?)\s*\)''', replace_url, html)

    output_path = base_dir / f"{html_path.stem.replace('-source', '')}-bundled.html"
    output_path.write_text(html, encoding="utf-8")

    print()
    print(f"Done.")
    print(f"  Bundled HTML: {output_path.name}  ({len(html) // 1024} KB)")
    print(f"  Embedded:     {stats['embedded']} files")
    if stats["cached"]:
        print(f"  Deduped:      {stats['cached']} repeat references")
    if stats["skipped"]:
        print(f"  Missing:      {stats['skipped']} files (left as-is)")


if __name__ == "__main__":
    main()
