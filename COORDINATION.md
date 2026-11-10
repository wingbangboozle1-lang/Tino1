# COORDINATION.md — Shared Task Board

**Repo:** wingbangboozle1-lang/Tino1
**Purpose of project:** Decision analysis for inheriting a Cupertino (95014) single-family home via trust (~2040–2050), while also holding a 3-unit San Francisco Outer Sunset (94122) building (2 units rented). Deliverable: executive summary + verified data tables + step-by-step inheritance process + 25-year projections + publishable static site on GitHub Pages.

## Operating rules in force
- Every published table row carries a source link to an official (government / utility-tariff / primary-filing) source.
- If a value cannot be confirmed from an official source it is **left blank and flagged `UNVERIFIED`**, never inferred.
- Money figures are rounded to the **nearest $10**.
- **No personal information** (names, street addresses, APNs, account numbers, exact household finances beyond owner-supplied rounded property figures) is published on the site. Properties are referred to as **Property A (Cupertino 95014)** and **Property B (San Francisco 94122)**.
- Shared outputs (`index.html`, navigation, `data/*.json`) are changed only by the integration session.
- Small frequent commits; `git pull --rebase` before every push.

## Sessions

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena-fafd7e15` | `arena/fafd7e15-tino1` | Research + build + integration (sole session this cycle) | active |

> Note: only one session is active in this cycle. The board is still maintained as specified so a later session can pick up cleanly. `needs review` items are published on `flagged.html` and do not block merge.

## Task board

| # | Task | Owner | Status | Files touched |
|---|---|---|---|---|
| T01 | Scaffold repo, coordination board, privacy policy, rounding convention | arena-fafd7e15 | in progress | `COORDINATION.md`, `README.md`, `PRIVACY.md`, `.nojekyll` |
| T02 | Federal inheritance/estate tax law, thresholds, projections, step-up basis | arena-fafd7e15 | unclaimed | `data/estate_tax.json`, `src/sources.json` |
| T03 | California property tax law (Prop 13 / Prop 19 / RTC 63.2 / $1M adjustment) | arena-fafd7e15 | unclaimed | `data/prop_tax_law.json` |
| T04 | Property A (95014) baseline + 2026–2050 assessed-value & tax projection | arena-fafd7e15 | unclaimed | `data/cupertino.json` |
| T05 | Property B (94122) baseline + tax projection, rent roll, SF-specific charges | arena-fafd7e15 | unclaimed | `data/san_francisco.json` |
| T06 | Insurance research (CA homeowners / landlord / FAIR Plan) | arena-fafd7e15 | unclaimed | `data/insurance.json` |
| T07 | Utilities research (SJW water, SFPUC water/sewer, PG&E tariff, NEM) | arena-fafd7e15 | unclaimed | `data/utilities.json` |
| T08 | Maintenance/repair + transaction cost research | arena-fafd7e15 | unclaimed | `data/maintenance.json` |
| T09 | Appreciation / inflation / rent growth assumptions from official indices | arena-fafd7e15 | unclaimed | `data/market.json` |
| T10 | Inheritance step-by-step process (trust administration, forms, deadlines) | arena-fafd7e15 | unclaimed | `data/process.json` |
| T11 | Decision model: live / rent / sell — after-tax NPV & net-worth projections | arena-fafd7e15 | unclaimed | `data/scenarios.json`, `src/model.py` |
| T12 | Pending & recent law changes watch list | arena-fafd7e15 | unclaimed | `data/law_watch.json` |
| T13 | Site build (static HTML + SVG charts, no external CDNs), link check | arena-fafd7e15 | unclaimed | `src/build.py`, `*.html` |
| T14 | Integration: merge, re-verify line by line, publish, PR, merge to `main`, confirm Pages | arena-fafd7e15 | unclaimed | `index.html`, `PR` |

## Log

- **2026-11-10** — Session `arena-fafd7e15` created the board. Repo contained only `README.md` (7 bytes) at `fd4bd84`. GitHub Pages already enabled: source `main` / root, legacy build, `https://wingbangboozle1-lang.github.io/Tino1/`. Claims T01–T14 (sole active session). Scope: everything except `.git/`.
