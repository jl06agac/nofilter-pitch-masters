#!/usr/bin/env python3
"""
repoint-shared.py — rewrite a pitch's SHARED asset references to the shared-assets site,
leaving client-specific assets local. Use it to make a SAFE TEST COPY of an existing deploy
(or to retrofit one) without touching the live original.

What counts as "shared": any `assets/<file>` whose <file> also exists in Pitches/_shared/.
Everything else (logo, -target mockups, counters, hero poster) stays `assets/<file>`.

Usage:
    python3 repoint-shared.py <input.html> <SHARED_BASE_URL> [output.html]

Example:
    python3 repoint-shared.py "Schools/UWCSEA/partnership-deploy/index.html" \
        "https://nofilter-shared.netlify.app" /tmp/uwcsea-shared-test.html

Notes:
- Never overwrites the input unless you pass it as the output. Default output is
  <input>-shared.html beside the input.
- Prints how many refs were repointed vs kept local, so you can sanity-check.
"""
import io, os, re, sys

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    inp = sys.argv[1]
    base = sys.argv[2].rstrip("/")
    out = sys.argv[3] if len(sys.argv) > 3 else (os.path.splitext(inp)[0] + "-shared.html")

    # locate _shared as sibling of this script's parent (script lives in Pitches/_tools)
    shared_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_shared"))
    if not os.path.isdir(shared_dir):
        print(f"!! can't find _shared at {shared_dir}"); sys.exit(2)
    shared_files = set(os.listdir(shared_dir))

    s = io.open(inp, encoding="utf-8").read()
    moved, kept = [0], set()

    def repl(m):
        fn = m.group(1)
        if fn in shared_files:
            moved[0] += 1
            return f"{base}/{fn}"
        kept.add(fn)
        return "assets/" + fn

    s2 = re.sub(r'assets/([A-Za-z0-9._-]+)', repl, s)

    # add a preconnect hint if there's a <head> and none yet
    if "<head>" in s2 and base not in s2.split("</head>")[0]:
        s2 = s2.replace("<head>", f'<head>\n<link rel="preconnect" href="{base}" crossorigin>', 1)

    io.open(out, "w", encoding="utf-8").write(s2)
    print(f"repointed {moved[0]} shared refs -> {base}")
    print(f"kept local ({len(kept)}): {sorted(kept)}")
    print(f"written: {out}")

if __name__ == "__main__":
    main()
