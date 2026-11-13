"""The inheritance process, step by step."""
from _gen import (B, P, T, Y0, src, page, table, banner, m)


def build():
    steps = [
        ['1', 'Now, and every year until the transfer',
         'Read the trust and keep it current. Confirm who the trustee is, whether the home is a trust asset, who the '
         'beneficiaries are, and whether the transferor holds a retained interest.',
         'Planning action. A trust is not a tax exemption, and a trust that does not hold the home transfers nothing.',
         src('IRS-ESTATE')],
        ['2', 'Now: ask whether the home will be in the gross estate',
         'This is the single fact that decides the case for selling. If the home is included, the basis resets at '
         'death. If it is outside the estate, the inheritor takes the transferor\'s basis and selling loses its '
         'advantage.',
         'Not a filing deadline. It is a question for the estate attorney, answered from the trust document.',
         src('IRS-INHERIT-FAQ')],
        ['3', 'At death: the trustee takes control',
         'The trustee secures the property, insures it, collects the documents and keeps the records. Contact the '
         'insurer about occupancy: a policy can exclude a loss after a long vacancy.',
         'Practical safeguard. California does not publish a single statutory deadline for this step; the policy '
         'wording controls.', src('CDI-RES')],
        ['4', 'Within 60 days: notification by the trustee',
         'The trustee serves the statutory notification on each beneficiary and each heir of the deceased settlor.',
         'Statutory. The notification must be served not later than 60 days after the event, with a defined rule '
         'when a trustee is appointed late.', src('PROB-16061.7')],
        ['5', 'Before the first property-tax instalment: confirm the assessed value and the roll',
         'Ask the county assessor for the current assessed value and confirm the parcel is on the secured roll. The '
         'value you inherit is the starting point for the Proposition 19 calculation.',
         'Deadlines for the secured roll are set by the county: the first instalment is delinquent after 10 December, '
         'the second after 10 April.', src('SCC-RATES')],
        ['6', 'Within 1 year: file BOE-266, the homeowners\' exemption',
         'The exemption reduces taxable value and is also an eligibility condition for the intergenerational '
         'exclusion. File it even if the plan is to sell, because it is what proves the home is the inheritor\'s '
         'principal residence.',
         'Statutory. The claim must be filed within one year of the transfer for the Proposition 19 exclusion to '
         'apply. Filing late can forfeit the relief.', src('BOE-HOX', 'RTC-63.2')],
        ['7', 'Within 1 year: the home must actually become the principal residence',
         'The transferee must occupy the home as a principal residence within one year of the transfer. Occupancy is '
         'a fact the assessor can check; a claim alone does not establish it.',
         'Statutory condition of the exclusion, not a filing step.', src('RTC-63.2')],
        ['8', 'Within 3 years: file BOE-19-P, the intergenerational transfer claim',
         'The claim for the parent-child exclusion. It is not a public document. The claim asks for the facts that '
         'establish eligibility: the relationship, the transferor\'s residence, the transferee\'s occupancy and the '
         'value test.',
         'Statutory. The claim must be filed within three years of the transfer, or before the property is '
         'transferred to a third party, whichever is earlier.', src('BOE-LTA-2026-026', 'SCC-P19')],
        ['9', 'When the assessor rules: check the new taxable value',
         'The new taxable value is the prior factored base year value plus the amount by which market value exceeds '
         'the prior value plus the allowance. If the assessor\'s figure differs from the calculation, appeal it.',
         'Statutory formula. The allowance is $1,044,586 for transfers from 16 February 2025 through 15 February '
         '2027; the next adjustment is published in February 2027.', src('BOE-LTA-2025-009', 'RTC-63.2')],
        ['10', 'If the property is sold: record the deed and pay the transfer tax',
         'The sale is recorded at the county recorder. The documentary transfer tax is paid at recording.',
         'County process. The recorder publishes what is required for recording.', src('SCC-P19')],
        ['11', 'By the tax deadline: report the sale on the income-tax return',
         'Report the sale on Schedule D and Form 8949 if a return is required. The basis is the date-of-death value, '
         'so the gain is small if the sale follows the transfer closely.',
         'Federal. The return is due on the normal filing date for the year of sale; estimated tax may apply.',
         src('IRS-INHERIT-FAQ', 'IRS-TC409')],
        ['12', 'If the estate is large: the executor files Form 706',
         'A federal estate-tax return is required if the gross estate exceeds the filing threshold for the year of '
         'death. Portability of a deceased spouse\'s unused exclusion requires a timely return.',
         'Federal. The 2026 threshold is $15,000,000 and the 2027 figure is $15,480,000; California has no separate '
         'estate or inheritance tax for deaths after 2004.', src('IRS-ESTATE', 'RP-2026-35', 'SCO-ESTATE')],
        ['13', 'If the inheritor moves in: keep the exclusion alive',
         'The exclusion is removed if the home stops being the transferee\'s principal residence or the exemption '
         'lapses. Moving out and renting the home can trigger a new base year value.',
         'Statutory. This is why "move in, then rent it later" is a different plan from "rent it now".', src('RTC-63.2')],
    ]
    rows = [s[:4] + [s[4]] for s in steps]
    body = ''.join([
        banner('<b>This is a sequence, not legal advice.</b> The order matters because three of the steps have '
               'statutory clocks that run from the same event, and one of them - the homeowners\' exemption - is also '
               'an eligibility condition for the other. Missing it does not just cost an exemption; it can cost the '
               'whole intergenerational relief.'),
        '<h2>Step by step from trust to decision</h2>',
        table(['#', 'When', 'What happens', 'Why it matters or what the clock is', 'Official source'],
              rows, caption='Thirteen steps, with the authoritative page for each', cls='',
              note='Dates are the statutory deadlines where a statute sets one. Where no statute sets a deadline, the '
                   'table says so rather than inventing one.'),
        '<h2>The three clocks that matter</h2>',
        '<div class="split"><div>',
        '<h3>60 days - tell the beneficiaries</h3>',
        '<p>The trustee must serve the statutory notification within 60 days of the event that makes the trust '
        'irrevocable, or of a change of trustee. This is the first clock and it is about information, not tax.</p>',
        '<h3>1 year - the exemption and the occupancy</h3>',
        '<p>Two conditions run on the same one-year clock: the transferee must file for the homeowners\' exemption, '
        'and the home must become the transferee\'s principal residence. Both are conditions of the Proposition 19 '
        'exclusion, not optional extras.</p>',
        '</div><div>',
        '<h3>3 years - the transfer claim</h3>',
        '<p>The BOE-19-P claim must be filed within three years of the transfer, or before a transfer to a third '
        'party if that comes first. Selling the home before filing can end the relief.</p>',
        '<h3>What this means for the plan</h3>',
        '<p>The recommendation is to sell within the year. The process is consistent with that: the claim and the '
        'exemption are filed, the assessor rules, and the sale follows. What the plan must not do is sell first and '
        'file later, because the claim is a condition of the relief and not a formality.</p>',
        '</div></div>',
        '<h2>What the inheritor needs to collect</h2>',
        table(['Document', 'Who holds it', 'Why it is needed', 'Official source'],
              [['The trust and every amendment', 'The transferor or the attorney', 'Decides inclusion, basis and who can act', src('IRS-ESTATE')],
               ['The deed and the vesting', 'County recorder', 'Shows how title is held and what interest passes', src('SCC-P19')],
               ['The current property-tax bill', 'The transferor', 'Shows the assessed value and the base year', src('SCC-RATES')],
               ['The homeowners\' exemption history', 'County assessor', 'Needed for the one-year condition', src('BOE-HOX')],
               ['The insurance policy and its exclusions', 'The transferor', 'Occupancy and vacancy terms control cover', src('CDI-RES')],
               ['The solar interconnection agreement', 'The transferor', 'Sets the tariff period behind the electricity credit', src('CPUC-NEM')],
               ['The prior year tax returns of the estate', 'The executor', 'Needed for the gross-estate figure and portability', src('IRS-ESTATE')]],
              caption='The document set that answers most of the open questions', cls='',
              note='Collect these privately. Do not upload them to this site or add them to this repository: it is public.'),
        banner('<b>Do not put any of these documents in this repository.</b> It is a public repository. It is also not a '
               'record-keeping system: an access-controlled folder with a documented backup is the right place for '
               'deeds, statements and tax returns.', 'stop'),
    ])
    return page('process.html', 'From trust to decision',
                'Practical roadmap / 05',
                'Every step from reading the trust to recording the deed, in order, with the statutory clock that '
                'governs each one.',
                body)
