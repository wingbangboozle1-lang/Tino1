# Tino1 — Property Inheritance Decision Dashboard

Research and decision analysis for inheriting two California properties through a revocable trust
(expected 2040–2050): **Property A** (Cupertino, ZIP 95014, single-family) and **Property B**
(San Francisco Outer Sunset, ZIP 94122, three units). Published as a static GitHub Pages site.

**Live site:** https://wingbangboozle1-lang.github.io/Tino1/

## Privacy

The repository is public. No names, street addresses, parcel numbers or account numbers appear anywhere.
Properties are referred to as Property A / Property B; people as Transferor / Heir. Owner-supplied
year-by-year assessment histories are deliberately **not** published; all amounts are rounded to the nearest $10.

## What is where

| Path | Contents |
|---|---|
| `docs/` | The website (plain HTML/CSS, no build step needed to view). `docs/index.html` is the dashboard. |
| `data/federal_tax.csv`, `data/california_tax.csv`, `data/local_rules.csv` | Verified legal facts, each row with its official source URL and a status. |
| `data/operating_costs.csv`, `data/property_*_history.csv` | Owner-supplied inputs, clearly marked `user-supplied`, plus benchmarks. |
| `data/economic_indicators.csv` | BLS / FHFA / Treasury anchors for the model assumptions. |
| `data/pending_changes.csv` | Enacted and pending law changes and their effect on the plan. |
| `data/flagged.csv` | Every unverified, derived, ambiguous or irregular item (published on the *Flagged for Review* page). |
| `analysis/model.py` | Deterministic projection + scenario model → `data/projections/*.csv`, `data/scenarios.csv`, `docs/data/model_output.json`. |
| `analysis/build_site.py` | Renders `docs/*.html` from the CSVs and model output. |
| `scripts/check_site.py` | Pre-publish checks: internal links, source links on verified rows, privacy scan. |
| `COORDINATION.md` | Multi-session task board, verification record and PR/merge record. |

## Reproduce

```bash
python3 analysis/model.py        # recompute projections and scenarios
python3 analysis/build_site.py   # rebuild docs/
python3 scripts/check_site.py    # verify before publishing
```

No third-party dependencies (Python 3.10+ standard library only).

## Status rules

- `verified` — read from an official source (IRS, U.S. Code, BOE, FTB, Legislature, SOS, county/city sites) on the build date; link in the row.
- `derived` — computed from verified or owner figures; the computation is stated.
- `user-supplied` — stated by the owner; not independently verified.
- `assumption` — model input, not a fact.
- `unverified` — no official confirmation obtained; the value is left blank and the item is flagged. Nothing is inferred to fill a gap.

This is an independent research summary, **not legal, tax or investment advice**.
