# Project Coordination Board (`COORDINATION.md`)

> **Privacy Mandate (TOP PRIORITY):** All personal identifiers, street addresses, parcel numbers (APNs), trust names, and individual names are strictly prohibited across all repository files, commits, and published pages. Placeholders (`[Property A — Cupertino 95014]`, `[Property B — San Francisco 94122]`, `[Grantor/Settlor]`, `[Beneficiary/Trustee]`, `[Family Trust]`) must be used exclusively, and reported cost/analysis dollar figures must be rounded to the nearest `$10` increment.

## Session Registry

| Session ID | Active Branch | Role | Started (UTC) | Status |
| :--- | :--- | :--- | :--- | :--- |
| `session-85899999` | `arena/85899999-tino1` | Primary Research, Verification, Site Engineering & Final Integration | 2026-11-10T06:03:00Z | Active |

---

## Shared Task Board

| Task ID | Task Description | Status | Owning Session ID | File Scope | Notes / Verification Log |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-01` | Official Source Verification: CA BOE Prop 13 CCPI Factors (2014–2026), Prop 19 Rules & Thresholds, Santa Clara (95014) & SF (94122) Tax Rates, Federal/State/Local Estate & Inheritance Tax Thresholds, Step-Up Basis (`IRC § 1014` / `Rev. Rul. 2023-2`) | `in progress` | `session-85899999` | `docs/research-tax-estate.md` | Claimed 2026-11-10T06:03:00Z |
| `TASK-02` | Official Source Verification: Operating Costs — Homeowners & Landlord Insurance (`95014` & `94122`), Water (`SJW`/`CWD` & `SFPUC`), Electricity/Solar (`PG&E` NEM 2.0 Sunset / NBT / Base Services Charge), Maintenance & SF Rent Ordinance | `unclaimed` | — | `docs/research-operating-costs.md` | Pending claim |
| `TASK-03` | Line-by-Line Historical Property Audit, `$10`-Increment Anonymized Financial Model (2026–2050 Projections), & Decision Scenario Analysis (Live In vs. Rent vs. Sell & Reinvest) | `unclaimed` | — | `scripts/build_data.py`, `data/verified_analysis.json`, `docs/executive-summary.md` | Pending claim |
| `TASK-04` | Trust Inheritance Step-by-Step Guide & Flagged Irregularities / Unverified Items Audit Log | `unclaimed` | — | `docs/inheritance-process.md`, `docs/flagged-irregularities.md` | Pending claim |
| `TASK-05` | Multi-Page Dashboard Website Build (`.nojekyll`, Landing Page, Category Subpages, Flagged for Review Page, Interactive Scenario Explorer, Source Links on Every Table Row) | `unclaimed` | — | `index.html`, `executive-summary.html`, `properties.html`, `projections.html`, `scenarios.html`, `estate-tax.html`, `inheritance-guide.html`, `flagged-review.html`, `assets/styles.css`, `assets/app.js`, `.nojekyll` | Pending claim |
| `TASK-06` | Final Integration, Line-by-Line Re-Verification, Link & Build Validation, PR Creation, Merge to `main`, & GitHub Pages Live Deployment Confirmation | `unclaimed` | — | `COORDINATION.md`, `README.md`, `scripts/verify_site.py` | Final integration task |

---

## Activity & Handoff Log

- **2026-11-10T06:03:00Z (`session-85899999` on `arena/85899999-tino1`):** Initialized `COORDINATION.md` after verifying repository state (`fd4bd84` on `main`, no competing remote branches or PRs). Claimed `TASK-01` (`docs/research-tax-estate.md`). Note: Arena platform binds this session strictly to branch `arena/85899999-tino1`; file-scope isolation and `git fetch` / `git pull --rebase` checks are enforced before every push.
