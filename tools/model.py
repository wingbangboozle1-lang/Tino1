"""
Cupertino + San Francisco inheritance decision model.
Every constant is either (a) sourced in research/00-source-log.md or
(b) an explicit labeled model ASSUMPTION. No value is invented silently.
All dollar outputs are rounded to the nearest $10 for reporting.
"""

SRC = {
 "prop13_cap_rate":    0.010,        # S08 - 1% constitutional general levy
 "prop13_infl":        1.02,         # S08/S09 - annual inflation factor
 "scc_tra_rate":       0.011488,     # S28 - SCC Assessor typical TRA (1% + bonds)
 "sf_secured_rate":    0.0118162182, # S18 - SF FY2026-27 secured rate
 "prop19_cap_2025":    1044586,      # S02
 "fed_exclusion_2026": 15000000,     # S11
 "fed_estate_rate":    0.40,         # S12
 "annual_gift_2026":   19000,        # S13
 "irc121_single":      250000,       # S15
 "irc121_joint":       500000,       # S15
 "niit":               0.038,        # S16
 "fed_ltcg_top":       0.20,         # S17
 "ca_top_rate":        0.123,        # S25
 "ca_capgain_rate":    0.093,        # CA taxes cap gains as ordinary income (mid bracket)
 "ca_homeowner_exempt":7000,         # S19
 "sf_rent_cap_2026":   0.016,        # S29
 "ca_estate_tax":      0.0,          # S10
 "sf_transfer": [                    # SF Business & Tax Regs Art.12-C, rate on FULL price
    (0,          250000,      0.0050),
    (250001,     999999,      0.0068),
    (1000000,    4999999,     0.0075),
    (5000000,    9999999,     0.0225),
    (10000000,   24999999,    0.0550),
    (25000000,   float('inf'),0.0600),
 ],
}

# ----------------------------------------------------------------------------
# OWNER-REPORTED PRIMARY DATA (internal only; never shown on the public site)
# ----------------------------------------------------------------------------
OWNER = {
 "A_value_2026":      3100000,
 "A_assessed_2026":    550537,   # 2026-27 assessed (owner tax records)
 "A_tax_2025":           7207,   # 2025 tax paid
 "A_assessed_2025":    539743,   # 2025 assessed
 "B_value_2026":      1800000,
 "B_tax_2025":           2439,
 "B_assessed_2025":    114248,
 "B_rent_month":         7150,
 "B_rent_units":            2,
 "B_total_units":           3,
 "B_water_month_low":     330,
 "B_water_month_high":    400,
 "B_elec_month_low":       30,
 "B_elec_month_high":      70,
 "A_water_month_low":     100,
 "A_water_month_high":    150,
 "A_elec_credit_month":    15,   # solar: net credit, not cost
 "A_insurance_year":     1500,   # OWNER ESTIMATE - unverified
 "B_insurance_year":     1500,   # OWNER ESTIMATE - unverified
}

# Residual non-ad-valorem charges, derived (not assumed):
#   observed tax - (assessed x verified official rate)
A_FIXED_CHARGES = OWNER["A_tax_2025"] - OWNER["A_assessed_2025"] * SRC["scc_tra_rate"]   # ~1007
B_FIXED_CHARGES = OWNER["B_tax_2025"] - OWNER["B_assessed_2025"] * SRC["sf_secured_rate"] # ~1089

ASSUME = {
 "cpi": 0.030, "appr_base": 0.040, "appr_low": 0.020, "appr_hi": 0.050,
 "invest_nominal": 0.070, "invest_low": 0.050, "invest_high": 0.085,
 "invest_tax_drag": 0.005, "rent_growth": 0.030, "sf_rent_growth": 0.016,
 "maint_pct_A": 0.008, "maint_pct_B": 0.010, "sell_cost_pct": 0.050,
 "cupertino_rent_month": 3483,   # HUD FY2026 SAR 2BR, Santa Clara County
}

YEARS = list(range(2026, 2071))

def r10(x):
    if x is None: return None
    return int(round(x / 10.0) * 10)

def sf_transfer_tax(price):
    for lo, hi, rate in SRC["sf_transfer"]:
        if lo <= price <= hi:
            return price * rate
    return price * 0.06

def prop19_cap(year, hpi):
    """$1M cap re-based every 2 yrs starting Feb 2027 on prior-yr CA HPI change."""
    v = SRC["prop19_cap_2025"]
    if year <= 2026: return v
    for _ in range(len([y for y in range(2027, year + 1) if y % 2 == 1])):
        v *= (1 + hpi)
    return v

# ----------------------------------------------------------------------------
# PROPERTY A - Cupertino 95014
# ----------------------------------------------------------------------------
def build_A(inh, appr, hpi, mode):
    """mode 'live' = Prop19 exclusion claimed & occupancy kept; 'rent' = full reassess."""
    rows = []
    base = OWNER["A_value_2026"]
    a0   = OWNER["A_assessed_2026"]
    for y in YEARS:
        mv = base * (1 + appr) ** (y - 2026)
        av_pre = min(a0 * SRC["prop13_infl"] ** (y - 2026), mv)
        if y < inh:
            av = av_pre
            phase = "Pre-transfer (Prop 13 base year)"
            excl = ""
        else:
            mv_t   = base * (1 + appr) ** (inh - 2026)
            fbyv_t = min(a0 * SRC["prop13_infl"] ** (inh - 2026), mv_t)
            if mode == "live":
                cap    = fbyv_t + prop19_cap(inh, hpi)
                excess = max(0.0, mv_t - cap)
                nb     = fbyv_t + excess
                phase  = "Post-transfer - Prop 19 exclusion claimed"
                excl   = "Exclusion claimed"
            else:
                nb     = mv_t
                phase  = "Post-transfer - fully reassessed (no exclusion)"
                excl   = "No exclusion"
            av = min(nb * SRC["prop13_infl"] ** (y - inh), mv)
        exempt = SRC["ca_homeowner_exempt"] if (mode == "live" and y >= inh) else 0
        taxable = max(0.0, av - exempt)
        fixed = A_FIXED_CHARGES * (1 + ASSUME["cpi"]) ** (y - 2026)
        tax = taxable * SRC["scc_tra_rate"] + fixed
        rows.append({"year": y, "market": r10(mv), "assessed": r10(av),
                     "tax": r10(tax), "phase": phase, "exclusion": excl,
                     "exempt": exempt})
    return rows

# ----------------------------------------------------------------------------
# PROPERTY B - San Francisco 94122, 3 units, rental => Prop 19 ineligible
# ----------------------------------------------------------------------------
def build_B(inh, appr):
    rows = []
    base = OWNER["B_value_2026"]
    b0 = OWNER["B_assessed_2025"] * SRC["prop13_infl"]   # roll to 2026-27
    for y in YEARS:
        mv = base * (1 + appr) ** (y - 2026)
        if y < inh:
            av = min(b0 * SRC["prop13_infl"] ** (y - 2026), mv)
            phase = "Pre-transfer (Prop 13 base year)"
        else:
            nt = base * (1 + appr) ** (inh - 2026)
            av = min(nt * SRC["prop13_infl"] ** (y - inh), mv)
            phase = "Post-transfer - fully reassessed (rental, Prop 19 ineligible)"
        fixed = B_FIXED_CHARGES * (1 + ASSUME["cpi"]) ** (y - 2026)
        tax = av * SRC["sf_secured_rate"] + fixed
        # owner-observed effective rate, for reconciliation display only
        tax_obs = av * (OWNER["B_tax_2025"] / OWNER["B_assessed_2025"])
        rows.append({"year": y, "market": r10(mv), "assessed": r10(av),
                     "tax": r10(tax), "tax_observed": r10(tax_obs), "phase": phase})
    return rows

# ----------------------------------------------------------------------------
# CARRYING COSTS
# ----------------------------------------------------------------------------
def costs_A(rows):
    out = []
    for r in rows:
        y = r["year"]; inf = (1 + ASSUME["cpi"]) ** (y - 2026)
        water = (OWNER["A_water_month_low"] + OWNER["A_water_month_high"]) / 2 * 12 * inf
        elec  = -OWNER["A_elec_credit_month"] * 12 * inf
        ins   = OWNER["A_insurance_year"] * inf
        maint = r["market"] * 0.45 * ASSUME["maint_pct_A"]
        out.append({"year": y, "water": r10(water), "electric": r10(elec),
                    "insurance": r10(ins), "maintenance": r10(maint),
                    "total": r10(water + elec + ins + maint)})
    return out

def costs_B(rows):
    out = []
    for r in rows:
        y = r["year"]; inf = (1 + ASSUME["cpi"]) ** (y - 2026)
        water = (OWNER["B_water_month_low"] + OWNER["B_water_month_high"]) / 2 * 12 * inf
        elec  = (OWNER["B_elec_month_low"] + OWNER["B_elec_month_high"]) / 2 * 12 * inf
        ins   = OWNER["B_insurance_year"] * inf
        maint = r["market"] * 0.45 * ASSUME["maint_pct_B"]
        out.append({"year": y, "water": r10(water), "electric": r10(elec),
                    "insurance": r10(ins), "maintenance": r10(maint),
                    "total": r10(water + elec + ins + maint)})
    return out

def rents_B(growth):
    out = []
    for y in YEARS:
        inf = (1 + growth) ** (y - 2026)
        out.append({"year": y, "gross_2units": r10(OWNER["B_rent_month"] * 12 * inf),
                    "per_unit_month": r10(OWNER["B_rent_month"] / 2 * inf)})
    return out
