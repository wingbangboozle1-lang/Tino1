# Independent integration safety audit

Date: 2026-11-11. Scope: spot checks of existing sites and model, not an exhaustive line-by-line verification. Do not rely on existing scenario rankings until the issues below are fixed and independently tested.

## Critical: public privacy exposure

The GitHub Pages source is `main:/`, so the repository's root files and subdirectories are published. The root property page, `docs/cupertino.html`, `docs/sanfrancisco.html`, and machine-readable data contain original user-supplied assessment and tax figures, including unrounded amounts. Several pages combine property location and distinctive facts. Rounding to $10 does not prevent linkage to public assessment rolls, especially across a series. A second dashboard withholds much of the history but still publishes a precise rounded anchor. The repository, coordination log, model outputs, generated pages, historical revisions and GitHub Pages may all disclose details; merely removing visible HTML is insufficient. Avoid copying identifiers into bug reports. Site takedown/access restriction and history/cache remediation require repository-owner action and coordination. A public GitHub Pages site cannot safely host internal-only inputs.

## Critical: wrong ownership and reassessment model

The request says the San Francisco home is already owned by the inheritor. `analysis/model.py` assumes that this property is fully reassessed in the inheritance year (`av_b = val_b_T`), and its estate table includes both properties in the transferor's estate. The root and dashboard summaries also state that this property is inherited or reassessed on the other property's transfer. These are inconsistent with the supplied ownership fact, materially distort costs and estate-tax exposure, and can reverse recommendations. An unrelated death alone is not evidence of a change in ownership. Ownership, fractional interests, and any separate reassessment triggers still need legal verification. [California Board of Equalization, change in ownership](https://www.boe.ca.gov/lawguides/property/current/ptlg/annt/220-0000-all.html); [IRS estate tax FAQs](https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes).

## Critical: unconditional basis claim

The dashboard says inheritance gives a full step-up, and the root page similarly states the basis resets. Trust type and estate inclusion are not established by the request. Under the facts in IRS Revenue Ruling 2023-2, certain irrevocable grantor trust assets not included in the grantor's estate do not receive a section 1014 adjustment. Basis can also step down, and sale proceeds depend on selling expenses, timing and other facts. [IRS Revenue Ruling 2023-2](https://www.irs.gov/irb/2023-16_IRB).

## Other unresolved problems

- User-provided values, forecasts and assumptions are displayed in tables without a row-specific official source, despite claims that every row has one. An official rule source cannot verify an individual's bill, a future price, or a subjective model assumption. Leave unverified factual cells blank, distinguish assumptions and calculated scenarios, and avoid claims of universal verification.
- The 2026 federal basic exclusion is $15 million, but the remaining exclusion for the actual decedent cannot be determined without taxable gifts, estate assets, deductions, citizenship/residency and any portability election. The separately owned home is not automatically part of the decedent's gross estate. Filing can be needed to elect portability even below the threshold. [IRS estate and gift tax updates](https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax); [IRS estate FAQs](https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes).
- Proposition 19 requires a qualifying relationship, transferor's principal residence, transferee occupancy and filing; its value limit and deadlines are conditional, not guaranteed. [BOE fact sheet](https://www.boe.ca.gov/pdf/pub801.pdf).
- `analysis/check_site.py` passes its own 14-page internal checks, but does not establish that every claim on every site is correct, that external links work, or that personal information is absent. Multiple competing sites contain conflicting recommendations and assumptions. Full site-wide privacy, source, external-link, arithmetic and scenario tests remain outstanding.
- A fixed annual return is not a realistic 50-year economic path. Black-swan paths need explicit shock timing, recovery, inflation and sequence risk, with clearly labeled hypothetical rather than verified predictions.

## Deployment status

GitHub reports an existing Pages build of main commit `2a16da867ed2aeab57be27f773e79ce7a56e1452` as built. This confirms build status only, not safety or accuracy. Integration, publication approval and merge must not be represented as completed while the issues above persist.
