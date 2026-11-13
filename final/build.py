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
# ROOT_MODE builds the household-specific numeric analysis into its historical root files,
# with its executive summary at summary.html. The public index.html is a generic landing
# page that links only to privacy-site/public; final/publish.py excludes all numeric pages.
HOME = 'summary.html' if ROOT_MODE else 'index.html'
Y0 = 2026
T = P['T']
BUILD_DATE = '2026-11-13'
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
        kpi('Federal estate-tax room for cash in %d, in %d dollars' % (T, T), m(B['exclusion_T'] - B['fmv_T']),
            'projected exclusion %s minus Property A; per transferor. That is about %s in 2026 dollars - compare a cash figure measured today against the second number, not the first'
            % (m(B['exclusion_T']), m((B['exclusion_T'] - B['fmv_T']) / B['cpi_T']))),
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
    # ---- what would overturn the ranking, and what is cheaper to settle now than in 2045 ----
    # Each lever is the model's own break-even point, so this table cannot drift from the pages.
    # The three answers that no model can supply are listed beside them, because they are the
    # ones that actually decide the outcome (flags Q01, Q06, Q15).
    overturn = table(
        ['Lever', 'Baseline assumption', 'What it would take to make renting better than selling', 'How to settle it', 'Official basis'],
        [
            ['Growth of Property A', '4.0%% a year (assumption %s)' % flag('A01'),
             'Home prices rising more than %s a year on average to 2076. The real 1976-2025 record for this area was 6.71%% a year, so this is possible, not remote.' % pc(BE['g_cup_rent_vs_sell']),
             'An appraisal now settles the starting value; the growth rate stays an assumption and is re-run at the decision date.',
             src('FHFA-SJ')],
            ['Return on the reinvested proceeds', '7.0%% a year on stocks (assumption %s)' % flag('A02'),
             'A stock return below %s a year on average. In savings or Treasury bills (%s a year) renting already wins, which is why the plan says not to park the money.' % (pc(BE['r_stock_rent_vs_sell']), pc(P['r_bill'])),
             'Nothing to discover: this is a choice about risk, not a missing fact.',
             src('TREASURY', 'DAMODARAN')],
            ['Rent Property A would command', 'HUD four-bedroom small-area rent for ZIP 95014, %s a month (assumption %s)' % (m(P['cup_rent_month']), flag('A07')),
             'Rent above about %s a month to 2076. That is far above the HUD benchmark, and the bedroom count is unconfirmed (%s).' % (m(BE['rent_month_rent_vs_sell']), flag('U08')),
             'A written rent opinion from a local manager, obtained privately. It does not need the address on this site.',
             src('HUD-95014')],
            ['Is the home in the Transferor gross estate?', 'Assumed yes, so the basis resets (flag %s)' % 'Q01',
             '<strong>Not a sensitivity: this can reverse the entire plan.</strong> If the trust sits outside the gross estate there is no basis reset and a prompt sale is taxed on decades of gain, which costs about %s of 2026-dollar wealth.' % m(B['real_sell'] - M['sensitivity'][-1]['real_sell']),
             '<strong>Settle first.</strong> An estate attorney reads the trust and writes one paragraph. A legal fee now is small against the amount at stake.',
             src('RR-2023-2', 'IRS-FAQ-INHERIT')],
            ['Does the parent-child test pass?', 'Assumed yes (flag %s)' % 'Q06',
             'If the relationship does not meet the definitions, the Proposition 19 relief is lost and the lived-in path becomes materially worse.',
             'Confirm the relationship against the Board of Equalization definitions. No names need to be published.',
             src('BOE-LTA-2026-026', 'BOE-PUB-800-1')],
            ['Is Property A the Transferor principal residence?', 'Assumed yes (flag %s)' % 'Q15',
             'If it is not, there is no family-home relief at all and the lived-in path loses its only tax advantage.',
             'Read the homeowners exemption on the Transferor bill, privately.',
             src('BOE-HOX', 'RTC-63.2')],
        ],
        caption='What would change the answer, and what no amount of modelling can settle',
        note='The first three rows are the model break-even points, computed by the same run that produces every other figure on this page. The last three are not sensitivities at all: they are the facts that decide whether the tax rules assumed here apply, and each one costs one letter or one document to settle. Flags Q01, Q06 and Q15 are open until then.')

    before = table(
        ['Before the inheritance (now to %d)' % (T - 1), 'Why it cannot wait until %d' % T, 'Cost of doing it now', 'Official basis'],
        [
            ['Have the trust read, and get the gross-estate answer in writing (%s)' % flag('Q01'),
             'It decides the basis reset, and the basis reset is most of the reason selling wins. It also decides whether a Form 706 is needed at all.',
             'One attorney consultation. Nothing on this site needs to be published to answer it.',
             src('RR-2023-2', 'IRS-FAQ-INHERIT')],
            ['Ask whether a Form 706 was filed for a predeceased spouse (%s)' % flag('Q02'),
             'A portability election can sometimes still be made up to the fifth anniversary of the first death. Once the window is gone it cannot be reopened, and the amount at stake is a second exclusion.',
             'Locate one filed return, or ask the preparer. This is the only item on the site with a deadline that may already be running.',
             src('IRS-FAQ-ESTATE', 'RP-2026-35')],
            ['Record the monthly figures as they change (water, electricity, insurance, rent)',
             'This site uses the current figures. A written record of the next ten years replaces the owner estimates with observed numbers, and observed numbers are what a lender, an insurer and an appraiser ask for.',
             'A spreadsheet. Do not publish it.',
             src('CDI-RPI', 'SFPUC')],
            ['Get one real insurance quote for each home (%s)' % flag('U01'),
             'The premium is the weakest number on the site. It is the owner estimate, and no official page publishes a ZIP-level premium. Tripling it does not change the ranking, but a real quote replaces an assumption.',
             'One broker call per property. Ask for a landlord policy on the three-unit building as well.',
             src('CDI-TOOL', 'CDI-EQ')],
            ['Read the bills for the things that are already knowable (the solar interconnection date, the tax rate area, which home has the homeowners exemption)',
             'These are flags %s, %s and %s. Each one fixes a number that is currently derived rather than read, and each takes minutes.' % (flag('U05'), flag('U03'), flag('Q18')),
             'Open three documents, privately.',
             src('CPUC-NEM', 'SCC-RATES', 'BOE-HOX')],
        ],
        caption='Decisions that are cheaper and safer to settle before the inheritance than after it')

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
        ('questions.html', 'Questions &amp; discovery', 'Known vs. unknown facts, answers needed before deciding, and ways to discover missing details'),
        ('suggestions.html', 'Site improvements', 'Proposed data, model, tax-detail and privacy improvements with review status so you can choose a path before any build'),
        ('flagged.html', 'Flagged for Review', 'Every unconfirmed value, assumption and irregularity, with links'),
        ('verification.html', 'Verification', 'Line-by-line check register: what was re-read on which official page, and what stays flagged'),
        ('requirements.html', 'Requirements', 'Every part of the brief, the page that answers it, and the official pages re-read'),
    ])
    body = """
<section class="kpis">%s</section>
<h2>Best plan and why - conditional on the assumptions in the flags</h2>%s
<h2>What would change the answer</h2>%s
<h2>What to settle before %d, and why it cannot wait</h2>%s
<h2>After-tax wealth in 2076, in 2026 dollars (baseline, inheritance in %d)</h2>%s
<p class="note">Wealth counts only what differs between the choices: Property A itself and every cash flow it causes. The two units already rented in Property B are the same in all three choices and are left out, and so is the third unit: no rent was ever supplied for it, so the baseline counts none (nothing is inferred). The upside of letting the third unit when the Inheritor moves to Property A appears only as one labelled scenario in the sensitivity table. All figures assume everything is sold and taxed at the end so that the choices can be compared like for like.</p>
<h2>Dashboard</h2>
<div class="seg" id="tsel" aria-label="Year of inheritance"><span>Year of inheritance:</span>%s</div>
%s
<p class="note"><strong>How to read the numbers.</strong> Three kinds of figures appear on this site. <strong>Official facts</strong> are quoted from the government page linked on the row. <strong>Owner-supplied figures</strong> (market values, rents, utilities, tax bills, insurance estimates) are the owner's own numbers: they are rounded to the nearest $10 for privacy, cannot be confirmed on an official page (%s), and the link on their row shows only the rule or index the calculation follows, not verification of the figure. <strong>Model outputs</strong> are projections from the assumptions on the <a href="flagged.html">Flagged for Review</a> page - conditional scenarios, not forecasts. Every official source on the site has now been read directly on its agency page across passes on 2026-11-11 and 2026-11-12: see <a href="verification.html">Verification</a>, <a href="questions.html">Questions &amp; discovery</a>, and <a href="suggestions.html">Site improvements</a>.</p>

<h2>The two homes are not the same case</h2>%s
<p class="callout"><strong>Looking for the version with no household figures?</strong> A separate <a href="privacy-site/public/index.html">no-figures decision guide</a> publishes the same rules, process and decision framework without any of this household's numbers - every illustration there is invented for teaching. This summary page carries the rounded (nearest $10) figures the owner asked to see in the decision analysis.</p>
<h2>Sections</h2><div class="cards">%s</div>
""" % (cards, plan, overturn, T - 1, before, T, chart, opts, dash, flag('P03'), diff, links)
    page(HOME, 'Executive summary',
         'Property A (Cupertino, 95014) will pass to the Inheritor through a trust some time around 2040 to 2050. Property B (San Francisco, 94122) is already owned by the Inheritor. This site works out, with official sources on every table row, whether to live in Property A, rent it out, or sell it and reinvest.', body)


# ====================================================================== decision
def build_decision():
    s = B
    at = table(['Item at inheritance in %d' % T, 'Amount', 'How it is worked out', 'Official basis'], [
        ['Market value of Property A', m(s['fmv_T']), '%s today, growing 4.0%% a year (assumption %s)' % (m(P['cup_value']), flag('A01')), src('FHFA-SJ')],
        ['Assessed value just before death', m(s['fbyv_T']), '%s in 2026, growing with the California CPI capped at 2%% a year (R&TC 51); future California CPI is unknown, so national inflation is used as a labelled proxy %s' % (m(P['cup_assessed']), flag('A11')), src('BOE-P19', 'RTC-51')],
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
        ['Rent from a third unit at Property B, after tax (baseline)', '$0 (nothing is inferred: no rent was ever supplied for the third unit)', '$0 (the Inheritor lives there)', '$0 (the Inheritor lives there)', src('SF-RENT-RULES', 'HUD-94122')],
        ['Net cash for the year', m(rT['live_unit3'] - rT['live_cost']), m(rT['rent_after_tax']), 'investment income on %s' % m(s['sell_net']), src('IRS-TC559')],
    ], caption='Cash flow in the first year', cls='num',
        note='The baseline counts no rent for the vacated third unit at Property B: nothing is inferred where no rent was ever supplied. Letting it at the average of the two known unit rents is shown only as one labelled scenario in the sensitivity table below. The rent for Property A is the HUD four-bedroom Small Area Fair Market Rent for ZIP 95014 (%s a month in fiscal year 2026) grown with inflation plus 0.5 point - the 40th-percentile HUD rent standard is a benchmark, not a verified rent for this home. The number of bedrooms and the rentable condition were not supplied (%s); the stand-in is an assumption (%s).' % (m(P['cup_rent_month']), flag('U08'), flag('A07')))
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
            ('RP-2026-35', 'FTB-RATES'), ('RP-2026-35', 'FTB-RATES'), ('SF-RENT-RULES', 'HUD-94122'), ('CDI-TOOL',), ('CDI-RES',), ('RR-2023-2',)])
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
    body = at + first + w + where + '<h2>Wealth over time, in 2026 dollars</h2>' + chart + why + sens + be + byT + '<h2>Property A or Property B?</h2>' + which + '<p class="note"><strong>Provenance note:</strong> Links in the Official basis column point to the governing tax rule, rate table, or government index applied in the row; they do not verify owner-supplied figures (%s) or future investment/housing returns (%s). Before finalizing any plan, review the open questions on <a href="questions.html">Questions &amp; discovery</a> and the candidate upgrades on <a href="suggestions.html">Site improvements</a>.</p>' % (flag('P03'), flag('A01'))
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
        ['Assessed values', '%s (A), %s (B)' % (m(P['cup_assessed']), m(P['sf_assessed'])), 'California CPI, capped at 2%; never above market value', 'owner figures; rule is official. The statutory index is the California CPI (R&TC 51); future California CPI is unknown, so each path\'s inflation rate is a labelled proxy %s (official BOE factor for 2026 rolls: 1.02)' % flag('A11'), src('BOE-P19', 'RTC-51', 'BOE-LTA-2026-002')],
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
            + '<h2>Year-by-year tables</h2><p class="note">Baseline path with inheritance in %d. Amounts are nominal dollars of each year, rounded to $10. A negative electricity figure is a credit. If Property A is sold, its costs stop in %d; the sale figures are on the <a href="decision.html">Decision</a> page. <strong>Provenance:</strong> the Official basis column links the statutory tax/rate rule or HUD/county schedule used; projected dollar figures are conditional model outputs built on the owner\'s rounded inputs (%s) and stated assumptions (%s), not official forecasts.</p>' % (T, T, flag('P03'), flag('A01'))
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
    PV = M['provenance']
    prov = table(['Series or construction', 'Provenance (what kind of source this is)', 'Official basis'], [
        ['Inflation, every path', e(PV['infl']), src('BLS-CPI')],
        ['Home-price changes: San Jose / San Francisco / California', e(PV['g_cup']) + '<br>' + e(PV['g_sf']) + '<br>' + e(PV['g_ca']), src('FHFA-SJ', 'FHFA-SF', 'FHFA-CA')],
        ['Stock, bond and bill returns', e(PV['r_stock']) + ' ' + flag('S02'), src('TREASURY') + ' &middot; ' + src('DAMODARAN')],
        ['National home prices 1929-1950 (Depression path)', e(PV['nat_re_early']) + ' ' + flag('S02'), src('BLS-CPI') + ' &middot; ' + src('DAMODARAN')],
        ['Japan 1991-2020 series (Japan path)', e(PV['japan']) + ' ' + flag('S08'), src('FRED-JP')],
        ['Proposition 13 assessment factor, every path', e(PV['prop13_factor']) + ' ' + flag('A11'), src('RTC-51', 'BOE-LTA-2026-002')],
        ['The fifty replays and every named path', e(PV['paths']), src('BLS-CPI', 'FHFA-SJ')],
    ], caption='Provenance: official statistics, one academic dataset, and hypothetical constructions are three different things and are never presented as one',
        note='Everything on this page is a stress test built from the series above. The official columns link the government index the numbers come from; the stock, bond and bill returns come from an academic table and are labelled as such; the paths themselves are constructions and are not forecasts.')
    named = table(['Path', 'Kind of path', 'Market value at inheritance', 'Tax if lived in / rented, first year', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Best', 'Official basis'], [
        [e(x['label']), e(x['kind_label']), m(x['summary']['fmv_T']), '%s / %s' % (m(x['summary']['tax_live_T']), m(x['summary']['tax_rent_T'])),
         m(x['summary']['real_live']), m(x['summary']['real_rent']), m(x['summary']['real_sell']), NAME[x['summary']['best']],
         (src('FRED-JP') if x['key'] == 'japan_at_T' else src('FHFA-SJ', 'BLS-CPI') + ' · ' + src('DAMODARAN'))]
        for x in M['paths']
    ] + [['Baseline (constant rates)', 'Baseline assumption (constant rates), kept apart from the stress paths', m(B['fmv_T']), '%s / %s' % (m(B['tax_live_T']), m(B['tax_rent_T'])), m(B['real_live']), m(B['real_rent']), m(B['real_sell']), NAME[B['best']], src('FHFA-SJ', 'BLS-CPI')]],
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
    body = ("""<p class="callout">This section is kept apart from the baseline on purpose. The baseline uses constant rates so that the three choices can be compared cleanly. Here nothing is constant: every path uses real recorded years, in their real order, for inflation, local home prices, stocks, bonds and bills. Read the provenance table first: official statistics, the academic return dataset and the hypothetical constructions below are three different kinds of material.</p>"""
            + prov + rep + named + '<h2>Property A market value in 2026 dollars under six paths</h2>' + ch + stats + other + yr + yr2 + hist)
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
        ['10', 'Within 1 year, only if moving in', 'Make Property A the Inheritor\'s principal residence and file for the homeowners\' exemption (form BOE-266) before filing the exclusion claim.', 'Without both, the Proposition 19 exclusion is not available and the home is reassessed at full market value. BOE Pub. 800-1 notes BOE-266 must be filed before BOE-19-P.', src('RTC-63.2', 'BOE-LTA-2026-026', 'BOE-PUB-800-1')],
        ['11', 'Within 3 years, only if moving in', 'File the parent-child exclusion claim (form BOE-19-P) with the Assessor, before any transfer to a third party (or within 6 months of a supplemental/escape notice).', 'Late claims receive prospective relief only; moving out later ends the exclusion on the next January 1 lien date and enrolls the date-of-death market value indexed for inflation. ' + flag('S03'), src('BOE-P19', 'SCC-P19', 'BOE-PUB-800-1')],
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
        ['Schedule A state &amp; local tax (SALT) deduction cap', 'P.L. 119-21 raised the cap to $40,000 (2025) / $40,400 (2026), phasing down above $500,000 MAGI to a $10,000 floor, and reverting to $10,000 after 2029 unless extended', 'Schedule E rental property taxes on a let unit or Property B are uncapped business deductions; Schedule A itemized deductions revert to $10,000 well before 2045 under current law.', src('IRS-SCHED-A', 'IRS-P527')],
    ], caption='Federal law in force')
    ca = table(['California rule', 'Current figure', 'Effect on this case', 'Official basis'], [
        ['Estate and inheritance tax', 'None for deaths on or after 2005-01-01', 'No state tax on Property A or the cash at death.', src('SCO-ESTATE')],
        ['Parent-child exclusion (Proposition 19)', 'Only for the Transferor\'s principal residence that becomes the child\'s principal residence within one year', 'Renting or holding Property A means full reassessment.', src('BOE-P19', 'RTC-63.2')],
        ['Value limit', 'Assessed value plus $1,044,586 for transfers from 2025-02-16 to 2027-02-15', 'Above the limit the excess is added to the assessed value.', src('BOE-LTA-2025-009')],
        ['How the limit grows', 'Every second February 16, by the California house-price change of the prior calendar year only', 'It grows about half as fast as home prices, so the relief shrinks over time. ' + flag('A03'), src('BOE-LTA-2025-009')],
        ['Continual-use rule', 'If the child stops using the home as a principal residence the exclusion ends on the next January 1 lien date and the date-of-death market value (indexed) is enrolled', 'Moving out later ends the relief; BOE-266 must be filed before BOE-19-P.', src('BOE-LTA-2026-026', 'RTC-63.2', 'BOE-PUB-800-1')],
        ['Homeowners\' exemption', '$7,000 off the assessed value of a principal residence', 'About $80 a year; needed to qualify for the exclusion.', src('BOE-HOX')],
        ['Date of change in ownership for a revocable trust', 'The date the trust becomes irrevocable (the date of death)', 'Starts every property-tax deadline.', src('BOE-RULE-462.260')],
        ['Change-in-ownership statement at death', 'Within 150 days of the date of death', 'Missed filings lead to a penalty.', src('RTC-480')],
        ['Trustee notification', 'Within 60 days; 120-day contest period', 'A duty of the successor trustee.', src('PROB-16061.7')],
        ['State income tax on gains', 'Taxed as ordinary income: 9.3% above $72,724, up to 12.3% above $742,953 (single, 2025), plus 1% Behavioral Health Services Tax (renamed from Mental Health Services Tax in 2025) above $1,000,000', 'Applies to any gain on Property B and to later gains on Property A or on investments.', src('FTB-RATES', 'FTB-MHS')],
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
        ['San Francisco water and sewer rates', 'Water +7.0%/yr, residential wastewater +10.8% (FY26-27) and +10.1% (FY27-28), stormwater charge phase-in; combined average SF residential bill +10.5% and +12.5%', 'Raises the largest utility bill at Property B.', src('SFPUC', 'SFPUC-RFB')],
        ['Cupertino water service providers', 'Three separate providers cover Cupertino: California Water Service (NE), San Jose Water Company (SE), and Cupertino Municipal Water System (W, leased to SJWC through 2036)', 'Confirm which utility serves Property A before forecasting future water hikes. ' + flag('U05'), src('CUP-WATER')],
    ], caption='Local rules in force')
    pend = table(['Change', 'Level', 'Status read on %s' % READ_DATE, 'Effect if it happens', 'Official basis'], [
        ['Indexing of the estate exclusion', 'Federal', 'In force. 2027 figure published 2026-11-05.', 'The exclusion rises each year with inflation; the model projects %s by %d.' % (m(B['exclusion_T']), T), src('RP-2026-35', 'IRS-NEW')],
        ['Temporary SALT cap increase and 2030 reversion (P.L. 119-21)', 'Federal', 'Enacted for 2025-2029 ($40,000 in 2025; $40,400 in 2026), reverting to $10,000 in 2030 unless extended.', 'Would alter Schedule A itemized tax deductions only if Congress extends it before 2045; does not cap Schedule E rental taxes.', src('IRS-SCHED-A')],
        ['Death Tax Repeal Act (S.587 and H.R.1301)', 'Federal', 'Introduced 2025-02-13 and referred to committee. No later action shown.', 'Would repeal the estate tax. No effect on the property-tax or income-tax results.', src('CONG-S587', 'CONG-HR1301')],
        ['Any reduction of the exclusion or of the basis reset', 'Federal', 'No enacted measure found. Would need a new Act of Congress.', 'See the stress rows on the Cash and Black swan pages.', src('IRS-NEW')],
        ['Next adjustment of the Proposition 19 allowance', 'California', 'Scheduled for 2027-02-16, using the 2026 California house-price change. Figure: ' + BLANK + ' ' + flag('U04'), 'Sets the allowance for transfers through 2029-02-15.', src('BOE-LTA-2025-009')],
        ['Proposition 3 (extends the existing tax on high incomes)', 'California', 'Yes 60.7% in unofficial returns as of 2026-11-11 6:51 p.m.; certification due by 2026-12-11.', 'Would keep the existing higher state rates on high incomes, which reach a large one-year gain. Details are in the voter guide.', src('SOS-RESULTS')],
        ['Proposition 40 (one-time tax on certain taxpayers)', 'California', 'No 52.5% in unofficial returns as of 2026-11-11 6:51 p.m.', 'None if the result holds.', src('SOS-RESULTS')],
        ['Proposition 42 (bars new state personal-property taxes and certain retroactive taxes)', 'California', 'Yes 51.4% in unofficial returns as of 2026-11-11 6:51 p.m.', 'Would bar new state taxes on personal property; relevant to invested sale proceeds if the result holds.', src('SOS-RESULTS')],
        ['Measure to undo the Proposition 19 inheritance rules', 'California', 'Reported by non-official websites as a signature drive. Not among the measures on the November 2026 ballot. ' + flag('S04'), 'Would restore relief for rented inherited homes.', src('SOS-RESULTS')],
        ['Limit on banked and capital-improvement rent increases (File No. 261020)', 'San Francisco', 'Not enacted; Pending Committee Action at the Board of Supervisors (introduced 2026-09-15; Rent Board notice posted 2026-11-09, read 2026-11-12).', 'Would cap banked and capital-improvement rent increases at 10%% a year for three years on notices served on or after 2026-09-15 if Property B is rent-controlled (%s). No effect on Property A.' % flag('Q04'), src('SF-RENT-RULES', 'SF-LEG-261020')],
        ['Empty Homes Tax appeal', 'San Francisco', 'City lost on appeal; no collection unless reversed.', 'If revived, a charge on the unit kept empty.', src('SF-EHT')],
        ['Residential fixed charge on electricity bills', 'California', 'Adopted: $24.15 a month for standard customers.', 'May reduce or remove the monthly solar credit at Property A.', src('CPUC-FIXED')],
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
        ['Official statewide yardstick', 'About $1,130 a policy in 2023 across all residential policy forms, with an average insured building value of about $324,970. Homeowners policies averaged $1,176 over 2008-2023.', 'Landlord (tenant-occupied dwelling-fire) policies averaged $601 over 2008-2023, statewide.', src('CDI-SB824', 'CDI-RPI')],
        ['What the yardstick suggests', 'The owner estimate is of the right order, but a home of this value insures a building worth far more than the state average, so a real quote may be higher.', 'The owner estimate is above the long-run statewide landlord average; a three-unit building in San Francisco may still cost more.', src('CDI-SB824', 'CDI-RPI')],
        ['Owner\'s own estimate used in the model', m(P['ins_home']) + ' a year', m(P['ins_rental']) + ' a year', src('CDI-TOOL')],
        ['Does a wrong estimate change the decision?', 'No. Tripling it lowers the Live result by %s and leaves the ranking unchanged' % m(M['sensitivity'][0]['real_live'] - M['sensitivity'][15]['real_live']), 'No. Property B is the same in all three choices', src('CDI-TOOL')],
        ['Wildfire surcharge', '15% to over 300% in higher-risk areas, not shown in the survey. Whether it applies to this home: ' + BLANK, 'Same', src('CDI-TOOL-APP')],
        ['Earthquake', 'Not covered by a homeowners policy; must be offered every other year. Premium: ' + BLANK + ' ' + flag('U02'), 'Same for a landlord policy; confirm with the insurer', src('CDI-EQ', 'USGS')],
        ['Vacancy', 'Losses to a house vacant 60 days or more are generally excluded; flood, earth movement, mold and wear/tear are also excluded', 'Applies to the unit kept empty if it is truly vacant', src('CDI-RES')],
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
        ['Water', '%s a year (owner: $100 to $150 a month; 3 Cupertino providers exist)' % m(P['cup_water']), '%s a year for three units (owner: $330 to $400 a month)' % m(P['sf_water']), 'inflation + 2 points; Property B combined residential bill +10.5% in FY26-27 and +12.5% in FY27-28 ' + flag('U05'), src('SFPUC', 'SFPUC-RFB', 'CUP-WATER')],
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

    p3 = [
        ('Form 706 Table A rate schedule &amp; 2026 Instructions',
         'Instructions for Form 706 (Rev. 07/2026) Table A confirms $345,800 base tax on $1,000,000 plus 40% above $1,000,000',
         'Upgraded IRS-I706 from search excerpt to full page', src('IRS-I706')),
        ('Publication 559 &amp; Form 1041 trust threshold',
         'Bequests are excluded from recipient gross income; Form 1041 required above $600 of fiduciary gross income; IRD and post-death income remain taxable',
         'Upgraded IRS-P559 and IRS-1041 from excerpt to full page', src('IRS-P559', 'IRS-1041')),
        ('Publication 527 residential rental depreciation',
         'Residential rental buildings placed in service after 1986 depreciate over 27.5 years (GDS) or 30 years (ADS) on the lesser of adjusted basis or date-placed-in-service FMV',
         'Upgraded IRS-P527 from excerpt to full page', src('IRS-P527')),
        ('Schedule A SALT deduction cap (P.L. 119-21)',
         'Instructions for Schedule A confirm $40,000 (2025) / $40,400 (2026) SALT cap phasing down above $500,000 MAGI to $10,000 floor, reverting to $10,000 after 2029; Schedule E rental property taxes remain uncapped',
         'Added IRS-SCHED-A and noted on Law &amp; Site improvements', src('IRS-SCHED-A')),
        ('California 1% millionaire surtax rename (2025+)',
         'FTB 2025 540 Booklet confirms the 1% tax over $1,000,000 was renamed from Mental Health Services Tax to Behavioral Health Services Tax',
         'Upgraded FTB-MHS to 2025-540-booklet.html and updated Law &amp; Flagged', src('FTB-MHS')),
        ('BOE Publication 800-1 Prop 19 procedural rules',
         'BOE-266 homeowners\' exemption must be filed before BOE-19-P; claims timely within 3 years or 6 months of supplemental notice; move-out ends exclusion on next Jan 1 lien date (date-of-death FMV indexed)',
         'Added BOE-PUB-800-1 and updated Process &amp; Law', src('BOE-PUB-800-1')),
        ('Tenant Protection Act, CDI Form 401 &amp; Congress bills',
         'AB 1482/SB 567 caps rent at 5% + CPI (max 10%) with SFH/owner-move-in rules; CDI Form 401 confirms 60-day vacancy, flood, quake &amp; mold exclusions; S.587/H.R.1301 remain Introduced',
         'Upgraded DOJ-TPA, CDI-RES, CONG-S587, CONG-HR1301 to full page', src('DOJ-TPA', 'CDI-RES', 'CONG-S587', 'CONG-HR1301')),
        ('CPUC NEM legacy, $24.15/mo Base Services Charge &amp; Cupertino/SF water',
         'CPUC confirms 20-yr NEM 2.0 / 9-yr NBT and $24.15/mo PG&amp;E Tier 3 fixed charge; Cupertino splits across 3 water providers (Cal Water, SJWC, Municipal leased to SJWC through 2036); SFPUC average combined residential bill +10.5% FY26-27 and +12.5% FY27-28',
         'Upgraded CPUC-NEM, CPUC-FIXED, SFPUC and added CUP-WATER &amp; SFPUC-RFB', src('CPUC-NEM', 'CPUC-FIXED', 'CUP-WATER', 'SFPUC', 'SFPUC-RFB')),
        ('CBO long-term outlook, USGS quake odds &amp; Nov 11 ballot update',
         'CBO Feb 2026 shows 2.7%->2.0% PCE &amp; 4.1%->4.3% 10Y; USGS 72% Bay Area M>=6.7 (2014-2043); CA SOS Nov 11 6:51 p.m. shows Prop 3 Yes 60.7%, Prop 40 No 52.5%, Prop 42 Yes 51.4%, and no Prop 19 repeal on Nov 2026 ballot',
         'Upgraded CBO &amp; USGS to full page and refreshed SOS-RESULTS', src('CBO', 'USGS', 'SOS-RESULTS')),
        ('SEC guides, State Bar specialists, Santa Clara BOE-19-P, FY27 FMR notice, SF File #261020 &amp; Digital.gov',
         'Opened all 8 additional official URLs from session 0adc9b0a directly: SEC Ten Things &amp; Asset Allocation, CalBar 11 specialties, Santa Clara Prop 19 estimator &amp; BOE-19-P REV.04, 91 FR 56156, SF File #261020 Pending Committee Action, and Digital.gov plain-language guide',
         'Upgraded SEC-TEN, SEC-ALLOC, CALBAR-SPEC, SCC-P19-EST, CAPF-BOE19P, FR-FMR-2027, SF-LEG-261020, DIGITAL-GOV to full page (zero official excerpts remain)',
         src('SEC-TEN', 'SEC-ALLOC', 'CALBAR-SPEC', 'CAPF-BOE19P', 'FR-FMR-2027', 'SF-LEG-261020', 'DIGITAL-GOV')),
    ]
    t5 = table(['What was checked', 'What the direct full-page read established', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in p3],
               caption='Full-page verification pass, 2026-11-12 (session a6ec5b1d): direct read of all formerly-excerpt official sources and new records')

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
    t6 = table(['What was checked', 'What the official page said when it was opened', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in x],
               caption='Fourth re-read, 2026-11-12 (session 0adc9b0a), on the official pages themselves')
    f5 = [
        ('Proposition 13 inflation factor (re-read 2026-11-13)',
         'BOE LTA 2026/002 of 2026-01-13: "please prepare your 2026 assessment roll using an inflation factor of 1.02"; the CCPI rose 3.307 percent from August 2024 to August 2025 (October 2025 CCPI was not published due to the federal shutdown) and the increase is capped at 2 percent. R&amp;TC 51 (re-read the same day): the inflation factor is the October-to-October change in the California CPI and "in no event shall the percentage increase ... exceed 2 percent of the prior year\'s value".',
         'Confirmed on the pages. The model\'s future factor is each path\'s inflation rate and is now explicitly labelled a proxy for the California CPI %s; the statutory rule and the official 2026 factor are quoted beside it (S5-P3).' % flag('A11'),
         src('RTC-51', 'BOE-LTA-2026-002')),
        ('HUD rent standards, ZIP 95014 and 94122 (re-read 2026-11-13)',
         'FY2026 Small Area Fair Market Rents: 95014 - two-bedroom $4,440, three-bedroom $5,870, four-bedroom $6,390; 94122 - two-bedroom $3,310, three-bedroom $4,230, four-bedroom $4,380. HUD derives the standard from the 40th-percentile gross rent, adjusted.',
         'Confirmed on the pages; the full bedroom-size tables read this time match every figure quoted on the site. The four-bedroom figure is now labelled a benchmark, not a verified rent for Property A %s, with the three-bedroom figure kept as the downside gate. The fiscal year 2027 lookup remains unread %s.' % (flag('U08'), flag('U09')),
         src('HUD-95014', 'HUD-94122', 'HUD-SAFMR-INDEX')),
        ('Baseline rent for the vacated third unit at Property B',
         'No official page supplies a rent for the third unit. The brief says never infer a value, and the no-figures guide\'s own method rule says: do not invent a new tenancy, rent for a vacated space, title status or legal-unit status.',
         'Corrected (S5-P1): the baseline counts no third-unit rent. The upside of letting it at the average of the two known unit rents now appears only as one labelled sensitivity scenario.',
         src('SF-RENT-RULES', 'HUD-94122')),
        ('Provenance of the Black swan series',
         'The stock, bond and bill return series is an academic dataset (NYU Stern), not a government statistic; the CPI and house-price indexes are official (BLS, FHFA); the Japan path uses official foreign series through FRED.',
         'Corrected (S5-P4): the Black swan page opens with a provenance table separating official statistics, the academic dataset and the hypothetical constructions, and every named path carries a Kind label.',
         src('BLS-CPI', 'FHFA-SJ') + ' &middot; ' + src('DAMODARAN')),
        ('Figures on the Suggestions page, Part 1',
         'Model-derived figures must be generated from the model data rather than typed into the page text, so the review page cannot drift from the model.',
         'Corrected (S5-P5): the HUD three-bedroom figure and the SALT cap amounts are now read from the model parameter set.',
         src('HUD-95014', 'IRS-SCHED-A')),
        ('Page text and menu after earlier merges',
         'A conflict marker and a truncated duplicated sentence had been left in this page\'s own text; the Questions and Suggestions pages each appeared twice in the page menu; the source register carried a stray trailing period on the R&amp;TC 51 link.',
         'Corrected 2026-11-13 (findings R38, R44 and R45 on the Repo review page).',
         src('RTC-51')),
    ]
    t7 = table(['What was checked', 'What the official page says (or why nothing can confirm it)', 'Result', 'Official page'],
               [[a, b_, c, d] for a, b_, c, d in f5],
               caption='Fifth pass, 2026-11-13 (session da3f2b99): direct re-read of the sources behind the corrected claims, and the corrections themselves')
    r8 = [
        ('Federal basic exclusion for 2027', 'Rev. Proc. 2026-35 section 3.44: the basic exclusion amount under section 2010(c)(3) is $15,480,000 for calendar year 2027; section 3.46(1): the first $20,000 of gifts to any person is excluded for 2027',
         'Confirmed today word for word - the same figures the estate projections use', src('RP-2026-35')),
        ('The 2026 exclusion is statutory, and how it is indexed', '26 U.S.C. 2010(c)(3): the basic exclusion amount is $15,000,000, increased after 2026 by a cost-of-living adjustment and rounded to the nearest multiple of $10,000, by Pub. L. 119-21 section 70106(a) (2025-07-04)',
         'Confirmed today - the statute behind the projection method', src('IRS-NEW')),
        ('Basis of inherited property', 'Fair market value on the date of death, or on the alternate valuation date if a Form 706 is filed and the election is made; a sale above basis is a taxable gain',
         'Confirmed today - the rule the Sell result depends on, subject to %s' % flag('Q01'), src('IRS-FAQ-INHERIT')),
        ('Capital-gain rates and the loss limit', '0%, 15% or 20% by taxable income for 2025; unrecaptured section 1250 gain at up to 25%; the capital-loss deduction is limited to $3,000 ($1,500 if married filing separately) a year',
         'Confirmed today - the loss limit bears on flag %s (selling-cost loss)' % flag('Q17'), src('IRS-TC409')),
        ('California estate and inheritance tax', 'No California estate tax return is required for decedents dying on or after 2005-01-01; the state death tax credit was eliminated from that date; inheritance tax is collected only for deaths before 1982-06-08',
         'Confirmed today - California adds no death tax', src('SCO-ESTATE')),
        ('Proposition 19 allowance in force', 'LTA 2025/009: $1,044,586 for transfers from 2025-02-16 through 2027-02-15 (2.15% up from $1,022,600); the next adjustment is February 2027',
         'Confirmed today - the model input; the next figure stays blank %s' % flag('U04'), src('BOE-LTA-2025-009')),
        ('Proposition 19 conditions and claim deadlines', 'LTA 2026/026: the exemption claim within one year of the transfer, the exclusion claim within three years or before a third-party transfer; no exceptions to the one-year occupancy rule; the exclusion is removed if the child moves out; transfers through a trust are covered',
         'Confirmed today - the deadlines the Process page states. The order the site recommends is practical advice only (%s)' % flag('R43'), src('BOE-LTA-2026-026')),
        ('Proposition 19: land included in the family home', 'LTA 2026/026 defines a family home as the dwelling plus only that portion of the land of a reasonable size used as its site; of a multi-unit property only the unit occupied as a principal residence qualifies',
         'Confirmed today - the model applies the exclusion to the whole parcel, flagged as %s' % flag('R42'), src('BOE-LTA-2026-026')),
        ('Proposition 19 statute', 'R&TC 63.2(a)(1)(A)-(C): transferee must occupy within one year and claim the exemption within a year; the base year value is re-enrolled if the exclusion is later lost',
         'Confirmed today - matches the Board of Equalization letter', src('RTC-63.2')),
        ("Homeowners' exemption", '$7,000 off the taxable value for an owner-occupied home; one-time claim, form BOE-266; file no later than February 15 for the full year',
         'Confirmed today', src('BOE-HOX')),
        ('San Francisco secured property-tax rate', 'The secured property tax rate for fiscal year 2026-27 is 1.18162182%; the page also confirms that a change in ownership requires the Assessor-Recorder to reappraise',
         'Confirmed today. The 2025-26 rate used in the model could not be read today and stays flagged %s' % flag('U07'), src('SF-TAX')),
        ('San Francisco rent increase and the pending cap', 'The allowed annual increase is 1.6% from 2026-03-01 through 2027-02-28 (60% of Bay Area CPI). A notice posted 2026-11-09 describes File No. 261020, which would cap combined banked and capital-improvement increases at 10% a year; it has not been enacted',
         'Confirmed today - matches the Law page, which lists the cap as a proposal', src('SF-RENT-RULES', 'SF-LEG-261020')),
        ('Net metering: the 20-year limit behind the solar credit', 'CPUC: NEM 2.0 customers remain on that tariff for 20 years from interconnection (D.14-03-041); the successor net-billing tariff pays export credits usually lower than the retail rate',
         'Confirmed today. The model carries the credit for 50 years - flagged as %s' % flag('R41'), src('CPUC-NEM')),
        ('Insurance premiums by ZIP', 'The Department of Insurance comparison tool states that its figures are hypothetical risks for illustration, that wildfire surcharges of 15% to over 300% are not reflected, and that an exact premium requires an agent, broker or insurer quote',
         'Confirmed today - the reason both insurance amounts stay blank and flagged (%s, %s)' % (flag('U01'), flag('U02')), src('CDI-TOOL-APP')),
        ('HUD rents for fiscal year 2027', 'The fiscal-year-2027 address in the same documentation format as the 2026 page returned "404 - File or directory not found" when opened today',
         'Not confirmable today: the 2027 figure stays blank %s and the 2026 figure remains in use' % flag('U09'), src('HUD-SAFMR-INDEX')),
    ]
    r8 = [(a, b_, c_.replace(flag('R39'), '<a class="flag" href="review.html#R39">R39</a>')
                              .replace(flag('R40'), '<a class="flag" href="review.html#R40">R40</a>')
                              .replace(flag('R41'), '<a class="flag" href="review.html#R41">R41</a>')
                              .replace(flag('R42'), '<a class="flag" href="review.html#R42">R42</a>')
                              .replace(flag('R43'), '<a class="flag" href="review.html#R43">R43</a>'), d) for a, b_, c_, d in r8]
    t8 = table(['What was checked', 'What the official page said when it was opened', 'Result', 'Official page'], r8,
               caption='Fifth independent re-read, 2026-11-13 (session arena/f8de1d0b), on the official pages themselves')

    body = """
<p class="callout">This page is the manual-review register for the whole site: one row per check, with the government page to open and re-read. Pass 1 was checked on 2026-11-11 (session faccd46d); Pass 2 re-opened the twelve core pages on 2026-11-12 (session e8636cac); subsequent same-day passes by sessions <code>3e79fc01</code>, <code>0adc9b0a</code>, and <code>a6ec5b1d</code> checked remaining official agency pages directly (leaving zero official agency excerpt entries in the register). Anything that cannot be confirmed from an agency page stays blank or labelled and carries a flag.</p>
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
<p class="note">The third and fourth re-reads were made on the same day; both are kept and agree wherever they cover the same official page.</p>
%s
<h2>Full-page direct read of remaining official sources, 2026-11-12 (session a6ec5b1d)</h2>
%s
<h2>Fifth pass, 2026-11-13 (session da3f2b99): model and provenance corrections</h2>
%s
<h2>Fifth independent re-read, 2026-11-13 (session arena/f8de1d0b)</h2>
%s
<p class="note">This pass re-opened the federal, California and local pages above on their own agency URLs. Two of them changed the picture rather than confirming it: the CPUC page limits the net-metering tariff behind the solar credit to 20 years, and the Department of Insurance tool states that its figures are illustrations rather than quotes. Both are recorded as flags. What was not re-opened today stands on the earlier passes and keeps its links.</p>
<p class="note"><strong>Coverage summary.</strong> Across the passes above, every official agency source in <a href="sources.html">Sources and method</a> has now been opened and read directly on its agency URL (only the non-government stock/bill dataset, Damodaran, remains labelled academic). The interactive CDI insurance survey and HUD FY2027 lookup require interactive form/spreadsheet access not resolved in automation, so those parcel values remain blank.</p>
<p class="note"><strong>What this pass does not establish.</strong> Model outputs and projections are conditional scenarios built on the assumptions in the flags; no official page can verify a forecast. The automated checker (<a href="%s/blob/main/final/check.py">final/check.py</a>) proves only that every table row carries an official link, that dollar figures are rounded to $10, and that no personal identifier pattern appears (no fingerprint of unrounded owner figures is stored; that extra scan runs only with a private local file) - it does not prove that each link supports each cell. This register exists so every claim can be checked by hand against its link. People remain placeholders (the Transferor, the Inheritor); no names, addresses or parcel numbers appear anywhere.</p>
""" % (t1, t2, t3, t4, tw3, render_verification(src, table, flag), t6, t5, t7, t8, REPO)
    page('verification.html', 'Verification',
         'Verification passes (2026-11-11 register, four re-reads on 2026-11-12, and the full-page direct read): every official source read directly on its agency page, each check linked for manual review, and everything unconfirmable left blank and flagged.', body)


# ====================================================================== questions & discovery
def build_questions():
    ku = [
        ['Transferor\'s Property A status &amp; rounded starting inputs',
         'Known (owner-supplied): Property A is the Transferor\'s principal residence in Cupertino (ZIP 95014), with rounded 2026 market value %s, assessed value %s, and 2025 tax bill %s.' % (m(P['cup_value']), m(P['cup_assessed']), m(P['cup_tax_2025'])),
         'Unknown: Whether the holding trust is revocable or an irrevocable grantor trust outside the gross estate, and exact date of Transferor\'s death (modeled 2040-2050).',
         'Check the recorded deed and trust certification with an estate attorney (%s).' % flag('Q01'),
         src('RR-2023-2', 'BOE-RULE-462.260')],
        ['Property B ownership &amp; San Francisco baseline',
         'Known (owner-supplied &amp; official SF rate): Already owned by the Inheritor (2 units let for %s/mo combined, 3rd unit occupied/held), assessed at %s (2026), SF rate 1.18162182%%.' % (m(P['sf_rent_2units'] / 12), m(P['sf_assessed'])),
         'Unknown: Whether Property B falls under SF rent control (pre-1979 vs. post-1979 / condo status), and whether the Inheritor would actually re-rent the 3rd unit or sell Property B.',
         'Look up permit/certificate of occupancy date and SF Rent Board status (%s).' % flag('Q04'),
         src('SF-TAX', 'SF-RENT-RULES', 'SF-RENT-LAW')],
        ['Estate size, cash, and spousal portability',
         'Known (statutory): Federal estate-tax basic exclusion is $15,000,000 (2026) and $15,480,000 (2027), indexed for inflation; California charges zero estate or inheritance tax.',
         'Unknown: Total expected cash and non-house estate assets, retirement accounts (tax-deferred IRAs), and whether a predeceased spouse\'s unused exclusion (DSUE) was ported via Form 706.',
         'Inventory brokerage/IRA statements and locate any prior Form 706 (%s).' % flag('Q02'),
         src('IRS-ESTATE', 'RP-2026-35', 'IRS-FAQ-ESTATE')],
        ['Property A parcel tax rate area &amp; fixed charges',
         'Known (county rate table + rounded bill): Cupertino components sum to 1.16360%%, leaving about %s/yr in derived parcel fixed charges (%s).' % (m(P['dc_cup']), flag('U03')),
         'Unknown: Exact Tax Rate Area (TRA) code on the Santa Clara County secured bill and whether parcel assessments are fixed-dollar or expire on a bond schedule.',
         'Read the 4-digit TRA and itemized parcel line items directly off the Santa Clara County tax bill.',
         src('SCC-RATES')],
        ['Cupertino utilities: solar NEM &amp; water service provider',
         'Known (owner monthly ranges &amp; CPUC/city records): Solar credit $10-$20/mo; water $100-$150/mo; PG&amp;E added a $24.15/mo Base Services Charge and Cupertino splits across three water utilities.',
         'Unknown: Solar Permission-to-Operate (PTO) date (determines when 20-year NEM 2.0 grandfathering expires) and which of Cupertino\'s 3 water utilities serves Property A.',
         'Pull the PG&amp;E interconnection agreement and check Property A on Cupertino\'s water provider map (%s).' % flag('U05'),
         src('CPUC-NEM', 'CPUC-FIXED', 'CUP-WATER')],
        ['Homeowners &amp; landlord insurance quotes + vacancy/quake coverage',
         'Known (owner estimate &amp; CDI survey): Owner estimates %s/yr (Cupertino) and %s/yr (SF); CDI interactive tool cannot show non-hypothetical quotes and homeowners policies exclude quake and 60+ day vacancy.' % (m(P['ins_home']), m(P['ins_rental'])),
         'Unknown: Actual current carrier declarations, wildfire/FAIR Plan surcharge risk, and earthquake insurance quote for Property A or 3-unit landlord quote for Property B.',
         'Request written replacement-cost, landlord (DP-3), vacancy, and CEA earthquake quotes from two brokers (%s, %s).' % (flag('U01'), flag('U02')),
         src('CDI-TOOL', 'CDI-RES', 'CDI-EQ')],
        ['Proposition 19 allowance &amp; Inheritor tax bracket',
         'Known (BOE rules): Current allowance is FBYV + $1,044,586 (through 2027-02-15); BOE-266 homeowners\' exemption must be filed before BOE-19-P; moving out later cancels exclusion next Jan 1.',
         'Unknown: Future post-2027 allowance index adjustments (%s) and Inheritor\'s actual marginal bracket &amp; filing status (single vs. married) when income/gains are realized (%s).' % (flag('U04'), flag('Q05')),
         'Confirm Inheritor\'s expected income tier, marital status, and holding-period commitment with a CPA.',
         src('BOE-LTA-2025-009', 'BOE-PUB-800-1', 'RP-2026-35')],
    ]
    t1 = table(['Topic', 'What is already known', 'What remains unknown', 'How to confirm', 'Official basis'],
               ku, caption='Known vs. unknown facts across the estate and both properties')

    qa = [
        ['1. Trust type &amp; estate inclusion (%s)' % flag('Q01'),
         'Does the trust holding Property A sit inside the Transferor\'s gross estate at death (e.g., revocable living trust), or is it an irrevocable trust excluded from the gross estate?',
         'Changes Sell &amp; Reinvest outcome by hundreds of thousands to over $1,000,000+ because Rev. Rul. 2023-2 denies the IRC 1014 basis step-up if outside the estate.',
         'Have an estate attorney read the full trust instrument, any amendments/restatements, and the recorded vesting deed (usually takes 1-2 hours).',
         src('RR-2023-2', 'IRS-FAQ-INHERIT')],
        ['2. Transferor\'s cash, brokerage &amp; retirement assets (%s)' % flag('Q02'),
         'Roughly how much non-real-estate wealth will be in the estate, how much sits in pre-tax retirement accounts (401k/IRA), and did an earlier spouse leave a Form 706 portability election?',
         'Tests whether the estate breaches the federal threshold (%s baseline room in %d with one exclusion) and flags 10-year SECURE Act income tax on inherited IRAs.' % (m(B['exclusion_T'] - B['fmv_T']), T),
         'Create a confidential net-worth summary (do NOT commit exact balances to a public repo) and ask whether Form 706 was ever filed for a prior spouse (check 5-yr Rev. Proc. 2022-32 window if recent).',
         src('IRS-ESTATE', 'IRS-P559', 'IRS-FAQ-ESTATE')],
        ['3. Inheritor\'s personal housing commitment (%s)' % flag('Q04'),
         'If the Inheritor moves into Property A to claim Prop 19 relief, will they genuinely live there continuously as their primary residence for 10+ years, and would they rent out their vacated SF unit?',
         'BOE Pub. 800-1 makes clear that moving out removes the Prop 19 cap on the next Jan 1 lien date and enrolls indexed date-of-death FMV; skipping SF unit rental drops Live wealth sharply.',
         'Stress-test lifestyle, commute, and SF Rent Board registration/buyout rules on the vacated Property B unit before counting on either Prop 19 savings or market rent on Unit 3.',
         src('BOE-PUB-800-1', 'SF-RENT-RULES')],
        ['4. Inheritor\'s tax profile &amp; residency (%s)' % flag('Q05'),
         'What are the Inheritor\'s filing status (single vs. married filing jointly), California vs. out-of-state residency, and ordinary/capital-gains bracket at inheritance?',
         'Alters NIIT threshold ($200,000 single / $250,000 joint), CA top brackets (13.3% / 14.3% including Behavioral Health Services Tax), and whether 15% vs. 20% federal LTCG applies.',
         'Share a single tax-bracket range with the CPA (without putting tax returns online) and re-run sensitivity with joint or non-CA assumptions if relevant.',
         src('FTB-MHS', 'IRS-TC559', 'IRS-TC409')],
        ['5. Exact utility, tax-bill &amp; repair reality (%s, %s, %s)' % (flag('U03'), flag('U05'), flag('A08')),
         'Which Santa Clara TRA code is on Property A\'s bill, which of the 3 Cupertino water utilities serves the parcel, when does PG&amp;E NEM 2.0 end, and what major capex (roof, HVAC, sewer lateral) awaits?',
         'Prevents surprises in Rent or Live holding costs (e.g., losing solar credits after 20 years, or underestimating capex on aging systems).',
         'Download 12 months of Santa Clara &amp; SF secured tax bills, PG&amp;E green-button PDF (shows NEM tariff &amp; PTO date), Cupertino water map lookup, and get a rough 10-year home inspection budget.',
         src('SCC-RATES', 'CUP-WATER', 'CPUC-NEM')],
        ['6. Insurance &amp; vacancy plan during transition (%s, %s)' % (flag('U01'), flag('U02')),
         'What do actual brokers quote for Property A (homeowners vs. DP-3 landlord + vacancy endorsement) and Property B (3-unit landlord), plus earthquake deductible options?',
         'California carriers have tightened 95014/94122 underwriting; standard homeowners policies cut off cover after 60 days of vacancy while waiting to close a sale or place a tenant.',
         'Call current insurers plus an independent California broker for ballpark replacement-cost and DP-3 quotes, and ask about short-term estate/vacancy endorsements for the post-death transition.',
         src('CDI-RES', 'CDI-TOOL', 'CDI-EQ')],
        ['7. Parent-child relationship, Property A bedrooms/rent &amp; Property B basis (%s, %s, %s)' % (flag('Q06'), flag('U08'), flag('Q03')),
         'Does the family relationship meet BOE Pub. 800-1 definitions, how many rentable bedrooms does Property A have vs. HUD benchmarks, and what is the Inheritor\'s cost/depreciation basis in Property B?',
         'Only qualifying children/stepchildren/in-laws get Prop 19 relief; rental break-even shifts with market rent; Property B basis matters if Property B were ever sold.',
         'Confirm relationship with the attorney, get a written local rent opinion matching Property A\'s layout, and keep Property B\'s closing &amp; Schedule E depreciation files privately with the CPA.',
         src('BOE-PUB-800-1', 'HUD-95014', 'IRS-TC409')],
        ['8. Principal residence at death, marital delay, selling-cost loss &amp; exemption home (%s, %s, %s, %s)' % (flag('Q15'), flag('Q16'), flag('Q17'), flag('Q18')),
         'Is Property A the Transferor\'s principal residence at death, does a surviving spouse/marital trust delay title, is a prompt-sale selling-cost loss deductible, and which home currently carries the $7,000 homeowners exemption?',
         'Prop 19 fails without Transferor principal residence; marital trusts change transfer timing; selling-cost losses are currently modeled as non-deductible cash outlays.',
         'Inspect both secured tax bills privately for the $7,000 exemption line, ask estate counsel on marital/transfer timing, and confirm prompt-sale loss treatment in writing with the CPA.',
         src('BOE-LTA-2026-026', 'IRS-ESTATE', 'IRS-TC701', 'BOE-HOX')],
    ]
    t2 = table(['Question &amp; flag', 'Exact answer needed before deciding', 'Why it matters to the answer', 'Concrete way to discover it', 'Official basis'],
               qa, caption='Questions to answer before making a final decision, and how to find each missing fact')

    plan = [
        ['Now (while Transferor is living)',
         'Confirm trust type (Q01), prior spouse portability (Q02), and rough estate total; verify Transferor keeps Property A homeowners\' exemption (BOE-266) active.',
         'High: determines step-up basis (worth over $1,000,000+ in tax savings) and protects any Prop 19 eligibility option.',
         src('RR-2023-2', 'BOE-HOX')],
        ['Now or next annual renewal',
         'Pull Santa Clara TRA bill lines, Property A PG&amp;E PTO/NEM date, Cupertino water provider map check, and 2 broker insurance quotes; verify SF Property B Rent Board registration status.',
         'Medium: refines holding costs and avoids vacancy/coverage gaps; keeps sensitive exact bills offline.',
         src('SCC-RATES', 'CUP-WATER', 'CDI-RES')],
        ['Only at/after Transferor\'s death (0-150 days)',
         'Order date-of-death appraisal, serve Probate Code 16061.7 notice (60d), file Change in Ownership Statement (150d), switch insurance to estate/vacancy endorsement, decide Sell vs. Rent vs. Live.',
         'Critical statutory sequence: BOE-266 must be filed before BOE-19-P if moving in; Form 706 due in 9 months.',
         src('BOE-PUB-800-1', 'RTC-480', 'IRS-I706')],
    ]
    t3 = table(['When to verify', 'Action checklist', 'Decision impact', 'Official basis'],
               plan, caption='Discovery timing: what must be checked now vs. only upon inheritance')

    evidence = [
        ['S5-Q1', 'The trust instrument, estate inclusion and the resulting income-tax basis of Property A',
         'Known: the model assumes the home is in the gross estate, so the basis resets (Q01, blockers B1-B2). Missing: the instrument itself has never been seen; a trust outside the estate gets no reset (Rev. Rul. 2023-2).',
         'Estate attorney reads the full trust, amendments and recorded vesting deed privately, then documents inclusion and the date-of-death valuation in writing. The document stays off this site.',
         'Q01, GAP-01',
         src('RR-2023-2', 'IRS-FAQ-INHERIT')],
        ['S5-Q2', 'Whether the Inheritor will occupy Property A within one year and keep it as the principal residence',
         'Known: the Proposition 19 relief is modelled on a qualifying parent-child transfer (Q06, Q15). Missing: intent, the Transferor\'s occupancy, and the exemption status on the bills.',
         'Owner decision plus counsel and assessor confirmation; file BOE-266 before BOE-19-P if moving in. Read the exemption line on both bills privately - do not publish the bills.',
         'Q06, Q15, blockers B5-B6',
         src('BOE-LTA-2026-026', 'BOE-PUB-800-1')],
        ['S5-Q3', 'The lawful rentable condition and market rent of Property A and of the vacated third unit at Property B',
         'Known: HUD benchmarks for both ZIP codes; the two let units earn an owner-supplied figure (A10). Missing: bedroom count, permits, leases, rent-control coverage, and any rent for the third unit - the baseline counts none of it.',
         'Private inspection, lease review, a property-manager rent opinion, and a Rent Board coverage check. Never derive one unit\'s rent from another unit.',
         'U08, Q04, A10, GAP-05',
         src('HUD-95014', 'SF-RENT-LAW')],
        ['S5-Q4', 'The actual utility accounts, meters, retailer and tax-roll charges for both homes',
         'Known: adopted rate schedules (SFPUC, county tax rate book) and the owner\'s rounded bill midpoints. Missing: account class, usage, the Cupertino water provider, and whether storm charges already sit on the tax bill (U10).',
         'Read the bills and the utility agreements privately; confirm retailer and account class with the utility. Avoid double counting charges that already appear on the tax roll.',
         'U03, U05, U10, GAP-04',
         src('CUP-WATER', 'SCC-RATES')],
        ['S5-Q5', 'What insurance is actually available for both homes, and at what price',
         'Known: the owner\'s rounded insurance estimate and the official statewide averages; tripling the estimate does not change the ranking. Missing: real quotes for homeowners, three-unit landlord cover, vacancy and earthquake (U01, U02).',
         'Obtain comparable quotes privately through a broker and the Department of Insurance tool. Quotes are personal documents; only rounded totals would ever be used.',
         'U01, U02, GAP-03',
         src('CDI-TOOL', 'CDI-EQ')],
        ['S5-Q6', 'The full estate inventory and the liquidity the family will need',
         'Known: the federal exclusion and the room the model shows. Missing: other assets, debts, deductions, prior gifts, retirement accounts, portability, and the cash actually expected (Q02).',
         'Executor and tax adviser prepare a confidential inventory and a Form 706 analysis privately; no balances belong in this repository.',
         'Q02, GAP-02, blocker B3',
         src('IRS-ESTATE', 'IRS-FAQ-ESTATE')],
        ['S5-Q7', 'How sale proceeds would be invested, and what loss the family can tolerate',
         'Known: the baseline result assumes stocks at 7.0%; break-even points show what would change the answer. Missing: the mix itself - no official forecast exists (A02).',
         'Read the SEC allocation guidance, choose a mix with the adviser, and re-read the sensitivities: proceeds kept only in savings rank renting ahead of selling in the tested cases.',
         'D03, A02, GAP-02',
         src('SEC-ALLOC', 'SEC-TEN')],
    ]
    t4 = table(['ID', 'Evidence needed before the decision', 'What is known and what is missing', 'Private discovery route (documents stay off this site)', 'Maps to', 'Official basis'],
               evidence, caption='Decision-gating evidence checklist carried from the independent audit of 2026-11-12 (S5-Q1 to S5-Q7)')

    body = """
<p class="callout">This page brings together what is already established, what cannot be verified from public records, the exact answers needed before making a final decision, and practical ways to uncover each missing piece without exposing private documents on the public repository.</p>
<p class="callout"><strong>Six blockers gate the decision.</strong> B1-B2: the trust instrument has never been seen and the basis treatment under Rev. Rul. 2023-2 is unconfirmed (Q01). B3: the estate size and any portability election are unknown against the $15,480,000 exclusion for 2027 (Q02). B4: the Inheritor's own income-tax bracket is unknown (Q05). B5: Proposition 19 parent-child eligibility is unconfirmed (Q06). B6: filing and claim deadlines need the date of death and the transfer timeline (Q15, Q16). Nothing on this page invents an answer: each row says what is known, what is missing, and the official basis.</p>
<h2>Part 1 - Known vs. unknown facts, pre-decision questions &amp; discovery sequence</h2>
<h3>1. What is known vs. what is unknown</h3>%s
<h3>2. Questions to answer before deciding, and how to discover missing info</h3>%s
<h3>3. Discovery sequence: now vs. later</h3>%s
<h3>4. Decision-gating evidence checklist from the independent audit (S5-Q1 to S5-Q7)</h3>%s
<p class="note">The independent audit session of 2026-11-12 recorded seven evidence questions with their private discovery routes. They are reproduced here mapped to this site\'s own registers so nothing is lost between the two works. Every route is private: no trust documents, leases, bills, quotes or balances belong in this repository, and none of them can be answered from an official page - which is why they gate the decision.</p>
""" % (t1, t2, t3, t4) + _questions_register()
    page('questions.html', 'Questions, unknowns, and discovery guide',
         'Clear summary of known vs. unknown information, exact pre-decision questions, reading-dated decision register, and practical ways to find missing details without compromising privacy.', body)


# ====================================================================== suggestions
def build_suggestions():
    # S5-P5: every model-derived figure on this page comes from model.json (P / B / sf_gap),
    # never from a hand-typed literal; official published figures are quoted and linked.
    mod = [
        ['IMP-01', 'Interactive browser sensitivity sliders',
         'High impact / medium effort (JS only)',
         'Add client-side sliders on Decision (house growth, stock return, inflation, marginal tax rate, Prop A rent, repair rate) so the user can test custom beliefs without rerunning Python.',
         'Static baseline numbers stay untouched until reviewed; requires no external libraries.',
         src('FHFA-SJ', 'TREASURY')],
        ['IMP-02', 'Model P.L. 119-21 SALT cap &amp; 2030 reversion + Joint Filer toggle',
         'Medium impact / low effort',
         'Show a side-by-side Single vs. Married Filing Jointly toggle (adjusting 3.8%% NIIT from $200,000 to $250,000 MAGI and LTCG brackets) and explicitly model the P.L. 119-21 Schedule A SALT cap ($%s in 2026 reverting to $%s in 2030) vs. uncapped Schedule E rental property taxes.' % (format(P['salt_cap_2026'], ','), format(P['salt_cap_floor'], ',')),
         'Highlights why Live loses even more tax deductibility relative to Rent if Schedule A remains capped at $10,000 after 2029.',
         src('IRS-SCHED-A', 'IRS-TC559', 'RP-2026-35')],
        ['IMP-03', 'Inherited IRA / SECURE Act 10-year tax drag on cash',
         'High impact if estate cash is in pre-tax IRAs',
         'Separate taxable cash/brokerage assets from pre-tax IRAs on Cash and estate tax, illustrating how 10-year required withdrawals push the Inheritor into higher CA/federal brackets (including the 1% Behavioral Health Services Tax above $1,000,000).',
         'Currently the cash table treats all cash/other assets as after-income-tax cash; only Q02 separates IRA vs. taxable.',
         src('IRS-P559', 'FTB-MHS')],
        ['IMP-04', 'Model PG&amp;E 20-year NEM 2.0 sunset &amp; $24.15/mo fixed charge',
         'Low-medium impact / low effort',
         'Add an optional year-N toggle when Property A\'s 20-year NEM legacy period ends (switching solar export credits to Net Billing Tariff rates plus the $24.15/mo Base Services Charge).',
         'Avoids assuming solar remains a permanent net credit over a 50-year horizon.',
         src('CPUC-NEM', 'CPUC-FIXED')],
        ['IMP-05', 'Hybrid strategies: Live briefly then Sell, or Prop 19 + Move Out',
         'Medium-high impact / medium effort',
         'Add a 4th scenario (Live 2-5 years to qualify for the $250,000/$500,000 Sec. 121 home-sale exclusion, then Sell) AND show the BOE Pub. 800-1 move-out rule (moving out later enrolls date-of-death FMV indexed).',
         'Helps if the Inheritor wants a trial period in Property A before selling.',
         src('IRS-TC701', 'BOE-PUB-800-1')],
        ['IMP-06', 'Treasury-staged deployment ("sell into bills/bonds for 2 years, then equities")',
         'High psychological &amp; sequence-risk value',
         'Add a phased-investing path in Black swan (parking sale proceeds in 3M-2Y Treasuries for 24-36 months after inheritance before phasing into stocks) to test how it softens 1929/2008 crash entry risk.',
         'Directly addresses the only black-swan failure mode where immediate all-in equity selling trails renting.',
         src('TREASURY', 'BLS-CPI')],
        ['IMP-07', 'Include California Prop 3 / FTB Behavioral Health Tax sensitivity in year-of-sale',
         'Low impact / low effort',
         'Explicitly test whether keeping CA top rates via Prop 3 affects a delayed sale or Property B divestment (note: immediate date-of-death sale has ~zero capital gain if step-up applies).',
         'Clarifies why Prop 3 barely touches immediate Sell if step-up holds, yet heavily hits a non-step-up sale.',
         src('SOS-RESULTS', 'FTB-MHS')],
        ['IMP-08', 'Earthquake self-insurance vs. CEA deductible &amp; Property B retrofit reserve',
         'Medium impact / medium effort',
         'Replace the single flat repair line with an optional periodic capital-expenditure / seismic-retrofit reserve schedule (roof, HVAC, soft-story/foundation) plus an illustrative CEA premium stress.',
         'Makes Live/Rent carrying costs more realistic given the 72% USGS Bay Area quake probability.',
         src('USGS', 'CDI-EQ')],
        ['IMP-09', 'Model Property B sale as a 4th comparison choice',
         'Medium impact / low-medium effort',
         'Show selling Property B instead of Property A as a full baseline option alongside keeping B, quantifying lost Prop 13 protection (%s/yr tax advantage) and un-reset capital gains on B.' % m(sf_gap),
         'Directly demonstrates with numbers why Property B is kept in the baseline plan.',
         src('SF-TAX', 'IRS-TC409')],
    ]
    t1 = table(['ID', 'Proposed model / financial-logic change', 'Impact &amp; effort', 'What would change if approved', 'Why review first', 'Your decision (saved in this browser only)', 'Official basis'],
               [r[:5] + [_sg(r[0])] + [r[5]] for r in mod], caption='Proposed model &amp; analytical improvements (pending reviewer approval)')

    data_gaps = [
        ['GAP-01', 'Attorney trust-inclusion letter (%s)' % flag('Q01'), 'Confirms revocable inclusion vs. irrevocable grantor trust under Rev. Rul. 2023-2 (largest single swing in Sell).', 'Low - 1 legal review', 'Proposed - owner approval needed', src('RR-2023-2')],
        ['GAP-02', 'Estate total &amp; prior spouse Form 706 portability (%s)' % flag('Q02'), 'Establishes cash vs. IRA mix against %s 2045 room and whether a second exclusion was preserved.' % m(B['exclusion_T'] - B['fmv_T']), 'Medium - CPA + attorney', 'Proposed - owner approval needed', src('IRS-ESTATE', 'IRS-FAQ-ESTATE')],
        ['GAP-03', 'Actual CDI comparison tool + broker quotes &amp; quake offer (%s, %s)' % (flag('U01'), flag('U02')), 'Replaces %s/yr placeholder with actual 95014 homeowners, 94122 3-unit DP-3 landlord, vacancy endorsement, and CEA earthquake quotes.' % m(P['ins_home']), 'Low - broker call + 5 min on CDI tool', 'Proposed - owner / broker', src('CDI-TOOL-APP', 'CDI-RES', 'CDI-EQ')],
        ['GAP-04', 'Santa Clara TRA bill lines, Cupertino water provider &amp; PG&amp;E PTO date (%s, %s)' % (flag('U03'), flag('U05')), 'Verifies parcel fixed charges, which of Cupertino\'s 3 water utilities serves Property A, and when 20-yr NEM 2.0 grandfathering expires.', 'Low - read utility &amp; tax bills', 'Proposed - owner', src('SCC-RATES', 'CUP-WATER', 'CPUC-NEM')],
        ['GAP-05', 'Local property-manager rent opinion + bedroom confirmation &amp; appraisals (%s)' % flag('U08'), 'Benchmarks actual rent against HUD 4-BR (%s/mo) / 3-BR (%s/mo) and updates owner estimates (%s / %s).' % (m(P['cup_rent_month']), m(P['cup_rent_month_3br']), m(P['cup_value']), m(P['sf_value'])), 'Medium - manager + appraiser', 'Proposed - owner approval needed', src('HUD-95014', 'FHFA-SJ')],
    ]
    t_gaps = table(['ID', 'Data-gathering step', 'Why it improves the decision', 'Effort', 'Status', 'Your decision (saved in this browser only)', 'Official basis'],
                   [r[:5] + [_sg(r[0])] + [r[5]] for r in data_gaps], caption='Data-gap items to gather before finalizing numbers')

    ux = [
        ['IMP-10', 'Scrub pre-rounding Git history / keep repo privacy-first (Flag P02)',
         'Critical privacy fix / owner action',
         'Rewrite Git history (<code>git filter-repo</code> or fresh orphan export of clean state) and/or change repository visibility from public to private before referencing exact bills or trust memos; keep public GitHub Pages on the non-household guide in <code>privacy-site/public/</code>.',
         'Cannot be solved via normal commits alone because early pre-rounding commits sit in public Git history.',
         src('SCC-RATES')],
        ['IMP-11', 'Split local private input overrides from public repo (<code>local_private.json</code>)',
         'High usability &amp; privacy value',
         'Allow the owner to keep an untracked, <code>.gitignore</code>-excluded <code>local_private.json</code> file locally to recompute exact household numbers on their own machine while keeping the GitHub repo strictly rounded to $10.',
         'Prevents accidental leaks while giving the owner exact household figures locally.',
         src('BLS-CPI')],
        ['IMP-12', 'One-page printable "Attorney &amp; CPA Briefing Sheet" export',
         'High practical utility / low effort',
         'Add a dedicated <code>@media print</code> CSS layout and a single-page summary view printing <code>Q01-Q06</code>, Prop 19 BOE-266/BOE-19-P sequence, and estate-tax headroom without charts/navigation clutter.',
         'Gives the Transferor and Inheritor a clean agenda to hand directly to an estate attorney or CPA.',
         src('BOE-PUB-800-1', 'RR-2023-2')],
    ]
    t2 = table(['ID', 'Proposed workflow, UX &amp; privacy option', 'Impact &amp; effort', 'What would change if approved', 'Why review first', 'Your decision (saved in this browser only)', 'Official basis'],
               [r[:5] + [_sg(r[0])] + [r[5]] for r in ux], caption='Proposed workflow, reporting &amp; privacy-governance improvements')

    path_rows = [
        ['Path 1 - Minimal (data verification first)', 'Keep baseline model as-is + resolve GAP-01..GAP-05 (trust letter, insurance quotes, tax bill/TRA, Cupertino water utility, NEM date, rent opinion).', '1-2 weeks part-time', 'Fastest way to eliminate major unknowns before any code changes', src('RR-2023-2', 'CUP-WATER')],
        ['Path 2 - Standard (recommended)', 'Path 1 + IMP-01 (sliders), IMP-02 (SALT/Joint toggle), IMP-06 (Treasury staging), IMP-12 (Attorney/CPA sheet), plus IMP-10/IMP-11 privacy split.', '2-4 weeks', 'Lets you test assumptions and tax details interactively while keeping household privacy intact', src('IRS-SCHED-A', 'TREASURY')],
        ['Path 3 - Comprehensive', 'Path 1 + Path 2 + IMP-03 (IRA 10-yr drag), IMP-04 (NEM sunset), IMP-05 (hybrid Live-then-Sell), IMP-08 (quake/capex reserve), IMP-09 (Sell B comparison).', '4-6 weeks', 'Complete household decision workbook ready for family, attorney, and CPA sign-off', src('IRS-P559', 'BOE-PUB-800-1')],
    ]
    paths = table(['Implementation path (choose before editing baseline)', 'Included items', 'Owner time', 'Best fit', 'Your decision (saved in this browser only)', 'Official basis'],
                  [r[:4] + [_pth('R%d' % (n + 1))] + [r[4]] for n, r in enumerate(path_rows)],
                  caption='Three implementation paths - pick one before any baseline numbers change')

    workflow = """
<h2>Review status workflow</h2>
<ul class="plan">
<li><strong>Proposed</strong> - waiting for your review; zero baseline figures modified.</li>
<li><strong>Under review</strong> - sent to estate attorney, CPA, broker, or appraiser.</li>
<li><strong>Approved / Built</strong> - selected for implementation, rebuilt through <code>final/model.py</code> and verified against <code>final/check.py</code>.</li>
<li><strong>Not approved / Deferred</strong> - explicitly declined and recorded for completeness.</li>
</ul>"""

    head = '<p class="callout">This is the <strong>review before implementation</strong>: choose Adopt / Hold / Reject in every “Your decision” column and pick one implementation path. Nothing is built until you approve it; your choices are a review aid kept in this browser only.</p>\n<p id="sgsum" class="status"></p>\n<p><button id="sgreset" type="button">Reset my review choices</button></p>'
    body = '<div id="sgwrap">' + head + ("""
<p class="callout"><strong>Proposed site improvements - for review before implementing.</strong> None of the changes below have been folded into the baseline numbers yet. Presenting them here lets the reviewer pick which data checks, model refinements, interactive tools, or privacy workflows to adopt (e.g., Path 1, Path 2, or Path 3) without silently shifting the verified baseline outputs (%s Sell vs. %s Rent vs. %s Live).</p>
%s
<h2>Part 1 - Data-gap, model &amp; privacy-workflow improvements</h2>
<h3>1. Data-gap verification candidates</h3>%s
<h3>2. Model &amp; financial-logic candidates</h3>%s
<h3>3. Workflow, reporting &amp; privacy candidates</h3>%s
<h3>4. Choose a path before implementing changes</h3>%s
<p class="note">See also the itemized <code>SG-1</code>–<code>SG-11</code> queue on <a href="requirements.html">Requirements and verification</a>.</p>
""" % (m(B['real_sell']), m(B['real_rent']), m(B['real_live']), workflow, t_gaps, t1, t2, paths)) + _suggestions_options() + '</div>'
    page('suggestions.html', 'Site improvements & proposed options',
         'Structured suggestions for improving the site, data coverage, model nuance, and privacy workflow so the reviewer can select the best path before implementing changes.', body)
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
    # Repository review findings R01-R43 are rendered on the repository review page; the flagged
    # page keeps one pointer row so that a flag link of the form review.html#R38 resolves.
    cats.append(('RY', 'Repository review findings, listed on the review page'))
    RYNOTE = ('Every repository review finding (R01-R43) is listed in full, with what was found, what was changed and the official link, on the '
              '<a href="review.html">repository review</a> page.')
    body = '<p class="callout">Flagged for Review. Nothing on this page blocks the rest of the site. Each item says what is missing or uncertain, what was used instead, and where to check it. See <a href="questions.html">Questions &amp; discovery</a> for ways to uncover missing answers and <a href="suggestions.html">Site improvements</a> for candidate model upgrades.</p>'
    for c, title in cats:
        if c == 'R':
            body += table(['No.', 'Item', 'What the site does', 'How to resolve it', 'Where to check'],
                          [['<span id="R01">R01-R37</span>', 'Repository irregularities found by every review pass', RYNOTE,
                            'Re-read the row on the review page; each one names the file and the official page.', src('SCC-RATES', 'BOE-LTA-2026-026')]],
                          caption=title)
            continue
        rows = [['<span id="%s">%s</span>' % (f['id'], f['id']), f['item'], f['used'], f['check'], src(*f['src']) + (' · ' + f['extra'] if f.get('extra') else '')] for f in FLAGS if f['id'].startswith(c)]
        body += table(['No.', 'Item', 'What the site does', 'How to resolve it', 'Where to check'], rows, caption=title)
    ex = [['E-' + k, e(v['title']), e(v['read']), '<a href="%s" rel="noopener">%s</a>' % (e(v['url']), e(v['label'])) + (' · official reference for current rates: ' + src('TREASURY') if v['how'] == 'academic' else '')] for k, v in sorted(S.items()) if v['how'] != 'page']
    body += table(['No.', 'Source not read in full', 'Text relied on', 'Open the page'], ex, caption='Sources not read as a direct official government page (as of 2026-11-12, zero official agency excerpt entries remain; only the academic return dataset appears here)')
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
<li><strong>Property B is never inherited in the model.</strong> Its assessed value, basis and rent continue unchanged. It enters the comparison only through the option of letting the third unit when the Inheritor moves to Property A: the baseline counts no rent for the third unit (nothing is inferred), and the letting upside appears only as one labelled scenario in the sensitivity table.</li>
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
        ['Clear list of questions, known vs. unknown information, answers needed before reasonably deciding, and ways to discover missing info',
         '<a href="questions.html">Questions &amp; discovery</a> (Part 1 known vs. unknown table, pre-decision questions, discovery methods &amp; timing; Part 2 reading-dated decision register with open/cannot-know/known rows) plus <a href="flagged.html">Flagged for Review</a>.',
         'Met; answers that no official page or owner figure settles remain blank', src('RR-2023-2', 'CDI-TOOL', 'BOE-LTA-2026-026')],
        ['Dedicated section for site-improvement suggestions so the reviewer can pick the best path before implementing changes',
         '<a href="suggestions.html">Site improvements</a> (Part 1: GAP-01..05, IMP-01..12, Paths 1–3; Part 2: G01..G15 options &amp; paths; plus <a href="requirements.html#suggestions">SG-1–SG-11</a>).',
         'Met as proposed options — nothing implemented until approved', src('IRS-SCHED-A', 'CPUC-NEM', 'HUD-SAFMR-INDEX')],
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
<p class="note">Updated on %s: added <a href="questions.html">Questions &amp; discovery</a> and <a href="suggestions.html">Site improvements</a>, verified all remaining fourteen official sources directly on their agency pages (zero official excerpt entries remain), added BOE Pub. 800-1, Cupertino water provider records, IRS Schedule A SALT cap guidance, and SFPUC combined bill increases, and re-built all published pages. If a later pass changes a figure, this page is regenerated with the rest of the site, so it cannot drift out of date.</p>
<ul class="plan">
<li>Build: <code>python3 final/model.py &amp;&amp; python3 final/build.py</code> - fifteen substantive pages, plus the earlier-versions page and redirects at retired addresses.</li>
<li>Checks: <code>python3 final/check.py .</code> - every table row carries a link to an official page, every internal link and anchor resolves, every dollar figure is a multiple of $10 unless it is a listed official figure, and no personal information or unrounded owner figure appears.</li>
<li>Model self-tests: the Proposition 19 formula is checked against the county assessor's own worked example, and Property B is asserted never to be reassessed.</li>
</ul>
""" % (t1, assumptions, rules, t2, BUILD_DATE)
    page('requirements.html', 'Requirements and verification',
         'Every part of the brief, the page that answers it, the official rule behind it - and the official pages that were re-read on 2026-11-11 to make sure the numbers on this site still match.', body)


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
    hdr = ['No.', 'Suggestion', 'What the site does today', 'Options', 'Suggested choice', 'Effect on the decision', 'Effort and risk', 'Your decision (saved in this browser only)', 'Official basis']
    for k in ('privacy', 'inputs', 'tools'):
        s[k] = [r[:7] + [_sg(r[0])] + r[7:] for r in s[k]]
    n = len(s['privacy']) + len(s['inputs']) + len(s['tools'])
    t0 = table(['Path', 'Name', 'Suggestions included', 'What it achieves', 'Effort', 'Official basis'], s['paths'], caption='Ready-made paths for Part 2')
    t1 = table(hdr, _anchor(s['privacy']), caption='Privacy and upkeep', cls='qa')
    t2 = table(hdr, _anchor(s['inputs']), caption='Better inputs', cls='qa')
    t3 = table(hdr, _anchor(s['tools']), caption='Decision tools', cls='qa')
    return """
<h2 id="options">Part 2 - options register for the site</h2>
<p class="callout"><strong>Nothing in this part has been implemented either.</strong> These are %d further proposals, written by a second work session on the same day and kept beside Part 1 (the data-gap and improvement register GAP-01 to GAP-05 and IMP-01 to IMP-12). Each row gives lettered options, a suggested choice, its effect on the decision, and the effort and risk. Status of every row: <strong>decision needed</strong>.</p>
<p class="note">Where a row covers the same ground as Part 1, choose once (the earlier S-01 to S-18 register these references were written for was retired when Part 1 became GAP-01 to GAP-05 and IMP-01 to IMP-12; every S-row has a GAP/IMP successor): G03 -> IMP-02 and IMP-06; G04 -> GAP-05 (current-state wording) and option A -> IMP-01, option D -> IMP-10; G05 -> GAP-01 and GAP-03; G10 option C -> IMP-03; G11 -> IMP-05 and IMP-09; G12 -> GAP-02; G13 -> IMP-12; G01 option D -> GAP-02 and GAP-05. To choose from this part, list numbers with an option letter (for example "G01 C, G04 B, G09 B"), or name one of the paths below. The suggestions change how the result is presented and tested, not the rules behind it. G10 and G12 would add new model results, which would be checked and flagged like the existing ones.</p>
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
section.card h3{margin:0 0 8px;font-size:16px;color:var(--ink)}
ul.dex{margin:0;padding-left:18px;font-size:14px}ul.dex li{margin:0 0 7px;color:var(--mut)}
ul.dex a{font-weight:600;text-decoration:none}ul.dex a:hover{text-decoration:underline}
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


# ---------------------------------------------------------------- front-door content
# Every category of the site, with a one-line description.  Used by the dashboard only.
NAV_CARDS = [
    ('Start here', [
        ('summary.html', 'Executive summary', 'the answer, the numbers behind it, and the six steps of the plan'),
        ('decision.html', 'Decision analysis', 'live, rent or sell: cash flows, after-tax wealth, sensitivities, break-even points'),
    ]),
    ('Money and projections', [
        ('projections.html', 'Year by year, 2026-2076', 'value, assessed value, property tax, insurance, water, electricity, repairs'),
        ('black-swan.html', 'Black swan', '50 replays of the real 1976-2025 record and named crisis paths'),
        ('costs.html', 'Insurance and running costs', 'what is quoted, what is assumed, and what is still unconfirmed'),
        ('estate-cash.html', 'Cash and estate tax', 'the threshold at each level, the room before tax, and projections'),
    ]),
    ('Law and process', [
        ('law.html', 'Law in force and under discussion', 'federal, California and local rules, plus pending measures'),
        ('process.html', 'Inheritance process, step by step', 'every step with its legal deadline and the official page it comes from'),
    ]),
    ('Before you decide', [
        ('questions.html', 'Questions to answer', 'what is known, what is missing, and how to find each missing answer'),
        ('suggestions.html', 'Suggestions for review', 'proposed improvements, status and effort - none implemented until chosen'),
    ]),
    ('How this was checked', [
        ('verification.html', 'Verification passes', 'every official page read, with the result, for manual re-check'),
        ('flagged.html', 'Flagged for Review', 'every unconfirmed value, assumption and irregularity'),
        ('sources.html', 'Sources and method', 'the source register and the cross-check against a second model'),
        ('requirements.html', 'Requirements', 'the brief line by line and the page that answers it'),
        ('review.html', 'Repository review', 'the findings of each review pass, what was changed and why'),
        ('versions.html', 'Earlier versions', 'superseded editions and why they were replaced'),
    ]),
]

# The four items that change the answer rather than refine it (dashboard "open" list).
DECISIVE = [
    ('Q01', 'What kind of trust holds Property A, and will the home be included in the Transferor\'s gross estate? Without the basis reset, selling loses its advantage over renting.'),
    ('Q02', 'How large is the estate, and was a deceased spouse\'s unused exclusion ported? This sets the room before federal estate tax applies.'),
    ('U04', 'What will the Proposition 19 allowance be for a transfer after 2027-02-16? The official figure is not published yet.'),
    ('A01', 'Growth, inflation and return assumptions: the ranking between renting and selling is sensitive to these over a 50-year horizon.'),
]

# Findings added by session arena/f8de1d0b on 2026-11-13 (also on the Flagged page).
NEW_FINDINGS = [
    ('R39', 'The Property B property-tax input is about 2.14% of assessed value against an official rate of 1.18162182%, leaving an unexplained residual of about $1,090 a year that the model carries forward.'),
    ('R41', 'The Cupertino solar credit is carried forward for 50 years, while the CPUC states that the net-metering tariff that creates it lasts 20 years from interconnection.'),
    ('R40', 'The third San Francisco unit\'s rent is inferred as half of the two let units\' combined rent; no per-unit figure was supplied.'),
    ('R38', 'A merge-conflict marker had been committed to the verification page and was live on the site. Removed.'),
]


def choice_table():
    """The three choices on one row, all figures from the model, rounded to $10."""
    hdr = ['Measure', 'Live in it', 'Rent it out', 'Sell and reinvest', 'Official rule behind it']
    rows = [
        ['Property A market value at inheritance (%d)' % T, m(B['fmv_T']), m(B['fmv_T']), m(B['fmv_T']), src('FHFA-SJ')],
        ['New assessed (taxable) value', m(B['taxable_live_T']), m(B['taxable_rent_T']), 'sold', src('BOE-LTA-2026-026', 'RTC-63.2')],
        ['Property tax, first year', m(B['tax_live_T']), m(B['tax_rent_T']), m(B['tax_before_T']), src('SCC-RATES', 'BOE-HOX')],
        ['Cash released at inheritance', '$0', '$0', m(B['sell_net']), src('IRS-FAQ-INHERIT', 'SCC-DTT')],
        ['After-tax wealth in 2076', m(B['w_live']), m(B['w_rent']), m(B['w_sell']), src('IRS-TC409', 'FTB-RATES')],
        ['The same in 2026 dollars', m(B['real_live']), m(B['real_rent']), m(B['real_sell']), src('BLS-CPI')],
    ]
    return table(hdr, rows, caption='The three choices on the baseline assumptions, inheritance in %d' % T, cls='num')


def build_home_choice():
    """Write the generic, privacy-first root landing page in ROOT_MODE.

    The public Pages site contains no link to the household-specific numeric edition.
    That edition and its inputs remain in this public repository, so exclusion from
    Pages is not represented as repository privacy or anonymization.
    """
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Privacy-first inheritance decision guide</title>
<style>
:root{color-scheme:light;--ink:#173334;--green:#24574f;--muted:#657572;--line:#dce6df;--paper:#f5f7f2}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:10vh auto;padding:40px 28px;background:#fff;border:1px solid var(--line)}
.eyebrow{font-size:.75rem;letter-spacing:.14em;font-weight:700;color:#5b786c}h1{font:500 clamp(2rem,5vw,3rem)/1.15 Georgia,serif;margin:.8rem 0 1rem}
p{color:var(--muted)}a.button{display:inline-block;margin:16px 0;padding:13px 19px;background:var(--green);color:#fff;text-decoration:none;font-weight:700;border-radius:4px}
a:focus-visible{outline:3px solid #c98d25;outline-offset:3px}.note{border-top:1px solid var(--line);padding-top:18px;font-size:.9rem}
</style></head><body><main><p class="eyebrow">PUBLIC EDITION · PRIVACY FIRST</p>
<h1>Inheritance decision guide</h1>
<p>A general guide to the legal process, the information still needed, operating-cost categories, and the choices that should be compared before a future trust transfer.</p>
<p>The public guide uses fictional teaching examples only. It does not publish household-specific property figures, tax histories, utility costs or forecasts.</p>
<p><a class="button" href="privacy-site/public/index.html">Open the decision guide</a></p>
<p class="note">Rounding is not anonymization. This page only describes the GitHub Pages publication boundary; the public source repository and its history are separate exposure surfaces.</p>
</main></body></html>
""")


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'style.css'), 'w').write(CSS)
    open(os.path.join(OUT, 'app.js'), 'w').write(JS)
    for f in (build_index, build_decision, build_projections, build_blackswan, build_process, build_law,
              build_estate, build_costs, build_questions, build_suggestions, build_flagged, build_sources,
              build_verification, build_requirements, build_review):

        f()
    if ROOT_MODE:
        build_home_choice()
        build_versions()
        for s_, t_, n_ in STUBS:
            stub(s_, t_, n_)
    print('built', len([x for x in os.listdir(OUT) if x.endswith('.html')]), 'pages in', OUT)


if __name__ == '__main__':
    main()
