# PART 1 BUILD RUNBOOK — read this first, every new Part 1 build

> ⤴ **Before anything, read the universal front door: [`_NEW-PITCH-INTAKE.md`](../_NEW-PITCH-INTAKE.md)** — the renderable guarantee (nothing broken on copy), the intake prompts, and the website-nav spoof best practices that apply to every part.

**This is the single front door for building any Part 1 microsite — school, workplace or
zoo.** Part 1 is stage one of the client journey: **Part 1 (intro) → Part 2 (proposal + the
client's price/machine/term choices) → Part 3 (the signable contract) → PDF → sign → take down or
morph to a live NGO-contribution tracker.** This file owns the Part 1 *process*;
`Part1-Template-Tokens.md` (beside it) owns the *values*.

> Files on disk are the source of truth. Confirm before renaming, moving, overwriting or
> deleting anything. Nothing goes to trash — superseded files move to `_archive/`.

---

## What's in this folder / how to open

`_Part1-Master/` is the starting point for **every** Part 1 (the "Conservation Coffee
Partnership" intro), whatever the target — school, workplace or zoo. Three files:

- **`NoFilter-Part1-Master-Template.html`** — the master. Part 1 is built **manually**: you copy
  this file into the client folder and fill its `[[TOKEN]]`s (Part 1 is *not* stamped). It links
  forward to Part 2 via `[[PART2_URL]]`. Don't edit it in place; don't rename it to `index.html`.
- **`Part1-Build-Runbook.md`** (this file) — the process, start to finish.
- **`Part1-Template-Tokens.md`** — the per-audience placeholder values for the render-clean pass.

To just look at the master, open the `.html` in a browser — it won't look finished (raw
`[[TOKENS]]` + a placeholder hero); that's expected, it's a blank to fill. There is **one**
master; never fork it per school/zoo/workplace (the difference is the token values you fill in).

---

## What the benchmark is

`NoFilter-Part1-Master-Template.html` is the audience-neutral Part 1, tokenised from the
**UWCSEA Part 1** build — the most complete exemplar of the current 9-section design
(`cover · impact · why · coffees · origins · how · verify · workplace · talk`). The
conservation narrative (origins, mechanism, verification, the live GIS map) is shared house
copy carried forward intact; only target-specific identity, venue and audience language is
tokenised. **UWCSEA is the parent of every Part 1, regardless of type.**

Deploy method (same as Part 2): `index.html` beside a folder of **real assets** — never a
base64 bundle (the bundles crash on media-heavy pages).

---

## The golden rule: ONE template, never fork per type

Per-audience differences (school / workplace / zoo) are **token values + a few rewritten
narrative lines — not separate template files.** Do not create a per-type `_TEMPLATE`. That
is how the old school templates drifted and went stale. There is one benchmark; you copy it
per *client*.

---

## Where things live

```
NoFilter/
├─ DO-NOT-TOUCH-Claude-files/
│  ├─ _Part1-Master/   ← you are here (Part 1 benchmark + these docs)
│  └─ _Part2-Master/   ← Part 2 benchmark + its runbook/tokens
├─ Clients/
│  ├─ _shared/         ← canonical heavy assets (symlink targets). NEVER move or delete.
│  └─ Schools/ Workplaces/ Zoos/  ← real CLIENT journey folders (one per client)
```

A client's journey folder (e.g. `Workplaces/Aon/`) holds all stages for that client: the
Part 1, Part 2 (and later Part 3) working sources, the client's own real assets, and an
`assets/` folder of **symlinks** into `_shared/`. Each stage's deployable artifact (`index.html`
+ materialized real assets) is generated into its own deploy subfolder and is disposable.

---

## The build, step by step

### 0. Intake
- **Target name** + audience type (school / workplace / zoo).
- **Colophon code** `DP-2026-[XX]01` (Part 1 ends `01`).
- **Locale preset** (Singapore / UAE): apply currency symbol (`[[CUR_SYMBOL]]` on the
  conservation counter) and contact values from `DO-NOT-TOUCH-Claude-files/_Locale-Presets.md`. Contact block
  stays dual — for a **UAE** build, reorder the two `deets` lines so `UAE ·` shows first.
- **Community number** — the headline figure (`[[COMMUNITY_NUM]]`).
- **Harvested brand** — real logo SVG, brand hex, fonts (DevTools probes, never eyeballed).
- **Hero poster image** for the target (`[[HERO_POSTER]]`).

### 1. Copy the benchmark into the client journey folder
Copy `_Part1-Master/NoFilter-Part1-Master-Template.html` into the client folder under a
working name, e.g. `Workplaces/Aon/NoFilter-Aon-PartOne.html`.
**Do NOT name it `index.html` yet** — that's the deploy artifact name only.

### 2. Fill every `[[TOKEN]]`
Use the per-audience column in `Part1-Template-Tokens.md`. Then run the **token gate**
(note: the regex allows digits — some tokens end in a number):
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <your-file>.html | sort -u    # must return nothing
```
Mind two prose details when filling: `[[VENUE_NOUN]]` follows "A " in the hero headline (use
"An office" if needed), and `[[VENUE_MOMENT]]` is a full narrative clause — rewrite it for the
audience, don't just swap a noun.

### 3. Swap the brand chrome
The benchmark keeps UWCSEA's nav structure as reusable chrome. Graft the target's real nav:
- logo SVG + its **`aria-label="UWC South East Asia"`**,
- rail items beyond the two tokenised labels (`Find it Fast`, `Login`, `Apply`, `Give`),
- primary nav items (`About Us`, `Admissions`, `Learning`, `Careers`, `Support Us`) — these
  read as a *school* site; re-skin to the target's real top-level nav,
- the provenance code-comments still mentioning UWCSEA (cosmetic; overwrite on graft).

### 4. Set the community constant  ⚠️ JS
`[[COMMUNITY_NUM]]` fills both the visible `<b id="guestCount">` figure and
`var GUEST_TARGET = [[COMMUNITY_NUM]];`. Use the same number in both.
The `var wait = 2500 …` line is the cup-drop **animation timer** — a false positive; leave it.

### 5. Replace the hero poster + check assets
Swap `[[HERO_POSTER]]` for the target's still (a client-specific local file). The conservation
media (origins videos, maps, mockups, the Smiirl counter) is shared — it's referenced by URL
via `[[SHARED_BASE]]`, not stored per-pitch. Only the hero poster and logo are local.

### 6. Preview locally & iterate — DO NOT bundle
**Default (always-URL):** set `[[SHARED_BASE]]` to the **live shared-assets URL** — the same
value you deploy with — then just open the working file:
```bash
open -a "Google Chrome" "Workplaces/<Client>/NoFilter-<Client>-PartOne.html"
```
The shared media streams from the shared site, so **what you preview is exactly what deploys**
(preview = production). Iterate with **edit → save → Cmd+R**. No build step.
- The pitch's own `assets/` holds only the **client-specific reals** — the hero poster
  (`[[HERO_POSTER]]`) and the logo. Add those as you build.
- Needs internet + the shared site live (a non-issue in normal use).
- **Offline / before the shared site exists (fallback only):** point `[[SHARED_BASE]]` at local
  files — `cp -R "Schools/UWCSEA/assets" "Workplaces/<Client>/assets"` (same depth, keeps
  symlinks) and set `[[SHARED_BASE]]` to `assets`. That `cp -R` drags UWCSEA's own reals in
  too, so don't mistake a leftover UWCSEA image for the client's during the brand swap.
- **Never run `bundle.py` on a Part 1** (base64 monolith crashes the browser).

### 7. Deploy (shared-asset model)
Switch `[[SHARED_BASE]]` from `assets` to the **live shared-assets site URL** (e.g.
`https://nofilter-shared.netlify.app`). The shared media then streams from that one site — you
do **not** upload it, and there's no "materialize the symlinks" step. The deploy folder you
push contains **only** `index.html` (with `[[SHARED_BASE]]` = the URL) plus a tiny `assets/`
holding the **client-specific reals only** — the hero poster and logo. A deployed Part 1 is
basically HTML + two small images.
- **Order:** the shared-assets site must be live first (see CLAUDE.md → "Shared assets").
- Netlify is case-sensitive — match every `src` exactly. After deploy, open a client asset URL
  and a `[[SHARED_BASE]]` asset URL; a 404 on either is the problem. Hard-refresh / incognito.

### 8. Post-deploy cleanup — gated
The deploy folder is now tiny (HTML + the client's own small images), so there's little to
reclaim. If you remove it, the only rule that bites: **never delete anything in `_shared/`**
or on the shared-assets site — every pitch points at those. Keep the working source + symlinks
for re-edits.

---

## Where Part 1 sits in the journey (context, not this file's job)

- **Part 2** — `_Part2-Master/` (proposal: merged experience, pricing mechanism, ledger, and the
  client's price/machine/term **choices wizard**). Built via the STAMP pipeline.
- **Part 3** — `_Part3-Master/NoFilter-Part3-Master-Contract-v2.html`, the signable contract. It
  reads the client's Part 2 wizard choices (schema-v2 fleet handoff) and fills the contract.
- **PDF contract** — printed from the Part 3 contract once the choices are in.
- **After signing** — default is to **morph the journey into one persistent, personalized
  NGO-contribution tracker** (the live counter promoted to a standalone page, ideally with
  light looping origin video), rather than taking everything down.

---

## NEVER
- Never fork the template per type (one benchmark; per-audience = token values).
- Never name a working file `index.html` (deploy artifact only).
- Never bundle a Part 1 (base64 monolith crashes media-heavy pages).
- Never delete anything in `_shared/`, or any real file that might be a symlink target. (This is
  the only deletion rule that bites: a deploy folder is disposable — its only local-only files are
  the client-specific reals, which also live in the working pitch folder.)
- Never guess a brand value a DevTools probe can measure exactly.

*Benchmark provenance: tokenised from `Schools/UWCSEA/NoFilter-UWCSEA-PartOne.html`
(current-generation Part 1, 18 Jun 2026). 16 tokens. Verified token sweep clean 29 Jun 2026.*
