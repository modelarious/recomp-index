#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
REMOTE="modelarious@punchcard"
LIVE_ROOT="/Volumes/CentralStorage/ai_os/infra/dns_stack/static/html/home/apps/recomp-index"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/recomp-index.XXXXXX")"
REMOTE_STAGE="${LIVE_ROOT}.stage-${STAMP}"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT INT TERM

mkdir -p "$TMP/data"
cp "$ROOT/src/index.html" "$ROOT/src/styles.css" "$ROOT/src/app.js" "$TMP/"
python3 "$ROOT/scripts/refresh.py" --output "$TMP/data/catalog.json"

python3 - "$TMP/data/catalog.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["schema"]=="recomp-index/v1"
assert d["summary"]["sources"] >= 4
assert d["summary"]["projects"] > 1000
print("DEPLOY_CATALOG_VALID")
PY

ssh -o BatchMode=yes "$REMOTE" "rm -rf '$REMOTE_STAGE' 2>/dev/null || true; mkdir '$REMOTE_STAGE'; chmod 755 '$REMOTE_STAGE'"
rsync -rlt --no-perms --no-owner --no-group --delete "$TMP/" "$REMOTE:$REMOTE_STAGE/"

ssh -o BatchMode=yes "$REMOTE" "
set -eu
live='$LIVE_ROOT'
stage='$REMOTE_STAGE'
find "\$stage" -type d -exec chmod 755 {} +
find "\$stage" -type f -exec chmod 644 {} +
if [ -e "\$live" ]; then
  if [ -r "\$live/index.html" ]; then
    old="\${live}.previous"
    rm -rf "\$old" 2>/dev/null || true
  else
    old="\${live}.broken-$STAMP"
  fi
  mv "\$live" "\$old"
else
  old=''
fi
if mv "\$stage" "\$live"; then
  [ -z "\$old" ] || rm -rf "\$old" 2>/dev/null || true
else
  [ -z "\$old" ] || [ -e "\$live" ] || mv "\$old" "\$live"
  exit 1
fi
test -r "\$live/index.html"
test -r "\$live/data/catalog.json"
"
printf 'RECOMP_INDEX_DEPLOYED %s\n' "$STAMP"
