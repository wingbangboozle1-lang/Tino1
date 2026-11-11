#!/usr/bin/env python3
"""Independent recomputation of the headline figures (session 84ad24ba, task S84-1).

Standard library only.   Run from the repository root:

    python3 final/model.py            # writes final/out/model.json
    python3 audit-84ad24ba/recompute.py

What it does
  * takes ONLY the input table `P` from final/model.py (so no owner figure is
    copied into this directory);
  * recomputes every headline figure with its own formulas and its own loops -
    it never calls simulate() or any other function of final/model.py;
  * compares each result (a) with final/out/model.json and (b) with the dollar
    figures printed on the published root pages;
  * writes audit-84ad24ba/recompute_result.json with the name of each check,
    the difference in dollars and pass / fail.  No owner-derived amount is
    written to that file.
"""
import importlib.util, json, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location('model_inputs', os.path.join(ROOT, 'final', 'model.py'))
_m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_m)          # defines P; main() is not run
P = dict(_m.P)
Y0, Y1 = 2026, 2076


def r10(x):
    return int(round(x / 10.0)) * 10


def at_inheritance(T):
    """Closed-form values in the year of inheritance T (baseline constant rates)."""
    n = T - Y0
    cpi = (1 + P['infl']) ** n
    fmv = P['cup_value'] * (1 + P['g_cup']) ** n
    fbyv = P['cup_assessed'] * 1.02 ** n                      # inflation 2.5% is above the 2% cap
    odd_after_2027 = len([y for y in range(2029, T + 1) if y % 2 == 1])
    cap = P['p19_cap'] * (1 + P['g_ca_2026']) * (1 + P['g_ca']) ** odd_after_2027
    taxable_live = fbyv + max(0.0, fmv - (fbyv + cap))
    fixed = P['dc_cup'] * cpi
    tax_before = fbyv * P['rate_cup'] + fixed
    tax_live = (taxable_live - P['hox']) * P['rate_cup'] + fixed
    tax_rent = fmv * P['rate_cup'] + fixed
    excl = P['excl_2027'] * (1 + P['infl']) ** (T - 2027)
    ins = P['ins_home'] * (1 + P['infl'] + P['ins_premium']) ** n
    maint = P['maint_cup'] * cpi
    hold = 0.5 * (tax_rent + ins + maint)
    proceeds = fmv * (1 - P['sell_cost'] - P['doc_transfer_tax'])
    return dict(cpi=cpi, fmv=fmv, fbyv=fbyv, cap=cap, excluded=fbyv + cap, taxable_live=taxable_live,
                tax_before=tax_before, tax_live=tax_live, tax_rent=tax_rent, exclusion=excl,
                room=excl - fmv, proceeds=proceeds, gain=proceeds - fmv, hold=hold, net=proceeds - hold,
                ins=ins, maint=maint)


class Account:
    """Taxable account: dividends (and interest) taxed each year, growth taxed when sold."""

    def __init__(self):
        self.b = 0.0
        self.k = 0.0

    def add(self, x):
        self.b += x
        self.k += x

    def year(self, part=1.0):
        t_div = P['t_fed_ltcg'] + P['niit'] + P['t_ca']
        t_int = P['t_fed_ord'] + P['niit'] + P['t_ca']
        rs, rb, rc = P['r_stock'] * part, P['r_bond'] * part, P['r_bill'] * part
        div = self.b * P['w_stock'] * P['div_yield'] * part
        inc = self.b * (P['w_bond'] * rb + P['w_bill'] * rc)
        tax = div * t_div + inc * t_int
        self.b = self.b * (1 + P['w_stock'] * rs + P['w_bond'] * rb + P['w_bill'] * rc) - tax
        self.k += div + inc - tax

    def cash_out(self):
        t = P['t_fed_ltcg_lump'] + P['niit'] + P['t_ca_lump']
        return self.b - t * (self.b - self.k)


def wealth_2076(T):
    """Own year-by-year loops for the three choices; returns after-tax wealth in 2076 (nominal) and the price level."""
    a = at_inheritance(T)
    t_ord = P['t_fed_ord'] + P['niit'] + P['t_ca']
    t_lump = P['t_fed_ltcg_lump'] + P['niit'] + P['t_ca_lump']
    t_recap = P['t_recap_fed'] + P['niit'] + P['t_ca_lump']
    sell, rent, live = Account(), Account(), Account()
    basis = a['fmv']                                           # reset to market value at death
    depr_total, carried_loss = 0.0, 0.0
    w10 = None
    for y in range(T, Y1 + 1):
        n = y - Y0
        k = y - T
        cpi = (1 + P['infl']) ** n
        value = P['cup_value'] * (1 + P['g_cup']) ** n
        fixed = P['dc_cup'] * cpi
        ins = P['ins_home'] * (1 + P['infl'] + P['ins_premium']) ** n
        maint = P['maint_cup'] * cpi
        water = P['cup_water'] * (1 + P['infl'] + P['water_premium']) ** n
        elec = P['cup_elec'] * (1 + P['infl'] + P['elec_premium']) ** n
        # --- sell: proceeds invested half-way through year T
        if y == T:
            sell.add(a['net'] - max(a['gain'], 0.0) * t_lump)
            sell.year(0.5)
        else:
            sell.year()
        # --- live and rent: last year's balance grows, then this year's cash flow is added
        live.year()
        rent.year()
        av_live = min(a['taxable_live'] * 1.02 ** k, value)
        tax_live = max(av_live - P['hox'], 0.0) * P['rate_cup'] + fixed
        g_ctrl, g_mkt = 0.6 * P['infl'], P['infl'] + P['rent_premium']
        unit3 = P['sf_unit3_rent'] * (1 + 0.5 * g_ctrl + 0.5 * g_mkt) ** n
        unit3_net = unit3 * (1 - P['vacancy']) * (1 - t_ord) if P['rent_sf_unit3'] else 0.0
        live.add(unit3_net - (tax_live + ins + maint + water + elec))
        av_rent = min(a['fmv'] * 1.02 ** k, value)
        tax_rent = av_rent * P['rate_cup'] + fixed
        collected = P['cup_rent_month'] * 12 * (1 + P['infl'] + P['rent_premium']) ** n * (1 - P['vacancy'])
        noi = collected * (1 - P['mgmt']) - tax_rent - ins - maint
        depr = basis * P['bldg_share'] / P['depr_years'] if k < 28 else 0.0
        if k == 27:
            depr *= 0.5
        depr_total += depr
        taxable = noi - depr - carried_loss
        if taxable < 0:
            carried_loss, income_tax = -taxable, 0.0
        else:
            carried_loss, income_tax = 0.0, taxable * t_ord
        rent.add(noi - income_tax)
        # --- value if everything were sold at the end of this year
        net_sale = value * (1 - P['sell_cost'] - P['doc_transfer_tax'])
        excl121 = P['sec121'] if k >= 2 else 0.0
        w_live = live.cash_out() + net_sale - max(net_sale - basis - excl121, 0.0) * t_lump
        g_all = net_sale - (basis - depr_total) - carried_loss
        recap = min(depr_total, max(g_all, 0.0))
        w_rent = rent.cash_out() + net_sale - recap * t_recap - max(g_all - recap, 0.0) * t_lump
        w_sell = sell.cash_out()
        if k == 10:
            w10 = dict(live=w_live, rent=w_rent, sell=w_sell)
    return dict(live=w_live, rent=w_rent, sell=w_sell, cpi=(1 + P['infl']) ** (Y1 - Y0), w10=w10)


def page_text():
    out = []
    for f in sorted(os.listdir(ROOT)):
        if f.endswith('.html'):
            s = open(os.path.join(ROOT, f), encoding='utf-8').read()
            s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
            out.append(html.unescape(re.sub(r'<[^>]+>', ' ', s)))
    return ' '.join(out)


def money(x):
    v = r10(x)
    return ('-$' if v < 0 else '$') + format(abs(v), ',d')


def main():
    mj = os.path.join(ROOT, 'final', 'out', 'model.json')
    if not os.path.exists(mj):
        sys.exit('run "python3 final/model.py" first (final/out/model.json is not kept in Git)')
    model = json.load(open(mj))
    text = page_text()
    checks = []

    def check(name, mine, theirs=None, on_page=True):
        diff = None if theirs is None else round(mine - theirs, 2)
        ok_model = True if theirs is None else abs(mine - theirs) < 1.0
        shown = money(mine) in text if on_page else None
        checks.append(dict(check=name, difference_to_model_usd=diff, matches_model=ok_model,
                           printed_on_a_published_page=shown,
                           passed=bool(ok_model and (shown is None or shown))))

    for T in (2040, 2045, 2050):
        a = at_inheritance(T)
        s = model['baseline']['summary'] if T == 2045 else model['by_T'][str(T)]
        tag = 'inheritance in %d: ' % T
        check(tag + 'market value of Property A', a['fmv'], s['fmv_T'])
        check(tag + 'assessed value just before', a['fbyv'], s['fbyv_T'], on_page=(T == 2045))
        check(tag + 'Proposition 19 allowance', a['cap'], s['cap_T'], on_page=(T == 2045))
        check(tag + 'new assessed value if lived in', a['taxable_live'], s['taxable_live_T'])
        check(tag + 'first-year tax if lived in', a['tax_live'], s['tax_live_T'])
        check(tag + 'first-year tax if rented', a['tax_rent'], s['tax_rent_T'])
        check(tag + 'federal exclusion', a['exclusion'], s['exclusion_T'])
        check(tag + 'room under the exclusion', a['room'], s['exclusion_T'] - s['fmv_T'])
        check(tag + 'net proceeds if sold', a['net'], s['sell_net'])
        w = wealth_2076(T)
        for kname, label in (('sell', 'sell and reinvest'), ('rent', 'rent it out'), ('live', 'live in it')):
            check(tag + 'after-tax wealth in 2076, ' + label, w[kname], s['w_' + kname])
            check(tag + 'the same in 2026 dollars, ' + label, w[kname] / w['cpi'], s['real_' + kname])
            check(tag + 'after-tax wealth 10 years later, ' + label, w['w10'][kname], s['w10'][kname])
    a = at_inheritance(2045)
    s = model['baseline']['summary']
    check('inheritance in 2045: tax just before inheritance', a['tax_before'], s['tax_before_T'])
    check('inheritance in 2045: excluded amount', a['excluded'], s['excluded_T'])
    check('inheritance in 2045: gain or loss on the sale', a['gain'], s['sell_gain'])
    check('inheritance in 2045: six months of carrying cost', a['hold'], s['sell_hold'])
    check('Property B: yearly tax kept by not selling', (P['sf_value'] - P['sf_assessed']) * P['rate_sf'])
    for row in model['estate']:
        b = at_inheritance(row['T'])
        estate = b['fmv'] + row['cash_today'] * b['cpi']
        tax = max(0.0, estate - b['exclusion']) * P['estate_rate']
        check('estate table %d, cash %s: federal estate tax' % (row['T'], format(row['cash_today'], ',d')),
              tax, row['tax'], on_page=False)
    bad = [c for c in checks if not c['passed']]
    json.dump(dict(checks=checks, total=len(checks), failed=len(bad)),
              open(os.path.join(HERE, 'recompute_result.json'), 'w'), indent=1)
    for c in bad:
        print('FAIL', c)
    print('%d checks, %d failed' % (len(checks), len(bad)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
