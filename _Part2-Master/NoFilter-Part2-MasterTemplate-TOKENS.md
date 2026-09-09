# Part 2 (Master Template 2) — Placeholder Example Values & MT2 Manifest

**Token definitions live in [`_TOKEN-DICTIONARY.md`](../_TOKEN-DICTIONARY.md) — the single source of truth.** This file only carries Part 2's *placeholder example values* for the render-clean pass, plus the Master Template 2 manifest (skin mechanics, verification, reconciliation).

**Master:** `NoFilter-Part2-MasterTemplate.html` · **First skin:** `NoFilter-Part2-Skin-Accenture.json`
**Extracted from:** `Workplaces/Accenture/NoFilter-Part2-Accenture-base-stepJ.html` (v133, md5 `d1a6a0e5…`), 3 Jul 2026. The crowned stepJ was copied, never edited.

> MT2 uses the **canonical** token names throughout (reconciled 2026-07-03: `[[TARGET_NAME]]`,
> `[[COLOPHON_CODE]]`, `[[TARGET_*]]`, `[[NF_ENTITY_*]]`, `[[NF_CONTACT_EMAIL_*]]`). The Accenture
> values below are recorded against those canonical names. In practice the values are split across
> `_skins/Accenture.json` (client + deal) and `_presets/SG.json` (market) and applied via `_tools/nf-stamp.mjs`.

## How it works
Master Template 2 is stepJ with every client, geography and commercial value lifted into `[[TOKEN]]` grammar. A **skin** is a values file (see the Accenture JSON) mapping each token to a concrete value. Stamping a client = substitute the skin's values for the tokens. Never edit a skin from a skin; never skin a second client until this master exists (it now does).

## Verification (lossless, proven)
Applying the Accenture skin to the master reproduces the original stepJ **byte-for-byte except three intended reconciliations** (see below): the regenerated file differs from stepJ only at `SMIN`, `SMAX`, `REC_PRICE`. Residual client/entity strings in the master: **zero**. All 13 inline scripts pass `node --check` both with tokens present and with the Accenture skin applied.

## Reconciliation baked in (the one deliberate change vs stepJ)
stepJ's price slider was canon (`min="45" max="55" value="48.00"`) but its JS scale constants were stale (`SMIN=42, SMAX=53, REC_PRICE=42`), leaving the thumb-bubble and recommended tick misaligned. In the master these are bound to the price-band tokens (`SMIN=[[PRICE_FLOOR]]`, `SMAX=[[PRICE_CEILING]]`, `REC_PRICE=[[PRICE_FLOOR]]`), so the Accenture skin now renders them as 45/55/45 - the fix. This is the only behavioural difference from stepJ.

---

## Placeholder / example values — Accenture skin (MT2 render-clean defaults)

### Client layer
- `[[TARGET_NAME]]` = Accenture · `[[TARGET_SIGNATORY]]` = Jessie Kok · `[[TARGET_SIGNATORY_FIRST]]` = Jessie · `[[TARGET_CONTACT_EMAIL]]` = jessie.kok@accenture.com · `[[TARGET_BILLING_ENTITY]]` = ISS Facility Services · `[[FORM_NAME]]` = accenture-terms · `[[COUNTER_SRC]]` = accenture-counter.html · `[[COLOPHON_CODE]]` = DP-2026-AC02
- Co-brand assets: `[[COBRAND_MACHINE]]` = accenture-nofilter-machine.png · `[[COBRAND_CARDS]]` = accenture-nofilter-cards.png · `[[COBRAND_CUP]]` = accenture-nofilter-cup.png · `[[COBRAND_BAG]]` = accenture-nofilter-bag.mp4

### Geography / entity layer
- `[[CURRENCY]]` = SGD · `[[NF_ENTITY_NAME]]` = NoFilter Pte. Ltd · `[[NF_ENTITY_REG]]` = 201839882N · `[[NF_ENTITY_ADDRESS]]` = 31 Kaki Bukit Road 3 · #01-02C Techlink · Singapore 417818 · `[[TAX_LABEL]]` = GST  *(market layer → `_presets/SG.json`)*
- NF contacts: `[[NF_CONTACT_EMAIL_SG]]` = alex@nofilter.sg · `[[NF_CONTACT_EMAIL_AE]]` = alex@nofilter.ae · `[[NF_CONTACT_EMAIL_2]]` = sinan@nofilter.sg

### Commercial layer
- `[[PRICE_FLOOR]]` = 45 · `[[PRICE_DEFAULT]]` = 48 · `[[PRICE_CEILING]]` = 55 · `[[RATE_THRESHOLD]]` = 46 · `[[RATE_LOW]]` = 0.05 · `[[RATE_FULL]]` = 0.10 · `[[SUPPLY_TERM]]` = 2-year

### Equipment layer (already tokenised in stepJ, preserved)
- `[[RATE_CM2_24MO]]`, `[[RATE_CM2_36MO]]`, `[[RATE_CM5_24MO]]`, `[[RATE_CM6_24MO]]`, `[[RATE_CM6_36MO]]`, `[[RATE_CM8_24MO]]`, `[[PURCHASE_CM2/5/6/8]]`, `[[CONTRACT_URL]]`

---

## Placeholder / example values — audience language (UWCSEA-derived, by audience type)

These narrative/language tokens come from the earlier UWCSEA Part 2 build and carry the
per-audience render-clean defaults (school / workplace / zoo). Fold the ones your MT2 skin needs.

### Venue language (the physical place coffee lives)
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[VENUE_ADJ]]` | campus | office | visitor |
| `[[VENUE_NOUN]]` | campus | the office | the zoo |
| `[[VENUE_POSS]]` | your campus | your team | your café |
| `[[VENUE_PREP]]` | on campus | at work | at the zoo |
| `[[NFBAR_VENUE]]` (nav bar item) | On Campus | At Work | At the Zoo |

### Audience language (the people)
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[AUDIENCE_PEOPLE]]` | kids | people | visitors |
| `[[AUDIENCE_PEOPLE_CAP]]` | Teenagers | People | Visitors |
| `[[AUDIENCE_PERSON]]` | a student | someone | a visitor |
| `[[AUDIENCE_PERSON_CAP]]` | A student | Someone | A visitor |
| `[[AUDIENCE_PEOPLE_LIST]]` | student, teacher and parent | colleague | visitor |
| `[[AUDIENCE_NOUN_CAP]]` (dial/stack label) | School | Company | Zoo |
| `[[AUDIENCE_POSS]]` | the school's | the company's | the zoo's |
| `[[AUDIENCE_THEY]]` | the school | the company | the zoo |

### Volume model (the headline math) — UWCSEA values
| Token | UWCSEA value |
|---|---|
| `[[AUDIENCE_COMMUNITY_SIZE]]` | around 2,500 staff and sixth-formers |
| `[[VOLUME_BASIS]]` | quarter of them having one campus coffee a day |
| `[[ANNUAL_DAYS]]` | 179 teaching days |
| `[[CALENDAR_PERIOD]]` | 2026/27 calendar |
| `[[ANNUAL_CUPS_APPROX]]` | 112,000 |
| `[[ANNUAL_CUPS]]` | 111,875 |
| `[[ANNUAL_CONSERVATION]]` | 11,188 |
| `[[UPTAKE_PCT]]` | 25% |

### CRT terminal (§02 typewriter) — UWCSEA copy
| Token | UWCSEA copy |
|---|---|
| `[[CRT_LINE_TEACHES]]` | The coffee on campus isn't just coffee. At a school like UWCSEA, it teaches something. |
| `[[CRT_COMMUNITY_LINE]]` | 2,500 staff & sixth-formers on campus |
| `[[CRT_COMMUNITY_SUFFIX]]` | ` on campus` (ticker suffix — keep leading space) |
| `[[COMMUNITY_NUM]]` | 2500 (ticker target — **numeric**, no commas) |

### Intro letter (opening typewriter) — personalised, rewrite fully per target
| Token | UWCSEA copy |
|---|---|
| `[[LETTER_GREETING]]` | Dear Aloni, Zoe and Jacyl, |
| `[[LETTER_LINE_NEVER]]` | Maybe it's that I've never worked inside a school before. |
| `[[LETTER_LINE_HONEST_A]]` | Or that schools run on something more honest: |
| `[[LETTER_LINE_HONEST_B]]` | kids close enough to the future to take it personally, and teachers who never stopped caring either. |
| `[[LETTER_LINE_STOPPED]]` | But a few Spotlight articles in, I'd mostly stopped looking for the trick. |
| `[[LETTER_LINE_NOTPERFORMATIVE]]` | Sustainability at UWCSEA doesn't feel performative. |
| `[[LETTER_LINE_SPECIFIC_A]]` | I keep coming back to the Dover water catchment system Zoe described: |
| `[[LETTER_LINE_SPECIFIC_B]]` | placed at the heart of the school, capturing, connecting, nourishing as it goes. |

> These lines reference real, researched specifics about the target. Keep researching one true
> detail per target rather than writing generic filler.

### Showcase tile tokens — UWCSEA copy
| Token | UWCSEA copy |
|---|---|
| `[[IMPACT_VISIBLE_TAIL]]` | Another lesson made real: that small choices add up, and that the claims worth making are the ones you can check. |
| `[[PERIOD_NOUN]]` | term (the period a goal is set over — "quarter", "season", etc.) |
| `[[CAMPAIGN_EXAMPLES]]` | a house competition, an Earth Week push |
| `[[ENGAGE_TITLE]]` | Something students can engage with |
| `[[ENGAGE_BODY]]` | students in SEED and service programs |
| `[[ENGAGE_TAIL]]` | The coffee that carries the lesson. |
| `[[CART_EVENTS]]` | Sports days, open mornings, parent-teacher conferences, graduations |
| `[[TRIPS_BODY]]` | UWCSEA's Outdoor Education trips already travel to Indonesia. The forests your coffee protects, in Sumatra, alongside the very NGOs your contribution funds, are within reach of the kind of trip your students already take. Conservation, agroforestry, coffee at origin: a partnership we could build into something students stand in, not just read about. |
| `[[TRIPS_TAIL]]` | *(in-tile emphasis line — UWCSEA version folded into TRIPS_BODY; set as needed or leave empty)* |
| `[[COMPOST_PARTNER]]` | the Sennett Community Harvest Hub |

> The "Closer than you'd think" trips tile is school-specific. For a workplace or zoo, repurpose
> it — e.g. a workplace CSR/offsite visit to origin, or a zoo's conservation-travel program.

### Nav chrome (kept as reusable structure; re-skin per target)
| Token | UWCSEA value | Note |
|---|---|---|
| `[[NAV_RAIL_1]]` | `Dover<br>Campus` | left utility rail label — `<br>` allowed |
| `[[NAV_RAIL_2]]` | `East<br>Campus` | left utility rail label |
| `[[NAV_ITEM_COMMUNITY]]` | `UWCSEA<br>Community` | primary nav item |
| `aria-label="UWC South East Asia"` (×3) | logo SVG labels | overwrite when grafting target's real logo |
| `assets/machine-livery-target.png` | machine mockup | replace with target-branded render |
| `assets/reusable-cup-target.png` | cup mockup | replace |
| `assets/bag-mockup-target.png` | bag mockup | replace |
| `[[COUNTER_SRC]]` | `uwcsea-counter.html` | the split-flap counter iframe source |

### Shared-asset hosting note
`[[SHARED_BASE]]` — base for the **shared** conservation/brand media (33 refs). **Default
(preview + deploy):** the shared-assets site URL, e.g. `https://nofilter-shared.netlify.app` (no
trailing slash). **Offline fallback only:** `assets` (local symlinks). The three `-target.png`
mockups, the counter and the logo stay **local**. Deploy the shared-assets site first.

---

## ⚠️ JS animation constants — edit by hand (not tokenized)

The display strings are tokenized, but the count-up animations target literal constants that still
hold UWCSEA's numbers. Search and edit:

- `const COFFEE_CUPS = 111875;`  → target's annual cups
- `var GUEST_TARGET  = 111875;`  → same figure (hero hook counter)
- CRT ticker `to:111875` (cups poured frame) → target's annual cups
- CRT ticker `to:11188` (SGD big-number frame) → target's annual conservation $
- CRT ticker `to:2500` is wired to `[[COMMUNITY_NUM]]` — set that token numerically
- `CUP_RETAIL` removed — no longer in the master (retail-cup readout dropped)

Each has an `EDIT PER TARGET` comment beside it in the file.

---

## Notes / not tokenised on purpose
- CSS/JS class hooks `nf-accenture-nav` and `q-mail--accenture` (5 refs) are internal identifiers, not visible content - left as-is (rename later if desired, needs matching CSS+JS).
- Prose rate mentions ("5% and 10%", "5-10%") are left literal: rates are stable brand policy, while the functional rates are configurable via `[[RATE_LOW]]`/`[[RATE_FULL]]`.
- Derived on-screen figures (fleet total, ¢/cup, annual contribution) are computed by `compute()` at runtime - not tokenised.
- `[[CUP_RETAIL]]` **removed** everywhere (retail-cup metric dropped from the master) — do not reintroduce.

## To stamp a new client / market (e.g. UAE)
Build a client skin (copy `_skins/_CLIENT-TEMPLATE.json` → `_skins/<Client>.json`) with the
client atoms, then pick the market preset: for UAE use `_presets/UAE.json`, which carries
`[[CURRENCY]]=AED`, the `[[NF_ENTITY_*]]` LLC values, `[[TAX_LABEL]]=VAT` and the AED price band
(see `_TOKEN-DICTIONARY.md` Layer 2/3). Stamp master + preset + skin via `_tools/nf-stamp.mjs`
(see `../_STAMP-A-PITCH.md`) — you never hand-substitute the market values. Governing law + tax
are set per market (SG = Singapore/GST; UAE = the laws of the UAE/VAT — basic boilerplate, no
solicitor review).

## Final check before deploy (Part 2 is never bundled)
```
grep -oE '\[\[[A-Z0-9_]+\]\]' your-file.html | sort -u    # must return nothing
grep -n '111875\|11188\|2500' your-file.html              # confirm JS constants updated
```
