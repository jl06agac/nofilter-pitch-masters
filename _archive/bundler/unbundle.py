#!/usr/bin/env python3
"""
unbundle.py — Extract base64-embedded images and fonts from an HTML file.

Run once on your bloated HTML. Produces:
  - <name>-source.html  : lean HTML with relative paths (edit this one)
  - assets/             : folder with all extracted images/fonts

Usage:
    python3 unbundle.py path/to/your.html
"""

import sys
import re
import base64
from pathlib import Path

EXT_MAP = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "font/woff2": "woff2",
    "font/woff": "woff",
    "font/ttf": "ttf",
    "font/otf": "otf",
    "application/font-woff2": "woff2",
    "application/font-woff": "woff",
    "application/x-font-ttf": "ttf",
}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 unbundle.py path/to/your.html")
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()
    if not html_path.exists():
        print(f"Error: {html_path} not found")
        sys.exit(1)

    base_dir = html_path.parent
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    html = html_path.read_text(encoding="utf-8")
    original_size = len(html)

    # Match: data:<media-type>;base64,<data>
    pattern = re.compile(r"data:([^;,\s]+);base64,([A-Za-z0-9+/=]+)")

    counter = {"n": 0}
    seen = {}  # dedupe identical assets

    def replace(match):
        media_type = match.group(1).strip().lower()
        b64data = match.group(2)

        if b64data in seen:
            return seen[b64data]

        ext = EXT_MAP.get(media_type, "bin")
        counter["n"] += 1
        filename = f"asset_{counter['n']:03d}.{ext}"
        filepath = assets_dir / filename

        try:
            filepath.write_bytes(base64.b64decode(b64data))
        except Exception as e:
            print(f"  Warning: failed to decode {filename}: {e}")
            return match.group(0)

        relative = f"assets/{filename}"
        seen[b64data] = relative
        size_kb = filepath.stat().st_size // 1024
        print(f"  Extracted {filename} ({size_kb} KB)")
        return relative

    new_html = pattern.sub(replace, html)

    output_path = base_dir / f"{html_path.stem}-source.html"
    output_path.write_text(new_html, encoding="utf-8")

    print()
    print(f"Done.")
    print(f"  Source HTML: {output_path.name}  ({len(new_html) // 1024} KB)")
    print(f"  Assets:      {assets_dir.name}/  ({counter['n']} files)")
    print(f"  Reduced:     {original_size // 1024} KB -> {len(new_html) // 1024} KB")


if __name__ == "__main__":
    main()
