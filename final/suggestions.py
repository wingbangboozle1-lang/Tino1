"""Suggestions register (session 0adc9b0a, task Z2) -> suggestions.html.

Proposals for making the site more useful for the decision. NOTHING here is implemented:
the page exists so the owner can read the options and choose a path first. Each row says
what the site does today, the options, the suggested choice, what the change would do to
the decision, and the effort and risk. Every row ends with an official link to the rule
or data the change would rest on.

`sections(h)` receives the same helper object as final/questions.py.
"""


def opts(*items):
    """Options as lettered lines inside one table cell."""
    return '<br>'.join('<strong>%s.</strong> %s' % (chr(65 + i), x) for i, x in enumerate(items))


def sections(h):
    m, src, flag = h.m, h.src, h.flag
    B, BE = h.B, h.BE
    GH = '<a href="https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site" rel="noopener">GitHub Docs: creating a Pages site</a>'
    rent_ratio = BE['rent_month_rent_vs_sell'] / h.P['cup_rent_month']

    # ------------------------------------------------------------------ 1. privacy and housekeeping
    privacy = [
        ['G01', 'Decide what to do about the public repository and its history',
         'The site shows figures rounded to $10 and no names. The repository behind it is public, and its Git history still holds the first pages, written before rounding. ' + flag('P01') + ' ' + flag('P02'),
         opts('Leave as it is. The exposure stays.',
              'Make the repository private. On a free GitHub plan a Pages site needs a public repository, so the site would stop unless the plan is upgraded; on a paid plan the site itself stays public.',
              'Create a fresh repository holding only the current generator and pages, with no history, then delete the old one. The site keeps working, possibly at a new address.',
              'Publish only the edition without figures and keep the numeric edition on a private computer.'),
         'C, because it keeps the numeric site and removes the history. D if any published figure is too much.',
         'None on the result. It decides how much of the analysis can stay online.',
         'Owner-only actions; about an hour. B and C drop the pull-request trail. Copies already made by others cannot be recalled.',
         GH + ' · ' + src('BOE-P19', 'SCC-RATES')],
        ['G02', 'Clear out superseded branches and directories',
         'The repository carries dozens of old branches and about fifteen superseded directories. Each is another copy of earlier figures. They are excluded from the site but readable in the repository.',
         opts('Leave them; they are the audit trail.',
              'Tag the current state, then delete merged and stale branches and the superseded directories.',
              'Let G01 option C take care of it.'),
         'Decide together with G01.',
         'None on the result.',
         'Deletion cannot be undone from a work session; it needs the owner\'s consent. Small effort once decided.',
         GH + ' · ' + src('BOE-P19')],
        ['G03', 'Show when each fact was last read, and when to read it again',
         'Pages carry one build date. Three verification passes exist, but a reader cannot see row by row which fact was re-read when, and nothing prompts a re-read when an official figure is due to change.',
         opts('Leave as it is.',
              'Add a "last read" date to every source and a short re-check calendar: ballot certification by 2026-12-11, the new Proposition 19 allowance in February 2027, federal inflation figures each autumn, local tax rates each year, HUD rents each October.',
              'B plus a scheduled reminder that opens a repository issue on those dates.'),
         'B.',
         'Keeps the answer from quietly going stale over a 15 to 25 year wait.',
         'Small. C adds automation that has to be maintained.',
         src('BOE-LTA-2025-009', 'SOS-RESULTS', 'HUD-SAFMR-INDEX')],
    ]

    # ------------------------------------------------------------------ 2. better inputs
    inputs = [
        ['G04', 'Use the current HUD rent and the real bedroom count for Property A',
         'The rent is the fiscal-year 2026 four-bedroom figure, %s a month. A fiscal-year 2027 release took effect 2026-10-01, and the bedroom count was never supplied. ' % m(h.P['cup_rent_month']) + flag('U08') + ' ' + flag('U09'),
         opts('Leave as it is.',
              'The owner reads the 2027 figure for the right bedroom count in the HUD lookup; the model is rerun.',
              'B, and also show an owner estimate of market rent beside it, rounded and flagged as unconfirmed.'),
         'B.',
         'Small. Rent would need to be about %.1f times the figure used before renting matches selling.' % rent_ratio,
         'Small. C adds one more owner figure that no official page can confirm.',
         src('HUD-SAFMR-INDEX', 'FR-FMR-2027', 'HUD-95014')],
        ['G05', 'Fill the blank insurance figures',
         'Both homes use the owner\'s estimate of $1,500 a year. The official ZIP-level premiums sit in an interactive tool that an automated session cannot read. ' + flag('U01') + ' ' + flag('U02'),
         opts('Leave the estimate.',
              'The owner reads the premium range for both ZIP codes in the comparison tool; the range is shown as the official figure.',
              'B plus real quotes: homeowners for Property A, landlord cover for a three-unit Property B, earthquake for both.'),
         'B now, C before the transfer.',
         'None on the ranking (tripling the estimate was tested). Makes the yearly cost tables trustworthy.',
         'Small. Quotes are personal documents and must stay off the site; only rounded totals would be used.',
         src('CDI-TOOL-APP', 'CDI-TOOL', 'CDI-EQ')],
        ['G06', 'Let the reader test their own cash amount without publishing it',
         'The Cash page lists example amounts from $2,000,000 to $30,000,000. The real amount is unknown and should not be published. ' + flag('Q02'),
         opts('Leave the example table.',
              'Add a box on the Cash page: the amount is typed in, the room and the tax are worked out in the browser, and nothing is stored or sent.',
              'Publish a broad band for the amount.'),
         'B.',
         'Turns "it may exceed the threshold" into a yes or no for the real figure.',
         'Small. C would reveal wealth and is not advised.',
         src('IRS-ESTATE', 'RP-2026-35')],
        ['G07', 'Show the result for the Inheritor\'s own tax bracket',
         'The baseline assumes 24% federal and 9.3% California. A low and a top bracket are in the sensitivity table only. ' + flag('Q05'),
         opts('Leave as it is.',
              'Add a bracket switch on the Decision page using results the model already produces.',
              'The owner supplies filing status and an income band; the baseline is rerun on it.'),
         'B.',
         'No change of ranking in the brackets tested; the amounts move by up to a few million dollars.',
         'Small for B. C adds a personal detail to the inputs.',
         src('RP-2026-35', 'FTB-RATES')],
        ['G08', 'Replace round-number assumptions with ranges or real figures',
         'Selling cost 5%, vacancy 5%, management 6% and repairs of $6,000 and $12,000 a year are planning figures with no official source. ' + flag('A06') + ' ' + flag('A08'),
         opts('Leave as they are, flagged.',
              'The owner supplies actual repair spending at Property B and typical agent and manager fees.',
              'Show a low and a high column for each, so the reader sees the spread instead of one figure.'),
         'C.',
         'Small on the ranking; mainly affects the yearly cash-flow tables.',
         'Small. B adds owner figures that cannot be confirmed officially.',
         src('SCC-DTT', 'IRS-P527')],
    ]

    # ------------------------------------------------------------------ 3. decision tools
    tools = [
        ['G09', 'Put "what would change the answer" on the first screen',
         'The tipping points are on the Decision page: stock returns below %.1f%% a year, home appreciation above %.1f%%, rent above %s a month, no basis reset, proceeds left in savings.' % (
             BE['r_stock_rent_vs_sell'] * 100, BE['g_cup_rent_vs_sell'] * 100, m(BE['rent_month_rent_vs_sell'])),
         opts('Leave them on the Decision page.',
              'Add a five-row panel to the Summary page, each row linking to its evidence.',
              'Replace some of the headline figures with the panel.'),
         'B.',
         'A reader sees at once under which conditions selling stops being first.',
         'Small. No new numbers.',
         src('FHFA-SJ', 'TREASURY', 'IRS-FAQ-INHERIT')],
        ['G10', 'Model mixed paths, not only the three pure choices',
         'Each choice is held unchanged to 2076 and Property B is never sold. Not modelled: live in Property A for some years and then sell; rent for some years and then sell; sell Property B and live in Property A.',
         opts('Leave as it is.',
              'Add "live, then sell" and "rent, then sell" with 5-year and 10-year holds.',
              'B plus "sell Property B instead", which first needs the basis of Property B (Questions, D10).'),
         'B.',
         'Shows what waiting costs. Moving out ends the Proposition 19 relief, and the home-sale exclusion needs two years of ownership and use, so the order of events matters.',
         'Medium: a model change and a fresh check of every new figure. More scenarios mean more numbers to keep consistent.',
         src('BOE-LTA-2026-026', 'IRS-TC701', 'IRS-1031')],
        ['G11', 'Show reinvestment risk beside the headline',
         'The headline for selling assumes all proceeds in stocks at 7.0%% a year (%s). The 60/40 mix and savings results are lower down, and investing in stages is not modelled.' % m(B['real_sell']),
         opts('Leave as it is.',
              'Show stocks, a 60/40 mix and savings side by side wherever the headline appears.',
              'B plus a staged-investment variant, for example over three years.'),
         'B, then C.',
         'Makes plain that selling is first only when the proceeds are invested for growth.',
         'Small for B, medium for C.',
         src('SEC-ALLOC', 'SEC-TEN', 'TREASURY')],
        ['G12', 'Add what-if controls',
         'The dashboard switches the year of inheritance between 2040, 2045 and 2050. Other inputs change only by reading the sensitivity table.',
         opts('Leave the fixed tables.',
              'Add sliders for home appreciation, stock return and rent, fed by a grid of results worked out in advance by the model.',
              'Rewrite the model to run in the browser.'),
         'B.',
         'Lets the owner test their own beliefs without asking for a rebuild.',
         'Medium for B. C creates a second copy of the model that can drift from the first.',
         src('FHFA-SJ', 'TREASURY', 'HUD-95014')],
        ['G13', 'Make a one-page brief for the attorney and the tax adviser',
         'The open questions are on the Questions page, in wide tables meant for a screen.',
         opts('Leave as it is.',
              'Add a print layout to the Questions page: open questions and the few figures an adviser needs, on one sheet.',
              'A separate adviser page.'),
         'B.',
         'Gets the decisive questions answered sooner.',
         'Small.',
         src('CALBAR-SPEC', 'IRS-FAQ-INHERIT')],
        ['G14', 'Show the deadlines as a timeline',
         'The Process page is a 16-row table. The clocks that start at the date of death (60 days, 150 days, nine months, one year, three years) are spread through it.',
         opts('Leave the table.',
              'Add a timeline above the table and a separate short list of what to do while the Transferor is alive.',
              'B plus a calendar file made in the browser from a typed date.'),
         'B.',
         'Lowers the risk of missing the one-year move-in limit, which has no exception.',
         'Small. For C the date stays in the browser.',
         src('BOE-LTA-2026-026', 'PROB-16061.7', 'RTC-480')],
        ['G15', 'Group the menu and add a glossary',
         'The top menu has sixteen entries of equal weight. Terms such as basis, assessed value and exclusion are explained where they first appear, not in one place.',
         opts('Leave as it is.',
              'Three groups - Decide, Evidence, Audit - and a short glossary page.',
              'Move the audit pages to the footer.'),
         'B.',
         'Makes the pages that carry the decision easier to find.',
         'Small. Addresses of existing pages would not change.',
         src('DIGITAL-GOV', 'BOE-P19')],
    ]

    # ------------------------------------------------------------------ 4. ready-made paths
    paths = [
        ['Path 0', 'Change nothing', 'none',
         'The site stays as it is. The Questions page can still be worked through on paper.',
         'None', src('IRS-FAQ-INHERIT')],
        ['Path 1', 'Privacy first', 'G01, G02',
         'Settles where the analysis may live before anything else is added to it. Recommended first, because privacy was set as the top priority.',
         'Owner only; about an hour', GH + ' · ' + src('BOE-P19')],
        ['Path 2', 'Better inputs', 'G04, G05, G06, G07, G08, G03',
         'A few facts from the owner and small page changes. The fastest way to firmer numbers.',
         'Small', src('HUD-SAFMR-INDEX', 'CDI-TOOL-APP')],
        ['Path 3', 'Decision tools', 'G09, G11, G13, G14, G15, then G10 and G12',
         'Makes the answer and its conditions easier to see and test. The two model changes come last because every new figure has to be checked.',
         'Small to medium', src('BOE-LTA-2026-026', 'SEC-ALLOC')],
    ]

    return dict(privacy=privacy, inputs=inputs, tools=tools, paths=paths)
