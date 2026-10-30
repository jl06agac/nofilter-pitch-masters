#!/usr/bin/env python3
"""
build_brief.py — NoFilter wholesale supply agreement, four A4 pages (five with the rental page).
Built per partner: `python3 build_brief.py <partner>` reads partners/<partner>.json over SG-WHOLESALE.json.
A partner whose file sets "RENTAL": true also gets a machine rental page, driven by
SG-RENTAL-PARTNER.json and Business-docs/RATE-CARD.md. Without that key the output is unchanged.

Sources of truth
----------------
Origin records (region, forest, NGO partner, tasting notes, coordinates) come from the
COFFEES array in the live site build SHIP-2026-09-09b/index.html. Two deliberate
departures, both on Alex's instruction:
  * Cup profiles for ALL FOUR origins were set by Alex on 10 Sep 2026 and no longer
    match the site's figures, nor does Arakan's lead tasting note (stone fruits, not
    grapefruit). The site is the outlier and needs updating.
  * Arakan is set to Honey process here; the site says Fully washed.
Gayo Lues coordinates come from the GIS map (3 deg 55'N, 97 deg 22'E), which is the
single source of truth for coordinates; the site's coffee data has placeholder dashes.

Typography is the locked brand set (Anton / Archivo / IBM Plex Mono), pulled from npm
@fontsource because neither the container nor the Mac can reach Google Fonts.
Field orange is #F27126 per Brand Bible v4.1, not the #EE4D17 the live site uses.

Run:  python3 build_brief.py  &&  chromium --headless --print-to-pdf=... brief.html
"""

import re
import json
import pathlib

HERE = pathlib.Path(__file__).parent

# Every price on page three comes from the wholesale rate card, never from this file. If a number here
# disagrees with the card, the card wins: it is the same source the quote tool and the contract read.
import sys
PARTNER = (sys.argv[1] if len(sys.argv) > 1 else "lyreco").lower()
CARD = json.loads((HERE / "SG-WHOLESALE.json").read_text())
CARD.update(json.loads((HERE / "partners" / f"{PARTNER}.json").read_text()))
LOCK = (f'<img class="ly" src="{CARD["LOGO"]}" alt="{CARD["PARTNER_NAME"]}">'
        if (HERE / CARD["LOGO"]).exists() else
        f'<span class="lyword">{CARD["PARTNER_NAME"]}</span>')
_r = 1 - CARD["REBATE_PCT"] / 100
# "FLAT_PRICE": true in a partner file offers the entry rung alone, at any volume, with no ladder.
if CARD.get("FLAT_PRICE"):
    CARD["TIERS"] = CARD["TIERS"][:1]
    CARD["TIERS"][0]["band"] = "Any volume"
for _t in CARD["TIERS"]:
    # "TIER_ADJ" in a partner file moves every rung by the same amount; the 30% guard below still applies.
    _t["list"] = _t["list"] + CARD.get("TIER_ADJ", 0)
    _t["net"] = _t["list"] * _r
    _t["m_lo"] = (CARD["RRP_LOW"] - _t["net"]) / CARD["RRP_LOW"] * 100
    _t["m_hi"] = (CARD["RRP_HIGH"] - _t["net"]) / CARD["RRP_HIGH"] * 100
    # The rule the whole ladder exists to protect. A price edit that breaks it stops the build
    # rather than reaching a client, which is the entire point of holding prices in the card.
    _t["net_pct"] = (_t["list"] - _t["list"] * (1 - _r) - CARD["CONTRIB_PER_KG"] - _t["cost"]) / _t["net"] * 100
    assert _t["net_pct"] >= CARD["MIN_NET_PCT"], (
        f'{_t["band"]} at {_t["list"]:.2f} nets {_t["net_pct"]:.1f}%, under the '
        f'{CARD["MIN_NET_PCT"]}% floor. Re-derive in the costing calculator before shipping this.')
CUR = CARD["CURRENCY"]
# A partner may carry their own accent; absent one, the document stays NoFilter field orange.
ACCENT = CARD.get("ACCENT") or "#F27126"
# Date line on pages one and two. A partner file may carry its own; absent one it stays as first issued.
BRIEF_DATE = CARD.get("BRIEF_DATE") or "September 2026"
# The paragraph under "Built to sell on its story". A partner file may carry its own ("STORY_PARA"),
# for a partner whose customers are not only offices.
STORY_PARA = CARD.get("STORY_PARA") or """Most coffee on a workplace shelf is bought where it is cheapest to grow,
        and cheap usually means cleared ground. This range is the opposite proposition, and it
        comes with the evidence to say so out loud."""
# The "prepared for" box on page two. A partner file may name the people it is for ("PREPARED_FOR").
import html as _html
WHO = f'Prepared for {CARD["PARTNER_NAME"]}<br>{BRIEF_DATE}<br>alex@nofilter.sg'
if CARD.get("PREPARED_FOR"):
    WHO = (f'Prepared for {_html.escape(CARD["PREPARED_FOR"])}<br>{CARD["PARTNER_NAME"]} &middot; {BRIEF_DATE}'
           f'<br>alex@nofilter.sg')

# ---------------------------------------------------------------------------------------------
# Machine rental through a reseller. Optional: only a partner file with "RENTAL": true gets it.
# Rental rates and cost-in are READ from Business-docs/RATE-CARD.md, never typed here; the only
# numbers this variant owns are the partner's share per machine, held in SG-RENTAL-PARTNER.json.
# ---------------------------------------------------------------------------------------------
# NoFilter's own direct price range (the client chooses within it). Read from the Singapore preset and
# checked against the live-site extract; needed for the introduction page.
LADDER = None
if CARD.get("RENTAL"):
    _sg = json.loads((HERE.parent / "_Part2-Master" / "_presets" / "SG.json").read_text())
    LADDER = dict(floor=float(_sg["PRICE_FLOOR"]), opener=float(_sg["RATE_HI_STEP"]),
                  ceil=float(_sg["PRICE_CEILING"]), low=float(_sg["RATE_LOW"]), full=float(_sg["RATE_FULL"]))
    _site = HERE.parent.parent / "Tools" / "NF-Ops" / "config" / "rate-card.json"
    if _site.exists():
        _kg = json.loads(_site.read_text())["markets"]["SG"]["kg"]
        assert (_kg["floor"], _kg["full"], _kg["ceil"]) == (LADDER["floor"], LADDER["opener"], LADDER["ceil"]), (
            "SG.json and the live-site extract disagree on the coffee range. Settle it in Business-docs/COFFEE-LADDER.md first.")
RENTAL = None
if CARD.get("RENTAL"):
    RENTAL = json.loads((HERE / "SG-RENTAL-PARTNER.json").read_text())
    _root = HERE.parent.parent
    _rc = (_root / "Business-docs" / "RATE-CARD.md").read_text()
    _num = lambda x: int(x.replace(",", ""))
    _s1 = _rc.split("## 1.", 1)[1].split("## 2.", 1)[0]
    _s2 = _rc.split("## 2.", 1)[1].split("## 3.", 1)[0]
    _rates = {int(n): {24: _num(a), 36: _num(b)} for n, a, b in re.findall(
        r"\|\s*Caf\S+ (\d)\s*\|\s*\*\*([\d,]+)\*\*\s*\|\s*\*\*([\d,]+)\*\*\s*\|", _s1)}
    _costs = {(int(n), int(t)): (_num(c), _num(r)) for n, t, c, r in re.findall(
        r"\|\s*C(\d)\s*\|\s*(24|36)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", _s2)}
    _ops = _root / "Tools" / "NF-Ops" / "config" / "rate-card.json"
    _mirror = json.loads(_ops.read_text())["markets"]["SG"]["mach"] if _ops.exists() else None
    for _m in RENTAL["MACHINES"]:
        assert _m["n"] in _rates, f'{_m["name"]} is not in RATE-CARD.md section 1'
        _m["rate"] = _rates[_m["n"]]
        _m["net_pct"] = {}
        for _t in RENTAL["TERMS_MONTHS"]:
            _cost, _rev = _costs[(_m["n"], _t)]
            # the card's own revenue column must be the rate x the term, or the two tables have drifted
            assert _rev == _m["rate"][_t] * _t, f'RATE-CARD.md: {_m["name"]} {_t} mo revenue {_rev} is not rate x term'
            if _mirror:
                assert _mirror[_m["key"]][f"r{_t}"] == _m["rate"][_t], (
                    f'{_m["name"]} {_t} mo: RATE-CARD.md says {_m["rate"][_t]}, the live site extract says '
                    f'{_mirror[_m["key"]][f"r{_t}"]}. Settle which is right before quoting a partner.')
            _m["net_pct"][_t] = (_rev - _cost - _m["share"] * _t) / _rev * 100
            assert _m["net_pct"][_t] >= RENTAL["MIN_NET_PCT_RENTAL"], (
                f'{_m["name"]} {_t} mo nets {_m["net_pct"][_t]:.1f}% after a {_m["share"]} share, under the '
                f'{RENTAL["MIN_NET_PCT_RENTAL"]}% floor in SG-RENTAL-PARTNER.json.')
    assert RENTAL["TERMS_MONTHS"] == [24, 36], "the rental page is laid out for the 24 and 36 month terms"
    # The coffee fee: checked at both named points of the direct range.
    _fee, _dc = RENTAL["COFFEE_FEE_PER_KG"], RENTAL["DIRECT_COST_PER_KG"]
    _pts = ((LADDER["floor"], LADDER["low"]), (LADDER["opener"], LADDER["full"]))
    # Coffee with no machine behind it has nothing to carry it, so that fee must clear the full 30% rule.
    _fee0 = RENTAL["COFFEE_ONLY_FEE_PER_KG"]
    RENTAL["coffee_only_net"] = {pr: (pr * (1 - rt) - _dc - _fee0) / pr * 100 for pr, rt in _pts}
    for pr, v in RENTAL["coffee_only_net"].items():
        assert v >= CARD["MIN_NET_PCT"], (
            f'Coffee-only at {pr:.2f} nets {v:.1f}% after a {_fee0:.2f} fee, under the {CARD["MIN_NET_PCT"]}% rule.')
    RENTAL["coffee_net"] = {pr: (pr * (1 - rt) - _dc - _fee) / pr * 100 for pr, rt in _pts}
    for pr, v in RENTAL["coffee_net"].items():
        assert v >= RENTAL["MIN_NET_PCT_COFFEE_INTRO"], (
            f'Coffee at {pr:.2f} nets {v:.1f}% after a {_fee:.2f} fee, under the '
            f'{RENTAL["MIN_NET_PCT_COFFEE_INTRO"]}% floor in SG-RENTAL-PARTNER.json.')
    # The worked example printed on the page, and the whole-account margin behind it (never printed).
    _ex = next(m for m in RENTAL["MACHINES"] if m["key"] == RENTAL["EXAMPLE_MACHINE"])
    _exkg = RENTAL["EXAMPLE_KG"]
    EX_EARN = _exkg * _fee + _ex["share"]
    _xc, _xr = _costs[(_ex["n"], 36)]
    RENTAL["account_net"] = {
        pr: (_exkg * (pr * (1 - rt) - _dc - _fee) + (_xr - _xc) / 36 - _ex["share"]) / (_exkg * pr + _xr / 36) * 100
        for pr, rt in _pts}
FAVICON = str(HERE / "nofilter-favicon-v3.svg")

# the two mark paths, lifted verbatim for the seal in the middle of the page-2 roundel
CROSS = re.findall(r'<path[^>]*\sd="([^"]+)"', pathlib.Path(FAVICON).read_text())
assert len(CROSS) == 2

# name, photo, where-lines, blurb, notes, (acidity, body, roast), coord, flag
ORIGINS = [
    dict(
        name="Batang Toru", photo="ph-batang-toru.jpg", seal="seals/nf-seal-batang-toru.svg",
        where=["Sipirok, South Tapanuli &middot; North Sumatra",
               "Forest <b>Batang Toru ecosystem</b> &middot; Partner <b>PRCF Indonesia &middot; SRI</b>",
               "Process <b>Wet-hulled (giling basah)</b>"],
        blurb="The buffer at the edge of Batang Toru, the only place the Tapanuli orangutan "
              "lives. Shade-grown, with farmers paid to keep the forest edge where it is.",
        notes=["Dark chocolate", "Red plum", "Cedar"], certs=[], prof=(3, 3, 4),
        coord="1&deg;38&prime;18&Prime;N<br>99&deg;15&prime;56&Prime;E", flag=None),
    dict(
        name="Batang Gadis", photo="ph-batang-gadis.jpg", seal="seals/nf-seal-batang-gadis.svg",
        where=["Ulu Pungkut, Mandailing Natal &middot; North Sumatra",
               "Forest <b>Batang Gadis National Park buffer</b> &middot; Partner <b>SRI &middot; Komanja</b>",
               "Process <b>Wet-hulled (giling basah)</b>"],
        blurb="The frontier of Batang Gadis National Park, where community-led agroforestry "
              "holds a hard line against clearing at the park's edge.",
        notes=["Brown sugar", "Orange", "Almond"], certs=[], prof=(4, 3, 3),
        coord="0&deg;31&prime;50&Prime;N<br>99&deg;46&prime;28&Prime;E", flag=None),
    dict(
        name="Gayo Lues", photo="ph-gayo-lues.jpg", seal="seals/nf-seal-gayo-lues.svg",
        where=["Agusen, Blangkejeren &middot; Aceh",
               "Forest <b>Leuser Ecosystem edge</b> &middot; Partner <b>OIC</b>",
               "Process <b>Wet-hulled, the Gayo way</b>"],
        blurb="High-grown on the edge of the Leuser Ecosystem, one of the last landscapes where "
              "elephant, tiger, rhinoceros and orangutan still share ground.",
        notes=["Syrupy", "Dried fig", "Cinnamon"], certs=[], prof=(2, 5, 3),
        coord="3&deg;55&prime;N<br>97&deg;22&prime;E", flag=None),
    dict(
        name="Arakan Mountains", photo="ph-arakan.jpg", seal="seals/nf-seal-arakan-mountains.svg",
        where=["Pauk Sa, Magway Region &middot; Myanmar",
               "Forest <b>Mann Wildlife Sanctuary, co-managed</b> &middot; Partner <b>ACCA &middot; Fauna &amp; Flora</b>",
               "Process <b>Honey</b>"],
        blurb="The Asho Chin highlands, where ACCA and Fauna &amp; Flora Myanmar keep the Mann "
              "Wildlife Sanctuary intact. Available subject to supply, which is limited.",
        notes=["Stone fruits", "Candied nuts", "Milk chocolate"],
        certs=["Certified Wildlife Friendly", "PGS Organic"], prof=(3, 4, 3),
        coord="19&deg;48&prime;N<br>94&deg;20&prime;30&Prime;E", flag="Low stock"),
]

ORIGIN_COLOURS = [("Batang Toru", "#2f5d3a"), ("Batang Gadis", "#b8531a"),
                  ("Gayo Lues", "#9c7212"), ("Arakan Mountains", "#1f5661")]

BEHIND = [
    ("Contracted, not charitable",
     "The conservation share is written into the supply contract and shown on every invoice, "
     "so it can be audited rather than taken on trust."),
    ("Mapped to a boundary",
     "Every lot ties to a named forest boundary with coordinates and a named NGO partner, held "
     "on NoFilter's public verification map."),
    ("Documented for reporting",
     "Chain of custody documentation is available for customers carrying Scope 3 or sustainable "
     "procurement obligations."),
    ("Range and formats",
     "Four single-origin roasts with genuinely different cup profiles, supplied in 1 kg whole bean. "
     "Trade pricing, volumes and terms are set out overleaf."),
]


# A partner file may replace one of the four blocks on the bag page: {"2": ["Title", "Text"]} (0-based).
for _i, _v in (CARD.get("BEHIND_OVERRIDE") or {}).items():
    BEHIND[int(_i)] = tuple(_v)


def pips(n):
    return "".join('<i class="pip on"></i>' if i < n else '<i class="pip"></i>' for i in range(5))


def row(o):
    flag = f'<span class="flag">{o["flag"]}</span>' if o["flag"] else ""
    chips = "".join(f'<span class="chip">{n}</span>' for n in o["notes"])
    chips += "".join(f'<span class="chip cert">{c}</span>' for c in o.get("certs", []))
    a, b, r = o["prof"]
    return f"""
  <div class="row">
    <div class="shot"><img class="bag" src="{o['photo']}" alt="{o['name']}">{flag}</div>
    <div>
      <div class="nm">{o['name']}</div>
      <div class="where">{'<br>'.join(o['where'])}</div>
      <p class="blurb">{o['blurb']}</p>
      <div class="chips">{chips}</div>
    </div>
    <div class="prof">
      <div>Acidity <span class="pips">{pips(a)}</span></div>
      <div>Body <span class="pips">{pips(b)}</span></div>
      <div>Roast <span class="pips">{pips(r)}</span></div>
      <div class="coord">{o['coord']}</div>
    </div>
  </div>"""


def slug(x):
    return x.lower().replace(" ", "-")


# The origin stickers as printed: the 40 mm V11 artwork, copied from Drive
# (NoFilter Shared / Brand / Origin_Stickers / NoFilter_Origin_Stickers_40mm_V11, the 600 ppi previews).
# They replaced the drawn seals in seals/ on 6 Oct 2026; if the sticker is revised, replace these four files.
SEALS = "".join(f'<img src="stickers/{slug(n)}.png" alt="{n} sticker">'
                for n, _ in ORIGIN_COLOURS)

def _mar(t):
    pct = f'{t["m_lo"]:.1f}% to {t["m_hi"]:.1f}%'
    if CARD["REBATE_PCT"]:
        return f'<b>{pct}</b>'
    return (f'<b>{CUR} {CARD["RRP_LOW"] - t["net"]:.2f} to {CARD["RRP_HIGH"] - t["net"]:.2f} a bag</b>'
            f' &nbsp;&middot;&nbsp; {pct}')


TIERROWS = "".join(
    f'''<div class="tr{" best" if t is CARD["TIERS"][-1] else ""}">
        <span class="band">{t["band"]}</span>
        <span class="amt"><small>{CUR}</small>{t["list"]:.2f}</span>
        {f'<span class="net">{CUR} {t["net"]:.2f}</span>' if CARD["REBATE_PCT"] else ""}
        <span class="mar">{_mar(t)}</span>
      </div>''' for t in CARD["TIERS"])
# "RETAIL_PACK": true in a partner file adds the 250 g bag and the household shelf prices. The 250 g trade
# price and both household prices live in SG-WHOLESALE.json; the guard below holds the 250 g bag to the
# same 30% rule as the kilo, after the allowance for the smaller bag.
RETAIL = None
if CARD.get("RETAIL_PACK"):
    assert CARD.get("FLAT_PRICE"), "the retail table is laid out for one price per bag size"
    RETAIL = CARD["RETAIL_250G"]
    _k = CARD["TIERS"][0]
    RETAIL["net_pct"] = (RETAIL["trade"] - CARD["CONTRIB_PER_KG"] / 4 - _k["cost"] / 4 - RETAIL["pack_extra"]) / RETAIL["trade"] * 100
    assert RETAIL["net_pct"] >= CARD["MIN_NET_PCT"], (
        f'250 g at {RETAIL["trade"]:.2f} nets {RETAIL["net_pct"]:.1f}%, under the {CARD["MIN_NET_PCT"]}% floor.')
    _h1, _h250 = CARD["RETAIL_RRP_1KG"], CARD["RETAIL_RRP_250G"]
    RETAIL["keep1"] = _h1 - _k["net"]
    RETAIL["keep250"] = _h250 - RETAIL["trade"]
CSS3 = """
/* ---------------- page three: the offer ---------------- */
.p3{display:flex;flex-direction:column;flex:1;padding:0;min-height:0;overflow:hidden}
.p3 .intro{padding:6mm 12mm 4mm}
.ptab{margin:0 12mm 3.5mm;border-top:.7mm solid var(--ink)}
.ptab .hr,.ptab .tr{display:grid;grid-template-columns:44mm 26mm 30mm 1fr;gap:4mm;align-items:baseline}
.ptab .hr{font-family:Plex,monospace;font-size:6.2pt;letter-spacing:.11em;text-transform:uppercase;
          color:var(--dim);padding:2.2mm 0 1.8mm;border-bottom:.35mm solid var(--rule)}
.ptab .tr{padding:3.4mm 0;border-bottom:.35mm solid var(--rule)}
/* the best rung is marked by fill and weight, never by hue */
/* the band is painted behind the row rather than widening it, so every column stays on the same
   grid and the right-hand figures line up across all three rungs */
.ptab .tr{position:relative}
.ptab .tr.best::before{content:"";position:absolute;top:0;bottom:0;left:0;right:0;
                       background:var(--parch)}
.ptab .tr.best>*{position:relative}
.ptab .band{font-family:Plex,monospace;font-size:7.4pt;letter-spacing:.06em;text-transform:uppercase;
            font-weight:600}
.ptab .amt{font-family:Anton,sans-serif;font-size:14pt;line-height:1}
.ptab .amt small{font-family:Plex,monospace;font-size:6pt;letter-spacing:.1em;color:var(--dim);
                 margin-right:1.2mm;vertical-align:.9mm}
.ptab .net{font-family:Archivo,sans-serif;font-size:10.5pt;font-weight:600}
.ptab .mar{font-family:Plex,monospace;font-size:7pt;letter-spacing:.05em;color:var(--dim);
           text-align:right}
.ptab .mar b{color:var(--ink);font-weight:600;font-size:8pt}
.ptabnote{margin:0 12mm 5mm;font-family:Plex,monospace;font-size:6.2pt;letter-spacing:.09em;
          text-transform:uppercase;color:var(--dim);line-height:1.8}

.cards{margin:0 12mm 5mm;display:grid;grid-template-columns:repeat(3,1fr);gap:6mm}
.card{border-top:.7mm solid var(--ink);padding-top:3.2mm}
.card b{display:block;font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.11em;
        text-transform:uppercase;color:var(--forest);margin-bottom:1.6mm;font-weight:600}
.card .big{font-family:Anton,sans-serif;font-size:15pt;line-height:1;margin-bottom:1.8mm}
.card p{font-size:7.7pt;line-height:1.45;color:#3a3b39}

.terms{margin:auto 12mm 6mm;display:grid;grid-template-columns:1fr 1fr;gap:0 9mm;align-content:start}
.tm{border-top:.4mm solid var(--rule);padding:2.1mm 0}
.tm:nth-of-type(1),.tm:nth-of-type(2){border-top:.7mm solid var(--ink)}
.tm b{display:block;font-family:Plex,monospace;font-size:6.3pt;letter-spacing:.11em;
      text-transform:uppercase;color:var(--dim);margin-bottom:.9mm;font-weight:600}
.tm p{font-size:8pt;line-height:1.42;color:#3a3b39}

/* the closing band repeats page two's, pushed to the foot of the page */
.p3 .next{margin:auto 12mm 3mm;background:var(--parch);padding:3.8mm 6mm;display:flex;
          justify-content:space-between;align-items:flex-end;gap:8mm}
.p3 .next h3{font-family:Anton,sans-serif;font-weight:400;font-size:11pt;
             text-transform:uppercase;margin-bottom:2mm}
.p3 .next p{font-size:8.2pt;line-height:1.45;max-width:112mm;color:#3a3b39}
/* ---------------- page four: acceptance ---------------- */
.p4{display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden}
.p4 .intro{padding:7mm 12mm 5mm}
.recap{margin:0 12mm;border-top:.7mm solid var(--ink)}
.recap .rr{display:grid;grid-template-columns:46mm 1fr;gap:7mm;padding:4.2mm 0;
           border-bottom:.35mm solid var(--rule)}
.recap .rk{font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.11em;text-transform:uppercase;
           color:var(--dim);font-weight:600;line-height:1.5}
.recap .rv{font-size:8.4pt;line-height:1.45;color:#3a3b39}
.recap .rv b{font-weight:600;color:var(--ink)}
.signbox{margin:auto 12mm 9mm;display:grid;grid-template-columns:1fr 1fr;gap:11mm}
.sb{border:.5mm solid var(--ink);padding:6mm 7mm 7mm}
.sb h4{font-family:Anton,sans-serif;font-weight:400;font-size:11pt;text-transform:uppercase;
       margin-bottom:11mm}
.sl{margin-bottom:9mm}
.sl:last-child{margin-bottom:0}
.sl .rule{border-bottom:.35mm solid var(--ink);height:12mm}
.sl span{display:block;margin-top:2mm;font-family:Plex,monospace;font-size:6.2pt;
         letter-spacing:.1em;text-transform:uppercase;color:var(--dim)}
.p3 .next .who{font-family:Plex,monospace;font-size:6.8pt;letter-spacing:.1em;
               text-transform:uppercase;color:var(--forest);text-align:right;
               line-height:1.9;white-space:nowrap}
"""
CSSR = """
/* ---------------- rental page (only for a partner with RENTAL) ---------------- */
.pr{display:flex;flex-direction:column;flex:1;padding:0;min-height:0;overflow:hidden}
.pr .intro{padding:6mm 12mm 4mm}
.mtab{margin:0 12mm 3mm;border-top:.7mm solid var(--ink)}
.mtab .hr,.mtab .mr{display:grid;grid-template-columns:17mm 1fr 25mm 25mm 30mm 27mm;gap:4mm;align-items:center}
.mtab .hr{font-family:Plex,monospace;font-size:6.2pt;letter-spacing:.11em;text-transform:uppercase;
          color:var(--dim);padding:2.2mm 0 1.8mm;border-bottom:.35mm solid var(--rule);align-items:end;
          line-height:1.5}
.mtab .hr span.r,.mtab .mr .r{text-align:right}
.mtab .mr{padding:1.2mm 0;border-bottom:.35mm solid var(--rule)}
.mtab .ph{width:17mm;height:17mm;object-fit:cover;display:block}
.mtab .mn{font-family:Anton,sans-serif;font-size:12.5pt;line-height:1;text-transform:uppercase;
          margin-bottom:1.3mm}
.mtab .ms{font-family:Plex,monospace;font-size:6.3pt;letter-spacing:.07em;text-transform:uppercase;
          color:var(--dim);line-height:1.5}
.mtab .rt{font-family:Archivo,sans-serif;font-size:10.5pt;font-weight:600}
.mtab .rt small,.mtab .sh small{font-family:Plex,monospace;font-size:6pt;letter-spacing:.1em;
          color:var(--dim);margin-right:1.2mm;font-weight:400}
/* the partner's own column is marked by fill and weight, never by hue */
.mtab .sh{font-family:Anton,sans-serif;font-size:14pt;line-height:1;background:var(--parch);
          padding:3.2mm 2.5mm;text-align:right}
.mtab .sh small{vertical-align:.9mm}
.mtab .tot{font-family:Plex,monospace;font-size:7.6pt;letter-spacing:.05em;font-weight:600}
.mtabnote{margin:0 12mm 3.5mm;font-family:Plex,monospace;font-size:6.2pt;letter-spacing:.09em;
          text-transform:uppercase;color:var(--dim);line-height:1.8}
.pr .cards{margin:0 12mm 4.5mm}
.pr .terms{margin:auto 12mm 5mm}
.pr .tm{padding:1.4mm 0}
.pr .tm p{font-size:7.8pt;line-height:1.4}
"""
PAGER = ""
RECAP_R = ""
PAGES_WORD = "four"
if RENTAL:
    SHARE_FREQ = RENTAL["SHARE_FREQUENCY"] + (", with the marketing rebate" if CARD["REBATE_PCT"] else "")
    CSS3 += CSSR
    PAGES_WORD = "five"
    _sh = [m["share"] for m in RENTAL["MACHINES"]]
    _t_lo, _t_hi = RENTAL["TERMS_MONTHS"]
    MROWS = "".join(
        f'''<div class="mr">
        <img class="ph" src="{m["photo"]}" alt="{m["name"]}">
        <div><div class="mn">{m["name"]}</div><div class="ms">{m["suits"]}</div></div>
        <span class="rt r"><small>{CUR}</small>{m["rate"][_t_lo]:,}</span>
        <span class="rt r"><small>{CUR}</small>{m["rate"][_t_hi]:,}</span>
        <span class="sh"><small>{CUR}</small>{m["share"]:,}</span>
        <span class="tot r">{CUR} {m["share"] * _t_hi:,}</span>
      </div>''' for m in RENTAL["MACHINES"])
    _fee_s = f'{CUR}&nbsp;{RENTAL["COFFEE_FEE_PER_KG"]:.2f}'
    RECAP_R = (f'''
      <div class="rr"><div class="rk">Introductions</div><div class="rv"><b>{CUR} {RENTAL["COFFEE_FEE_PER_KG"]:.2f} per kilogram of coffee and {CUR} {min(_sh)} to {max(_sh)} per machine per month</b>, on every client you introduce who contracts with NoFilter, for {RENTAL["FEE_TERM"]}; {CUR} {RENTAL["COFFEE_ONLY_FEE_PER_KG"]:.2f} per kilogram for {RENTAL["COFFEE_ONLY_MONTHS"]} months where the client takes coffee only. Paid {SHARE_FREQ}, and fees on clients already signed continue if this agreement ends</div></div>''')
    PAGER = f'''

<!-- ============ introductions page: the partner introduces, NoFilter contracts ============ -->
<div class="page">
  <div class="pr">
    <div class="head">
      <div class="lock"><img class="nf" src="wordmark.png" alt="NoFilter">
        <span class="x">&times;</span>{LOCK}</div>
      <div class="meta">INTRODUCTIONS<br>{CARD["MARKET"].upper()}<br>VALID TO {CARD["VALID_TO_TEXT"].upper()}</div>
    </div>

    <div class="intro">
      <div class="kicker">CLIENT INTRODUCTIONS &middot; MACHINE AND COFFEE &middot; {_t_lo} OR {_t_hi} MONTHS</div>
      <h1>Introduce the client.<br>Earn on <em>every kilo</em>.</h1>
      <p class="lede">Some of the offices, hotels and restaurants you deliver to will want more than bags: a
      machine on site and coffee on standing supply. Introduce them, and NoFilter contracts with them directly for
      both, with the machine financed through {RENTAL["FINANCE_PARTNER"]}. You carry no stock, no lease, no
      credit risk and no servicing, and you earn a fixed amount on every kilo they buy and on every
      machine they rent, for {RENTAL["FEE_TERM"]}.</p>
    </div>

    <div class="mtab">
      <div class="hr"><span></span><span>Machine</span><span class="r">Client pays<br>{_t_lo} months</span><span class="r">Client pays<br>{_t_hi} months</span><span class="r">Your share<br>per month</span><span class="r">Your share over<br>{_t_hi} months</span></div>
      {MROWS}
    </div>
    <div class="mtabnote">Rental per machine per month, before GST, at NoFilter&rsquo;s published {CARD["MARKET"]}
      rates &middot; your share is the same on either term &middot; a client on one {_ex["name"]} taking
      {_exkg} kg a month earns you {CUR} {EX_EARN:,.0f} a month, or {CUR} {EX_EARN * _t_hi:,.0f} over {_t_hi} months</div>

    <div class="cards">
      <div class="card"><b>On the coffee</b>
        <div class="big">{_fee_s} a kilo</div>
        <p>On every kilogram NoFilter supplies to a client you introduce, whatever price the client
        chooses.</p></div>
      <div class="card"><b>On the machine</b>
        <div class="big">{CUR}&nbsp;{min(_sh)}&ndash;{max(_sh)} a month</div>
        <p>A fixed amount by model, shown above, for every month the rental is in place and paid.</p></div>
      <div class="card"><b>What your client gets</b>
        <div class="big">One monthly figure</div>
        <p>The machine, installation, a milk cooler, a co-branded wrap and servicing, with a live
        impact screen on site. Nothing is quoted separately.</p></div>
    </div>

    <div class="terms">
      <div class="tm"><b>Who contracts</b><p>NoFilter contracts with your client directly for the machine and the coffee, on its standard agreement, for {_t_lo} or {_t_hi} months. The client pays NoFilter or {RENTAL["FINANCE_PARTNER"]}, never you.</p></div>
      <div class="tm"><b>The client&rsquo;s price</b><p>The client chooses their own coffee price, from {CUR} {LADDER["floor"]:.0f} to {LADDER["ceil"]:.0f} a kilo, and pays the same published machine rates as any NoFilter client. Each agreement is subject to credit approval and to our acceptance of the site.</p></div>
      <div class="tm"><b>Introductions</b><p>A client is yours once you have named them to us in writing and we have confirmed they are not already a NoFilter account or a live enquiry. Fees on a client already signed continue if this agreement ends.</p></div>
      <div class="tm"><b>What you earn</b><p>{CUR} {RENTAL["COFFEE_FEE_PER_KG"]:.2f} on every kilogram of coffee supplied and the monthly amount shown for each machine, for {RENTAL["FEE_TERM"]}. Where a client has its own machine and takes coffee only, {CUR} {RENTAL["COFFEE_ONLY_FEE_PER_KG"]:.2f} a kilogram for {RENTAL["COFFEE_ONLY_MONTHS"]} months.</p></div>
      <div class="tm"><b>When it is paid</b><p>{SHARE_FREQ[0].upper() + SHARE_FREQ[1:]}, with a statement of the kilos supplied and the machines in place. It is paid on what the client has paid us.</p></div>
      <div class="tm"><b>Two routes</b><p>Where a client contracts with NoFilter, we supply them under this page. Everything else you sell is yours to price and invoice, on the wholesale terms on the previous page.</p></div>
    </div>

  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>'''
# ---------------------------------------------------------------------------------------------
# A partner on no marketing rebate ("REBATE_PCT": 0 in the partner file). The net-of-rebate column,
# the rebate card and the rebate row on the acceptance page all go, and the margin column is then
# simply the shelf price against the list price. With a rebate, every string below is exactly the
# markup this file has always produced.
# ---------------------------------------------------------------------------------------------
if CARD["REBATE_PCT"]:
    PTAB_CLS = CARDS_CLS = ""
    NET_HEAD = "<span>Net of rebate</span>"
    CARD_REBATE = f'''<div class="card"><b>Marketing rebate</b>
        <div class="big">{CARD["REBATE_PCT"]}%</div>
        <p>Of invoiced value, paid {CARD["REBATE_FREQUENCY"]}, against {CARD["REBATE_EARNED_BY"]}. Calculated on {CARD["REBATE_BASIS"]}.</p></div>'''
    RECAP_REBATE = f'''      <div class="rr"><div class="rk">Marketing rebate</div><div class="rv"><b>{CARD["REBATE_PCT"]}%</b> of invoiced value, paid {CARD["REBATE_FREQUENCY"]}</div></div>
'''
else:
    PTAB_CLS, NET_HEAD, RECAP_REBATE = " norb", "", ""
    CSS3 += """.ptab.norb .hr,.ptab.norb .tr{grid-template-columns:30mm 26mm 1fr}
.ptab.norb .mar{line-height:1.9}
.cards.two{grid-template-columns:repeat(2,1fr)}
"""
    if RENTAL:
        CARDS_CLS = ""
        CARD_REBATE = f'''<div class="card"><b>Introduce a client</b>
        <div class="big">{_fee_s} a kilo</div>
        <p>Plus {CUR}&nbsp;{min(_sh)} to {max(_sh)} a month per machine, where a business you deliver to
        takes a machine and its coffee from NoFilter directly. Set out overleaf.</p></div>'''
    else:
        CARDS_CLS, CARD_REBATE = " two", ""
# ---------------------------------------------------------------------------------------------
# Photographic cover ("COVER": true in the partner file), in the style of the Accenture contract and
# the Brand Ambassador pack: full-bleed farm photograph, white lockup, title at the foot.
# ---------------------------------------------------------------------------------------------
COVER_PAGE = ""
if CARD.get("COVER"):
    PAGES_WORD = {"four": "five", "five": "six"}[PAGES_WORD]
    CSS3 += """
/* ---------------- cover ---------------- */
.cv{position:relative;flex:1;background:#1c1f1c;color:#fff;overflow:hidden}
.cv img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
/* the shade carries the legibility of the type; contrast is by lightness, not hue */
.cv .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.42) 0%,
           rgba(0,0,0,.05) 24%,rgba(0,0,0,.05) 46%,rgba(0,0,0,.72) 70%,rgba(0,0,0,.9) 100%)}
.cv .top{position:absolute;left:14mm;top:13mm}
.cv .lock img.nf{height:12mm}
.cv .lock img.ly{height:24mm}
.cv .lock .x{font-size:16pt}
.cv .bot{position:absolute;left:14mm;right:14mm;bottom:11mm}
.cv .kick{font-family:Plex,monospace;font-weight:600;font-size:7pt;letter-spacing:.2em;
          text-transform:uppercase;color:#F27126;margin-bottom:3mm}
.cv h1{font-family:Anton,sans-serif;font-weight:400;font-size:43pt;line-height:1;text-transform:uppercase;
       margin-bottom:3mm;color:#fff}
.cv .sub{font-family:Anton,sans-serif;font-size:18pt;line-height:1;text-transform:uppercase;
         color:#F27126;margin-bottom:8mm}
.cv .who{font-size:9pt;line-height:1.75;margin-bottom:5mm}
.cv .rule{border-top:.35mm solid rgba(255,255,255,.75);padding-top:3mm;display:flex;
          justify-content:space-between;font-family:Plex,monospace;font-size:6.6pt;letter-spacing:.12em;
          text-transform:uppercase}
"""
    COVER_PAGE = f'''
<!-- ============ cover ============ -->
<div class="page">
  <div class="cv">
    <img class="bg" src="cover-photo.jpg" alt="">
    <div class="shade"></div>
    <div class="top"><div class="lock"><img class="nf" src="wordmark.png" alt="NoFilter">
      <span class="x">&times;</span>{LOCK}</div></div>
    <div class="bot">
      <div class="kick">{CARD["COVER_KICKER"]}</div>
      <h1>{CARD["COVER_TITLE"]}</h1>
      <div class="sub">{CARD["COVER_SUB"]}</div>
      <div class="who">For: {_html.escape(CARD.get("PREPARED_FOR") or CARD["PARTNER_NAME"])}<br>Prepared by {CARD["NF_ENTITY_NAME"]}</div>
      <div class="rule"><span>{BRIEF_DATE} &nbsp;/&nbsp; Valid to {CARD["VALID_TO_TEXT"]}</span><span>nofilter.sg</span></div>
    </div>
  </div>
</div>
'''
# ---------------------------------------------------------------------------------------------
# Wording that depends on the kind of offer. Each default is the sentence this file has always
# produced, so a partner that sets none of the keys below builds exactly as before.
#   "PROPOSAL": true      the document calls itself a proposal that becomes the agreement on signature
#   "VALID_LEAD": "To"    for a brief issued part-way through the term, where "twelve months" is untrue
#   "FLAT_PRICE": true    one price at any volume (see the top of this file)
#   "FIRST_ORDER_KG": n   a smaller first order than the standing minimum
# ---------------------------------------------------------------------------------------------
DOC_LABEL = "Partner proposal" if CARD.get("PROPOSAL") else "Partner brief"
VALID_LEAD = CARD.get("VALID_LEAD") or "Twelve months to"
HOLD_WORDS = f'hold to {CARD["VALID_TO_TEXT"]}' if CARD.get("VALID_LEAD") else "hold for twelve months"
MOQ_EXTRA = f' Your first order can be {CARD["FIRST_ORDER_KG"]} kg.' if CARD.get("FIRST_ORDER_KG") else ""
W_VOLHEAD, W_MARHEAD, FOREST_LEAD = "Annual volume bought", "Your margin at", "The same on every tier"
W_PRICEHEAD = "Per kg"
RRP_CARD = f'''<div class="card"><b>Recommended shelf price</b>
        <div class="big">{CUR}&nbsp;{CARD["RRP_LOW"]}&ndash;{CARD["RRP_HIGH"]}</div>
        <p>A recommendation, not a condition; the price you set is yours. The margins shown in the
        table are calculated against this band.</p></div>'''
W_LEDE = f'''These prices hold for twelve months, delivered to {CARD["DELIVERY_SHORT"]}. They
      are set so that a listing at the recommended shelf price returns you a normal trade margin without
      NoFilter cutting the share that goes back to the forest. In the first year the rate is settled on
      what you actually buy rather than on a forecast: pass a threshold and we credit the difference back
      across everything you have bought, so there is nothing to commit to up front.'''
W_NOTE = f'''First year invoiced at the entry rate, with any tier credit applied at twelve
      months, see tier review &middot; minimum order {CARD["MOQ_KG"]} kg &middot; delivery included'''
W_TIERTERM = '''<div class="tm"><b>Tier review</b><p>Year one is invoiced at the entry rate. Pass a threshold over the twelve months and the better rate applies to everything bought, with the difference credited. From year two the tier is set in advance on the preceding year.</p></div>'''
RECAP_TRADE = "" if CARD.get("FLAT_PRICE") else f'''<div class="rr"><div class="rk">Trade price</div><div class="rv"><b>{CUR} {CARD["TIERS"][0]["list"]:.2f}, {CARD["TIERS"][1]["list"]:.2f} and {CARD["TIERS"][2]["list"]:.2f} per kg</b>, by annual volume bought, with any year-one tier credit applied at twelve months</div></div>'''
ACCEPT_LEDE = f'''These {PAGES_WORD} pages are the supply agreement. Signing this page puts the pricing and
      terms set out overleaf into effect for the validity period and replaces anything discussed before
      it. Nothing here commits {CARD["PARTNER_NAME"]} to a volume.'''
if not CARD["REBATE_PCT"]:
    W_MARHEAD = "What you keep at"
if CARD.get("FLAT_PRICE"):
    _t0 = CARD["TIERS"][0]
    W_VOLHEAD, FOREST_LEAD = "Volume", "On every kilo"
    W_LEDE = (f'This price holds to {CARD["VALID_TO_TEXT"]}, delivered to {CARD["DELIVERY_SHORT"]}. At the '
              f'recommended shelf price a 1 kg bag leaves you {CUR} {CARD["RRP_LOW"] - _t0["net"]:.2f} to '
              f'{CARD["RRP_HIGH"] - _t0["net"]:.2f}, with nothing to chill and nothing to throw away, and NoFilter '
              f'does not cut the share that goes back to the forest to get there. There is no volume to commit to. '
              f'We review the price together when the term ends, on what you have bought.')
    W_NOTE = (f'One price at any volume &middot; minimum order {CARD["MOQ_KG"]} kg'
              + (f', first order {CARD["FIRST_ORDER_KG"]} kg' if CARD.get("FIRST_ORDER_KG") else "")
              + ' &middot; delivery included')
    W_TIERTERM = ('<div class="tm"><b>Review</b><p>One price at any volume for this term. We review it together '
                  'when the term ends, on the volume you have bought.</p></div>')
    RECAP_TRADE = (f'<div class="rr"><div class="rk">Trade price</div><div class="rv"><b>{CUR} {_t0["list"]:.2f} per kg</b>'
                   f' at any volume, reviewed together when the term ends</div></div>')
W_MARCELL = f'{W_MARHEAD} {CUR}&nbsp;{CARD["RRP_LOW"]}&ndash;{CARD["RRP_HIGH"]}'
PTAB = f'''<div class="ptab{PTAB_CLS}">
      <div class="hr"><span>{W_VOLHEAD}</span><span>{W_PRICEHEAD}</span>{NET_HEAD}<span style="text-align:right">{W_MARCELL}</span></div>
      {TIERROWS}
    </div>'''
if RETAIL:
    # One row per place the bag is sold, each figure in its own column. The partner's own column is
    # marked by fill, as on the introductions page, never by hue.
    _k = CARD["TIERS"][0]
    _h1, _h250 = CARD["RETAIL_RRP_1KG"], CARD["RETAIL_RRP_250G"]
    _b_lo, _b_hi = CARD["RRP_LOW"], CARD["RRP_HIGH"]

    def _panel(kick, bag, who, trade, shelf, keep, pct, unit, foot):
        return (f'<div class="pp"><div class="pk">{kick}</div><div class="pb">{bag}</div><p class="pw">{who}</p>'
                f'<div class="pl"><span>You pay NoFilter</span><b>{CUR} {trade:.2f}</b></div>'
                f'<div class="pl"><span>Recommended selling price</span><b>{CUR} {shelf}</b></div>'
                f'<div class="pl keep"><span>You keep, {unit}<i>{pct} margin</i></span><b>{CUR} {keep}</b></div>'
                f'<p class="pf">{foot}</p></div>')
    PTAB = ('<div class="duo">'
            + _panel("Retail &middot; households", "250 g bag",
                     "For private buyers, through your shop and your boxes.",
                     RETAIL["trade"], f"{_h250}", f'{RETAIL["keep250"]:.2f}',
                     f'{RETAIL["keep250"] / _h250 * 100:.1f}%', "per bag",
                     'The selling price matches nofilter.sg. Retail sale to households is in 250 g bags only.')
            + _panel("Wholesale &middot; businesses", "1 kg bag",
                     "For the offices, hotels and restaurants you already deliver to.",
                     _k["list"], f"{_b_lo}&ndash;{_b_hi}", f'{_b_lo - _k["net"]:.2f} to {_b_hi - _k["net"]:.2f}',
                     f'{_k["m_lo"]:.1f}% to {_k["m_hi"]:.1f}%', "per kilo",
                     'The selling price is a recommendation, not a condition. What you charge your customers is yours to set.')
            + '</div>')
    CSS3 += """.duo{margin:0 12mm 3mm;display:grid;grid-template-columns:1fr 1fr;gap:8mm}
.pp{border-top:.7mm solid var(--ink);padding-top:3mm}
.pk{font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.11em;text-transform:uppercase;color:var(--forest);font-weight:600}
.pb{font-family:Anton,sans-serif;font-size:21pt;line-height:1;margin:1.6mm 0 1.4mm;text-transform:uppercase}
.pw{font-size:8pt;line-height:1.4;color:#3a3b39;margin-bottom:2mm}
.pl{display:flex;justify-content:space-between;align-items:center;padding:2.3mm 0;border-top:.35mm solid var(--rule);font-size:8.4pt}
.pl b{font-family:Archivo,sans-serif;font-size:11pt;font-weight:600;white-space:nowrap}
.pl.keep{background:var(--parch);border-top:none;padding:2.8mm 3mm;margin-top:.6mm}
.pl.keep span{font-weight:600}
.pl.keep i{display:block;font-style:normal;font-weight:400;font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.05em;color:var(--dim);margin-top:.8mm}
.pl.keep b{font-family:Anton,sans-serif;font-size:15pt;font-weight:400}
.pf{font-size:7.3pt;line-height:1.45;color:#3a3b39;margin-top:2.2mm}
.p3 .duo ~ .cards{margin-top:1.5mm}
"""
    CARDS_CLS, RRP_CARD = " two", ""
    W_LEDE = (f'These prices hold to {CARD["VALID_TO_TEXT"]}, delivered to {CARD["DELIVERY_SHORT"]}. There is nothing '
              f'to chill, nothing to throw away and no volume to commit to. We review the prices together when the '
              f'term ends, on what you have bought.')
    W_NOTE = (W_NOTE.replace("One price at any volume", "One price per bag size at any volume")
)
    W_TIERTERM = W_TIERTERM.replace("One price at any volume", "One price per bag size at any volume")
    RECAP_TRADE = (f'<div class="rr"><div class="rk">Trade price</div><div class="rv"><b>{CUR} {CARD["TIERS"][0]["list"]:.2f} per 1 kg bag for business customers and '
                   f'{CUR} {RETAIL["trade"]:.2f} per 250 g bag for retail sale</b>, at any volume, reviewed together when the term ends</div></div>')
# "PRICES_EX_GST": true states on the wholesale page that every price is before GST.
if CARD.get("PRICES_EX_GST"):
    W_NOTE = W_NOTE.replace(" &middot; delivery included", " &middot; delivery included &middot; all prices exclude GST", 1)
if CARD.get("PROPOSAL"):
    ACCEPT_LEDE = (f'This proposal becomes the supply agreement when both parties sign this page. Signing puts the '
                   f'pricing and terms in these {PAGES_WORD} pages into effect to {CARD["VALID_TO_TEXT"]} and replaces '
                   f'anything discussed before it. Nothing here commits {CARD["PARTNER_NAME"]} to a volume.')
# A partner with no logo file gets its name set in type; the rule ships only when it is needed.
if 'class="lyword"' in LOCK:
    CSS3 += """.lock .lyword{font-family:Anton,sans-serif;font-size:17pt;line-height:1;color:#fff;
             text-transform:uppercase;letter-spacing:.02em}
"""
PAGE4 = f'''
<!-- ============ page 4: acceptance ============ -->
<div class="page">
  <div class="p4">
    <div class="head">
      <div class="lock"><img class="nf" src="wordmark.png" alt="NoFilter">
        <span class="x">&times;</span>{LOCK}</div>
      <div class="meta">ACCEPTANCE<br>{CARD["MARKET"].upper()}<br>VALID TO {CARD["VALID_TO_TEXT"].upper()}</div>
    </div>

    <div class="intro">
      <div class="kicker">SIGN AND RETURN &middot; ONE PAGE</div>
      <h1>Agreed and <em>accepted</em>.</h1>
      <p class="lede">{ACCEPT_LEDE}</p>
    </div>

    <div class="recap">
      {RECAP_TRADE}
{RECAP_REBATE}      <div class="rr"><div class="rk">To the forest</div><div class="rv"><b>{CUR} {CARD["CONTRIB_PER_KG"]:.2f} per kilogram</b>, {FOREST_LEAD[0].lower() + FOREST_LEAD[1:]}, contracted and shown on the invoice</div></div>{RECAP_R}
      <div class="rr"><div class="rk">Territory</div><div class="rv">{CARD["MARKET"]}, non-exclusive</div></div>
      <div class="rr"><div class="rk">Term and notice</div><div class="rv">Runs to {CARD["VALID_TO_TEXT"]}. Either party may end it earlier on <b>{CARD["TERM_NOTICE_DAYS"]} days&rsquo; written notice</b>, with orders already accepted honoured</div></div>
      <div class="rr"><div class="rk">Governing law</div><div class="rv">{CARD["GOVERNING_LAW"]}</div></div>
    </div>

    <div class="signbox">
      <div class="sb">
        <h4>For {CARD["NF_ENTITY_NAME"]}</h4>
        <div class="sl"><div class="rule"></div><span>Signature</span></div>
        <div class="sl"><div class="rule"></div><span>{CARD["NF_SIGNATORY"]}</span></div>
        <div class="sl"><div class="rule"></div><span>Date</span></div>
      </div>
      <div class="sb">
        <h4>For {CARD["PARTNER_LEGAL"]}</h4>
        <div class="sl"><div class="rule"></div><span>Signature</span></div>
        <div class="sl"><div class="rule"></div><span>{CARD["SIGNATORY"]}</span></div>
        <div class="sl"><div class="rule"></div><span>Date</span></div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>
'''
PAGE3 = f'''
<!-- ============ page 3: the offer ============ -->
<div class="page">
  <div class="p3">
    <div class="head">
      <div class="lock"><img class="nf" src="wordmark.png" alt="NoFilter">
        <span class="x">&times;</span>{LOCK}</div>
      <div class="meta">WHOLESALE OFFER<br>{CARD["MARKET"].upper()}<br>VALID TO {CARD["VALID_TO_TEXT"].upper()}</div>
    </div>

    <div class="intro">
      <div class="kicker">TRADE PRICING &middot; {CARD["FORMAT"].upper()} &middot; ALL FOUR ORIGINS AT ONE PRICE</div>
      <h1>A price that leaves room<br>for <em>both of us</em>.</h1>
      <p class="lede">{W_LEDE}</p>
    </div>

    {PTAB}
    <div class="ptabnote">{W_NOTE}</div>

    <div class="cards{CARDS_CLS}">
      {CARD_REBATE}
      <div class="card"><b>To the forest, per kilo</b>
        <div class="big">{CUR}&nbsp;{CARD["CONTRIB_PER_KG"]:.2f}</div>
        <p>{FOREST_LEAD}, contracted and shown on the invoice. Your customer gets a figure for
        their own reporting, and you get a listing that answers a procurement question instead of raising
        one.</p></div>
      {RRP_CARD}
    </div>

    <div class="terms">
      <div class="tm"><b>Format</b><p>{CARD["FORMAT"]}. All four origins at the same price, ordered in any mix.{CARD.get("FORMAT_NOTE", "")}</p></div>
      <div class="tm"><b>Minimum order</b><p>{CARD["MOQ_KG"]} kg per delivery, any combination of origins.{MOQ_EXTRA}</p></div>
      {W_TIERTERM}
      <div class="tm"><b>Delivery</b><p>Included, to {CARD["DELIVERY_POINT"]}. Title and risk pass on delivery.</p></div>
      <div class="tm"><b>Territory</b><p>{CARD["MARKET"]}, non-exclusive.{CARD["TERRITORY_NOTE"]}</p></div>
      <div class="tm"><b>Roasting and delivery</b><p>Roasted to order. Orders placed by {CARD["ORDER_CUTOFF"]} are roasted the following {CARD["ROAST_DAYS"]} and delivered to your warehouse on {CARD["DELIVERY_DAYS"]}. Anything later falls into the next week&rsquo;s roast.</p></div>
      <div class="tm"><b>Payment</b><p>Coffee is {CARD["INVOICING"]}, payable {CARD["PAYMENT_DAYS"]} days from invoice.</p></div>
      <div class="tm"><b>Price validity</b><p>{VALID_LEAD} {CARD["VALID_TO_TEXT"]}, adjustable on 30 days&rsquo; notice only if landed green coffee moves more than {CARD["GREEN_TRIGGER_PCT"]}%.</p></div>
      <div class="tm"><b>Stock</b><p>Rotation is yours once delivered and the roast date is printed on every bag. Coffee is not returnable on age.</p></div>
      <div class="tm"><b>Conservation claims</b><p>Approved wording is supplied and may not be varied without our written agreement.</p></div>
    </div>

  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>
'''

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>NoFilter &times; {CARD["PARTNER_NAME"]} — Wholesale Supply Agreement</title>
<style>
@font-face{{font-family:Anton;src:url(f/anton.woff2) format('woff2');font-weight:400}}
@font-face{{font-family:Archivo;src:url(f/archivo400.woff2) format('woff2');font-weight:400}}
@font-face{{font-family:Archivo;src:url(f/archivo600.woff2) format('woff2');font-weight:600}}
@font-face{{font-family:Plex;src:url(f/plex400.woff2) format('woff2');font-weight:400}}
@font-face{{font-family:Plex;src:url(f/plex600.woff2) format('woff2');font-weight:600}}

:root{{--ink:#2A2B2A;--orange:{ACCENT};--parch:#FFE8C3;--forest:#1B3A2D;
       --rule:#d9d3c6;--dim:#6d6f6b}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Archivo,sans-serif;color:var(--ink);background:#fff;
      -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:210mm;height:297mm;display:flex;flex-direction:column;overflow:hidden;
       page-break-after:always}}
.page:last-child{{page-break-after:auto}}

/* fixed band so a partner lockup of any shape cannot change the page height */
.head{{background:var(--orange);height:25.4mm;flex:none;padding:0 12mm;display:flex;
       align-items:center;justify-content:space-between;gap:10mm}}
.lock{{display:flex;align-items:center;gap:6mm}}
.lock img.nf{{height:9mm;display:block}}
.lock img.ly{{height:{CARD["LOGO_HEIGHT_MM"]}mm;display:block}}
.lock .x{{font-family:Archivo,sans-serif;font-weight:600;font-size:13pt;color:#fff;opacity:.85}}
.meta{{font-family:Plex,monospace;font-size:7pt;letter-spacing:.14em;text-transform:uppercase;
       color:#fff;text-align:right;line-height:1.7}}

.intro{{padding:6mm 12mm 4mm}}
.kicker{{font-family:Plex,monospace;font-size:6.8pt;letter-spacing:.2em;text-transform:uppercase;
         color:var(--dim);margin-bottom:2.5mm}}
h1{{font-family:Anton,sans-serif;font-weight:400;font-size:22.5pt;line-height:1.02;
    text-transform:uppercase;margin-bottom:3mm}}
h1 em{{font-style:normal;color:var(--orange)}}
.lede{{font-size:9pt;line-height:1.48;max-width:152mm;color:#3a3b39}}

.rows{{padding:0 12mm;flex:1}}
.row{{display:grid;grid-template-columns:24mm 1fr 34mm;gap:6mm;align-items:start;
      padding:5.4mm 0;border-top:.4mm solid var(--rule)}}
.row:first-child{{border-top:.7mm solid var(--ink)}}
.shot{{position:relative;width:24mm}}
.bag{{width:24mm;height:34mm;object-fit:cover;display:block}}
.flag{{position:absolute;left:0;bottom:0;background:var(--orange);color:#fff;
       font-family:Plex,monospace;font-weight:600;font-size:6pt;letter-spacing:.12em;
       text-transform:uppercase;padding:1mm 1.8mm}}

.nm{{font-family:Anton,sans-serif;font-size:13pt;line-height:1;text-transform:uppercase;
     margin-bottom:1.4mm}}
.where{{font-family:Plex,monospace;font-size:6.5pt;letter-spacing:.08em;text-transform:uppercase;
        color:var(--dim);line-height:1.7;margin-bottom:2.2mm}}
.where b{{color:var(--ink);font-weight:600}}
.blurb{{font-size:8.1pt;line-height:1.4;color:#3a3b39;margin-bottom:2.2mm;max-width:96mm}}
.chips{{display:flex;gap:1.6mm;flex-wrap:wrap}}
.chip{{font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.07em;text-transform:uppercase;
       border:.35mm solid var(--ink);padding:.8mm 1.8mm;border-radius:.8mm}}
/* credentials are solid rather than outlined, so they separate from flavour by
   fill and not by colour */
.chip.cert{{background:var(--ink);color:#fff;font-weight:600}}

/* profile scales read as filled/empty blocks, never by colour alone */
.prof{{font-family:Plex,monospace;font-size:6.2pt;letter-spacing:.1em;text-transform:uppercase;
       color:var(--dim)}}
.prof div{{display:flex;align-items:center;justify-content:space-between;gap:2mm;margin-bottom:1.5mm}}
.pips{{display:flex;gap:.9mm}}
.pip{{width:2.5mm;height:2.5mm;border:.35mm solid var(--ink);border-radius:.4mm}}
.pip.on{{background:var(--ink)}}
.coord{{font-family:Plex,monospace;font-size:6pt;letter-spacing:.06em;color:var(--dim);
        margin-top:2mm;padding-top:1.8mm;border-top:.35mm solid var(--rule);line-height:1.6}}

.foot{{padding:4mm 12mm;display:flex;justify-content:space-between;align-items:baseline;
       border-top:.7mm solid var(--ink);font-family:Plex,monospace;font-size:7pt;
       letter-spacing:.1em;text-transform:uppercase}}
.foot span{{color:var(--dim)}}
.foot b{{font-weight:600}}

/* ---------------- page two ---------------- */
.p2{{display:flex;flex-direction:column;flex:1}}
.p2 .upper{{height:168mm;display:grid;grid-template-columns:100mm 1fr}}
.p2 .lower{{flex:1;padding:9mm 12mm 0 10mm;display:grid;grid-template-columns:1fr 1fr;
            gap:0 9mm;align-content:start}}
.p2 .next{{margin:0 12mm 7mm 10mm;background:var(--parch);padding:5.5mm 6mm;
           display:flex;justify-content:space-between;align-items:flex-end;gap:8mm}}
.p2 .next h3{{font-family:Anton,sans-serif;font-weight:400;font-size:11pt;
              text-transform:uppercase;margin-bottom:2mm}}
.p2 .next p{{font-size:8.2pt;line-height:1.45;max-width:112mm;color:#3a3b39}}
.p2 .next .who{{font-family:Plex,monospace;font-size:6.8pt;letter-spacing:.1em;
                text-transform:uppercase;color:var(--forest);text-align:right;
                line-height:1.9;white-space:nowrap}}
.p2 .art{{background:#efeae1;position:relative;overflow:hidden}}
.p2 .art img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
              object-position:50% 50%}}
.p2 .side{{padding:12mm 12mm 0 10mm;display:flex;flex-direction:column}}
.sealgrid{{display:grid;grid-template-columns:repeat(2,34mm);gap:5mm;margin-bottom:5mm}}
.sealgrid img{{width:34mm;height:34mm;display:block}}
.sealcap{{font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.11em;
          text-transform:uppercase;color:var(--dim);margin-bottom:0;
          max-width:76mm;line-height:1.7}}
.sealT{{font-family:Plex,monospace;font-size:12.5px;font-weight:600;letter-spacing:.16em;
        fill:#fff}}
h2{{font-family:Anton,sans-serif;font-weight:400;font-size:19pt;line-height:1.06;
    text-transform:uppercase;margin-bottom:3.5mm}}
.p2 .para{{font-size:8.6pt;line-height:1.5;color:#3a3b39;margin-bottom:9mm}}
.bl{{border-top:.4mm solid var(--rule);padding:4.6mm 0}}
.bl:first-of-type{{border-top:.7mm solid var(--ink)}}
.bl b{{display:block;font-family:Plex,monospace;font-size:6.6pt;letter-spacing:.11em;
       text-transform:uppercase;color:var(--forest);margin-bottom:1.1mm;font-weight:600}}
.bl p{{font-size:8.4pt;line-height:1.45;color:#3a3b39}}
.p2 .tail{{grid-column:1 / -1;margin-top:6mm;font-family:Plex,monospace;font-size:6.6pt;
           letter-spacing:.1em;text-transform:uppercase;color:var(--dim);line-height:1.9}}
{CSS3}
</style></head>
<body>
{COVER_PAGE}
<!-- ============ page 1 ============ -->
<div class="page">
  <div class="head">
    <div class="lock">
      <img class="nf" src="wordmark.png" alt="NoFilter">
      <span class="x">&times;</span>
      {LOCK}
    </div>
    <div class="meta">{DOC_LABEL}<br>Origins and supply<br>{BRIEF_DATE}</div>
  </div>

  <div class="intro">
    <div class="kicker">Conservation coffee &middot; Indonesia and Myanmar</div>
    <h1>Coffee grown on the edge of forests<br>that are <em>still standing</em>.</h1>
    <p class="lede">NoFilter buys from smallholders farming under canopy in the buffer zones of
    threatened forest, and pays a contracted share of every sale through to the conservation NGO
    holding that boundary. Three Sumatran origins are available for supply now. A fourth, from the
    Arakan Mountains in Myanmar, is possible, but supply there is limited and may run out.</p>
  </div>

  <div class="rows">{''.join(row(o) for o in ORIGINS)}
  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>

<!-- ============ page 2 ============ -->
<div class="page">
  <div class="p2">
    <div class="upper">
      <div class="art"><img src="hero-bag-batang-toru.jpg" alt="NoFilter 1 kg bag, Batang Toru"></div>
      <div class="side">
        <h1>Built to sell<br>on its <em>story</em>.</h1>
        <p class="para">{STORY_PARA}</p>
        <div class="sealgrid">{SEALS}</div>
        <div class="sealcap">Every listing carries its own sticker, in the colour reserved to that
        origin, so a bag, carton or sample says which coffee it is before it is opened.</div>
      </div>
    </div>
    <div class="lower">
      {''.join(f'<div class="bl"><b>{h}</b><p>{t}</p></div>' for h, t in BEHIND)}
    </div>
    <div class="next">
      <div>
        <h3>Next step</h3>
        <p>Trade pricing and terms are overleaf and {HOLD_WORDS}. The call is to agree
        which of the four origins earn a listing first, and when you want the first delivery.</p>
      </div>
      <div class="who">{WHO}</div>
    </div>
  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>

{PAGE3}{PAGER}
{PAGE4}
</body></html>
"""

(HERE / "brief.html").write_text(HTML)
print(f"[{PARTNER}]", "wrote brief.html:", len(ORIGINS), "origins,", len(CARD["TIERS"]), "tiers from SG-WHOLESALE.json")
print("margin check:", ", ".join(f'{t["band"]} {t["net_pct"]:.1f}%' for t in CARD["TIERS"])
      + (f', 250 g bag {RETAIL["net_pct"]:.1f}%' if RETAIL else ""))
if RENTAL:
    print("rental check:", ", ".join(
        m["name"] + " " + "/".join("%.1f%%" % m["net_pct"][t] for t in RENTAL["TERMS_MONTHS"])
        for m in RENTAL["MACHINES"]),
        f'(floor {RENTAL["MIN_NET_PCT_RENTAL"]}%, rates from RATE-CARD.md)')
    print("coffee fee check:", ", ".join("at %.0f nets %.1f%%" % kv for kv in RENTAL["coffee_net"].items()),
          "| coffee only:", ", ".join("%.1f%% at %.0f" % (v, k) for k, v in RENTAL["coffee_only_net"].items()),
          "| whole account, example office:", ", ".join("%.1f%% at %.0f" % (v, k) for k, v in RENTAL["account_net"].items()))
