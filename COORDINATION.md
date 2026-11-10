# COORDINATION — Shared Task Board

**Repo:** `wingbangboozle1-lang/Tino1`
**Purpose:** Decision-support site for an inherited Cupertino (95014) residence and an existing San Francisco Outer Sunset (94122) triplex, inherited via trust ~2040–2050.

> **Privacy rule (highest priority):** No personal information (names, street addresses, APNs, account numbers, SSNs, phone/email) may appear in this repo or the published site. All owners are referred to as `[OWNER-A]` (trust grantor), `[OWNER-B]` (successor trustee), `[TENANT-1..3]`. APNs replaced by `[APN-CUP]`, `[APN-SF]`.

## Session registry

| Session ID | Branch | Claimed scope | Status |
| --- | --- | --- | --- |
| `arena-da94d83b` | `arena/da94d83b-tino1` | All files (repo was empty at start — no other sessions active) | in progress |

**Conflict note:** At session start the repository contained only `README.md` at commit `fd4bd84` — no `COORDINATION.md`, no other branches (`git branch -a` showed only `main` and this session branch), no open PRs, no other session claims. This session therefore claims the whole repository and acts as its own final integration session (single-session build). If another session appears later, it must claim a non-overlapping scope below before editing.

## Task board

| # | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T1 | Repo review, coordination board, privacy policy | done | arena-da94d83b | `COORDINATION.md`, `README.md` |
| T2 | Source registry + verified research (federal) | in progress | arena-da94d83b | `data/sources.json`, `data/federal.json` |
| T3 | Verified research (California property tax / Prop 19 / Prop 13) | in progress | arena-da94d83b | `data/california.json` |
| T4 | Verified research (San Francisco + Santa Clara County local) | in progress | arena-da94d83b | `data/local.json` |
| T5 | Verified research (operating costs: water, power, insurance, maintenance) | in progress | arena-da94d83b | `data/operating_costs.json` |
| T6 | Verified research (inheritance tax thresholds + process) | in progress | arena-da94d83b | `data/inheritance.json` |
| T7 | Projection model (value, tax, costs, rent, reinvestment) | unclaimed | — | `scripts/model.py`, `data/projections.json` |
| T8 | Decision analysis (live / rent / sell) | unclaimed | — | `data/decision.json` |
| T9 | Site build (dashboard + category pages) | unclaimed | — | `site/`, `index.html`, `assets/` |
| T10 | Verification script (no row without official source; privacy scan; rounding check) | unclaimed | — | `scripts/verify.py` |
| T11 | Link/build check + GitHub Pages deploy | unclaimed | — | `.nojekyll`, Pages settings |
| T12 | PR to `main`, merge, deploy confirmation | unclaimed | — | `COORDINATION.md` |

Status values: `unclaimed` · `in progress` · `needs review` · `done`.

## Verification standard (applies to every task)

1. Every table row that states a value must carry a **source link** to a primary/官方 source (IRS, California Legislature, BOE/CDTFA, county assessor/treasurer, city, CPUC, BLS, Census, FHFA, HUD, PG&E/SFPUC/water utility tariffs).
2. If a value cannot be confirmed from an official source it is **left blank** and flagged `UNVERIFIED` on the *Flagged for Review* page. Values are never inferred or back-filled.
3. Third-party commentary (law firm blogs, real-estate sites) is **not** used as a source of record; it may only point to a primary document, and then the primary document is cited.
4. Derived numbers (projections, NPV, tax math) are labeled **MODELED** with the formula and input sources shown. They are not presented as official figures.
5. All money rounded to the nearest **$10** (per project requirement); percentages to 2 decimals.

## Log

| Date | Session | Entry |
| --- | --- | --- |
| 2026-11-10 | arena-da94d83b | Repo reviewed: empty except `README.md`; GitHub Pages already configured (`main`, `/`, legacy build). Board created; scope claimed for entire repository. |
