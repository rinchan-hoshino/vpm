#!/usr/bin/env python3
import hashlib
import json
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
PACKAGE_SHA256 = "e800d54e21b3c5f544b9422c8bb8f1e951dd018a504ecb23bf7c6f973facc173"
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
    assert listing["id"] == "com.k-neco.vpm"
    assert set(listing["packages"]) == {PACKAGE_ID}

    version = listing["packages"][PACKAGE_ID]["versions"][PACKAGE_VERSION]
    assert version["url"] == PACKAGE_URL
    assert version["repo"] == LISTING_URL
    assert version["zipSHA256"] == PACKAGE_SHA256

    for text in (html, app):
        assert LISTING_URL in text
        assert PACKAGE_ID in text
        assert "AFK Motion Patcher" in text
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

    with urllib.request.urlopen(PACKAGE_URL, timeout=30) as response:
        package_bytes = response.read()
    assert hashlib.sha256(package_bytes).hexdigest() == PACKAGE_SHA256

    print("VPM listing validation passed")


if __name__ == "__main__":
    main()
