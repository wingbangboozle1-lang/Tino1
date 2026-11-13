"""Cash inheritance and estate tax projections."""
from _gen import (M, P, T, Y0, Y1, src, page, table, banner, m, mm, pc, kpi)


def build():
    est = M['estate']
    s = M['baseline']['summary']
    years = sorted({r['T'] for r in est})
    by = {}
    for r in est:
        by.setdefault(r['T'], []).append(r)

    # one row per (year, cash) showing the headroom and the tax
    rows = []
    for r in est:
        rows.append([str(r['T']), m(r['cash_today']), m(r['cash_then']), m(r['house']), m(r['exclusion']),
                     m(r['headroom']), m(r['tax']), src('IRS-ESTATE', 'RP-2026-35')])

    milestone = []
    for y in years:
        rows_y = by[y]
        base = rows_y[0]
        # find the largest cash level with zero tax, and the first with tax
        zero = [r for r in rows_y if r['tax'] <= 0.5]
        taxed = [r for r in rows_y if r['tax'] > 0.5]
        milestone.append([str(y), m(base['exclusion']), m(base['house']), m(base['headroom']),
                          m(zero[-1]['cash_today']) if zero else 'none',
                          m(taxed[0]['cash_today']) if taxed else 'none',
                          src('IRS-ESTATE', 'RP-2026-35')])

    body = ''.join([
        banner('<b>The inheritance is two things.</b> Property A, and a cash amount. The cash matters for the estate '
               'tax calculation even though it is not real estate, because the federal tax is computed on the gross '
               'estate as a whole. The tables below show the room before tax at three transfer dates and five estate '
               'sizes.'),
        '<h2>No inheritance tax at state or local level</h2>',
        '<p>California imposes no estate tax and no inheritance tax for deaths on or after 1 January 2005, and no '
        'California generation-skipping tax on transfers after 31 December 2004. The only transfer tax at death is '
        'federal, and it is paid by the estate, not by the heir. The table on the <a href="law.html">tax and law '
        'page</a> links the State Controller\'s own statement.</p>',
        '<div class="kpis">%s</div>' % ''.join([
            kpi('Federal exclusion, 2026 death', '$15,000,000', 'official amount; per person, not per heir'),
            kpi('Federal exclusion, 2027 death', '$15,480,000', 'official amount, published November 2026'),
            kpi('Rate above the exclusion', '40%', 'official top rate on the taxable estate'),
            kpi('Projected exclusion at %d' % T, m(s['exclusion_T']), 'model projection - the indexing after 2027 is '
                'statutory but the inflation path is an assumption'),
        ]),
        '<h2>Room before federal estate tax, by transfer date</h2>',
        '<p>Headroom is the exclusion minus the projected value of Property A. The cash column is measured in '
        'today\'s dollars and then inflated to the transfer date, so compare like with like: the "cash today" column '
        'is what a deposit of that size today would be worth at the transfer date.</p>',
        table(['Transfer year', 'Projected exclusion', 'Property A value', 'Headroom after Property A',
               'Largest cash level with no tax (today\'s dollars)', 'First cash level that is taxed (today\'s dollars)',
               'Official source'],
              milestone, caption='Where the taxable zone begins, at each transfer date'),
        '<h2>The full calculation</h2>',
        table(['Transfer year', 'Cash, in today\'s dollars', 'Cash at the transfer date', 'Property A value',
               'Projected exclusion', 'Headroom', 'Federal estate tax', 'Official source'],
              rows, caption='Estate calculation at three transfer dates and six cash levels',
              note='All amounts are model outputs rounded to $10 except the exclusion before 2027, which is the '
                   'official published figure. The tax is 40% of the excess of the gross estate over the exclusion. '
                   'Deductions, charitable gifts and the marital deduction are not modelled and would reduce it.'),
        '<h2>What the projection shows</h2>',
        '<div class="split"><div>',
        '<h3>The room is large but not unlimited</h3>',
        ('<p>At a ' + str(T) + ' transfer the projected exclusion is %s and the house accounts for %s of it, leaving %s of '
        'headroom. Cash above that headroom is taxed at 40%%. The projection is not a prediction of the law: it '
        'assumes the exclusion keeps being indexed. The 2026 and 2027 amounts are official; everything after them is '
        'a projection.</p>') % (m(s['exclusion_T']), m(s['fmv_T']), m(s['exclusion_T'] - s['fmv_T'])),
        '<h3>The house consumes headroom whichever path is chosen</h3>',
        '<p>The house is in the estate whether it is later sold, rented or lived in. Selling it after the transfer '
        'does not remove it from the gross estate: the estate is measured at the date of death. That is why the '
        'estate calculation does not depend on the decision this site is about - but it does decide whether the '
        'estate has to sell something to pay the tax.</p>',
        '</div><div>',
        '<h3>Liquidity is the real risk</h3>',
        '<p>An estate tax bill is due in cash, generally nine months after death, and the estate may hold mostly '
        'real estate. The options are to sell the house, borrow against it, or use life insurance held outside the '
        'estate. This is a question for the trustee and the estate attorney, and it is question Q02 in the register.</p>',
        '<h3>Portability is the other lever</h3>',
        '<p>If the transferor had a spouse who died earlier, the unused exclusion of that spouse can be ported only '
        'if a timely estate-tax return was filed for the first death. If it was not, the estate may have half the '
        'room it thought it had. The executor controls this election and it cannot be made after the fact.</p>',
        banner('<b>Gifts before death are part of the estate.</b> Taxable gifts made during life are added back when '
               'the estate tax is computed. A plan that gives assets away shortly before death does not reduce the '
               'estate; it only moves assets.', 'warn'),
        '</div></div>',
        '<h2>If estate tax is due: the options</h2>',
        table(['Option', 'How it works', 'Cost or constraint', 'Official source'],
              [['Pay from cash in the estate', 'The executor pays the tax before distributing',
                'Requires enough liquid assets; the cash inheritance may be the source', src('IRS-ESTATE')],
               ['Sell the house', 'The executor or trustee sells and uses the proceeds',
                'The basis resets at death, so the gain tax is small; the sale is at a forced time', src('IRS-INHERIT-FAQ')],
               ['Borrow against the house', 'A mortgage or a loan to the estate',
                'Interest cost and a lender\'s appraisal; keeps the house if that is the plan', src('IRS-ESTATE')],
               ['Pay in instalments', 'The internal revenue code allows an instalment election in limited cases',
                'Only for closely held business interests, not for a personal residence', src('IRS-I706')],
               ['Life insurance outside the estate', 'An irrevocable life insurance trust pays the tax',
                'Premium cost and the policy must be outside the estate to work', src('IRS-ESTATE')]],
              caption='How an estate pays a federal estate-tax bill'),
    ])
    return page('estate.html', 'Cash, estate and inheritance tax',
                'Cash and estate / 08',
                'The threshold at each level of government, the room before federal tax, and a projection to 2050 - '
                'including the part of the inheritance that is not a house.',
                body)
