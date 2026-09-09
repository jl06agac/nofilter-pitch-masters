import re, sys, os
base = os.path.expanduser("~/Desktop/Pitches Master/Schools/UWCSEA")
src = os.path.join(base, "index.html")
dst = os.path.join(base, "NoFilter-UWCSEA-PartTwo.html")
s = open(src, encoding="utf-8").read()
d = open(dst, encoding="utf-8").read()
m = re.search(r'(<div class="deets-interview">.*?</div>)\s*</div>', s, re.S)
if not m:
    print("!! interview block not found in index.html"); sys.exit(1)
interview = m.group(1)
print("Found interview block:", len(interview), "chars")
if '<a class="moneyfm-link"' in d:
    print("Markup already present, done."); sys.exit(0)
anchor = '<div class="deets">UAE \u00b7 <a href="mailto:alex@nofilter.ae">alex@nofilter.ae</a> \u00b7 Botim +971 50 871 3588</div>'
if anchor in d:
    d = d.replace(anchor, anchor + "\n        " + interview, 1)
    open(dst, "w", encoding="utf-8").write(d)
    print("SUCCESS: markup injected after UAE line.")
else:
    print("!! anchor not found"); sys.exit(1)
