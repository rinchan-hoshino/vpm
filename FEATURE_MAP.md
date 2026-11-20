# Feature Map

| Path | Responsibility |
| --- | --- |
| `Website/index.html` | Static portal shell with trilingual switcher (`ja` / `en` / `zh`), VCC deep-link button, URL copy control, package container, and setup guide. |
| `Website/styles.css` | Minimalist responsive stylesheet with light/dark `prefers-color-scheme` tokens. |
| `Website/app.js` | Browser language detection, instant `ja` / `en` / `zh` i18n switching, clipboard copy feedback, and dynamic `./index.json` package card rendering. |
| `Website/index.json` | VPM repository manifest consumed by VCC, ALCOM, and `Website/app.js`. |
| `Website/CNAME` | GitHub Pages custom domain (`vpm.k-neco.com`). |
| `source.json` | Repository-level VPM metadata (`com.the-cattail.vpm`). |
| `scripts/update-index.py` | CLI tool to compute `zipSHA256`, validate URLs/fields, and update `Website/index.json` from a `package.json` + `.zip` release. |
| `tests/validate_listing.py` | Automated gate checking `source.json`, `Website/*`, deprecated link removal, and optional `.zip` SHA-256 verification. |
| `.github/workflows/build-listing.yml` | GitHub Actions workflow that runs `tests/validate_listing.py` and deploys `Website/` to GitHub Pages. |
