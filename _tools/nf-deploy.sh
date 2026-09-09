#!/usr/bin/env bash
# nf-deploy.sh — deploy a NoFilter client site to Netlify, with a guard rail.
#
# WHY THIS EXISTS
#   A Netlify deploy REPLACES the entire contents of the target site. Deploy the wrong
#   folder to the right site — or the right folder to the wrong site — and everything
#   already there is gone. That is how the shared media site got wiped: a deploy resolved
#   to site 7e2274d8-… (Clients/_shared) and replaced it with something else.
#
#   The Netlify CLI resolves a target by walking UP the directory tree looking for
#   .netlify/state.json. It will happily pick up a link you forgot about. This script
#   never lets it: the target site is passed explicitly, checked against a blocklist of
#   sites that must never receive a client deploy, and shown to you for confirmation
#   before a single byte moves.
#
# USAGE
#   ./nf-deploy.sh <deploy-folder> <site-name>
#   ./nf-deploy.sh "Clients/Workplaces/Sprinklr Gulf/sprinklr-gulf-deploy" nofilter-sprinklr
#
# The token: the script asks for it (hidden) the first time and can save it to
#   ~/.nofilter-netlify-token, mode 600. You never put it on a command line again.
#   Never paste a live token into a chat thread.

set -euo pipefail

DIR="${1:?usage: nf-deploy.sh <deploy-folder> <site-name>}"
SITE_NAME="${2:?usage: nf-deploy.sh <deploy-folder> <site-name>}"
die(){ printf '\n  ABORTED: %s\n\n' "$1" >&2; exit 1; }

# ── the token ─────────────────────────────────────────────────────────────────
# This used to demand NETLIFY_AUTH_TOKEN in the environment, which meant editing a
# token into a command line every single time. That failed three ways in one session:
# the placeholder from an example got pasted verbatim (twice), and a real token ends
# up in shell history where it does not belong.
#
# So the script now finds the token itself, in this order:
#   1. NETLIFY_AUTH_TOKEN, if it is set and is not obviously an example
#   2. ~/.nofilter-netlify-token, saved on a previous run, mode 600
#   3. a hidden prompt — typed or pasted, never echoed, never in history
# Answer the save prompt once and step 3 never happens again.
TOKEN_FILE="$HOME/.nofilter-netlify-token"

# One test, used everywhere: is this an example rather than a credential?
is_placeholder(){
  case "$1" in
    ''|*…*|*...*|'<'*|[Yy][Oo][Uu][Rr]*|*YOUR_*|*_HERE*|*PASTE*|*paste*|*EXAMPLE*|*example*|*xxxx*|'TOKEN'*) return 0 ;;
  esac
  [ ${#1} -lt 20 ] && return 0
  return 1
}

TOKEN="${NETLIFY_AUTH_TOKEN:-}"
if is_placeholder "$TOKEN"; then
  [ -n "$TOKEN" ] && printf '  ignoring NETLIFY_AUTH_TOKEN — that is an example, not a token (%s).\n' "$TOKEN" >&2
  TOKEN=""
  if [ -r "$TOKEN_FILE" ]; then
    TOKEN=$(tr -d ' \t\r\n' < "$TOKEN_FILE")
    if is_placeholder "$TOKEN"; then
      printf '  %s does not contain a usable token — ignoring it.\n' "$TOKEN_FILE" >&2; TOKEN=""
    else
      printf '  using the token saved in %s\n' "$TOKEN_FILE"
    fi
  fi
fi

if is_placeholder "$TOKEN"; then
  [ -t 0 ] || die "no usable token, and no terminal to ask on"
  printf '\n  No Netlify token found. Paste one — it is NOT echoed and NOT saved to history.\n'
  printf '  New token: https://app.netlify.com/user/applications#personal-access-tokens\n'
  printf '  token: '
  read -rs TOKEN < /dev/tty; printf '\n'
  is_placeholder "$TOKEN" && die "that is still an example, not a token"
  printf '  Save it to %s so this never asks again? [y/N] ' "$TOKEN_FILE"
  read -r SAVE < /dev/tty
  case "$SAVE" in
    [Yy]*) ( umask 077; printf '%s\n' "$TOKEN" > "$TOKEN_FILE" ); chmod 600 "$TOKEN_FILE"
           printf '  saved — readable only by you. Delete that file to revoke it locally.\n' ;;
    *)     printf '  not saved.\n' ;;
  esac
fi

# Netlify personal access tokens start nfp_. Warn rather than refuse: the API is the real
# authority and token formats change, but this catches a wrong-service token before upload.
case "$TOKEN" in
  nfp_*) : ;;
  *) printf '  note: that token does not start nfp_ — continuing, but expect a 401 if it is not a Netlify PAT.\n' >&2 ;;
esac

NETLIFY_AUTH_TOKEN="$TOKEN"

API="https://api.netlify.com/api/v1"
AUTH=(-H "Authorization: Bearer ${NETLIFY_AUTH_TOKEN}")

# api <METHOD> <PATH> [curl args...] — returns the body, dies with a readable message on
# any non-2xx. Never use bare `curl -sf` here: it exits silently and the empty string then
# lands in a JSON parser, which is how this script used to fail with a python traceback
# instead of saying "your token is wrong".
api(){
  local method="$1" path="$2"; shift 2
  local body code out
  out=$(curl -s -w $'\n%{http_code}' -X "$method" "${AUTH[@]}" "$@" "$API$path") || {
    printf '\n  ABORTED: could not reach api.netlify.com (no network?).\n\n' >&2; exit 1; }
  code=${out##*$'\n'}; body=${out%$'\n'*}
  case "$code" in
    2*) printf '%s' "$body" ;;
    401|403) printf '\n  ABORTED: Netlify rejected the token (HTTP %s).\n  %s\n\n' "$code" "$body" >&2; exit 1 ;;
    422) printf '\n  ABORTED: Netlify refused that request (HTTP 422) — usually the site name is taken.\n  %s\n\n' "$body" >&2; exit 1 ;;
    *)  printf '\n  ABORTED: Netlify returned HTTP %s.\n  %s\n\n' "$code" "$body" >&2; exit 1 ;;
  esac
}

# ── Sites that must NEVER receive a client-pitch deploy ────────────────────────
# 7e2274d8… is the shared media site. The others are live tools, not pitches.
BLOCKED_IDS="
7e2274d8-fa6c-44b9-9af6-779cc0e89ad0   shared-media-assets
6c64fb40-0d1a-4e80-9095-1a9b212cf981   nofilter-gis-map
c2ab7d04-4ff9-4842-8b12-7a65b80b675f   nf-servicing-scheduler
"
BLOCKED_NAMES="nofilter-shared nofilter-gis-map nf-servicing-scheduler"


# ── 1. sanity-check the folder ────────────────────────────────────────────────
[ -d "$DIR" ]            || die "no such folder: $DIR"
[ -f "$DIR/index.html" ] || die "$DIR has no index.html — that is the deploy artifact name"
case "$(cd "$DIR" && pwd)" in
  */Clients/_shared*) die "refusing to deploy from inside Clients/_shared" ;;
esac
for n in $BLOCKED_NAMES; do
  [ "$SITE_NAME" = "$n" ] && die "'$SITE_NAME' is a protected site, not a client pitch"
done

FILES=$(find "$DIR" -type f | wc -l | tr -d ' ')
SIZE=$(du -sh "$DIR" | cut -f1)

# ── 2. resolve the site by NAME, create it only if it does not exist ──────────
api GET "/user" >/dev/null   # fail fast and loudly if the token is bad
SITE_JSON=$(api GET "/sites?filter=all&name=$SITE_NAME")
SITE_ID=$(printf '%s' "$SITE_JSON" | python3 -c '
import json,sys
try: sites=json.load(sys.stdin)
except Exception: sites=[]
name=sys.argv[1]
for s in sites:
    if s.get("name")==name: print(s["site_id"]); break
' "$SITE_NAME")

if [ -z "${SITE_ID:-}" ]; then
  printf '  site "%s" does not exist yet — creating it.\n' "$SITE_NAME"
  SITE_ID=$(api POST "/sites" -H "Content-Type: application/json" -d "{\"name\":\"$SITE_NAME\"}" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["site_id"])')
fi
[ -n "$SITE_ID" ] || die "could not resolve or create site '$SITE_NAME'"

# ── 3. the guard: never write over a protected site ───────────────────────────
while read -r id label; do
  [ -z "$id" ] && continue
  if [ "$SITE_ID" = "$id" ]; then
    die "target resolved to $id ($label). That site must never receive a client deploy."
  fi
done <<< "$BLOCKED_IDS"

# ── 4. show the target and make the human agree to it ─────────────────────────
INFO=$(api GET "/sites/$SITE_ID")
URL=$(printf '%s' "$INFO" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("ssl_url") or json.load(sys.stdin).get("url",""))' 2>/dev/null || echo "?")

cat <<EOF

  ────────────────────────────────────────────────────────────
   DEPLOY  $FILES files · $SIZE
     from  $DIR
       to  $SITE_NAME
           $SITE_ID
           $URL

   This REPLACES everything currently on that site.
  ────────────────────────────────────────────────────────────

EOF
printf '  Type the site name to confirm: '
read -r CONFIRM
# Strip surrounding whitespace and trailing punctuation before comparing. The point of
# this gate is "did a human read the box and agree to that site", not "can a human avoid
# copying the comma out of a chat message" — a stray , . ; or quote is agreement, not a
# mismatch, and failing it just makes the human run the whole thing again.
CONFIRM=$(printf '%s' "$CONFIRM" | tr -d '[:space:]' | sed 's/[.,;:]*$//; s/^["'"'"']//; s/["'"'"']$//')
[ "$CONFIRM" = "$SITE_NAME" ] || die "confirmation did not match — you typed '$CONFIRM', the site is '$SITE_NAME'"

# ── 5. zip and push ───────────────────────────────────────────────────────────
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT                    # scoped to this temp dir only
ZIP="$TMP/deploy.zip"
( cd "$DIR" && zip -qr "$ZIP" . -x '.*' -x '__MACOSX/*' -x '.netlify/*' )

printf '  uploading…\n'
RESP=$(api POST "/sites/$SITE_ID/deploys" -H "Content-Type: application/zip" --data-binary "@$ZIP")

printf '%s' "$RESP" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("\n  deploy id :", d.get("id"))
print("  state     :", d.get("state"))
print("  live url  :", d.get("ssl_url") or d.get("url"))
print()
'
