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
    cup_value=3_100_000, cup_assessed=550_540, cup_tax_2025=7_210,
    cup_water=1_500,            # midpoint of 100-150 per month
    cup_elec=-180,              # solar: credit of 10-20 per month (midpoint)
    sf_value=1_800_000, sf_assessed=116_540, sf_tax_2025=2_440,   # assessed value for 2026 = prior year + 2%
    dc_cup=930, dc_sf=1_090,    # fixed charges inside the bills: bill minus official rate times assessed value (prior-year values not stored)
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
    cup_rent_month=6_390,       # HUD FY2026 SAFMR 95014, 4-bedroom -- BENCHMARK only, not a verified rent for
                                #   Property A (bedroom count and rentable condition unknown: U08/A07)
    cup_rent_month_3br=5_870,   # HUD FY2026 SAFMR 95014, 3-bedroom (official figure, used as the downside gate)
    doc_transfer_tax=0.0011,    # Santa Clara County: $0.55 per $500
    salt_cap_2026=40_400,       # P.L. 119-21 Schedule A SALT cap, 2026 (official figure; IRS) - text only
    salt_cap_floor=10_000,      # pre-2025 SALT cap the law reverts to (official figure; IRS) - text only
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
    rent_sf_unit3=False,        # baseline counts NO rent for the vacated third SF unit: no rent was ever supplied
                                #   for it and nothing may be inferred (brief rule; S5-P1). The leasing upside runs
                                #   only as one labelled scenario in `sensitivity` below.
    step_up=True,
    T=2045,
    # --- Proposition H (San Francisco parcel tax, approved by voters 2026-11-03; official terms read on
    #     SFMTA's page 2026-11-16). Multifamily rate: $249 up to 5,000 sq ft of building area, plus $0.195 per
    #     sq ft over 5,000, capped at $50,000. Starts with the FY 2027-28 bill; rises with inflation from FY 2028-29.
    #     prop_h_sf is the building area, which is NOT in the repository (owner input). The default is the
    #     5,000 sq ft point, which gives the MINIMUM tax for a multifamily parcel ($249), not an estimate of the
    #     owner's bill. Parcel classification to be confirmed by the SFMTA (flag U-PH1).
    prop_h_base=249, prop_h_per_sf=0.195, prop_h_cap=50_000, prop_h_sf=5_000, prop_h_start=2027,
)

# derived, shown rounded.  Scenario input only (S5-P1): letting the third unit at the average of the two known
# rents is an INFERENCE, so it never enters the baseline; it is used only by the labelled sensitivity scenario.
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
                    r_bill=float(ret[y]['tbill_3m_pct']) / 100,
                    f_p13=FACTORS[y])   # official BOE R&TC 51 factor for this roll year
    # 1929-1950: national data only (no local index exists that far back)
    N = {}
    for y in range(1929, 1951):
        g = float(ret[y]['real_estate_national_pct']) / 100
        N[y] = dict(infl=early[y] / early[y - 1] - 1, g_cup=g, g_sf=g, g_ca=g,
                    r_stock=float(ret[y]['sp500_total_return_pct']) / 100,
                    r_bond=float(ret[y]['tbond_10y_return_pct']) / 100,
                    r_bill=float(ret[y]['tbill_3m_pct']) / 100)
    # Japan 1991-2020 (official series via FRED: BIS residential property prices, Nikkei 225 price index, OECD CPI)
    jp = {int(r['year']): r for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_japan.csv')))}
    J = {}
    for y in range(1991, 2021):
        infl = float(jp[y]['cpi']) / float(jp[y - 1]['cpi']) - 1
        g = float(jp[y]['home_yoy_pct']) / 100
        J[y] = dict(infl=infl, g_cup=g, g_sf=g, g_ca=g,
                    r_stock=float(jp[y]['nikkei']) / float(jp[y - 1]['nikkei']) - 1,   # price only, no dividends
                    r_bond=max(0.0, infl), r_bill=max(0.0, infl))                          # cash keeps pace with prices at best
    return H, N, J


def load_factors():
    """Official BOE R&TC 51 inflation factors by assessment roll year, 1976-2026.

    Source: final/data/hist_prop13_factor.csv (Letter to Assessors 2026/002 enclosure,
    cross-checked against LTA 2020/067 and LTA 2021/065). Used only where a real
    assessment year exists - the historical replays. The baseline after 2026 and the
    Japan / Depression counterfactuals have no California factor and keep the labelled
    proxy (flag A11).
    """
    return {int(r['year']): float(r['factor'])
            for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_prop13_factor.csv')))}


FACTORS = load_factors()
HIST, NAT, JPN = load_hist()
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
    ph_amt = 0.0
    for y in range(Y0, Y1 + 1):
        e = path.get(y)
        if y > Y0:
            cpi *= 1 + e['infl']
            Vc *= 1 + e['g_cup']
            Vs *= 1 + e['g_sf']
            # Proposition 13 annual factor (R&TC 51): replayed real years carry the official
            # BOE factor from the LTA 2026/002 enclosure (flag A11); where no California factor
            # exists - the baseline after 2026 and the Japan / Depression counterfactuals -
            # the statutory structure applies with the path's inflation as a LABELLED PROXY.
            f = e['f_p13'] if 'f_p13' in e else (1 + min(0.02, max(e['infl'], 0.0)))
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
        if y == p['prop_h_start']:
            ph_amt = min(p['prop_h_base'] + p['prop_h_per_sf'] * max(p['prop_h_sf'] - 5000, 0), p['prop_h_cap'])
        elif y > p['prop_h_start']:
            ph_amt *= 1 + e['infl']                          # indexed to inflation from FY 2028-29
        prop_h = ph_amt if y >= p['prop_h_start'] else 0.0
        row = dict(year=y, cpi=cpi, cup_value=Vc, sf_value=Vs, sf_assessed=av_s, sf_tax=tax_s,
                   sf_ins=ins_r, sf_water=wat_s, sf_elec=el_s, sf_maint=maint_s, sf_rent=rent_s2,
                   sf_prop_h=prop_h,
                   sf_net=rent_s2 * (1 - p['vacancy']) - tax_s - prop_h - ins_r - wat_s - el_s - maint_s,
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
            excl121 = p['sec121'] if (y - T) >= 2 else 0.0   # IRS Topic 701: owned and lived in for 2 years before the sale
            gL = net_sale - basis - excl121
            wL = A['live'].liq(p) + net_sale - max(gL, 0.0) * t_lump
            g_tot = net_sale - (basis - acc_depr) - susp
            recap = min(acc_depr, max(g_tot, 0.0))
            wR = A['rent'].liq(p) + net_sale - recap * t_recap - max(g_tot - recap, 0.0) * t_lump
            wS = A['sell'].liq(p)
            row.update(live_assessed=av_L, live_tax=tax_L, live_cost=cost_L, live_unit3=unit3,
                       rent_assessed=av_R, rent_tax=tax_R, rent_collected=coll, rent_noi=noi, rent_depr=depr,
                       rent_income_tax=inc_tax, rent_after_tax=noi - inc_tax,
                       rent_susp=susp, w_live=wL, w_rent=wR, w_sell=wS,
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


# ----------------------------------------------------------------------------
# Mixed paths (session 59feaf6e, H-2): live in Property A for `years` years and then
# sell, or rent it for `years` years and then sell.  Uses the same per-year cash flows
# as simulate(), so a path that is never sold reproduces the pure live / rent results
# exactly (self-test below).  The sale is at the end of year T + years.
# ----------------------------------------------------------------------------
def mixed(path, p=P, first='live', years=None):
    rows, s = simulate(path, p)
    T = p['T']
    S = None if years is None else T + years
    t_lump = p['t_fed_ltcg_lump'] + p['niit'] + p['t_ca_lump']
    t_recap = p['t_recap_fed'] + p['niit'] + p['t_ca_lump']
    basis = s['fmv_T'] if p['step_up'] else min(float(p['cup_assessed']), s['fmv_T'])
    acc = Acct()
    depr = 0.0
    susp = 0.0
    sale = None
    for y in range(T, Y1 + 1):
        r = rows[y - Y0]
        acc.grow(path[y], p)
        if sale is None and (S is None or y < S):
            if first == 'live':
                acc.add(r['live_unit3'] - r['live_cost'])
            else:
                acc.add(r['rent_after_tax'])
                depr += r['rent_depr']
                susp = r['rent_susp']
        elif sale is None and y == S:
            V = r['cup_value']
            proceeds = V * (1 - p['sell_cost'] - p['doc_transfer_tax'])
            hold = 0.5 * (r['rent_tax'] + r['ins_home'] + r['cup_maint'])
            if first == 'live':
                gain = proceeds - basis - (p['sec121'] if (S - T) >= 2 else 0.0)   # IRS Topic 701: 2 of 5 years
                tax = max(gain, 0.0) * t_lump
            else:
                g_tot = proceeds - (basis - depr) - susp
                recap = min(depr, max(g_tot, 0.0))
                tax = recap * t_recap + max(g_tot - recap, 0.0) * t_lump
            acc.add(proceeds - tax - hold)
            sale = dict(year=S, proceeds=proceeds, tax=tax, hold=hold, net=proceeds - tax - hold,
                        gain=proceeds - basis)
    last = rows[-1]
    if sale is None:
        Vc = last['cup_value']
        net_sale = Vc * (1 - p['sell_cost'] - p['doc_transfer_tax'])
        if first == 'live':
            gL = net_sale - basis - p['sec121']
            nominal = acc.liq(p) + net_sale - max(gL, 0.0) * t_lump
        else:
            g_tot = net_sale - (basis - depr) - susp
            recap = min(depr, max(g_tot, 0.0))
            nominal = acc.liq(p) + net_sale - recap * t_recap - max(g_tot - recap, 0.0) * t_lump
    else:
        nominal = acc.liq(p)
    return dict(nominal=nominal, real=nominal / last['cpi'], sale=sale, first=first, years=years)


# ----------------------------------------------------------------------------
# Phased entry (session 59feaf6e, H-1).  After the sale, the net proceeds are parked in
# 3-month to 2-year Treasuries for `park_m` months, then moved into stocks in equal
# monthly tranches over `phase_m` months.  `phase_m == 0` with `park_m == 0` is the
# lump-sum entry.  One monthly engine serves both arms, so the difference between them
# is the entry timing and nothing else.  Annual path rates are converted to monthly
# rates.  Interest is taxed as ordinary income each month, dividends at the qualified
# rate, and the capital gain is taxed at liquidation (end of Y1), as in Acct.
# The parking return is the path's 3-month Treasury bill series (r_bill); the 2-year
# note is not in the repository (flag H01).
# ----------------------------------------------------------------------------
def phased_entry(path, p, proceeds, park_m, phase_m, entry_m=6):
    """entry_m = month of the inheritance year in which the proceeds arrive (6 = mid-year, as in simulate())."""
    T = p['T']
    t_int = p['t_fed_ord'] + p['niit'] + p['t_ca']
    t_div = p['t_fed_ltcg'] + p['niit'] + p['t_ca']
    t_lump = p['t_fed_ltcg_lump'] + p['niit'] + p['t_ca_lump']
    cash = cash_b = 0.0            # the proceeds arrive in month entry_m
    stk = stk_b = 0.0
    tranche = float(proceeds) / phase_m if phase_m else float(proceeds)
    cpi = 1.0
    cpi_y = {}
    for y in range(Y0 + 1, Y1 + 1):
        cpi *= 1 + path[y]['infl']
        cpi_y[y] = cpi
    real_at = {}
    net = None
    for m in range(12 * (Y1 - T + 1)):
        y = T + m // 12
        e = path[y]
        if m == entry_m:
            cash = cash_b = float(proceeds)
        mr = m - entry_m                 # months since the proceeds arrived
        # transfer at the start of the month
        if phase_m == 0:
            amt = cash if mr == park_m else 0.0
        else:
            amt = tranche if park_m <= mr < park_m + phase_m else 0.0
        amt = min(amt, cash)
        if amt > 0:
            frac = amt / cash
            cash_b *= (1 - frac)
            cash -= amt
            stk += amt
            stk_b += amt
        # growth during the month
        rb = (1 + e['r_bill']) ** (1 / 12) - 1
        rs = (1 + e['r_stock']) ** (1 / 12) - 1
        if cash:
            i = cash * rb
            ti = max(i, 0.0) * t_int
            cash += i - ti
            cash_b += i - ti
        if stk:
            dv = stk * p['div_yield'] / 12
            dvt = dv * t_div
            stk = stk * (1 + rs) - dvt
            stk_b += dv - dvt
        # year end: liquidation value after the capital-gain tax, in nominal and real dollars
        if (m + 1) % 12 == 0 and m >= entry_m:
            net = cash - t_lump * (cash - cash_b) + stk - t_lump * (stk - stk_b)
            real_at[y] = net / cpi_y[y]
    return dict(real=real_at[Y1], nominal=net, real_at=real_at,
                real_T1=real_at[T + 1], real_T5=real_at[T + 5], real_T10=real_at[T + 10])


def phased_selftest():
    """Zero returns and zero tax: every arm must return exactly the proceeds."""
    z = with_(t_fed_ord=0.0, t_ca=0.0, niit=0.0, t_fed_ltcg=0.0, t_fed_ltcg_lump=0.0, t_ca_lump=0.0,
              div_yield=0.0)
    zero = {y: dict(infl=0.0, g_cup=0.0, g_sf=0.0, g_ca=0.0, r_stock=0.0, r_bond=0.0, r_bill=0.0,
                    f_p13=1.0) for y in range(Y0 + 1, Y1 + 1)}
    out = []
    for park, ph in ((0, 0), (24, 12), (36, 12)):
        r = phased_entry(zero, z, 1_000_000.0, park, ph)['real']
        out.append(abs(r - 1_000_000.0) < 1e-6)
    return all(out)


def mixed_selftest():
    """A path that is never sold must reproduce the pure live and rent results."""
    rows, s = run(P)
    a = mixed(baseline_path(P), P, 'live', None)['nominal']
    b = mixed(baseline_path(P), P, 'rent', None)['nominal']
    return abs(a - s['w_live']) < 0.01 and abs(b - s['w_rent']) < 0.01, a - s['w_live'], b - s['w_rent']



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
        ('Top tax bracket (37% federal; CA 13.3% top marginal rate on gains above $1M - 12.3% top bracket plus the 1% Form 540 surtax on taxable income over $1,000,000, R&TC 17043)', dict(t_fed_ord=0.37, t_ca=0.123, t_ca_lump=0.133, t_fed_ltcg=0.20)),
        ('Third unit at Property B let at the average of the two known unit rents (scenario only; the baseline counts none)', dict(rent_sf_unit3=True)),
        ('Insurance three times the owner estimate', dict(ins_home=4500, ins_rental=4500)),
        ('Prop H at a hypothetical 10,000 sq ft Property B building (not the owner\'s building; Property B only)', dict(prop_h_sf=10000)),
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
        ('replay_1976', 'Real 1976-2025 sequence in order (high inflation first)', 'replay', replay_path(1976)),
        ('replay_2000', 'Real sequence starting in 2000 (dot-com bust and 2008 crisis first)', 'replay', replay_path(2000)),
        ('replay_1990', 'Real sequence starting in 1990 (early-1990s California housing slump first)', 'replay', replay_path(1990)),
        ('replay_1982', 'Real sequence starting in 1982 (long boom first, busts near the end)', 'replay', replay_path(1982)),
        ('crash_at_T', 'Baseline, then the real 2007-2012 housing and stock bust starting the year of inheritance', 'overlay', overlay_path(P, HIST, 2007, 2012, T)),
        ('stagflation_at_T', 'Baseline, then the real 1977-1982 inflation years starting the year of inheritance', 'overlay', overlay_path(P, HIST, 1977, 1982, T)),
        ('lost_decade_at_T', 'Baseline, then the real 2000-2009 "lost decade" for stocks starting the year of inheritance', 'overlay', overlay_path(P, HIST, 2000, 2009, T)),
        ('slump_at_T', 'Baseline, then the real 1990-1996 California housing slump starting the year of inheritance', 'overlay', overlay_path(P, HIST, 1990, 1996, T)),
        ('depression_at_T', 'Baseline, then the real 1929-1941 national Depression sequence starting the year of inheritance (national data)', 'overlay-national', overlay_path(P, NAT, 1929, 1941, T)),
        ('crash_before_T', 'Baseline, then the real 2007-2012 bust ending the year before inheritance', 'overlay', overlay_path(P, HIST, 2007, 2012, T - 6)),
        ('japan_at_T', 'Baseline, then Japan\'s real 1991-2020 stagnation starting the year of inheritance (home prices, Nikkei without dividends, consumer prices)', 'overlay-japan', overlay_path(P, JPN, 1991, 2020, T)),
    ]
    KIND = {
        'replay': 'Hypothetical construction: real 1976-2025 years kept in their real order but started in a chosen year (not a forecast)',
        'overlay': 'Hypothetical construction: real crisis years of the US record dropped into the constant baseline at a chosen moment (illustrative timing; not a forecast)',
        'overlay-national': 'Hypothetical construction: real 1929-1941 national years (national home prices; academic returns) dropped into the baseline at a chosen moment',
        'overlay-japan': 'Hypothetical construction: Japan\'s real 1991-2020 official series (via FRED) dropped into the baseline at a chosen moment',
    }
    out['paths'] = []
    for key, label, kind, path in named:
        r_, s_ = run(P, path)
        out['paths'].append(dict(key=key, label=label, kind=kind, kind_label=KIND[kind], summary=pick(s_), rows=r_,
                                 econ=[dict(year=y, **path[y]) for y in sorted(path)]))
    # the Japan path again with everything kept in savings instead of stocks
    out['japan_savings'] = pick(run(with_(w_stock=0.0, w_bill=1.0), overlay_path(P, JPN, 1991, 2020, T))[1])
    # how often each choice leads at 10 years, 20 years and in 2076, across the 50 replays
    hz = {}
    for name, get in (('10', lambda x: x['w10']), ('20', lambda x: x['w20']), ('end', lambda x: dict(live=x['w_live'], rent=x['w_rent'], sell=x['w_sell'], cpi=x['cpi_end']))):
        cnt = dict(live=0, rent=0, sell=0)
        worst = {}
        for x in replays:
            d = get(x)
            cnt[max(('live', 'rent', 'sell'), key=lambda k: d[k])] += 1
            for k in ('live', 'rent', 'sell'):
                v = d[k] / d['cpi']
                worst[k] = min(worst.get(k, v), v)
        gaps = sorted(get(x)['sell'] / get(x)['cpi'] - get(x)['rent'] / get(x)['cpi'] for x in replays)
        hz[name] = dict(wins=cnt, worst=worst, sell_minus_rent_worst=gaps[0], sell_minus_rent_median=gaps[len(gaps) // 2])
    out['replay_horizons'] = hz
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
    # Provenance of every series the model consumes (S5-P4): official statistics, the academic return
    # dataset, and hypothetical constructions must never be presented as one thing.
    out['provenance'] = dict(
        infl='Official statistics: BLS Consumer Price Index (Dec/Dec) via FRED',
        g_cup='Official statistics: FHFA all-transactions house-price index, San Jose metro (Q4/Q4) via FRED',
        g_sf='Official statistics: FHFA all-transactions house-price index, San Francisco metro (Q4/Q4) via FRED',
        g_ca='Official statistics: FHFA all-transactions house-price index, California via FRED',
        r_stock='ACADEMIC dataset (NYU Stern / Damodaran) - NOT a government statistic and not officially verified',
        r_bond='ACADEMIC dataset (NYU Stern / Damodaran) - NOT a government statistic and not officially verified',
        r_bill='ACADEMIC dataset (NYU Stern / Damodaran) - NOT a government statistic and not officially verified',
        cpi_early='Official statistics: BLS CPI (1929-1950)',
        nat_re_early='ACADEMIC dataset (Damodaran national real-estate returns, 1929-1950) - no official local index exists that far back',
        japan='Official series via FRED: BIS residential property prices, OECD CPI; Nikkei 225 PRICE index (dividends excluded)',
        prop13_factor='Statutory index: California CPI capped at 2% (R&TC 51). Replayed years 1976-2025 use the official BOE factor table (LTA 2026/002 enclosure; cross-checked against LTA 2020/067 and 2021/065). Future California CPI is unknowable, so baseline years after 2026 and the Japan/Depression counterfactuals use each path\'s inflation as a LABELLED PROXY (flag A11). Official BOE factor for 2026: 1.02.',
        paths='The fifty replays and every named path are HYPOTHETICAL constructions from the series above: illustrative stress tests, not forecasts.',
    )
    # ---------------- phased entry (H-1): park 24 or 36 months, then phase in over 12 months ----------------
    PARK = dict(lump=dict(park_m=0, phase_m=0), park24=dict(park_m=24, phase_m=12), park36=dict(park_m=36, phase_m=12))

    def phased_row(path, summ):
        proceeds = summ['sell_net']
        res = {k: phased_entry(path, P, proceeds, **v) for k, v in PARK.items()}
        d = dict(proceeds=proceeds)
        for k, r_ in res.items():
            d[k] = r_['real']
            d[k + '_T1'] = r_['real_T1']
            d[k + '_T10'] = r_['real_T10']
        d['lump_nominal'] = res['lump']['nominal']
        return d

    base_path = baseline_path(P)
    BS = out['baseline']['summary']
    ph_base = phased_row(base_path, BS)
    ph_named = {x['key']: phased_row(x_path, x['summary']) for x, x_path in
                zip(out['paths'], [p_ for _, _, _, p_ in named])}
    ph_replays = []
    for rp_ in replays:
        ph_replays.append(dict(start=rp_['start'], **phased_row(replay_path(rp_['start']), rp_)))
    wins = {k: 0 for k in ('lump', 'park24', 'park36')}
    gaps24 = sorted(x['park24'] - x['lump'] for x in ph_replays)
    gaps36 = sorted(x['park36'] - x['lump'] for x in ph_replays)
    for x in ph_replays:
        wins[max(('lump', 'park24', 'park36'), key=lambda k: x[k])] += 1
    out['phased'] = dict(
        baseline=ph_base, named=ph_named, replays=ph_replays,
        replay_wins=wins,
        replay_gap24=dict(worst=gaps24[0], median=gaps24[len(gaps24) // 2], best=gaps24[-1]),
        replay_gap36=dict(worst=gaps36[0], median=gaps36[len(gaps36) // 2], best=gaps36[-1]),
        rule=dict(park_months=[24, 36], phase_months=12, park_return='3-month Treasury bill series (r_bill) of each path',
                  start='start of the inheritance year, with the net proceeds of the sale after tax and selling costs'),
    )

    # ---------------- mixed paths (H-2): live or rent for 5 or 10 years, then sell ----------------
    MIX = [('live', 5), ('live', 10), ('rent', 5), ('rent', 10)]

    def mixed_row(path):
        d = {}
        for first, yrs in MIX:
            d['%s%d' % (first, yrs)] = mixed(path, P, first, yrs)['real']
        d['never_live'] = mixed(path, P, 'live', None)['real']
        d['never_rent'] = mixed(path, P, 'rent', None)['real']
        return d

    mix_base = mixed_row(base_path)
    mix_named = {x['key']: mixed_row(x_path) for x, x_path in zip(out['paths'], [p_ for _, _, _, p_ in named])}
    mix_replays = [dict(start=rp_['start'], **mixed_row(replay_path(rp_['start']))) for rp_ in replays]
    out['mixed'] = dict(baseline=mix_base, named=mix_named, replays=mix_replays,
                        pure=dict(live=BS['real_live'], rent=BS['real_rent'], sell=BS['real_sell']),
                        rule=dict(first=['live', 'rent'], years=[5, 10],
                                  note='Sale at the end of year T + years; live years carry the Proposition 19 '
                                       'taxable value; rent years carry full reassessment and depreciation; '
                                       'the gain on sale is taxed as in the pure sell path.'))
    # sale-year detail for the baseline mixed paths
    out['mixed_detail'] = {'%s%d' % (f, y): mixed(base_path, P, f, y)['sale'] for f, y in MIX}

    # ---------------- what-if grid (H-3): every combination of four controls, all outputs from this model ----------------
    AX = dict(
        home_growth=[0.03, 0.04, 0.05],       # applied to Property A and B and the California index
        stock_return=[0.05, 0.07, 0.10],      # annual total return, stocks
        rent=[5870, 6390, 8310],              # monthly rent for Property A (HUD 3-bedroom, HUD 4-bedroom, 30% above 4-bedroom)
        park_return=[0.035, 0.0432],          # 3-month Treasury: model assumption, and the official 13 Nov 2026 rate
    )
    cells = []
    for g in AX['home_growth']:
        for rs_ in AX['stock_return']:
            for rent_ in AX['rent']:
                for rb_ in AX['park_return']:
                    p_ = with_(g_cup=g, g_ca=g, g_sf=g, r_stock=rs_, cup_rent_month=rent_, r_bill=rb_)
                    rows_, s_ = run(p_)
                    path_ = baseline_path(p_)
                    c = dict(g=g, s=rs_, rent=rent_, b=rb_,
                             live=s_['real_live'], rent_now=s_['real_rent'], sell=s_['real_sell'],
                             fmv=s_['fmv_T'], proceeds=s_['sell_net'])
                    for first, yrs in MIX:
                        c['%s%d' % (first, yrs)] = mixed(path_, p_, first, yrs)['real']
                    for k, v in PARK.items():
                        if k != 'lump':
                            c[k] = phased_entry(path_, p_, s_['sell_net'], **v)['real']
                    # reinvestment risk: the same choices when a crash lands just after the sale.
                    # 2008 = real 2007-2012 bust starting in the inheritance year; 1929 = real 1929-1941 national Depression
                    for tag, src_, a_, b_ in (('c08', HIST, 2007, 2012), ('d29', NAT, 1929, 1941)):
                        cp_ = overlay_path(p_, src_, a_, b_, T)
                        sc_ = run(p_, cp_)[1]
                        c[tag + '_sell'] = sc_['real_sell']
                        for k, v in PARK.items():
                            c[tag + '_' + k] = phased_entry(cp_, p_, sc_['sell_net'], **v)['real']
                    c['lump'] = phased_entry(path_, p_, s_['sell_net'], 0, 0)['real']
                    for tag, cp_ in (('c08', overlay_path(p_, HIST, 2007, 2012, T)), ('d29', overlay_path(p_, NAT, 1929, 1941, T))):
                        sc_ = run(p_, cp_)[1]
                        c[tag + '_live'] = sc_['real_live']
                        c[tag + '_rent'] = sc_['real_rent']
                        for first, yrs in MIX:
                            c[tag + '_%s%d' % (first, yrs)] = mixed(cp_, p_, first, yrs)['real']
                    cells.append(c)
    out['whatif'] = dict(axes=AX, cells=cells,
                         labels=dict(home_growth='Home prices, % a year (Property A, Property B and the California index)',
                                     stock_return='Stock return, % a year (total return)',
                                     rent='Property A rent, $ a month (HUD 3-bedroom; HUD 4-bedroom; 30% above HUD 4-bedroom)',
                                     park_return='Three-month Treasury yield while parked, % a year'))
    # ---------------- crash timing (H-1): where the crash lands decides whether parking helps ----------------
    timing = []
    for tag, srcd, a_, b_, name in (('c08', HIST, 2007, 2012, '2007-2012 bust (2008 is the worst year)'),
                                    ('d29', NAT, 1929, 1941, '1929-1941 Depression sequence (national data)')):
        for off in range(0, 5):
            cp_ = overlay_path(P, srcd, a_, b_, T + off)
            rows_c, sc_ = run(P, cp_)
            ph_c = phased_row(cp_, sc_)
            timing.append(dict(tag=tag, name=name, offset=off, year=T + off, sell=sc_['real_sell'],
                               lump=ph_c['lump'], park24=ph_c['park24'], park36=ph_c['park36']))
    out['crash_timing'] = timing

    # self-tests recorded with the output
    out['selftest'] = dict(phased_zero_returns=phased_selftest(), mixed_never_sold=mixed_selftest()[0])

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
    ph = o['phased']
    print('phased baseline', {k: round(v) for k, v in ph['baseline'].items() if not k.endswith(('_T1', '_T10'))})
    print('phased replay wins', ph['replay_wins'], 'gap24', ph['replay_gap24'], 'gap36', ph['replay_gap36'])
    print('mixed baseline', {k: round(v) for k, v in o['mixed']['baseline'].items()})
    print('whatif cells', len(o['whatif']['cells']), 'selftest', o['selftest'])
