# Locale presets — region values for the client journey

> **Token VALUES now live in [`_TOKEN-DICTIONARY.md`](_TOKEN-DICTIONARY.md) — the single source of truth.** This file keeps the locale *mechanics* (USD-peg slider, contact-card order, milestone constants) and mirrors the values; if they ever disagree, the dictionary wins.

A **locale preset** is a small set of token values that varies by *region*, layered on the one
neutral master per part **before** the per-client tokens. It is NOT a separate template — there
is still one master for Part 1, one for Part 2, one for Part 3. A build is:

> neutral master  →  apply a **locale preset** (below)  →  fill the **client** tokens  →  ship

Region lives here, once. Two axes, both just token values: **locale** (Singapore / UAE) and
**client** (UWCSEA, Aon, …). Brand/conservation assets are identical across locales (the one
`[[SHARED_BASE]]` bucket); only the values below change.

---

## The presets

| Token | Meaning | 🇸🇬 Singapore | 🇦🇪 UAE |
|---|---|---|---|
| `[[CURRENCY]]` | currency code shown on figures | `SGD` | `AED` |
| `[[CUR_SYMBOL]]` | short symbol (e.g. Part 1 conservation counter prefix) | `S$` | `AED` |
| `[[NF_CONTACT_EMAIL]]` | NoFilter contact address | `alex@nofilter.sg` | `alex@nofilter.ae` |
| `[[COFFEE_PRICE_PER_KG]]` | retail coffee, per kg (Part 3 rate card headline) | `48.00` | `155` |

### Part-specific numeric values that move with the locale

These are the hand-edit figures already flagged in the build runbooks; their **value** is a
locale concern (set from the column above), their *placement* is per-part.

| Where | Token / constant | 🇸🇬 Singapore | 🇦🇪 UAE |
|---|---|---|---|
| Part 1 | conservation-counter symbol (`.cafe-flap-prefix`) | `S$` | `AED` |
| Part 2 | `[[CURRENCY]]` on all figures | `SGD` | `AED` |
| Part 2 | retail-cup metric | **removed** (was `CUP_RETAIL`) — see slider note below | same |
| Part 2 | `IMPACT_TARGET` / contribution figures | derive in `[[CURRENCY]]` | derive in AED |
| Part 3 | contract rate card (machines, coffees, services) | the SGD card already in the file | **AED card** — coffee band 145/155/165 (default `155`; transacted ≈140); remaining machine/service prices TBD |

---

## Part 2 pricing slider — the currency-specific parameters

Part 2 has three range sliders. Only the **coffee price** changes with currency; the
co-contribution and volume sliders don't. SGD is the master; AED is the locked UAE build.

**How the contribution is computed (not set):**
```
coffeePerCup = price/kg × DOSE_G(18)/1000
nfCupC (contribution, sub-unit/cup) = price/kg × NGO_RATE(0.10) × 18/1000 × 100 = price × 0.18
```
So everything per-cup **derives from the per-kg price and the 18 g dose** — you do NOT set a
cup price. The old "% of a retail café cup" readout (and its `CUP_RETAIL` constant) has been
**removed from the master**: most clients give staff coffee free, so a retail-cup percentage is
meaningless. The dark payoff now shows the **absolute** conservation contribution,
`≈ [[CURRENCY]] x.xx per cup, all-in` (JS: `cupPct = (totalC/100).toFixed(2)`).

The pricing section is also now the **redesigned** one (soft `#f3ead9` topo cards per slider,
the top-up broken into its own titled card, hover-gutter context, single dark payoff) and the
currency is the `[[CURRENCY]]` token across the slider, the ledger figure, and the per-cup JS
readout — so swapping locale is a token swap, not an edit.

| Slider / constant | `id` / const | 🇸🇬 SGD (master) | 🇳🇿 NZD (ref) | 🇦🇪 AED (LOCKED) |
|---|---|---|---|---|
| Coffee wholesale /kg | `wholePrice` | `48.00` (min 45, max 55, step 0.25) | `54.00` (50–60) | **`155`** (min **145**, max **165**, step **0.5**) |
| Dose per cup | `DOSE_G` | `18` | `18` | `18` (unchanged) |
| Conservation rate | `NGO_RATE` | `0.10` | `0.10` | `0.10` (unchanged) |
| ⇒ derived contribution (headline) | `nfCupC` | `8.6` ¢/cup (SGD cents) | ~`9.7` ¢/cup | **~`7.6` ¢/cup, in USD cents** (`÷ 3.6725`) |
| Co-contribution top-up | `topUp` | `0`–`5` ¢ | `0`–`5` | `0`–`5` (USD cents, unchanged) |
| Dark-payoff local figure | `cupPct` | `≈ SGD 0.09 /cup` | — | `≈ AED 0.28 /cup` |
| Annual volume | `volCups` | client-specific | client-specific | client-specific |

**✅ Milestone constants stay as-is — do NOT rescale (the fils plan was abandoned).** The AED
build expresses the contribution **headline in USD cents** (`nfCupC ÷ 3.6725`, the fixed peg),
which lands it back in the same `~7–12` range as SGD cents. So the existing `10¢` / `12¢` / `15`
milestones (`round target` / `STRETCH_C` / `BAR_MAX`) fire **natively** — the confetti + gold
glow work without touching them. This is exactly why the earlier "rescale to ~30 fils" idea was
dropped: fils overshoots the 10/12 scale and breaks the milestone crossings (no glow, no
confetti).

| Const | meaning | SGD | AED (LOCKED) |
|---|---|---|---|
| round target | headline milestone | `10` ¢ | `10` ¢ (USD) — unchanged |
| `STRETCH_C` | "going further" | `12` | `12` — unchanged |
| `BAR_MAX` | bar scale max | `15` | `15` — unchanged |
| headline unit | what the ¢ means | SGD cents | **USD cents** (`nfCupC ÷ 3.6725`) |

> AED slider is fully specified: range **145–165**, start **155**, step **0.5**; contribution
> headline in **USD cents**; dark payoff `≈ AED x.xx /cup`; optional USD sub-line below.

### UAE slider — USD equivalent sub-line (a UAE-only nicety)

The AED is **pegged to USD** at the fixed rate **1 USD = 3.6725 AED** (the long-standing
official peg), so a USD equivalent is exact and never drifts. On the AED slider, show a small,
muted secondary line under each key figure, computed `AED ÷ 3.6725`:

- the AED you set: `AED 155/kg` → `· ~$42.2/kg`
- local per-cup: `≈ AED 0.28/cup` → `· ~$0.076 (7.6¢)`

Note: in the locked build the **contribution headline is already in USD cents** (7.6¢), so the
USD conversion is partly visible by design; the sub-line is now an optional nicety on the
**price/kg** and **local per-cup** figures rather than essential. Keep it subtle (smaller,
lighter) so the AED figure stays primary, UAE locale only. **Alex previews it live**
(rendered/animated UI can't be verified from inspection).

## Contact block (Parts 1 & 2) — show both, relevant region first

Parts 1 and 2 carry a contact card listing **both** regional lines — `SG · alex@nofilter.sg`
and `UAE · alex@nofilter.ae` — deliberately: showing two markets is credibility. **Keep both.**
The only locale change is **order**: put the build's region first.

- **Singapore build:** leave SG line first (current order).
- **UAE build:** move the `UAE ·` `deets` line *above* the `SG ·` line so UAE is seen first.

It's a one-line reorder of the two `<div class="deets">` lines — no token, both stay. Part 3
uses a single contact (`[[NF_CONTACT_EMAIL]]`), so there it's just the locale value.

## Part 3 contract — locale tokens

The Part 3 contract is tokenised. Locale-driven values:

| Token | 🇸🇬 Singapore | 🇦🇪 UAE |
|---|---|---|
| `[[CURRENCY]]` | `SGD` | `AED` |
| `[[NF_CONTACT_EMAIL]]` | `alex@nofilter.sg` | `alex@nofilter.ae` |
| `[[FINANCE_PARTNER]]` | `Orix Leasing Singapore Ltd` | TBD (UAE financier) |
| `[[PREMISES_CITY]]` / `_UC` | `Singapore` / `SINGAPORE` | e.g. `Dubai` / `DUBAI` |
| `[[GOVERNING_JURISDICTION]]` / `_UC` | `Singapore` / `SINGAPORE` | `the United Arab Emirates` / `THE UNITED ARAB EMIRATES` |
| `[[TAX_LABEL]]` / `[[TAX_LABEL_LONG]]` | `GST` / `Goods and Services Tax` | `VAT` / `Value Added Tax` |
| rate card (Schedule A/B/C numbers) | the SG card already in the file | **AED card — TBD** |
| `[[NF_ENTITY_NAME]]` / `[[NF_ENTITY_REG]]` / `[[NF_ENTITY_ADDRESS]]` (NoFilter's own entity) | NoFilter Pte. Ltd · UEN 201839882N · 31 Kaki Bukit Road 3 #01-02C Techlink Singapore 417818 | NoFilter LLC · TL 2540001.01 (Shams) · Sharjah Media City (Shams), UAE · VAT TRN pending |

> UAE governing law is set to **the laws of the United Arab Emirates** (federal) and tax to **VAT**
> — basic boilerplate per Alex, no solicitor review. Indicative equipment rates (any combo other
> than CaféMatic 5 & 8, 3-yr rental) print an "(indicative — subject to written confirmation)"
> marker and must be confirmed in writing before signature (a commercial check, not a legal one).

## Notes

- **Singapore** values are the ones already living in the existing pitches (the Sprinklr/UWCSEA
  builds): SGD, `48.00`/kg coffee (v133 band 45/48/55), `alex@nofilter.sg`. (CUP_RETAIL was removed from the master — no retail-cup metric.)
- **UAE**: AED band 145/155/165 (transacted ≈140 from real invoices), `alex@nofilter.ae`; entity NoFilter LLC · Sharjah Media City (Shams) · TL 2540001.01 · VAT TRN pending FTA. No CUP_RETAIL. **Machine rate card = a full set of estimates in `UAE.json`** (all 4 machines × 24/36-mo rental + purchase), scaled from the SG card by the C8 anchor ratio (~2.42×) as render-clean placeholders. The **only real figure is `RATE_CM8_36MO` = AED 1,211.89/mo** (CaféMatic 8 + fridge, 3-yr lease, from the Sprinklr Gulf deal, USD 329.99/mo × 3.6725 peg). Replace the estimates with actuals when known; finance partner still TBD.
- The Part 3 contract's pricing math is **display-only currency** (`[[CURRENCY]]` labels);
  the rate-card *numbers* are the locale values above. Swapping locale = swap the number set,
  not the code.
- The colophon `DP-2026-[XX]0N` `[XX]` is the **client** code, not the region — locale doesn't
  change it.

> Keep this file as the single home for region values. If a number is wrong, fix it here, not
> in a built pitch.
