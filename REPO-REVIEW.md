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
TINO1_PRIVATE_FIGURES=/path/outside/the/repository/figures.txt python3 _d3c614ec/verify_all.py
# expect: "unrounded owner figures: none found" and zero 64-hex fingerprint hashes in-repo
# canonical & isolated Pages gates:
python3 privacy-site/check.py
python3 legacy95/check_legacy.py
python3 -m http.server 8080  # then open /, /flagged.html, /black-swan.html, …
```

## 7. Flagged for the owner (not resolvable by any agent)

1. B2 — git-history erasure decision (`git filter-repo`).
2. A2 — whether to narrow Pages source away from `main:/`.
3. P09/P03/P07/P08/P16 — appraisals, insurance quotes, utility bills, NEM status, itemized tax bills (owner documents only).
4. P21 — marital status of the transferor (determines portability; single estates: no DSUE).
5. PR #7 disposition (merge/close) — if merged, diff vs canonical before adopting.
6. Confirmation that the Transferor holds/qualifies for the Homeowners’ Exemption on Property A (Cupertino), since Property B (San Francisco) is already owned by the Inheritor and does not transfer at death.

## 8. Bottom line

The repository contained real, good work — four parallel builds that mostly agreed on the law (step-up, Prop 19, $15M, no CA tax) and disagreed on tone and arithmetic. It also contained a live privacy breach (B1) now closed, and a broken-links patchwork now catalogued. The canonical site is self-consistent, privacy-clean, source-linked, regime-tested, and honest about what it cannot verify — which is the whole assignment.

---

## 9. Follow-up whole-tree audit (2026-11-11, session `arena/d3c614ec-tino1` & `8fc06844`)

1. **Exact-figure & hash-table remediation (`8fc06844` PR #37 + `d3c614ec` `D3-1`):** `REPO-REVIEW.md` §6's literal regex, `final/data/privacy_fingerprints.txt` (reversible brute-forceable SHA-256 hashes over small integers), and 7 Python underscore-formatted literals in `model/project.py` and `model/verified_model_85899999.py` were removed/rounded to `$10`, and remaining non-`$10` comments in `model/verified_model_85899999.py` and `model/assumptions.md` were rounded. Zero hashes or encodings of owner figures are stored in `_d3c614ec/verify_all.py`.
2. **`model/**` Change-Request close-out (`d3c614ec` `D3-1`):** `model/project.py` and `model/assumptions.md` now close **CR-43-3** (San Francisco 3-unit Property B is already owned by the Inheritor and is never reassessed or stepped up at the Transferor's death), **CR-85-5** (ad valorem tax rate separated from fixed parcel charges + `$7,000` Homeowners' Exemption), and **CR-85-6** (CPUC 20-year NEM legacy period under `D.14-03-041` / `D.22-12-056`, PG&E `$24.15/mo` residential fixed charge under `D.24-05-028` / `Res. E-5354`, SF Rent Board `60%-of-CPI` cap, and `IRS Rev. Rul. 2023-2` irrevocable-trust basis sensitivity).
3. **Updated primary `.gov` checks (`2026-11-11`):**
   - **BLS CPI (`https://www.bls.gov/news.release/cpi.nr0.htm`):** Updated on `2026-11-10` (`USDL-26-1685`) to October 2026 (`CPI-U = 337.511`, `+0.4%` SA m/m; 12-month percent change omitted by BLS because October 2025 survey data were not collected during the 2025 appropriations lapse).
   - **IRS `Rev. Proc. 2026-35` (`https://www.irs.gov/pub/irs-drop/rp-26-35.pdf`):** Confirms 2027 basic exclusion `$15,480,000` (§ 3.44), 2027 annual gift exclusion `$20,000` (§ 3.46), and 2027 capital-gains / ordinary-income brackets (§§ 3.01, 3.03).
   - **SF Rent Board (`https://www.sf.gov/learn-about-rent-increases-san-francisco/`):** Confirms `1.6%` allowable increase (`2026-03-01` to `2027-02-28`) and flags the `2026-11-09` notice on pending Board of Supervisors File No. `261020` (proposed temporary `10%/yr` cap on combined banked + capital-improvement increases; not yet enacted).
   - **Santa Clara County Assessor (`https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2`):** Official page contains a stale post-2021 copy-paste irregularity under its Prop 19 parent-child bullets referencing age-55 replacement-home rules (`R&TC § 69.6`) and stating "adjusted annually" rather than biennially (`CA Const. art. XIII A § 2.1(c)(4)`, `BOE LTA 2025/009`); governing constitutional/statutory text controls and is flagged in `_d3c614ec/VERIFICATION-LEDGER.md`.
   - **Historical Git commits (`B2`):** Remains a repository-owner action (`git filter-repo` + force-push or setting repository visibility to private), as branch commits cannot rewrite merged `main` history without rewriting history.
