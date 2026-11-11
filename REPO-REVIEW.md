# Repository review — Tino1

**Review date:** 2026-11-11 UTC
**Review session:** `arena/ad120b45`
**Scope:** current root site, `final/` generator/model/checker, source register, privacy controls, and retained legacy editions.

This is a technical and source-verification record, not legal, tax, investment, appraisal, insurance, or property-management advice. The public site uses **Property A** for the Cupertino home and **Property B** for the San Francisco home. No names, street addresses, APNs, contact details, or private-document contents are published.

## 1. Canonical site and repository structure

| Finding | Result | Source / verification |
|---|---|---|
| One public front door | **Closed:** the current edition is the root site, beginning at [`index.html`](index.html). Root navigation links the current pages, including [`properties.html`](properties.html), [`decision.html`](decision.html), [`projections.html`](projections.html), [`black-swan.html`](black-swan.html), [`process.html`](process.html), [`law.html`](law.html), [`estate-cash.html`](estate-cash.html), [`costs.html`](costs.html), [`flagged.html`](flagged.html), [`sources.html`](sources.html), and [`review.html`](review.html). | `python3 final/check.py .` — 20 root HTML pages, 640 table rows, 1,587 links; zero reported failures. |
| Retained parallel work | `dashboard/`, `docs/`, `site/`, `archive/`, and session-named research/model directories remain for traceability. Their HTML pages are marked superseded and are not linked from the current navigation. | [`versions.html`](versions.html); the legacy pages carry a visible superseded notice. |
| GitHub Pages exposure | The Pages source is the repository's main branch, so retained directories remain publicly reachable by URL. This is disclosed rather than treated as private storage. | [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) · owner decision remains on whether to make the repository private or rewrite history. |
| Reproducibility | The current site is generated with the standard-library-only model and builder. | `python3 final/model.py && python3 final/integrate.py`; `python3 -m py_compile final/*.py`; all passed. |

## 2. Privacy review — highest urgency

| Check | Result | Verification |
|---|---|---|
| Personal identifiers | **Pass for current site:** no names, street addresses, APNs, phone numbers, or private e-mail addresses were added. People are placeholders: “the Transferor” and “the Inheritor.” | `final/check.py` PII scan; current root pages use `noindex, nofollow`. |
| Owner-provided history | **Withheld from the current canonical site:** the supplied year-by-year assessment and tax-bill series is not reproduced. | [`properties.html`](properties.html) and [`flagged.html#P01`](flagged.html#P01). |
| Publication rounding | **Pass for canonical site:** model and owner planning dollars are displayed at $10 increments. Official legal constants and rates remain linked to the source; planning displays are rounded. | `python3 final/check.py .` — 2,092 dollar figures checked; privacy fingerprints clean. |
| Git history | **Open owner action:** earlier commits may still be readable in public Git history even though the current files are scrubbed. An agent did not force-rewrite history. | [`README.md`](README.md) privacy notice; owner must decide whether to privatize or rewrite history. |
| Private records | Keep bills, trust instruments, basis records, insurance quotes, rent ledger, and utility statements offline for licensed advisers. They are not required for the public site. | [`flagged.html#P03`](flagged.html#P03). |

## 3. Material ownership distinction

The **San Francisco property is already owned by the Inheritor**. It is not the asset being inherited in this analysis. The current model therefore:

- does not treat the Transferor's death as a change in ownership of Property B;
- does not apply a death-time reassessment to Property B;
- does not give Property B a new inherited basis;
- does not add Property B to the Transferor's gross estate; and
- carries Property B's existing rent, utilities, insurance, and ordinary assessment growth as a separate status-quo property.

Property A is different: it passes through the trust at the Transferor's death. A revocable trust generally changes ownership when it becomes irrevocable at death; an inheritance is dated at death. Whether any Prop 19 exclusion applies and whether basis resets depend on the actual trust, relationship, occupancy, filing, and gross-estate facts.

**Sources read:** [BOE Rule 462.260](https://boe.ca.gov/proptaxes/pdf/rules/Rule462_260.pdf), [IRS estate tax](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax), [BOE Proposition 19](https://www.boe.ca.gov/prop19/), [R&TC §63.2](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2.).

## 4. Legal and tax verification register

| Topic | Canonical treatment | Status and official source |
|---|---|---|
| Federal estate threshold | The model shows approximately **$15,000,000** for a 2026 death and approximately **$15,480,000** for 2027. It measures the Transferor's whole gross estate, adjusted taxable gifts, deductions, and elections—not “cash inherited” in isolation. | Verified against [IRS estate-tax threshold table](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax) and [Rev. Proc. 2026-35](https://www.irs.gov/pub/irs-drop/rp-26-35.pdf). Future years are projections, not enacted thresholds. |
| Federal estate-tax rate | The model uses the top **40%** rate only for a planning illustration above the applicable exclusion; actual Form 706 computation is progressive and fact dependent. | [IRS Form 706 instructions](https://www.irs.gov/instructions/i706). |
| California estate/inheritance tax | No California estate-tax return is required for deaths on or after January 1, 2005; the older inheritance-tax cutoff is stated by the State Controller. | [California State Controller](https://www.sco.ca.gov/ardtax_estate_tax.html). |
| Inherited basis | The model assumes a reset to date-of-death FMV only when the asset is included in the gross estate. A trust outside the gross estate is shown as a sensitivity case. | [IRS inherited-property FAQ](https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances) · [Rev. Rul. 2023-2](https://www.irs.gov/irb/2023-16_IRB). |
| Prop 19 eligibility | Property A receives partial relief only in the live-in case: eligible family relationship, qualifying principal residence, move-in within one year, homeowners' exemption within one year, and timely exclusion claim. Renting or leaving it empty is modeled as full reassessment. | [BOE Prop 19](https://www.boe.ca.gov/prop19/) · [R&TC §63.2](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2.) · [BOE LTA 2026/026](https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf). |
| Prop 19 value cap | The published amount for the current 2025–2027 window is rounded in planning displays; the official exact amount and the every-other-February prior-year HPI mechanism are linked. The 2027 amount is intentionally flagged until the official adjustment is published. | [BOE LTA 2025/009](https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf) · [`flagged.html#U04`](flagged.html#U04). |
| Filing clocks | The site shows the trust notice, change-in-ownership statement, Form 706, homeowners' exemption, and Prop 19 claim deadlines separately. They are not interchangeable. | [Probate Code §16061.7](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.) · [R&TC §480](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.) · [IRS estate FAQ](https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes). |

## 5. Operating-cost verification

| Cost | Property A — Cupertino | Property B — San Francisco | Status |
|---|---:|---:|---|
| Water | Rounded planning midpoint from the owner's stated range: **$1,500/year**. | Rounded planning midpoint for three units: **$4,380/year**. | User-supplied planning inputs; no parcel bills published. Official rate material is linked on [`properties.html`](properties.html) and [`costs.html`](costs.html). |
| Electricity / solar | Rounded planning credit: **-$180/year**. | Rounded planning amount: **$600/year**. | Solar tariff and interconnection date are not confirmed. [CPUC NEM/NBT](https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing); [`flagged.html#U05`](flagged.html#U05). |
| Insurance | Owner estimate **$1,500/year** is used only as a flagged planning input; official ZIP-level quote is blank. | Same treatment; a three-unit landlord/dwelling-fire quote is required. | [California Department of Insurance comparison tool](https://www.insurance.ca.gov/01-consumers/105-type/9-compare-prem/index.cfm) says survey results are not quotes. [`flagged.html#U01`](flagged.html#U01). |
| Repairs and maintenance | **$6,000/year** assumption. | **$12,000/year** assumption. | Not independently confirmed; sensitivity tests double maintenance. [`flagged.html#A08`](flagged.html#A08). |
| Rent | Property A uses HUD FY2026 SAFMR as a labeled proxy, not a private rent appraisal. | Property B uses the owner's rounded two-unit rent input; rent-control status remains flagged. | [HUD SAFMR 95014](https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026) · [SF Rent Board](https://www.sf.gov/learn-about-rent-increases-san-francisco/). |

## 6. Economic model and black-swan review

The baseline is deliberately not presented as a forecast. It is a planning case with constant nominal assumptions, while the separate black-swan page replays variable growth and inflation. The stress set includes historical 1976–2025 sequences, California housing slumps, high-inflation/stagflation, the 2007–2012 crash sequence, a Depression-era national path, a Japan-style stagnation path, and a savings/Treasury alternative.

The current model's baseline headline is **sell Property A after inheritance, keep Property B, and reinvest**, but the result is not universal. The first decade is the main sequence risk; the Japan-style path and cash/T-bill case can favor retaining/renting. The site therefore shows a sensitivity table and a 50-sequence count rather than presenting “sell” as a certainty.

| Model item | Treatment | Source / limitation |
|---|---|---|
| CPI and home-price history | FRED series for BLS CPI and FHFA San Jose/San Francisco/California HPI. | [FRED CPI](https://fred.stlouisfed.org/series/CPIAUCSL) · [FHFA San Jose](https://fred.stlouisfed.org/series/ATNHPIUS41940Q) · [FHFA San Francisco](https://fred.stlouisfed.org/series/ATNHPIUS41884Q). |
| Cash/risk-free reference | Treasury daily yields are shown as a current reference, not a guaranteed future return. | [U.S. Treasury daily yield curve](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView). |
| Long-run stock return series | The long-run total-return table is academic, not a government series; it is labeled and flagged rather than presented as an official forecast. | [NYU Stern table](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html) · [`flagged.html#S02`](flagged.html#S02). |
| Baseline assumptions | Inflation, home growth, portfolio return, rent growth, insurance growth, repairs, vacancy, management, tax brackets, and sale costs are planning assumptions. | [`flagged.html`](flagged.html) lists each assumption and sensitivity. |

## 7. Verification commands and results

```text
python3 -m py_compile final/*.py                 PASS
python3 final/model.py                           PASS; rounded outputs generated
python3 final/integrate.py                       PASS; 1,967 internal links, 0 broken
python3 final/check.py .                         PASS; 20 pages, 640 sourced rows, privacy clean
```

The checker also verifies the Prop 19 worked example, checks that Property B's modeled assessment does not jump by more than the annual cap, confirms that the live-in value is not above the full-reassessment value, checks internal anchors, and scans for street-address, phone, e-mail, parcel-pattern, and stored owner-figure fingerprints.

## 8. Remaining flagged items

These items are intentionally visible on [`flagged.html`](flagged.html) and do not block publication:

1. Trust type, gross-estate inclusion, family relationship, portability, and the Inheritor's filing status.
2. Private parcel-level assessment/tax bills, basis records, rent ledger, utility bills, insurance quotes, tax-rate areas, solar interconnection record, and bedroom/rent condition.
3. Future law, future federal exclusion indexing, future Prop 19 adjustment, future rates, insurance availability, and market returns.
4. Academic return history and the Japan stress path's non-U.S. data limitations.
5. Public Git history may contain earlier versions; only the owner can authorize a history rewrite or repository privacy change.

## 9. Bottom line

The current site is a privacy-conscious, source-linked planning tool. It separates the inherited Cupertino decision from the already-owned San Francisco property, distinguishes verified law from owner inputs and assumptions, shows rounded costs and projections, and preserves the uncertainty that cannot be resolved without private documents or future facts.
