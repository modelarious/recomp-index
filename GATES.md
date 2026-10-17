# Recomp Index completion gates

G1: Catalog refresh is deterministic and source-backed.
CHECK: python3 scripts/refresh.py --offline-fixture-test && python3 tests/test_catalog.py
EXPECT: CATALOG_TESTS_PASS

G2: Static Home build is valid.
CHECK: python3 .home/build.py
EXPECT: HOME_BUILD_VERIFIED

G3: Refresh automation publishes source, never Home bytes directly.
CHECK: python3 tests/test_refresh_contract.py
EXPECT: REFRESH_CONTRACT_PASS

G4: Public repository is the canonical source and descends from home-service-template.
CHECK: python3 tests/check_repository.py
EXPECT: REPOSITORY_PASS

G5: Home auto-deploy owns the live app and reports green.
CHECK: python3 tests/check_live.py
EXPECT: LIVE_HOME_PASS
