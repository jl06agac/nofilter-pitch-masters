# Benchmark master: runbook

The "Benchmark for Sustainable Workplace Coffee" brochure, one tokenised master stamped per market.
Replaces the 2025/Feb 2026 Canva-era PDFs on Drive (`NoFilter - SG's Benchmark for Sustainable Workplace Coffee.pdf` and the UAE copy).
Created 30 Sep 2026.

## Files

| File | Role |
|---|---|
| `NoFilter-Benchmark-Master.html` | The only file to edit. Ten A4 pages, photo-led but self-explaining: cover, who we are, what we offer, forests, coffees, machines, rental inclusions, service & supply, impact, contact. Every section opens with a two-line lede so the brochure reads without a pitch. |
| `markets/SG.json`, `markets/UAE.json` | Market-layer token values. Contact order is this market first, per `_Locale-Presets.md`. |
| `build_benchmark.py` | Stamps the master, gathers assets, optional PDF + page check. |
| `assets-src/` | Fonts (woff2), cover photo and cover wordmark (both extracted from the Part 3 master's base64), and `grain.png`, a PNG stand-in for Part 3's SVG grain that keeps the PDF around 6 MB instead of 14. |

Outputs go to `Clients/Generic/Benchmark/`: `NoFilter-Benchmark-SG.html`, `-UAE.html`, `assets/`, and the PDFs.
Outputs are generated. Never edit them; edit the master and rebuild.

## Build

    cd DO-NOT-TOUCH-Claude-files/_Benchmark-Master
    python3 build_benchmark.py            # HTML + assets for SG and UAE
    python3 build_benchmark.py --pdf      # also PDFs, needs playwright + chromium

`--pdf` measures every page and fails if any content box overflows, an image is broken or a font
fails to load. Pages are fixed A4 boxes with `overflow:hidden`, so an overrun would otherwise hide itself.
Run it after every copy edit. Without playwright, open the HTML in Chrome and print to PDF
(A4, margins none, background graphics on).

## Where things come from

- **Styling**: harvested verbatim from `_Part3-Master/NoFilter-Part3-Master-Contract-v2.html`
  (line ranges named in the CSS provenance comments). Benchmark-only components sit in the second `<style>` block.
  Part 3's Google Fonts link is replaced by local `@font-face` so the PDF renders identically offline.
- **Origin copy, partners, coordinates, tasting notes, profiles**: verbatim from
  `_Partner-Brief-Master/build_brief.py` `ORIGINS`. Seal colours from its `ORIGIN_COLOURS`.
  If the brief's origin data changes, change it here too.
- **Bag photos**: `Marketing/Product-Images/` (the single home for bag photos). Cropped and downsized at build time.
- **Every other photo, including the CaféMatic shots**: `_CDN-UPLOAD-SAFE/`, listed in `CDN_FILES`. JPEGs are downsized to 1600 px and the machine WebPs re-encoded as JPEG at build time; sources are never touched.
- **Machine names, team sizes and spec lines**: verbatim from the website master's `MACHINES` array. Rental inclusions from its SG `machNote`.

## Standing content decisions (30 Sep 2026)

- All four origins shown; Arakan carries the brief's "Low stock" flag. Swap it out when the Myanmar coffee is replaced.
- No prices. Readers are sent to the quote builder on nofilter.sg / nofilter.ae.
- Carbon: no certification claim. +5 mentions Cinta Raja restoration planting and chain-of-custody documentation only.
- Contribution stated as 5 to 10%, never a flat 10%. Never "specialty".
- UAE values for roasting cadence and service response are kept general until confirmed.
- 30 Sep, second pass: Alex asked for "way more photo based", machinery included, framed as what we can offer. The text-heavy nine-reasons page was dropped; its points live in the photo captions.
