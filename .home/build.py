from __future__ import annotations
import hashlib
import shutil
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DIST = ROOT / "dist"
VERIFY = ROOT / ".home" / ".verify-dist"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.values.append(value)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_tree(root: Path) -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not publishable: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = sha256(path)
    if "index.html" not in files:
        raise ValueError("src/index.html is required")
    return files
def validate_links(root: Path) -> None:
    for html in root.rglob("*.html"):
        parser = Links()
        text = html.read_text(errors="replace")
        if 'name="color-scheme" content="dark"' not in text:
            raise ValueError(f"Dark first-paint metadata is required: {html}")
        if 'data-theme="dark"' not in text:
            raise ValueError(f"Dark default is required: {html}")
        parser.feed(text)
        for raw in parser.values:
            if raw.startswith(("#", "//", "data:", "mailto:", "tel:")):
                continue
            parsed = urllib.parse.urlsplit(raw)
            if parsed.scheme:
                continue
            if parsed.path.startswith("/"):
                raise ValueError(f"Root-relative URL breaks Home base paths: {html}: {raw}")
            if not parsed.path:
                continue
            target = (html.parent / urllib.parse.unquote(parsed.path)).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                raise ValueError(f"Link escapes published tree: {html}: {raw}") from None
            if parsed.path.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                raise ValueError(f"Missing relative link target: {html}: {raw}")

def assemble(destination: Path) -> dict[str, str]:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(SOURCE, destination)
    files = validate_tree(destination)
    validate_links(destination)
    return files

def main() -> None:
    if not SOURCE.is_dir():
        raise ValueError("src/ is required")
    first = assemble(DIST)
    second = assemble(VERIFY)
    try:
        if first != second:
            raise ValueError("Build output is not deterministic")
    finally:
        shutil.rmtree(VERIFY, ignore_errors=True)
    fingerprint = hashlib.sha256(
        "\n".join(f"{name} {digest}" for name, digest in sorted(first.items())).encode()
    ).hexdigest()
    print(f"HOME_BUILD_VERIFIED files={len(first)} sha256={fingerprint}")

if __name__ == "__main__":
    main()
