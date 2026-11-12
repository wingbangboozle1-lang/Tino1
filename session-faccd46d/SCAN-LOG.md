# FAC-3 — published-tree privacy and rounding sweep (session faccd46d, 2026-11-11)

Scope: every tracked file in the repository (root pages, `dashboard/`, `docs/`, `site/`, `archive/`,
`verify-4395771d/`, `analysis/`, `data/`, `downloads/`, `final/`, `integrated/`, `model/`, `research/`,
`scripts/`, `legacy95/`). Purpose: confirm the privacy mandate (no personal information; owner figures
only rounded to $10) before release, acting on the release-safety points raised in PR #31
(`audit-de9174cd/REPORT.md`).

## A. Unrounded owner figures

Tested for every exact, non-$10-multiple figure from the owner-supplied history series (assessed values
and tax bills for both properties, 2014–2026). Six substring hits; each inspected in context; **all six
are false positives**:

| File | Token | What it actually is |
|---|---|---|
| `analysis/data/blackswan_history.csv` | `[figure withheld]` | Part of the episode id `H2,1979-1982` (a year range) |
| `black-swan.html` | `[figure withheld]` | SVG chart coordinate fragment (`359.2,197.1`) |
| `projections.html` | `[figure withheld]` | SVG chart coordinate fragment (`669.2,134.9`) |
| `decision.html` | `[figure withheld]` | Mid-number inside a rounded model output |
| `verify-4395771d/site/black-swans.html` | `[figure withheld]` | Mid-number inside a rounded model output |
| `verify-4395771d/site/decision.html` | `[figure withheld]` | SVG chart coordinate fragment |

Historical session result: the specific token sweep described above did not find an unrounded owner figure in its inspected files. This is not proof of anonymity or completeness; the fingerprint register was subsequently removed because it was reversible. The token column below is masked by the repository's privacy scrub (`step7_fingerprints`,
which rewrites fingerprinted tokens outside `final/`); each masked hit was only a substring of the
non-owner content described in the third column (the underlying tokens are themselves owner figures from
the brief, which is why the scrub masks them even in this log).

Note on the superseded dashboard: one assessed-value illustration is a rounded derived model output rather than the rounded owner-reported anchor. Both values appeared in earlier material; the distinction does not verify either figure. The original branch is retained for the full historical audit.

## B. PII patterns (street addresses, e-mail addresses, phone numbers, parcel numbers)

Five regex hits, **none personal information**:

| File | Hit | What it is |
|---|---|---|
| `analysis/check_site.py` | `assessor@sfgov.org`, `cpi_info@bls.gov`, `PressOffice@bls.gov` | Public agency contact addresses inside a checker’s source list |
| `analysis/data/local_rules.csv`, `dashboard/tax-law.html` | `415-252-4600` | San Francisco Rent Board’s public phone number (agency contact) |

Known accepted false positive: `chart.js@4.4.8` CDN strings under `docs/` trip the e-mail regex
(unchanged from earlier sessions).

## C. Parcel numbers / APNs

Zero unmasked APN-like tokens. All parcel references are masked placeholders (`[APN: ***-**-***]`).

## D. Residual risk (owner action — recorded, not fixable by a session)

- The repository is **public** and its **Git history** contains the earliest page versions, written before
  the $10 rounding convention. Deleting files now does not erase history. Only the owner can make the
  repository private or have the history rewritten; this is recorded in `README.md` (“Owner action still
  needed for full privacy”), flags **P02** on the Flagged for Review page, and PR #31’s blocker 1.
- Rounded owner figures plus ZIP codes remain *linkable in principle* to county assessment rolls for
  anyone who already has the roll. The owner’s own brief prescribes $10 rounding as one requested
  mitigation (not a guarantee of anonymity); the year-by-year series is withheld entirely (flag **P01**) to reduce that risk further.

## E. Gates run after the sweep

- `python3 final/check.py .` → OK (22 pages, 703 sourced rows, 2,138 dollar figures rounded to $10,
  privacy fingerprints clean, model self-tests 51/51).
- `python3 final/integrate.py` → 2,038 internal links repo-wide, 0 broken.
- `python3 legacy95/check_legacy.py` → PASS (banned commercial links 0).
