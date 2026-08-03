#!/usr/bin/env python3
import hashlib
import io
import json
import os
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "Website"
LISTING_URL = "https://vpm.k-neco.com/index.json"
PACKAGE_ID = "com.the-cattail.afk-motion-patcher"
EXPECTED_PACKAGES = {
    "1.0.0": (
        "https://github.com/k-neco-lab/afk-motion-patcher/releases/download/v1.0.0/"
        "com.the-cattail.afk-motion-patcher-1.0.0.zip",
        "998dd560158febedd7e27736dc7359cca6f3efd1950bb0f6edb062f003504c17",
    ),
}
LISTING_REPOSITORY_URL = "https://github.com/rinchan-hoshino/vpm"
OLD_LISTING_REPOSITORY_URL = "https://github.com/k-neco-lab/" + "vpm"
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
    assert source["infoLink"]["url"] == LISTING_REPOSITORY_URL
    assert listing["name"] == "THE_cattail VPM"
    assert listing["author"] == "THE_cattail"
    assert listing["id"] == "com.the-cattail.vpm"
    assert set(listing["packages"]) == {PACKAGE_ID}

    versions = listing["packages"][PACKAGE_ID]["versions"]
    assert set(versions) == set(EXPECTED_PACKAGES)
    for version, (package_url, package_sha256) in EXPECTED_PACKAGES.items():
        package = versions[version]
        assert package["author"]["name"] == "THE_cattail"
        assert package["version"] == version
        assert package["url"] == package_url
        assert package["repo"] == LISTING_URL
        assert PACKAGE_ID not in package.get("legacyPackages", [])
        assert package["zipSHA256"] == package_sha256

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
    assert html.count(LISTING_REPOSITORY_URL) == 2

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            assert OLD_VPM_PREFIX not in text, f"old VPM URL remains in {path}"
            assert OLD_LISTING_REPOSITORY_URL not in text, f"old listing repository remains in {path}"

    package_path = os.environ.get("VPM_PACKAGE_FILE")
    for version, (package_url, package_sha256) in EXPECTED_PACKAGES.items():
        if package_path:
            package_bytes = Path(package_path).read_bytes()
        else:
            with urllib.request.urlopen(package_url, timeout=30) as response:
                package_bytes = response.read()
        assert hashlib.sha256(package_bytes).hexdigest() == package_sha256
        with zipfile.ZipFile(io.BytesIO(package_bytes)) as archive:
            package_manifest = json.loads(archive.read("package.json"))
        listing_manifest = dict(versions[version])
        assert listing_manifest.pop("zipSHA256") == package_sha256
        listing_overrides = {
            "description",
            "keywords",
            "legacyFiles",
            "legacyFolders",
            "legacyPackages",
            "licensesUrl",
        }
        for key, value in package_manifest.items():
            if key not in listing_overrides:
                assert listing_manifest[key] == value
        assert set(listing_manifest) - set(package_manifest) <= listing_overrides

    print("VPM listing validation passed")


if __name__ == "__main__":
    main()
