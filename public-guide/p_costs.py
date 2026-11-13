"""Operating costs: insurance, water, electricity, repairs, rent."""
from _gen import (M, P, ROWS, T, Y0, Y1, src, page, table, banner, m, pc, kpi)


def build():
    r0 = ROWS[0]
    rT = ROWS[T - Y0]
    verified = table(
        ['Cost line', 'Property A', 'Property B', 'Status', 'What is actually known', 'Official source'],
        [['Homeowners insurance', m(r0['cup_tax_pre']) if False else 'not quoted', m(r0['sf_ins']),
          '<span class="pill open">placeholder</span>',
          'No property-specific quote for either home. The figures shown are the owner\'s estimates rounded to $10. '
          'A California homeowners policy excludes earthquake, flood, mold and losses after a long vacancy unless '
          'separate cover is bought.', src('CDI-RES')],
         ['Landlord insurance for the let units', 'not applicable today', 'included in the figure above',
          '<span class="pill open">placeholder</span>',
          'A landlord policy is a different product from a homeowners policy: it covers loss of rent and liability '
          'for tenants. The model carries one figure for the whole Property B building.', src('CDI-RES')],
         ['Water and wastewater', m(r0['cup_water']), m(r0['sf_water']),
          '<span class="pill open">owner bill</span>',
          'Both figures are the owner\'s bills, rounded to $10. The water provider differs by street, and the city '
          'publishes which of three systems serves an address.', src('CUP-WATER')],
         ['Electricity', m(r0['cup_elec']), m(r0['sf_elec']),
          '<span class="pill open">modelled credit</span>',
          'Property A shows a net credit because of the installed solar system. Property B is a small positive cost. '
          'The credit is modelled as a negative cost for the whole horizon, which is optimistic.', src('CPUC-NEM')],
         ['Repairs and maintenance', m(r0['cup_maint']), m(r0['sf_maint']),
          '<span class="pill open">allowance</span>',
          'An allowance per year growing with inflation, not a quotation. Property B is the larger figure, as the '
          'owner described.', src('CDI-RES')],
         ['Property tax', m(r0['cup_tax_pre']), m(r0['sf_tax']),
          '<span class="pill ok">computed from official rates</span>',
          'Assessed value times the published rate for each city. The assessed values are private and are not '
          'published here; the tax bills are model outputs.', src('SCC-RATES', 'SF-TAX')],
         ['Rent received', 'none before the transfer', m(r0['sf_rent']),
          '<span class="pill ok">owner figure</span>',
          'The two let units produce the monthly figure the owner supplied, rounded to $10. The third unit is not let '
          'and is not counted as income in any projection.', src('SF-RENT')],
         ['Vacancy and management allowance', 'not applicable', pc(P['vacancy']) + ' vacancy, ' + pc(P['mgmt']) + ' management',
          '<span class="pill">assumption</span>',
          'Modelled as a deduction from rent. A unit that is never vacant is not the normal case for a three-unit '
          'building over fifty years.', src('HUD-SAFMR')]],
        caption='Every operating line, what is known about it, and how confident the number is',
        note='Placeholder means the figure is an estimate or a bill, rounded to $10, and is not a binding price. '
             'Nothing on this page is an insurance quotation.')

    ins = table(
        ['Insurance question', 'Answer', 'Why it matters', 'Official source'],
        [['Does a homeowners policy cover earthquake?', 'No, not unless the policy or a separate policy includes it',
          'The state insurance department publishes a separate earthquake guide; a standard policy excludes the peril',
          src('CDI-RES')],
         ['Does it cover flood?', 'No', 'Flood needs a separate policy, typically through the federal programme', src('CDI-RES')],
         ['What happens if the house is vacant?', 'Cover can be excluded or restricted after a stated vacancy period',
          'A long vacancy between inheriting and selling is a real gap in cover', src('CDI-RES')],
         ['Is a landlord policy the same product?', 'No',
          'Loss of rent, tenant liability and the actual occupancy must be disclosed. Using a homeowners policy for '
          'a let building can void a claim', src('CDI-RES')],
         ['How should a premium be obtained?', 'A written quote for the actual occupancy and building',
          'ZIP-code averages are marketing figures. The state publishes a premium comparison tool, and its own guide '
          'says to compare coverage, not only price', src('CDI-RES')]],
        caption='Six insurance questions, and the official answer to each')

    around = table(
        ['Year', 'A water', 'A electricity', 'A repairs', 'A tax', 'A insurance', 'Total A', 'Official source'],
        [[str(y), m(ROWS[y - Y0]['cup_water']), m(ROWS[y - Y0]['cup_elec']), m(ROWS[y - Y0]['cup_maint']),
          m(ROWS[y - Y0]['cup_tax_pre']) if y < T else m(M['baseline']['summary']['tax_rent_T']),
          'not quoted', 'partly unquoted', src('CUP-WATER', 'CPUC-NEM')]
         for y in (Y0, 2030, 2035, T, 2060, Y1)],
        caption='Property A running costs, selected years, model values',
        note='Insurance is left out of the total because there is no quote. The total is therefore a lower bound. '
             'The tax column before the transfer is the transferor\'s bill; after it, the rent-out case.')

    body = ''.join([
        banner('<b>The rule on this page: a figure that cannot be verified is labelled, not filled in.</b> Every '
               'premium, bill and allowance below is marked as an owner estimate, an official rate or a model output. '
               'A ZIP-code average is not a price for a particular house, and this edition does not present one as if '
               'it were.'),
        '<div class="kpis">%s</div>' % ''.join([
            kpi('Property A annual running cost, first year', m(sum(v for k, v in r0.items() if isinstance(v, (int, float)) and k in ('cup_water', 'cup_elec', 'cup_maint'))) if False else m(r0['cup_water'] + r0['cup_elec'] + r0['cup_maint']),
                'water, electricity net credit and repairs; insurance excluded because there is no quote'),
            kpi('Property B annual running cost, first year', m(r0['sf_water'] + r0['sf_elec'] + r0['sf_maint']),
                'water, electricity and repairs for the whole building, before tax and insurance'),
            kpi('Property B net income, first year', m(r0['sf_net']), 'rent after a vacancy allowance, every cost above, tax and insurance'),
            kpi('Quoted premiums obtained', '0', 'no binding insurance quote exists for either property - flag U09'),
        ]),
        '<h2>Every cost line</h2>',
        verified,
        '<h2>Insurance: what a policy actually covers</h2>',
        '<p>Insurance is the largest unverified number in the whole analysis, and the one most likely to be wrong. '
        'The California Department of Insurance publishes a residential insurance guide that states what a standard '
        'policy covers and, more importantly, what it excludes. The questions below are the ones a quote must answer.</p>',
        ins,
        '<h2>What the running costs look like over time</h2>',
        around,
        banner('<b>Why insurance is not in the total.</b> Adding an unverified premium to a total would make the total '
               'look verified. The model does carry a premium - the owner\'s estimate, grown with inflation - but the '
               'tables on this page say so wherever it appears rather than folding it silently into a number.', 'warn'),
        '<h2>Costs that are easy to miss</h2>',
        table(['Cost', 'When it applies', 'Size', 'Official source'],
              [['Supplemental property tax', 'After a change of ownership, when the assessor\'s new value is higher than the old one',
                'Prorated for the part of the fiscal year after the transfer; it arrives as a separate bill',
                src('SCC-RATES')],
               ['Escape assessment', 'If the reassessment is determined late', 'The difference is billed later, with a possible instalment plan', src('SCC-RATES')],
               ['Delinquency penalty', 'If either instalment is late', '10%, then 1.5% a month after the roll defaults', src('SF-TAX')],
               ['Fixed electric charge', 'Monthly, regardless of solar generation', 'Approved for the large investor-owned utilities; the amount depends on the tariff and income tier', src('CPUC-FIXED')],
               ['Net-metering true-up', 'At the annual true-up date', 'Surplus energy is paid at a low wholesale-like rate, not at retail', src('CPUC-NEM')],
               ['Selling cost', 'On any sale', pc(P['sell_cost']) + ' of the price in the model - a standard allowance, not a quote', src('IRS-TC409')]],
              caption='Costs that do not appear on a property-tax bill but do appear in the analysis'),
    ])
    return page('costs.html', 'The cost of keeping',
                'Operating costs / 07',
                'What each property costs to hold: property tax from official rates, utilities from the owner\'s bills, '
                'insurance from no quote at all - and every figure labelled by how well it is known.',
                body)
