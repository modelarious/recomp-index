# Recomp Index — delivery gates

G1: Source-backed aggregation
CHECK: python3 scripts/refresh.py --offline-fixture-test
EXPECT: REFRESH_FIXTURES_PASS
Manual acceptance: production refresh ingests at least two independent ecosystem sources, preserves source provenance, and emits canonical game/project records.

G2: Searchable consumer interface
CHECK: python3 tests/test_catalog.py
EXPECT: CATALOG_TESTS_PASS
Manual acceptance: dark-mode UI supports text search plus platform/type/status filters and exposes project provenance/links without requiring users to understand source-specific schemas.

G3: Deterministic static build
CHECK: python3 .home/build.py
EXPECT: HOME_BUILD_VERIFIED
Manual acceptance: build emits dist/index.html and a normalized catalog with no external runtime dependency for core browsing.

G4: Live Home deployment
CHECK: python3 tests/check_live.py
EXPECT: LIVE_HOME_PASS
Manual acceptance: http://home.lan/apps/recomp-index/ serves the current build and the Home landing page exposes a launch card.

G5: Versioned project source
CHECK: git status --porcelain=v1 && git rev-parse --verify HEAD
EXPECT: HEAD
Manual acceptance: implementation, source adapters, tests, deployment metadata, and operating docs are committed locally; public upstream publication is attempted separately and must not block the working Home deployment.
