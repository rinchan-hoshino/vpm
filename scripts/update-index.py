#!/usr/bin/env python3
"""Update Website/index.json from a VPM package.json and release .zip archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = ROOT / "Website" / "index.json"
LISTING_URL = "https://vpm.k-neco.com/index.json"
DEFAULT_REPO_URL = "https://github.com/rinchan-hoshino/afk-motion-patcher"
FORBIDDEN_FRAGMENTS = ("k-neco-" + "lab", "k-neco.com" + "/vpm")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_MANIFEST_FIELDS = (
    "name",
    "displayName",
    "version",
    "unity",
    "description",
    "author",
    "license",
    "vpmDependencies",
)


def compute_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_https_url(label: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty URL string")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be a valid https:// URL: {value!r}")
    for forbidden in FORBIDDEN_FRAGMENTS:
        if forbidden in value:
            raise ValueError(f"{label} contains deprecated fragment {forbidden!r}: {value!r}")
    return value


def validate_entry(entry: dict) -> None:
    for field in REQUIRED_MANIFEST_FIELDS:
        if not entry.get(field):
            raise ValueError(f"Missing required package field: {field}")

    author = entry["author"]
    if not isinstance(author, dict) or not author.get("name"):
        raise ValueError("package.author.name must be non-empty")

    validate_https_url("package.url", entry.get("url"))
    validate_https_url("package.repo", entry.get("repo"))
    validate_https_url("package.author.url", author.get("url"))

    for optional_url in ("documentationUrl", "changelogUrl", "licensesUrl"):
        if optional_url in entry and entry[optional_url] is not None:
            validate_https_url(f"package.{optional_url}", entry[optional_url])

    sha = entry.get("zipSHA256", "")
    if not isinstance(sha, str) or not SHA256_RE.match(sha):
        raise ValueError(f"Invalid zipSHA256: {sha!r}")


def build_version_entry(manifest: dict, zip_sha256: str, zip_url: str | None) -> dict:
    entry = dict(manifest)
    pkg_id = entry.get("name", "")
    version = entry.get("version", "")

    if zip_url:
        entry["url"] = zip_url
    elif not entry.get("url") and pkg_id == "com.the-cattail.afk-motion-patcher":
        entry["url"] = (
            f"{DEFAULT_REPO_URL}/releases/download/v{version}/{pkg_id}-{version}.zip"
        )

    entry["repo"] = LISTING_URL
    entry["zipSHA256"] = zip_sha256

    if isinstance(entry.get("author"), dict) and not entry["author"].get("url"):
        entry["author"]["url"] = DEFAULT_REPO_URL

    validate_entry(entry)
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update Website/index.json with a new package version and SHA-256."
    )
    parser.add_argument("--package-json", required=True, type=Path, help="Path to package.json")
    parser.add_argument("--zip", required=True, type=Path, help="Path to release .zip archive")
    parser.add_argument("--zip-url", default=None, help="Public HTTPS download URL for the .zip")
    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX_PATH,
        type=Path,
        help="Path to Website/index.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing index.json")
    args = parser.parse_args()

    if not args.package_json.is_file():
        raise FileNotFoundError(f"package.json not found: {args.package_json}")
    if not args.zip.is_file():
        raise FileNotFoundError(f".zip file not found: {args.zip}")
    if not args.index.is_file():
        raise FileNotFoundError(f"index.json not found: {args.index}")

    manifest = json.loads(args.package_json.read_text(encoding="utf-8"))
    zip_sha256 = compute_sha256(args.zip)
    entry = build_version_entry(manifest, zip_sha256, args.zip_url)

    listing = json.loads(args.index.read_text(encoding="utf-8"))
    packages = listing.setdefault("packages", {})
    pkg_bucket = packages.setdefault(entry["name"], {"versions": {}})
    versions = pkg_bucket.setdefault("versions", {})
    versions[entry["version"]] = entry

    rendered = json.dumps(listing, indent=2, ensure_ascii=False) + "\n"
    if args.dry_run:
        print(f"[dry-run] Validated {entry['name']} {entry['version']} (sha256={zip_sha256})")
        return

    args.index.write_text(rendered, encoding="utf-8")
    print(f"Updated {args.index} with {entry['name']} {entry['version']} (sha256={zip_sha256})")


if __name__ == "__main__":
    main()
