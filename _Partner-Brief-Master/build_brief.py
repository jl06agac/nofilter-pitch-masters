#!/usr/bin/env python3
"""
build_brief.py — NoFilter wholesale supply agreement, four A4 pages.
Built per partner: `python3 build_brief.py <partner>` reads partners/<partner>.json over SG-WHOLESALE.json.

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
for _t in CARD["TIERS"]:
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


SEALS = "".join(f'<img src="seals/nf-seal-{slug(n)}.svg" alt="{n} seal">'
                for n, _ in ORIGIN_COLOURS)

TIERROWS = "".join(
    f'''<div class="tr{" best" if t is CARD["TIERS"][-1] else ""}">
        <span class="band">{t["band"]}</span>
        <span class="amt"><small>{CUR}</small>{t["list"]:.2f}</span>
        <span class="net">{CUR} {t["net"]:.2f}</span>
        <span class="mar"><b>{t["m_lo"]:.1f}% to {t["m_hi"]:.1f}%</b></span>
      </div>''' for t in CARD["TIERS"])
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
      <p class="lede">These four pages are the supply agreement. Signing this page puts the pricing and
      terms set out overleaf into effect for the validity period and replaces anything discussed before
      it. Nothing here commits {CARD["PARTNER_NAME"]} to a volume.</p>
    </div>

    <div class="recap">
      <div class="rr"><div class="rk">Trade price</div><div class="rv"><b>{CUR} {CARD["TIERS"][0]["list"]:.2f}, {CARD["TIERS"][1]["list"]:.2f} and {CARD["TIERS"][2]["list"]:.2f} per kg</b>, by annual volume bought, with any year-one tier credit applied at twelve months</div></div>
      <div class="rr"><div class="rk">Marketing rebate</div><div class="rv"><b>{CARD["REBATE_PCT"]}%</b> of invoiced value, paid {CARD["REBATE_FREQUENCY"]}</div></div>
      <div class="rr"><div class="rk">To the forest</div><div class="rv"><b>{CUR} {CARD["CONTRIB_PER_KG"]:.2f} per kilogram</b>, the same on every tier, contracted and shown on the invoice</div></div>
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
      <p class="lede">These prices hold for twelve months, delivered to {CARD["DELIVERY_SHORT"]}. They
      are set so that a listing at the recommended shelf price returns you a normal trade margin without
      NoFilter cutting the share that goes back to the forest. In the first year the rate is settled on
      what you actually buy rather than on a forecast: pass a threshold and we credit the difference back
      across everything you have bought, so there is nothing to commit to up front.</p>
    </div>

    <div class="ptab">
      <div class="hr"><span>Annual volume bought</span><span>Per kg</span><span>Net of rebate</span><span style="text-align:right">Your margin at {CUR}&nbsp;{CARD["RRP_LOW"]}&ndash;{CARD["RRP_HIGH"]}</span></div>
      {TIERROWS}
    </div>
    <div class="ptabnote">First year invoiced at the entry rate, with any tier credit applied at twelve
      months, see tier review &middot; minimum order {CARD["MOQ_KG"]} kg &middot; delivery included</div>

    <div class="cards">
      <div class="card"><b>Marketing rebate</b>
        <div class="big">{CARD["REBATE_PCT"]}%</div>
        <p>Of invoiced value, paid {CARD["REBATE_FREQUENCY"]}, against {CARD["REBATE_EARNED_BY"]}. Calculated on {CARD["REBATE_BASIS"]}.</p></div>
      <div class="card"><b>To the forest, per kilo</b>
        <div class="big">{CUR}&nbsp;{CARD["CONTRIB_PER_KG"]:.2f}</div>
        <p>The same on every tier, contracted and shown on the invoice. Your customer gets a figure for
        their own reporting, and you get a listing that answers a procurement question instead of raising
        one.</p></div>
      <div class="card"><b>Recommended shelf price</b>
        <div class="big">{CUR}&nbsp;{CARD["RRP_LOW"]}&ndash;{CARD["RRP_HIGH"]}</div>
        <p>A recommendation, not a condition; the price you set is yours. The margins shown in the
        table are calculated against this band.</p></div>
    </div>

    <div class="terms">
      <div class="tm"><b>Format</b><p>{CARD["FORMAT"]}. All four origins at the same price, ordered in any mix.</p></div>
      <div class="tm"><b>Minimum order</b><p>{CARD["MOQ_KG"]} kg per delivery, any combination of origins.</p></div>
      <div class="tm"><b>Tier review</b><p>Year one is invoiced at the entry rate. Pass a threshold over the twelve months and the better rate applies to everything bought, with the difference credited. From year two the tier is set in advance on the preceding year.</p></div>
      <div class="tm"><b>Delivery</b><p>Included, to {CARD["DELIVERY_POINT"]}. Title and risk pass on delivery.</p></div>
      <div class="tm"><b>Territory</b><p>{CARD["MARKET"]}, non-exclusive.{CARD["TERRITORY_NOTE"]}</p></div>
      <div class="tm"><b>Roasting and delivery</b><p>Roasted to order. Orders placed by {CARD["ORDER_CUTOFF"]} are roasted the following {CARD["ROAST_DAYS"]} and delivered to your warehouse on {CARD["DELIVERY_DAYS"]}. Anything later falls into the next week&rsquo;s roast.</p></div>
      <div class="tm"><b>Payment</b><p>Coffee is {CARD["INVOICING"]}, payable {CARD["PAYMENT_DAYS"]} days from invoice.</p></div>
      <div class="tm"><b>Price validity</b><p>Twelve months to {CARD["VALID_TO_TEXT"]}, adjustable on 30 days&rsquo; notice only if landed green coffee moves more than {CARD["GREEN_TRIGGER_PCT"]}%.</p></div>
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
              object-position:52% 46%}}
.p2 .side{{padding:12mm 12mm 0 10mm;display:flex;flex-direction:column}}
.sealgrid{{display:grid;grid-template-columns:repeat(2,34mm);gap:5mm;margin-bottom:5mm}}
.sealgrid img{{width:34mm;height:34mm;display:block}}
.sealcap{{font-family:Plex,monospace;font-size:6.4pt;letter-spacing:.11em;
          text-transform:uppercase;color:var(--dim);margin-bottom:8mm;
          max-width:76mm;line-height:1.7}}
.sealT{{font-family:Plex,monospace;font-size:12.5px;font-weight:600;letter-spacing:.16em;
        fill:#fff}}
h2{{font-family:Anton,sans-serif;font-weight:400;font-size:19pt;line-height:1.06;
    text-transform:uppercase;margin-bottom:3.5mm}}
.p2 .para{{font-size:8.6pt;line-height:1.5;color:#3a3b39;margin-bottom:6mm}}
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

<!-- ============ page 1 ============ -->
<div class="page">
  <div class="head">
    <div class="lock">
      <img class="nf" src="wordmark.png" alt="NoFilter">
      <span class="x">&times;</span>
      <img class="ly" src="{CARD["LOGO"]}" alt="{CARD["PARTNER_NAME"]}">
    </div>
    <div class="meta">Partner brief<br>Origins and supply<br>September 2026</div>
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
      <div class="art"><img src="hero-bag.png" alt="NoFilter 1 kg bag"></div>
      <div class="side">
        <div class="sealgrid">{SEALS}</div>
        <div class="sealcap">Every listing carries its own seal, in the colour reserved to that
        origin, so a bag, carton or sample says which coffee it is before it is opened.</div>
        <h2>Built to sell<br>on its story.</h2>
        <p class="para">Most coffee on a workplace shelf is bought where it is cheapest to grow,
        and cheap usually means cleared ground. This range is the opposite proposition, and it
        comes with the evidence to say so out loud.</p>
      </div>
    </div>
    <div class="lower">
      {''.join(f'<div class="bl"><b>{h}</b><p>{t}</p></div>' for h, t in BEHIND)}
    </div>
    <div class="next">
      <div>
        <h3>Next step</h3>
        <p>Trade pricing and terms are overleaf and hold for twelve months. The call is to agree
        which of the four origins earn a listing first, and when you want the first delivery.</p>
      </div>
      <div class="who">Prepared for {CARD["PARTNER_NAME"]}<br>September 2026<br>alex@nofilter.sg</div>
    </div>
  </div>

  <div class="foot">
    <span><b>NoFilter Pte. Ltd.</b> &middot; Singapore</span>
    <span>alex@nofilter.sg</span>
    <span>nofilter.sg&nbsp;&nbsp;/&nbsp;&nbsp;nofilter.ae</span>
  </div>
</div>

{PAGE3}
{PAGE4}
</body></html>
"""

(HERE / "brief.html").write_text(HTML)
print(f"[{PARTNER}]", "wrote brief.html:", len(ORIGINS), "origins,", len(CARD["TIERS"]), "tiers from SG-WHOLESALE.json")
print("margin check:", ", ".join(f'{t["band"]} {t["net_pct"]:.1f}%' for t in CARD["TIERS"]))
