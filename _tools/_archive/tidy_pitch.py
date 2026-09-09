#!/usr/bin/env python3
"""tidy_pitch.py — bring one pitch folder to the agreed convention. Dry-run default; --go to execute."""
import os, sys, re, json, shutil, datetime

_here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_here) if os.path.basename(_here) == "_tools" \
       else os.path.expanduser("~/Desktop/Pitches Master")
SHARED = os.path.join(ROOT, "_shared")
ASSET_EXT = (".mp4", ".mp3", ".wav", ".jpg", ".jpeg", ".png", ".svg", ".webp", ".gif", ".woff2", ".ttf", ".otf")
GO = "--go" in sys.argv
args = [a for a in sys.argv[1:] if a != "--go"]
if not args:
    print('Usage: python3 tidy_pitch.py "Schools/UWCSEA" [--go]'); sys.exit(1)

pitch = os.path.abspath(args[0] if os.path.isabs(args[0]) else os.path.join(ROOT, args[0]))
if not os.path.isdir(pitch):
    print("!! pitch not found:", pitch); sys.exit(1)

ASSETS = os.path.join(pitch, "assets")
ARCHIVE = os.path.join(pitch, "_archive")
reldepth = os.path.relpath(SHARED, ASSETS)
LIVE = os.environ.get("LIVE_DECKS", "").split(",") if os.environ.get("LIVE_DECKS") else None

def is_asset(name): return name.lower().endswith(ASSET_EXT)

root_items = [f for f in os.listdir(pitch) if f not in (".", "..")]
html_files = [f for f in root_items if f.lower().endswith(".html")]

dep_html = set(); deck_text = {}
for h in html_files:
    p = os.path.join(pitch, h)
    if os.path.isfile(p):
        t = open(p, encoding="utf-8", errors="ignore").read()
        deck_text[h] = t
        for m in re.finditer(r'(?:data-[a-z-]*src|src)="([^"]+\.html)"', t):
            dep_html.add(os.path.basename(m.group(1)))

if LIVE:
    live_decks = [h for h in html_files if h in LIVE]
else:
    cand = [h for h in html_files
            if not re.search(r'(original|v1|old|backup|new)', h, re.I) and h.lower() != "index.html"]
    cand.sort(key=lambda h: os.path.getsize(os.path.join(pitch, h)), reverse=True)
    live_decks = cand[:1]
live_set = set(live_decks) | dep_html

referenced = set()
for h in live_decks:
    for m in re.finditer(r'(?:src|poster|data-[a-z-]*src)="([^"]+)"', deck_text.get(h, "")):
        ref = m.group(1)
        if not ref.startswith(("http", "mailto", "tel", "#", "data:")):
            referenced.add(os.path.basename(ref))

plan = []
for f in sorted(root_items):
    low = f.lower()
    if f in ("assets", "_archive", "_netlify-build", "files", "_tools"): continue
    if low == ".ds_store": plan.append(("delete", f, None, "junk")); continue
    if f == "bundle.py": plan.append(("delete", f, None, "tool lives in _tools/")); continue
    if low.endswith(".html"):
        if f in live_set: plan.append(("keep-html", f, None, "live deck / dependency"))
        else: plan.append(("archive", f, os.path.join(ARCHIVE, f), "superseded HTML"))
        continue
    if is_asset(f):
        if f in referenced: plan.append(("asset->assets/", f, os.path.join(ASSETS, f), "into assets/"))
        else: plan.append(("archive", f, os.path.join(ARCHIVE, f), "UNUSED asset (no live ref)"))
        continue
    plan.append(("archive", f, os.path.join(ARCHIVE, f), "non-asset clutter"))

def rewrite_refs(text):
    pat = re.compile(r'((?:src|poster)=")([^"/]+)(")')
    changes = []
    def repl(m):
        pre, val, post = m.group(1), m.group(2), m.group(3)
        if val.lower().endswith(".html") or not val.lower().endswith(ASSET_EXT): return m.group(0)
        changes.append(val); return f"{pre}assets/{val}{post}"
    return pat.sub(repl, text), changes

print("=" * 70)
print("EXECUTING" if GO else "DRY RUN — nothing changes")
print("Pitch:", os.path.relpath(pitch, ROOT))
print("Live deck(s):", ", ".join(live_decks) if live_decks else "(none detected!)")
if dep_html: print("Dependency HTML kept:", ", ".join(sorted(dep_html)))
print("=" * 70)
for action, f, dest, note in plan:
    tag = f"[{action}]"
    if dest: print(f"  {tag:18} {f}  ->  {os.path.relpath(dest, pitch)}   ({note})")
    else: print(f"  {tag:18} {f}   ({note})")
print("\n  --- HTML rewrites (live decks only) ---")
rewrite_preview = {}
for h in live_decks:
    new, changes = rewrite_refs(deck_text.get(h, "")); rewrite_preview[h] = new
    print(f"  {h}: {len(changes)} reference(s) would be prefixed with assets/")
    for c in changes[:6]: print(f"       {c}  ->  assets/{c}")
    if len(changes) > 6: print(f"       ... and {len(changes)-6} more")
if not GO:
    print("\nDry run only. Re-run with --go to execute."); sys.exit(0)

os.makedirs(ASSETS, exist_ok=True); os.makedirs(ARCHIVE, exist_ok=True)
done = []
def seed_and_link(name, src_path, dst):
    sp = os.path.join(SHARED, name)
    if not os.path.exists(sp):
        if os.path.islink(src_path):
            real = os.path.realpath(src_path)
            if os.path.exists(real): shutil.copy2(real, sp)
        elif os.path.isfile(src_path): shutil.copy2(src_path, sp)
    os.remove(src_path); os.symlink(os.path.join(reldepth, name), dst)
for action, f, dest, note in plan:
    src = os.path.join(pitch, f)
    try:
        if action == "delete": os.remove(src); done.append({"action":"delete","item":f})
        elif action == "archive":
            os.makedirs(os.path.dirname(dest), exist_ok=True); shutil.move(src, dest)
            done.append({"action":"archive","item":f,"to":dest})
        elif action == "asset->assets/":
            seed_and_link(f, src, dest); done.append({"action":"asset->assets/","item":f})
    except Exception as e: print(f"  !! FAILED {f}: {e}")
for h in live_decks:
    p = os.path.join(pitch, h); shutil.copy2(p, p + ".pre-tidy")
    open(p, "w", encoding="utf-8").write(rewrite_preview[h])
    done.append({"action":"rewrite-html","item":h,"backup":h+".pre-tidy"})
print("\n  --- verifying references resolve ---")
broken = []
for h in live_decks:
    t = open(os.path.join(pitch, h), encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'(?:src|poster|data-[a-z-]*src)="([^"]+)"', t):
        ref = m.group(1)
        if ref.startswith(("http","mailto","tel","#","data:")): continue
        if not os.path.exists(os.path.join(pitch, ref)): broken.append((h, ref))
if broken:
    print(f"  !! {len(broken)} reference(s) DO NOT resolve:")
    for h, r in broken[:20]: print(f"     {h}: {r}")
else: print("  All references resolve.")
mpath = os.path.join(pitch, f"tidy-{os.path.basename(pitch).replace(' ','_')}-manifest.json")
json.dump({"timestamp":datetime.datetime.now().isoformat(),"pitch":pitch,"live_decks":live_decks,"moves":done,"broken_after":broken}, open(mpath,"w"), indent=2)
print(f"\nManifest: {os.path.relpath(mpath, ROOT)}")
print("Done. HTML backups saved as <deck>.html.pre-tidy (delete once verified).")
