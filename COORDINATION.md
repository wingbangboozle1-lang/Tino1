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
| T0 | Repo review (inventory, irregularities) | in progress | `6ea079fa` | `COORDINATION.md`, `README.md` | Repo contained only `README.md` ("# Tino1") at `fd4bd84`. Pages already enabled: source `main` / root, legacy build. |
| T1 | Federal estate / gift / income-tax rules & thresholds (verified from IRS) | in progress | `6ea079fa` | `data/federal_tax.csv`, `docs/inheritance-tax.html` | |
| T2 | California state rules: no estate/inheritance tax, Prop 13, Prop 19, income/cap-gains rates, homeowners' exemption (BOE / FTB / SCO) | in progress | `6ea079fa` | `data/california_tax.csv`, `docs/prop19.html`, `docs/tax-law.html` | |
| T3 | Local rules: Santa Clara County / Cupertino and San Francisco (tax rates, transfer tax, rent ordinance, vacancy tax, utilities) | in progress | `6ea079fa` | `data/local_rules.csv`, `docs/tax-law.html` | |
| T4 | Operating-cost research: insurance, water, electricity, maintenance (official sources where they exist; otherwise flagged) | in progress | `6ea079fa` | `data/operating_costs.csv`, `docs/costs.html` | |
| T5 | User-supplied property data (assessment history, values, rents) — recorded as *user-supplied, unverified* | in progress | `6ea079fa` | `data/property_a_history.csv`, `data/property_b_history.csv`, `docs/properties.html` | Values rounded to nearest $10 per project rule. |
| T6 | Projection model (value, assessed value, property tax, operating costs, 2026–2055) | in progress | `6ea079fa` | `analysis/model.py`, `data/projections_*.csv`, `docs/projections.html` | Deterministic script; assumptions documented. |
| T7 | Decision analysis (live / rent / sell-and-reinvest; after-tax) | in progress | `6ea079fa` | `analysis/model.py`, `data/scenarios.csv`, `docs/scenarios.html` | |
| T8 | Step-by-step trust inheritance process (CA Probate Code, BOE forms, IRS forms) | in progress | `6ea079fa` | `docs/process.html` | |
| T9 | Pending / proposed law changes (federal + CA + local) | in progress | `6ea079fa` | `data/pending_changes.csv`, `docs/pending-legislation.html` | |
| T10 | Executive summary | in progress | `6ea079fa` | `docs/executive-summary.html`, `docs/index.html` | |
| T11 | Flagged for Review page (unverified items, irregularities, privacy notes) | in progress | `6ea079fa` | `docs/flagged.html`, `data/flagged.csv` | |
| T12 | **Integration**: site shell/nav, link check, build check, PR, merge, Pages deploy confirmation | in progress | `6ea079fa` | `docs/assets/*`, `docs/index.html`, `docs/sources.html`, `.nojekyll`, `README.md`, `COORDINATION.md` | Runs after T0–T11. |

## Change requests (for files owned by another session)

_None._

## Log

| Time (UTC) | Session | Entry |
|---|---|---|
| 2026-11-10 | `6ea079fa` | Board created. No other sessions, branches, or PRs existed. Claimed T0–T12 (sole session). |

## Verification record (filled in as tasks complete)

| Task | Sources checked (official) | Verification performed | Irregularities |
|---|---|---|---|
| _pending_ | | | |

## Pull request / merge record

_pending_
