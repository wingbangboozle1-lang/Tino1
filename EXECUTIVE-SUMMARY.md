# Executive summary — two-home inheritance decision analysis

**Where things stand (2026-11-11):** the numeric pages of this analysis live in this repository (root
`*.html`, generated from [`final/`](final/)) with every figure rounded to $10 and people as placeholders
("the Transferor", "the Inheritor"). The public Pages deployment currently serves an interim
*privacy-first guide without household figures* (session `cab26ebb`, PRs #34/#36); the front-door
reconciliation (session `8fc06844`, task K3) will republish the full numeric site on an exact allowlist.
Links below point at the repository pages; they become live-site links when K3 lands.

This is a decision analysis, not legal or tax advice. It prepares questions for a licensed estate attorney
and tax adviser. Forecasts are conditional scenarios on labelled assumptions ([Flagged for Review](https://wingbangboozle1-lang.github.io/Tino1/flagged.html)), not verified predictions.

---

## 1. The situation

| | Property A — Cupertino (ZIP 95014) | Property B — San Francisco (ZIP 94122) |
|---|---|---|
| How the Inheritor gets it | Inherited through a trust, expected **2040–2050** | **Already owned** by the Inheritor |
| What changes at the Transferor's death | Ownership changes; reassessment rules apply | **Nothing** — no transfer, no reassessment, not in the estate |
| Value today (owner estimate) | $3,100,000 | $1,800,000 |
| Assessed value today | $550,540 | $116,540 |
| Property tax today | $7,210 a year | $2,440 a year |
| Income today | None (owner-occupied) | $85,800 a year from two rented units; the third unit houses the Inheritor |

**The distinction drives everything.** Property A gets a *new* tax base and a *reset* income-tax basis at
death; Property B keeps its old (low) tax base and old (unknown) basis forever. Sources:
[BOE Rule 462.260](https://boe.ca.gov/proptaxes/pdf/rules/Rule462_260.pdf),
[IRS inherited-property FAQ](https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances).

## 2. Recommendation (conditional on the model assumptions)

**Keep Property B exactly as it is, and sell Property A within a few months of inheriting it, investing
the proceeds in a diversified stock fund.** On the baseline the ranking is Sell > Rent > Live, and it stays
that way in every sensitivity except two named crisis paths.

Why, in numbers (baseline: inheritance in 2045, all figures after tax, in 2026 dollars):

| Measure | Live in A | Rent A out | Sell A and reinvest |
|---|---|---|---|
| Property A value at inheritance | $6,531,230 | $6,531,230 | $6,531,230 |
| New assessed value (Prop 19) | $5,031,080 | $6,531,230 | — (sold) |
| First-year property tax | $59,950 | $77,480 | $44,980 carrying cost until sale |
| Cash released at inheritance | $0 | $0 | $6,152,510 |
| Wealth in 2076 (2026 dollars) | $3,446,200 | $5,582,450 | **$9,747,210** |
| Best choice in 50 real 1976–2025 replays (10 yr / 20 yr) | 0 / 0 | 7 / 0 | **43 / 50** |

Key mechanics:

- **Basis reset.** A sale soon after death has almost no taxable gain (the model shows a $333,750 *loss*
  from selling costs), because the basis steps up to the date-of-death value
  ([IRC basis rules](https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances),
  [Rev. Rul. 2023-2](https://www.irs.gov/irb/2023-16_IRB) for the trust caveat).
- **Proposition 19 does not rescue living in A.** Even with the family-home relief the assessed value rises
  from $802,030 to $5,031,080 (the allowance is only $1,500,150 by 2045), so the tax bill rises from about
  $10,820 to about $59,950 a year
  ([BOE LTA 2026/026](https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf),
  [BOE LTA 2025/009](https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf)). Living there costs about
  $6,301,010 of 2076 wealth versus selling.
- **Property B is the tax prize.** Its assessed value ($116,540 vs $1,800,000 market) saves about
  $19,890 a year in property tax — permanently lost if sold — and it already produces $85,800 a year.
- **Do not park the proceeds in savings.** At about 3.5% the rental option beats selling
  ($5,118,360 vs $3,554,580). If the money would sit in savings or T-bills, keep A as a rental instead.
- **The first ten years are the risky ones.** Selling trails renting in 7 of the 50 real replays at the
  10-year mark (worst case $2,069,690 behind) and leads in all 50 at 20 years. Two named paths — a
  1929–1941-style Depression and Japan-style stagnation — end with renting ahead of selling into stocks;
  investing in stages with a few years of spending in Treasury bills narrows that risk
  ([Black swan section](https://wingbangboozle1-lang.github.io/Tino1/black-swan.html)).

## 3. Estate tax and the cash inheritance

| Level | Threshold before tax | Status |
|---|---|---|
| Federal estate tax | $15,000,000 (2026) / $15,480,000 (2027), indexed; 40% above | [IRS](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax), [Rev. Proc. 2026-35](https://www.irs.gov/pub/irs-drop/rp-26-35.pdf) |
| California estate / inheritance tax | None for deaths since 2005 | [CA Controller](https://www.sco.ca.gov/ardtax_estate_tax.html) |
| Local | None | — |

Room for cash in 2045 (per transferor, baseline): projected exclusion $24,143,520 minus Property A
$6,531,230 = **$17,612,280** of headroom before any federal estate tax. The considerable cash
inheritance sits inside that room on these projections; if the estate is larger than the room shown
(possible with portability or a later Congress), the excess costs 40 cents on the dollar. Numbers:
[Cash and estate tax](https://wingbangboozle1-lang.github.io/Tino1/estate-cash.html).

## 4. The inheritance process, step by step

Full list with deadlines: [Process](https://wingbangboozle1-lang.github.io/Tino1/process.html). The clock
items: trustee notice within **60 days** ([Prob. Code §16061.7](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.));
change-in-ownership statement within **150 days** ([R&TC §480](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.));
Form 706 within **9 months** if the estate is above the threshold ([IRS FAQ](https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes));
if moving in, homeowners' exemption within **1 year** and the parent-child claim within **3 years**
([BOE Prop 19](https://www.boe.ca.gov/prop19/)). **First action: have the estate attorney confirm the
trust type and gross-estate inclusion in writing** — if the home is outside the estate there is no basis
reset and selling triggers tax on decades of gain ($3,319,060 less wealth in the model).

## 5. Operating costs at inheritance (Property A, first year)

Water $100–$150/month; electricity net **credit** of $10–$20/month (solar); insurance **unconfirmed** —
ZIP-level premiums are not published (owner estimate $1,500/year used; tripling it does not change the
ranking) — [California Department of Insurance](https://www.insurance.ca.gov/01-consumers/105-type/9-compare-prem/index.cfm).
Property B: water $330–$400/month, electricity $30–$70/month, landlord insurance also unconfirmed.
Details and growth assumptions: [Insurance and costs](https://wingbangboozle1-lang.github.io/Tino1/costs.html).

## 6. Black swan conditions (kept apart from the baseline)

Growth and inflation are never constant for 50 years. The site replays the **real 1976–2025 record** from
every one of its 50 starting years and adds named crisis paths (Depression, Japan-style stagnation,
stagflation, lost decade, 2007–2012 bust at the wrong moment). Selling leads in 43/50 replays at ten
years and 50/50 at twenty; it loses to renting in the Depression and Japan paths. Baseline assumptions
(inflation 2.5%, home prices 4.0%, stocks 7.0%) sit just below the 2000–2025 record — deliberately
conservative. See [Black swan](https://wingbangboozle1-lang.github.io/Tino1/black-swan.html) and
[Year by year](https://wingbangboozle1-lang.github.io/Tino1/projections.html) (2026–2076).

## 7. Verification and flagged items

Every headline legal fact was re-read on its official page on 2026-11-11 in an independent pass — each
check is listed with its link on the [Verification](https://wingbangboozle1-lang.github.io/Tino1/verification.html)
register (22 checks, IRS / BOE / LegInfo / SCO / SF Treasurer / Santa Clara County / HUD). Anything that
cannot be confirmed from an official source is blank and flagged: insurance premiums (U01/U02), the exact
tax rate area (U03), the 2027 Proposition 19 allowance (U04), solar interconnection (U05), the owner's own
figures (P03), and open questions only a professional can answer (Q01–Q06). Full list:
[Flagged for Review](https://wingbangboozle1-lang.github.io/Tino1/flagged.html). Irregularities found in
the sources themselves (two IRS pages disagreeing on the old closing-letter fee, the Assessor's
"annually" vs the BOE's biennial adjustment, unofficial ballot results) are recorded there too.

## 8. Privacy

No names, street addresses or parcel numbers appear anywhere on the site. People are "the Transferor" and
"the Inheritor". Owner-supplied figures are rounded to the nearest $10 and the year-by-year bill history is
not published (a multi-year series can identify one parcel). **Owner action remains:** the repository is
public and its Git history contains pre-rounding versions of early pages; only the owner can make the
repository private or rewrite history (flags P01/P02; `README.md`).
