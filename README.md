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
| `black-swan.html` | Non-constant growth and inflation: 50 replays of the real 1976-2025 record and named crisis paths, with a provenance table separating official statistics, academic returns and hypothetical constructions |
| `process.html` | Step-by-step process with legal deadlines (`BOE-266` before `BOE-19-P` per BOE Pub. 800-1) |
| `law.html` | Federal, California (`Behavioral Health Services Tax`), and local law in force, plus pending measures & Nov 11 ballot updates |
| `estate-cash.html` | Cash inheritance: thresholds at each level, room before tax, projections |
| `costs.html` | Insurance for both ZIP codes and running costs (CPUC NEM / `$24.15` fixed charge, water, rent) |
| `suggestions.html` | Proposed site, data & privacy improvements to review before implementing — Part 1: GAP/IMP/Paths; Part 2: options register G01–G15; review controls now cover nine proposals |
| `issues.html` | **Published guide page.** Every open question this analysis found (I01–I24): what is unresolved, what would close it, and the official context. Blank means unverified, never zero |
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

## Verification in this edition (session bd0afb0a)

Every substantive claim published in `privacy-site/public/` was re-read on its official page on 2026-11-13 and logged
claim by claim in [`session-bd0afb0a/VERIFICATION.md`](session-bd0afb0a/VERIFICATION.md). Three published statements did not
survive that re-read and were corrected:

- a ballot percentage that did not match the Secretary of State's returns page (now 52.4%, with the current timestamp and
  precinct count; still unofficial until certification);
- a 2026 personal state-and-local-tax amount asserted from a link that only supports the 2025 amount (the row now states
  only what the linked IRS instructions say, and the gap is flagged as P10);
- a rename label applied to the 1% California additional tax that the linked FTB page did not confirm (the row now cites
  Revenue and Taxation Code section 17043 only, flagged as P12).

Four additions came out of the same pass: an executive summary on the landing page, an explicit baseline table separating
the already-owned home from the inherited home, six ordered decision gates on the Open questions page, and an official
BLS CPI-U decade table on the Black swan page showing why a single constant inflation rate is not a baseline (P13).

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

### Privacy-first inheritance decision guide

**Public site:** <https://wingbangboozle1-lang.github.io/Tino1/>

A general decision guide for a future trust inheritance when the beneficiary already owns a separate home. It explains the legal process, the questions to resolve, the operating-cost evidence to collect, and the choices to compare. The public Pages edition uses generic property placeholders and fictional examples; it does not publish household-specific values, tax histories, rents, utility bills or forecasts.

## What the public site contains

- **Overview:** conditional decision framework and the distinction between the future inheritance and the already-owned home.
- **Decision:** live, rent and sell/reinvest gates; a clearly labeled fictional teaching example.
- **Projections:** synthetic annual calculations only; actual household forecast fields are blank.
- **Black swan:** official macroeconomic context plus explicitly invented stress paths, not predictions or probabilities.
- **Process:** trust-administration steps, filing clocks and legal cautions.
- **Tax & law:** current federal and California rules; future thresholds, local charges and eligibility are not treated as known.
- **Costs:** insurance, water, energy, maintenance and property-tax items with no verified household prices filled in.
- **Questions:** known legal context, unanswered household facts and ways to verify them privately.
- **Suggestions:** review-only proposals with local Adopt / Hold / Reject radio controls and a path selector. No form or site code stores, submits or transmits selections; the controls do not implement choices.
- **Flagged for Review:** unverified items, source limitations and privacy risks.

The public allowlist is intentionally limited to the generic root landing page and `privacy-site/public/`. `final/publish.py --check`, the two published-output checkers, the site privacy gate and the GitHub Actions workflow verify that Jekyll emits no extra file. Noindex is only a request to search engines; it is not access control.

## Critical privacy warning

**The GitHub repository itself is public.** Excluding files from GitHub Pages does not hide those files from repository visitors, and it does not erase commits, pull-request references, forks, caches or prior deployments. The repository currently contains household-derived analysis outside the public Pages edition, and its history may contain still earlier material. Rounding to `$10` is disclosure minimization, not anonymization. Do not treat this repository or its history as private. No account-level visibility change or destructive history rewrite was performed by this work because either could affect the live site and retained references.

Keep deeds, statements, bills, account details, names, addresses and exact balances out of this public repository. If a secure household-specific model is required, it needs a separately access-controlled location and an independent security review. Repository visibility/history remediation remains an owner-level action; see the public site's **Flagged for Review** page.

## Rebuild and verify

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

The public-guide generator reads only `privacy-site/research.json` and `privacy-site/illustrations.py`; its examples are not household projections. `final/check.py` also validates the separate, non-Pages numeric analysis stored in the public repository. The latter is not a privacy boundary or a public recommendation. Consult qualified estate counsel, a tax professional and an insurance adviser before acting; this guide is not legal, tax, investment or insurance advice.

