# PART 2 BUILD RUNBOOK — read this first, every new Part 2 build

> ⤴ **Before anything, read the universal front door: [`_NEW-PITCH-INTAKE.md`](../_NEW-PITCH-INTAKE.md)** — the renderable guarantee (nothing broken on copy), the intake prompts, and the website-nav spoof best practices that apply to every part.

**This file is the single front door for building any Part 2 microsite — school, workplace
or zoo.** If you are about to make a new Part 2, read this top to bottom before you touch
anything. It owns the *process*. Part 2 is **stamped, not hand-filled** — the full stamp
mechanics live in [`../_STAMP-A-PITCH.md`](../_STAMP-A-PITCH.md). Token **definitions** live in
[`../_TOKEN-DICTIONARY.md`](../_TOKEN-DICTIONARY.md) (the single source of truth); the
*placeholder/example values* live in `NoFilter-Part2-MasterTemplate-TOKENS.md` (beside it).

> Files on disk are the source of truth. Confirm before renaming, moving, overwriting or
> deleting anything. Nothing goes to trash — superseded files move to `_archive/`.

---

## What's in this folder / how to open

`_Part2-Master/` is the starting point for **every** Part 2, whatever the target (school,
workplace or zoo). Key contents:

- **`NoFilter-Part2-MasterTemplate.html`** — the master. Part 2 is **not** hand-filled — it is
  built via the **STAMP pipeline** (`_tools/nf-stamp.mjs` merges a market preset + a client skin
  into the master). Don't edit it in place; don't rename it to `index.html`. You *can* open the
  raw file to inspect it, but it won't look finished (raw `[[TOKENS]]` + placeholder images).
- **`_presets/`** — market presets (`SG.json`, `UAE.json`, `London.json`): currency, contact,
  rate, legal. **`_skins/`** — one `<Client>.json` per client (copy `_CLIENT-TEMPLATE.json`).
- **`Part2-Build-Runbook.md`** (this file) — the process. Full stamp mechanics: `../_STAMP-A-PITCH.md`.
- **`NoFilter-Part2-MasterTemplate-TOKENS.md`** — placeholder/example values + the MT2 manifest.
- **`_device-donor/`** — a parts-only donor (video-intro + CRT animation) to lift devices FROM.
  It is **not** a master and is never stamped or shipped.

There is **one** master; never fork it per school/zoo/workplace (the difference is the preset +
skin values the stamp fills in).

---

## What the master is (and why)

`NoFilter-Part2-MasterTemplate.html` in this folder is the **audience-neutral master**. It
is the tokenised Part 2 base (from the Accenture stepJ v133 build, reconciled to the canonical
token vocabulary), carrying our most polished architecture and prime copy forward with
everything target-specific lifted out into tokens.

You do **not** copy this file and hand-fill it. A Part 2 is produced by the **STAMP pipeline**
(`_tools/nf-stamp.mjs`), which merges a market preset + a client skin into the master and
writes a per-client file. See §1–§2 and [`../_STAMP-A-PITCH.md`](../_STAMP-A-PITCH.md).

The master also defines the **deploy method**: `index.html` shipped beside a folder of
real asset files (the always-URL / UWCSEA pattern) — never a base64 bundle (see §7).

---

## The golden rule: ONE template, never fork per type

Per-audience differences (school / workplace / zoo) are **token VALUES and a few rewritten
tiles — not separate template files.** Do not create `NoFilter-ZOO-PartTwo.html` or a
per-type `_TEMPLATE`. That is exactly how the old `Schools/_TEMPLATE` ended up with UWCSEA
branding baked into it and became a rogue second source of truth. There is one master. You
stamp it per *client* (market preset + client skin) and ship.

---

## Where things live

```
NoFilter/
├─ DO-NOT-TOUCH-Claude-files/                 ← all the machinery (you work here)
│   ├─ _Part2-Master/            ← the master + presets/skins + these docs
│   │   ├─ NoFilter-Part2-MasterTemplate.html   ← STAMP this per build (never hand-fill)
│   │   ├─ _presets/{SG,UAE}.json                ← market presets (currency/contact/rate)
│   │   ├─ _skins/_CLIENT-TEMPLATE.json          ← copy → _skins/<Client>.json per build
│   │   ├─ Part2-Build-Runbook.md                ← this file
│   │   └─ NoFilter-Part2-MasterTemplate-TOKENS.md  ← placeholder/example values
│   ├─ _tools/nf-stamp.mjs       ← the stamp engine (preset + skin → client HTML)
│   ├─ _STAMP-A-PITCH.md         ← full stamp mechanics
│   └─ _TOKEN-DICTIONARY.md      ← canonical token DEFINITIONS (single source of truth)
└─ Clients/
    ├─ _shared/                  ← canonical heavy assets (symlink targets). NEVER move/delete.
    └─ Schools/ Workplaces/ Zoos/  ← real CLIENT builds only, one folder per client
```

A client build lives in its type folder, e.g. `Workplaces/Aon/`. Inside it: the working
HTML source, the counter file, and the client's own real assets (logo, mockups) in a small
`assets/`. Shared media is **not** stored per-pitch — both preview and deploy reference it by
URL via `[[SHARED_BASE]]` (the shared-assets site). The deployed artifact is tiny: `index.html`
+ the client-specific reals; the heavy media streams from the shared site (see §8).

---

## The build, step by step

### 0. Intake
Settle these before copying anything (token definitions in `../_TOKEN-DICTIONARY.md`;
placeholder values in `NoFilter-Part2-MasterTemplate-TOKENS.md`):
- **Target name**, and URL-encoded form (mailto/WhatsApp).
- **Audience type**: school / workplace / zoo — this drives every per-audience token column.
- **Colophon code** (`DP-2026-[XX]02` — Part 2 always ends `02`).
- **Locale preset** (Singapore / UAE): apply currency, contact and rate-card values from
  `DO-NOT-TOUCH-Claude-files/_Locale-Presets.md` *before* the client tokens. Contact block stays dual — for a
  **UAE** build, reorder the two `deets` lines so the `UAE ·` line shows first.
- **Harvested brand**: real logo SVG(s), brand hex, fonts — measured via DevTools console
  probes, never eyeballed from a screenshot.
- **One true researched detail** about the target for the intro letter (a named system, a
  person, a real article). Specificity is the point — no generic filler.

### 1. Build the client skin
Copy `_skins/_CLIENT-TEMPLATE.json` to `_skins/<Client>.json` and fill in the client-specific
values (name, brand, colophon, narrative hooks). The **market** values (currency, contact, rate
card) come from the market preset — `_presets/SG.json` or `_presets/UAE.json` — you do not
re-enter them in the skin. Token definitions: `../_TOKEN-DICTIONARY.md`; example values:
`NoFilter-Part2-MasterTemplate-TOKENS.md`. Full skin schema: `../_STAMP-A-PITCH.md`.

### 2. Stamp the master into the client folder
Run the stamp — it merges the market preset + client skin into the master and writes the
per-client file:
```
node ../_tools/nf-stamp.mjs NoFilter-Part2-MasterTemplate.html \
  _presets/<MARKET>.json _skins/<Client>.json \
  --out ../Workplaces/<Client>/NoFilter-<Client>-Part2.html
```
(`<MARKET>` = `SG` or `UAE`.) **Do NOT stamp to `index.html`** — that name is reserved for the
Netlify deploy artifact; naming a working file `index.html` has caused critical overwrites. The
deploy `index.html` is produced later, in its own folder.

Then run the **token gate** on the stamped output — it must return nothing:
```
grep -oE '\[\[[A-Z_]+\]\]' <your-file>.html | sort -u
```

### 3. Swap the brand chrome
The benchmark keeps UWCSEA's nav structure/sprite/fonts as reusable chrome, but the UWCSEA
identity must be grafted out. Replace:
- the **three** `aria-label="UWC South East Asia"` logo labels with the target's,
- the nav rail labels (UWCSEA: `Dover Campus` / `East Campus`) and the community nav item,
- the colophon code (`DP-2026-NF02` → the target's `DP-2026-[XX]02`),
- the provenance code-comments that still say "UWCSEA … from Part 1" (cosmetic, but overwrite
  them when you graft so the file's provenance is honest).

### 4. Hand-edit the JS volume constants  ⚠️ NOT tokenised
By deliberate design the count-up animations target literal numbers, not tokens. They still
hold **UWCSEA's** figures and WILL silently render UWCSEA's volume on your build if skipped.
Run the **constant gate** and edit each real hit:
```
grep -n '111875\|11188\|2500' <your-file>.html
```
What each hit is:
- `value="111875"` — the volume **slider** default (easy to miss; no comment beside it) → target's annual cups.
- `const COFFEE_CUPS = 111875` → target's annual cups.
- `var GUEST_TARGET = 111875` → same annual-cups figure (hero hook counter).
- `IMPACT_TARGET = 11188` → target's annual conservation contribution (cups × 10¢).
- `ticker:{to:111875…}` (CRT "cups poured") → target's annual cups.
- (removed) `CUP_RETAIL` no longer exists — the retail-cup % readout was dropped; the dark payoff now shows an absolute `[[CURRENCY]] x.xx per cup, all-in`. See `_Locale-Presets.md` → Part 2 slider.
- **`var wait = 2500 …` is a FALSE POSITIVE** — that's the cup-drop animation timer (2.5s),
  NOT the community number. Leave it. The community figure is already the `[[COMMUNITY_NUM]]`
  token, set in step 2.

### 5. Replace mockups and the counter source
- Swap the three placeholder renders with target-branded versions:
  `assets/bag-mockup-target.png`, `assets/machine-livery-target.png`,
  `assets/reusable-cup-target.png`.
- Replace `[[COUNTER_SRC]]` (the split-flap counter iframe) with the target's counter file,
  e.g. `aon-counter.html`.

### 6. Rewrite the type-specific narrative
Some content is narrative, not slot-fillable — a pure find-and-replace produces a
school-flavoured zoo. Rewrite per type:
- **Intro letter** — personal, built around your one researched true detail.
- **CRT typewriter lines** — the "what the coffee teaches" framing.
- **The "Closer than you'd think" tile** — UWCSEA's version is school field trips to origin.
  Repurpose it: a **workplace** CSR/offsite visit to origin; a **zoo's** existing
  conservation-travel or keeper-exchange program.

### 7. Preview locally & iterate — DO NOT bundle
**Default (always-URL):** set `[[SHARED_BASE]]` to the **live shared-assets URL** — the same
value you deploy with — then just open the working file:
```bash
open -a "Google Chrome" "Workplaces/<Client>/NoFilter-<Client>-Part2.html"
```
The shared media streams from the shared site, so **what you preview is exactly what deploys**
(preview = production; you catch a missing/misnamed shared asset now, not after sending the
link). Iterate with **edit → save → Cmd+R**. No build step.
- The pitch's own `assets/` holds only the **client-specific reals** — the 3 `-target.png`
  mockups, the counter file, the logo. Add those as you build.
- Needs internet + the shared site live (a non-issue in normal use).
- **Offline / before the shared site exists (fallback only):** point `[[SHARED_BASE]]` at local
  files instead — `cp -R "Schools/UWCSEA/assets" "Workplaces/<Client>/assets"` (same depth,
  keeps symlinks) and set `[[SHARED_BASE]]` to `assets`. That `cp -R` also drags UWCSEA's own
  reals in, so don't mistake a leftover UWCSEA image for the client's during the brand swap.
- **Never run `bundle.py` on a Part 2** — base64 monolith crashes the browser.

### 8. Deploy (shared-asset model)
Switch `[[SHARED_BASE]]` from `assets` to the **live shared-assets site URL**
(e.g. `https://nofilter-shared.netlify.app`). The shared media (videos, maps, fonts) then
streams from that one site — you do **not** upload it.

The deploy folder you push to the client's Netlify site contains **only**:
- `index.html` (with `[[SHARED_BASE]]` = the shared URL), and
- a small `assets/` folder of the **client-specific reals only**: the 3 `-target.png` mockups,
  the counter file, the logo. No videos, no shared media — those live on the shared site.

There is **no "materialize the symlinks" step anymore.** The symlinks were a local-preview
convenience; the deploy never carries them or the shared files. This is what makes the upload
tiny (HTML + a few small images instead of ~100 MB).

- **Order:** the shared-assets site must be live first (see CLAUDE.md → "Shared assets").
- Netlify is case-sensitive: `Rainforest.mp3` ≠ `rainforest.mp3`. Match every `src` exactly.
- After deploy, open a client asset URL and a `[[SHARED_BASE]]` asset URL — a 404 on either is
  the problem, before touching any JS.
- Hard-refresh (Cmd+Shift+R) and check in incognito; caching hides stale versions.

### 9. Post-deploy cleanup — careful, gated
On the shared-asset model the deploy folder is now small (HTML + a few client-specific images),
so there's little disk to reclaim. The discipline that matters:
- **NEVER delete anything in `_shared/` or on the shared-assets site.** Those are the canonical
  targets every pitch points at; deleting/renaming one breaks every live pitch at once.
- **KEEP** the working source HTML, the counter file, the client's own real assets, and the
  working `assets/` symlinks — that's the lightweight, editable, re-deployable record.
- If a client-specific file exists *only* in a deploy folder (a mockup made there and never
  copied back), don't delete it blind — confirm it exists in the working tree first.
- **NEVER auto-delete on a timer or as a blanket "remove duplication" sweep.**

---

## Per-audience nuance — quick reference

The full placeholder-value table is in `NoFilter-Part2-MasterTemplate-TOKENS.md` (token
definitions: `../_TOKEN-DICTIONARY.md`). The shape of the differences:

| | School (UWCSEA) | Workplace | Zoo |
|---|---|---|---|
| Venue | campus / on campus | office / at work | the zoo / at the zoo |
| Audience | students, staff, parents | the team, colleagues | visitors, staff |
| Volume basis | community × uptake × teaching days | headcount × uptake × working days | footfall/community × uptake × open days |
| Repurposed tile | Outdoor-Ed field trip to origin | CSR / offsite visit to origin | conservation-travel / keeper-exchange |
| Colophon | `DP-2026-NF02` | `DP-2026-[XX]02` | `DP-2026-[XX]02` |

---

## NEVER (carried from DO-NOT-TOUCH-Claude-files/CLAUDE.md + hard-won here)

- **Never fork the template per type.** One master; per-audience = token values (skin) + rewritten tiles.
- **Never name a working file `index.html`.** That name is the deploy artifact only.
- **Never bundle a Part 2** (base64 monolith crashes media-heavy pages).
- **Never delete anything in `_shared/`**, or any real file that might be a symlink target. (This
  is the only deletion rule that bites: a deploy folder is disposable — its only local-only files
  are the client-specific reals, which also live in the working pitch folder.)
- **Never guess a brand value** a DevTools probe can measure exactly.

## Final gates before deploy
```
grep -oE '\[\[[A-Z_]+\]\]' <file>.html | sort -u        # tokens: must be empty
grep -n '111875\|11188\|2500' <file>.html   # JS constants: each reviewed (2500=timer, ignore)
```

---

*Master provenance: `NoFilter-Part2-MasterTemplate.html`, tokenised from the Accenture stepJ
v133 base and reconciled to the canonical `_TOKEN-DICTIONARY.md` vocabulary. The old 137-token
`NoFilter-Part2-Master-Template.html` (UWCSEA-derived) was retired and deleted 3 Jul 2026;
builds now go through the STAMP pipeline (market preset + client skin via `_tools/nf-stamp.mjs`).*
