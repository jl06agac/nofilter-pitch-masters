# HANDOVER — NoFilter marketing site (workplace/shop build)

_For the next Claude chat. Files on disk are the source of truth; this is a map, not gospel._
_Read `/Users/alexanderclark/Desktop/NoFilter/CLAUDE.md` first (standing orders), then this._

## What this work is
Building NoFilter's public marketing site — a static, multi-page, stamped Netlify site — by
**harvesting tested components verbatim** from the Generic master (VERBATIM-OR-NOTHING standing order).
This session focused on the **Shop** (B2C e-comm) and the **Workplace ("At Work")** page + its **gated builder**.

## Paths, pipeline, verify (memorise these)
- Site: `Marketing/NoFilter-Website/` — edit `*.src.html`, then **stamp** to `*.html`.
  (Note: root CLAUDE.md still calls this `Marketing/NF-Site/` — stale; real folder is `NoFilter-Website/`.)
- Partials (single source of truth, shared across pages): `DO-NOT-TOUCH-Claude-files/_partials/`
  `nfbar, site-head, hero-holdtheline, impact-holdtheline, choice-holdtheline, coffee-picker, machine-picker, footer`
- Stamp tool: `DO-NOT-TOUCH-Claude-files/_tools/nf-stamp.mjs` — expands `[[INCLUDE:name]]` + `[[TOKEN]]`.
- **Stamp command** (run from `Marketing/NoFilter-Website/`):
  `node ../../DO-NOT-TOUCH-Claude-files/_tools/nf-stamp.mjs <page>.src.html /tmp/empty.json --out <page>.html`
  Pages: `index machines shop workplace` (`workplace-builder.html` was DELETED 4 Sep 2026 — the quote builder now lives only in the website master; see SOURCE-OF-TRUTH-REGISTER.md §2) (was standalone, NOT stamped — see below).
- **Verify**: extract each inline `<script>`, strip HTML comments (`re.sub(r'<!--.*?-->','',h,flags=re.S)`),
  run `node --check` on each. (A python one-liner doing this is used all session.)
- Generic master (for harvesting): `Clients/Generic/NoFilter-Generic-Part2-SG.html` (~5900 lines, 406KB).
- Assets: LOCAL originals at `Clients/Zoos/_TEMPLATE/*.mp4`; served in prod from `https://nofilter-shared.netlify.app/`.

## ⚠️ Environment constraint — YOU CANNOT VISUALLY RENDER HERE
- Headless chromium (playwright) fails: missing `libXdamage.so.1`, no root/apt to install.
- Chrome MCP prepends `https://` to `file://` URLs, so it can't open local files either.
- **So: verify with `node --check` + careful reasoning; Alex is the eyes.** Don't burn time trying to render.
- To view an image you generate (e.g. an ffmpeg contact sheet), copy it into a **mounted** folder
  (Desktop/…) then `Read` it — `Read` cannot reach `/tmp` or `/sessions/…`.

## STATE — what's built this session

### Shop (`shop.src.html` + `_partials/coffee-picker.html`) — DONE, needs Alex's live click-through
- Carousel replaced with a **grid of quick-buy tiles**: tap the bag → reveals size pills (1KG/250G),
  a rotating **10% conservation seal + "raised SGD" figure**, price, and an **Add-to-cart button that
  morphs into a −/qty/+ stepper**. Price + raised figures **tally with qty**. Minus to 0 collapses the tile.
- Tasting-note chips + **Acidity/Body/Roast** dot scales restored on tiles.
- **Find out more** still opens the origin dossier (hero-colour morph) below the grid.
- **Nav cart** (in `nfbar`): icon + live count badge (pulses on add) + `window.NFCart` store.
- **Toast** ("Added — View cart") + **slide-in cart drawer** (lines, steppers, subtotal, 10%-to-forest, Checkout →).
- `window.NFCart` persistence: **`PERSIST=false` in `nfbar.html`** → session-only during build (empties on reload).
  **Flip `PERSIST=true` before launch** for a real cross-page cart. Checkout is a placeholder (Shopify later).

### Workplace ("At Work") page (`workplace.src.html`) — heavy WIP, Alex iterating
Order of sections: **orange hero → clears/keeps immersive → "Why this coffee" (pared-back manifesto) → 4 feature tiles → machine picker → request-access gate → footer.**
- **Orange strobe hero** (full-bleed, id="cover", nav enmeshed over it like the homepage hero):
  - Strobing headline cycling 4 messages (strobe-cut); eyebrow removed.
  - **Foliage glimpse**: `atwork-loop.mp4` (Arakan canopy, boomerang loop, sky cropped) flashes behind the
    text via the orange `.aw-field` blinking — fires on **every other headline cut** (`cutCount%2`), synced.
  - **Nav "+" strobes white↔orange in sync** with the glimpse (fill-animated; opacity would phase-cancel).
    Nav "+" is forced white over the orange hero via `.nfbar:not(.is-stuck) .lk-plus path{fill:#fff}` (target the
    PATH — inline fill is on the path, not the group). CTA also flipped white on the hero.
  - **Flip-counter odometer** (rolling digits, starts on scroll-into-view). Metric = placeholder "m² of rainforest" — **Alex to confirm real number/label.**
  - Pulsing triple-chevron scroll cue at the bottom (click scrolls past the band). Height ~82vh.
- **Clears/keeps immersive** = shared `choice-holdtheline` partial, dropped under the hero.
  - **SEAM is now the packaging contour**: normalised the `<polyline id="back-contour">` from the uploaded
    `250g-back.svg` (Batang Gadis) into the `JAG` array; `JAG_VH=26` sets its amplitude (**tune this number** to
    match the packaging ridge). Subtle GPS coordinate `0°30′30″N · 99°47′44″E` stamped bottom-right (`.cs-coord`).
  - Optional mission close-line (`.cs-close`, "Most workplaces go with the first…") is **dormant** — only shows
    with `body.cs-mission` (not currently applied; the manifesto carries that beat instead).
  - Card height reduced (`.choice-pin .cs-stage` top/bottom `11vh`). NB: the device has an intentional
    text-free gap mid-wipe (clears text fades ~44%, keeps text appears ~78%).
- **"Why this coffee"** section: just switched to the **pared-back "text as subject" device** matching the
  homepage About (`.band band--pa` + `.eyebrow`/`.sec-title`/`.sec-lead`, plain black headline). The richer
  original (`.wp-mani-*`, orange-emphasis head + pull-quote) is REMOVED from markup but its CSS still sits
  dormant in the page `<style>`. **Alex is comparing clean-vs-rich — decision pending.**
- 4 feature tiles, machine picker (`[[INCLUDE:machine-picker]]`), **request-access gate** (name + work email,
  freemail blocked, Netlify Forms, sets `sessionStorage nf_wp_access` then links to the builder).

### Gated workplace builder — DELETED 4 Sep 2026, now the master's §12 QUOTE CONSOLE (was `workplace-builder.html`, standalone, NOT stamped
- A near-verbatim copy of the Generic Part2 configurator (whole pricing engine intact — sliders, machine
  steppers, morph, quote, submit). **Coffee step swapped** to shop-style grid tiles (notes + A/B/R), preserving
  the engine contract `window.__pickedOrigins()` → `compute()` (kept inside the same `<script>` closure — do NOT
  move `compute` out of it). Client (UWCSEA) branding neutralised; soft gate-check redirects to `workplace.html#quote`
  unless `sessionStorage nf_wp_access` set (fails open on error for local testing). Engine map lives in this chat's history.

### Nav (`_partials/nfbar.html`) — shared, changed this session
- Added cart (icon/badge/`window.NFCart`, `PERSIST=false`).
- **Scroll-hide uses an accumulator** (`__nfAcc`): hides on sustained scroll-down, returns on sustained
  scroll-up, ignores jitter, always shown at top. (A per-tick delta version FAILED on slow scroll — don't revert.)
- Height reverted to original (padding 26/14, lockup 60px) — the "imposing" complaint was the video card, not the nav.

### Machine picker (`_partials/machine-picker.html`)
- Spec detail panel enlarged to the master's focus-mode sizing (`.mx-inline` 1240px, gallery 440px, bigger type).

## OPEN THREADS / decisions pending from Alex
1. **Manifesto**: keep pared-back (just shipped) or the richer version? 
2. **Seam amplitude** `JAG_VH` (26) — match to the real packaging ridge once he eyeballs it.
3. **Hero counter** — real metric + number + label (currently placeholder "m² of rainforest").
4. **Coffee-pour glimpses** — Alex may want to alternate forest + an espresso/latte pour clip in the glimpse
   rotation. Candidate local clips: `wp-pour.mp4`, `coffee-cup-motion.mp4`, `cafe-scene-*.mp4` in `_TEMPLATE/`.
5. Strobe/glimpse cadence (`cutCount%2`), whether to draw a visible cream stroke ON the seam line, and whether
   the seam should also appear on the homepage (it currently does — shared partial).
6. **Machines page** has no full spec panel (only 1-line specs) — offered to add the big panel; not yet done.
7. Longer term: build a proper public builder / origins page; wire cart → Shopify.

## Assets created this session (in `Marketing/NoFilter-Website/`)
- `atwork-loop.mp4` + `atwork-loop-poster.jpg` — Arakan canopy, boomerang, cropped (the live hero glimpse).
- `atwork-forest-loop.mp4/-poster`, `atwork-rain-loop.mp4/-poster` — earlier tests (rain reversed-upward if boomeranged — DON'T).
- Uploaded packaging SVG: `uploads/250g-back.svg` (+ its coordinate-pin key in chat). Front + back panel pins available.
- **Temp junk to bin** (sandbox couldn't delete): `_frames-check.jpg`, `_rain-check.jpg`, and `index.html.bak`.
- `_test-*.html` in the site folder are prototypes (clickbuy, dossier, atwork-orange, etc.) — not part of the site.

## ffmpeg recipes used (for footage loops)
- Find stillest window: `fps=10,scale=320:-1,tblend=all_mode=difference,signalstats,metadata=print` → parse `YAVG` per frame, min over a sliding window.
- **Boomerang loop** (seamless, near-static footage only): trim → `-vf reverse` → `concat=n=2`. **Never boomerang directional motion (rain/pours).**
