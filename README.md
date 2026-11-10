# Tino1 — Cupertino & San Francisco Inheritance Decision Hub

**Live site:** GitHub Pages (Cayman theme) — `https://wingbangboozle1-lang.github.io/Tino1/`

> **Privacy:** No personal information appears on the site. All names/addresses/APNs are placeholders (e.g., `Grantor Trust A`, `Property 95014`). Keep private records in your trust file, not in this repo.
> **Money:** All figures rounded to nearest $10.

## What this is
A verified, line-by-line decision framework for two California properties:

- **Cupertino 95014** — est. $3.10M Nov 2026, assessed $550,537 (Prop 13 base), tax ~$7,210/yr, solar net credit, low maintenance.
- **San Francisco 94122** — Outer Sunset 3-unit, est. $1.80M Nov 2026, assessed $114,248, tax ~$2,440/yr, two units rented $7,150/mo, third unit owner-occupiable.

The plan: inherit the Cupertino house by revocable living trust around **2040–2050**, then choose to **live in it, rent it, or sell and reinvest** — while the SF house remains the base.

## Site map
- `/index.html` — Executive summary (the answer, key numbers, 3 paths, risks, next steps)
- `docs/cupertino.html` — Cupertino file (history, rate build, costs, Prop 19 scenarios)
- `docs/sanfrancisco.html` — SF file (history, rental accounting, landlord taxes)
- `docs/compare-decisions.html` — Side-by-side decision model (10-yr + 20-yr wealth)
- `docs/process.html` — Step-by-step inheritance process (forms, deadlines)
- `docs/inheritance-tax.html` — Local / state / federal tax law (Prop 13/19, estate, gift, step-up, cap gains)
- `docs/projections.html` — Model 2026–2050 (value, assessed, tax, portfolio) + sensitivity + CSV downloads
- `docs/operating-costs.html` — Insurance, water/electric, maintenance breakdowns
- `docs/sources.html` — Every row's official source (IRS, BOE, FTB, SCO, Assessor, Treasurer, C.A.R., CDI, NAIC)
- `docs/flagged.html` — Unverified items left blank/flagged (does not block merge)
- `data/` — Machine-readable CSV/JSON (projections, scenarios, assumptions)

## How we built it
1. **Line-by-line verification** — each table row links to an official source. If unverifiable, left blank and flagged.
2. **Numbers rounded to $10** per request.
3. **Projections** assume: 3.5% home appreciation (C.A.R. 3.6% statewide, 2–6% Bay Area), 2% Prop 13 cap, Prop 19 cap $1,044,586 (BOE LTA 2025/009) inflating 2%/yr, 5% insurance inflation, 3% rent/water/electric, 6.5% 70/30 portfolio.
4. **Three paths modeled** (inherit 2045 → 2055):  
   - **A. Live in Cupertino** (Prop 19 partial shield) + rent SF fully  
   - **B. Rent out Cupertino** (full reassessment — weakest)  
   - **C. Sell promptly** (stepped-up basis → $0 cap gain if sold near FMV → reinvest → highest liquid wealth)

See `docs/compare-decisions.html` for the full math.

## Verification
Every table row has a **Source** column. Key official sources:

- IRS Form 709 Instr. 2026 + Rev Proc 2025-32 ($15M exemption, $19k gift exclusion) — [IRS](https://www.irs.gov/pub/irs-dft/i709--dft.pdf)
- BOE Prop 13 / Prop 19 — [BOE](https://www.boe.ca.gov/prop19/) + LTA 2025/009 ($1,044,586)
- Santa Clara County Assessor Annual Report 2025 — [SCC](https://www.sccassessor.org/)
- SF Treasurer FY2025-26 rate 1.18268325% — [SF Treasurer](https://sftreasurer.org/property-tax)
- C.A.R. 2026 forecast — [C.A.R.](https://www.car.org/aboutus/newsreleases/2026housingforecast)
- CDI / NAIC insurance — [CDI](https://www.insurance.ca.gov/), [NAIC](https://content.naic.org/reports/homeowners-insurance-report)
- FTB, Cal Courts self-help — [FTB](https://www.ftb.ca.gov/), [Courts](https://selfhelp.courts.ca.gov/probate)

If you spot an error, open an issue with the source link — we flag rather than infer.

## Coordination
See `COORDINATION.md` for task board, file ownership, and verification log. This repo started empty; single session `arena/37f99282-tino1` built all tasks on this branch.

## Local dev
```bash
# Jekyll (optional)
bundle install
bundle exec jekyll serve
# or just open index.html in a browser — no build required
```

## GitHub Pages
- Theme: `jekyll-theme-cayman` via `remote_theme`
- Source: this branch, root `/` (enable in repo Settings → Pages → Source: branch `arena/37f99282-tino1`, folder `/ (root)`)
- Custom domain: none

## License
Internal family decision support — not legal/tax advice. Consult CA licensed attorney & CPA.

## Changelog
- 2026-11-10 — v1.0 initial site: executive summary, projections 2026–2050, decision model, tax law, process, sources, flagged, data CSVs.
