#!/usr/bin/env python3
"""Validate VPM listing metadata, static website files, and optional release archives."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "Website"

LISTING_URL = "https://vpm.k-neco.com/index.json"
LISTING_REPO_URL = "https://github.com/rinchan-hoshino/vpm"
PACKAGE_REPO_URL = "https://github.com/rinchan-hoshino/afk-motion-patcher"
BOOTH_URL = "https://the-cattail.booth.pm/items/8783972"
PACKAGE_ID = "com.the-cattail.afk-motion-patcher"

FORBIDDEN_STRINGS = (
    "k-neco-" + "lab",
    "https://k-neco.com" + "/vpm",
)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def assert_https_url(label: str, url: object) -> None:
    assert isinstance(url, str) and url.strip(), f"{label} must be non-empty"
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc, f"{label} must be https://: {url!r}"


def verify_remote_archive(version_entry: dict, local_zip: str | None) -> None:
    package_url = version_entry["url"]
    package_sha256 = version_entry["zipSHA256"]

    if local_zip:
        package_bytes = Path(local_zip).read_bytes()
    else:
        with urllib.request.urlopen(package_url, timeout=30) as response:
            package_bytes = response.read()

    actual_sha = hashlib.sha256(package_bytes).hexdigest()
    assert actual_sha == package_sha256, (
        f"SHA-256 mismatch for {version_entry['version']}: expected {package_sha256}, got {actual_sha}"
    )

    with zipfile.ZipFile(io.BytesIO(package_bytes)) as archive:
        manifest = json.loads(archive.read("package.json"))

    assert manifest["name"] == version_entry["name"]
    assert manifest["version"] == version_entry["version"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate K-NECO VPM listing.")
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="Download release .zip archives and verify SHA-256 against index.json.",
    )
    args = parser.parse_args()

    source = json.loads((ROOT / "source.json").read_text(encoding="utf-8"))
    listing = json.loads((WEBSITE / "index.json").read_text(encoding="utf-8"))
    html = (WEBSITE / "index.html").read_text(encoding="utf-8")
    app = (WEBSITE / "app.js").read_text(encoding="utf-8")
    styles = (WEBSITE / "styles.css").read_text(encoding="utf-8")

    assert (WEBSITE / "CNAME").read_text(encoding="utf-8").strip() == "vpm.k-neco.com"

    # source.json checks
    assert source["url"] == LISTING_URL
    assert source["name"] == "THE_cattail"
    assert source["id"] == "com.the-cattail.vpm"
    assert source["author"]["name"] == "THE_cattail"
    assert source["author"]["url"] == PACKAGE_REPO_URL
    assert source["infoLink"]["url"] == LISTING_REPO_URL
    assert source["githubRepos"] == ["rinchan-hoshino/afk-motion-patcher"]

    # Website/index.json checks
    assert listing["url"] == LISTING_URL
    assert listing["name"] == "THE_cattail"
    assert listing["author"] == "THE_cattail"
    assert listing["id"] == "com.the-cattail.vpm"
    assert set(listing["packages"]) == {PACKAGE_ID}

    versions = listing["packages"][PACKAGE_ID]["versions"]
    assert len(versions) >= 1, "At least one package version must be present"
    for ver_key, pkg in versions.items():
        assert pkg["name"] == PACKAGE_ID
        assert pkg["version"] == ver_key
        assert pkg["repo"] == LISTING_URL
        assert pkg["author"]["name"] == "THE_cattail"
        assert_https_url(f"{ver_key}.url", pkg.get("url"))
        assert_https_url(f"{ver_key}.author.url", pkg["author"].get("url"))
        for opt_field in ("documentationUrl", "changelogUrl", "licensesUrl"):
            if opt_field in pkg and pkg[opt_field] is not None:
                assert_https_url(f"{ver_key}.{opt_field}", pkg[opt_field])
        assert SHA256_RE.match(pkg.get("zipSHA256", "")), f"Invalid zipSHA256 in {ver_key}"

    # Static frontend checks
    assert "vcc://vpm/addRepo?url=https%3A%2F%2Fvpm.k-neco.com%2Findex.json" in html
    assert LISTING_URL in html
    assert LISTING_REPO_URL in html
    assert BOOTH_URL in html
    assert 'data-lang="ja"' in html
    assert 'data-lang="en"' in html
    assert 'data-lang="zh"' in html
    assert "@fluentui/web-components" not in html

    assert 'fetch("./index.json"' in app
    assert LISTING_URL in app
    assert PACKAGE_REPO_URL in app
    assert BOOTH_URL in app
    assert "@media (max-width: 720px)" in styles

    # Forbidden legacy references check across repository
    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for forbidden in FORBIDDEN_STRINGS:
                assert forbidden not in text, f"Deprecated reference {forbidden!r} found in {path}"

    # Optional release archive verification
    local_zip = os.environ.get("VPM_PACKAGE_FILE")
    if args.verify_remote or os.environ.get("VPM_VERIFY_REMOTE") == "1" or local_zip:
        for pkg in versions.values():
            verify_remote_archive(pkg, local_zip)

    print("VPM listing validation passed")


if __name__ == "__main__":
    main()
