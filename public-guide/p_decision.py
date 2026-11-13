"""Decision analysis: live / rent / sell, with sensitivities and break-evens."""
from _gen import (B, M, P, ROWS, T, Y0, Y1, E, S, neut, src, page, table, kpi, banner, m, mm, pc)

def _scenario_rows():
    rows = []
    for s in M['sensitivity']:
        rows.append([E(neut(s['label'])), m(s['w_live']), m(s['w_rent']), m(s['w_sell']),
                     s['best'].capitalize(), src('IRS-TC409')])
    return rows


def build():
    s = B
    be = M['breakeven']
    horizons = M['replay_horizons']
    w10 = s['w10']
    w20 = s['w20']

    three = [
        ['Market value of A at inheritance (%d)' % T, m(s['fmv_T']), m(s['fmv_T']), m(s['fmv_T']),
         'the same home; the paths differ in what you do with it', src('FHFA-SJ')],
        ['Taxable (assessed) value after the transfer', m(s['taxable_live_T']), m(s['taxable_rent_T']), 'sold',
         'Proposition 19 relief only applies to a home used as the transferee\'s principal residence', src('RTC-63.2')],
        ['Property tax, first year after inheritance', m(s['tax_live_T']), m(s['tax_rent_T']), 'none after sale',
         'living in it also keeps the homeowners\' exemption', src('BOE-HOX', 'SCC-RATES')],
        ['Net cash released at inheritance', '$0', '$0', m(s['sell_net']),
         'sale price less %s selling costs less the gain tax the model computes' % pc(P['sell_cost']),
         src('IRS-INHERIT-FAQ')],
        ['Annual rent received', '$0', m(ROWS[T - Y0]['cup_rent']), '$0',
         'HUD small-area FMR benchmark for a 3-bedroom, before vacancy and management', src('HUD-SAFMR')],
        ['After-tax wealth in %d' % Y1, m(s['w_live']), m(s['w_rent']), m(s['w_sell']),
         'nominal dollars; the model carries property, rent, tax and investment flows to the end', src('IRS-TC409')],
        ['The same in %s dollars' % Y0, m(s['real_live']), m(s['real_rent']), m(s['real_sell']),
         'deflated by the model\'s inflation path - the honest comparison across 50 years', src('BLS-CPI')],
        ['Ranking', 'third', 'second', 'first', 'on the baseline assumptions only', src('IRS-TC409')],
    ]

    breakevens = [
        ['Growth of Property A at which renting matches selling', pc(be['g_cup_rent_vs_sell'], 2),
         'above this annual appreciation, renting wins', src('FHFA-SJ')],
        ['Growth of Property A at which living in it matches selling', pc(be['g_cup_live_vs_sell'], 2),
         'a much higher bar, because living there gives up both rent and the portfolio', src('FHFA-SJ')],
        ['Stock-market return at which renting matches selling', pc(be['r_stock_rent_vs_sell'], 2),
         'below this annual return, keeping the house and renting wins', src('DAMODARAN')],
        ['Monthly rent at which renting matches selling', m(be['rent_month_rent_vs_sell']),
         'against the HUD benchmark of %s for a 3-bedroom' % m(P['cup_rent_month_3br']), src('HUD-SAFMR')],
    ]

    horizon = [
        ['Selling wins', '%d of 50' % horizons['10']['wins']['sell'], '%d of 50' % horizons['20']['wins']['sell'],
         'replaying the real 1976-2025 record from each of its 50 starting years', src('FHFA-SJ', 'BLS-CPI')],
        ['Renting wins', '%d of 50' % horizons['10']['wins']['rent'], '%d of 50' % horizons['20']['wins']['rent'],
         'the early years are where renting can win', src('FHFA-SJ')],
        ['Living in it wins', '%d of 50' % horizons['10']['wins']['live'], '%d of 50' % horizons['20']['wins']['live'],
         'never first on wealth alone; the benefit is housing, which the model does not price', src('BLS-CPI')],
        ['Worst ten-year gap, selling minus renting', m(horizons['10']['sell_minus_rent_worst']), '',
         'the one bad decade in fifty: this is the risk being accepted', src('FHFA-SJ')],
        ['Median ten-year gap, selling minus renting', m(horizons['10']['sell_minus_rent_median']), '', '',
         src('FHFA-SJ')],
        ['Worst twenty-year gap, selling minus renting', '', m(horizons['20']['sell_minus_rent_worst']),
         'positive in every replay', src('FHFA-SJ')],
        ['Median twenty-year gap, selling minus renting', '', m(horizons['20']['sell_minus_rent_median']), '',
         src('FHFA-SJ')],
    ]

    at10 = ['After-tax wealth at %d (10 years after inheritance)' % w10['year'], m(w10['live']), m(w10['rent']), m(w10['sell']),
            'selling leads by %s here, but by only %s of %s dollars across the 50 replays'
            % (mm(w10['sell'] - w10['rent']), mm(M['replay_horizons']['10']['sell_minus_rent_worst']), Y0),
            src('IRS-TC409')]
    at20 = ['After-tax wealth at %d (20 years after inheritance)' % w20['year'], m(w20['live']), m(w20['rent']), m(w20['sell']),
            '', src('IRS-TC409')]

    body = ''.join([
        banner('<b>What this page does and does not say.</b> It prices three choices on one set of stated assumptions. '
               'It does not know future growth, inflation, tax law, rents or insurance prices. The result is a '
               '<b>ranking with a margin</b>, and the margin is what the sensitivity table tests.'),
        '<h2>The three choices on one page</h2>',
        table(['Measure', 'Live in A', 'Rent A out', 'Sell A and reinvest', 'What drives it', 'Official source'],
              three, caption='The comparison, inheritance in %d, baseline assumptions' % T,
              note='Household and model amounts are rounded to $10. A negative wealth gap is not a loss in cash terms; '
                   'it is the difference between two paths.'),
        at10 and table(['Measure', 'Live in A', 'Rent A out', 'Sell A and reinvest', 'Note', 'Official source'],
                       [at10, at20], caption='The same comparison at two earlier dates'),
        '<h2>Why selling leads: the arithmetic</h2>',
        '<div class="split"><div>',
        '<h3>The basis reset does the work</h3>',
        '<p>Inherited property generally takes a basis equal to its value on the date of death, so a sale soon after '
        'inheritance produces almost no taxable gain. The model shows a sale at %s against a basis of the same value, '
        'which is why the gain tax is %s and the deduction from the sale is mostly the %s selling cost.</p>'
        % (m(s['sell_proceeds']), m(s['sell_tax']), pc(P['sell_cost'])),
        '<h3>The alternative is a concentrated single asset</h3>',
        '<p>Renting keeps one house as the whole of the marginal position: one structure, one housing market, one insurance '
        'market, and rent that is capped in law. A diversified fund spreads the same money across hundreds of '
        'businesses. The model rewards that diversification at %s a year, which is an <b>academic historical average, '
        'not a government statistic and not a promise</b>.</p>' % pc(P['r_stock']),
        '</div><div>',
        '<h3>The costs the sale avoids</h3>',
        '<p>These are running costs in the transfer year, not the difference against living in the home: the owner '
        'pays the same property tax and insurance whichever of the three paths is chosen. What selling avoids is the '
        '<b>operating</b> cost of holding a home that produces nothing.</p>',
        table(['Cost avoided by selling', 'First year after inheritance', 'Official source'],
              [['Property tax on the reassessed value', m(s['tax_rent_T']), src('SCC-RATES')],
               ['Landlord insurance, not homeowners', m(ROWS[T - Y0]['ins_rental']), src('CDI-RES')],
               ['Water and wastewater', m(ROWS[T - Y0]['cup_water']), src('CUP-WATER')],
               ['Repairs and maintenance allowance, an assumption', m(ROWS[T - Y0]['cup_maint']), src('CDI-RES')],
               ['Electricity, near zero today because of the solar credit', m(ROWS[T - Y0]['cup_elec']), src('CPUC-NEM')]],
              caption='Operating costs of holding Property A, first year after inheritance, model values'),
        '</div></div>',
        '<h2>What would have to be true for another answer</h2>',
        '<p>Break-even points are the cleanest way to see the size of the disagreement. Each one holds everything '
        'else at the baseline and asks what a single input would have to be for the ranking to flip.</p>',
        table(['Break-even', 'Value', 'Meaning', 'Official source'], breakevens,
              caption='Break-even points on the baseline, each solved numerically by the model'),
        banner('<b>Read the rent break-even carefully.</b> Renting would need a monthly rent of %s to match selling on '
               'the baseline. The HUD benchmark for a 3-bedroom in the same ZIP code is %s, and HUD itself describes '
               'that figure as a 40th-percentile fair-market benchmark, not a valuation of any particular house. The '
               'gap between the two is the size of the case for selling.' % (m(be['rent_month_rent_vs_sell']), m(P['cup_rent_month_3br'])), 'warn'),
        '<h2>Risk: the same comparison replayed 50 times</h2>',
        '<p>The single baseline is one invented future. A better test is to replay the <b>real</b> 1976-2025 record - '
        'actual inflation, actual house-price growth, actual stock and bill returns - starting from each of its 50 '
        'years in turn. That keeps the order of crises rather than averaging them away.</p>',
        table(['Result across 50 real historical sequences', 'After 10 years', 'After 20 years', 'How to read it', 'Official source'],
              horizon, caption='Selling, renting and living in the home, replayed on the real record'),
        banner('<b>The honest caveat.</b> A replay of 1976-2025 is not a probability. It is 50 observations drawn from '
               'one history, and the future may contain a sequence that history does not. What it does show is that the '
               'result does not depend on one lucky decade: selling wins every twenty-year window in the sample, and '
               'loses some ten-year ones. Any plan that needs the money within ten years is taking real risk.', 'warn'),
        '<h2>Sensitivity: one assumption changed at a time</h2>',
        '<p>Each row re-runs the whole model with one input changed and everything else held. The "best" column is '
        'the path with the highest after-tax wealth at %d.</p>' % Y1,
        table(['Scenario', 'Live in A', 'Rent A out', 'Sell and reinvest', 'Best', 'Official source'],
              _scenario_rows(), caption='Sensitivity runs, after-tax wealth in %d' % Y1, cls='num'),
        '<h2>The recommendation, stated as a plan</h2>',
        '<ol class="steps">',
        '<li><h3>Before anything else: read the trust</h3><p>Confirm whether the home will be in the transferor\'s gross '
        'estate and whether the trust or the inheritor will be the owner. If the home is outside the gross estate the '
        'basis does not reset and the ranking can flip. This is Q01 and Q03.</p></li>',
        '<li><h3>Do not sell Property B</h3><p>It is the housing baseline and the income baseline. Its assessed value '
        'is low precisely because it has not changed hands, and that advantage is permanent if it is kept. Keep living '
        'in the third unit; the model assumes the same occupancy in every path.</p></li>',
        '<li><h3>At the transfer: file the claims inside the statutory windows</h3><p>The homeowners\' exemption and '
        'the Proposition 19 exclusion have different deadlines and both are needed for the relief to hold. The '
        '<a href="process.html">process page</a> lists them in order.</p></li>',
        '<li><h3>Sell within the year, and sell once</h3><p>The basis reset is at its most valuable immediately: every '
        'month of ownership after the transfer adds exposure to the market without adding to the basis. %s is '
        'released on the baseline. Selling costs are already deducted.</p></li>' % m(s['sell_net']),
        '<li><h3>Invest the proceeds, in stages</h3><p>The comparison is against a diversified stock fund at the '
        'historical average, not against cash. Holding a few years of spending in short-term Treasury bills while '
        'investing the rest in stages narrows the ten-year risk the replays expose.</p></li>',
        '<li><h3>Re-check the four decisive facts every year</h3><p>Estate size, portability, the Proposition 19 '
        'allowance and the trust\'s terms all change the answer. They are listed on the '
        '<a href="questions.html">questions page</a> with a discovery route for each.</p></li>',
        '</ol>',
    ])
    return page('decision.html', 'Live, rent or sell',
                'Decision framework / 02',
                'The three paths priced with the same costs, the same tax rules and the same assumptions - then tested '
                'against 50 real historical sequences and one-at-a-time sensitivities.',
                body)
