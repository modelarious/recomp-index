#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src" / "data" / "catalog.json"

data = json.loads(CATALOG.read_text())
assert data["schema"] == "recomp-index/v1"
s = data["summary"]
assert s["sources"] >= 4, s
assert s["source_records"] >= s["projects"] >= s["games"] > 1000, s

games = data["games"]
assert len(games) == s["games"]
assert all(g["projects"] for g in games)

# Search-relevant fixtures from the current live union.
titles = [g["title"].lower() for g in games]
assert any("wario land 4" in t for t in titles)
assert any("metroid" in t for t in titles)

# Provenance must survive normalization.
projects = [p for g in games for p in g["projects"]]
assert any(len(p.get("evidence", [])) >= 2 for p in projects)
assert all(p.get("evidence") for p in projects)

# The frontend must remain standalone and dark-first.
html = (ROOT / "src" / "index.html").read_text()
css = (ROOT / "src" / "styles.css").read_text()
js = (ROOT / "src" / "app.js").read_text()
assert "Recomp Index" in html and 'id="query"' in html
assert "color-scheme: dark" in css
assert 'fetch("data/catalog.json"' in js
assert "conflictFilter" in js

subprocess.run(["python3", str(ROOT / "scripts" / "refresh.py"), "--offline-fixture-test"], check=True)
print("CATALOG_TESTS_PASS")
