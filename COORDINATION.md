# COORDINATION.md — Shared Task Board

**Repository:** `wingbangboozle1-lang/Tino1`
**Purpose:** Cupertino + San Francisco inherited-property decision analysis.
**Last updated:** 2026-11-10

## Session registry

| Session ID | Branch | Started | Status |
|---|---|---|---|
| `arena-e25621af` | `arena/e25621af-tino1` | 2026-11-10 | active |

> **Branch note.** This workspace permits work only on `arena/e25621af-tino1`. The
> `session-<id>/<task>` branch convention is therefore represented as **task IDs with
> non-overlapping file scopes** on that single branch. This preserves the intent of the
> protocol — no overlapping writes, no duplicate work — while respecting the branch
> constraint imposed by the environment. Claims are committed and pushed immediately.

## Task board

| Task ID | Description | Status | Owner | File scope |
|---|---|---|---|---|
| T01 | Repo review + coordination scaffold | **done** | `arena-e25621af` | `COORDINATION.md`, `README.md` |
| T02 | CA property tax research (Prop 13/19, reassessment) | **done** | `arena-e25621af` | `research/00-source-log.md` |
| T03 | Inheritance / estate tax research (federal + CA) | **done** | `arena-e25621af` | `research/00-source-log.md` |
| T04 | Carrying costs research (water, electricity, insurance) | **done** | `arena-e25621af` | `research/00-source-log.md` |
| T05 | Rental, rent control, transfer tax research | **done** | `arena-e25621af` | `research/00-source-log.md` |
| T06 | Financial model + projections engine | **done** | `arena-e25621af` | `tools/`, `data/` |
| T07 | GitHub Pages site (landing + 10 subpages) | **done** | `arena-e25621af` | `docs/` |
| T08 | Verification pass (line by line, source links) | **done** | `arena-e25621af` | `docs/flagged.html` |
| T09 | Integration, PR to `main`, merge, Pages deploy | in progress | `arena-e25621af` | `main` merge |

*No other session has claimed a task. All scopes are held by `arena-e25621af`.*

## Handoff / dispute log

- None. No conflicting claims. No takeover required (no claim older than 60 minutes
  with no commits).

## Log

- **2026-11-10** — `arena-e25621af` created this board. Repo contained only `README.md`
  at commit `fd4bd84`. GitHub Pages already enabled: source = `main` branch, path `/`,
  URL `https://wingbangboozle1-lang.github.io/Tino1/`, build type `legacy`, HTTPS enforced.
- **2026-11-10** — T01–T05 complete. 27 official sources verified and logged in
  `research/00-source-log.md` (S01–S27). Verified directly against boe.ca.gov, leginfo,
  irs.gov, sftreasurer.org, sf.gov, ftb.ca.gov, fhfa.gov, huduser.gov, sccassessor.
- **2026-11-10** — T06 complete. Deterministic model in `tools/model.py` +
  `tools/build_data.py` + `tools/breakeven.py`. Model validates against the owner's
  actual 2025 tax bill to within 1.7%. Outputs `data/model_output.json`,
  `data/projections.csv`, `data/breakeven.json`.
- **2026-11-10** — T07 complete. 11 HTML pages + stylesheet in `docs/`. No build step,
  no dependencies, no JavaScript. Self-contained static site.
- **2026-11-10** — T08 complete. `tools/check.py` validates: 11/11 pages, 0 broken
  internal links, 0 unclosed structural tags, 0 malformed values. Nine unverified items
  published on `docs/flagged.html` with the document that would resolve each.

## Sources

See `research/00-source-log.md` for S01–S27 and `docs/sources.html` for the published,
linked version. All figures on the site trace to a row in one of those two tables.

## Verification performed

| Check | Method | Result |
|---|---|---|
| Every table row has a source link | Manual review of all 11 pages | Pass — unverified rows marked `Owner`/`Unverified`, not filled in |
| Internal links resolve | `tools/check.py` | Pass — 0 broken |
| HTML structural balance | `tools/check.py` | Pass — 0 errors |
| No `NaN` / `None` / malformed currency in output | `tools/check.py` | Pass |
| Model reconciles to actual tax bill | 2025 bill $7,207 vs model $7,330 | Pass — 1.7% variance, disclosed |
| Statistics quoted in prose match model output | Recomputed from `data/model_output.json` | Pass after correcting one prose figure (2.7% not 3.2%) |
| Prop 19 $1M cap current value | BOE LTA 2025/009 | Verified $1,044,586 (not the stale $1,000,000) |
| Federal exclusion 2026 | IRS + IR-2025-103 | Verified $15,000,000 |
| CA inheritance tax | R&TC §13301 full text | Verified $0 |

## Irregularities flagged (non-blocking)

1. Property A implied effective tax rate 1.335% vs. typical county 1.1488%.
2. Property B implied effective tax rate 2.135% vs. SF secured rate 1.18162%.
3. Both insurance figures are owner estimates, not quotes; Property B's is almost
   certainly too low for a 3-unit rental.
4. Earthquake coverage status unknown and excluded from carrying costs.
5. Cash/securities value in the estate not disclosed — cannot determine estate tax
   liability for a single decedent.
6. No appraisal for either property.
7. Original cost basis unknown (immaterial at inheritance due to the step-up).
8. Trust funding not confirmed.
9. Number of heirs not disclosed — affects Prop 19 occupancy eligibility.

All nine are published on the site's Flagged for Review page with the specific document
that would resolve each.
