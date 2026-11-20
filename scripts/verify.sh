#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -d "$ROOT/.github" ]; then
  echo "[verify] ERROR: .github directory must not exist (GitHub Actions disabled)." >&2
  exit 1
fi

echo "[verify] Running validate_listing.py..."
python3 "$ROOT/tests/validate_listing.py"

echo "[verify] Checking Website/index.json version hygiene and trilingual UI..."
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
index_path = root / "Website" / "index.json"
listing = json.loads(index_path.read_text(encoding="utf-8"))

pkgs = listing.get("packages", {})
assert set(pkgs.keys()) == {"com.the-cattail.afk-motion-patcher"}, f"Unexpected packages: {list(pkgs.keys())}"

versions = pkgs["com.the-cattail.afk-motion-patcher"]["versions"]
assert list(versions.keys()) == ["2.0.0"], f"Expected only 2.0.0, got: {list(versions.keys())}"
for v in versions:
    assert not v.startswith("1."), f"Forbidden 1.x version found: {v}"

raw_index = json.dumps(listing)
for forbidden in ("chocolat-afk-adapters", "k-neco-" + "lab", "k-neco.com" + "/vpm", "v1.0.0"):
    assert forbidden not in raw_index, f"Forbidden string {forbidden!r} in Website/index.json"

html = (root / "Website" / "index.html").read_text(encoding="utf-8")
app = (root / "Website" / "app.js").read_text(encoding="utf-8")
for lang in ("ja", "en", "zh"):
    assert f'data-lang="{lang}"' in html, f"Missing data-lang={lang} in index.html"
    assert f"{lang}:" in app or f'"{lang}"' in app, f"Missing {lang} translations in app.js"

print("[verify] Website/index.json and trilingual copy OK (2.0.0 only).")
PY
