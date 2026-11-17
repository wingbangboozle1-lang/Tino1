# Two-home inheritance analysis

**Live site:** https://wingbangboozle1-lang.github.io/Tino1/

A decision analysis for two California homes. Property A (the future inherited home) will pass to the Inheritor through a trust around 2040 to 2050. Property B (the home already owned) is not part of the inheritance. The site answers one question with numbers: live in Property A, rent it out, or sell it and reinvest. City, ZIP code and parcel identifiers are deliberately omitted from this front page.

## What is current

GitHub Pages publishes the **rounded-figures analysis** at the repository root, generated from [`final/`](final/), behind a dashboard landing page. The **no-figures guide** in [`privacy-site/public/`](privacy-site/public/) is published alongside it, one click away, for anyone who wants the process with invented teaching examples instead of household numbers. The exact published file list is pinned in [`final/published.txt`](final/published.txt) and enforced in CI.

Rounding to the nearest $10 is the disclosure-minimisation control the brief asks for; it is **not** anonymisation, and this repository is public. Options G01 and G02 on the Suggestions page set out the narrower boundary and the history remediation; only the owner can make the repository private or have its history rewritten. Pages:

| Page | Content |
|---|---|
| `index.html` | The published front door: a dashboard grouping every page by category, with the headline numbers and a link to the no-figures guide |
| `summary.html` | Executive summary, dashboard, best plan and why (rounded-figures numeric edition) |
| `decision.html` | Live, rent or sell: cash flows, after-tax wealth, sensitivities, break-even points |
| `questions.html` | Questions, known vs. unknown info, and discovery guide — Part 1: Q01–Q18, U01–U10, the S5-Q1–S5-Q7 evidence checklist & discovery sequence; Part 2: reading-dated decision register (open, unknowable, answered) |
| `projections.html` | Year by year 2026 to 2076: value, assessed value, property tax, insurance, water, electricity, repairs, rental insurance |
| `black-swan.html` | Non-constant growth and inflation: 50 replays of the real 1976-2025 record, named crisis paths, and a phased-entry test that parks the sale proceeds in 3-month to 2-year Treasuries for 24 to 36 months before phasing into stocks (1929 and 2008 crash entries), with a provenance table separating official statistics, academic returns and hypothetical constructions |
| `process.html` | Step-by-step process with legal deadlines (`BOE-266` before `BOE-19-P` per BOE Pub. 800-1) |
| `law.html` | Federal, California (`Behavioral Health Services Tax`), and local law in force, plus pending measures & Nov 11 ballot updates |
| `estate-cash.html` | Cash inheritance: thresholds at each level, room before tax, projections |
| `costs.html` | Insurance for both ZIP codes and running costs (CPUC NEM / `$24.15` fixed charge, water, rent) |
| `suggestions.html` | Proposed site, data & privacy improvements to review before implementing — Part 1: GAP/IMP/Paths; Part 2: options register G01–G15 |
| `flagged.html` | Flagged for Review: every unconfirmed value, assumption and irregularity, with links |
| `sources.html` | Source register (zero official `excerpt` sources remain), method, cross-check against a second model |
| `verification.html` | Verification passes (2026-11-11, 2026-11-12 and 2026-11-13): every official agency source opened and read directly |
| `requirements.html` | Every part of the brief, the page that answers it, the official pages re-read, and `SG-1`–`SG-11` queue |
| `review.html` | Repository review findings (`R01`–`R54`) |
| `versions.html` | Earlier editions and why they were replaced |

## Reproduce

```
python3 final/model.py && python3 final/integrate.py && python3 final/check.py .
```

Standard library only. `final/check.py` fails if a table row has no link to an official page, if an internal link is broken, if a dollar figure is not a multiple of $10 (listed official figures excepted), if a git merge-conflict marker survives anywhere, or if a street address, e-mail address, parcel-number or telephone pattern appears. GitHub Pages serves exactly the allowlist in [`final/published.txt`](final/published.txt) (the rounded-figures analysis plus the no-figures guide), enforced against the real Jekyll output in CI by `final/check_published.py` and `privacy-site/check_published.py`.

## Rules followed

- **Privacy first.** No names, addresses or parcel numbers. People are "the Transferor" and "the Inheritor". Properties are "Property A" (Cupertino) and "Property B" (San Francisco). Owner-supplied figures are stored and shown only rounded to $10; no year-by-year history is listed. Pages ask search engines not to index them and set `no-referrer`.
- **Official sources.** Every table row links to an official page. A value that could not be confirmed is left blank and listed on the Flagged for Review page. Assumptions are labelled as assumptions.
- **Not advice.** The site prepares questions for a licensed estate attorney and tax adviser.

## Not current

Earlier editions (`archive/`, `dashboard/`, `docs/`, `site/`) are kept for the record. Each page carries a notice pointing to the current site. See `versions.html`. An independent second model is in [`verify-4395771d/`](verify-4395771d/); it is a check, not a second front door.

## Owner action still needed for full privacy

This repository is public, and its Git history contains the first versions of the pages, written before the figures were rounded. Rounding the current pages does not remove that history. Only the owner can make the repository private or have the history rewritten.

## Coordination

Work sessions, claims, change requests and merge records are in [`COORDINATION.md`](COORDINATION.md).

---

## History: README of the earlier editions (kept unchanged except for two corrected source links)

### Inheritance decision guide

**Public guide:** <https://wingbangboozle1-lang.github.io/Tino1/>

**Decision frame:** Property A is expected to transfer in the future; Property B is already owned by the inheritor.

**Status:** The public guide is a privacy-limited reference, not a household-specific recommendation.

This project organizes the questions, evidence and decision gates for comparing living in, renting or selling a future inherited home. The already-owned home is the baseline; count only changes actually caused by the inheritance. The public guide deliberately withholds property-specific values, rents, assessments, operating costs and derived forecasts. Unknowns remain blank or explicitly illustrative.

The public front page now states the decision status and the facts most likely to change an answer: trust/title and eligibility, basis/valuation and same-year sale taxes, estate liquidity/prior gifts/portability, verified rent and costs, and a documented investment-risk policy. See the [questions checklist](https://wingbangboozle1-lang.github.io/Tino1/privacy-site/public/questions.html), [suggestions for review](https://wingbangboozle1-lang.github.io/Tino1/privacy-site/public/suggestions.html), and the [printable Attorney & CPA briefing sheet](https://wingbangboozle1-lang.github.io/Tino1/privacy-site/public/brief.html).

## Public publication boundary

GitHub Pages publishes only the root `index.html` and the 16-file guide under `privacy-site/public/` (15 HTML pages plus one stylesheet). The exact 17-file allowlist is in [`final/published.txt`](final/published.txt), generated and checked by [`final/publish.py`](final/publish.py), and verified against Jekyll output in CI. The public guide uses independently labeled synthetic examples; they are not missing household values or recommendations. See [`privacy-site/README.md`](privacy-site/README.md) for the generator, source and test boundaries.

The guide includes an executive overview, same-horizon decision framework, synthetic projections and stress examples, a staged-entry page tested on real annual history with official Federal Reserve cash legs, transfer process and deadline timeline, current-rule references, operating-cost evidence checklist, questions, review-only suggestions, a glossary, and a one-page printable adviser brief that ends with a dated decision record. The navigation is grouped into four labelled sections. The Black swan page now carries a seeded outcome-percentile band beside every single-point figure, so a median and a 10th percentile are visible next to the familiar compounding result. The 2026 SALT cap is cited to the IRS correction page for Form 1040-ES; the 2027–2029 amounts are labelled arithmetic on the statute because no IRS page read here states them. Each public data row links to official context; a source link does not verify a private property fact or turn an assumption into an official forecast. Legal rules and local processes must be rechecked at the actual transfer date.

## Critical privacy notice — Pages are not repository access control

**The GitHub repository is public.** The Pages allowlist limits what the website serves; it does not hide excluded repository files. The repository contains household-derived working analysis, and its Git history includes earlier pre-rounding material. Rounding to the nearest $10 is disclosure minimization, not anonymization. Do not treat this repository, its history, branches, pull-request diffs, or its public website as a confidential workspace. Do not add names, addresses, parcel identifiers, bills, account data, exact balances, or completed adviser worksheets.

This session verified the current public Pages boundary, but did **not** make the repository private, delete remote branches, or rewrite shared Git history. A normal pull request cannot erase old commits, forks, clones, or cached pull-request views. GitHub’s [official sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) describes the coordinated history rewrite, cleanup of other clones/forks, risks to branches and pull requests, and the need to contact GitHub Support about cached views and pull-request references. Any full purge is a repository-owner operation that must account for every affected branch/tag/ref and coordinate collaborators; changing visibility may also affect Pages, so check the hosting plan and desired public-site behavior first. No claim that historical exposure has been contained or erased is made here.

For a household-specific model, use a separately access-controlled workspace with an independent security review. Keep evidence with trusted advisers, not in a public issue, pull request, Pages form, or this repository.

## Build and verify

From the repository root:

```sh
python3 privacy-site/build.py
python3 privacy-site/check.py
python3 -m unittest discover -s privacy-site -p 'test_*.py' -v
python3 final/publish.py --check
python3 final/check.py .
jekyll build --trace
python3 final/check_published.py _site
python3 privacy-site/check_published.py _site
```

The Pages checks enforce the allowlist, internal links, reviewed source links, visible-dollar rounding for synthetic/legal amounts, and several common privacy signatures. They are not a complete privacy audit, a proof of anonymity, or a scan of all data reachable in Git history. The numeric model and its tests are repository content, not private merely because Pages excludes them.

## Coordination and review

`COORDINATION.md` is the shared task/verification ledger, including open evidence gaps and repository-privacy actions. `privacy-site/public/flagged.html` lists items that remain unverified or limited. Suggestions are review-only; none are automatically implemented by the website. No legal, tax, investment or insurance advice is provided.

