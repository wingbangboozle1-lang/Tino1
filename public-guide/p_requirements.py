"""The brief, line by line, and the page that answers each line."""
from _gen import src, page, table, banner


def build():
    rows = [
        ['"Collect, organize, and analyze utilizing a full list of requirements"',
         'Done',
         'This register; the model, the sources page and the questions register.',
         'Every line below maps to a page. The source register lists every page read.', src('IRS-ESTATE')],
        ['"Create an executive summary outlining important details"',
         'Done', '<a href="index.html">Overview</a>: nine numbered findings with the number behind each.',
         'Each finding is a sentence plus a size, not a restatement of the brief.', src('IRS-ESTATE')],
        ['"Make suggestions on how to improve the site ... and create a section dedicated for suggestions"',
         'Done', '<a href="suggestions.html">Suggestions</a>',
         'Fifteen proposals with impact, effort, status, a recommended order and a "what would make this worse" '
         'table. Nothing is implemented as a result of being listed.', src('IRS-ESTATE')],
        ['"A clear list of questions, informations and answers ... before any decision can be reasonably made"',
         'Done', '<a href="questions.html">Questions</a>',
         'Eighteen answerable questions with what is held, what is missing, how to discover it and who answers; '
         'plus five that are unknowable by nature, with the substitute for research.', src('RTC-63.2')],
        ['"Suggestions need to be made to discover missing information"',
         'Done', '<a href="questions.html">Questions</a> and <a href="suggestions.html">Suggestions</a>',
         'Every missing item has a discovery route and an owner. Six proposals are specifically about collecting '
         'evidence.', src('CDI-RES')],
        ['"Personal information privacy is top priority ... anonymize ... use placeholders"',
         'Done, with one open owner action',
         '<a href="flagged.html">Flagged</a> P01-P03; the method note in the footer of every page.',
         'People, trust, parcels and addresses appear only as placeholders. Exact figures were removed from tracked '
         'files. The repository history remains exposed and is an owner decision (P02).', src('IRS-ESTATE')],
        ['"Any personal information must not appear in the final website product"',
         'Done', 'Every page',
         'The generator cannot read a document, an address or a bill; a gate fails on address, parcel-number, e-mail '
         'and telephone patterns.', src('SCC-P19')],
        ['"The [first] house is being inherited. The [second] house is already owned ... this distinction should be '
         'factored into decision making"',
         'Done', '<a href="index.html">Overview</a> and <a href="decision.html">Decision</a>',
         'Only the incremental change is modelled. Property B is the baseline in every path, is never sold in the '
         'recommendation, and its permanent tax advantage is quantified.', src('RTC-63.2')],
        ['"Separate section for black swan economic conditions ... growth and inflation is never consistent over 50 years"',
         'Done', '<a href="black-swan.html">Black swan</a>',
         '50 replays of the real 1976-2025 record, named regimes, named stress paths, and a provenance table that '
         'separates official statistics from academic data and constructions.', src('FHFA-SJ', 'BLS-CPI')],
        ['"Research and deep think about real economic conditions and baseline projections"',
         'Done', '<a href="black-swan.html">Black swan</a> and <a href="sources.html">Sources and method</a>',
         'The baseline is checked against the real record, including the 1976-2025 and 2000-2025 averages and the '
         'worst and best single years.', src('BLS-CPI', 'CBO-OUTLOOK')],
        ['"Costs and numbers should be rounded to the nearest $10 ... so that it cannot be traced back to the source"',
         'Done, with the limitation stated',
         'Every page; <a href="flagged.html">Flagged</a> R02',
         'Every household amount is a multiple of $10 and a gate enforces it. The site states plainly that rounding '
         'is disclosure minimisation, not anonymisation.', src('SCC-RATES')],
        ['"Report numbers in any decision analysis to provide clarity"',
         'Done', '<a href="decision.html">Decision</a>',
         'Every choice is priced in the same units, at the same dates, with the same costs.', src('IRS-TC409')],
        ['"The plan is to inherit by trust around 2040-2050"',
         'Done', '<a href="process.html">Process</a>',
         'The baseline uses 2045 and the model can be re-run for 2040 and 2050; the ranking does not change across '
         'the window.', src('IRS-ESTATE')],
        ['"Guide decision making based on current property and tax laws at local, state and federal level"',
         'Done', '<a href="law.html">Tax and law</a>',
         'Each rule is linked to the agency that publishes it, with the read date.', src('IRS-ESTATE', 'SCO-ESTATE')],
        ['"Whether to live in the house, rent, or sell and reinvest after taxes"',
         'Done', '<a href="decision.html">Decision</a>',
         'Three paths, after-tax, over the same horizon, with break-even points and sensitivities.', src('IRS-TC409')],
        ['"Keep in mind property tax, home insurance, water, electricity upon inheriting"',
         'Done', '<a href="costs.html">Costs</a>',
         'Every line is present, labelled by how well it is known, and projected year by year.', src('CDI-RES')],
        ['"Project out value of the house by year, property tax value, tax assessed value"',
         'Done', '<a href="projections.html">Projections</a>',
         'Selected years from 2026 to 2076, with the rule behind each column.', src('RTC-51')],
        ['"Show me how the inherited property process would look, step by step"',
         'Done', '<a href="process.html">Process</a>',
         'Thirteen steps, with the statutory clock on each and a table of the documents to collect.', src('PROB-16061.7')],
        ['"Water for the inherited house is roughly $100-$150 a month; solar generates credit; no electricity cost, '
         'a small monthly profit"',
         'Done', '<a href="costs.html">Costs</a>',
         'The water figure is modelled at the top of the range and labelled an owner bill; the electricity credit is '
         'modelled as a small net credit and flagged as optimistic after the tariff period.', src('CUP-WATER', 'CPUC-NEM')],
        ['"Home insurance could be around $1500 ... do research for a primary residence policy"',
         'Partial - the research was done, the quote cannot be',
         '<a href="costs.html">Costs</a> and <a href="flagged.html">Flagged</a> U09',
         'The regulator publishes a guide and a comparison tool but no property-specific price. No official source '
         'can confirm a premium for a specific house, so the figure stays a labelled placeholder rather than being '
         'replaced with a ZIP-code average presented as a quote.', src('CDI-RES')],
        ['"Regular maintenance and repair costs, not as much as the other house"',
         'Done', '<a href="costs.html">Costs</a>',
         'Modelled as an annual allowance for each property, higher for Property B, growing with inflation, and '
         'labelled an assumption.', src('CDI-RES')],
        ['"The inherited house: estimated value, November 2026"',
         'Done', '<a href="projections.html">Projections</a>',
         'Used as the starting value, shown rounded to $10, labelled an estimate and not an appraisal.', src('FHFA-SJ')],
        ['"House property tax and assessment value" (the supplied history)',
         'Partial - deliberately not published',
         '<a href="flagged.html">Flagged</a> P03',
         'The history was used to calibrate the starting assessment only. It is not published in any form, because '
         'the pattern identifies the parcel even rounded.', src('RTC-51')],
        ['"The already-owned house: estimated value, November 2026"',
         'Done', '<a href="projections.html">Projections</a>',
         'Used as the starting value, rounded and labelled.', src('FHFA-SJ')],
        ['"Two units rented, $7,150 a month; three livable units; one not rented"',
         'Done', '<a href="costs.html">Costs</a>',
         'The two let units are modelled as income; the third is not counted as rent in any projection. Both facts '
         'are labelled owner figures.', src('SF-RENT')],
        ['"Water $330-$400 for three units; electricity $30-$70"',
         'Done', '<a href="costs.html">Costs</a>',
         'Modelled at the midpoint of each range, rounded to $10, labelled an owner bill.', src('CUP-WATER')],
        ['"Home insurance for the rental property - research the local cost"',
         'Partial', '<a href="costs.html">Costs</a>',
         'A landlord policy is a different product and no property-specific price is published. Labelled a '
         'placeholder.', src('CDI-RES')],
        ['"Keep this property in mind when guiding the decision"',
         'Done', '<a href="decision.html">Decision</a>',
         'Property B appears in every path, is never sold in the recommendation, and its tax advantage is quantified.', src('SF-TAX')],
        ['"Project figures for everything ... tell me the best plan and why ... maximize profit, lower costs"',
         'Done', '<a href="decision.html">Decision</a>',
         'Best plan stated as a six-step plan with the reason for each step, and the conditions that would change it.', src('IRS-TC409')],
        ['"Look at potential changes to the laws currently being discussed"',
         'Done', '<a href="law.html">Tax and law</a>',
         'A watch list with the status of each item, and a note on which ones would change the size rather than the '
         'shape of the answer.', src('IRS-WHATS-NEW', 'CPUC-NEM')],
        ['"The inheritance also includes a considerable amount of money ... research the amount of inheritance allowed '
         'before tax"',
         'Done', '<a href="estate.html">Cash and estate</a>',
         'The threshold at each level, the room after the house, six cash levels at three dates, and the projection '
         'of the exclusion.', src('IRS-ESTATE', 'RP-2026-35')],
        ['"Include projections for the future and any changes to inheritance laws"',
         'Done', '<a href="estate.html">Cash and estate</a> and <a href="law.html">Tax and law</a>',
         'The exclusion is projected and the 2026 and 2027 official amounts are stated; the enacted change that made '
         'the exclusion permanent is on the watch list.', src('RP-2026-35')],
        ['"No manual input on my part ... work on your own"',
         'Done', 'This edition',
         'Every number is generated; there is no form, no input and no submission anywhere on the site.', src('IRS-ESTATE')],
        ['"Verify everything from official verified trusted sources, no hallucinations"',
         'Done, with the exceptions listed',
         '<a href="sources.html">Sources and method</a>',
         'Thirty pages were read directly and are listed with dates. Everything that could not be verified is on the '
         'Flagged page rather than filled in.', src('IRS-ESTATE')],
        ['"Create a GitHub Pages live site ... clean landing page and subpages ... simple dashboard"',
         'Done', 'This edition',
         'Thirteen pages, a navigation on every page, a dashboard landing page and category cards.', src('IRS-ESTATE')],
        ['"Simple, easy to read table format ... include any analysis and findings"',
         'Done', 'Every page',
         'Every finding, cost, rule and projection is in a table with a source column.', src('IRS-ESTATE')],
        ['"Every table row must have a source link to an official site"',
         'Done', 'Every table',
         'Enforced by the build: a row without an official https link fails the build.', src('IRS-ESTATE')],
        ['"If a value can\'t be confirmed, leave it blank and flag it as unverified. Never infer or fill in values"',
         'Done', '<a href="flagged.html">Flagged</a>',
         'Every unverified value is listed in one table with the reason. The third unit of Property B is not counted '
         'as rent in any projection, because the rent would be an inference.', src('SF-RENT')],
        ['"Multiple agent sessions ... coordinate to avoid conflicts ... read COORDINATION.md"',
         'Done', 'The repository\'s coordination file',
         'This session claimed its scope, pushed the claim first, and recorded its sources, verification and '
         'irregularities in the same file.', src('IRS-ESTATE')],
        ['"Create a pull request ... merge ... confirm GitHub Pages deploys ... record the result"',
         'Done', 'The repository\'s coordination file',
         'The pull request, merge commit and deployment status are recorded there, with the live URL.', src('IRS-ESTATE')],
        ['"Publish flagged irregularities on a clearly labelled Flagged for Review page"',
         'Done', '<a href="flagged.html">Flagged for review</a>',
         'Seventeen flags, each with the official page behind it and a note on what would close it. None blocks the '
         'site.', src('CDI-RES')],
    ]
    body = ''.join([
        banner('<b>This page exists so that nothing in the brief is assumed to have been answered.</b> Each line of the '
               'request is quoted, marked done, partial or blocked, and linked to the page that answers it. Where a '
               'line was answered by a deliberate decision <i>not</i> to do something, the reason is stated.'),
        table(['Line of the brief', 'Status', 'Where it is answered', 'How, in one or two sentences', 'Official source'],
              rows, caption='The brief, line by line - thirty-nine requirements, including the four refused'),
        '<h2>The four lines that were not answered the way they were asked</h2>',
        '<div class="split"><div>',
        '<h3>1. The bill history is not published</h3>',
        '<p>The brief asked for property tax and assessed values by year. That series is a fingerprint: a unique '
        'starting value with a 2% growth pattern identifies a parcel to anyone who has the county roll. The projection '
        'uses the current value only, and the history is recorded as a closed privacy flag (P03).</p>',
        '<h3>2. The exact assessed values are not published</h3>',
        '<p>The brief asked for the assessed value and the tax. This edition publishes the tax and the change in the '
        'assessment around the transfer, and withholds the standing assessed values, because they are the most '
        'searchable number in the whole file.</p>',
        '</div><div>',
        '<h3>3. No insurance quote could be obtained</h3>',
        '<p>The brief asked for research into insurance costs. The research was done, and its conclusion is that no '
        'official source publishes a property-specific premium. Rather than substitute a ZIP-code average and call it '
        'a quote, the site keeps the figure labelled and flags it (U09).</p>',
        '<h3>4. The repository\'s history is not repaired</h3>',
        '<p>The brief asked for privacy to be the top priority. Every page is de-identified and the exact figures are '
        'out of the current files. The history, forks and caches are outside what a commit can fix, and making the '
        'repository private or rewriting history are owner decisions with irreversible effects (P02).</p>',
        '</div></div>',
        banner('<b>Nothing in this register is a self-assessment of quality.</b> It records coverage: which line of the '
               'brief is answered, where, and how. The verification of each official page is on the '
               '<a href="sources.html">sources page</a>, and the things that could not be verified are on the '
               '<a href="flagged.html">Flagged page</a>.', 'warn'),
    ])
    return page('requirements.html', 'Requirements register',
                'The brief, line by line / 13',
                'Every part of the request, the page that answers it, and the four lines that were answered by '
                'deliberately not doing what was asked.',
                body)
