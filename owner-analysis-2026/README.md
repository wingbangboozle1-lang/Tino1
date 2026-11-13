# Two-home inheritance analysis: owner working pack (not published)

Session `arena/022b1ea7-tino1`. Scope is claimed on `COORDINATION.md` (tasks O1–O4).

## What is in this folder

| File | Contents | Public? |
|---|---|---|
| `sources/official-sources.csv` | 24-row register of values, each with a source URL, source type and status (verified, flagged or unverified) | Safe to publish (no household figures) |
| `exemption-projection.csv` | Federal basic exclusion 2027–2050 under two indexing assumptions (2.0% and 2.3%) | Safe to publish (generic, no household data) |
| `FLAGS.md` | Flagged items, repository irregularities and open questions | Safe to publish |

Household projections (values, assessed value, property tax, insurance, water, electricity, rent) are **not in this repository**. They were computed privately from owner-supplied inputs and kept outside the repo, because they are personal financial details and the repo is public. Their outputs are rounded to the nearest $10. Any cost the owner has not supplied is left blank.

## Status

- **Verified official sources:** 2027 federal exclusion, Prop 19 cap and conditions, the 2026-27 CA roll factor, the SF FY2026-27 tax rate, the SF 2026-27 rent increase, SB 974 chaptering, NIIT thresholds, the SCO state estate-tax status, the Treasury 10-year yield and the Civil Code §1947.12 rent cap.
- **Not complete:** the historical CPI series (only 1947–1963 of FRED CPIAUCSL was read), the official FHFA county-level HPI files for both properties (the metro CSV URL returned 404), Property A water provider, Property A rent, repair and maintenance costs, after-tax sale math, and the Japan question. These are flagged, not filled.
- **Publication:** the public site is **not** expanded in this change. Under decision D1 the existing numeric pages are already public. Adding household-specific projections requires the owner's privacy decision first (G01/G02 routing and history remediation). See `FLAGS.md` F21–F23.

## Privacy rules applied

- No names, street addresses, parcel numbers or contacts appear here.
- The city and ZIP for Property A are owner-supplied and are kept out of public outputs.
- Rounding to $10 is disclosure minimization, not anonymization.

## Not legal, tax, investment or insurance advice

The figures and rules here are for planning review. The owner should confirm them with a qualified tax or estate professional before acting on them.
