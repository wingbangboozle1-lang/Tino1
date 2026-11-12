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
| A05 | High model | Cupertino rent uses HUD four-bedroom SAFMR as if it were the property's market rent. Bedroom count and rentable condition are unknown. | HUD FY2026 SAFMR [ZIP-A]; `final/model.py`. | Treat HUD as an official benchmark, not a verified property rent. Flag bedroom/condition and obtain a rent opinion. |
| A06 | Medium model | Assessment inflation uses national CPI in the model, while California Proposition 13 uses the California CPI factor published by BOE. Baseline is capped at 2%, but historical replays can differ. | RTC 51; BOE annual CCPI letters; `final/model.py`. | Use official California CCPI/BOE factors where verified; otherwise label national CPI as a proxy assumption. |
| A07 | Medium model | Black-swan equity/bond returns rely on an academic table, not an official source. The brief requires official sources for verified rows. | `final/data/hist_returns_damodaran.csv`; NYU Stern table. | Do not present those returns as officially verified. Use official inflation/housing/Treasury data plus explicitly hypothetical equity stress paths, or leave unverified. |
| A08 | Medium model | Insurance premiums are owner estimates, not official property-specific quotes. CDI survey/tool values are hypothetical comparisons, not quotes. | CDI premium comparison page and residential insurance reports. | Leave verified ZIP-level premium blank. Use the rounded owner estimate only as an unverified planning input and show sensitivity. |
| A09 | Medium tax | Estate-tax headroom subtracts only Property A from the projected exclusion. Actual gross estate, debts, deductions, prior taxable gifts, other assets, retirement accounts, and portability are unknown. | IRS Form 706 instructions and estate-tax FAQ. | Present headroom as a conditional illustration, not the amount that can be inherited tax-free. Leave actual estate tax blank. |
| A10 | Medium tax | Rental depreciation/recapture and passive-loss release are simplified; placed-in-service month, land/building split, prior depreciation, and passive activity status are unknown. | IRS Publication 527 and Topic 409. | Flag simplifications; obtain tax-adviser calculation before acting. |
| A11 | Medium law | Future Proposition 19 allowance, federal exclusion, tax rates, rent rules, insurance, utilities, and solar tariffs cannot be verified decades ahead. | BOE LTA 2025/009; IRS Rev. Proc. 2026-35; SF Rent Board; CPUC. | Current verified amounts are anchors only. Future values are scenarios/assumptions, not official forecasts. |
| A12 | Medium publication | Concurrent sessions repeatedly changed the Pages front door between numeric and no-figures editions. | Coordination board; PRs #55-#61. | Final integration must choose one stable, user-requested anonymized numeric dashboard, preserve other editions as non-public/source-only, and enforce an exact publication allowlist. |
| A13 | Low source / missing input | SFPUC's FY2026-27/FY2027-28 water/sewer PDF was successfully read after an initial transient fetch failure. Adopted unit rates are known; the household's meter size, usage, account class, parcel area and bill are not. | `SOURCES.md` V31–V31c; official bill-structure page. | Cite the adopted schedules, not the failed fetch. Leave the household tariff/bill unverified; owner water range remains an unverified planning input. |
| A14 | Low source | Existing source register contains IRS closing-letter fee wording that may differ across IRS pages. | IRS estate FAQ vs What's New. | Not material to the decision; flag source wording and avoid relying on the fee. |
| A15 | Medium model | The model uses one blended near-term SFPUC escalation (`sf_water_near = 0.09`) while the adopted schedule changes water, wastewater and stormwater components by different amounts. | `final/model.py`; V31/V31b/V31c. | Label 9% as a planning assumption, not an adopted combined household increase. Replace only after meter/usage/parcel/account facts are known; do not infer a bill from unit rates alone. |
| A16 | Low applicability | San José storm/connection charges and Valley Water wholesale increases are official local context, but Property A's retailer, service area and whether a charge is already on the tax bill are unknown. | V35–V37. | Do not add these charges to the household model without private bill/service confirmation; avoid double counting tax-roll charges. |

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

## Additional bounded checks (2026-11-12 16:25 UTC)

- Rebased base is main `536ee03` (PR #62). Local checks on this tree: `final/check.py .` OK (25 pages, 912 official-linked rows, 2,362 links, 2,358 dollar figures, 51 model paths; unrounded-owner scan skipped without the external private-values file); `privacy-site/build.py` reproducible with clean `git diff -- privacy-site/public`; `privacy-site/check.py` PASS (11 pages, 316 context-linked rows); 8/8 privacy-site tests; `final/publish.py --check` OK (26 numeric files excluded).
- Corrected the SFPUC fetch claim: the adopted PDF was read in full (V31–V31c). Added primary IRS Rev. Proc. 2026-35 §3.44/§3.46, San José storm/connection context, Valley Water wholesale context and CBO 2026–2036 outlook (V01, V35–V38). No household tariff, retailer or parcel charge is inferred.
- In-memory sensitivity reruns without writing `final/out/model.json`: removing the inferred third-unit rent, using the HUD 3BR benchmark, raising the rent benchmark 30%, tripling insurance, doubling maintenance, raising vacancy/management, lowering stock returns to 5%, using 60/40, removing basis step-up, and moving transfer to 2040/2050 all leave terminal wealth ranked sell > rent > live. T-bill-only proceeds rank rent > live > sell. With the inferred third-unit rent removed, the 50 historical-sequence replays still end with sell first in 50/50; sell leads 43/50 at ten years and 50/50 at twenty years. The Depression and Japan overlays still favor rent at the terminal horizon. These are assumption-dependent model results, not verified forecasts; see `FINDINGS.md` and `recheck.py`.
- `_config.yml` had no exclusion for `session-5ea93a0e/`; Jekyll would convert these Markdown files into public HTML and break the exact 13-file publication allowlist. Added one hand-written exclude entry, preserving R29 (`final/publish.py` does not rewrite `_config.yml`). Ruby/Jekyll are absent locally, so the real Jekyll boundary check must run in CI.
- PR #69 proposes dual-edition publication and a 38-file union allowlist while conflicting and without checks; PR #59 remains conflicting with a byte-identity failure. Comments were posted requesting preservation of the privacy-first boundary and correction of inferred rent/provenance before any numeric publication. Neither branch was edited or merged.

## Verification limits

No parcel lookup, address search, owner identity search, trust document, lease, insurance quote, appraisal, or private tax record was accessed. Household figures remain owner-supplied and unverified. Official links verify rules/benchmarks, not the household's actual facts. Future law and market outcomes are unknown.
