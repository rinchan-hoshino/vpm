# Feature Map

| Path | Responsibility |
| --- | --- |
| `Website/index.html` | Static portal shell with trilingual switcher (`ja` / `en` / `zh`), VCC deep-link button, URL copy control, package container, and setup guide. |
| `Website/styles.css` | Restrained technical-docs stylesheet: paper/white blocks, ink text, 1px hairline rules, single cobalt accent, Hiragino/Noto Sans JP + JetBrains Mono for URLs/versions/section numbers, 4px corners, hard offset shadow only; light/dark `prefers-color-scheme` tokens and responsive breakpoints (720px / 480px). |
| `Website/app.js` | Browser language detection, instant `ja` / `en` / `zh` i18n switching, clipboard copy feedback, and dynamic `./index.json` package card rendering. |
| `Website/index.json` | VPM repository manifest consumed by VCC, ALCOM, and `Website/app.js`. |
| `Website/CNAME` | GitHub Pages custom domain (`vpm.k-neco.com`). |
| `source.json` | Repository-level VPM metadata (`com.the-cattail.vpm`). |
| `scripts/update-index.py` | CLI tool to compute `zipSHA256`, validate URLs/fields, and update `Website/index.json` from a `package.json` + `.zip` release. |
| `tests/validate_listing.py` | Automated gate checking `source.json`, `Website/*`, deprecated link removal, and optional `.zip` SHA-256 verification. |
| `.githooks/pre-push` | Local git pre-push hook (enable with `git config core.hooksPath .githooks`) that execs `scripts/verify.sh`: fails if a `.github/` directory exists (GitHub Actions disabled), runs `tests/validate_listing.py`, then checks `Website/index.json` contains only `com.the-cattail.afk-motion-patcher` 2.0.0 with no forbidden legacy strings, and that `ja` / `en` / `zh` are present in `index.html` and `app.js`. |
