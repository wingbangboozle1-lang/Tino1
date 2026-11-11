#!/usr/bin/env python3
"""
Inheritance decision model — session 4395771d.  Standard library only.

Run:  python3 verify-4395771d/model/model.py
Writes CSV/JSON files to verify-4395771d/model/out/.

Three kinds of numbers are kept strictly apart:
  OWNER    - supplied by the owner, shown rounded (never confirmed against an official record,
             because looking the parcels up would identify them)
  VERIFIED - read on an official page on 2026-11-11 (see ../facts/*.csv for link and wording)
  ASSUME   - a modelling choice.  Every one is listed in ASSUME below and on the site.

"Property A" = the Cupertino home that will be inherited.
"Property B" = the San Francisco three-unit building the heir ALREADY owns.
Because B is already the heir's, a parent's death does not change its ownership:
it is not reassessed and it is not part of the estate.  It appears here only where
the choice made for A changes B's cash flow (who lives in B's third unit).
"""
import csv, json, os, math, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

def r10(x):
    """Round to the nearest $10 (halves up)."""
    return int(math.floor(x / 10.0 + 0.5) * 10)

# ----------------------------------------------------------------------------- inputs
OWNER = dict(
    a_value_2026=3_100_000,     # owner's estimate, Nov 2026
    a_assessed_2026=550_540,    # rounded to $10
    a_assessed_2025=539_740,    # rounded to $10
    a_tax_2025=7_210,           # rounded to $10
    a_water_month=125,          # midpoint of $100-150
    a_insurance_year=1_500,     # owner's rough figure - NOT confirmed (facts K04)
    b_value_2026=1_800_000,
    b_assessed_2025=114_250,
    b_tax_2025=2_440,
    b_rent_month_2units=7_150,
    b_water_month=365,          # midpoint of $330-400
    b_electric_month=50,        # midpoint of $30-70
    b_insurance_year=1_500,     # owner's rough figure - NOT confirmed (facts K05)
)

VERIFIED = dict(
    a_rate=0.011636,            # facts L11 (derived from L06-L10, FY2025-26 rate book)
    b_rate=0.0118162182,        # facts L01 (FY2026-27)
    prop13_cap=0.02,            # facts C14
    hox=7_000,                  # facts C18
    p19_allowance_2025=1_044_586,   # facts C03 (transfers Feb 16 2025 - Feb 15 2027)
    p19_next_adjust=2027,       # facts C04/P06: every other February 16
    excl_2026=15_000_000,       # facts F01
    excl_2027=15_480_000,       # facts F03
    estate_rate=0.40,           # top federal estate tax rate (26 U.S.C. 2001(c))
    a_hud_rent_4br_month=6_390, # facts L15 (HUD FY2026, 40th percentile, 4 bedrooms)
    sf_rent_cap_share=0.60,     # SF allowable increase is set at 60% of CPI (L13: 1.6% / 1.4%)
    depreciation_years=27.5,    # facts F17
    sec121_single=250_000,      # facts F15
    tbill_now=0.0430, t10_now=0.0498,   # facts E02
)

ASSUME = dict(
    # --- baseline economy (constant rates; the black-swan section replaces these with real history)
    inflation=0.025,        # CBO projects 2.3% from 2028 (E03); California averaged 2.6% in 2000-2019
    a_apprec=0.040,         # San Jose metro: 6.7%/yr 1976-2025, 4.7%/yr 2015-2025, +0.3% in 2025 (E05, E07)
    b_apprec=0.035,         # San Francisco metro division: 6.5%/yr 1976-2025, 3.2%/yr 2015-2025 (E06, E07)
    ca_apprec=0.040,        # statewide index that drives the Prop 19 allowance (C04)
    ca_change_2026=0.013,   # statewide change for calendar 2026 is not published yet; 2025 was +1.3% (data/hpi_fhfa_annual.csv)
    stock_return=0.070,     # S&P 500 with dividends earned 10.0%/yr 1928-2025 (E08); 7.0% is deliberately lower
    dividend_yield=0.015,
    cash_return=0.034,      # CBO: federal funds rate about 3.4% (E03 source); 3-month Treasury is 4.30% today (E02)
    rent_growth_over_cpi=0.005,
    # --- taxes on the heir (income not supplied; rates below sit in the middle-upper brackets of F10-F14, C21-C22)
    tax_ordinary=0.371,     # 24% federal + 9.3% California + 3.8% net investment income tax
    tax_gains=0.281,        # 15% federal + 9.3% California + 3.8%
    tax_recapture=0.381,    # 25% federal maximum + 9.3% + 3.8%
    # --- property A costs not supplied by the owner
    a_electric_after_solar_year=1_800,  # 2026 dollars, once the 20-year net-metering term ends (K01-K03)
    a_solar_credit_ends=2040,      # unknown (K03); assumed over by the earliest inheritance year
    a_maintenance_year=8_000,      # 2026 dollars
    a_building_share=0.30,         # share of value that is building (depreciable) rather than land
    a_rent_vacancy=0.05,
    a_rent_mgmt=0.06,
    a_landlord_insurance_mult=1.25,
    # --- property B
    b_maintenance_year=12_000,     # 2026 dollars
    b_third_unit_rent_month=3_580, # half of the present two-unit rent, rounded to $10; 2026 dollars
    b_third_unit_vacancy=0.05,
    b_third_unit_cost_share=0.10,
    b_rent_controlled=True,        # not confirmed (L14); shown both ways on the site
    # --- cost growth above inflation
    insurance_over_cpi=0.02,
    utilities_over_cpi=0.02,
    # --- transactions
    selling_cost=0.06,
    months_to_sell=6,
    other_assets_at_T=1_000_000,   # illustrative inherited cash/securities that fund the carrying costs
)

T_YEARS = (2040, 2045, 2050)
HORIZONS = (10, 20, 30)
END_YEAR = 2080

# ----------------------------------------------------------------------------- data
def _load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        rows = [r for r in csv.reader(l for l in f if not l.startswith('#'))]
    return rows[0], rows[1:]

def load_history():
    h, d = _load('hpi_fhfa_annual.csv')
    hpi = {int(r[0]): {h[i]: (float(r[i]) if r[i] else None) for i in range(1, 4)} for r in d}
    h, d = _load('returns_us_annual.csv')
    ret = {int(r[0]): {h[i]: float(r[i]) / 100 for i in range(1, 5)} for r in d}
    _, d = _load('cpi_us_december.csv')
    cpi = {int(r[0]): float(r[1]) for r in d}
    _, d = _load('ca_cpi_prop13_factors.csv')
    p13 = {int(r[0][:4]): float(r[2]) for r in d}          # keyed by first year of the roll year
    _, d = _load('japan_annual.csv')
    jp = {int(r[0]): dict(home=(float(r[1]) / 100 if r[1] else None), nikkei=float(r[2]),
                          cpi=(float(r[3]) if r[3] else None)) for r in d}
    return hpi, ret, cpi, p13, jp

HPI, RET, CPI, P13, JP = load_history()

def hist_year(y, local=True):
    """One historical calendar year as a dict of rates.  local=True uses the San Jose / San Francisco /
    California FHFA indexes (1977-2025); local=False uses the national home series (1929-2025)."""
    infl = CPI[y] / CPI[y - 1] - 1
    if local:
        a = HPI[y]['san_jose'] / HPI[y - 1]['san_jose'] - 1
        b = HPI[y]['san_francisco'] / HPI[y - 1]['san_francisco'] - 1
        ca = HPI[y]['california'] / HPI[y - 1]['california'] - 1
        fac = P13.get(y + 1, min(1.02, 1 + infl))      # factor used on the next January 1
    else:
        a = b = ca = RET[y]['home_us']
        fac = P13.get(y + 1) if (y + 1) in P13 else min(1.02, 1 + infl)
    return dict(infl=infl, a=a, b=b, ca=ca, stock=RET[y]['sp500'], cash=RET[y]['tbill'], p13=fac, src=y)

def base_year():
    A = ASSUME
    return dict(infl=A['inflation'], a=A['a_apprec'], b=A['b_apprec'], ca=A['ca_apprec'],
                stock=A['stock_return'], cash=A['cash_return'], p13=1 + VERIFIED['prop13_cap'], src=None)

def baseline_path(**over):
    y = base_year(); y.update(over)
    y['p13'] = min(1.02, 1 + y['infl'])
    return {t: dict(y) for t in range(2027, END_YEAR + 1)}

def shock_after(T, seq):
    """Baseline until the inheritance year T, then the given list of historical years, then baseline again."""
    p = baseline_path()
    for i, yr in enumerate(seq):
        if T + 1 + i <= END_YEAR:
            p[T + 1 + i] = dict(yr)
    return p

def rotation_path(start, first, last, local):
    """The real record first..last played in order from `start`, wrapping round, laid over 2027 onward."""
    n = last - first + 1
    return {t: hist_year(first + (start - first + (t - 2027)) % n, local) for t in range(2027, END_YEAR + 1)}

def japan_seq(n=30):
    out = []
    for y in range(1991, 1991 + n):
        j = JP[y]
        infl = j['cpi'] / JP[y - 1]['cpi'] - 1
        out.append(dict(infl=infl, a=j['home'], b=j['home'], ca=j['home'],
                        stock=j['nikkei'] / JP[y - 1]['nikkei'] - 1, cash=max(0.0, infl),
                        p13=min(1.02, 1 + infl), src=y))
    return out

# ----------------------------------------------------------------------------- indexes along a path
def build_indexes(path):
    """Cumulative price level and market values for every year 2026..END_YEAR along one path."""
    cpi = {2026: 1.0}; av = {2026: float(OWNER['a_value_2026'])}; bv = {2026: float(OWNER['b_value_2026'])}
    allow = {2026: float(VERIFIED['p19_allowance_2025'])}
    for t in range(2027, END_YEAR + 1):
        y = path[t]
        cpi[t] = cpi[t - 1] * (1 + y['infl'])
        av[t] = av[t - 1] * (1 + y['a'])
        bv[t] = bv[t - 1] * (1 + y['b'])
        # Prop 19 allowance: every other February 16 from 2027, by the PRIOR calendar year's statewide change (C04)
        if (t - VERIFIED['p19_next_adjust']) % 2 == 0 and t >= VERIFIED['p19_next_adjust']:
            prior = path[t - 1]['ca'] if (t - 1) in path else ASSUME['ca_change_2026']
            allow[t] = allow[t - 1] * (1 + prior)
        else:
            allow[t] = allow[t - 1]
    return cpi, av, bv, allow

def factored(base, start_year, year, path):
    """Prop 13: a base value carried from start_year to year with each January's factor (never above 2%)."""
    v = float(base)
    for t in range(start_year + 1, year + 1):
        v *= path[t - 1]['p13'] if (t - 1) in path else 1.02      # 2026-27 factor is 1.02 (facts C15)
    return v

def exclusion(year, cpi):
    """Federal basic exclusion: statutory 2026 and 2027 figures, then indexed with the path's price level."""
    if year <= 2026: return float(VERIFIED['excl_2026'])
    if year == 2027: return float(VERIFIED['excl_2027'])
    return VERIFIED['excl_2027'] * cpi[year - 1] / cpi[2026]

def derive_direct_charges():
    """Fixed charges on each 2025 bill = bill minus the ad valorem part (documented on the site as 'derived')."""
    a = OWNER['a_tax_2025'] - VERIFIED['a_rate'] * (OWNER['a_assessed_2025'] - VERIFIED['hox'])
    b = OWNER['b_tax_2025'] - VERIFIED['b_rate'] * OWNER['b_assessed_2025']
    return a, b

# ----------------------------------------------------------------------------- Prop 19
def prop19(T, path, idx):
    cpi, av, bv, allow = idx
    fbyv = factored(OWNER['a_assessed_2026'], 2026, T, path)
    fmv = av[T]
    cap = fbyv + allow[T]
    new_taxable = fbyv if fmv <= cap else fbyv + (fmv - cap)
    return dict(fmv=fmv, fbyv=fbyv, allowance=allow[T], value_cap=cap,
                taxable_move_in=new_taxable, taxable_no_move_in=fmv)

# ----------------------------------------------------------------------------- investment account
class Account:
    """A taxable investment account with cost basis.  Dividends/interest are taxed every year;
    growth is taxed only when money is taken out or at the final valuation."""
    def __init__(self, value, mix_stock=1.0):
        self.v = float(value); self.basis = float(value); self.mix = mix_stock

    def grow(self, y):
        A = ASSUME
        s = self.v * self.mix; c = self.v * (1 - self.mix)
        div = s * A['dividend_yield']
        price = s * (y['stock'] - A['dividend_yield'])
        interest = c * y['cash']
        tax = div * A['tax_gains'] + interest * A['tax_ordinary']
        self.v += div + price + interest - tax
        self.basis += div + interest - tax
        if self.v < 0: self.basis = self.v

    def flow(self, amount):
        if amount >= 0:
            self.v += amount; self.basis += amount; return
        need = -amount
        if self.v <= 0:
            self.v -= need; self.basis = self.v; return
        gain_share = max(0.0, 1 - self.basis / self.v)
        gross = need / (1 - ASSUME['tax_gains'] * gain_share)
        if gross > self.v:                       # account exhausted: the rest is borrowed from future wealth
            net_available = self.v * (1 - ASSUME['tax_gains'] * gain_share)
            self.v = -(need - net_available); self.basis = self.v; return
        self.basis -= gross * (self.basis / self.v)
        self.v -= gross

    def after_tax(self):
        if self.v <= 0: return self.v
        return self.v - ASSUME['tax_gains'] * max(0.0, self.v - self.basis)

# ----------------------------------------------------------------------------- the three choices
def run_option(option, T, path, idx, mix=1.0, horizon=30, detail=False):
    """option: 'move_in' | 'rent_out' | 'sell'.  Returns after-tax wealth at each horizon and yearly rows."""
    A, V, O = ASSUME, VERIFIED, OWNER
    cpi, av, bv, allow = idx
    p19 = prop19(T, path, idx)
    a_dc0, _ = derive_direct_charges()
    acct = Account(A['other_assets_at_T'] * cpi[T], mix)
    rows = []; wealth = {}
    basis_a = p19['fmv']                         # stepped-up basis (facts F08)
    depreciation_taken = 0.0; suspended_loss = 0.0
    holds_a = option != 'sell'
    if option == 'sell':
        # carrying cost from death to sale: taxed on the full date-of-death value because the heir did not move in (C10)
        m = A['months_to_sell'] / 12.0
        carry = m * (p19['fmv'] * V['a_rate'] + a_dc0 * cpi[T]
                     + O['a_insurance_year'] * cpi[T] + A['a_maintenance_year'] * cpi[T] + O['a_water_month'] * 12 * cpi[T])
        proceeds = p19['fmv'] * (1 - A['selling_cost'])
        acct.flow(proceeds - carry)              # sale at about the stepped-up basis: no taxable gain (F19)
    taxable0 = p19['taxable_move_in'] if option == 'move_in' else p19['taxable_no_move_in']
    ins_idx = 1.0; util_idx = 1.0
    for t in range(2027, T + 1):
        ins_idx *= 1 + path[t]['infl'] + A['insurance_over_cpi']
        util_idx *= 1 + path[t]['infl'] + A['utilities_over_cpi']
    third_rent = A['b_third_unit_rent_month'] * 12 * math.prod(
        1 + path[t]['infl'] + A['rent_growth_over_cpi'] for t in range(2027, T + 1))
    a_rent = V['a_hud_rent_4br_month'] * 12 * math.prod(
        1 + path[t]['infl'] + A['rent_growth_over_cpi'] for t in range(2027, T + 1))
    for k in range(1, horizon + 1):
        t = T + k
        y = path[t]
        ins_idx *= 1 + y['infl'] + A['insurance_over_cpi']
        util_idx *= 1 + y['infl'] + A['utilities_over_cpi']
        a_rent *= 1 + y['infl'] + A['rent_growth_over_cpi']
        third_rent *= 1 + (y['infl'] * V['sf_rent_cap_share'] if A['b_rent_controlled'] and k > 1
                           else y['infl'] + A['rent_growth_over_cpi'])
        acct.grow(y)
        row = dict(year=t)
        net = 0.0
        if holds_a:
            fb = factored(taxable0, T, t, path)
            taxable = min(fb, av[t])              # temporary reduction when market value is below the factored value
            hox = V['hox'] if option == 'move_in' else 0
            ptax = max(0.0, taxable - hox) * V['a_rate'] + a_dc0 * cpi[t]
            maint = A['a_maintenance_year'] * cpi[t]
            if option == 'move_in':
                ins = O['a_insurance_year'] * ins_idx
                water = O['a_water_month'] * 12 * util_idx
                elec = A['a_electric_after_solar_year'] * util_idx if t >= A['a_solar_credit_ends'] else 0.0
                rent_in = third_rent * (1 - A['b_third_unit_vacancy'])
                rent_cost = third_rent * A['b_third_unit_cost_share']
                income_tax = max(0.0, rent_in - rent_cost) * A['tax_ordinary']
                net = rent_in - rent_cost - income_tax - ptax - ins - water - elec - maint
                row.update(a_market=av[t], a_assessed=taxable, a_property_tax=ptax, a_insurance=ins, a_water=water,
                           a_electricity=elec, a_maintenance=maint, rent_received=rent_in, income_tax=income_tax)
            else:
                ins = O['a_insurance_year'] * A['a_landlord_insurance_mult'] * ins_idx
                rent_in = a_rent * (1 - A['a_rent_vacancy'])
                mgmt = rent_in * A['a_rent_mgmt']
                dep = basis_a * A['a_building_share'] / V['depreciation_years'] if k <= 28 else 0.0
                taxable_income = rent_in - mgmt - ptax - ins - maint - dep
                if taxable_income >= 0:
                    used = min(suspended_loss, taxable_income); suspended_loss -= used
                    income_tax = (taxable_income - used) * A['tax_ordinary']
                else:
                    suspended_loss += -taxable_income; income_tax = 0.0
                depreciation_taken += dep
                net = rent_in - mgmt - ptax - ins - maint - income_tax
                row.update(a_market=av[t], a_assessed=taxable, a_property_tax=ptax, a_insurance=ins, a_water=0.0,
                           a_electricity=0.0, a_maintenance=maint, rent_received=rent_in, income_tax=income_tax)
        acct.flow(net)
        # value of A if it were sold at the end of this year
        house_net = 0.0
        if holds_a:
            sale = av[t] * (1 - A['selling_cost'])
            gain = sale - basis_a
            if option == 'move_in':
                gain_taxed = max(0.0, gain - (V['sec121_single'] if k >= 2 else 0))
                tax_on_sale = gain_taxed * A['tax_gains']
            else:
                total_gain = gain + depreciation_taken            # depreciation lowers the basis
                if total_gain <= 0:
                    tax_on_sale = 0.0
                else:
                    recap = min(depreciation_taken, total_gain)
                    tax_on_sale = recap * A['tax_recapture'] + (total_gain - recap) * A['tax_gains']
                tax_on_sale = max(0.0, tax_on_sale - suspended_loss * A['tax_ordinary'])
            house_net = sale - tax_on_sale
        total = acct.after_tax() + house_net
        row.update(net_cash_flow=net, account=acct.v, house_after_sale=house_net, wealth_after_tax=total,
                   wealth_2026_dollars=total / cpi[t])
        rows.append(row)
        if k in HORIZONS:
            wealth[k] = dict(nominal=total, real=total / cpi[t])
    return dict(wealth=wealth, rows=rows, prop19=p19)

OPTIONS = (('sell', 1.0, 'Sell and invest in a stock index fund'),
           ('sell', 0.6, 'Sell and invest 60% stocks / 40% cash'),
           ('sell', 0.0, 'Sell and hold cash / savings'),
           ('rent_out', 1.0, 'Keep and rent out'),
           ('move_in', 1.0, 'Move in (Prop 19) and rent the San Francisco third unit'))
OPT_KEYS = ('sell_stocks', 'sell_6040', 'sell_cash', 'rent_out', 'move_in')

def compare(T, path, horizon=30):
    idx = build_indexes(path)
    res = {}
    for key, (opt, mix, _) in zip(OPT_KEYS, OPTIONS):
        res[key] = run_option(opt, T, path, idx, mix=mix, horizon=horizon)
    return res, idx

# ----------------------------------------------------------------------------- outputs
def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

def main():
    summary = {'assumptions': ASSUME, 'verified': VERIFIED, 'owner': OWNER}
    base = baseline_path()
    idx = build_indexes(base)
    cpi, av, bv, allow = idx
    a_dc, b_dc = derive_direct_charges()
    summary['derived_direct_charges_2025'] = dict(a=r10(a_dc), b=r10(b_dc))

    # ---- 1. status-quo projection 2026-2076 (no inheritance yet): both properties, every cost line
    rows = []; ins_i = util_i = 1.0
    for t in range(2026, 2077):
        if t > 2026:
            ins_i *= 1 + base[t]['infl'] + ASSUME['insurance_over_cpi']
            util_i *= 1 + base[t]['infl'] + ASSUME['utilities_over_cpi']
        a_ass = factored(OWNER['a_assessed_2026'], 2026, t, base)
        b_ass = factored(OWNER['b_assessed_2025'], 2025, t, base)
        a_tax = (a_ass - VERIFIED['hox']) * VERIFIED['a_rate'] + a_dc * cpi[t]
        b_tax = b_ass * VERIFIED['b_rate'] + b_dc * cpi[t]
        b_rent = OWNER['b_rent_month_2units'] * 12 * math.prod(
            1 + (base[u]['infl'] * VERIFIED['sf_rent_cap_share'] if ASSUME['b_rent_controlled']
                 else base[u]['infl'] + ASSUME['rent_growth_over_cpi']) for u in range(2027, t + 1))
        a_el = ASSUME['a_electric_after_solar_year'] * util_i if t >= ASSUME['a_solar_credit_ends'] else 0
        rows.append([t, r10(av[t]), r10(a_ass), r10(a_tax), r10(OWNER['a_insurance_year'] * ins_i),
                     r10(OWNER['a_water_month'] * 12 * util_i), r10(a_el), r10(ASSUME['a_maintenance_year'] * cpi[t]),
                     r10(bv[t]), r10(b_ass), r10(b_tax), r10(OWNER['b_insurance_year'] * ins_i),
                     r10(OWNER['b_water_month'] * 12 * util_i), r10(OWNER['b_electric_month'] * 12 * util_i),
                     r10(ASSUME['b_maintenance_year'] * cpi[t]), r10(b_rent), r10(allow[t]), r10(exclusion(t, cpi))])
    write_csv('projection_status_quo.csv',
              ['year', 'a_market_value', 'a_assessed_value', 'a_property_tax', 'a_insurance', 'a_water', 'a_electricity',
               'a_maintenance', 'b_market_value', 'b_assessed_value', 'b_property_tax', 'b_insurance', 'b_water',
               'b_electricity', 'b_maintenance', 'b_rent_two_units', 'prop19_allowance', 'federal_exclusion'], rows)
    summary['status_quo'] = {r[0]: dict(zip(['a_market', 'a_assessed', 'a_tax', 'b_market', 'b_assessed', 'b_tax',
                                              'b_rent', 'allowance', 'exclusion'],
                                             [r[1], r[2], r[3], r[8], r[9], r[10], r[15], r[16], r[17]]))
                             for r in rows if r[0] in (2026, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070, 2076)}

    # ---- 2. Prop 19 and the three choices for each inheritance year (baseline)
    p19_rows = []; cmp_rows = []; summary['baseline'] = {}
    for T in T_YEARS:
        res, _ = compare(T, base)
        p = res['move_in']['prop19']
        tax_in = (p['taxable_move_in'] - VERIFIED['hox']) * VERIFIED['a_rate'] + a_dc * cpi[T]
        tax_out = p['taxable_no_move_in'] * VERIFIED['a_rate'] + a_dc * cpi[T]
        tax_before = (p['fbyv'] - VERIFIED['hox']) * VERIFIED['a_rate'] + a_dc * cpi[T]
        p19_rows.append([T, r10(p['fmv']), r10(p['fbyv']), r10(p['allowance']), r10(p['value_cap']),
                         r10(p['taxable_move_in']), r10(p['taxable_no_move_in']), r10(tax_before), r10(tax_in),
                         r10(tax_out), r10(tax_out - tax_in)])
        summary['baseline'][T] = dict(prop19={k: r10(v) for k, v in p.items()},
                                      tax_before=r10(tax_before), tax_move_in=r10(tax_in), tax_no_move_in=r10(tax_out),
                                      options={})
        for key, (_, _, label) in zip(OPT_KEYS, OPTIONS):
            w = res[key]['wealth']
            cmp_rows.append([T, label] + [r10(w[h]['nominal']) for h in HORIZONS] + [r10(w[h]['real']) for h in HORIZONS])
            summary['baseline'][T]['options'][key] = {h: dict(nominal=r10(w[h]['nominal']), real=r10(w[h]['real']))
                                                      for h in HORIZONS}
        if T == 2045:
            for key in ('sell_stocks', 'rent_out', 'move_in'):
                rr = res[key]['rows']
                cols = [c for c in ('year', 'a_market', 'a_assessed', 'a_property_tax', 'a_insurance', 'a_water',
                                    'a_electricity', 'a_maintenance', 'rent_received', 'income_tax', 'net_cash_flow',
                                    'account', 'house_after_sale', 'wealth_after_tax', 'wealth_2026_dollars')
                        if c in rr[0] or c == 'year']
                write_csv(f'yearly_{key}_T2045.csv', cols,
                          [[x['year']] + [r10(x.get(c, 0)) for c in cols[1:]] for x in rr])
    write_csv('prop19_by_inheritance_year.csv',
              ['inheritance_year', 'market_value', 'factored_base_value', 'allowance', 'value_cap',
               'taxable_if_move_in', 'taxable_if_not', 'tax_year_before', 'tax_if_move_in', 'tax_if_not',
               'yearly_saving_from_moving_in'], p19_rows)
    write_csv('options_baseline.csv',
              ['inheritance_year', 'choice'] + [f'wealth_after_{h}y' for h in HORIZONS] +
              [f'wealth_after_{h}y_in_2026_dollars' for h in HORIZONS], cmp_rows)

    # ---- 3. sensitivity grid (T = 2045, 20 years): home appreciation x stock return
    grid = []
    for ga in (0.025, 0.04, 0.055):
        for gs in (0.05, 0.07, 0.09):
            pth = baseline_path(a=ga, ca=ga, stock=gs)
            res, _ = compare(2045, pth, horizon=20)
            vals = {k: res[k]['wealth'][20]['nominal'] for k in ('sell_stocks', 'rent_out', 'move_in')}
            best = max(vals, key=vals.get)
            grid.append([f'{ga:.1%}', f'{gs:.1%}'] + [r10(vals[k]) for k in ('sell_stocks', 'rent_out', 'move_in')] + [best])
    write_csv('sensitivity_grid_T2045_20y.csv',
              ['home_appreciation', 'stock_return', 'sell_stocks', 'rent_out', 'move_in', 'best'], grid)
    summary['sensitivity'] = grid
    # break-even stock return (T = 2045, 20 years) against keeping the house
    def gap(gs, other):
        res, _ = compare(2045, baseline_path(stock=gs), horizon=20)
        return res['sell_stocks']['wealth'][20]['nominal'] - res[other]['wealth'][20]['nominal']
    be = {}
    for other in ('rent_out', 'move_in'):
        lo, hi = 0.0, 0.15
        for _ in range(40):
            mid = (lo + hi) / 2
            if gap(mid, other) > 0: hi = mid
            else: lo = mid
        be[other] = round((lo + hi) / 2, 4)
    summary['break_even_stock_return'] = be
    # insurance sensitivity: owner's figure x1, x2, x3 (T = 2045, 20 years, move in)
    ins_rows = []
    for mult in (1, 2, 3):
        save = OWNER['a_insurance_year']; OWNER['a_insurance_year'] = save * mult
        res, _ = compare(2045, base, horizon=20)
        ins_rows.append([mult, r10(save * mult), r10(res['move_in']['wealth'][20]['nominal']),
                         r10(res['rent_out']['wealth'][20]['nominal'])])
        OWNER['a_insurance_year'] = save
    write_csv('sensitivity_insurance.csv', ['multiple', 'premium_2026', 'move_in_wealth_20y', 'rent_out_wealth_20y'], ins_rows)
    summary['insurance_sensitivity'] = ins_rows
    # rent control off for the third unit
    ASSUME['b_rent_controlled'] = False
    res, _ = compare(2045, base, horizon=20)
    summary['move_in_if_not_rent_controlled_20y'] = r10(res['move_in']['wealth'][20]['nominal'])
    ASSUME['b_rent_controlled'] = True

    # ---- 4. estate-tax headroom (property A only: B is already the heir's and is not in the estate)
    est = []
    for T in (2026, 2027, 2030, 2035, 2040, 2045, 2050):
        ex = exclusion(T, cpi)
        est.append([T, r10(ex), r10(av[T]), r10(ex - av[T]), r10(2 * ex - av[T])])
    write_csv('estate_headroom.csv', ['year_of_death', 'exclusion_one_person', 'a_market_value',
                                      'other_assets_before_tax_one_exclusion', 'other_assets_before_tax_two_exclusions'], est)
    summary['estate'] = est
    ex_rows = []
    for T in T_YEARS:
        ex = exclusion(T, cpi)
        for other_2026 in (5e6, 10e6, 15e6, 20e6, 30e6):
            other = other_2026 * cpi[T]
            taxable = av[T] + other
            ex_rows.append([T, r10(other_2026), r10(other), r10(taxable), r10(ex),
                            r10(max(0, taxable - ex) * VERIFIED['estate_rate']),
                            r10(max(0, taxable - 2 * ex) * VERIFIED['estate_rate'])])
    write_csv('estate_tax_examples.csv', ['year_of_death', 'other_assets_in_2026_dollars', 'other_assets_then',
                                          'estate_total', 'exclusion_one_person', 'tax_one_exclusion', 'tax_two_exclusions'], ex_rows)
    summary['estate_examples'] = ex_rows

    # ---- 5. black swans
    T = 2045
    named = [
        ('Baseline (constant rates)', base, 'Assumptions table'),
        ('1970s inflation starts the year after inheriting (real 1977-2006 record)',
         shock_after(T, [hist_year(y) for y in range(1977, 2007)]), '1977-2006'),
        ('Early-1990s California housing slump (real 1990-2019)',
         shock_after(T, [hist_year(y) for y in range(1990, 2020)]), '1990-2019'),
        ('Dot-com bust, then the 2008 crash (real 2000-2025)',
         shock_after(T, [hist_year(y) for y in range(2000, 2026)]), '2000-2025'),
        ('2007-2011 housing and stock crash (real 2007-2025)',
         shock_after(T, [hist_year(y) for y in range(2007, 2026)]), '2007-2025'),
        ('Great Depression (real 1929-1958, national home prices)',
         shock_after(T, [hist_year(y, local=False) for y in range(1929, 1959)]), '1929-1958'),
        ('1973-74 crash and stagflation (real 1973-2002, national home prices)',
         shock_after(T, [hist_year(y, local=False) for y in range(1973, 2003)]), '1973-2002'),
        ('Japan after 1990 (real 1991-2020: homes, Nikkei, prices)', shock_after(T, japan_seq(30)), 'Japan 1991-2020'),
    ]
    bs_rows = []; summary['black_swan_named'] = []
    for name, pth, span in named:
        res, ix = compare(T, pth)
        for h in HORIZONS:
            vals = {k: res[k]['wealth'][h]['real'] for k in ('sell_stocks', 'sell_6040', 'sell_cash', 'rent_out', 'move_in')}
            best = max(vals, key=vals.get)
            bs_rows.append([name, span, h] + [r10(vals[k]) for k in ('sell_stocks', 'sell_6040', 'sell_cash', 'rent_out', 'move_in')] + [best])
            summary['black_swan_named'].append(dict(name=name, span=span, horizon=h, best=best,
                                                    **{k: r10(v) for k, v in vals.items()}))
    write_csv('black_swan_named.csv', ['scenario', 'history_used', 'years_after_inheriting', 'sell_stocks', 'sell_6040',
                                       'sell_cash', 'rent_out', 'move_in', 'best'], bs_rows)

    # every rotation of the real record: local 1977-2025 (49 paths) and national 1929-2025 (97 paths)
    rot_rows = []; summary['rotations'] = {}
    for label, first, last, local in (('Bay Area record 1977-2025', 1977, 2025, True),
                                      ('National record 1929-2025', 1929, 2025, False)):
        for T in T_YEARS:
            for h in HORIZONS:
                outs = {k: [] for k in ('sell_stocks', 'sell_6040', 'rent_out', 'move_in')}
                wins = {k: 0 for k in outs}; n = 0
                value_T = []; worst = {k: (None, float('inf')) for k in outs}
                for s in range(first, last + 1):
                    pth = rotation_path(s, first, last, local)
                    res, ix = compare(T, pth, horizon=h)
                    vals = {k: res[k]['wealth'][h]['real'] for k in outs}
                    for k in outs:
                        outs[k].append(vals[k])
                        if vals[k] < worst[k][1]: worst[k] = (s, vals[k])
                    wins[max(vals, key=vals.get)] += 1; n += 1
                    value_T.append(ix[1][T] / ix[0][T])
                for k in outs:
                    v = sorted(outs[k])
                    rot_rows.append([label, T, h, k, n, r10(v[0]), r10(v[len(v) // 10]), r10(statistics.median(v)),
                                     r10(v[-1 - len(v) // 10]), r10(v[-1]), wins[k], worst[k][0]])
                summary['rotations'][f'{label}|{T}|{h}'] = dict(
                    n=n, wins=wins, median={k: r10(statistics.median(outs[k])) for k in outs},
                    worst={k: r10(min(outs[k])) for k in outs}, best={k: r10(max(outs[k])) for k in outs},
                    a_value_at_T_2026_dollars=dict(min=r10(min(value_T)), median=r10(statistics.median(value_T)),
                                                   max=r10(max(value_T))))
    write_csv('black_swan_rotations.csv', ['record', 'inheritance_year', 'years_after', 'choice', 'paths', 'worst',
                                           'tenth_percentile', 'median', 'ninetieth_percentile', 'best',
                                           'paths_where_this_choice_is_best', 'start_year_of_worst_path'], rot_rows)

    # the single "last 50 years again" path, year by year (2027 = 1977 ... 2075 = 2025)
    pth = rotation_path(1977, 1977, 2025, True); ix = build_indexes(pth)
    rows = []
    for t in range(2027, 2076):
        y = pth[t]
        rows.append([t, y['src'], f"{y['infl']:.4f}", f"{y['a']:.4f}", f"{y['b']:.4f}", f"{y['stock']:.4f}",
                     f"{y['p13']:.5f}", r10(ix[1][t]), r10(ix[2][t]), r10(factored(OWNER['a_assessed_2026'], 2026, t, pth)),
                     r10(ix[3][t]), r10(exclusion(t, ix[0]))])
    write_csv('replay_1977_2025_year_by_year.csv',
              ['year', 'history_year_used', 'inflation', 'cupertino_area_price_change', 'sf_area_price_change',
               'stock_return', 'prop13_factor', 'a_market_value', 'b_market_value', 'a_assessed_if_not_inherited',
               'prop19_allowance', 'federal_exclusion'], rows)
    summary['replay_checkpoints'] = {t: dict(a_market=r10(ix[1][t]), b_market=r10(ix[2][t]), allowance=r10(ix[3][t]),
                                             exclusion=r10(exclusion(t, ix[0])), price_level=round(ix[0][t], 3))
                                     for t in (2030, 2035, 2040, 2045, 2050, 2060, 2075)}

    with open(os.path.join(OUT, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=1, default=str)
    return summary

if __name__ == '__main__':
    s = main()
    print('direct charges 2025 (derived):', s['derived_direct_charges_2025'])
    for T in T_YEARS:
        b = s['baseline'][T]
        print(f"\nT={T}: market {b['prop19']['fmv']:,}  base {b['prop19']['fbyv']:,}  allowance {b['prop19']['allowance']:,}"
              f"  taxable move-in {b['prop19']['taxable_move_in']:,}")
        print(f"   tax before {b['tax_before']:,}  move-in {b['tax_move_in']:,}  not {b['tax_no_move_in']:,}")
        for k in OPT_KEYS:
            print('   %-12s' % k, '  '.join(f"{h}y {b['options'][k][h]['nominal']:>12,} (real {b['options'][k][h]['real']:>11,})" for h in HORIZONS))
    print('\nbreak-even stock return:', s['break_even_stock_return'])
