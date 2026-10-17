#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
script = (root / "scripts" / "refresh_and_publish.sh").read_text()
workflow = root / ".github" / "workflows" / "refresh.yml"
old_script = root / "scripts" / "refresh_and_deploy.sh"

assert not workflow.exists(), "hosted scheduled workflow must not be used"
assert not old_script.exists(), "direct Home deploy script must be removed"
assert "git push origin HEAD:main" in script
assert "scripts/refresh.py" in script
assert "tests/test_catalog.py" in script
assert ".home/build.py" in script

for forbidden in (
    "home.lan",
    "/Volumes/CentralStorage",
    "rsync ",
    "ssh ",
    "home-deploy",
):
    assert forbidden not in script, f"refresh automation must not deploy Home directly: {forbidden}"

print("REFRESH_CONTRACT_PASS")
