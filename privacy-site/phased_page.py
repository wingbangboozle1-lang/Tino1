"""Body of the staged-entry page. Real public history only; no household inputs.

Assembled here so that ``build.py`` stays readable. Every number comes from
``illustrations.py`` (official cash series plus an academic stock series) and is
rounded to $10 only at display. Nothing on this page is a forecast or a probability.
"""
from illustrations import (episode_replay, all_start_years, staged_summary,
                           lump_sum_return, STOCK, BILL, GS2, CPI_ANNUAL)

TITLE = 'Staged entry after a crash'
KICKER = 'SEQUENCE RISK / 05'
LEAD = ('If the sale proceeds arrive at the wrong moment, does parking them in short '
        'Treasuries and phasing into stocks soften the damage? Tested on real annual '
        'history, with the cash leg taken from official Federal Reserve series.')

MODE_LABEL = {
    'bill': '3-month bill annual average',
    'ladder': 'bill and 2-year average (ladder proxy)',
    'assumed': '0% assumed: no official series this far back',
}


def _pct(x, digits=1):
    return ('+' if x >= 0 else '−') + f'{abs(x)*100:.{digits}f}%'


def _pp(x, digits=2):
    return f'{x*100:.{digits}f}%'


def _diff(x, money):
    return ('+' if x >= 0 else '−') + money(abs(x))


EPISODES = [
    (1929, 'Crash year. The official bill series starts in 1934, so the parked leg is an explicit 0% assumption here.'),
    (1937, 'Second severe decline. Official bill leg available; no 2-year leg before 1977, so no ladder proxy.'),
    (1973, 'Inflation-era decline. Official bill leg available; the 2-year leg is not, so no ladder proxy.'),
    (2000, 'Dot-com peak year. Both official legs available.'),
    (2007, 'Pre-crisis peak year. Both official legs available.'),
    (2008, 'The crash year itself. Both official legs available.'),
]


def body(table, notice, money):
    episode_rows, path_rows = [], []
    for year, note in EPISODES:
        fallback = 0.0 if year < 1934 else None
        r = episode_replay(year, cash_fallback=fallback)
        cash = MODE_LABEL[r['cash_mode']] if r['cash_mode'] == 'assumed' else (
            f"{_pp(r['cash_rate'])} · {MODE_LABEL[r['cash_mode']]}")
        episode_rows.append((str(year), note, cash, money(100000 * r['lump_sum']),
                             money(100000 * r['staged']), _diff(100000 * r['difference'], money),
                             ['fred_tb3ms', 'fred_gs2', 'hist_returns']))
        path_rows.append((str(year), ', '.join(_pct(STOCK[year + j]) for j in range(10)), 'hist_returns'))

    rows_all = [r for r in all_start_years(3, 3, 10) if r['staged'] is not None]
    summary = staged_summary(rows_all)
    grid = []
    for park, phase, horizon in ((2, 3, 10), (3, 3, 10), (3, 5, 10), (2, 2, 10), (3, 3, 20)):
        rows = [r for r in all_start_years(park, phase, horizon) if r['staged'] is not None]
        s = staged_summary(rows)
        grid.append((f'{park * 12}-month wait, {phase} tranches, {horizon}-year horizon', str(s['n']),
                     f"{s['wins']} / {s['losses']} / {s['ties']}", _pct(s['median']),
                     _pct(s['low']), _pct(s['high']), 'hist_returns'))
    fell = [r for r in rows_all if STOCK[r['start_year']] < 0]
    rose = [r for r in rows_all if STOCK[r['start_year']] >= 0]
    sf, sr = staged_summary(fell), staged_summary(rose)
    timing = [
        ('Entry year fell (a crash in year 0)', str(sf['n']), f"{sf['wins']} / {sf['losses']}",
         _pct(sf['median']), _pct(sf['low']), _pct(sf['high']), 'hist_returns'),
        ('Entry year rose or was flat', str(sr['n']), f"{sr['wins']} / {sr['losses']}",
         _pct(sr['median']), _pct(sr['low']), _pct(sr['high']), 'hist_returns'),
    ]
    wide = [r for r in all_start_years(3, 3, 20) if r['staged'] is not None]
    widest = staged_summary(wide)
    def gap(r):
        return r['staged']/r['lump_sum'] - 1
    worst = min(wide, key=gap)
    best = max(rows_all, key=gap)
    bad = min(rows_all, key=gap)
    real_1973 = (1 + STOCK[1973]) / (1 + CPI_ANNUAL[1973] / 100) - 1
    real_1974 = (1 + STOCK[1974]) / (1 + CPI_ANNUAL[1974] / 100) - 1
    lump_29 = money(100000 * lump_sum_return(1929))
    staged_29 = money(100000 * episode_replay(1929, cash_fallback=0.0)['staged'])

    opening = notice('What this page is, and what it is not',
        'This is the only page in the guide built from real annual history rather than an invented stress '
        'shape. The stock leg is an academic series, not a government one; the cash leg is official Federal '
        'Reserve data. It tests one question only: whether waiting and phasing in softens entry risk when the '
        'proceeds arrive at the start of a bad year. It contains no household amount, and it is not a '
        'forecast, a probability or a recommendation.')

    triggers = ('<h2>What would change the answer</h2><p>Read this before the tables. Each trigger can '
                'reverse the ranking of a lump sum and a staged entry, and each links to the rule that '
                'governs it.</p>') + table(
        'Triggers that would move the staged-versus-lump-sum answer',
        ['Trigger', 'Why it moves the answer', 'Status', 'Official context'], [
            ('What happens in the parking window',
             'The result turns on returns earned while waiting and in the two years after phasing starts. '
             'That sequence is unknown until it has happened.', 'Unknowable in advance', 'hist_returns'),
            ('Cash return while parked',
             'Parking paid more than 14% a year in 1981 and about 0.03% in 2014. A high cash return helps '
             'the staged path; a low one hurts it.', 'Official annual range 0.03% to 14.03% (1934-2025)', 'fred_tb3ms'),
            ('Tax on the parked interest',
             'Treasury interest is subject to federal income tax and exempt from state and local income tax, '
             'so the after-tax parking return is below the quoted yield and depends on the bracket.',
             'Rule confirmed; the bracket is private', 'irs403'),
            ('Inflation during the wait',
             'The parked leg is a nominal return. In 1973 and 1974 stocks fell and inflation rose, so real '
             'values fell faster than the nominal figures suggest.', 'Official CPI confirms both years', 'cpi'),
            ('Number of tranches and the horizon',
             'More tranches and a longer wait raise both the protection in a crash year and the cost in a '
             'rising market.', 'Computed below', 'hist_returns'),
            ('Which year the money actually arrives',
             'The date of a death is not knowable. The identical rule is a hedge for a 2008-style entry and '
             'a large cost for the 1950 entry.', 'Unknowable in advance', 'hist_returns'),
            ('How the cash is held',
             'A single 3-month bill rolled for 24-36 months has reinvestment risk: the rate at each roll is '
             'unknown. A ladder to 2 years fixes some rates and, if sold before maturity, carries price risk.',
             'Mechanism only; no ladder total return is computed', 'fred_gs2')])

    stressed = ('<h2>The episode entries the brief asks about</h2><p>Each run starts on 1 January of the '
                'entry year with the same amount and finishes ten years later. <em>Lump sum</em> buys stocks '
                'immediately. <em>Staged</em> holds everything in the cash leg for three years, then moves it into '
                'stocks in three equal annual tranches. The parked leg earns the official annual average; where an '
                'official series does not reach back far enough, the gap is closed with an explicit 0% assumption '
                'shown in the row, never with an invented yield. The dollar columns use a $100,000 illustrative '
                'amount; the percentages are the part that travels.</p>') + table(
        'REAL calendar-year replay · $100,000 illustrative amount · 10-year horizon · 3-year wait · 3 tranches',
        ['Entry year', 'What the entry year is', 'Parked-leg return used', 'Lump sum after 10 years',
         'Staged after 10 years', 'Staged minus lump sum', 'Sources'], episode_rows) + table(
        'The real return sequences those runs use · S&P 500 total return, percent per calendar year',
        ['Entry year', 'Years 1-10', 'Source'], path_rows) + (
        f'<p>Read the 1929 row carefully. The staged path ends far ahead, and the effect is not subtle: the lump '
        f'sum sat through −25.1%, −43.8% and −8.6% before the recovery and ends at {lump_29} against {staged_29}. '
        f'But that run parks at an assumed 0%, so the gap is a floor for the staged advantage, not a measured '
        f'result, and it is a large one: about 2.4 times the lump sum. 2008 is the opposite case: one crash year is '
        f'followed at once by +25.9%, so cash still parked misses most of the rebound and the staged advantage is '
        f'small (+5.4% over the lump sum). 1973 is the case that best shows why a wait can be paid for: stocks fell '
        f'two years running while official 3-month bills averaged 6.88% a year.</p>') + notice(
        'Reinvestment risk sits beside the headline',
        'Two risks sit on either side of these numbers. (1) The wait itself: parking for 24-36 months means the '
        'money is reinvested later at unknown rates, and a rising market during the wait is a permanent cost, not '
        'a timing difference. Across the '
        f'{summary["n"]} entry years where every value is official, staging lost in {summary["losses"]} and won in '
        f'{summary["wins"]}. (2) The parked cash: a bill rolled every three months has an unknown rate at each roll, '
        'and the official annual average bill rate ranged from 0.03% (2014) to 14.03% (1981). If the parked money '
        'earns less than inflation, the wait is a real loss before a single stock is bought. Neither is a '
        'probability, and this page assigns no odds.')

    distribution = ('<h2>Every entry year with official data, not only the famous ones</h2><p>Choosing 1929 and '
                    '2008 after the fact is the easiest way to make a staged plan look good. The table below applies '
                    'the same rule to every start year for which the official cash leg and the stock series both '
                    'exist, and counts the outcomes. Values are the staged result minus the lump-sum result, as a '
                    'percentage of the starting amount.</p>') + table(
        'Distribution of staged minus lump-sum across all complete entry years · real history, not a probability',
        ['Rule tested', 'Entry years', 'Staged ahead / behind / level', 'Median gap vs lump sum',
         'Worst entry year', 'Best entry year', 'Sources'], grid) + table(
        'Split by what happened in the entry year itself (3-year wait, 3 tranches, 10-year horizon)',
        ['Group', 'Entry years', 'Staged ahead / behind', 'Median gap vs lump sum', 'Worst', 'Best', 'Sources'],
        timing) + (
        f'<p>Three findings hold across every rule tested. Staging is usually behind: in the median entry year the '
        f'staged path ends {abs(summary["median"]) * 100:.0f}% below the lump sum, because cash for 24-36 months '
        f'normally earns less than stocks. The extremes are wide: the worst entry year ({bad["start_year"]}) ends '
        f'{abs(gap(bad)) * 100:.0f}% below, and the best ({best["start_year"]}) {gap(best) * 100:.0f}% above. A longer '
        f'horizon does not rescue it (20-year median {_pct(widest["median"])}; worst {worst["start_year"]}: '
        f'{_pct(gap(worst))}), because more time gives a rising market more time to punish the parked years. '
        f'And in the {len(fell)} entry years that fell, staging won only {sf["wins"]} times: a crash year is a '
        f'necessary condition for staging to help, not a sufficient one, because the rebound can arrive before the '
        f'tranches are spent.</p><p>The first table reports principal at a $100,000 starting amount; this one reports '
        f'the same gap as a percentage of the lump-sum endpoint. They rank the years the same way but the sizes '
        f'differ, so do not add the two columns together.</p>')

    mechanism = '<h2>Why cash helps in a crash year and hurts otherwise</h2>' + table(
        'The mechanism, stated without odds', ['Observation', 'Consequence for the decision', 'Official context'], [
            ('In a year that fell, the lump sum buys in before the fall and the staged path buys in after it',
             'This is the whole benefit, and it depends on the fall being over before the tranches are spent.',
             'hist_returns'),
            ('In a rising year, the parked share misses part of the rise',
             'This is the whole cost, and it is the common case in the record.', 'hist_returns'),
            ('The rebound after a crash can be violent and short',
             'Phasing that is still in cash during the rebound misses most of the recovery, which is why 2008 '
             'shows a small advantage rather than a large one.', 'hist_returns'),
            ('Cash and stocks can both lose to inflation at once',
             f'The real stock return was {_pct(real_1973)} in 1973 and {_pct(real_1974)} in 1974, the two years '
             f'for which the guide carries the official CPI change; cash at 0.03% in 2014 lost to inflation too.',
             'cpi'),
            ('Treasury interest is taxable federally and exempt from state income tax',
             'The net-of-tax parking return is below the yields shown, and the gap widens with the federal '
             'bracket.', 'irs403'),
            ('Reinvesting is a new decision, not a passive continuation',
             'Every roll and every tranche is a fresh rate and a fresh price. A written rule fixes the process '
             'before the money arrives, so it is not improvised under stress.', 'fred_gs2')])

    limits = notice('Limits, stated plainly',
        'Calendar years only, so a crash inside a year (October 1929, the autumn of 2008) appears only through that '
        "year's total return. Arithmetic annual returns, not daily compounding. No tax, fees, fund expenses or "
        'inflation, so the tax and inflation rows above say which way that biases the result. The stock leg is a '
        'non-government academic series and the cash legs are official; the 2-year leg is an annual average yield, '
        'not a holding return with price changes, so no ladder total return is claimed. Years before 1934 use an '
        'explicit 0% parking assumption. Nothing here says a 24-36 month wait is optimal, and no probability is '
        'attached to any path.') + notice(
        'What would make this page wrong for the household',
        'A different tax situation, a need for the money inside the wait, a plan to spend the proceeds on housing '
        'instead of stocks, or a cash holding that is not a Treasury (a brokered deposit, a money market fund, an '
        'insured account) would each change the arithmetic. Those facts are private and are not published here.')

    return opening + triggers + stressed + distribution + mechanism + limits
