# Bundler — ARCHIVED (kept in case of future need)

`bundle.py` / `unbundle.py` inline every relative asset (images, fonts, video) into a **single
self-contained HTML file** as base64. `unbundle.py` reverses it.

## Why it's archived, not deleted
NoFilter pitches now ship **URL-based**: the working `.html` opens straight in Chrome, heavy media
streams from the shared-assets site (`nofilter-shared.netlify.app`) or the local `_shared/`
symlinks, and you iterate edit → save → Cmd+R with **no build step** (preview = production). That
is the way for Parts 1, 2 and 3. Alex prefers sending URL pitches.

Bundling is the **opposite** of an iteration tool — it inserts a re-bundle step between every edit
and viewing, and a base64 monolith **crashes** media-heavy pages (Parts 1 & 2). So it has no place
in the normal workflow.

## The one case it's still good for
Producing a **portable single file** to email or hand off where there's no server and no shared-site
connection (the old brochure and the download-only zoo one-offs used it). Kept here purely for that
"what if we ever need to send a standalone file" scenario.

## How to run it (if ever needed)
```bash
python3 bundle.py <input>.html          # → <input>-bundled.html
python3 unbundle.py <bundled>.html      # reverse
```
Do **not** run it on a Part 1 or Part 2 (it crashes them). Never a substitute for the URL workflow.

## Note on the scattered copies
Working copies of `bundle.py` still sit inside the legacy zoo pitch folders and the brochure (those
dormant pitches were built with it). Those are left untouched with their pitches. **This folder is
the canonical archived reference.**
