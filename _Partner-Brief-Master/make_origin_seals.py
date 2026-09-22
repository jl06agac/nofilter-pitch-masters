#!/usr/bin/env python3
"""
make_origin_seals.py — per-origin NoFilter seals.

Two arcs of type, the maker above and the coffee below:
  upper arc   NOFILTER
  lower arc   the origin name
with the torn cross in the middle, geometry lifted verbatim from
_CDN-UPLOAD-SAFE/nofilter-favicon-v3.svg. Nothing about the mark is redrawn.

Field colour is the origin's own colour, taken from the COFFEES array in the live
site build, which the Brand Bible makes permanently exclusive to that origin:
  Batang Toru      #2f5d3a
  Batang Gadis     #b8531a
  Gayo Lues        #9c7212
  Arakan Mountains #1f5661
Colour is never the only signal, though: the origin is also named on the seal, so
the four stay tellable apart in mono, in a photocopy, and by a colourblind reader.
White on Gayo Lues ochre measures 4.35:1, just under the 4.5:1 small-text
threshold, which is why the ring type is set at 600 weight. The alternative would
be shifting a locked brand colour, which is not mine to do.

Output is SVG because these are label artwork and have to hold at roughly 15mm on
a sample bag and 80mm on a carton. IBM Plex Mono is embedded as a base64 woff2 so
the type renders identically on a machine that has never had the font installed.

Two variants per origin:
  <slug>.svg           origin colour disc, white marks, for light stock
  <slug>-reversed.svg  white disc, origin colour marks, for dark or photographic stock

Run:  python3 make_origin_seals.py <outdir>
"""

import base64
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
FAVICON = str(HERE / "nofilter-favicon-v3.svg")

ORIGINS = [
    ("Batang Toru", "#2f5d3a"),
    ("Batang Gadis", "#b8531a"),
    ("Gayo Lues", "#9c7212"),
    ("Arakan Mountains", "#1f5661"),
]

CROSS = re.findall(r'<path[^>]*\sd="([^"]+)"', pathlib.Path(FAVICON).read_text())
assert len(CROSS) == 2, "favicon should carry exactly the two mark paths"

FONT_B64 = base64.b64encode((HERE / "f" / "plex600.woff2").read_bytes()).decode()


def seal(origin, colour, reversed_=False):
    field = "#ffffff" if reversed_ else colour
    ink = colour if reversed_ else "#ffffff"
    name = origin.upper()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>NoFilter - {origin}</title>
  <defs>
    <style>
      @font-face{{font-family:'NFPlex';font-weight:600;
        src:url(data:font/woff2;base64,{FONT_B64}) format('woff2');}}
      .a{{font-family:'NFPlex','IBM Plex Mono',monospace;font-weight:600;font-size:12.4px;
          letter-spacing:1.9px;fill:{ink};}}
    </style>
    <path id="arcT"  d="M 100,100 m -76,0 a 76,76 0 1,1 152,0" fill="none"/>
    <path id="arcB"  d="M 100,100 m -76,0 a 76,76 0 0,0 152,0" fill="none"/>
  </defs>
  <circle cx="100" cy="100" r="99" fill="{field}"/>
  <circle cx="100" cy="100" r="88" fill="none" stroke="{ink}" stroke-width="1.3" opacity=".75"/>
  <circle cx="12.6" cy="100" r="2.5" fill="{ink}"/>
  <circle cx="187.4" cy="100" r="2.5" fill="{ink}"/>
  <text class="a"><textPath href="#arcT" startOffset="50%" text-anchor="middle">NOFILTER</textPath></text>
  <text class="a"><textPath href="#arcB" startOffset="50%" text-anchor="middle">{name}</textPath></text>
  <g transform="translate(100 103) scale(0.108) translate(-510 -518)">
    <path d="{CROSS[0]}" fill="{ink}"/><path d="{CROSS[1]}" fill="{ink}"/>
  </g>
</svg>"""


def slug(s):
    return s.lower().replace(" ", "-")


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for name, colour in ORIGINS:
        (out / f"nf-seal-{slug(name)}.svg").write_text(seal(name, colour))
        (out / f"nf-seal-{slug(name)}-reversed.svg").write_text(seal(name, colour, True))
    print(f"wrote {len(ORIGINS) * 2} seals to {out}")


if __name__ == "__main__":
    main()
