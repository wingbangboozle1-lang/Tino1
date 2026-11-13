"""Overview / executive brief page."""
from _gen import (B, M, P, ROWS, T, Y0, Y1, E, S, src, page, table, kpi, card, banner, m, mm, pc, r10)


def build():
    s = B
    path = M['paths']
    break_even = M['breakeven']
    horizons = M['replay_horizons']
    best = s['best']
    gap_20 = s['w_sell'] - s['w_rent']

    kpis = ''.join([
        kpi('Property A at inheritance (%d)' % T, m(s['fmv_T']),
            'from %s today at %s a year - an assumption, flag A01' % (m(P['cup_value']), pc(P['g_cup']))),
        kpi('Property A tax: now / live in / rent out',
            '%s / %s' % (m(s['tax_before_T']), m(s['tax_live_T'])),
            'per year; renting out adds %s (no homeowners\' exemption)' % m(s['tax_rent_T'] - s['tax_live_T'])),
        kpi('Cash released by selling at inheritance', m(s['sell_net']),
            'after %s selling costs and the gain tax the model computes (%s)' % (pc(P['sell_cost']), m(s['sell_tax']))),
        kpi('After-tax wealth in %d' % Y1, mm(s['w_sell']),
            'selling vs %s renting vs %s living in it (nominal)' % (mm(s['w_rent']), mm(s['w_live']))),
        kpi('The same in %s dollars' % Y0, mm(s['real_sell']),
            '%s renting, %s living in it' % (mm(s['real_rent']), mm(s['real_live']))),
        kpi('Historical replays won by selling', '%d of 50' % horizons['20']['wins']['sell'],
            'after 20 years; %d of 50 after 10 years' % horizons['10']['wins']['sell']),
    ])

    findings = [
        ['1', 'The answer is sale, then reinvest - conditional on four checks',
         'Selling leads in the baseline by %s of %d wealth (%s in %s dollars). It is not a forecast: it is the '
         'ranking of three choices under stated assumptions, and it survives 50 replays of the real 1976-2025 record.'
         % (mm(gap_20), Y1, mm(s['real_sell'] - s['real_rent']), Y0), src('IRS-INHERIT-FAQ')],
        ['2', 'The basis reset is the whole case for selling',
         'Inherited property generally takes a date-of-death basis, so a sale soon after inheritance has almost no '
         'gain. If the home is not in the transferor\'s gross estate the reset is lost and the model shows selling '
         'falling behind. This is question Q01 and it is decided by the trust document, not by the market.',
         src('IRS-INHERIT-FAQ')],
        ['3', 'Property B is the anchor and should not be sold',
         'It is already owned, its assessed value is a fraction of its market value, and it produces rent every '
         'month. Its bill of %s a year is what a market-value assessment would cost several times over, and that '
         'advantage is lost permanently on sale. It has had no basis reset, so a sale would tax decades of gain.'
         % m(ROWS[0]['sf_tax']),
         src('SF-TAX')],
        ['4', 'Living in Property A costs more than keeping it empty, and far more than selling',
         'The transfer takes the bill from %s to %s a year even with the Proposition 19 relief, and the difference '
         'against selling is %s of %d wealth in %s dollars. Living there also gives up the rent it would earn.'
         % (m(s['tax_before_T']), m(s['tax_live_T']), mm(s['real_sell'] - s['real_live']), Y1, Y0),
         src('BOE-LTA-2026-026')],
        ['5', 'Renting is the middle path and wins in two crises',
         'Renting beats selling in the Japan-style stagnation path and in the 1929-41 depression path, and it wins '
         '%d of the 50 ten-year replays. It needs a landlord operation, rent-control compliance and insurance the '
         'owner does not have today.' % horizons['10']['wins']['rent'], src('SF-RENT-LAW')],
        ['6', 'Do not sell and hold the cash',
         'If the proceeds would sit in savings or Treasury bills at about %s, keeping the house as a rental comes '
         'out ahead. The case for selling is the case for a diversified stock fund, not for cash.'
         % pc(P['r_bill']), src('IRS-TC409')],
        ['7', 'The estate-tax question is about the whole estate, not this house',
         'The federal exclusion is $15,000,000 for 2026 and $15,480,000 for 2027 (official amounts). California has '
         'no estate or inheritance tax for deaths on or after 1 January 2005. Whether tax is due depends on the '
         'entire gross estate, including the cash inheritance.', src('IRS-ESTATE', 'RP-2026-35', 'SCO-ESTATE')],
        ['8', 'Two operating costs are unverified and one assumption is optimistic',
         'No property-specific insurance quote has been obtained. The solar credit is carried for 50 years, but the '
         'net-metering tariff behind it runs 20 years from interconnection, so electricity is likely to become a '
         'cost. Both are on the Flagged page and both are in the questions register.', src('CDI-RES', 'CPUC-NEM')],
        ['9', 'The historical bill figures supplied are not published here, and must not be',
         'A year-by-year property-tax and assessed-value history identifies a parcel even when every figure is '
         'rounded: the pattern is the identifier. This edition therefore publishes projections and official rates '
         'only, and the repository records the exposure as an open privacy action.', src('SCC-P19')],
    ]

    question_cards = ''.join([
        card('questions.html#q01', 'Q01 - Is the home in the gross estate?',
             'Decides whether the basis resets. Without it, selling loses its advantage.'),
        card('questions.html#q02', 'Q02 - How large is the whole estate?',
             'Sets the room before federal estate tax and whether liquidity is needed at death.'),
        card('questions.html#q03', 'Q03 - Will the trust be the owner, and how is it titled?',
             'A trust is not a tax exemption; the interest held decides inclusion and basis.'),
        card('questions.html#q05', 'Q05 - Who occupies the home at transfer?',
             'Proposition 19 relief needs the home as the transferee\'s principal residence within one year.'),
        card('questions.html#q07', 'Q07 - What will the Proposition 19 allowance be?',
             'The official figure after 2027-02-16 is not published yet; the model must project it.'),
        card('questions.html#q11', 'Q11 - What does insurance actually cost?',
             'No binding quote exists for either property; every premium figure here is a placeholder.'),
    ])

    body = ''.join([
        banner('<b>How to read this site.</b> Property A is the home to be inherited through the trust, expected between '
               '2040 and 2050 (baseline %d). Property B is the home the inheritor already owns, with two '
               'of its three units let. The two are never treated as one asset: B is the baseline, and A is the only '
               'thing that changes. Every number is either a <b>model output rounded to $10</b> or an <b>official '
               'amount quoted exactly</b>, and every table row links the official page behind it.' % T),
        '<div class="kpis">%s</div>' % kpis,
        '<h2>Recommendation, in one paragraph</h2>',
        '<p class="lead"><b>Keep Property B, stay in its third unit, and sell Property A, then invest the proceeds in a '
        'diversified stock fund.</b> The model puts selling %s ahead of renting and %s ahead of living in it by %d, in '
        '%s dollars. Selling wins %d of 50 replays of the real 1976-2025 record after twenty years and %d of 50 after '
        'ten - so the plan is strongest on a horizon of twenty years or more. The recommendation is conditional: it '
        'fails if the home is outside the gross estate (no basis reset), if the estate is large enough for federal tax '
        'that must be paid from the house, if the home is not the transferor\'s principal residence or cannot become '
        'the inheritor\'s within a year (which decides the post-transfer assessment), or if the proceeds would not '
        'actually be invested.</p>'
        % (mm(s['real_sell'] - s['real_rent']), mm(s['real_sell'] - s['real_live']), Y1, Y0,
           horizons['20']['wins']['sell'], horizons['10']['wins']['sell']),
        banner('<b>What would change the answer.</b> Q01 (estate inclusion), Q02 (estate size and portability), '
               'Q05 (who lives in the home and when) and Q07 (the post-2027 Proposition 19 allowance) are the four '
               'facts that can reverse the ranking. They are listed first on the <a href="questions.html">questions '
               'page</a>, and four sensitivity runs on the <a href="decision.html">decision page</a> show the size '
               'of each effect.', 'warn'),
        '<h2>Executive findings</h2>',
        table(['#', 'Finding', 'Evidence and size', 'Official source'], findings,
              caption='Nine findings, each with the number behind it', cls='',
              note='Sizes are model outputs rounded to $10 unless marked official. The ranking, not the level, is the '
                   'result: the level depends on growth and return assumptions that no one can know for 50 years.'),
        '<h2>Where to go next</h2>',
        '<div class="cards">%s</div>' % ''.join([
            card('decision.html', 'The decision', 'Live, rent or sell: cash flows, after-tax wealth, break-even points, sensitivity runs and the historical replays.'),
            card('projections.html', 'Year-by-year projections', 'Every year 2026-2076: value, assessed value, tax, insurance, water, electricity, repairs and rent.'),
            card('black-swan.html', 'Black swan conditions', 'Growth and inflation are never constant for 50 years; named crisis paths and 50 real historical sequences.'),
            card('process.html', 'The inheritance process', 'Step by step from trust check to recorded deed, with the statutory clock on each step.'),
            card('law.html', 'Tax and law', 'Federal, California and local rules, with the pending measures that would change them.'),
            card('costs.html', 'Operating costs', 'What is verified, what is assumed and what cannot be verified from a ZIP-code average.'),
            card('estate.html', 'Cash and estate tax', 'The thresholds at each level, the room before tax, and projections to 2050.'),
            card('questions.html', 'Questions before deciding', 'Every open question with what is missing and how to discover it privately.'),
            card('suggestions.html', 'Suggestions for review', 'Proposals with Adopt / Hold / Reject and a recommended path. Nothing is implemented until chosen.'),
            card('flagged.html', 'Flagged for review', 'Every unconfirmed value, assumption and irregularity, with its source.'),
            card('sources.html', 'Sources and method', 'The source register, the model, and how the verification was done.'),
            card('requirements.html', 'Requirements register', 'The brief line by line, and the page that answers each line.'),
        ]),
        '<h2>The four facts that decide it</h2>',
        '<div class="cards">%s</div>' % question_cards,
        '<h2>The important distinction</h2>',
        table(['', 'Property A - to be inherited', 'Property B - already owned', 'Why the difference matters', 'Official source'],
              [['Ownership today', 'Held by the transferor in trust', 'Held by the inheritor',
                'Only A changes hands; B is not part of the transferor\'s estate unless the transferor holds an interest',
                src('IRS-ESTATE')],
               ['Assessed value vs market', 'Assessed %s against %s market' % (m(P['cup_assessed']), m(P['cup_value'])),
                'Assessed %s against %s market' % (m(P['sf_assessed']), m(P['sf_value'])),
                'B carries a very low assessment; A\'s assessment moves toward market on transfer unless the Proposition 19 claim succeeds',
                src('RTC-63.2', 'BOE-P19')],
               ['Income tax basis on transfer', 'Generally resets to date-of-death value',
                'No reset - the inheritor already owns it',
                'A can be sold with little gain; selling B would tax decades of appreciation',
                src('IRS-INHERIT-FAQ')],
               ['Property tax on change', 'Reassessed unless the intergenerational exclusion is claimed and qualifies',
                'Unchanged - no change of ownership',
                'A\'s tax can rise by more than five times; B\'s stays where it is',
                src('BOE-LTA-2026-026')],
               ['Rent today', 'None - it is not let', 'Two of three units let',
                'B produces income in every path and remains the housing baseline',
                src('SF-RENT')],
               ['Annual property tax today', m(ROWS[0]['cup_tax_pre']), m(ROWS[0]['sf_tax']),
                'The two tax bills differ by a factor of about three on very different assessments',
                src('SCC-RATES', 'SF-TAX')]],
              caption='Property A and Property B are analysed separately, because almost every rule treats them differently'),
    ])
    return page('index.html', 'A clearer path forward',
                'Executive brief / 01',
                'A future trust inheritance, an already-owned home, and three paths compared with numbers instead of '
                'assumptions. Every figure below is a model output rounded to $10 or an official amount quoted exactly.',
                body)
