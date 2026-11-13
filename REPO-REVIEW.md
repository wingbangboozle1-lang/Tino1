# REPO REVIEW — wingbangboozle1-lang/Tino1 (2026-11-11, session arena/944a92cd-tino1)

Method: line-by-line read of tracked files; every figure either traced to an official source or flagged; claims verified against live official pages (links in §5). Nothing was corrected silently — canonical pages were rewritten; legacy content was preserved (not deleted) with exact parcel figures rounded to $10.

## 1. Architecture irregularities (structural)

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| A1 | **Four overlapping sites deployed simultaneously**: root `/` (mirror), `/docs/` (9-page lab), `/site/` (standalone suite), `/dashboard/` (after-tax model). Different assumptions (A appreciation 3.0/3.5/4.0/4.5%, portfolio 6.5 vs 7.0%, CPI 2.5 vs 3.0%) and contradictory headline verdicts ("Sell wins by ≈ $1M @10yr NPV" vs "S4 ≈ $14.2M at 2055" vs "S1 = $22.68M by 2060"). | HIGH | **Closed**: canonical site = root pages (this session). Legacy trees kept in repo, exact figures purged (§3), removed from canonical nav. See COORDINATION.md log. |
| A2 | **GitHub Pages source = `main:/`** (legacy build, root `.nojekyll`): every directory in the repo is public. Anyone can reach `/docs/`, `/site/`, `/dashboard/`, `/model/`, `/research/`, `/analysis/`, `/data/`. | HIGH | Content now privacy-clean repo-wide; canonical entry is `/`. Consider Pages = `/docs` with curated content or excluding legacy dirs via `_config.yml`/`.nojekyll` hygiene (Jekyll not in use). **Owner decision needed — not changed unilaterally** (Pages settings are out-of-band-state). |
| A3 | `_config.yml` (Jekyll Cayman) unused under `.nojekyll`; misleading. | LOW | Harmless; left untouched. |
| A4 | `steps.html` duplicated `process.html`; root `index.html` duplicated `docs/index.html`. | LOW | **Closed**: `steps.html` is now a redirect → `process.html`; root `index.html` is the canonical executive summary. |
| A5 | `scripts/`, `model/verified_model_85899999.py`, `research/repo-audit-85899999.md` etc. — session-named artifacts in shared tree. | LOW | Retained (no discard); not part of canonical build. |
| A6 | Open PR #7 (session e25621af, opened 2026-11-10, never merged, >60 min stale) — content unknown to this review. | MEDIUM | Not merged, not used. If it merges later, a diff against canonical pages is mandatory before treating it as authoritative. |

## 2. Privacy findings (top priority)

| # | Finding | Where | Resolution |
|---|---------|-------|------------|
| B1 | **Exact user-supplied assessed values & tax bills published**: year-by-year assessed values (A: 2014–2026; B: 2016–2025) and exact bills (exact, non-$10 bills for both properties) — quasi-identifiers searchable against public county rolls. Violated both the privacy mandate and the $10-rounding rule. | `properties.html`, `docs/properties.html`, `docs/cupertino.html`, `docs/sanfrancisco.html`, `docs/index.html`, `docs/projections.html`, `docs/taxes.html`, `docs/flagged.html`, `docs/data/projections.json`, `model/assumptions.md`, `data/assumptions.json`, `docs/js/app.js`, `site/assets/app.js`, `scripts/build_site_85899999.py`, `research/repo-audit-85899999.md`, `COORDINATION.md` | **Closed 2026-11-11**: automated purge (`integrated/scrub.py`, literal-map ROUND_HALF_UP to nearest $10). Verified: exact values no longer matchable anywhere in working tree. Statutory constants kept exact by design (P15). |
| B2 | **Exact values remain in git history** (commits ≤ 2a16da8). True erasure requires `git filter-repo` + force-push — destructive, rewrites PR refs. **Not performed without owner consent.** | all pre-merge commits | **Flagged for owner decision.** Recommend: (a) accept residual risk (repo is public), or (b) owner runs history-rewrite + secret/PII scan + re-publish. |
| B3 | ZIP codes 95014 / 94122 are public and intentional; values & assessment-ratio patterns narrow identification further but are now all $10-rounded. | site-wide | Mitigated by rounding; appraisals/exacts remain owner-side only. |
| B4 | `analysis/data/property_a_history.csv` already withholds series (privacy-correct pattern — kept); `property_b_history.csv` derived-ratio-only (kept). | analysis/ | No change. |
| B5 | COORDINATION.md embeds exact figures quoted while documenting CR-85-4 itself. | COORDINATION.md | **Closed** (scrubbed). |

## 3. Content-accuracy irregularities found in legacy pages (all superseded by canonical pages)

Numbers cited as published (pre-purge rounding):

1. **docs/cupertino.html**: "Assessed value" anchor published unrounded (quasi-ID; now $10-rounded); "2025 bill" and "assessed" both published unrounded = 1.34% effective (arithmetic ✓; effective rate above 1.16% composite — direct charges ≈ $930/yr, derived, unverified (flagged X02/X17)); "County avg for Cupertino 1.15–1.22%" — no .gov source; industry-ish figure.
2. **docs/sanfrancisco.html**: "2.13% effective vs 1.18% ad valorem — extra ≈ 0.95% (fixed charges)" — arithmetic ✓, unitemized; "$7,150/yr $85,800/yr" user-supplied, flagged; "$3,500/mo HUD benchmark" — superseded by HUD FY2026 metro 2-BR ≈ $3,174 (my pages) — note: metro vs small-area distinction unresolved in legacy.
3. **docs/index.html / root index.html**: "Sell wins ~$1M at 10-yr NPV (6.5% portfolio)" — method mismatch across sessions (NPV vs terminal wealth); both favor S1; canonical model uses terminal-wealth accounting with after-tax liquidation (scenarios.html).
4. **docs/projections.html**: parent-assessed column uses unrounded anchor (now rounded); Prop 19 example "live-in" figure computed off $3.1M- 2026 values with 2026 cap — internally consistent then; canonical 2045 worked example supersedes it.
5. **dashboard/ (6ea079fa)**: consistently privacy-safe (withholds series) and well-structured; its verdict "S4: $14,218,760 (2055)" differs in horizon (2055 vs my 2060), in scenario taxonomy (S4 = sell+invest+live-B-unit ≈ my S1), and in assumptions (A +4% vs my +3.5%, CPI 2.5% same, portfolio 7% same). Arithmetic internally consistent; not directly comparable to canonical. Its 23 X-flags carry forward as X01–X23 here.
6. **site/ (85899999)**: "All figures $10-rounded" claim verified on spot checks of its pages (compliant); verdict identical (Strategy S1); its $22,682,780 (2045→2060) vs my $19,840,500 — difference from A appreciation (theirs ≈ 4%+, B 5-yr HPI path) and tax/horizon handling; both rank S1 first.
7. **README.md**: SF Treasurer was linked `sftreasurer.org/property-tax` → **dead (verified 2026-11-11: "Page Not Found")**. SCO link `state_finances_estate_tax.html` → **dead (verified 2026-11-11: "The page you requested is not found")**. Correct destinations: `sftreasurer.org/property/secured-property-taxes` and `sco.ca.gov/ardtax_estate_tax.html` — both live (verified 2026-11-11) and used throughout the canonical site. (CR-6E-2 closed with evidence.)
8. **docs/ & root pages**: SCC rate-book figure for FY2026-27/2025-26 conflated: FY2025-26 SCC composite ≈ 1.1636% (derived); FY2026-27 SF = 1.18162182% (official). Legacy mixed the two vintages ("FY25-26 rate 1.18268325%") — SF figure for FY2025-26 is not verified; FY2026-27 is. Flagged.
9. **Assumption drift across sites**: home appreciation 3.0–4.5%, SF 3.8%, Cupertino 4.0–4.5% vs FHFA 2026Q2 actual prints (CA −0.2% y/y, SF metro ≈ −2.4% y/y, 5-yr CA +17.3%). Canonical re-anchored to FHFA (P01) — flagged, not silently adopted.
10. **Verification hygiene**: "SCO no CA estate tax" was cited to a dead URL in the root mirror and docs; FTB "Programs" pages cited loosely; nerdwallet/policygenius industry figures presented next to official stats without separation labels. All canonical pages separate **verified / user-supplied / assumption / derived / unverified**.

## 4. What was done in this session (traceability)

- Claimed V2 (integration), B1 (black swans), B2 (repo review), B3 (privacy purge) in COORDINATION.md, commit pushed before content work.
- Canonical site: 13 pages at root (`index`, `properties`, `process`, `projections`, `scenarios`, `black-swan`, `estate-tax`, `taxes`, `costs`, `pending-changes`, `flagged`, `sources`, `methodology`) + `steps.html` redirect + `assets/site.css` + `downloads/inheritance-baseline-2026-2060.csv`.
- New analysis: 2045 inheritance quantified (A FMV $5,959,750 · FBYV $802,030 · Prop 19 cap $1,521,770 · live-in assessed $4,437,980 · taxes $7,360 → $53,320/$71,030 · B → $39,050 · estate headroom ≈ $14,863,690 @2045); terminal wealth 2060 across 7 regimes; estate-exclusion grid 2040–2060; 25 new flags (P01–P25); 23 carried (X01–X23).
- Repo-wide privacy purge executed and audited (`grep` gate in §6).

## 5. Live-link verification performed (2026-11-11)

| URL | Result |
|---|---|
| https://sftreasurer.org/property-tax (legacy) | **DEAD** — "Page Not Found" |
| https://www.sco.ca.gov/state_finances_estate_tax.html (legacy) | **DEAD** — "This page has been redesigned… not found" |
| https://sftreasurer.org/property/secured-property-taxes | **LIVE** — FY2026-27 rate **1.18162182%** verbatim |
| https://www.sco.ca.gov/ardtax_estate_tax.html | **LIVE** — "For decedents that die on or after January 1, 2005, there is no longer a requirement to file a California Estate Tax Return." |
| https://www.bls.gov/news.release/cpi.nr0.htm | Live archive (Sept 2026: 3.7% y/y, core 2.6%) |
| https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm | Live (hold 3.75–4.00%; two dissents preferred hike; next FOMC 2026-12-09) |
| https://www.fhfa.gov/document/d/hpi/fhfa-house-price-index-report-2026q2 | Live (CA −0.2% y/y; 5-yr +17.31%; SF metro ≈ −2.4%) |
| https://www.boe.ca.gov/prop19/ · lta25009.pdf · lta26026.pdf · /homeowners_exemption.htm | Live (LTA 2025/009 cap $1,044,586) |
| github.com PRs #1–#11 statuses | verified via `gh pr list` (all merged except #7 open/stale) |

Spot-checks not repeated for every link on legacy pages — legacy pages are superseded, not retired, and their failures are logged here.

## 6. Re-run the audits

```bash
# privacy gate: unrounded owner figures anywhere?
# The search pattern that stood here listed the unrounded figures themselves and was removed on 2026-11-11
# (session 8fc06844, K1). List the figures one per line in a file OUTSIDE the repository and run:
TINO1_PRIVATE_FIGURES=/path/outside/the/repository/figures.txt python3 final/check.py .
# expect: "unrounded owner figures: none found"
# every canonical HTML page reachable:
python3 -m http.server 8080  # then open /, /flagged.html, /black-swan.html, …
```

## 7. Flagged for the owner (not resolvable by any agent)

1. B2 — git-history erasure decision (`git filter-repo`).
2. A2 — whether to narrow Pages source away from `main:/`.
3. P09/P03/P07/P08/P16 — appraisals, insurance quotes, utility bills, NEM status, itemized tax bills (owner documents only).
4. P21 — marital status of the transferor (determines portability; single estates: no DSUE).
5. PR #7 disposition (merge/close) — if merged, diff vs canonical before adopting.
6. Which property carries the transferor’s Homeowners’ Exemption (determines which property Prop 19 can protect).

## 8. Bottom line

The repository contained real, good work — four parallel builds that mostly agreed on the law (step-up, Prop 19, $15M, no CA tax) and disagreed on tone and arithmetic. It also contained a live privacy breach (B1) now closed, and a broken-links patchwork now catalogued. The canonical site is self-consistent, privacy-clean, source-linked, regime-tested, and honest about what it cannot verify — which is the whole assignment.

---

# REPO REVIEW — second pass, 2026-11-13 (session `arena/46d1a561-tino1`)

The review above is kept exactly as written. This pass re-reads the repository as it stands
now and adds what has changed since. Method: whole-tree scans for owner-supplied figures,
direct reads of eight official agency URLs (recorded in
[`session-46d1a561/VERIFICATION.md`](session-46d1a561/VERIFICATION.md)), and a line-by-line
check of the generator, the publication boundary and the checkers.

## 1. What the earlier pass left open, and where it stands

| Earlier finding | Status now |
|---|---|
| A1 four overlapping sites | Still four directory trees in the repository (`docs/`, `site/`, `dashboard/`, `analysis/`), all excluded from the published site and all carrying a superseded notice. Nothing links to them from the current site. Kept by design; suggestion G02 asks the owner whether to delete them. |
| A2 Pages source is `main:/` | Unchanged. The whole repository is readable. `_config.yml` now excludes everything except the 31-file allowlist, so Pages serves only those; the rest is reachable through the repository itself. |
| B2 exact values in git history | **Still open, owner-only.** Now finding R61. No session can fix this without a destructive rewrite. |
| B3 ZIP codes published | Unchanged and intentional: the brief supplies both ZIP codes and asks for ZIP-level research. |
| §7.1–§7.6 owner documents | Unchanged. All remain blank on the site and listed on the Flagged page. |

## 2. New findings (published on `review.html` as R55–R61)

| # | Where | Finding | Severity | Status |
|---|---|---|---|---|
| R56 | `final/check.py` comments, `COORDINATION.md`, `owner-analysis-2026/FLAGS.md` | Four exact owner-supplied figures in clear text (Property A 2026 assessed value and 2025 bill, Property B assessed value, Property B 2025 bill), inside documentation describing the scan that is meant to catch exactly those figures. The repository is public. | **High** | Closed this session: documentation reworded, flag note rounded, full-tree sweep for all 45 owner values now returns none. |
| R57 | `final/published.txt`, `_config.yml` | Pages served 13 files. The 16-page rounded-figures analysis was built and checked in CI and never served, so the live site could not answer the brief. | **High** | Closed: allowlist is now 31 files. Recorded as option D of suggestion G01. |
| R55 | `README.md`, `final/README_ROOT.md`, `final/build.py`, `final/publish.py` | All four described the numeric edition as deliberately unpublished while the brief asks for it to be published with $10 rounding. The prose stated as fact a boundary that was recorded elsewhere as an open owner decision. | Medium | Closed. |
| R58 | root `index.html` | Front door was a single card with one button; the brief asks for a dashboard-style landing page with subpages organised by category. | Medium | Closed: dashboard front door with six headline figures and six category groups. |
| R59 | `privacy-site/check_published.py`, `privacy-site/test_illustrations.py` | Both hard-coded the 13-file set instead of reading `final/published.txt`, so the boundary could not be changed at all without breaking CI, and the root landing was forbidden by test from showing a dollar figure. | Medium | Closed: both derive from `final/published.txt`; guide-specific invariants kept. |
| R60 | every generated page | `noindex` present, but no referrer policy, so a click from a figure-bearing page to an official site sent the page address as a referrer. | Low | Closed and now enforced on every published file. |
| R61 | git history, superseded directories | Public history holds pre-rounding pages; `docs/`, `site/`, `dashboard/`, `analysis/`, `integrated/`, `legacy95/`, `verify-4395771d/` hold earlier figures. Excluding a directory from Pages removes nothing. | **Open, owner-only** | Recorded as G02 and privacy flag P02. |

## 3. Verification performed

- Eight official agency URLs opened and read in full: BOE LTA 2026/002, LTA 2025/009, LTA 2026/026, IRS Rev. Proc. 2026-35 §3.44, the IRS "what's new — estate and gift tax" page, the SF Treasurer secured-tax page, HUD FY2026 SAFMR for ZIP 95014, and the Santa Clara County FY2025-26 tax rate book.
- Three arithmetic checks done by hand: the Santa Clara rate components sum to 1.16360 (matches `rate_cup`); the Proposition 19 allowance roll-forward matches the biennial statutory rule; the BOE factor table matches `final/data/hist_prop13_factor.csv`.
- Whole-tree scan of all 45 owner-supplied figures (with and without thousands separators), covering every tracked file: no match remains.
- Gates: `final/check.py .` (25 pages, 1,011 table rows each with an official link, 2,630 links, 2,421 dollar figures rounded to $10, secretless 6-digit scan clean against 14,552 model numbers, model self-tests on 51 paths); `final/publish.py --check`; `final/check_published.py` and `privacy-site/check_published.py` against a rebuilt 31-file output; `privacy-site/check.py` (11 pages, 322 linked rows); `unittest` 9/9.
- Two matches in that scan were investigated and are **not** leaks: row-label years `2061`/`2066`, and two model outputs (`$6,130` in 2058, `$1,740` in 2057) that happen to equal four-digit owner tax bills.

## 4. Links for manual review

| Page | Purpose |
|---|---|
| https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf | Prop 13 inflation factor 2026-27 and the full factor table |
| https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf | Prop 19 allowance $1,044,586 and the every-other-February rule |
| https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf | Prop 19 FAQ, including the one-year residence rule and "no exceptions" |
| https://www.irs.gov/pub/irs-drop/rp-26-35.pdf | 2027 basic exclusion, section 3.44 |
| https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax | Public Law 119-21, $15,000,000 for 2026 |
| https://sftreasurer.org/property/secured-property-taxes | FY2026-27 rate 1.18162182% |
| https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026 | FY2026 SAFMRs for ZIP 95014 |
| https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf | Santa Clara County rate components |
