# Independent decision review — session arena/5ea93a0e-tino1

Checked: 2026-11-12 UTC. This is a source-only review pack, excluded from GitHub Pages. It does not republish household figures, historical series, ZIPs or private documents. Evidence passages are in `SOURCES.md`; code/model/privacy findings are in `AUDIT.md`.

## Executive finding

Under the current numeric model's assumptions, selling Property A at inheritance and reinvesting leads terminal after-tax wealth, followed by renting, then living in it. Removing the inferred rent for the vacated third unit of Property B does not change that terminal ranking. The result is **not** a verified personalized recommendation: trust/basis treatment, occupancy intent, lawful rentable condition, actual rents, insurance, liquidity needs and investment risk tolerance are unresolved.

The ranking is assumption-sensitive in important ways. Proceeds kept only in savings/T-bills favor renting over selling in the current model. The Depression and Japan stress overlays also favor renting at the terminal horizon. A lower stock-return assumption narrows the sell lead; a 60/40 mix narrows it further than the all-equity baseline but still leaves sell first in the tested run. These are model comparisons, not forecasts.

The public privacy-first guide is structurally green and excludes the numeric root pages. That protects the current Pages surface, not the public repository or Git history. The original request for rounded decision numbers on the public site is therefore only partially satisfied: the public guide uses synthetic illustrations, while the household-derived numeric edition remains source-only. Any future public numeric edition must be rebuilt privacy-safe and provenance-labeled; do not simply expose the existing root pages.

## Requirements coverage

| Requirement | Current coverage | Gap / required treatment |
|---|---|---|
| Live vs rent vs sell comparison | `final/model.py`, `decision.html`, `summary.html`; privacy guide has a synthetic decision page. | Numeric baseline counts inferred third-unit rent and treats HUD SAFMR as property rent. Correct provenance before publication; keep owner decision gates visible. |
| Year-by-year projections and rounded costs | Numeric edition covers 2026–2076 and $10 display rounding. | Excluded from Pages; rounding is not anonymization. Do not republish exact or rounded historical assessment/bill series. |
| Federal/state/local tax and trust process | `law.html`, `process.html`, `estate-cash.html`, privacy guide equivalents; official passages in `SOURCES.md`. | Future law unknown; estate headroom is conditional; trust inclusion, basis, depreciation and passive-loss facts require private records. |
| Official source for every verified row | Checkers enforce an official-context link per row. | A link is not cell-level verification. Label verified rule, owner input, assumption, model output or unverified blank separately. |
| Insurance, utilities, market context | CDI/CPUC/PG&E/SFPUC/HUD/FHFA/FRED/BOE sources read; owner estimates flagged. | No property-specific quote, meter/usage facts, retailer confirmation or appraisal. San José/Valley Water charges are context, not automatic household inputs. |
| Black-swan / variable economy | 50 historical-sequence replays, named overlays, sensitivities and break-evens in `final/model.py`. | Equity/bond series are academic, not official; assessment replays use national CPI rather than California CCPI; Japan bond/cash paths are assumptions. Label or replace before claiming verification. |
| Questions and missing information | `questions.html`, privacy `questions.html`/`suggestions-detail.html`, flags Q/U/D registers. | Keep answers blank where private evidence is missing; discovery must happen privately, not through public uploads or parcel lookups. |
| Suggestions before implementation | `suggestions.html`, `requirements.html`, privacy suggestions pages; review queue SG/GAP/IMP items. | Proposals are not owner choices. This pack adds review-only S5 proposals below; none changes shared generators. |
| Privacy and publication boundary | Root redirect + 12 privacy-site files; exact allowlist checker; locality/signature guards. | Public repo/history exposure remains unresolved (P01/P02). PR #69 would reverse the boundary; do not merge while conflicting/unverified. |
| Final integration and deploy | This branch rebased on main `536ee03`; checks green locally; one `_config.yml` exclusion added for this audit directory. | PR/CI/Pages verification still required. Preserve other sessions' work; merge only green. |

## Evidence questions to resolve privately

These use S5 identifiers to avoid colliding with existing D/Q/U registers.

| ID | Question | Known / missing | Private discovery route |
|---|---|---|---|
| S5-Q1 | Will Property A be included in the Transferor's gross estate, and what is the resulting basis? | Trust type, title, powers and estate inclusion unknown. Basis reset is the largest legal swing factor. | Estate attorney reviews trust/title; tax adviser documents inclusion and date-of-death valuation. See V03–V05. |
| S5-Q2 | Does the Inheritor intend to occupy Property A within one year and keep it as principal residence? | Relationship, transferor occupancy, transferee occupancy and exemption status unknown. | Owner decision plus counsel/assessor confirmation; BOE-266 and BOE-19-P workflow. See V08–V10. |
| S5-Q3 | What is the lawful, rentable condition and market rent of Property A and the vacated third unit of Property B? | Bedroom count, permits, leases, rent-control coverage and third-unit rent unknown. HUD is only a benchmark. | Private inspection, leases, property-manager rent opinion, local rent-board coverage check. Do not infer rent from another unit. |
| S5-Q4 | What are the actual utility accounts, meter sizes, usage, retailer and tax-roll charges? | SFPUC tariffs are verified; household class/bill is not. Property A retailer and whether storm charges are already on the tax bill are unknown. | Read bills privately; confirm retailer/service area and account class with the utility. Avoid double counting V35–V37. |
| S5-Q5 | What insurance is available and at what price? | Owner estimates only; CDI averages/tool scenarios are not quotes. Earthquake coverage unknown. | Obtain comparable homeowner, landlord/mixed-occupancy and earthquake quotes privately. See V23–V26. |
| S5-Q6 | What is the full estate inventory and liquidity need? | Other assets, debts, deductions, prior gifts, retirement accounts, portability and cash needs unknown. | Executor/tax adviser prepare confidential inventory and Form 706 analysis. See V01/V02/V05. |
| S5-Q7 | What investment mix and loss tolerance apply to sale proceeds? | No official forecast of equity returns; allocation is an owner choice. | Read SEC allocation guidance, choose mix with adviser, rerun sensitivities. T-bill-only and 60/40 cases materially change the comparison. |

## Review-only suggestions

No item below is implemented by this session. Shared generators and public pages are unchanged except the one publication-boundary exclusion needed to keep this audit directory out of Jekyll.

| ID | Proposal | Why | Decision needed |
|---|---|---|---|
| S5-P1 | Remove inferred third-unit rent from the numeric baseline; show leasing upside only as an explicit scenario. | The brief supplies no third-unit rent and says never infer. | Owner/reviewer approves correction; model owner regenerates numeric pages. |
| S5-P2 | Relabel HUD SAFMR as a benchmark and add bedroom/condition gates. | Official benchmark ≠ verified property rent. | Obtain private rent opinion before treating any figure as property-specific. |
| S5-P3 | Use BOE California CCPI factors for Prop 13 indexing where verified; otherwise label national CPI as a proxy. | Statutory indexing differs from national CPI, especially in replays. | Model owner chooses verified-factor replacement or explicit proxy label. |
| S5-P4 | Separate official data, academic return series and hypothetical stress paths in the black-swan pages. | Academic returns cannot be presented as officially verified. | Reviewer approves provenance labels or replacement paths. |
| S5-P5 | Generate Suggestions Part 1 figures from `model.json` instead of hand-typed literals. | Current figures match after rounding but are drift-prone. | Model/build owner implements after active claims resolve. |
| S5-P6 | Keep the privacy-first front door until a privacy-safe rounded numeric edition is reviewed. | Existing numeric pages contain ZIP/locality cues and household-derived outputs; PR #69 would reverse the boundary without green checks. | Owner decides G01/G02 and repository/history remediation; do not merge conflicting dual-edition routing. |
| S5-P7 | Treat repository visibility/history cleanup as urgent owner action. | Pages exclusion and noindex are not access control; clones/forks/caches may persist. | Owner chooses private repo, history rewrite and GitHub Support cleanup; coordinate before destructive rewrite. |

## Variable-economy method and bounded results

`recheck.py` imports `final/model.py` read-only and prints rankings/counts only. It does not write `final/out/model.json`, regenerate pages or emit household dollar totals.

- One-at-a-time variants tested: no inferred third-unit rent; HUD 3BR benchmark; rent benchmark +30%; insurance ×3; maintenance ×2; vacancy 10%/15%; management 10%; stocks 5%; 60/40; T-bills; no basis step-up; transfer 2040/2050.
- Terminal ranking remains sell > rent > live in every variant except T-bill-only proceeds, which ranks rent > live > sell.
- With inferred third-unit rent removed, the 50 wrapped 1976–2025 sequences still end with sell first in 50/50 cases; sell leads 43/50 at ten years and 50/50 at twenty years.
- Named overlays with the same correction: crash, stagflation, lost decade and California slump favor sell; Depression and Japan favor rent at the terminal horizon.
- Limitations: these replays inherit the model's national-CPI Prop 13 proxy, academic equity/bond returns, Japan price-only equity series and assumed bond/cash behavior. CBO's official outlook (V38) covers 2026–2036 only and uses PCE inflation; it is context, not a 50-year household forecast.

Reproduce:

```sh
python3 session-5ea93a0e/recheck.py
python3 final/check.py .
python3 privacy-site/build.py
git diff --exit-code -- privacy-site/public
python3 privacy-site/check.py
python3 -m unittest discover -s privacy-site -p 'test_*.py' -v
python3 final/publish.py --check
```

The real Jekyll build and `privacy-site/check_published.py _site` must run in CI; Ruby/Jekyll are not installed in this sandbox.
