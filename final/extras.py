#!/usr/bin/env python3
"""Mixed paths and phased reinvestment (session arena/88de34f6).  Standard library only.

Built on final/model.py. The per-year rows that model.run() produces for the
three pure choices (live, rent, sell) are re-used, and this module composes them into:

  * MIXED PLANS - live in Property A (or rent it out) for K years, then sell it;
  * PHASED REINVESTMENT - the sale proceeds sit in a 3-month-to-2-year Treasury
    sleeve and move linearly into stocks over 24 or 36 months after the sale.

The sleeve return is the model's 3-month T-bill series (a proxy for a 3M-2Y
Treasury ladder; the 2-year series is not loaded - flag A21). Interest on the sleeve is
taxed as ordinary income; stock growth is taxed as the model taxes it.

Self-check: the pure plans rebuilt here must reproduce model.run()'s summary to
within $1 for every replay path, or the module refuses to produce output.

Units: every dollar output here is rounded to $10 before it leaves this module.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as MD  # noqa: E402

P = MD.P
Y0, Y1 = MD.Y0, MD.Y1
Acct = MD.Acct


def r10(x):
    return int(round(x / 10.0)) * 10


# plan key -> (label, mode, years of occupancy K (None = never sold), phase in years (0 = all stocks at once))
PLANS = [
    ('live', 'Live in Property A (pure)', 'live', None, 0),
    ('rent', 'Rent Property A out (pure)', 'rent', None, 0),
    ('sell', 'Sell at inheritance, all in stocks (pure)', 'sell', 0, 0),
    ('sell_p24', 'Sell, park in 3M-2Y Treasuries 24 months, then stocks', 'sell', 0, 2),
    ('sell_p36', 'Sell, park in 3M-2Y Treasuries 36 months, then stocks', 'sell', 0, 3),
    ('live5_sell', 'Live 5 years, then sell (mixed)', 'live', 5, 0),
    ('live10_sell', 'Live 10 years, then sell (mixed)', 'live', 10, 0),
    ('rent5_sell', 'Rent 5 years, then sell (mixed)', 'rent', 5, 0),
    ('rent10_sell', 'Rent 10 years, then sell (mixed)', 'rent', 10, 0),
    ('rent5_sell_p24', 'Rent 5 years, sell, park 24 months, then stocks (mixed + phased)', 'rent', 5, 2),
]
PLAN = {k: dict(label=l, mode=m, K=K, phase=ph) for k, l, m, K, ph in PLANS}


def _weights(p, f):
    """Stock weight f during a year (rest in the Treasury sleeve). f None -> the model's own weights."""
    q = dict(p)
    if f is None:
        return q
    f = min(1.0, max(0.0, f))
    q['w_stock'] = f
    q['w_bill'] = 1.0 - f
    q['w_bond'] = 0.0
    return q


def _t_lump(p):
    return p['t_fed_ltcg_lump'] + p['niit'] + p['t_ca_lump']


def _t_recap(p):
    return p['t_recap_fed'] + p['niit'] + p['t_ca_lump']


def _house_tax(p, mode, net_sale, basis, depr_cum, susp, years_owned):
    """Tax if the house were sold now. Same rules as model.simulate (sale-year wealth)."""
    if mode == 'live':
        excl121 = p['sec121'] if years_owned >= 2 else 0.0
        return max(net_sale - basis - excl121, 0.0) * _t_lump(p), net_sale - basis - excl121
    g_tot = net_sale - (basis - depr_cum) - susp
    recap = min(depr_cum, max(g_tot, 0.0))
    return recap * _t_recap(p) + max(g_tot - recap, 0.0) * _t_lump(p), g_tot


def run_plan(path, p, key, rows=None):
    """Rebuild one plan from the model's per-year rows. Returns dollars and real (2026) values."""
    spec = PLAN[key]
    mode, K, phase = spec['mode'], spec['K'], spec['phase']
    T = p['T']
    if rows is None:
        rows, _ = MD.run(p, path)
    R = {r['year']: r for r in rows}
    sale = T if mode == 'sell' else (None if K is None else T + K)
    v_T = R[T]['cup_value']
    basis = v_T if p['step_up'] else min(float(p['cup_assessed']), v_T)
    occ, cash = Acct(), Acct()          # occupancy portfolio (live / rent) and sale-proceeds portfolio
    depr_cum, susp = 0.0, 0.0
    sold = False
    W = {}
    sale_info = None
    for y in range(T, Y1 + 1):
        e, r = path[y], R[y]
        Vc = r['cup_value']
        net_sale = Vc * (1 - p['sell_cost'] - p['doc_transfer_tax'])
        if sold:
            if mode in ('live', 'rent'):
                occ.grow(e, p)
            cash.grow(e, _weights(p, (y - sale) / float(phase) if phase else None))
            W[y] = occ.liq(p) + cash.liq(p)
            continue
        if mode in ('live', 'rent'):
            occ.grow(e, p, frac=0.5 if y == sale else 1.0)
        if sale is not None and y == sale:
            # sold mid-year: six months of carrying cost, as the model does
            hold = 0.5 * (r['rent_tax'] + r['ins_home'] + r['cup_maint'])
            if mode == 'sell':
                gain = net_sale - basis
                tax, gain_out = max(gain, 0.0) * _t_lump(p), gain
            else:
                tax, gain_out = _house_tax(p, mode, net_sale, basis, depr_cum, susp, y - T)
            cash.add(net_sale - tax - hold)
            cash.grow(e, _weights(p, 0.0 if phase else None), frac=0.5)
            sold = True
            sale_info = dict(proceeds=net_sale, gain=gain_out, tax=tax, hold=hold, net=net_sale - tax - hold)
            W[y] = occ.liq(p) + cash.liq(p)
            continue
        # still living in it or renting it out during year y
        if mode == 'rent':
            ti = r['rent_noi'] - r['rent_depr'] - susp
            susp = -ti if ti < 0 else 0.0
            depr_cum += r['rent_depr']
            occ.add(r['rent_noi'] - r['rent_income_tax'])
        elif mode == 'live':
            occ.add(r['live_unit3'] - r['live_cost'])
        house, _ = _house_tax(p, mode, net_sale, basis, depr_cum, susp, y - T) if mode != 'sell' else (0.0, 0.0)
        W[y] = occ.liq(p) + (net_sale - house if mode != 'sell' else 0.0)
    last = Y1
    out = dict(w_end=W[last], cpi_end=R[last]['cpi'], real_end=W[last] / R[last]['cpi'])
    for h in (10, 20):
        if T + h <= Y1:
            out['w%d' % h] = W[T + h]
            out['real%d' % h] = W[T + h] / R[T + h]['cpi']
    out['sale'] = sale_info
    return out


def self_check(path, p, rows):
    """Pure plans must reproduce the model's own summary (to $1)."""
    _, s = MD.simulate(path, p)
    _ = rows
    for key, field in (('live', 'w_live'), ('rent', 'w_rent'), ('sell', 'w_sell')):
        mine = run_plan(path, p, key, rows=rows)['w_end']
        if abs(mine - s[field]) > 1.0:
            raise SystemExit('self-check failed for %s: %.2f vs model %.2f' % (key, mine, s[field]))
    return True


# ---------------------------------------------------------------------------- scenarios
def crisis_paths(p):
    """The crisis paths the Black swan page already uses, reproduced here (same definitions as model.main)."""
    T = p['T']
    return [
        ('crash_at_T', '2007-2012 housing and stock bust starting the year of inheritance (2008-type entry)',
         MD.overlay_path(p, MD.HIST, 2007, 2012, T)),
        ('depression_at_T', '1929-1941 national Depression sequence starting the year of inheritance (1929-type entry)',
         MD.overlay_path(p, MD.NAT, 1929, 1941, T)),
        ('lost_decade_at_T', '2000-2009 "lost decade" for stocks starting the year of inheritance',
         MD.overlay_path(p, MD.HIST, 2000, 2009, T)),
        ('slump_at_T', '1990-1996 California housing slump starting the year of inheritance',
         MD.overlay_path(p, MD.HIST, 1990, 1996, T)),
        ('japan_at_T', "Japan's real 1991-2020 stagnation starting the year of inheritance",
         MD.overlay_path(p, MD.JPN, 1991, 2020, T)),
        ('replay_2000', 'Real 1976-2025 sequence started in 2000 (dot-com bust and 2008 crisis first)',
         MD.replay_path(2000)),
    ]


def window_stock_drawdown(path, p, first, last):
    """Peak-to-trough fall of the cumulative stock index over the overlay years (from the same series the model uses)."""
    idx, peak, worst = 1.0, 1.0, 0.0
    T = p['T']
    for y in range(T, T + (last - first) + 1):
        idx *= 1 + path[y]['r_stock']
        peak = max(peak, idx)
        worst = min(worst, idx / peak - 1.0)
    return worst


def _plan_row(o, key):
    return dict(plan=key, real_end=o['real_end'], real10=o.get('real10'), real20=o.get('real20'))


def compute():
    p = P
    base_path = MD.baseline_path(p)
    rows0, _ = MD.run(p, base_path)
    self_check(base_path, p, rows0)
    X = {'plans': [dict(key=k, label=PLAN[k]['label'], mode=PLAN[k]['mode'], K=PLAN[k]['K'], phase_years=PLAN[k]['phase'])
                   for k, _, _, _, _ in PLANS]}
    X['baseline'] = {k: run_plan(base_path, p, k, rows=rows0) for k in PLAN}
    T = p['T']
    # ---- crisis paths: 2008-type and 1929-type entries, plus the real replays
    crises = []
    for key, label, path in crisis_paths(p):
        rows, _ = MD.run(p, path)
        self_check(path, p, rows)
        res = {k: run_plan(path, p, k, rows=rows) for k in ('sell', 'sell_p24', 'sell_p36', 'live', 'rent', 'rent5_sell')}
        dd = None
        if key == 'crash_at_T':
            dd = window_stock_drawdown(path, p, 2007, 2012)
        if key == 'depression_at_T':
            dd = window_stock_drawdown(path, p, 1929, 1941)
        crises.append(dict(key=key, label=label, drawdown=dd, res=res))
    X['crises'] = crises
    # ---- all 50 real starting years (1976-2025)
    reps = []
    for st in range(1976, 2026):
        path = MD.replay_path(st)
        rows, _ = MD.run(p, path)
        self_check(path, p, rows)
        reps.append(dict(start=st, res={k: run_plan(path, p, k, rows=rows) for k in PLAN}))
    X['replays'] = reps

    def stats(key, field):
        vals = sorted(r['res'][key][field] for r in reps)
        return dict(min=vals[0], median=vals[len(vals) // 2], max=vals[-1])

    summ = {}
    for k in PLAN:
        summ[k] = dict(real10=stats(k, 'real10'), real_end=stats(k, 'real_end'))
    X['replay_stats'] = summ
    # phased versus immediate sale, across the 50 real starting years
    ph = {}
    for k in ('sell_p24', 'sell_p36'):
        d10 = [r['res'][k]['real10'] - r['res']['sell']['real10'] for r in reps]
        dE = [r['res'][k]['real_end'] - r['res']['sell']['real_end'] for r in reps]
        ph[k] = dict(wins10=sum(1 for x in d10 if x > 0), winsE=sum(1 for x in dE if x > 0), n=len(reps),
                     worst10=min(d10), median10=sorted(d10)[len(d10) // 2], worstE=min(dE), medianE=sorted(dE)[len(dE) // 2])
    X['phase_vs_sell'] = ph
    # ---- what-if grid (every combination the page offers; each one a full model run)
    grid = {}
    for Tt in (2040, 2045, 2050):
        for rs in (0.05, 0.07, 0.10):
            for inf in (0.02, 0.025, 0.035):
                for cost in (0.05, 0.07):
                    shift = inf - 0.025
                    q = MD.with_(T=Tt, r_stock=rs, infl=inf, g_cup=0.04 + shift, g_sf=0.04 + shift,
                                 g_ca=0.04 + shift, r_bond=0.045 + shift, r_bill=0.035 + shift,
                                 sell_cost=cost)
                    path = MD.baseline_path(q)
                    rows, _ = MD.run(q, path)
                    key = '%d|%s|%s|%s' % (Tt, rs, inf, cost)
                    grid[key] = {}
                    for k in ('live', 'rent', 'sell', 'sell_p24', 'sell_p36', 'rent5_sell'):
                        o = run_plan(path, q, k, rows=rows)
                        grid[key][k] = dict(real_end=o['real_end'], real10=o.get('real10'))
    X['grid'] = grid
    return X


def r10_all(o):
    """Round every dollar in a nested structure to $10 (ratios and counts unchanged)."""
    if isinstance(o, dict):
        return {k: r10_all(v) for k, v in o.items()}
    if isinstance(o, list):
        return [r10_all(v) for v in o]
    if isinstance(o, float) and abs(o) >= 1000:
        return r10(o)
    return o


if __name__ == '__main__':
    import json
    X = compute()
    print('self-checks passed; replays', len(X['replays']), 'grid', len(X['grid']))
    print(json.dumps(X['phase_vs_sell'], indent=1)[:900])
    for c in X['crises']:
        print(c['key'], round(c['drawdown'] or 0, 3) if c['drawdown'] is not None else '-',
              {k: round(v['real10']) for k, v in c['res'].items()})
