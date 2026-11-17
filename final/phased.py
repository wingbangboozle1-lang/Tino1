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
    # mdd3 = the worst fall inside the first three years only: the window the brief calls crash-entry risk.
    return dict(end=v[-1], mdd=max_drawdown(v), mdd3=max_drawdown(v[:4]),
                floor3=min(1.0, min(v[:4])))


def lump_end(R, s):
    return metrics(R, s, 0, 1)['end']


# Official Treasury annual averages, read on 2026-11-16 (session arena/83baf48f-tino1) from the FRED
# graph endpoint with fq=Annual&fam=avg: GS2 = 2-year constant-maturity Treasury yield (H.15);
# TB3MS = 3-month Treasury bill secondary market rate. Percent per year.
GS2_AVG = {2006: 4.82, 2007: 4.36, 2008: 2.00, 2009: 0.96, 2010: 0.70, 2011: 0.45}
TB3MS_AVG = {2006: 4.73, 2007: 4.35, 2008: 1.37, 2009: 0.15, 2010: 0.14, 2011: 0.05}


def official_check(R):
    """Cross-check the bill proxy against the official 3-month series, then test the 2-year sleeve.

    The sleeve return for 2007-2010 is replaced by the 2-year yield annual average (a yield, not a
    total return: a 2-year bought in those years would also have gained or lost on price, which this
    test does not model). Other years are unchanged. Only a sensitivity; the page's main test is not changed.
    """
    out = dict(gs2_avg_pct=GS2_AVG, tb3ms_avg_pct=TB3MS_AVG, nyu_bill_minus_tb3ms_pts={}, sleeve_2y={})
    for y in range(2007, 2011):
        out['nyu_bill_minus_tb3ms_pts'][str(y)] = round(R[y]['bill'] * 100 - TB3MS_AVG[y], 2)
        out.setdefault('gs2_minus_tb3ms_pts', {})[str(y)] = round(GS2_AVG[y] - TB3MS_AVG[y], 2)
    R2 = {y: dict(v) for y, v in R.items()}
    for y in range(2007, 2011):
        R2[y]['bill'] = GS2_AVG[y] / 100.0
    for s in (2007, 2008):
        rows = {}
        for n, k in ((2, 2), (2, 3), (3, 2), (3, 3)):
            a = metrics(R, s, n, k)['end']
            b = metrics(R2, s, n, k)['end']
            rows['park%d_phase%d' % (n, k)] = dict(bill_proxy_end=round(a, 4), two_year_sleeve_end=round(b, 4),
                                                  change_pct_of_proceeds=round((b - a) * 100, 2))
        rows['lump_end'] = round(metrics(R, s, 0, 1)['end'], 4)
        out['sleeve_2y'][str(s)] = rows
    return out


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
                    ('2000 entry (dot-com peak)', 2000), ('2007 entry (housing and stock peak)', 2007),
                    ('2008 entry (the crash year itself)', 2008)):
        if s in per['lump']:
            l_end, l_mdd, l_mdd3 = per['lump'][s]['end'], per['lump'][s]['mdd'], per['lump'][s]['mdd3']
            out['episodes'][str(s)] = dict(
                label=name,
                paths={k: dict(end=per[k][s]['end'], mdd=per[k][s]['mdd'],
                               mdd3=per[k][s]['mdd3'], floor3=per[k][s]['floor3'],
                               # how the path ends against the lump sum, and how much shallower its worst fall is
                               end_vs_lump=per[k][s]['end'] / l_end - 1,
                               mdd_relief_pts=(per[k][s]['mdd'] - l_mdd) * 100,
                               mdd3_relief_pts=(per[k][s]['mdd3'] - l_mdd3) * 100) for k, _, _ in paths},
                bill_avg_parked=statistics.mean(R[y]['bill'] for y in range(s, s + 2)),
                bill_avg_parked_24=statistics.mean(R[y]['bill'] for y in range(s, s + 2)),
                bill_avg_parked_36=statistics.mean(R[y]['bill'] for y in range(s, s + 3)),
                # the same money left in bills for the whole ten years: the floor a parked path cannot fall below
                all_cash_end=metrics(R, s, HORIZON, 1)['end'],
                lump_end=l_end, lump_mdd=l_mdd, lump_mdd3=l_mdd3,
                stock_1yr=R[s]['stock'], stock_2yr=(1 + R[s]['stock']) * (1 + R[s + 1]['stock']) - 1,
                stock_3yr=(1 + R[s]['stock']) * (1 + R[s + 1]['stock']) * (1 + R[s + 2]['stock']) - 1,
                stock_years={str(y): R[y]['stock'] for y in range(s, s + 5)},
                bill_years={str(y): R[y]['bill'] for y in range(s, s + 5)})
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
    out['official_check'] = official_check(R)
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
