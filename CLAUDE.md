# CLAUDE.md — NoFilter DO-NOT-TOUCH-Claude-files (the pitch machinery)

Read this first, every session. These are hard rules, not suggestions. When a rule
here conflicts with something that seems faster or more convenient, the rule wins.

---

## Who you're working with

Alex is a non-coder who works visually and directs builds by screenshot and precise
verbal diagnosis. When Alex says something is broken, it is — investigate the actual
code, don't defend the file or deflect. Alex catches technical errors accurately;
listen immediately rather than re-explaining why the current state should be fine.

When Alex says "your call," build it — don't re-ask.

---

## How we work (the operating model)

This workspace is worked in **Cowork/agent mode — direct file access + a code sandbox**, not the
old chat-and-screenshot hand-off. The standing way of working:

1. **Work directly, execute directly.** Edit files in place; run code (node, python, grep, md5)
   in the sandbox. No "deliver the file and wait for Alex to bundle it".
2. **Verify — don't defer. Prove it.** Back every structural/logical claim with an automated
   check: a jsdom / round-trip harness, `node --check`, a byte-diff/md5 proof, the token gate.
   Never assert "it works" or push verification onto Alex. The **one** thing you can't self-verify
   is **rendered appearance + animation** — open it in Chrome and say "ready for you to view",
   never "the animation works".
3. **Show the rendered work, with assets — it's how Alex reviews.** Alex works visually and wants
   to *see* the pitch rendered **alongside its real assets** (images, video, fonts loading), not
   read a description of it. So when a change is visual, actually **open it in Chrome** — via the
   always-URL model (`[[SHARED_BASE]]` pointed at the live shared site, or a local `assets/` for
   offline) so the media resolves and **preview = production**. Opening the rendered page for Alex
   is the **default** end-of-change step, not a fallback for when something can't be verified.
4. **Stamp, don't hand-fill.** Part 2 pitches are generated with `_tools/nf-stamp.mjs`
   (market preset + client skin) — see `_STAMP-A-PITCH.md`. (Parts 1 & 3 are still manual
   `[[TOKEN]]` fills until they get the same pipeline.)
5. **Diagnose before fixing.** Read the code → trace to the line → confirm the cause → make the
   minimum fix. No speculative fixes.
6. **Delegate + checkpoint.** Use subagents for bounded, well-specified work, then **independently
   verify** their output before trusting it.
7. **Files are the source of truth; confirm before destructive acts.** Deletion is allowed, but
   only on Alex's explicit, per-item confirmation (quarantine by default).

---

## NEVER (critical — a mistake here is costly or destructive)

- **NEVER rename any file to `index.html`.** Each pitch folder already has a Netlify
  master `index.html`. Overwriting it is a critical error. If a build needs an entry
  file, ask — do not assume.
- **NEVER remove or reinterpret a design device without explicit confirmation.**
  The wave-interlock transition in the brochure was accidentally destroyed twice in
  one session. If an instruction about removing/changing a visual device is at all
  ambiguous, stop and confirm before acting.
- **NEVER trust the `.bak` backup** — it is stale and unreliable. To revert, reverse
  the specific edits using the session transcript, not the `.bak`.
- **NEVER dump thousands of lines of base64 to the terminal.** No diagnostic command
  that floods output with inlined asset data.
- **NEVER guess a brand value when a DevTools console probe can return the exact
  number.** Brand hex, font names, logo SVGs, measurements — measured, not eyeballed.

---

## ALWAYS

- **Investigate root causes; don't re-guess.** This is a standing instruction. When
  something breaks, read the code and find the actual cause before proposing a fix.
- **Everything is always-URL.** Every pitch (Parts 1, 2 & 3) previews and ships URL-based:
  open the working `.html` in Chrome, media streams from the shared site or `_shared/` symlinks,
  iterate edit → save → Cmd+R, no build step. **Never bundle** (base64 monoliths crash media-heavy
  pages). The old bundler is archived at `_archive/bundler/` for portable-file emergencies only.
- **Grep for stale/duplicate CSS after any large edit.** Duplicate rules silently
  override intended styles. Check for them, especially after big changes.
- **Confirm before destructive actions** (deleting, renaming, overwriting, reverting).
- **Measure at 1440px calibration width.** All brand measurements and layout checks.

---

## The one thing you can't self-verify — rendered visuals (defer to Alex)

Everything structural and logical, you **prove** with an automated check (see "How we work").
The single exception is **rendered appearance + animation/scroll** — you can't see a page render.
Open it in Chrome and hand it to Alex; never claim a motion/scroll/visual effect "works" — say
it's ready for Alex to view. (A prompt implying an image is present doesn't mean one is — check.)

---

## Known technical traps (learned the hard way)

- **`overflow:hidden` on ANY ancestor silently kills `position:sticky`.** This has
  caused at least two sticky-section failures. Check the full ancestor chain before
  debugging a sticky/pinned element elsewhere.
- The video-rendering bug: a rule like `.vid-bg:not([src]){display:none;}` wrongly
  hides `<video>` because `src` lives on the `<source>` child, not the `<video>`.
  That rule was removed; don't reintroduce it.
- **`bundle.py` is archived** at `_archive/bundler/` (canonical copy + README). Working copies
  still sit inside the dormant zoo/brochure pitch folders. It's not part of the normal workflow.

---

## The build loop

Work directly on the file and verify with automated checks (see "How we work"):
**edit in place → run the gates/tests** (`node --check`, the token gate, a round-trip / byte-diff
where applicable) **→ for anything visual or animated, open it in Chrome and hand it to Alex to
view** (the only step you can't self-verify). No chat hand-off; no waiting for Alex to bundle.

> **Bundling is retired.** Every pitch ships **URL-based** (the always-URL model) — Parts 1, 2 & 3
> are never bundled. The old base64 `bundle.py` bundler is archived at `_archive/bundler/` (with a
> README) purely for the rare case of a portable single-file hand-off where there's no server;
> working copies still sit in the dormant zoo/brochure folders. It is **never** part of the normal
> edit-and-view loop.

---

## Deploy & assets

**Each Netlify deploy is a self-contained folder.** The `index.html` ships alongside
exactly the `assets/` that build needs to render (video, images, ambient audio, logo
files). The deployed site has no dependency outside its own folder.

- **Relative paths must match the deployed folder exactly.** Netlify is
  case-sensitive: `Rainforest.mp3` ≠ `rainforest.mp3`. Confirm the exact lowercase
  filename against the `src` line.
- **Verify by hitting the asset's direct URL** (e.g. `https://SITE.netlify.app/assets/rainforest.mp3`).
  A 404 there means the file isn't deployed where the page expects — that *is* the
  problem, before touching any JS.
- **Audio ships as a separate file** beside/under `index.html`, referenced by path/URL like
  every other asset in the URL model.
- After each deploy, hard-refresh (Cmd+Shift+R) and check in incognito; caching shows
  stale versions otherwise.

### Symlinks — DO NOT touch unsupervised (open question, not yet documented)

Assets under `assets/` **may be symlinks** to a canonical shared location (heavy files
like videos are linked rather than copied across pitch folders to avoid duplication).
A real-looking file may be the canonical *target* of a symlink used elsewhere.

- **NEVER delete a file under `assets/` (or anywhere) to "remove duplication."**
  Deleting a canonical target breaks every pitch that links to it. Deletion happens
  only on Alex's explicit, per-file confirmation.
- **Do NOT restructure, materialize, or re-point assets at deploy time.** Alex handles
  any symlink → Netlify materialization manually. The exact sequence (whether real
  files are dropped in and later deleted, or Netlify simply follows the links on
  upload) is **not yet confirmed** — leave it to Alex until it's documented here.
- When that real deploy sequence has been observed once, replace this block with the
  exact commands and a hard gate: the delete/cleanup step runs only after a
  confirmed-successful deploy.

---

## Pitch build methodology

> **Start every new pitch from [`_NEW-PITCH-INTAKE.md`](_NEW-PITCH-INTAKE.md)** — the universal
> front door for Parts 1–3: the renderable-from-first-copy guarantee, the intake prompts (what to
> ask Alex for), and the website-nav spoof best practices.

Each pitch is a pixel-matched clone: harvest the target's real site assets and brand
values, graft them onto NoFilter's master pitch template.

1. Download the target's actual homepage (Save Page As → Webpage, Complete).
2. Extract real brand hex, font names, and logo SVGs via DevTools console probes —
   never approximate from screenshots.
3. Calibrate at 1440px.
4. Colophon codes follow the `DP-2026-[XX]01` pattern (Part 2 uses `02`).
5. Tease the mechanism in outreach without revealing the pixel-match trick.

`_NEW-PITCH-INTAKE.md` is the universal process front door (intake prompts, the renderable
guarantee, the nav-spoof method) and `_TOKEN-DICTIONARY.md` is the canonical token vocabulary.
Defer to those for process + token detail; this file is the guardrails layer on top. (The one
sector-specific playbook is `Zoos/ZOO-PITCH-PLAYBOOK.md`.)

### Part 1, 2 & 3 master templates

Each stage of the client journey has ONE audience-neutral benchmark, each in its own
folder with a read-me-first runbook and a token guide (how-to-open detail is folded into
each runbook). Copy the benchmark per *client* — never fork a per-type template.

- **Part 1** — `_Part1-Master/NoFilter-Part1-Master-Template.html` (the Conservation
  Coffee Partnership intro). Docs: `Part1-Build-Runbook.md`, `Part1-Template-Tokens.md`.
  Tokenised from the UWCSEA Part 1 build. Colophon ends `01`. Links forward to Part 2 via
  `[[PART2_URL]]`. **Still built manually** (copy + fill tokens; no stamp pipeline yet).
- **Part 2** — `_Part2-Master/NoFilter-Part2-MasterTemplate.html` (the proposal), tokenised
  from the **Accenture stepJ v133** base and reconciled to the canonical vocabulary. Docs:
  `Part2-Build-Runbook.md`, `NoFilter-Part2-MasterTemplate-TOKENS.md` (placeholder values;
  definitions in `_TOKEN-DICTIONARY.md`). Colophon ends `02`. Pricing is the topo-card slider,
  band 45/48/55 (v133), currency via `[[CURRENCY]]`; retail-cup metric removed (absolute per-cup).
  **Built via the STAMP pipeline** — `_tools/nf-stamp.mjs` merges a market preset
  (`_Part2-Master/_presets/{SG,UAE}.json`) + a client skin (`_Part2-Master/_skins/<Client>.json`);
  see `_STAMP-A-PITCH.md`. (The old 137-token `NoFilter-Part2-Master-Template.html` was deleted 3 Jul.)
- **Part 3** — `_Part3-Master/NoFilter-Part3-Master-Contract-v2.html` (the contract endpoint).
  Docs: `Part3-Build-Runbook.md`, `Part3-Template-Tokens.md`. Reads Part 2's
  schema-v2 (fleet) handoff and fills equipment / rate / term / derived service dates / Schedule B.
  Colophon ends `03`. The standalone **Configurator lineage is retired**; `-Contract.html` /
  `-Contract-WIP.html` are static ancestors. Governing law + tax are set per market (SG =
  Singapore/GST; UAE = the laws of the UAE/VAT — basic boilerplate, no solicitor review);
  **indicative rates must be confirmed in writing before signature.**

Per build: **Part 2** = *stamp it* (market preset + client skin via `nf-stamp.mjs`), then graft
the target's harvested nav chrome, swap the hero poster / mockups / counter source, hand-edit the
JS volume constants (still NOT tokenised), and rewrite the audience narrative. **Parts 1 & 3** are
still manual `[[TOKEN]]` fills. **Read the stage's runbook first;** token definitions live in
`_TOKEN-DICTIONARY.md`.

**Local preview & iterate loop (before any Netlify deploy).** Default is **always-URL**: set
`[[SHARED_BASE]]` (below) to the live shared-assets URL — the same value you deploy with — then
just `open -a "Google Chrome" "Workplaces/<Client>/NoFilter-<Client>-PartOne.html"`. The shared
media streams from the shared site, so **preview = production** (you catch a missing/misnamed
shared asset during preview, not after sending the link). Iterate with **edit → save → Cmd+R**;
no build step; never bundle. Each pitch keeps only its **client-specific reals** (hero poster,
logo, mockups) in a small local `assets/`.

Needs internet + the shared site live. **Offline / before the shared site exists (fallback):**
point `[[SHARED_BASE]]` at local files — `cp -R "Schools/UWCSEA/assets" "Workplaces/<Client>/assets"`
(same `Clients/Type/Client` depth so the `_shared` symlinks resolve) and set `[[SHARED_BASE]]`
to `assets`. Full detail in each stage runbook's "Preview locally & iterate" step.

### Shared assets — one hosted source of truth (no more re-deploying video)

The heavy conservation/brand media (videos, maps, fonts, favicon) is identical across every
pitch. Instead of materializing a copy into each client deploy, host it **once** and reference
it by URL. In the masters those refs are `[[SHARED_BASE]]/<file>`.

**One bucket, all parts (the union model).** `_shared/` holds the **union of every asset used
by any part** — Parts 1, 2 and 3, including the product-catalogue imagery (machines, coffees).
Every part and every client references the **same** `[[SHARED_BASE]]` URL; each part just uses
the subset it needs. An asset unique to one part still lives in the one bucket. Rule: any
`[[SHARED_BASE]]/<file>` referenced by a master MUST exist in `_shared/` (and thus on the
shared site) — audit with a grep before deploying the shared site.

- **`_shared/` is the source of truth, two ways:** locally it's the symlink target for
  preview; for production it's deployed **once** as its own Netlify site (the "shared-assets
  site", e.g. `nofilter-shared.netlify.app`). A `_shared/_headers` file grants the fonts CORS.
- **`[[SHARED_BASE]]`** = that site's URL at deploy, or `assets` for local preview.
- **Netlify has no symlinks** — it never follows them; that's *why* assets used to be
  materialized per deploy. The shared-site URL is the hosted equivalent of the symlink.
- **Client deploys become tiny:** a deployed Part 1 is HTML + hero poster + logo; a Part 2
  adds only the 3 `-target` mockups. The big bytes stream from the shared site.
- **Order rule (don't bust a build):** deploy/refresh the shared-assets site **before** any
  pitch that references it. Never reference a `[[SHARED_BASE]]` file that isn't live yet.
- **Blast radius:** renaming/deleting a file on the shared site breaks every pitch at once —
  same "never delete a canonical `_shared` target" discipline, now hosted.
- **Existing live sites are unaffected** — they keep their own baked-in assets. Migration is
  opt-in, per-site, preview-tested, and one-click-rollback-able on Netlify.

**Do NOT bundle Part 1 or Part 2 builds** — base64 monoliths crash on these media-heavy
pages. Deploy `index.html` beside a folder of real (materialized) assets — the UWCSEA
pattern. Before deploying any build, run the gates (the token regex allows digits):
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <file>.html | sort -u            # tokens: must be empty
# Part 2 JS constants:  grep -n '111875\|11188\|2500' <file>.html
# Part 1 JS constant:   grep -n 'GUEST_TARGET\|guestCount' <file>.html   (2500 'wait' = timer, ignore)
```

---

## Design tokens (NoFilter house)

Colors: `--nf-orange #ee4d17` · `--nf-stamp-red #FA2B1C` · `--nf-cream #F4F2EE`
· `--nf-parchment #EDE7D9` · `--nf-near-black #1A1815` · `--nf-amber-dim #FFE8C3`

Fonts: Big Shoulders Display · Archivo · IBM Plex Mono · Source Serif 4

---

## Tools available locally

ffmpeg (video trim, image compress, audio clip) · Netlify (deploy) · DevTools
console probes (canonical source for all brand measurements) · the stamp engine
(`_tools/nf-stamp.mjs`). (The base64 bundler is archived at `_archive/bundler/`.)
