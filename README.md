# Inheritance decision guide

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
