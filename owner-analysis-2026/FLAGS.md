# Flagged for review

Each flag names what is unverified or irregular, what was checked and what is needed next. Flags do not block merge, per the owner's instruction. "Blank" means the value was not supplied and was not inferred.

## Owner-supplied household inputs (internal)

- **F01 Household values not from a public source.** Estimated values, assessed values, 2025 property taxes, water, electricity, insurance, and the Property B rental total are owner-supplied. They have no public source to link, so they are kept out of public tables. Status: flagged, private.
- **F02 Property A water provider unresolved.** The city site says California Water Service serves the northeast, San Jose Water the southeast, and the city system is leased to San Jose Water through 2036. Which applies to Property A is not known. Status: blank until the parcel's provider is confirmed from the owner's own bill.
- **F03 Property A rent not verified.** The earlier HUD SAFMR four-bedroom figure used without a confirmed bedroom count is not used here. Status: blank.
- **F04 Repairs and maintenance blank for both properties.** The owner said Property A is lower than Property B but gave no figure. Status: blank.
- **F05 Insurance.** The owner's ~$1,500/yr is below the CDI data-call average of $2,339.99 (secondary, flagged in S22) and the FAIR Plan dwelling average of $2,918.18 (secondary). Both benchmarks are shown beside the owner figure. Status: flagged.
- **F06 Property B property tax reconciliation.** The owner's 2025 bill ($2,439) is about $1,090 above 1.18% of assessed value. The residual is a derived figure that may include bond or direct charges not identified here. Status: flagged, bill needed.
- **F07 Japan.** The owner's location is recorded internally. If the heir is domiciled in Japan, or is a Japanese national who lived in Japan in the last 10 years, Japan inheritance tax may apply to worldwide assets. Secondary sources describe a ¥30M + ¥6M per-heir basic exclusion and 10–55% rates; the National Tax Agency was not fetched. Status: unverified, not modeled.

## Federal and California law

- **F08 IRC §1014 (basis step-up at death).** Not fetched this session (uscode.house.gov returned 404). The IRS page for topic 703 defers to Pub 551. Status: unverified citation.
- **F09 Federal capital gains rates, NIIT and CA income tax brackets.** NIIT thresholds verified (S05, S06). The federal long-term rate brackets and CA brackets were not confirmed (FTB rate page returned 404; secondary 2025 CA rates 1%–12.3% plus 1% MHST above $1M). Status: blank for after-tax sale math.
- **F10 Prop 19 conditions for the trust transfer.** Occupancy within 1 year and filing within 1 year (S09) are verified. The owner's plan is for the Inheritor to occupy the home, which would qualify for the family-home exclusion. If not, the home is reassessed to market value. Status: verified; the trust timing (150 days after death for trust-held property, R&T §480) is from a prior leginfo fetch, not re-read here.
- **F11 Prop 19 cap changes February 2027.** The $1,044,586 cap applies until 2027-02-15. The next biennial adjustment is not yet known. Status: pending.
- **F12 Federal estate exclusion 2040–2050.** The 2026 figure ($15,000,000) and the 2027 figure ($15,480,000) are verified. Projections beyond 2027 are scenarios, not law. Status: assumption-based (`exemption-projection.csv`).
- **F13 Rent cap exemptions.** Civil Code §1947.12 exempts units with a certificate of occupancy in the last 15 years. Whether the Property B units qualify is not known. Status: flagged.
- **F14 SB 974.** Chaptered as Stats. 2026 ch. 665 on 2026-09-27 (S12, verified on leginfo). The effective date (2027-01-01) is secondary only, see F26.

## Economic baselines and history

- **F15 SF Treasurer tax-rate conflict in the repository.** `COORDINATION.md` entry #7 cites an SF Treasurer rate of 1.18268325%. The SF Treasurer page now lists 1.18162182% for FY2026-27 (S11). The repo figure does not match the current official page. Status: irregular, needs correction.
- **F16 Federal "$15M permanent" wording.** Board entry #9 calls the $15M exclusion permanent. The verified sources show $15,000,000 for 2026 and $15,480,000 for 2027, indexed. The "permanent" wording is not supported by the fetched sources. Status: irregular wording.
- **F17 Projection inputs cited on the board but not verified here.** FHFA HPI 4.5% and 3.8%, BLS CPI 3%, portfolio 7%→6.5%. None was reproduced here. Status: unverified, not used.
- **F18 Sell-vs-hold result on the board.** "Sell wins by ~$1M at 10 years" cannot be reproduced without the model inputs. Status: unverified.
- **F19 Historical CPI not complete.** FRED CPIAUCSL chunk 0 of 4 (1947–1963) was read. Chunks 2–4 were not read. Long-run inflation history is therefore unverified. Forward inflation references are from the Fed (2%), CBO (2.7%→2.0%), and SSA (2.4% ultimate CPI-W), all verified (S17–S19). Status: partial.
- **F20 FHFA county-level HPI files.** The metro CSV at fhfa.gov returned 404. Official county-level series for both properties were not located. The San Jose series (S20) is verified via FRED. Status: unresolved.
- **F21 Election results are unofficial.** The SOS page (S21) is partial, as of 2026-11-12 6:47 pm. Certification is by 2026-12-11. The earlier fetch-log percentages (for example Prop 3 60.6%) do not match the current page (60.7%), so the fetch log is out of date. Status: flagged; not used for any figure.
- **F22 Prop 19 repeal.** The current SOS list of 14 statewide measures contains no Prop 19 repeal (S21). Secondary claims of a 2026 repeal are not supported. Status: verified against the list.
- **F23 Treasury yield.** The 10-year was 4.98% on 2026-11-10 and 5.10% on 2026-11-12 (S16). The prior fetch-log value (4.98%) is dated, not current. Status: dated reference.

## Repository and privacy

- **F24 Household-derived numeric pages are public (decision D1).** The root numeric pages publish household-derived figures rounded to $10, with ZIP and locality cues. Rounding is not anonymization. This needs an owner decision (G01/G02 routing, history remediation, or privacy-only revert). Status: owner decision open; not changed in this pass.
- **F25 Public Git history contains pre-rounding figures.** Previously recorded on the board. Remediation needs owner approval. Status: open.
- **F26 SB 974 effective date.** Secondary sources say effective 2027-01-01. Leginfo confirmed the chaptering, not the effective date. Status: flagged.
- **F27 `privacy-site/check.py` scope.** It checks a fixed list of literals, not all personal information (per the prior audit). This pass did not change it. Status: known limitation.
- **F28 Fed and CBO URLs.** The FOMC press-release URL and the CBO URL come from search results and were not fully re-read. S17 uses the Fed homepage. Status: partial.
- **F29 Line-by-line repository review is partial.** This pass checked the publish allowlist, `_config.yml`, `index.html`, `COORDINATION.md` entries #5–#12 and the claims they make. It did not check every page in `summary.html` or the other numeric pages. Status: incomplete.

## What was not done in this pass

- Owner-level decisions on public publication of household projections (F24, F25).
- Official Property A water provider, repair costs, Property A rent (F02–F04).
- Full after-tax live/rent/sell comparison (F08, F09 unresolved, F04 blank). No "best plan" is stated because the inputs for one are not complete.
- The historical CPI series and FHFA CA/SF files (F19, F20).
