"""Year-by-year projections 2026-2076."""
from _gen import (B, M, P, ROWS, T, Y0, Y1, src, page, table, banner, m, mm, pc, kpi)


def build():
    s = B
    # The projection table is long: show 2026-2050 in five-year steps and then every
    # fifth year to 2076, so the page stays readable on a phone.
    picks = [y for y in range(Y0, T)] + [T, T + 1] + list(range(T + 5, Y1 + 1, 5)) + [Y1]
    picks = sorted(set(y for y in picks if Y0 <= y <= Y1))
    by_year = {r['year']: r for r in ROWS}

    def post_transfer(y):
        """Assessed value and tax after the transfer.

        The model records the post-transfer assessment only in the transfer year, so the
        roll is projected here with the same statutory rule the model uses for Property B:
        the prior taxable value times the annual factor (the lesser of the California
        consumer price index and 2%), capped at market value. The factor is taken from the
        row's own CPI index, so the projection stays consistent with the model's path.
        """
        av = s['taxable_rent_T']
        prev = by_year[T]['cpi']
        for yy in range(T + 1, y + 1):
            cpi_now = by_year[yy]['cpi']
            factor = {}
            factor['f'] = min(1.02, max(cpi_now / prev - 1.0, 0.0)) + 1.0
            av *= factor['f']
            av = min(av, by_year[yy]['cup_value'])
            prev = cpi_now
        return av

    rent_tax_2060 = post_transfer(2060) * P['rate_cup'] + P['dc_cup'] * by_year[2060]['cpi']
    rent_tax_2076 = post_transfer(Y1) * P['rate_cup'] + P['dc_cup'] * by_year[Y1]['cpi']
    rows = []
    for y in picks:
        r = by_year[y]
        if y < T:
            a_av, a_tax = r['cup_assessed_pre'], r['cup_tax_pre']
        elif y == T:
            a_av, a_tax = s['taxable_rent_T'], s['tax_rent_T']
        else:
            a_av = post_transfer(y)
            a_tax = a_av * P['rate_cup'] + P['dc_cup'] * r['cpi']
        rows.append([str(y), m(r['cup_value']), m(a_av), m(a_tax),
                     m(r['sf_value']), m(r['sf_assessed']), m(r['sf_tax']),
                     m(r['sf_rent']), m(r['cup_rent']),
                     '%.2f' % r['cpi'], src('RTC-51', 'SCC-RATES')])

    first = by_year[Y0]
    net_b = first['sf_net']
    costs = table(
        ['Operating line', 'Property A', 'Property B', 'Growth assumed', 'Why the assumption', 'Official source'],
        [['Property tax', m(first['cup_tax_pre']), m(first['sf_tax']),
          'assessed value capped at 2% a year',
          'R&TC 51 limits the annual inflation factor to 2%; a change of ownership resets the base', src('RTC-51')],
         ['Insurance', 'no quote', m(first['sf_ins']),
          'inflation plus 1 point',
          'the owner\'s estimate is a placeholder; no binding premium exists. Both properties are flagged',
          src('CDI-RES')],
         ['Water and wastewater', m(first['cup_water']), m(first['sf_water']),
          'inflation plus 2 points',
          'utility rates have risen faster than headline inflation; the city page states water is provided by three different systems, so the owner\'s bill is the only basis', src('CUP-WATER')],
         ['Electricity', m(first['cup_elec']), m(first['sf_elec']),
          'inflation plus 1 point',
          'the A figure is a net credit from the solar tariff; it is modelled as a negative cost', src('CPUC-NEM', 'CPUC-FIXED')],
         ['Repairs and maintenance', m(first['cup_maint']), m(first['sf_maint']),
          'inflation',
          'an allowance, not a quotation; a house of this age needs a reserve whether or not it is spent', src('CDI-RES')],
         ['Rent received', m(first['cup_rent']) + ' (from ' + str(T) + ')', m(first['sf_rent']),
          'inflation, rent-capped for B',
          'B is under the rent ordinance; A is modelled at the HUD benchmark for a 3-bedroom', src('SF-RENT', 'HUD-SAFMR')],
         ['Net operating result for B', '-', m(net_b), '-',
          'rent after vacancy and every cost above; A has no rent until it is inherited', src('HUD-SAFMR')]],
        caption='Costs and income in %d, the model\'s first year' % Y0,
        note='A dash means the line does not apply before the inheritance. Every premium and utility figure here is a '
             'placeholder from the owner\'s estimate, rounded to $10, and is listed on the Flagged page.')

    key = table(['What is projected', 'How', 'Where the rule comes from', 'Official source'],
                [['Market value of each home', 'today\'s estimate compounded at the assumed growth rate',
                  'no official page predicts a house price; the rate is an assumption and is labelled one', src('FHFA-SJ')],
                 ['Assessed value', 'inflation factor capped at 2% a year before the transfer; reassessed after it',
                  'R&TC 51 for the cap; R&TC 63.2 and Proposition 19 for the transfer', src('RTC-51', 'RTC-63.2')],
                 ['Property tax', 'assessed value times the local tax rate, plus fixed charges',
                  'the county puts the rate in a published rate book; the city publishes its rate every year',
                  src('SCC-RATES', 'SF-TAX')],
                 ['Base cost growth', 'inflation, with a premium per line', 'an assumption; the CPI link is the anchor',
                  src('BLS-CPI')],
                 ['Estate-tax exclusion', 'the published 2027 amount, then indexed',
                  'the 2027 amount is official; the indexing after it is statutory and is modelled', src('RP-2026-35')],
                 ['Proposition 19 allowance', 'the published amount, re-indexed in February of odd years',
                  'the statute sets the cadence; the amount after 2027 is not yet published', src('BOE-LTA-2025-009')]],
                caption='How each projected line is built')

    body = ''.join([
        banner('<b>These are scenarios, not forecasts.</b> A 50-year projection cannot be a prediction: growth, '
               'inflation and tax law will not hold constant. What the table is for is to show the <b>shape</b> of the '
               'cost and the size of the numbers, so that a decision taken today is not based on today\'s bill.'),
        '<div class="kpis">%s</div>' % ''.join([
            kpi('Property A, %d' % T, m(s['fmv_T']), 'model value at the baseline inheritance year'),
            kpi('Property A assessed, if rented after inheritance', m(s['taxable_rent_T']),
                '%s relief claims apply only to a home lived in' % 'Proposition 19'),
            kpi('Property A assessed, if lived in', m(s['taxable_live_T']),
                'the prior assessed value plus the excess over the allowance'),
            kpi('Property B assessed, %d' % Y1, m(ROWS[-1]['sf_assessed']),
                'still far below its market value of %s' % m(ROWS[-1]['sf_value'])),
        ]),
        '<h2>The projection table</h2>',
        '<p>Selected years from 2026 to 2076. Every row is a model output rounded to $10. Property A is valued '
        'throughout, but its assessed value and tax stay at the transferor\'s level until the transfer; after the '
        'transfer the row shows the <b>rent-out</b> case, which is the more expensive of the two post-transfer '
        'assessments, with the roll projected forward under the 2% cap. The lived-in case is on the '
        '<a href="decision.html">decision page</a>.</p>',
        table(['Year', 'A market value', 'A assessed value', 'A property tax', 'B market value', 'B assessed value',
               'B property tax', 'B rent', 'A rent', 'CPI index', 'Official source'],
              rows, caption='Projection 2026-2076, selected years, baseline assumptions',
              note='CPI index is 1.00 in 2026. A rent starts at the inheritance year. All amounts are $10-rounded '
                   'model outputs, and all are nominal dollars unless a row says otherwise.'),
        '<h2>What the table shows</h2>',
        '<div class="split"><div>',
        '<h3>The tax bill, not the house price, is the moving part</h3>',
        '<p>Property B\'s assessed value grows at the 2% cap while its market value grows faster, so the gap between '
        'the two widens every year. By ' + str(Y1) + ' the assessed value is %s against a market value of %s. That gap is the '
        'reason Property B is the anchor of the plan: it is a permanent, compounding tax advantage that exists only '
        'for as long as the property is not sold.</p>'
        % (m(ROWS[-1]['sf_assessed']), m(ROWS[-1]['sf_value'])),
        '<h3>Property A\'s bill jumps at the transfer</h3>',
        '<p>Before the transfer A is taxed on %s. In the transfer year the rent-out assessment is %s and the tax is '
        '%s. Because the roll keeps growing at the 2%% cap, the tax reaches about %s a year by %d and about %s by %d. '
        'Living in it holds the assessment to %s and the first-year tax to %s, because the Proposition 19 relief '
        'applies - but only if the claims are filed in time and the home really is the inheritor\'s principal '
        'residence.</p>'
        % (m(s['fbyv_T']), m(s['taxable_rent_T']), m(s['tax_rent_T']), m(rent_tax_2060), 2060,
           m(rent_tax_2076), Y1, m(s['taxable_live_T']), m(s['tax_live_T'])),
        '</div><div>',
        '<h3>How each line is projected</h3>',
        key,
        '</div></div>',
        '<h2>Operating costs in the first year</h2>',
        costs,
        banner('<b>The single biggest weakness in this table is insurance.</b> No property-specific quote has been '
               'obtained for either home. The figures shown are the owner\'s estimates rounded to $10. A California '
               'homeowners policy excludes earthquake, flood, mold and losses after a long vacancy unless separate '
               'cover is bought, and a landlord policy is a different product from a homeowners policy. Treat every '
               'premium figure here as a placeholder and replace it with a quote before deciding.', 'warn'),
        '<h2>Where the numbers are weakest</h2>',
        table(['Weakness', 'Effect on the projection', 'What would fix it', 'Official source'],
              [['Insurance is an estimate, not a quote', 'A doubling of the premium changes 2076 wealth by a few hundred thousand dollars, not the ranking',
                'two binding quotes per property; the state publishes a premium comparison tool', src('CDI-RES')],
               ['The solar credit is modelled for 50 years',
                'If electricity becomes a cost after the tariff period, the rent-out net falls every year after it',
                'read the interconnection agreement and the tariff period', src('CPUC-NEM')],
               ['Water is the owner\'s bill, not a published rate',
                'Water is a small line; the providers differ street by street, so a rate cannot be inferred',
                'the actual bill, or the serving company\'s published tariff', src('CUP-WATER')],
               ['Growth and returns are one invented path',
                'This is the dominant uncertainty, and it is why the site replays history instead',
                'see the black-swan page; no input can remove this uncertainty', src('FHFA-SJ')],
               ['Property A rent is a HUD benchmark',
                'HUD publishes a 40th-percentile fair-market rent, not a rent for this house',
                'two appraisals or a rent estimate from a local agent', src('HUD-SAFMR')]],
              caption='The projection is only as good as its weakest input'),
    ])
    return page('projections.html', 'Year-by-year outlook',
                'Model and method / 03',
                'Every year from 2026 to 2076: market value, assessed value, property tax, insurance, water, '
                'electricity, repairs and rent - and the rule behind each one.',
                body)
