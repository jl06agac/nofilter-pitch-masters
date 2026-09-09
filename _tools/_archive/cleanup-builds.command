#!/bin/bash
# cleanup-builds.command — double-click in Finder to delete all leftover
# _netlify-build/ folders across every pitch. Safe: these are disposable.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$DIR")"
echo "Sweeping for leftover _netlify-build folders under:"
echo "  $ROOT"
echo ""
FOUND=$(find "$ROOT" -type d -name "_netlify-build" 2>/dev/null)
if [ -z "$FOUND" ]; then
  echo "Nothing to clean — no build folders found."
else
  echo "Deleting:"
  echo "$FOUND" | sed 's/^/   /'
  find "$ROOT" -type d -name "_netlify-build" -exec rm -rf {} + 2>/dev/null
  echo ""
  echo "Done. All build folders removed."
fi
echo ""
echo "(This window can be closed.)"
