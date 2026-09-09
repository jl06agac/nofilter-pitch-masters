# Package Sheet — light Part 2 (build runbook)

**What it is.** A stripped, configurator-forward variant of the Part 2 master for a client
who "just wants a look at packages" — no full spiel. Derived directly from
`_Part2-Master/NoFilter-Part2-MasterTemplate.html`, so it shares that master's design,
CSS, JS and — critically — the **same tokens**. It is not a hand-built one-off.

**File:** `NoFilter-Package-Sheet-Master.html`

## What it keeps vs the full Part 2
Kept:
- **Hero** — the shared **HOLD THE LINE** cover (RGB-split video glitch + cascade title),
  injected via `[[INCLUDE:hero-holdtheline]]` from `_partials/hero-holdtheline.html` — one source of
  truth, shared with the Generic route and a future website. (Formerly: The "We've talked it through…" text
  overlay and the temporary footprint layer were removed.
- **The coffee** — the four-origins showcase (`#recap`: origin videos, NGO partners, copy).
- **The machines** — the full price **configurator** (`#price`: machine cards, rental /
  purchase, 24 / 36-mo toggles, live rates, sticky quote, submit-to-Alex form).
- **Close** — `#talkClose`.

Cut:
- `#merged-experience` ("How NoFilter shows up") and `#whatYouGet` ("behind the scenes") —
  the narrative spiel. The "At Work" nav item that pointed at them was removed too.

## How it stamps
Identical to Part 2 — **same token set, same command**. No new tokens were introduced, so
the existing SG / UAE presets and a client skin resolve it fully. Prices come from the
preset; nothing is typed by hand.

Follow `../_STAMP-A-PITCH.md` / `../_CLIENT-PIPELINE-RUNBOOK.md`, using **this** file as the
Part-2 input. Output goes to `Clients/{Sector}/{Client}/` like any pitch.

Tokens used (all inherited from Part 2): `[[TARGET_NAME]]`, `[[CURRENCY]]`,
`[[RATE_CM2/5/6/8_24MO|_36MO]]`, `[[RATE_FULL|LOW|THRESHOLD]]`,
`[[PURCHASE_CM2/5/6/8]]`, `[[COLOPHON_CODE]]`.

## Verification done at build
- jsdom load test: **zero new script errors** vs the untouched Part 2 master (identical
  error profile — both only surface an unstamped-token ReferenceError and a jsdom
  `getTotalLength` gap, neither real in a browser).
- Token integrity: all prices remain tokens, no literals.
- Structure: 4 origin cards + 4 machine cards present; `#price`, `#recap`, `#talkClose`,
  `#cover` all intact.

## Optional swap
The coffee section currently reuses Part 2's four-origins showcase. Part 1's origin
introduction is an easy drop-in replacement if a different visual treatment is preferred.
