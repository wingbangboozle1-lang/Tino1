"""Sources and method."""
from _gen import M, P, S, neut, src, page, table, banner, pc, m, BUILD_DATE


def build():
    rows = []
    for key, (url, title, note) in S.items():
        rows.append([key, neut(title), note, 'official' if 'academic' not in note else 'academic',
                     '<a href="%s" rel="noopener noreferrer" target="_blank">%s</a>' % (url, key)])
    body = ''.join([
        banner('<b>How this edition was built.</b> A single Python generator reads one model output file and writes '
               'every page. The generator has no access to any document, address or bill: the only household inputs it '
               'can see are the model\'s rounded parameters and results. That is a structural privacy control, not a '
               'promise.'),
        '<h2>The source register</h2>',
        '<p>Every page this session opened directly is listed below with the date it was read. Sources described as '
               '"re-read by session da3f2b99" were read live in an earlier session today and are cited on that basis; '
               'they were not re-opened here.</p>',
        table(['Key', 'Page', 'What it was used for', 'Type', 'Link'], rows,
              caption='Every source used in this edition'),
        '<h2>How the numbers are produced</h2>',
        '<table class="num"><caption>The calculation chain</caption>'
        '<thead><tr><th scope="col">Step</th><th scope="col">What happens</th><th scope="col">Where it is checked</th><th scope="col">Official source</th>'
        '</tr></thead><tbody>'
        '<tr><td>1</td><td>A single model script holds every input, every formula and every assumption, including the '
        'property-tax cap, the transfer assessment, the estate calculation and the historical replays.</td>'
        '<td>Its own self-tests, including the Proposition 19 formula against the county assessor\'s worked example</td><td><a href="https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2" rel="noopener noreferrer" target="_blank">SCC-P19</a></td></tr>'
        '<tr><td>2</td><td>The model writes one JSON file containing every intermediate number.</td>'
        '<td>The build fails if a page needs a number the model does not produce</td><td><a href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax" rel="noopener noreferrer" target="_blank">IRS-ESTATE</a></td></tr>'
        '<tr><td>3</td><td>This generator formats every household amount to the nearest $10 and quotes statutory '
        'amounts exactly.</td><td>A gate fails on any household dollar figure that is not a multiple of $10</td><td><a href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51" rel="noopener noreferrer" target="_blank">RTC-51</a></td></tr>'
        '<tr><td>4</td><td>Every table row is checked for an https link to an official host.</td>'
        '<td>A row without one fails the build</td><td><a href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax" rel="noopener noreferrer" target="_blank">IRS-ESTATE</a></td></tr>'
        '<tr><td>5</td><td>Locality names and ZIP codes are replaced with Property A and Property B after generation.'
        '</td><td>A gate fails if any published page still names a city or a ZIP code</td><td><a href="https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2" rel="noopener noreferrer" target="_blank">SCC-P19</a></td></tr>'
        '<tr><td>6</td><td>The generated pages are compared byte for byte against a fresh build, and the published set '
        'is compared against an explicit allowlist.</td><td>Both run in continuous integration on every change</td><td><a href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax" rel="noopener noreferrer" target="_blank">IRS-ESTATE</a></td></tr>'
        '</tbody></table>',
        '<h2>The assumptions, in one place</h2>',
        table(['Assumption', 'Value used', 'Why this value', 'Official source'],
              [['Growth of both housing markets', pc(P['g_cup']) + ' a year', 'close to, but below, the long-run real average on the official index; an assumption', src('FHFA-SJ')],
               ['Inflation', pc(P['infl']) + ' a year', 'above the recent average and below the 1976-2025 average', src('BLS-CPI')],
               ['Stock-market return', pc(P['r_stock']) + ' a year', 'an academic long-run average, not a forecast', src('DAMODARAN')],
               ['Short-term Treasury return', pc(P['r_bill']) + ' a year', 'used for the alternative-to-stocks case', src('DAMODARAN')],
               ['Property-tax annual factor', 'lesser of inflation or 2%', 'statutory cap, not an assumption', src('RTC-51')],
               ['Property B rent growth', '60% of inflation for covered units', 'the local rent board sets an annual percentage; the model uses a rule-shaped proxy', src('SF-RENT')],
               ['Vacancy allowance', pc(P['vacancy']), 'a long-run allowance for a three-unit building', src('HUD-SAFMR')],
               ['Management allowance', pc(P['mgmt']), 'the cost of not managing the property yourself', src('CDI-RES')],
               ['Selling cost', pc(P['sell_cost']), 'a standard allowance including commission and closing costs', src('IRS-TC409')],
               ['Property A rent', m(P['cup_rent_month_3br']) + ' a month', 'the HUD small-area fair-market rent for a three-bedroom in the same ZIP code', src('HUD-SAFMR')],
               ['Federal exclusion after 2027', 'indexed', 'statutory indexing; the amount itself is an assumption', src('RP-2026-35')],
               ['Property A value today', m(P['cup_value']), 'an estimate, not an appraisal', src('FHFA-SJ')],
               ['Property B value today', m(P['sf_value']), 'an estimate, not an appraisal', src('FHFA-SJ')]],
              caption='Every assumption that moves a number'),
        '<h2>What was verified directly, and what was not</h2>',
        '<div class="split"><div>',
        '<h3>Verified on %s, in this session</h3>' % BUILD_DATE,
        '<ul>',
        '<li>The federal estate-tax filing-threshold table, including $15,000,000 for 2026.</li>',
        '<li>The 2027 inflation adjustments, including a $15,480,000 exclusion and a $20,000 annual gift exclusion, '
        'read from the revenue procedure itself rather than from a summary.</li>',
        '<li>That California has no estate or inheritance tax for deaths on or after 1 January 2005.</li>',
        '<li>The Proposition 19 comparison and the intergenerational transfer FAQ, including the three-year claim, '
        'the one-year occupancy and the continual-use rule.</li>',
        '<li>The value cap of $1,044,586 for transfers through 15 February 2027.</li>',
        '<li>The parent-child worked example published by the assessor, which the model reproduces.</li>',
        '<li>The homeowners\' exemption and its filing deadline.</li>',
        '<li>The statutory 2% cap and the California consumer price index as the factor.</li>',
        '<li>The county rate book: 1% general levy plus voter-approved charges, and the instalment deadlines.</li>',
        '<li>The city secured rate for fiscal 2026-27: 1.18162182%.</li>',
        '<li>The 1.6% allowable rent increase for covered units from 1 March 2026.</li>',
        '<li>Rent control coverage for units built on or before 13 June 1979.</li>',
        '<li>The Statewide rent cap under the civil code.</li>',
        '<li>HUD\'s FY2026 small-area fair-market rents for both ZIP codes, at every bedroom size.</li>',
        '<li>The net-metering tariff structure, including the 20-year NEM 2.0 transition period and the fixed charge.</li>',
        '<li>The insurance regulator\'s residential guide, including the exclusions.</li>',
        '<li>The federal budget office\'s inflation path, as context for the baseline.</li>',
        '<li>The Federal Reserve History account of the Great Inflation.</li>',
        '<li>That the city\'s empty-homes tax is not being enforced after the appellate decision.</li>',
        '<li>The trust notification deadline and the basis rule for inherited property.</li>',
        '</ul>',
        '</div><div>',
        '<h3>Not verified, and said so</h3>',
        '<ul>',
        '<li>Any insurance premium. No quote was obtained; all premiums are placeholders.</li>',
        '<li>The current assessed values and the bill history. Supplied by the owner, withheld from this edition by '
        'design, and not independently confirmed.</li>',
        '<li>The market value of either property. An estimate, not an appraisal.</li>',
        '<li>The rent for Property A. A published benchmark, not a valuation.</li>',
        '<li>The solar interconnection terms. The agreement was not read.</li>',
        '<li>Estate and legal fees. Not modelled.</li>',
        '<li>The future Proposition 19 allowance. Not published yet.</li>',
        '<li>Any future tax law. Only the law in force is stated.</li>',
        '</ul>',
        '<h3>Where the earlier editions are</h3>',
        '<p>Earlier editions are retained in the repository and are not republished here. The original no-figures '
        'guide remains live and is linked from the front door; this edition is additive.</p>',
        '</div></div>',
        banner('<b>The professional help this site is not.</b> Nothing here is legal, tax, investment or insurance '
               'advice. The site prepares the questions and the arithmetic for a licensed estate attorney, a tax '
               'adviser and an insurance broker, and it is written so that each of them can check a number rather '
               'than take it on trust.', 'warn'),
    ])
    return page('sources.html', 'Sources and method',
                'How this was checked / 12',
                'Every page read, every assumption used, what was verified directly and what was not - so that any '
                'number on this site can be traced or rejected.',
                body)
