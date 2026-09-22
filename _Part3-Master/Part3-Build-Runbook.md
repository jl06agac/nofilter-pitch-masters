# PART 3 BUILD RUNBOOK — read this first, every new Part 3 build

> ⤴ **Before anything, read the universal front door: [`_NEW-PITCH-INTAKE.md`](../_NEW-PITCH-INTAKE.md)** — the renderable guarantee (nothing broken on copy), the intake prompts, and the website-nav spoof best practices that apply to every part.

**This is the single front door for building a Part 3 — the signable contract endpoint. The
client's price / machinery / term choices are now made in **Part 2's own wizard**; Part 2 hands
those choices to Part 3, which renders them into a signable contract.** This file owns the
*process*; `Part3-Template-Tokens.md` (beside it) owns the *values*.

> Files on disk are the source of truth. Confirm before renaming, moving, overwriting or deleting
> anything. Nothing goes to trash — superseded files move to `_archive/`.

The journey: **Part 1 (intro) → Part 2 (proposal + choices wizard) → Part 3 (contract fills from
those choices) → PDF contract → sign → take down or morph to a live NGO-contribution tracker.**

---

## What's in this folder / how to open

`_Part3-Master/` holds the signable-contract endpoint. There is **one** Part 3 file now:

- **`NoFilter-Part3-Master-Contract-v2.html`** — the ONLY Part 3 master. Built **manually** (apply
  the locale preset + fill the `[[TOKEN]]`s per client — no stamp pipeline for Part 3 yet). To
  view it populated, walk **Part 2's wizard** first (it writes the choices to the browser), then
  open this file and **Print (⌘P)** — the contract pages appear in the print preview. The raw
  master shows `[[TOKENS]]`; that's expected. Set the locale governing-law + tax values per market
  (SG = Singapore/GST; UAE = the laws of the UAE/VAT). Don't rename a working file to `index.html`.
- **`Part3-Build-Runbook.md`** (this file) — the process. **`Part3-Template-Tokens.md`** — the values.

(Superseded files, when there are any, quarantine to `_archive/` — there are none right now.)

> The old Configurator lineage (standalone Configurator, static `Contract.html` /
> `-Contract-WIP.html`, v1 donor) was retired and deleted 2026-07-03 — there is nothing else here
> to open or build from.

---

## What the master is

`NoFilter-Part3-Master-Contract-v2.html` is the **ONLY Part 3 file now** — the canonical contract
endpoint. It reads Part 2's **schema-v2 (fleet) handoff** from `localStorage` and fills the
equipment summary, Schedule A machine + monthly rate, printed term dates, the derived
service-visit dates, and the Schedule B coffee prices. Tokenised from the Sprinklr Singapore
build. **Sprinklr is the parent of every Part 3.**

> The old Configurator lineage (the standalone Configurator, the static `Contract.html` /
> `-Contract-WIP.html`, and the v1 donor) was **retired and deleted 2026-07-03**. Part 2's own
> wizard now feeds the contract, so there is nothing else to open or build from here.

---

## The golden rule: ONE template, never fork

Per-client and per-locale differences are **token values**, not separate files. Copy the
master (`-Contract-v2.html`) per *client*; never make a per-client `_TEMPLATE`.

---

## The build, step by step

### 0. Intake
- **Target** name + full legal entity, UEN, registered office, signatory, contact email.
- **Locale preset** (Singapore / UAE): currency, contact, finance partner, premises city,
  governing law, tax label — from `DO-NOT-TOUCH-Claude-files/_Locale-Presets.md`.
- **Colophon** `DP-2026-[XX]03` (Part 3 ends `03`).
- **Term**: start date, end date, length (months) — these drive the printed dates AND the
  derived service-visit schedule.
- **Equipment + rate**: the machine(s), rental/purchase, term — and whether the rate is
  **confirmed** (see "The bridge").

### 1. Copy the master into the client journey folder
Part 3 is still built **manually** (no stamp pipeline yet). Copy
`NoFilter-Part3-Master-Contract-v2.html` into the client folder under a working name, e.g.
`Workplaces/Aon/NoFilter-Aon-PartThree.html`.
**Do NOT name a working file `index.html`** — that's the deploy artifact name only.

### 2. Apply the locale preset, then fill every `[[TOKEN]]`
Use `Part3-Template-Tokens.md`. Apply the locale values first, then the client values. Then run
the **token gate** — it must return nothing:
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <your-file>.html | sort -u
```
Mind the case-variant pairs: `[[PREMISES_CITY]]`/`[[PREMISES_CITY_UC]]` and
`[[GOVERNING_JURISDICTION]]`/`[[GOVERNING_JURISDICTION_UC]]` — the `_UC` ones are the UPPERCASE
form used in the cover stamp and the binding-clause headers (a literal-caps line, not CSS-cased).

### 3. The bridge — what fills itself, and what to check
The contract pages are print/PDF-only. The choices are made in **Part 2's own wizard**; Part 2
writes a **schema-v2 (fleet) handoff** to `localStorage`. `NoFilter-Part3-Master-Contract-v2.html`
reads that handoff and writes the values into the contract **at runtime** (on load and again on
`beforeprint`). It populates: equipment summary, Schedule A machine + monthly rate, the printed
term dates, the **service-visit dates** (derived from `[[TERM_START]]` at six-month intervals,
count = `[[TERM_MONTHS_N]] ÷ 6`), and the Schedule B coffee prices.

So `[[TERM_START]]` MUST be filled with a real date (e.g. `01 June 2026`) — the service dates are
parsed from it. On the raw, unfilled master the date derivation safely no-ops.

- **Indicative rates ⚠:** only confirmed combos (CaféMatic 5 & 8, 3-yr rental) print a clean
  rate. Everything else prints `(indicative — subject to written confirmation)`. **Confirm the
  rate in writing before the client signs.**
- **Tier-1 scope:** single primary machine on rental. Multi-machine / barista / no-machine paths
  render `— (on application)` or "see addendum" — finalise those by hand.

### 4. Locale values — set per market (no solicitor review)
These are tokenised; set them from the locale preset:
- **Governing law** (`[[GOVERNING_JURISDICTION]]` / `_UC`): SG = `Singapore` / `SINGAPORE`;
  UAE = `the United Arab Emirates` / `THE UNITED ARAB EMIRATES` (federal). Basic boilerplate per Alex.
- **Tax** (`[[TAX_LABEL]]` / `[[TAX_LABEL_LONG]]`): SG = GST; UAE = VAT / Value Added Tax.
- **Indicative rates**: see step 3 — a commercial confirmation, not a legal one.

### 5. Preview & verify
Walk **Part 2's wizard** (price → machine → term → consumables → review) so it writes the
schema-v2 handoff, then open `NoFilter-Part3-Master-Contract-v2.html`, print-preview the contract,
and confirm: equipment, rate (+ indicative marker if unconfirmed), term dates, the service-visit
dates, and Schedule B prices all reflect the choices.
**This live click-through is the only real test of the bridge — it can't be verified from the
code alone.**

Token gate (empty) and a JS syntax check before deploy:
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <file>.html | sort -u    # must be empty
node --check on each inline <script>                    # no syntax errors
```

### 6. Deploy
Same model as Parts 1 & 2: `index.html` + a small client `assets/`; heavy media streams from
`[[SHARED_BASE]]` (the shared-assets site). Deploy the shared site first. Never bundle.

---

## NEVER
- **Never delete a client contract file — Part 3 HTML *or* exported PDF, draft or signed.** They
  are commercial records and they earn their keep. Archive, never purge. (The original Sprinklr
  contract was purged 3 Jul 2026; its structure survives only because `Contract-v2.html` was
  tokenised from it — don't repeat that.)
- Never let an **indicative** rate go to signature as if confirmed.
- Never name a working file `index.html`.
- Never delete anything in `_shared/` or any symlink target.
- Never edit the build-time `[[TOKENS]]` text expecting JS to read them — the bridge writes live
  values into ids/classes, not into the token text.

*Master provenance: `NoFilter-Part3-Master-Contract-v2.html`, tokenised from the Sprinklr
Singapore Part 3, 30 Jun 2026. Reads Part 2's schema-v2 (fleet) handoff. The old Configurator
lineage (standalone Configurator, static `-Contract.html` / `-Contract-WIP.html`, v1 donor) was
retired and deleted 2026-07-03.*


## Terms pages pack themselves (added 18 Sep 2026)

The clause area is a balanced two-column flow (`column-fill: balance`, one clause block per
terms page). A `nf-paginate` script embedded after `nf-contract-sync` runs on load, after
fonts are ready: it works out how many terms pages the clauses need, spreads them evenly
across those pages by text length, adds or removes terms pages, and renumbers tags, header
ranges, footers and screen labels. So:

- Adding, deleting or rewriting a clause in the master or a stamped file needs no manual
  page shuffling. Open the file; it packs itself. Export to PDF from the open tab.
- Do not hand-place clauses across pages. Whatever static split the file carries is only
  the no-JS fallback.
- The source copy of the script is `_partials/nf-paginate.html`. If you change it, paste the
  same block into the master.
- Standard clauses are now 01-17. Cl. 15 Confidentiality and 16 Supplier Indemnity are new;
  De-installation & Collection moved from Cl. 15 to Cl. 17. New tokens: `RATE_RUNG_MID`,
  `RATE_RUNG_FULL`, `DATA_PROTECTION_LAW` (all three presets updated).
