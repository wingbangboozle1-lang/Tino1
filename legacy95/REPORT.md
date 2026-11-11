# Legacy edition close-out report — session `95383689` (2026-11-11)

Scope: **L95-1..3** — closing the open change requests that sat on the *superseded*
editions (`dashboard/**`, `docs/**`, `site/**`, `archive/root-site-2026-11-11/**`)
plus their supporting `analysis/**` and `research/**` files, without touching the
canonical root site, `final/**`, `README.md`, or other sessions' lanes.

Rule applied throughout (per the claim in `COORDINATION.md`): a table row gets an
official link only to a page that was **read this session** or is carried in
`final/sources.py` (re-read 2026-11-11 by session `07a57a05`); a value with no
official source keeps its number and is given an explicit unverified/assumption/
model-output label — **never** a made-up source, never silently altered.

---

## 1. Change requests closed

| CR | What was wrong | Fix | Evidence |
|---|---|---|---|
| **CR-07-5** | 856/1,515 legacy `<tr>` rows had neither an official link nor a label (raw count before applying the label rule; 588 rows needed work once declared-label rows were counted as compliant) | `legacy95/source_rows.py` appended an official link or an explicit label into each row's **last `<td>`** (no columns added, structure byte-preserved per `git show` comparison) | `legacy95/check_legacy.py` → **1,490 rows: 1,207 official link / 283 flagged label / 0 work — PASS** |
| **CR-07-7** | `analysis/data/federal_tax.csv` F06 note said closing-letter fee was "previously $67"; the cited IRS page (read this session) says the TD 10055 fee went **$56 → $76** eff. 2026-10-26 | CSV note → "previously $56"; same correction in `dashboard/inheritance-tax.html` closing-letter row | IRS "What's new — estate and gift tax" fetched this session; `check_legacy.py` reports 0 stale notes |
| **CR-43-1** | `docs/js/app.js` SyntaxError (stray `}` line 69), previously fixed by another session | Re-tested: `node --check docs/js/app.js` → exit 0 (also `site/assets/app.js` exit 0) | Closed as verified-fixed; no edit needed |
| **CR-85-1** | Commercial/non-official citations in `docs/*.html`, `research/*.md` (policygenius, nerdwallet, zillow, rentometer, car.org, ballotpedia, gethomeinsurancequotes, law.cornell) | HTML: anchors **unlinked** (origin text kept, marked "commercial estimate — non-official") + official context link added (CDI compare-prem / CDI study / HUD FMR / FHFA HPI via FRED / SOS election returns). Code citations swapped to official publisher: IRC §1014 & §2001 → govinfo (page text read this session), §1411 → IRS Topic 559, §121 → Pub 523, §2503 → IRS gift tax, §2010 → IRS "what's new" (read this session; it states §2010(c)(3) $15M), §401 → unlinked (companion official link remains in cell). `research/*.md`: origin URL kept visible with "(commercial estimate — non-official; official context …)" marker — never re-attributed | `check_legacy.py` banned-host scan = **0** across the four trees; audit-log prose in `research/repo-audit-85899999.md` intentionally left quoting the old URLs (descriptive record, not a citation) |
| **CR-85-2** | 3 wrong links | `irs.gov/newsroom/irs-releases-2025-amounts…` → `https://www.irs.gov/pub/irs-drop/rp-25-32.pdf` (9 anchors); FTB `income-types/capital-gains.html` → `capital-gains-and-losses.html` (`research/tax-law.md`); Federal Reserve `fomcprojtabl20260617.htm` → `https://www.cbo.gov/publication/62105` (`research/utilities-insurance-market.md`) | applied by `source_rows.py`, logged in run output |
| **CR-85-3** | Missing official primary-source links in `properties.html`, `flagged.html`, `scenarios.html`, `docs/projections`, `docs/decision`, `docs/cupertino`, `docs/sanfrancisco`, `docs/operating-costs` | `docs/**` + `site/**` copies subsumed by the CR-07-5 row pass; the root copies were already clean (they are inside `final/check.py`'s 668/668 sourced-row gate, which stays green) | `check_legacy.py` PASS + `final/check.py` OK |
| **CR-85-4** | $10-rounding re-audit + blank Cupertino actual-tax cell | Re-audit of all four trees + `properties.html` + `data/*.json|csv`: **owner/analysis figures $10-clean**. Fixed this session: `dashboard/costs.html` + `dashboard/properties.html` rent midpoint rows ($3,575→$3,580, $125/$365 midpoints reworded to the already-rounded user ranges $100–150 / $330–400), `docs/index.html` derived figures ($2,055,414→≈$2,055,410, $12,326→≈$12,330), `dashboard/executive-summary.html` ($433,824→$433,820), `dashboard/methodology.html` year typo `$2,045`→`2045`. Kept exact: statutory constants ($1,044,586 BOE allowance, $15,000,000/$19,000 exclusions, IRS fee $76/$56, FTB/HUD/CDI published rates — rounding falsifies sources) and commercial survey quotes (public averages, marked non-official). Cupertino 2026 actual-tax cell: blank + "Flagged: 2026 tax bill unverified (left blank; never inferred)" already present in `site/properties.html` ✓ | final scan: 1 remaining hit is the rounding note's own counter-example ($3,100,001) |
| **CR-85-5** | Legacy `model/project.py` mixed ad valorem + fixed parcel charges | **Closed by reference, no legacy rework** (canonical engine): `final/model.py:40` `dc_cup=930, dc_sf=1_090` separates fixed charges from `rate × value`; used at line 228. These are exactly the ~$930/~$1,090 figures the CR asked for | `final/check.py` PASS |
| **CR-85-6** | NEM sunset / PG&E base charge / SF 60 %-CPI cap / Rev. Rul. 2023-2 into `model/project.py` + docs | Policy context is present across the superseded docs (NEM & D.22-12-056 in 9 files incl. `docs/projections`, `docs/taxes`; SF rent-cap & fixed-fee coverage in `dashboard/*`; Rev. Rul. 2023-2 row in `docs/inheritance-tax` now links IRS IRB 2023-16). The `model/project.py` code target is **outside L95-1's claimed scope** (`model/**` owned elsewhere) → remainder flagged for owner decision in §3, non-blocking per owner rule | see §3 |

## 2. Row pass — final numbers

| Tree | Rows | Official link | Flagged label | Work |
|---|---|---|---|---|
| `dashboard/**` | 614 | 525 | 89 | 0 |
| `docs/**` | 369 | 264 | 105 | 0 |
| `site/**` | 161 | 161 | 0 | 0 |
| `archive/root-site-2026-11-11/**` | 346 | 257 | 89 | 0 |
| **Total** | **1 490** | **1 207** | **283** | **0** |

Label reasons (283): assumption 71, owner/user figure 65, "same" cross-reference 56,
calc/sum-of-flagged 19, qualitative/status 19, estimate/industry rule 7, derived 10,
flag-register row 8, projections-note 5, placeholder 2, unverified citation 5,
market-history 1.

Mechanics: links/labels appended into the last `<td>` (column count unchanged —
verified row-by-row against `git show HEAD:` for all 34 changed HTML files);
idempotent; `python3 legacy95/source_rows.py` re-run is a no-op. Full gate:
`python3 legacy95/check_legacy.py`.

## 3. Flagged for owner review (non-blocking)

1. **Source disagreement (CR-07-7):** an earlier session recorded the closing-letter
   fee as "$67"; the IRS page read today says $56 → $76 (TD 10055). Live IRS text
   wins; discrepancy logged here per protocol.
2. **CR-85-6 code remainder:** NEM-sunset / PG&E BSC / SF 60 %-CPI modeling inside
   legacy `model/project.py` was **not** reworked (scope belongs to `model/**`
   owners; the canonical engine already separates fixed charges). Decision needed:
   rework legacy model or let the superseded notice stand.
3. **`model/assumptions.md` $10 pass:** one non-$10 token remains (`~$189/mo`
   SFPUC average, attributed to SFPUC) — file outside L95-1 scope; flagged for its
   owner to confirm it is an official published average or round it.
4. **F4 memory arithmetic (corrected):** earlier session notes said "3 audit dirs
   on main" — main actually has 2 (`audit-5d8f7074`, `audit-7bac5c33`);
   `audit-84ad24ba` exists only on its unmerged branch. Also T20's claim that
   `docs/js/app.js` fails `node --check` is stale (fixed; re-verified this session).
5. **Docs rate-label skew:** `docs/sources.html` register rows label their rate
   citations FY24-25/FY25-26 vintage while the dashboard uses FY26-27
   (1.18162182%) — each row describes the page it cites; left as-is, noted here.
6. **Failed URL patterns (do not retry):** `govinfo …subtitleA-chap12-…sec1014.htm`
   (correct: `subtitleA-chap1-subchapO-partII-sec1014`), govinfo `partI-sec2010`
   (404), `uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-…` (site in
   temporary format, 404), `selfhelp.courts.ca.gov/trusts` (404; root works).
   Redirects confirmed by reading: `sfassessor.org` → `www.sf.gov/departments--assessor-recorder`,
   `sccassessor.org` → `asr.santaclaracounty.gov/home`.

## 4. URLs read in this session (2026-11-11)

IRS what's-new estate/gift (fee $56→$76; §2010(c)(3) $15M), RTC §51 (2 % cap),
IRS Pub 551, Pub 523, Pub 946, FTB home, govinfo §1014 + §2001, sfassessor→sf.gov,
sccassessor→asr.santaclaracounty.gov, selfhelp.courts.ca.gov root, NBER business-cycle
data. Reused from `final/sources.py` (read same day by `07a57a05`): FRED HPI/CPI,
BLS CPI, BOE LTA 2025/009 + 2026/026 + Prop 19 + homeowners'-exemption pages,
sftreasurer, SCC Tax Rate Book, clerk-recorder, IRS TC701/TC409/TC559/FAQ/i706/
IRB 2023-16/P527/Rev. Proc. 2025-32/estate-tax/gift-tax, leginfo Prob. Code
§16061.7, HUD FY2026 FMR, CDI (5 pages), CPUC NEM, SFPUC rates, SF rent-law pages,
SOS election results, CBO publication 62105, SCO.

## 5. Gate battery (all green at time of commit)

- `python3 legacy95/check_legacy.py` → PASS (0 work rows, 0 banned links, 0 stale notes)
- `python3 final/check.py .` → OK — 21 pages, 668 sourced rows, 1,654 links,
  2,101 dollar figures rounded to $10, privacy fingerprints clean, model self-tests 51/51
- `python3 final/integrate.py` → 1,990 internal links, 0 broken
- `node --check docs/js/app.js` (and `site/assets/app.js`) → exit 0
- `docs/data/projections.json` → valid JSON after citation swaps
- Row-structure diff vs `HEAD`: all 34 changed HTML files byte-count-identical tables
