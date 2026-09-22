# Partner brief master

Four A4 pages: two origin pages, a wholesale offer page and an acceptance page.
Built per partner: `python3 build_brief.py <partner>` merges `partners/<partner>.json`
over the shared price card.
The document IS the supply agreement. Nothing separate follows it, so any clause the
parties need has to be on these pages.

**`SG-WHOLESALE.json` is the source of truth.** Every figure and term in the document is
derived from it at build time: tier prices, the net-of-rebate column, the margin the partner
earns at the recommended shelf price, the rebate, the per-kilo conservation share, delivery,
payment, the roasting cycle, term and notice, and governing law. No price is typed into
`build_brief.py` or into the PDF. Change the card, rebuild, and the document follows.

The card was set on 17 Sep 2026 against `Tools/NF-Cost-Calculator-Internal`: cost base
SGD 27.63 per roasted kg at a 6.00 green-kg roast fee, blended freight 0.59 carrying 30 kg
minimum drops. Every rung must net 30% or better after rebate and contribution.

## Build

    python3 build_brief.py && python3 check_pages.py
    chromium --headless --no-pdf-header-footer --print-to-pdf=NoFilter-Origins-Brief-<Partner>.pdf brief.html

Two guards, and neither is optional.

`build_brief.py` asserts every rung still nets `MIN_NET_PCT` using the cost recorded against
each tier. A price edit that breaks the 30% rule stops the build instead of reaching a client.

`check_pages.py` measures the rendered page and fails if anything overflows or is clipped.
The content column carries `overflow:hidden` so a footer can never be pushed off the page,
which means an overrun would otherwise hide itself. Copy edits change page height, so run
this every time, not just when the layout looks wrong.

## Adding a partner

Drop a logo in (SVG or PNG, reversed white for the orange band) and write
`partners/<name>.json` with PARTNER_NAME, PARTNER_LEGAL, MARKET, TERRITORY_NOTE,
DELIVERY_POINT, DELIVERY_SHORT, LOGO, LOGO_HEIGHT_MM, SIGNATORY and REBATE_EARNED_BY.
Nothing else is partner-specific: no price, term or clause lives in a partner file, which is
what stops two resellers in the same market being quoted different numbers.

The header band is a fixed 25.4mm so a lockup of any shape cannot change page height.
A partner with no logo file yet still builds, with the name set in type instead.

A second *market* is different: it needs its own price card built off that market's cost base,
never converted from this one.

Current partners: `lyreco` (SG and Malaysia, Woodlands) and `kumpulan` (SG, Changi). They are
direct competitors for the same end accounts, so they are deliberately on identical numbers.
