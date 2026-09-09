#!/usr/bin/env python3
"""netlify_pack.py — build a symlink-free folder ready to drag into Netlify."""
import os, sys, shutil

_here = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_here) == "_tools":
    ROOT = os.path.dirname(_here)
else:
    ROOT = os.path.expanduser("~/Desktop/Pitches Master")
BUILD_DIRNAME = "_netlify-build"

def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print('Usage: python3 _tools/netlify_pack.py "Schools/UWCSEA" [--html part-two.html]')
        sys.exit(1)
    html_override = None
    if "--html" in args:
        i = args.index("--html"); html_override = args[i+1]; del args[i:i+2]
    pitch_rel = args[0].rstrip("/")
    pitch_dir = pitch_rel if os.path.isabs(pitch_rel) else os.path.join(ROOT, pitch_rel)
    pitch_dir = os.path.abspath(pitch_dir)
    if not os.path.isdir(pitch_dir):
        print(f"!! Pitch folder not found: {pitch_dir}"); sys.exit(1)
    build_dir = os.path.join(pitch_dir, BUILD_DIRNAME)
    if os.path.exists(build_dir): shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    SKIP = (BUILD_DIRNAME.lower(), "deploy", "partnership-deploy", "__pycache__")
    copied, deref = 0, 0
    for dirpath, dirnames, filenames in os.walk(pitch_dir):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP and BUILD_DIRNAME not in d]
        rel = os.path.relpath(dirpath, pitch_dir)
        if rel == ".": rel = ""
        dest_subdir = os.path.join(build_dir, rel)
        os.makedirs(dest_subdir, exist_ok=True)
        for fn in filenames:
            src = os.path.join(dirpath, fn); dst = os.path.join(dest_subdir, fn)
            was_link = os.path.islink(src)
            try:
                shutil.copy2(src, dst, follow_symlinks=True)
                copied += 1
                if was_link: deref += 1
            except OSError as e:
                print(f"   !! failed: {src}: {e}")
    root_files = os.listdir(build_dir)
    htmls = [f for f in root_files if f.lower().endswith(".html")]
    index_made = None
    if html_override:
        src_html = os.path.join(build_dir, html_override)
        if not os.path.exists(src_html):
            print(f"   !! --html '{html_override}' not found in build; leaving as-is")
        elif html_override != "index.html":
            shutil.copy2(src_html, os.path.join(build_dir, "index.html")); index_made = html_override
    elif "index.html" not in [h.lower() for h in htmls] and len(htmls) == 1:
        shutil.copy2(os.path.join(build_dir, htmls[0]), os.path.join(build_dir, "index.html")); index_made = htmls[0]
    remaining_links = []
    for dp, dn, fns in os.walk(build_dir):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p): remaining_links.append(p)
    print(f"\n{'='*64}")
    print("Netlify build ready (real files, no symlinks):")
    print(f"  {build_dir}")
    print(f"{'='*64}")
    print(f"Files copied: {copied}  (symlinks turned into real files: {deref})")
    if index_made: print(f"index.html created from: {index_made}")
    elif "index.html" in [h.lower() for h in htmls]: print("index.html already present.")
    else: print("!! No single index.html — pass --html <file>.")
    if remaining_links:
        print(f"!! WARNING: {len(remaining_links)} symlink(s) still present:")
        for l in remaining_links[:5]: print(f"   {l}")
    else:
        print("Verified: zero symlinks in build. Safe to drag into Netlify.")
    print(f"\nDrag THIS folder into the Netlify drop zone:\n  {build_dir}")
    print("(Delete it after deploying, or re-run to refresh.)")

if __name__ == "__main__":
    main()
