# Black Swan Economic Conditions — Research Log (session `arena/62c87525`, 2026-11-11)

Purpose: user requirement — "a separate section for black swan economic conditions that can
mimic real world conditions as growth and inflation is usually never consistent over a 50 year
period. Research and deep think about real economic conditions and baseline projections."

This log records what was read from official sources and what is model assumption. Nothing here
is legal, tax or investment advice.

## 1. Why constant-rate projections fail — the 50-year record

| Fact | Value | Status | Official source |
|---|---|---|---|
| CPI-U annual inflation, 50 completed years (1976–2025) | ranged **−0.4% (2009) to +13.5% (1980)**; the 1970s ran ~7%/yr, the 2010s under 2%/yr | verified | [BLS historical CPI-U](https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202407.pdf) |
| 30-year fixed mortgage rate (Freddie Mac PMMS, weekly) | all-time high **18.63% (Oct 9 1981)**; all-time low **2.65% (Jan 2021)** — a 7× range | verified (series publisher) | [Freddie Mac PMMS](https://www.freddiemac.com/pmms) |
| SF metro home prices, GFC | fell roughly **−23% (purchase-only HPI) to −35% (all-transactions HPI)** peak (2006–07) to trough (2011–12), depending on measure | derived (recompute from dataset for exact figures) | [FHFA HPI datasets](https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx) |
| US recessions since 1980 (NBER dates) | 1980 (Jan–Jul), 1981–82 (Nov–Nov), 1990–91 (Jul–Mar), 2001 (Mar–Nov), 2007–09 (Dec–Jun, 18 mo), 2020 (Feb–Apr, **2 months — shortest on record**) | verified | [NBER chronology](https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions), [NBER 2021 announcement](https://www.nber.org/news/business-cycle-dating-committee-announcement-july-19-2021) |
| Current baseline (CBO Feb 2026) | deficit **$1.9T (5.8% of GDP)** FY2026; debt held by public **101% of GDP (2026) → 120% (2036)**, past the 1946 record by 2030; PCE inflation projected 2.7% (2026) | verified | [CBO The Budget and Economic Outlook: 2026 to 2036](https://www.cbo.gov/publication/61882) |

Conclusion used on the site: a smooth 2.5%-inflation / 4%-appreciation line has **never**
occurred over any 50-year window of US economic history. Model paths must therefore include
variable growth and inflation.

## 2. Real episodes encoded into the scenario paths

| Episode | What we replay | Years used in model | Status |
|---|---|---|---|
| 1974–1983 stagflation | actual CPI 11.0, 9.1, 5.8, 6.5, 7.6, 11.3, 13.5, 10.3, 6.2, 3.8 | STAG window 2031–2040 | CPI leg verified (BLS); home +2%/yr and portfolio +5%/yr legs are assumptions calibrated to the episode |
| 2007–2012 GFC + SF crash | actual CPI 2.9, 3.8, −0.4, 1.6, 3.2, 2.1; home −8.2%/yr × 5 (≈ −35%, the SF all-transactions peak-to-trough); portfolio −37% then rebounds | GFC window 2038–2047 | CPI verified (BLS); home leg derived from FHFA measure; portfolio leg assumption (2008–2012 pattern) |
| 2020–2023 COVID whiplash | actual CPI 1.2, 4.7, 8.0, 4.1; home +18, +2, −3, +4; portfolio +16, +27, −19, +24 | COVID window 2036–2039 | CPI verified (BLS); home/portfolio legs assumptions (2020–2023 pattern) |
| 1976–2025 replay | all 50 actual CPI rates re-run through 2026–2075; home real growth per era (+2, −4, +1.5, −1.5, +4, −7, +4, pandemic pattern) | whole horizon | CPI verified; home/portfolio legs assumptions calibrated to cited episodes |
| Japan-style deflation tail | home −2%/yr × 15, CPI 0.5%, portfolio +2% | JP window 2036–2050 | **assumption (tail scenario, not a forecast)** — historical Japanese major-city land declined for more than a decade after 1991; the −2%/yr used here is a moderate stylization, not a measured series |

## 3. Property-tax rules that shape the black-swan answer (verified)

| Rule | Effect in stress | Official source |
|---|---|---|
| Prop 13 (Cal. Const. art. XIII A §2): assessment grows ≤2%/yr absent change in ownership | Cupertino effective tax rate on market value **falls** as values rise; in stagflation the tax bill is paid in devalued dollars (inflation hedge) | [BOE Prop 13 info](https://www.boe.ca.gov/proptaxes/prop13.htm) — see `analysis/data/california_tax.csv` for the row used site-wide |
| Prop 8 (RTC §51; BOE Pub 800-10): assessed value = **lower of factored base year value or current market value**; while below FBYV, annual increases are NOT capped at 2% until FBYV is re-reached | In a bust the assessment CAN drop with the market — but for this deeply under-assessed property (FBYV ≈ $550K vs market in the millions) the floor is far below any plausible crash value, so Prop 8 provides no practical relief in the modeled crashes | [BOE Pub 800-10](https://www.boe.ca.gov/pdf/pub800-10.pdf), [BOE LTA 2025/023](https://www.boe.ca.gov/proptaxes/pdf/lta25023.pdf) |
| Prop 19 parent-child exclusion: heir must occupy as principal residence within 1 year to keep the base year value up to the inflation-adjusted cap ($1,044,586 for 2025–2027 per BOE LTA 2025/009); otherwise full reassessment at market | "RENT the house" path pays the full FMV assessment; "LIVE in it" keeps a partial shield (~$18K/yr first-year saving in the base case) | [BOE Prop 19](https://www.boe.ca.gov/prop19/), LTA 2025/009 (see `analysis/data/california_tax.csv`) |
| IRC §1014 basis step-up at death | Selling at inheritance ≈ zero gain regardless of when the crash happened before death; the crash before death also **lowers estate value** (estate-tax headroom) | IRS — see `analysis/data/federal_tax.csv` |
| Federal estate exclusion $15,000,000 (2026, permanent + indexing under P.L. 119-21 §70106) | Two indexed slots (assumption: couple/trust) cover the two properties in every modeled scenario; the owner's additional cash assets decide the exposure — see the estate-tax page grid | IRS Rev. Proc. 2025-32 / P.L. 119-21 (see `analysis/data/federal_tax.csv`) |

## 4. Deep-think conclusions (analysis, not facts)

1. **SELL & reinvest wins 12 of 18 stress cells** (6 scenarios × inherit 2040/2045/2050). LIVE
   wins the other 3 (historical-replay 2045/2050 and nothing else) when a housing boom coincides
   with a weak stock window. RENT never wins: full reassessment at death + ordinary-rate rent tax
   erases the legacy Prop 13 advantage in every path tested.
2. **Crash timing vs the death year dominates the crash itself.** A −35% crash ending 3 years
   before death (GFC window 2038–2047, death 2045) still leaves SELL ahead; a crash landing
   right after inheritance punishes holders hard. SELL converts a concentrated, undiversified
   real-estate bet into a diversified portfolio exactly at the point of the step-up.
3. **Stagflation is the strongest HOLD case** — but the grid still gives SELL the edge, because
   post-tax stock returns in the replayed 1970s window were assumed flat rather than negative in
   nominal terms; the honest reading: under stagflation the decision tightens materially and the
   LIVE option (fixed tax bill + housing services) becomes competitive. Sensitivity flagged.
4. **Deflation (Japan-style) makes every strategy worse; SELL merely loses least.** A right
   decision still yields 2.5× less terminal wealth than the baseline (≈$4.3M vs ≈$10.4M at
   2045→2055). Decision quality ≠ outcome quality; this is exactly why the black-swan section
   exists.
5. **Insurance and water are the inflation-transmission channels** (grown at CPI + 2.5% / +2%
   assumptions; CA homeowners insurance is in a hard market — flagged on the costs page). The
   property tax is the one cost that inflation *shrinks* in real terms.

## 5. Irregularities / flagged items

- SF metro HPI crash magnitude is measure-dependent (−23% vs −35%); exact figures require
  recomputation from the FHFA dataset. The model uses −35% (conservative). **Flagged.**
- Portfolio and home-price scenario legs are **assumptions** calibrated to published episode
  magnitudes; they are not forecasts and not probabilities. **Flagged.**
- "Cupertino has no local rent-control ordinance" (used in the RENT strategy) is an assumption;
  not confirmed from an official city source in this session. **Flagged.**
- Estate exclusion indexing (2.5%/yr) is an assumption; the statute indexes to chained CPI
  (P.L. 119-21). **Flagged.**

Model + outputs: `analysis/blackswan_model.py`, `analysis/data/blackswan_*.csv`,
`dashboard/data/blackswan_output.json`. Site page: `dashboard/black-swan.html`.
