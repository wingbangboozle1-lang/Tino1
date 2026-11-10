#!/usr/bin/env python3
"""Deterministic projection and decision model for Property A (Cupertino 95014)
and Property B (San Francisco Outer Sunset 94122).

Everything here is a MODEL. Verified legal parameters are listed in
data/*.csv with their official sources; items marked "assumption" or
"user-supplied" are not verified facts. All dollar outputs are rounded to the
nearest $10 (project rule). Run:  python3 analysis/model.py
Outputs: data/projections/*.csv, data/scenarios.csv, docs/data/model_output.json
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, asdict, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "projections")
DOCS_DATA = os.path.join(ROOT, "docs", "data")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DOCS_DATA, exist_ok=True)


def r10(x: float) -> int:
    """Round to nearest $10 (project rule)."""
    return int(round(x / 10.0)) * 10


# ---------------------------------------------------------------------------
# Parameters.  status: verified | derived | user-supplied | assumption
# ---------------------------------------------------------------------------
@dataclass
class Params:
    base_year: int = 2026
    end_year: int = 2060
    inherit_year: int = 2045            # midpoint of the user's 2040-2050 window
    hold_years: int = 10                # evaluation horizon after inheritance

    # --- verified legal parameters (see data/*.csv for sources) ---
    av_growth: float = 0.02             # Cal. Const. art. XIII A sec. 2(b) max
    rate_a: float = 0.0116360           # Cupertino composite FY2025-26 (derived from rate book components)
    rate_b: float = 0.0118162182        # SF FY2026-27 secured rate
    hox: float = 7000.0                 # Homeowners' Exemption (BOE)
    prop19_cap_2025: float = 1_044_586  # BOE LTA 2025/009 (Feb 16 2025 - Feb 15 2027)
    prop19_cap_growth: float = 0.02     # assumption (observed ~1.1%/yr 2021-2025)
    estate_exclusion_2026: float = 15_000_000.0  # Rev. Proc. 2025-32 / P.L. 119-21
    estate_rate: float = 0.40           # 26 U.S.C. 2001(c)
    sec121_exclusion: float = 250_000.0  # single filer (500,000 MFJ)
    transfer_tax_sf: float = 0.0075     # $3.75 per $500, $1M-<$5M tier
    transfer_tax_scc: float = 0.0011    # $1.10 per $1,000 (R&T 11911)

    # --- income-tax assumptions on the heir (combined federal + CA) ---
    ltcg_combined: float = 0.371        # 20% + 3.8% NIIT + 13.3% CA (gain-year income > $1M)
    recapture_combined: float = 0.411   # 25% + 3.8% + 12.3% CA on depreciation taken
    ordinary_combined: float = 0.371    # 24% federal + 9.3% CA + 3.8% NIIT on net rent (assumption)
    portfolio_liquidation_tax: float = 0.30  # blended tax on portfolio gains at horizon (assumption)
    building_share: float = 0.60        # depreciable share of FMV (assumption)
    depreciation_years: float = 27.5    # residential rental GDS (IRS Pub. 527; not re-verified)

    # --- economic assumptions ---
    cpi: float = 0.025
    appreciation_a: float = 0.04
    appreciation_b: float = 0.03
    market_rent_growth: float = 0.03
    controlled_rent_growth: float = 0.016   # SF Rent Board 2026-27 allowable increase
    utility_growth: float = 0.04
    insurance_growth: float = 0.05
    exclusion_index: float = 0.025
    portfolio_return: float = 0.07
    safe_return: float = 0.045

    # --- user-supplied 2026 inputs (rounded to $10) ---
    value_a_2026: float = 3_100_000.0
    value_b_2026: float = 1_800_000.0
    av_a_2025: float = 539_740.0
    fixed_a_2025: float = 930.0          # derived: bill - rate x AV
    fixed_b_2026: float = 1_000.0        # assumption (flagged)
    water_a: float = 125.0 * 12
    elec_a: float = 0.0                 # solar credit ignored (conservative)
    ins_a: float = 1_500.0
    maint_a: float = 6_000.0
    water_b: float = 365.0 * 12
    elec_b: float = 50.0 * 12
    ins_b: float = 1_500.0
    maint_b: float = 12_000.0
    rent_b_2units: float = 7_150.0 * 12
    rent_b_unit3_market: float = 3_500.0 * 12
    rent_a_market: float = 6_390.0 * 12  # HUD FY2026 SAFMR 95014 4BR (40th pct)
    alt_housing_rent: float = 4_500.0 * 12  # heir's rent if living elsewhere (assumption)
    mgmt_fee: float = 0.06
    vacancy: float = 0.05
    selling_cost: float = 0.05


P = Params()


def grow(base: float, rate: float, years: int) -> float:
    return base * (1 + rate) ** years


# ---------------------------------------------------------------------------
# Year-by-year projections of value, assessed value and carrying costs
# ---------------------------------------------------------------------------
def project_property(prop: str, p: Params, inherit_year: int, heir_occupies: bool,
                     transferor_residence: bool) -> list[dict]:
    """Project one property from base_year to end_year.

    heir_occupies: after inheritance the heir lives there (Prop 19 exclusion
    possible only if transferor_residence is also True).
    """
    rows = []
    if prop == "A":
        value0, apprec, rate = p.value_a_2026, p.appreciation_a, p.rate_a
        av_prev = p.av_a_2025 * (1 + p.av_growth)  # 2026 roll
        fixed0 = p.fixed_a_2025 * (1 + p.av_growth)
        ins0, water0, elec0, maint0 = p.ins_a, p.water_a, p.elec_a, p.maint_a
        transfer_tax = p.transfer_tax_scc
    else:
        value0, apprec, rate = p.value_b_2026, p.appreciation_b, p.rate_b
        av_prev = None  # pre-inheritance series withheld (privacy) - not modeled
        fixed0 = p.fixed_b_2026
        ins0, water0, elec0, maint0 = p.ins_b, p.water_b, p.elec_b, p.maint_b
        transfer_tax = p.transfer_tax_sf

    for y in range(p.base_year, p.end_year + 1):
        n = y - p.base_year
        value = grow(value0, apprec, n)
        if y < inherit_year:
            owner = "Transferor"
            if av_prev is None:
                av = None
            else:
                av = av_prev if n == 0 else av_prev * (1 + p.av_growth)
                av_prev = av
            note = ""
        elif y == inherit_year:
            owner = "Heir"
            # change in ownership at date of death: FMV = value in that year
            cap = grow(p.prop19_cap_2025, p.prop19_cap_growth, y - 2025)
            if heir_occupies and transferor_residence and av_prev is not None:
                fbyv = av_prev * (1 + p.av_growth)
                limit = fbyv + cap
                if value <= limit:
                    av = fbyv
                    note = "Prop 19 full exclusion"
                else:
                    av = fbyv + (value - limit)
                    note = f"Prop 19 partial exclusion (cap {r10(cap):,})"
            else:
                av = value
                note = "Reassessed to market value (no Prop 19 exclusion)"
            av_prev = av
        else:
            owner = "Heir"
            av = av_prev * (1 + p.av_growth)
            av_prev = av
            note = ""
        fixed = grow(fixed0, p.av_growth, n)
        if av is None:
            tax = None
        else:
            taxable = av - (p.hox if (y >= inherit_year and heir_occupies) else 0.0)
            tax = taxable * rate + fixed
        ins = grow(ins0, p.insurance_growth, n)
        water = grow(water0, p.utility_growth, n)
        elec = grow(elec0, p.utility_growth, n)
        maint = grow(maint0, p.cpi, n)
        total = (tax or 0.0) + ins + water + elec + maint
        rows.append({
            "year": y,
            "owner": owner,
            "market_value": r10(value),
            "assessed_value": None if av is None else r10(av),
            "property_tax": None if tax is None else r10(tax),
            "insurance": r10(ins),
            "water_sewer": r10(water),
            "electricity": r10(elec),
            "maintenance": r10(maint),
            "total_carrying_cost": None if tax is None else r10(total),
            "note": note,
        })
    return rows


# ---------------------------------------------------------------------------
# Scenario engine (post-inheritance, evaluated over hold_years)
# ---------------------------------------------------------------------------
@dataclass
class Scenario:
    key: str
    name: str
    live_in: str            # "A", "B" or "none"
    keep_a: bool
    keep_b: bool
    rent_a: bool            # A rented at market (requires keep_a and live_in != A)
    rent_b_units: int       # number of B units rented (0-3)
    description: str


SCENARIOS = [
    Scenario("S1", "Live in A, keep B as a 3-unit rental", "A", True, True, False, 3,
             "Heir moves into Property A within 1 year (Prop 19 exclusion). Property B is fully reassessed; the vacant unit is rented at market."),
    Scenario("S2", "Live in A, sell B at inheritance and invest", "A", True, False, False, 0,
             "Heir moves into A; B is sold shortly after death (stepped-up basis, little or no capital-gains tax) and the net proceeds are invested."),
    Scenario("S3", "Live in B's vacant unit, rent A at market", "B", True, True, True, 2,
             "Heir occupies the vacant unit of B; both properties are reassessed to market value (A is no longer anyone's principal residence)."),
    Scenario("S4", "Live in B's vacant unit, sell A and invest", "B", False, True, False, 2,
             "Heir occupies the vacant unit; A is sold at inheritance and invested."),
    Scenario("S5", "Keep both as rentals, live elsewhere", "none", True, True, True, 3,
             "Both properties reassessed to market; heir rents housing elsewhere."),
    Scenario("S6", "Sell both at inheritance, invest, rent elsewhere", "none", False, False, False, 0,
             "Both sold after death using the stepped-up basis; all proceeds invested; heir rents housing elsewhere."),
]


def sale_proceeds(value: float, basis: float, prop: str, p: Params, principal_residence: bool,
                  accumulated_depreciation: float = 0.0) -> dict:
    ttax = p.transfer_tax_sf if prop == "B" else p.transfer_tax_scc
    costs = value * (p.selling_cost + ttax)
    gain = value - costs - basis
    if gain < 0:
        gain = 0.0
    excl = p.sec121_exclusion if principal_residence else 0.0
    taxable_gain = max(gain - excl, 0.0)
    cg_tax = taxable_gain * p.ltcg_combined
    recapture_tax = accumulated_depreciation * p.recapture_combined
    net = value - costs - cg_tax - recapture_tax
    return {"gross": value, "selling_costs": costs, "gain": gain, "cap_gains_tax": cg_tax,
            "recapture_tax": recapture_tax, "net": net}


def run_scenario(s: Scenario, p: Params, inherit_year: int, hold: int,
                 appreciation_a: float | None = None, appreciation_b: float | None = None,
                 portfolio_return: float | None = None) -> dict:
    pa = appreciation_a if appreciation_a is not None else p.appreciation_a
    pb = appreciation_b if appreciation_b is not None else p.appreciation_b
    ret = portfolio_return if portfolio_return is not None else p.portfolio_return
    nT = inherit_year - p.base_year
    val_a_T = grow(p.value_a_2026, pa, nT)
    val_b_T = grow(p.value_b_2026, pb, nT)

    # Assessed values at inheritance
    cap = grow(p.prop19_cap_2025, p.prop19_cap_growth, inherit_year - 2025)
    fbyv_a = grow(p.av_a_2025, p.av_growth, inherit_year - 2025)
    if s.live_in == "A":
        av_a = fbyv_a if val_a_T <= fbyv_a + cap else fbyv_a + (val_a_T - fbyv_a - cap)
        prop19_saving_year1 = (val_a_T - av_a) * p.rate_a
    else:
        av_a = val_a_T
        prop19_saving_year1 = 0.0
    av_b = val_b_T   # rentals: full reassessment (BOE LTA 2026/026 Q5)

    portfolio = 0.0
    sold_a = sold_b = None
    if not s.keep_a:
        sold_a = sale_proceeds(val_a_T, val_a_T, "A", p, False)   # stepped-up basis -> gain ~0
        portfolio += sold_a["net"]
    if not s.keep_b:
        sold_b = sale_proceeds(val_b_T, val_b_T, "B", p, False)
        portfolio += sold_b["net"]

    dep_a = dep_b = 0.0
    yearly = []
    cum_cash = 0.0
    for k in range(1, hold + 1):
        y = inherit_year + k - 1
        n = y - p.base_year
        g = {}
        # --- Property A ---
        cash_a = 0.0
        if s.keep_a:
            av_a_y = av_a * (1 + p.av_growth) ** (k - 1)
            taxable = av_a_y - (p.hox if s.live_in == "A" else 0.0)
            tax_a = taxable * p.rate_a + grow(p.fixed_a_2025 * (1 + p.av_growth), p.av_growth, n)
            cost_a = tax_a + grow(p.ins_a, p.insurance_growth, n) + grow(p.water_a, p.utility_growth, n) \
                + grow(p.elec_a, p.utility_growth, n) + grow(p.maint_a, p.cpi, n)
            rent_a = 0.0
            tax_on_rent_a = 0.0
            if s.rent_a:
                gross = grow(p.rent_a_market, p.market_rent_growth, n)
                rent_a = gross * (1 - p.vacancy - p.mgmt_fee)
                dep = val_a_T * p.building_share / p.depreciation_years
                dep_a += dep
                taxable_income = rent_a - cost_a - dep
                tax_on_rent_a = max(taxable_income, 0.0) * p.ordinary_combined
            cash_a = rent_a - cost_a - tax_on_rent_a
            g.update({"a_property_tax": tax_a, "a_costs": cost_a, "a_rent_net": rent_a, "a_income_tax": tax_on_rent_a})
        # --- Property B ---
        cash_b = 0.0
        if s.keep_b:
            av_b_y = av_b * (1 + p.av_growth) ** (k - 1)
            taxable = av_b_y - (p.hox if s.live_in == "B" else 0.0)
            tax_b = taxable * p.rate_b + grow(p.fixed_b_2026, p.av_growth, n)
            cost_b = tax_b + grow(p.ins_b, p.insurance_growth, n) + grow(p.water_b, p.utility_growth, n) \
                + grow(p.elec_b, p.utility_growth, n) + grow(p.maint_b, p.cpi, n)
            gross = 0.0
            if s.rent_b_units >= 2:
                gross += grow(p.rent_b_2units, p.controlled_rent_growth, n)   # existing tenancies, rent-controlled
            if s.rent_b_units == 3:
                gross += grow(p.rent_b_unit3_market, p.market_rent_growth, n)
            rent_b = gross * (1 - p.vacancy - p.mgmt_fee)
            rented_share = s.rent_b_units / 3.0
            dep = val_b_T * p.building_share * rented_share / p.depreciation_years
            dep_b += dep
            taxable_income = rent_b - cost_b * rented_share - dep
            tax_on_rent_b = max(taxable_income, 0.0) * p.ordinary_combined if s.rent_b_units else 0.0
            cash_b = rent_b - cost_b - tax_on_rent_b
            g.update({"b_property_tax": tax_b, "b_costs": cost_b, "b_rent_net": rent_b, "b_income_tax": tax_on_rent_b})
        # --- housing paid elsewhere ---
        housing = grow(p.alt_housing_rent, p.market_rent_growth, n) if s.live_in == "none" else 0.0
        net_cash = cash_a + cash_b - housing
        cum_cash += net_cash
        # portfolio: grows, then absorbs the year's net cash (positive adds, negative draws)
        portfolio = portfolio * (1 + ret) + net_cash
        if s.live_in == "A":
            housing_value = grow(p.rent_a_market, p.market_rent_growth, n)
        elif s.live_in == "B":
            housing_value = grow(p.rent_b_unit3_market, p.market_rent_growth, n)
        else:
            housing_value = housing
        g.update({"year": y, "housing_paid": housing, "housing_value_consumed": housing_value,
                  "net_cash": net_cash, "portfolio_end": portfolio})
        yearly.append({k2: (r10(v) if isinstance(v, float) else v) for k2, v in g.items()})

    # Terminal wealth at end of horizon (liquidation view, after tax)
    yT = inherit_year + hold
    val_a_end = grow(p.value_a_2026, pa, yT - p.base_year)
    val_b_end = grow(p.value_b_2026, pb, yT - p.base_year)
    liq = 0.0
    details = {}
    if s.keep_a:
        sa = sale_proceeds(val_a_end, val_a_T, "A", p, s.live_in == "A", dep_a)
        liq += sa["net"]
        details["a_sale_at_horizon"] = {k: r10(v) for k, v in sa.items()}
    if s.keep_b:
        sb = sale_proceeds(val_b_end, val_b_T, "B", p, False, dep_b)   # mixed-use: treat as rental (conservative)
        liq += sb["net"]
        details["b_sale_at_horizon"] = {k: r10(v) for k, v in sb.items()}
    # portfolio liquidation tax on gains above contributions
    contributions = (sold_a["net"] if sold_a else 0.0) + (sold_b["net"] if sold_b else 0.0) + cum_cash
    port_gain = max(portfolio - contributions, 0.0)
    port_after_tax = portfolio - port_gain * p.portfolio_liquidation_tax
    terminal = liq + port_after_tax

    return {
        "key": s.key, "name": s.name, "description": s.description,
        "inherit_year": inherit_year, "horizon_year": yT,
        "value_a_at_inheritance": r10(val_a_T), "value_b_at_inheritance": r10(val_b_T),
        "assessed_a_year1": r10(av_a) if s.keep_a else None,
        "assessed_b_year1": r10(av_b) if s.keep_b else None,
        "prop19_tax_saving_year1": r10(prop19_saving_year1),
        "sale_at_inheritance_a": {k: r10(v) for k, v in sold_a.items()} if sold_a else None,
        "sale_at_inheritance_b": {k: r10(v) for k, v in sold_b.items()} if sold_b else None,
        "year1_net_cash": yearly[0]["net_cash"],
        "year1_housing_value_consumed": yearly[0]["housing_value_consumed"],
        "year1_property_tax_a": yearly[0].get("a_property_tax"),
        "year1_property_tax_b": yearly[0].get("b_property_tax"),
        "cumulative_net_cash": r10(cum_cash),
        "portfolio_end_pre_tax": r10(portfolio),
        "portfolio_end_after_tax": r10(port_after_tax),
        "property_liquidation_after_tax": r10(liq),
        "terminal_wealth_after_tax": r10(terminal),
        "terminal_wealth_2026_dollars": r10(terminal / (1 + p.cpi) ** (yT - p.base_year)),
        "yearly": yearly,
        "details": details,
    }


def estate_tax_table(p: Params) -> list[dict]:
    rows = []
    for T in (2040, 2045, 2050):
        excl = grow(p.estate_exclusion_2026, p.exclusion_index, T - p.base_year)
        va = grow(p.value_a_2026, p.appreciation_a, T - p.base_year)
        vb = grow(p.value_b_2026, p.appreciation_b, T - p.base_year)
        props = va + vb
        for other in (0, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000):
            gross = props + other
            for married, mult in (("single transferor", 1), ("married (portability)", 2)):
                taxable = max(gross - excl * mult, 0.0)
                rows.append({
                    "death_year": T, "exclusion_per_person": r10(excl), "transferor": married,
                    "properties_value": r10(props), "other_assets": other, "gross_estate": r10(gross),
                    "amount_over_exclusion": r10(taxable), "federal_estate_tax": r10(taxable * p.estate_rate),
                    "california_estate_tax": 0,
                })
    return rows


def write_csv(path: str, rows: list[dict]):
    if not rows:
        return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


def main():
    p = P
    out = {"params": asdict(p), "projections": {}, "scenarios": {}, "sensitivity": [], "estate_tax": []}

    # Base-case projections (inheritance 2045; heir lives in A; A is the transferor's residence)
    proj_a = project_property("A", p, p.inherit_year, heir_occupies=True, transferor_residence=True)
    proj_b = project_property("B", p, p.inherit_year, heir_occupies=False, transferor_residence=False)
    write_csv(os.path.join(OUT_DIR, "projection_property_a_base.csv"), proj_a)
    write_csv(os.path.join(OUT_DIR, "projection_property_b_base.csv"), proj_b)
    out["projections"]["A_base"] = proj_a
    out["projections"]["B_base"] = proj_b
    # Alternative: A reassessed (heir does not occupy)
    proj_a_alt = project_property("A", p, p.inherit_year, heir_occupies=False, transferor_residence=True)
    write_csv(os.path.join(OUT_DIR, "projection_property_a_no_prop19.csv"), proj_a_alt)
    out["projections"]["A_no_prop19"] = proj_a_alt

    # Rent projections for B (informational)
    rent_rows = []
    for y in range(p.base_year, p.end_year + 1):
        n = y - p.base_year
        rent_rows.append({
            "year": y,
            "two_units_rent_controlled_path": r10(grow(p.rent_b_2units, p.controlled_rent_growth, n)),
            "two_units_market_path": r10(grow(p.rent_b_2units, p.market_rent_growth, n)),
            "third_unit_market": r10(grow(p.rent_b_unit3_market, p.market_rent_growth, n)),
            "property_a_market_rent": r10(grow(p.rent_a_market, p.market_rent_growth, n)),
        })
    write_csv(os.path.join(OUT_DIR, "projection_rents.csv"), rent_rows)
    out["projections"]["rents"] = rent_rows

    # Scenarios: base case
    scen_rows = []
    for s in SCENARIOS:
        res = run_scenario(s, p, p.inherit_year, p.hold_years)
        out["scenarios"][s.key] = res
        scen_rows.append({k: v for k, v in res.items() if k not in ("yearly", "details", "description",
                                                                   "sale_at_inheritance_a", "sale_at_inheritance_b")})
        write_csv(os.path.join(OUT_DIR, f"scenario_{s.key}_yearly.csv"), res["yearly"])
    write_csv(os.path.join(ROOT, "data", "scenarios.csv"), scen_rows)

    # Sensitivity: inheritance year x appreciation x portfolio return
    for T in (2040, 2045, 2050):
        for (aa, ab, label) in ((0.02, 0.01, "low appreciation (A 2%, B 1%)"),
                                (0.04, 0.03, "base appreciation (A 4%, B 3%)"),
                                (0.06, 0.05, "high appreciation (A 6%, B 5%)")):
            for ret in (0.05, 0.07, 0.09):
                row = {"inherit_year": T, "appreciation_case": label, "portfolio_return": ret}
                best = None
                for s in SCENARIOS:
                    res = run_scenario(s, p, T, p.hold_years, aa, ab, ret)
                    row[s.key] = res["terminal_wealth_after_tax"]
                    if best is None or res["terminal_wealth_after_tax"] > best[1]:
                        best = (s.key, res["terminal_wealth_after_tax"])
                row["best"] = best[0]
                out["sensitivity"].append(row)
    write_csv(os.path.join(OUT_DIR, "sensitivity.csv"), out["sensitivity"])

    out["estate_tax"] = estate_tax_table(p)
    write_csv(os.path.join(OUT_DIR, "estate_tax_exposure.csv"), out["estate_tax"])

    with open(os.path.join(DOCS_DATA, "model_output.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("Scenarios (base case, inheritance", p.inherit_year, "):")
    for s in SCENARIOS:
        r = out["scenarios"][s.key]
        print(f"  {s.key} {s.name:55s} year-1 cash {r['year1_net_cash']:>10,}  terminal {r['terminal_wealth_after_tax']:>13,}")


if __name__ == "__main__":
    main()
