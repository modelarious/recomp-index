from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DIST = ROOT / "dist"
VERIFY = ROOT / ".home" / ".verify-dist"

REQUIRED = ("index.html", "styles.css", "app.js", "data/catalog.json")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(root: Path) -> dict[str, str]:
    for rel in REQUIRED:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"missing required artifact: {rel}")
    catalog = json.loads((root / "data/catalog.json").read_text())
    if catalog.get("schema") != "recomp-index/v1":
        raise SystemExit("unexpected catalog schema")
    summary = catalog.get("summary", {})
    if summary.get("games", 0) < 1 or summary.get("projects", 0) < 1:
        raise SystemExit("catalog is empty")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"symlink not publishable: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = sha256(path)
    return files

def assemble(destination: Path) -> dict[str, str]:
    shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(SOURCE, destination)
    return validate(destination)

def main() -> None:
    first = assemble(DIST)
    second = assemble(VERIFY)
    try:
        if first != second:
            raise SystemExit("build is not deterministic")
    finally:
        shutil.rmtree(VERIFY, ignore_errors=True)
    digest = hashlib.sha256("\n".join(f"{k} {v}" for k,v in sorted(first.items())).encode()).hexdigest()
    print(f"HOME_BUILD_VERIFIED files={len(first)} sha256={digest}")

if __name__ == "__main__":
    main()
