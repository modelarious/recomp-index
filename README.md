# Recomp Index

A public, source-backed search interface for game decompilation, static recompilation, and source-port projects.

## What it does

Recomp Index aggregates public reverse-engineering trackers into one searchable catalog. Duplicate GitHub repositories collapse into one project. Conflicting upstream claims remain attached as evidence instead of being silently overwritten.

Current direct adapters:

- awesome-decomp-games
- recomp.fyi
- Recomp Software — recompiled games
- Recomp Software — decompiled games

`awesome-decomp-games` itself carries provenance from additional ecosystem lists, so the normalized catalog exposes both the direct adapter and embedded upstream-source evidence.

## Architecture

The project follows the normal `modelarious/home-service-template` path.

1. `scripts/refresh.py` fetches and normalizes upstream public data into `src/data/catalog.json`.
2. `scripts/refresh_and_publish.sh` runs locally on the Mac Studio every three hours. It refreshes, verifies, commits, and pushes **source only** when the normalized data actually changed.
3. The existing Home controller discovers the new Git commit from `home-service.json`, builds it on Punchcard, creates the immutable release receipt/tag, and atomically publishes `/apps/recomp-index/`.
4. Recomp Index never writes Home's live web root itself.

There is no AI in ingestion, normalization, search, scheduling, or deployment, and no scheduled hosted GitHub Actions workflow.

## Refresh manually

```sh
python3 scripts/refresh.py
python3 tests/test_catalog.py
python3 .home/build.py
```

To run the production source refresh/publish path:

```sh
./scripts/refresh_and_publish.sh
```

To install or reinstall the local three-hour LaunchAgent:

```sh
./deploy/install-macos-refresh.sh
```

## Data model

Upstream trackers are evidence, not canonical truth. Repository identity is the strongest deduplication key. Claimed recomp.fyi metadata outranks unclaimed scraped metadata, while every source observation remains attached to the normalized project. The UI exposes source disagreements.

## Verification

```sh
python3 scripts/refresh.py --offline-fixture-test
python3 tests/test_catalog.py
python3 tests/test_refresh_contract.py
python3 .home/build.py
python3 tests/check_repository.py
python3 tests/check_live.py
```

The public repository is `modelarious/recomp-index`; the private Home deployment remains an independently verified consumer of that source.
