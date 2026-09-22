#!/usr/bin/env python3
"""Fails the build if any page overflows or clips. Run after build_brief.py, before rendering the PDF.
The column carries overflow:hidden so a footer can never be pushed off the page, which means an
overrun hides itself. This measures scrollHeight against clientHeight and says so out loud."""
from playwright.sync_api import sync_playwright
import pathlib, sys

url = "file://" + str((pathlib.Path(__file__).parent / "brief.html").resolve())
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                           args=["--no-sandbox"])
    pg = b.new_page(); pg.goto(url); pg.wait_for_timeout(700)
    rows = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((p,i) => {
        const col = p.querySelector('.p2,.p3,.p4') || p;
        const kids = [...p.children], last = kids[kids.length-1];
        return {page:i+1,
                overrun:+(p.scrollHeight - p.clientHeight).toFixed(1),
                clipped:+(col.scrollHeight - col.clientHeight).toFixed(1),
                slack:+(p.clientHeight - kids.reduce((h,k)=>h+k.getBoundingClientRect().height,0)).toFixed(1),
                tail:last.className};
      })""")
    b.close()

bad = False
for r in rows:
    problem = r["overrun"] > 1 or r["clipped"] > 1
    bad |= problem
    print(f"page {r['page']}: overrun {r['overrun']:+.0f}px, clipped inside column {r['clipped']:+.0f}px, "
          f"slack {r['slack']:.0f}px, ends with .{r['tail']}"
          + ("   <-- FIX THIS" if problem else ""))
if bad:
    sys.exit("\nA page does not fit. Adjust spacing or move content, then rebuild.")
print("\nAll pages fit with nothing clipped.")
