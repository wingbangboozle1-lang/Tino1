# S7 independent public-output and privacy-boundary audit

**Audit date:** 2026-11-13 UTC  
**Integration PR:** [#89](https://github.com/wingbangboozle1-lang/Tino1/pull/89), merged as `1ac58155541a82bf29bafa51e6e2c1ca7e5027f5`  
**Current Pages snapshot checked:** `d19d34654c5928524b384680bd2c817503278a22` (Pages API: `built`, no error)  
**Scope:** the figure-free public guide and its generated Pages output; this is not a complete privacy audit of all repository contents or Git history.

## Findings

- The public guide uses a generic decision framework. No household values, location, identity, address, lease text, assessment history, or private documents were added in this pass.
- The executive baseline includes only a generic, owner-supplied note to hold existing occupancy/rental continuity constant in comparisons. It is expressly unverified and does not establish tenancy, legal-unit status, title, or an occupancy fact.
- The personal SALT row now links to [Public Law 119-21 §70120](https://www.congress.gov/bill/119th-congress/house-bill/1/text) for the enacted schedule: $40,000 for 2025; $40,400 for 2026; 101% increases for 2027–2029; and $10,000 after 2029 under current law. For 2025–2029, the cap phases down by 30% of modified AGI above the indexed threshold, but not below $10,000; MFS amounts are half. The row distinguishes the individual Schedule A itemized limit from property-specific rental-tax calculations. The linked [2025 IRS Schedule A instructions](https://www.irs.gov/instructions/i1040sca) are scoped to 2025 and are not presented as authority for later-year amounts.
- No publication-boundary expansion was made. The 14-file output allowlist remained unchanged; this audit note is excluded from Jekyll output by the generated `_config.yml`.

## Pages allowlist checked

`final/published.txt` at the time of this audit declares exactly these 14 files:

```text
index.html
privacy-site/public/costs.html
privacy-site/public/decision.html
privacy-site/public/flagged.html
privacy-site/public/index.html
privacy-site/public/issues.html
privacy-site/public/law.html
privacy-site/public/process.html
privacy-site/public/projection.html
privacy-site/public/questions.html
privacy-site/public/stress.html
privacy-site/public/style.css
privacy-site/public/suggestions-detail.html
privacy-site/public/suggestions.html
```

The PR `verify` workflow installed GitHub Pages/Jekyll, built actual `_site`, and passed both `final/check_published.py` and `privacy-site/check_published.py`. On PR head `fad8abd7a87834b89aa444e23be933b35c0e5528`, run `43422616028` passed; the workflow reported 14 emitted files and one builder output compared. The subsequent main-branch `verify` on merge commit `1ac5815` (run `43422853989`) and GitHub Pages deployment (run `43422853000`) also passed.

## Reproducible checks

At the rebased current base, local checks reported:

- `python3 privacy-site/build.py`: 12 pages built; no private inputs read.
- `python3 privacy-site/check.py`: 383 official-context-linked rows; anchors, local resources, PII-pattern checks, $10 display rounding, and known-signature checks passed.
- `python3 -m unittest discover -s privacy-site -p 'test_*.py' -v`: 12/12 passed.
- `python3 final/publish.py --check`: `_config.yml` and `final/published.txt` matched the 14-file allowlist.
- `python3 final/check.py .`: 25 pages, 1,010 linked rows, 2,572 links, 2,469 rounded dollar figures, 14,552 model numbers in the secretless scan, and 51 model paths passed.
- The separate private-figure-list scan reported **SKIPPED** because `TINO1_PRIVATE_FIGURES` was not set. Do not interpret the checks above as a complete secret scan or whole-repository privacy certification.

## Post-merge live check and limits

After deployment, the Pages API reported `built` for `d19d34654c5928524b384680bd2c817503278a22`, with no error. The live [Tax & law page](https://wingbangboozle1-lang.github.io/Tino1/privacy-site/public/law.html) showed the new statutory SALT row, and the live [Overview page](https://wingbangboozle1-lang.github.io/Tino1/privacy-site/public/index.html) showed only the generic, explicitly unverified baseline note. These checks confirm the figure-free guide content at that deployment; they do not establish facts about a household.

The repository remains public. A Pages allowlist does not protect other tracked files, prior history, clones, caches, or third-party copies. No repository-visibility change or history rewrite was performed or authorized here. At audit close, separate open PRs #91 and #92 proposed numeric-edition changes; they are outside this audit and this merge does not approve their publication-boundary effects. Reassess the exact emitted output and privacy implications before merging any separate proposal that changes the allowlist.
