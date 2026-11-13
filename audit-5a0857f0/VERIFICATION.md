# Independent official-source re-read — 2026-11-13 (session `arena/5a0857f0`)

Method: each URL below is the exact address recorded in `final/sources.py` (or the
official page that supersedes it). Every page was fetched directly in this session on
2026-11-13 UTC and the quoted wording/values were compared with what the register and
the site state. Anything that could not be confirmed is left blank and flagged. No
value entered the site without a direct read recorded here.

## Result table

| # | Register id | Official URL | What the page says (quoted / read) | vs register & site | Result |
|---|---|---|---|---|---|
| 1 | IRS-ESTATE | https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax | Filing-threshold table: "2026 — $15,000,000"; portability election needs a timely filed Form 706 | match | PASS |
| 2 | RP-2026-35 | https://www.irs.gov/pub/irs-drop/rp-26-35.pdf | §3.44: "For calendar year 2027, the basic exclusion amount under § 2010(c)(3) is $15,480,000." §3.46: 2027 annual gift exclusion $20,000 | match | PASS |
| 3 | BOE-LTA-2026-002 | https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf | "please prepare your 2026 assessment roll using an inflation factor of 1.02"; CCPI 343.108 (Aug 2024) → 354.456 (Aug 2025) = 3.307%, capped at 2% (R&TC 51, art. XIII A §2(b)); full 1976-77→2026-27 factor table enclosed | match | PASS |
| 4 | BOE-LTA-2025-009 | https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf | "$1 million amount is adjusted to $1,044,586" for transfers 2025-02-16 through 2027-02-15; FHFA California HPI 2024 change 2.15%; next adjustment February 2027; table: 2021-23 $1,000,000 / 2023-25 $1,022,600 / 2025-27 $1,044,586 | match | PASS |
| 5 | RTC-51 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51 | 51(a)(1)(C): inflation factor = October-to-October CCPI change; 51(a)(1)(D): "In no event shall the percentage increase ... exceed 2 percent of the prior year's value" | match | PASS |
| 6 | SF-TAX | https://sftreasurer.org/property/secured-property-taxes | "The secured property tax rate for Fiscal Year 2026-27 is 1.18162182%."; supplemental assessment follows a change in ownership | match | PASS |
| 7 | RR-2023-2 | https://www.irs.gov/irb/2023-16_IRB | Rev. Rul. 2023-2: "the basis adjustment under section 1014 generally does not apply to the assets of an irrevocable grantor trust not included in the deceased grantor's gross estate for Federal estate tax purposes" | match | PASS |
| 8 | SFPUC-RFB | https://www.sfpuc.gov/sites/default/files/agendas-minutes-rate-fairness-board/6a-Rates-Presentation.pdf | Rate Fairness Board 2026-03-19: Water flat +7.0% FY2026-27 and FY2027-28; residential wastewater +10.8% / +10.1%; stormwater +53.3% / +43.1%; average residential combined bill +10.5% (FYE2027) / +12.5% (FYE2028) | match (basis of assumption A12) | PASS |
| 9 | HUD-94122 | https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=94122&metro_code=METRO41860MM7360&year=2026 | FY2026 SAFMR 94122: efficiency $2,280; one-bedroom $2,730; two-bedroom $3,310; three-bedroom $4,230; four-bedroom $4,380 | match (re-confirmed on 2026-11-13) | PASS |
| 10 | HUD-27-95014 (new) | https://www.huduser.gov/datasets/fmr/fmr2027/zip-calc?year=2027&zip=95014&cbsasub=METRO41940M41940 | FY2027 SAFMR 95014: efficiency $3,040; one-bedroom $3,440; two-bedroom $4,050; three-bedroom $5,440; four-bedroom $5,800. The FY2026 row printed on the same page ($3,340 / $3,800 / $4,440 / $5,870 / $6,390) matches the register exactly | new reading; closes flag U09 for this ZIP | PASS (added) |
| 11 | HUD-27-94122 (new) | https://www.huduser.gov/datasets/fmr/fmr2027/zip-calc?year=2027&zip=94122&cbsasub=METRO41860M41884 | FY2027 SAFMR 94122: efficiency $2,370; one-bedroom $2,770; two-bedroom $3,410; three-bedroom $4,460; four-bedroom $5,020. The FY2026 reference row printed on the same page ($2,485 / $2,977 / $3,604 / $4,604 / $4,772) does NOT match the FY2026 computation page (row 9) | new reading; closes flag U09 for this ZIP; discrepancy recorded as finding R55 | PASS with irregularity R55 |

## U09 close-out (HUD FY2027 Small Area Fair Market Rents, ZIPs 95014 and 94122)

The FY2027 ZIP rows were unread in earlier passes because the interactive lookup and the
spreadsheet could not be operated. On 2026-11-13 the official server-rendered
documentation pages were found and read directly (rows 10–11 above). Flag U09 is closed
with those values recorded in `final/sources.py`. The model is unchanged and keeps the
FY2026 figures (four-bedroom $6,390 for 95014, $4,380 for 94122); the earlier sensitivity
run (recorded with flag U09/R26) shows the decision ranking does not change until rent is
about 2.6 times the figure used. Switching the model to FY2027 would lower the 95014 rent
input about 9% and raise the 94122 input about 15% (four-bedroom basis) — a model change
left to the owner as a reviewed suggestion, not made here.

## Irregularity R55 (published on the review page)

The FY2027 calculation page for ZIP 94122 prints an "FY2026 FMR" reference row
($2,485 / $2,977 / $3,604 / $4,604 / $4,772) that differs from the official FY2026
calculation page for the same ZIP ($2,280 / $2,730 / $3,310 / $4,230 / $4,380). The
FY2027 page also notes that only a portion of 94122 lies in the San Francisco, CA HUD
Metro FMR Area and leaves the parent-area name blank in its render. Possible explanations
(a FY2026 revision — HUD lists "Revised FY 2026 FMRs", 91 FR 21301, effective 2026-05-21 —
or a different parent-area basis for the straddling ZIP) are not resolvable from the pages
read and are NOT asserted. The FY2026 figures quoted on the site remain those of the FY2026
computation page (row 9); nothing was overwritten. Owner/adviser can resolve by downloading
HUD's revised FY2026 SAFMR file (`fy2026_safmrs_revised.xlsx`, linked from
https://www.huduser.gov/portal/datasets/fmr.html) and comparing the 94122 row.

## Target set not re-read in this pass

- BOE Prop 19 landing page and BOE LTA 2026/026: unchanged purpose; last direct reads
  2026-11-12/13 by earlier passes stand (their links remain on every row that uses them).
- IRS inherited-property FAQ / Topic pages: covered by the 2026-11-12 full-page pass; not
  re-opened here.

## Privacy check of this audit

No names, street addresses, parcel/account numbers, or unrounded household figures appear
in this audit file. Public HUD rents and statutory amounts are official published figures.
