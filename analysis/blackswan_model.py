#!/usr/bin/env python3
"""Black swan economic-condition model: 50-year (2026-2076) VARIABLE-rate projections.

Complements analysis/model.py (constant-rate baseline) because growth and
inflation are never consistent over a 50-year period. Every scenario's yearly
rate path is written out for audit (analysis/data/blackswan_paths.csv).

- CPI legs marked "verified" replay actual BLS annual CPI-U rates (see
  analysis/data/blackswan_history.csv for the official source).
- Home-price and portfolio legs are ASSUMPTIONS calibrated to cited historical
  episodes (status column says so); they are not forecasts.

Property A = Cupertino 95014 (inherited via trust ~2045). Property B (SF 94122)
is already owned by the heir and is common to every strategy, so only the
incremental flows of Property A's three uses are compared:
  LIVE  - move into A (Prop 19 partial shield), rent B's vacant unit at market
  RENT  - keep A as a rental (full reassessment at inheritance)
  SELL  - sell A at inheritance (stepped-up basis -> ~zero gain) and invest

All dollar outputs rounded to nearest $10 (project rule). Run:
  python3 analysis/blackswan_model.py
Outputs: analysis/data/blackswan_paths.csv, blackswan_projection_{base,replay}.csv,
         blackswan_stress.csv, dashboard/data/blackswan_output.json
"""
from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "analysis", "data")
DOCS_DATA = os.path.join(ROOT, "dashboard", "data")
os.makedirs(DOCS_DATA, exist_ok=True)

BLS_CPI_URL = "https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202407.pdf"
FHFA_URL = "https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx"
NBER_URL = "https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions"
PMMS_URL = "https://www.freddiemac.com/pmms"
CBO_URL = "https://www.cbo.gov/publication/61882"

BASE_YEAR, END_YEAR = 2026, 2076          # 50 completed years
INHERIT_YEARS = (2040, 2045, 2050)        # user's 2040-2050 trust window
HOLD = 10                                 # evaluate +10 years after inheritance


def r10(x: float) -> int:
    return int(round(x / 10.0)) * 10


# --- verified / user-supplied parameters (same as analysis/model.py) -------
RATE_A = 0.011636          # Cupertino composite FY2025-26 (SCC rate book; see model.py)
HOX = 7000.0
PROP19_CAP_2025 = 1_044_586.0   # BOE LTA 2025/009
CAP_GROWTH = 0.02
ESTATE_EXCL_2026 = 15_000_000.0  # P.L. 119-21 sec. 70106 / Rev. Proc. 2025-32
ESTATE_RATE = 0.40
AV_A_2026 = 550_540.0     # user-supplied 2026 roll (550,537 rounded to $10)
FIXED_A_2026 = 940.0      # derived (bill - rate x AV), rounded to $10
VALUE_A_2026 = 3_100_000.0
VALUE_B_2026 = 1_800_000.0
AV_B_2026 = 114_250.0     # user-supplied 2025 roll 114,248 -> $10
WATER_A = 1500.0          # user-supplied ~$125/mo
ELEC_A = 0.0              # solar net-credit ignored (conservative)
INS_A = 1500.0            # user-supplied estimate
MAINT_A = 6000.0
RENT_A = 6390.0 * 12      # HUD FY2026 SAFMR 95014 4BR (40th pct)
UNIT3_B = 3500.0 * 12     # B's vacant unit at market (assumption)
SELLING_COST, TRANSFER_TAX = 0.05, 0.0011
VACANCY, MGMT = 0.05, 0.06
DEP_SHARE, DEP_YEARS = 0.60, 27.5
COMBINED_ORDINARY, COMBINED_RECAP = 0.371, 0.411
PORTFOLIO_LIQ_TAX = 0.30
BUILDING_A_SHARE = 0.60

# --- verified BLS annual CPI-U inflation: 1976-2025 (percent) ------------
CPI_1976_2025 = [
    5.8, 6.5, 7.6, 11.3, 13.5, 10.3, 6.2, 3.2, 4.3, 3.5,          # 1976-1985
    1.9, 3.7, 4.1, 4.8, 5.4, 4.2, 3.0, 3.0, 2.6, 2.8,             # 1986-1995
    3.0, 2.3, 1.6, 2.2, 3.4, 2.8, 1.6, 2.3, 2.7, 3.4,             # 1996-2005
    3.2, 2.9, 3.8, -0.4, 1.6, 3.2, 2.1, 1.5, 1.6, 0.1,            # 2006-2015
    1.3, 2.1, 2.4, 1.8, 1.2, 4.7, 8.0, 4.1, 2.9, 2.6,             # 2016-2025
]
assert len(CPI_1976_2025) == 50


def build_paths() -> dict[str, dict[int, dict[str, float]]]:
    """Yearly rate paths per scenario. Rates are decimal fractions."""
    paths: dict[str, dict[int, dict[str, float]]] = {}

    def rec(scen: str, y: int, cpi: float, aa: float, ab: float, port: float) -> None:
        paths.setdefault(scen, {})[y] = {
            "cpi": cpi, "appr_a": aa, "appr_b": ab, "portfolio": port,
            "rent_growth": max(cpi + 0.01, 0.015),
            "utility_growth": cpi + 0.02, "ins_growth": cpi + 0.025,
            "maint_growth": cpi,
        }

    for y in range(BASE_YEAR, END_YEAR + 1):
        # BASE
        rec("BASE", y, 0.025, 0.04, 0.03, 0.07)
        # REPLAY: actual CPI 1976-2025 -> 2026-2075 (2076 repeats 2025 rate)
        i = min(y - BASE_YEAR, 49)
        cpi = CPI_1976_2025[i] / 100.0
        hist_year = 1976 + i
        if hist_year <= 1980:
            real = 0.02
        elif hist_year <= 1983:
            real = -0.04
        elif hist_year <= 1990:
            real = 0.015
        elif hist_year <= 1996:
            real = -0.015
        elif hist_year <= 2005:
            real = 0.04
        elif hist_year <= 2011:
            real = -0.07
        elif hist_year <= 2019:
            real = 0.04
        else:  # 2020-2025 pandemic pattern (real home growth per episode H8)
            real = {2020: 0.088, 2021: 0.10, 2022: -0.03,
                    2023: -0.06, 2024: 0.01, 2025: 0.004}[hist_year]
        aa = cpi + real
        ab = aa - 0.01
        port = 0.045 + 0.5 * (cpi - 0.025)
        if hist_year == 2008:
            port = -0.37
        elif hist_year == 2009:
            port = 0.26
        elif hist_year == 2002:
            port = -0.22
        elif hist_year == 2022:
            port = -0.19
        elif hist_year == 2021:
            port = 0.27
        rec("REPLAY", y, cpi, aa, ab, port)

        # STAG: 1974-1983 CPI replay in 2031-2040
        stag_cpi = [11.0, 9.1, 5.8, 6.5, 7.6, 11.3, 13.5, 10.3, 6.2, 3.8]
        if 2031 <= y <= 2040:
            c = stag_cpi[y - 2031] / 100.0
            rec("STAG", y, c, 0.02, 0.01, 0.05)
        else:
            rec("STAG", y, 0.025 if y < 2031 else 0.03, 0.04, 0.03, 0.07)

        # GFC: crash 2038-2042, recovery 2043-2047 (episode H5/H6)
        gfc_cpi = [2.9, 3.8, -0.4, 1.6, 3.2]  # actual 2007-2011 CPI
        gfc_port = [-0.37, 0.26, 0.15, 0.02, 0.16]
        if 2038 <= y <= 2042:
            rec("GFC", y, gfc_cpi[y - 2038] / 100.0, -0.082, -0.082, gfc_port[y - 2038])
        elif 2043 <= y <= 2047:
            rec("GFC", y, 0.02, 0.08, 0.08, 0.07)
        else:
            rec("GFC", y, 0.025, 0.04, 0.03, 0.07)

        # JP: deflation 2036-2050
        if 2036 <= y <= 2050:
            rec("JP", y, 0.005, -0.02, -0.02, 0.02)
        else:
            rec("JP", y, 0.025 if y < 2036 else 0.015,
                0.04 if y < 2036 else 0.01, 0.03 if y < 2036 else 0.01,
                0.07 if y < 2036 else 0.05)

        # COVID: 2020-2023 pattern in 2036-2039
        cov_cpi = [1.2, 4.7, 8.0, 4.1]
        cov_home = [0.18, 0.02, -0.03, 0.04]
        cov_port = [0.16, 0.27, -0.19, 0.24]
        if 2036 <= y <= 2039:
            rec("COVID", y, cov_cpi[y - 2036] / 100.0,
                cov_home[y - 2036], cov_home[y - 2036] - 0.01, cov_port[y - 2036])
        else:
            rec("COVID", y, 0.025 if y < 2036 else 0.028, 0.04, 0.03, 0.07)
    return paths


# ---------------------------------------------------------------------------
def project_a(scen: str, path: dict[int, dict]) -> list[dict]:
    """Year-by-year Property A under a scenario: value, AV (Prop 8), tax, costs."""
    rows = []
    fbyv = AV_A_2026
    fixed = FIXED_A_2026
    ins, water, elec, maint = INS_A, WATER_A, ELEC_A, MAINT_A
    value = VALUE_A_2026
    for y in range(BASE_YEAR, END_YEAR + 1):
        p = path[y]
        if y > BASE_YEAR:
            value *= 1 + p["appr_a"]
            fbyv *= 1.02                      # Prop 13 cap (Cal. Const. art. XIII A)
            fixed *= 1.02
            ins *= 1 + p["ins_growth"]
            water *= 1 + p["utility_growth"]
            elec *= 1 + p["utility_growth"]
            maint *= 1 + p["maint_growth"]
        av = min(fbyv, value)                 # Prop 8: lower of FBYV or market (BOE Pub 800-10)
        tax = av * RATE_A + fixed
        total = tax + ins + water + elec + maint
        rows.append({
            "scenario": scen, "year": y,
            "market_value": r10(value), "factored_base_year_value": r10(fbyv),
            "assessed_value": r10(av), "property_tax": r10(tax),
            "insurance": r10(ins), "water": r10(water), "electricity": r10(elec),
            "maintenance": r10(maint), "total_carrying_cost": r10(total),
            "cpi": round(p["cpi"] * 100, 2), "appreciation_a": round(p["appr_a"] * 100, 2),
            "prop8_active": "yes" if value < fbyv else "no",
        })
    return rows


def strategy_compare(scen: str, path: dict[int, dict], inherit_year: int) -> dict:
    """Terminal wealth (after tax, $10-rounded) of A's three uses, +10 yr horizon."""
    horizon = inherit_year + HOLD

    # value path lookup
    v = VALUE_A_2026
    values = {}
    for y in range(BASE_YEAR, END_YEAR + 1):
        if y > BASE_YEAR:
            v *= 1 + path[y]["appr_a"]
        values[y] = v

    fbyv_T = AV_A_2026 * (1.02 ** (inherit_year - BASE_YEAR))
    fixed_T = FIXED_A_2026 * (1.02 ** (inherit_year - BASE_YEAR))
    cap_T = PROP19_CAP_2025 * ((1 + CAP_GROWTH) ** (inherit_year - 2025))
    fm_T = values[inherit_year]

    results = {}
    for strat in ("LIVE", "RENT", "SELL"):
        portfolio = 0.0
        cum_cash = 0.0
        initial_invest = 0.0
        if strat == "SELL":
            initial_invest = fm_T * (1 - SELLING_COST - TRANSFER_TAX)   # stepped-up basis -> gain ~0
            portfolio = initial_invest
        if strat == "LIVE":
            av = fbyv_T + max(0.0, fm_T - fbyv_T - cap_T)          # Prop 19 partial shield
        elif strat == "RENT":
            av = fm_T                                              # full reassessment
        av_y = av
        ins, water, elec, maint = INS_A, WATER_A, ELEC_A, MAINT_A
        for k, y in enumerate(range(inherit_year, horizon)):
            p = path[y]
            if k > 0:
                av_y *= 1.02
                ins *= 1 + p["ins_growth"]
                water *= 1 + p["utility_growth"]
                elec *= 1 + p["utility_growth"]
                maint *= 1 + p["maint_growth"]
            tax = (av_y - (HOX if strat == "LIVE" else 0.0)) * RATE_A + fixed_T * (1.02 ** k)
            cost = tax + ins + water + elec + maint
            net = 0.0
            if strat == "RENT":
                gross = RENT_A * ((1 + p["rent_growth"]) ** (y - BASE_YEAR))
                net_rent = gross * (1 - VACANCY - MGMT)
                dep = fm_T * DEP_SHARE / DEP_YEARS
                taxable = net_rent - cost - dep
                inc_tax = max(taxable, 0.0) * COMBINED_ORDINARY
                net = net_rent - cost - inc_tax
            elif strat == "LIVE":
                unit3 = UNIT3_B * ((1 + p["rent_growth"]) ** (y - BASE_YEAR))
                net_rent = unit3 * (1 - VACANCY - MGMT)
                inc_tax = max(net_rent - cost, 0.0) * COMBINED_ORDINARY
                net = net_rent - cost - inc_tax
            else:
                net = 0.0            # sold: no A cash flows
            cum_cash += net
            portfolio = portfolio * (1 + p["portfolio"]) + net
        # terminal property value and after-tax liquidation (for keep strategies)
        prop_liquid = 0.0
        if strat in ("LIVE", "RENT"):
            v_end = values[horizon]
            sell_costs = v_end * (SELLING_COST + TRANSFER_TAX)
            gain = max(v_end - sell_costs - fm_T, 0.0)             # basis = FMV at death
            if strat == "LIVE":
                gain = max(gain - 250_000.0, 0.0)                  # IRC 121 (single)
            dep_taken = fm_T * DEP_SHARE / DEP_YEARS * HOLD if strat == "RENT" else 0.0
            cg = gain * COMBINED_ORDINARY
            recap = dep_taken * COMBINED_RECAP
            prop_liquid = v_end - sell_costs - cg - recap
        contributions = initial_invest + cum_cash
        port_gain = max(portfolio - contributions, 0.0)
        port_after_tax = portfolio - port_gain * PORTFOLIO_LIQ_TAX
        terminal = port_after_tax + prop_liquid
        results[strat] = {
            "terminal_wealth": r10(terminal),
            "portfolio_after_tax": r10(port_after_tax),
            "property_liquidation_after_tax": r10(prop_liquid),
            "cumulative_net_cash": r10(cum_cash),
        }

    # estate tax exposure at inheritance (before any strategy)
    excl = ESTATE_EXCL_2026 * (1.025 ** (inherit_year - BASE_YEAR))
    vb = VALUE_B_2026
    for y in range(BASE_YEAR, inherit_year):
        vb *= 1 + path[y]["appr_b"]
    gross = fm_T + vb
    over = max(gross - excl * 2, 0.0)   # two exclusion slots assumed (couple/trust) — assumption
    estate_tax = over * ESTATE_RATE

    best = max(results, key=lambda k: results[k]["terminal_wealth"])
    return {
        "scenario": scen, "inherit_year": inherit_year, "horizon_year": horizon,
        "value_a_at_inheritance": r10(fm_T), "value_b_at_inheritance": r10(vb),
        "prop19_cap_at_T": r10(cap_T), "fbyv_a_at_T": r10(fbyv_T),
        "gross_estate_at_T": r10(gross), "estate_exclusion_2slots": r10(excl * 2),
        "federal_estate_tax_if_unsheltered": r10(estate_tax),
        "strategies": results, "best": best,
    }


def main() -> None:
    paths = build_paths()

    # 1) audit trail of every yearly rate used
    with open(os.path.join(DATA, "blackswan_paths.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "year", "cpi_pct", "appreciation_a_pct", "appreciation_b_pct",
                    "portfolio_pct", "rent_growth_pct", "utility_growth_pct", "ins_growth_pct",
                    "maint_growth_pct", "cpi_status", "source_url"])
        for scen in ("BASE", "REPLAY", "STAG", "GFC", "JP", "COVID"):
            for y in range(BASE_YEAR, END_YEAR + 1):
                p = paths[scen][y]
                w.writerow([scen, y, round(p["cpi"] * 100, 2), round(p["appr_a"] * 100, 2),
                            round(p["appr_b"] * 100, 2), round(p["portfolio"] * 100, 2),
                            round(p["rent_growth"] * 100, 2), round(p["utility_growth"] * 100, 2),
                            round(p["ins_growth"] * 100, 2), round(p["maint_growth"] * 100, 2),
                            "verified BLS replay" if scen in ("REPLAY", "STAG", "GFC", "COVID")
                            and scen != "BASE" else "assumption", BLS_CPI_URL])

    # 2) year-by-year Property A projections: baseline vs replay
    for scen, fname in (("BASE", "blackswan_projection_base.csv"),
                        ("REPLAY", "blackswan_projection_replay.csv"),
                        ("STAG", "blackswan_projection_stag.csv"),
                        ("GFC", "blackswan_projection_gfc.csv"),
                        ("JP", "blackswan_projection_jp.csv"),
                        ("COVID", "blackswan_projection_covid.csv")):
        rows = project_a(scen, paths[scen])
        with open(os.path.join(DATA, fname), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # 3) strategy stress grid
    stress = []
    for scen in ("BASE", "REPLAY", "STAG", "GFC", "JP", "COVID"):
        for iy in INHERIT_YEARS:
            stress.append(strategy_compare(scen, paths[scen], iy))
    with open(os.path.join(DATA, "blackswan_stress.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "inherit_year", "horizon_year", "value_a_at_inheritance",
                    "value_b_at_inheritance", "gross_estate_at_T", "federal_estate_tax_if_unsheltered",
                    "terminal_sell", "terminal_rent", "terminal_live", "best"])
        for s in stress:
            st = s["strategies"]
            w.writerow([s["scenario"], s["inherit_year"], s["horizon_year"],
                        s["value_a_at_inheritance"], s["value_b_at_inheritance"],
                        s["gross_estate_at_T"], s["federal_estate_tax_if_unsheltered"],
                        st["SELL"]["terminal_wealth"], st["RENT"]["terminal_wealth"],
                        st["LIVE"]["terminal_wealth"], s["best"]])

    out = {
        "params": {
            "rate_a": RATE_A, "av_a_2026": r10(AV_A_2026), "value_a_2026": r10(VALUE_A_2026),
            "value_b_2026": r10(VALUE_B_2026), "prop19_cap_2025": r10(PROP19_CAP_2025),
            "estate_exclusion_2026": r10(ESTATE_EXCL_2026),
            "horizon": f"{BASE_YEAR}-{END_YEAR}", "sources": {
                "cpi_replay": BLS_CPI_URL, "recessions": NBER_URL, "mortgage_rates": PMMS_URL,
                "home_price_crash": FHFA_URL, "baseline_anchor": CBO_URL,
            },
        },
        "stress": stress,
        "projections": {
            "BASE": project_a("BASE", paths["BASE"]),
            "REPLAY": project_a("REPLAY", paths["REPLAY"]),
            "STAG": project_a("STAG", paths["STAG"]),
            "GFC": project_a("GFC", paths["GFC"]),
            "JP": project_a("JP", paths["JP"]),
            "COVID": project_a("COVID", paths["COVID"]),
        },
    }
    with open(os.path.join(DOCS_DATA, "blackswan_output.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("blackswan model complete:",
          len(out["projections"]["BASE"]), "projection rows,", len(stress), "stress rows")


if __name__ == "__main__":
    main()
