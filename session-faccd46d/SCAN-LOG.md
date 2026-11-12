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
| `decision.html` | `[figure withheld]` | Mid-number inside the rounded model output `$12,197,660` |
| `verify-4395771d/site/black-swans.html` | `[figure withheld]` | Mid-number inside the rounded model output `$12,179,270` |
| `verify-4395771d/site/decision.html` | `[figure withheld]` | SVG chart coordinate fragment |

Result: **no unrounded owner figure is present in any published or stored file.** The canonical checker
agrees (`final/check.py .` — privacy fingerprints clean; the fingerprint register covers the exact
unrounded tokens). The token column below is masked by the repository's privacy scrub (`step7_fingerprints`,
which rewrites fingerprinted tokens outside `final/`); each masked hit was only a substring of the
non-owner content described in the third column (the underlying tokens are themselves owner figures from
the brief, which is why the scrub masks them even in this log).

Note on `dashboard/projections.html` and `dashboard/properties.html`: they show `$550,530` for the 2026
assessed value. This is **not** a mis-rounding of the owner figure; it is a *derived* model output of the
superseded 6ea079fa model (2025 anchor `$539,740` × 1.02 = 550,534.8, rounded to $10), and it is labelled
“derived” and flagged on that page. The canonical model uses the owner’s 2026 figure rounded to `$550,540`.
Left unchanged: altering another edition’s model output would falsify it; it is consistent inside its own
edition and its label is accurate.

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
  anyone who already has the roll. The owner’s own brief prescribes the $10 rounding as the accepted
  mitigation; the year-by-year series is withheld entirely (flag **P01**) to reduce that risk further.

## E. Gates run after the sweep

- `python3 final/check.py .` → OK (22 pages, 703 sourced rows, 2,138 dollar figures rounded to $10,
  privacy fingerprints clean, model self-tests 51/51).
- `python3 final/integrate.py` → 2,038 internal links repo-wide, 0 broken.
- `python3 legacy95/check_legacy.py` → PASS (banned commercial links 0).
