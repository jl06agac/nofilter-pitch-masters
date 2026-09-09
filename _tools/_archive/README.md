# _tools/_archive — legacy one-off scripts (kept, not deleted)

These are single-purpose Python/command scripts from earlier build sessions. None are referenced
by any current doc or workflow — the only live tool is `../nf-stamp.mjs` (the Part 2 stamp engine).
Kept here in case one is ever useful again.

- `add_moneyfm.py`, `add_pulse_stop.py`, `fix_pulse.py` — one-off HTML patch scripts for specific pitches.
- `cleanup_orphans.py`, `dedupe_assets.py`, `tidy_pitch.py`, `cleanup-builds.command` — housekeeping utilities.
- `netlify_pack.py`, `repoint-shared.py` — deploy/asset-path helpers (superseded by the always-URL model).

The base64 bundler (`bundle.py` / `unbundle.py`) lives in `../../_archive/bundler/`, not here.
