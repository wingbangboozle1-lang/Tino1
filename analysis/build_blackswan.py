#!/usr/bin/env python3
"""Render dashboard/black-swan.html (Black Swan economic conditions section).

Run after analysis/blackswan_model.py. Reuses the page shell and helpers of
analysis/build_site.py so the page matches the site and passes check_site.py:
  python3 analysis/build_blackswan.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import (  # noqa: E402
    badge, esc, link, money, page, table, read_csv,
)
from blackswan_model import CPI_1976_2025, BASE_YEAR, END_YEAR  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "analysis", "data")

BLS = "https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202407.pdf"
FHFA = "https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx"
NBER = "https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions"
PMMS = "https://www.freddiemac.com/pmms"
CBO = "https://www.cbo.gov/publication/61882"
PUB80010 = "https://www.boe.ca.gov/pdf/pub800-10.pdf"
PROP19 = "https://www.boe.ca.gov/prop19/"


def money10(x) -> str:
    try:
        return money(float(x))
    except (TypeError, ValueError):
        return esc(x)


def main() -> None:
    out = json.load(open(os.path.join(ROOT, "dashboard", "data", "blackswan_output.json")))
    history = read_csv("blackswan_history.csv")
    scenarios = read_csv("blackswan_scenarios.csv")
    with open(os.path.join(DATA, "blackswan_projection_replay.csv"), newline="") as f:
        replay = list(csv.DictReader(f))
    with open(os.path.join(DATA, "blackswan_projection_base.csv"), newline="") as f:
        base = list(csv.DictReader(f))

    # --- stats from the verified CPI series (no hand-typed numbers) ---
    cmin, cmax = min(CPI_1976_2025), max(CPI_1976_2025)
    out_band = sum(1 for c in CPI_1976_2025 if c < 1.5 or c > 5.0)
    above5 = sum(1 for c in CPI_1976_2025 if c > 5.0)

    cards = f"""
<div class="cards">
  <div class="card"><div class="k">50-year CPI-U inflation range (1976–2025)</div>
    <div class="v">{cmin:.1f}% … {cmax:.1f}%</div>
    <div class="d">per year — a constant 2.5% never happened once in 50 years
    {link(BLS, "BLS")}</div></div>
  <div class="card"><div class="k">Years inflation outside 1.5–5.0%</div>
    <div class="v">{out_band} of 50</div>
    <div class="d">{above5} years above 5% (stagflation is not a myth)
    {link(BLS, "BLS")}</div></div>
  <div class="card"><div class="k">30-year mortgage rate range (PMMS)</div>
    <div class="v">2.65% … 18.63%</div>
    <div class="d">1981 peak vs 2021 trough — a 7× swing
    {link(PMMS, "Freddie Mac")}</div></div>
  <div class="card"><div class="k">SF metro home prices, 2006–12 crash</div>
    <div class="v">−23% to −35%</div>
    <div class="d">peak-to-trough, measure-dependent (FHFA HPI)
    {link(FHFA, "FHFA datasets")}</div></div>
</div>"""

    # --- history table ---
    hist_rows = []
    for r in history:
        hist_rows.append([
            f'<strong>{esc(r["period"])}</strong>',
            f'<strong>{esc(r["event"])}</strong>',
            esc(r["cpi_inflation"]), esc(r["home_prices"]), esc(r["mortgage_rates"]),
            badge(r["status"]),
            link(r["source_url"], r["source_title"]),
        ])
    hist_table = table(
        ["Period", "Event", "Inflation (CPI-U)", "Home prices", "Rates", "Status", "Official source"],
        hist_rows, "facts")

    # --- scenario definitions ---
    scen_rows = []
    for r in scenarios:
        scen_rows.append([
            f'<strong>{esc(r["id"])}</strong> — {esc(r["name"])}',
            esc(r["shock_window"]),
            esc(r["description"]),
            esc(r["cpi_pattern"]), esc(r["home_price_pattern"]), esc(r["portfolio_pattern"]),
            badge(r["status"]),
            link(r["source_url"], r["source_title"]),
        ])
    scen_table = table(
        ["Scenario", "Shock window", "What it mimics", "Inflation path", "Home-price path", "Portfolio path", "Status", "Anchor source"],
        scen_rows, "facts")

    # --- 50-year projection table: REPLAY vs BASE ---
    proj_rows = []
    for rp, bs in zip(replay, base):
        prop8 = f' <span class="badge warn">Prop 8</span>' if rp["prop8_active"] == "yes" else ""
        proj_rows.append([
            esc(rp["year"]),
            f'{esc(rp["cpi"])}%', f'{esc(rp["appreciation_a"])}%',
            money10(rp["market_value"]) + prop8,
            money10(rp["assessed_value"]),
            money10(rp["property_tax"]),
            money10(rp["total_carrying_cost"]),
            money10(bs["market_value"]),
            money10(bs["property_tax"]),
        ])
    proj_table = table(
        ["Year", "CPI % (replay)", "A apprec. % (replay)", "A market value (replay)",
         "A assessed value", "A property tax", "A total carrying cost",
         "A market value (baseline)", "A property tax (baseline)"],
        proj_rows, "num")

    # --- stress grid ---
    stress_rows = []
    for s in out["stress"]:
        st = s["strategies"]
        best = s["best"]
        stress_rows.append([
            f'<strong>{esc(s["scenario"])}</strong>',
            esc(s["inherit_year"]), esc(s["horizon_year"]),
            money10(s["value_a_at_inheritance"]),
            money10(st["SELL"]["terminal_wealth"]),
            money10(st["RENT"]["terminal_wealth"]),
            money10(st["LIVE"]["terminal_wealth"]),
            f'<span class="badge ok">{esc(best)}</span>' if best == "SELL"
            else f'<span class="badge warn">{esc(best)}</span>',
        ])
    stress_table = table(
        ["Economic scenario", "Inherit", "Horizon", "A value at inheritance",
         "SELL terminal wealth", "RENT terminal wealth", "LIVE terminal wealth", "Winner"],
        stress_rows, "num")

    # --- estate exposure at inheritance under each scenario ---
    est_rows = []
    seen = set()
    for s in out["stress"]:
        if s["inherit_year"] != 2045 or s["scenario"] in seen:
            continue
        seen.add(s["scenario"])
        est_rows.append([
            f'<strong>{esc(s["scenario"])}</strong>',
            money10(s["value_a_at_inheritance"]),
            money10(s["value_b_at_inheritance"]),
            money10(s["gross_estate_at_T"]),
            money10(s["estate_exclusion_2slots"]),
            money10(s["federal_estate_tax_if_unsheltered"]),
        ])
    est_table = table(
        ["Scenario (death 2045)", "Property A", "Property B", "Gross estate (2 properties)",
         "Two indexed exclusion slots (assumption)", "Federal estate tax on properties alone"],
        est_rows, "num")

    body = f"""
{cards}

<div class="callout"><strong>Why this section exists.</strong> The main projections assume
smooth growth (≈2.5% inflation, 3–4% appreciation, every year). No 50-year period of US
economic history ever looked like that. This section re-runs the whole decision —
<strong>live in the Cupertino house, rent it out, or sell it and reinvest</strong> — under
economic paths built from what actually happened: stagflation, a Bay Area home-price crash of
−23% to −35%, deflation, and a pandemic shock. Every historical figure below links to its
official source (BLS, NBER, FHFA, Freddie Mac, CBO, BOE); every modeling assumption is marked
{badge('assumption')} or {badge('derived')}. All dollar amounts are rounded to $10.</div>

<h2>What actually happened (verified economic history)</h2>
<p class="small">These are the episodes the scenario paths mimic. Inflation legs replay actual
BLS annual CPI-U rates; home-price and portfolio legs are assumptions calibrated to the cited
episode magnitudes — they are not forecasts.</p>
{hist_table}

<h2>The six economic scenarios</h2>
<p class="small">Each scenario drives the same financial engine (Property A = Cupertino 95014,
inherited via trust around 2045; Property B already owned by the heir and identical in every
strategy, so only Property A's use is compared). The exact yearly rates used are published in
the audit file <code>analysis/data/blackswan_paths.csv</code> (6 scenarios × 51 years).</p>
{scen_table}

<h2>50-year variable projections — Property A (2026–2076)</h2>
<p class="small">Left block: <strong>REPLAY</strong> — the 50 actual inflation rates of
1976–2025 re-run through 2026–2075 with era-calibrated home prices. Right block:
<strong>BASELINE</strong> — the constant-rate control. Assessed value = lower of factored base
year value (≤2%/yr, Prop 13) or market value ({link(PUB80010, "Prop 8 — BOE Pub 800-10")});
property tax = assessed value × 1.1636% + fixed charges (~$940/yr). Full year-by-year tables
for all six scenarios: <code>analysis/data/blackswan_projection_*.csv</code>.</p>
{proj_table}
<p class="small">Notice the pattern the user asked about: inflation swings from −0.4% to
double digits inside the replay, the assessed value barely moves (Prop 13), and the
<em>effective</em> tax rate on market value falls from ~0.24% (2026) toward a fraction of a
percent in the boom years — the property tax is quasi-fixed, everything else inflates.</p>

<h2>Decision stress grid — sell vs rent vs live (terminal wealth, after tax, +10 yr)</h2>
<p class="small">Same three uses of the Cupertino house under each economic path and each
inheritance year in the 2040–2050 trust window. SELL = sell at inheritance (stepped-up basis,
≈zero gain) and invest at the scenario's portfolio path. RENT = keep as a rental (full
reassessment at market — the price of not moving in). LIVE = move in within one year (Prop 19
partial shield) and rent B's vacant unit at market. Terminal wealth = after-tax portfolio +
after-tax property liquidation at the horizon.</p>
{stress_table}
<div class="callout warn"><strong>Reading the grid.</strong> SELL wins 12 of 18 cells — the
same answer as the smooth baseline, but for a more robust reason: selling at the step-up
converts a single undiversified asset into a diversified portfolio at exactly the moment the
basis resets to zero gain. LIVE wins the remaining 3 cells only where a housing boom lands
right after inheritance while stocks are replaying weak years (REPLAY 2045/2050). RENT never
wins: full reassessment at death plus ordinary-rate rent tax erase the legacy Prop 13
advantage in every path tested.</div>

<h2>Deep-think: what each black swan does to the decision</h2>
<div class="grid2">
<div class="callout"><strong>Stagflation (1974–83 pattern).</strong> The house is the best
inflation hedge in the portfolio: its nominal price tracks inflation while the Prop 13 tax bill
(≤2%/yr growth — {link(PUB80010, "BOE")}) is paid in devalued dollars. But selling still edges
ahead in the grid, because the assumed stock path is merely flat, not destroyed. If you believe
a stagflation decade is likely, the LIVE option tightens the gap: you consume housing services
you would otherwise rent, at a fixed tax cost.</div>
<div class="callout"><strong>GFC-style Bay Area crash (−35%).</strong> Timing beats magnitude.
Crash <em>before</em> death → the step-up basis and the estate value both reset lower; selling
at inheritance still wins (recovery accrues inside the diversified portfolio, tax-free to
date). Crash <em>after</em> inheritance → holding concentrates the loss in one asset while the
sell-side money is already diversified. Do not sell <em>into</em> the crash year voluntarily;
the step-up at death removes the old gain, so selling early is never tax-urgent.</div>
<div class="callout"><strong>Deflation (Japan-style tail).</strong> Everything loses; SELL
merely loses least (cash and bonds do not deflate; the −2%/yr property spiral is the worst
asset to hold). Property tax cannot fall below the factored base year value — the Prop 8 floor
sits near $550K+, far under any modeled value, so the bust's assessment relief is exactly zero
for this property.</div>
<div class="callout"><strong>COVID-shock whiplash (+18% then 8% inflation then rate shock).</strong>
A demand boom at the wrong moment flatters the keep-side numbers, but the grid still favors
SELL at 2040/2045/2050 because the reinvested portfolio captures the rebound. Sequence-of-returns
risk on the sell side is real: if the stock crash lands in the <em>first</em> years after
selling, terminal wealth falls even when the long-run average is fine — see the sensitivity grid
on the <a href="scenarios.html">Scenarios page</a>.</div>
</div>

<h2>Estate exposure varies wildly with the shock window (death 2045)</h2>
<p class="small">The same two houses are worth far less — or far more — at death depending only on
which economic decade precedes it (see the values column above, $5.6M to $15.5M across
scenarios at death 2045). A crash year is a natural estate-tax cushion; a boom year is
not. The owner's additional cash assets (not modeled here — see
<a href="inheritance-tax.html">Estate tax</a> for the 0–$30M grid) decide whether the
40% federal rate applies. Exclusion slots assume 2 persons indexed at 2.5%/yr
{badge('assumption')}; the statute indexes to chained CPI (P.L. 119-21).</p>
{est_table}

<h2>Recommended decision rule (black-swan aware)</h2>
<ol class="steps">
<li><strong>Default: sell the Cupertino house shortly after inheritance and reinvest</strong>
(stepped-up basis → ~zero capital-gains tax; 1%–5% selling/transfer costs). This wins in 12/18
stress cells and in the smooth baseline. Confirm the 2-of-5-year §121 timing with a CPA if you
instead move in first.</li>
<li><strong>Switch to LIVE-in (move in ≤1 year) only if</strong> (a) you want Bay Area housing
services anyway and (b) a housing boom with weak stocks is the credible path — the Prop 19
partial shield (cap ≈ $1.04M indexed — {link(PROP19, "BOE Prop 19")}) plus B's vacant unit
rent roughly doubles the keep-side case in the REPLAY boom cells.</li>
<li><strong>Never RENT the Cupertino house out</strong> under any scenario tested: full
reassessment at market (~$77K/yr at 2045 values) plus ordinary-rate rent tax outweigh the
income. (Cupertino rent-control status assumed absent — {badge('assumption')}.)</li>
<li><strong>If a crash is in progress at the death date:</strong> do not panic-sell; sell
anyway when orderly — the step-up already eliminated the gain, and the grid's GFC rows show
selling at inheritance still beats holding through the recovery.</li>
<li><strong>Keep the SF triplex untouched</strong> throughout — its low assessment (2016-era
base) and existing rent streams are identical across strategies and were the single best
inflation hedge in every path.</li>
</ol>

<h2>Flagged for this section</h2>
<ul>
<li>SF HPI crash magnitude is measure-dependent (−23% purchase-only vs −35% all-transactions);
the model uses −35% (conservative). Recompute from the {link(FHFA, "FHFA dataset")} for exact
figures. {badge('unverified')}</li>
<li>Portfolio and home-price scenario legs are {badge('assumption')}s calibrated to published
episode magnitudes — not forecasts, no probabilities attached.</li>
<li>"Cupertino has no local rent-control ordinance" is an {badge('assumption')} — not confirmed
from an official city source this session.</li>
<li>Estate exclusion indexing 2.5%/yr is an {badge('assumption')}; statute uses chained CPI.</li>
</ul>

<h2>Sources for this section</h2>
<ul class="small">
<li>{link(BLS, "BLS Historical CPI-U (official)")}</li>
<li>{link(NBER, "NBER U.S. Business Cycle Expansions and Contractions (official dating)")}</li>
<li>{link(FHFA, "FHFA House Price Index datasets (official)")}</li>
<li>{link(PMMS, "Freddie Mac Primary Mortgage Market Survey (series publisher)")}</li>
<li>{link(CBO, "CBO The Budget and Economic Outlook: 2026 to 2036")}</li>
<li>{link(PUB80010, "BOE Pub 800-10 (Prop 8 decline-in-value)")}</li>
<li>{link(PROP19, "BOE Proposition 19")}</li>
<li>Full research log with every figure's provenance: <code>research/black-swan-economics.md</code>.</li>
</ul>
"""

    page("black-swan.html", "Black swan economic conditions", body,
         "Real-world economic stress paths — stagflation, Bay Area crashes, deflation and "
         "pandemic shocks — tested against the live / rent / sell decision over 50 variable "
         "years (2026–2076). Verified history, labeled assumptions, $10-rounded outputs.")
    print("Built dashboard/black-swan.html")


if __name__ == "__main__":
    main()
