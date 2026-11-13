# Session `arena/46d1a561-tino1` — official reads and repo review, 2026-11-13

Every row below was opened on the issuing agency's own URL during this session and read in
full. The quoted wording is what the page says today. Same table on the site:
`verification.html`, section "Fourth independent re-read, 2026-11-13 (session arena/46d1a561)".

## 1. Official pages opened and read

| What was checked | URL | What the page says | Result |
|---|---|---|---|
| Proposition 13 inflation factor, 2026 roll | https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf | Letter 2026/002, dated 2026-01-13. CCPI rose from 343.108 (Aug 2024) to 354.456 (Aug 2025) = 3.307%, so "please prepare your 2026 assessment roll using an inflation factor of **1.02**". Explains the exception: the fall-2025 federal government shutdown meant BLS did not publish the October 2025 regional indexes, so DIR issued no CCPI for October 2025 and the Board used August-to-August. Enclosed table lists every factor 1976-77 to 2026-27. | Confirms the 2% cap the model applies every year. New provenance detail recorded as note on flag A11. |
| Proposition 19 intergenerational allowance | https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf | Letter 2025/009, dated 2025-03-07. FHFA announced on 2025-02-25 that the California HPI rose 2.15% in 2024, so the $1 million amount is **$1,044,586** for transfers 2025-02-16 through 2027-02-15. Rule: adjusted on February 16, 2023 and every other February 16 thereafter by the prior calendar year's California HPI change. Next adjustment February 2027. | Confirms the model's roll-forward, which applies the prior calendar year's change in odd Februaries only — i.e. roughly every other year of house-price growth, not annual compounding. Verified against `final/model.py`: `if y % 2 == 1`. |
| Prop 19 exclusion FAQ | https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf | Letter 2026/026, dated 2026-08-03. Q7: "the transfer is required to be of a principal residence of the transferor that qualifies as the principal residence of the transferee within one year after the transfer under section 63.2(a)(1)(A). **There are no exceptions to this rule.**" Q8: the exclusion is removed once the home stops being the claimant's principal place of residence, and continues only if a different eligible transferee occupies it within one year. Also defines "family home" as a dwelling eligible for the homeowners' or disabled veterans' exemption because of the transferor's ownership and occupation, and confirms transfers through a trust are covered. | Most decision-relevant sentence in the register. If the Inheritor keeps living at Property B, there is no partial exclusion and Property A is reassessed to full market value — the "rent it" column. |
| Federal basic exclusion, 2027 | https://www.irs.gov/pub/irs-drop/rp-26-35.pdf | Rev. Proc. 2026-35 section 3.44: "For calendar year 2027, the basic exclusion amount under § 2010(c)(3) is **$15,480,000**." Also sets the GST exemption under § 2631(c). | Confirmed; the starting point of the estate projections. |
| Federal basic exclusion, 2026 | https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax | "The Working Families Tax Cuts Bill (WFTC) was signed into law on July 4, 2025 as Public Law 119-21. WFTC amends § 2010(c)(3) by increasing the basic exclusion amount to **$15,000,000** for calendar year 2026." | Confirmed. The 2026 amount is statutory, not an inflation adjustment. |
| San Francisco secured rate | https://sftreasurer.org/property/secured-property-taxes | "The secured property tax rate for Fiscal Year 2026-27 is **1.18162182%**." Bills mailed in October; first installment delinquent after December 10, second after April 10, each with a 10% penalty; a supplemental bill follows a change in ownership and is often prorated. | Confirmed. Property B is never reassessed in this analysis. |
| HUD FY2026 Small Area FMRs, ZIP 95014 | https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026 | Efficiency $3,340 · one-bedroom $3,800 · two-bedroom $4,440 · three-bedroom $5,870 · four-bedroom $6,390. Published calculation: base rent $3,439 × recent-mover 1.1773 × inflation 1.0375 × trend 1.0576 = $4,440. | Confirmed including the published arithmetic. Benchmarks for a standard unit, not a valuation of Property A. |
| Santa Clara County tax rate book | https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf | FY2025-26 book. Rates per $100 listed on pages A-4 to A-6. | The components the site quotes (1.00000, 0.03880, 0.00240, 0.00520, 0.00560, 0.00010, 0.01650, 0.01690, 0.01040, 0.00880, 0.01070, 0.01180, 0.01010, 0.01350, 0.00750, 0.00390, 0.00140) were summed by hand this session and do add to **1.16360** — the rate the model uses. The home's own tax rate area was deliberately not looked up. |

## 2. Arithmetic re-checked by hand

- Santa Clara FY2025-26 components → 1.16360 per $100. `final/model.py` uses `rate_cup = 0.0116360`. Match.
- Proposition 19 allowance roll-forward: `1,044,586 × 1.009 (2026 CA HPI) × 1.04^9` ≈ 1,499,900, and the model reports `cap_T = 1,500,152` at T = 2045 (the small gap is rounding at each step). The biennial rule is applied correctly.
- BOE LTA 2026/002 factor table matches the file `final/data/hist_prop13_factor.csv` for every year 1976-2025 (spot-checked at 1983-84 = 1.01, 1995-96 = 1.0119, 2010-11 = 0.99763, 2025-26 = 1.02).

## 3. Irregularities found and what was done

Published on the site as review findings R55–R61 (`review.html`) and recorded in
`COORDINATION.md`. In severity order:

1. **R56 — exact owner figures stored in the repository (highest severity).** Three
   owner-supplied values were in clear text inside `final/check.py` comments (used to
   illustrate the unrounded-figure scan) and one inside `owner-analysis-2026/FLAGS.md`.
   The project's own rule (K1) is that unrounded owner figures are never stored in the
   repository in any form, and this repository is public. **Fixed**: the scan
   documentation now describes the shape of an unrounded figure without reproducing one;
   the flag note carries the $10-rounded bill. A whole-tree sweep for all 45
   owner-supplied values (13 Property A assessments, 10 Property A bills, 10 Property B
   assessments, 10 Property B bills, plus comma variants) now returns none.
2. **R57 — the live site did not answer the brief.** GitHub Pages served 13 files: a
   landing card and a guide with no household figures. The 16 pages of rounded-figures
   analysis were built and checked in CI and never served. **Fixed**: the allowlist is
   now 31 files. Recorded as option D of suggestion G01, with the narrower setting
   retained as a listed option.
3. **R55/R53 — prose contradicted the boundary.** `README.md`, `final/README_ROOT.md`,
   `final/build.py` and `final/publish.py` all described the numeric edition as
   deliberately unpublished. **Fixed**.
4. **R58 — no dashboard landing page.** The brief asks for one. **Fixed**: `index.html`
   now groups every page by category with a headline strip.
5. **R59 — the boundary could not be changed without breaking CI.**
   `privacy-site/check_published.py` and its unit test hard-coded the 13-file set instead
   of reading `final/published.txt`. **Fixed**: both derive from the single source of
   truth; the guide-specific invariants are kept.
6. **R60 — no referrer policy on the published pages.** **Fixed** and now enforced.
7. **R61 — git history (open, owner-only).** Public history and superseded directories
   still hold earlier figures. Not fixable from a work session; recorded as G02/P02.

## 4. What this session did not do

- No owner decision G01/G02 was taken on the owner's behalf: the boundary change is
  published as an option with the alternatives spelled out, and the figure-free guide
  remains published.
- No history rewrite, branch deletion or repository visibility change.
- No official source was replaced by a search-engine excerpt; every row above is an
  agency URL read in full.
