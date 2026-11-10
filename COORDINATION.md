# COORDINATION.md — Shared Task Board

Project: **Cupertino / San Francisco house inheritance decision analysis** (static GitHub Pages dashboard).

Privacy rule (applies to every session): **no names, addresses, parcel numbers (APNs), account numbers, or other
personal identifiers anywhere in the repo or the site.** Properties are referred to only as
**Property A (Cupertino, ZIP 95014)** and **Property B (San Francisco Outer Sunset, ZIP 94122)**.
People are referred to only as **Transferor(s)** (current owner(s)/trustor(s)) and **Heir** (beneficiary).

## How to use this board

1. Read this file first. Claim a task by writing your session ID + file scope in the table, commit, and push immediately.
2. Never start a task another session has claimed (unless the claim is >60 min old with no commits — note the handoff in the log).
3. Edit only files in your claimed scope. Requests to change another session's files go in the **Change requests** section.
4. `git pull --rebase` before every push. Small, frequent commits.
5. Status values: `unclaimed` | `in progress` | `done` | `needs review` (= published on the Flagged for Review page; does not block).
6. Shared outputs (site index/nav, combined tables) are changed only by the final **integration** task.
7. Nothing is marked verified without a link to an official source.

## Session registry

| Session ID | Branch | Started (UTC) | Role |
|---|---|---|---|
| `6ea079fa` | `arena/6ea079fa-tino1` (platform-fixed branch name; the `session-<id>/<task>` naming could not be used because this platform pins each session to one branch) | 2026-11-10 | Research + build + **integration** (sole session at start; no other branches/PRs existed when claimed) |

## Task board

| # | Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|---|
| T0 | Repo review (inventory, irregularities) | done | `6ea079fa` | `COORDINATION.md`, `README.md` | Repo contained only `README.md` ("# Tino1") at `fd4bd84`. Pages already enabled: source `main` / root, legacy build. |
| T1 | Federal estate / gift / income-tax rules & thresholds (verified from IRS) | done | `6ea079fa` | `data/federal_tax.csv`, `docs/inheritance-tax.html` | |
| T2 | California state rules: no estate/inheritance tax, Prop 13, Prop 19, income/cap-gains rates, homeowners' exemption (BOE / FTB / SCO) | done | `6ea079fa` | `data/california_tax.csv`, `docs/prop19.html`, `docs/tax-law.html` | |
| T3 | Local rules: Santa Clara County / Cupertino and San Francisco (tax rates, transfer tax, rent ordinance, vacancy tax, utilities) | done | `6ea079fa` | `data/local_rules.csv`, `docs/tax-law.html` | |
| T4 | Operating-cost research: insurance, water, electricity, maintenance (official sources where they exist; otherwise flagged) | done | `6ea079fa` | `data/operating_costs.csv`, `docs/costs.html` | |
| T5 | User-supplied property data (assessment history, values, rents) — recorded as *user-supplied, unverified* | done | `6ea079fa` | `data/property_a_history.csv`, `data/property_b_history.csv`, `docs/properties.html` | Values rounded to nearest $10 per project rule. |
| T6 | Projection model (value, assessed value, property tax, operating costs, 2026–2055) | done | `6ea079fa` | `analysis/model.py`, `data/projections_*.csv`, `docs/projections.html` | Deterministic script; assumptions documented. |
| T7 | Decision analysis (live / rent / sell-and-reinvest; after-tax) | done | `6ea079fa` | `analysis/model.py`, `data/scenarios.csv`, `docs/scenarios.html` | |
| T8 | Step-by-step trust inheritance process (CA Probate Code, BOE forms, IRS forms) | done | `6ea079fa` | `docs/process.html` | |
| T9 | Pending / proposed law changes (federal + CA + local) | done | `6ea079fa` | `data/pending_changes.csv`, `docs/pending-legislation.html` | |
| T10 | Executive summary | done | `6ea079fa` | `docs/executive-summary.html`, `docs/index.html` | |
| T11 | Flagged for Review page (unverified items, irregularities, privacy notes) | done | `6ea079fa` | `docs/flagged.html`, `data/flagged.csv` | |
| T12 | **Integration**: site shell/nav, link check, build check, PR, merge, Pages deploy confirmation | in progress (PR stage) | `6ea079fa` | `docs/assets/*`, `docs/index.html`, `docs/sources.html`, `.nojekyll`, `README.md`, `COORDINATION.md` | Runs after T0–T11. |

## Change requests (for files owned by another session)

_None._

## Log

| Time (UTC) | Session | Entry |
|---|---|---|
| 2026-11-10 | `6ea079fa` | Board created. No other sessions, branches, or PRs existed. Claimed T0–T12 (sole session). |
| 2026-11-10 | `6ea079fa` | Research complete (IRS, U.S. Code, BOE, FTB, SCO, Legislature, SOS, SCC rate book, SF TTX/Assessor/Rent Board, HUD, BLS, FHFA, Treasury, CDI). Facts recorded in `data/*.csv` with source URLs. |
| 2026-11-10 | `6ea079fa` | `analysis/model.py` (projections 2026–2060, 6 scenarios, 27-case sensitivity, estate-tax exposure) and `analysis/build_site.py` (14 pages) written; `scripts/check_site.py` passes (internal links, verified-row source links, privacy scan). Commit `ba9482d`. |
| 2026-11-10 | `6ea079fa` | Privacy decision: owner's year-by-year assessment series withheld from the public repo (quasi-identifier); only a rounded 2025 anchor (A) and a derived ratio (B) retained. Recorded as flagged item X09. |
| 2026-11-10 | `6ea079fa` | Integration: README, COORDINATION updated; PR opened from `arena/6ea079fa-tino1` → `main`; Pages source to be switched from `main:/` to `main:/docs` after merge. |

## Verification record (filled in as tasks complete)

| Task | Sources checked (official) | Verification performed | Irregularities |
|---|---|---|---|
| T0 | github.com/wingbangboozle1-lang/Tino1 (`gh api repos/.../pages`) | Repo contained only `README.md`; Pages enabled from `main:/` (legacy build) → live URL showed an empty README page. | Flagged X18; fixed by publishing `/docs` with `.nojekyll` and switching the Pages source. |
| T1 | Rev. Proc. 2025-32; IRS Estate Tax page; IRS What's New (estate & gift); IRS estate-tax FAQs; IRS Topics 409/559/701/704; IRS Deceased-person page; 26 U.S.C. §§1014, 2001 (GovInfo) | Each figure in `data/federal_tax.csv` read directly from the cited page on 2026-11-10 ($15M exclusion, 40% rate, 9-month Form 706, portability, $19k annual exclusion, LTCG brackets, NIIT, §121, step-up). | Depreciation period (27.5 yr) not re-read in Pub. 527 → X10. |
| T2 | SCO estate-tax page; Cal. Const. art. XIII A; BOE Prop 19 page; BOE LTA 2025/009 and 2026/026; BOE HOX page; FTB 2025 rate schedules; R&TC §§480, 11911, 11930, 17043; Prob. Code §16061.7; Civ. Code §1947.12; SOS qualified measures + results | Each row of `data/california_tax.csv` traced to the cited text. | Election results unofficial until Dec 11 2026 → X12. |
| T3 | SF TTX secured-tax page (1.18162182%); SF Assessor fee schedule (transfer-tax tiers); SF TTX Empty Homes Tax page; sf.gov rent-increase notice (1.6%) and rental-laws page; Santa Clara County FY2025-26 Tax Rate Book pp. A-4–A-6; SCC Assessor Prop 19 page; SF Assessor Prop 19 fact sheet; HUD FY2026 FMR/SAFMR pages | Component rates summed for Cupertino (1.1636%); SF rate read directly. | Cupertino TRA table unreadable (PDF > 30 pages) → X01; no Cupertino city transfer-tax confirmation → X13; EHT litigation → X14. |
| T4 | CDI residential-insurance guide and premium-comparison tool; SFPUC rates landing page; BLS CPI (Sept 2026) | Tool/landing pages contain no figures → insurance and utilities left as user-supplied / unverified. | X04, X20. |
| T5 | — (owner-supplied) | Values recorded as user-supplied, rounded to $10; histories withheld for privacy. | Effective rates 1.335% (A) and ≈2.14% (B) vs ad valorem rates → X16, X17; principal residence and ownership structure ambiguous → X07, X08. |
| T6–T7 | FHFA HPI tables (2026Q2); BLS CPI; Treasury yields (Nov 9 2026); BOE LTA 2025/009 | Model parameters anchored on cited indicators; all assumptions labelled; results reproducible with `python3 analysis/model.py`. | Assumptions listed as X19, X21–X23. |
| T8 | Prob. Code §16061.7; R&TC §§480, 11930; BOE LTA 2026/026; IRS estate FAQs; SF/SCC assessor pages | Deadlines (60 days, 150 days, 1 year, 9 months, 3 years) read from the statutes/pages. | — |
| T9 | Rev. Proc. 2025-32; SOS qualified measures, initiative status, unofficial results; BOE Prop 19 legislation list; SF TTX EHT page | Status of each measure read on 2026-11-10. | HJTA signature counts from news only → X11. |
| T10–T11 | All of the above | Executive summary and Flagged page generated from the same CSVs/model (no hand-typed numbers). | 23 flagged items published. |
| T12 | `scripts/check_site.py` | 14 pages, 0 broken internal links, every verified row has a source link, privacy scan clean. | — |

## Pull request / merge record

_pending_
