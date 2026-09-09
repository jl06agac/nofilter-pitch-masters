# CLIENT PIPELINE RUNBOOK — prospect → signed PDF sent

**The single end-to-end procedure.** From the moment a prospect is identified to the moment the
PDF contract is in the client's inbox for sign-off. Every other pitch doc is a *detail* of one
step in this sequence; this file is the sequence. Last set: 3 July 2026.

> The journey:
> **Prospect → Part 1 (intro) → Part 2 (proposal + the client's price/machine/term choices) →
> Part 3 (the signable contract, filled from those choices) → export PDF → send for sign-off.**

**State legend** (each step is annotated with its honest current state):
`[READY]` works today · `[MANUAL]` works but hand-cranked · `[GATED]` blocked on legal/commercial sign-off.

The Notion twin of this page is **"New Client Pipeline — Runbook (Part 1 → Part 2 → Contract →
Signed)"** in the Master Build Index. This on-disk file and that page say the same thing; if they
ever drift, the file on disk wins.

---

## Where each step's detail lives

| Step | Detail doc |
|---|---|
| Intake + brand harvest + nav spoof (all parts) | `_NEW-PITCH-INTAKE.md` |
| Token vocabulary (single source of truth) | `_TOKEN-DICTIONARY.md` |
| Per-market values (SG · UAE · London) | `_Locale-Presets.md` |
| Part 1 build | `_Part1-Master/Part1-Build-Runbook.md` |
| Part 2 build (the stamp) | `_Part2-Master/Part2-Build-Runbook.md` + `_STAMP-A-PITCH.md` |
| Part 3 contract build | `_Part3-Master/Part3-Build-Runbook.md` |
| Whole-workspace map | `CLAUDE.md` → "Layout" |

---

## Conventions (apply to every client)

- **Folder:** `Clients/{Sector}/{Client}/` (mirrors `Workplaces/Accenture/`). One journey folder
  holds all stages for that client.
- **Working files:** `NoFilter-{Client}-PartOne.html` · `-PartTwo.html` · `-PartThree.html`.
  Never name a working file `index.html` — that is the deploy artifact name only.
- **Masters are never edited for a client.** Copy the master, fill the tokens. One master per part;
  you never fork a template per school/zoo/workplace — the difference is always the token values.
- **Netlify:** heavy media stays on the shared-assets site (`[[SHARED_BASE]]`), referenced by URL,
  never duplicated. The client folder holds only the skin HTML + genuinely client-specific media.
- **Form name per client:** `{client}-terms` (Netlify Forms auto-registers it on deploy).
- **The handoff object:** Part 2's wizard writes **NF Terms Schema v2 (fleet)** to the browser —
  `{coffeePrice, conservationRate, topUp, allInPerKg, annualConservation, fleet:[{machine, qty,
  mode, termMonths}], fleetMonthly, origins}`. Part 3 reads that same object. (v1 single-machine is
  retired.)

---

## The procedure

### 0. Prospect identified — intake  `[MANUAL]`
Capture client, contact, sector, market (SG / UAE), email domain, headcount, website URL. Run the
intake in **`_NEW-PITCH-INTAKE.md` §2**. The moment a master is copied, run the **placeholder pass**
(§1) so the pitch renders cleanly before Alex has answered anything — no raw `[[TOKENS]]`, no broken
media, no other client's identity in the nav.

### 1. Brand harvest + nav spoof  `[MANUAL]`
Harvest the client's real nav, logo SVG, exact hex, fonts and motion from their live site with the
DevTools probes in **`_NEW-PITCH-INTAKE.md` §3**. The brand harvest is universal (Parts 1–3 all use
it); the full nav spoof applies to Parts 1–2. Never guess a value a probe can measure.

### 2. Part 1 — the intro microsite  `[MANUAL]`
Copy `_Part1-Master/NoFilter-Part1-Master-Template.html` into the client folder, fill every
`[[TOKEN]]`, graft the harvested nav, set the community constant, swap the hero poster. Must end
with a CTA into the client's Part 2 URL — reserve that URL now, even before Part 2 exists
(`[[PART2_URL]]`). Full steps: `_Part1-Master/Part1-Build-Runbook.md`.

### 3. Part 2 — the proposal + choices wizard (STAMP)  `[READY]`
Part 2 is **stamped**, not hand-filled. Copy `_skins/_CLIENT-TEMPLATE.json` to `_skins/{Client}.json`,
fill it from the intake, pick the market preset, then:

```bash
node _tools/nf-stamp.mjs \
  _Part2-Master/NoFilter-Part2-MasterTemplate.html \
  _Part2-Master/_presets/<MARKET>.json \
  _Part2-Master/_skins/<Client>.json \
  --out builds/<Client>-part2.html
```

The TOKEN GATE must report **0 MISSING** (deploy-time tokens are expected). Full steps and the
round-trip acceptance test: `_STAMP-A-PITCH.md`. The tokenised master + stamp engine are built and
verified — this step is no longer a find-and-replace.

### 4. Deploy + wire capture  `[READY]`

**Deploy with `_tools/nf-deploy.sh`. Never hand-roll a netlify command.**

```bash
export NETLIFY_AUTH_TOKEN='…'          # in the shell, never pasted into a chat
DO-NOT-TOUCH-Claude-files/_tools/nf-deploy.sh \
  "Clients/{Sector}/{Client}/{client}-deploy" {site-name}
```

**A Netlify deploy REPLACES the whole site.** Deploy the wrong folder to the right site, or
the right folder to the wrong site, and everything already there is gone. That is not
hypothetical: it is how the shared media site was wiped. The CLI resolves a target by
walking UP the tree for `.netlify/state.json` and will silently pick up a link nobody
remembered — `Clients/_shared/.netlify/state.json` points at the media site.

`nf-deploy.sh` closes that off. It takes the site explicitly, refuses to run from inside
`Clients/_shared`, blocks the protected site IDs below, prints the target and byte count,
and makes you type the site name before anything moves.

**Protected — never receives a client deploy:**

| Site ID | What it is |
|---|---|
| `7e2274d8-fa6c-44b9-9af6-779cc0e89ad0` | **shared media assets** — the one that got wiped |
| `6c64fb40-0d1a-4e80-9095-1a9b212cf981` | nofilter-gis-map |
| `c2ab7d04-4ff9-4842-8b12-7a65b80b675f` | nf-servicing-scheduler |

Then confirm the `{client}-terms` form appears in Netlify Forms and set the notification
email **in the UI, not the API** — an API-created hook comes back with `form_id: null` and
never fires. Verify with one test submission. Capture is already built into the Part 2
master.

### 5. Selections arrive  `[READY]`
The client walks Part 2's wizard (price → machine → term → consumables → review). Netlify delivers
the **NF Terms Schema v2 (fleet)** payload by dashboard/email; the same object is written to the
browser for Part 3 to read.

### 6. Part 3 — build the signable contract  `[READY]`
Copy `_Part3-Master/NoFilter-Part3-Master-Contract-v2.html` into the client folder, apply the locale
preset, fill every `[[TOKEN]]` (mind the `_UC` uppercase variants), and clear the token gate to empty.
The contract **reads Part 2's schema-v2 handoff** and auto-fills the equipment summary, Schedule A
machine + monthly rate, printed term dates, the derived six-monthly service-visit dates, and the
Schedule B coffee prices. Full steps: `_Part3-Master/Part3-Build-Runbook.md`. The v2 contract and the
choices→contract bridge are built and verified.

> **Locale + commercial checks (no solicitor review):**
> - **Governing law** is set per market: SG = Singapore; **UAE = the laws of the United Arab
>   Emirates** (federal), tax = VAT. Basic boilerplate per Alex — no lawyer sign-off gate.
> - **Indicative rates:** only confirmed combos print a clean rate; anything else prints
>   "(indicative — subject to written confirmation)". Confirm the rate in writing before signature
>   (a commercial check, not a legal one).

### 7. Export the PDF + send for sign-off  `[MANUAL]`
This is the finish line. The contract pages are print/PDF-only.

1. Walk **Part 2's wizard** first so it writes the schema-v2 handoff to the browser, then open the
   filled Part 3 file in Chrome.
2. **Print-preview (⌘P)** and confirm every field is populated: equipment, rate (with the indicative
   marker only if genuinely unconfirmed), term dates, the service-visit dates, and Schedule B prices.
3. **Save as PDF** — name it `NoFilter-{Client}-Contract-{YYYY-MM-DD}.pdf`.
4. Final check before it leaves: legal gates in step 6 are cleared, and no indicative rate is going
   out as if confirmed.
5. **Send** the PDF to the client's contact for sign-off (e-signature or wet signature, per client).

At this point the client has the contract for their sign-off — the goal of this runbook is met.

### 8. Sign → flip to impact tracker  `[MANUAL · future]`
After signing, the default is to **morph the journey into one persistent NGO-contribution tracker**
(the live counter promoted to a standalone page) rather than taking everything down. A fully
automated signed-mode flip is not yet built.

### 9. Ops handoff  `[MANUAL]`
Notion Order Inbox entry · Xero coffee items (`COF-GAYO` / `COF-ARAKAN` / `COF-BTORU` / `COF-BGADIS`)
· NGO contribution tracker · quarterly statement cycle.

---

## The check that runs — `nf-doctor`

Everything above is a rule a human has to follow. This is the one thing that checks.

```bash
node DO-NOT-TOUCH-Claude-files/_tools/nf-doctor.mjs --quiet
```

Run it before a stamp and before a deploy. Exit code 1 means at least one ERROR. Add `--json`
for machine-readable output, or pass extra paths to scan scratch areas outside the workspace.

What it checks, and the real failure each one is named after:

| Check | The failure it catches |
|---|---|
| `duplicate-name` | Two files with the same name and different bytes. `NoFilter-Generic-Part2-SG.html` existed twice, 30KB apart, for a month. |
| `version-collision` | The same `vNNN` label on differently-sized files. Both Generic copies said `v256`, which is why the confusion survived. |
| `stale-doc-path` | An SOP asserting a path that is wrong. The housekeeping note named the wrong canonical file and stayed wrong for a month. |
| `foreign-identity` | A build carrying another client's name or brand hex. The Part 2 master shipped Accenture's logo geometry and `#A100FF` into every stamp. |
| `branded-template` | A `_TEMPLATE` with a real client baked in, which becomes a rogue second source of truth. |
| `unfilled-token` / `placeholder` | A client build going out with `[[TOKENS]]` or "to confirm" copy still in it. |
| `reserved-name` | A working file named `index.html` outside a deploy folder. That name has caused overwrites. |

It scans the workspace plus `~/Desktop`, `~/Downloads` and `~/Documents`, because the scratch
areas outside the workspace are exactly where duplicates breed and are the blind spot the
`nf-guard` hook cannot see into. Roots nested inside one another are de-duplicated, and hard
links are counted once.

**It is a smoke alarm, not a fire brigade.** It changes nothing on disk. WARN is usually a
judgement call; ERROR means two things claim to be the same thing.

## Standing risks (do not skip)

- **UAE is fully set** on price (155, band 145–165), entity (NoFilter LLC · Shams · TL 2540001.01),
  governing law (the laws of the UAE, federal) and tax (VAT). No solicitor review. What's still
  open for UAE is the **AED machine/service rate card** and the **finance partner**.
- **London** is a stub until the UK entity exists (entity, address, contact, price band, governing law).
- **Never skin from a skin** — masters only. Structural fixes go to the master and re-skin, never
  patched per client.
- **Files on disk are the source of truth.** Confirm before renaming, moving, overwriting or deleting.
