#!/usr/bin/env python3
"""Phased-investing test on real annual history (session arena/7895b5d7).  Standard library only.

  python3 final/phased.py      ->  final/out/phased.json

Question: the sale proceeds are parked in short Treasuries for N years after the inheritance, then
moved into stocks in K equal annual tranches. Does that soften the entry risk of a crash that starts
right at the entry date (1929, 2007) - and what does it cost in the years with no crash?

Data: NYU Stern annual total returns, 1928-2025 (S&P 500 total return, 3-month Treasury bill return).
This is a NON-GOVERNMENT academic dataset; it is the only annual history in the repository that has
both stock and bill returns back to 1928. The 2-year Treasury series is NOT in the repository, so the
3-month bill stands in for the parked "3-month to 2-year" cash (flagged on the page).

Limits, stated on the page: annual resolution (a calendar year is one step, so an intra-year crash
such as Oct 1929 is only visible as that year's total return); gross of tax, costs and inflation; a
single entry date per test; no rebalancing; no transaction costs.
"""
import csv, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'hist_returns_damodaran.csv')
OUT = os.path.join(HERE, 'out', 'phased.json')
HORIZON = 10                       # years after entry over which every path is compared
PARK = (2, 3)                      # 24 and 36 months in cash (bills), as the brief asks
PHASE = (2, 3)                     # number of equal annual tranches into stocks


def load():
    rows = {}
    for r in csv.DictReader(open(DATA)):
        rows[int(r['year'])] = dict(stock=float(r['sp500_total_return_pct']) / 100,
                                    bill=float(r['tbill_3m_pct']) / 100)
    return rows


def run_path(R, s, park, phase, horizon=HORIZON):
    """Start with 1.0 at the start of year s. Cash earns the 3-month bill return and stock earns the S&P
    total return, one calendar year at a time. Years 0..park-1 are parked; years park..park+phase-1 each
    move an equal share of the ORIGINAL proceeds into stocks at the start of the year (the last tranche
    takes whatever cash is left). park=0, phase=1 is the lump sum into stocks on day one.
    Returns the total value at the start of each year (length horizon+1)."""
    cash, stock = 1.0, 0.0
    vals = [1.0]
    for j in range(horizon):
        y = s + j
        if park <= j < park + phase:
            move = cash / (park + phase - j)    # tranches still to go, including this one
            cash -= move
            stock += move
        cash *= 1 + R[y]['bill']
        stock *= 1 + R[y]['stock']
        vals.append(cash + stock)
    return vals


def max_drawdown(vals):
    peak, worst = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


def metrics(R, s, park, phase):
    v = run_path(R, s, park, phase)
    return dict(end=v[-1], mdd=max_drawdown(v))


def lump_end(R, s):
    return metrics(R, s, 0, 1)['end']


def compute(proceeds=None):
    R = load()
    last_start = max(R) - HORIZON + 1
    starts = sorted(y for y in R if y <= last_start)
    paths = [('lump', 0, 1)] + [('park%d_phase%d' % (n, k), n, k) for n in PARK for k in PHASE]
    out = dict(horizon=HORIZON, first_start=starts[0], last_start=starts[-1],
               paths=[dict(key=k, park_years=n, phase_years=p) for k, n, p in paths], episodes={}, summary={})
    # every entry year: terminal multiple and worst peak-to-trough inside the horizon
    per = {}
    for k, n, p in paths:
        per[k] = {s: metrics(R, s, n, p) for s in starts}
    for name, s in (('1929 entry (Depression crash begins)', 1929), ('1937 entry (second slump)', 1937),
                    ('2000 entry (dot-com peak)', 2000), ('2007 entry (housing and stock peak)', 2007)):
        if s in per['lump']:
            out['episodes'][str(s)] = dict(
                label=name,
                paths={k: dict(end=per[k][s]['end'], mdd=per[k][s]['mdd']) for k, _, _ in paths},
                bill_avg_parked=statistics.mean(R[y]['bill'] for y in range(s, s + 2)),
                stock_1yr=R[s]['stock'], stock_2yr=(1 + R[s]['stock']) * (1 + R[s + 1]['stock']) - 1)
    for k, n, p in paths[1:]:
        diffs = [per[k][s]['end'] / per['lump'][s]['end'] - 1 for s in starts]
        mdds_l = [per['lump'][s]['mdd'] for s in starts]
        mdds_p = [per[k][s]['mdd'] for s in starts]
        out['summary'][k] = dict(
            starts=len(starts),
            share_phased_ends_higher=sum(1 for d in diffs if d > 0) / len(diffs),
            median_end_vs_lump=statistics.median(diffs),
            worst_end_vs_lump=min(diffs),
            median_mdd_lump=statistics.median(mdds_l), median_mdd_phased=statistics.median(mdds_p),
            worst_mdd_lump=min(mdds_l), worst_mdd_phased=min(mdds_p),
            mean_bill_yield=statistics.mean(R[y]['bill'] for y in range(1928, 2026)),
            # worst-drop comparison, year by year: never deeper than the lump sum; strictly shallower in some years
            years_drop_not_deeper=sum(1 for l, p_ in zip(mdds_l, mdds_p) if p_ >= l - 1e-12),
            years_drop_strictly_shallower=sum(1 for l, p_ in zip(mdds_l, mdds_p) if p_ > l + 1e-12),
        )
    out['lump_median_end'] = statistics.median(per['lump'][s]['end'] for s in starts)
    out['bill_stats'] = dict(
        all_1928_2025=statistics.mean(R[y]['bill'] for y in range(1928, 2026)),
        y1929_1931=statistics.mean(R[y]['bill'] for y in range(1929, 1932)),
        y2009_2015=statistics.mean(R[y]['bill'] for y in range(2009, 2016)))
    out['proceeds'] = proceeds
    return out


if __name__ == '__main__':
    import sys
    base = None
    try:
        base = json.load(open(os.path.join(HERE, 'out', 'model.json')))['baseline']['summary']['sell_net']
    except Exception:
        pass
    # the household figure is stored only rounded to the nearest $10 (site rule; the repository is public)
    res = compute(proceeds=None if base is None else int(round(base / 10.0)) * 10)
    json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
    print('wrote', OUT)
    for k, v in res['episodes'].items():
        print(k, v['label'], {p: round(x['end'], 3) for p, x in v['paths'].items()}, {p: round(x['mdd'], 3) for p, x in v['paths'].items()})
    for k, v in res['summary'].items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
