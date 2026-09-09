# NoFilter Pitch System — Canonical Token Dictionary
**Single source of truth for the token vocabulary across Part 1 (intro) · Part 2 (proposal) · Part 3 (contract), and across markets Singapore / UAE / London.**
Supersedes the per-part `*-Template-Tokens.md` lists and folds in `_Locale-Presets.md`. Last set: 2026-07-03.

A build is: **neutral master → apply MARKET preset → fill CLIENT tokens → set DEAL commercials → ship.** One answer fills the same token everywhere, because there is now one name per concept.

---

## Layer 1 · CLIENT tokens (per pitch, from the intake — one value flows to all parts)
| Canonical token | Meaning | Parts | Example (Accenture) |
|---|---|---|---|
| `[[TARGET_NAME]]` | client display name | 1·2·3 | Accenture |
| `[[TARGET_NAME_URLENC]]` | URL-encoded client name (mailto) | 2 | Accenture |
| `[[COLOPHON_CODE]]` | doc code `DP-2026-[XX]0N` (`[XX]`=client) | 1·2·3 | DP-2026-AC02 |
| `[[TARGET_SIGNATORY]]` | client signer / prefilled contact name | 2·3 | Jessie Kok |
| `[[TARGET_CONTACT_EMAIL]]` | client contact email | 2·3 | jessie.kok@accenture.com |
| `[[TARGET_BILLING_ENTITY]]` | billing/counterparty entity if not the client itself | 2·3 | ISS Facility Services (o/b/o Accenture) |
| `[[TARGET_LEGAL_ENTITY]]` · `[[TARGET_UEN]]` · `[[TARGET_OFFICE]]` | client's own legal entity for the contract | 3 | (client-supplied) |
| `[[FORM_NAME]]` | Netlify form id (unique per client) | 2 | accenture-terms |
| `[[COUNTER_SRC]]` | live impact-counter iframe src | 1·2 | accenture-counter.html |
| `[[COBRAND_MACHINE/CARDS/CUP/BAG]]` · `[[HERO_POSTER]]` · `[[CLIENT_LOGO]]` | client co-brand media | per part | accenture-nofilter-*.png |
| audience/venue language set: `[[AUDIENCE_*]]`, `[[VENUE_*]]`, `[[NAV_ITEM_COMMUNITY]]`, `[[NAV_RAIL_1/2]]`, `[[COMMUNITY_NUM]]`, `[[PERIOD_NOUN]]`, `[[CAMPAIGN_EXAMPLES]]`, letter/CRT lines | derived from audience type (school/workplace/zoo) | 1·2 | workplace set |

## Layer 2 · MARKET / LOCALE tokens (one preset per region)
| Canonical token | Meaning | 🇸🇬 Singapore | 🇦🇪 UAE (Sharjah/Shams) | 🇬🇧 London (future) |
|---|---|---|---|---|
| `[[CURRENCY]]` | currency **code** | SGD | AED | GBP |
| `[[CUR_SYMBOL]]` | currency **symbol** (Part 1 counter) | S$ | AED | £ |
| `[[TAX_LABEL]]` / `[[TAX_LABEL_LONG]]` | tax name | GST / Goods and Services Tax | VAT / Value Added Tax | VAT / Value Added Tax |
| `[[NF_CONTACT_EMAIL]]` | NoFilter contact | alex@nofilter.sg | alex@nofilter.ae | **TBD** |
| `[[NF_ENTITY_NAME]]` | **NoFilter's own supplier entity** | NoFilter Pte. Ltd | NoFilter LLC | **TBD (NoFilter Ltd, UK)** |
| `[[NF_ENTITY_REG]]` | its registration no. | UEN 201839882N | Trade Licence 2540001.01 (Shams free zone) · VAT TRN pending FTA | **TBD (Companies House)** |
| `[[NF_ENTITY_ADDRESS]]` | its registered address | 31 Kaki Bukit Road 3 · #01-02C Techlink · Singapore 417818 | Sharjah Media City (Shams), UAE | **TBD** |
| `[[GOVERNING_JURISDICTION]]` / `_UC` | governing law | Singapore / SINGAPORE | the United Arab Emirates / THE UNITED ARAB EMIRATES | TBD (set when UK entity lands) |
| `[[PREMISES_CITY]]` / `_UC` | client premises city (per client) | Singapore / SINGAPORE | e.g. Dubai / DUBAI | London / LONDON |
| `[[FINANCE_PARTNER]]` | leasing partner (kept out of client-facing copy → "our leasing partner") | (SG financier) | **TBD** | **TBD** |
| price band | see Layer 3 | 45 / 48 / 55 | 155 (145–165) — set; note transacted ≈140 | **TBD** |
| `[[NF_SIGNATORY]]` | NoFilter-side signer | Alexander Graham Allen Clark, MD | Alexander Graham Allen Clark, MD | — |

> Contact card (Parts 1 & 2): show **both** SG and UAE lines for credibility; only the *order* changes by build (build's region first). London adds a third line when live. Part 3 uses the single `[[NF_CONTACT_EMAIL]]`.
> AED contribution headline is shown in **USD cents** (`nfCupC ÷ 3.6725`, the fixed peg) so the 10¢/12¢/15 milestone constants fire natively — do NOT rescale them.

## Layer 3 · DEAL / COMMERCIAL tokens (per deal; SG canon = v133)
| Canonical token | Meaning | SG canon (v133) | UAE | London |
|---|---|---|---|---|
| `[[PRICE_FLOOR]]` / `[[PRICE_DEFAULT]]` / `[[PRICE_CEILING]]` | coffee /kg band | 45 / 48 / 55 | 145 / 155 / 165 (set; transacted ≈140) | TBD |
| `[[RATE_THRESHOLD]]` | price where full rate applies | 46 | market | market |
| `[[RATE_LOW]]` / `[[RATE_FULL]]` | conservation rate below / at threshold | 0.05 / 0.10 | 0.05 / 0.10 | 0.05 / 0.10 |
| `[[SUPPLY_TERM]]` | coffee supply term | 2-year | — | — |
| `[[RATE_CM*_*MO]]` / `[[PURCHASE_CM*]]` | machine rental/purchase rates (all 4 machines × 24/36-mo + purchase) | full card in master fallbacks (SGD) | full card in `UAE.json` (AED) — **estimates except** `RATE_CM8_36MO` = 1,211.89 (real C8 + fridge, 3-yr, Sprinklr Gulf). Replace estimates with actuals when known | TBD |

---

## Reconciliation map (DONE 2026-07-03 — kept as history)
`NoFilter-Part2-MasterTemplate.html` and its Accenture skin were reconciled to the canonical set
on 2026-07-03; they now use only the canonical names below. This table is the historical old→new
map — the **left column is retired**, do not use it in any current doc or build:

| Old (retired) | → Canonical (current) | Notes |
|---|---|---|
| `[[CLIENT_NAME]]` | `[[TARGET_NAME]]` | Part 1 & 3 already use TARGET_NAME |
| `[[DOC_CODE]]` | `[[COLOPHON_CODE]]` | Part 1 & 3 use COLOPHON_CODE |
| `[[CONTACT_NAME]]` | `[[TARGET_SIGNATORY]]` | matches Part 3 |
| `[[CONTACT_FIRST_NAME]]` | `[[TARGET_SIGNATORY_FIRST]]` | (email-mockup first name) |
| `[[CONTACT_EMAIL]]` | `[[TARGET_CONTACT_EMAIL]]` | matches Part 3 |
| `[[CONTACT_ENTITY_NAME]]` | `[[TARGET_BILLING_ENTITY]]` | ISS ≠ the client; distinct concept |
| `[[NF_EMAIL_SG]]` / `[[NF_EMAIL_AE]]` / `[[NF_EMAIL_SINAN]]` | `[[NF_CONTACT_EMAIL]]` (+ `[[NF_CONTACT_EMAIL_2]]`) | market-driven, both lines kept |
| `[[ENTITY_NAME]]` / `[[ENTITY_REG]]` / `[[ENTITY_ADDRESS]]` | `[[NF_ENTITY_NAME]]` / `[[NF_ENTITY_REG]]` / `[[NF_ENTITY_ADDRESS]]` | NoFilter's entity = market preset, not per-client |
| already canonical | `[[CURRENCY]]` `[[TAX_LABEL]]` `[[SHARED_BASE]]` `[[COUNTER_SRC]]` `[[FORM_NAME]]` `[[RATE_THRESHOLD]]` `[[PRICE_*]]` `[[RATE_LOW/FULL]]` `[[SUPPLY_TERM]]` `[[COBRAND_*]]` | keep |

Also: Part 1 `[[CUR_SYMBOL]]` stays (valid symbol token); **add `[[PART2_URL]]`** to Part 1 as the CTA into Part 2 (mirrors Part 2's `[[CONTRACT_URL]]`).

## Outdated items this dictionary corrects
- SG price band `46 / 45–53` → **v133 `45 / 48 / 55`, threshold 46**.
- `CUP_RETAIL` **removed** everywhere (retail-cup % dropped from the master) — do not reintroduce.
- NoFilter's own entity is now **tokenised per market** (`[[NF_ENTITY_*]]`), not a hardcoded SG literal.
- Client entity (`[[TARGET_*]]`) vs NoFilter entity (`[[NF_ENTITY_*]]`) vs billing entity (`[[TARGET_BILLING_ENTITY]]`) are three distinct things — no longer conflated.

## Value gaps to fill (need Alex / the NoFilter LLC folder / legal)
1. **AED price band — SET to 155 (145–165)** per Alex. Evidence flag: real Sprinklr Gulf invoices transact coffee at ~$37 USD/kg ≈ **AED 140** (below the 145 floor); UAE invoices are issued in USD, AED at the 3.6725 peg. Revisit if the slider should reflect ~140.
2. **UAE entity — RESOLVED:** NoFilter LLC · Sharjah Media City (Shams), UAE · Trade Licence 2540001.01 · VAT TRN **pending FTA** · `[[NF_CONTACT_EMAIL]]` = alex@nofilter.ae · signatory Alexander Graham Allen Clark (MD). **Finance partner still TBD.**
3. **London:** entity, address, contact, price band — all future/stub.
4. **Governing law (set, no solicitor review):** SG = Singapore; **UAE = the laws of the United Arab Emirates** (federal), tax = VAT. Basic boilerplate per Alex's instruction — no solicitor review gate. London governing law is set when the UK entity lands.
