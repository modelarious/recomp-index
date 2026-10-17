# Recomp Index

A unified, source-backed search interface for game decompilation, static recompilation and source-port projects.

## What it does

Recomp Index ingests multiple public ecosystem trackers, normalizes duplicate repositories into a common project model, groups projects by game/platform, and preserves every upstream claim as provenance. Conflicting claims are shown rather than silently resolved.

Current adapters:

- awesome-decomp-games
- recomp.fyi
- Recomp Software — recompiled games
- Recomp Software — decompiled games

The initial production snapshot contains more than 4,000 normalized projects and nearly 3,000 game/platform entries.

## Refresh

```sh
python3 scripts/refresh.py
python3 tests/test_catalog.py
python3 .home/build.py
```

The live Home deployment uses `scripts/refresh_and_deploy.sh`, which refreshes into a temporary tree and atomically replaces only Recomp Index's own published directory.

## Data model

Upstream trackers are evidence, not canonical truth. Repository identity is the strongest deduplication key. Claimed recomp.fyi metadata outranks unclaimed scraped metadata; all source evidence remains attached to the project. The UI exposes disagreements.

No AI model is required for ingestion, normalization, search, or scheduled refresh.
