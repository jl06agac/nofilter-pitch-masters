#!/usr/bin/env python3
"""cleanup_orphans.py — tidy the Pitches Master root (orphans/dead weight only)."""
import os, sys, json, shutil, datetime

_here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_here) if os.path.basename(_here) == "_tools" \
       else os.path.expanduser("~/Desktop/Pitches Master")
GO = "--go" in sys.argv

A = os.path.join(ROOT, "assets")
SHARED = os.path.join(ROOT, "_shared")
ARCHIVE = os.path.join(ROOT, "_archive")
QUARANTINE = os.path.join(ARCHIVE, "quarantine")
PZA = os.path.join(ROOT, "Zoos", "Pittsburgh Zoo")
plan = []

def real_file(p):
    return os.path.exists(p) and not os.path.islink(p)

brand = ["Arakan-Mountains.svg", "Batang-Gadis.svg", "Batang-Toru.svg",
         "Gayo-Lues.svg", "nofilter-wordmark.svg", "nofilter_badge_vectors"]
for name in brand:
    src = os.path.join(A, name); dst = os.path.join(SHARED, name)
    if os.path.exists(src) and not os.path.islink(src):
        plan.append(("skip (already in _shared)", src, dst) if os.path.exists(dst)
                    else ("move->_shared", src, dst))

pza_files = ["pza.html", "source.html", "pza-logo-green.svg", "pza-logo-ko.svg"]
for name in pza_files:
    src = os.path.join(A, name); dst = os.path.join(PZA, name)
    if os.path.exists(src) and not os.path.islink(src):
        plan.append(("skip (already in Pittsburgh)", src, dst) if os.path.exists(dst)
                    else ("move->Pittsburgh", src, dst))

dead = [os.path.join(ROOT, "assets.backup"),
        os.path.join(A, "Sumatran rainforest sounds [7zfnAOttUy4].mp3"),
        os.path.join(A, "favicon_io.zip")]
for src in dead:
    if os.path.exists(src):
        plan.append(("move->_archive", src, os.path.join(ARCHIVE, os.path.basename(src))))

junk = ["assets:torn-frame", "deforestation-image-2jpeg"]
for name in junk:
    src = os.path.join(A, name)
    if os.path.exists(src):
        plan.append(("quarantine", src, os.path.join(QUARANTINE, name.replace(":", "_"))))

print("=" * 70)
print("EXECUTING" if GO else "DRY RUN — nothing will change")
print("Root:", ROOT); print("=" * 70)
if not plan:
    print("Nothing to do — already clean."); sys.exit(0)
for action, src, dst in plan:
    print(f"  [{action}]"); print(f"      {os.path.relpath(src, ROOT)}")
    if not action.startswith("skip"): print(f"   -> {os.path.relpath(dst, ROOT)}")
sizes = sum(os.path.getsize(s) for a, s, d in plan
            if not a.startswith("skip") and os.path.isfile(s))
print(f"\nApprox data moved: {sizes/1e6:.1f} MB")
if not GO:
    print("\nDry run only. Re-run with --go to execute."); sys.exit(0)

os.makedirs(ARCHIVE, exist_ok=True); os.makedirs(QUARANTINE, exist_ok=True)
done = []
for action, src, dst in plan:
    if action.startswith("skip"): continue
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst); done.append({"action": action, "from": src, "to": dst})
        print(f"  done: {os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)}")
    except Exception as e:
        print(f"  !! FAILED {src}: {e}")
mpath = os.path.join(ROOT, "orphan-cleanup-manifest.json")
json.dump({"timestamp": datetime.datetime.now().isoformat(), "root": ROOT, "moves": done},
          open(mpath, "w"), indent=2)
print(f"\nManifest written: {os.path.relpath(mpath, ROOT)}")
if os.path.isdir(A):
    rem = os.listdir(A)
    reals = [r for r in rem if real_file(os.path.join(A, r))]
    links = [r for r in rem if os.path.islink(os.path.join(A, r))]
    print(f"\nOrphan assets/ now holds {len(reals)} real file(s), {len(links)} symlink(s).")
    if reals:
        print("  Real files still present (review before removing):")
        for r in reals[:20]: print("   ", r)
    else:
        print("  Only symlinks/empty — safe to remove assets/ by hand once checked.")
print("\nDone. Reversible from the manifest.")
