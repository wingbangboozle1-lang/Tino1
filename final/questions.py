"""Questions register (session 0adc9b0a, task Z3) -> questions.html.

What has to be answered before the live / rent / sell choice can reasonably be made:
what is already known (with the official page), what is not, and how to find it.

Pure data plus one function. `sections(h)` receives a small helper object from
final/build.py (money formatter, source links, flag links, model results) and returns
the rows of each table. Every row ends with an official link; a value that could not be
confirmed on an official page is the BLANK marker, never a guess.

Reading dates: "2026-11-12" means this session opened the official page itself on that
day. "2026-11-11" means the row stands on the earlier pass and was not re-opened.
"""

TODAY = '2026-11-12'
EARLIER = '2026-11-11'


def sections(h):
    m, src, flag, BLANK = h.m, h.src, h.flag, h.BLANK
    B, S_, BE, RH, BY, E = h.B, h.SENS, h.BE, h.RH, h.BY, h.E
    T = B['T']
    sens = dict((s['label'], s) for s in S_)

    def pick(prefix):
        for label, s in sens.items():
            if label.startswith(prefix):
                return s
        raise KeyError(prefix)

    nostep = pick('No basis step-up')
    savings = pick('Proceeds kept in savings')
    mix = pick('Proceeds 60% stocks')
    low = pick('Lower tax bracket')
    top = pick('Top tax bracket')
    ins3 = pick('Insurance three times')
    rent_ratio = BE['rent_month_rent_vs_sell'] / h.P['cup_rent_month']
    e45 = [x for x in E if x['T'] == T][0]
    room, room_real, room_port = e45['exclusion'] - e45['house'], (e45['exclusion'] - e45['house']) / e45['cpi'], 2 * e45['exclusion'] - e45['house']

    # ------------------------------------------------------------------ 1. decisive, still open
    decisive = [
        ['D01', 'What kind of trust holds Property A, and will the home be counted in the Transferor\'s gross estate?',
         'It decides whether the income-tax basis resets to market value at death. With the reset a prompt sale has almost no taxable gain. '
         'Without it the sale is taxed on the whole gain: selling falls from %s to %s and its lead over renting shrinks from %s to %s (wealth in 2076, 2026 dollars).' % (
             m(B['real_sell']), m(nostep['real_sell']), m(B['real_sell'] - B['real_rent']), m(nostep['real_sell'] - nostep['real_rent'])),
         'The rule: the basis of inherited property is generally its market value at the date of death (IRS page re-read %s). '
         'Assets of an irrevocable trust that are outside the gross estate get no reset (revenue ruling read %s, not re-opened).' % (TODAY, EARLIER),
         BLANK + ' ' + flag('Q01'),
         'Nobody working on this site has read the trust document.',
         'Ask the attorney who drafted or will administer the trust for a written answer to two questions: can the Transferor still revoke the trust, '
         'and will Property A be included in the gross estate? The State Bar lists certified specialists in estate planning, trust and probate law.',
         src('IRS-FAQ-INHERIT', 'RR-2023-2', 'CALBAR-SPEC')],
        ['D02', 'Does the Inheritor want to live in Property A?',
         'It is the only question that is not about money. Living there costs about %s of 2076 wealth in 2026 dollars against selling (%s against %s), '
         'and the relief is lost unless the Inheritor moves in within one year.' % (m(B['real_sell'] - B['real_live']), m(B['real_live']), m(B['real_sell'])),
         'The Board of Equalization letter says the home must become the Inheritor\'s principal residence within one year of the transfer, with no exceptions (re-read %s).' % TODAY,
         'Only the Inheritor can answer.',
         'A personal decision, ideally made before the transfer so the one-year clock is not spent deciding.',
         'Decide whether the price above is worth paying. If the answer is "maybe", note that moving in and later moving out ends the relief (row K07).',
         src('BOE-LTA-2026-026', 'BOE-P19')],
        ['D03', 'If Property A is sold, how would the proceeds be invested, and how much risk is acceptable?',
         'Selling wins only if the proceeds are invested for growth. In stocks at 7.0%% a year: %s. In a 60/40 stock and Treasury-bond mix: %s. '
         'In savings at 3.5%%: %s, which is behind renting (%s). Renting catches up when stocks return less than %.1f%% a year.' % (
             m(B['real_sell']), m(mix['real_sell']), m(savings['real_sell']), m(savings['real_rent']), BE['r_stock_rent_vs_sell'] * 100),
         'The SEC investor pages describe spreading money between asset classes and adding it in stages rather than all at once (read %s through excerpts of the official pages).' % TODAY,
         'Only the Inheritor can answer.',
         'A chosen mix of stocks, bonds and cash, and a timetable for investing the proceeds.',
         'Read the two SEC guides, pick a mix, then read that row of the sensitivity table on the Decision page.',
         src('SEC-ALLOC', 'SEC-TEN', 'TREASURY')],
    ]

    # ------------------------------------------------------------------ 2. open, changes the amounts
    amounts = [
        ['D04', 'Is the Inheritor the Transferor\'s child, as Proposition 19 defines it?',
         'The partial property-tax relief for living in the home exists only for parent-to-child transfers (or grandparent-to-grandchild when the parents are deceased). '
         'Without it, living there is taxed like renting: %s a year instead of %s in %d.' % (m(B['tax_rent_T']), m(B['tax_live_T']), T),
         'The rule is on the Board of Equalization page (re-read %s).' % TODAY,
         BLANK + ' ' + flag('Q06'),
         'The family relationship was not supplied.',
         'Check the definition of an eligible child on the Board of Equalization page; confirm with the County Assessor if in doubt.',
         src('BOE-P19', 'BOE-LTA-2026-026')],
        ['D05', 'Will Property A still be the Transferor\'s principal residence at the date of death?',
         'The relief applies only to a home that was the Transferor\'s principal residence. A move to a care home does not break this if the Transferor would return and the home is not rented outside the immediate family.',
         'Board of Equalization letter, care-facility answer (re-read %s). The homeowners\' exemption is $7,000 of assessed value and is claimed on form BOE-266 (re-read %s).' % (TODAY, TODAY),
         BLANK,
         'Whether the homeowners\' exemption is on the current tax bill, and the Transferor\'s future living arrangements.',
         'Look for a homeowners\' exemption line of $7,000 on the annual bill for Property A. If it is missing, ask the Assessor how to claim it.',
         src('BOE-LTA-2026-026', 'BOE-HOX')],
        ['D06', 'Are there other beneficiaries, and does the trust give Property A to the Inheritor alone?',
         'A home given to one child out of a shared estate qualifies in full only if its value is no more than that child\'s share. It also decides how much of the cash arrives.',
         'Board of Equalization letter, answer on unequal distributions (re-read %s).' % TODAY,
         BLANK,
         'The distribution terms of the trust.',
         'Same letter to the attorney as D01: who receives what, and may the trustee distribute unequally?',
         src('BOE-LTA-2026-026', 'CALBAR-SPEC')],
        ['D07', 'How much cash and other property is in the Transferor\'s estate, and in what form?',
         'Federal estate tax is 40%% of the estate above the exclusion. The baseline leaves room for %s of cash and other assets in %d (%s in 2026 dollars). '
         'The form matters too: inherited retirement accounts are taxed as they are withdrawn.' % (m(room), T, m(room_real)),
         'Exclusion $15,000,000 for 2026 and $15,480,000 for 2027 (both re-read %s). No California tax (re-read %s).' % (TODAY, TODAY),
         BLANK + ' ' + flag('Q02'),
         'The total, and the split between bank deposits, investment accounts, retirement accounts and life insurance.',
         'Add up the latest statements and read the matching row of the table on the Cash page. Nothing needs to be published.',
         src('IRS-ESTATE', 'RP-2026-35', 'IRS-P559')],
        ['D08', 'Did a spouse of the Transferor die earlier, and was the unused exclusion carried over?',
         'A carried-over exclusion roughly doubles the room, to about %s in %d.' % (m(room_port), T),
         'Carrying it over needs a timely Form 706 for the first death (re-read %s). A late election can sometimes be made up to the fifth anniversary (read %s).' % (TODAY, EARLIER),
         BLANK + ' ' + flag('Q02'),
         'Whether a Form 706 was filed after the first death.',
         'Look for the return in the family records or ask the attorney or accountant who handled that estate.',
         src('IRS-ESTATE', 'IRS-FAQ-ESTATE')],
        ['D09', 'What will the Inheritor\'s filing status and income be?',
         'They set the tax rates on rent, dividends and gains. Selling stays first in both brackets tested: %s in a low bracket and %s in the top bracket, against %s and %s for renting.' % (
             m(low['real_sell']), m(top['real_sell']), m(low['real_rent']), m(top['real_rent'])),
         'Federal 2027 rate tables and California rate schedules (both read %s, not re-opened).' % EARLIER,
         'Baseline assumes 24% federal and 9.3% California. ' + flag('Q05'),
         'The Inheritor\'s own figures.',
         'Take them from the most recent tax return, or ask a tax adviser to project them.',
         src('RP-2026-35', 'FTB-RATES')],
        ['D10', 'What is the Inheritor\'s income-tax basis in Property B, and how much depreciation has been claimed on the rented units?',
         'Only matters if Property B is ever sold. The model never sells it; the upper-bound tax on a sale is about %s.' % m(h.SF_SALE_TAX),
         'Basis is generally cost, raised by improvements and lowered by depreciation allowed (IRS topic read %s).' % TODAY,
         BLANK + ' ' + flag('Q03'),
         'Purchase or earlier inheritance records, and past depreciation schedules.',
         'Find the closing statement for Property B and the depreciation form attached to past returns.',
         src('IRS-TC703', 'IRS-TC409')],
        ['D11', 'Is Property B covered by San Francisco rent control?',
         'It limits how fast rent on the two let units can rise. It does not change the choice for Property A, because Property B is the same in all three choices.',
         'Allowed increase 1.6%% from 2026-03-01 to 2027-02-28; a vacant unit can be let at any first rent (re-read %s).' % TODAY,
         BLANK + ' ' + flag('Q04'),
         'The year the building was built and its legal unit count.',
         'Read the coverage rules on the City\'s rental-law page, or ask a Rent Board counselor.',
         src('SF-RENT-LAW', 'SF-RENT-RULES')],
    ]

    # ------------------------------------------------------------------ 3. facts the owner can look up
    lookups = [
        ['F01', 'How many bedrooms does Property A have, and what would it rent for?',
         'Rent would have to be about %s a month, roughly %.1f times the figure used, before renting matches selling. A more exact rent changes the amounts, not the ranking.' % (m(BE['rent_month_rent_vs_sell']), rent_ratio),
         'HUD fiscal-year 2026 rent for ZIP 95014: four-bedroom %s, three-bedroom $5,870 a month (re-read %s). A fiscal-year 2027 release took effect 2026-10-01.' % (m(h.P['cup_rent_month']), TODAY),
         'Fiscal-year 2027 figure for the ZIP: ' + BLANK + ' ' + flag('U08') + ' ' + flag('U09'),
         'The bedroom count, and the 2027 figure, which sits behind an interactive lookup this session could not operate.',
         'Open the HUD release list, choose fiscal year 2027, enter the ZIP code and read the row for the right number of bedrooms.',
         src('HUD-95014', 'HUD-SAFMR-INDEX', 'FR-FMR-2027')],
        ['F02', 'What does insurance really cost for each home?',
         'Tripling the estimate lowers the Live result by %s and leaves the ranking unchanged.' % m(B['real_live'] - ins3['real_live']),
         'The owner\'s estimate is $1,500 a year for each home. The Department of Insurance publishes ZIP-level comparison premiums in an interactive tool (page read %s).' % EARLIER,
         BLANK + ' ' + flag('U01') + ' ' + flag('U02'),
         'The ZIP-level premium range, a landlord quote for a three-unit building, and earthquake cover.',
         'Follow the four steps on the Insurance and costs page; ask an agent for the landlord and earthquake quotes.',
         src('CDI-TOOL', 'CDI-TOOL-APP', 'CDI-EQ')],
        ['F03', 'What is the 2026 tax bill for Property A, its tax rate area and its fixed charges?',
         'Sets the starting point of every property-tax row. The 2025 bill was %s.' % m(h.P['cup_tax_2025']),
         'County rate 1.16360%% from the rate book (read %s, not re-opened).' % EARLIER,
         '2026 bill: ' + BLANK + ' ' + flag('U03'),
         'The 2026 bill itself.',
         'Read the tax rate area code and the list of special assessments printed on the bill.',
         src('SCC-RATES', 'BOE-P19')],
        ['F04', 'Is the solar system at Property A owned or leased, and on which tariff?',
         'The credit is small (%s a year in the model). Ownership and tariff decide what a buyer or tenant would take over; neither was supplied.' % m(-h.P['cup_elec']),
         'State net-metering and fixed-charge material (read %s through excerpts, not re-opened).' % EARLIER,
         BLANK + ' ' + flag('U05'),
         'The solar contract and the interconnection date.',
         'Read the contract and the rate schedule named on the electricity bill.',
         src('CPUC-NEM', 'CPUC-FIXED')],
    ]

    # ------------------------------------------------------------------ 4. cannot be known in advance
    y = dict((int(k), v) for k, v in BY.items())
    later = [
        ['T01', 'In which year will the inheritance happen?',
         'Selling is first in every year tested. 2040: %s against %s for renting. 2045: %s against %s. 2050: %s against %s.' % (
             m(y[2040]['real_sell']), m(y[2040]['real_rent']), m(y[2045]['real_sell']), m(y[2045]['real_rent']), m(y[2050]['real_sell']), m(y[2050]['real_rent'])),
         'Cannot be known.',
         'Use the year switch on the Summary page; rerun the model when the date is known.',
         src('BOE-RULE-462.260', 'RTC-480')],
        ['T02', 'What will Property A be worth at the date of death?',
         'The baseline grows %s at 4.0%% a year to %s in %d. Renting would match selling only if the home rose %.1f%% a year for the whole period.' % (
             m(h.P['cup_value']), m(B['fmv_T']), T, BE['g_cup_rent_vs_sell'] * 100),
         'Cannot be known; today\'s value is the owner\'s estimate ' + flag('P03') + '.',
         'Order a written appraisal as of the date of death. It sets both the new basis and the reassessed value.',
         src('FHFA-SJ', 'IRS-FAQ-INHERIT')],
        ['T03', 'What will the law be at that time?',
         'Three rules carry the result: the basis reset at death, the Proposition 19 allowance ($1,044,586 until 2027-02-15, next figure not yet published) and the federal exclusion.',
         'Cannot be known. ' + flag('U04') + ' ' + flag('S05'),
         'Re-read the Law page once a year. Dates already known: ballot results certified by 2026-12-11; new allowance letter in February 2027; next federal inflation figures each autumn.',
         src('BOE-LTA-2025-009', 'SOS-RESULTS', 'RP-2026-35')],
        ['T04', 'How will stocks, house prices and inflation behave afterwards?',
         'In replays of the real 1976-2025 record, selling is ahead of renting in %d of 50 ten-year periods and %d of 50 twenty-year periods. Renting ends ahead in the Japan-style and 1929-1941 paths.' % (
             RH['10']['wins']['sell'], RH['20']['wins']['sell']),
         'Cannot be known.',
         'Read the Black swan page before choosing a mix (D03); investing in stages narrows the worst cases.',
         src('BLS-CPI', 'FHFA-SJ', 'SEC-TEN')],
    ]

    # ------------------------------------------------------------------ 5. answered
    known = [
        ['K01', 'Is there a city, county or California tax on an inheritance?',
         'No. California requires no estate tax return for deaths on or after 2005-01-01, and its inheritance tax applies only to deaths before 1982-06-08.',
         'None.', TODAY, src('SCO-ESTATE')],
        ['K02', 'How much can pass free of federal estate tax?',
         '$15,000,000 per person for deaths in 2026 and $15,480,000 in 2027, indexed after that; 40% above it. The tax is paid by the estate.',
         'None on live, rent or sell: the tax is fixed at the date of death.', TODAY + ' (amounts); ' + EARLIER + ' (rate, excerpt)', src('IRS-ESTATE', 'RP-2026-35', 'IRS-I706')],
        ['K03', 'Does the Inheritor pay income tax on inherited cash?',
         'Not on the inheritance itself. Interest, dividends and gains earned afterwards are taxable.',
         'None.', EARLIER + ' (excerpt; not re-opened)', src('IRS-P559')],
        ['K04', 'Is a sale of Property A soon after the death taxed?',
         'The basis is generally the market value at the date of death, so only growth after that date is gain. In the baseline, selling costs turn it into a loss of %s and no tax is due. This depends on D01.' % m(-B['sell_gain']),
         'The main reason selling comes first.', TODAY, src('IRS-FAQ-INHERIT')],
        ['K05', 'Will Property A be reassessed for property tax?',
         'Yes. Lived in by the Inheritor: only the value above the old assessed value plus $1,044,586 is added, so the baseline assessed value goes from %s to %s and the tax from %s to %s a year. '
         'Rented, left empty or held for sale: full market value, %s, and %s a year.' % (m(B['fbyv_T']), m(B['taxable_live_T']), m(B['tax_before_T']), m(B['tax_live_T']), m(B['taxable_rent_T']), m(B['tax_rent_T'])),
         'Makes renting the most heavily taxed route and living there only partly relieved.', TODAY + ' (rules); model output', src('BOE-P19', 'BOE-LTA-2025-009', 'SCC-P19', 'SCC-P19-EST')],
        ['K06', 'What are the deadlines for keeping that relief?',
         'Move in and claim the homeowners\' exemption within one year of the transfer. File the exclusion claim (form BOE-19-P) within three years and before any sale to a third party.',
         'Applies only to living in the home.', TODAY, src('BOE-LTA-2026-026', 'BOE-HOX', 'CAPF-BOE19P')],
        ['K07', 'Can the Inheritor move in, keep the relief, and rent the home out later?',
         'No. The exclusion is removed when the home stops being the principal residence of an eligible child, and the value then enrolled is the market value at the date of the transfer, adjusted for inflation since.',
         'Rules out "live first, rent later" as a way to keep the low tax.', TODAY, src('BOE-LTA-2026-026')],
        ['K08', 'Can Property A be held through a limited liability company and keep the relief?',
         'No. Property held in, or moved into, a company is not eligible, including a single-member company. Property held in a trust is treated as held by its beneficiaries.',
         'Relevant if a company is suggested for a rental.', TODAY, src('BOE-LTA-2026-026')],
        ['K09', 'Does the inheritance change anything for Property B?',
         'No. It is already owned by the Inheritor: it is not reassessed, its basis does not reset, and it is not in the Transferor\'s estate. Its low assessed value saves about %s a year against a new buyer\'s tax.' % m(h.SF_GAP),
         'Keep Property B as it is in every choice.', TODAY + ' (San Francisco rate)', src('SF-TAX', 'BOE-RULE-462.260')],
        ['K10', 'How fast can rent on Property B rise if it is rent-controlled?',
         '1.6% for increases from 2026-03-01 to 2027-02-28. A proposal to cap banked and capital-improvement increases at 10% a year (File No. 261020) has not been enacted.',
         'None on Property A.', TODAY, src('SF-RENT-RULES', 'SF-LEG-261020')],
        ['K11', 'How is a large cash balance protected while a decision is pending?',
         'Bank deposits are insured up to $250,000 per depositor, per bank, per ownership category. Treasury securities are not deposit-insured but are backed by the U.S. government.',
         'Practical point for the cash and for sale proceeds.', TODAY, src('FDIC', 'TREASURY')],
        ['K12', 'Can tax on the sale of a rental be deferred?',
         'Gain is generally not recognised when investment real estate is exchanged solely for like-kind real estate; any cash received is taxed. This is not modelled.',
         'Relevant only if Property B, or Property A after a period as a rental, is sold.', TODAY, src('IRS-1031')],
        ['K13', 'Which notices and filings follow the death?',
         'Trustee notification within 60 days; change-in-ownership statement within 150 days; Form 706, if required, within nine months. The full list is on the Process page.',
         'Same for all three choices.', EARLIER + ' (statutes not re-opened)', src('PROB-16061.7', 'RTC-480', 'IRS-FAQ-ESTATE')],
        ['K14', 'On today\'s law and the stated assumptions, which choice leaves the most wealth?',
         'Sell Property A and reinvest: %s, against %s for renting and %s for living there (2076, after tax, 2026 dollars). Keep Property B. Conditional on D01 and D03.' % (m(B['real_sell']), m(B['real_rent']), m(B['real_live'])),
         'The conditional recommendation on the Summary page.', TODAY + ' (rules); model output', src('IRS-FAQ-INHERIT', 'BOE-P19')],
    ]

    # ------------------------------------------------------------------ 6. who to ask
    who = [
        ['1', 'Estate attorney', 'D01, D06, D08, and D04 and D05 if in doubt', 'One letter. The answer to D01 can change the amounts by millions of dollars.', src('CALBAR-SPEC', 'IRS-FAQ-INHERIT')],
        ['2', 'The Inheritor, alone', 'D02, D03', 'No outside help needed; these two set the direction.', src('BOE-LTA-2026-026', 'SEC-ALLOC')],
        ['3', 'Tax adviser', 'D07, D09, D10', 'Bring the estate total, the last tax return and the Property B records.', src('IRS-ESTATE', 'IRS-TC703')],
        ['4', 'County Assessor (estimator and claim form)', 'D04, D05, F03', 'The county publishes an estimator for the parent-child exclusion.', src('SCC-P19-EST', 'SCC-P19')],
        ['5', 'Insurance comparison tool and an agent', 'F02', 'About five minutes for the tool; quotes take longer.', src('CDI-TOOL-APP', 'CDI-EQ')],
        ['6', 'Papers already at home', 'F01, F03, F04, D11', 'Tax bill, solar contract, electricity bill, building records.', src('HUD-SAFMR-INDEX', 'SF-RENT-LAW')],
    ]

    return dict(decisive=decisive, amounts=amounts, lookups=lookups, later=later, known=known, who=who)
