# Line-by-Line Repository Review & Irregularity Report (`arena/459d7aa2-tino1`)

**Reviewed baseline:** `main` (`759ced9` through `d7fcdcc`, 2026-11-11 UTC).  
**Method:** Every external URL in `final/sources.py` (54 entries) and `privacy-site/build.py` (19 entries) was fetched directly via HTTP (`fetch_page`), and `final/model.py`, `final/build.py`, `final/flags.py`, `final/check.py`, `privacy-site/*`, `legacy95/*`, `REPO-REVIEW.md`, and `model/*` were audited line by line against primary official `.gov` / statutory sources.

---

## 1. Critical Factual & Link Defects Discovered in `final/` (Previously Marked Verified)

`final/check.py` validates only whether an external link's *hostname* is in its `OFFICIAL` allowlist — it never fetches URLs or verifies bill numbers. Our direct HTTP fetch of all 54 entries in `final/sources.py` uncovered **2 misattributed/hallucinated California legislative bills**, **8 dead HTTP 404 URLs** (all marked `how='page'`), **1 stale local tax rate**, and **4 internal `final/build.py` contradictions**:

### 1.1 Two Misattributed / Hallucinated California Bills (`final/sources.py`, `final/build.py` -> `law.html`)

| Source ID | Claim in `final/sources.py` & `law.html` | Actual Official Text on `leginfo.legislature.ca.gov` | Required Remediation (`CR-45-1`) |
| :--- | :--- | :--- | :--- |
| `CA-ACA11` (`final/sources.py:62`, `final/build.py:617`) | Claims `202520260ACA11` is a *"Proposed constitutional amendment in the 2025-26 session on property taxation; requires two-thirds of each house and a statewide vote; not enacted."* | [ACA-11 (2025–2026, Macedo)](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260ACA11) is the **California Water Resiliency Act**, proposing Article X § 8 to transfer 1% of General Fund revenues to water conveyance infrastructure. It has **nothing** to do with property taxation or Prop 19 (Prop 19 was `201920200ACA11` in 2020). | Remove `202520260ACA11` as a property-tax bill; cite `201920200ACA11` for Prop 19's enactment history and [CA Const. Art. XIII A § 2.1](https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=CONS&article=XIII%20A) for constitutional amendment requirements. |
| `CA-SB472` (`final/sources.py:64`, `final/build.py:618`) | Claims `202520260SB472` is an *"Introduced bill on intergenerational property-tax rules; cannot override Article XIII A §2.1 without a ballot measure."* | [SB-472 (2025–2026, Stern, Ch. 761)](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260SB472) is **Pupil instruction: Holocaust and genocide education** (adding Education Code § 51221.2, enacted Oct. 13, 2025). It has **zero** connection to property taxation. Meanwhile, the **actual** 2025–2026 bill amending `R&TC § 63.2` is **[SB-974 (Seyarto, Ch. 665, approved Sept. 27, 2026)](https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260SB974)**, which added court-established special needs trusts as an eligible transfer medium under Prop 19. | Replace `CA-SB472` with `CA-SB974` (`202520260SB974`) in `final/sources.py` and `final/build.py` (`law.html`). |

### 1.2 Eight Dead HTTP 404 URLs in `final/sources.py` (All Falsely Marked `how='page'`)

| Source ID (`final/sources.py`) | Dead URL Returning HTTP 404 | Verified Live Official Replacement URL (Fetched 2026-11-11) |
| :--- | :--- | :--- |
| `BOE-P19` (line 45) | `https://www.boe.ca.gov/proptaxes/prop19.htm` (`404 – File or Page Not Found`) | https://www.boe.ca.gov/prop19/ |
| `SCC-P19` (line 75) | `https://www.sccassessor.org/property-information/homeowners/proposition-19` (`Page Not Found`) | https://asr.santaclaracounty.gov/proposition-19-overview |
| `SFT-RPTT` (line 79) | `https://sftreasurer.org/business/taxes-fees/real-property-transfer-tax-rptt` (`Page Not Found`) | https://www.sf.gov/transfer-tax |
| `SF-RENT-LAW` (line 80) | `https://www.sf.gov/reports--march-2026--learn-about-san-francisco-rental-laws` (`We can't find that page`) | https://www.sf.gov/learn-about-san-francisco-rental-laws |
| `SF-RENT-RATE` (line 81) | `https://www.sf.gov/information--annual-rent-increase` (`We can't find that page`) | https://www.sf.gov/learn-about-rent-increases-san-francisco/ (and https://www.sf.gov/news--annual-rent-increase-3126-22827-announced) |
| `CDI-RPI` (line 84) | `https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/residential-property-insurance.cfm` (`Document Not Found`) | https://www.insurance.ca.gov/01-consumers/200-wrr/DataAnalysisOnWildfiresAndInsurance.cfm |
| `CDI-SB824` (line 86) | `https://www.insurance.ca.gov/01-consumers/200-wrr/sb824.cfm` (`Document Not Found`) | https://www.insurance.ca.gov/01-consumers/140-catastrophes/MandatoryOneYearMoratoriumNonRenewals.cfm |
| `CDI-TOOL` (line 87) | `https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:110` (`Application "111" Page "110" not found`) | https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20 (`2026 Homeowners Insurance Comparison Tool`) |

### 1.3 Stale FY 2025–26 San Francisco Tax Rate & Internal `final/` Mismatches

1. **`SFT-RATE` (`final/sources.py:78`, `final/model.py:42`)**: Uses FY 2025–26 rate `1.18259092%`, whereas the live [SF Treasurer Secured Property Taxes page](https://sftreasurer.org/property/secured-property-taxes) publishes the **FY 2026–27 rate = `1.18162182%`**.
2. **`requirements.html` row 13 (`final/build.py:905`)**: States *"Walks through fourteen steps in order"*, whereas `process.html` (`final/build.py:553–570`) actually contains **sixteen steps** (`1`–`16`).
3. **`requirements.html` row 8 (`final/build.py:900`)**: Claims *"no official source publishes them"* / *"no official ZIP-level premium exists"*, contradicting `costs.html` and CDI's published [2026 Comparison Tool](https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20) and [ZIP-level policy/FAIR Plan datasets](https://www.insurance.ca.gov/01-consumers/200-wrr/DataAnalysisOnWildfiresAndInsurance.cfm) (the accurate reason for leaving static ZIP quotes blank is that CDI's interactive tool requires per-risk session parameters and omits 15%–300%+ wildfire surcharges, and CDI publishes no static 3-unit landlord rate table).
4. **`requirements.html` row 10 (`final/build.py:902`)**: Links `flag('A03')` (Prop 19 allowance growth) instead of `flag('A01')` (general CPI inflation) for future federal estate-tax exclusion indexation.
5. **Missing Cupertino (`95014`) water-provider source (`final/sources.py` / `costs.html`)**: `costs.html` links SFPUC for SF water and PG&E/CPUC for electricity, leaving Cupertino water without a local official water-provider citation; [City of Cupertino — Water Utilities](https://www.cupertino.gov/Residents/Utilities/Water) confirms Cupertino is split across San Jose Water Company, California Water Service, and the City-owned water system operated by SJWC under lease extended to 2036.
6. **Stale `REVIEW` items in `final/flags.py`**: `R05`, `R06`, and `R09` still describe superseded-edition unsourced rows that were remediated in PR #30 (`L95`, verified by `python3 legacy95/check_legacy.py`), and `R15` lists an outdated open-PR set.

---

## 2. Audit of `privacy-site/` (Merged in PRs #34 & #36 by `cab26ebb`)

1. **External links (`privacy-site/build.py:5–25`)**: All 19 external URLs in `privacy-site/build.py` were verified against `.gov`/FED hosts (`SB 974` is genuinely enacted Chapter 665 of 2026; `cpuc` points to the general Customer Generation landing page `.../demand-side-management/net-energy-metering`, which is HTTP 200 though the 20-year NEM legacy period text resides one click deeper on `.../customer-generation/net-energy-metering-and-net-billing`).
2. **Deliverable completeness gap vs. user brief (`CR-45-3`)**: `privacy-site/public/projection.html` renders `'—'` in every single Market Value, Assessed Value, Property Tax, and Operating Cost cell across all 51 rows (`2026–2076`), `costs.html` renders `'—'` in all figure cells, and `decision.html` withholds a quantitative recommendation. While `cab26ebb` documented this as an intentional privacy withholding, the user's explicit prompt instructs: *"Costs and numbers should be used but rounded to the nearest $10 increments ... and should be reported in any decision analysis to provide clarity. I want clear numbers and projections for the reasoning behind decisions."* Our suite in `_session_459d7aa2/` provides the full `$10`-rounded (and `$100`-coarsened on zero-ending county-roll inputs) projections, Black Swan paths, and decision numbers while logging `CR-45-3` for `8fc06844`'s active `K3` front-door reconciliation claim.

---

## 3. Audit of Privacy & Residual Exposures Across Legacy / Working Tree Paths

1. **PR #37 (`8fc06844`, commit `d156f7c`) verified effective on `main`**: Removed the reversible 64-entry SHA-256 hash file `final/data/privacy_fingerprints.txt`, redacted the regex list in `REPO-REVIEW.md` §6, and rounded 7 underscore-separated literals in `model/project.py` and `model/verified_model_85899999.py`.
2. **Remaining active sibling scopes (not edited by this session per non-overlap rule)**:
   - Superseded year-by-year historical tax roll tables (`2014–2026` / `2016–2025` sequence quasi-identifiers) and the two zero-ending county-roll base inputs: actively claimed by `8f259271` (`R8-1..R8-4`). In `_session_459d7aa2/`, we omit multi-year parcel history tables altogether and coarsen zero-ending county-roll base inputs to `$100` (`$550,500`, `$7,200`) so zero county-roll parcel identifiers appear in our code, CSVs, JSON, or HTML.
   - Residual unrounded comment tokens in `model/verified_model_85899999.py:46` and `model/assumptions.md:33`: actively claimed by `d3c614ec` (`D3-1`).
   - **Public Git history & PR refs (Owner Action Required)**: Historical commits and PR refs on public GitHub still contain earlier unredacted files; only the repository owner can switch repository visibility to Private or purge Git history/PR refs.
