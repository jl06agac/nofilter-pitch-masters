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
| Part 3 | contract rate card (machines, coffees, services) | the SGD card already in the file | **AED card** — coffee floor 150 / opener 165 (default `165`; transacted ≈140 — see the ladder note below); remaining machine/service prices TBD |

---

## Part 2 pricing slider — the currency-specific parameters

Part 2 has three range sliders. Only the **coffee price** changes with currency; the
co-contribution and volume sliders don't. SGD is the master; AED is the locked UAE build.

**How the contribution is computed (not set):**
```
coffeePerCup = price/kg × DOSE_G(18)/1000
nfCupC (contribution, sub-unit/cup) = price/kg × RATE(price) × 18/1000 × 100
```

> **CORRECTED 30 Aug 2026 — `NGO_RATE` is NOT a flat 0.10.** This block previously read
> `NGO_RATE(0.10)`, i.e. `price × 0.18`, and every per-cup figure in this document was
> computed from it. The live site has never worked that way: the rate is a three-step
> ladder chosen by the price, applied to the **whole** price.
>
> | | 5% | 7.5% | full 10% | slider ends |
> |---|---|---|---|---|
> | 🇸🇬 SGD | 45.00 | 48.00 | 51.00 | 55.00 |
> | 🇦🇪 AED | 150.00 | 157.50 | 165.00 | 165.00 |
>
> The practical consequence: at the **default** price the rate is 7.5%, not 10%. So the old
> AED headline of `7.6 ¢`/`AED 0.28` per cup, quoted at the 155 default, overstated by a third
> — the correct figures are `5.7 ¢`/`AED 0.21` there, and `8.1 ¢`/`AED 0.30` at the full rate.
> **Always compute a client's per-cup figure at THEIR rate.**
>
> **The ladder was reset 22 Sep 2026 (see `Business-docs/COFFEE-LADDER.md`, the source of truth).**
> Two named points per market and ONE STEP between them: 5% below the opener, 10% at and above it (23 Sep, replacing the 22 Sep ramp):
>
> | | Floor · 5% | Opener · 10% | Ceiling (flat 10%) |
> |---|---|---|---|
> | 🇸🇬 SGD | 46.00 | 51.00 | 60.00 |
> | 🇦🇪 AED | 150.00 | 165.00 | 200.00 |
> | 🇬🇧 GBP | 39.00 | 43.00 | 52.00 |
>
> `PRICE_DEFAULT` = the opener; the floor is a concession. Below the opener every step is 95% NoFilter's, above it 90%; the opener is the one point where the rate changes. `RATE_MID_STEP` / `RATE_RUNG_MID` are
> the 7.5% midpoint, informational only. `rateForPrice()` in the Part 2 master and the Package
> Sheet implements exactly this; the website still carries the old three whole-price bands
> (deliberately untouched 22 Sep) and needs its own patch.
>
> **Why one step, not a ramp.** A ramp between the points gave the forest half of every
> dirham a client added and NoFilter the other half; Alex: "ramping up the price translated
> into no extra margin for me". With one step, every step below the opener is 95% NoFilter's
> and every step above it 90%. The step at the opener is the device: it is where the client
> is told the forest gets the full share, and it is accepted that 164.50 keeps more than 165.
>
> **Milestones still fire.** The 10 / 12 / 15 constants are untouched: the full-rate headline is
> 9.2 ¢ (SGD) and 8.1 ¢ (USD), both inside the 7–12 range. A client at the entry rung sits at
> 3.6–4.1 ¢, well under the 10 ¢ round target — expect no glow there.
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
| Coffee wholesale /kg | `wholePrice` | `48.00` (min 45, max 55, step 0.25) | `54.00` (50–60) | **`155`** (min **147**, max **165**, step **0.5**) |
| Dose per cup | `DOSE_G` | `18` | `18` | `18` (unchanged) |
| Conservation rate | `NGO_RATE` | ladder — see below | `0.10` | ladder — see below |
| ⇒ derived contribution, AT THE FULL RATE | `nfCupC` | `9.2` ¢/cup (SGD cents, at 51) | ~`9.7` ¢/cup | **~`8.1` ¢/cup, USD cents** (`÷ 3.6725`, at 165) |
| ⇒ and at the DEFAULT price | `nfCupC` | `6.5` ¢/cup (48 @ 7.5%) | — | `5.7` ¢/cup USD (155 @ 7.5%) |
| Co-contribution top-up | `topUp` | **`0`–`4.00` / kg**, step `0.25` | `0`–`5` ¢ | **`0`–`12.00` / kg**, step `0.50` |
| Dark-payoff local figure (full rate) | `cupPct` | `≈ SGD 0.09 /cup` | — | `≈ AED 0.30 /cup` |
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

> **The top-up dial is PER KG, not per cup.** Changed 30 Aug 2026 to match the live site. It was
> `0–7.5 ¢/cup` in 0.1 steps — which is `0–SGD 4.17/kg` in increments of 5.6 cents a kilo, a
> per-kilo commitment the client could neither see nor name, in a different unit from the price
> directly above it and from the contract. It is now **SGD 0–4.00/kg in 0.25 steps** and
> **AED 0–12.00/kg in 0.50 steps**, carried by the new `TOPUP_MAX` / `TOPUP_STEP` preset tokens.
> Still 100% pass-through; still converted to cents-per-cup internally, so the 10 / 12 / 15
> milestone constants below are **untouched**. The joint figure shown to the reader stays
> per-cup — decisions in per-kg, payoff in per-cup.
>
> This also repaired something that was quietly broken: the coffee dial alone tops out at 9.2 ¢,
> so the 10 ¢ milestone could never fire from it. At the SGD 48.00 default with a 2.00/kg top-up
> the combined figure is 10.1 ¢ and it fires.
>
> AED slider is fully specified: range **147–165**, start **155**, step **0.5**; contribution
> headline in **USD cents**; dark payoff `≈ AED x.xx /cup`; optional USD sub-line below.

### UAE slider — USD equivalent sub-line (a UAE-only nicety)

The AED is **pegged to USD** at the fixed rate **1 USD = 3.6725 AED** (the long-standing
official peg), so a USD equivalent is exact and never drifts. On the AED slider, show a small,
muted secondary line under each key figure, computed `AED ÷ 3.6725`:

- the AED you set: `AED 155/kg` → `· ~$42.2/kg`
- local per-cup at the full rate: `≈ AED 0.30/cup` → `· ~$0.081 (8.1¢)`

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
  builds): SGD, `48.00`/kg coffee (floor 46, opener 51, slider to 60; 22 Sep 2026), `alex@nofilter.sg`. (CUP_RETAIL was removed from the master — no retail-cup metric.)
- **UAE**: AED floor 150 / opener 165 / ceiling 200 (22 Sep 2026; transacted ≈140 from real invoices — Sprinklr Gulf sits BELOW the floor; override in a client skin), `alex@nofilter.ae`; entity NoFilter LLC · Sharjah Media City (Shams) · TL 2540001.01 · VAT TRN pending FTA. No CUP_RETAIL. **Machine rate card = a full set of estimates in `UAE.json`** (all 4 machines × 24/36-mo rental + purchase), scaled from the SG card by the C8 anchor ratio (~2.42×) as render-clean placeholders. The **only real figure is `RATE_CM8_36MO` = AED 1,211.89/mo** (CaféMatic 8 + fridge, 3-yr lease, from the Sprinklr Gulf deal, USD 329.99/mo × 3.6725 peg). Replace the estimates with actuals when known; finance partner still TBD.
- The Part 3 contract's pricing math is **display-only currency** (`[[CURRENCY]]` labels);
  the rate-card *numbers* are the locale values above. Swapping locale = swap the number set,
  not the code.
- The colophon `DP-2026-[XX]0N` `[XX]` is the **client** code, not the region — locale doesn't
  change it.

> Keep this file as the single home for region values. If a number is wrong, fix it here, not
> in a built pitch.
