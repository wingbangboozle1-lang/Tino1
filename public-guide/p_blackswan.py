"""Black swan and regime risk: named crisis paths plus 50 historical replays."""
from _gen import (B, M, P, T, Y0, Y1, neut, src, page, table, banner, m, mm, pc, kpi)


def build():
    s = B
    paths = M['paths']
    hs = M['hist_stats']
    rev = M['provenance']

    hist = table(['Measure', 'Value', 'What it says', 'Provenance', 'Official source'],
                 [['House-price growth, 1977-2025', pc(hs['sj_1976_2025'], 2),
                   'the long-run average the baseline growth rate is checked against; the 1976 level is the base year, so no 1976 return exists', neut(rev['g_cup']), src('FHFA-SJ')],
                  ['House-price growth, 2001-2025', pc(hs['sj_2000_2025'], 2),
                   'much lower: this century so far has not repeated the last one', neut(rev['g_cup']), src('FHFA-SJ')],
                  ['Inflation, 1977-2025 (consumer prices)', pc(hs['cpi_1976_2025'], 2),
                   'the average the model\'s inflation assumption is checked against', neut(rev['infl']), src('BLS-CPI')],
                  ['Inflation, 2001-2025', pc(hs['cpi_2000_2025'], 2),
                   'the recent regime; the 2022 surge is inside it', neut(rev['infl']), src('BLS-CPI')],
                  ['Worst single year for house prices', pc(hs['worst_sj'][0], 1) + ' (%d)' % hs['worst_sj'][1],
                   'the largest one-year fall in the record', neut(rev['g_cup']), src('FHFA-SJ')],
                  ['Best single year for house prices', pc(hs['best_sj'][0], 1) + ' (%d)' % hs['best_sj'][1],
                   'the largest one-year rise in the record', neut(rev['g_cup']), src('FHFA-SJ')],
                  ['Worst single year for the stock index', pc(hs['worst_sp'][0], 1) + ' (%d)' % hs['worst_sp'][1],
                   'the worst calendar year in the 1928-2025 academic series, which is wider than the replay window', neut(rev['r_stock']), src('DAMODARAN')],
                  ['Highest single year of inflation', pc(hs['max_infl'][0], 1) + ' (%d)' % hs['max_infl'][1],
                   'the inflation peak of the 1976-2025 record', neut(rev['infl']), src('BLS-CPI')]],
                 caption='The real record the assumptions are checked against, 1976-2025 and 2000-2025',
                 note='House-price and inflation rows are nominal annual rates compounded over the period. A single-year row '
                      'says so. The 1976 value is the base year of the model\'s history, so the returns run from 1977. The '
                      'stock figures come from an academic dataset and are never presented as a government statistic.')

    named = []
    for p in paths:
        sm = p['summary']
        named.append([p['label'], p['kind_label'].split(':')[0], m(sm['w_live']), m(sm['w_rent']), m(sm['w_sell']),
                      sm['best'].capitalize() if 'best' in sm else '', src('FHFA-SJ', 'BLS-CPI')])

    regime = table(['Regime', 'What happened', 'What it does to this decision', 'Official source'],
                   [['The Great Inflation, 1965-1982',
                     'Four recessions, two energy shortages, inflation above 14% in 1980, and a long climb down to about 3.5% in the late 1980s',
                     'Property tax rises at its 2% cap while the general price level rises much faster, so the real tax burden falls - this is the path where a fixed, capped assessment is most valuable',
                     src('FED-GREAT-INFL')],
                    ['Stagflation', 'Inflation and unemployment high together; real asset returns poor',
                     'The model replays the 1970s order and finds selling still leads, because the stock fund is also priced in nominal terms, but by a thinner margin', src('DAMODARAN')],
                    ['A lost decade', 'Ten to fifteen years with no real house-price gain',
                     'This is where renting closes the gap: the house keeps producing rent while a sale would have bought into a flat market', src('FHFA-SJ')],
                    ['Depression', 'Asset prices fall for years and unemployment is high',
                     'Selling loses to renting here, because the proceeds are invested into the fall', src('DAMODARAN')],
                    ['Japan-style stagnation', 'A very long period of weak growth and near-zero returns',
                     'The one path where renting wins comfortably. It is the strongest argument against selling everything at once', src('DAMODARAN')]],
                   caption='Named regimes, and what each one does to the three choices')

    body = ''.join([
        banner('<b>Why a separate section.</b> The baseline projection compounds one growth rate and one inflation '
               'rate for fifty years. The real record does not look like that: from 1976 to 2025 the same economy '
               'produced inflation of 13% and deflation, house-price years of +29% and -15%, and stock-market years of '
               '+52% and -37%. A decision that only works on the average is not a decision, it is a bet on the average.'),
        '<div class="kpis">%s</div>' % ''.join([
            kpi('Historical sequences replayed', '50', 'the real 1976-2025 record, started from each year in turn'),
            kpi('Selling wins after 20 years', '%d of 50' % M['replay_horizons']['20']['wins']['sell'],
                'and %d of 50 after 10' % M['replay_horizons']['10']['wins']['sell']),
            kpi('Worst 10-year gap, selling minus renting', mm(M['replay_horizons']['10']['sell_minus_rent_worst']),
                'the risk a short horizon actually carries'),
            kpi('Named crisis paths where renting wins', '2',
                'the Japan-style stagnation path and the Depression path'),
        ]),
        '<h2>The real record, not the average</h2>',
        hist,
        '<h2>Named regimes</h2>',
        '<p>Each regime is a constructed sequence, not a forecast: it takes the shape of a known period and applies it '
        'to this decision. The provenance of every element is in the table on the '
        '<a href="sources.html">sources and method page</a>.</p>',
        regime,
        '<h2>The stress paths, run through the model</h2>',
        table(['Named path', 'Kind', 'Live in A', 'Rent A out', 'Sell and reinvest', 'Best', 'Official source'],
              named, caption='Named crisis paths, nominal after-tax wealth in %d, for comparison with the baseline only' % Y1,
              note='Kind separates a replay of the real record from a construction. A construction is labelled one '
                   'because it is not a forecast and has no probability attached.'),
        '<h2>What the stress tests actually say</h2>',
        '<div class="split"><div>',
        '<h3>Selling survives every twenty-year window</h3>',
        '<p>Replaying the real record from each of its 50 starting years, selling leads after twenty years in all 50 '
        'and after ten years in %d. The median ten-year advantage is %s; the worst is %s. That is the risk being '
        'accepted: a bad decade is possible, a bad twenty years is not in the sample.</p>'
        % (M['replay_horizons']['10']['wins']['sell'], m(M['replay_horizons']['10']['sell_minus_rent_median']),
           m(M['replay_horizons']['10']['sell_minus_rent_worst'])),
        '<h3>Two paths invert the answer</h3>',
        '<p>If the next fifty years look like Japan after 1990, or like the Depression, renting wins. Both are '
        'long-period, low-return environments where a house that produces rent beats a portfolio that does not. The '
        'practical response is not to reject selling; it is to <b>invest the proceeds in stages</b> and keep a few '
        'years of spending in short-term Treasury bills, so that a fall in the first years does not force a sale at '
        'the bottom.</p>',
        '</div><div>',
        '<h3>The right response to a black swan</h3>',
        '<ol class="steps">',
        '<li><h3>Do not rely on one sale date</h3><p>Invest in tranches over twelve to twenty-four months rather '
        'than all at once. The model is a single-date calculation; the real plan does not have to be.</p></li>',
        '<li><h3>Keep a cash and bill reserve</h3><p>The replays show the damage in a bad decade comes from being '
        'forced to sell investments to live. A reserve removes that forcing.</p></li>',
        '<li><h3>Insure the risks that are insurable</h3><p>Earthquake is excluded from a standard California '
        'homeowners policy. If the house is kept, the uninsured loss is a real black swan; if it is sold, it is '
        'transferred with the house.</p></li>',
        '<li><h3>Re-check after a regime change</h3><p>If inflation runs above 4% for several years, or house prices '
        'fall more than 20%, the ranking should be recomputed rather than assumed.</p></li>',
        '</ol>',
        '</div></div>',
        banner('<b>What a black-swan section cannot do.</b> It cannot give a probability to a named crisis. The figures '
               'below are conditional outcomes - "if this happened, this is what the three paths would produce" - and '
               'they are labelled by provenance so that a government statistic is never confused with a construction. '
               'The 1976-2025 replays are the closest thing here to evidence, and they are 50 observations from one '
               'history.', 'warn'),
    ])
    # The Great Inflation row needs the official source link in the same shape as src().
    return page('black-swan.html', 'When the baseline breaks',
                'Black swan and regime risk / 04',
                'Growth and inflation are never constant for fifty years. This page replays the real record instead of '
                'averaging it, and names the crises that change the answer.',
                body)
