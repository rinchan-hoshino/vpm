#!/usr/bin/env python3
import hashlib
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "Website"
LISTING_URL = "https://vpm.k-neco.com/index.json"
PACKAGE_ID = "com.the-cattail.afk-motion-patcher"
PACKAGE_VERSION = "1.0.0"
PACKAGE_URL = (
    "https://github.com/k-neco-lab/afk-motion-patcher/releases/download/v1.0.0/"
    "com.the-cattail.afk-motion-patcher-1.0.0.zip"
)
PACKAGE_SHA256 = "6af2397ea1e87a899b0b5a690c4754e5f1d85102297299933dd4b76be449cec2"
OLD_VPM_PREFIX = "https://k-neco.com" + "/vpm"


def main() -> None:
    source = json.loads((ROOT / "source.json").read_text())
    listing = json.loads((WEBSITE / "index.json").read_text())
    html = (WEBSITE / "index.html").read_text()
    app = (WEBSITE / "app.js").read_text()
    styles = (WEBSITE / "styles.css").read_text()

    assert (WEBSITE / "CNAME").read_text().strip() == "vpm.k-neco.com"
    assert source["url"] == LISTING_URL
    assert listing["url"] == LISTING_URL
    assert source["name"] == "THE_cattail VPM"
    assert source["author"]["name"] == "THE_cattail"
    assert listing["name"] == "THE_cattail VPM"
    assert listing["author"] == "THE_cattail"
    assert listing["id"] == "com.the-cattail.vpm"
    assert set(listing["packages"]) == {PACKAGE_ID}

    version = listing["packages"][PACKAGE_ID]["versions"][PACKAGE_VERSION]
    assert version["author"]["name"] == "THE_cattail"
    assert version["url"] == PACKAGE_URL
    assert version["repo"] == LISTING_URL
    assert version["zipSHA256"] == PACKAGE_SHA256

    for text in (html, app):
        assert LISTING_URL in text
        assert PACKAGE_ID in text
        assert "AFK Motion Patcher" in text
        assert "THE_cattail" in text
        assert "K-NECO VPM" not in text
        assert "猫尾草" not in text
        assert OLD_VPM_PREFIX not in text

    assert "@fluentui/web-components@2.6.1" in html
    assert 'id="vccAddRepoButton"' in html
    assert 'id="packageGrid"' in html
    assert "rowPackageInfoButton" in html
    assert "@media (max-width: 640px)" in styles
    assert 'fluent-data-grid-row[data-package-id]' in styles

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            assert OLD_VPM_PREFIX not in text, f"old VPM URL remains in {path}"

    package_path = os.environ.get("VPM_PACKAGE_FILE")
    if package_path:
        package_bytes = Path(package_path).read_bytes()
    else:
        with urllib.request.urlopen(PACKAGE_URL, timeout=30) as response:
            package_bytes = response.read()
    assert hashlib.sha256(package_bytes).hexdigest() == PACKAGE_SHA256

    print("VPM listing validation passed")


if __name__ == "__main__":
    main()
