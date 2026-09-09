# NoFilter Part 1 — Placeholder Example Values

**Token definitions live in [`_TOKEN-DICTIONARY.md`](../_TOKEN-DICTIONARY.md) — the single source of truth.** This file only carries Part 1's *placeholder example values* for the render-clean pass.

`NoFilter-Part1-Master-Template.html` is the audience-neutral Part 1 microsite (the
"Conservation Coffee Partnership" intro). Colophon ends `01`. Tokenised from the UWCSEA
Part 1 build (16 tokens); the conservation narrative is shared house copy and stays.
For the build process see `Part1-Build-Runbook.md`.

---

## Placeholder / example values by audience (the render-clean defaults)

### Core identity
| Token | School eg | Workplace eg | Zoo eg |
|---|---|---|---|
| `[[TARGET_NAME]]` | UWCSEA | Aon Singapore | Auckland Zoo |
| `[[COLOPHON_CODE]]` | DP-2026-NF01 | DP-2026-AON01 | DP-2026-AZ01 |

### Volume (the headline number)
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[COMMUNITY_NUM]]` (numeric, no commas) | 2500 | the headcount | daily footfall / members |

> `[[COMMUNITY_NUM]]` appears twice: the visible `<b id="guestCount">` figure and
> `var GUEST_TARGET = [[COMMUNITY_NUM]];` in the script. Fill both (same value).
> ⚠️ The `var wait = 2500 …` line is a **false positive** — it's an animation timer, not the
> community number. Leave it.

### Venue language (where the coffee lives)
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[VENUE_NOUN]]` | campus | office *(mind the "A"→"An")* | zoo |
| `[[VENUE_PREP]]` | on campus | at work | at the zoo |
| `[[VENUE_PLACES]]` | common room or reception | kitchen or reception | café or members' room |
| `[[VENUE_MOMENT]]` *(narrative, rewrite per type)* | a staffroom lingers over, and a parents' evening remembers | a team lingers over between meetings | a keeper's break and a members' morning remember |

### Audience language (the people)
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[AUDIENCE_COMMUNITY]]` | staff and sixth formers | your team | staff and visitors |
| `[[AUDIENCE_PEOPLE]]` | students | colleagues | visitors |
| `[[AUDIENCE_PEOPLE_LIST]]` | staff, students and parents | the whole team | staff and visitors |
| `[[AUDIENCE_SERVE_LIST]]` | staff, sixth form and parents | the team | staff and visitors |

### Form + asset placeholders
| Token | School | Workplace | Zoo |
|---|---|---|---|
| `[[ORG_PLACEHOLDER]]` | School name… | Company name… | Organisation name… |
| `[[HERO_POSTER]]` | assets/schoolphoto.jpg | assets/officephoto.jpg | assets/zoophoto.jpg |
| `[[PART2_URL]]` | — | — | — |

### Nav chrome (kept as reusable structure; re-skin per target)
| Token | UWCSEA value |
|---|---|
| `[[NAV_RAIL_1]]` | `Dover<br>Campus` (left utility rail; `<br>` allowed) |
| `[[NAV_RAIL_2]]` | `East<br>Campus` |
| `[[NAV_ITEM_COMMUNITY]]` | `UWCSEA<br>Community` (primary nav item) |

Overwrite by hand when you graft the target's real nav (not tokenised, but must change):
the logo SVG + its `aria-label="UWC South East Asia"`, the other rail items
(`Find it Fast`, `Login`, `Apply`, `Give`) and primary nav items (`About Us`, `Admissions`,
`Learning`, `Careers`, `Support Us`), and the provenance code-comments mentioning UWCSEA.

### Shared-asset hosting note
`[[SHARED_BASE]]` — base for the **shared** conservation/brand media (the 39 heavy assets
reference `[[SHARED_BASE]]/<file>`). **Default (preview + deploy):** the shared-assets site URL,
e.g. `https://nofilter-shared.netlify.app` (no trailing slash). **Offline fallback only:** `assets`
(local symlinks). The hero-poster and logo stay **local** (per-client). Deploy the shared-assets
site **before** any pitch that points at it.

---

## Final check before deploy
```
grep -oE '\[\[[A-Z0-9_]+\]\]' <file>.html | sort -u   # tokens: must be empty
grep -n 'GUEST_TARGET\|guestCount\|UWCSEA' <file>.html # JS constant set; no stray UWCSEA in visible text
```

*Benchmark provenance: tokenised from `Schools/UWCSEA/NoFilter-UWCSEA-PartOne.html`
(the current-generation Part 1, 18 Jun 2026). 16 tokens. Conservation narrative left intact.*
