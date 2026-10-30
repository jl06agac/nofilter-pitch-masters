#!/usr/bin/env python3
"""Stamp the NoFilter Benchmark brochure for one or more markets.

    python3 build_benchmark.py            # SG and UAE
    python3 build_benchmark.py SG         # one market
    python3 build_benchmark.py --pdf      # also render PDFs + page-overflow check (needs playwright)

Reads   NoFilter-Benchmark-Master.html  (the only file to edit)
        markets/<MARKET>.json           (market-layer token values)
Writes  Clients/Generic/Benchmark/<OUT_NAME>.html  + assets/  (+ <OUT_NAME>.pdf with --pdf)

Assets come from their canonical homes, never from a copy:
  assets-src/                         fonts, cover photo, cover wordmark (this folder)
  _CDN-UPLOAD-SAFE/                   origin landscapes, cherries, machine
  Marketing/Product-Images/           1 kg bag photos, cropped and downsized here at build time
"""
import json, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                   # .../NoFilter
MASTER = HERE / "NoFilter-Benchmark-Master.html"
OUT = ROOT / "Clients" / "Generic" / "Benchmark"
CDN = ROOT / "_CDN-UPLOAD-SAFE"
PRODUCT = ROOT / "Marketing" / "Product-Images"

CDN_FILES = ["batang-toru-banner-poster.jpg", "batang-gadis-banner-poster.jpg",
             "gayo-lues-banner-poster.jpg", "batang-arakan-banner-poster.jpg",
             "cafematic-2-w1400.webp", "cafematic-5-w1400.webp", "cafematic-6-w1400.webp", "cafematic-8-w1400.webp",
             "nw-bag-rotate-poster.jpg", "quote-pour.jpg", "orangutan-canopy.jpg", "tapanuli-orangutan.jpg",
             "batang-toru-processor-2.jpg", "arakan-drying-house.jpg", "unit-machine.jpg", "smiirl-counter.jpg",
             "wp-pour-atmos.jpg", "img-02-8eac2398.jpg", "wp-office-poster.jpg", "img-13-pour-88b47e5b.jpg",
             "wp-compost.jpg", "coffee-cart.jpg", "sabar-agroforest.jpg", "verify-drone-poster.jpg",
             "cinta-raja-planting.jpg", "arakan-hoolock.jpg", "batang-gadis-intro.jpg", "nf-cherries-end.jpg", "batang-gadis-farmer.jpg"]
MAX_W = 1600          # photos are downsized to this width for the page and PDF; sources untouched
BAGS = {  # output name -> product photo
    "bag-batang-toru.jpg": "nofilter-batang-toru-1kg-front.png",
    "bag-batang-gadis.jpg": "nofilter-batang-gadis-1kg-front.png",
    "bag-gayo-lues.jpg": "nofilter-gayo-lues-1kg-front.png",
    "bag-arakan-mountains.jpg": "nofilter-arakan-mountains-1kg-front.png",
}
BAG_CROP = (560, 60, 1440, 1990)   # bag plus its floor shadow, on the 2000 px product photos
BAG_W = 600
TOKEN = re.compile(r"\[\[[A-Z0-9_]+\]\]")


def build_assets():
    dst = OUT / "assets"
    (dst / "fonts").mkdir(parents=True, exist_ok=True)
    for p in (HERE / "assets-src").rglob("*"):
        if p.is_file():
            t = dst / p.relative_to(HERE / "assets-src")
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, t)
    from PIL import Image
    for f in CDN_FILES:
        if f.endswith(".jpg"):
            im = Image.open(CDN / f).convert("RGB")
            if im.width > MAX_W:
                im = im.resize((MAX_W, round(MAX_W * im.height / im.width)), Image.LANCZOS)
            im.save(dst / f, quality=82, optimize=True, progressive=True)
        elif f.endswith(".webp"):          # machine photos: JPEG embeds far smaller in the PDF
            im = Image.open(CDN / f).convert("RGB")
            im.save(dst / f.replace("-w1400.webp", ".jpg"), quality=86, optimize=True)
        else:
            shutil.copyfile(CDN / f, dst / f)
    for out, src in BAGS.items():
        im = Image.open(PRODUCT / src).convert("RGB")
        assert im.size == (2000, 2000), f"{src} is {im.size}; re-measure BAG_CROP"
        im = im.crop(BAG_CROP)
        im = im.resize((BAG_W, round(BAG_W * im.height / im.width)), Image.LANCZOS)
        im.save(dst / out, quality=86, optimize=True)


def stamp(code):
    vals = json.loads((HERE / "markets" / f"{code}.json").read_text())
    html = MASTER.read_text()
    for k, v in vals.items():
        if not k.startswith("_") and k != "OUT_NAME":
            html = html.replace(f"[[{k}]]", v)
    left = sorted(set(TOKEN.findall(html)))
    assert not left, f"{code}: unfilled tokens {left}"
    missing = [s for s in re.findall(r'src="(assets/[^"]+)"', html) if not (OUT / s).exists()]
    assert not missing, f"{code}: missing assets {missing}"
    out = OUT / f"{vals['OUT_NAME']}.html"
    out.write_text(html)
    print("wrote", out.relative_to(ROOT))
    return out


def render(html_path):
    """Overflow check + PDF. Every .page is a fixed A4 box with overflow:hidden, so an
    overrun hides itself; this measures every flex container inside each page instead."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1000, "height": 1400})
        pg.goto(html_path.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        bad = pg.evaluate("""() => {
          const out = [];
          document.querySelectorAll('.page').forEach((page, i) => {
            page.querySelectorAll('.cover, .relief, .relief__body, .mosaic, .machines, .tile__cap, .party, .who__photo').forEach(el => {
              if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)
                out.push(`page ${i+1} .${el.className.split(' ')[0]} ${el.scrollHeight}>${el.clientHeight}`);
            });
            const r = page.querySelector('.rail--bottom').getBoundingClientRect(), pr = page.getBoundingClientRect();
            if (r.bottom > pr.bottom + 1) out.push(`page ${i+1} footer rail pushed off`);
          });
          document.querySelectorAll('img').forEach(im => { if (!im.naturalWidth) out.push('broken img ' + im.getAttribute('src')); });
          if ([...document.fonts].some(f => f.status === 'error')) out.push('a font failed to load');
          return out; }""")
        pdf = html_path.with_suffix(".pdf")
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
        b.close()
    print("wrote", pdf.relative_to(ROOT), "| checks:", "OK" if not bad else bad)
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    codes = [a.upper() for a in args] or ["SG", "UAE"]
    OUT.mkdir(parents=True, exist_ok=True)
    build_assets()
    outs = [stamp(c) for c in codes]
    if "--pdf" in sys.argv:
        problems = sum((render(o) for o in outs), [])
        sys.exit(1 if problems else 0)
