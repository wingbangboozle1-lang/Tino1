# FDD bounded publication, privacy and decision-readiness audit

**Date:** 2026-11-13 UTC  
**Branch:** `arena/fdd454a6-tino1`  
**Scope:** the actual GitHub Pages boundary, the isolated public guide, the official-source registry used by that guide, and the integration checks. This is not a complete re-verification of every historical edition or every file in the public repository.

## Finding that required the integration change

The Pages API reported that Pages is public and built from `main:/`. In the starting tree, `final/published.txt` declared 39 published files, including the numeric summary, projections, decision, costs, law and other household-model pages. `privacy-site/check_published.py` described the same union allowlist. The README elsewhere said only the no-figures edition was published, and the initial `_config.yml` did not exclude the numeric root pages. Thus the stated privacy boundary did not match the configured allowlist; passing the old allowlist check did not establish a privacy-first publication.

Jekyll/Ruby is not installed in this workspace. I did not claim to have run a local Jekyll build or to have opened the live numeric URLs. The PR workflow is the required real Jekyll check. The local synthetic output check below is only a fixture check, not a substitute for CI or a post-deploy check.

## Integration result in this working tree

- Replaced the union allowlist with an exact 13-file privacy-first set: a generic root landing and the 12 reviewed files under `privacy-site/public/`.
- Regenerated `_config.yml` so the household-specific numeric pages, other root files, audit directories and non-public `privacy-site` sources are excluded. Added an independent exact-set assertion to `privacy-site/check_published.py` so expanding the manifest to include numeric pages fails closed.
- Changed the root landing and `final/build.py` ROOT_MODE landing so a future model rebuild cannot add a link to the numeric edition on Pages. The root page points only to the generic guide and clearly states that the repository itself remains a separate exposure surface.
- Updated the README to accurately describe the published edition and to warn that the repository and Git history are public; a Pages exclusion is not privacy for tracked files.
- Corrected the water/wastewater row: its previous CPUC net-metering link was not a water-rate source. It now links to the California Water Boards service-area lookup page, says explicitly that this only helps identify a drinking-water system, and leaves actual water, wastewater, stormwater and utility prices unverified.
- Removed an overbroad statement that a PG&E implementation resolution proves a universal electricity charge or rollout date. The source description now says it is PG&E-specific and not a property quote. The SALT row separates personal itemized-deduction limits from rental-expense treatment and links to both relevant IRS context pages.
- Added browser-only Adopt / Hold / Reject radios for each suggestion and an implementation-path selector. There is no form or site code to store, submit or transmit choices. “Keep the public guide generic” is the safe default; the controls do not implement a change.
- Added source-host and radio-control checks. All table rows in the public guide are linked to the reviewed official-context registry; captions distinguish official rules from synthetic assumptions.

## Local checks run

- `python3 privacy-site/build.py` — rebuilt 11 public guide pages; builder reports it reads no private inputs.
- `python3 privacy-site/check.py` — PASS, 318 official-context-linked table rows; it checks local links, direct source allowlist, known household-value/locality signatures, `$10` display rounding, CSP/no remote assets, and only local radio controls on Suggestions. This is a bounded site check, not a scan of Git history.
- `python3 -m unittest discover -s privacy-site -p 'test_*.py' -v` — PASS, 8 tests.
- `python3 final/publish.py --check` — PASS, 13-file privacy-first allowlist and matching Jekyll exclusions.
- `python3 final/check.py .` — PASS, 25 internal pages / 925 table rows / 2,410 links / 2,368 displayed dollar figures rounded to $10; 51 model paths passed internal model tests. The external unrounded-owner-value scan was **skipped** because no private value file was supplied. This check does not certify the numeric edition as private or as a verified household forecast.
- A temporary local fixture copied only the 13 allowlisted source files into a scratch directory. `final/check_published.py` and `privacy-site/check_published.py` both passed: exact set, byte identity, root-landing freshness and internal links. This is **not** the real Jekyll build; CI must confirm the actual `_site` output.

## Official source passages re-read on 2026-11-13

These are direct primary-source links. Their facts are general law or context, not proof of any household document, bill, title, price, forecast or eligibility.

- IRS, 2026 estate-tax filing threshold and estate scope: <https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax>
- IRS, published 2027 inflation adjustments: <https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts>
- California BOE, Proposition 19 requirements: <https://www.boe.ca.gov/prop19/>
- California BOE, Publication 800-1: <https://www.boe.ca.gov/pdf/pub800-1.pdf>
- California Revenue and Taxation Code §51: <https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC>
- IRS, inherited-property basis FAQ: <https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances>
- IRS, Revenue Ruling 2023-2: <https://www.irs.gov/irb/2023-16_IRB#REV-RUL-2023-2>
- California State Controller, California estate tax: <https://www.sco.ca.gov/ardtax_estate_tax.html>
- IRS Topic 701, home-sale exclusion: <https://www.irs.gov/taxtopics/tc701>
- IRS Topic 414, rental income and expenses: <https://www.irs.gov/taxtopics/tc414>
- California DOI Residential Insurance Guide (Form 401): <https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/res-ins-guide.cfm>
- CPUC customer-sited generation and NEM / net billing context: <https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/net-energy-metering>
- CPUC Resolution E-5354, PG&E implementation context: <https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M555/K816/555816677.pdf>
- California Legislature, SB 974 (chaptered, not a pending blanket Prop 19 repeal): <https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260SB974>
- SEC Investor.gov, allocation and risk context: <https://www.investor.gov/introduction-investing/getting-started/asset-allocation>
- California Water Boards, water-system lookup resource: <https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/shutoff-protection.html>

Other registry sources retain their earlier 2026-11-12 per-source checked dates; the public page says so. They were not all re-read in this pass.

## Open / owner-only items

1. **Public repository and history exposure remains unresolved.** The current tracked numeric analysis, earlier editions and history remain accessible through the public repository even though they are excluded from new Pages output. The prior Pages edition may have been cached or copied. This work does not make the repository private, rewrite history, or promise erasure from forks/caches. GitHub guidance: <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>.
2. Property-specific insurance, water/electric bills, lawful rents, tax assessments, direct charges, repairs, debt, title, trust terms, tax basis, estate inventory, gifts and portability remain unverified; the public guide leaves their amounts blank.
3. Local fee and rental-law application, future law, long-run appreciation/inflation and future investment returns are not confirmed. The black-swan illustrations are labeled synthetic and historical episodes are context, not assigned probabilities.
4. No personal “best path” is certified. The public recommendation is conditional; a secure private analysis requires verified inputs and qualified professional review.
5. Pages deployment status and actual Jekyll output remain pending until the PR checks and post-merge Pages build complete.
