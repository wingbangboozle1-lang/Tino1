# Tino1 — Cupertino & San Francisco Inheritance Decision Hub

**Live site (GitHub Pages):** https://wingbangboozle1-lang.github.io/Tino1/  
**Canonical dashboard:** [`dashboard/`](dashboard/index.html) — 15 pages, model-generated, line-verified (linked from the landing page).  
Landing page: [`index.html`](index.html) (clean entry point with category links). Archive sites preserved at [`docs/`](docs/index.html), [`site/`](site/index.html), and [`mirror-archived-2026-11-10.html`](mirror-archived-2026-11-10.html) — no session's work was discarded.

Anonymized decision-analysis site for a 2040–2050 trust inheritance: two CA houses (Cupertino 95014 ~$3.1M, San Francisco 94122 ~$1.8M), live vs rent vs sell+invest.

> **Privacy:** No personal information on the site — placeholders only (e.g., `Grantor Trust A`, `[Property Address]`, `[APN: ***]`).  
> **Money:** All dollars rounded to nearest $10.

## Site maps (merged from two parallel sessions — no work discarded)

**Canonical dashboard (session arena/5c7cfaf6 — 9-page lab):** served from `docs/`:
- `docs/index.html` — Executive Summary dashboard (metrics, charts, decision at-a-glance)
- `docs/cupertino.html` — Cupertino 95014 detailed profile
- `docs/sanfrancisco.html` — SF 94122 triplex profile
- `docs/inheritance.html` — Trust inheritance step-by-step (14 steps, Prop 19 clocks)
- `docs/taxes.html` — Tax Law Hub (federal/state/local, estate, Prop 13/19, step-up, cap gains)
- `docs/projections.html` — Projections 2026–2050 (market, assessed, tax, costs, charts + CSV/JSON)
- `docs/decision.html` — Decision analysis: live vs rent vs sell & reinvest (NPV 10/20/30 yr)
- `docs/sources.html` — Sources & verification index (every row traced)
- `docs/flagged.html` — Flagged for Review (unverified items, not blocking)

**Additional pages (session arena/37f99282-tino1 — detailed complements):**
- `docs/compare-decisions.html` — Side-by-side 10-yr/20-yr wealth model (6.5% portfolio vs housing)
- `docs/process.html` — Trust administration process with forms/deadlines checklist
- `docs/inheritance-tax.html` — Expanded federal/state tax tables (gift, GST, NIIT, QBI)
- `docs/operating-costs.html` — Insurance, water/electric (SFPUC/SJ Water/PG&E), maintenance
- `index.html` (repo root) — Mirror executive summary for Pages root build
- `data/assumptions.json`, `data/projections-*.csv`, `data/inheritance-scenarios.json` — machine-readable

**Parallel session model & research (arena/3676d6a0):**
- `model/project.py` + `model/assumptions.md` — reproducible Python model
- `research/tax-law.md`, `research/utilities-insurance-market.md` — official-source notes
- `data/cupertino_projection.csv`, `data/sanfrancisco_projection.csv`, `data/model_summary.json`

## What we built (combined)
1. **Line-by-line verification** — every table row links to an official source. If unverifiable, left blank/flagged.
2. **Numbers rounded to $10** per request.
3. **Projections:** 3.5–4.5% Cupertino / 3.8% SF appreciation (C.A.R. 3.6% statewide, 2–6% Bay Area), 2% Prop 13 cap (RTC §51), Prop 19 cap $1,044,586 (BOE LTA 2025/009) biennially FHFA HPI, 5% insurance inflation, 3% rent/water/electric, 6.5% 70/30 portfolio.
4. **Three paths (inherit ~2045 → 2055/2065):**
   - **A. Live in Cupertino** (move in ≤12 mo, Prop 19 partial shield) + rent SF fully
   - **B. Rent out Cupertino** (full reassessment — weakest; CA taxes rent as ordinary)
   - **C. Sell promptly** (stepped-up basis IRC §1014 → ~$0 gain if sold near FMV → reinvest → highest liquid wealth, ~$2M+ ahead at 10 yr)
5. **Inheritance process:** 14 steps, PCOR, BOE-19-P (3 yr), HO exemption (1 yr), Form 706 only above $15M.

See `docs/decision.html` + `docs/compare-decisions.html` for full math.

## Verification
Key official sources (Source pages list all):
- IRS Form 709 Instr. 2026 + Rev Proc 2025-32 ($15M exemption, $19k gift) — [IRS](https://www.irs.gov/pub/irs-dft/i709--dft.pdf)
- BOE Prop 13/19 + LTA 2025/009 ($1,044,586) — [BOE](https://www.boe.ca.gov/prop19/)
- SCO no CA estate tax — [SCO](https://www.sco.ca.gov/state_finances_estate_tax.html)
- SCC Assessor Annual Report 2025 — [SCC](https://www.sccassessor.org/)
- SF Treasurer 1.18268325% FY25-26 — [SF Treasurer](https://sftreasurer.org/property-tax)
- C.A.R. forecast — [C.A.R.](https://www.car.org/aboutus/newsreleases/2026housingforecast)
- CDI / NAIC insurance — [CDI](https://www.insurance.ca.gov/), [NAIC](https://content.naic.org/reports/homeowners-insurance-report)
- FTB, Cal Courts — [FTB](https://www.ftb.ca.gov/), [Courts](https://selfhelp.courts.ca.gov/probate)

## Coordination
See `COORDINATION.md` for combined 16-task board, file ownership, verification & merge-conflict logs. Built by two parallel sessions + final integrator (arena/5c7cfaf6), now merged with arena/37f99282-tino1 additions — no discarded work.

## Local dev
```bash
# no build required — open docs/index.html or index.html
python -m http.server 8000
# or Jekyll (Cayman theme via _config.yml in root, .nojekyll in docs/)
bundle exec jekyll serve
```

## GitHub Pages
- Canonical: `docs/` folder via Pages (current live build 1356405344) — `https://wingbangboozle1-lang.github.io/Tino1/`
- Mirror root `index.html` also builds via legacy Pages source (branch arena/37f99282-tino1 → now main after merge)

## License
Internal family decision support — not legal/tax advice. Consult CA attorney & CPA.

## Changelog
- 2026-11-10 — v1.0 initial site (executive summary, projections, decision, tax hub, flagged, data CSVs)
- 2026-11-10 — v1.1 merged parallel sessions (model/research + 4 complement pages, no discard, integrated Pages deploy)
- 2026-11-11 — v1.2 final integration (session `arena/62c87525`): **black swan economic conditions section** (user requirement), 50-year variable-rate projections 2026–2076, clean root landing page, one canonical dashboard (`dashboard/`, 15 pages), central flagged list extended to 27 items

## Session `6ea079fa` — verified dataset + after-tax scenario dashboard (`analysis/`, `dashboard/`)

**Live:** https://wingbangboozle1-lang.github.io/Tino1/dashboard/ — 14 pages: dashboard, executive summary, properties, step-by-step process, Prop 19, estate tax, tax law, operating costs, year-by-year projections 2026–2055, six after-tax scenarios with a 27-case sensitivity grid, pending law changes, **Flagged for Review** (23 items), sources, methodology.

- `analysis/data/*.csv` — every fact row carries an official source URL and a status (`verified` / `derived` / `user-supplied` / `assumption` / `unverified`); unverifiable values are blank and flagged, never inferred. Owner-supplied assessment histories are deliberately not published (privacy); all amounts rounded to $10.
- `analysis/model.py` → `analysis/data/projections/*.csv`, `analysis/data/scenarios.csv`, `dashboard/data/model_output.json`; `analysis/build_site.py` renders `dashboard/`; `analysis/check_site.py` runs link / source / privacy checks.
- Reproduce: `python3 analysis/model.py && python3 analysis/build_site.py && python3 analysis/check_site.py` (standard library only).

## Canonical consolidated site (2026-11-11, session `arena/944a92cd-tino1`, merged with `arena/62c87525`)

> Root `index.html` is ONE canonical 13-page site. Root navigation covers: executive summary, properties, inheritance steps, projections, live/rent/sell, black swans, estate tax, costs, pending changes, flagged, sources, methodology. Session `62c87525` independently published a complementary **black-swan analysis + dashboard-integrated pages** (`dashboard/black-swan.html`, `analysis/data/blackswan_*.csv`, `research/black-swan-economics.md`) — preserved in full; see the cross-links from the root Black swans page. The root portal design of `arena/62c87525` is preserved at `archive/root-portal-62c87525.html`.

## Canonical site (2026-11-11, session `arena/944a92cd-tino1`)

**Live:** https://wingbangboozle1-lang.github.io/Tino1/ — `index.html` is the canonical **Executive summary**. Nav: Executive summary · Properties · Inheritance steps · Projections 2026–2060 · Live/Rent/Sell · **Black swans** · Estate tax · Tax law · Costs · Pending changes · Flagged for Review · Sources · Methodology.

- Privacy first: placeholders only; every user-supplied dollar figure rounded to the nearest **$10** repo-wide (exact statutory constants excepted); assessment histories withheld/rounded; PII grep-audited.
- Every table row → official source or a flag on **Flagged for Review** (25 new P-flags + 23 carried X-flags).
- Headline: sell [Property A] at the step-up (≈ $0 capital-gains tax), reinvest (≈ $5,660,000 net at 2045), live in [Property B]'s vacant unit; keep B's rents. Stagflation is the one regime that flips the answer — see **Black swans** page for the full 7-regime grid and tripwires. Full math: **Live/Rent/Sell** and **Methodology** pages; model: `integrated/model.py`; CSV: `downloads/inheritance-baseline-2026-2060.csv`.
- Legacy multi-session sites (`/docs/`, `/site/`, `/dashboard/`) are superseded but retained; exact figures purged. See **REPO-REVIEW.md** for the line-by-line repo audit (including two verified-dead government URLs corrected with evidence).
- Not legal/tax/investment advice.

## Complementary work preserved from `arena/62c87525` (merged via PR #14; recorded in this merge)

**Live:** https://wingbangboozle1-lang.github.io/Tino1/dashboard/black-swan.html — verified economic history (BLS CPI-U 1976–2025, NBER recession dating, FHFA HPI crash magnitudes, Freddie Mac PMMS rate extremes, CBO Feb 2026 baseline) turned into six **variable-growth** economic scenarios over 50 years (2026–2076): baseline control, historical CPI replay, 1970s stagflation, 2006–12 GFC/Bay-Area crash, Japan-style deflation tail, and the 2020–23 COVID whiplash.

- `analysis/blackswan_model.py` → `analysis/data/blackswan_paths.csv` (every yearly rate used, auditable), `blackswan_projection_*.csv` (year-by-year value / assessed / tax / costs, $10-rounded, Prop 8 handling), `blackswan_stress.csv` (sell vs rent vs live × 3 inheritance years × 6 scenarios).
- Finding: **sell & reinvest at inheritance wins 12 of 18 stress cells and the baseline**; "live in it" wins only housing-boom/replay cells; renting never wins (full reassessment + ordinary-rate rent tax). Crash *timing* vs the death year dominates crash *magnitude*.
- `analysis/build_blackswan.py` → `dashboard/black-swan.html`. Research log with per-figure provenance: `research/black-swan-economics.md`.
