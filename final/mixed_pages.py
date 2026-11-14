#!/usr/bin/env python3
"""Mixed and phased paths page (session arena/88de34f6-tino1). Standard library only.

Called from final/build.py (build_all). Writes paths.html from final/mixed.py. Every table row ends in a
link to an official page (build.src). Every dollar is rounded to $10 (build.m). The phased test here is
the model's own crisis windows (2008-type and 1929-type) and its 50 real starting years; the separate
phased page from session arena/7895b5d7 uses the NYU Stern 1928-2025 table and is not replaced.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mixed as X  # noqa: E402

# bound by build_all(); the names below are used by build_paths()
m = pc = src = table = flag = e = page = None
P = None
T = None


def money_or_dash(v):
    return '&mdash;' if v is None else m(v)


def _sign(v):
    return ('+' if v >= 0 else '') + m(v)


# ------------------------------------------------------------------ mixed and phased paths
def build_paths(D):
    base = D['baseline']
    st = D['replay_stats']
    plan_sources = {
        'live': ('BOE-P19', 'SCC-RATES', 'BOE-HOX'),
        'rent': ('BOE-P19', 'RTC-63.2', 'IRS-P527'),
        'sell': ('IRS-FAQ-INHERIT', 'IRS-TC409'),
        'sell_p24': ('TREASURY', 'IRS-TC409', 'DAMODARAN'),
        'sell_p36': ('TREASURY', 'IRS-TC409', 'DAMODARAN'),
        'live5_sell': ('IRS-TC701', 'BOE-P19', 'IRS-FAQ-INHERIT'),
        'live10_sell': ('IRS-TC701', 'BOE-P19', 'IRS-FAQ-INHERIT'),
        'rent5_sell': ('IRS-P527', 'IRS-TC409', 'RTC-63.2'),
        'rent10_sell': ('IRS-P527', 'IRS-TC409', 'RTC-63.2'),
        'rent5_sell_p24': ('IRS-P527', 'TREASURY', 'IRS-TC409'),
    }
    rows = []
    for pl in D['plans']:
        k = pl['key']
        b = base[k]
        tax = b['sale']['tax'] if b.get('sale') else None
        rows.append([
            e(pl['label']),
            m(b['real10']),
            m(st[k]['real10']['min']),
            m(st[k]['real10']['median']),
            m(b['real_end']),
            money_or_dash(tax),
            src(*plan_sources[k]),
        ])
    t1 = table(
        ['Plan (inheritance in %d; 50 real starting years 1976-2025)' % T,
         'After-tax wealth 10 years after inheritance (2026 dollars)',
         'Worst of 50 starts, 10 years (2026 dollars)',
         'Median of 50 starts, 10 years (2026 dollars)',
         'After-tax wealth in 2076 (2026 dollars)',
         'Tax on the sale (sale-year dollars)',
         'Official basis'],
        rows, caption='Every plan, baseline assumptions, with reinvestment risk shown beside the result',
        note='Reinvestment risk is the "worst of 50 starts" column: the same plan replayed from each of the 50 real starting years. Phased paths park the proceeds in a Treasury sleeve first (flag A14). Mixed paths are conventions set out in flag A16.')

    crow = []
    for c in D['crises']:
        r = c['res']
        dd = c['drawdown']
        srcs = {
            'crash_at_T': ('FHFA-CA', 'BLS-CPI', 'DAMODARAN'),
            'depression_at_T': ('DAMODARAN', 'BLS-CPI'),
            'lost_decade_at_T': ('DAMODARAN', 'BLS-CPI'),
            'slump_at_T': ('FHFA-CA', 'BLS-CPI'),
            'japan_at_T': ('FRED-JP', 'BLS-CPI'),
            'replay_2000': ('DAMODARAN', 'FHFA-SF', 'BLS-CPI'),
        }[c['key']]
        d24 = r['sell_p24']['real10'] - r['sell']['real10']
        d36 = r['sell_p36']['real10'] - r['sell']['real10']
        crow.append([
            e(c['label']),
            ('%s' % pc(dd)) if dd is not None else '&mdash;',
            m(r['sell']['real10']), m(r['sell_p24']['real10']), m(r['sell_p36']['real10']),
            _sign(d24), _sign(d36), src(*srcs),
        ])
    t2 = table(
        ['Crash-entry test: when the crash starts in the inheritance year', 'Stock fall in the window (total return, peak to trough)',
         'Sell now and invest in stocks: 10 years later (2026 dollars)', 'Park 24 months, then stocks: 10 years later',
         'Park 36 months, then stocks: 10 years later', '24-month park minus sell now', '36-month park minus sell now', 'Official basis'],
        crow, caption='Does phasing soften the entry into a crash?',
        note='The 2008-type and 1929-type rows drop a real crash sequence into the baseline at the inheritance year. The real starting years 1976-2025 are tested in the next table. Flags A14, A15, A18.')

    ph = D['phase_vs_sell']
    prow = []
    for label, get in (
            ('Real starting years in which parking wins, measured at 10 years (of 50)', lambda d: str(d['wins10'])),
            ('Real starting years in which parking wins, measured in 2076 (of 50)', lambda d: str(d['winsE'])),
            ('Median difference, 10 years (2026 dollars)', lambda d: _sign(d['median10'])),
            ('Worst difference, 10 years (2026 dollars)', lambda d: _sign(d['worst10'])),
            ('Median difference, 2076 (2026 dollars)', lambda d: _sign(d['medianE'])),
            ('Worst difference, 2076 (2026 dollars)', lambda d: _sign(d['worstE']))):
        prow.append([label, get(ph['sell_p24']), get(ph['sell_p36']), src('TREASURY', 'IRS-TC409')])
    t3 = table(['Measure (parked minus sell now; a negative number means parking was worse)', '24 months', '36 months', 'Official basis'],
               prow, caption='Phasing across all 50 real starting years (1976-2025)',
               note='Phasing is insurance: it helps most when the first years after the entry are bad, and it costs money in the typical case. The table shows both sides.')

    mixed_rows = []
    for k in ('live', 'rent', 'sell', 'live5_sell', 'rent5_sell', 'rent10_sell', 'rent5_sell_p24'):
        lab = [pl['label'] for pl in D['plans'] if pl['key'] == k][0]
        mixed_rows.append([e(lab), m(st[k]['real_end']['median']), m(st[k]['real_end']['min']), m(st[k]['real_end']['max']),
                           src(*plan_sources[k])])
    t4 = table(['Plan', 'Median of 50 starts, in 2076 (2026 dollars)', 'Worst of 50 starts, in 2076', 'Best of 50 starts, in 2076', 'Official basis'],
               mixed_rows, caption='Mixed paths against the three pure choices, across the 50 real starting years',
               note='Mixed paths sit between the pure choices. The model shows a living or renting period followed by a sale; no mixed path is a recommendation.')
    body = ('<section class="summary"><p><strong>How to read this page.</strong> Each row is a complete path for Property A, '
            'run through the same model and the same tax rules as the rest of the site. The baseline inherits in %d. '
            'Phasing is tested on the 2008-type and 1929-type crash sequences and on all 50 real starting years. '
            'Figures are after tax, in 2026 dollars, and rounded to $10. Property B is the same in every row and is left out.</p></section>' % T)
    body += ('<p class="note">Caution on comparing tables: the replay rows carry the real return of each year, and the 1976-2025 record includes stock returns above the 7%% baseline in many years. Compare plans within one table; do not compare a replay median with a baseline figure.</p>')
    body += '<h2>Every plan, with reinvestment risk beside the result</h2>' + t1
    body += '<h2>Crash-entry test</h2>' + t2
    body += '<h2>Phasing across the 50 real starting years</h2>' + t3
    body += '<h2>Mixed paths across the 50 real starting years</h2>' + t4
    body += '<p class="note">Method, conventions and limits: ' + ' '.join(flag(f) for f in ('A14', 'A15', 'A16', 'A17', 'A18')) + ' on the Flagged for Review page. Not tax, legal or investment advice.</p>'
    page('paths.html', 'Mixed and phased paths',
         'Mixed paths (live or rent for some years, then sell) and phased reinvestment (park the proceeds in Treasuries, then move into stocks over 24 or 36 months), tested against the 1929-type and 2008-type crashes.',
         body)




def build_all(Bd):
    g = globals()
    g.update(m=Bd.m, pc=Bd.pc, src=Bd.src, table=Bd.table, flag=Bd.flag, e=Bd.e, page=Bd.page, P=Bd.P, T=Bd.P['T'])
    D = X.compute()
    build_paths(D)
    return D
