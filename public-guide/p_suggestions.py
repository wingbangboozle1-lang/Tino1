"""Suggestions for review: proposals, options, and a recommended path."""
from _gen import src, page, table, banner

PROPOSALS = [
    ('s01', 'S01', 'Remove the owner\'s exact bill figures from every tracked file',
     'Privacy', 'High', 'Low',
     'Replace the exact assessed values and tax bills used as examples in the repository\'s own checker and '
     'coordination notes with round-number illustrations. The live site never showed them, but a public repository is '
     'a public file store, and an exact assessed value identifies a parcel.',
     'Gate passes and a search of the whole tree for the exact figures returns nothing.',
     'Adopt', src('SCC-RATES')),
    ('s02', 'S02', 'Publish the de-identified numeric edition, and keep the no-figures guide',
     'Product', 'High', 'Medium',
     'The brief asks for numbers and projections; the published site had none. This edition publishes model outputs '
     'rounded to $10 and official amounts exactly, with every row sourced, and links the original no-figures guide '
     'rather than removing it.',
     'Eight published pages whose every table row links an official page, with a gate that fails on any unrounded '
     'household figure.',
     'Adopt', src('SCC-P19')),
    ('s03', 'S03', 'Keep the historical bill series out of the published product permanently',
     'Privacy', 'High', 'Low',
     'A year-by-year assessed value and tax pattern is a fingerprint even when each figure is rounded to $10. The '
     'series is not needed to answer any question on this site: the projection uses the current value only.',
     'No page contains a year-by-year bill series, and the flagged page records the decision.',
     'Adopt', src('RTC-51')),
    ('s04', 'S04', 'Obtain two written insurance quotes for each property',
     'Evidence', 'High', 'Medium',
     'Insurance is the largest unverified number in the analysis and the one most likely to be wrong. A ZIP-code '
     'average is not a price. Quotes must match the actual occupancy: homeowners for A if lived in, landlord for A if '
     'let, and a three-unit policy for B.',
     'Two quotes per property, recorded privately, with the premium and the exclusions.',
     'Adopt', src('CDI-RES')),
    ('s05', 'S05', 'Replace the owner\'s placeholder premiums and bills with the actual documents',
     'Evidence', 'High', 'Low',
     'Every utility and premium figure in the projection is an owner estimate. Replacing them with the last twelve '
     'months of bills would turn the projection from a scenario into an estimate without changing a single rule.',
     'Twelve months of bills for each property, entered privately, with the projection re-run.',
     'Adopt', src('CUP-WATER')),
    ('s06', 'S06', 'Read the solar interconnection agreement before relying on the electricity credit',
     'Evidence', 'Medium', 'Low',
     'The projection carries a net credit for fifty years. The net-metering tariff that creates it runs for twenty '
     'years from interconnection, and a system interconnected today would be on a different, less generous tariff. '
     'If the credit ends, electricity becomes a cost.',
     'The interconnection date and tariff are known, and the projection stops the credit at the right year.',
     'Adopt', src('CPUC-NEM')),
    ('s07', 'S07', 'Have the trust read by an estate attorney and get a written answer to Q01',
     'Decision', 'Critical', 'Medium',
     'The basis reset is the whole case for selling. If the home is outside the gross estate, the recommendation '
     'changes. No amount of modelling substitutes for reading the document.',
     'A written opinion that states whether the home is included and whether the inheritor takes a stepped-up basis.',
     'Adopt', src('IRS-INHERIT-FAQ')),
    ('s08', 'S08', 'Write a dated occupancy plan for Property A',
     'Decision', 'High', 'Low',
     'Proposition 19 relief requires the home to become the inheritor\'s principal residence within one year, and the '
     'exemption claim in the same year. Whether the plan is to move in, let it, or sell it, the occupancy intention '
     'has to be decided before the transfer, not after.',
     'A one-page plan with a date, filed privately with the trust documents.',
     'Adopt', src('RTC-63.2')),
    ('s09', 'S09', 'Model estate liquidity, not only estate tax',
     'Analysis', 'High', 'Medium',
     'The model computes the tax but not whether the estate can pay it in cash within nine months. For an estate '
     'that is mostly a house, that is the binding constraint. Add a liquidity line and an option to sell under time '
     'pressure.',
     'A liquidity projection by year, with the forced-sale cost shown separately.',
     'Adopt', src('IRS-ESTATE')),
    ('s10', 'S10', 'Add a second, independent property-value source',
     'Evidence', 'Medium', 'Low',
     'The market value of both homes is a single estimate. A second, independent source - an appraisal or a '
     'different index - would show how much of the result depends on that one number.',
     'A second value for each property, and the difference shown on the decision page.',
     'Hold', src('FHFA-SJ')),
    ('s11', 'S11', 'Re-index the Proposition 19 allowance automatically each February',
     'Maintenance', 'Medium', 'Low',
     'The statute re-indexes the allowance every second February 16. Hard-coding one year\'s figure would silently '
     'go stale. A documented update step, with the BOE letter as the trigger, prevents that.',
     'A checklist entry for each odd February, with the published figure recorded.',
     'Adopt', src('BOE-LTA-2025-009')),
    ('s12', 'S12', 'Show a confidence band instead of a single line',
     'Presentation', 'Medium', 'High',
     'The projection is a single path, which reads as more certain than it is. A band built from the 10th and 90th '
     'percentiles of the historical replays would communicate the uncertainty honestly.',
     'A chart and a table where every projection cell has a range, with the method stated.',
     'Hold', src('FHFA-SJ')),
    ('s13', 'S13', 'Add a printable one-page decision sheet',
     'Presentation', 'Low', 'Low',
     'The site is long. A single printable page with the recommendation, the four decisive questions and the numbers '
     'would make it usable in a meeting with an attorney or a broker.',
     'A one-page PDF-free printable page linked from the overview.',
     'Hold', src('IRS-ESTATE')),
    ('s14', 'S14', 'Do not add names, addresses, parcel numbers or account numbers, ever',
     'Privacy', 'Critical', 'Low',
     'The site uses placeholders for every person and property. Any future edit that adds a real address or parcel '
     'number would undo the whole privacy position and could not be recalled from caches.',
     'A gate that fails on an address, parcel-number or e-mail pattern, already enforced.',
     'Adopt', src('SCC-P19')),
    ('s15', 'S15', 'Keep the repository public but treat its history as exposed',
     'Privacy', 'High', 'Medium',
     'Excluding a file from the published site does not hide it in a public repository, and does not remove it from '
     'history, forks or caches. The honest options are to make the repository private or to rewrite history, and both '
     'are owner decisions with side effects.',
     'A recorded owner decision, either way, with the reason.',
     'Hold', src('IRS-ESTATE')),
]


def build():
    rows = []
    for sid, code, title, area, impact, effort, why, done, status, source in PROPOSALS:
        pill = 'ok' if status == 'Adopt' else ''
        rows.append(['<b>%s</b><br>%s' % (code, title), area, impact, effort, why, done,
                     '<span class="pill %s">%s</span>' % (pill, status), source])

    path = [
        ['Week 1', 'S01, S14', 'Close the exposure and keep it closed',
         'Remove the exact figures from tracked files; confirm the privacy gate fails on a re-introduction.', src('SCC-RATES')],
        ['Week 1-2', 'S07', 'Read the trust',
         'One attorney meeting, one written answer on Q01 and Q03. Everything else can wait; this cannot.', src('IRS-INHERIT-FAQ')],
        ['Week 2-4', 'S04, S05', 'Replace placeholders with documents',
         'Two insurance quotes per property, and twelve months of bills. This turns the projection into an estimate.', src('CDI-RES')],
        ['Week 4', 'S08, S06', 'Write the occupancy plan and read the solar agreement',
         'Two short documents that remove two of the four decisive unknowns.', src('RTC-63.2', 'CPUC-NEM')],
        ['Month 2', 'S09, S11', 'Improve the model where it is thin',
         'Add estate liquidity; add the annual re-index step for the Proposition 19 allowance.', src('IRS-ESTATE', 'BOE-LTA-2025-009')],
        ['Later', 'S10, S12, S13', 'Presentation and second sources',
         'Useful, not decisive. Hold until the evidence work is done.', src('FHFA-SJ')],
        ['Owner decision', 'S15', 'Decide what to do about repository history',
         'A privacy decision only the owner can make. This site states the trade-off and does not take the decision.', src('IRS-ESTATE')],
    ]

    body = ''.join([
        banner('<b>Nothing on this page has been implemented as a result of being listed here.</b> Each row is a '
               'proposal with a review status. The Adopt / Hold / Reject controls are browser-only: there is no form, '
               'nothing is stored, nothing is submitted, and no choice on this page changes any figure on this site.'),
        '<h2>Twelve site improvements, and why each one matters</h2>',
        table(['Proposal', 'Area', 'Impact', 'Effort', 'Why / what it fixes', 'Done when', 'Status', 'Official source'],
              rows, caption='Proposals for review - Adopt means recommended, not implemented'),
        '<h2>The recommended path, in order</h2>',
        '<p>If you review one thing, review this table. It sequences the proposals so that the cheapest and most '
        'decisive work happens first, and it defers the presentation work that cannot change an answer.</p>',
        table(['When', 'Proposals', 'What happens', 'Why in this order', 'Official source'],
              path, caption='A recommended implementation path - a proposal, not a schedule that has started'),
        '<h2>Record a review decision</h2>',
        '<p>These controls are for use during a review. They do not submit anything, they are not stored, and they '
        'reset when the page is reloaded. When a decision is made, record it in the project\'s coordination file so '
        'that the next change is deliberate.</p>',
        '<div class="path"><b>Your review, for each proposal above:</b><div class="budget">'
        '<label><input type="radio" name="d-s01" disabled> S01 Adopt / Hold / Reject</label>'
        '<label><input type="radio" name="d-s04" disabled> S04 Adopt / Hold / Reject</label>'
        '<label><input type="radio" name="d-s07" disabled> S07 Adopt / Hold / Reject</label>'
        '<label><input type="radio" name="d-s09" disabled> S09 Adopt / Hold / Reject</label>'
        '<label><input type="radio" name="d-s15" disabled> S15 Adopt / Hold / Reject</label>'
        '</div><p class="note">The controls are shown disabled on purpose: this static site cannot record a choice, '
        'and a control that looks live but silently discards the answer would be worse than no control. Copy the '
        'decision you want into an e-mail to your adviser, or into the coordination file.</p></div>',
        '<h2>What would make this site worse</h2>',
        table(['Tempting change', 'Why it would be a mistake', 'Official source'],
              [['Adding the exact house value and the exact bill history to make it "more useful"',
                'That is the fingerprint. The projection only needs the current value and the rate.', src('SCC-RATES')],
               ['Rounding harder - to the nearest $100 - to look safer',
                'It changes the arithmetic without changing the fingerprint, and it makes the tax calculations visibly wrong. Rounding is disclosure minimisation, not anonymisation.', src('RTC-51')],
               ['Removing the assumptions to make the page simpler',
                'The assumptions are the result. A number without its assumption is a claim about the future.', src('IRS-ESTATE')],
               ['Adding a live calculator that accepts the real address',
                'The site is public and static. A calculator that asks for an address would collect exactly the data this site refuses to hold.', src('SCC-RATES')],
               ['Filling in the unverified blanks with estimates so every cell has a number',
                'A labelled blank is information; an invented number is misinformation. The Flagged page exists for this reason.', src('CDI-RES')]],
              caption='Five changes that would look like improvements and would not be'),
    ])
    return page('suggestions.html', 'Suggestions for review',
                'Review before action / 10',
                'Proposals, a recommended order, and the changes that would look like improvements and would not be. '
                'Nothing here is implemented until it is chosen.',
                body)
