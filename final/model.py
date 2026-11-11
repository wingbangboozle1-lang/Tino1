#!/usr/bin/env python3
"""Year-by-year model 2026-2076 for the two properties (session 07a57a05).

Standard library only.  Run:  python3 final/model.py   ->  final/out/model.json

Privacy: owner-supplied inputs are stored here ONLY rounded to the nearest $10.
No names, addresses, parcel numbers or exact bill amounts are stored anywhere.

Key structural facts encoded (see final/sources.py for the official pages):
  * Property B (San Francisco) is ALREADY owned by the inheritor: no change in
    ownership, no reassessment, no basis step-up, not in the transferor's estate.
  * Property A (Cupertino) passes by trust at the transferor's death, year T:
      - Live in it within 1 year + homeowners' exemption  -> Prop 19 partial
        exclusion: new taxable value = FBYV + max(0, FMV - (FBYV + adjusted $1M)).
      - Rent it or leave it                                -> full reassessment at FMV.
      - Sell it                                            -> basis = FMV at death
        (if the trust assets are included in the gross estate), gain ~ 0.
"""
import csv, json, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))
Y0, Y1 = 2026, 2076


def r10(x):
    """Round to nearest $10 (publication rule)."""
    return int(round(x / 10.0)) * 10


# ----------------------------------------------------------------------------
# Inputs.  kind: 'owner' (owner-supplied, rounded $10), 'official' (read on an
# official page this session), 'assumption' (no official value exists; flagged).
# ----------------------------------------------------------------------------
P = dict(
    # --- owner-supplied, rounded to $10 ---
    cup_value=3_100_000, cup_assessed=550_540, cup_tax_2025=7_210, cup_assessed_2025=539_740,
    cup_water=1_500,            # midpoint of 100-150 per month
    cup_elec=-180,              # solar: credit of 10-20 per month (midpoint)
    sf_value=1_800_000, sf_assessed_2025=114_250, sf_tax_2025=2_440,
    sf_rent_2units=85_800,      # 7,150 per month for the two rented units
    sf_water=4_380,             # midpoint of 330-400 per month, all three units
    sf_elec=600,                # midpoint of 30-70 per month
    ins_home=1_500, ins_rental=1_500,   # owner's own estimate; NOT confirmed by an official source
    # --- official ---
    rate_cup=0.0116360,         # Santa Clara County FY2025-26 Tax Rate Book components (see sources)
    rate_sf=0.0118162182,       # SF Treasurer FY2026-27 secured rate
    hox=7_000,                  # homeowners' exemption (BOE)
    p19_cap=1_044_586,          # BOE LTA 2025/009, transfers 2025-02-16..2027-02-15
    excl_2026=15_000_000, excl_2027=15_480_000,  # IRS; Rev. Proc. 2026-35 s.3.44
    estate_rate=0.40,           # Form 706 instructions, Table A top rate
    sec121=250_000,             # IRS Topic 701 (single; 500,000 joint)
    depr_years=27.5,            # IRS Pub 527
    cup_rent_month=6_390,       # HUD FY2026 SAFMR 95014, 4-bedroom (3-BR 5,870)
    doc_transfer_tax=0.0011,    # Santa Clara County: $0.55 per $500
    niit=0.038,                 # IRS Topic 559
    # --- assumptions (flagged; none is an official figure) ---
    infl=0.025, g_cup=0.040, g_sf=0.040, g_ca=0.040,
    r_stock=0.070, r_bond=0.045, r_bill=0.035, div_yield=0.015,
    g_ca_2026=0.009,            # FHFA CA HPI 2025Q2->2026Q2 (FRED CASTHPI); calendar-2026 figure not yet published
    rent_premium=0.005,         # market rent growth = inflation + 0.5 pt
    ins_premium=0.010,          # insurance grows inflation + 1 pt
    water_premium=0.020,        # water/sewer grows inflation + 2 pt
    sf_water_near=0.09,         # SFPUC adopted FY2026-27/FY2027-28 increases (7% water, ~10-11% sewer)
    elec_premium=0.010,
    maint_cup=6_000, maint_sf=12_000,
    sell_cost=0.05, vacancy=0.05, mgmt=0.06,
    bldg_share=0.30,            # depreciable building share of Cupertino stepped-up basis
    t_fed_ord=0.24, t_ca=0.093, t_fed_ltcg=0.15,
    t_fed_ltcg_lump=0.20, t_ca_lump=0.133, t_recap_fed=0.25,
    w_stock=1.0, w_bond=0.0, w_bill=0.0,
    rent_sf_unit3=True,         # in "Live" the inheritor's vacated SF unit is rented
    step_up=True,
    T=2045,
)

# derived, shown rounded
P['dc_cup'] = r10(P['cup_tax_2025'] - P['cup_assessed_2025'] * P['rate_cup'])   # fixed charges on the bill
P['dc_sf'] = r10(P['sf_tax_2025'] - P['sf_assessed_2025'] * P['rate_sf'])
P['sf_assessed'] = r10(P['sf_assessed_2025'] * 1.02)
P['sf_unit3_rent'] = r10(P['sf_rent_2units'] / 2)                                # average of the two rented units


# ----------------------------------------------------------------------------
# Historical data (FRED / FHFA / BLS; Damodaran for asset returns)
# ----------------------------------------------------------------------------
def load_hist():
    fred = {int(r['year']): r for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_fred.csv')))}
    ret = {int(r['year']): r for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_returns_damodaran.csv')))}
    early = {int(r['year']): float(r['cpi_dec']) for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_cpi_early.csv')))}
    H = {}
    f = lambda y, k: float(fred[y][k])
    for y in range(1976, 2026):
        infl = f(y, 'cpi_dec_CPIAUCSL') / f(y - 1, 'cpi_dec_CPIAUCSL') - 1
        g_ca = f(y, 'hpi_ca_CASTHPI_q4') / f(y - 1, 'hpi_ca_CASTHPI_q4') - 1
        if y == 1976:
            g_sf = 23.70 / 19.28 - 1          # SF MSAD 1975Q4 = 19.28 (FRED)
            g_sj = g_ca                        # San Jose series starts 1976Q4; California change used for 1976
        else:
            g_sf = f(y, 'hpi_sf_ATNHPIUS41884Q_q4') / f(y - 1, 'hpi_sf_ATNHPIUS41884Q_q4') - 1
            g_sj = f(y, 'hpi_sanjose_ATNHPIUS41940Q_q4') / f(y - 1, 'hpi_sanjose_ATNHPIUS41940Q_q4') - 1
        H[y] = dict(infl=infl, g_cup=g_sj, g_sf=g_sf, g_ca=g_ca,
                    r_stock=float(ret[y]['sp500_total_return_pct']) / 100,
                    r_bond=float(ret[y]['tbond_10y_return_pct']) / 100,
                    r_bill=float(ret[y]['tbill_3m_pct']) / 100)
    # 1929-1950: national data only (no local index exists that far back)
    N = {}
    for y in range(1929, 1951):
        g = float(ret[y]['real_estate_national_pct']) / 100
        N[y] = dict(infl=early[y] / early[y - 1] - 1, g_cup=g, g_sf=g, g_ca=g,
                    r_stock=float(ret[y]['sp500_total_return_pct']) / 100,
                    r_bond=float(ret[y]['tbond_10y_return_pct']) / 100,
                    r_bill=float(ret[y]['tbill_3m_pct']) / 100)
    return H, N


HIST, NAT = load_hist()
KEYS = ('infl', 'g_cup', 'g_sf', 'g_ca', 'r_stock', 'r_bond', 'r_bill')


def baseline_path(p=P):
    return {y: {k: p[k] for k in KEYS} for y in range(Y0 + 1, Y1 + 1)}


def replay_path(start):
    """Real 1976-2025 sequence, started at `start`, wrapped around, mapped to 2027-2076."""
    return {Y0 + 1 + i: dict(HIST[1976 + ((start - 1976 + i) % 50)]) for i in range(50)}


def overlay_path(p, src, first, last, at):
    """Baseline constant path with the real years first..last dropped in starting at year `at`."""
    path = baseline_path(p)
    for i, hy in enumerate(range(first, last + 1)):
        if at + i <= Y1:
            path[at + i] = dict(src[hy])
    return path


# ----------------------------------------------------------------------------
class Acct:
    """Taxable investment account.  Negative balance = money that would otherwise
    have been invested (opportunity cost), treated symmetrically."""

    def __init__(self):
        self.bal = 0.0
        self.basis = 0.0

    def add(self, x):
        self.bal += x
        self.basis += x

    def grow(self, e, p, frac=1.0):
        ws, wb, wc = p['w_stock'], p['w_bond'], p['w_bill']
        t_div = p['t_fed_ltcg'] + p['niit'] + p['t_ca']
        t_int = p['t_fed_ord'] + p['niit'] + p['t_ca']
        r_s, r_b, r_c = e['r_stock'] * frac, e['r_bond'] * frac, e['r_bill'] * frac
        div = self.bal * ws * p['div_yield'] * frac
        inc = self.bal * (wb * r_b + wc * r_c)
        tax = div * t_div + inc * t_int
        self.bal = self.bal * (1 + ws * r_s + wb * r_b + wc * r_c) - tax
        self.basis += div + inc - tax

    def liq(self, p):
        t = p['t_fed_ltcg_lump'] + p['niit'] + p['t_ca_lump']
        return self.bal - t * (self.bal - self.basis)


def prop19_taxable(fbyv, fmv, cap):
    """R&TC 63.2(d) / BOE LTA 2026/026 definition 10 (100% transferred to an eligible child)."""
    return fbyv + max(0.0, fmv - (fbyv + cap))


def simulate(path, p=P):
    T = p['T']
    t_ord = p['t_fed_ord'] + p['niit'] + p['t_ca']
    t_lump = p['t_fed_ltcg_lump'] + p['niit'] + p['t_ca_lump']
    t_recap = p['t_recap_fed'] + p['niit'] + p['t_ca_lump']
    cpi = 1.0
    Vc, Vs = float(p['cup_value']), float(p['sf_value'])
    fby_c, fby_s = float(p['cup_assessed']), float(p['sf_assessed'])
    cap = float(p['p19_cap'])
    excl = float(p['excl_2026'])
    ins_h, ins_r = float(p['ins_home']), float(p['ins_rental'])
    wat_c, wat_s = float(p['cup_water']), float(p['sf_water'])
    el_c, el_s = float(p['cup_elec']), float(p['sf_elec'])
    rent_c = p['cup_rent_month'] * 12.0
    rent_s2, rent_s3 = float(p['sf_rent_2units']), float(p['sf_unit3_rent'])
    base_L = base_R = None
    basis = None
    acc_depr = 0.0
    susp = 0.0
    A = {k: Acct() for k in ('live', 'rent', 'sell')}
    rows = []
    summary = {}
    for y in range(Y0, Y1 + 1):
        e = path.get(y)
        if y > Y0:
            cpi *= 1 + e['infl']
            Vc *= 1 + e['g_cup']
            Vs *= 1 + e['g_sf']
            f = 1 + min(0.02, max(e['infl'], 0.0))            # Prop 13 annual factor
            fby_c *= f
            fby_s *= f
            if base_L is not None:
                base_L *= f
                base_R *= f
            if y % 2 == 1:                                    # Feb 16 of odd years: prior calendar year's CA HPI change
                cap *= 1 + (p['g_ca_2026'] if y == 2027 else path[y - 1]['g_ca'])
            excl = p['excl_2027'] if y == 2027 else excl * (1 + path[y - 1]['infl'])
            ins_h *= 1 + e['infl'] + p['ins_premium']
            ins_r *= 1 + e['infl'] + p['ins_premium']
            wat_c *= 1 + e['infl'] + p['water_premium']
            wat_s *= 1 + (p['sf_water_near'] if y in (2027, 2028) else e['infl'] + p['water_premium'])
            el_c *= 1 + e['infl'] + p['elec_premium']
            el_s *= 1 + e['infl'] + p['elec_premium']
            rent_c *= 1 + max(e['infl'] + p['rent_premium'], -0.05)
            g_ctrl = 0.6 * max(e['infl'], 0.0)                # SF Rent Board: 60% of Bay Area CPI
            g_mkt = e['infl'] + p['rent_premium']
            rent_s2 *= 1 + 0.5 * g_ctrl + 0.5 * g_mkt         # half controlled increase, half turnover-to-market
            rent_s3 *= 1 + 0.5 * g_ctrl + 0.5 * g_mkt
        maint_c, maint_s = p['maint_cup'] * cpi, p['maint_sf'] * cpi
        dc_c, dc_s = p['dc_cup'] * cpi, p['dc_sf'] * cpi
        # ---------------- Property B (SF): status quo every year ----------------
        av_s = min(fby_s, Vs)
        tax_s = av_s * p['rate_sf'] + dc_s
        row = dict(year=y, cpi=cpi, cup_value=Vc, sf_value=Vs, sf_assessed=av_s, sf_tax=tax_s,
                   sf_ins=ins_r, sf_water=wat_s, sf_elec=el_s, sf_maint=maint_s, sf_rent=rent_s2,
                   sf_net=rent_s2 * (1 - p['vacancy']) - tax_s - ins_r - wat_s - el_s - maint_s,
                   p19_cap=cap, exclusion=excl, cup_fbyv=min(fby_c, Vc), phase='before' if y < T else 'after',
                   ins_home=ins_h, ins_rental=ins_r, cup_water=wat_c, cup_elec=el_c, cup_maint=maint_c,
                   cup_rent=rent_c)
        if y < T:
            av = min(fby_c, Vc)
            row.update(cup_assessed_pre=av, cup_tax_pre=av * p['rate_cup'] + dc_c)
        else:
            if y == T:
                fb = min(fby_c, Vc)
                base_L = prop19_taxable(fb, Vc, cap)
                base_R = Vc
                basis = Vc if p['step_up'] else min(float(p['cup_assessed']), Vc)
                summary.update(T=T, fmv_T=Vc, fbyv_T=fb, cap_T=cap, excluded_T=fb + cap, taxable_live_T=base_L,
                               taxable_rent_T=base_R, exclusion_T=excl, cpi_T=cpi,
                               tax_live_T=(base_L - p['hox']) * p['rate_cup'] + dc_c,
                               tax_rent_T=base_R * p['rate_cup'] + dc_c,
                               tax_before_T=fb * p['rate_cup'] + dc_c)
            # grow accounts for the year (flows are added at year end)
            for k in ('live', 'rent'):
                A[k].grow(e, p)
            # ---- LIVE ----
            av_L = min(base_L, Vc)
            tax_L = max(av_L - p['hox'], 0) * p['rate_cup'] + dc_c
            cost_L = tax_L + ins_h + maint_c + wat_c + el_c
            unit3 = rent_s3 * (1 - p['vacancy']) * (1 - t_ord) if p['rent_sf_unit3'] else 0.0
            A['live'].add(unit3 - cost_L)
            # ---- RENT ----
            av_R = min(base_R, Vc)
            tax_R = av_R * p['rate_cup'] + dc_c
            coll = rent_c * (1 - p['vacancy'])
            noi = coll - p['mgmt'] * coll - tax_R - ins_r - maint_c
            depr = basis * p['bldg_share'] / p['depr_years'] if (y - T) < 28 else 0.0
            if y - T == 27:
                depr *= 0.5
            acc_depr += depr
            ti = noi - depr - susp
            if ti < 0:
                susp, inc_tax = -ti, 0.0
            else:
                susp, inc_tax = 0.0, ti * t_ord
            A['rent'].add(noi - inc_tax)
            # ---- SELL ---- (sold in year T; six months of carrying costs; proceeds invested mid-year)
            if y == T:
                hold = 0.5 * (tax_R + ins_h + maint_c)
                proceeds = Vc * (1 - p['sell_cost'] - p['doc_transfer_tax'])
                gain = proceeds - basis
                sale_tax = max(gain, 0.0) * t_lump
                A['sell'].add(proceeds - sale_tax - hold)
                A['sell'].grow(e, p, frac=0.5)
                summary.update(sell_proceeds=proceeds, sell_gain=gain, sell_tax=sale_tax, sell_hold=hold,
                               sell_net=proceeds - sale_tax - hold)
            else:
                A['sell'].grow(e, p)
            # ---- wealth if everything were liquidated at this year-end ----
            net_sale = Vc * (1 - p['sell_cost'] - p['doc_transfer_tax'])
            gL = net_sale - basis - p['sec121']
            wL = A['live'].liq(p) + net_sale - max(gL, 0.0) * t_lump
            g_tot = net_sale - (basis - acc_depr) - susp
            recap = min(acc_depr, max(g_tot, 0.0))
            wR = A['rent'].liq(p) + net_sale - recap * t_recap - max(g_tot - recap, 0.0) * t_lump
            wS = A['sell'].liq(p)
            row.update(live_assessed=av_L, live_tax=tax_L, live_cost=cost_L, live_unit3=unit3,
                       rent_assessed=av_R, rent_tax=tax_R, rent_collected=coll, rent_noi=noi, rent_depr=depr,
                       rent_income_tax=inc_tax, rent_after_tax=noi - inc_tax,
                       w_live=wL, w_rent=wR, w_sell=wS,
                       h_live=A['live'].bal + Vc, h_rent=A['rent'].bal + Vc, h_sell=A['sell'].bal)
        rows.append(row)
    last = rows[-1]
    summary.update(w_live=last['w_live'], w_rent=last['w_rent'], w_sell=last['w_sell'],
                   h_live=last['h_live'], h_rent=last['h_rent'], h_sell=last['h_sell'], cpi_end=last['cpi'],
                   real_live=last['w_live'] / last['cpi'], real_rent=last['w_rent'] / last['cpi'],
                   real_sell=last['w_sell'] / last['cpi'])
    for h in (10, 20):
        if T + h <= Y1:
            rr = rows[T + h - Y0]
            summary['w%d' % h] = dict(year=T + h, live=rr['w_live'], rent=rr['w_rent'], sell=rr['w_sell'], cpi=rr['cpi'])
    best = max(('live', 'rent', 'sell'), key=lambda k: summary['w_' + k])
    summary['best'] = best
    return rows, summary


def with_(**kw):
    p = copy.deepcopy(P)
    p.update(kw)
    return p


def run(p, path=None):
    return simulate(path or baseline_path(p), p)


def breakeven(param, lo, hi, a='rent', b='sell', base=None):
    """Value of `param` (constant path) at which strategies a and b end with equal wealth."""
    base = base or P

    def f(v):
        p = with_(**{**{k: base[k] for k in base}, param: v})
        s = run(p)[1]
        return s['w_' + a] - s['w_' + b]

    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        fm = f(mid)
        if flo * fm <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2


def pick(s):
    keys = ('T', 'fmv_T', 'fbyv_T', 'cap_T', 'excluded_T', 'taxable_live_T', 'taxable_rent_T', 'exclusion_T',
            'tax_live_T', 'tax_rent_T', 'tax_before_T', 'sell_proceeds', 'sell_gain', 'sell_tax', 'sell_hold',
            'sell_net', 'w_live', 'w_rent', 'w_sell', 'h_live', 'h_rent', 'h_sell', 'real_live', 'real_rent',
            'real_sell', 'best', 'cpi_end', 'cpi_T', 'w10', 'w20')
    return {k: s[k] for k in keys if k in s}


def main():
    out = {'params': P, 'years': [Y0, Y1]}
    rows, s = run(P)
    out['baseline'] = dict(rows=rows, summary=pick(s))
    # inheritance-year variants
    out['by_T'] = {str(T): pick(run(with_(T=T))[1]) for T in (2040, 2045, 2050)}
    out['rows_T'] = {str(T): run(with_(T=T))[0] for T in (2040, 2050)}
    # sensitivities (one change at a time, constant path)
    sens = [
        ('Baseline', {}),
        ('Home appreciation 3.0% a year', dict(g_cup=0.03, g_ca=0.03)),
        ('Home appreciation 5.0% a year', dict(g_cup=0.05, g_ca=0.05)),
        ('Home appreciation 6.7% a year (San Jose index 1976-2025)', dict(g_cup=0.0671, g_ca=0.0601)),
        ('Stocks 5.0% a year', dict(r_stock=0.05)),
        ('Stocks 10.0% a year (S&P 500 1928-2025)', dict(r_stock=0.10)),
        ('Proceeds kept in savings / T-bills 3.5%', dict(w_stock=0.0, w_bill=1.0)),
        ('Proceeds 60% stocks / 40% Treasury bonds', dict(w_stock=0.6, w_bond=0.4)),
        ('Inflation 4.0% a year (all nominal rates +1.5 pt)', dict(infl=0.04, g_cup=0.055, g_sf=0.055, g_ca=0.055, r_stock=0.085, r_bond=0.06, r_bill=0.05)),
        ('Cupertino rent 30% above the HUD figure', dict(cup_rent_month=r10(6390 * 1.3))),
        ('Cupertino rent at the HUD 3-bedroom figure', dict(cup_rent_month=5870)),
        ('Selling costs 7%', dict(sell_cost=0.07)),
        ('Lower tax bracket (12% federal, 6% state, 0% gains)', dict(t_fed_ord=0.12, t_ca=0.06, t_fed_ltcg=0.0, t_fed_ltcg_lump=0.15, t_ca_lump=0.093, niit=0.0)),
        ('Top tax bracket (37% federal, 12.3% state)', dict(t_fed_ord=0.37, t_ca=0.123, t_fed_ltcg=0.20)),
        ('Vacated SF unit left empty', dict(rent_sf_unit3=False)),
        ('Insurance three times the owner estimate', dict(ins_home=4500, ins_rental=4500)),
        ('Maintenance doubled', dict(maint_cup=12000)),
        ('No basis step-up (trust assets outside the estate)', dict(step_up=False)),
    ]
    out['sensitivity'] = [dict(label=l, change=c, **pick(run(with_(**c))[1])) for l, c in sens]
    out['breakeven'] = dict(
        g_cup_rent_vs_sell=breakeven('g_cup', 0.0, 0.15),
        g_cup_live_vs_sell=breakeven('g_cup', 0.0, 0.20, a='live'),
        r_stock_rent_vs_sell=breakeven('r_stock', 0.0, 0.15),
        rent_month_rent_vs_sell=breakeven('cup_rent_month', 1000, 60000),
    )
    # ---------------- non-constant paths ----------------
    T = P['T']
    replays = []
    for st in range(1976, 2026):
        r_, s_ = run(P, replay_path(st))
        replays.append(dict(start=st, **pick(s_)))
    out['replays'] = replays
    named = [
        ('replay_1976', 'Real 1976-2025 sequence in order (high inflation first)', replay_path(1976)),
        ('replay_2000', 'Real sequence starting in 2000 (dot-com bust and 2008 crisis first)', replay_path(2000)),
        ('replay_1990', 'Real sequence starting in 1990 (early-1990s California housing slump first)', replay_path(1990)),
        ('replay_1982', 'Real sequence starting in 1982 (long boom first, busts near the end)', replay_path(1982)),
        ('crash_at_T', 'Baseline, then the real 2007-2012 housing and stock bust starting the year of inheritance', overlay_path(P, HIST, 2007, 2012, T)),
        ('stagflation_at_T', 'Baseline, then the real 1977-1982 inflation years starting the year of inheritance', overlay_path(P, HIST, 1977, 1982, T)),
        ('lost_decade_at_T', 'Baseline, then the real 2000-2009 "lost decade" for stocks starting the year of inheritance', overlay_path(P, HIST, 2000, 2009, T)),
        ('slump_at_T', 'Baseline, then the real 1990-1996 California housing slump starting the year of inheritance', overlay_path(P, HIST, 1990, 1996, T)),
        ('depression_at_T', 'Baseline, then the real 1929-1941 national Depression sequence starting the year of inheritance (national data)', overlay_path(P, NAT, 1929, 1941, T)),
        ('crash_before_T', 'Baseline, then the real 2007-2012 bust ending the year before inheritance', overlay_path(P, HIST, 2007, 2012, T - 6)),
    ]
    out['paths'] = []
    for key, label, path in named:
        r_, s_ = run(P, path)
        out['paths'].append(dict(key=key, label=label, summary=pick(s_), rows=r_,
                                 econ=[dict(year=y, **path[y]) for y in sorted(path)]))
    # historical summary statistics used on the site
    def cagr(vals):
        prod = 1.0
        for v in vals:
            prod *= 1 + v
        return prod ** (1.0 / len(vals)) - 1
    yrs = range(1977, 2026)
    out['hist_stats'] = dict(
        sj_1976_2025=cagr([HIST[y]['g_cup'] for y in yrs]), sf_1976_2025=cagr([HIST[y]['g_sf'] for y in yrs]),
        ca_1976_2025=cagr([HIST[y]['g_ca'] for y in yrs]), cpi_1976_2025=cagr([HIST[y]['infl'] for y in yrs]),
        sj_2000_2025=cagr([HIST[y]['g_cup'] for y in range(2001, 2026)]),
        sf_2000_2025=cagr([HIST[y]['g_sf'] for y in range(2001, 2026)]),
        cpi_2000_2025=cagr([HIST[y]['infl'] for y in range(2001, 2026)]),
        sp_1976_2025=cagr([HIST[y]['r_stock'] for y in range(1976, 2026)]),
        bond_1976_2025=cagr([HIST[y]['r_bond'] for y in range(1976, 2026)]),
        bill_1976_2025=cagr([HIST[y]['r_bill'] for y in range(1976, 2026)]),
        worst_sj=min((HIST[y]['g_cup'], y) for y in yrs), best_sj=max((HIST[y]['g_cup'], y) for y in yrs),
        worst_sp=min((HIST[y]['r_stock'], y) for y in range(1976, 2026)),
        max_infl=max((HIST[y]['infl'], y) for y in range(1976, 2026)),
    )
    out['hist'] = [dict(year=y, **HIST[y]) for y in sorted(HIST)]
    # estate-tax headroom for the cash part of the inheritance
    est = []
    for Tn in (2040, 2045, 2050):
        r_ = run(with_(T=Tn))[0]
        rr = r_[Tn - Y0]
        for cash in (2_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000):
            real_cash = cash * rr['cpi']
            taxable = max(0.0, rr['cup_value'] + real_cash - rr['exclusion'])
            est.append(dict(T=Tn, cash_today=cash, cash_then=real_cash, house=rr['cup_value'], exclusion=rr['exclusion'],
                            headroom=rr['exclusion'] - rr['cup_value'], tax=taxable * P['estate_rate'],
                            tax_two=max(0.0, rr['cup_value'] + real_cash - 2 * rr['exclusion']) * P['estate_rate'],
                            cpi=rr['cpi']))
    out['estate'] = est
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'out', 'model.json'), 'w'), indent=0)
    return out


if __name__ == '__main__':
    o = main()
    s = o['baseline']['summary']
    print('T', s['T'], 'FMV', r10(s['fmv_T']), 'FBYV', r10(s['fbyv_T']), 'cap', r10(s['cap_T']),
          'taxable live', r10(s['taxable_live_T']), 'excl', r10(s['exclusion_T']))
    print('tax before/live/rent', r10(s['tax_before_T']), r10(s['tax_live_T']), r10(s['tax_rent_T']))
    print('sell net', r10(s['sell_net']), 'gain', r10(s['sell_gain']))
    for k in ('live', 'rent', 'sell'):
        print(k, 'nominal', r10(s['w_' + k]), 'real', r10(s['real_' + k]))
    print('best', s['best'], 'breakeven', o['breakeven'])
    for x in o['sensitivity']:
        print('%-62s L %12d R %12d S %12d  %s' % (x['label'][:62], x['real_live'], x['real_rent'], x['real_sell'], x['best']))
    wins = {}
    for x in o['replays']:
        wins[x['best']] = wins.get(x['best'], 0) + 1
    print('replay wins', wins)
    for x in o['paths']:
        s = x['summary']
        print('%-18s L %12d R %12d S %12d %s' % (x['key'], s['real_live'], s['real_rent'], s['real_sell'], s['best']))
