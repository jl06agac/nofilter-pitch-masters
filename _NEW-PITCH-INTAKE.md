# NEW PITCH — UNIVERSAL INTAKE & STANDARDS (Parts 1–3)

**Read this first when starting ANY client pitch — Part 1 (intro), Part 2 (proposal + choices
wizard) or Part 3 (the signable contract).** It governs three things that apply to every part:

1. **The renderable guarantee** — a fresh pitch is never broken on screen.
2. **The intake** — exactly what to prompt Alex for, and what to default.
3. **The website-nav spoof** — how to make the pitch read as the client's own site, done well.

Part-specific process lives in each part's runbook (`_Part1-Master/`, `_Part2-Master/`,
`_Part3-Master/`); this is the shared front door they all point back to.

---

## 1. The renderable guarantee (ALL PARTS)

The instant a master is copied, the agent runs a **placeholder pass** so the pitch renders
cleanly end-to-end **before Alex has answered anything**. Real values then *replace* placeholders
as intake answers arrive. Previewing a half-built pitch full of raw `[[TOKENS]]`, dead animations
and broken images is never acceptable.

**Placeholder rules (every part):**
- **Numbers stay numbers.** Any numeric token or count-up constant gets a real placeholder figure
  (e.g. headcount `3000`) — an unfilled numeric token renders `NaN` and kills the animation.
- **Text placeholders are complete sentences**, marked where a real fact must go
  (e.g. `[a specific commitment — replace me]`).
- **Assets never 404.** Heavy media resolves via `assets/` symlinks into `_shared/`; client-only
  files (mockups, counter, hero poster) point at neutral placeholder files until the real ones exist.
- **The nav never shows another client.** Until the client's brand is harvested, the nav falls back
  to the **neutral NoFilter logo + generic items** — never a leftover UWCSEA/Sprinklr identity.
- **Always tell Alex which fields are still placeholders**, so nothing fake ever ships.

Token **definitions** live in [`_TOKEN-DICTIONARY.md`](_TOKEN-DICTIONARY.md) — the single
source of truth. Each part's token doc carries only the placeholder/example VALUES (Part 1 &
Part 3: `*-Template-Tokens.md`; Part 2: `_Part2-Master/NoFilter-Part2-MasterTemplate-TOKENS.md`);
the placeholder pass = fill from those.

---

## 2. The intake — what to PROMPT Alex for

Ask up front, in order. Each has a default so a missing answer never blocks a preview. Items
marked ★ genuinely need Alex; the rest the agent infers or defaults.

| # | Prompt | Used by | Default if not given |
|---|---|---|---|
| 1 | **Client name** + legal entity | all parts | working name |
| 2 | **Market** — Singapore / UAE | all parts (currency, contact, slider, governing law/tax) | Singapore |
| 3 | **Audience type** — school / workplace / zoo | Parts 1–2 language & tiles | workplace |
| 4 ★ | **Headcount / community size** | Parts 1–2 volume figures | 3,000 → ~187,500 cups → $18,750 |
| 5 ★ | **Intro-letter hook** — addressee + one true researched detail | Parts 1–2 letter/CRT | generic copy, flagged "replace me" |
| 6 ★ | **Client website URL** | the nav spoof + brand harvest (ALL parts use the harvested brand) | neutral NoFilter brand |
| 7 | **Branded assets** — logo, mockups, counter, hero poster, Part 3 signatory/term/equipment | per part | neutral placeholders |
| 8 | **Part 3 only:** signatory, UEN, office, term dates, equipment, confirmed rate | Part 3 contract | placeholders + locale values set |

The agent fills without asking: colophon `DP-2026-[XX]0N`, all venue/audience language from the
audience type, period nouns / event lists, and the locale preset values from `_Locale-Presets.md`.

---

## 3. The website-nav spoof — best practices

**The device:** Parts 1 & 2 are **pixel-match clones of the client's own website** — the pitch
should feel like it opened *on their site*, because familiarity buys trust and attention. This is
the one thing tokens can't do: the nav (logo artwork, menu, colours, fonts) is **harvested from
the client's live site and grafted**, never find-and-replaced.

**Where it applies:**
- **Parts 1 & 2 (microsites):** full nav spoof — the client's real top nav, logo and chrome.
- **Part 3 (the signable contract):** NOT a website spoof — it's a NoFilter document. But it
  uses the **same harvested brand** (the client's logo on the cover, their colours/fonts) so the
  identity is consistent. So: **brand harvest is universal; the nav spoof itself is Parts 1–2.**

**Step 1 — CAPTURE THE LIVE NAV'S REAL STRUCTURE + COMPUTED STYLES (do this FIRST, before building anything).**
The replica is **derived from their code, never guessed.** On the client's homepage at **1440px**,
open DevTools (**⌥⌘I**) and run this — it tells you the nav *pattern* (a simple inline bar vs a
Menu+overlay), the exact typography/spacing, the structure, and hands you the real markup:

```js
(() => {
  const g=(el,ps)=>el?Object.fromEntries(ps.map(p=>[p,getComputedStyle(el)[p]])):null;
  const H=document.querySelector('header,[role=banner],[class*=global-nav],nav');
  const item=[...H.querySelectorAll('a,button')].find(a=>a.offsetParent&&a.getBoundingClientRect().top<90&&a.textContent.trim().length>2);
  return {
    pattern: H.querySelector('[aria-label*=menu i],[class*=hamburger],button[class*=menu i]') ? 'MENU+OVERLAY — replicate the trigger + overlay, NOT a plain bar' : 'INLINE BAR',
    bar:  g(H,['display','height','padding','backgroundColor','position','alignItems','justifyContent','fontFamily']),
    item: g(item,['fontFamily','fontSize','fontWeight','color','letterSpacing','lineHeight','padding','textTransform']),
    itemText: item && item.textContent.trim(),
    structure: [...H.children].map(c=>({tag:c.tagName.toLowerCase(),cls:(c.className||'')+'', txt:c.textContent.trim().replace(/\s+/g,' ').slice(0,40)})),
    navHTML: H.outerHTML.replace(/\s+/g,' ').slice(0,4000)   // the REAL markup to model the replica on
  };
})()
```
Then **screenshot the bar at rest at 1440px** (and one with a nav item hovered). You build the
replica to match that screenshot **and** these computed values — pixel for pixel.

**Step 2 — pull the brand assets** (logo SVG, exact hex, fonts, item labels):

```js
// helper + logo + colours + fonts + items (run on the same page)
toHex = c => '#'+(c.match(/\d+/g)||[]).slice(0,3).map(n=>(+n).toString(16).padStart(2,'0')).join('');
L = document.querySelector('header a[href="/"] svg, header svg, [class*=logo] svg, [class*=logo] img'); copy(L.outerHTML);
H = document.querySelector('header,[role=banner],nav');
console.log('bar bg', toHex(getComputedStyle(H).backgroundColor), '| item', toHex(getComputedStyle(H.querySelector('a')).color));
console.log('font', getComputedStyle(H).fontFamily);
console.log('items', [...H.querySelectorAll('a')].map(a=>a.textContent.trim()).filter(Boolean));
```

**Capture the logo's MOTION too (not just its shape).** A nav logo usually animates — on load
and/or on hover. Inspect it: check the logo/link for CSS `animation`/`transition`, scan the
stylesheets for `@keyframes`, and look for Lottie/JS. Replicate the motion with the SAME easing and
timing. (Real example — Accenture's nav logo: the `accenture` wordmark is hidden (`translateY(24px)`)
and slides up on hover via `transition: 550ms cubic-bezier(0.85,0,0,1)`; the replica must do the
same, not sit static.) 

**Lift the logo's ACTUAL SVG geometry, never a text stand-in.** Grab the real `<path>` data (e.g.
Accenture's greater-than mark + the full wordmark path) so the logotype is exact — an "accenture"
in a similar font is not a replica. For a long path that the console truncates, extract it in
marker-verified chunks (`'X>'+d.slice(0,800)+'<X'`) or via the clipboard/a data-URL, and verify by
length before grafting.

**Rule — build the replica FROM the captured code.** Match the measured font-size, weight,
letter-spacing, colour, bar height, padding and item spacing **exactly**. If the real nav is a
Menu+overlay, replicate *that* pattern — never substitute a simpler bar. Never invent spacing or
layout you didn't measure. (The agent can run all of the above itself via the in-browser tools.)

**Graft — REBUILD the nav to match the captured structure (do NOT just reskin the master's nav):**
- Replace the master's nav markup with a faithful replica of the client's real bar from Step 1 —
  its pattern (inline bar vs Menu+overlay), layout, item set, logo placement and utility cluster.
  Slapping the client's logo onto the master's (e.g. UWCSEA's) nav architecture is NOT acceptable.
- Keep ONLY the master's JS hook (the wrapper id) so existing behaviour (sticky-on-scroll) still
  fires — everything visible is rebuilt to the client's bar.
- **Fonts:** if the client's webfont isn't ours to embed, match with the closest licensed/web-safe
  stack and note it — don't ship a broken `@font-face`.
- **Fidelity:** exact hex, spacing and weight; match the client's nav layout. Responsive down to
  mobile; don't let the graft break the burger/scroll behaviour.
- **Accessibility:** `aria-label`s and `alt` text carry the client's name, not UWCSEA's.

**Placeholder until harvested:** neutral NoFilter logo + generic nav items. Never leave a previous
client's identity in the chrome.

**Tone / disclosure:** tease the mechanism in outreach without revealing the pixel-match trick.
The pitch is a private, client-specific link shown *to that client* — keep it that way; don't
deploy it publicly where it could be mistaken for the client's official site.

---

## Build sequence (every part)
1. Copy the part master → `Schools|Workplaces|Zoos/<Client>/NoFilter-<Client>-Part<N>.html` (never `index.html`).
2. `assets/` symlinks into `_shared/` (`[[SHARED_BASE]] = assets` for local preview).
3. **Placeholder pass** — render-clean before any answers.
4. **Run the intake** (§2); replace placeholders as answers land; flag what's still placeholder.
5. **Brand harvest + nav spoof** (§3) from the client URL.
6. Gates + live preview: token gate empty · numeric constants reviewed · open in Chrome and eyeball.
7. Deploy: `[[SHARED_BASE]]` → shared-assets site URL (deploy the shared site first); Part 3 locale values set.

> Per-part detail: `_Part1-Master/Part1-Build-Runbook.md`, `_Part2-Master/Part2-Build-Runbook.md`,
> `_Part3-Master/Part3-Build-Runbook.md`. Token **definitions**: `_TOKEN-DICTIONARY.md` (single
> source of truth). Placeholder values: Part 1 & 3 `*-Template-Tokens.md`, Part 2
> `_Part2-Master/NoFilter-Part2-MasterTemplate-TOKENS.md`.
> Sector-specific method (zoos): `Zoos/ZOO-PITCH-PLAYBOOK.md`.
