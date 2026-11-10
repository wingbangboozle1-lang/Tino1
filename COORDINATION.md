# COORDINATION.md — Shared Task Board

**Repository:** `wingbangboozle1-lang/Tino1`
**Purpose:** Cupertino + San Francisco inherited-property decision analysis.
**Last updated:** 2026-11-10

## Session registry

| Session ID | Branch | Started | Status |
|---|---|---|---|
| `arena-e25621af` | `arena/e25621af-tino1` | 2026-11-10 | active |

> This workspace only permits work on the branch `arena/e25621af-tino1` (session branch).
> Sub-branches (`session-<id>/<task>`) are therefore represented as **task IDs** and
> non-overlapping **file scopes** on that single branch. This preserves the intent of the
> coordination protocol (no overlapping writes, no duplicate work) while respecting the
> branch constraint. Every claim is committed and pushed immediately.

## Task board

| Task ID | Description | Status | Owner | File scope |
|---|---|---|---|---|
| T01 | Repo review + coordination scaffold | in progress | `arena-e25621af` | `COORDINATION.md`, `README.md` |
| T02 | Research: CA property tax (Prop 13 / Prop 19 / reassessment) | unclaimed | — | `research/02-property-tax.md` |
| T03 | Research: inheritance/estate tax (federal + CA) | unclaimed | — | `research/03-estate-tax.md` |
| T04 | Research: carrying costs (water, electricity, insurance, maintenance) | unclaimed | — | `research/04-carrying-costs.md` |
| T05 | Research: rental market, rent control, SF transfer tax | unclaimed | — | `research/05-rental-and-transfer.md` |
| T06 | Financial model + projections engine | unclaimed | — | `tools/`, `research/06-model.md` |
| T07 | Build GitHub Pages site (landing + subpages) | unclaimed | — | `docs/` |
| T08 | Verification pass (line by line, source links) | unclaimed | — | `research/verify/` |
| T09 | Integration, PR to `main`, merge, Pages deploy confirm | unclaimed | — | `main` merge |

## Log

- **2026-11-10** — `arena-e25621af` created this board. Repo contained only `README.md`
  at commit `fd4bd84`. GitHub Pages already enabled: source = `main` branch, path `/`,
  URL https://wingbangboozle1-lang.github.io/Tino1/ , build type `legacy`, HTTPS enforced.
