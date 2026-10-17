#!/bin/zsh
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
LOCK="$HOME/.local/state/recomp-index-refresh.lock"
TMP="$(mktemp "${TMPDIR:-/tmp}/recomp-index-catalog.XXXXXX")"

cleanup() {
  rm -f "$TMP"
  rmdir "$LOCK" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if ! mkdir "$LOCK" 2>/dev/null; then
  echo "REFRESH_ALREADY_RUNNING"
  exit 0
fi

cd "$ROOT"

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "REFRESH_REFUSED_DIRTY_WORKTREE" >&2
  exit 2
fi

git fetch origin main
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse origin/main)"
if [[ "$local_sha" != "$remote_sha" ]]; then
  if git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
    git merge --ff-only origin/main
  else
    echo "REFRESH_REFUSED_DIVERGED_HISTORY" >&2
    exit 3
  fi
fi

python3 scripts/refresh.py --output "$TMP"

if python3 - src/data/catalog.json "$TMP" <<'PY'
import json, sys
old=json.load(open(sys.argv[1]))
new=json.load(open(sys.argv[2]))
old.pop("generated_at", None)
new.pop("generated_at", None)
raise SystemExit(0 if old == new else 1)
PY
then
  echo "REFRESH_NO_DATA_CHANGE"
  exit 0
fi

mv "$TMP" src/data/catalog.json
TMP="/dev/null"

python3 tests/test_catalog.py
python3 .home/build.py

git add src/data/catalog.json
stamp="$(date -u '+%Y-%m-%d %H:%MZ')"
git commit -m "data: refresh catalog $stamp"

git fetch origin main
if [[ "$(git rev-parse HEAD^)" != "$(git rev-parse origin/main)" ]]; then
  echo "REFRESH_REFUSED_REMOTE_MOVED" >&2
  exit 4
fi

git push origin HEAD:main
echo "REFRESH_PUBLISHED $(git rev-parse HEAD)"
