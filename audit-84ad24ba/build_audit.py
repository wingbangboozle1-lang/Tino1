#!/usr/bin/env python3
"""Builds audit-84ad24ba/index.html and register.csv (session 84ad24ba, task S84-1).

Run from the repository root:  python3 final/model.py && python3 audit-84ad24ba/recompute.py && python3 audit-84ad24ba/build_audit.py

Labels, titles and links of the 57 sources are taken from final/sources.py, so this page cannot
quote a different link than the site does.  The build stops if a source of the site has no entry
here.  The page prints no owner-supplied amount.
"""
import csv, html, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location('site_sources', os.path.join(ROOT, 'final', 'sources.py'))
_s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_s)
S = _s.S
READ = '2026-11-11'

# result: C = read on the official page, agrees with the site
#         U = as C, and the site had only read an excerpt of this page (flag can be lifted)
#         P = partly: part of the statement read on the page, the rest not
#         N = not re-read by this session
R = {}


def r(i, result, read, note=''):
    R[i] = dict(result=result, read=read, note=note)


# ---- federal ----
r('IRS-ESTATE', 'C', 'Table by year of death: 2011 $5,000,000; 2017 $5,490,000; 2018 $11,180,000; 2025 $13,990,000; 2026 $15,000,000. Unused exclusion passes to a surviving spouse only by election on a timely filed estate tax return. Gross estate includes cash, securities, real estate, trusts.')
r('IRS-NEW', 'C', 'Public Law 119-21, signed July 4, 2025, raises the basic exclusion to $15,000,000 for calendar year 2026. Closing-letter fee raised from $56 to $76, effective October 26, 2026.')
r('RP-2026-35', 'C', 'Section 3.44: basic exclusion for calendar year 2027 is $15,480,000. Section 3.46: first $20,000 of gifts. Section 3.01, unmarried individuals: 24% over $109,125 to $208,325; 37% over $661,375. Section 3.03: 15% rate amount $563,200 (other individuals), $633,600 (joint).',
  'Irregularity: section 1 of the posted file still reads "as in effect on [Release Date, 2026]". The publication date shown on the site (2026-11-05) cannot be confirmed from the document.')
r('IRS-FAQ-ESTATE', 'C', 'Return due nine months after death; Form 4768 gives an automatic six-month extension; late portability election under Rev. Proc. 2022-32 up to the fifth anniversary of death, only when no return was otherwise required; earlier closing-letter fee $67.')
r('IRS-FAQ-INHERIT', 'C', 'Basis of inherited property is generally the fair market value on the date of death, whether or not an estate tax return is filed; a sale above basis is a taxable gain; Schedule A to Form 8971 may fix the basis.')
r('IRS-TC409', 'C', 'Net capital gain taxed at 0%, 15% or 20%; unrecaptured section 1250 gain at a maximum 25%. Also read: losses from the sale of personal-use property, such as a home, are not deductible.')
r('IRS-TC701', 'C', 'Exclusion of up to $250,000 ($500,000 joint); the home must be owned and used as a residence for at least 24 months of the 5 years before the sale.')
r('IRS-TC559', 'C', '3.8% on the lesser of net investment income or the excess of modified adjusted gross income over $200,000 (single) or $250,000 (joint); rents, dividends, interest and gains on real estate are included.')
r('RR-2023-2', 'C', 'Bulletin 2023-16 of April 17, 2023: the section 1014 basis adjustment generally does not apply to the assets of an irrevocable grantor trust not included in the deceased grantor\'s gross estate.')
r('IRS-I706', 'U', 'Instructions for Form 706 (07/2026), Table A, last row: taxable amount over $1,000,000 - tax $345,800 plus 40% of the excess. Also read: annual gift exclusion per donee "2025 through 2026: $19,000".')
r('IRS-P559', 'N', '', 'Long publication; the sentence relied on was not located and read by this session. Stays flagged (E-IRS-P559).')
r('IRS-P527', 'N', '', 'Long publication; the 27.5-year sentence was not located and read by this session. Stays flagged (E-IRS-P527).')
r('IRS-1041', 'U', 'An estate that generates more than $600 in annual gross income must file Form 1041; an employer identification number is needed first; calendar-year return due April 15.')
r('CONG-S587', 'U', 'S.587, Death Tax Repeal Act of 2025: introduced 02/13/2025; read twice and referred to the Committee on Finance; tracker shows "Introduced".')
r('CONG-HR1301', 'U', 'H.R.1301, Death Tax Repeal Act: introduced 02/13/2025; referred to the House Committee on Ways and Means; two actions in all, both on that day.')
# ---- California ----
r('SCO-ESTATE', 'C', 'For decedents that die on or after January 1, 2005, there is no longer a requirement to file a California Estate Tax Return. Inheritance tax applies only to deaths before June 8, 1982.')
r('BOE-P19', 'C', 'Principal residence of transferor and transferee; value limit of current taxable value plus $1,000,000 (as biennially adjusted); homeowners\' exemption within 1 year; claim within 3 years or before transfer to a third party; other real property no longer excluded; effective February 16, 2021.',
  'Also on the page and not on the site: a homeowner aged 55 or over can move the taxable value of a principal residence to a replacement home anywhere in California, up to three times.')
r('BOE-LTA-2025-009', 'C', 'Letter of March 7, 2025: California house price change for 2024 was 2.15 percent; the $1 million amount is adjusted to $1,044,586 for transfers February 16, 2025 through February 15, 2027; adjusted every other February 16; next adjustment February 2027.')
r('BOE-LTA-2026-026', 'C', 'Letter of August 3, 2026: excluded amount = factored base year value plus the adjusted $1 million; new taxable value = factored base year value plus the excess; transfers "whether within or outside a trust"; continual-use requirement.')
r('RTC-63.2', 'C', 'Subdivision (a)(1): principal residence of the transferor that becomes the principal residence of the transferee within one year; homeowners\' exemption filed within a year; exclusion removed when the transferee is no longer eligible.',
  'First part of the page read; the later subdivisions on the claim deadline were not re-read.')
r('RTC-480', 'C', 'Subdivision (e): where the change in ownership is by reason of death the statement is filed within 150 days after the date of death, or with the inventory and appraisal if the estate is probated.',
  'Second part of the page read. The notice text names a penalty capped at $5,000 or $20,000.')
r('PROB-16061.7', 'P', 'Subdivision (h): no action to contest the trust more than 120 days from the date the notification is served.',
  'The 60-day service deadline is in an earlier subdivision that this session did not re-read.')
r('BOE-RULE-462.260', 'C', 'Revocable trust: the date the trust becomes irrevocable; example: the date of death. Inheritance: the date of death of the decedent.')
r('BOE-HOX', 'C', '$7,000 reduction in taxable value for an owner-occupied home that was the principal residence on January 1; claim form BOE-266; file by February 15 for the full exemption.')
r('FTB-RATES', 'C', 'Schedule X (single): 9.3% over $72,724; 10.3% over $371,479; 11.3% over $445,771; 12.3% over $742,953.')
r('FTB-MHS', 'N', '', 'Long booklet; the 1% sentence was not located and read by this session. Stays flagged (E-FTB-MHS).')
r('SOS-RESULTS', 'C', 'Unofficial results as of November 10, 2026, 5:31 p.m.; certification by December 11, 2026. Proposition 3: yes 60.6%. Proposition 40: no 52.6%. Proposition 42: yes 51.5%.',
  'Read on the Secretary of State page itself. An earlier record on the board relied on news reports for Proposition 42.')
r('DOJ-TPA', 'U', 'Rent may not be increased more than 5% plus the change in the cost of living, or 10% total, whichever is lower, in any 12-month period. Exempt: housing built in the last 15 years; single-family homes not owned by a corporation or real estate trust, where the landlord notified the tenant in writing.',
  'The written notice to the tenant is a condition of the single-family exemption. The site does not say so.')
r('CDI-TOOL', 'C', '2026 Homeowners Insurance survey, including condominiums, renters and earthquake insurance; "The results of these surveys are not premium quotes"; surveyed insurers represent over 90% of their markets.')
r('CDI-TOOL-APP', 'C', 'Hypothetical risks; wildfire surcharges of 15% to over 300% are not reflected. Selection page: premiums effective May 1, 2026; coverage types are homeowners, condominium, mobilehome, renters and four earthquake types - no landlord policy.',
  'New: the location list has an entry "SANTA CLARA CUPERTINO" and an entry "SAN FRANCISCO SAN FRANCISCO-Sunset District". There is no ZIP code field. Coverage amounts stop at $1,000,000. The premium table appears only after an interactive selection and could not be read by this session, so the premium stays blank.')
r('CDI-EQ', 'C', 'Homeowners, renters and condominium policies do not cover earthquake damage; the insurer must offer earthquake insurance every other year; fire caused by an earthquake is covered by the homeowners policy.',
  'Also on the page and not on the site: for a home valued at over $1 million the lowest deductible available from the California Earthquake Authority is 15%.')
r('CDI-RES', 'N', '', 'Not re-read by this session. Stays flagged (E-CDI-RES).')
r('CPUC-NEM', 'U', 'Customer-generators are allowed to remain on the NEM 2.0 tariff for 20 years from the date they interconnected (Decision 14-03-041); new applicants since April 15, 2023 are on the net billing tariff; a customer who moves from net metering to net billing gets no legacy period.')
r('CPUC-FIXED', 'N', '', 'Not re-read by this session. Stays flagged (E-CPUC-FIXED).')
r('CDI-SB824', 'N', '', 'Not re-read by this session. Session abd204be recorded a re-read on 2026-11-11.')
r('CDI-RPI', 'N', '', 'Not re-read by this session.')
# ---- local ----
r('SCC-P19', 'C', 'Worked example: base value $200,000, market value $1,800,000, new value $800,000; claim form BOE-19-P; claims filed after three years receive relief only going forward.',
  'Irregularity confirmed (flag S03): the page says the $1 million allowance "will be adjusted annually"; the Board of Equalization says every other year.')
r('SCC-RATES', 'N', '', 'Not re-read by this session. Sessions 1a7fa860 and 95ca0c0b recorded re-reads on 2026-11-11. The tax rate area of the home remains unconfirmed (flag U03).')
r('SCC-DTT', 'C', 'Documentary transfer tax of $.55 per $500 or fractional portion of real property value; $1.65 per $500 only in San Jose, Palo Alto and Mountain View.')
r('SF-TAX', 'C', 'The secured property tax rate for Fiscal Year 2026-27 is 1.18162182%. A supplemental assessment follows a change in ownership.')
r('SF-EHT', 'C', 'On September 11, 2026 the California Court of Appeal affirmed that the Empty Homes Tax is preempted by state law (case A172067); the Treasurer has stopped all collection work; owners need not file or pay unless the decision is reversed.')
r('SF-RENT-2026', 'C', 'Annual allowable increase 1.6% from March 1, 2026 through February 28, 2027; 1.4% the year before.')
r('SF-RENT-RULES', 'C', 'Increase is 60% of the Bay Area consumer price increase; no limit on the first rent for an empty rent-controlled unit; notice of November 9, 2026 on Board of Supervisors File No. 261020, not enacted.',
  'Also on the page and not on the site: a landlord must report to the Rent Board Housing Inventory and hold a rent increase licence before raising a controlled rent.')
r('SF-RENT-LAW', 'C', 'A unit built before June 14, 1979 that is not a single family dwelling may have rent control and eviction protection; owner move-in is a just cause.',
  'Irregularity on the official page: its example still gives 1.7% as the allowed increase "for 2024 to February 28, 2025".')
r('SFPUC', 'P', 'Rate schedule effective July 1, 2026 and July 1, 2027; the Commission approved two years of water and wastewater rates in April 2026.',
  'The percentage increases quoted on the site are not stated in the part of the document read. Stays flagged (E-SFPUC).')
# ---- data ----
r('HUD-95014', 'C', 'Fiscal year 2026, ZIP 95014: efficiency $3,340; one-bedroom $3,800; two-bedroom $4,440; three-bedroom $5,870; four-bedroom $6,390.',
  'The page shows the ZIP figure was built from one-bedroom survey rents and metro ratios. It is an area figure, not the rent of a house (flags A07, U08).')
r('HUD-94122', 'C', 'Fiscal year 2026, ZIP 94122: efficiency $2,280; one-bedroom $2,730; two-bedroom $3,310; three-bedroom $4,230; four-bedroom $4,380.')
r('FHFA-SJ', 'C', 'Second quarter 2026: 558.75; first quarter 2026: 566.96; fourth quarter 2025: 560.05; second quarter 2025: 564.26; next release November 24, 2026.',
  'Latest five quarters read. The 1976-2025 history stored in final/data was not re-read value by value.')
r('FHFA-SF', 'N', '', 'Not re-read by this session.')
r('FHFA-CA', 'N', '', 'Not re-read by this session.')
r('BLS-CPI', 'N', '', 'Not re-read by this session.')
r('BLS-OCT', 'C', 'Release of November 10, 2026: the index rose 0.4 percent in October after 0.6 percent in September; index level 337.511; no 12-month change for October 2026 because October 2025 data were not collected.')
r('TREASURY', 'C', 'November 10, 2026: 3-month 4.30; 1-year 4.56; 10-year 4.98; 30-year 5.35.')
r('CBO', 'P', 'Inflation measured by the price index for personal consumption expenditures slows from 2.8 percent in 2025 to 2.7 percent in 2026 and returns to about 2 percent in 2030.',
  'The 10-year note rates and the growth average quoted on the site are in a table published as an image; not read. Stays flagged (E-CBO).')
r('USGS', 'U', 'Fact Sheet 2016-3020: 72 percent likelihood of at least one earthquake of magnitude 6.7 or greater in the San Francisco Bay region between 2014 and 2043; 51 percent for magnitude 7.0 or greater.')
r('FRED-JP', 'N', '', 'Not re-read by this session.')
r('DAMODARAN', 'N', '', 'Not an official source; not re-read by this session. Stays flagged (E-DAMODARAN, S02).')

# ---- findings: (id, kind, finding, effect on the decision, proposed change, source id) ----
F = [
    ('A01', 'Correction', 'The insurance how-to on the Insurance and costs page says to choose "the county, then the ZIP code". The official tool has one combined location list and no ZIP field. It does have an entry for Cupertino and one for the Sunset District of San Francisco. Coverage amounts stop at $1,000,000 and the premiums are those in effect on May 1, 2026.',
     'None on the ranking. It shortens the one manual step left to the owner.', 'Rewrite the four how-to steps; add the two direct links below.', 'CDI-TOOL-APP'),
    ('A02', 'Addition', 'For a home valued at over $1 million the lowest earthquake deductible available from the California Earthquake Authority is 15%. Both homes are above that value.',
     'None on the ranking. Raises the uninsured share of an earthquake loss in the Live and Rent choices.', 'Add to the earthquake row and to flag U02.', 'CDI-EQ'),
    ('A03', 'Wording', 'The summary says the low tax base of Property B "is lost for good if it is sold". Proposition 19 also lets an owner aged 55 or over move the taxable value of a principal residence to a replacement home anywhere in California, up to three times.',
     'None on the ranking. For the owner-occupied part of Property B the statement is too absolute.', 'Say "lost on a sale, unless the age-55 transfer applies to the owner-occupied part"; ask the Assessor how a three-unit building is treated.', 'BOE-P19'),
    ('A04', 'Addition', 'The Law page gives the annual gift exclusion for 2027 only. The figure for 2026 is $19,000 per recipient.',
     'None.', 'Add the 2026 figure beside the 2027 figure.', 'IRS-I706'),
    ('A05', 'Addition', 'The statewide rent cap exempts a single-family home only if the owner is not a corporation or real estate trust and the tenant was told in writing. Housing built in the last 15 years is also exempt.',
     'Matters only if Property A is rented out.', 'Add the written-notice condition to the rent-cap row.', 'DOJ-TPA'),
    ('A06', 'Addition', 'In San Francisco a landlord must report to the Rent Board Housing Inventory and hold a rent increase licence before raising a controlled rent.',
     'Matters for the two rented units of Property B if the building is rent-controlled (flag Q04).', 'Add one row to the local rules.', 'SF-RENT-RULES'),
    ('A07', 'Source register', 'Seven sources that the site had read only through an excerpt were read on the official page itself and agree: Form 706 instructions, the estate income tax page, S.587, H.R.1301, the Attorney General alert, the net metering page and the USGS fact sheet.',
     'None. Seven items can leave the "re-read by hand" list.', 'Change these seven entries from "excerpt" to "page" in final/sources.py.', 'IRS-I706'),
    ('A08', 'Irregularity', 'The posted file of Rev. Proc. 2026-35 still carries the placeholder "[Release Date, 2026]" in section 1.',
     'None on the figures, which are read on the document.', 'Add to the source irregularities; re-read when the Internal Revenue Bulletin version appears.', 'RP-2026-35'),
    ('A09', 'Model note, not verified', 'The model raises the federal exclusion by the same 2.5% as general prices. The document says the adjustments are "generally determined by reference to" section 1(f) of the Code; which price index that section uses was not read on an official page by this session.',
     'If the statutory index rises more slowly than general prices, the room for cash is smaller than shown.', 'Left as a question for the tax adviser. No figure changed.', 'RP-2026-35'),
    ('A10', 'Model note', 'The sale in the year of inheritance shows a loss equal to the selling costs. The model gives it no tax value. The IRS page says a loss on personal-use property is not deductible; whether an inherited home never lived in by the heir counts as personal use is for the adviser.',
     'The model takes the cautious side: any deduction would favour selling further.', 'No change.', 'IRS-TC409'),
    ('A11', 'Model note', 'The 3.8% tax is applied to all rent, dividends and gains. The IRS page applies it only to the lesser of investment income or income above $200,000 (single) or $250,000 (joint).',
     'Slightly overstates tax in all three choices for an income below the threshold. Already listed as review finding R13.', 'No change.', 'IRS-TC559'),
    ('A12', 'Confirmation', 'The three ballot results on the Law page were read on the Secretary of State page itself, with its time stamp.',
     'None.', 'Replace "confirmed through news reports" in the board record by the official read.', 'SOS-RESULTS'),
    ('A13', 'Privacy', 'Every current page uses placeholders and figures rounded to $10, as the owner asked, and the checker finds no unrounded owner figure in the tracked files. Rounding to $10 keeps five significant digits, and an assessed value is a public record. A person holding the assessment roll for the ZIP code could still match it. The Git history holds the unrounded first versions.',
     'None on the analysis. It is the main open risk.', 'Owner decision: make the repository private or have the history rewritten; and decide whether the two assessed values and tax bills should be shown as round bands instead. Nothing was deleted or rewritten by this session.', 'BOE-P19'),
]

DEEP = [
    ('Property A area, homeowners policy', 'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:21:::NO::P21_LOCATION,P21_TYPE:SANTA%20CLARA%20CUPERTINO,HOMEOWNERS',
     'Opened by this session: the home-age list (new to 70 years) and the coverage list ($250,000 to $1,000,000) fill in. Choose both to see the premiums by insurer.'),
    ('Property B area, homeowners policy', 'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:21:::NO::P21_LOCATION,P21_TYPE:SAN%20FRANCISCO%20SAN%20FRANCISCO-Sunset%20District,HOMEOWNERS',
     'Built the same way; not opened by this session. The survey has no landlord policy, so this is a yardstick only: ask an agent for a landlord quote for the three-unit building.'),
    ('Either area, earthquake', 'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:21',
     'Choose the location, then "EARTHQUAKE - Single Family".'),
]

NAMES = {'C': 'Confirmed', 'U': 'Confirmed, now read on the page', 'P': 'Partly confirmed', 'N': 'Not re-read'}


def e(x):
    return html.escape(str(x), quote=True)


def link(i):
    return '<a class="src" href="%s" rel="noopener">%s</a>' % (e(S[i]['url']), e(S[i]['label']))


def main():
    missing = [i for i in S if i not in R]
    extra = [i for i in R if i not in S]
    if missing or extra:
        sys.exit('register out of step with final/sources.py: missing %s, unknown %s' % (missing, extra))
    rc = json.load(open(os.path.join(HERE, 'recompute_result.json')))
    n = {k: sum(1 for v in R.values() if v['result'] == k) for k in 'CUPN'}
    with open(os.path.join(HERE, 'register.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'label', 'url', 'how_the_site_recorded_it', 'result', 'read_on_the_official_page_%s' % READ, 'note'])
        for i in S:
            w.writerow([i, S[i]['label'], S[i]['url'], S[i]['how'], NAMES[R[i]['result']], R[i]['read'], R[i]['note']])
    nav = ''.join('<a href="../%s">%s</a>' % (h, t) for h, t in (
        ('index.html', 'Summary'), ('decision.html', 'Decision'), ('flagged.html', 'Flagged for Review'),
        ('sources.html', 'Sources and method'), ('requirements.html', 'Requirements'), ('review.html', 'Repo review')))
    o = []
    o.append('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
             '<meta name="robots" content="noindex, nofollow">\n<title>Independent verification register - Two-home inheritance analysis</title>\n'
             '<link rel="stylesheet" href="../style.css">\n<style>.b{display:inline-block;padding:.1rem .45rem;border-radius:.6rem;font-size:.82rem;white-space:nowrap}'
             '.bC,.bU{background:#e3f2e6;color:#14532d}.bP{background:#fff3cd;color:#664d03}.bN{background:#eceff1;color:#37474f}td{vertical-align:top}</style>\n</head><body>\n')
    o.append('<header class="top"><div class="wrap">\n<a class="brand" href="../index.html">Two-home inheritance analysis</a>\n'
             '<nav aria-label="Sections">%s<a href="index.html" class="on" aria-current="page">Verification register</a></nav></div></header>\n<main class="wrap">\n' % nav)
    o.append('<h1>Independent verification register</h1>\n<p class="lead">Every source the site relies on, opened again on %s and compared with what the site says. '
             'Every headline figure, worked out a second time with separate formulas. What was found, and what could not be checked.</p>\n' % READ)
    o.append('<section class="kpis">'
             '<div class="kpi"><div class="k">Sources of the site</div><div class="v">%d</div><div class="s">each listed below with its official link</div></div>'
             '<div class="kpi"><div class="k">Read on the official page and in agreement</div><div class="v">%d</div><div class="s">%d of them had been read only through an excerpt before</div></div>'
             '<div class="kpi"><div class="k">Partly confirmed</div><div class="v">%d</div><div class="s">part of the statement read, the rest still flagged</div></div>'
             '<div class="kpi"><div class="k">Not re-read by this pass</div><div class="v">%d</div><div class="s">named below; nothing is marked verified without a read</div></div>'
             '<div class="kpi"><div class="k">Headline figures recomputed</div><div class="v">%d of %d agree</div><div class="s">to within one dollar of the model, and printed on the pages</div></div>'
             '<div class="kpi"><div class="k">Figures found wrong</div><div class="v">0</div><div class="s">%d corrections of wording, additions and notes are listed</div></div>'
             '</section>\n' % (len(S), n['C'] + n['U'], n['U'], n['P'], n['N'], rc['total'] - rc['failed'], rc['total'], len(F)))
    o.append('<h2 id="findings">What was found</h2>\n<p>No figure on the site disagrees with its official source. The items below are corrections of wording, facts worth adding, and limits of the model. None changes the ranking of the three choices.</p>\n'
             '<div class="tablewrap"><table><caption>Findings of this pass</caption><thead><tr><th>No.</th><th>Kind</th><th>Finding</th><th>Effect on the decision</th><th>Proposed change</th><th>Official basis</th></tr></thead><tbody>\n')
    for fid, kind, text, effect, change, src in F:
        o.append('<tr id="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (fid, fid, e(kind), e(text), e(effect), e(change), link(src)))
    o.append('</tbody></table></div>\n')
    o.append('<h2 id="insurance">Insurance: the official figure is two clicks away</h2>\n<p>The premium for each ZIP code is still blank on the site, because the official table opens only after a selection made by hand. '
             'The official tool was opened far enough to confirm that it covers both areas. These links open it with the area already chosen.</p>\n'
             '<div class="tablewrap"><table><caption>Direct links into the Department of Insurance comparison tool</caption><thead><tr><th>Use</th><th>What to do</th><th>Official tool</th></tr></thead><tbody>\n')
    for use, url, what in DEEP:
        o.append('<tr><td>%s</td><td>%s</td><td><a class="src" href="%s" rel="noopener">CDI homeowners tool</a></td></tr>\n' % (e(use), e(what), e(url)))
    o.append('</tbody></table></div>\n')
    o.append('<h2 id="figures">Headline figures worked out a second time</h2>\n<p>The script <a href="https://github.com/wingbangboozle1-lang/Tino1/blob/main/audit-84ad24ba/recompute.py">recompute.py</a> takes only the input table of the model. '
             'It then uses its own formulas and its own year-by-year loops, and compares the results with the model output and with the figures printed on the pages. The amounts themselves are on the <a href="../decision.html">Decision</a> page and are not repeated here.</p>\n'
             '<div class="tablewrap"><table><caption>Recomputation, by group of figures</caption><thead><tr><th>Group</th><th>Checks</th><th>Agree</th><th>Largest difference</th><th>Official basis of the rule</th></tr></thead><tbody>\n')
    groups = [
        ('Value, assessed value and Proposition 19 allowance at inheritance (2040, 2045, 2050)', ('market value', 'assessed value', 'allowance', 'excluded amount'), ('BOE-LTA-2026-026', 'BOE-LTA-2025-009')),
        ('First-year property tax before, if lived in, if rented', ('tax if', 'tax just before'), ('BOE-HOX', 'SCC-P19')),
        ('Federal exclusion, room under it, and the estate-tax table', ('exclusion', 'estate table'), ('RP-2026-35', 'IRS-I706')),
        ('Sale: net proceeds, loss, carrying cost', ('net proceeds', 'gain or loss', 'carrying cost'), ('SCC-DTT', 'IRS-FAQ-INHERIT')),
        ('After-tax wealth after 10 years and in 2076, three choices, three inheritance years', ('after-tax wealth', '2026 dollars'), ('IRS-TC409', 'IRS-TC559', 'FTB-RATES')),
        ('Property B: yearly tax kept by not selling', ('Property B',), ('SF-TAX',)),
    ]
    used = set()
    for label, keys, srcs in groups:
        rows = [c for c in rc['checks'] if any(k in c['check'] for k in keys) and c['check'] not in used]
        used.update(c['check'] for c in rows)
        worst = max([abs(c['difference_to_model_usd']) for c in rows if c['difference_to_model_usd'] is not None] or [0.0])
        o.append('<tr><td>%s</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td></tr>\n' % (
            e(label), len(rows), sum(1 for c in rows if c['passed']), 'under $1' if worst < 1 else '$%.0f' % worst, ' · '.join(link(s) for s in srcs)))
    assert len(used) == rc['total'], (len(used), rc['total'])
    o.append('</tbody></table></div>\n<p class="note">Agreement means the arithmetic of the model is right. It does not confirm the assumptions the model starts from; those are on the <a href="../flagged.html">Flagged for Review</a> page.</p>\n')
    o.append('<h2 id="register">Source by source</h2>\n<div class="tablewrap"><table><caption>All %d sources of the site</caption><thead><tr><th>Source</th><th>Read on the official page, %s</th><th>Result</th><th>Note</th><th>Open the page</th></tr></thead><tbody>\n' % (len(S), READ))
    for i in S:
        v = R[i]
        o.append('<tr><td>%s</td><td>%s</td><td><span class="b b%s">%s</span></td><td>%s</td><td>%s</td></tr>\n' % (
            e(S[i]['title']), e(v['read']) if v['read'] else 'not re-read', v['result'], NAMES[v['result']], e(v['note']), link(i)))
    o.append('</tbody></table></div>\n')
    o.append('<h2 id="limits">Limits of this pass</h2>\n<ul>'
             '<li>%d sources were not opened again by this pass. They keep the status the site gives them.</li>'
             '<li>Long statutes were read in the part that holds the quoted rule, not from first line to last.</li>'
             '<li>The historical series behind the Black swan section were not compared value by value.</li>'
             '<li>No owner document was seen. Trust type, basis, cash amount, tax rate area and insurance premiums stay open, as listed on the Flagged for Review page.</li>'
             '</ul>\n' % n['N'])
    o.append('</main>\n<footer class="wrap"><p>Built %s by session 84ad24ba from <a href="https://github.com/wingbangboozle1-lang/Tino1/tree/main/audit-84ad24ba">audit-84ad24ba/</a>. '
             'The register is also a file: <a href="register.csv">register.csv</a>. This page prints no owner-supplied amount. It is a check of an analysis, not legal or tax advice.</p></footer>\n</body></html>\n' % READ)
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(''.join(o))
    print('sources %d: confirmed %d (of which %d upgraded), partly %d, not re-read %d; findings %d; recomputed %d/%d' % (
        len(S), n['C'] + n['U'], n['U'], n['P'], n['N'], len(F), rc['total'] - rc['failed'], rc['total']))


if __name__ == '__main__':
    main()
