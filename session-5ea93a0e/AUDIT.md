# Independent bounded audit — session arena/5ea93a0e-tino1

Checked: 2026-11-12 UTC. Scope: current canonical numeric edition (`final/` and generated root pages), current privacy-first edition (`privacy-site/`), coordination/publication state, and the household inputs supplied in the brief. This is **not** a certification of every historical/legacy file in the repository.

## Method

- Re-opened official source pages/PDFs and recorded the relevant passage in `SOURCES.md`.
- Re-ran the existing model and checkers.
- Inspected model formulas for ownership treatment, tax rules, inferred inputs, and privacy.
- Scanned tracked files for the exact unrounded historical figures supplied in the brief. Exact values are not repeated here.
- Checked GitHub repository visibility, Pages configuration, open PRs, and the coordination board.

## Findings that must be corrected or prominently flagged

| ID | Severity | Finding | Evidence / official context | Required treatment |
|---|---|---|---|---|
| A01 | Critical privacy | The repository is public. Pages exclusions and `noindex` do not protect source files, Git history, PR refs, forks, or caches. Earlier editions contain household-derived history. | GitHub repository API: `private=false`, `visibility=public`; GitHub sensitive-data guidance. | Keep exact historical series out of the public site. Flag repository visibility/history remediation as urgent owner action. Do not claim rounding is anonymization. |
| A02 | High privacy | A multi-year rounded assessment/tax series can still identify a parcel. Some legacy pages publish such series. | Repo scan; BOE/county assessment context. | Do not republish exact or rounded historical series on the current site. Use only the rounded anchor inputs needed for scenarios, labeled owner-supplied/unverified. |
| A03 | High verification | Existing checker proves each table row contains an official-domain link, not that the linked source supports every cell. Several rows are assumptions, owner inputs, or model outputs. | `final/check.py`; source register. | Label provenance explicitly: verified rule, owner-supplied planning input, assumption, model output, or unverified blank. |
| A04 | High model | The model infers rent for the vacated third San Francisco unit as half of the two rented units' total rent. The brief does not supply that rent and says never infer. | `final/model.py`: `sf_unit3_rent = r10(sf_rent_2units / 2)`. | Leave actual third-unit rent blank/unverified. Baseline should not count new third-unit rent. Show any leasing upside only as a separate explicit scenario. |
| A05 | High model | Cupertino rent uses HUD four-bedroom SAFMR as if it were the property's market rent. Bedroom count and rentable condition are unknown. | HUD FY2026 SAFMR 95014; `final/model.py`. | Treat HUD as an official benchmark, not a verified property rent. Flag bedroom/condition and obtain a rent opinion. |
| A06 | Medium model | Assessment inflation uses national CPI in the model, while California Proposition 13 uses the California CPI factor published by BOE. Baseline is capped at 2%, but historical replays can differ. | RTC 51; BOE annual CCPI letters; `final/model.py`. | Use official California CCPI/BOE factors where verified; otherwise label national CPI as a proxy assumption. |
| A07 | Medium model | Black-swan equity/bond returns rely on an academic table, not an official source. The brief requires official sources for verified rows. | `final/data/hist_returns_damodaran.csv`; NYU Stern table. | Do not present those returns as officially verified. Use official inflation/housing/Treasury data plus explicitly hypothetical equity stress paths, or leave unverified. |
| A08 | Medium model | Insurance premiums are owner estimates, not official property-specific quotes. CDI survey/tool values are hypothetical comparisons, not quotes. | CDI premium comparison page and residential insurance reports. | Leave verified ZIP-level premium blank. Use the rounded owner estimate only as an unverified planning input and show sensitivity. |
| A09 | Medium tax | Estate-tax headroom subtracts only Property A from the projected exclusion. Actual gross estate, debts, deductions, prior taxable gifts, other assets, retirement accounts, and portability are unknown. | IRS Form 706 instructions and estate-tax FAQ. | Present headroom as a conditional illustration, not the amount that can be inherited tax-free. Leave actual estate tax blank. |
| A10 | Medium tax | Rental depreciation/recapture and passive-loss release are simplified; placed-in-service month, land/building split, prior depreciation, and passive activity status are unknown. | IRS Publication 527 and Topic 409. | Flag simplifications; obtain tax-adviser calculation before acting. |
| A11 | Medium law | Future Proposition 19 allowance, federal exclusion, tax rates, rent rules, insurance, utilities, and solar tariffs cannot be verified decades ahead. | BOE LTA 2025/009; IRS Rev. Proc. 2026-35; SF Rent Board; CPUC. | Current verified amounts are anchors only. Future values are scenarios/assumptions, not official forecasts. |
| A12 | Medium publication | Concurrent sessions repeatedly changed the Pages front door between numeric and no-figures editions. | Coordination board; PRs #55-#61. | Final integration must choose one stable, user-requested anonymized numeric dashboard, preserve other editions as non-public/source-only, and enforce an exact publication allowlist. |
| A13 | Low source | SFPUC's working rates index was found, but the linked FY2026-27 water/sewer PDF failed to parse during this audit. | Official rates index and bill-structure page read; PDF fetch failed. | Cite the working index/bill structure; leave adopted unit rates and household tariff unverified. Owner water range remains an unverified input. |
| A14 | Low source | Existing source register contains IRS closing-letter fee wording that may differ across IRS pages. | IRS estate FAQ vs What's New. | Not material to the decision; flag source wording and avoid relying on the fee. |

## What is structurally correct in the existing model

- Property B is already owned by the Inheritor. Inheriting Property A does not itself reassess Property B or reset Property B's income-tax basis.
- Property B is excluded from the Transferor's estate in the model.
- Proposition 19 partial exclusion formula is structurally correct for a qualifying 100% parent-child family-home transfer: new taxable value = factored base year value + max(0, market value - (factored base year value + adjusted allowance)).
- A trust transfer does not by itself guarantee income-tax basis step-up; estate inclusion is the key question.
- Federal estate tax is generally an estate-level tax, not a California/local inheritance tax. California has no estate-tax return requirement for deaths on/after 2005-01-01.

## Additional bounded checks (2026-11-12 16:10 UTC)

- Re-ran on rebased main `7b02eb8`: `final/check.py .` passed structurally (25 pages, 966 official-linked rows, 2,340 links, 2,340 dollar figures, 51 model paths), but the unrounded-owner scan was explicitly skipped without the external private-values file. `privacy-site/check.py` passed (11 pages, 309 context-linked rows); all 8 privacy-site tests passed.
- The three hand-typed figures in numeric Suggestions Part 1 match the current model after $10 rounding: S-09 estate room, S-12 live-vs-sell opportunity cost, S-15 worst ten-year sell-minus-rent gap. They are nevertheless drift-prone because they are literals rather than generated from `model.json`.
- The numeric generator footer and several numeric pages publish ZIP codes. The current Pages boundary excludes those pages; if any numeric page is ever published, remove ZIPs and household-locality cues first.
- PR #59 failure cause was recovered from check annotations despite log-download EOF: committed `verification.html`, `review.html`, and `requirements.html` differ from generator output. Posted the precise cause on the PR; did not edit its active branch.
- GitHub Pages API reports `built`, no error, at main `7b02eb8`; post-merge validation and pages-build-deployment runs succeeded. Current public edition remains the privacy-first guide, not the numeric root pages.

## Verification limits

No parcel lookup, address search, owner identity search, trust document, lease, insurance quote, appraisal, or private tax record was accessed. Household figures remain owner-supplied and unverified. Official links verify rules/benchmarks, not the household's actual facts. Future law and market outcomes are unknown.
