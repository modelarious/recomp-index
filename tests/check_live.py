#!/usr/bin/env python3
from __future__ import annotations
import json
import urllib.request

URL = "http://home.lan/apps/recomp-index/"
with urllib.request.urlopen(URL, timeout=10) as r:
    html = r.read().decode("utf-8", "replace")
    assert r.status == 200
assert "Recomp Index" in html

with urllib.request.urlopen(URL + "data/catalog.json", timeout=20) as r:
    data = json.load(r)
assert data["schema"] == "recomp-index/v1"
assert data["summary"]["projects"] > 1000

with urllib.request.urlopen("http://home.lan/", timeout=10) as r:
    home = r.read().decode("utf-8", "replace")
assert "Recomp Index" in home
print("LIVE_HOME_PASS")
