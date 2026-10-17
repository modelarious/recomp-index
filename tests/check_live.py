#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import urllib.request

APP = "http://home.lan/apps/recomp-index/"
STATIC_CATALOG = "http://home.lan/apps.json"
DEPLOY_CATALOG = "http://home.lan/deployment/catalog.json"
STATUS = "http://home.lan/deployment/status.json"

with urllib.request.urlopen(APP, timeout=10) as r:
    html = r.read().decode("utf-8", "replace")
    assert r.status == 200
assert "Recomp Index" in html

with urllib.request.urlopen(APP + "data/catalog.json", timeout=20) as r:
    data = json.load(r)
assert data["schema"] == "recomp-index/v1"
assert data["summary"]["projects"] > 1000

# Recomp Index must not be a hand-maintained legacy Home card.
with urllib.request.urlopen(STATIC_CATALOG, timeout=10) as r:
    static = json.load(r)
assert not any(x.get("id") == "recomp-index" for x in static.get("apps", []))

# It must be present through Home's project-owned auto-discovery catalog.
with urllib.request.urlopen(DEPLOY_CATALOG, timeout=10) as r:
    deployment = json.load(r)
cards = [x for x in deployment.get("projects", []) if x.get("id") == "recomp-index"]
assert len(cards) == 1, cards
card = cards[0]
assert card.get("repo", "modelarious/recomp-index") == "modelarious/recomp-index"
assert card.get("state") == "green", card
assert card.get("url") == "/apps/recomp-index/", card

with urllib.request.urlopen(STATUS, timeout=10) as r:
    status = json.load(r)
rows = [row for row in status.get("projects", []) if row.get("repo") == "modelarious/recomp-index"]
assert len(rows) == 1, rows
row = rows[0]
assert row.get("state") == "green", row
assert row.get("live"), row
assert row["live"].get("sha") == row.get("desired_sha"), row

remote = subprocess.check_output(
    ["git", "ls-remote", "origin", "refs/heads/main"], text=True
).split()[0]
assert row.get("desired_sha") == remote, (row, remote)

print("LIVE_HOME_PASS")
