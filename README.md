# Privacy-first inheritance decision guide

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
