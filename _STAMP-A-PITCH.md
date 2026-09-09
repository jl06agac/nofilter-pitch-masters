# Stamp a Pitch — Part 2 build pipeline

**Model:** neutral master → apply MARKET preset → apply CLIENT skin → **stamp** → deploy-time fill.
One neutral, tokenised master holds the layout; a market preset carries the locale/legal/price
values; a client skin carries the per-client + deal values. The stamp engine merges them and
substitutes every `[[TOKEN]]`. A short allowlist of tokens stays unfilled until deploy.

Vocabulary source of truth: **`_TOKEN-DICTIONARY.md`** (three layers — CLIENT / MARKET / DEAL).

---

## The command

```bash
node _tools/nf-stamp.mjs \
  _Part2-Master/NoFilter-Part2-MasterTemplate.html \
  _Part2-Master/_presets/<MARKET>.json \
  _Part2-Master/_skins/<Client>.json \
  --out builds/<Client>-part2.html
```

- Value files merge **in order, later overrides earlier** — so preset first, skin second.
  (Put a deploy-values JSON last if you have one.)
- `--strict` exits non-zero if any **MISSING** token remains (use in CI / pre-deploy).
- Omit `--out` to write to stdout.
- Keys beginning with `_` (e.g. `_NOTE`, `_README`) are metadata and are ignored for substitution.

After every stamp the engine prints the **TOKEN GATE** to stderr:
- **DEPLOY-TIME** — allowlisted tokens that are supposed to be filled later (OK to see these).
- **MISSING** — anything else still `[[…]]`. A real problem; fix the preset or skin.

---

## Where things live

```
_Part2-Master/
  NoFilter-Part2-MasterTemplate.html   ← READ-ONLY neutral master ([[TOKEN]] grammar)
  _presets/  SG.json  UAE.json  London.json   ← MARKET presets (locale · legal · price band)
  _skins/    <Client>.json  _CLIENT-TEMPLATE.json   ← CLIENT + DEAL values
_tools/nf-stamp.mjs                       ← the stamp engine (Node ESM, no deps)
_TOKEN-DICTIONARY.md                      ← canonical token vocabulary
```

---

## Add a client

1. Copy the template:
   `cp _Part2-Master/_skins/_CLIENT-TEMPLATE.json _Part2-Master/_skins/<Client>.json`
2. Fill it from the intake — see **`_NEW-PITCH-INTAKE.md` §2** (client identity, signatory,
   billing entity, form id, counter src, co-brand media, supply term).
   Note `TARGET_BILLING_ENTITY` is the **bare** entity name; the master supplies the
   "o/b/o [[TARGET_NAME]]" wrapper.
3. Pick the market preset (`SG` / `UAE` / `London`). The preset — **not** the skin — carries
   currency, tax label, NoFilter entity, governing law, contact emails, and the price band.
4. Stamp with the command above.

---

## Deploy-time tokens (left unfilled by design)

These are on the engine's allowlist and are supplied at deploy, not at stamp:

```
RATE_CM*        machine rental rate card
PURCHASE_CM*    machine purchase prices
CONTRACT_URL    link into Part 3 / contract
PART2_URL       link into Part 2 (from Part 1)
MACHINE_COBRAND_LOGO · DEFAULT_MACHINE · DEFAULT_ORIGIN · DEFAULT_PATH
COST_PER_KG · SHARED_BASE
```

Seeing these in the DEPLOY-TIME group is expected. Seeing anything in **MISSING** is not.

---

## Non-SG markets — what's set and what's open

**UAE** is set: currency AED, tax VAT, governing law = the laws of the United Arab Emirates
(federal — basic boilerplate per Alex, no solicitor review), entity NoFilter LLC · Shams ·
TL 2540001.01, price band 145/155/165. Still open for UAE: the **AED machine/service rate card**
and the **finance partner**. **London** is a stub until the UK entity exists.

---

## Acceptance test (round-trip proof)

Stamping the master with **SG + Accenture** reproduces the known-good Accenture build (`stepJ`)
byte-for-byte, except the intended scale fix:

```bash
# run from DO-NOT-TOUCH-Claude-files/
node _tools/nf-stamp.mjs _Part2-Master/NoFilter-Part2-MasterTemplate.html \
  _Part2-Master/_presets/SG.json _Part2-Master/_skins/Accenture.json --out /tmp/acc-stamped.html
diff /tmp/acc-stamped.html ../Clients/Workplaces/Accenture/NoFilter-Part2-Accenture-base-stepJ.html
```

Expected diff — only the price-scale reconciliation (v133 band 45/55, was 42/53):
- `SMIN=42→45`, `SMAX=53→55` (one line)
- `REC_PRICE=42→45` (one line)

And the TOKEN GATE reports deploy-time tokens only, **0 MISSING**. That proves the whole
pipeline (master + market preset + client skin ⇒ the exact known-good build).
