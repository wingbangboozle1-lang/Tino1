# Live GitHub Pages verification — 2026-11-13 UTC (session `arena/e351c885-tino1`)

Fetched with a full-page reader from `https://wingbangboozle1-lang.github.io/Tino1/` while
`main` was at `11cf93c` (PR #77 merged) and the Pages API reported `build_type: legacy`,
`source: {branch: main, path: /}`, `status: built`, public.

| Address fetched | What rendered | Result |
|-----------------|---------------|--------|
| `/` (chooser) | Two-edition chooser: no-figures guide first (privacy first), rounded-figures analysis second; links to `privacy-site/public/index.html`, `summary.html`, `flagged.html`; states "rounding is not anonymization"; placeholder people (the Transferor, the Inheritor); "Not legal, tax, investment or insurance advice." | PASS |
| `/summary.html` | Full numeric executive dashboard: best plan ("Sell Property A, keep Property B", conditional, 43-of-50 and 50-of-50 historical-sequence evidence), Property A at inheritance $6,531,230, tax triple $7,210 / $59,950 / $77,480, Property B tax advantage $19,890/yr, estate-tax room $17,612,280 (2045) ≈ $11,016,970 (2026 dollars), "no California or local inheritance tax", "What would change the answer" lever table with flag links A01/A02/A07/U08/Q01/Q06/Q15 | PASS |
| `/flagged.html` | Flagged-for-review tables (Q01–Q18 incl. Q15–Q18, P01–P02 privacy flags, …), each with "What the site does / How to resolve it / Where to check" and official links; statement that nothing blocks | PASS |
| `/privacy-site/public/index.html` | No-figures guide front page: ownership distinction A vs B, official-context rows with links (RTC §51, BOE Prop 19, IRS inherited-basis FAQ, 2027 IRS inflation adjustments, CA DOI, SEC investor page), conditional recommendation, "rounding is not anonymization" notice | PASS |

## Consistency checks between the live dashboard and directly-read sources

- Dashboard rent benchmark "HUD four-bedroom small-area rent for ZIP 95014, $6,390 a month"
  equals the HUD page value fetched directly (VERIFICATION.md row 10). 
- Dashboard Property B tax advantage is computed against the SF secured rate; the model uses
  1.18162182%, exactly the rate published live on the SF Treasurer page today (row 8).
- The dashboard's estate-tax room cites the projected 2045 exclusion $24,143,520 — consistent
  with the verified 2026 $15,000,000 and published 2027 $15,480,000 trajectory (rows 1–3)
  continued at inflation.
- No name, street address, e-mail, phone or parcel number appeared in any fetched live page.

## Deployment evidence

- Pages API (fetched via `gh api repos/wingbangboozle1-lang/Tino1/pages`): `status: built`,
  no error, branch `main`, path `/`, `public: true`, `https_enforced: true`.
- The four addresses above were fetched live, so what is deployed matches what CI builds.
