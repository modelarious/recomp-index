#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "src" / "data" / "catalog.json"
USER_AGENT = "Mozilla/5.0 (compatible; RecompIndex/0.1; +https://github.com/modelarious/recomp-index)"

SOURCES = {
    "awesome-decomp-games": "https://raw.githubusercontent.com/SubmitGame/awesome-decomp-games/main/data/games.json",
    "recomp.fyi": "https://recomp.fyi/",
    "recomp-software-recomp": "https://www.recompsoftware.com/recompiled-games-list/",
    "recomp-software-decomp": "https://www.recompsoftware.com/decompiled-games-list/",
}

SOURCE_PRIORITY = {
    "recomp.fyi:claimed": 100,
    "recomp.fyi": 80,
    "awesome-decomp-games": 70,
    "recomp-software-recomp": 50,
    "recomp-software-decomp": 50,
}

STATUS_RANK = {
    "complete": 6,
    "released": 5,
    "playable": 4,
    "in-progress": 3,
    "exploring": 2,
    "paused": 1,
    "unknown": 0,
}

def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", "replace")

def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "unknown"

def text_only(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(fragment)).strip()

def attr(fragment: str, name: str) -> str | None:
    m = re.search(rf'\b{name}="([^"]*)"', fragment, re.I)
    return html_lib.unescape(m.group(1)) if m else None

def normalize_platform(value: str | None) -> str:
    if not value:
        return "Unknown"
    value = re.sub(r"\s+", " ", value).strip()
    aliases = {
        "Nintendo 64": "N64",
        "Nintendo DS": "NDS",
        "Nintendo GameCube": "GameCube",
        "PlayStation": "PS1",
        "PlayStation 1": "PS1",
        "PlayStation 2": "PS2",
        "PlayStation 3": "PS3",
        "PlayStation 4": "PS4",
        "Xbox360": "Xbox 360",
        "Game Boy Advance": "GBA",
        "Game Boy Color": "GBC",
        "Game Boy": "GB",
        "Super Nintendo": "SNES",
        "Super Famicom": "SNES",
        "PC": "PC (Windows)",
        "Windows": "PC (Windows)",
        "MS-DOS": "PC (DOS)",
    }
    return aliases.get(value, value)

def normalize_type(value: str | None) -> str:
    value = (value or "").lower().strip()
    if "recomp" in value:
        return "recomp"
    if "decomp" in value or "disassembl" in value:
        return "decomp"
    if "port" in value or "remake" in value or "recreation" in value or "rewrite" in value:
        return "port"
    return value or "other"

def normalize_status(value: str | None) -> str:
    value = (value or "").lower().strip()
    if not value:
        return "unknown"
    if "complete" in value or value == "100%":
        return "complete"
    if "released" in value or "release" in value:
        return "released"
    if "playable" in value:
        return "playable"
    if "paused" in value or "stalled" in value or "archiv" in value or "inactive" in value:
        return "paused"
    if "explor" in value or "prototype" in value:
        return "exploring"
    if "wip" in value or "progress" in value or "active" in value:
        return "in-progress"
    return value if value in STATUS_RANK else "unknown"

def parse_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None

def clean_game_title(value: str) -> str:
    value = re.sub(r"\s+\d{4}$", "", value).strip()
    return value or "Unknown game"

def awesome_records(raw: str) -> list[dict]:
    data = json.loads(raw)
    out = []
    for row in data.get("games", []):
        title = (row.get("title") or "").strip()
        repo = (row.get("repo") or "").strip()
        url = row.get("url") or (f"https://github.com/{repo}" if repo else None)
        status = "unknown"
        if row.get("archived") or row.get("inactive"):
            status = "paused"
        elif row.get("progress") in (100, 100.0, "100", "100%"):
            status = "complete"
        elif row.get("release"):
            status = "released"
        elif row.get("play_status"):
            status = normalize_status(str(row.get("play_status")))
        elif row.get("last_commit"):
            status = "in-progress"
        project = repo.split("/")[-1] if repo else title
        out.append({
            "game": title or project,
            "platform": normalize_platform(row.get("platform")),
            "type": normalize_type(row.get("type")),
            "project": project,
            "project_url": url,
            "repo": repo or None,
            "status": status,
            "last_activity": parse_iso_date(row.get("last_commit")),
            "release": row.get("release"),
            "progress": row.get("progress"),
            "toolchain": None,
            "targets": [],
            "claimed": False,
            "made": "AI-flagged" if row.get("ai_flag") else None,
            "stars": row.get("stars"),
            "source": "awesome-decomp-games",
            "source_id": row.get("id"),
            "source_url": SOURCES["awesome-decomp-games"],
            "embedded_sources": row.get("sources") or [],
        })
    return out

def recomp_fyi_records(raw: str) -> list[dict]:
    out = []
    row_re = re.compile(r'<tr class="data-row"(?P<attrs>[^>]*)>(?P<body>.*?)</tr>', re.S | re.I)
    cell_re = re.compile(r"<td(?P<attrs>[^>]*)>(?P<body>.*?)</td>", re.S | re.I)
    for match in row_re.finditer(raw):
        row_attrs = match.group("attrs")
        cells = list(cell_re.finditer(match.group("body")))
        if len(cells) < 10:
            continue
        bodies = [c.group("body") for c in cells]
        game = text_only(bodies[0])
        game_href = attr(bodies[0], "href")
        platform = text_only(bodies[1])
        targets = [x.strip() for x in text_only(bodies[2]).split("/") if x.strip()]
        type_match = re.search(r'data-type="([^"]+)"', bodies[3], re.I)
        work_type = normalize_type(type_match.group(1) if type_match else text_only(bodies[3]))
        toolchain = text_only(bodies[4]) or None
        project_href = attr(bodies[5], "href")
        project_text = text_only(re.sub(r'<span class="(?:chip|project-by)[^"]*"[^>]*>.*?</span>', "", bodies[5], flags=re.S | re.I))
        status_match = re.search(r'data-status="([^"]+)"', bodies[6], re.I)
        status = normalize_status(status_match.group(1) if status_match else text_only(bodies[6]))
        version = text_only(bodies[7]) or None
        last_activity = parse_iso_date(text_only(bodies[8]))
        claimed = "claim-tag" in bodies[9]
        out.append({
            "game": game,
            "platform": normalize_platform(platform),
            "type": work_type,
            "project": project_text or game,
            "project_url": project_href,
            "repo": github_repo(project_href),
            "status": status,
            "last_activity": last_activity,
            "release": version,
            "progress": None,
            "toolchain": toolchain,
            "targets": targets,
            "claimed": claimed,
            "made": None,
            "stars": None,
            "source": "recomp.fyi",
            "source_id": attr(row_attrs, "data-id"),
            "source_url": urllib.parse.urljoin(SOURCES["recomp.fyi"], game_href or ""),
            "activity": attr(row_attrs, "data-activity"),
            "embedded_sources": [],
        })
    return out

def recomp_software_records(raw: str, source: str, work_type: str) -> list[dict]:
    out = []
    current_platform = "Unknown"
    token_re = re.compile(r"(<h2\b.*?</h2>|<table\b.*?</table>)", re.S | re.I)
    for token in token_re.findall(raw):
        if token.lower().startswith("<h2"):
            heading = text_only(token)
            if heading and len(heading) < 80:
                current_platform = normalize_platform(heading)
            continue
        for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", token, re.S | re.I):
            cells = re.findall(r"<td\b[^>]*>(.*?)</td>", tr, re.S | re.I)
            if len(cells) != 6:
                continue
            project = text_only(cells[0])
            href = attr(cells[0], "href")
            original = clean_game_title(text_only(cells[1]))
            status_text = text_only(cells[2])
            made = text_only(cells[3]) or None
            latest_text = text_only(cells[4])
            date_match = re.search(r"([A-Z][a-z]{2} \d{1,2}, \d{4})", latest_text)
            last_activity = parse_iso_date(date_match.group(1) if date_match else None)
            progress_match = re.search(r"(\d+(?:\.\d+)?)%", status_text)
            stars_text = text_only(cells[5]).lower().replace(",", "")
            try:
                stars = int(float(stars_text[:-1]) * 1000) if stars_text.endswith("k") else int(stars_text)
            except ValueError:
                stars = None
            project_url = urllib.parse.urljoin("https://www.recompsoftware.com", href or "")
            out.append({
                "game": original,
                "platform": current_platform,
                "type": work_type,
                "project": project,
                "project_url": project_url,
                "repo": None,
                "status": normalize_status(status_text),
                "last_activity": last_activity,
                "release": latest_text.split(" ")[0] if latest_text and latest_text != "—" else None,
                "progress": float(progress_match.group(1)) if progress_match else None,
                "toolchain": None,
                "targets": [],
                "claimed": False,
                "made": made,
                "stars": stars,
                "source": source,
                "source_id": href.strip("/") if href else slugify(project),
                "source_url": project_url,
                "embedded_sources": [],
            })
    return out

def github_repo(url: str | None) -> str | None:
    if not url:
        return None
    p = urllib.parse.urlparse(url)
    if p.netloc.lower() not in {"github.com", "www.github.com"}:
        return None
    bits = [b for b in p.path.strip("/").split("/") if b]
    if len(bits) >= 2:
        return f"{bits[0]}/{bits[1].removesuffix('.git')}"
    return None

def project_key(record: dict) -> str:
    repo = record.get("repo") or github_repo(record.get("project_url"))
    if repo:
        return "repo:" + repo.lower()
    return "sig:" + ":".join([
        slugify(record.get("game", "")),
        slugify(record.get("project", "")),
        normalize_type(record.get("type")),
    ])

def source_priority(record: dict) -> int:
    source = record["source"]
    if source == "recomp.fyi" and record.get("claimed"):
        return SOURCE_PRIORITY["recomp.fyi:claimed"]
    return SOURCE_PRIORITY.get(source, 0)

def merge_records(records: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    fields = ["game", "platform", "type", "project", "project_url", "repo", "status",
              "last_activity", "release", "progress", "toolchain", "targets", "made", "stars"]
    for record in records:
        key = project_key(record)
        priority = source_priority(record)
        if key not in merged:
            merged[key] = {
                "id": slugify(key),
                "_field_priority": {},
                "evidence": [],
                "embedded_sources": set(),
            }
        item = merged[key]
        for field in fields:
            value = record.get(field)
            if value in (None, "", [], "Unknown", "unknown"):
                continue
            existing_priority = item["_field_priority"].get(field, -1)
            if priority >= existing_priority:
                item[field] = value
                item["_field_priority"][field] = priority
        item["embedded_sources"].update(record.get("embedded_sources") or [])
        item["evidence"].append({
            "source": record["source"],
            "source_url": record.get("source_url"),
            "source_id": record.get("source_id"),
            "claimed": bool(record.get("claimed")),
            "status": record.get("status"),
            "type": record.get("type"),
            "platform": record.get("platform"),
            "last_activity": record.get("last_activity"),
        })
    out = []
    for item in merged.values():
        item.pop("_field_priority", None)
        item["embedded_sources"] = sorted(item["embedded_sources"])
        values = defaultdict(set)
        for ev in item["evidence"]:
            for field in ("status", "type", "platform"):
                val = ev.get(field)
                if val and val not in {"unknown", "Unknown"}:
                    values[field].add(val)
        item["conflicts"] = {k: sorted(v) for k, v in values.items() if len(v) > 1}
        item.setdefault("game", item.get("project", "Unknown game"))
        item.setdefault("platform", "Unknown")
        item.setdefault("type", "other")
        item.setdefault("project", item["game"])
        item.setdefault("status", "unknown")
        item.setdefault("targets", [])
        item.setdefault("evidence", [])
        out.append(item)
    return out

def group_games(projects: list[dict]) -> list[dict]:
    buckets = {}
    for p in projects:
        game_id = slugify(p["game"]) + "--" + slugify(p.get("platform", "Unknown"))
        bucket = buckets.setdefault(game_id, {
            "id": game_id,
            "title": p["game"],
            "platform": p.get("platform", "Unknown"),
            "projects": [],
        })
        bucket["projects"].append(p)
    games = []
    for g in buckets.values():
        g["projects"].sort(key=lambda p: (
            p.get("last_activity") or "",
            STATUS_RANK.get(p.get("status", "unknown"), 0),
            p.get("project", "").lower(),
        ), reverse=True)
        g["project_count"] = len(g["projects"])
        g["types"] = sorted({p.get("type", "other") for p in g["projects"]})
        g["statuses"] = sorted({p.get("status", "unknown") for p in g["projects"]})
        g["sources"] = sorted({ev["source"] for p in g["projects"] for ev in p.get("evidence", [])})
        g["last_activity"] = max((p.get("last_activity") or "" for p in g["projects"]), default="") or None
        g["best_status"] = max(g["statuses"], key=lambda s: STATUS_RANK.get(s, 0), default="unknown")
        g["has_conflict"] = any(bool(p.get("conflicts")) for p in g["projects"])
        games.append(g)
    games.sort(key=lambda g: (g.get("last_activity") or "", g["title"].lower()), reverse=True)
    return games

def build_catalog(records: list[dict]) -> dict:
    projects = merge_records(records)
    games = group_games(projects)
    platforms = defaultdict(int)
    types = defaultdict(int)
    statuses = defaultdict(int)
    source_counts = defaultdict(int)
    for p in projects:
        platforms[p.get("platform", "Unknown")] += 1
        types[p.get("type", "other")] += 1
        statuses[p.get("status", "unknown")] += 1
        for ev in p.get("evidence", []):
            source_counts[ev["source"]] += 1
    return {
        "schema": "recomp-index/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "games": len(games),
            "projects": len(projects),
            "source_records": len(records),
            "platforms": len(platforms),
            "sources": len(source_counts),
            "conflicted_projects": sum(1 for p in projects if p.get("conflicts")),
        },
        "sources": [
            {"id": k, "url": SOURCES[k], "records": source_counts.get(k, 0)}
            for k in SOURCES
        ],
        "facets": {
            "platforms": sorted(platforms.items(), key=lambda x: (-x[1], x[0])),
            "types": sorted(types.items(), key=lambda x: (-x[1], x[0])),
            "statuses": sorted(statuses.items(), key=lambda x: (-x[1], x[0])),
        },
        "games": games,
    }

def refresh(output: Path) -> dict:
    records = []
    awesome_raw = fetch_text(SOURCES["awesome-decomp-games"])
    records.extend(awesome_records(awesome_raw))
    fyi_raw = fetch_text(SOURCES["recomp.fyi"])
    records.extend(recomp_fyi_records(fyi_raw))
    sw_recomp = fetch_text(SOURCES["recomp-software-recomp"])
    records.extend(recomp_software_records(sw_recomp, "recomp-software-recomp", "recomp"))
    sw_decomp = fetch_text(SOURCES["recomp-software-decomp"])
    records.extend(recomp_software_records(sw_decomp, "recomp-software-decomp", "decomp"))
    catalog = build_catalog(records)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    return catalog

def fixture_test() -> None:
    fyi = '''<table><tbody>
<tr class="data-row" data-id="wave-race" data-activity="active"><td class="cell-game"><a href="/game/wave-race-64-n64">Wave Race 64</a></td><td><span class="system-tag">N64</span></td><td class="cell-targets">Windows / Linux</td><td><span class="type-tag" data-type="recomp">recomp</span></td><td class="cell-tool">N64recomp</td><td class="cell-project"><a href="https://github.com/example/wave">Wave Recompiled</a></td><td><span class="status" data-status="playable">Playable</span></td><td class="cell-version">v0.1</td><td class="cell-mono"><span class="commit">2026-10-16</span></td><td><span class="claim-tag">claimed</span></td></tr>
</tbody></table>'''
    rows = recomp_fyi_records(fyi)
    assert len(rows) == 1 and rows[0]["claimed"] and rows[0]["type"] == "recomp"
    assert rows[0]["repo"] == "example/wave" and rows[0]["status"] == "playable"
    awesome = json.dumps({"games": [{"title":"Wave Race 64","platform":"N64","type":"static recompilation","url":"https://github.com/example/wave","repo":"example/wave","last_commit":"2026-10-15T10:00:00Z","release":"v0.1","sources":["test"]}]})
    combined = build_catalog(awesome_records(awesome) + rows)
    assert combined["summary"]["projects"] == 1
    assert combined["summary"]["games"] == 1
    assert len(combined["games"][0]["projects"][0]["evidence"]) == 2
    print("REFRESH_FIXTURES_PASS")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline-fixture-test", action="store_true")
    args = parser.parse_args()
    if args.offline_fixture_test:
        fixture_test()
        return 0
    catalog = refresh(args.output)
    s = catalog["summary"]
    print(f"REFRESH_OK games={s['games']} projects={s['projects']} source_records={s['source_records']} sources={s['sources']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
