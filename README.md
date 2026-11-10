# Cupertino + San Francisco Inherited-Property Decision Analysis

A source-verified financial analysis of whether to **live in**, **rent out**, or **sell** a
Cupertino home inherited through a trust around 2040–2050, given a second rent-controlled
San Francisco property that passes to the same heirs.

## Live site

**https://wingbangboozle1-lang.github.io/Tino1/**

## Headline conclusions

| Question | Answer |
|---|---|
| Is there an inheritance tax? | **No.** California prohibits inheritance, estate and gift taxes outright (R&TC §13301). The federal exclusion is $15,000,000 per person for 2026. |
| Live, rent, or sell the Cupertino house? | **Sell at inheritance.** Highest after-tax net worth in all 12 tested scenarios — about $41.3M vs $19.5M by 2070. Holding only wins above **9.5% annual appreciation for 25 years**. |
| What happens to property tax? | The parent's Prop 13 basis survives **only if an heir moves in** within one year. Otherwise the house is reassessed from ~$0.80M to ~$6.53M and the tax jumps from ~$7,330 to ~$76,800/yr. |
| What about the San Francisco property? | **Keep it.** Cash-flow positive, basis locked near zero, rent capped at 1.6%/yr by the SF Rent Board. |

## Repository layout

```
docs/            GitHub Pages site (no JavaScript, no build step)
  index.html       executive summary
  findings.html    every headline number + verification status
  property-tax.html  Prop 13 / Prop 19 analysis
  inheritance.html   federal + California estate tax
  projections.html   year-by-year to 2070
  costs.html         carrying costs
  scenarios.html     sensitivity grid + break-even
  process.html       step-by-step inheritance process
  law-changes.html   enacted vs pending law changes
  sources.html       all 27 sources, linked
  flagged.html       everything unverified, with what would resolve it
data/            generated datasets (CSV + JSON)
research/        source log (S01–S27)
tools/           deterministic model and generators
COORDINATION.md  task board and verification log
```

## Reproducing

```bash
python3 tools/build_data.py      # regenerate data/model_output.json + projections.csv
python3 tools/breakeven.py       # solve for break-even appreciation
python3 tools/gen.py             # landing page
python3 tools/render.py          # the 10 subpages
python3 tools/check.py           # validate: links, HTML balance, malformed values
```

Deterministic — no randomness, no external API calls at build time.

## Verification standard

Every figure traces to a row in `research/00-source-log.md` or `docs/sources.html`. If a value
could not be confirmed against an official source it is **left blank and flagged** on
`docs/flagged.html` rather than inferred or filled in. Nine inputs are family-supplied and
marked `Owner`; two were downgraded to `Flagged` after the primary source could not be
isolated.

## Caveats

Not legal, tax, or investment advice. Market values, rent roll, utility costs and insurance
premiums are owner estimates — no appraisal or insurance quote was obtained. The sale
recommendation assumes disciplined reinvestment of proceeds at 6.5% net; that is a
behavioural assumption, not a market fact. Confirm everything with a California attorney,
CPA, and enrolled agent before acting.
