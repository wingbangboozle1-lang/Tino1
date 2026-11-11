#!/usr/bin/env python3
"""
Canonical model for the Cupertino & San Francisco inheritance decision hub.
Session arena/944a92cd-tino1. Standard library only.

ALL DISPLAYED FIGURES ARE ROUNDED TO THE NEAREST $10.
Numbers sourced from official pages carry a source tag in the CSV/JSON;
model inputs are labelled ASSUMPTION and are NOT facts.
"""
import json, math, csv

r10 = lambda x: int(round(x / 10.0) * 10)

# ---------- Anchors (official sources listed on the site) ----------
# FHFA HPI 2026Q2 (purchase-only, CA -0.2% y/y, 5-yr +17.31%) https://www.fhfa.gov/document/d/hpi/fhfa-house-price-index-report-2026q2
# BLS CPI Sept 2026 3.7% y/y https://www.bls.gov/news.release/cpi.nr0.htm
# FOMC 2026-10-28: hold 3.75-4.00% https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm
# Treasury daily par yield 2026-11-04: 10Y 4.90% https://home.treasury.gov/ (par yield curve) [via search summary]
# Prop 19 cap $1,044,586 transfers 2/16/2025-2/15/2027 https://www.boe.ca.gov/prop19/ (LTA 2025/009)
# SCC FY2025-26 rate book components summed 1.1636% https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf
# SF secured tax FY2026-27 1.18162182% https://sftreasurer.org/property/secured-property-taxes
# Prop 13 2% cap, RTC 51; Fan explicit user-supplied anchors below.

USER = dict(
    a_value_2026   = 3_100_000,   # user estimate Nov 2026, not an appraisal
    b_value_2026   = 1_800_000,   # user estimate Nov 2026, not an appraisal
    a_assessed_2026= 550_540,     # USER-SUPPLIED, $10-rounded (was non-rounded; privacy)
    b_assessed_2025= 114_250,     # USER-SUPPLIED, $10-rounded; provenance flagged
    a_tax_2025     = 7_210,       # USER-SUPPLIED, $10-rounded
    b_tax_2025     = 2_440,       # USER-SUPPLIED, $10-rounded
    b_rent_2026    = 85_800,      # USER-SUPPLIED $7,150/mo combined (2 units)
    a_water        = 125 * 12,    # user range $100-150 -> midpoint $125/mo
    a_elec_net     = -15 * 12,    # user: solar credit ~$10-20/mo -> -$15/mo
    a_dres         = 1_500,       # user estimate, flagged (no quote)
    b_water        = 365 * 12,    # user range $330-400 -> midpoint
    b_elec         = 50 * 12,     # user range $30-70 -> midpoint
    b_dres         = 2_600,       # ASSUMPTION for 3-unit landlord policy, flagged (user said ~$1,500; CDI tool unreadable)
    a_maint        = 6_000,       # ASSUMPTION
    b_maint        = 12_000,      # ASSUMPTION
)

# ---------- Model parameters (ASSUMPTIONS, labelled on site) ----------
P = dict(
    a_appr   = 0.035,   # A nominal appreciation (anchor: FHFA CA 5-yr 17.3%)
    b_appr   = 0.030,   # B nominal appreciation (anchor: FHFA, SF metro ~-2.4% y/y; long-run positive)
    cpi      = 0.025,   # baseline long-run CPI (CURRENT 3.7% y/y - see flagged; 2% Fed target long-run)
    prop13   = 0.02,    # Prop 13 annual cap (RTC 51)
    p19_cap0 = 1_044_590, # 2025-27 Prop 19 cap, $10-rounded (BOE LTA 2025/009)
    p19_cap_growth = 0.02, # cap indexed by FHFA HPI every 2 yrs; modelled 2%/yr
    a_adval  = 0.011636, # SCC composite FY2025-26 (derived, flagged X01)
    b_adval  = 0.011816, # SF FY2026-27 (SF Treasurer)
    a_direct0= 930,      # A direct charges 2025 derived (flagged X02), grows 3%
    b_fixed0 = 1_000,    # B fixed parcel charges (assumption, flagged X03), grows 3%
    ins_growth = 0.05,
    rent_controlled = 0.016,   # SF allowable increase 2026-27 (sf.gov)
    rent_market     = 0.03,
    portfolio_ret   = 0.07,     # nominal gross (flagged vs current 10Y ~4.9%; see scenarios)
    index_excl      = 0.025,    # federal estate exclusion indexation (Rev Proc 2025-32; 2026 $15,000,000)
    estate_excl_2026= 15_000_000,
    sell_cost_a     = 0.050,    # agent ~4.9% + SCC transfer tax $1.10/$1,000
    sell_cost_b     = 0.0575,   # agent + SF transfer tax 0.75% tier ($5-25/$1,000 >$5M? no: $2.50-$7.50/$1,000; $2.5M-$5M = $5.75/$1,000 -> 0.575%! recheck)
)

# Correct SF transfer tax tiers (R&TC 11911/11912, SF): $5 per $1,000 ($250k-$999,999),
# $5.75 ($1M-<5M)? Officially: $5.00 ($1M-$5M?) Actually SF: 0.5% $250k-$1M; 0.75% $1M-$5M -> $7.50 per $1,000. 0.75% used for B sale. Flagged.
P['sell_cost_b'] = 0.049 + 0.0075 + 0.0011  # agent 4.9% + SF 0.75% + note SCC does not apply

# income-tax rates for after-tax baseline (ASSUMPTIONS, high-income CA heir)
IT = dict(gains=0.371, recapture=0.411, estate_marg=0.40)

INH_YEAR = 2045
END_YEAR = 2060

def a_val(t): return USER['a_value_2026'] * (1 + P['a_appr']) ** (t - 2026)
def b_val(t): return USER['b_value_2026'] * (1 + P['b_appr']) ** (t - 2026)
def a_prop13(t): return USER['a_assessed_2026'] * (1 + P['prop13']) ** (t - 2026)
def b_prop13(t): return USER['b_assessed_2025'] * (1 + P['prop13']) ** (t - 2025)
def p19_cap(t): return P['p19_cap0'] * (1 + P['p19_cap_growth']) ** (t - 2026)
def estate_excl(t): return P['estate_excl_2026'] * (1 + P['index_excl']) ** (t - 2026)
def a_direct(t): return P['a_direct0'] * 1.03 ** (t - 2025)
def b_fixed(t):  return P['b_fixed0']  * 1.03 ** (t - 2026)
def insurance_a(t): return USER['a_dres'] * (1 + P['ins_growth']) ** (t - 2026)
def insurance_b(t): return USER['b_dres'] * (1 + P['ins_growth']) ** (t - 2026)
def water_a(t): return USER['a_water'] * 1.03 ** (t - 2026)
def elec_a(t):  return USER['a_elec_net'] * 1.03 ** (t - 2026)
def water_b(t): return USER['b_water'] * 1.03 ** (t - 2026)
def elec_b(t):  return USER['b_elec'] * 1.03 ** (t - 2026)
def maint_a(t): return USER['a_maint'] * (1 + P['cpi']) ** (t - 2026)
def maint_b(t): return USER['b_maint'] * (1 + P['cpi']) ** (t - 2026)
def rent_controlled_monthly_2026(): return USER['b_rent_2026'] / 12
def rent_b_controlled(t): return USER['b_rent_2026'] * (1 + P['rent_controlled']) ** (t - 2026)
def rent_b_market(annual, t):  return annual * (1 + P['rent_market']) ** (t - 2026)
MKT_UNIT_2026 = 3_200 * 12   # ASSUMPTION: market rent for the vacant 3rd unit, $10-rounded

def a_tax_bill(t, transferred=False, live_in=True):
    if not transferred:
        return P['a_adval'] * a_prop13(t) + a_direct(t)
    fbyv = a_prop13(t)
    fmv  = a_val(t)
    if live_in:
        taxable = max(fbyv, fmv - p19_cap(t))
    else:
        taxable = fmv
    return P['a_adval'] * taxable + a_direct(t)

def b_tax_bill(t, transferred=False):
    if not transferred:
        return P['b_adval'] * b_prop13(t) + b_fixed(t)
    return P['b_adval'] * b_val(t) + b_fixed(t)

# ---------- Build baseline tables ----------
rows = []
for t in range(2026, 2,060):
    inh = (t >= INH_YEAR)
    rows.append(dict(
        year=t,
        a_value=r10(a_val(t)), a_assessed=r10(a_prop13(t) if not inh else max(a_prop13(t), a_val(t) - p19_cap(t))),
        a_tax=r10(a_tax_bill(t, inh, True) if t >= INH_YEAR else a_tax_bill(t, False)),
        a_tax_nolive=r10(a_tax_bill(t, inh, False)) if t >= INH_YEAR else None,
        b_value=r10(b_val(t)), b_assessed=r10(b_prop13(t) if not inh else b_val(t)),
        b_tax=r10(b_tax_bill(t, inh)),
        b_rent=r10(rent_b_controlled(t)),
        estate_excl=r10(estate_excl(t)),
        p19_cap=r10(p19_cap(t)),
    ))

json.dump(rows, open('/home/user/Tino1/integrated/baseline_rows.json','w'), indent=1)
with open('/home/user/Tino1/integrated/baseline_rows.csv','w',newline='') as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)

# ---------- Black-swan regimes: terminal wealth, 2045 inheritance, evaluated 2060 ----------
# Wealth = after-tax liquidation value of all real estate + investment account.
# NOMINAL, excludes income tax on rents (noted on site); includes capital-gains tax vs stepped-up basis.
REGIMES = {
    "baseline":  dict(appr_a=0.035, appr_b=0.030, ret=0.070, cpi=0.025, rent_m=0.030),
    "stagflation":dict(appr_a=0.045, appr_b=0.040, ret=0.040, cpi=0.080, rent_m=0.065),  # 1970s replay: nominal homes keep pace w/ CPI, real returns ~0
    "gfc":       dict(appr_a=-0.075, appr_b=-0.070, ret=-0.10, cpi=0.015, rent_m=0.005, shock_years=4, post_appr=0.045, post_ret=0.090),  # 2008-12 style crash then recovery
    "japan":     dict(appr_a=0.005, appr_b=0.000, ret=0.020, cpi=0.005, rent_m=0.000),
    "deflation": dict(appr_a=-0.020, appr_b=-0.025, ret=-0.010, cpi=-0.015, rent_m=-0.010),
    "energyshock":dict(appr_a=0.020, appr_b=0.015, ret=0.050, cpi=0.045, rent_m=0.030),   # 2026 status quo extends
    "productivity":dict(appr_a=0.050, appr_b=0.045, ret=0.105, cpi=0.020, rent_m=0.035),  # AI/productivity boom
}

def path(appr, shock_years, post_appr, t0, t1):
    out = {}
    v = 1.0
    for t in range(t0, t1 + 1):
        rate = appr if (not shock_years or t < t0 + shock_years) else post_appr
        v *= (1 + rate)
        out[t] = v
    return out

def terminal_wealth(reg_key, scenario):
    """
    Terminal wealth (nominal, USD, 2045 inheritance evaluated at end-2060).
    Components: investment account balance (deposit of S1 sale proceeds + all annual
    net cash flows) + liquidation value of retained real estate, net of selling
    costs and capital-gains tax on post-inheritance appreciation (stepped-up basis).
    Housing consumption is NOT monetised. Income tax on rents/ordinary income is
    excluded (applies to all scenarios); capital-gains tax is included.
    """
    R = REGIMES[reg_key]
    base_a, base_b = a_val(INH_YEAR), b_val(INH_YEAR)
    shock, post_appr, post_ret = R.get('shock_years'), R.get('post_appr', R['appr_a']), R.get('post_ret', R['ret'])
    pa = path(R['appr_a'], shock, post_appr, INH_YEAR, END_YEAR)
    pb = path(R['appr_b'], shock, post_appr, INH_YEAR, END_YEAR)

    invest = base_a * (1 - P['sell_cost_a']) if scenario == 'S1' else 0.0
    rent, mkt = USER['b_rent_2026'], MKT_UNIT_2026
    a_owned = scenario in ('S2', 'S3')
    for t in range(INH_YEAR, END_YEAR + 1):
        if t > INH_YEAR:
            rent *= (1 + P['rent_controlled'])
            mkt  *= (1 + R['rent_m'])
            r = R['ret'] if (not shock or t <= INH_YEAR + shock) else post_ret
            invest *= (1 + r)
        flow = rent  # two controlled units, all scenarios
        if scenario == 'S2':
            flow += mkt                                  # 3rd unit rented at market
        if scenario == 'S3':
            flow += a_rent_income(t, R) - (a_tax_bill(t, True, False) + water_a(t) + insurance_a(t) + maint_a(t) + elec_a(t))
        if scenario == 'S2':
            flow -= (a_tax_bill(t, True, True) + water_a(t) + insurance_a(t) + maint_a(t) + elec_a(t))
        flow -= b_tax_bill(t, True) + water_b(t) + elec_b(t) + insurance_b(t) + maint_b(t)
        invest += flow
    a_end = a_val(INH_YEAR) * pa[END_YEAR]
    b_end = b_val(INH_YEAR) * pb[END_YEAR]
    wealth = invest
    if a_owned:
        wealth += a_end * (1 - P['sell_cost_a']) - max(0.0, a_end - base_a) * IT['gains']
    wealth += b_end * (1 - P['sell_cost_b']) - max(0.0, b_end - base_b) * IT['gains']
    return wealth

def a_rent_income(t, R):
    base = 6_390 * 12   # ASSUMPTION: $6,390/mo 95014 market rent proxy (HUD small-area FMR based, flagged X19)
    return base * (1 + R['rent_m']) ** (t - 2026)

print("=== 2045 inheritance key figures (baseline) ===")
fbyv = a_prop13(INH_YEAR); fmv_a = a_val(INH_YEAR); fmv_b = b_val(INH_YEAR); cap = p19_cap(INH_YEAR)
print(f"A FBYV 2045      : {r10(fbyv):>12,}")
print(f"A FMV 2045       : {r10(fmv_a):>12,}")
print(f"B FMV 2045       : {r10(fmv_b):>12,}")
print(f"Prop19 cap 2045  : {r10(cap):>12,}")
print(f"A assessed live-in: {r10(max(fbyv, fmv_a - cap)):>12,}")
print(f"A assessed full   : {r10(fmv_a):>12,}")
print(f"A bill live-in    : {r10(a_tax_bill(INH_YEAR, True, True)):>12,}")
print(f"A bill no Prop19  : {r10(a_tax_bill(INH_YEAR, True, False)):>12,}")
print(f"B bill 2045       : {r10(b_tax_bill(INH_YEAR, True)):>12,}")
print(f"Estate exclusion 2045: {r10(estate_excl(INH_YEAR)):>12,}")
print(f"Estate exclusion 2050: {r10(estate_excl(2050)):>12,}")
print(f"Estate exclusion 2055: {r10(estate_excl(2055)):>12,}")

print("\n=== Terminal wealth 2060 by regime (NOMINAL, USD) ===")
print(f"{'Regime':<14}{'S1 Sell':>16}{'S2 Live A':>16}{'S3 Rent A':>16}")
bs = {}
for k in REGIMES:
    vals = [terminal_wealth(k, s) for s in ('S1', 'S2', 'S3')]
    bs[k] = [r10(v) for v in vals]
    print(f"{k:<14}{bs[k][0]:>16,}{bs[k][1]:>16,}{bs[k][2]:>16,}")
json.dump(bs, open('/home/user/Tino1/integrated/blackswan_results.json','w'), indent=1)
