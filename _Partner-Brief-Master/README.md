# Partner brief master

Four A4 pages: two origin pages, a wholesale offer page and an acceptance page. Five where the
partner also takes the machine rental page (see below).
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

One exception, added 6 Oct 2026: a partner file may set `"REBATE_PCT": 0`. Talula is on no
marketing rebate because it is much smaller than Lyreco and Kumpulan. The build then drops the
net-of-rebate column, the rebate card and the rebate row on the acceptance page, and the margin
shown is the shelf price against the list price. The tier prices stay the shared card's.

The header band is a fixed 25.4mm so a lockup of any shape cannot change page height.
A partner with no logo file yet still builds, with the name set in type instead.

A second *market* is different: it needs its own price card built off that market's cost base,
never converted from this one.

Current partners: `lyreco` (SG and Malaysia, Woodlands) and `kumpulan` (SG, Changi). They are
direct competitors for the same end accounts, so they are deliberately on identical numbers.

`talula` (SG, Chia Ping Road) was added 6 Oct 2026 on the same coffee numbers, and is the first
partner with the machine rental page.

## Introductions page (optional, added 6 Oct 2026)

A partner file with `"RENTAL": true` gets a fifth page, placed before acceptance, and one extra
row in the acceptance recap. A partner without that key builds exactly as before: Lyreco and
Kumpulan are rebuilt after every change to this file and compared byte for byte.

The structure: the partner introduces a business, and NoFilter contracts with that business
directly for the machine and the coffee. The partner holds no lease and no stock. It earns a flat
amount per kilogram of coffee supplied and a fixed amount per machine per month, for the length
of the client's first agreement. Bags the partner sells itself stay on the wholesale page.

Where each number comes from:

- **Rental rates and cost-in** are read from `Business-docs/RATE-CARD.md` (sections 1 and 2).
- **The client's coffee range** (46 to 60, opening at 51, 5% and 10%) is read from
  `_Part2-Master/_presets/SG.json`.
- Both are cross-checked against `Tools/NF-Ops/config/rate-card.json`, the extract of the live
  site. If they disagree the build stops. Nothing is typed.
- **What the partner earns** lives in `SG-RENTAL-PARTNER.json`: SGD 3.00 a kilo on coffee, and
  30 / 40 / 40 / 50 a month for the CaféMatic 2 / 5 / 6 / 8.
- **The guards**: every machine on every term must net 40% after its share. Coffee must net 28%
  after the fee at both the floor and the opener. It currently nets 28.4% and 29.9%, which is
  under the 30% rule on coffee alone; the card's `_NOTE_COFFEE_GUARD` records why that stands.

Alex set the structure and the SGD 3.00 on 6 Oct 2026. **The machine amounts, the first-agreement
limit and the two guard floors were proposed the same day and are not yet confirmed by him.** The
`STATUS` key in the card says so; update it when he has.

One more partner-file key, first used for Talula:

- `"TIER_ADJ"` moves every rung of the wholesale ladder by the same amount (Talula: -1.00, so
  43.50 / 42.50 / 41.50). The 30% guard still runs on the adjusted prices.

## Offer keys a partner file may set (6 Oct 2026, all first used for Talula)

Each one changes wording or layout for that partner only; a partner that sets none builds as before.

- `"FLAT_PRICE": true`: one price at any volume, no ladder. For a buyer the 1,500 kg tier is out of
  reach for.
- `"FIRST_ORDER_KG": 20`: a smaller first order than the standing 30 kg. 20 kg is the car limit and
  still nets about 30% on that delivery.
- `"RETAIL_PACK": true`: adds the 250 g bag and the household shelf prices. Those live in
  `SG-WHOLESALE.json` (`RETAIL_250G`, `RETAIL_RRP_250G`; `RETAIL_RRP_1KG` is kept on the card but no longer printed, since `FORMAT_NOTE` limits household sale to 250 g) and nothing else reads
  them. **The 250 g trade price (14.00) and its 1.00 packing allowance are proposals, not yet
  confirmed by Alex.**
- `"PROPOSAL": true`: the document calls itself a proposal that becomes the agreement on signature.
- `"VALID_LEAD": "To"`: for a brief issued part-way through the term, where "twelve months" is untrue.
- `"PRICES_EX_GST": true`: states on the wholesale page that all prices exclude GST.
- `"STORY_PARA"`, `"BEHIND_OVERRIDE"`: partner-specific wording on the bag page.

The introductions page also pays a coffee-only fee (`COFFEE_ONLY_FEE_PER_KG`, 2.00 for 24 months) for
a client with its own machine, held to the full 30% rule because no machine margin sits behind it.

Machine photos `cm-2/5/6/8.jpg` are downscaled copies of `_CDN-UPLOAD-SAFE/cafematic-*.png`.

## Stickers and bag photo (6 Oct 2026)

Page two shows the origin stickers as printed and the current bag, for every partner:

- `stickers/*.png` are the 40 mm V11 sticker previews from Drive: NoFilter Shared / Brand /
  Origin_Stickers / NoFilter_Origin_Stickers_40mm_V11 (`*_600ppi.png`, checked against its MANIFEST).
- `hero-bag-batang-toru.jpg` is `Marketing/Product-Images/nofilter-batang-toru-1kg-front.png`,
  cropped to the panel and tinted to the panel colour.

They replace the drawn seals in `seals/` and `hero-bag.png`, which nothing in the build reads any
more (nor `make_origin_seals.py`, which only generated those seals). Left in place pending Alex's
say-so to remove them. Lyreco and Kumpulan will pick up the new stickers and bag the next time
they are rebuilt; the PDFs already sent to them are unchanged.

`BRIEF_DATE` in a partner file sets the date on pages one and two; absent, it reads September 2026.
`PREPARED_FOR` names the people the brief is for in the box on page two; absent, it names the partner.

## Cover (optional, added 6 Oct 2026)

`"COVER": true` in a partner file adds a photographic cover as the first page, in the style of the
Accenture contract and the Brand Ambassador pack, with `COVER_KICKER`, `COVER_TITLE` and `COVER_SUB`
as its three lines of type. `cover-photo.jpg` is a portrait crop of `accenture-cover-photo.jpg` from
Drive (NoFilter LLC / Brand Ambassador Programme / Internal build files). First used for Talula.
A partner with no logo file now builds on every page (page one used to assume the file existed).
