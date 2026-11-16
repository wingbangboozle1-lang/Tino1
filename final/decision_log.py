"""Decision log and pre-commitment rules (session arena/3adb817a-tino1).

Two pages that the owner asked for and that the site did not have:

  * decisions.html - every decision the analysis has taken, with the date it was
    taken, what was decided, why, and the official page or model output it rests
    on, so a reader in 2045 can see what was chosen and on what evidence. A
    second, empty table is left for the household's own decisions: date, choice,
    reason, sign.
  * precommit.html - the rule that says, in advance, what would make the
    household choose each path. The point is to write it before the figures
    arrive, so the outcome is not reverse-engineered from one projection. The
    model's break-even points are given as the reference the rule should be
    compared with; the rule itself is left blank for the household.

Every row ends with a link to an official page or to a flagged item. Nothing
here is invented: each figure comes from final/model.py or from a source in
final/sources.py, and each reading date is the day a work session opened the
page itself.
"""

# Decisions taken by the analysis, with the date the work session recorded them.
# (date, item, decision, why, basis). "{T}" and "{cup}"/"{sf}" are replaced by the
# model values when the page is built; nothing else is interpolated.
DECISIONS = [
    ['2026-11-10', 'Which home is being inherited',
     'Property A (the future inheritance) is the only property this analysis decides about. Property B is already owned by the Inheritor.',
     'The brief says so, and the law follows: a reassessment follows a change in ownership, and Property B does not change hands when the Transferor dies. So Property B keeps its assessed value, keeps its income-tax basis, and stays outside the Transferor\'s estate.',
     'SF-TAX'],
    ['2026-11-10', 'What the model treats as the estate',
     'Only the assets of the Transferor count for the federal estate-tax test; Property B is excluded from every estate figure on this site.',
     'The gross estate is what the decedent owned. Adding an already-owned home would overstate the estate and understate the room left for cash.',
     'IRS-ESTATE'],
    ['2026-11-11', 'Which year to model',
     'The inheritance year is {T}, and the what-if grid also runs 2040 and 2050.',
     'The brief puts the inheritance "around 2040-2050". A single year hides the effect of a different date, so the year is a control, not a fixed input.',
     'IRS-ESTATE'],
    ['2026-11-11', 'Whether the basis resets at death',
     'The baseline assumes Property A is in the Transferor\'s gross estate, so the income-tax basis resets to market value at death. The opposite case is a labelled sensitivity, not the baseline.',
     'The trust has not been read. The question is decisive: without the reset a prompt sale is taxed on decades of gain, which is the difference between selling and keeping.',
     'IRS-FAQ-INHERIT'],
    ['2026-11-11', 'Starting values for the two homes',
     'Property A {cup} and Property B {sf} (owner estimates, rounded to the nearest $10); rents, utilities and insurance are owner figures too.',
     'No official page publishes a particular parcel\'s value or bill. They are shown rounded, labelled as owner figures, and never silently replaced.',
     'SCC-RATES'],
    ['2026-11-12', 'What rent to model for Property A',
     'The HUD fair market rent for the ZIP code is used as a benchmark, with the 3-bedroom figure as the downside gate. It is not treated as a quote.',
     'The bedroom count and the rentable condition of Property A are not known, and no rent comparables have been obtained. A benchmark that is labelled as one is honest; a made-up rent is not.',
     'HUD-95014'],
    ['2026-11-13', 'How to park sale proceeds',
     'The phased test parks the proceeds in a 3-month-to-2-year Treasury sleeve for 24 or 36 months, then phases into stocks. The 3-month bill is the proxy for the sleeve because the 2-year series is not in the repository for the whole test period.',
     'The brief asks whether parking the money softens the crash at entry in 1929 and 2008. The proxy and its limits are stated on the page rather than hidden.',
     'TREASURY'],
    ['2026-11-13', 'How to treat laws that are not in force',
     'Enacted law, pending bills and proposals are kept in separate tables everywhere, and no model row depends on a measure that has not been enacted.',
     'A proposal that changes the answer has to be visible as a proposal. A site that treats a bill as law is worse than a site that is silent about it.',
     'SOS-RESULTS'],
    ['2026-11-16', 'Proposition H (San Francisco parcel tax)',
     'The model charges the official minimum multifamily amount, $249 a year from fiscal year 2027-28, indexed to inflation afterwards.',
     'The building area and the parcel classification are private facts that are not in the repository, so the official minimum is used and the area-dependent rate is shown as a labelled sensitivity.',
     'SFMTA-PROP-H'],
    ['2026-11-16', 'What the live site publishes',
     'This rounded-figures edition is published, and the figure-free guide stays published one click away.',
     'The brief asks for a live site that carries the analysis and the numbers. Rounding to the nearest $10 and using placeholders for every person and property is the disclosure control the brief sets; the guide without figures remains available for anyone who wants to share only the method.',
     'BOE-P19'],
    ['2026-11-16', 'When the rules are written down',
     'The pre-commitment rules on the next page are written before the inheritance, not after the numbers are known.',
     'A decision rule written after the projection is reverse-engineered from one projection. The rule is the thing that protects the decision from that.',
     'IRS-ESTATE'],
]

# The household's own decisions. The cells are deliberately unfilled, but they are
# never empty: a blank that is not labelled reads as an oversight, and the checker
# treats an empty cell as a value that must be flagged.
HOUSEHOLD_HEADER = ['No.', 'Decision to be taken', 'Date', 'Decision taken', 'Why (one line)', 'Signed', 'Official basis']
TO_COMPLETE = '(to be completed by the household)'
HOUSEHOLD_ROWS = [
    ['1', 'Whether, and when, to sell Property A', TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, 'IRS-FAQ-INHERIT'],
    ['2', 'Which path the sale proceeds follow, and for how long they stay in Treasuries', TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, 'TREASURY'],
    ['3', 'Whether Property B is kept, and whether the third unit is let', TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, 'SF-RENT-RULES'],
    ['4', 'Who the estate attorney and the tax adviser are, and what each is asked', TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, TO_COMPLETE, 'IRS-ESTATE'],
]


def _fill(text, h):
    """Replace the fixed tokens. Nothing else is interpolated, so a literal % in
    the text can never be read as a format directive."""
    return (text.replace('{T}', str(h.B['T']))
                .replace('{cup}', h.m(h.P['cup_value']))
                .replace('{sf}', h.m(h.P['sf_value'])))


def household_rows(h):
    """The household's own decision rows, with the official basis of each rule resolved."""
    return [[r[0], r[1], r[2], r[3], r[4], r[5], h.src(r[6])] for r in HOUSEHOLD_ROWS]


def decision_log(h):
    """Rows for the decisions table, with the basis resolved to an official link."""
    src = h.src
    rows = []
    for date, item, decision, why, basis in DECISIONS:
        rows.append([date, item, _fill(decision, h), _fill(why, h), src(basis)])
    return rows


def precommit_rows(h):
    """The three paths, the rule the household should write for each, and the model's reference point."""
    m, pc, src, flag = h.m, h.pc, h.src, h.flag
    BE, B, RH = h.BE, h.B, h.RH
    n10 = RH['10']['wins']['sell'] + RH['10']['wins']['rent'] + RH['10']['wins']['live']
    return [
        ['Live in Property A',
         'We will live in Property A if:',
         'The modelled break-even is a home appreciation rate of %s a year: below it, living in the home leaves the household with less than selling would. The rule should name a rate, not a feeling. %s' % (
             pc(BE['g_cup_live_vs_sell'], 1), flag('A01')),
         'Living in the home has a price that is easy to understate: the interest on the money that could have been invested elsewhere, the difference between the rent Property B could charge and what it does charge, and the repair and insurance bill. Write the rule as "if the house is worth more than X, we live in it", so the trigger is a number.',
         src('FHFA-SJ')],
        ['Rent Property A',
         'We will rent Property A if:',
         'The modelled break-even is a market rent of %s a month, against the HUD benchmark of %s, and a stock return of %s. Renting wins only if the rent is real and the proceeds are not parked in cash. %s' % (
             m(BE['rent_month_rent_vs_sell']), m(h.P['cup_rent_month']), pc(BE['r_stock_rent_vs_sell'], 1), flag('A08')),
         'Renting is the most sensitive of the three to two things the household controls: what it actually charges, and where the money goes. Both belong in the rule, in writing, before the inheritance.',
         src('HUD-95014')],
        ['Sell Property A and reinvest',
         'We will sell Property A if:',
         'The modelled break-even is a home appreciation rate of %s a year and a stock return of %s. Selling leads in the baseline and in %d of the %d real historical sequences after ten years, and in all of them after twenty. %s' % (
             pc(BE['g_cup_rent_vs_sell'], 1), pc(BE['r_stock_rent_vs_sell'], 1),
             RH['10']['wins']['sell'], n10, flag('A02')),
         'Selling is the path the numbers support, and it is also the one that is irreversible and the one whose outcome depends on markets. The rule should say in advance what the household will do with the money, and when it may not change its mind.',
         src('IRS-FAQ-INHERIT')]
    ]
