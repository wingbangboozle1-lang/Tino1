#!/usr/bin/env python3
"""Pages added by session arena/7895b5d7-tino1 (standard library only).

Called from final/build.py. Writes:
  phased.html     phased-investing test on real annual history (black swan)
  what-if.html    what-if controls over precomputed model cases, reinvestment risk beside the headline
  glossary.html   glossary, each term linked to its official page where one exists
  timeline.html   deadlines as a timeline (figures and rules taken from process.html)
  brief.html      one-page printable Attorney & CPA briefing sheet

Every dollar figure is rounded to $10 (build.r10 / build.m). Every table row ends in a link to an
official source (build.src). Nothing here stores or prints a name, address or account number.
"""
import json, os, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as MD                       # noqa: E402
import phased as PH                      # noqa: E402


def r10(x):
    return int(round(x / 10.0)) * 10


# ----------------------------------------------------------------- glossary and timeline data
# (term, definition, [source keys in final/sources.py S] or [] for a model term)
GLOSSARY = [
    ('Assessed value', 'The value on which California property tax is calculated. It is not the market value; it is the base year value, adjusted each year under Proposition 13.', ['BOE-P19']),
    ('Basic exclusion amount', 'The amount of a person\'s estate that is exempt from federal estate tax. It is $15,000,000 for deaths in 2026 under the federal statute as amended in 2025; it is indexed for inflation after 2026.', ['IRS-ESTATE', 'IRS-NEW']),
    ('Basis (stepped-up)', 'The starting figure for measuring a capital gain. For inherited property the basis is generally its fair market value on the date of death, or on the alternate valuation date if one is elected.', ['IRS-FAQ-INHERIT']),
    ('Base year value', 'The value fixed when a property last changed ownership. Under Proposition 13 it is adjusted by an inflation factor each year, capped at 2% a year.', ['RTC-51']),
    ('Break-even', 'A model term: the value of one input at which two paths give the same result, with every other input held at its baseline.', []),
    ('Black swan', 'A model term: a rare, extreme sequence of economic conditions outside the baseline. On this site it is shown through real historical replays and named stress paths, not as a forecast.', []),
    ('Change in ownership', 'A transfer that causes property to be reassessed to its current market value under California law, unless an exclusion applies. A transfer at death is a change in ownership.', ['RTC-480', 'BOE-P19']),
    ('CPI-U', 'The Consumer Price Index for All Urban Consumers, published by the U.S. Bureau of Labor Statistics. It is the common measure used to turn nominal dollars into real dollars.', ['BLS-CPI']),
    ('Depreciation (residential rental)', 'Yearly deduction for the building part of a rental property, spread over 27.5 years. It reduces taxable rent but is taxed back on a later sale.', ['IRS-P527']),
    ('Earthquake insurance', 'Separate cover for earthquake damage. Standard homeowners policies generally do not include earthquake damage; the California Department of Insurance explains the options.', ['CDI-EQ']),
    ('Empty homes tax (San Francisco)', 'A San Francisco tax on certain vacant residential property. Whether it applies to Property B is an open question, not an assumption on this site.', ['SF-EHT']),
    ('Estate tax', 'A federal tax on the transfer of a large estate at death. California has no estate tax for deaths after 2004.', ['SCO-ESTATE', 'IRS-ESTATE']),
    ('Form 706', 'The federal estate tax return. It is due nine months after death; a six-month extension is available on Form 4768.', ['IRS-I706', 'IRS-FAQ-ESTATE']),
    ('Form 1041', 'The income tax return for an estate or trust. It is required when the estate or trust has gross income of $600 or more in a year.', ['IRS-1041']),
    ('Gross estate', 'The property counted for federal estate tax at death. Whether Property A is in the Transferor\'s gross estate depends on the trust type and is an open question (Q01).', ['RR-2023-2']),
    ('Grantor trust (irrevocable)', 'A trust whose assets may fall outside the estate for estate tax. Under Revenue Ruling 2023-2, a basis step-up generally does not apply to such assets.', ['RR-2023-2']),
    ('Homeowners\' exemption', 'A $7,000 reduction in assessed value for an owner-occupied principal residence, claimed on form BOE-266.', ['BOE-HOX']),
    ('Homeowners insurance', 'Cover for the building and contents of an owner-occupied home. Premiums are set by each insurer; the California Department of Insurance publishes guides and a premium survey.', ['CDI-RES', 'CDI-TOOL']),
    ('Net-metering (NEM)', 'California billing for rooftop solar that credits exported power against the bill. The rules of the tariff set how long a credit is carried.', ['CPUC-NEM']),
    ('Net investment income tax (NIIT)', 'A 3.8% federal tax on certain investment income above income thresholds. It can apply to a gain on a sale.', ['IRS-TC559']),
    ('Parent-child exclusion (Proposition 19)', 'The rule that lets a child keep a parent\'s assessed value on a family home, up to the excluded amount, if the child makes it a principal residence within a year and claims the exclusion within three years.', ['BOE-P19', 'SCC-P19']),
    ('Phased investing', 'A model term: moving cash into stocks in equal tranches over several years rather than all at once. Tested on the phased-investing page.', []),
    ('Portability', 'Transfer of a deceased spouse\'s unused federal exclusion to the surviving spouse. It requires a timely Form 706 return.', ['IRS-FAQ-ESTATE']),
    ('Probate notice (trust)', 'The duty of a successor trustee to notify beneficiaries and heirs after a trust becomes irrevocable at death. The statute sets a 60-day period.', ['PROB-16061.7']),
    ('Proposition 13', 'The 1978 California constitutional amendment. It caps the property tax rate at 1% of assessed value plus voter-approved debt, and limits assessed-value growth to 2% a year.', ['RTC-51']),
    ('Real vs nominal', 'Nominal means the dollars of that year. Real means the same amount expressed in dollars of the start year, using CPI. The site shows both.', ['BLS-CPI']),
    ('Reinvestment risk', 'A model term: the risk that proceeds, or cash waiting to be invested, earn less than the planned return. The what-if page shows it next to the headline.', []),
    ('Revocable trust', 'A trust the creator can change or revoke while alive. Its assets are generally counted in the creator\'s estate; the trust terms and the attorney decide the specifics.', ['RR-2023-2']),
    ('Rent control (San Francisco)', 'Limits on yearly rent increases for covered units, set by the San Francisco Rent Board. The limit is tied to inflation.', ['SF-RENT-RULES']),
    ('Safmr (HUD small-area fair market rent)', 'A federal benchmark rent by ZIP code, published by HUD. It is a benchmark only; it is not a quote for any property.', ['HUD-95014', 'HUD-94122']),
    ('Secured property tax', 'The annual property tax on real estate, secured by the land. In San Francisco the rate for the year is published by the Treasurer and Tax Collector.', ['SF-TAX']),
    ('Sequence risk', 'A model term: the risk that the order of good and bad years, not just the average, decides the outcome. It is why the replays use real sequences.', []),
    ('Section 121 exclusion', 'Exclusion of part of a gain on a principal residence: $250,000 for a single owner, $500,000 for a married couple filing jointly, if the owner-use test is met.', ['IRS-TC701']),
    ('Step-up in basis', 'See Basis (stepped-up).', ['IRS-FAQ-INHERIT']),
    ('Supplemental assessment', 'An extra property tax bill for the period after a change in ownership, when the new value is higher than the old one.', ['SF-TAX']),
    ('Tax rate book', 'The county document that sets the property tax rates for each area for the year.', ['SCC-RATES']),
    ('Treasury bill, note, bond', 'U.S. government debt. Bills mature within a year; notes run two to ten years; bonds longer. Yields change daily; the Treasury publishes them.', ['TREASURY']),
    ('Unrecaptured section 1250 gain', 'The part of a gain on depreciated real estate that is taxed at up to 25% federally.', ['IRS-TC409']),
]

TIMELINE = [
    ('Now, while the Transferor is alive', 'Ask the estate attorney which trust holds Property A and whether it is in the gross estate (Q01). Keep the homeowners\' exemption on file.', ['RR-2023-2', 'BOE-HOX']),
    ('Date of death (day 0)', 'Record the date. Order a written appraisal as of that date: it sets the basis and the change-in-ownership value.', ['IRS-FAQ-INHERIT']),
    ('Within 60 days', 'The successor trustee notifies every beneficiary and heir.', ['PROB-16061.7']),
    ('Within 150 days', 'File the change-in-ownership statement for Property A with the Santa Clara County Assessor.', ['RTC-480']),
    ('Within 9 months', 'File Form 706 if the estate is above the filing threshold or to elect portability. Form 4768 adds six months.', ['IRS-I706', 'IRS-FAQ-ESTATE']),
    ('Within 1 year (only if moving in)', 'Become the principal residence and file the homeowners\' exemption (BOE-266) before the exclusion claim.', ['RTC-63.2', 'BOE-PUB-800-1']),
    ('Within 3 years (only if moving in)', 'File the parent-child exclusion claim (BOE-19-P) with the Assessor, before any transfer to a third party.', ['BOE-P19', 'SCC-P19']),
    ('February 2027 (rule change date)', 'The Proposition 19 allowance of $1,044,586 applies until 2027-02-15; the next adjustment takes effect on 2027-02-16. Adjustments are made every second year.', ['BOE-LTA-2025-009']),
    ('Tax year of any sale', 'Report the sale on Form 8949 and Schedule D using the date-of-death basis.', ['IRS-FAQ-INHERIT', 'IRS-TC409']),
    ('Five years after death', 'Last date for a late portability election under the IRS relief procedure.', ['IRS-FAQ-ESTATE']),
]


# ----------------------------------------------------------------- helpers
def r10(x):
    return int(round(x / 10.0)) * 10


def pc_(x, d=1):
    return ('%.' + str(d) + 'f%%') % (x * 100)


def flagged(fid):
    return '<a class="flag" href="flagged.html#%s" title="Flagged for review">flag %s</a>' % (fid, fid)


def _srcs(B, keys):
    return B.src(*keys) if keys else '<span class="blank">model term - no official page</span>'


def _money(x):
    v = r10(x)
    return ('-$' if v < 0 else '$') + format(abs(v), ',')


# ----------------------------------------------------------------- what-if cases (precomputed)
G_OPTS = [0.03, 0.04, 0.05]                         # Property A home growth a year (baseline 4.0%)
R_OPTS = [0.05, 0.07, 0.10]                         # stock return a year (baseline 7.0%)
RENT_OPTS = [('3br', 5870), ('4br', 6390), ('up30', r10(6390 * 1.3))]   # Cupertino rent a month (baseline 4br)
INF_OPTS = [0.025, 0.04]                            # inflation (baseline 2.5%)
T_OPTS = [2040, 2045, 2050]                         # year of inheritance (baseline 2045); the owner's window is 2040 to 2050


def cell_key(g, r, rent, inf, t):
    return '%.2f|%.2f|%s|%.3f|%d' % (g, r, rent, inf, t)


def whatif_cases():
    cases = {}
    for g in G_OPTS:
        for r in R_OPTS:
            for rk, rent in RENT_OPTS:
                for inf in INF_OPTS:
                  for t in T_OPTS:
                    d = inf - MD.P['infl']          # 4% inflation raises nominal rates by the same 1.5 points
                    kw = dict(g_cup=g + d, g_ca=g + d, r_stock=r + d, r_bond=MD.P['r_bond'] + d,
                              r_bill=MD.P['r_bill'] + d, infl=inf, cup_rent_month=rent, T=t)
                    _, s = MD.run(MD.with_(**kw))
                    _, sb = MD.run(MD.with_(**dict(kw, w_stock=0.0, w_bill=1.0)))
                    cases[cell_key(g, r, rk, inf, t)] = dict(
                        live=r10(s['w_live']), rent=r10(s['w_rent']), sell=r10(s['w_sell']),
                        live_real=r10(s['real_live']), rent_real=r10(s['real_rent']), sell_real=r10(s['real_sell']),
                        best=s['best'], sell_net=r10(s['sell_net']),
                        sell_bills=r10(sb['w_sell']), sell_bills_real=r10(sb['real_sell']),
                        bills_gap=r10(s['w_sell'] - sb['w_sell']))
    return cases


def bills_gap():
    """Baseline reinvestment check: the sell path with proceeds in bills instead of stocks (2076, nominal)."""
    _, s = MD.run(MD.P)
    _, sb = MD.run(MD.with_(w_stock=0.0, w_bill=1.0))
    return dict(sell=r10(s['w_sell']), sell_bills=r10(sb['w_sell']), gap=r10(s['w_sell'] - sb['w_sell']))


def bills_gap_text():
    g = bills_gap()
    return '%s less' % _money(g['gap'])


# ----------------------------------------------------------------- pages
PATH_NAMES = {'lump': 'Lump sum into stocks on day one (no parking)',
              'park2_phase2': 'Park 24 months, then 2 equal annual tranches',
              'park2_phase3': 'Park 24 months, then 3 equal annual tranches',
              'park3_phase2': 'Park 36 months, then 2 equal annual tranches',
              'park3_phase3': 'Park 36 months, then 3 equal annual tranches'}
PATH_ORDER = ['lump', 'park2_phase2', 'park2_phase3', 'park3_phase2', 'park3_phase3']
EPISODES = ['1929', '1937', '2000', '2007', '2008']


def phased_claims():
    res = json.load(open(os.path.join(HERE, 'out', 'phased.json')))
    s = res['summary'][PH_KEY]
    return dict(n=s['starts'], not_deeper=s['years_drop_not_deeper'], shallower=s['years_drop_strictly_shallower'],
                share_higher=s['share_phased_ends_higher'])


PH_KEY = 'park2_phase2'


def PHASED_SRC(B):
    return (B.src('TREASURY') + ' (official reference for bill yields) · ' + B.src('DAMODARAN')
            + ' (stock and bill returns; academic table, not government)')


def build_phased(B, res):
    ep = res['episodes']
    proceeds = res.get('proceeds') or 0
    rows = []
    for k in PATH_ORDER:
        cells = ['%.2f times; worst drop %s' % (ep[c]['paths'][k]['end'], pc_(ep[c]['paths'][k]['mdd'], 0)) for c in EPISODES]
        rows.append([PATH_NAMES[k]] + cells + [PHASED_SRC(B)])
    t1 = B.table(['Path (proceeds start at the entry year)'] + ['%s entry' % c for c in EPISODES] + ['Source'], rows,
                 caption='Value 10 years after entry, per 1 dollar of proceeds, and the worst fall from a peak inside those 10 years',
                 note='A worst drop of -65% means the account fell 65%% from its highest point before recovering. Figures are gross: before tax, costs and inflation. Annual resolution: each calendar year is one step.')
    drows = [[PATH_NAMES[k]] + [_money(proceeds * ep[c]['paths'][k]['end']) for c in EPISODES] + [PHASED_SRC(B)] for k in PATH_ORDER]
    t2 = B.table(['Path'] + ['%s entry' % c for c in EPISODES] + ['Source'], drows,
                 caption='The same test in dollars: 10 years after entry, starting from baseline net sale proceeds of %s' % _money(proceeds),
                 note='The starting amount is the model\'s baseline net sale proceeds in the inheritance year, after selling costs, carrying costs and the sale tax, rounded to $10. Real proceeds depend on the actual sale price and tax, which are not yet known.')
    srows = []
    for k in PATH_ORDER[1:]:
        s = res['summary'][k]
        srows.append([PATH_NAMES[k], pc_(s['share_phased_ends_higher'], 0), pc_(s['median_end_vs_lump'], 0),
                      pc_(s['median_mdd_lump'], 0) + ' to ' + pc_(s['median_mdd_phased'], 0),
                      pc_(s['worst_mdd_lump'], 0) + ' to ' + pc_(s['worst_mdd_phased'], 0), PHASED_SRC(B)])
    nstarts = res['summary'][PATH_ORDER[1]]['starts']
    t3 = B.table(['Path', 'Share of entry years that end higher than the lump sum', 'Median 10-year result vs lump sum',
                  'Median worst drop: lump sum to phased', 'Worst drop in any year tested: lump sum to phased', 'Source'], srows,
                 caption='All %d entry years tested, %d to %d' % (nstarts, res['first_start'], res['last_start']),
                 note='Reading: in most entry years the lump sum ends higher, because stocks rose in most years. Phasing reduces the worst falls. That is the trade-off the owner is choosing between.')
    bs = res['bill_stats']
    oc = res['official_check']
    _nyu = [abs(v) for v in oc['nyu_bill_minus_tb3ms_pts'].values() if v is not None][:4]
    _nyu_08_10 = max(abs(oc['nyu_bill_minus_tb3ms_pts'][str(y)]) for y in (2008, 2009, 2010))
    _gap = [oc['gs2_minus_tb3ms_pts'][str(y)] for y in (2008, 2009, 2010)]
    _moves = [v['change_pct_of_proceeds'] for s_ in oc['sleeve_2y'].values() for k_, v in s_.items() if k_.startswith('park')]
    def _order(d):
        return sorted(k_ for k_ in d if k_.startswith('park') or k_ == 'lump_end') 
    _same = all(
        sorted((k_ for k_ in oc['sleeve_2y'][s_] if k_.startswith('park')), key=lambda k_: -oc['sleeve_2y'][s_][k_]['bill_proxy_end'])
        == sorted((k_ for k_ in oc['sleeve_2y'][s_] if k_.startswith('park')), key=lambda k_: -oc['sleeve_2y'][s_][k_]['two_year_sleeve_end'])
        for s_ in oc['sleeve_2y'])
    _same_txt = 'does not change' if _same else 'CHANGES'
    _nyu_txt = '%.2f' % _nyu_08_10
    _parked_li = ("<li><strong>Parked cash is a proxy, now checked against official data.</strong> The test parks cash in the "
                  "3-month bill. On 2026-11-16 that bill return was checked against the official 3-month annual averages: within %s points "
                  "for 2008 to 2010. The 2-year Treasury, which the brief names, paid %s to %s points more in 2008 to 2010 (official annual "
                  "averages). Using it for 2007 to 2010 raises the parked-path results by %s to %s percent of the proceeds and %s the order "
                  "of the four parked paths in either entry year. Yields are not total returns, and a ladder return from daily data is not "
                  "computed (flag A14). %s</li>") % (_nyu_txt, '%.2f' % min(_gap), '%.2f' % max(_gap), '%.1f' % min(_moves),
                  '%.1f' % max(_moves), _same_txt, B.src('FRED-GS2', 'FRED-TB3MS'))
    body = """
<h2>What the test asks</h2>
<ul>
<li><strong>Question.</strong> If the sale proceeds wait in short Treasuries for 24 or 36 months after the inheritance, and only then move into stocks, how much of a crash that starts at entry is avoided, and what does the wait cost in years with no crash?</li>
<li><strong>Method.</strong> Real annual history from 1928 to 2025. Cash earns the 3-month Treasury bill return; stocks earn the S&amp;P 500 total return. Each path is followed for 10 years after entry. Tranches are equal and move at the start of each year. %s</li>
%s
</ul>
""" % (flagged('S-PHASE'), _parked_li) + t1 + t2 + t3 + """
<h2>Reinvestment risk on the parked cash</h2>
<p>Parked cash earns whatever bills yield in those years, and that is not fixed. The average 3-month bill return was about <strong>%s</strong> a year over 1928 to 2025, about <strong>%s</strong> over 1929 to 1931, and about <strong>%s</strong> over 2009 to 2015. The parked cash earns no stock growth, so a long wait gives up part of any recovery. %s</p>
""" % (pc_(bs['all_1928_2025'], 1), pc_(bs['y1929_1931'], 1), pc_(bs['y2009_2015'], 2), PHASED_SRC(B)) + """
<h2>How to read it</h2>
<ul>
<li>Phasing does not avoid losses that come after the stocks are bought. In the 1929 test the phased paths still fell about 35%% from their peak, because they bought stocks in 1931, before the rebound.</li>
<li>In the 2007 test the parked cash stayed out of stocks through 2008 and the worst drop was 0%%: the wait avoided the crash. Parking was ahead of the lump sum after 10 years.</li>
<li>The 2008 row is the same crash seen from inside it: the entry year is the crash year, so the lump sum fell %s in its first twelve months while the parked paths had no fall at all. After ten years the 24-month park was still %s ahead of the lump sum on gross returns, even though the bill paid almost nothing in 2008 to 2010.</li>
<li>@@CLAIM@@</li>
<li>The test uses one entry date per row. A real decision also depends on tax, cash needed for carrying costs, and how much fall in value the owner can accept.</li>
</ul>
<h2>Limits and sources</h2>
<ul>
<li>Annual data. A calendar year is one step, so the October 1929 crash appears only in the full-year 1929 return. Intra-year drops are understated.</li>
<li>Gross of tax, selling costs, carrying costs and inflation. The <a href="decision.html">Decision</a> page carries those; this page isolates timing.</li>
<li>Stock and bill returns come from an academic table, not a government source. This is flagged for review: <a href="flagged.html#S-PHASE">Flagged for Review</a>.</li>
<li>Results are historical. Future sequences can differ; the <a href="black-swan.html">Black swan</a> page shows named stress paths, and carries the same test run through the model itself, after tax and after inflation.</li>
</ul>
""" % (pc_(ep['2008']['stock_1yr'], 0), pc_(ep['2008']['paths']['park2_phase2']['end_vs_lump'], 0))
    c = phased_claims()
    claim = ('Across the %d entry years, the phased worst drop was never deeper than the lump sum&rsquo;s, and it was strictly shallower in %d of them '
             '(24-month park, 2 tranches). The phased path ends higher than the lump sum in only %s of entry years, so the benefit is protection against one bad entry, not a higher average return.'
             % (c['n'], c['shallower'], pc_(c['share_higher'], 0)))
    body = body.replace('@@CLAIM@@', claim)
    B.page('phased.html', 'Phased investing: parking proceeds before stocks',
           'Does parking the sale proceeds in short Treasuries for 24 to 36 months soften entry into a crash? Tested on real annual history, 1928 to 2025.', body)


def build_whatif(B, cases):
    d = dict(g='0.04', r='0.07', rent='4br', inf='0.025')
    controls = """<div class="ctrl">
<label>Home growth a year, Property A <select id="c-growth"><option value="0.03">3.0%</option><option value="0.04" selected>4.0% (baseline)</option><option value="0.05">5.0%</option></select></label>
<label>Stock return a year <select id="c-stock"><option value="0.05">5.0%</option><option value="0.07" selected>7.0% (baseline)</option><option value="0.10">10.0%</option></select></label>
<label>Cupertino rent a month <select id="c-rent"><option value="3br">HUD 3-bedroom, $5,870</option><option value="4br" selected>HUD 4-bedroom, $6,390 (baseline)</option><option value="up30">HUD 4-bedroom plus 30%, $8,310</option></select></label>
<label>Year of inheritance <select id="c-t"><option value="2040">2040</option><option value="2045" selected>2045 (baseline)</option><option value="2050">2050</option></select></label>
<label>Inflation a year <select id="c-infl"><option value="0.025" selected>2.5% (baseline)</option><option value="0.04">4.0% (nominal rates raised 1.5 points)</option></select></label>
</div>"""
    body = """
<div class="kpis">
<div class="kpi"><div class="k">Best path in the chosen case</div><div class="v" id="best">-</div><div class="sub" id="bestsub"></div></div>
<div class="kpi"><div class="k">Reinvestment risk, beside the headline</div><div class="v" id="rrisk">-</div><div class="sub">Sell path with the proceeds held in Treasury bills at the bill yield, instead of stocks. Shown beside the headline on purpose.</div></div>
</div>
<h2>Controls</h2>
<p>Choose a case. Each choice selects one of %d precomputed model runs (%d cases in all). The browser does no estimating and sends nothing; the figures were produced by <code>final/extras.py</code> from the model. Defaults are the baseline.</p>
%s
<h2>Result for the chosen case</h2>
<div class="tablewrap"><table><caption>Wealth in 2076, nominal and in today's dollars, with the reinvestment check</caption>
<thead><tr><th scope="col">Path</th><th scope="col">Nominal, 2076</th><th scope="col">Today's dollars, 2076</th><th scope="col">Sell path if proceeds sit in bills (reinvestment check)</th><th scope="col">Source</th></tr></thead>
<tbody>
<tr><td>Live in Property A (the Inheritor moves in)</td><td id="w-live"></td><td id="r-live"></td><td>not applicable</td><td>%s</td></tr>
<tr><td>Rent Property A out</td><td id="w-rent"></td><td id="r-rent"></td><td>not applicable</td><td>%s</td></tr>
<tr><td>Sell Property A and reinvest the proceeds</td><td id="w-sell"></td><td id="r-sell"></td><td id="rb-sell"></td><td>%s</td></tr>
</tbody></table></div>
<p class="note">Baseline sell-path net proceeds in the inheritance year (this case): <span id="sellnet"></span>. Only the five controls change; every other input is at its baseline (see the <a href="decision.html">Decision</a> page and <a href="sources.html">Sources and method</a>). Rounded to the nearest $10.</p>
<h2>What the controls can and cannot show</h2>
<ul>
<li>Each control moves one group of inputs together. The controls do not cover every risk; the <a href="black-swan.html">Black swan</a> page covers sequences of years.</li>
<li>The rent figures are HUD benchmarks, not a quote for Property A. The bedroom count is unknown (%s).</li>
<li>The 4.0%% inflation case raises nominal stock, bond, bill and home growth by the same 1.5 points, as the Decision page does.</li>
</ul>
<script src="whatif.js"></script>
""" % (len(cases), len(cases), controls,
       B.src('HUD-95014', 'BLS-CPI'), B.src('HUD-95014', 'FHFA-SJ'), B.src('DAMODARAN', 'TREASURY'), flagged('U08'))
    B.page('what-if.html', 'What-if controls',
           'Change growth, returns, rent or inflation and see which path comes out ahead, with reinvestment risk beside the headline.', body)
    open(os.path.join(B.OUT, 'whatif.js'), 'w').write(
        '// Generated by final/extras.py from the model. Reads precomputed cases only: no network, no storage.\n'
        'var WHATIF = ' + json.dumps(dict(cases=cases), sort_keys=True) + ';\n' + WHATIF_JS)


WHATIF_JS = """(function () {
  function fmt(x) { var v = Math.round(x / 10) * 10; return (v < 0 ? '-$' : '$') + Math.abs(v).toLocaleString('en-US'); }
  function val(id) { return document.getElementById(id).value; }
  function set(id, t) { var el = document.getElementById(id); if (el) el.textContent = t; }
  var NAMES = { live: 'Live in Property A', rent: 'Rent Property A out', sell: 'Sell and reinvest' };
  function show() {
    var key = [parseFloat(val('c-growth')).toFixed(2), parseFloat(val('c-stock')).toFixed(2), val('c-rent'), parseFloat(val('c-infl')).toFixed(3), val('c-t')].join('|');
    var c = WHATIF.cases[key];
    if (!c) { set('best', 'not computed'); return; }
    set('best', NAMES[c.best]);
    set('bestsub', 'Nominal wealth in 2076: ' + fmt(c[c.best]) + '. In today\\'s dollars: ' + fmt(c[c.best + '_real']) + '.');
    set('rrisk', fmt(c.bills_gap) + ' less in 2076, nominal');
    set('w-live', fmt(c.live)); set('r-live', fmt(c.live_real));
    set('w-rent', fmt(c.rent)); set('r-rent', fmt(c.rent_real));
    set('w-sell', fmt(c.sell)); set('r-sell', fmt(c.sell_real));
    set('rb-sell', fmt(c.sell_bills) + ' (today\\'s dollars: ' + fmt(c.sell_bills_real) + ')');
    set('sellnet', fmt(c.sell_net));
  }
  ['c-growth', 'c-stock', 'c-rent', 'c-infl', 'c-t'].forEach(function (id) {
    document.getElementById(id).addEventListener('change', show);
  });
  show();
})();
"""


def build_glossary(B):
    rows = []
    for term, text, keys in GLOSSARY:
        rows.append('<div class="gl"><dt>%s</dt><dd>%s <span class="gsrc">%s</span></dd></div>' % (
            html.escape(term), html.escape(text), _srcs(B, keys)))
    body = ('<p class="note">Terms marked <em>model term</em> are this site\'s own words for the analysis, not legal or tax terms. '
            'Read each definition as a pointer to the official page, not as a full statement of the law. '
            'The attorney and the tax adviser decide how a term applies to this trust.</p>'
            '<div class="glossary"><dl>%s</dl></div>') % ''.join(rows)
    B.page('glossary.html', 'Glossary', 'Plain-English meanings of the terms used on this site, each linked to its official page.', body)


def build_timeline(B):
    items = []
    for when, what, keys in TIMELINE:
        items.append('<li><div class="tlwhen">%s</div><div class="tlwhat">%s <span class="gsrc">%s</span></div></li>' % (
            html.escape(when), html.escape(what), B.src(*keys)))
    body = ('<p class="note">Deadlines are the ones on the <a href="process.html">Process</a> page, arranged in time order. '
            'Each row links to the statute, form or agency page it comes from. Counting starts from the date of death.</p>'
            '<ol class="timeline">%s</ol>') % ''.join(items)
    B.page('timeline.html', 'Deadlines as a timeline',
           'When each step falls, counted from the date of death. Confirm every date with the attorney and the county office.', body)


def build_brief(B, cases):
    """One printable page for the estate attorney and the tax adviser (no site chrome)."""
    s = B.B
    P = B.P
    T = B.T
    rows = [
        ('Market value of Property A in %d (model)' % T, _money(s['fmv_T']), 'Owner estimate %s today, growing at an assumed 4.0%% a year' % _money(P['cup_value']), B.src('FHFA-SJ')),
        ('Assessed value just before death (model)', _money(s['fbyv_T']), 'Proposition 13 base year value, inflation-adjusted', B.src('RTC-51')),
        ('Proposition 19 allowance (model)', _money(s['cap_T']), '$1,044,586 until 2027-02-15, then adjusted', B.src('BOE-LTA-2025-009')),
        ('New assessed value if the Inheritor moves in', _money(s['taxable_live_T']), 'Excluded amount plus the excess over it', B.src('BOE-LTA-2026-026')),
        ('New assessed value if rented or held for sale', _money(s['taxable_rent_T']), 'Full market value', B.src('BOE-P19')),
        ('Property tax the first year, if lived in / if rented (model)', '%s / %s' % (_money(s['tax_live_T']), _money(s['tax_rent_T'])), 'Official Santa Clara rate components before fixed charges', B.src('SCC-RATES')),
        ('Net sale proceeds if sold (model)', _money(s['sell_net']), 'After 5% selling cost and carrying costs; basis reset assumed', B.src('SCC-DTT')),
        ('Federal estate tax exclusion, 2026', '$15,000,000 per person', 'Estate size unknown (Q02); no California estate tax', B.src('IRS-ESTATE', 'SCO-ESTATE')),
    ]
    trows = ''.join('<tr><td>%s</td><td class="num">%s</td><td>%s</td><td class="small">%s</td></tr>' % (html.escape(a), html.escape(b), html.escape(c), d) for a, b, c, d in rows)
    names = {'live': 'live in Property A', 'rent': 'rent Property A out', 'sell': 'sell and reinvest'}
    n_other = sum(1 for c in cases.values() if c['best'] != s['best'])
    ranking = ('On the baseline the model ranks <strong>%s</strong> first, after tax. In %d of the %d what-if cases another path ranks first, so the ranking is not settled (site: What-if controls).'
               % (names[s['best']], n_other, len(cases)))
    trows = ''.join('<tr><td>%s</td><td class="num">%s</td><td>%s</td><td class="small">%s</td></tr>' % (html.escape(a), html.escape(b), html.escape(c), d) for a, b, c, d in rows)
    atty = ['Which trust holds Property A, and is it in the gross estate? (Q01: the basis reset depends on it.)',
            'Does the trust plan to distribute Property A in kind, or sell it first? Who is the successor trustee?',
            'Is there a deceased spouse whose unused exclusion could be ported? Was a Form 706 filed? (Q02)',
            'Confirm the 60-day notice and the 150-day change-in-ownership filing dates for this trust.',
            'Confirm the Transferor is the Inheritor\'s parent (or meets the grandchild rule) for the parent-child exclusion. (Q06)']
    cpa = ['Rerun the comparison with the Inheritor\'s actual bracket and filing status. (Q05)',
           'Confirm the basis step-up under the trust type, and the date-of-death appraisal used for basis. (Q01)',
           'Property B: the owner\'s basis and depreciation already claimed on the rented units. (Q03)',
           'Form 1041 for the trust or estate while the home is held; treatment of rent received before distribution.',
           'Whether the solar credit and the rent on Property B are reported as the model assumes. Unverified items are on Flagged for Review.']
    body = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><meta name="referrer" content="no-referrer">
<title>Attorney and CPA briefing sheet - Two-home inheritance analysis</title>
<style>
@page{size:letter;margin:.45in}
body{font:9.3pt/1.28 system-ui,Arial,sans-serif;color:#111;margin:0;background:#fff}
.sheet{max-width:7.5in;margin:0 auto;padding:.1in 0}
h1{font-size:15pt;margin:0 0 2px}
.sub{font-size:8.5pt;color:#333;margin:0 0 6px}
h2{font-size:10.5pt;margin:8px 0 3px;border-bottom:1px solid #999;padding-bottom:1px}
table{width:100%%;border-collapse:collapse;font-size:8.2pt}
td,th{border:1px solid #bbb;padding:2px 4px;vertical-align:top;text-align:left}
th{background:#eee}
td.num{white-space:nowrap;text-align:right}
ol,ul{margin:2px 0 0 16px;padding:0}li{margin:1px 0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.small{font-size:7.8pt;color:#333}
.noprint{margin:0 0 8px}
@media print{.noprint{display:none}}
</style></head><body><div class="sheet">
<p class="noprint"><a href="index.html">Back to the site</a> &middot; use your browser's Print command (Ctrl+P / Cmd+P) for one page.</p>
<h1>Attorney and CPA Briefing Sheet</h1>
<p class="sub">Two-home inheritance analysis. Property A = the Cupertino home (ZIP 95014) to be inherited by trust around 2040-2050. Property B = the San Francisco three-unit home (ZIP 94122) already owned by the Inheritor. People are placeholders: the Transferor and the Inheritor. Figures are model outputs rounded to the nearest $10 and are not advice; the estate attorney and tax adviser decide the law as it applies.</p>
<h2>Key figures for the inheritance year (%d, model; assumptions flagged on the site)</h2>
<table><thead><tr><th>Item</th><th>Amount</th><th>Basis</th><th>Official source</th></tr></thead><tbody>%s</tbody></table>
<h2>Best path on the model, and why it changes</h2>
<p>%s If the basis is not reset at death, selling loses its advantage over renting (Q01).</p>
<div class="two">
<div><h2>For the estate attorney</h2><ol>%s</ol></div>
<div><h2>For the CPA / tax adviser</h2><ol>%s</ol></div>
</div>
<h2>Deadlines (from the date of death)</h2>
<p class="small">Notice to beneficiaries within 60 days (Prob. Code 16061.7); change-in-ownership filing within 150 days (R&amp;T Code 480); Form 706 within 9 months, six more with Form 4768; homeowners' exemption and principal-residence move within 1 year and the exclusion claim (BOE-19-P) within 3 years, only if the Inheritor moves in. Full timeline on the site.</p>
<h2>Official sources to check</h2>
<p class="small">IRS estate tax (irs.gov/businesses/small-businesses-self-employed/estate-tax) &middot; IRS inherited property FAQ (irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances) &middot; Rev. Rul. 2023-2 (irs.gov/irb/2023-16_IRB) &middot; California Board of Equalization Proposition 19 (boe.ca.gov/prop19/) &middot; BOE LTA 2025/009 (boe.ca.gov/proptaxes/pdf/lta25009.pdf) &middot; BOE Pub. 800-1 (boe.ca.gov/pdf/pub800-1.pdf) &middot; California Controller estate tax (sco.ca.gov/ardtax_estate_tax.html) &middot; Santa Clara County Assessor (asr.santaclaracounty.gov).</p>
<p class="small">Open questions Q01 to Q06 and the Flagged for Review list are on the site. Nothing here is verified legal or tax advice. Prepared from the site's model; confirm every figure before it is used.</p>
</div></body></html>""" % (T, trows, ranking, ''.join('<li>%s</li>' % html.escape(x) for x in atty), ''.join('<li>%s</li>' % html.escape(x) for x in cpa))
    from scrub import scrub   # publication scrub (session 6f85fbe1): ZIP codes and city name in visible text
    open(os.path.join(B.OUT, 'brief.html'), 'w').write(scrub(body))


def build_all(B):
    """Called from final/build.py after the core pages are written."""
    res = json.load(open(os.path.join(HERE, 'out', 'phased.json')))
    build_phased(B, res)
    cases = whatif_cases()
    build_whatif(B, cases)
    build_glossary(B)
    build_timeline(B)
    build_brief(B, cases)
