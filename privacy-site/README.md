# Isolated public guide

## Boundary and privacy

The only Pages deliverables are the generic root landing page and the twelve files (eleven HTML pages plus CSS) in `public/`. `_config.yml` excludes prior numeric editions, all model/data/research files, this README and tests. CI builds with GitHub Pages Jekyll and `check_published.py` fails on **any** unexpected output file or changed byte. It uses a fixed allowlist, not files discovered at runtime.

The public generator reads only the reviewed official-source registry (`research.json`) and independent synthetic teaching model (`illustrations.py`). It does **not** import earlier models, owner values, tax histories, ZIP codes, rents or utility amounts. Those amounts and household-derived forecasts remain blank. It also withholds city names and city-specific tax/rent figures because they could associate the guide with the household; local rates, coverage and fees must be confirmed privately. The public site has no JavaScript, submitting forms, trackers, remote resources or uploads. The Suggestions page has radio-only review controls with no site-controlled storage, submission or transmission. A restrictive CSP and no-referrer policy are embedded. Noindex is a request to crawlers, not confidentiality or access control. Hosting access logs, old Git files, history, forks and caches are not removed by this work. The repository is a separate exposure surface; this is not a promise that old public information is erased.

## Evidence

Most official passages were read on 2026-11-12; selected high-impact sources and the new water-system lookup were re-read on 2026-11-13, with per-source dates in `research.json`. The Flagged for Review page publishes the bounded source register and rejected error pages. Every data row has an official-context link. Links support the cited rule/concept, **not** private facts, assumptions or forecast returns. This distinction appears in captions and page prose. Prior claims of whole-repository line-by-line verification have not been reproduced and are not adopted here.

## Examples

`illustrations.py` contains unrelated round-number examples chosen to teach compounding, assessed value, reassessment, expenses, after-tax rent/sale comparisons and inflation/regime risk. All rates and cost inputs are assumptions, labeled as such. No return is guaranteed, no odds are assigned, and the stresses are not called historical replays. The 2027 IRS exclusion is a published official amount; later amounts in the sensitivity table are explicitly hypothetical, not a statutory indexing implementation. The fictional fixed family-home allowance in the annual example is **not** the actual legal allowance.

Dollar outputs round half away from zero to $10 only at display; calculations retain precision. All terminal wealth comparisons use the same horizon and liquidated after-tax framework. B's common property/income and estate costs are excluded from both sides, not counted as new benefits. Live-in utility is not assigned an invented monetary benefit. Simplified depreciation, effective tax rates and ignored loss carryovers/capital-work depreciation are prominent limitations.

## Run

```sh
python3 privacy-site/build.py
python3 privacy-site/check.py
python3 -m unittest discover -s privacy-site -p 'test_*.py' -v
# With the GitHub Pages Ruby gem installed (CI):
jekyll build
python3 privacy-site/check_published.py _site
```

Tests cover branch boundaries for family assessment, three transfer dates, annual series and real values, half-dollar rounding behavior, an independently checked first-year rent cash bridge, investment crash invariance without withdrawals, sensitivity directions, reproducibility, and failure on unexpected/modified published files. Python checks use explicit exceptions in normal execution; do not invoke with optimization (`-O`), which removes assertions. CI uses the ordinary interpreter. External URL health cannot be continuously guaranteed; official sources can move after the audit.

## What remains unresolved

Actual future costs/returns, private estate headroom, property-specific insurance quotes, an exhaustive local fee/pending-law review, occupancy/relationship/title/trust facts and a proven personalized optimal plan. These remain publicly flagged rather than being silently filled in. Public Git history/privacy remediation is not completed by the Pages allowlist.
