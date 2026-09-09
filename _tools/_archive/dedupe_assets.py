#!/usr/bin/env python3
"""
dedupe_assets.py — collapse duplicate pitch assets into one shared store + symlinks.

SAFE BY DEFAULT: runs as a DRY RUN unless you pass --go.
  Dry run:   python3 dedupe_assets.py
  Execute:   python3 dedupe_assets.py --go

Rules (locked with Alex):
  - Only collapses files that share BOTH the same content (sha256) AND the same filename.
  - NEVER touches anything under a path containing 'deploy' or 'partnership-deploy'
    (those are meant to stay self-contained for bundling / Netlify).
  - Canonical copy goes to _shared/ at the tree root, mirroring the basename.
  - Every other copy is replaced with a RELATIVE symlink pointing at the canonical file.
  - Skips files that are already symlinks.
  - Asset types only (images/video/fonts). HTML/JS/CSS untouched.

Reversible: a manifest is written so every symlink can be turned back into a real file.
"""
import os, sys, hashlib, json
from collections import defaultdict

ROOT = os.path.expanduser("~/Desktop/Pitches Master")
SHARED_DIRNAME = "_shared"
GO = "--go" in sys.argv

EXTS = {".mp4",".mov",".jpg",".jpeg",".png",".webp",".woff2",".woff",".ttf",".otf",".JPG",".JPEG"}
# substrings in the path that mean "leave it alone"
EXCLUDE_PATH_PARTS = ("deploy", "partnership-deploy", SHARED_DIRNAME, ".backup", "_archive")

def is_excluded(path):
    low = path.lower()
    return any(part in low for part in (p.lower() for p in EXCLUDE_PATH_PARTS))

def sha256(path, buf=1<<20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(buf)
            if not b: break
            h.update(b)
    return h.hexdigest()

def human(n):
    for unit in ("B","KB","MB","GB"):
        if n < 1024: return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"

def main():
    if not os.path.isdir(ROOT):
        print(f"!! Root not found: {ROOT}"); sys.exit(1)

    # 1. collect candidate files
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if is_excluded(dirpath):
            continue
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext not in EXTS: continue
            full = os.path.join(dirpath, fn)
            if os.path.islink(full):  # already a symlink, skip
                continue
            if is_excluded(full): continue
            files.append(full)

    # 2. group by (basename, hash)
    groups = defaultdict(list)
    for f in files:
        try:
            key = (os.path.basename(f), sha256(f))
        except OSError as e:
            print(f"   (skip unreadable: {f}: {e})"); continue
        groups[key].append(f)

    shared_root = os.path.join(ROOT, SHARED_DIRNAME)
    plan = []          # (canonical, dest, [links_to_make], size)
    reclaimed = 0
    # Track which dest names are taken, and by which content hash, so two groups
    # that share a filename but differ in content NEVER collide in _shared.
    dest_by_name = {}   # basename -> {hash -> dest_path}
    for (base, h), paths in sorted(groups.items()):
        if len(paths) < 2:
            continue   # not duplicated, leave it
        # choose canonical: prefer an existing _shared copy, else shortest path
        canonical = sorted(paths, key=lambda p: (0 if SHARED_DIRNAME in p else 1, len(p)))[0]

        # Resolve a collision-safe destination name.
        taken = dest_by_name.setdefault(base, {})
        if h in taken:
            dest = taken[h]                      # same content already placed
        else:
            if not taken:
                dest = os.path.join(shared_root, base)   # first content for this name -> plain name
            else:
                # same name, DIFFERENT content already exists -> disambiguate with short hash
                stem, ext = os.path.splitext(base)
                dest = os.path.join(shared_root, f"{stem}.{h[:8]}{ext}")
            taken[h] = dest

        links = [p for p in paths if p != canonical]
        try:
            sz = os.path.getsize(canonical)
        except OSError:
            sz = 0
        reclaimed += sz * len(links)
        plan.append((canonical, dest, links, sz))

    # 3. report
    plan.sort(key=lambda x: x[3]*len(x[2]), reverse=True)
    print(f"\n{'='*70}")
    print(f"{'DRY RUN — no changes' if not GO else 'EXECUTING — writing changes'}")
    print(f"Root: {ROOT}")
    print(f"Shared store: {shared_root}")
    print(f"Duplicate groups (same name + content, outside deploy/): {len(plan)}")
    print(f"Total space reclaimable: {human(reclaimed)}")
    print(f"{'='*70}\n")

    for canonical, dest, links, sz in plan[:40]:
        print(f"• {os.path.basename(canonical)}  ({human(sz)} × {len(links)} dup copies = {human(sz*len(links))})")
        print(f"    canonical → {os.path.relpath(dest, ROOT)}")
        for l in links[:3]:
            print(f"    symlink   → {os.path.relpath(l, ROOT)}")
        if len(links) > 3:
            print(f"    … and {len(links)-3} more")
    if len(plan) > 40:
        print(f"\n… and {len(plan)-40} more groups (full list in manifest).")

    manifest = {
        "root": ROOT, "shared": shared_root,
        "groups": [
            {"canonical": c, "dest": d, "links": l, "size": s}
            for (c,d,l,s) in plan
        ],
        "reclaimable_bytes": reclaimed,
    }
    mpath = os.path.join(ROOT, "dedupe-manifest.json") if GO else "/tmp/dedupe-manifest-dryrun.json"

    if not GO:
        with open(mpath, "w") as f: json.dump(manifest, f, indent=2)
        print(f"\nDry run only. Nothing changed.")
        print(f"Full plan written to: {mpath}")
        print(f"To execute for real:  python3 {os.path.basename(__file__)} --go")
        return

    # 4. EXECUTE
    os.makedirs(shared_root, exist_ok=True)
    moved, linked, skipped = 0, 0, 0
    for canonical, dest, links, sz in plan:
        # Place the canonical file at dest.
        if os.path.abspath(canonical) != os.path.abspath(dest):
            if not os.path.exists(dest):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.rename(canonical, dest)
                moved += 1
            else:
                # dest already exists — only safe if it's the SAME content.
                if sha256(dest) != sha256(canonical):
                    print(f"   !! SKIP (name+hash collision guard): {dest} already exists with different content; leaving {canonical} as-is")
                    skipped += 1
                    continue
            # the old canonical location also becomes a symlink
            links = [canonical] + links
        for l in links:
            try:
                # never clobber a real file unless it is genuinely identical to dest
                if os.path.islink(l):
                    os.remove(l)
                elif os.path.exists(l):
                    if sha256(l) != sha256(dest):
                        print(f"   !! SKIP link (content differs): {l}")
                        skipped += 1
                        continue
                    os.remove(l)
                rel = os.path.relpath(dest, os.path.dirname(l))
                os.symlink(rel, l)
                linked += 1
            except OSError as e:
                print(f"   !! failed on {l}: {e}")
    with open(mpath, "w") as f: json.dump(manifest, f, indent=2)
    print(f"\nDone. Canonical files moved to _shared: {moved}. Symlinks created: {linked}. Skipped (collision guard): {skipped}.")
    print(f"Reclaimed ~{human(reclaimed)}. Manifest: {mpath}")
    print("Reversible: re-copy from _shared over each symlink, or restore from manifest.")

if __name__ == "__main__":
    main()
