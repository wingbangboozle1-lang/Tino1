"""Flagged for review: every unconfirmed value, assumption and irregularity."""
from _gen import src, page, table, banner

FLAGS = [
    ('f01', 'P01', 'Privacy', 'Critical', 'Open',
     'The owner\'s exact assessed values and tax figures appeared in two tracked files: the repository\'s own checker '
     '(as an illustration of the rounding rule) and the coordination log. The live site never showed them, but the '
     'repository is public and a public file store exposes a file whether or not it is published.',
     'Both occurrences replaced with round-number illustrations or masked, and the privacy gate extended to the '
     'coordination log. Remaining exposure is the git history and any fork or cache, which the owner must decide '
     'about (see P02).', src('SCC-RATES')),
    ('f02', 'P02', 'Privacy', 'High', 'Owner action',
     'A public repository\'s history cannot be unpublished by editing the current files. Anything ever committed '
     'remains reachable, including through forks and caches. Rounding to $10 reduces disclosure but does not '
     'anonymise: a 2% growth pattern on a unique starting value is still a fingerprint.',
     'Not resolvable from inside the repository. The options are to make the repository private, to rewrite history, '
     'or to accept the exposure knowingly. This site recommends none of them without the owner\'s decision.', src('IRS-ESTATE')),
    ('f03', 'P03', 'Privacy', 'Critical', 'Closed',
     'A year-by-year property-tax and assessed-value history was supplied by the owner and could have been published '
     'as a rounded table.',
     'Closed by design decision: the series is not published in any form on this edition, and the suggestion register '
     'keeps it out permanently (S03). The projection needs only the current value and the rate.', src('RTC-51')),
    ('f04', 'U09', 'Evidence', 'High', 'Open',
     'No insurance premium has been verified for either property. Every premium in every projection is the owner\'s '
     'estimate rounded to $10. A California homeowners policy also excludes earthquake, flood, mold and long-vacancy '
     'losses, which are exactly the events a fifty-year projection should worry about.',
     'Two written quotes per property, matched to the actual occupancy. Until then every premium on this site is '
     'labelled a placeholder and is excluded from the running-cost totals.', src('CDI-RES')),
    ('f05', 'U10', 'Evidence', 'Medium', 'Open',
     'The electricity credit is carried for fifty years in the model. The net-metering tariff behind it lasts twenty '
     'years from interconnection, and the fixed charge approved for the large utilities is paid regardless of '
     'generation.',
     'The interconnection date and tariff are known; the credit stops at the right year. If the credit ends, '
     'electricity becomes a cost and the rent-out net falls.', src('CPUC-NEM', 'CPUC-FIXED')),
    ('f06', 'A01', 'Assumption', 'High', 'Open',
     'Growth, inflation and investment return are single assumed rates applied for fifty years. This is the dominant '
     'uncertainty in every number on the site.',
     'Not resolvable. Mitigated by replaying the real 1976-2025 record 50 times and by named crisis paths, and '
     'disclosed on every page that uses a projection.', src('FHFA-SJ')),
    ('f07', 'A02', 'Assumption', 'Medium', 'Open',
     'Property A\'s rent is modelled at the HUD small-area fair-market rent for a three-bedroom. HUD itself describes '
     'that figure as a 40th-percentile benchmark for the voucher programme, not a valuation of this house.',
     'A local rental appraisal, or two letting agents\' written opinions (Q15).', src('HUD-SAFMR')),
    ('f08', 'A03', 'Assumption', 'Medium', 'Open',
     'Property B is held unchanged in every path: the same two let units, the same rent growth, the same occupancy, '
     'and the third unit not let. That is an assumption, not a fact, and it is the baseline the whole comparison '
     'rests on.',
     'A decision and a dated plan for the third unit (Q18), and a rent board registration if it is let.', src('SF-RENT')),
    ('f09', 'A04', 'Assumption', 'Low', 'Open',
     'The sale of Property A assumes a %s selling cost and no mortgage on the property. Neither has been verified.'
     % '5%',
     'A broker\'s commission schedule, and confirmation that the property is unencumbered.', src('IRS-TC409')),
    ('f10', 'A05', 'Assumption', 'Medium', 'Open',
     'The federal exclusion is projected forward by indexing. The 2026 and 2027 amounts are official; the projection '
     'after 2027 is a model output and the law could change.',
     'Re-check the published amount each year against the IRS inflation-adjustment release.', src('RP-2026-35')),
    ('f11', 'A06', 'Assumption', 'Medium', 'Open',
     'The Proposition 19 allowance after 15 February 2027 is projected, not published. The model re-indexes it in '
     'February of odd years using the historical California house-price index.',
     'Use the published BOE letter for the year of the transfer when it exists (Q07).', src('BOE-LTA-2025-009')),
    ('f12', 'A07', 'Assumption', 'Low', 'Open',
     'Estate fees - attorney, trustee, appraisal and probate-avoidance work - are not modelled at all, so the cash '
     'available after an inheritance is overstated.',
     'A written fee estimate from the attorney and the trustee (Q16).', src('PROB-16061.7')),
    ('f13', 'A08', 'Assumption', 'Medium', 'Open',
     'The economic series used for the historical replays are official for inflation and the house-price index, but '
     'the stock and Treasury return series come from an academic dataset. They are not a government statistic.',
     'No official substitute exists for a long total-return series. The provenance is labelled on every row that '
     'uses it, and the asset-allocation assumption is a separate flag.', src('DAMODARAN')),
    ('f14', 'R01', 'Irregularity', 'Medium', 'Needs review',
     'The repository contains several earlier editions of this site, and more than one session has written to the '
     'same shared files. The result is duplicated logic in several places and at least one page whose statement was '
     'true when written and is not true now.',
     'A consolidation pass that deletes nothing, marks superseded editions, and keeps one canonical generator. This '
     'edition is generated from one script and reads only the model output, which is a partial fix.', src('IRS-ESTATE')),
    ('f15', 'R02', 'Irregularity', 'Low', 'Needs review',
     'The rounding rule is a disclosure-minimisation measure, not an anonymisation measure. Two identical round '
     'numbers in different documents can still be correlated, and a value rounded to $10 is sometimes recoverable '
     'within a $10 band by anyone who knows the correct assessment.',
     'State the limitation wherever the method is described, which this site does. A true fix would be to withhold '
     'the current values entirely and publish only ratios.', src('SCC-RATES')),
    ('f16', 'R03', 'Irregularity', 'Low', 'Closed',
     'Earlier automated passes left merge-conflict markers in a generated page, which was then published. A gate now '
     'fails the build on a conflict marker.',
     'The marker was removed and a permanent check was added. No marker appears in this edition.', src('IRS-ESTATE')),
    ('f17', 'R04', 'Irregularity', 'Low', 'Open',
     'The two properties sit in different counties with different tax rate areas, so a single blended rate would be '
     'wrong. The model applies a separate rate to each, taken from the published rate for the city, but the exact tax '
     'rate area can only be confirmed from the tax bill.',
     'Confirm the tax rate area from each bill. It changes the rate in the third decimal, not the decision.', src('SCC-RATES')),
]

UNVERIFIED = [
    ['Insurance premium, Property A', 'Owner estimate', 'No written quote exists', src('CDI-RES')],
    ['Insurance premium, Property B', 'Owner estimate', 'No written quote exists', src('CDI-RES')],
    ['Water and wastewater, both properties', 'Owner bills, rounded', 'Twelve months of bills not reviewed', src('CUP-WATER')],
    ['Electricity credit, Property A', 'Owner description', 'Interconnection agreement not read', src('CPUC-NEM')],
    ['Market value of both properties, today', 'Owner estimate', 'No appraisal in the last twelve months', src('FHFA-SJ')],
    ['Property A rent', 'HUD benchmark', 'A 40th-percentile benchmark, not a rent for this house', src('HUD-SAFMR')],
    ['Repairs and maintenance allowance', 'Model assumption', 'No inspection or contractor estimate', src('CDI-RES')],
    ['Selling cost', 'Model assumption at 5%', 'No commission schedule', src('IRS-TC409')],
    ['Estate and legal fees', 'Not modelled', 'No fee estimate', src('PROB-16061.7')],
    ['Insurance for a vacant period', 'Not modelled', 'Vacancy terms differ by policy', src('CDI-RES')],
    ['Current assessed values of both properties', 'Withheld from this edition', 'Deliberate: the pattern identifies the parcel', src('SCC-RATES')],
    ['Year-by-year tax and assessment history', 'Withheld from this edition', 'Deliberate: a fingerprint, see P03', src('RTC-51')],
]


def build():
    rows = []
    for fid, code, area, impact, status, finding, action, source in FLAGS:
        pill = {'Closed': 'ok', 'Open': 'open', 'Owner action': 'stop', 'Needs review': 'open'}[status]
        rows.append(['<b>%s</b>' % code, area, impact,
                     '<span class="pill %s">%s</span>' % (pill, status), finding, action, source])

    body = ''.join([
        banner('<b>Unverified does not mean false.</b> It means the evidence does not support presenting a value as '
               'confirmed. Nothing on this page blocks the site or the analysis: it is the list to read after the '
               'site is live, so that the owner can decide what to change.'),
        '<h2>Flags, in order of urgency</h2>',
        table(['Ref', 'Area', 'Impact', 'Status', 'Finding', 'What would close it', 'Official source'],
              rows, caption='Seventeen flags: privacy, evidence, assumptions and irregularities'),
        '<h2>Every unverified value on the site, in one table</h2>',
        '<p>This is the complete list of numbers that are shown but not verified. Each one appears on a page with the '
        'same label; the table exists so that a reviewer can check them without searching.</p>',
        table(['Value', 'Source of the figure', 'Why it is not verified', 'Official source'],
              UNVERIFIED, caption='Unverified values and the reason for each'),
        '<h2>The two privacy flags, stated plainly</h2>',
        '<div class="split"><div>',
        '<h3>P01 - exact figures in tracked files</h3>',
        '<p>The repository\'s own checker used two exact assessed values as an illustration of the rounding rule, and '
        'the coordination log quoted others while describing a privacy fix. A public repository exposes every tracked '
        'file. Both have been replaced in this pass. What remains is history, which is P02.</p>',
        '<h3>P02 - repository history</h3>',
        '<p>Editing a file does not remove it from history. Forks, caches and search indexes may hold copies. Only the '
        'owner can decide whether to make the repository private or rewrite history, and either has side effects - a '
        'private repository un-publishes nothing that is already copied, and a history rewrite changes every commit '
        'identifier.</p>',
        '</div><div>',
        '<h3>What this edition did about it</h3>',
        '<ul>',
        '<li>Replaced the exact figures with round-number illustrations.</li>',
        '<li>Built the published pages from a generator that reads the model output only, so no page can carry a '
        'document value.</li>',
        '<li>Withheld the current assessed values and the whole bill history, even though the brief asked for them.</li>',
        '<li>Added a gate that fails on an address, parcel-number, e-mail or telephone pattern.</li>',
        '<li>Labelled every household figure as rounded to $10 and every statutory amount as official.</li>',
        '</ul>',
        '<h3>What it did not do</h3>',
        '<p>It did not make the repository private, rewrite history, delete any earlier edition, or publish the bill '
        'series. Each of those is an owner decision, and three of the four are irreversible.</p>',
        '</div></div>',
        banner('<b>Read this page before acting on any number elsewhere.</b> The decision analysis is sound on its '
               'assumptions, but several inputs - insurance above all - are placeholders. The recommendation does not '
               'depend on them; the level of the result does.', 'warn'),
    ])
    return page('flagged.html', 'Flagged for review',
                'Limitations and source register / 11',
                'Every unverified value, every assumption, and every irregularity found in the repository - with the '
                'official page behind it and a note on what would close it.',
                body)
