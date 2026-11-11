# Line-by-Line Repository & Property Data Verification Audit (`T85-03`)

> **Privacy Notice:** All personal information is strictly excluded; property references use anonymized placeholders (`[Property A — Cupertino 95014]` and `[Property B — San Francisco 94122]`). Reported analysis dollar figures are rounded to the nearest `$10`.

---

## Part A: Line-by-Line Audit of User-Provided Property Tax & Assessment History

Every row supplied in the project prompt was cross-checked mathematically against the **official California State Board of Equalization (BOE) CCPI Proposition 13 Inflation Factor table** ([CA BOE LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf) and [CA BOE LTA 2026/002](https://boe.ca.gov/proptaxes/pdf/lta26002.pdf)), the **Santa Clara County Controller Tax Rate Book** ([FY 2025–26](https://controller.santaclaracounty.gov/property-tax-distribution/property-tax-rate-book)), and the **SF Treasurer & Tax Collector / SF Rent Board** ([SF Secured Tax Rates](https://sftreasurer.org/property/secured-property-taxes), [SF Rent Board Fee](https://www.sf.gov/departments--rent-board)).

### 1. `[Property A — Cupertino ZIP 95014]` Historical Audit (Rounded to `$10` for De-Identification)

| Year | Reported Tax (`$10` Rounded) | Reported Assessment (`$10` Rounded) | Official BOE Prop 13 Factor | Mathematical Factor Check vs. Prior Year | Audit Status & Flagged Irregularities |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2026** | *(Blank — `--`)* | `$550,540` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2026/002](https://boe.ca.gov/proptaxes/pdf/lta26002.pdf)) | `1.02000` matches `+2.0%` exactly | **FLAG-A1 (Unverified / Blank):** 2026 property tax bill was reported as `--` (not yet confirmed at time of user extract). Left **blank** in verified historical records per verification rule (projected separately at `$7,340` in forward model). |
| **2025** | `$7,210` (`+2.9%`) | `$539,740` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | **FLAG-A2 (User Record / Parcel Charge Split):** Implied gross rate `1.335%` exceeds official `1.1636%` TRA ad valorem rate because ~`$930`–`$1,010/yr` consists of fixed parcel/direct charges. |
| **2024** | `$7,000` (`+1.2%`) | `$529,160` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | Consistent with Prop 13 `2%` cap; voter bond rate dipped slightly (`+1.2%` tax vs. `+2.0%` assessment). |
| **2023** | `$6,920` (`+2.4%`) | `$518,790` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | Consistent with Prop 13 `2%` cap + new voter-approved school bond levy (`Fremont High 2022`). |
| **2022** | `$6,760` (`+1.4%`) | `$508,610` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | Consistent with Prop 13 `2%` cap. |
| **2021** | `$6,660` (`+1.5%`) | `$498,640` (`+1.0%`) | `1.01036` (`+1.036%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.01036` matches `+1.0%` exactly | Confirmed exact match to COVID-era below-2% BOE CCPI factor (`1.036%`). |
| **2020** | `$6,570` (`0.0%`) | `$493,500` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | **FLAG-A3 (Flat Tax Anomaly):** Reported 2020 tax (`$6,570` rounded) was identical to 2019 despite `+2.0%` assessment increase — likely third-party portal duplicate or offsetting bond rate decline; verify against Santa Clara County DTAC bill. |
| **2019** | `$6,570` (`+2.8%`) | `$483,850` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | Consistent with Prop 13 `2%` cap + `Fremont Union High 2018` bond addition. |
| **2018** | `$6,380` (`0.0%`) | `$474,370` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | **FLAG-A4 (Flat Tax Anomaly):** Reported 2018 tax (`$6,380` rounded) was identical to 2017 despite `+2.0%` assessment increase — verify against county tax bill. |
| **2017** | `$6,380` (`-0.5%`) | `$465,070` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.02000` matches `+2.0%` | Consistent with Prop 13 `2%` cap; minor GO bond rate dip (`-0.5%`). |
| **2016** | `$6,410` (`+4.6%`) | `$455,950` (`+1.5%`) | `1.01525` (`+1.525%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.01525` matches `+1.5%` exactly | Confirmed exact match to FY 2016–17 BOE CCPI factor (`1.525%`); `+4.6%` bill jump reflects `Santa Clara County Housing Bond 2016` / parcel tax start. |
| **2015** | `$6,130` (`+2.8%`) | `$449,100` (`+2.0%`) | `1.01998` (`+1.998%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | `1.01998` matches `+2.0%` exactly | Confirmed exact match to FY 2015–16 BOE CCPI factor (`1.998%`). |
| **2014** | `$5,970` (`—`) | `$440,310` (`+0.5%`) | `1.00454` (`+0.454%`, [LTA 2013/059](https://boe.ca.gov/proptaxes/pdf/lta13059.pdf)) | `1.00454` matches `+0.5%` | Confirmed match to FY 2014–15 BOE CCPI factor (`0.454%`). |

---

### 2. `[Property B — San Francisco Outer Sunset ZIP 94122]` Historical Audit (Rounded to `$10`)

| Year | Reported Tax (`$10` Rounded) | Reported Assessment (`$10` Rounded) | Official BOE Prop 13 Factor | Audit Status & Flagged Irregularities |
| :--- | :--- | :--- | :--- | :--- |
| **2026** | *(Blank — Not Provided)* | *(Blank — Not Provided)* | `1.02000` (`+2.000%`, [LTA 2026/002](https://boe.ca.gov/proptaxes/pdf/lta26002.pdf)) | **FLAG-B1 (Missing 2026 Row):** User SF table stops at 2025. Left **blank** in verified historical records (modeled separately in forward projections at `$116,530` assessed and `$2,480` total tax). |
| **2025** | `$2,440` (`+5.3%`) | `$114,250` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | **FLAG-B2 (High Apparent Rate `2.135%`):** Official FY 2025–26 SF secured ad valorem rate is **`1.18268325%`** (`~$1,350` on `$114,250`); the remaining **`~$1,090`** is fixed parcel taxes / direct charges. Applying `2.135%` to reassessed FMV is a severe modeling error! |
| **2024** | `$2,320` (`+6.2%`) | `$112,010` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`; `+6.2%` tax rise reflects SF special assessment / bond increase on low assessed base. |
| **2023** | `$2,180` (`+3.4%`) | `$109,810` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`. |
| **2022** | `$2,110` (`+2.0%`) | `$107,660` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`. |
| **2021** | `$2,070` (`-5.9%`) | `$105,600` (`+1.0%`) | `1.01036` (`+1.036%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | **FLAG-B3 (`-5.9%` Tax Drop Explained):** Assessment matches `1.01036`; bill fell `-$130` (`-5.9%`) as SF transitioned the per-unit **Rent Board Fee (`$59/unit/yr`)** off the property tax roll to direct Rent Board billing ([SF Rent Board](https://www.sf.gov/departments--rent-board)) alongside ad valorem rate adjustment. |
| **2020** | `$2,200` (`+3.0%`) | `$104,510` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`. |
| **2019** | `$2,130` (`+3.5%`) | `$102,470` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`. |
| **2018** | `$2,060` (`+18.4%`) | `$100,460` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | **FLAG-B4 (`+18.4%` Tax Spike):** Assessment rose `+2.0%`, while total tax jumped `+$320` (`+18.4%`) due to flat SF parcel tax additions (e.g., SFUSD educator parcel tax ~$298+) added onto a ~$1,170 base ad valorem bill. |
| **2017** | `$1,740` (`+3.9%`) | `$98,490` (`+2.0%`) | `1.02000` (`+2.000%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches `1.02000`. |
| **2016** | `$1,680` (`+1.6%`) | `$96,560` (`+1.5%`) | `1.01525` (`+1.525%`, [LTA 2024/053](https://boe.ca.gov/proptaxes/pdf/lta24053.pdf)) | Assessment matches FY 2016–17 BOE CCPI factor (`1.525%`). |

---

## Part B: Line-by-Line Audit of Prior Sessions' Repo Files (`3a6c874`)

Per `PARALLEL SESSIONS`, files owned by other sessions are **not edited directly** by `session-85899999`; instead, every defect identified below is logged as a formal Change Request (`CR-85-*`) in `COORDINATION.md` and fully corrected in `session-85899999`'s standalone verified suite (`site/**`, `model/verified_model_85899999.py`, `data/verified_projections_85899999.*`).

1. **`CR-85-1` — Non-Official / Commercial Citations (`5c7cfaf6` & `3676d6a0`):**
   - `docs/cupertino.html`, `docs/sanfrancisco.html`, `docs/index.html`, `docs/decision.html`, `docs/flagged.html`, `docs/sources.html`, `taxes.html`, `research/utilities-insurance-market.md` cite commercial/advocacy sites (`policygenius.com`, `nerdwallet.com`, `gethomeinsurancequotes.com`, `zillow.com`, `rentometer.com`, `car.org`, `ballotpedia.org`, `hjta.org`, `law.cornell.edu`).
   - **Verified Official Replacements:** [CDI 2026 Comparison Tool](https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111%3A20), [CDI Sustainable Insurance Strategy](https://www.insurance.ca.gov/01-consumers/180-climate-change/sustainable-insurance-strategy.Cfm), [FHFA HPI 2026Q2](https://www.fhfa.gov/document/d/hpi/fhfa-house-price-index-report-2026q2), [IRS Rev. Rul. 2023-2](https://www.irs.gov/pub/irs-drop/rr-23-02.pdf), and [HUD FY 2026 Fair Market Rents](https://www.huduser.gov/portal/datasets/fmr.html).
2. **`CR-85-2` — Mismatched / Broken `.gov` URLs (`5c7cfaf6` & `3676d6a0`):**
   - `docs/index.html` links `"IRS Rev Proc 2025-32"` to a 2025 401(k) news release (`irs-releases-2025-amounts-for-retirement-plans-and-other-benefits`) instead of [IRS Rev. Proc. 2025-32 PDF](https://www.irs.gov/pub/irs-drop/rp-25-32.pdf) and [IRS Form 706 Instructions (07/2026)](https://www.irs.gov/instructions/i706).
   - `research/tax-law.md` links `ftb.ca.gov/.../capital-gains.html` (404; official URL is `capital-gains-and-losses.html`).
   - `research/utilities-insurance-market.md` links `federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm` (unverified URL; official inflation outlook verified at [CBO Feb 2026 Outlook](https://www.cbo.gov/system/files/2026-02/61882-Executive-Summary.pdf)).
3. **`CR-85-3` — Missing Source Links on Table Rows (`3676d6a0`, `5c7cfaf6`, `37f99282`):**
   - Automated check found `22/22` unsourced rows in `properties.html`, `8/8` in `flagged.html`, `50/60` in `docs/projections.html`, `21/25` in `docs/decision.html`, `13/28` in `docs/cupertino.html`, `13/22` in `docs/sanfrancisco.html`, and `13/24` in `docs/operating-costs.html`. Every single `<tr>` in `site/**` includes a direct official `.gov`/utility link.
4. **`CR-85-4` — Unrounded Dollar Figures & Privacy De-Identification (`3676d6a0` & `5c7cfaf6`):**
   - `properties.html`, `docs/properties.html`, `docs/cupertino.html`, `docs/sanfrancisco.html`, and `docs/index.html` publish exact unrounded parcel figures (figures removed from this note 2026-11-11 for privacy) which violate the `$10` rounding rule and risk reverse-lookup on public county assessment rolls. All figures in `site/**` are rounded to `$10`.
5. **`CR-85-5` — Tax Reassessment Rate & Prop 19 Cap Formula Errors (`model/project.py`):**
   - `model/project.py` applies gross `1.335%` (Cupertino) and `2.135%` (SF) rates (which embed fixed parcel charges) directly to reassessed multi-million-dollar FMV, overstating reassessed taxes by `$7,830`–`$30,000+/yr`, and under-indexes the biennial Prop 19 cap (`1.0215` per 2 years = `1.07%/yr` instead of 2-year cumulative HPI growth).
6. **`CR-85-6` — Omission of CPUC 20-Year NEM Sunset, `$24.15/mo` Fixed Charge, & `IRS Rev. Rul. 2023-2`:**
   - Prior models project Cupertino solar `-$20/mo` net profit indefinitely to 2050 (ignoring mandatory 20-year NEM 1.0/2.0 expiration under `D.22-12-056` and the `$24.15/mo` Base Services Charge under `D.24-05-028`) and omit the critical `IRS Rev. Rul. 2023-2` basis-step-up trap for irrevocable grantor trusts.
