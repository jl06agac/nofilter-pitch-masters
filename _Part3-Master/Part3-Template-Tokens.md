# NoFilter Part 3 — Placeholder Example Values

**Token definitions live in [`_TOKEN-DICTIONARY.md`](../_TOKEN-DICTIONARY.md) — the single source of truth.** This file only carries Part 3's *placeholder example values* for the render-clean pass.

The canonical Part 3 is `NoFilter-Part3-Master-Contract-v2.html` — the ONLY Part 3 file now, the
contract endpoint. It reads Part 2's schema-v2 (fleet) handoff and fills equipment / rate / term /
service dates / Schedule B at runtime. (The old Configurator lineage — standalone Configurator,
static `Contract.html` / `-Contract-WIP.html`, v1 donor — was retired and deleted 2026-07-03.)

Fill every `[[TOKEN]]` with find-and-replace, then run the token gate (must return nothing):
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <file>.html | sort -u
```

> ◆ = **locale value**: set per market from the locale preset (no solicitor review; see
> `Part3-Build-Runbook.md` → "Locale values").

---

## Placeholder / example values (the render-clean defaults)

### Client (Customer) identity — 🇸🇬 Sprinklr example
| Token | Sprinklr example |
|---|---|
| `[[TARGET_NAME]]` | `Sprinklr` |
| `[[TARGET_LEGAL_ENTITY]]` | `Sprinklr Singapore Pte Ltd` |
| `[[TARGET_UEN]]` | `201706621H` |
| `[[TARGET_OFFICE]]` | `38 Beach Road, South Beach Tower #08-11, Singapore 189767` |
| `[[TARGET_SIGNATORY]]` | `Ranisah (Anise) Abdul Rahman` |
| `[[TARGET_CONTACT_EMAIL]]` | `ranisah.abdulrahman@sprinklr.com` |

### NoFilter / programme — SG example
| Token | SG example |
|---|---|
| `[[NF_CONTACT_EMAIL]]` | `alex@nofilter.sg` |
| `[[FINANCE_PARTNER]]` | `Orix Leasing Singapore Ltd` |
| `[[COLOPHON_CODE]]` (Part 3 ends `03`) | `DP-2026-[XX]03` |
| `[[SHARED_BASE]]` | live shared-assets site URL |

### Currency, place & term — SG / AED examples
| Token | 🇸🇬 SGD | 🇦🇪 AED |
|---|---|---|
| `[[CURRENCY]]` | `SGD` | `AED` |
| `[[PREMISES_CITY]]` | `Singapore` | e.g. `Dubai` |
| `[[PREMISES_CITY_UC]]` | `SINGAPORE` | `DUBAI` |
| `[[TERM_START]]` — **drives service-date derivation** | `01 June 2026` | per deal |
| `[[TERM_END]]` | `01 June 2029` | per deal |
| `[[TERM_MONTHS]]` | `thirty-six (36)` | per deal |
| `[[TERM_MONTHS_N]]` — **drives service-visit count** (`N ÷ 6`) | `36` | per deal |
| `[[PROGRAMME_YEARS]]` | `2026-2029` | per deal |
| `[[EQUIPMENT_SUMMARY]]` — build-time default; the bridge overwrites at runtime | `CAFÉMATIC 5 · MILK COOLER` | per deal |

### Locale values ◆ (set per market — no solicitor review)
| Token | 🇸🇬 SGD | 🇦🇪 AED |
|---|---|---|
| `[[GOVERNING_JURISDICTION]]` ◆ | `Singapore` | `the United Arab Emirates` |
| `[[GOVERNING_JURISDICTION_UC]]` ◆ | `SINGAPORE` | `THE UNITED ARAB EMIRATES` |
| `[[TAX_LABEL]]` ◆ | `GST` | `VAT` |
| `[[TAX_LABEL_LONG]]` ◆ | `Goods and Services Tax` | `Value Added Tax` |

> UAE governing law is set to the laws of the United Arab Emirates (federal) and tax to VAT —
> basic boilerplate per Alex, no solicitor review.

> **NoFilter supplier note:** Part 3 keeps NoFilter's own SG entity (name, UEN `201839882N`,
> address, "Alex Clark") **literal**; only `[[NF_CONTACT_EMAIL]]` is a token. A UAE deal likely
> needs a different NoFilter supplier entity — not yet tokenised in Part 3; handle by hand and
> tell us so we can add it. (See `_TOKEN-DICTIONARY.md` Layer 2 for the per-market `[[NF_ENTITY_*]]`.)

---

## The choices→contract bridge (what's NOT a token — Part-3-specific)

Equipment model, the monthly rate (Schedule A), the term dates as printed, the six service-visit
dates, and the Schedule B coffee prices are **populated at runtime** from **Part 2's wizard
choices** — Part 2 writes a schema-v2 (fleet) handoff to `localStorage` and
`NoFilter-Part3-Master-Contract-v2.html` reads it. They are not per-build tokens. See
`Part3-Build-Runbook.md` → "The bridge".

- **Indicative rates:** only confirmed machine/term combos (CaféMatic 5 & 8, 3-yr rental) print a
  clean rate. Any other combo prints the rate followed by `(indicative — subject to written
  confirmation)`. **Confirm the rate in writing before a client signs.**
- **Tier-1 scope:** the bridge handles a single primary machine on rental. Multi-machine, the
  barista path, and the no-machine path render `— (on application)` / "see addendum" — finalise
  those by hand for now.
