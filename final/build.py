#!/usr/bin/env python3
"""Static site generator (session 07a57a05).  Standard library only.

  python3 final/model.py && python3 final/build.py && python3 final/check.py

Writes final/site/*.html.  Every table row carries a link to an official page.
Every dollar figure that comes from the owner or from the model is rounded to $10.
"""
import json, os, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sources import S          # noqa: E402
from flags import FLAGS, REVIEW  # noqa: E402

M = json.load(open(os.path.join(HERE, 'out', 'model.json')))
P = M['params']
B = M['baseline']['summary']
ROWS = M['baseline']['rows']
OUT = os.path.join(HERE, 'site')
Y0 = 2026
T = P['T']
BUILD_DATE = '2026-11-11'
REPO = 'https://github.com/wingbangboozle1-lang/Tino1'


def r10(x):
    return int(round(x / 10.0)) * 10


def m(x):
    v = r10(x)
    return ('-$' if v < 0 else '$') + format(abs(v), ',')


def mm(x):
    """Short form in millions, built from the $10-rounded value."""
    v = r10(x)
    return ('-$' if v < 0 else '$') + ('%.2f' % (abs(v) / 1e6)) + ' million'


def pc(x, d=1):
    return ('%.' + str(d) + 'f%%') % (x * 100)


def e(s):
    return html.escape(str(s), quote=True)


def src(*ids):
    out = []
    for i in ids:
        s = S[i]
        out.append('<a class="src" href="%s" title="%s" rel="noopener">%s</a>' % (e(s['url']), e(s['title']), e(s['label'])))
    return ' · '.join(out)


def table(headers, rows, caption=None, cls='', note=None, tid=None):
    for r in rows:
        assert 'href="http' in r[-1], 'row without an official source link: %r' % (r,)
        assert len(r) == len(headers), (len(r), len(headers), r)
    h = ['<div class="tablewrap"><table class="%s"%s>' % (cls, ' id="%s"' % tid if tid else '')]
    if caption:
        h.append('<caption>%s</caption>' % caption)
    h.append('<thead><tr>' + ''.join('<th scope="col">%s</th>' % x for x in headers) + '</tr></thead><tbody>')
    for r in rows:
        h.append('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>')
    h.append('</tbody></table></div>')
    if note:
        h.append('<p class="note">%s</p>' % note)
    return '\n'.join(h)


def flag(fid):
    return '<a class="flag" href="flagged.html#%s" title="Flagged for review">flag %s</a>' % (fid, fid)


BLANK = '<span class="blank">not confirmed - left blank</span>'

NAV = [
    ('index.html', 'Summary'),
    ('decision.html', 'Decision'),
    ('projections.html', 'Year by year'),
    ('black-swan.html', 'Black swan'),
    ('process.html', 'Process'),
    ('law.html', 'Law'),
    ('estate-cash.html', 'Cash and estate tax'),
    ('costs.html', 'Insurance and costs'),
    ('flagged.html', 'Flagged for Review'),
    ('sources.html', 'Sources and method'),
    ('review.html', 'Repo review'),
]


def page(slug, title, lead, body):
    nav = ''.join('<a href="%s"%s>%s</a>' % (h, ' class="on" aria-current="page"' if h == slug else '', t) for h, t in NAV)
    doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s - Two-home inheritance analysis</title>
<link rel="stylesheet" href="style.css">
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="index.html">Two-home inheritance analysis</a>
<nav aria-label="Sections">%s</nav></div></header>
<main class="wrap">
<h1>%s</h1>
<p class="lead">%s</p>
%s
</main>
<footer class="wrap"><p>Built %s from <a href="%s/tree/main/final">final/</a> (model, generator and checker). Property A = Cupertino home (ZIP 95014). Property B = San Francisco three-unit home (ZIP 94122). People are placeholders: "the Transferor" (current owner of Property A) and "the Inheritor" (already owns Property B). Owner-supplied and modelled dollar figures are rounded to the nearest $10. This is an analysis to prepare questions for a licensed estate attorney and tax adviser, not legal or tax advice. Open items are on the <a href="flagged.html">Flagged for Review</a> page.</p></footer>
<script src="app.js"></script>
</body></html>""" % (e(title), nav, e(title), lead, body, BUILD_DATE, REPO)
    open(os.path.join(OUT, slug), 'w').write(doc)


# ------------------------------------------------------------------ charts (inline SVG)
COL = {'live': '#2f6f4f', 'rent': '#b7791f', 'sell': '#1f4e8c', 'before': '#666', 'x': '#8a3ffc'}


def bars(items, unit='', width=640, bar_h=30, fmt=m):
    mx = max(abs(v) for _, v, _ in items) or 1
    h = len(items) * (bar_h + 14) + 10
    o = ['<svg class="chart" viewBox="0 0 %d %d" role="img" aria-label="Bar chart">' % (width, h)]
    for i, (lab, v, col) in enumerate(items):
        y = 8 + i * (bar_h + 14)
        w = max(2, (width - 330) * abs(v) / mx)
        o.append('<text x="0" y="%d" class="lab">%s</text>' % (y + bar_h * 0.65, e(lab)))
        o.append('<rect x="200" y="%d" width="%.1f" height="%d" fill="%s" rx="3"/>' % (y, w, bar_h, col))
        o.append('<text x="%.1f" y="%d" class="val">%s%s</text>' % (206 + w, y + bar_h * 0.65, fmt(v), unit))
    o.append('</svg>')
    return ''.join(o)


def lines(series, x0, x1, width=720, height=300, yfmt=lambda v: '$%.0fM' % (v / 1e6), mark=None, ymin0=True):
    """series: list of (label, color, {year: value})."""
    allv = [v for _, _, d in series for v in d.values()]
    lo, hi = (0 if ymin0 else min(allv)), max(allv)
    lo = min(lo, min(allv))
    if hi == lo:
        hi = lo + 1
    L, R, Tm, Bm = 62, 12, 12, 34
    X = lambda y: L + (width - L - R) * (y - x0) / float(x1 - x0)
    Y = lambda v: Tm + (height - Tm - Bm) * (1 - (v - lo) / float(hi - lo))
    o = ['<svg class="chart" viewBox="0 0 %d %d" role="img" aria-label="Line chart">' % (width, height)]
    for k in range(5):
        v = lo + (hi - lo) * k / 4.0
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" class="grid"/>' % (L, width - R, Y(v), Y(v)))
        o.append('<text x="%d" y="%.1f" class="ax" text-anchor="end">%s</text>' % (L - 6, Y(v) + 4, yfmt(v)))
    for y in range(x0, x1 + 1):
        if y % 10 == 0 or y == x0:
            o.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%d</text>' % (X(y), height - 12, y))
    if mark:
        o.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="mark"/>' % (X(mark), X(mark), Tm, height - Bm))
        o.append('<text x="%.1f" y="%d" class="ax">inheritance %d</text>' % (X(mark) + 4, Tm + 10, mark))
    for lab, col, d in series:
        pts = ' '.join('%.1f,%.1f' % (X(y), Y(d[y])) for y in sorted(d))
        o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, col))
    o.append('</svg><p class="legend">' + ' '.join('<span><i style="background:%s"></i>%s</span>' % (c, e(l)) for l, c, _ in series) + '</p>')
    return ''.join(o)


# ------------------------------------------------------------------ shared numbers
rT = ROWS[T - Y0]
r26 = ROWS[0]
sf_gap = (P['sf_value'] - P['sf_assessed']) * P['rate_sf']
BE = M['breakeven']
HS = M['hist_stats']
wins = {}
for x in M['replays']:
    wins[x['best']] = wins.get(x['best'], 0) + 1
rep_sorted = lambda k: sorted(x['real_' + k] for x in M['replays'])
NAME = {'live': 'Live in it', 'rent': 'Rent it out', 'sell': 'Sell and reinvest'}
SRC_MODEL_TAX = ('SCC-RATES', 'BOE-LTA-2026-026')


def kpi(label, value, sub=''):
    return '<div class="kpi"><div class="k">%s</div><div class="v">%s</div><div class="s">%s</div></div>' % (label, value, sub)


# ====================================================================== index
def build_index():
    by = M['by_T']
    cards = ''.join([
        kpi('Best financial outcome', 'Sell Property A, keep Property B', 'ahead in the baseline and in %d of 50 real historical sequences' % wins.get('sell', 0)),
        kpi('Property A at inheritance (%d)' % T, m(B['fmv_T']), 'from %s today at 4.0%% a year (assumption)' % m(P['cup_value'])),
        kpi('Property A tax: today / if lived in / if rented', '%s / %s / %s' % (m(P['cup_tax_2025']), m(B['tax_live_T']), m(B['tax_rent_T'])), 'per year; first year after inheritance'),
        kpi('Property B tax advantage kept by not selling', m(sf_gap) + ' a year', 'difference between tax on market value and on the current assessed value'),
        kpi('Federal estate-tax room for cash in %d' % T, m(B['exclusion_T'] - B['fmv_T']), 'projected exclusion %s minus Property A; per transferor' % m(B['exclusion_T'])),
        kpi('California and local inheritance tax', 'None', 'no California estate or inheritance tax return for deaths since 2005'),
    ])
    opts = ''.join('<button type="button" data-t="%s"%s>%s</button>' % (k, ' class="on"' if int(k) == T else '', k) for k in sorted(by))
    dash_rows = []
    for k in sorted(by):
        s = by[k]
        dash_rows.append('<tbody data-t="%s"%s>' % (k, '' if int(k) == T else ' hidden') + ''.join(
            '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (a, b_, c, d, f) for a, b_, c, d, f in [
                ('Property A market value at inheritance', m(s['fmv_T']), m(s['fmv_T']), m(s['fmv_T']), src('FHFA-SJ')),
                ('New assessed value', m(s['taxable_live_T']), m(s['taxable_rent_T']), 'sold', src('BOE-LTA-2026-026', 'RTC-63.2')),
                ('Property tax, first year', m(s['tax_live_T']), m(s['tax_rent_T']), m(s['sell_hold']) + ' carrying cost until sale', src('SCC-RATES', 'BOE-HOX')),
                ('Cash released at inheritance', '$0', '$0', m(s['sell_net']), src('IRS-FAQ-INHERIT', 'SCC-DTT')),
                ('After-tax wealth 10 years later', m(s['w10']['live']), m(s['w10']['rent']), m(s['w10']['sell']), src('IRS-TC409', 'IRS-TC559')),
                ('After-tax wealth in 2076', m(s['w_live']), m(s['w_rent']), m(s['w_sell']), src('IRS-TC409', 'FTB-RATES')),
                ('The same in 2026 dollars', m(s['real_live']), m(s['real_rent']), m(s['real_sell']), src('BLS-CPI')),
            ]) + '</tbody>')
    dash = ('<div class="tablewrap"><table class="num" id="dash"><caption>Dashboard: three choices for Property A, by assumed year of inheritance</caption>'
            '<thead><tr><th scope="col">Measure</th><th scope="col">Live in it</th><th scope="col">Rent it out</th><th scope="col">Sell and reinvest</th><th scope="col">Official basis</th></tr></thead>'
            + ''.join(dash_rows) + '</table></div>')
    diff = table(
        ['Question', 'Property A - Cupertino (to be inherited)', 'Property B - San Francisco (already owned)', 'Official basis'],
        [
            ['Does ownership change at the Transferor\'s death?', 'Yes. For a revocable trust the change-in-ownership date is the date of death.', 'No. The Inheritor already owns it, so nothing transfers.', src('BOE-RULE-462.260')],
            ['Property-tax reassessment', 'Yes. Full market value if rented or left empty; partial relief only if the Inheritor moves in within one year.', 'None. The assessed value stays on its current base with at most 2% a year.', src('BOE-P19', 'RTC-63.2')],
            ['Income-tax basis', 'Reset to market value at the date of death if the home is included in the Transferor\'s gross estate. A sale soon after has almost no taxable gain.', 'No reset. The Inheritor keeps the existing basis, so a sale is taxed on the whole gain since acquisition.', src('IRS-FAQ-INHERIT', 'RR-2023-2')],
            ['Counted in the Transferor\'s taxable estate', 'Yes, with the cash.', 'No.', src('IRS-ESTATE')],
            ['Value today / assessed value today', '%s / %s' % (m(P['cup_value']), m(P['cup_assessed'])), '%s / %s' % (m(P['sf_value']), m(P['sf_assessed'])), src('SCC-RATES', 'SF-TAX')],
            ['What it earns today', 'Nothing (the Transferor lives in it).', '%s a year from two rented units; the third unit is free for the Inheritor.' % m(P['sf_rent_2units']), src('SF-RENT-RULES')],
        ], caption='Why the two homes must be treated differently')
    plan = """
<ol class="plan">
<li><strong>Keep Property B and keep living in its third unit.</strong> Its assessed value is %s against a market value of %s, which saves about %s of property tax every year, and that saving is lost for good if it is sold. It also has no basis reset, so selling it would tax the whole gain. It already produces %s a year.</li>
<li><strong>Sell Property A within a few months of inheriting it and invest the proceeds in a diversified stock fund.</strong> With the basis reset to the date-of-death value the sale has no taxable gain (the model shows a small loss of %s from selling costs). About %s is released. In the baseline it grows to %s by 2076 after all taxes (%s in 2026 dollars), against %s if rented and %s if lived in.</li>
<li><strong>Do not sell and park the money in savings.</strong> If the proceeds would sit in savings or Treasury bills at about 3.5%%, keeping the house as a rental comes out ahead (%s against %s in 2026 dollars).</li>
<li><strong>Living in Property A is a lifestyle choice with a price.</strong> The assessed value jumps from %s to %s even with the Proposition 19 relief, so the tax bill rises from about %s to about %s a year. Compared with selling, living there costs about %s of 2076 wealth in 2026 dollars.</li>
<li><strong>Before anything else, have the trust read by an estate attorney.</strong> The whole result depends on the home being included in the Transferor's gross estate so that the basis resets. If it is not, selling triggers tax on decades of gain (the model shows %s less wealth in 2026 dollars). See the <a href="flagged.html">Flagged for Review</a> page.</li>
</ol>""" % (
        m(P['sf_assessed']), m(P['sf_value']), m(sf_gap), m(P['sf_rent_2units']),
        m(-B['sell_gain']), m(B['sell_net']), m(B['w_sell']), m(B['real_sell']), m(B['w_rent']), m(B['w_live']),
        m(M['sensitivity'][6]['real_rent']), m(M['sensitivity'][6]['real_sell']),
        m(B['fbyv_T']), m(B['taxable_live_T']), m(B['tax_before_T']), m(B['tax_live_T']),
        m(B['real_sell'] - B['real_live']),
        m(B['real_sell'] - M['sensitivity'][-1]['real_sell']))
    chart = bars([(NAME[k], B['real_' + k], COL[k]) for k in ('sell', 'rent', 'live')])
    links = ''.join('<a class="card" href="%s"><b>%s</b><span>%s</span></a>' % x for x in [
        ('decision.html', 'Decision', 'Live, rent or sell: numbers, sensitivities and break-even points'),
        ('projections.html', 'Year by year', 'Value, assessed value, tax, insurance, water, electricity and repairs, 2026 to 2076'),
        ('black-swan.html', 'Black swan', 'Fifty real historical sequences and named crisis paths, kept apart from the baseline'),
        ('process.html', 'Process', 'Step-by-step list with legal deadlines after the Transferor\'s death'),
        ('law.html', 'Law', 'Federal, California and local rules today, and changes under discussion'),
        ('estate-cash.html', 'Cash and estate tax', 'Thresholds, room before tax is due, and projections to 2050'),
        ('costs.html', 'Insurance and costs', 'What could and could not be confirmed for ZIP 95014 and 94122'),
        ('flagged.html', 'Flagged for Review', 'Every unconfirmed value, assumption and irregularity, with links'),
    ])
    body = """
<section class="kpis">%s</section>
<h2>Best plan and why</h2>%s
<h2>After-tax wealth in 2076, in 2026 dollars (baseline, inheritance in %d)</h2>%s
<p class="note">Wealth counts only what differs between the choices: Property A itself, every cash flow it causes, and rent from the Inheritor's vacated unit in Property B when the Inheritor moves to Property A. The two units already rented in Property B are the same in all three choices and are left out. All figures assume everything is sold and taxed at the end so that the choices can be compared like for like.</p>
<h2>Dashboard</h2>
<div class="seg" id="tsel" aria-label="Year of inheritance"><span>Year of inheritance:</span>%s</div>
%s
<h2>The two homes are not the same case</h2>%s
<h2>Sections</h2><div class="cards">%s</div>
""" % (cards, plan, T, chart, opts, dash, diff, links)
    page('index.html', 'Executive summary',
         'Property A (Cupertino, 95014) will pass to the Inheritor through a trust some time around 2040 to 2050. Property B (San Francisco, 94122) is already owned by the Inheritor. This site works out, with official sources on every table row, whether to live in Property A, rent it out, or sell it and reinvest.', body)


# ====================================================================== decision
def build_decision():
    s = B
    at = table(['Item at inheritance in %d' % T, 'Amount', 'How it is worked out', 'Official basis'], [
        ['Market value of Property A', m(s['fmv_T']), '%s today, growing 4.0%% a year (assumption %s)' % (m(P['cup_value']), flag('A01')), src('FHFA-SJ')],
        ['Assessed value just before death', m(s['fbyv_T']), '%s in 2026, growing 2%% a year' % m(P['cup_assessed']), src('BOE-P19')],
        ['Proposition 19 allowance (the adjusted $1 million)', m(s['cap_T']), '$1,044,586 until February 2027, then raised every second year by one year of California house-price change %s' % flag('A03'), src('BOE-LTA-2025-009')],
        ['Excluded amount', m(s['excluded_T']), 'assessed value plus allowance', src('BOE-LTA-2026-026')],
        ['New assessed value if the Inheritor moves in', m(s['taxable_live_T']), 'assessed value plus (market value minus excluded amount)', src('BOE-LTA-2026-026', 'SCC-P19')],
        ['New assessed value if rented, left empty or held for sale', m(s['taxable_rent_T']), 'full market value', src('BOE-P19')],
        ['Yearly property tax before / if lived in / if rented', '%s / %s / %s' % (m(s['tax_before_T']), m(s['tax_live_T']), m(s['tax_rent_T'])), 'rate 1.16360%% plus fixed charges of about %s (inflated); $7,000 exemption if owner-occupied %s' % (m(P['dc_cup']), flag('U03')), src('SCC-RATES', 'BOE-HOX')],
        ['Income-tax basis after death', m(s['fmv_T']), 'market value at the date of death, if the home is in the gross estate %s' % flag('Q01'), src('IRS-FAQ-INHERIT', 'RR-2023-2')],
        ['Net proceeds if sold', m(s['sell_net']), '5%% selling cost (assumption %s), county transfer tax $1.10 per $1,000, six months of carrying costs %s' % (flag('A06'), m(s['sell_hold'])), src('SCC-DTT')],
        ['Taxable gain on that sale', m(s['sell_gain']), 'sale price less costs, minus basis; a loss, so no tax', src('IRS-FAQ-INHERIT', 'IRS-TC409')],
    ], caption='What happens to Property A on the day it is inherited', cls='num')
    first = table(['First full year after inheritance (%d)' % T, 'Live in it', 'Rent it out', 'Sell and reinvest', 'Official basis'], [
        ['Rent collected from Property A', '$0', m(rT['rent_collected']), '$0', src('HUD-95014')],
        ['Property tax', m(-rT['live_tax']), m(-rT['rent_tax']), 'none after the sale', src('SCC-RATES', 'BOE-P19')],
        ['Insurance, repairs, water, electricity, management', m(-(rT['live_cost'] - rT['live_tax'])), m(-(rT['rent_collected'] - rT['rent_noi'] - rT['rent_tax'])), 'none after the sale', src('CDI-TOOL')],
        ['Income tax on the rent (after depreciation)', '$0', m(-rT['rent_income_tax']), '$0', src('IRS-P527', 'IRS-TC559')],
        ['Rent from the vacated unit in Property B, after tax', m(rT['live_unit3']), '$0 (the Inheritor lives there)', '$0 (the Inheritor lives there)', src('SF-RENT-RULES', 'HUD-94122')],
        ['Net cash for the year', m(rT['live_unit3'] - rT['live_cost']), m(rT['rent_after_tax']), 'investment income on %s' % m(s['sell_net']), src('IRS-TC559')],
    ], caption='Cash flow in the first year', cls='num',
        note='The rent for Property A is the HUD four-bedroom Small Area Fair Market Rent for ZIP 95014 (%s a month in fiscal year 2026) grown with inflation plus 0.5 point. The number of bedrooms was not supplied; see %s.' % (m(P['cup_rent_month']), flag('A07')))
    w = table(['After-tax wealth from Property A', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Official basis'], [
        ['%d (10 years after)' % s['w10']['year'], m(s['w10']['live']), m(s['w10']['rent']), m(s['w10']['sell']), src('IRS-TC409', 'IRS-TC701')],
        ['%d (20 years after)' % s['w20']['year'], m(s['w20']['live']), m(s['w20']['rent']), m(s['w20']['sell']), src('IRS-TC409', 'IRS-TC701')],
        ['2076', m(s['w_live']), m(s['w_rent']), m(s['w_sell']), src('IRS-TC409', 'FTB-RATES')],
        ['2076 in 2026 dollars', m(s['real_live']), m(s['real_rent']), m(s['real_sell']), src('BLS-CPI')],
        ['2076 before the final sale and its taxes', m(s['h_live']), m(s['h_rent']), m(s['h_sell']), src('IRS-TC409')],
    ], caption='Baseline result (inheritance in %d)' % T, cls='num')
    series = [(NAME[k], COL[k], {r['year']: r['w_' + k] / r['cpi'] for r in ROWS if r['year'] >= T}) for k in ('sell', 'rent', 'live')]
    chart = lines(series, T, 2076, mark=None)
    sens = table(['One assumption changed', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Best', 'Official basis'], [
        [e(x['label']), m(x['real_live']), m(x['real_rent']), m(x['real_sell']), NAME[x['best']], src(*sb)]
        for x, sb in zip(M['sensitivity'], [
            ('FHFA-SJ', 'BLS-CPI'), ('FHFA-SJ',), ('FHFA-SJ',), ('FHFA-SJ', 'FHFA-CA'), ('TREASURY',), ('TREASURY',),
            ('TREASURY',), ('TREASURY',), ('BLS-CPI', 'CBO'), ('HUD-95014',), ('HUD-95014',), ('SCC-DTT',),
            ('RP-2026-35', 'FTB-RATES'), ('RP-2026-35', 'FTB-RATES'), ('SF-RENT-RULES',), ('CDI-TOOL',), ('CDI-RES',), ('RR-2023-2',)])
    ], caption='Sensitivity: after-tax wealth in 2076, in 2026 dollars', cls='num',
        note='Stock-return assumptions have no official source; the Treasury yield is linked as the risk-free reference and the historical S&P 500 series is academic (%s).' % flag('A02'))
    be = table(['Break-even question', 'Answer', 'Compare with', 'Official basis'], [
        ['Home appreciation at which renting equals selling', pc(BE['g_cup_rent_vs_sell']) + ' a year', 'baseline 4.0%%; San Jose index %s a year 2000-2025 and %s a year 1976-2025' % (pc(HS['sj_2000_2025']), pc(HS['sj_1976_2025'])), src('FHFA-SJ')],
        ['Home appreciation at which living there equals selling', pc(BE['g_cup_live_vs_sell']) + ' a year', 'same', src('FHFA-SJ')],
        ['Stock return below which renting beats selling', pc(BE['r_stock_rent_vs_sell']) + ' a year', 'baseline 7.0%; 10-year Treasury yield 4.98% on 2026-11-10', src('TREASURY')],
        ['Monthly rent today at which renting equals selling', m(BE['rent_month_rent_vs_sell']), 'HUD four-bedroom figure %s' % m(P['cup_rent_month']), src('HUD-95014')],
    ], caption='Break-even points', cls='num')
    byT = table(['Year of inheritance', 'Market value', 'Assessed if lived in', 'Tax if lived in / rented', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Official basis'], [
        [k, m(v['fmv_T']), m(v['taxable_live_T']), '%s / %s' % (m(v['tax_live_T']), m(v['tax_rent_T'])), m(v['real_live']), m(v['real_rent']), m(v['real_sell']), src('BOE-LTA-2026-026', 'SCC-RATES')]
        for k, v in sorted(M['by_T'].items())
    ], caption='Earlier or later inheritance (wealth in 2076, in 2026 dollars)', cls='num')
    sf_net = P['sf_value'] * (1 - P['sell_cost'])
    which = table(['If one home had to be sold', 'Sell Property A after inheriting', 'Sell Property B instead', 'Official basis'], [
        ['Basis used to measure the gain', 'Market value at death (reset)', 'The Inheritor\'s own basis: ' + BLANK + ' ' + flag('Q03'), src('IRS-FAQ-INHERIT')],
        ['Tax on the sale', 'None in the baseline (small loss)', 'Up to about 37.1%% of the gain for a large one-year gain (20%% federal + 3.8%% + 13.3%% California). If the basis were as low as the assessed value, about %s.' % m((sf_net - P['sf_assessed']) * 0.371), src('IRS-TC409', 'IRS-TC559', 'FTB-RATES')],
        ['Property-tax position given up', 'Already lost at inheritance (assessed value moves to market or near it)', 'A %s assessed value on a %s home: about %s a year of tax saving, lost permanently' % (m(P['sf_assessed']), m(P['sf_value']), m(sf_gap)), src('SF-TAX', 'BOE-P19')],
        ['Income given up', 'None today', '%s a year of rent' % m(P['sf_rent_2units']), src('SF-RENT-RULES')],
        ['Home-sale exclusion', 'Not needed; the gain is already near zero', 'Up to $250,000 ($500,000 joint) only for the part used as the Inheritor\'s main home for 2 of the last 5 years', src('IRS-TC701')],
    ], caption='Which home to keep')
    why = """
<h2>Why selling wins on the numbers</h2>
<ul>
<li><strong>The tax base is lost either way.</strong> Property A is taxed on %s just before inheritance. Afterwards it is taxed on %s if rented, and still on %s if the Inheritor moves in, because the Proposition 19 allowance (%s by then) is small next to a %s home.</li>
<li><strong>The basis reset makes the sale almost tax-free once.</strong> That is worth about %s of income tax compared with a sale without the reset. It is used in full by selling; it is used slowly, through depreciation, by renting.</li>
<li><strong>The rent is small next to the value.</strong> %s of rent on a %s home is a gross yield of %s, and the reassessed property tax alone takes %s of it.</li>
<li><strong>Property B already supplies housing and a protected tax base.</strong> The Inheritor does not need Property A to live in, and Property B cannot be replaced at its tax cost.</li>
</ul>
<h2>When the answer changes</h2>
<ul>
<li>If the proceeds would be kept in savings or Treasury bills, renting comes out ahead.</li>
<li>If the home appreciates %s a year or more for decades (it did %s a year from 1976 to 2025) while stocks earn 7%%, renting catches up.</li>
<li>If the trust does not give a basis reset, every choice is worse and the gap between selling and renting narrows.</li>
<li>If the Inheritor wants to live in Property A for reasons that are not financial, the cost is shown above and the Proposition 19 claim must be filed in time (see <a href="process.html">Process</a>).</li>
</ul>""" % (
        m(s['fbyv_T']), m(s['taxable_rent_T']), m(s['taxable_live_T']), m(s['cap_T']), mm(s['fmv_T']),
        m((s['sell_proceeds'] - min(P['cup_assessed'], s['fmv_T'])) * 0.371),
        m(rT['rent_collected']), mm(s['fmv_T']), pc(rT['rent_collected'] / s['fmv_T']), pc(rT['rent_tax'] / rT['rent_collected'], 0),
        pc(BE['g_cup_rent_vs_sell']), pc(HS['sj_1976_2025']))
    body = at + first + w + '<h2>Wealth over time, in 2026 dollars</h2>' + chart + why + sens + be + byT + '<h2>Property A or Property B?</h2>' + which
    page('decision.html', 'Decision: live in it, rent it, or sell and reinvest',
         'One model, one set of assumptions, three choices for Property A. Property B stays as it is in every case because the Inheritor already owns it.', body)


# ====================================================================== projections
def build_projections():
    sA = src('SCC-RATES', 'BOE-P19')
    pre = table(['Year', 'Market value', 'Assessed value', 'Property tax', 'Home insurance', 'Water', 'Electricity (solar credit)', 'Repairs', 'Official basis'], [
        [r['year'], m(r['cup_value']), m(r['cup_assessed_pre']), m(r['cup_tax_pre']), m(r['ins_home']), m(r['cup_water']), m(r['cup_elec']), m(r['cup_maint']), sA]
        for r in ROWS if r['year'] < T
    ], caption='Property A before inheritance (owned and paid by the Transferor), 2026 to %d' % (T - 1), cls='num yr', tid='a-pre')
    post = [r for r in ROWS if r['year'] >= T]
    live = table(['Year', 'Market value', 'Assessed value', 'Property tax', 'Home insurance', 'Water', 'Electricity (solar credit)', 'Repairs', 'Total yearly cost', 'Official basis'], [
        [r['year'], m(r['cup_value']), m(r['live_assessed']), m(r['live_tax']), m(r['ins_home']), m(r['cup_water']), m(r['cup_elec']), m(r['cup_maint']), m(r['live_cost']), src('SCC-RATES', 'BOE-LTA-2026-026')]
        for r in post
    ], caption='Property A if the Inheritor lives in it, %d to 2076' % T, cls='num yr', tid='a-live')
    rent = table(['Year', 'Market value', 'Assessed value', 'Property tax', 'Rental (landlord) insurance', 'Repairs', 'Rent collected', 'Net before income tax', 'Net after income tax', 'Official basis'], [
        [r['year'], m(r['cup_value']), m(r['rent_assessed']), m(r['rent_tax']), m(r['ins_rental']), m(r['cup_maint']), m(r['rent_collected']), m(r['rent_noi']), m(r['rent_after_tax']), src('SCC-RATES', 'HUD-95014')]
        for r in post
    ], caption='Property A if rented out, %d to 2076 (tenant pays water and electricity)' % T, cls='num yr', tid='a-rent')
    sfb = table(['Year', 'Market value', 'Assessed value', 'Property tax', 'Rental (landlord) insurance', 'Water (3 units)', 'Electricity', 'Repairs', 'Rent, two units', 'Net before income tax', 'Official basis'], [
        [r['year'], m(r['sf_value']), m(r['sf_assessed']), m(r['sf_tax']), m(r['sf_ins']), m(r['sf_water']), m(r['sf_elec']), m(r['sf_maint']), m(r['sf_rent']), m(r['sf_net']), src('SF-TAX', 'SF-RENT-RULES')]
        for r in ROWS
    ], caption='Property B (already owned; no change at the Transferor\'s death), 2026 to 2076', cls='num yr', tid='b-all')
    chart = lines([
        ('Property A tax if rented (full reassessment)', COL['rent'], {r['year']: (r['cup_tax_pre'] if r['year'] < T else r['rent_tax']) for r in ROWS}),
        ('Property A tax if lived in (Proposition 19)', COL['live'], {r['year']: (r['cup_tax_pre'] if r['year'] < T else r['live_tax']) for r in ROWS}),
        ('Property B tax (no reassessment)', COL['sell'], {r['year']: r['sf_tax'] for r in ROWS}),
    ], 2026, 2076, yfmt=lambda v: '$%.0fk' % (v / 1e3), mark=T)
    chart2 = lines([
        ('Property A market value', COL['rent'], {r['year']: r['cup_value'] for r in ROWS}),
        ('Property B market value', COL['sell'], {r['year']: r['sf_value'] for r in ROWS}),
        ('Property A assessed value if lived in', COL['live'], {r['year']: (r['cup_assessed_pre'] if r['year'] < T else r['live_assessed']) for r in ROWS}),
        ('Property B assessed value', COL['before'], {r['year']: r['sf_assessed'] for r in ROWS}),
    ], 2026, 2076, mark=T)
    assum = table(['Line', 'Starting figure (2026)', 'Growth each year', 'Kind', 'Official basis'], [
        ['Property A market value', m(P['cup_value']), '4.0%', 'owner figure; growth is an assumption ' + flag('A01'), src('FHFA-SJ')],
        ['Property B market value', m(P['sf_value']), '4.0%', 'owner figure; growth is an assumption ' + flag('A01'), src('FHFA-SF')],
        ['Assessed values', '%s (A), %s (B)' % (m(P['cup_assessed']), m(P['sf_assessed'])), 'inflation, capped at 2%; never above market value', 'owner figures; rule is official', src('BOE-P19')],
        ['Property-tax rate', '1.16360% (A), 1.18162182% (B)', 'held constant', 'official rates; fixed charges %s (A) and %s (B) derived from the bills %s' % (m(P['dc_cup']), m(P['dc_sf']), flag('U03')), src('SCC-RATES', 'SF-TAX')],
        ['Home and landlord insurance', m(P['ins_home']) + ' each', 'inflation + 1 point', 'owner estimate, not confirmed ' + flag('U01'), src('CDI-TOOL')],
        ['Water', '%s (A), %s (B, three units)' % (m(P['cup_water']), m(P['sf_water'])), 'inflation + 2 points; Property B +9% in 2027 and 2028', 'owner figures; growth is an assumption ' + flag('A09'), src('SFPUC')],
        ['Electricity', '%s (A, solar credit), %s (B)' % (m(P['cup_elec']), m(P['sf_elec'])), 'inflation + 1 point', 'owner figures ' + flag('U05'), src('CPUC-NEM', 'CPUC-FIXED')],
        ['Repairs and maintenance', '%s (A), %s (B)' % (m(P['maint_cup']), m(P['maint_sf'])), 'inflation', 'assumption; the owner said only that A costs less than B ' + flag('A08'), src('BLS-CPI')],
        ['Property B rent, two units', m(P['sf_rent_2units']), 'half the rent-controlled rate (60% of inflation), half market rate', 'owner figure; growth rule is an assumption ' + flag('A10'), src('SF-RENT-RULES', 'SF-RENT-2026')],
        ['Property A market rent', m(P['cup_rent_month'] * 12), 'inflation + 0.5 point', 'HUD four-bedroom figure used as a stand-in ' + flag('A07'), src('HUD-95014')],
        ['Inflation', '2.5%', 'constant in the baseline', 'assumption; the CPI rose %s a year 2000-2025 %s' % (pc(HS['cpi_2000_2025']), flag('A01')), src('BLS-CPI', 'CBO')],
    ], caption='What drives each line')
    tabs = '<div class="seg" id="ysel"><span>Show:</span><button type="button" data-y="a-pre" class="on">A before inheritance</button><button type="button" data-y="a-live">A lived in</button><button type="button" data-y="a-rent">A rented</button><button type="button" data-y="b-all">B</button><button type="button" data-y="all">All tables</button></div>'
    body = ('<h2>Property tax by year</h2>' + chart + '<h2>Market and assessed values</h2>' + chart2 + assum
            + '<h2>Year-by-year tables</h2><p class="note">Baseline path with inheritance in %d. Amounts are nominal dollars of each year, rounded to $10. A negative electricity figure is a credit. If Property A is sold, its costs stop in %d; the sale figures are on the <a href="decision.html">Decision</a> page.</p>' % (T, T)
            + tabs + pre + live + rent + sfb)
    page('projections.html', 'Year-by-year projections, 2026 to 2076',
         'House value, assessed value, property tax, insurance, water, electricity and repairs for both homes, with rental insurance and rent where the home is let.', body)


# ====================================================================== black swan
def build_blackswan():
    hist = table(['Year', 'Inflation (CPI, Dec to Dec)', 'San Jose area home prices', 'San Francisco area home prices', 'S&P 500 total return', '3-month Treasury bill', 'Official basis'], [
        [h['year'], pc(h['infl']), pc(h['g_cup']), pc(h['g_sf']), pc(h['r_stock']), pc(h['r_bill']), src('BLS-CPI', 'FHFA-SJ', 'FHFA-SF') + ' · ' + src('DAMODARAN')]
        for h in M['hist']
    ], caption='The real record that is replayed: 1976 to 2025', cls='num yr', tid='hist',
        note='Home-price changes are fourth quarter to fourth quarter of the FHFA all-transactions index. The San Jose series starts at the end of 1976, so its 1976 change uses the California index. Stock and bill returns come from an academic table, not a government source (%s).' % flag('S02'))
    stats = table(['Measure, 1976 to 2025', 'Value', 'Baseline assumption', 'Official basis'], [
        ['Inflation, average per year', pc(HS['cpi_1976_2025'], 2), '2.5%', src('BLS-CPI')],
        ['Highest inflation in one year', '%s in %d' % (pc(HS['max_infl'][0]), HS['max_infl'][1]), 'constant', src('BLS-CPI')],
        ['San Jose area home prices, average per year', pc(HS['sj_1976_2025'], 2), '4.0%', src('FHFA-SJ')],
        ['San Jose area, worst and best single year', '%s in %d; %s in %d' % (pc(HS['worst_sj'][0]), HS['worst_sj'][1], pc(HS['best_sj'][0]), HS['best_sj'][1]), 'constant', src('FHFA-SJ')],
        ['San Francisco area home prices, average per year', pc(HS['sf_1976_2025'], 2), '4.0%', src('FHFA-SF')],
        ['S&P 500 total return, average per year', pc(HS['sp_1976_2025'], 2), '7.0%', src('TREASURY') + ' · ' + src('DAMODARAN')],
        ['S&P 500, worst single year', '%s in %d' % (pc(HS['worst_sp'][0]), HS['worst_sp'][1]), 'constant', src('TREASURY') + ' · ' + src('DAMODARAN')],
        ['3-month Treasury bill, average per year', pc(HS['bill_1976_2025'], 2), '3.5%', src('TREASURY') + ' · ' + src('DAMODARAN')],
    ], caption='How uneven the real record was', cls='num')
    med = lambda k: rep_sorted(k)[25]
    rep = table(['Across all 50 real starting years', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Official basis'], [
        ['Times it was the best choice', wins.get('live', 0), wins.get('rent', 0), wins.get('sell', 0), src('FHFA-SJ', 'BLS-CPI')],
        ['Worst result (2026 dollars)', m(rep_sorted('live')[0]), m(rep_sorted('rent')[0]), m(rep_sorted('sell')[0]), src('FHFA-SJ', 'BLS-CPI')],
        ['Middle result (2026 dollars)', m(med('live')), m(med('rent')), m(med('sell')), src('FHFA-SJ', 'BLS-CPI')],
        ['Best result (2026 dollars)', m(rep_sorted('live')[-1]), m(rep_sorted('rent')[-1]), m(rep_sorted('sell')[-1]), src('FHFA-SJ', 'BLS-CPI')],
        ['Baseline (constant rates) for comparison', m(B['real_live']), m(B['real_rent']), m(B['real_sell']), src('FHFA-SJ', 'BLS-CPI')],
    ], caption='Replay of the real 1976-2025 sequence from every possible starting year (wrapped around to fill 2027-2076)', cls='num',
        note='Each replay keeps the real year-to-year order, so inflation, home prices and stocks move together as they actually did. The spread is very wide because the order of good and bad years matters: a boom just after the sale helps the seller, a crash just after hurts.')
    named = table(['Path', 'Market value at inheritance', 'Tax if lived in / rented, first year', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Best', 'Official basis'], [
        [e(x['label']), m(x['summary']['fmv_T']), '%s / %s' % (m(x['summary']['tax_live_T']), m(x['summary']['tax_rent_T'])),
         m(x['summary']['real_live']), m(x['summary']['real_rent']), m(x['summary']['real_sell']), NAME[x['summary']['best']],
         src('FHFA-SJ', 'BLS-CPI') + ' · ' + src('DAMODARAN')]
        for x in M['paths']
    ] + [['Baseline (constant rates)', m(B['fmv_T']), '%s / %s' % (m(B['tax_live_T']), m(B['tax_rent_T'])), m(B['real_live']), m(B['real_rent']), m(B['real_sell']), NAME[B['best']], src('FHFA-SJ', 'BLS-CPI')]],
        caption='Named paths (wealth in 2076, in 2026 dollars; inheritance in %d)' % T, cls='num',
        note='The Depression path uses national home-price data because no local index goes back that far (%s).' % flag('S02'))
    PATHS = {x['key']: x for x in M['paths']}
    ch = lines([
        ('Baseline', COL['before'], {r['year']: r['cup_value'] / r['cpi'] for r in ROWS}),
        ('Real 1976-2025 order', COL['rent'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['replay_1976']['rows']}),
        ('Real order from 2000', COL['sell'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['replay_2000']['rows']}),
        ('2007-2012 bust at inheritance', COL['live'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['crash_at_T']['rows']}),
        ('Depression at inheritance', COL['x'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['depression_at_T']['rows']}),
    ], 2026, 2076, mark=T)
    cr = PATHS['crash_at_T']
    yr = table(['Year', 'Inflation', 'Home prices', 'Stocks', 'Market value', 'Assessed if lived in', 'Tax if lived in', 'Tax if rented', 'Wealth: live', 'Wealth: rent', 'Wealth: sell', 'Official basis'], [
        [r['year'], pc(ec['infl']), pc(ec['g_cup']), pc(ec['r_stock']), m(r['cup_value']), m(r['live_assessed']), m(r['live_tax']), m(r['rent_tax']), m(r['w_live']), m(r['w_rent']), m(r['w_sell']), src('BOE-P19', 'FHFA-SJ')]
        for r, ec in zip(cr['rows'][T - Y0:T - Y0 + 16], cr['econ'][T - Y0 - 1:T - Y0 + 15])
    ], caption='Year by year through one crisis: the real 2007-2012 bust arriving in the year of inheritance', cls='num yr',
        note='When the market value falls below the assessed value the assessment is lowered to market value for that year, and it climbs back as prices recover. Wealth is after tax, nominal dollars.')
    rp = PATHS['replay_1976']
    yr2 = table(['Year', 'Real year replayed', 'Inflation', 'Home prices', 'Stocks', 'Property A value', 'Property A tax (before / lived in)', 'Property B value', 'Property B tax', 'Official basis'], [
        [r['year'], 1976 + i, pc(ec['infl']), pc(ec['g_cup']), pc(ec['r_stock']), m(r['cup_value']),
         m(r['cup_tax_pre'] if r['year'] < T else r['live_tax']), m(r['sf_value']), m(r['sf_tax']), src('FHFA-SJ', 'FHFA-SF', 'BLS-CPI')]
        for i, (r, ec) in enumerate(zip(rp['rows'][1:], rp['econ']))
    ], caption='Fifty-year projection under the real 1976-2025 sequence, in its real order', cls='num yr', tid='replay')
    other = table(['Event that is not an economic cycle', 'What is known', 'Effect on each choice', 'Official basis'], [
        ['Large Bay Area earthquake', '72% chance of at least one magnitude 6.7 or larger quake in the region between 2014 and 2043. Homeowners policies do not cover earthquake damage; the insurer must offer separate cover every other year.', 'Live and Rent carry the uninsured loss on Property A; Sell does not. Property B carries it in every case. Premium for earthquake cover: ' + BLANK + ' ' + flag('U02'), src('USGS', 'CDI-EQ')],
        ['Home left empty during administration', 'Losses to a house vacant for 60 days or more are generally not covered by a homeowners policy.', 'Matters most for Sell (the home may sit empty until closing) and for the months before a tenant or the Inheritor moves in. Ask the insurer for a vacancy endorsement.', src('CDI-RES')],
        ['Federal estate-tax exclusion cut by a later Congress', 'The exclusion is $15,000,000 for 2026 and $15,480,000 for 2027 and is indexed. Any reduction would need new legislation; none is enacted.', 'Affects the cash and Property A equally in all three choices; see the stress rows on the <a href="estate-cash.html">Cash and estate tax</a> page.', src('IRS-NEW', 'RP-2026-35')],
        ['Loss of the basis reset at death', 'Current law resets basis to market value at death for property in the gross estate. No enacted change was found.', 'Sell would owe tax on the full historic gain; the model shows %s less wealth in 2026 dollars.' % m(B['real_sell'] - M['sensitivity'][-1]['real_sell']), src('IRS-FAQ-INHERIT', 'RR-2023-2')],
        ['Change to Proposition 19', 'A voter measure would be needed. None of the fourteen state measures on the November 2026 ballot changes it.', 'A return to the old rule would mainly help Rent (no reassessment); the first-year tax would drop from %s to about %s.' % (m(B['tax_rent_T']), m(B['tax_before_T'])), src('SOS-RESULTS', 'BOE-P19')],
        ['Stricter rent rules', 'Statewide cap of 5% plus inflation (10% maximum) with an exemption for many single-family homes; San Francisco allows 60% of inflation on controlled units.', 'Lowers the Rent result for Property A if the exemption is lost, and limits Property B rent growth in every case.', src('DOJ-TPA', 'SF-RENT-RULES')],
    ], caption='Shocks that no price history captures')
    body = ("""<p class="callout">This section is kept apart from the baseline on purpose. The baseline uses constant rates so that the three choices can be compared cleanly. Here nothing is constant: every path uses real recorded years, in their real order, for inflation, local home prices, stocks, bonds and bills.</p>"""
            + rep + named + '<h2>Property A market value in 2026 dollars under five paths</h2>' + ch + stats + other + yr + yr2 + hist)
    page('black-swan.html', 'Black swan section: non-constant growth and inflation over 50 years',
         'What happens to the decision when inflation, home prices and markets behave the way they really have: in bursts, busts and long flat stretches.', body)


# ====================================================================== process
def build_process():
    steps = table(['Step', 'When', 'What to do', 'Why it matters here', 'Official basis'], [
        ['1', 'Now, while the Transferor is alive', 'Have an estate attorney confirm what kind of trust holds Property A and whether the home will be included in the Transferor\'s gross estate.', 'The basis reset, and with it the whole case for selling, depends on it. Assets of an irrevocable grantor trust outside the estate get no reset. ' + flag('Q01'), src('RR-2023-2', 'IRS-FAQ-INHERIT')],
        ['2', 'Now', 'Keep Property A as the Transferor\'s principal residence with the homeowners\' exemption on file.', 'The parent-child exclusion applies only to a home that was the Transferor\'s principal residence.', src('BOE-P19', 'BOE-HOX')],
        ['3', 'Now', 'Total the expected estate: Property A, cash and everything else the Transferor owns. Property B is not part of it.', 'Shows how much room is left under the federal exclusion; see <a href="estate-cash.html">Cash and estate tax</a>. ' + flag('Q02'), src('IRS-ESTATE')],
        ['4', 'Date of death', 'Record the date. Order a written appraisal of Property A as of that date.', 'For a revocable trust this is the change-in-ownership date, and the appraisal sets the new basis.', src('BOE-RULE-462.260', 'IRS-FAQ-INHERIT')],
        ['5', 'Within 60 days', 'The successor trustee serves the notification to every beneficiary and heir.', 'Required when a revocable trust becomes irrevocable by death; starts the 120-day contest period.', src('PROB-16061.7')],
        ['6', 'Soon after death', 'Get an employer identification number for the trust or estate; file Form 1041 if it has more than $600 of gross income in a year.', 'Rent, interest or dividends received before distribution are taxed to the trust or passed through.', src('IRS-1041')],
        ['7', 'Within 150 days of death', 'File the change-in-ownership statement for Property A with the Santa Clara County Assessor.', 'Statutory deadline when ownership changes by death; a penalty applies after a written request is ignored.', src('RTC-480')],
        ['8', 'Within 9 months of death', 'File Form 706 if the gross estate plus adjusted taxable gifts is above the filing threshold, or to elect portability for a surviving spouse. Form 4768 gives six more months.', 'Above the threshold the tax is 40% of the excess. Portability is lost without a timely return.', src('IRS-FAQ-ESTATE', 'IRS-I706')],
        ['9', 'Decide early: live, rent or sell', 'Use the <a href="decision.html">Decision</a> page. If selling, list promptly and keep the home insured while empty.', 'A sale near the date-of-death value has almost no taxable gain. Vacant homes can lose cover after 60 days.', src('IRS-FAQ-INHERIT', 'CDI-RES')],
        ['10', 'Within 1 year, only if moving in', 'Make Property A the Inheritor\'s principal residence and file for the homeowners\' exemption there.', 'Without both, the Proposition 19 exclusion is not available and the home is reassessed at full market value.', src('RTC-63.2', 'BOE-LTA-2026-026')],
        ['11', 'Within 3 years, only if moving in', 'File the parent-child exclusion claim (form BOE-19-P) with the Assessor, before any transfer to a third party.', 'Later claims give relief only going forward.', src('BOE-P19', 'SCC-P19')],
        ['12', 'After the Assessor acts', 'Expect a supplemental tax bill for Property A covering the period from the date of death.', 'Budget for it in every choice. The San Francisco page describes the same California process. ' + flag('U06'), src('SF-TAX')],
        ['13', 'Tax year of the sale, if sold', 'Report the sale on Form 8949 and Schedule D using the date-of-death value as basis; match any Schedule A to Form 8971 received.', 'A basis above the value finally determined for estate tax can draw an accuracy penalty.', src('IRS-FAQ-INHERIT', 'IRS-TC409')],
        ['14', 'Every year, if rented', 'Report rent and expenses; depreciate the building part of the new basis over 27.5 years. Follow the state rent cap and its notice rules.', 'Depreciation shelters part of the rent but is taxed back at up to 25% federal on a later sale.', src('IRS-P527', 'IRS-TC409', 'DOJ-TPA')],
        ['15', 'When the cash arrives', 'Nothing to report as income for the inheritance itself. Income earned on it afterwards is taxable. Inherited retirement accounts follow different rules.', 'The cash is taxed, if at all, to the estate before it is paid out, not to the Inheritor.', src('IRS-P559')],
        ['16', 'Throughout', 'Leave Property B exactly as it is: same owner, same exemption or rental status.', 'Any transfer of Property B could trigger its own reassessment; nothing about the inheritance requires one.', src('BOE-P19', 'SF-TAX')],
    ], caption='Steps and deadlines for Property A')
    body = steps + '<p class="note">Deadlines are quoted from the linked statutes and agency pages as read on %s. Forms and county procedures change; confirm each one with the county office and the attorney handling the trust.</p>' % BUILD_DATE
    page('process.html', 'Step-by-step process for the inherited home',
         'What has to be done, by whom and by when, from today through the first tax return after the inheritance.', body)


# ====================================================================== law
def build_law():
    fed = table(['Federal rule', 'Current figure', 'Effect on this case', 'Official basis'], [
        ['Estate-tax basic exclusion (per person)', '$15,000,000 for deaths in 2026; $15,480,000 for 2027; indexed after that', 'Property A plus the cash is taxed only above this amount.', src('IRS-ESTATE', 'RP-2026-35')],
        ['Top estate-tax rate', '40% on the amount above the exclusion', 'Each $1,000,000 over the line costs $400,000.', src('IRS-I706')],
        ['Portability of a spouse\'s unused exclusion', 'Available only if a timely Form 706 was filed for the first spouse to die', 'Could double the room. Whether it applies: ' + BLANK + ' ' + flag('Q02'), src('IRS-FAQ-ESTATE')],
        ['Annual gift exclusion', '$20,000 per recipient for 2027', 'Gifts within it do not use the lifetime exclusion.', src('RP-2026-35')],
        ['Basis of inherited property', 'Market value at the date of death', 'Makes a prompt sale of Property A nearly free of income tax. Does not apply to Property B.', src('IRS-FAQ-INHERIT')],
        ['Trust assets outside the gross estate', 'No basis adjustment for an irrevocable grantor trust not included in the estate', 'The single largest legal risk to the plan. ' + flag('Q01'), src('RR-2023-2')],
        ['Long-term capital-gain rates', '0%, 15% or 20%; 15% applies up to $563,200 of taxable income (single) for 2027', 'Applies to later growth after the reset and to all of the gain on Property B.', src('IRS-TC409', 'RP-2026-35')],
        ['Net investment income tax', '3.8% above $200,000 (single) or $250,000 (joint) of modified AGI', 'Adds to the tax on rent, dividends and gains.', src('IRS-TC559')],
        ['Home-sale exclusion', '$250,000 ($500,000 joint) after owning and living in the home 2 of the last 5 years', 'Only helps if the Inheritor moves into Property A and it rises after the date of death.', src('IRS-TC701')],
        ['Depreciation of a rental home', 'Straight line over 27.5 years; taxed back at up to 25% on sale', 'Shelters part of the rent if Property A is let.', src('IRS-P527', 'IRS-TC409')],
        ['Inheritance as income', 'Not included in the recipient\'s income', 'The cash itself is not taxed to the Inheritor.', src('IRS-P559')],
        ['Income-tax brackets for 2027 (single)', '24% from $109,125 to $208,325; 37% above $661,375', 'The model uses 24% for yearly income and the top gain rate for one-off sales. ' + flag('A05'), src('RP-2026-35')],
    ], caption='Federal law in force')
    ca = table(['California rule', 'Current figure', 'Effect on this case', 'Official basis'], [
        ['Estate and inheritance tax', 'None for deaths on or after 2005-01-01', 'No state tax on Property A or the cash at death.', src('SCO-ESTATE')],
        ['Parent-child exclusion (Proposition 19)', 'Only for the Transferor\'s principal residence that becomes the child\'s principal residence within one year', 'Renting or holding Property A means full reassessment.', src('BOE-P19', 'RTC-63.2')],
        ['Value limit', 'Assessed value plus $1,044,586 for transfers from 2025-02-16 to 2027-02-15', 'Above the limit the excess is added to the assessed value.', src('BOE-LTA-2025-009')],
        ['How the limit grows', 'Every second February 16, by the California house-price change of the prior calendar year only', 'It grows about half as fast as home prices, so the relief shrinks over time. ' + flag('A03'), src('BOE-LTA-2025-009')],
        ['Continual-use rule', 'If the child stops using the home as a principal residence the full new base year value is enrolled', 'Moving out later ends the relief.', src('BOE-LTA-2026-026', 'RTC-63.2')],
        ['Homeowners\' exemption', '$7,000 off the assessed value of a principal residence', 'About $80 a year; needed to qualify for the exclusion.', src('BOE-HOX')],
        ['Date of change in ownership for a revocable trust', 'The date the trust becomes irrevocable (the date of death)', 'Starts every property-tax deadline.', src('BOE-RULE-462.260')],
        ['Change-in-ownership statement at death', 'Within 150 days of the date of death', 'Missed filings lead to a penalty.', src('RTC-480')],
        ['Trustee notification', 'Within 60 days; 120-day contest period', 'A duty of the successor trustee.', src('PROB-16061.7')],
        ['State income tax on gains', 'Taxed as ordinary income: 9.3% above $72,724, up to 12.3% above $742,953 (single, 2025), plus 1% above $1,000,000', 'Applies to any gain on Property B and to later gains on Property A or on investments.', src('FTB-RATES', 'FTB-MHS')],
        ['Statewide rent cap', '5% plus inflation, at most 10% in 12 months; many single-family homes exempt', 'Applies to Property A if rented without the exemption.', src('DOJ-TPA')],
        ['Net metering for the solar system', 'Existing customers keep their tariff for 20 years from interconnection', 'The electricity credit at Property A is not permanent. Interconnection date: ' + BLANK + ' ' + flag('U05'), src('CPUC-NEM')],
    ], caption='California law in force')
    loc = table(['Local rule', 'Current figure', 'Effect on this case', 'Official basis'], [
        ['Local inheritance or estate tax', 'None exists at county or city level; the local effects are reassessment and transfer tax', 'Nothing to file locally for the cash.', src('SCO-ESTATE')],
        ['Santa Clara County property-tax rate (Cupertino components)', '1.16360% for fiscal year 2025-26', 'Applied to the new assessed value of Property A. Exact tax rate area not looked up ' + flag('U03'), src('SCC-RATES')],
        ['Santa Clara County documentary transfer tax', '$0.55 per $500 ($1.10 per $1,000); no added city tax in Cupertino', 'About %s on a sale at the %d value.' % (m(B['fmv_T'] * P['doc_transfer_tax']), T), src('SCC-DTT')],
        ['Santa Clara County Proposition 19 claim', 'Form BOE-19-P; special rules for multi-unit dwellings', 'Filed with the Assessor if the Inheritor moves in.', src('SCC-P19')],
        ['San Francisco secured property-tax rate', '1.18162182% for fiscal year 2026-27', 'Applied to Property B\'s unchanged assessed value.', src('SF-TAX')],
        ['San Francisco rent control', 'Annual increase 1.6% from 2026-03-01 to 2027-02-28 (60% of Bay Area inflation); first rent on an empty unit is not limited', 'Limits rent growth on the two let units; the vacated third unit can be let at market rent. Whether the building is covered: ' + BLANK + ' ' + flag('Q04'), src('SF-RENT-2026', 'SF-RENT-RULES', 'SF-RENT-LAW')],
        ['San Francisco Empty Homes Tax', 'Not collected: held preempted by the Court of Appeal on 2026-09-11', 'No tax today on the unit kept empty in Property B.', src('SF-EHT')],
        ['San Francisco water and sewer rates', 'Water +7.0% and residential sewer about +10% in each of fiscal years 2026-27 and 2027-28', 'Raises the largest utility bill at Property B.', src('SFPUC')],
    ], caption='Local rules in force')
    pend = table(['Change', 'Level', 'Status on %s' % BUILD_DATE, 'Effect if it happens', 'Official basis'], [
        ['Indexing of the estate exclusion', 'Federal', 'In force. 2027 figure published 2026-11-05.', 'The exclusion rises each year with inflation; the model projects %s by %d.' % (m(B['exclusion_T']), T), src('RP-2026-35', 'IRS-NEW')],
        ['Death Tax Repeal Act (S.587 and H.R.1301)', 'Federal', 'Introduced 2025-02-13 and referred to committee. No later action shown.', 'Would repeal the estate tax. No effect on the property-tax or income-tax results.', src('CONG-S587', 'CONG-HR1301')],
        ['Any reduction of the exclusion or of the basis reset', 'Federal', 'No enacted measure found. Would need a new Act of Congress.', 'See the stress rows on the Cash and Black swan pages.', src('IRS-NEW')],
        ['Next adjustment of the Proposition 19 allowance', 'California', 'Scheduled for 2027-02-16, using the 2026 California house-price change. Figure: ' + BLANK + ' ' + flag('U04'), 'Sets the allowance for transfers through 2029-02-15.', src('BOE-LTA-2025-009')],
        ['Proposition 3 (extends the existing tax on high incomes)', 'California', 'Yes 60.6% in unofficial returns; certification due by 2026-12-11.', 'Keeps the top state rates that apply to a large one-year gain.', src('SOS-RESULTS')],
        ['Proposition 40 (one-time tax on certain taxpayers)', 'California', 'No 52.6% in unofficial returns.', 'None if the result holds.', src('SOS-RESULTS')],
        ['Proposition 42 (bars new state personal-property taxes and certain retroactive taxes)', 'California', 'Yes 51.5% in unofficial returns.', 'Lowers the chance of a new state tax on invested sale proceeds.', src('SOS-RESULTS')],
        ['Measure to undo the Proposition 19 inheritance rules', 'California', 'Reported by non-official websites as a signature drive. Not among the measures on the November 2026 ballot. ' + flag('S04'), 'Would restore relief for rented inherited homes.', src('SOS-RESULTS')],
        ['Limit on banked and capital-improvement rent increases (File No. 261020)', 'San Francisco', 'Under consideration by the Board of Supervisors; not enacted.', 'Would cap those increases at 10% a year on Property B.', src('SF-RENT-RULES')],
        ['Empty Homes Tax appeal', 'San Francisco', 'City lost on appeal; no collection unless reversed.', 'If revived, a charge on the unit kept empty.', src('SF-EHT')],
        ['Residential fixed charge on electricity bills', 'California', 'Adopted: $24.15 a month for standard customers.', 'Reduces or removes the monthly solar credit at Property A.', src('CPUC-FIXED')],
        ['Missing October 2025 inflation data', 'Federal', 'No 12-month change published for October 2026.', 'Indexed figures still use the published series; watch for revisions.', src('BLS-OCT')],
    ], caption='Changes under discussion or recently decided')
    body = fed + ca + loc + '<h2>Changes under discussion</h2>' + pend
    page('law.html', 'Property and tax law: current rules and changes under discussion',
         'Federal, California and local rules that decide the outcome, each read on the official page, followed by pending or recent changes and what they would do.', body)


# ====================================================================== estate / cash
def build_estate():
    lv = table(['Level', 'Tax on an inheritance or estate', 'Tax-free amount', 'Rate above it', 'Official basis'], [
        ['City (Cupertino, San Francisco)', 'None', 'not applicable', 'not applicable', src('SCO-ESTATE')],
        ['County (Santa Clara, San Francisco)', 'None; counties reassess real property and charge transfer tax on sales', 'not applicable', 'not applicable', src('SCO-ESTATE', 'SCC-DTT')],
        ['California', 'None for deaths on or after 2005-01-01', 'not applicable', 'not applicable', src('SCO-ESTATE')],
        ['Federal, death in 2026', 'Estate tax, paid by the estate', '$15,000,000 per person', '40%', src('IRS-ESTATE', 'IRS-I706')],
        ['Federal, death in 2027', 'Estate tax, paid by the estate', '$15,480,000 per person', '40%', src('RP-2026-35', 'IRS-I706')],
        ['Federal income tax on the Inheritor', 'None on the inheritance itself; later income is taxable', 'not applicable', 'ordinary rates on later income', src('IRS-P559')],
    ], caption='Is there a tax, and above what amount?')
    hist = table(['Year of death', 'Federal filing threshold', 'Official basis'], [
        [y, v, src('IRS-ESTATE')] for y, v in [(2011, '$5,000,000'), (2017, '$5,490,000'), (2018, '$11,180,000'), (2021, '$11,700,000'), (2022, '$12,060,000'), (2023, '$12,920,000'), (2024, '$13,610,000'), (2025, '$13,990,000'), (2026, '$15,000,000')]
    ] + [[2027, '$15,480,000', src('RP-2026-35')]], caption='How the federal threshold has moved', cls='num')
    E = M['estate']
    proj = table(['Year of death', 'Projected exclusion', 'Property A value', 'Room left for cash and other assets', 'The same in 2026 dollars', 'Room if a spouse\'s unused exclusion was ported', 'Official basis'], [
        [x['T'], m(x['exclusion']), m(x['house']), m(x['headroom']), m(x['headroom'] / x['cpi']), m(2 * x['exclusion'] - x['house']), src('RP-2026-35', 'IRS-FAQ-ESTATE')]
        for x in E if x['cash_today'] == 2_000_000
    ], caption='Room under the federal exclusion (baseline: exclusion indexed at 2.5%, home at 4.0%)', cls='num',
        note='The home is assumed to grow faster than the exclusion, so the room for cash shrinks in today\'s dollars the later the inheritance happens. The amount of cash was not supplied (%s).' % flag('Q02'))
    cash = table(['Cash and other assets, in 2026 dollars', 'Year of death', 'Estate (cash + Property A)', 'Exclusion', 'Federal estate tax, one exclusion', 'Federal estate tax, two exclusions', 'Official basis'], [
        [m(x['cash_today']), x['T'], m(x['cash_then'] + x['house']), m(x['exclusion']), m(x['tax']), m(x['tax_two']), src('IRS-I706', 'RP-2026-35')]
        for x in E if x['T'] in (2040, 2050) or x['cash_today'] in (10_000_000, 20_000_000)
    ], caption='What different amounts of cash would cost', cls='num',
        note='Cash is assumed to keep pace with inflation until the year of death. Tax is 40% of the estate above the exclusion; deductions, debts and prior taxable gifts are ignored.')
    x45 = [x for x in E if x['T'] == T and x['cash_today'] == 10_000_000][0]
    stress = table(['If a later law changed the exclusion', 'Exclusion in %d' % T, 'Estate tax with %s of cash (2026 dollars)' % m(10_000_000), 'Official basis'], [
        ['Current law, indexed', m(x45['exclusion']), m(x45['tax']), src('RP-2026-35')],
        ['Hypothetical: cut to one half', m(x45['exclusion'] / 2), m(max(0, x45['house'] + x45['cash_then'] - x45['exclusion'] / 2) * 0.4), src('IRS-ESTATE')],
        ['Hypothetical: cut to one quarter (near the indexed pre-2018 level)', m(x45['exclusion'] / 4), m(max(0, x45['house'] + x45['cash_then'] - x45['exclusion'] / 4) * 0.4), src('IRS-ESTATE')],
        ['Hypothetical: estate tax repealed', 'no limit', '$0', src('CONG-S587')],
    ], caption='Stress test: a different exclusion', cls='num',
        note='The cut scenarios are illustrations only. No bill to reduce the exclusion was found; the threshold was $5,490,000 as recently as 2017.')
    pts = """
<h2>What this means for the cash</h2>
<ul>
<li>There is no city, county or California tax on the inheritance. The only threshold that matters is the federal one, and it is measured on the Transferor's whole estate: Property A, the cash and everything else. Property B is not counted.</li>
<li>With inheritance in %d the baseline leaves about %s of room for cash and other assets (%s in 2026 dollars). Above that, each extra dollar is taxed at 40%%.</li>
<li>If the Transferor is a surviving spouse and a timely Form 706 elected portability when the first spouse died, the room is roughly doubled. This needs to be checked now, because a missed election can sometimes still be made within five years of the first death.</li>
<li>Selling, renting or living in Property A does not change the estate tax. It is fixed at the date of death.</li>
<li>The Inheritor does not report the cash as income. Interest, dividends and gains earned on it afterwards are taxable, and inherited retirement accounts are taxed as they are withdrawn.</li>
</ul>""" % (T, m(B['exclusion_T'] - B['fmv_T']), m((B['exclusion_T'] - B['fmv_T']) / B['cpi_T']))
    body = lv + pts + proj + cash + stress + hist
    page('estate-cash.html', 'Cash inheritance and the tax-free threshold',
         'Exemption amounts at local, state and federal level, how much room is left before tax is due, and how that changes by 2040 to 2050.', body)


# ====================================================================== costs
def build_costs():
    ins = table(['Question', 'Property A - 95014, owner-occupied', 'Property B - 94122, rental', 'Official basis'], [
        ['Official premium figure for the ZIP code', BLANK + ' ' + flag('U01'), BLANK + ' ' + flag('U01'), src('CDI-TOOL', 'CDI-TOOL-APP')],
        ['Where the official figure is published', 'California Department of Insurance 2026 homeowners premium survey, by ZIP code, in an interactive tool', 'Same tool. It covers homeowner, condominium, renter and earthquake policies; a landlord (dwelling fire) policy for a three-unit building is not one of its scenarios', src('CDI-TOOL-APP')],
        ['What the survey figures are', 'Premiums for hypothetical homes, for comparison only; not quotes', 'Same', src('CDI-TOOL')],
        ['Owner\'s own estimate used in the model', m(P['ins_home']) + ' a year', m(P['ins_rental']) + ' a year', src('CDI-TOOL')],
        ['Does a wrong estimate change the decision?', 'No. Tripling it lowers the Live result by %s and leaves the ranking unchanged' % m(M['sensitivity'][0]['real_live'] - M['sensitivity'][15]['real_live']), 'No. Property B is the same in all three choices', src('CDI-TOOL')],
        ['Wildfire surcharge', '15% to over 300% in higher-risk areas, not shown in the survey. Whether it applies to this home: ' + BLANK, 'Same', src('CDI-TOOL-APP')],
        ['Earthquake', 'Not covered by a homeowners policy; must be offered every other year. Premium: ' + BLANK + ' ' + flag('U02'), 'Same for a landlord policy; confirm with the insurer', src('CDI-EQ', 'USGS')],
        ['Vacancy', 'Losses to a house vacant 60 days or more are generally excluded', 'Applies to the unit kept empty if it is truly vacant', src('CDI-RES')],
        ['If Property A is rented out', 'The policy must change from homeowners to a landlord policy; the model keeps the same starting premium ' + flag('U01'), 'not applicable', src('CDI-RES')],
    ], caption='Insurance: what could and could not be confirmed')
    how = """<h2>How to get the official insurance figure in five minutes</h2>
<ol><li>Open the <a href="%s" rel="noopener">2026 Homeowners Insurance comparison tool</a> of the California Department of Insurance.</li>
<li>Choose Homeowners, then the county, then the ZIP code (95014, then 94122), a coverage amount near the rebuilding cost and the age of the home.</li>
<li>Read the range of annual premiums across insurers and compare it with the %s estimate used here.</li>
<li>For Property B ask an agent for a landlord (dwelling fire) quote for a three-unit building; the survey has no such scenario.</li></ol>""" % (S['CDI-TOOL-APP']['url'], m(P['ins_home']))
    op = table(['Cost', 'Property A', 'Property B', 'How it is projected', 'Official basis'], [
        ['Property tax (2025 bill)', '%s on an assessed value of %s' % (m(P['cup_tax_2025']), m(P['cup_assessed_2025'])), '%s on an assessed value of %s' % (m(P['sf_tax_2025']), m(P['sf_assessed_2025'])), 'official rate times assessed value, plus fixed charges', src('SCC-RATES', 'SF-TAX')],
        ['Fixed charges inside the bill', 'about %s (bill minus rate times value)' % m(P['dc_cup']), 'about %s' % m(P['dc_sf']), 'with inflation ' + flag('U03'), src('SCC-RATES', 'SF-TAX')],
        ['Water', '%s a year (owner: $100 to $150 a month)' % m(P['cup_water']), '%s a year for three units (owner: $330 to $400 a month)' % m(P['sf_water']), 'inflation + 2 points; Property B +9% in 2027 and 2028', src('SFPUC')],
        ['Electricity', '%s a year: a credit, because of the solar system (owner: $10 to $20 a month)' % m(P['cup_elec']), '%s a year (owner: $30 to $70 a month)' % m(P['sf_elec']), 'inflation + 1 point ' + flag('U05'), src('CPUC-NEM', 'CPUC-FIXED')],
        ['Repairs and maintenance', '%s a year (assumption; owner says lower than B)' % m(P['maint_cup']), '%s a year (assumption)' % m(P['maint_sf']), 'inflation ' + flag('A08'), src('BLS-CPI')],
        ['Rent received', 'none today; HUD figure %s a month if let' % m(P['cup_rent_month']), '%s a month for two units; HUD two-bedroom figure for the ZIP is $3,310' % m(P['sf_rent_2units'] / 12), 'see Year by year', src('HUD-95014', 'HUD-94122')],
        ['Management and vacancy if Property A is let', '6% of rent and 5% of the year (assumptions)', 'self-managed; 5% vacancy', flag('A06'), src('HUD-95014')],
    ], caption='Running costs and the figures behind them')
    hA = table(['Tax year', 'Property A tax bill', 'Property A assessed value', 'Official basis'], [
        [y, m(t), m(a), src('SCC-RATES')] for y, t, a in [
            (2026, None, 550540), (2025, 7210, 539740), (2024, 7000, 529160), (2023, 6920, 518790), (2022, 6760, 508610), (2021, 6660, 498640),
            (2020, 6570, 493500), (2019, 6570, 483850), (2018, 6380, 474370), (2017, 6380, 465070), (2016, 6410, 455950), (2015, 6100, 449100), (2014, 5970, 440310)]
        if t is not None
    ] + [[2026, 'not yet billed', m(550540), src('SCC-RATES')]], caption='Property A history as supplied by the owner (rounded to $10)', cls='num',
        note='The assessed value rose 2% in most years, the legal maximum, which is what the projection continues. A supplied figure that was already a multiple of $10 is shown to the nearest $100.')
    hB = table(['Tax year', 'Property B tax bill', 'Property B assessed value', 'Official basis'], [
        [y, m(t), m(a), src('SF-TAX')] for y, t, a in [
            (2025, 2440, 114250), (2024, 2320, 112010), (2023, 2180, 109810), (2022, 2110, 107660), (2021, 2070, 105600),
            (2020, 2200, 104510), (2019, 2130, 102470), (2018, 2060, 100460), (2017, 1700, 98490), (2016, 1680, 96560)]
    ], caption='Property B history as supplied by the owner (rounded to $10)', cls='num')
    body = ins + how + op + hA + hB
    page('costs.html', 'Insurance and running costs',
         'Home insurance for ZIP 95014, rental-property insurance for ZIP 94122, and the utility and repair figures used in the projections.', body)


# ====================================================================== flagged
def build_flagged():
    cats = [
        ('Q', 'Questions only the owner or a professional can answer'),
        ('U', 'Values that could not be confirmed on an official page (left blank)'),
        ('A', 'Model assumptions (no official figure exists)'),
        ('S', 'Irregularities in sources'),
        ('R', 'Irregularities in the repository'),
    ]
    body = '<p class="callout">Flagged for Review. Nothing on this page blocks the rest of the site. Each item says what is missing or uncertain, what was used instead, and where to check it.</p>'
    for c, title in cats:
        rows = [['<span id="%s">%s</span>' % (f['id'], f['id']), f['item'], f['used'], f['check'], src(*f['src']) + (' · ' + f['extra'] if f.get('extra') else '')] for f in FLAGS if f['id'].startswith(c)]
        body += table(['No.', 'Item', 'What the site does', 'How to resolve it', 'Where to check'], rows, caption=title)
    ex = [['E-' + k, e(v['title']), e(v['read']), '<a href="%s" rel="noopener">%s</a>' % (e(v['url']), e(v['label'])) + (' · official reference for current rates: ' + src('TREASURY') if v['how'] == 'academic' else '')] for k, v in sorted(S.items()) if v['how'] != 'page']
    body += table(['No.', 'Source not read in full', 'Text relied on', 'Open the page'], ex, caption='Sources read through an excerpt of the official page, or not official: re-read by hand')
    page('flagged.html', 'Flagged for Review',
         'Every value that could not be confirmed, every assumption, and every irregularity found, with a link for manual checking.', body)


# ====================================================================== sources
def build_sources():
    how = {'page': 'Official page read in full', 'excerpt': 'Official page, read through a search excerpt', 'academic': 'Not a government source'}
    rows = [[k, e(v['title']), how[v['how']], e(v['read']), '<a href="%s" rel="noopener">%s</a>' % (e(v['url']), e(v['label'])) + (' · official reference for current rates: ' + src('TREASURY') if v['how'] == 'academic' else '')] for k, v in sorted(S.items())]
    t = table(['Key', 'Source', 'How it was read on %s' % BUILD_DATE, 'What was read there', 'Link'], rows, caption='Source register')
    method = """
<h2>Method</h2>
<ul>
<li><strong>One model.</strong> <a href="%s/blob/main/final/model.py">final/model.py</a> projects both homes year by year from 2026 to 2076 and compares three choices for Property A from the year of inheritance. It uses only the Python standard library.</li>
<li><strong>Like-for-like comparison.</strong> Each choice has an investment account that receives every dollar the choice produces or costs, invested the same way. At each year-end the model works out what would be left if everything were sold and all taxes paid.</li>
<li><strong>Property B is never inherited in the model.</strong> Its assessed value, basis and rent continue unchanged. It enters the comparison only through the third unit, which is let when the Inheritor moves to Property A.</li>
<li><strong>Property tax.</strong> Assessed values rise with inflation up to 2%% a year and never exceed market value. At inheritance Property A is set to market value, or to the Proposition 19 partial value if lived in.</li>
<li><strong>Income tax.</strong> Yearly income at 24%% federal, 9.3%% California and the 3.8%% investment-income tax. One-off sales at 20%% + 3.8%% + 13.3%%. Depreciation taken on a rental is taxed back at 25%% federal on sale.</li>
<li><strong>Non-constant paths.</strong> Real recorded years 1976-2025 are replayed in order from each possible start; named paths insert real crisis years into the baseline.</li>
<li><strong>Rounding and privacy.</strong> Owner figures are stored only rounded to $10. No names, addresses or parcel numbers are used. Search engines are asked not to index the pages.</li>
<li><strong>Checks.</strong> <a href="%s/blob/main/final/check.py">final/check.py</a> fails the build if a table row has no official link, if an internal link is broken, if a dollar figure is not a multiple of $10 (official published figures excepted), or if a stored fingerprint of an unrounded owner figure appears anywhere.</li>
</ul>
<h2>Reproduce</h2>
<pre>python3 final/model.py &amp;&amp; python3 final/build.py &amp;&amp; python3 final/check.py</pre>""" % (REPO, REPO)
    page('sources.html', 'Sources and method', 'Every source used, how it was read, and how the numbers are produced.', t + method)


# ====================================================================== review
def build_review():
    rows = [[r['id'], r['where'], r['finding'], r['status'], src(*r['src']) + ' · <a href="%s/%s" rel="noopener">file</a>' % (REPO, r['path'])] for r in REVIEW]
    t = table(['No.', 'Where', 'Finding', 'Status', 'Rule or source, and file'], rows, caption='Repository review findings') if rows else ''
    body = """<p class="callout">The repository holds several generations of the same analysis written by parallel sessions. This page records what an independent pass found, so that a reader knows which pages to trust. The full history is in <a href="%s/blob/main/COORDINATION.md">COORDINATION.md</a>.</p>""" % REPO + t
    page('review.html', 'Repository review', 'Irregularities found while reading the repository, with links to the files and to the rule each one is measured against.', body)


CSS = """
:root{--ink:#16202b;--mut:#5b6875;--line:#d9dee4;--bg:#f6f7f9;--card:#fff;--acc:#1f4e8c;--warn:#9a5b00;--warnbg:#fff6e0}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#12283f;color:#fff;position:sticky;top:0;z-index:5}
header.top .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;padding-top:10px;padding-bottom:10px}
.brand{color:#fff;font-weight:700;text-decoration:none;margin-right:8px}
nav{display:flex;flex-wrap:wrap;gap:2px}
nav a{color:#d5e1ee;text-decoration:none;padding:5px 9px;border-radius:5px;font-size:14px}
nav a:hover{background:#21405f}nav a.on{background:#fff;color:#12283f;font-weight:600}
h1{font-size:30px;line-height:1.2;margin:28px 0 8px}h2{font-size:21px;margin:34px 0 10px}
.lead{font-size:18px;color:var(--mut);max-width:900px;margin:0 0 20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.kpi .k{font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em}
.kpi .v{font-size:22px;font-weight:700;margin:4px 0;font-variant-numeric:tabular-nums}
.kpi .s{font-size:13px;color:var(--mut)}
.plan li{margin:0 0 10px}.plan{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 16px 8px 38px}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
caption{text-align:left;font-weight:700;padding:12px 14px;font-size:15px;caption-side:top}
th,td{padding:8px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:#eef1f5;font-size:13px;position:sticky;top:0}
table.num td:not(:first-child):not(:last-child){font-variant-numeric:tabular-nums}
table.yr td{white-space:nowrap;padding:5px 10px}table.yr td:last-child{white-space:normal;min-width:150px}
tbody tr:hover{background:#f3f7fc}
a{color:var(--acc)}a.src{font-size:12.5px;white-space:nowrap}
a.flag{font-size:12px;background:var(--warnbg);color:var(--warn);border:1px solid #e6c98a;border-radius:4px;padding:0 5px;text-decoration:none;white-space:nowrap}
.blank{font-style:italic;color:var(--warn)}
.note{font-size:13.5px;color:var(--mut);max-width:980px}
.callout{background:var(--warnbg);border:1px solid #e6c98a;border-radius:10px;padding:12px 16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--acc)}.card b{display:block;color:var(--acc);margin-bottom:4px}.card span{font-size:14px;color:var(--mut)}
.seg{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:10px 0}.seg span{font-size:14px;color:var(--mut)}
.seg button{font:inherit;font-size:14px;padding:5px 12px;border:1px solid var(--line);background:#fff;border-radius:6px;cursor:pointer}
.seg button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.chart{width:100%;max-width:820px;height:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}
.chart .lab{font-size:13px;fill:#16202b}.chart .val{font-size:13px;fill:#16202b;font-weight:600}
.chart .ax{font-size:11px;fill:#5b6875}.chart .grid{stroke:#e3e7ec;stroke-width:1}.chart .mark{stroke:#9a5b00;stroke-dasharray:4 3}
.legend{font-size:13px;color:var(--mut);display:flex;flex-wrap:wrap;gap:4px 16px;margin:6px 0 0}
.legend i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:5px;vertical-align:-1px}
pre{background:#12283f;color:#e8eef5;padding:12px 14px;border-radius:8px;overflow:auto}
footer{color:var(--mut);font-size:13px;margin-top:40px;padding-bottom:40px;border-top:1px solid var(--line)}
[hidden]{display:none!important}
@media (max-width:640px){h1{font-size:24px}.lead{font-size:16px}}
"""

JS = """
(function(){
  var t=document.getElementById('tsel');
  if(t){t.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;
    t.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
    document.querySelectorAll('#dash tbody').forEach(function(tb){tb.hidden=tb.getAttribute('data-t')!==b.getAttribute('data-t')});});}
  var y=document.getElementById('ysel');
  if(y){var ids=['a-pre','a-live','a-rent','b-all'];
    var show=function(k){ids.forEach(function(i){var el=document.getElementById(i);if(el)el.closest('.tablewrap').hidden=(k!=='all'&&k!==i)});};
    show('a-pre');
    y.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;
      y.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});show(b.getAttribute('data-y'));});}
})();
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'style.css'), 'w').write(CSS)
    open(os.path.join(OUT, 'app.js'), 'w').write(JS)
    for f in (build_index, build_decision, build_projections, build_blackswan, build_process, build_law,
              build_estate, build_costs, build_flagged, build_sources, build_review):
        f()
    print('built', len([x for x in os.listdir(OUT) if x.endswith('.html')]), 'pages in', OUT)


if __name__ == '__main__':
    main()
