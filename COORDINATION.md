# COORDINATION.md — Shared Task Board

**Branch:** `arena/5c7cfaf6-tino1` | **Session:** Primary (arena/5c7cfaf6) | **Date:** 2026-11-10

## Overview
This file tracks all tasks for the Cupertino + San Francisco Inheritance Decision project.
All work is done on `arena/5c7cfaf6-tino1`. No parallel sessions active at start — primary session claims all scopes.

## Task Board

| # | Task | Status | Owner Session ID | Files / Scope | Sources / Verification | Notes |
|---|------|--------|------------------|---------------|------------------------|-------|
| 1 | Executive Summary + Landing Dashboard | done | arena/5c7cfaf6 | docs/index.html, docs/css/style.css, docs/js/app.js | IRS Rev Proc 2025-32, BOE Prop13/19, SCC Assessor, SF Treasurer | Landing verified 200, all nav links OK — committed e1522a4 |
| 2 | Cupertino House Detail Page | done | arena/5c7cfaf6 | docs/cupertino.html | SCC Assessor, tax rate book FY24-25, RTC §51, BOE LTA inflation factors | History table flagged as unverified (user-provided) — committed |
| 3 | San Francisco House Detail Page | done | arena/5c7cfaf6 | docs/sanfrancisco.html | SF Assessor-Recorder, SF Treasurer 1.18268325%, Rent Board | Rental $7,150 flagged; triplex income modeled — committed |
| 4 | Trust Inheritance Process (Step-by-Step) | done | arena/5c7cfaf6 | docs/inheritance.html | CA Probate Code §§16061.7, 18105, 850, 10810; RTC §§480, 63.2; IRC §§1014, 2010 | 14 steps, 1-year Prop19 clock, placeholders only — committed |
| 5 | Tax Law Hub (Federal/State/Local) | done | arena/5c7cfaf6 | docs/taxes.html | IRS, FTB, BOE, CA Leg Info, SCO, PL 119-21 §70106 | $15M permanent, no CA estate tax, cap $1,044,586 verified — committed |
| 6 | Projections 2026-2050 (Values, Assessed, Taxes, Costs) | done | arena/5c7cfaf6 | docs/projections.html, docs/data/projections.json, docs/data/projections.csv | Prop13 2% cap (RTC §51), FHFA HPI 4.5%/3.8%, BLS CPI 3%, 1.18% rate | All dollars rounded to $10; 25-yr table + CSV/JSON — committed |
| 7 | Decision Analysis (Live / Rent / Sell) | done | arena/5c7cfaf6 | docs/decision.html | Market rent, insurance surveys, portfolio 7%→6.5% net | NPV 10/20/30yr: Sell wins by ~$1M at 10yr — committed |
| 8 | Insurance & Operating Cost Research | done | arena/5c7cfaf6 | Referenced in cupertino/sanfrancisco/projections | Policygenius CA avg $1,383, SF $1,235–1,244, NerdWallet $2,230, CA DOI | Placeholders flagged — formal quotes needed — committed |
| 9 | Flagged for Review Page | done | arena/5c7cfaf6 | docs/flagged.html | All verification notes | 10 flagged items published, no blocking — committed |
| 10 | Sources & Verification Index | done | arena/5c7cfaf6 | docs/sources.html | All official sources with URLs | Every table row traceable; verification log included — committed |
| 11 | Site Build Verification + GitHub Pages Deploy | done | arena/5c7cfaf6 | docs/.nojekyll | Site builds: all 9 HTML pages 200, no broken internal links, charts via Chart.js CDN — verified via python http.server |
| 12 | PR to main + Merge | in progress | arena/5c7cfaf6 | GitHub PR | — | Creating PR now |

## File Ownership (to avoid conflicts)
- Primary session owns all `docs/*` until final integration.
- No other sessions currently claimed.

## Verification Log
- [x] Every table row has source link — enforced.
- [x] If value can't be confirmed from official source, left blank/flagged — done (historical bills, market estimates, insurance).
- [x] Never infer or fill in values — verified.
- User-provided historical property tax tables: marked **UNVERIFIED — requires county bill cross-check** (see Flagged page) — done.
- Market value estimates ($3.1M Cupertino, $1.8M SF Nov 2026): marked **User-provided estimate — not an appraisal** — done.
- Insurance $1,500 estimates: marked as **Estimate — actual quote required** — done.

## Handoff Log
- No handoffs yet. Claims older than 60 min with no commits may be taken over per instructions (not applicable — single session).

## Final Integration Checklist
- [x] All 9 pages build and render (index, cupertino, sanfrancisco, inheritance, taxes, projections, decision, sources, flagged)
- [x] All internal nav links work (verified via grep — no missing targets)
- [x] External source links spot-checked (IRS, BOE, SCC, SF Treasurer, LegInfo)
- [x] No PII in output (placeholders used: [Grantor], [APN: ***-**-***], addresses)
- [x] Numbers rounded to $10
- [x] .nojekyll present, site verified with no broken links (http.server 200)
- [x] GitHub Pages config to be enabled via API after PR
- [ ] PR created and merged to main (in progress)
- [ ] Deploy confirmed live (after merge)
