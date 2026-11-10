# COORDINATION.md — Shared Task Board

**Branch:** `arena/5c7cfaf6-tino1` | **Session:** Primary (arena/5c7cfaf6) | **Date:** 2026-11-10

## Overview
This file tracks all tasks for the Cupertino + San Francisco Inheritance Decision project.
All work is done on `arena/5c7cfaf6-tino1`. No parallel sessions active at start — primary session claims all scopes.

## Task Board

| # | Task | Status | Owner Session ID | Files / Scope | Sources / Verification | Notes |
|---|------|--------|------------------|---------------|------------------------|-------|
| 1 | Executive Summary + Landing Dashboard | in progress | arena/5c7cfaf6 | docs/index.html, docs/css/style.css, docs/js/app.js | IRS Rev Proc 2025-32, BOE Prop13/19, SCC Assessor, SF Treasurer | Building landing page |
| 2 | Cupertino House Detail Page | in progress | arena/5c7cfaf6 | docs/cupertino.html, docs/data/cupertino.json | Same as above + county tax rate books | Includes assessment history table |
| 3 | San Francisco House Detail Page | in progress | arena/5c7cfaf6 | docs/sanfrancisco.html, docs/data/sanfrancisco.json | SF Assessor-Recorder, SF Treasurer | Rental income analysis |
| 4 | Trust Inheritance Process (Step-by-Step) | in progress | arena/5c7cfaf6 | docs/inheritance.html | CA Probate Code, SCP, SCC/SF Assessor BOE-19 forms, IRS Pub 559 | Revocable trust administration |
| 5 | Tax Law Hub (Federal/State/Local) | in progress | arena/5c7cfaf6 | docs/taxes.html | IRS, FTB, BOE, CA Leg Info, SCO | Estate, gift, cap gains, Prop13/19 |
| 6 | Projections 2026-2050 (Values, Assessed, Taxes, Costs) | in progress | arena/5c7cfaf6 | docs/projections.html, docs/data/projections.json | Prop13 2% cap, FHFA HPI, BLS CPI, county rates | All numbers rounded to $10 |
| 7 | Decision Analysis (Live / Rent / Sell) | in progress | arena/5c7cfaf6 | docs/decision.html | Market rent data, insurance sources, NMV assumptions | NPV 10/20/30yr |
| 8 | Insurance & Operating Cost Research | in progress | arena/5c7cfaf6 | docs/data/costs.json, referenced in cupertino/sanfrancisco pages | CA DOI, Policygenius, NerdWallet, Zebra | Avg CA $1,383-$1,653; SF $1,235-1,244; Cupertino ~$926 |
| 9 | Flagged for Review Page | in progress | arena/5c7cfaf6 | docs/flagged.html | All verification notes | User-provided tax history flagged as unverified without bill |
| 10 | Sources & Verification Index | in progress | arena/5c7cfaf6 | docs/sources.html | All official sources with URLs | Line-by-line verification log |
| 11 | Site Build Verification + GitHub Pages Deploy | pending | arena/5c7cfaf6 | docs/.nojekyll, _config.yml, site config | GitHub Pages build logs | Must confirm no broken links |
| 12 | PR to main + Merge | pending | arena/5c7cfaf6 | GitHub PR | — | Do not merge broken site |

## File Ownership (to avoid conflicts)
- Primary session owns all `docs/*` until final integration.
- No other sessions currently claimed.

## Verification Log (entries added as tasks complete)
- [ ] Every table row must have source link — enforced in HTML templates.
- [ ] If value can't be confirmed from official source, leave blank + flag as unverified.
- [ ] Never infer or fill in values.
- User-provided historical property tax tables: marked **UNVERIFIED — requires county bill cross-check** (see Flagged page).
- Market value estimates ($3.1M Cupertino, $1.8M SF Nov 2026): marked **User-provided estimate — not an appraisal**.
- Insurance $1,500 estimates: marked as **Estimate — actual quote required**.

## Handoff Log
- No handoffs yet. Claims older than 60 min with no commits may be taken over per instructions (not applicable — single session).

## Final Integration Checklist (to be completed by this session as final integrator)
- [ ] All 10 pages build and render
- [ ] All internal nav links work
- [ ] All external source links return 200 (manual spot-check)
- [ ] No PII in output (placeholders used)
- [ ] Numbers rounded to $10
- [ ] .nojekyll present, site verified with no broken links
- [ ] GitHub Pages deploy succeeds
- [ ] PR created and merged to main
- [ ] Deploy confirmed live
