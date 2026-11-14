#!/usr/bin/env python3
"""Pages added in session arena/88de34f6: mixed and phased paths, what-if controls, glossary,
one-page printable Attorney & CPA Briefing Sheet, and the deadline timeline.

Imported by final/build.py (build_all). Every dollar shown is rounded to $10 by build.m().
Every table row carries a link to an official page from final/sources.py (checked by final/check.py).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as Bd  # noqa: E402
import extras as X  # noqa: E402

m, pc, src, table, flag, e, page = Bd.m, Bd.pc, Bd.src, Bd.table, Bd.flag, Bd.e, Bd.page
P = Bd.P
T = P['T']


def money_or_dash(v):
    return '&mdash;' if v is None else m(v)


def _sign(v):
    return ('+' if v >= 0 else '') + m(v)


def _res():
    return X.compute()


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
            Bd.e(pl['label']),
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
            Bd.e(c['label']),
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
        mixed_rows.append([Bd.e(lab), m(st[k]['real_end']['median']), m(st[k]['real_end']['min']), m(st[k]['real_end']['max']),
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


# ------------------------------------------------------------------ what-if controls
def build_whatif(D):
    grid = {}
    for key, plans in D['grid'].items():
        grid[key] = {k: dict(real_end=(None if v['real_end'] is None else Bd.r10(v['real_end'])),
                             real10=(None if v['real10'] is None else Bd.r10(v['real10'])))
                     for k, v in plans.items()}
    labels = {pl['key']: pl['label'] for pl in D['plans']}
    show = ['live', 'rent', 'sell', 'sell_p24', 'sell_p36', 'rent5_sell']
    default = '%d|%s|%s|%s' % (T, '0.07', '0.025', '0.05')
    dk = default

    def opts(name, values, labels_, cur):
        return ('<label class="ctl">%s<select id="%s">' % (name[0], name[1])) + ''.join(
            '<option value="%s"%s>%s</option>' % (v, ' selected' if v == cur else '', l) for v, l in zip(values, labels_)) + '</select></label>'

    controls = ''.join([
        opts(('Year of inheritance (baseline 2045)', 'c_t'), ['2040', '2045', '2050'], ['2040', '2045', '2050'], str(T)),
        opts(('Stock return a year (range 5%-10%)', 'c_r'), ['0.05', '0.07', '0.1'], ['5.0%', '7.0% (baseline)', '10.0%'], '0.07'),
        opts(('Inflation a year (range 2.0%-3.5%)', 'c_i'), ['0.02', '0.025', '0.035'], ['2.0%', '2.5% (baseline)', '3.5%'], '0.025'),
        opts(('Selling costs (range 5%-7%)', 'c_c'), ['0.05', '0.07'], ['5%', '7%'], '0.05'),
    ])
    cur = grid[dk]
    rows = []
    for k in show:
        rows.append('<tr data-k="%s"><td>%s</td><td class="r10">%s</td><td class="rend">%s</td></tr>' % (
            k, e(labels[k]), m(cur[k]['real10']), m(cur[k]['real_end'])))
    best = max(show, key=lambda k: cur[k]['real_end'])
    table_html = ('<div class="tablewrap"><table class="num" id="whatif"><caption>Results for the settings above</caption>'
                  '<thead><tr><th scope="col">Plan</th><th scope="col">After-tax wealth 10 years after inheritance (2026 dollars)</th>'
                  '<th scope="col">After-tax wealth in 2076 (2026 dollars)</th></tr></thead><tbody>' + ''.join(rows) +
                  '</tbody></table></div>')
    cards = ('<div class="kpis"><div class="kpi"><div class="k">Best in 2076 for these settings</div><div class="v" id="best">%s</div>'
             '<div class="s">Ranking only. Each plan is shown with its own reinvestment risk in the table below and on the Mixed and phased paths page.</div></div></div>'
             % e(labels[best]))
    gj = json.dumps(grid, separators=(',', ':'))
    labj = json.dumps({k: labels[k] for k in show}, separators=(',', ':'))
    js = ('<script type="application/json" id="grid">%s</script>\n<script type="application/json" id="labels">%s</script>\n'
          '<script>(function(){function f(v){if(v===null)return "-";var n=Math.round(v/10)*10;return (n<0?"-$":"$")+Math.abs(n).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,",");}'
          'var G=JSON.parse(document.getElementById("grid").textContent),L=JSON.parse(document.getElementById("labels").textContent);'
          'var ids=["c_t","c_r","c_i","c_c"];function upd(){var k=ids.map(function(i){return document.getElementById(i).value;}).join("|");var d=G[k];'
          'if(!d){return;}var best=null,bv=-1e18;var rows=document.querySelectorAll("#whatif tbody tr");'
          'for(var i=0;i<rows.length;i++){var key=rows[i].getAttribute("data-k");rows[i].cells[1].textContent=f(d[key].real10);'
          'rows[i].cells[2].textContent=f(d[key].real_end);if(d[key].real_end>bv){bv=d[key].real_end;best=key;}}'
          'document.getElementById("best").textContent=L[best];}'
          'ids.forEach(function(i){document.getElementById(i).addEventListener("change",upd);});upd();})();</script>'
          % (gj, labj))
    body = ('<section class="summary"><p><strong>What-if controls.</strong> Change a setting and the table updates. The results come '
            'from complete model runs for each combination of settings, stored on this page (%d combinations). Nothing is '
            'calculated from a formula in the browser, and nothing you choose is sent anywhere.</p></section>' % len(grid))
    body += '<div class="whatif">' + controls + '</div>' + cards + table_html
    body += ('<h2>Why these ranges</h2>' + table(
        ['Setting', 'Range offered', 'Why this range, and how it is sourced', 'Official basis'], [
            ['Year of inheritance', '2040, 2045, 2050', 'The trust is expected around 2040 to 2050 (the brief). The middle value is the baseline.', src('BOE-P19')],
            ['Stock return a year', '5%, 7%, 10%', 'The baseline is 7%. Ten percent is the long-run S&P 500 total return the replay data uses; 5% is a low case. Not a forecast.', src('DAMODARAN', 'SEC-ALLOC')],
            ['Inflation a year', '2.0%, 2.5%, 3.5%', 'Official CPI history shows decades where inflation ran above and below 2.5% (see Black swan). Each setting also moves home growth and bill and bond rates by the same difference.', src('BLS-CPI', 'BLS-OCT')],
            ['Selling costs', '5%, 7%', 'The baseline is 5% of the sale price. Seven percent tests a more expensive sale. No official figure exists for this range.', src('SCC-DTT')],
        ], caption='Each range is a choice made for this page, not an official projection (flag A17)'))
    body += ('<h2>What would change the answer</h2><ul>'
             '<li>A different stock return moves the sell-and-invest result most: compare the 5% and 10% rows.</li>'
             '<li>A higher inflation setting raises the home value and the property-tax base together, so it does not change the ranking by itself.</li>'
             '<li>The estate and basis-reset facts (flags Q01 and Q02) decide whether the sell result is possible at all; no setting here changes that.</li>'
             '</ul>' + js)
    page('whatif.html', 'What-if controls',
         'Change the year of inheritance, the stock return, inflation or the selling costs and see the three choices, the phased paths and the mixed path update. Ranges are shown with their sources.',
         body)


# ------------------------------------------------------------------ glossary
GLOSSARY = [
    ('Basic exclusion amount', 'The amount an estate can pass without federal estate tax. Per person. Set by federal law and indexed for inflation.', 'Cash and estate tax page: the room before any federal estate tax.', 'RP-2026-35'),
    ('Base-year value (assessed value)', 'The taxable value of a property for California property tax. Starts at the purchase or transfer price and rises at most 2% a year.', 'Property A and Property B assessed values on the projections.', 'RTC-51'),
    ('Change in ownership', 'A transfer that triggers reassessment in California. A revocable trust transfers ownership at death.', 'Starts the reassessment clock and the 150-day filing deadline.', 'BOE-RULE-462.260'),
    ('Depreciation recapture', 'Tax on the part of a rental gain that reverses depreciation taken on the building, at a higher rate than other long-term gains.', 'Rent-then-sell mixed paths.', 'IRS-P527'),
    ('Fixed monthly charge', 'A flat monthly charge on an electricity bill, not tied to use. Relevant to a solar home that is a net credit.', 'Electricity line for Property A (solar).', 'CPUC-FIXED'),
    ('Form 706', 'The federal estate tax return. Required above the filing threshold; also used to elect portability.', 'Deadline list on the Process page.', 'IRS-I706'),
    ('Form 1041', 'The income-tax return for a trust or estate after death.', 'Rent or interest received before distribution.', 'IRS-1041'),
    ('Gross estate', 'Everything the decedent owned or controlled at death, counted before debts and expenses. Determines the estate tax.', 'Whether Property A is in the estate decides the basis reset.', 'IRS-ESTATE'),
    ('Homeowners\' exemption', 'A California reduction in assessed value for an owner-occupied home, currently $7,000 of assessed value.', 'Property A if the Inheritor moves in.', 'BOE-HOX'),
    ('Net investment income tax', 'A federal 3.8% tax on investment income above certain thresholds.', 'Included in the investment and sale tax rates.', 'IRS-TC559'),
    ('Parent-child exclusion (Proposition 19)', 'California rule that lets a child keep the parent\'s assessed value only if the child moves in as the principal residence and claims it in time.', 'The central property-tax choice for Property A.', 'BOE-P19'),
    ('Portability', 'Carrying a deceased spouse\'s unused federal exclusion to the survivor. Requires a timely Form 706.', 'Estate room if a spouse died earlier.', 'IRS-FAQ-ESTATE'),
    ('Principal residence and the two-year test', 'A home lived in as the main home for at least two of the five years before a sale may exclude up to a set amount of gain.', 'Live-then-sell mixed paths (flag A16).', 'IRS-TC701'),
    ('Proposition 13', 'California\'s property-tax limit: assessed value resets to market value only on a change in ownership, and rises at most 2% a year.', 'Why Property B\'s assessed value stays far below its market value.', 'RTC-51'),
    ('Reinvestment risk', 'The chance that money must be put back to work at lower returns than planned, or in a bad market.', 'The worst-of-50 column and the phased paths.', 'SEC-ALLOC'),
    ('Revocable trust', 'A trust the creator can change while alive. Its assets are generally part of the creator\'s estate.', 'The trust that holds Property A.', 'PROB-16061.7'),
    ('Solar net billing and credits', 'How California pays for solar exports. Credits can offset the electricity bill; the owner should confirm the tariff in force.', 'Electricity line for Property A.', 'CPUC-NEM'),
    ('Stepped-up basis (date-of-death value)', 'The income-tax cost basis of inherited property is reset to its value at death, so a sale soon after has little taxable gain.', 'The reason selling soon after inheritance can be cheap.', 'IRS-FAQ-INHERIT'),
    ('3-month to 2-year Treasuries', 'US government debt with 3 months to 2 years to maturity. Used here as the parking place for proceeds (proxied by the 3-month bill; flag A14).', 'Phased paths.', 'TREASURY'),
    ('Tax rate book', 'The county publication of the property-tax rates that apply in each tax rate area.', 'Rate used for Property A.', 'SCC-RATES'),
    ('Tax rate, secured property (San Francisco)', 'The annual secured property-tax rate published by the San Francisco Treasurer and Tax Collector.', 'Rate used for Property B.', 'SF-TAX'),
    ('Rent-controlled unit (San Francisco)', 'A unit covered by the San Francisco Rent Ordinance, with annual increases capped by the Rent Board.', 'Rent growth on Property B\'s let units.', 'SF-RENT-RULES'),
    ('Consumer Price Index (CPI)', 'The official measure of consumer prices. Used here to convert every result into 2026 dollars.', 'Real (2026-dollar) results on every page.', 'BLS-CPI'),
    ('Total return', 'Price change plus reinvested dividends.', 'The stock series used in every replay (flag A18).', 'INVESTOR-TOTAL'),
    ('Estate tax exemption for a surviving spouse (DSUE)', 'The unused federal exclusion of a deceased spouse, if portability is elected.', 'Estate room (see Portability).', 'IRS-FAQ-ESTATE'),
]


def build_glossary():
    rows = [[Bd.e(t), Bd.e(d), Bd.e(w), src(s)] for t, d, w, s in GLOSSARY]
    rows.sort(key=lambda r: r[0].lower())
    t = table(['Term', 'Plain meaning', 'Where it matters on this site', 'Official page'], rows,
              caption='Glossary (%d terms, alphabetical). Each term links to the official page this site relies on' % len(rows),
              note='Definitions are plain-language summaries and not legal or tax definitions (flag A19). The linked page governs.')
    body = ('<p class="note">Terms in the glossary appear in the notes across the site. Use the links to read the governing page before relying on a term. '
            '"Black swan" is not listed: no official definition was located, so the term is explained on the Black swan page as this site uses it (flag A19).</p>' + t)
    page('glossary.html', 'Glossary', 'Plain-language meanings of the legal, tax, property and money terms used on this site, each with its official page.', body)


# ------------------------------------------------------------------ one-page briefing sheet
def build_briefing(D, M):
    b = M['by_T'][str(T)]
    rows = [
        ['Property A (Cupertino) value at inheritance (model estimate)', m(b['fmv_T']), src('FHFA-SJ')],
        ['Assessed value after inheritance: if lived in / if rented', '%s / %s' % (m(b['taxable_live_T']), m(b['taxable_rent_T'])), src('BOE-P19', 'RTC-63.2')],
        ['First-year property tax: if lived in / if rented', '%s / %s' % (m(b['tax_live_T']), m(b['tax_rent_T'])), src('SCC-RATES', 'BOE-HOX')],
        ['Property B (San Francisco) assessed value and tax, 2025 (owner-supplied)', '%s / %s' % (m(P['sf_assessed']), m(P['sf_tax_2025'])), src('SF-TAX')],
        ['Federal basic exclusion per person, 2026', m(P['excl_2026']), src('RP-2026-35')],
        ['California estate or inheritance tax', 'None', src('SCO-ESTATE')],
    ]
    fig = table(['Figure (rounded to $10)', 'Value', 'Official basis'], rows, caption='Key figures')
    bb = D['baseline']
    res = [
        ['Sell now, invest in stocks', m(bb['sell']['real10']), m(bb['sell']['real_end']), src('IRS-FAQ-INHERIT', 'IRS-TC409')],
        ['Sell, park 24 months, then stocks', m(bb['sell_p24']['real10']), m(bb['sell_p24']['real_end']), src('TREASURY', 'IRS-TC409')],
        ['Rent 5 years, then sell', m(bb['rent5_sell']['real10']), m(bb['rent5_sell']['real_end']), src('IRS-P527', 'IRS-TC409')],
        ['Rent for good', m(bb['rent']['real10']), m(bb['rent']['real_end']), src('BOE-P19', 'RTC-63.2', 'IRS-P527')],
        ['Live in it for good', m(bb['live']['real10']), m(bb['live']['real_end']), src('BOE-P19', 'SCC-RATES')],
    ]
    rtab = table(['Path (inheritance %d, baseline)' % T, 'Real, 10 years', 'Real, 2076', 'Official basis'], res, caption='After-tax wealth, 2026 dollars')
    dl = [
        ['Death: record the date; order a written appraisal', 'PROB-16061.7'],
        ['Within 60 days: trustee serves the trust notice', 'PROB-16061.7'],
        ['Within 150 days: change-in-ownership statement to the Assessor', 'BOE-RULE-462.260'],
        ['Within 9 months: Form 706 if above the threshold (Form 4768 gives 6 more)', 'IRS-I706'],
        ['Within 1 year, only if moving in: homeowners\' exemption (BOE-266)', 'BOE-P19'],
        ['Within 3 years, only if moving in: parent-child claim (BOE-19-P)', 'BOE-P19'],
    ]
    dtab = table(['Deadline (see Process for the full list)', 'Official basis'], [[a, src(s)] for a, s in dl], caption='Deadlines')
    q_att = ('<ol><li>Is Property A held by a trust that is included in the Transferor\'s gross estate, so the date-of-death value becomes the basis? (Q01)</li>'
             '<li>What is the total gross estate, and how much federal exclusion is left after cash and other assets? (Q02)</li>'
             '<li>Is a Form 706 filed for a predeceased spouse, and is portability available? (Q02)</li>'
             '<li>How should the trust distribute Property A, and is any sale or transfer to a third party planned?</li>'
             '<li>Does Property B need any trust or deed change so that it is untouched by the plan?</li></ol>')
    q_cpa = ('<ol><li>What is the Inheritor\'s filing status and bracket, and is the sale-year tax rate as modelled? (Q05)</li>'
             '<li>Is a two-year residence test met before any live-then-sell path, and what is the §121 exclusion? (flag A16)</li>'
             '<li>How is depreciation recapture computed if Property A is rented first? (A16)</li>'
             '<li>How would interest on Treasuries parked after a sale be reported, and is a 24- or 36-month schedule workable? (A14, A15)</li>'
             '<li>What is the Schedule A and Form 8971 treatment, and what basis is reported? (Process step 13)</li></ol>')
    R = D['replays']
    n = len(R)
    s10 = sum(1 for r in R if r['res']['sell']['real10'] > r['res']['rent']['real10'])
    sE = sum(1 for r in R if r['res']['sell']['real_end'] > r['res']['rent']['real_end'])
    p10 = D['phase_vs_sell']['sell_p24']['wins10']
    body = """
<div class="brief">
<p class="bl"><strong>Question.</strong> After the Transferor\'s death, should the Inheritor live in Property A, rent it out, or sell it and reinvest, and should the proceeds be invested at once or phased in? Property B is already owned and is not part of the inheritance.</p>
<p class="bl"><strong>Answer on the numbers, if the basis resets to the date-of-death value.</strong> Selling beats renting in %d of %d real starting years after 10 years, and in %d of %d by 2076 (inheritance in %d, baseline). Phasing the sale over 24 months beats selling at once in only %d of %d starting years after 10 years, but it softens the 2008-type and 1929-type entries (see the Mixed and phased paths page). Both points are conditional on the basis reset and the flags below.</p>
<div class="two">
<div>%s%s</div>
<div>%s%s</div>
</div>
<div class="two">
<div><h3>Questions for the estate attorney</h3>%s</div>
<div><h3>Questions for the CPA / tax adviser</h3>%s</div>
</div>
<p class="bl"><strong>What would change the answer.</strong> (1) The trust is outside the gross estate (no basis reset) (Q01). (2) The Inheritor moves in and claims the parent-child relief in time, so the property tax stays low (BOE-P19). (3) A rate, exclusion or property-tax rule changes before the inheritance (flag A13). (4) Stock returns well below the 7%% baseline for the first decade (see <a href="whatif.html">What-if controls</a>).</p>
<p class="bl small">Figures are rounded to $10 and are model estimates in 2026 dollars, not forecasts. Owner-supplied figures are not confirmed by an official source; see <a href="flagged.html">Flagged for Review</a>. Not legal, tax or investment advice. Prepared for review by a licensed estate attorney and a tax adviser. People are placeholders: the Transferor and the Inheritor. Property A is Cupertino; Property B is San Francisco.</p>
</div>""" % (s10, n, sE, n, T, p10, n, fig, '', rtab, dtab, q_att, q_cpa)
    css = ('<style>@page{size:letter;margin:0.45in}@media print{header.top,nav,footer,.noprint{display:none!important}main.wrap{max-width:none;padding:0}'
           '.brief{font-size:8.6pt;line-height:1.28}}'
           '.brief{border:1px solid #333;padding:8px 10px;font-size:9pt}'
           '.brief h3{font-size:9.5pt;margin:4px 0 2px}.brief p.bl{margin:4px 0}.brief .small{font-size:7.6pt;color:#333}'
           '.brief table{font-size:8pt}.brief th,.brief td{padding:2px 4px}.brief ol{margin:2px 0 2px 16px;padding:0;font-size:8.2pt}'
           '.brief .two{display:grid;grid-template-columns:1fr 1fr;gap:8px}.brief .tablewrap{margin:0}</style>')
    body = css + '<p class="noprint"><button type="button" onclick="window.print()">Print this one-page sheet</button> Print at letter size; the page is set to fit on one sheet.</p>' + body
    page('briefing.html', 'Attorney &amp; CPA Briefing Sheet',
         'A single printable page for the estate attorney and the tax adviser: the question, the figures, the questions to answer, the deadlines and what would change the answer.', body)


# ------------------------------------------------------------------ timeline (used by the process page)
TIMELINE = [
    ('Now', 'Have the attorney confirm the trust type and the gross-estate status (Step 1). Keep the homeowners\' exemption right (Step 2).'),
    ('Day 0', 'Death: record the date; order an appraisal (Step 4).'),
    ('60 days', 'Trust notice served to beneficiaries (Step 5).'),
    ('150 days', 'Change-in-ownership statement filed with the Assessor (Step 7).'),
    ('9 months', 'Form 706 if above the filing threshold; Form 4768 gives six more months (Step 8).'),
    ('1 year', 'Homeowners\' exemption filed, only if the Inheritor moves in (Step 10).'),
    ('3 years', 'Parent-child exclusion claim, only if moving in (Step 11).'),
    ('Sale year', 'If sold: report on Form 8949 and Schedule D with the date-of-death basis (Step 13).'),
]


def timeline_html():
    items = ''.join('<li><span class="tl-when">%s</span><span class="tl-what">%s</span></li>' % (e(a), e(b)) for a, b in TIMELINE)
    return ('<h2>Deadlines as a timeline</h2><ol class="timeline" aria-label="Deadline timeline">%s</ol>'
            '<p class="note">Read left to right from the date of death. Dates are the periods stated in the linked official pages; check each one with the attorney.</p>' % items)


def build_all(D=None, M=None):
    D = D or _res()
    M = M or Bd.M
    build_paths(D)
    build_whatif(D)
    build_glossary()
    build_briefing(D, M)
    return D


EXTRA_CSS = """
.timeline{list-style:none;margin:10px 0 6px;padding:0;border-left:3px solid #1f4e8c}
.timeline li{display:flex;gap:12px;padding:6px 0 6px 14px;position:relative}
.timeline li:before{content:"";position:absolute;left:-8px;top:12px;width:12px;height:12px;border-radius:50%;background:#1f4e8c}
.tl-when{font-weight:700;min-width:96px;color:#12283f}
.whatif{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:12px 0}
.ctl{display:flex;flex-direction:column;font-size:14px;color:#33414e;gap:4px}
.ctl select{font:inherit;padding:6px;border:1px solid #c7ced6;border-radius:6px;background:#fff}
nav .grp{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#9fb6cf;margin:0 6px 0 14px;align-self:center}
"""


_CACHE = {}
_NAME = {'live': 'live for good', 'rent': 'rent for good', 'sell': 'sell and invest'}


def _D():
    if 'D' not in _CACHE:
        _CACHE['D'] = _res()
    return _CACHE['D']


def first_screen_html():
    """The first screen of the front door: headline, reinvestment risk beside it, and what would change the answer."""
    D = _D()
    bb, R, st = D['baseline'], D['replays'], D['replay_stats']
    worst = min(R, key=lambda r: r['res']['sell']['real10'])
    n = len(R)
    s10 = sum(1 for r in R if r['res']['sell']['real10'] > r['res']['rent']['real10'])
    ph = D['phase_vs_sell']['sell_p24']
    return ('<section class="first" aria-label="The answer on one screen">'
            '<h2>The answer on one screen</h2>'
            '<div class="firstgrid">'
            '<div><h3>Headline (baseline, inheritance in %d, basis reset)</h3>'
            '<p>On the 2076 measure the baseline ranks %s first. After-tax wealth in 2026 dollars, 10 years after inheritance: '
            '<strong>sell and invest %s</strong>, rent 5 years then sell %s, rent for good %s, live for good %s. '
            'Selling beats renting in %d of %d real starting years after 10 years.</p></div>'
            '<div><h3>Reinvestment risk, beside the headline</h3>'
            '<p>Worst of the %d real starting years for selling: <strong>%s</strong> at 10 years (start year %d), against %s for renting from the same year. '
            'Median of the %d starts: %s. Parking the proceeds for 24 months first costs up to %s in the worst start and %s in the median, at 10 years (2026 dollars).</p></div>'
            '</div>'
            '<div class="firstgrid">'
            '<div><h3>What would change the answer</h3><ol>'
            '<li>No basis reset: if the trust keeps Property A outside the estate, selling triggers income tax on decades of gain (%s, %s).</li>'
            '<li>Moving in and claiming the parent-child relief in time keeps the property tax low; renting or leaving it empty reassesses it (%s).</li>'
            '<li>Stock returns and inflation far from the baseline: see <a href="whatif.html">What-if controls</a> (ranges and sources shown).</li>'
            '<li>Law changes before the inheritance (%s, %s): nothing decades ahead can be verified today.</li>'
            '</ol></div>'
            '<div><h3>Next pages</h3><p><a href="paths.html">Mixed and phased paths</a> &middot; '
            '<a href="whatif.html">What-if controls</a> &middot; <a href="briefing.html">Attorney &amp; CPA Briefing Sheet (one page)</a> &middot; '
            '<a href="glossary.html">Glossary</a> &middot; <a href="process.html">Process and timeline</a></p></div>'
            '</div></section>') % (
        T, _NAME[max(('live', 'rent', 'sell'), key=lambda k: bb[k]['real_end'])],
        m(bb['sell']['real10']), m(bb['rent5_sell']['real10']), m(bb['rent']['real10']), m(bb['live']['real10']),
        s10, n,
        n, m(worst['res']['sell']['real10']), worst['start'], m(worst['res']['rent']['real10']),
        n, m(st['sell']['real10']['median']), m(ph['worst10']), m(ph['median10']),
        flag('Q01'), flag('Q02'), src('BOE-P19'),
        flag('A13'), src('RP-2026-35'))
