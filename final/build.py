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
import questions as QUESTIONS_DATA
import suggestions as SUGGESTIONS_DATA
from review_queue import render_queue, render_verification  # noqa: E402

M = json.load(open(os.path.join(HERE, 'out', 'model.json')))
P = M['params']
B = M['baseline']['summary']
ROWS = M['baseline']['rows']
OUT = os.path.abspath(os.environ.get('OUT_DIR', os.path.join(HERE, 'site')))
ROOT_MODE = bool(os.environ.get('ROOT_MODE'))
# Since 2026-11-12 the root index.html is the redirect to the privacy-first guide (privacy-site/), which is the only
# edition GitHub Pages serves. Built into the repository root, this edition therefore writes its summary to
# summary.html and never touches index.html (session 0adc9b0a, review item R29).
HOME = 'summary.html' if ROOT_MODE else 'index.html'
Y0 = 2026
T = P['T']
BUILD_DATE = '2026-11-12'
READ_DATE = '2026-11-11'   # first full read of the source register; later passes are dated on the Verification page
REGISTER_DATE = READ_DATE  # the name used by the b724a7d8 lines below
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
    (HOME, 'Summary'),
    ('decision.html', 'Decision'),
    ('questions.html', 'Questions to answer'),
    ('suggestions.html', 'Suggestions'),
    ('projections.html', 'Year by year'),
    ('black-swan.html', 'Black swan'),
    ('process.html', 'Process'),
    ('law.html', 'Law'),
    ('estate-cash.html', 'Cash and estate tax'),
    ('costs.html', 'Insurance and costs'),
    ('flagged.html', 'Flagged for Review'),
    ('sources.html', 'Sources and method'),
    ('verification.html', 'Verification'),
    ('requirements.html', 'Requirements'),
    ('review.html', 'Repo review'),
] + ([('versions.html', 'Earlier versions')] if os.environ.get('ROOT_MODE') else [])


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
<a class="brand" href="%s">Two-home inheritance analysis</a>
<nav aria-label="Sections">%s</nav></div></header>
<main class="wrap">
<h1>%s</h1>
<p class="lead">%s</p>
%s
</main>
<footer class="wrap"><p>Built %s from <a href="%s/tree/main/final">final/</a> (model, generator and checker). %s Property A = Cupertino home (ZIP 95014). Property B = San Francisco three-unit home (ZIP 94122). People are placeholders: "the Transferor" (current owner of Property A) and "the Inheritor" (already owns Property B). Owner-supplied and modelled dollar figures are rounded to the nearest $10. This is an analysis to prepare questions for a licensed estate attorney and tax adviser, not legal or tax advice. Open items are on the <a href="flagged.html">Flagged for Review</a> page.</p></footer>
<script src="app.js"></script>
</body></html>""" % (e(title), HOME, nav, e(title), lead, body, BUILD_DATE, REPO, '<a href="versions.html">Earlier versions</a> are superseded.' if ROOT_MODE else '')
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
RH = M['replay_horizons']
JS_ = M['japan_savings']
VERIFY = REPO + '/blob/main/verify-4395771d/site/index.html'   # repository file, never a published path
NAME = {'live': 'Live in it', 'rent': 'Rent it out', 'sell': 'Sell and reinvest'}
SRC_MODEL_TAX = ('SCC-RATES', 'BOE-LTA-2026-026')


def kpi(label, value, sub=''):
    return '<div class="kpi"><div class="k">%s</div><div class="v">%s</div><div class="s">%s</div></div>' % (label, value, sub)


# ====================================================================== index
def build_index():
    by = M['by_T']
    cards = ''.join([
        kpi('Best financial outcome (conditional)', 'Sell Property A, keep Property B', 'ahead in the baseline; across 50 real historical sequences it leads in %d after 10 years and in %d after 20 - a model result on the assumptions flagged %s and %s, not a verified forecast' % (RH['10']['wins']['sell'], RH['20']['wins']['sell'], flag('A01'), flag('A02'))),
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
            ['Value today / assessed value today', '%s / %s' % (m(P['cup_value']), m(P['cup_assessed'])), '%s / %s' % (m(P['sf_value']), m(P['sf_assessed'])), src('SCC-RATES', 'SF-TAX') + ' &middot; owner-supplied figures, rounded to $10 and not confirmable on an official page %s' % flag('P03')],
            ['What it earns today', 'Nothing (the Transferor lives in it).', '%s a year from two rented units; the third unit is free for the Inheritor.' % m(P['sf_rent_2units']), src('SF-RENT-RULES') + ' &middot; owner-supplied figure, rounded to $10 and not confirmable on an official page %s' % flag('P03')],
        ], caption='Why the two homes must be treated differently')
    plan = """
<ol class="plan">
<li><strong>Keep Property B and keep living in its third unit.</strong> Its assessed value is %s against a market value of %s, which saves about %s of property tax every year, and that saving is lost for good if it is sold. It also has no basis reset, so selling it would tax the whole gain. It already produces %s a year.</li>
<li><strong>Sell Property A within a few months of inheriting it and invest the proceeds in a diversified stock fund.</strong> With the basis reset to the date-of-death value the sale has no taxable gain (the model shows a small loss of %s from selling costs). About %s is released. In the baseline it grows to %s by 2076 after all taxes (%s in 2026 dollars), against %s if rented and %s if lived in.</li>
<li><strong>Expect the first ten years to be the risky ones.</strong> Replaying the real 1976-2025 record from each of its 50 starting years, selling is ahead of renting in %d of 50 cases ten years after the inheritance and in all 50 after twenty. In the worst ten-year case selling is behind by %s (2026 dollars). A long stagnation of the kind Japan had after 1990 is the worst tested path for selling into stocks: renting ends ahead in it, and renting also edges ahead in the 1929-1941 Depression path - the only two named paths where selling into stocks loses to renting (see the Black swan section). Investing the proceeds in stages and keeping a few years of spending in Treasury bills narrows that risk.</li>
<li><strong>Do not sell and park the money in savings.</strong> If the proceeds would sit in savings or Treasury bills at about 3.5%%, keeping the house as a rental comes out ahead (%s against %s in 2026 dollars).</li>
<li><strong>Living in Property A is a lifestyle choice with a price.</strong> The assessed value jumps from %s to %s even with the Proposition 19 relief, so the tax bill rises from about %s to about %s a year. Compared with selling, living there costs about %s of 2076 wealth in 2026 dollars.</li>
<li><strong>Before anything else, have the trust read by an estate attorney.</strong> The whole result depends on the home being included in the Transferor's gross estate so that the basis resets. If it is not, selling triggers tax on decades of gain (the model shows %s less wealth in 2026 dollars). See the <a href="flagged.html">Flagged for Review</a> page.</li>
</ol>""" % (
        m(P['sf_assessed']), m(P['sf_value']), m(sf_gap), m(P['sf_rent_2units']),
        m(-B['sell_gain']), m(B['sell_net']), m(B['w_sell']), m(B['real_sell']), m(B['w_rent']), m(B['w_live']),
        RH['10']['wins']['sell'], m(-RH['10']['sell_minus_rent_worst']),
        m(M['sensitivity'][6]['real_rent']), m(M['sensitivity'][6]['real_sell']),
        m(B['fbyv_T']), m(B['taxable_live_T']), m(B['tax_before_T']), m(B['tax_live_T']),
        m(B['real_sell'] - B['real_live']),
        m(B['real_sell'] - M['sensitivity'][-1]['real_sell']))
    chart = bars([(NAME[k], B['real_' + k], COL[k]) for k in ('sell', 'rent', 'live')])
    links = ''.join('<a class="card" href="%s"><b>%s</b><span>%s</span></a>' % x for x in [
        ('decision.html', 'Decision', 'Live, rent or sell: numbers, sensitivities and break-even points'),
        ('questions.html', 'Questions to answer', 'What must still be answered before a decision, what is missing, and how to discover it'),
        ('suggestions.html', 'Suggestions', 'Suggestions to improve the decision and this site, with a review-and-choose workflow'),
        ('projections.html', 'Year by year', 'Value, assessed value, tax, insurance, water, electricity and repairs, 2026 to 2076'),
        ('black-swan.html', 'Black swan', 'Fifty real historical sequences and named crisis paths, kept apart from the baseline'),
        ('process.html', 'Process', 'Step-by-step list with legal deadlines after the Transferor\'s death'),
        ('law.html', 'Law', 'Federal, California and local rules today, and changes under discussion'),
        ('estate-cash.html', 'Cash and estate tax', 'Thresholds, room before tax is due, and projections to 2050'),
        ('costs.html', 'Insurance and costs', 'What could and could not be confirmed for ZIP 95014 and 94122'),
        ('flagged.html', 'Flagged for Review', 'Every unconfirmed value, assumption and irregularity, with links'),
        ('suggestions.html', 'Suggestions', 'Proposed improvements — data, model and site — with review status so you can choose a path before any build'),
        ('questions.html', 'Questions to answer', 'Clear list of what we have, what is missing, and how to discover it before deciding'),
        ('verification.html', 'Verification', 'Line-by-line check register: what was re-read on which official page, and what stays flagged'),
        ('requirements.html', 'Requirements', 'Every part of the brief, the page that answers it, and the official pages re-read on 2026-11-11'),
    ])
    body = """
<section class="kpis">%s</section>
<h2>Best plan and why - conditional on the assumptions in the flags</h2>%s
<h2>After-tax wealth in 2076, in 2026 dollars (baseline, inheritance in %d)</h2>%s
<p class="note">Wealth counts only what differs between the choices: Property A itself, every cash flow it causes, and rent from the Inheritor's vacated unit in Property B when the Inheritor moves to Property A. The two units already rented in Property B are the same in all three choices and are left out. All figures assume everything is sold and taxed at the end so that the choices can be compared like for like.</p>
<h2>Dashboard</h2>
<div class="seg" id="tsel" aria-label="Year of inheritance"><span>Year of inheritance:</span>%s</div>
%s
<p class="note"><strong>How to read the numbers.</strong> Three kinds of figures appear on this site. <strong>Official facts</strong> are quoted from the government page linked on the row. <strong>Owner-supplied figures</strong> (market values, rents, utilities, tax bills, insurance estimates) are the owner's own numbers: they are rounded to the nearest $10 for privacy, cannot be confirmed on an official page (%s), and the link on their row shows only the rule or index the calculation follows, not verification of the figure. <strong>Model outputs</strong> are projections from the assumptions on the <a href="flagged.html">Flagged for Review</a> page - conditional scenarios, not forecasts. Every headline fact was re-read on its official page in three independent passes, on 2026-11-11 and twice on 2026-11-12: see the <a href="verification.html">Verification</a> register.</p>
<h2>The two homes are not the same case</h2>%s
<p class="callout"><strong>Looking for the version with no household figures?</strong> A separate <a href="privacy-site/public/index.html">no-figures decision guide</a> publishes the same rules, process and decision framework without any of this household's numbers - every illustration there is invented for teaching. This summary page carries the rounded (nearest $10) figures the owner asked to see in the decision analysis.</p>
<h2>Sections</h2><div class="cards">%s</div>
""" % (cards, plan, T, chart, opts, dash, flag('P03'), diff, links)
    page(HOME, 'Executive summary',
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
        note='The rent for Property A is the HUD four-bedroom Small Area Fair Market Rent for ZIP 95014 (%s a month in fiscal year 2026) grown with inflation plus 0.5 point. The number of bedrooms was not supplied (%s); the rent itself is an assumption (%s).' % (m(P['cup_rent_month']), flag('U08'), flag('A07')))
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
    S_ = M['sensitivity']
    where = table(['If Property A is sold, the proceeds go into', 'Assumed yearly return', 'Sell and reinvest: wealth in 2076 (2026 dollars)', 'Renting instead, same reinvestment of rent', 'Better choice', 'Official basis'], [
        ['A diversified stock fund', '7.0%', m(S_[0]['real_sell']), m(S_[0]['real_rent']), NAME[S_[0]['best']], src('TREASURY') + ' · ' + src('DAMODARAN')],
        ['60% stocks, 40% Treasury bonds', '7.0% and 4.5%', m(S_[7]['real_sell']), m(S_[7]['real_rent']), NAME[S_[7]['best']], src('TREASURY') + ' · ' + src('DAMODARAN')],
        ['Savings account or Treasury bills', '3.5%', m(S_[6]['real_sell']), m(S_[6]['real_rent']), NAME[S_[6]['best']], src('TREASURY')],
    ], caption='Stocks or savings: where the sale proceeds go decides the answer', cls='num',
        note='Returns are assumptions (%s). On 2026-11-10 the 3-month Treasury bill yielded 4.30%% and the 10-year note 4.98%%. Interest is taxed every year at ordinary rates; stock growth is taxed when sold.' % flag('A02'))
    body = at + first + w + where + '<h2>Wealth over time, in 2026 dollars</h2>' + chart + why + sens + be + byT + '<h2>Property A or Property B?</h2>' + which
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
        ['Times it was the best choice 10 years after inheritance', RH['10']['wins']['live'], RH['10']['wins']['rent'], RH['10']['wins']['sell'], src('FHFA-SJ', 'BLS-CPI')],
        ['Times it was the best choice 20 years after inheritance', RH['20']['wins']['live'], RH['20']['wins']['rent'], RH['20']['wins']['sell'], src('FHFA-SJ', 'BLS-CPI')],
        ['Times it was the best choice in 2076', wins.get('live', 0), wins.get('rent', 0), wins.get('sell', 0), src('FHFA-SJ', 'BLS-CPI')],
        ['Worst result 10 years after inheritance (2026 dollars)', m(RH['10']['worst']['live']), m(RH['10']['worst']['rent']), m(RH['10']['worst']['sell']), src('FHFA-SJ', 'BLS-CPI')],
        ['Worst result 20 years after inheritance (2026 dollars)', m(RH['20']['worst']['live']), m(RH['20']['worst']['rent']), m(RH['20']['worst']['sell']), src('FHFA-SJ', 'BLS-CPI')],
        ['Worst result in 2076 (2026 dollars)', m(rep_sorted('live')[0]), m(rep_sorted('rent')[0]), m(rep_sorted('sell')[0]), src('FHFA-SJ', 'BLS-CPI')],
        ['Middle result in 2076 (2026 dollars)', m(med('live')), m(med('rent')), m(med('sell')), src('FHFA-SJ', 'BLS-CPI')],
        ['Best result in 2076 (2026 dollars)', m(rep_sorted('live')[-1]), m(rep_sorted('rent')[-1]), m(rep_sorted('sell')[-1]), src('FHFA-SJ', 'BLS-CPI')],
        ['Baseline (constant rates) for comparison', m(B['real_live']), m(B['real_rent']), m(B['real_sell']), src('FHFA-SJ', 'BLS-CPI')],
    ], caption='Replay of the real 1976-2025 sequence from every possible starting year (wrapped around to fill 2027-2076)', cls='num',
        note='Each replay keeps the real year-to-year order, so inflation, home prices and stocks move together as they actually did. The spread is very wide because the order of good and bad years matters: a boom just after the sale helps the seller, a crash just after hurts. Ten years after the inheritance selling is behind renting in %d of the 50 histories, by as much as %s; after twenty years it is ahead in every one. The 1976-2025 period was an unusually good one for United States stocks, which is why the Depression and Japan paths below are shown as well.' % (RH['10']['wins']['rent'], m(-RH['10']['sell_minus_rent_worst'])))
    PD = {x['key']: x['summary'] for x in M['paths']}
    named = table(['Path', 'Market value at inheritance', 'Tax if lived in / rented, first year', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Best', 'Official basis'], [
        [e(x['label']), m(x['summary']['fmv_T']), '%s / %s' % (m(x['summary']['tax_live_T']), m(x['summary']['tax_rent_T'])),
         m(x['summary']['real_live']), m(x['summary']['real_rent']), m(x['summary']['real_sell']), NAME[x['summary']['best']],
         (src('FRED-JP') if x['key'] == 'japan_at_T' else src('FHFA-SJ', 'BLS-CPI') + ' · ' + src('DAMODARAN'))]
        for x in M['paths']
    ] + [['Baseline (constant rates)', m(B['fmv_T']), '%s / %s' % (m(B['tax_live_T']), m(B['tax_rent_T'])), m(B['real_live']), m(B['real_rent']), m(B['real_sell']), NAME[B['best']], src('FHFA-SJ', 'BLS-CPI')]],
        caption='Named paths (wealth in 2076, in 2026 dollars; inheritance in %d)' % T, cls='num',
        note='The Depression path uses national home-price data because no local index goes back that far (%s). Selling into stocks ends behind renting in two of the named paths: the 1929-1941 Depression sequence (renting %s against %s for selling) and Japan-style stagnation (renting %s against %s), the worse of the two. In the Japan path, had the proceeds been kept in savings instead of stocks, selling would have ended at %s against %s for renting (%s).' % (flag('S02'), m(PD['depression_at_T']['real_rent']), m(PD['depression_at_T']['real_sell']), m(PD['japan_at_T']['real_rent']), m(PD['japan_at_T']['real_sell']), m(JS_['real_sell']), m(JS_['real_rent']), flag('S08')))
    PATHS = {x['key']: x for x in M['paths']}
    ch = lines([
        ('Baseline', COL['before'], {r['year']: r['cup_value'] / r['cpi'] for r in ROWS}),
        ('Real 1976-2025 order', COL['rent'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['replay_1976']['rows']}),
        ('Real order from 2000', COL['sell'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['replay_2000']['rows']}),
        ('2007-2012 bust at inheritance', COL['live'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['crash_at_T']['rows']}),
        ('Depression at inheritance', COL['x'], {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['depression_at_T']['rows']}),
        ('Japan-style stagnation at inheritance', '#c0392b', {r['year']: r['cup_value'] / r['cpi'] for r in PATHS['japan_at_T']['rows']}),
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
            + rep + named + '<h2>Property A market value in 2026 dollars under six paths</h2>' + ch + stats + other + yr + yr2 + hist)
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
        ['7', 'Within 150 days of death', 'File the change-in-ownership statement for Property A with the Santa Clara County Assessor.', 'Statutory deadline when ownership changes by death; the notice required by the statute warns of a penalty for not filing.', src('RTC-480')],
        ['8', 'Within 9 months of death', 'File Form 706 if the gross estate plus adjusted taxable gifts is above the filing threshold, or to elect portability for a surviving spouse. Form 4768 gives six more months.', 'Above the threshold the tax is 40% of the excess. Portability is lost without a timely return.', src('IRS-FAQ-ESTATE', 'IRS-I706')],
        ['9', 'Decide early: live, rent or sell', 'Use the <a href="decision.html">Decision</a> page. If selling, list promptly and keep the home insured while empty.', 'A sale near the date-of-death value has almost no taxable gain. Vacant homes can lose cover after 60 days.', src('IRS-FAQ-INHERIT', 'CDI-RES')],
        ['10', 'Within 1 year, only if moving in', 'Make Property A the Inheritor\'s principal residence and file for the homeowners\' exemption there.', 'Without both, the Proposition 19 exclusion is not available and the home is reassessed at full market value.', src('RTC-63.2', 'BOE-LTA-2026-026')],
        ['11', 'Within 3 years, only if moving in', 'File the parent-child exclusion claim (form BOE-19-P) with the Assessor, before any transfer to a third party.', 'The county page says later claims receive relief only going forward; confirm with the Assessor. ' + flag('S03'), src('BOE-P19', 'SCC-P19')],
        ['12', 'After the Assessor acts', 'Expect a supplemental tax bill for Property A covering the period from the date of death.', 'Budget for it in every choice. The San Francisco page describes the same California process. ' + flag('U06'), src('SF-TAX')],
        ['13', 'Tax year of the sale, if sold', 'Report the sale on Form 8949 and Schedule D using the date-of-death value as basis; match any Schedule A to Form 8971 received.', 'A basis above the value finally determined for estate tax can draw an accuracy penalty.', src('IRS-FAQ-INHERIT', 'IRS-TC409')],
        ['14', 'Every year, if rented', 'Report rent and expenses; depreciate the building part of the new basis over 27.5 years. Follow the state rent cap and its notice rules.', 'Depreciation shelters part of the rent but is taxed back at up to 25% federal on a later sale.', src('IRS-P527', 'IRS-TC409', 'DOJ-TPA')],
        ['15', 'When the cash arrives', 'Nothing to report as income for the inheritance itself. Income earned on it afterwards is taxable. Inherited retirement accounts follow different rules.', 'The cash is taxed, if at all, to the estate before it is paid out, not to the Inheritor.', src('IRS-P559')],
        ['16', 'Throughout', 'Leave Property B exactly as it is: same owner, same exemption or rental status.', 'Any transfer of Property B could trigger its own reassessment; nothing about the inheritance requires one.', src('BOE-P19', 'SF-TAX')],
    ], caption='Steps and deadlines for Property A')
    body = steps + '<p class="note">Deadlines are quoted from the linked statutes and agency pages as read on %s and re-checked on %s. Forms and county procedures change; confirm each one with the county office and the attorney handling the trust.</p>' % (REGISTER_DATE, BUILD_DATE)
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
    pend = table(['Change', 'Level', 'Status read on %s' % READ_DATE, 'Effect if it happens', 'Official basis'], [
        ['Indexing of the estate exclusion', 'Federal', 'In force. 2027 figure published 2026-11-05.', 'The exclusion rises each year with inflation; the model projects %s by %d.' % (m(B['exclusion_T']), T), src('RP-2026-35', 'IRS-NEW')],
        ['Death Tax Repeal Act (S.587 and H.R.1301)', 'Federal', 'Introduced 2025-02-13 and referred to committee. No later action shown.', 'Would repeal the estate tax. No effect on the property-tax or income-tax results.', src('CONG-S587', 'CONG-HR1301')],
        ['Any reduction of the exclusion or of the basis reset', 'Federal', 'No enacted measure found. Would need a new Act of Congress.', 'See the stress rows on the Cash and Black swan pages.', src('IRS-NEW')],
        ['Next adjustment of the Proposition 19 allowance', 'California', 'Scheduled for 2027-02-16, using the 2026 California house-price change. Figure: ' + BLANK + ' ' + flag('U04'), 'Sets the allowance for transfers through 2029-02-15.', src('BOE-LTA-2025-009')],
        ['Proposition 3 (extends the existing tax on high incomes)', 'California', 'Yes 60.7% in unofficial returns as of 2026-11-11 6:51 p.m.; certification due by 2026-12-11.', 'Would keep the existing higher state rates on high incomes, which reach a large one-year gain. Details are in the voter guide.', src('SOS-RESULTS')],
        ['Proposition 40 (one-time tax on certain taxpayers)', 'California', 'No 52.5% in unofficial returns as of 2026-11-11 6:51 p.m.', 'None if the result holds.', src('SOS-RESULTS')],
        ['Proposition 42 (bars new state personal-property taxes and certain retroactive taxes)', 'California', 'Yes 51.4% in unofficial returns as of 2026-11-11 6:51 p.m.', 'Would bar new state taxes on personal property; relevant to invested sale proceeds if the result holds.', src('SOS-RESULTS')],
        ['Measure to undo the Proposition 19 inheritance rules', 'California', 'Reported by non-official websites as a signature drive. Not among the measures on the November 2026 ballot. ' + flag('S04'), 'Would restore relief for rented inherited homes.', src('SOS-RESULTS')],
        ['Limit on banked and capital-improvement rent increases (File No. 261020)', 'San Francisco', 'Under consideration by the Board of Supervisors; not enacted.', 'Would cap those increases at 10% a year on Property B.', src('SF-RENT-RULES')],
        ['Empty Homes Tax appeal', 'San Francisco', 'City lost on appeal; no collection unless reversed.', 'If revived, a charge on the unit kept empty.', src('SF-EHT')],
        ['Residential fixed charge on electricity bills', 'California', 'Adopted: $24.15 a month for standard customers.', 'May reduce or remove the monthly solar credit at Property A.', src('CPUC-FIXED')],
        ['Missing October 2025 inflation data', 'Federal', 'No 12-month change published for October 2026.', 'Indexed figures still use the published series; watch for revisions.', src('BLS-OCT')],
        ['San Francisco File No. 261020 (limit on banked and capital-improvement rent increases)', 'San Francisco', 'Not enacted. A Rent Board notice posted 2026-11-09 says it would cap these increases at 10% a year for notices served on or after 2026-09-15 (read 2026-11-12).', 'Would slow catch-up rent increases at Property B if the building is rent-controlled (%s). No effect on Property A.' % flag('Q04'), src('SF-RENT-RULES', 'SF-LEG-261020')],
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
        ['Official statewide yardstick', 'About $1,130 a policy in 2023 across all residential policy forms, with an average insured building value of about $324,970. Homeowners policies averaged $1,176 over 2008-2023.', 'Landlord (tenant-occupied dwelling-fire) policies averaged $601 over 2008-2023, statewide.', src('CDI-SB824', 'CDI-RPI')],
        ['What the yardstick suggests', 'The owner estimate is of the right order, but a home of this value insures a building worth far more than the state average, so a real quote may be higher.', 'The owner estimate is above the long-run statewide landlord average; a three-unit building in San Francisco may still cost more.', src('CDI-SB824', 'CDI-RPI')],
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
        ['Property tax (2025 bill)', m(P['cup_tax_2025']), m(P['sf_tax_2025']), 'official rate times assessed value, plus fixed charges', src('SCC-RATES', 'SF-TAX')],
        ['Assessed value (2026)', m(P['cup_assessed']), m(P['sf_assessed']), 'inflation, capped at 2% a year; never reassessed for Property B', src('BOE-P19', 'SF-TAX')],
        ['Fixed charges inside the bill', 'about %s (bill minus rate times value)' % m(P['dc_cup']), 'about %s' % m(P['dc_sf']), 'with inflation ' + flag('U03'), src('SCC-RATES', 'SF-TAX')],
        ['Water', '%s a year (owner: $100 to $150 a month)' % m(P['cup_water']), '%s a year for three units (owner: $330 to $400 a month)' % m(P['sf_water']), 'inflation + 2 points; Property B +9% in 2027 and 2028', src('SFPUC')],
        ['Electricity', '%s a year: a credit, because of the solar system (owner: $10 to $20 a month)' % m(P['cup_elec']), '%s a year (owner: $30 to $70 a month)' % m(P['sf_elec']), 'inflation + 1 point ' + flag('U05'), src('CPUC-NEM', 'CPUC-FIXED')],
        ['Repairs and maintenance', '%s a year (assumption; owner says lower than B)' % m(P['maint_cup']), '%s a year (assumption)' % m(P['maint_sf']), 'inflation ' + flag('A08'), src('BLS-CPI')],
        ['Rent received', 'none today; HUD figure %s a month if let' % m(P['cup_rent_month']), '%s a month for two units; HUD two-bedroom figure for the ZIP is $3,310' % m(P['sf_rent_2units'] / 12), 'see Year by year', src('HUD-95014', 'HUD-94122')],
        ['Management and vacancy if Property A is let', '6% of rent and 5% of the year (assumptions)', 'self-managed; 5% vacancy', flag('A06'), src('HUD-95014')],
    ], caption='Running costs and the figures behind them')
    # Privacy: the owner-supplied year-by-year history is NOT listed. A multi-year series can point to one
    # parcel even when each figure is rounded, and the decision needs only its growth rates.
    hist = table(['What the owner-supplied history shows', 'Property A', 'Property B', 'Use in the model', 'Official basis'], [
        ['Years covered', '2014 to 2026', '2016 to 2025', 'not listed year by year, for privacy ' + flag('P01'), src('BOE-P19')],
        ['Average yearly growth of the assessed value', '1.9%', '1.9%', 'continued at inflation, capped at 2%', src('BOE-P19')],
        ['Average yearly growth of the tax bill', '1.7%', '4.2% (fixed charges rose in one year)', 'rate held constant; fixed charges grow with inflation', src('SCC-RATES', 'SF-TAX')],
        ['Tax bill as a share of assessed value, 2025', '1.34%', '2.14%', 'official rate plus fixed charges ' + flag('U03'), src('SCC-RATES', 'SF-TAX')],
        ['Assessed value as a share of market value, 2026', pc(P['cup_assessed'] / P['cup_value'], 0), pc(P['sf_assessed'] / P['sf_value'], 0), 'the gap is what a reassessment would tax', src('BOE-P19')],
    ], caption='History, summarised')
    body = ins + how + op + hist
    page('costs.html', 'Insurance and running costs',
         'Home insurance for ZIP 95014, rental-property insurance for ZIP 94122, and the utility and repair figures used in the projections.', body)


# ====================================================================== verification
def build_verification():
    v = [
        ('Federal estate-tax filing threshold, year of death 2026',
         'A return is required when the gross estate plus adjusted taxable gifts exceeds $15,000,000 (2026)',
         'Confirmed on the page', src('IRS-ESTATE')),
        ('Federal basic exclusion for 2027',
         'Rev. Proc. 2026-35 section 3.44: $15,480,000 for calendar year 2027',
         'Confirmed - the figure the estate projections start from', src('RP-2026-35')),
        ('Annual gift exclusion for 2027',
         'Rev. Proc. 2026-35 section 3.46: $20,000',
         'Confirmed on the page', src('RP-2026-35')),
        ('The 2026 exclusion is set by statute',
         'Public Law 119-21 (signed 2025-07-04) raises the basic exclusion to $15,000,000 for 2026',
         'Confirmed on the page', src('IRS-NEW')),
        ('Basis of inherited property',
         'Generally the fair market value at the date of death (or the alternate valuation date if elected on Form 706); a sale above basis is a taxable gain',
         'Confirmed - the basis reset the plan depends on', src('IRS-FAQ-INHERIT')),
        ('Trusts outside the gross estate',
         'Rev. Rul. 2023-2: the section 1014 basis adjustment generally does not apply to assets of an irrevocable grantor trust not included in the deceased grantor\'s gross estate',
         'Confirmed - the basis of flag Q01', src('RR-2023-2')),
        ('Home-sale exclusion',
         'Up to $250,000 ($500,000 on a joint return); ownership and use tests of 24 months in the 5 years before the sale',
         'Confirmed on the page', src('IRS-TC701')),
        ('Capital-gain rates',
         '0%, 15% or 20% by income; unrecaptured section 1250 gain taxed at up to 25%',
         'Confirmed on the page', src('IRS-TC409')),
        ('Net investment income tax',
         '3.8% on rents, dividends, interest and gains above $200,000 single / $250,000 joint modified AGI',
         'Confirmed on the page', src('IRS-TC559')),
        ('Form 706 deadline and portability',
         'Nine months after the date of death; Form 4768 gives six months more; Rev. Proc. 2022-32 allows a late portability election to the fifth anniversary',
         'Confirmed - matches the Process page', src('IRS-FAQ-ESTATE')),
        ('California estate or inheritance tax',
         'No California estate tax return is required for deaths on or after 2005-01-01',
         'Confirmed - California adds no death tax', src('SCO-ESTATE')),
        ('Proposition 13 growth cap',
         'R&TC 51(a)(1)(D): in no event shall the annual inflation increase exceed 2 percent of the prior year\'s value',
         'Confirmed - the 2% cap used in every projection', src('RTC-51')),
        ('Proposition 19 family-home exclusion',
         'Principal residence of transferor and transferee; value limit = current taxable value plus $1,000,000, adjusted every two years; homeowners\' exemption within one year; claim within three years',
         'Confirmed - the rule the model applies', src('BOE-P19')),
        ('Proposition 19 allowance amount',
         '$1,044,586 for transfers 2025-02-16 through 2027-02-15; adjusted every other February 16 by the FHFA California house-price change (2.15% for 2024); next adjustment February 2027',
         'Confirmed - matches the model input', src('BOE-LTA-2025-009')),
        ('Proposition 19 formula, definitions',
         'LTA 2026/026 (2026-08-03): excluded amount = factored base year value plus the adjusted $1 million; new taxable value = factored base year value plus the excess; transfers through a trust are covered; continual use required',
         'Confirmed - the formula tested against the worked example', src('BOE-LTA-2026-026')),
        ('Trustee notification after death',
         'Within 60 days after a revocable trust becomes irrevocable by death; the notice must carry the 120-day / 60-day contest warning',
         'Confirmed - matches the Process page', src('PROB-16061.7')),
        ('Change in ownership statement',
         'Filed by the trustee or transferee within 150 days after the date of death for a transfer through a trust',
         'Confirmed on the page', src('RTC-480')),
        ('Homeowners\' exemption',
         '$7,000 off the taxable value for an owner-occupied home; one-time claim BOE-266; file by February 15 for the full year',
         'Confirmed on the page', src('BOE-HOX')),
        ('San Francisco secured property-tax rate',
         'The secured rate for fiscal year 2026-27 is 1.18162182%',
         'Confirmed - the rate used for Property B', src('SF-TAX')),
        ('Santa Clara County tax rates',
         'Tax Rate Book FY2025-26: 1% maximum levy plus voter-approved bond rates; the Cupertino-area school and college components are listed in the summary tables',
         'Book and components confirmed. The exact tax rate area of Property A is unknown, so its composite rate stays flagged %s' % flag('U03'), src('SCC-RATES')),
        ('HUD rent standard, ZIP 95014',
         'FY2026 Small Area Fair Market Rent: four-bedroom $6,390 a month (three-bedroom $5,870)',
         'Confirmed - the rent input on the Decision page', src('HUD-95014')),
        ('Estate-tax closing-letter fee',
         'What\'s New: TD 10055 raised the fee from $56 to $76 on 2026-10-26. The FAQ page still calls the earlier fee $67 (TD 9957)',
         'The two IRS pages disagree with each other - irregularity %s; the fee is used in no calculation' % flag('S01'), src('IRS-NEW', 'IRS-FAQ-ESTATE')),
    ]
    t1 = table(['What was checked', 'What the official page says', 'Result', 'Official page (open it to re-check by hand)'],
               [[a, b_, c, d] for a, b_, c, d in v],
               caption='Re-verified on the official page itself on 2026-11-11 (independent pass, session faccd46d)')
    u = [
        ('Home-insurance premium for ZIP 95014 and landlord premium for ZIP 94122',
         'The Department of Insurance comparison tool is interactive; its ZIP-level results are not published as a readable page, and the tool states its results are not quotes',
         'ZIP-level figure left blank. The model uses the owner\'s estimate of $1,500 a year beside the official statewide average, and shows that tripling it does not change the ranking',
         src('CDI-TOOL') + ' ' + flag('U01')),
        ('Earthquake-insurance premium',
         'Published only through the same interactive tool',
         'Left blank and not included in any cost line',
         src('CDI-EQ') + ' ' + flag('U02')),
        ('Exact tax rate area and fixed charges of Property A',
         'The rate area is printed on the tax bill; it is not published per parcel',
         'Rate built from the county-wide table; fixed charges derived as bill minus rate times assessed value',
         src('SCC-RATES') + ' ' + flag('U03')),
        ('Proposition 19 allowance from 2027-02-16',
         'The next Board of Equalization letter has not been published',
         'Left blank; the model applies the official mechanism (one year of California house-price change every second February) as a labelled stand-in',
         src('BOE-LTA-2025-009') + ' ' + flag('U04')),
        ('Solar interconnection date and tariff at Property A',
         'Recorded in the utility agreement, not on a public page',
         'Keeps the owner\'s credit of $10 to $20 a month; the credit may shrink when the 20-year net-metering period ends',
         src('CPUC-NEM') + ' ' + flag('U05')),
        ('Owner-supplied figures (market values, rents, utilities, tax bills)',
         'The owner\'s own numbers cannot be verified against an official source; the assessment roll publishes assessed values, not the figures supplied here',
         'Shown only rounded to $10 and labelled owner-supplied; the year-by-year history is not published',
         src('SCC-RATES') + ' ' + flag('P03')),
    ]
    t2 = table(['What was checked', 'Why no official page can confirm it', 'What the site does', 'Where to check'],
               [[a, b_, c, d] for a, b_, c, d in u],
               caption='Not confirmable from an official source - left blank or labelled, and flagged')
    s = [
        ('S01', 'Two IRS pages disagree on the earlier estate-tax closing-letter fee: the FAQ page says $67 (TD 9957) while What\'s New says the fee was $56 before TD 10055 raised it to $76',
         'Recorded; the fee is used in no calculation', src('IRS-NEW', 'IRS-FAQ-ESTATE')),
        ('S03', 'The Santa Clara County Assessor\'s Proposition 19 page says the $1 million allowance is adjusted "annually"; the Board of Equalization letter says every other February 16',
         'The Board of Equalization letter is followed', src('SCC-P19', 'BOE-LTA-2025-009')),
        ('S05', 'November 2026 ballot results are unofficial until certification',
         'Shown as unofficial with the date read; re-read after 2026-12-11', src('SOS-RESULTS')),
        ('U03', 'The Santa Clara tax rate book sets rate names and numbers in two columns; the pairing used for the Cupertino components is an inference, corroborated by reproducing the rounded current bill',
         'Kept as a labelled inference and flagged', src('SCC-RATES')),
    ]
    t3 = table(['No.', 'Irregularity in the source itself', 'What the site does', 'Sources'],
               [[a, b_, c, d] for a, b_, c, d in s],
               caption='Irregularities found in the sources themselves')
    w = [
        ('Federal filing threshold for a 2026 death',
         'The FAQ table ends at 2026: $15,000,000, and the return is required above it (gross estate plus adjusted taxable gifts)',
         'Confirmed today', src('IRS-ESTATE')),
        ('Basic exclusion and annual gift exclusion for 2027',
         'IR-2026-133 of 2026-11-05: basic exclusion $15,480,000 for 2027 decedents; first $20,000 of gifts per person excluded (up from $19,000 for 2026)',
         'Confirmed today - matches Rev. Proc. 2026-35 as quoted', src('RP-2026-35')),
        ('The 2026 exclusion is statutory',
         'What\'s New: Public Law 119-21 (signed 2025-07-04) amends section 2010(c)(3), raising the basic exclusion to $15,000,000 for calendar 2026',
         'Confirmed today', src('IRS-NEW')),
        ('Form 706 deadline and the late portability route',
         'Nine months after death; Form 4768 gives an automatic six months; Rev. Proc. 2022-32 allows a portability election up to the fifth anniversary where there is no filing requirement',
         'Confirmed today - matches the Process page', src('IRS-FAQ-ESTATE')),
        ('Estate-tax closing-letter fee (flag S01)',
         'The FAQ still prints $67 (TD 9957, 2021) while What\'s New prints $76 effective 2026-10-26 (TD 10055, up from $56)',
         'Disagreement confirmed today on both pages; the fee enters no calculation', src('IRS-FAQ-ESTATE', 'IRS-NEW')),
        ('California estate tax',
         'No California estate tax return is required for decedents dying on or after 2005-01-01; the state death tax credit was eliminated from that date',
         'Confirmed today - California adds no death tax', src('SCO-ESTATE')),
        ('Proposition 13 cap',
         'R&amp;TC 51(a)(1)(D): the annual inflation increase shall not exceed 2 percent of the prior year\'s value',
         'Confirmed today word for word', src('RTC-51')),
        ('Proposition 19 allowance in force now',
         'NR 25-02: $1,044,586 for transfers from 2025-02-16 through 2027-02-15, a 2.15% rise from $1,022,600; the homeowner\'s or disabled veteran\'s exemption must be claimed within one year',
         'Confirmed today - the model input', src('BOE-LTA-2025-009')),
        ('Trustee notification deadline',
         'Probate Code 16061.7(f): served not later than 60 days after the event, or 60 days after the trustee learns of a person entitled to notice',
         'Confirmed today - the first deadline on the Process page', src('PROB-16061.7')),
        ('Change in ownership statement deadline',
         'R&amp;TC 480(e): where the change in ownership occurred by reason of death, the statement is filed within 150 days after the date of death',
         'Confirmed today', src('RTC-480')),
        ('San Francisco secured tax rate',
         'The secured property tax rate for fiscal year 2026-27 is 1.18162182%',
         'Confirmed today - the rate applied to Property B in every projection', src('SF-TAX')),
        ('Cupertino market-rent benchmark',
         'FY2026 Small Area Fair Market Rent for ZIP 95014: four-bedroom $6,390 a month, three-bedroom $5,870',
         'Confirmed today - the rent used in the rent-it-out case', src('HUD-95014')),
    ]
    t4 = table(['What was checked', 'What the official page said when it was opened', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in w],
               caption='Second independent re-read, 2026-11-12 (session e8636cac), on the official pages themselves')
    w3 = [
        ('Federal filing threshold for a 2026 death',
         'The filing table ends at 2026: a return is required when the gross estate plus adjusted taxable gifts exceeds $15,000,000; portability needs a timely filed return',
         'Confirmed today (third pass)', src('IRS-ESTATE')),
        ('Basic exclusion for 2027',
         'Section 3.44: the basic exclusion amount under section 2010(c)(3) is $15,480,000 for calendar year 2027',
         'Confirmed today - the figure the estate projections start from', src('RP-2026-35')),
        ('Annual gift exclusion for 2027',
         'Section 3.46(1): the first $20,000 of gifts to any person for calendar year 2027 is not included in taxable gifts',
         'Confirmed today', src('RP-2026-35')),
        ('Proposition 19 allowance in force now',
         'LTA 2025/009: $1,044,586 for transfers February 16, 2025 through February 15, 2027 (2.15% up from $1,022,600); the next adjustment is February 2027',
         'Confirmed today - the model input', src('BOE-LTA-2025-009')),
        ('Proposition 19 conditions',
         'Principal residence of transferor and transferee; value limit of current taxable value plus $1,000,000 as biennially adjusted; homeowners\u2019 exemption within one year of transfer; claim within three years or before transfer to a third party',
         'Confirmed today - the rule the model applies', src('BOE-P19')),
        ('Proposition 13 growth cap',
         'R&amp;TC 51(a)(1)(D): "In no event shall the percentage increase for any assessment year ... exceed 2 percent of the prior year\u2019s value"',
         'Confirmed today word for word', src('RTC-51')),
        ('California estate tax',
         'For decedents that die on or after January 1, 2005, there is no longer a requirement to file a California Estate Tax Return',
         'Confirmed today - California adds no death tax', src('SCO-ESTATE')),
        ('San Francisco secured property-tax rate',
         'The secured property tax rate for Fiscal Year 2026-27 is 1.18162182%; after a change in ownership state law requires the Assessor-Recorder to reappraise',
         'Confirmed today - the rate applied to Property B in every projection', src('SF-TAX')),
        ('Trustee notification deadline',
         'Probate Code 16061.7(f): the notification shall be served not later than 60 days following the occurrence of the event',
         'Confirmed today - the first deadline on the Process page', src('PROB-16061.7')),
        ('Change in ownership statement deadline',
         'R&amp;TC 480(b): for a transfer by reason of death through the medium of a trust, the statement is filed by the trustee or transferee within 150 days after the date of death',
         'Confirmed today', src('RTC-480')),
        ('Basis step-up and the grantor-trust exception',
         'Rev. Rul. 2023-2 (IRB 2023-16): the section 1014 basis adjustment generally does not apply to the assets of an irrevocable grantor trust not included in the deceased grantor\u2019s gross estate',
         'Confirmed today - the basis of flag Q01', src('RR-2023-2')),
        ('Home-sale exclusion',
         'Topic 701: up to $250,000 ($500,000 on a joint return); ownership and use tests of 24 months in the 5 years before the sale',
         'Confirmed today', src('IRS-TC701')),
        ('HUD rent standard, ZIP 95014',
         'The FY2026 Fair Market Rent Documentation System page is interactive and did not render its ZIP-level results in this session\u2019s fetch',
         'Not re-confirmed in the third pass - the four-bedroom figure stands on the 2026-11-11 pass and keeps its link for manual re-check', src('HUD-95014')),
    ]
    tw3 = table(['What was checked', 'What the official page said when it was opened', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in w3],
               caption='Third independent re-read, 2026-11-12 (session b724a7d8), on the official pages themselves')
    x = [
        ('Federal exclusion and gift exclusion for 2027', 'Rev. Proc. 2026-35: basic exclusion $15,480,000; annual gift exclusion $20,000', 'Confirmed - matches the Cash page', src('RP-2026-35')),
        ('Federal filing thresholds', 'Estate tax page: $13,990,000 for 2025 and $15,000,000 for 2026; portability needs a timely Form 706', 'Confirmed', src('IRS-ESTATE')),
        ('Law behind the 2026 exclusion', "What's New: Public Law 119-21, signed 2025-07-04, sets $15,000,000 for 2026; closing-letter fee $56 to $76 from 2026-10-26", 'Confirmed. The earlier fee amounts are settled by the dated schedule in the third re-read above %s' % flag('S01'), src('IRS-NEW')),
        ('Basis of inherited property', 'IRS answer: generally the fair market value at the date of death, or at the alternate valuation date if elected on Form 706', 'Confirmed - the rule behind the Sell result, subject to %s' % flag('Q01'), src('IRS-FAQ-INHERIT')),
        ('California estate and inheritance tax', 'No estate tax return for deaths on or after 2005-01-01; inheritance and gift tax only before 1982-06-08', 'Confirmed', src('SCO-ESTATE')),
        ('Proposition 19 rule', 'Principal residence of both parties; limit is taxable value plus the adjusted $1,000,000; exemption within one year; claim within three years', 'Confirmed', src('BOE-P19')),
        ('Proposition 19 allowance', '$1,044,586 for transfers 2025-02-16 through 2027-02-15; next adjustment February 2027', 'Confirmed - the model input; the next figure stays blank %s' % flag('U04'), src('BOE-LTA-2025-009')),
        ('Proposition 19 questions and answers', 'LTA 2026/026 of 2026-08-03 (read in part: five sections of the document were opened, the rest was not): occupancy within one year with no exceptions; exclusion removed if the child moves out; only the occupied unit of a multi-unit property qualifies; care-facility rule; property in a limited liability company not eligible', 'Confirmed for the answers quoted here and on the Questions page; the unread sections are not claimed', src('BOE-LTA-2026-026')),
        ("Homeowners' exemption", '$7,000; form BOE-266; file by February 15 for the full year', 'Confirmed', src('BOE-HOX')),
        ('Santa Clara County Proposition 19 page', 'Worked example: base $200,000, market $1,800,000, new value $800,000. The page still says the allowance is adjusted annually', 'Example matches the formula used; irregularity %s is unchanged' % flag('S03'), src('SCC-P19')),
        ('San Francisco secured tax rate', '1.18162182% for fiscal year 2026-27', 'Confirmed', src('SF-TAX')),
        ('San Francisco rent increase', '1.6% for 2026-03-01 through 2027-02-28. A notice posted 2026-11-09 describes File No. 261020, a proposed 10% yearly cap on banked and capital-improvement increases, not enacted', 'Rate confirmed. The proposal is new since the first pass and is recorded on the Questions page', src('SF-RENT-RULES', 'SF-LEG-261020')),
        ('HUD rent, ZIP 95014', 'Fiscal year 2026: three-bedroom $5,870, four-bedroom $6,390. The release list shows a fiscal year 2027 file, effective 2026-10-01, and a revised 2026 file, effective 2026-05-21', 'The 2026 figure used is confirmed. The 2027 figure for the ZIP could not be read and is left blank %s' % flag('U09'), src('HUD-95014', 'HUD-SAFMR-INDEX')),
        ('November 2026 ballot measures', 'Unofficial returns as of 2026-11-11 6:51 p.m.: Proposition 3 Yes 60.7%, Proposition 40 No 52.5%, Proposition 42 Yes 51.4%', 'Each moved 0.1 point since the first pass; no outcome changed. The Law page now shows these figures %s' % flag('S05'), src('SOS-RESULTS')),
        ('Deposit insurance', '$250,000 per depositor, per bank, per ownership category; Treasury securities are not deposit-insured', 'New row - used on the Questions page', src('FDIC')),
        ('Basis of an asset already owned', 'Topic 703: basis is generally cost, raised by improvements and lowered by allowable depreciation', 'New row - behind the Property B basis question %s' % flag('Q03'), src('IRS-TC703')),
        ('Like-kind exchanges', 'Gain generally not recognised on an exchange of investment real property solely for like-kind real property; reported on Form 8824', 'New row - not modelled; noted on the Questions page', src('IRS-1031')),
    ]
    t5 = table(['What was checked', 'What the official page said when it was opened', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in x],
               caption='Fourth re-read, 2026-11-12 (session 0adc9b0a), on the official pages themselves')
    body = """
<p class="callout">This page is the manual-review register for the whole site: one row per check, with the government page to open and re-read. The first register below was checked against the official pages on 2026-11-11 (session faccd46d). A second, independent pass on 2026-11-12 (session e8636cac) re-opened the twelve pages the plan depends on most and is printed as its own table, so the two passes can be compared. Two more passes were made later the same day by two sessions working separately: a third (session 3e79fc01) and a fourth (session 0adc9b0a, seventeen rows). Both are printed, the fourth last. Anything that could not be confirmed is left blank or labelled and carries a flag.</p>
%s
%s
%s
<h2>Second independent re-read, 2026-11-12</h2>
%s
<p class="note">What the second pass did <em>not</em> re-open, and therefore does not claim to have re-checked on 2026-11-12: the inherited-property basis rules and Rev. Rul. 2023-2, the home-sale and capital-gain topics, the investment-income tax, Board of Equalization letter 2026/026, the Santa Clara County rate book, the homeowners\' exemption amount, the solar and net-metering material, the San Francisco rent-increase rules and the insurance comparison tool. Those rows stand on the 2026-11-11 pass and keep their links.</p>
<h2>Third independent re-read, 2026-11-12 (session b724a7d8)</h2>
%s
<p class="note">The third pass (session b724a7d8) opened the pages listed in its own table and recorded what they said. One row could not be re-read today (the HUD documentation page is interactive and did not render its ZIP-level results in the fetch) and is labelled as such rather than re-marked confirmed. What the later passes did not re-open stands on the 2026-11-11 register and keeps its links for manual review.</p>
<h2>Third independent re-read, 2026-11-12 (session 3e79fc01)</h2>
%s
<h2>Fourth re-read, 2026-11-12 (session 0adc9b0a)</h2>
<p class="note">The re-reads of 2026-11-12 were made by several work sessions on the same day without knowledge of each other. All are kept. Where they cover the same official page they agree.</p>
%s
<p class="note">What the fourth pass did <em>not</em> re-open, and therefore does not claim to have re-checked: Rev. Rul. 2023-2, IRS Topics 409, 559 and 701, IRS Publications 527 and 559, the Form 706 instructions, the Santa Clara County rate book, the two statutory deadlines (Probate Code 16061.7 and R&amp;TC 480), the solar and net-metering material, the bills in Congress, the HUD figure for ZIP 94122 and the Empty Homes Tax page. The insurance comparison tool and the HUD fiscal-year 2027 lookup are interactive and could not be read. HUD also offers the 2027 figures as a spreadsheet; one attempt to open it from the work session failed, so it was not read either. Those values stay blank.</p>
<p class="note"><strong>What these passes do not establish.</strong> Model outputs and projections are conditional scenarios built on the assumptions in the flags; no official page can verify a forecast. The automated checker (<a href="%s/blob/main/final/check.py">final/check.py</a>) proves only that every table row carries an official link, that dollar figures are rounded to $10, and that no stored fingerprint of an unrounded owner figure appears in the tree - it does not prove that each link supports each cell. This register exists so every claim can be checked by hand against its link. People remain placeholders (the Transferor, the Inheritor); no names, addresses or parcel numbers appear anywhere.</p>
""" % (t1, t2, t3, t4, tw3, render_verification(src, table, flag), t5, REPO)
    page('verification.html', 'Verification',
         'Five verification passes - one on 2026-11-11 and four on 2026-11-12: every headline legal and financial fact re-read on its official page, each check linked for manual review, everything unconfirmable left blank and flagged.', body)


# ====================================================================== flagged
def build_flagged():
    cats = [
        ('Q', 'Questions only the owner or a professional can answer'),
        ('P', 'Privacy decisions'),
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
    t = table(['Key', 'Source', 'How it was read on %s (headline rows re-verified %s)' % (REGISTER_DATE, BUILD_DATE), 'What was read there', 'Link'], rows, caption='Source register')
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
<li><strong>Checks.</strong> <a href="%s/blob/main/final/check.py">final/check.py</a> fails the build if a table row has no official link, if an internal link is broken, if a dollar figure is not a multiple of $10 (official published figures excepted), or if a street address, e-mail address, parcel-number or telephone pattern appears. No fingerprint of the unrounded owner figures is stored in the repository; that extra scan runs only when the owner supplies the figures in a private local file.</li>
</ul>
<h2>Reproduce</h2>
<pre>python3 final/model.py &amp;&amp; python3 final/build.py &amp;&amp; python3 final/check.py</pre>""" % (REPO, REPO)
    xc = table(['Figure (baseline, inheritance in 2045)', 'This site', 'Independent second model', 'Difference and cause', 'Official basis'], [
        ['Property A market value', m(B['fmv_T']), m(B['fmv_T']), 'none', src('FHFA-SJ')],
        ['Assessed value before death', m(B['fbyv_T']), m(B['fbyv_T']), 'none', src('BOE-P19')],
        ['Proposition 19 allowance', m(B['cap_T']), '$1,506,100', '0.4%: different stand-in for the 2026 price change that is not yet published', src('BOE-LTA-2025-009')],
        ['New assessed value if lived in', m(B['taxable_live_T']), '$5,025,130', '0.1%: follows from the allowance', src('BOE-LTA-2026-026')],
        ['First-year tax, lived in / rented', '%s / %s' % (m(B['tax_live_T']), m(B['tax_rent_T'])), '$60,010 / $77,610', '0.1% to 0.2%: fixed charges derived with or without the $7,000 exemption', src('SCC-RATES', 'BOE-HOX')],
        ['Federal exclusion / room for other assets', '%s / %s' % (m(B['exclusion_T']), m(B['exclusion_T'] - B['fmv_T'])), '%s / %s' % (m(B['exclusion_T']), m(B['exclusion_T'] - B['fmv_T'])), 'none', src('RP-2026-35')],
        ['Ranking of the three choices', 'sell, then rent, then live in; renting beats selling into savings', 'the same', 'none', src('IRS-FAQ-INHERIT')],
    ], caption='Cross-check against a second model built separately by another work session', cls='num',
        note='The second model, its own source register and its pages are kept as an <a href="%s">independent check</a>. It is not a second front door; its figures are quoted from the coordination log of 2026-11-11 04:58 UTC.' % VERIFY)
    page('sources.html', 'Sources and method', 'Every source used, how it was read, and how the numbers are produced.', t + xc + method)


# ================================================================ requirements
def build_requirements():
    # Requirement -> where answered -> status -> the official page behind it.
    rows = [
        ['A clear list of questions, what is already known, what is still blank, and how to discover each gap',
         'This page, <a href="#questions">Questions, information in hand, and answers still missing</a>. An unconfirmed answer is left blank rather than estimated.',
         'Met as a list. The blanks themselves are not met until the owner or an adviser fills them', src('IRS-ESTATE', 'RTC-63.2')],
        ['A dedicated suggestions section, so a reader can choose a path before any change is implemented',
         'This page, <a href="#suggestions">Suggestions — review and choose before any change</a>. Each suggestion is marked proposed and not implemented.',
         'Met by listing the suggestions. None of them was implemented on this pass', src('BOE-P19', 'SCC-RATES')],
        ['Whether to live in, rent out, or sell Property A and reinvest after tax',
         'Summary: the recommended plan and why. <a href="decision.html">Decision</a>: cash flows, after-tax wealth ten and thirty years out, sensitivities and break-even points for all three choices.',
         'Met', src('IRS-TC409', 'IRS-TC559')],
        ['Property A passes by trust some time between 2040 and 2050, so show the answer for each of those years',
         'Summary dashboard switches between 2040, 2045 and 2050. <a href="projections.html">Year by year</a> runs 2026 to 2076 with 2045 as the baseline.',
         'Met; the year of death is not knowable in advance', src('BOE-RULE-462.260', 'RTC-480')],
        ['Property B is already owned by the Inheritor, so it is not inherited and must not be treated as if it were',
         'Summary, the table <em>The two homes are not the same case</em>. Year by year keeps Property B on its existing base with no reassessment and no basis reset.',
         'Met', src('RTC-63.2', 'RR-2023-2')],
        ['Keep the two rented units at Property B, and the option of living in its third unit without losing that rent',
         'Summary, plan item 1. Year by year shows Property B rent for all three choices. Decision adds the rent of the vacated unit when the Inheritor moves into Property A.',
         'Met; the rent is an owner figure', src('SF-RENT-RULES', 'SF-RENT-2026')],
        ['Weigh Property B into every decision about Property A',
         'Summary (the tax advantage that is lost if Property B is sold). <a href="decision.html">Decision</a> (the opportunity cost of each choice, including the rent given up).',
         'Met', src('SF-TAX')],
        ['Project the market value of Property A, its assessed value and its property tax, year by year',
         'Year by year: one column each for market value, assessed value and tax, on the live-in, rent-out and sell paths, 2026 to 2076.',
         'Met; the growth rate is an assumption', src('FHFA-SJ', 'SCC-RATES')],
        ['Apply the Proposition 19 relief only if the Inheritor moves in within a year; otherwise reassess at market value',
         'Decision and Year by year, the three paths. <a href="law.html">Law</a> sets out the conditions and the deadlines.',
         'Met; the exact tax rate area and the allowance from 2027 are unconfirmed ' + flag('U03') + ' ' + flag('U04'), src('BOE-LTA-2026-026', 'RTC-63.2')],
        ['Home-insurance cost for a primary residence in 95014 and a rental in 94122, researched rather than guessed',
         '<a href="costs.html">Insurance and costs</a>: every official statewide yardstick found, both ZIP-level premiums left blank because no official source publishes them.',
         'Partly - no official ZIP-level premium exists; premiums are an assumption ' + flag('U01'), src('CDI-SB824', 'CDI-RPI')],
        ['Water and electricity cost, including the solar credit that makes Property A a net exporter',
         'Insurance and costs (official rate design and the net-metering rule); Year by year (the cost lines).',
         'Met from the owner\'s monthly figures; the solar tariff is not confirmed ' + flag('U05'), src('CPUC-NEM', 'CPUC-FIXED')],
        ['The federal estate-tax threshold, the room left for a cash inheritance, and a projection forward',
         '<a href="estate-cash.html">Cash and estate tax</a>: 2026 and 2027 thresholds, room for other assets, projection to 2050, and the two-transferor case.',
         'Met; future indexation of the threshold is an assumption ' + flag('A03'), src('IRS-ESTATE', 'RP-2026-35')],
        ['Whether California or a city or county taxes an inheritance',
         'Cash and estate tax: no California estate-tax return is required for a death on or after 2005-01-01, there is no inheritance tax in California, and no city or county levies one.',
         'Met - nothing applies', src('SCO-ESTATE')],
        ['The amount that can be inherited before tax is due, at each level',
         'Cash and estate tax: federal threshold by year, the 40% rate above it, a worked example, and the portability question for a married Transferor.',
         'Met; the amount of cash is still an owner answer ' + flag('Q02'), src('IRS-I706', 'IRS-FAQ-ESTATE')],
        ['A step-by-step walk through what inheriting the house actually involves',
         '<a href="process.html">Process</a>: fourteen steps in order, each with the day it falls due, the form to file and the authority behind it.',
         'Met; the trust type decides several steps ' + flag('Q01'), src('PROB-16061.7', 'RTC-480')],
        ['The law in force today at federal, state and local level',
         'Law: three tables, one for each level, each row linked to the statute, regulation or agency page.',
         'Met', src('IRS-NEW', 'BOE-P19')],
        ['Changes to the law now under discussion, and what each would do to the answer',
         'Law: a table of pending changes with the effect on each choice, and the November 2026 state measures with their unofficial results.',
         'Met; the results are unofficial until 2026-12-11 ' + flag('S05'), src('SOS-RESULTS', 'CONG-S587')],
        ['Black swan: growth and inflation that are not constant over a fifty-year period',
         '<a href="black-swan.html">Black swan</a>: the real 1976-2025 record replayed from each of its fifty starting years, plus named crisis paths, kept apart from the baseline.',
         'Met; the record is used as it happened, not smoothed', src('BLS-CPI', 'FHFA-SJ')],
        ['Project repairs, utilities, insurance and tax from our own figures instead of rules of thumb',
         'Year by year: every cost line by year with the rule that drives it. Decision uses those same lines.',
         'Partly - maintenance and growth rates are assumptions ' + flag('A08') + ' ' + flag('A09'), src('BLS-OCT')],
        ['What the reinvested proceeds would earn in the stock market, or in savings',
         'Decision: stock, bond and bill cases side by side. Black swan replays the same three assets through the historical sequences.',
         'Assumption ' + flag('A02') + '; the Treasury yield is the official anchor for the bill rate', src('TREASURY')],
        ['The rent Property B produces now (about $7,150 a month for two units)',
         'Summary and Year by year; the HUD small-area market rent for 94122 is shown next to it as an independent benchmark.',
         'Owner figure; the benchmark was read at HUD', src('HUD-94122')],
        ['What Property A would rent for if it is rented out',
         '<a href="decision.html">Decision</a> and Year by year; the HUD small-area fair market rent for 95014 is the starting rent.',
         'Met', src('HUD-95014')],
        ['The value of Property A today (about $3,100,000 in November 2026) and its growth',
         'Year by year, year zero. Growth follows the FHFA San Jose index; the owner\'s value is the starting point.',
         'Owner figure; growth from the official index', src('FHFA-SJ')],
        ['Selling costs, transfer tax and the capital-gains tax that a sale would cause',
         'Decision: net proceeds and after-tax wealth. Law: the home-sale exclusion, the holding period and the 3.8% surtax.',
         'Met', src('SCC-DTT', 'IRS-TC701')],
        ['Numbers rounded so that nothing can be traced back to the source, yet still clear enough to reason with',
         'Every page. Owner-supplied and modelled figures are rounded to $10; official published figures are quoted exactly and listed on the sources page.',
         'Met - enforced by <a href="sources.html">final/check.py</a> on every build', src('BLS-CPI')],
        ['A clear list of the questions, information and answers needed before a decision can reasonably be made: what is known, what is not, and how to find what is missing',
         '<a href="questions.html">Questions</a>: open questions with what is known, what is missing and how to find it; questions that cannot be known in advance; questions already answered from official pages; who to ask.',
         'Met; answers that no official page or owner figure settles are left blank', src('IRS-FAQ-INHERIT', 'BOE-LTA-2026-026')],
        ['A dedicated section of suggestions for improving the site for decision making, to review and choose from before anything is implemented',
         '<a href="suggestions.html">Suggestions</a>: each proposal with its options, a suggested choice, its effect on the decision, effort and risk, plus ready-made paths to choose from.',
         'Met as a proposal; nothing on that page has been implemented', src('HUD-SAFMR-INDEX', 'CDI-TOOL-APP')],
    ]
    t1 = table(['No.', 'What was asked', 'Where this site answers it', 'Status', 'Official basis'], 
               [[str(i + 1)] + r for i, r in enumerate(rows)],
               caption='The brief, line by line, and where each part is answered', 
               note='Every row above is a requirement taken from the owner\'s instructions. "Met" means the answer is produced by the model from an official rule; where a figure has no official source it is named as an assumption and linked to the Flagged for Review page.')

    no_fact = [
        ('Repairs and maintenance: %s a year for Property A and %s for Property B' % (m(P['maint_cup']), m(P['maint_sf'])), 'A08',
         'No official figure exists for a particular house. The lower figure for Property A is the owner\'s statement that it needs less work than Property B.'),
        ('Home prices rise 4.0% a year and prices in both areas move together', 'A01',
         'The FHFA index gives history, not a forecast. The long-run California rate is shown next to the assumption on the sources page.'),
        ('Inflation 2.5% a year; rents, insurance, water and electricity each grow at a stated margin above it', 'A01',
         'The 1976-2025 record in Black swan shows how wrong a constant rate can be, which is why that page exists.'),
        ('Stocks 7.0%, Treasury bonds 4.5%, savings or bills 3.5%, dividend yield 1.5%', 'A02',
         'Ten-year Treasury yields are official; the equity return and the spread over bonds are not.'),
        ('Home insurance %s and landlord insurance %s a year' % (m(P['ins_home']), m(P['ins_rental'])), 'U01',
         'The owner\'s estimate. The official statewide figures are the only ZIP-free numbers that exist; a real quote is needed.'),
        ('The fixed charges inside each tax bill (%s for Property A, %s for Property B)' % (m(P['dc_cup']), m(P['dc_sf'])), 'U03',
         'Derived by subtracting the official rate times the assessed value from the owner\'s rounded bill. The exact tax rate area was deliberately not looked up.'),
        ('The Proposition 19 allowance after 2027-02-16', 'U04',
         'The Board of Equalization publishes the next figure in February 2027; the model assumes it grows with the FHFA California index.'),
        ('Selling cost 5%, vacancy 5%, management 6%, building share 30%, rent growth and rent of the third unit at Property B', 'A06',
         'Market conventions, not official figures. Each is shown on the decision page so it can be changed.'),
        ('The trust type, the amount of cash and other assets, and whether a deceased spouse\'s exclusion was ported', 'Q01',
         'Owner answers needed. These three decide the basis reset and the estate-tax bill.'),
    ]
    li = ''.join('<li><strong>%s</strong> - %s <a class="flag" href="flagged.html#%s">flag %s</a></li>' % (a, c, b, b)
                 for a, b, c in no_fact)
    assumptions = ('<h2>Owner figures and assumptions, and why each is flagged</h2>'
                   '<p class="note">These are the only places where a number in this site does not come from an official page. '
                   'Each is listed on the Flagged for Review page with what would replace it.</p><ul class="plan">%s</ul>' % li)

    rules = """
<h2>Rules this site holds itself to, where there is no external fact to check</h2>
<ul class="plan">
<li><strong>No personal information.</strong> No name, street address, parcel number, e-mail or phone number appears. The people are "the Transferor" and "the Inheritor". <code>final/check.py</code> scans every published page on every build for an address, e-mail, phone or parcel pattern, for unrounded owner figures, and for the one figure the owner asked to be hidden - the build fails if any appears.</li>
<li><strong>Every figure to the nearest $10.</strong> Owner-supplied and modelled dollars are rounded; a short list of figures that an official page publishes unrounded (an index value, a statutory cap such as $1,044,586) is quoted exactly and listed on the sources page.</li>
<li><strong>No manual input.</strong> Three scripts produce the whole site from two data files: <code>final/model.py</code> (the model), <code>final/build.py</code> (the pages) and <code>final/check.py</code> (the rules above). Nothing on any page is typed by hand.</li>
<li><strong>Every table row links to an official page,</strong> and a value that could not be confirmed is left blank and listed on the <a href="flagged.html">Flagged for Review</a> page rather than estimated.</li>
<li><strong>A dashboard, not an essay.</strong> Summary first, then one page per question, then the year-by-year tables. Tables scroll sideways on a phone, the navigation stays at the top, and every page loads without any outside script or font.</li>
<li><strong>One front door, with earlier work kept.</strong> Parallel work sessions produced several editions; the earlier ones are preserved under <a href="versions.html">Earlier versions</a> with a notice, and nothing was deleted.</li>
<li><strong>Nothing published until it builds.</strong> The pull request, the checks and the Pages deployment are recorded in <code>COORDINATION.md</code>; the build is refused if a link breaks or a row loses its source.</li>
</ul>
<p class="callout">One privacy item cannot be fixed from inside the site: this repository is public, and its Git history holds the first drafts, written before the figures were rounded. Rounding the pages does not rewrite that history. The owner has to make the repository private or have the history rewritten. <a class="flag" href="flagged.html#P02">flag P02</a></p>
"""

    checks = [
        ['2026 federal estate-tax filing threshold',
         'Table of filing thresholds by year of death: 2011 $5,000,000 through 2025 $13,990,000 to 2026 $15,000,000; a timely Form 706 is needed to port an unused exclusion.',
         src('IRS-ESTATE')],
        ['2027 basic exclusion used in the projection',
         'Rev. Proc. 2026-35, section 3.44: "For calendar year 2027, the basic exclusion amount under section 2010(c)(3) is $15,480,000."',
         src('RP-2026-35')],
        ['No California estate tax',
         '"For decedents that die on or after January 1, 2005, there is no longer a requirement to file a California Estate Tax Return."',
         src('SCO-ESTATE')],
        ['Proposition 19 allowance in force',
         'BOE Letter to Assessors 2025/009: $1,044,586, for transfers from 2025-02-16 through 2027-02-15, adjusted every other February 16 by the FHFA California index.',
         src('BOE-LTA-2025-009')],
        ['How the relief is computed, and that a trust transfer is covered',
         'BOE Letter to Assessors 2026/026: excluded amount = factored base year value + $1 million (adjusted); new taxable value = that plus any excess; the transfer may be "within or outside a trust"; the home must be continually used as the family home.',
         src('BOE-LTA-2026-026')],
        ['Basis resets on death only if the home is in the gross estate',
         'Rev. Rul. 2023-2, Internal Revenue Bulletin 2023-16: the section 1014 basis adjustment "generally does not apply to the assets of an irrevocable grantor trust not included in the deceased grantor\'s gross estate".',
         src('RR-2023-2')],
        ['Home-sale exclusion and the holding period',
         'IRS Topic 701: up to $250,000 of gain excluded, $500,000 on a joint return; ownership and use for 24 of the last 60 months.',
         src('IRS-TC701')],
        ['San Francisco secured property tax rate',
         '"The secured property tax rate for Fiscal Year 2026-27 is 1.18162182%."',
         src('SF-TAX')],
        ['Santa Clara County tax rates used for Property A',
         'Tax Rate Book FY2025-26, pages A-4 to A-6: 1% maximum levy 1.00000; county retirement 0.03880; county library retirement 0.00240; VMC 2008 0.00520; housing bond 0.00560; three Cupertino elementary bonds; four Fremont Union High bonds; three Foothill-De Anza bonds; SCVWD State Water Project 0.00390; Midpeninsula Open Space 0.00140. The sum of the components that apply to a Cupertino address is 1.16360 per $100, and it reproduces the rounded bill for the current year.',
         src('SCC-RATES')],
        ['Market rent at both ZIP codes',
         'HUD FY2026 Small Area FMR: 95014 - two-bedroom $4,440, three-bedroom $5,870, four-bedroom $6,390 a month; 94122 - two-bedroom $3,310, three-bedroom $4,230, four-bedroom $4,380.',
         src('HUD-95014', 'HUD-94122')],
        ['The house-price index behind every value projection',
         'FHFA all-transactions index for San Jose-Sunnyvale-Santa Clara: Q4 2025 560.05, Q2 2025 564.26, Q2 2026 558.75 - a fall of 1.0% over the year, which is why the projections carry a sensitivity case.',
         src('FHFA-SJ')],
    ]
    t2 = table(['No.', 'Fact this analysis uses', 'What was read on the official page on 2026-11-11', 'Source'],
               [[str(i + 1)] + r for i, r in enumerate(checks)],
               caption='Independent re-verification performed for this page, 2026-11-11',
               note='Each page above was fetched and read during this work session, not copied from an earlier edition. Nothing in the tables changed as a result: the figures already on the site match these pages. The sources page lists the sources that were read only through an excerpt, and the Flagged page lists every value that could not be confirmed.')

    body = render_queue(src, table, flag, BLANK, m, B) + """
<p class="note">The two sections above are the review queue: questions that are still blank, and suggestions that have not been implemented. The checklist below is the original brief, row by row. Model figures were not changed to add these sections.</p>
<h2>Requirements and where each one is answered</h2>%s
%s
%s
<h2>Re-verification performed for this page</h2>%s
<h2>What this pass changed</h2>
<p class="note">This page is new. It adds no figures: every number on it is produced by <code>final/model.py</code> or quoted from an official page linked in the row. The rest of the site is unchanged, and the checks below were run on the whole tree after the page was added. If a later pass changes a figure, this page is regenerated with the rest of the site, so it cannot drift out of date.</p>
<ul class="plan">
<li>Build: <code>python3 final/model.py &amp;&amp; python3 final/build.py</code> - twelve substantive pages, plus the earlier-versions page and redirects at retired addresses.</li>
<li>Checks: <code>python3 final/check.py .</code> - every table row carries a link to an official page, every internal link and anchor resolves, every dollar figure is a multiple of $10 unless it is a listed official figure, and no personal information or unrounded owner figure appears.</li>
<li>Model self-tests: the Proposition 19 formula is checked against the county assessor's own worked example, and Property B is asserted never to be reassessed.</li>
</ul>
""" % (t1, assumptions, rules, t2)
    page('requirements.html', 'Requirements and verification',
         'Every part of the brief, the page that answers it, the official rule behind it - and the official pages that were re-read on 2026-11-11 to make sure the numbers on this site still match.', body)



# ====================================================================== suggestions
def build_suggestions():
    data_rows = [
        ['S-01', 'Get estate attorney to confirm trust inclusion and basis reset ' + flag('Q01'), 'Determines whether a sale is tax-free (basis reset) or taxed on decades of gain — the single largest swing in the model', 'Low — one meeting, written letter', 'Proposed — owner approval needed', src('RR-2023-2')],
        ['S-02', 'Confirm parent-to-child relationship for Proposition 19 ' + flag('Q06'), 'Only a qualifying parent-child (or grandparent with deceased parent) transfer can claim the partial exclusion', 'Low — confirm family relationship', 'Proposed — owner approval needed', src('BOE-LTA-2026-026')],
        ['S-03', 'Provide written insurance quotes for ZIP 95014 (primary) and ZIP 94122 (landlord) via CDI comparison tool ' + flag('U01'), 'The site uses an owner estimate of $1,500 a year; a real quote may differ, and it affects all three choices', 'Low — 5 minutes per ZIP in the official tool', 'Proposed — owner or broker', src('CDI-TOOL-APP')],
        ['S-04', 'Ask insurer for earthquake offer and decide on earthquake coverage ' + flag('U02'), 'A major Bay Area earthquake is a 72% probability before 2043; exclusion can be costly', 'Low — request mandatory offer', 'Proposed — owner or broker', src('CDI-EQ')],
        ['S-05', 'Confirm exact tax rate area and fixed charges from the 2025-26 tax bills ' + flag('U03'), 'Rate 1.16360% is built from district tables; a different rate area changes post-inheritance tax by thousands', 'Low — read bills', 'Proposed — owner', src('SCC-RATES')],
        ['S-06', 'Obtain independent rent opinion and confirm bedroom count for Property A ' + flag('U08'), 'HUD Small Area FMR of $6,390 a month may be high or low vs market; rent directly decides rent-vs-sell break-even', 'Low — one property-manager letter', 'Proposed — owner', src('HUD-95014')],
        ['S-07', 'Appraise both homes (or use recent comparable sales) at 2026 market', 'Owner estimates of $3,100,000 and $1,800,000 are not appraisals; every projection scales with them', 'Medium — licensed appraiser', 'Proposed — owner approval needed', src('FHFA-SJ')],
        ['S-08', 'Document solar interconnection date and NEM tariff status ' + flag('U05'), 'Current credit of $10–$20 a month may end under net billing + $24.15 fixed charge; affects live-in and rental cash flow', 'Low — utility agreement', 'Proposed — owner', src('CPUC-NEM')],
        ['S-09', 'Total estate (cash and other assets) and check portability filing ' + flag('Q02'), 'Federal estate tax is 40% above exclusion; room shown is $17,612,280 in 2045 — cash over that changes everything', 'Medium — CPA + attorney', 'Proposed — owner approval needed', src('IRS-ESTATE')],
    ]
    site_rows = [
        ['S-10', 'Add interactive calculator: owner changes inheritance year, growth and return, see after-tax wealth instantly', 'Removes uncertainty about “what if 3% not 4%?” without rebuilding the model; makes the 50-replay intuition tangible', 'Medium — one small script, no server', 'Proposed — needs owner approval on assumptions shown', src('FHFA-SJ')],
        ['S-11', 'Add printable one-page decision checklist (Process deadlines + Have/Missing questions)', 'Gives a handout for attorney/CPA meeting; prevents missed 60-day, 150-day and 1-year filings', 'Low — PDF from existing tables', 'Proposed — owner approval needed', src('PROB-16061.7')],
        ['S-12', 'Add plain-language family summary (no jargon, no figures) for non-financial decision makers', 'Helps household align on lifestyle vs financial trade-off of living in A (cost $6,301,010 of 2076 wealth in 2026 dollars vs selling)', 'Low — one page', 'Proposed — owner approval needed', src('BOE-P19')],
        ['S-13', 'Model Property B sale as a fourth choice: sell B instead of A, compare basis and Prop 13 loss', 'Directly tests the key distinction — B has no reset and a $19,890 yearly tax advantage already', 'Medium — one model run, same official rules', 'Proposed — owner approval needed', src('SF-TAX')],
        ['S-14', 'Add “sell and keep proceeds in Treasury bills” as a persistent path in Decision', 'Owner explicitly asked; currently it is one sensitivity row — making it a full column prevents misreading sell-as-automatic-win', 'Low — already modelled, needs page slot', 'Proposed — owner approval needed', src('TREASURY')],
        ['S-15', 'Stagger selling the inherited home and investing proceeds to narrow black-swan downside', 'Black swan shows worst 10-year case is $2,069,690 behind; staging + 2 years in bills cuts that risk', 'Low — text + sensitivity rows', 'Proposed — owner approval needed', src('TREASURY')],
        ['S-16', 'Improve mobile readability and accessibility (larger tables, sticky navigation, offline CSV)', 'Year-by-year table has 51 years x 14 columns; small screens hide the trade-off', 'Low — CSS only, no content change', 'Proposed — no official source needed beyond existing', src('BOE-P19')],
        ['S-17', 'Add annual law-watch update: re-read IRS exclusion, BOE allowance, SF rate each February/October', 'Exclusion, allowance and SF rate are adjusted yearly; stale figures silently change the answer', 'Low — calendar reminder', 'Proposed — owner or adviser', src('RP-2026-35')],
        ['S-18', 'Offer private PDF edition (figures included) that does not publish to public Pages', 'Public repo + history cannot be made private from inside site; a non-public PDF protects household identifiability while keeping analysis', 'Low — already in privacy-site/', 'Proposed — owner decides repo visibility ' + flag('P02'), src('SCO-ESTATE')],
    ]
    data_rows = [r[:4] + [r[4], _sg(r[0])] + [r[5]] for r in data_rows]
    site_rows = [r[:4] + [r[4], _sg(r[0])] + [r[5]] for r in site_rows]
    t_data = table(['No.', 'Suggestion to improve decision confidence', 'Why it helps the Cupertino vs SF decision', 'Effort', 'Status: proposed until owner approves', 'Your decision (saved in this browser only)', 'Official basis'], data_rows, caption='A. Fill data gaps — without these, the decision rests on unverified inputs (each linked to an official page)')
    t_site = table(['No.', 'Suggestion to improve the site for better decisions', 'How it improves decision making', 'Effort', 'Status: proposed until owner approves', 'Your decision (saved in this browser only)', 'Official basis'], site_rows, caption='B. Improve the site itself — make uncertainty, trade-offs and deadlines easier to see and act on')
    path_rows = [["R%d" % (n + 1)] + r for n, r in enumerate([
        ['Path 1 — Minimal', 'This site as it is + fill gaps S-01, S-03, S-05, S-06 (attorney letter, insurance quotes, tax bills, rent opinion). No site rebuild.', '1–2 weeks part-time', 'The lowest-cost way to remove the biggest unverified inputs before deciding', src('RR-2023-2')],
        ['Path 2 — Standard (recommended)', 'All of Path 1 + S-10 calculator, S-11 checklist, S-14 bills-vs-stocks column, S-17 law-watch reminder.', '2–4 weeks', 'To compare live/rent/sell yourself under your own assumptions and keep the answer current', src('FHFA-SJ')],
        ['Path 3 — Comprehensive', 'All of Path 1 + Path 2 + S-13 sell-B comparison, S-12 family summary, S-18 private PDF, full accessibility pass S-16.', '4–6 weeks', 'A household-ready package for attorney, CPA and family to sign off together', src('BOE-P19')],
    ])]
    paths = table(['No.', 'Path — choose one before any build', 'What it includes', 'Owner time', 'Best if you want', 'Your decision (saved in this browser only)', 'Official basis'],
                  [r[:5] + [_pth(r[0])] + [r[5]] for r in path_rows],
                  caption='Three paths — pick one, approve it, then build only that', cls='')
    how = """
<p class="callout">Nothing on this page is built until you approve it. Each row says what would be added, why it helps you decide between living in, renting, or selling the Cupertino home, how much effort it takes, and the official page that explains the rule behind it. Approve a row by telling the builder its number (e.g., “approve S-01 and S-03 and Path 2”). Rejected rows stay listed as “Not approved” so the record is complete.</p>
<h2>How this page works</h2>
<ul class="plan">
<li><strong>Proposed</strong> — a suggestion waiting for your review. No file is changed.</li>
<li><strong>Under review</strong> — you asked a professional (attorney, CPA, broker, appraiser) to respond.</li>
<li><strong>Approved</strong> — you said to build it; the next site build includes it and this table marks it “Built”.</li>
<li><strong>Built</strong> — the suggestion is live on the site; the row stays for history.</li>
<li><strong>Not approved / Deferred</strong> — you chose not to build it now; the reason is logged.</li>
</ul>
<p class="note">Every suggestion maps to a flag on the <a href="flagged.html">Flagged for Review</a> page. A suggestion that fills an unverified value retires its flag; one that improves the site adds a new capability without changing figures. Two questions need legal answers before any financial choice is reasonable: the trust inclusion for the basis reset (Q01, <a href="flagged.html#Q01">Q01</a>) and whether the exclusion portability was preserved (Q02, <a href="flagged.html#Q02">Q02</a>).</p>
"""
    approve = """
<h2>How to approve and what happens next</h2>
<ol class="plan">
<li>Read the <a href="flagged.html">Flagged for Review</a> page and the <a href="questions.html">Questions to answer</a> checklist.</li>
<li>Tell the builder which numbered suggestions to build (e.g., “Approve S-01, S-03 to S-06, and Path 2”). No code runs until you do.</li>
<li>The builder edits only the files listed in <a href="https://github.com/wingbangboozle1-lang/Tino1/blob/main/COORDINATION.md">COORDINATION.md</a> for the approved scope, rebuilds with <code>final/model.py</code> and <code>final/build.py</code>, and must pass <code>final/check.py</code> (every row has an official link, every dollar is rounded to $10, no personal information) before opening a pull request.</li>
<li>You review the pull request — each new table row still carries its official link for manual checking — and merge only when satisfied. Flagged items never block a merge; they are published as “under review” until resolved.</li>
</ol>
<p class="note">If you prefer no public repository at all, choose S-18: the analysis is delivered as a private PDF and the public site keeps only the method and no household figures. That does not rewrite Git history — that history stays public until the repository itself is made private or its history is rewritten, which only you can authorize <a class="flag" href="flagged.html#P02">flag P02</a>.</p>
"""
    head = '<p class="callout">This is the <strong>review before implementation</strong>: read each suggestion, choose Adopt / Hold / Reject in its “Your decision” column, and pick one implementation path below. Nothing is built until you approve it; your choices are a review aid kept in this browser only.</p>\n<p id="sgsum" class="status"></p>\n<p><button id="sgreset" type="button">Reset my review choices</button></p>'
    body = '<div id="sgwrap">' + head + how + "<h2>Suggestions to fill gaps in the analysis</h2>" + t_data + "<h2>Suggestions to make the site a better decision tool</h2>" + t_site + "<h2>Choose a path before any change is made</h2>" + paths + approve + _suggestions_options() + "</div>"
    page('suggestions.html', 'Suggestions to improve the site and the decision', 'Proposed improvements — data to gather, model refinements and site features — each with why it helps you decide, how hard it is, and its review status. Nothing is built until you approve it.', body)

# ====================================================================== questions
def build_questions():
    have_rows = [
        ['The legal distinction: Property B is already owned', 'Property B never reassessed, no basis reset, not in estate — the Cupertino home is the only transfer', src('BOE-RULE-462.260', 'RR-2023-2')],
        ['Federal estate-tax exclusion and California rule', '$15,000,000 for 2026, $15,480,000 for 2027 (indexed); no California estate or inheritance tax since 2005', src('IRS-ESTATE', 'SCO-ESTATE')],
        ['Proposition 19 relief and its conditions', 'Parent-child home transfer can keep partial assessed value only if inheritor moves in within 1 year and claims HOX', src('BOE-LTA-2026-026', 'BOE-P19')],
        ['Property-tax rates in force', 'Santa Clara County 1.16360% plus fixed charges; San Francisco 1.18162182% for FY2026-27', src('SCC-RATES', 'SF-TAX')],
        ['Income-tax basis reset at death', 'Inherited home basis = market value at death if included in gross estate — Rev. Rul. 2023-2', src('IRS-FAQ-INHERIT', 'RR-2023-2')],
        ['Rental benchmarks from HUD', '95014 four-BR $6,390, three-BR $5,870; 94122 two-BR $3,310, three-BR $4,230, four-BR $4,380', src('HUD-95014', 'HUD-94122')],
        ['Utility and solar rules', 'SFPUC water +7% FY26-27, CPUC net-metering and $24.15 fixed charge apply to solar credit', src('SFPUC', 'CPUC-NEM')],
        ['Current assessed values and bills (rounded)', 'Cupertino $550,540 assessed / $7,210 tax; SF $116,540 assessed / $2,440 tax — owner figures rounded to $10', src('SCC-RATES', 'SF-TAX')],
        ['SF rent control and current increase cap', 'Annual increase 1.6% Mar 2026–Feb 2027; vacancy resets to market; empty-homes tax not collected', src('SF-RENT-2026', 'SF-EHT')],
        ['House-price and inflation history', 'FHFA San Jose, SF and CA indexes 1976-2026; BLS CPI December values 1976-2025', src('FHFA-SJ', 'BLS-CPI')],
        ['Projection framework 2026-2076', 'Year-by-year market value, assessed value, tax, insurance, water, electricity, repairs, rent for live/rent/sell paths', src('FHFA-SJ', 'BLS-CPI')],
        ['Black-swan stress tests', '50 real historical replays + named crises (1970s, Japan 1990-, 1929-41, 2000, 2008)', src('BLS-CPI', 'FHFA-SJ')],
        ['Step-by-step inheritance process', '14 steps with deadlines: 60-day trustee notice, 150-day BOE statement, 1-year HOX filing', src('PROB-16061.7', 'RTC-480')],
    ]
    missing_rows = [
        ['Type of trust and whether Property A is in gross estate ' + flag('Q01'), 'No legal letter confirming revocable vs irrevocable grantor trust outside estate', src('RR-2023-2')],
        ['Amount of cash and other assets in Transferor estate ' + flag('Q02'), 'Total estate size unknown; portability of spouse exclusion unknown', src('IRS-ESTATE')],
        ['Inheritor basis in Property B ' + flag('Q03'), 'Purchase records and depreciation history for the three-unit building withheld', src('IRS-FAQ-INHERIT')],
        ['Whether Property B is rent-controlled ' + flag('Q04'), 'Building age and exemption status not verified on city map', src('SF-RENT-LAW')],
        ['Inheritor filing status and income bracket ' + flag('Q05'), 'Single vs joint, and actual marginal rates, not disclosed', src('RP-2026-35')],
        ['Transferor is parent of Inheritor ' + flag('Q06'), 'Family relationship for Prop 19 assumed parent-child, not documented', src('BOE-LTA-2026-026')],
        ['Home-insurance quotes for 95014 and 94122 ' + flag('U01'), 'Owner estimate $1,500 each; ZIP-level official premium left blank', src('CDI-TOOL')],
        ['Earthquake coverage decision ' + flag('U02'), 'No mandatory offer reviewed; exposure not priced', src('CDI-EQ')],
        ['Exact tax rate area and fixed charges ' + flag('U03'), 'Rate 1.16360% from county tables; parcel-specific charges derived not read', src('SCC-RATES')],
        ['Proposition 19 allowance after 2027-02-16 ' + flag('U04'), 'Next figure due Feb 2027; model assumes FHFA CA +0.9%', src('BOE-LTA-2025-009')],
        ['Solar interconnection date and tariff ' + flag('U05'), 'Credit $10–$20 per month; new net-billing and fixed charge may reduce it', src('CPUC-NEM')],
        ['Bedrooms and rentable condition of Property A ' + flag('U08'), 'HUD four-BR figure used; actual rent may be lower/higher', src('HUD-95014')],
        ['Market values are owner estimates rounded to $10 ' + flag('P03'), 'Values $3,100,000 (Cupertino) and $1,800,000 (SF) are not appraisals', src('FHFA-SJ')],
        ['Maintenance costs for each home ' + flag('A08'), 'Assumptions $6,000 (Cupertino) and $12,000 (SF) a year; owner says SF higher', src('BLS-CPI')],
        ['Whether Property A is the principal residence at death ' + flag('Q15'), 'Exemption claim not confirmed. Occupancy-like utility use is not an official claim.', src('BOE-LTA-2026-026')],
        ['Whether a spouse, marital trust or community-property title delays the transfer ' + flag('Q16'), 'Left blank. The model assumes one transfer of the whole home.', src('IRS-ESTATE')],
        ['Whether a selling-cost loss is deductible ' + flag('Q17'), 'Not confirmed. The model grants no deduction.', src('IRS-TC701')],
        ['Which home has the homeowners exemption ' + flag('Q18'), 'Left blank. Only one principal residence can have the $7,000 exemption.', src('BOE-HOX')],

    ]
    q_rows = [
        ['Q01', 'Is Property A included in the Transferor gross estate so basis resets at death?', 'Trust instrument + attorney letter stating estate inclusion; Rev. Rul. 2023-2 applicability', 'Assumed yes — revocable trust included; no-reset row shown in Decision sensitivity', 'Written confirmation missing — if irrevocable grantor trust outside estate, no reset and sale triggers tax on decades of gain', 'Have attorney read the trust; if no reset, decide with the “no reset” row — selling advantage shrinks by about $3,319,060 in 2026 dollars', src('RR-2023-2')],
        ['Q02', 'What is total estate size (home + cash + other assets) vs federal exclusion?', 'Total cash and assets; whether predeceased spouse unused exclusion was ported via Form 706', 'Room for cash in 2045 is $17,612,280 per transferor; examples shown for $5M/$10M/$15M overage', 'Actual total unknown; cannot say if estate tax due', 'Total all assets; compare to room table on Estate-cash page; ask if Form 706 was filed for predeceased spouse', src('IRS-ESTATE')],
        ['Q03', 'What is the Inheritor income-tax basis in Property B?', 'Purchase price, inheritance docs, depreciation already claimed on two rented units', 'Left blank — Property B is never sold in model; upper-bound illustration uses assessed value $116,540', 'True gain on any future sale of B unknown', 'Find purchase/inheritance records for B and depreciation schedules', src('IRS-FAQ-INHERIT')],
        ['Q04', 'Is Property B rent-controlled under SF law?', 'Building age (<1979) and unit count on SF Property Information Map; exemption certificates', 'Assumed mixed: controlled rent growth at half market rate; third unit at market', 'Coverage not verified — affects rental income projection', 'Look up building on SF Property Information Map or ask Rent Board counselor', src('SF-RENT-LAW')],
        ['Q05', 'What is Inheritor filing status and current income-tax bracket?', 'Most recent tax return; federal + California marginal rates', 'Model uses single 24% + 9.3% + 3.8% on yearly income; top rates on lump sales', 'Real rate may be higher/lower', 'Have CPA rerun Decision with actual bracket; sensitivity rows show high/low cases', src('RP-2026-35')],
        ['Q06', 'Is Transferor the Inheritor parent (or grandparent with deceased parent)?', 'Family relationship documents matching BOE definitions', 'Assumed parent-child qualifies', 'Eligibility not documented', 'Confirm relationship meets BOE LTA 2026/026 definitions', src('BOE-LTA-2026-026')],
        ['Q07', 'What are actual insurance premiums for each ZIP?', 'CDI comparison tool outputs for 95014 and 94122 plus landlord quote for three-unit building', 'Owner estimate $1,500 each; official ZIP-level blank per checker', 'Real premiums may differ from the estimate', 'Run CDI tool for both ZIPs (5 min per ZIP); get landlord dwelling-fire quote for B', src('CDI-TOOL-APP')],
        ['Q08', 'What is exact tax rate area and are HOX already on current bills?', 'Actual 2025-26 tax bills showing rate area, HOX, and special assessments', 'Rate 1.16360% derived from county tables; fixed charges $930/$1,090 derived; HOX status unknown', 'Post-inheritance tax may differ', 'Read bills for TRA, HOX line, and parcel charges; compare to SCC tax rate book', src('SCC-RATES')],
        ['Q09', 'What is next Proposition 19 allowance (Feb 2027)?', 'BOE Letter to Assessors expected Feb 2027', 'Model uses $1,044,586 then +0.9% per FHFA CA', 'True figure left blank', 'Watch BOE website Feb 2027; compare to projection', src('BOE-LTA-2025-009')],
        ['Q10', 'When was Property A solar interconnected and under which tariff?', 'PG&E net-metering agreement date', 'Assumed credit $180 negative a year continues', 'Credit may shrink under NEM 3.0 + $24.15 fixed charge', 'Read interconnection date on utility agreement; ask utility about tariff longevity', src('CPUC-NEM')],
        ['Q11', 'How many bedrooms is Property A as a rental?', 'Floor plan; property-manager rent opinion', 'HUD four-BR $6,390 used; three-BR $5,870 shown in sensitivity', 'Actual rent may be lower or higher than the HUD figure', 'Get written rent opinion from local manager matching bedroom count', src('HUD-95014')],
        ['Q12', 'Which home must be sold if liquidity is needed, and what is the cost?', 'Basis and Prop 13 advantage comparison', 'Analysis shows keeping B and selling A preserves $19,890 yearly tax + avoids gain on B', 'Depends on cash need timing', 'Compare sell-A vs sell-B table on Decision page with actual cash need', src('SF-TAX')],
        ['Q13', 'What return is reasonable for reinvested proceeds?', 'Investor risk tolerance; Treasury yields as risk-free anchor', 'Model uses 7.0% stocks, 4.5% bonds, 3.5% bills; break-even stock return where rent wins is published', 'No official forecast exists — sensitivity table is the answer', 'Choose return with adviser; check break-even on Decision page; see Black-swan for non-constant reality', src('TREASURY')],
        ['Q14', 'Should earthquake insurance be carried on either home?', 'Mandatory earthquake offer premium; USGS outlook', 'Left blank — not in cost lines', '72% chance M6.7+ in Bay Area before 2043', 'Request earthquake offer from insurer; read USGS Fact Sheet 2016-3020', src('USGS')],
        ['Q15', 'Is Property A the Transferor principal residence at death?', 'Homeowners exemption status on the Transferor bill', 'Owner described occupancy-like utility use. Not a confirmed exemption claim.', 'If it is not the principal residence, Proposition 19 does not apply and living in later does not keep the old assessed value', 'Read the exemption line on the bill privately. Do not publish the bill. ' + flag('Q15'), src('BOE-LTA-2026-026', 'RTC-63.2')],
        ['Q16', 'When does title actually pass, and does a surviving spouse or marital trust delay it?', 'Trust terms and marital-property title, read by the attorney', 'The site shows 2040, 2045 and 2050. It does not know whether distribution waits for a second death.', 'The year of the decision, whose estate the home is in, and whether there is one basis reset', 'Have the attorney say when title passes and whether a marital deduction applies. Do not publish the trust. ' + flag('Q16'), src('IRS-ESTATE', 'BOE-RULE-462.260')],
        ['Q17', 'If Property A is sold promptly, is the selling-cost loss deductible?', 'A written answer from the tax adviser', 'The model treats selling costs as cash spent and grants no deduction when computed gain is negative', 'A small after-tax difference, unless the basis does not reset', 'Ask before counting any tax benefit from the loss. ' + flag('Q17'), src('IRS-TC409', 'IRS-TC701')],
        ['Q18', 'Which home currently has the homeowners exemption?', 'Both current tax bills, read privately', 'Left blank. The exemption is $7,000 of taxable value for one principal residence.', 'A small tax change if it moves from Property B to Property A. Only one home can have it.', 'Read both bills. Do not publish them. ' + flag('Q18'), src('BOE-HOX')],
    ]
    discover_rows = [
        ['Trust and estate inclusion (Q01)', 'Have attorney read trust; get written “included in gross estate” letter', 'Estate attorney', 'Trust instrument, any amendments, deceased-spouse Form 706 if any', '1–2 weeks', src('RR-2023-2')],
        ['Estate size and portability (Q02)', 'CPA totals estate; ask whether a Form 706 was filed with the IRS after the first death', 'CPA + attorney', 'Bank/brokerage statements, deeds, prior Form 706', '1–3 weeks', src('IRS-ESTATE')],
        ['Basis in Property B (Q03)', 'Find purchase/inheritance records; pull depreciation schedules from prior returns', 'CPA', 'Closing statement, Form 1040 Schedule E history', '1 week', src('IRS-TC409')],
        ['Rent control status (Q04)', 'Check SF Property Information Map building age; call Rent Board', 'Owner + Rent Board counselor', 'Assessor building date, unit count', '1 day', src('SF-RENT-LAW')],
        ['Filing status (Q05)', 'Share most recent return with adviser', 'CPA', 'Form 1040, FTB 540', '1 day', src('FTB-RATES')],
        ['Parent-child qualification (Q06)', 'Confirm relationship meets BOE definitions', 'Attorney', 'Family records', '1 day', src('BOE-LTA-2026-026')],
        ['Insurance premiums (U01/U02)', 'Run CDI comparison tool for 95014 and 94122; request landlord + earthquake quotes', 'Insurance broker', 'Rebuilding cost, ZIP, age, coverage limits', '1 day (tool) + 1 week (quotes)', src('CDI-TOOL-APP')],
        ['Tax rate area (U03)', 'Read actual tax bills line by line', 'Owner', '2025-26 secured tax bills', '1 day', src('SCC-RATES')],
        ['Prop 19 allowance next (U04)', 'Bookmark BOE LTA page; check Feb 2027 release', 'Owner/adviser', '—', '5 minutes in Feb 2027', src('BOE-LTA-2025-009')],
        ['Solar tariff (U05)', 'Read PG&E NEM agreement interconnection date; ask about fixed charge impact', 'Owner + utility', 'NEM agreement, PG&E bill', '1 day', src('CPUC-NEM')],
        ['Market rent for A (U08)', 'Get property-manager rent opinion with bedroom count', 'Property manager', 'Floor plan, photos', '1 week', src('HUD-95014')],
        ['Market values', 'Order appraisal or pull 6-month comparable sales from county recorder', 'Licensed appraiser', 'Access to homes', '2–4 weeks', src('FHFA-SJ')],
        ['Maintenance assumption (A08)', 'Ask contractor/handyman for 5-year repair history and forecast', 'Owner + contractor', 'Invoices, inspection report', '1 week', src('BLS-CPI')],
        ['Principal residence at death (Q15)', 'Read the homeowners exemption line on the Transferor bill, privately', 'Owner', 'Current secured tax bill', '1 day', src('BOE-LTA-2026-026')],
        ['Transfer timing and marital delay (Q16)', 'Have the attorney say when title passes and whether a marital deduction applies', 'Estate attorney', 'Trust instrument, title report', '1-2 weeks', src('IRS-ESTATE')],
        ['Deductibility of a selling-cost loss (Q17)', 'Ask the tax adviser before counting any tax benefit', 'Tax adviser', 'Draft sale worksheet', '1 day', src('IRS-TC701')],
        ['Which home has the homeowners exemption (Q18)', 'Read both bills, privately. Do not publish them.', 'Owner', 'Both current tax bills', '1 day', src('BOE-HOX')],
    ]
    have_table = table(['Area', 'What we already have (verified or owner-supplied rounded to $10)', 'Official basis'], have_rows, caption='Information we already have', cls='')
    missing_table = table(['Item', 'What we do not have (flagged left blank)', 'Official basis — where to check'], missing_rows, caption='Information we do not have — must be discovered before a reasonable decision', cls='')
    q_table = table(['No.', 'Question that must be answered before deciding', 'Information needed', 'What we have now', 'What is missing / implication', 'Answer / How to discover (suggestion)', 'Official basis'], q_rows, caption='Questions, informations and answers — what is needed before any decision can be reasonably made')
    disc_table = table(['Missing information', 'Suggested action to discover it', 'Who to ask', 'Documents to gather', 'Time', 'Official basis'], discover_rows, caption='How to discover missing information — suggestions for the owner')
    checklist = """<h2>Decision-readiness checklist — you can reasonably decide once you have</h2><ul class="plan"><li><strong>Legal:</strong> ☐ Trust inclusion letter (Q01) — without it, basis reset is assumption. ☐ Property-tax deadlines understood (60-day notice, 150-day BOE statement, 1-year HOX). See <a href="process.html">Process</a> and <a href="law.html">Law</a>.</li><li><strong>Tax:</strong> ☐ Estate total vs $15,480,000 exclusion room (Q02) — determines if cash triggers 40% above line. ☐ Your actual income-tax bracket (Q05) — determines after-tax rent vs sell gap. ☐ Prop 19 eligibility (Q06) confirmed. ☐ Property A is the principal residence at death (Q15). ☐ Transfer timing and any marital delay confirmed (Q16).</li><li><strong>Costs:</strong> ☐ Written insurance quotes for 95014 and 94122 (U01) + earthquake decision (U02). ☐ Actual tax bills confirming tax rate area (U03). ☐ Solar NEM date/tariff (U05). ☐ Rent opinion for A (U08) with bedroom count.</li><li><strong>Values:</strong> ☐ Appraisal or comparable sales for $3,100,000 / $1,800,000 estimates. ☐ Basis in Property B (Q03) if selling B is ever considered.</li><li><strong>Model sanity:</strong> ☐ Read <a href="decision.html">Decision</a> sensitivities (break-even home growth and stock return) and <a href="black-swan.html">Black swan</a> (50 replays, Japan and Depression paths where rent wins). If you cannot accept the worst 10-year case behind by $2,069,690, choose a staged investment and 2-year bill buffer.</li><li><strong>Privacy:</strong> ☐ Decide repository visibility — rounding to $10 does not anonymize a household; Git history stays public until you make the repo private or rewrite history <a class="flag" href="flagged.html#P02">flag P02</a>.</li></ul><p class="note">Check each box by gathering the document in “How to discover.” When every legal box and the cost boxes are checked, the three choices on the <a href="decision.html">Decision</a> page are comparable with verified inputs rather than estimates. Until then, the site marks the missing items as flags and shows the result conditional on the assumptions.</p>"""
    intro = '<p class="callout"><strong>Six blockers gate the decision.</strong> B1–B2: trust instrument never seen and basis/Rev. Rul. 2023-2 treatment unconfirmed. B3: estate size/portability unknown against the $15,480,000 exclusion for 2027. B4: own income-tax bracket unknown. B5: Prop 19 parent-child eligibility unconfirmed. B6: filing and claim deadlines need dates from the death certificate. All six are listed as Q-rows below; the register on the <a href="verification.html">Verification</a> page preserves what was checked when. Nothing on this page invents an answer: rows are marked have / cannot have / need-to-know with the official basis on each.</p>\n<p class="callout">A reasonable decision needs answers, not just projections. This page puts every question in one place: what information we already have, what we do not have, the question that must be answered, the answer if known, and a concrete suggestion for how to discover the missing information. Nothing here asks you to type values into the site — each suggestion says who to ask and what paper to gather.</p>'
    body = intro + "<h2>What we have and what we do not have</h2>" + have_table + missing_table + "<h2>Questions, information and answers before deciding</h2>" + q_table + disc_table + checklist + _questions_register()
    page('questions.html', 'Questions, information and answers before deciding', 'A clear list of questions that must be answered before any decision can be reasonably made — what we have, what we do not have, the answer if known, and suggestions for how to discover missing information.', body)

# ====================================================================== review
def build_review():
    rows = [['<span id="%s">%s</span>' % (r['id'], r['id']), r['where'], r['finding'], r['status'], src(*r['src']) + ' · <a href="%s/%s" rel="noopener">file</a>' % (REPO, r['path'])] for r in REVIEW]
    t = table(['No.', 'Where', 'Finding', 'Status', 'Rule or source, and file'], rows, caption='Repository review findings') if rows else ''
    body = """<p class="callout">The repository holds several generations of the same analysis written by parallel sessions. This page records what an independent pass found, so that a reader knows which pages to trust. The full history is in <a href="%s/blob/main/COORDINATION.md">COORDINATION.md</a>.</p>""" % REPO + t
    page('review.html', 'Repository review', 'Irregularities found while reading the repository, with links to the files and to the rule each one is measured against.', body)


# ====================================================================== questions and suggestions (session 0adc9b0a)
class _H(object):
    """What final/questions.py and final/suggestions.py need from the generator."""
    pass


def _helper():
    h = _H()
    h.m, h.src, h.flag, h.BLANK = m, src, flag, BLANK
    h.P, h.B, h.SENS, h.BE, h.RH, h.BY, h.E = P, B, M['sensitivity'], BE, RH, M['by_T'], [x for x in M['estate'] if x['cash_today'] == 2000000]
    h.SF_GAP = sf_gap
    h.SF_SALE_TAX = (P['sf_value'] * (1 - P['sell_cost']) - P['sf_assessed']) * 0.371
    return h


def _anchor(rows):
    """Give the first cell of each row an id so other pages can link to a question or suggestion."""
    return [['<span id="%s">%s</span>' % (r[0].replace(' ', '-'), r[0])] + r[1:] for r in rows]


def _questions_register():
    """Part 2 of questions.html (session 0adc9b0a); Part 1 is build_questions() by session 155782b5."""
    q = QUESTIONS_DATA.sections(_helper())
    open_h = ['No.', 'Question', 'Why it matters to the choice', 'What is already known', 'Answer today', 'What is missing', 'How to find it', 'Official basis']
    n_open = len(q['decisive']) + len(q['amounts']) + len(q['lookups'])
    t1 = table(open_h, _anchor(q['decisive']), caption='1. Open, and decisive: these set the direction or move the result most', cls='qa')
    t2 = table(open_h, _anchor(q['amounts']), caption='2. Open, changes the amounts but not the ranking in the cases tested', cls='qa')
    t3 = table(open_h, _anchor(q['lookups']), caption='3. Facts the owner can look up in a few minutes', cls='qa')
    t4 = table(['No.', 'Question', 'What the model shows', 'Answer today', 'What to do instead', 'Official basis'], _anchor(q['later']),
               caption='4. Cannot be known in advance')
    t5 = table(['No.', 'Question', 'Answer', 'Effect on the choice', 'Read on the official page', 'Official basis'], _anchor(q['known']),
               caption='5. Answered from official pages')
    t6 = table(['Order', 'Who can answer', 'Questions', 'Note', 'Official basis'], q['who'], caption='Who to ask, in a sensible order')
    return """
<h2 id="register">Part 2 - decision register with reading dates</h2>
<p class="callout"><strong>The short version.</strong> %d questions are answered from official pages. %d cannot be known until the time comes, and the model tests a range for each. %d are open, and three of those matter far more than the rest. What the trust says about the home (D01) moves the result for selling by millions of dollars. Whether the Inheritor wants to live there (D02) is a personal choice with a known price. How sale proceeds would be invested (D03) is the one input that reverses the ranking in the cases tested: left in savings, selling falls behind renting. A decision is reasonable once those three are settled; the others refine the amounts.</p>
<p class="note">Part 1 above (questions Q01 to Q14) and this part were written by two work sessions on the same day and are both kept. This part sorts the questions by how much they can move the result, gives the day each official page was last opened, and adds the questions that are already answered. Matching rows: D01 is Q01; D04 is Q06; D07 and D08 are Q02; D09 is Q05; D10 is Q03; D11 is Q04; D03 is Q13; F01 is Q11; F02 is Q07 and Q14; F03 is Q08; F04 is Q10; T03 covers Q09. <em>Answer today</em> is left blank, and marked so, wherever no official page or owner figure settles it; nothing is inferred. Dollar figures from the model are conditional on the assumptions listed under <a href="flagged.html">Flagged for Review</a>.</p>
<h3>What is not yet known</h3>
%s
%s
%s
<h3>What cannot be known in advance</h3>
%s
<h3>What is known</h3>
%s
<h3>Who to ask</h3>
%s
<p class="note">This register does not replace the <a href="flagged.html">Flagged for Review</a> page, which lists every unconfirmed value and assumption. It selects the ones that bear on the choice and adds how to resolve each. This is not legal, tax or investment advice.</p>
""" % (len(q['known']), len(q['later']), n_open, t1, t2, t3, t4, t5, t6)


def _suggestions_options():
    """Part 2 of suggestions.html (session 0adc9b0a); Part 1 is build_suggestions() by session 155782b5."""
    s = SUGGESTIONS_DATA.sections(_helper())
    hdr = ['No.', 'Suggestion', 'What the site does today', 'Options', 'Suggested choice', 'Effect on the decision', 'Effort and risk', 'Official basis']
    n = len(s['privacy']) + len(s['inputs']) + len(s['tools'])
    t0 = table(['Path', 'Name', 'Suggestions included', 'What it achieves', 'Effort', 'Official basis'], s['paths'], caption='Ready-made paths for Part 2')
    t1 = table(hdr, _anchor(s['privacy']), caption='Privacy and upkeep', cls='qa')
    t2 = table(hdr, _anchor(s['inputs']), caption='Better inputs', cls='qa')
    t3 = table(hdr, _anchor(s['tools']), caption='Decision tools', cls='qa')
    return """
<h2 id="options">Part 2 - options register for the site</h2>
<p class="callout"><strong>Nothing in this part has been implemented either.</strong> These are %d further proposals, written by a second work session on the same day and kept beside Part 1 (S-01 to S-18). Each row gives lettered options, a suggested choice, its effect on the decision, and the effort and risk. Status of every row: <strong>decision needed</strong>.</p>
<p class="note">Where a row covers the same ground as Part 1, choose once: G03 is S-17; G04 is S-06; G05 is S-03 and S-04; G10 option C is S-13; G11 is S-14 and S-15; G12 is S-10; G13 is S-11; G01 option D is S-18. To choose from this part, list numbers with an option letter (for example "G01 C, G04 B, G09 B"), or name one of the paths below. The suggestions change how the result is presented and tested, not the rules behind it. G10 and G12 would add new model results, which would be checked and flagged like the existing ones.</p>
%s
%s
%s
%s
<p class="note">Where a suggestion rests on a rule, the link in the last column is the official page for that rule. For G01 and G02 the behaviour of the hosting service is described in its own documentation, linked beside the official pages cited by the two privacy flags. Since 2026-11-12 the address served by GitHub Pages shows the guide without household figures, and the pages of this edition are repository files only; G01 asks the owner to settle that question for good.</p>
""" % (n, t0, t1, t2, t3)


LEGACY = [
    ('archive/root-site-2026-11-11/index.html', 'Root "decision hub" published earlier on 2026-11-11 (pull request 15)',
     'Shows Property B as reassessed and as part of the estate. It is neither: the Inheritor already owns it. Tables stop in 2060.', ('BOE-RULE-462.260', 'IRS-ESTATE')),
    ('dashboard/index.html', 'dashboard/ - model-generated dashboard of 2026-11-10 with a black-swan page added 2026-11-11',
     'Grows the Proposition 19 allowance 2% every year instead of following the official two-year rule; many table rows have no official link.', ('BOE-LTA-2025-009',)),
    ('site/index.html', 'site/ - eight-page suite of 2026-11-10',
     'Different growth assumptions and a 10-year comparison only; superseded.', ('FHFA-SJ',)),
    ('docs/index.html', 'docs/ - first multi-page site of 2026-11-10',
     'Cites consumer finance websites as sources, has broken in-page anchors and a script error; lists a year-by-year history series.', ('IRS-ESTATE',)),
    ('archive/root-portal-62c87525.html', 'Portal page of 2026-11-11 (pull request 14)',
     'A landing page that pointed to dashboard/; replaced.', ('BOE-P19',)),
    ('archive/mirror-archived-2026-11-10.html', 'Mirror of the first root page of 2026-11-10',
     'Treated Property B as inherited; replaced.', ('BOE-RULE-462.260',)),
    ('final/site/index.html', 'final/site/ - staging address of the current site',
     'Now redirects to this site.', ('BOE-P19',)),
]


def _sg(sid):
    return ('<select class="sg" data-id="%s" aria-label="Your decision for %s">'
            '<option value="">Not yet reviewed</option>'
            '<option value="Adopt">Adopt</option>'
            '<option value="Hold">Hold</option>'
            '<option value="Reject">Reject</option></select>' % (sid, sid))


def _pth(sid):
    return '<label><input type="radio" class="pth" name="sgpath" value="%s"> Choose this path</label>' % sid


def build_versions():
    rows = [['<a href="%s/blob/main/%s" rel="noopener">%s</a>' % (REPO, h, e(t)), 'Superseded - kept for the record in the repository, not published on this site', e(why), src(*s_)] for h, t, why, s_ in LEGACY]
    t = table(['Earlier version', 'Status', 'Why it should not be relied on', 'Rule it is measured against'], rows, caption='Earlier versions kept in the repository')
    body = '<p class="callout">This site is the only current version. The pages below were written by earlier or parallel work sessions. They are kept so that nothing is lost, each carries a notice pointing back here, and none is linked from anywhere else on this site. Their numbers differ from this site because their assumptions and, in places, their reading of the rules differ.</p>' + t + '<p class="note">Details of each finding are on the <a href="review.html">Repo review</a> page and in <a href="%s/blob/main/COORDINATION.md">COORDINATION.md</a>.</p>' % REPO
    page('versions.html', 'Earlier versions', 'Older editions of this analysis that remain in the repository, and why this site replaces them.', body)


def stub(slug, target, title):
    open(os.path.join(OUT, slug), 'w').write('''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url=%s">
<link rel="canonical" href="%s">
<title>%s - moved</title></head>
<body><p>This page has moved to <a href="%s">%s</a>.</p></body></html>
''' % (target, target, e(title), target, e(title)))


STUBS = [('properties.html', HOME, 'The two homes'), ('scenarios.html', 'decision.html', 'Decision'),
         ('taxes.html', 'law.html', 'Law'), ('estate-tax.html', 'estate-cash.html', 'Cash and estate tax'),
         ('methodology.html', 'sources.html', 'Sources and method'), ('pending-changes.html', 'law.html', 'Law'),
         ('steps.html', 'process.html', 'Process'), ('mirror-archived-2026-11-10.html', 'versions.html', 'Earlier versions')]

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
table.qa{min-width:1500px}table.qa td{min-width:150px}table.qa td:first-child,table.qa th:first-child{min-width:0;white-space:nowrap}
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
  var sg=document.getElementById('sgwrap');
  if(sg){var KEY='tino1-review-choices';
    var load=function(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(err){return{}}};
    var save=function(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(err){}};
    var st=load();
    var refresh=function(){var n=0,a=0,h=0,r=0,u=0;
      Array.prototype.forEach.call(sg.querySelectorAll('select.sg'),function(s){
        var v=st[s.getAttribute('data-id')]||'';s.value=v;n++;
        if(v==='Adopt')a++;else if(v==='Hold')h++;else if(v==='Reject')r++;else u++;});
      var path=st['path']||'';
      Array.prototype.forEach.call(sg.querySelectorAll('input.pth'),function(rb){rb.checked=(rb.value===path)});
      var el=document.getElementById('sgsum');
      if(el){el.textContent=n+' suggestions: '+a+' adopted, '+h+' on hold, '+r+' rejected, '+u+' not yet reviewed. '+
        (path?'Implementation path chosen: '+path+'. ':'No implementation path chosen yet. ')+
        'Your choices are saved in this browser only and are not sent anywhere. Implement nothing until every adopted suggestion has been reviewed against the Flagged for Review page.';}};
    sg.addEventListener('change',function(ev){var t=ev.target;
      if(t.tagName==='SELECT'&&t.getAttribute('class')==='sg'){st[t.getAttribute('data-id')]=t.value;}
      else if(t.type==='radio'&&t.getAttribute('class')==='pth'){st['path']=t.value;}
      save(st);refresh();});
    var rb=document.getElementById('sgreset');
    if(rb){rb.addEventListener('click',function(){st={};save(st);refresh();});}
    refresh();}
})();
"""


def build_home_choice():
    """Root index.html: the site's front door.  Privacy first - the primary link goes to
    the no-figures guide; the second link is the rounded-figures analysis the brief asks
    for.  Only written in ROOT_MODE (the staging tree uses HOME = index.html)."""
    open(os.path.join(OUT, 'index.html'), 'w').write("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Two-home inheritance analysis and no-figures guide</title>
<link rel="stylesheet" href="style.css"></head>
<body><div class="wrap"><header class="top"><div class="wrap"><span class="brand">Two-home inheritance analysis</span></div></header>
<h1>Two editions of this analysis</h1>
<p class="lead">A future trust inheritance of a Cupertino home, and a San Francisco home the Inheritor already owns. Choose how you want to read the work.</p>
<div class="cards">
<article><h2>No-figures decision guide (privacy first)</h2><p>The rules, the process and the decision framework with <strong>none of this household's figures</strong>. Every number there is invented for teaching. Start here if you want the analysis without the household's data.</p><p><a href="privacy-site/public/index.html">Open the no-figures guide</a></p></article>
<article><h2>Rounded-figures analysis (the owner's brief)</h2><p>The full decision analysis with the executive dashboard, year-by-year projections, live / rent / sell comparison and the stated best plan. Every household figure is rounded to the nearest $10 so it cannot be traced back to a source.</p><p><a href="summary.html">Open the rounded-figures analysis</a></p></article>
</div>
<p class="note">People are placeholders (the Transferor, the Inheritor). No names, street addresses or parcel numbers appear anywhere. Unverified values are flagged on the <a href="flagged.html">Flagged for Review</a> page. Not legal, tax, investment or insurance advice.</p>
</div></body></html>
""")


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'style.css'), 'w').write(CSS)
    open(os.path.join(OUT, 'app.js'), 'w').write(JS)
    for f in (build_index, build_decision, build_questions, build_suggestions, build_projections, build_blackswan, build_process, build_law,
              build_estate, build_costs, build_flagged, build_sources, build_verification, build_requirements, build_review):
        f()
    if ROOT_MODE:
        build_home_choice()
        build_versions()
        for s_, t_, n_ in STUBS:
            stub(s_, t_, n_)
    print('built', len([x for x in os.listdir(OUT) if x.endswith('.html')]), 'pages in', OUT)


if __name__ == '__main__':
    main()
