#!/usr/bin/env python3
"""Phased-entry test for the inheritance proceeds (session 1a8bae22). Standard library only.

  python3 final/phased_1a8bae22.py      ->  final/out/phased_1a8bae22.json

Question: if the after-tax sale proceeds are parked in short Treasuries for 24 or 36 months
after the inheritance and only then phased into stocks, does that soften entry risk in a
1929-style or 2008-style crash, and what does it cost in a normal market?

Method (annual data, so read it as a stress test, not a forecast):
  * Starting capital = the after-tax net sale proceeds the model already computes (model.json, sell_net).
  * Stocks: S&P 500 total return by calendar year (academic table, final/data/hist_returns_damodaran.csv).
  * Parking: 3-month Treasury bill return by calendar year from the same table. The 2-year Treasury
    (FRED GS2) is only in the repository for 2007-2010 (final/data/fred_gs2_monthly_2007_2010.csv); it is
    compared with the bill series in the output, not used in the simulation.
  * Each calendar year's return is spread evenly over its 12 months (so a crash inside a year is
    not separated from the rest of the year: the intra-year path is smoothed; flagged on the page).
  * Strategies over a 10-year horizon from 1 January of the entry year:
      lump     : all in stocks on day 0
      park24   : all in bills for 24 months, then 12 equal monthly tranches into stocks
      park36   : all in bills for 36 months, then 12 equal monthly tranches into stocks
      bills    : all in bills (reference: no stock exposure at all)
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
C0 = None
M = json.load(open(os.path.join(HERE, 'out', 'model.json')))
C0 = round(M['by_T']['2045']['sell_net'] / 10.0) * 10   # after-tax net sale proceeds from the model, rounded to $10
RET = {int(r['year']): {'stock': float(r['sp500_total_return_pct']) / 100, 'bill': float(r['tbill_3m_pct']) / 100}
       for r in csv.DictReader(open(os.path.join(HERE, 'data', 'hist_returns_damodaran.csv')))}
GS2 = [dict(year=int(r['year']), month=int(r['month']), gs2=float(r['gs2_pct']) / 100)
       for r in csv.DictReader(open(os.path.join(HERE, 'data', 'fred_gs2_monthly_2007_2010.csv')))]
HORIZON_Y = 10
LAST_Y = max(RET)                            # 2025
STRATS = {'lump': (0, 0), 'park24': (24, 12), 'park36': (36, 12), 'bills': (None, None)}


def run(entry, strat, horizon_y=HORIZON_Y, c0=None):
    c0 = C0 if c0 is None else c0
    park, phase = STRATS[strat]
    H = horizon_y * 12
    stock, cash = 0.0, c0
    if park == 0:
        stock, cash = c0, 0.0
    vals = []
    park_years = []
    for i in range(H + 1):
        if park and park <= i < park + phase:
            amt = min(cash, c0 / phase)
            cash -= amt
            stock += amt
        if strat == 'bills':
            pass
        vals.append(stock + cash)
        if i == H:
            break
        y = entry + i // 12
        if park and i < park:
            park_years.append(y)
        ms = (1 + RET[y]['stock']) ** (1 / 12) - 1
        mb = (1 + RET[y]['bill']) ** (1 / 12) - 1
        if strat == 'bills':
            cash *= 1 + mb
        else:
            stock *= 1 + ms
            cash *= 1 + mb
    peak, mdd = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    trough = min(vals)
    return dict(strategy=strat, entry=entry, end=vals[-1], trough=trough,
                trough_vs_start=trough / c0 - 1, max_drawdown=mdd,
                end_vs_start=vals[-1] / c0 - 1, park_years=park_years,
                trough_month=vals.index(trough))


def geo(vals):
    p = 1.0
    for v in vals:
        p *= 1 + v
    return p ** (1 / len(vals)) - 1 if vals else 0.0


def named(entry, label, note):
    rows = {s: run(entry, s) for s in STRATS}
    park_bill = [RET[y]['bill'] for y in range(entry, entry + 3)]
    stock_yrs = [RET[y]['stock'] for y in range(entry, entry + 3)]
    return dict(entry=entry, label=label, note=note, results=rows,
                bill_3y_avg=geo(park_bill), stock_3y_avg=geo(stock_yrs),
                bill_path=[dict(year=y, bill=RET[y]['bill'], stock=RET[y]['stock']) for y in range(entry - 1, entry + 4)])


def main():
    out = {'C0': C0, 'horizon_y': HORIZON_Y, 'data_last_year': LAST_Y,
           'assumptions': dict(park_phase_months=12, return_spread='even monthly within calendar year',
                               parking_series='3-month Treasury bill (academic table, 1928-2025)'),
           'named': [], 'robust': {}, 'gs2_check': []}
    out['named'].append(named(1929, '1929 entry: start of the year the market peaked (Sept. 1929), then the Great Depression',
                              'Entry on 1 January 1929 (annual data cannot place the Sept. 1929 peak or the Oct. 1929 crash inside the year).'))
    out['named'].append(named(2008, '2008 entry: start of the year after the Oct. 2007 peak and during the 2008 crash',
                              'Entry on 1 January 2008 (the 2008 fall is inside the first year of the test).'))
    # robustness: every entry year that has a full 10-year window in the data
    entries = list(range(min(RET), LAST_Y - HORIZON_Y + 2))
    rob = {}
    for s in STRATS:
        res = [run(e, s) for e in entries]
        rob[s] = dict(n=len(res), median_end=sorted(r['end'] for r in res)[len(res) // 2],
                      median_mdd=sorted(r['max_drawdown'] for r in res)[len(res) // 2],
                      worst_trough=min(r['trough'] for r in res))
    lump = {e: run(e, 'lump') for e in entries}
    for s in ('park24', 'park36'):
        pr = {e: run(e, s) for e in entries}
        rob[s]['share_end_above_lump'] = sum(pr[e]['end'] > lump[e]['end'] for e in entries) / len(entries)
        rob[s]['share_mdd_shallower'] = sum(pr[e]['max_drawdown'] > lump[e]['max_drawdown'] for e in entries) / len(entries)
        rob[s]['share_trough_above_lump'] = sum(pr[e]['trough'] > lump[e]['trough'] for e in entries) / len(entries)
        rob[s]['median_end_vs_lump'] = sorted(pr[e]['end'] - lump[e]['end'] for e in entries)[len(entries) // 2]
    rob['entry_years'] = [entries[0], entries[-1]]
    rob['n_entries'] = len(entries)
    out['robust'] = rob
    # 2-year Treasury cross-check for the 2008 test window (FRED GS2 monthly averages vs the bill series)
    for y in range(2007, 2011):
        vals = [g['gs2'] for g in GS2 if g['year'] == y]
        out['gs2_check'].append(dict(year=y, gs2_avg=sum(vals) / len(vals), bill=RET[y]['bill'], stock=RET[y]['stock']))
    # publication rule: every dollar value stored in the repository is rounded to the nearest $10
    def r10(x):
        return int(round(x / 10.0)) * 10
    for n in out['named']:
        for v in n['results'].values():
            for k in ('end', 'trough'):
                v[k] = r10(v[k])
    for k in ('median_end', 'worst_trough', 'median_end_vs_lump'):
        for s_ in STRATS:
            if k in out['robust'].get(s_, {}):
                out['robust'][s_][k] = r10(out['robust'][s_][k])
    json.dump(out, open(os.path.join(HERE, 'out', 'phased_1a8bae22.json'), 'w'), indent=1)
    return out


if __name__ == '__main__':
    o = main()
    for n in o['named']:
        print(n['entry'], {k: round(v['end']) for k, v in n['results'].items()},
              {k: round(v['trough']) for k, v in n['results'].items()})
    print('robust', json.dumps(o['robust'], indent=1)[:1500])
    print('gs2', o['gs2_check'])
