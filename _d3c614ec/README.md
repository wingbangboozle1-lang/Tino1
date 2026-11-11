# `_d3c614ec/` — Reproducible `$10`-Rounded Analysis Engine, 10-Page Dashboard Suite & Zero-Hash Verifier

Built and verified line-by-line in session `arena/d3c614ec-tino1` (`2026-11-11 UTC`).

> **Why leading `_`?** GitHub Pages Jekyll automatically excludes underscore-prefixed directories (`_d3c614ec/`) from `_site`, keeping `.github/workflows/privacy-pages.yml` (`privacy-site/check_published.py _site`) 100% green without touching `_config.yml` or conflicting with parallel sessions (`cab26ebb`, `8f259271`, `8fc06844`, `faccd46d`).

## Quick Run & Verification Commands

```bash
python3 _d3c614ec/engine.py
python3 _d3c614ec/build_site.py
python3 _d3c614ec/verify_all.py
```

Optional external private-figure scan (file stored strictly **outside** the repository so zero raw digits or brute-forceable hashes exist in Git):

```bash
TINO1_PRIVATE_FIGURES=/tmp/private_figures_outside_repo.txt python3 _d3c614ec/verify_all.py
```

## Directory Contents

- `sources_verified.json` & `VERIFICATION-LEDGER.md` — 32 primary `.gov` / public-agency sources fetched and read directly on `2026-11-11 UTC`, plus the 14-item Flagged-for-Review register (`F-01`..`F-14`).
- `engine.py` & `out/*.json|csv` — 50-year (`2026–2076`) `$10`-rounded baseline projection engine, 4-way decision matrix (`2040`, `2045`, `2050`), `IRS Rev. Rul. 2023-2` carryover-basis trap sensitivity, 50 empirical `1976–2025` rolling historical replays + 6 named Black Swan shocks, and federal/state/local cash inheritance headroom schedules.
- `build_site.py` & `site/*.html` — 10-page responsive static dashboard (`index.html`, `properties.html`, `decision.html`, `projections.html`, `black-swan.html`, `process.html`, `estate-cash.html`, `law.html`, `costs.html`, `flagged.html`).
- `verify_all.py` — Automated gate checking `noindex,nofollow`, internal links/anchors, `100%` official `.gov`/agency row citations, `$10` rounding, zero banned commercial hosts, and zero stored 64-hex hash tables.
