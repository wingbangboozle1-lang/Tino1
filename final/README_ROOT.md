# Two-home inheritance analysis

**Live site:** https://wingbangboozle1-lang.github.io/Tino1/

A decision analysis for two California homes. Property A (the future inherited home) will pass to the Inheritor through a trust around 2040 to 2050. Property B (the home already owned) is not part of the inheritance. The site answers one question with numbers: live in Property A, rent it out, or sell it and reinvest. City, ZIP code and parcel identifiers are deliberately omitted from this front page.

## What is current

GitHub Pages publishes the **rounded-figures decision dashboard** at the repository root, generated from [`final/`](final/), together with the **no-figures guide** in [`privacy-site/public/`](privacy-site/public/) (every illustration invented for teaching; the exact file list is pinned in [`final/published.txt`](final/published.txt)). This boundary resolves owner questions G01 and G02 in the owner's favour: the owner brief of 2026-11-13 requires the figures in the decision analysis "to provide clarity", and $10 rounding, placeholders for people and document identifiers, `noindex` and `no-referrer` are disclosure minimisation, labelled as such on every page (PR #94, 2026-11-13). Pages:

| Page | Content |
|---|---|
| `index.html` | The published front door: the decision dashboard landing, linking every section and the no-figures guide |
| `summary.html` | Executive summary, dashboard, best plan and why (rounded-figures numeric edition) |
| `decision.html` | Live, rent or sell: cash flows, after-tax wealth, sensitivities, break-even points |
| `questions.html` | Questions, known vs. unknown info, and discovery guide — Part 1: Q01–Q18, U01–U10, the S5-Q1–S5-Q7 evidence checklist & discovery sequence; Part 2: reading-dated decision register (open, unknowable, answered) |
| `projections.html` | Year by year 2026 to 2076: value, assessed value, property tax, insurance, water, electricity, repairs, rental insurance |
| `black-swan.html` | Non-constant growth and inflation: 50 replays of the real 1976-2025 record and named crisis paths, with a provenance table separating official statistics, academic returns and hypothetical constructions |
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

Standard library only. `final/check.py` fails if a table row has no link to an official page, if an internal link is broken, if a dollar figure is not a multiple of $10 (listed official figures excepted), or if a street address, e-mail address, parcel-number or telephone pattern appears. GitHub Pages serves the reviewed allowlist in [`final/published.txt`](final/published.txt) (decision dashboard + no-figures guide), enforced in CI by `final/check_published.py` and `privacy-site/check_published.py`.

## Rules followed

- **Privacy first.** No names, addresses or parcel numbers. People are "the Transferor" and "the Inheritor". Owner-supplied figures are stored and shown only rounded to $10 and labelled owner-supplied (flag P03); the recorded tax and assessment history appears only in that rounded form. Pages ask search engines not to index them.
- **Official sources.** Every table row links to an official page. A value that could not be confirmed is left blank and listed on the Flagged for Review page. Assumptions are labelled as assumptions.
- **Not advice.** The site prepares questions for a licensed estate attorney and tax adviser.

## Not current

Earlier editions (`archive/`, `dashboard/`, `docs/`, `site/`) are kept for the record. Each page carries a notice pointing to the current site. See `versions.html`. An independent second model is in [`verify-4395771d/`](verify-4395771d/); it is a check, not a second front door.

## Owner action still needed for full privacy

This repository is public, and its Git history contains the first versions of the pages, written before the figures were rounded. Rounding the current pages does not remove that history. Only the owner can make the repository private or have the history rewritten.

## Coordination

Work sessions, claims, change requests and merge records are in [`COORDINATION.md`](COORDINATION.md).
