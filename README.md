# THE_cattail VPM

Official VRChat Package Manager (VPM) repository for general-purpose VRChat editor tools by **THE_cattail**.

- **Web Portal**: <https://vpm.k-neco.com/>
- **Repository JSON**: <https://vpm.k-neco.com/index.json>
- **One-Click Add to VCC**: `vcc://vpm/addRepo?url=https%3A%2F%2Fvpm.k-neco.com%2Findex.json`

## Included Packages

| Package ID | Display Name | Source | BOOTH |
| --- | --- | --- | --- |
| `com.the-cattail.afk-motion-patcher` | AFK Motion Patcher | [GitHub](https://github.com/rinchan-hoshino/afk-motion-patcher) | [BOOTH](https://the-cattail.booth.pm/items/8783972) |

> Character-specific preset packages are distributed separately and are intentionally not listed on `vpm.k-neco.com`.

## Updating `Website/index.json`

Use [`scripts/update-index.py`](scripts/update-index.py) when publishing a new package release:

```bash
python3 scripts/update-index.py \
  --package-json path/to/package.json \
  --zip path/to/com.the-cattail.afk-motion-patcher-x.y.z.zip \
  --zip-url https://github.com/rinchan-hoshino/afk-motion-patcher/releases/download/vx.y.z/com.the-cattail.afk-motion-patcher-x.y.z.zip
```

## Validation

Run the listing gate locally before committing:

```bash
python3 tests/validate_listing.py
```

Pass `--verify-remote` (or set `VPM_VERIFY_REMOTE=1`) to also download the release `.zip` and verify its SHA-256 against `Website/index.json`.

## Local Preview

```bash
python3 -m http.server 8080 --directory Website
```
