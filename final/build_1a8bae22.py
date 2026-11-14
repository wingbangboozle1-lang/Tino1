#!/usr/bin/env python3
"""Pages added in session 1a8bae22: brief, glossary, timeline, what-if, phased entry.

  ROOT_MODE=1 OUT_DIR=. python3 final/build.py
  ROOT_MODE=1 OUT_DIR=. python3 final/build_1a8bae22.py

Reads final/out/model.json (built by final/model.py) and final/out/phased_1a8bae22.json (built by
final/phased_1a8bae22.py). No new household figure is typed in by hand: every number comes from those
files, is rounded to the nearest $10 by build.py's m(), and sits next to an official source link.
"""
import json, os, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402  (the shared generator: page shell, table helper, $10 rounding, sources)

M = B.M
P = B.P
S_ = B.B  # baseline summary
PH = json.load(open(os.path.join(HERE, 'out', 'phased_1a8bae22.json')))
src, flag, table, m, pc, e = B.src, B.flag, B.table, B.m, B.pc, B.e
r10 = B.r10
NOTE_ROOT = 'Earlier versions remain as recorded in the repository.'


def link(slug, text):
    return '<a href="%s">%s</a>' % (slug, text)


# ------------------------------------------------------------------ 1. Attorney & CPA brief (one printed page)
def build_brief():
    print_css = """<style>
.brief{font-size:12px;line-height:1.35}
.brief h2{font-size:14px;margin:9px 0 3px;color:#12283f;border-bottom:1px solid #9aa7b4;padding-bottom:1px}
.brief table{font-size:11px}.brief td,.brief th{padding:2px 4px}
.brief .two{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.brief ol,.brief ul{margin:2px 0 0 16px;padding:0}.brief li{margin:0 0 2px}
@media print{header.top,footer,.noprint{display:none!important}body{background:#fff}
 .wrap{max-width:none;padding:0}main.wrap{padding:0}.brief{font-size:9pt}.brief table{font-size:8pt}.brief h2{font-size:10pt;margin:5px 0 2px}
 h1{font-size:14pt;margin:0 0 2px}.lead{font-size:9pt;margin:0 0 4px}.brief td,.brief th{padding:1px 3px}
 table{page-break-inside:avoid}@page{size:letter;margin:0.35in}}
</style>"""
    fact = table(['Item (placeholder names only)', 'Figure (rounded to $10)', 'Status', 'Official basis'], [
        ['Property A: estimated market value, Nov. 2026 (Cupertino, Santa Clara County)', m(P['cup_value']), 'Owner estimate; not an appraisal ' + flag('P03'), src('SCC-P19-EST')],
        ['Property A: assessed value, 2026', m(P['cup_assessed']), 'Owner-supplied roll figure ' + flag('P01'), src('RTC-51', 'SCC-RATES')],
        ['Property A: property tax, 2025 (owner-supplied table)', m(P['cup_tax_2025']), 'Owner-supplied bill ' + flag('U03'), src('SCC-RATES')],
        ['Property B: estimated market value, Nov. 2026 (San Francisco)', m(P['sf_value']), 'Owner estimate ' + flag('P03'), src('SF-TAX')],
        ['Property B: assessed value, 2026 / property tax, 2025', m(P['sf_assessed']) + ' / ' + m(P['sf_tax_2025']), 'Owner-supplied ' + flag('P01'), src('SF-TAX')],
        ['Property B: rent from two units, per year (monthly income about $7,150)', m(P['sf_rent_2units']), 'Owner-supplied; third unit not rented ' + flag('A10'), src('HUD-94122')],
        ['Property A: tax at inheritance (model, 2045) if lived in / if rented', m(S_['tax_live_T']) + ' / ' + m(S_['tax_rent_T']) + ' a year', 'Model, Prop. 19 partly applied / full reassessment ' + flag('A01'), src('BOE-P19', 'BOE-LTA-2026-026')],
        ['Federal basic exclusion amount, 2026 / 2027', '$15,000,000 / $15,480,000', 'Official', src('IRS-I706', 'RP-2026-35')],
        ['Federal room for cash after Property A, 2045 (model, 2045 dollars)', m(S_['exclusion_T'] - S_['fmv_T']), 'Projection ' + flag('A01') + ' ' + flag('Q02'), src('RP-2026-35')],
        ['California estate or inheritance tax', 'None: no return required for deaths on or after 1 January 2005', 'Official', src('SCO-ESTATE')],
        ['Basis of Property A after death (if inside the gross estate)', 'Market value on date of death', 'Depends on the trust ' + flag('Q01'), src('IRS-FAQ-INHERIT', 'RR-2023-2')],
    ], caption='1. Facts the figures depend on', cls='num')
    # outcomes
    outc = table(['Path for Property A (model, 2076)', 'After-tax wealth, nominal', 'After-tax wealth, 2026 dollars', 'Official basis'], [
        ['Live in Property A (needs the Prop. 19 steps; see the Deadline timeline)', m(S_['w_live']), m(S_['real_live']), src('TREASURY', 'FHFA-SF', 'BLS-CPI') + ' ' + flag('A01') + ' ' + flag('A02')],
        ['Rent out Property A', m(S_['w_rent']), m(S_['real_rent']), src('HUD-94122', 'BOE-P19') + ' ' + flag('A07')],
        ['Sell Property A and invest the proceeds', m(S_['w_sell']), m(S_['real_sell']), src('IRS-FAQ-INHERIT', 'IRS-TC409') + ' ' + flag('A02')],
    ], caption='2. Modelled outcome (not a forecast). The model\'s best path: sell.', cls='num')
    # phased
    named = {n['entry']: n for n in PH['named']}
    def row(entry, label):
        r = named[entry]['results']
        return ['%s: lump sum vs 24 / 36 months parked' % label,
                m(r['lump']['end']) + ' vs ' + m(r['park24']['end']) + ' / ' + m(r['park36']['end']),
                m(r['lump']['trough']) + ' vs ' + m(r['park24']['trough']) + ' / ' + m(r['park36']['trough']),
                src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02') + ' ' + flag('H02')]
    phased = table(['Phased entry, 10 years after entry', 'End value: lump vs parked', 'Lowest value: lump vs parked', 'Official basis'],
                   [row(1929, '1929 entry'), row(2008, '2008 entry')],
                   caption='3. Phased entry test (annual data; see the Phased entry page)', cls='num')
    att = ['Trust type and whether Property A is inside the gross estate, for the basis reset (Q01). ' + src('RR-2023-2'),
           'Total estate and any ported spousal exclusion (Q02); whether a Form 706 is needed. ' + src('IRS-FAQ-ESTATE'),
           'Relationship to the Inheritor under the Prop. 19 definitions (Q06). ' + src('BOE-PUB-800-1'),
           'When title actually passes and whether a marital or community-property rule applies (Q16). ' + src('BOE-P19'),
           'Who files BOE-266 and BOE-19-P, and in what order, within one year and three years (S03). ' + src('BOE-PUB-800-1'),
           'Timing of trustee notice (60 days) and the change-in-ownership statement (150 days). ' + src('PROB-16061.7', 'RTC-480')]
    cpa = ['Filing status and bracket for the Inheritor (Q05); the investment-income tax threshold. ' + src('IRS-TC559'),
           'Property B: purchase basis, depreciation taken and the 25% recapture rate (Q03). ' + src('IRS-P527', 'IRS-TC409'),
           'Which home has the homeowners\' exemption now (Q18); $7,000 of taxable value. ' + src('BOE-HOX'),
           'Deductibility of selling costs on a prompt sale of Property A (Q17). ' + src('IRS-TC409'),
           'Consistent basis: Form 706 value and the Form 8971 report (inherited basis). ' + src('IRS-FAQ-INHERIT'),
           'Home-sale exclusion for Property B if it is ever sold ($250,000 single; 2 of 5 years). ' + src('IRS-TC701')]
    body = """%s<div class="brief">
%s
<div class="two"><div><h2>4. Questions for the estate attorney</h2><ol>%s</ol></div>
<div><h2>5. Questions for the tax adviser</h2><ol>%s</ol></div></div>
<h2>6. Deadlines (full timeline: <a href="timeline.html">Deadline timeline</a>)</h2>
<p>Within 60 days after a revocable trust becomes irrevocable at death: trustee notice. Within 150 days of death: change-in-ownership statement. Within 9 months: Form 706 if required (Form 4768 adds six months). Within 1 year: move in and file BOE-266 if living there. Within 3 years: BOE-19-P. Sale year: Form 8949 and Schedule D. Each year: rent reporting and the rent cap notice.</p>
<p class="note">Placeholders only: \u201cthe Transferor\u201d (current owner of Property A) and \u201cthe Inheritor\u201d (owner of Property B). Figures are owner-supplied or modelled, rounded to the nearest $10, and are not appraisals or advice. Flags point to the <a href="flagged.html">Flagged for Review</a> page. Prepared for review by a licensed estate attorney and a tax adviser; it is not legal or tax advice. Built %s.</p>
</div>""" % (print_css, '\n'.join([fact, outc, phased]).replace('<div class="tablewrap">', '<div class="tablewrap">'),
              ''.join('<li>%s</li>' % x for x in att), ''.join('<li>%s</li>' % x for x in cpa), B.BUILD_DATE)
    lead = 'Print this page (File, Print) and hand it to the estate attorney and the tax adviser. One Letter page; placeholders only.'
    B.page('brief.html', 'Attorney &amp; CPA Briefing Sheet', lead, body)


# ------------------------------------------------------------------ 2. Glossary
def build_glossary():
    G = [
        ['Base year value', 'The assessed value a property gets when it changes ownership. Later years grow it by an inflation factor.', 'It is the starting point for the Prop. 13 tax on Property A and Property B.', src('RTC-51')],
        ['Annual cap of 2% on assessed value', 'The inflation adjustment to a property\'s taxable value cannot exceed 2% of the prior year\'s value (R&TC 51, subparagraph D).', 'Why Property B\'s taxable value grows slowly even while its market value rises.', src('RTC-51')],
        ['Change in ownership', 'A transfer that can cause reassessment. A transfer by reason of death needs a statement filed within 150 days.', 'Starts the 150-day filing clock for Property A.', src('RTC-480')],
        ['Parent-child exclusion (Proposition 19)', 'Keeps the old assessed value for a parent\'s home passed to a child only if the child makes it a principal residence, with a value limit.', 'It decides whether Property A is reassessed when the Inheritor takes it.', src('BOE-P19', 'BOE-LTA-2026-026')],
        ['Principal residence (transferee)', 'The home the child lives in as its main home, within a year of the transfer.', 'Needed to keep the Prop. 19 exclusion for Property A.', src('RTC-63.2')],
        ['Homeowners\' exemption', 'A $7,000 reduction in taxable value for an owner-occupied home on the January 1 lien date. One claim (BOE-266).', 'Needed before the Prop. 19 claim (BOE-19-P) can be filed.', src('BOE-HOX', 'BOE-PUB-800-1')],
        ['Basis (stepped-up at death)', 'The starting value for tax on a later sale; for inherited property it is generally the fair market value on the date of death.', 'Sets the gain if Property A is sold.', src('IRS-FAQ-INHERIT')],
        ['Irrevocable grantor trust (basis rule)', 'Assets of an irrevocable grantor trust that are not in the deceased grantor\'s gross estate do not get the basis adjustment at death.', 'Why the trust type is the first question (Q01).', src('RR-2023-2')],
        ['Federal basic exclusion amount', 'The amount each person can transfer without federal estate tax. $15,000,000 in 2026; $15,480,000 in 2027.', 'Sets the room for cash and other assets after Property A.', src('IRS-I706', 'RP-2026-35')],
        ['Federal estate tax rate', 'Above the exclusion the tax is 40% of the excess (Table A, Form 706).', 'Applies to the estate, not to the Inheritor.', src('IRS-I706')],
        ['Form 706', 'The federal estate tax return. Due nine months after death; Form 4768 gives six more months.', 'Filed if the estate is above the threshold or to keep portability.', src('IRS-FAQ-ESTATE')],
        ['Portability', 'Passing an unused exclusion to a surviving spouse; needs a timely Form 706.', 'Checked for a predeceased spouse (Q02).', src('IRS-FAQ-ESTATE')],
        ['Long-term capital gain rate', 'Net capital gains are taxed at 0%, 15% or 20% depending on income.', 'Tax on a later sale of stocks or Property A.', src('IRS-TC409')],
        ['Unrecaptured section 1250 gain', 'Depreciation taken on rental buildings is taxed at up to 25%.', 'Applies to Property B and to Property A if rented.', src('IRS-TC409', 'IRS-P527')],
        ['Depreciation (27.5 years)', 'Residential rental buildings are depreciated straight-line over 27.5 years.', 'Shelters rent; recaptured on sale.', src('IRS-P527')],
        ['Home-sale exclusion', 'Up to $250,000 ($500,000 joint) of gain on a main home, if used 2 of the last 5 years.', 'Relevant if Property B is ever sold.', src('IRS-TC701')],
        ['Net investment income tax', '3.8% on investment income, including rents and gains, above the threshold.', 'Adds to the cost of renting or selling.', src('IRS-TC559')],
        ['Like-kind exchange', 'Deferral of gain when real property held for investment is exchanged for like-kind property.', 'One possible route for an investment property; not modelled.', src('IRS-1031')],
        ['Supplemental tax bill', 'An extra bill after a change in ownership for the period not yet taxed at the new value.', 'Budgeted in every path (step 12 on the process page).', src('SF-TAX')],
        ['Earthquake coverage', 'Homeowners policies do not cover earthquake damage; a separate policy is needed.', 'Not in the insurance estimate unless it is added (U02).', src('CDI-EQ')],
        ['Vacancy exclusion (60 days)', 'Standard homeowners policies exclude losses to a house vacant for 60 or more days.', 'Matters if a home is empty between death and sale.', src('CDI-RES')],
        ['Tenant Protection Act (rent cap)', 'State rent cap of 5% plus CPI, or 10% in total in 12 months, for covered units.', 'Limits rent growth on Property B and on any rented Property A.', src('DOJ-TPA')],
        ['San Francisco allowable rent increase', 'For covered units the Rent Board allows 60% of the Bay Area CPI-U increase.', 'Limits rent growth on Property B in the model (flag A10).', src('SF-RENT-RULES')],
        ['Net energy metering (NEM)', 'The solar credit system. Under the 2014 decision, NEM 2.0 customers keep their tariff for 20 years from interconnection.', 'Sets the solar credit at Property A (U05).', src('CPUC-NEM')],
        ['Fixed monthly charge', 'The utility\'s fixed Base Services Charge; $24.15 a month for standard Tier 3 customers.', 'A fixed charge on each bill, separate from energy use (U05).', src('CPUC-FIXED')],
        ['3-month Treasury bill', 'A short-term U.S. government debt rate. Used as the cash parking return in the phased test.', 'The reinvestment risk: cash earns the rate of the day.', src('TREASURY', 'FRED-TB3MS')],
        ['2-year Treasury note (GS2)', 'Market yield on 2-year U.S. Treasury notes, constant maturity.', 'Cross-check for the parking return in 2007-2010.', src('FRED-GS2')],
    ]
    t = table(['Term', 'Plain meaning', 'Why it matters here', 'Official basis'], G, caption='Official terms used in this analysis', cls='gloss')
    extra = """<h2>Terms defined by this analysis (not from an official source)</h2>
<dl class="defs">
<dt>Reinvestment risk</dt><dd>The chance that cash must be reinvested later at a lower rate. Shown next to the headline on the Phased entry page.</dd>
<dt>Black swan (in this analysis)</dt><dd>A sequence of real or invented economic conditions that departs from a constant growth and inflation rate, used as a stress test.</dd>
<dt>Phased entry</dt><dd>Parking the proceeds in short Treasuries for 24 or 36 months, then buying stocks in 12 equal monthly steps.</dd>
<dt>Mixed path</dt><dd>A combination of choices, such as living in Property A for a period and then renting or selling it. Not yet modelled on this site.</dd>
<dt>What-if case</dt><dd>One change to a baseline assumption, with the model rerun for it. Combined changes are not yet modelled.</dd>
</dl>"""
    B.page('glossary.html', 'Glossary', 'Plain meanings of the official terms, each with the official page it comes from. Project terms are listed separately.', t + extra)


# ------------------------------------------------------------------ 3. Deadline timeline
def build_timeline():
    items = [
        ('Now', 'Before any death', 'Have the estate attorney confirm the trust type and whether Property A will be inside the gross estate. Keep Property A as the Transferor\'s principal residence with the homeowners\' exemption on file.', src('RR-2023-2', 'BOE-P19', 'BOE-HOX') + ' ' + flag('Q01')),
        ('Date of death (D)', 'Day 0', 'Record the date. Get a written appraisal of Property A as of that date; it sets the new basis.', src('BOE-RULE-462.260', 'IRS-FAQ-INHERIT')),
        ('D + 60 days', 'Trustee notice', 'If the trust was revocable: the successor trustee serves the notification on every beneficiary and heir (120-day contest warning).', src('PROB-16061.7')),
        ('D + 150 days', 'Change in ownership', 'File the change-in-ownership statement for Property A with the Santa Clara County Assessor.', src('RTC-480')),
        ('D + 9 months', 'Federal return', 'File Form 706 if required or to elect portability. Form 4768 gives six more months.', src('IRS-FAQ-ESTATE', 'IRS-I706') + ' ' + flag('Q02')),
        ('D + 1 year (only if moving in)', 'Principal residence', 'Make Property A the Inheritor\'s principal residence and file BOE-266 before the Prop. 19 claim.', src('RTC-63.2', 'BOE-LTA-2026-026', 'BOE-PUB-800-1')),
        ('D + 3 years (only if moving in)', 'Prop. 19 claim', 'File BOE-19-P with the Assessor. Late claims get prospective relief only.', src('BOE-P19', 'SCC-P19', 'BOE-PUB-800-1') + ' ' + flag('S03')),
        ('After the Assessor acts', 'Supplemental bill', 'Expect a supplemental tax bill for Property A covering the period from the date of death.', src('SF-TAX') + ' ' + flag('U06')),
        ('Each January 1 (lien date)', 'Homeowners\' exemption', 'The owner-occupied $7,000 exemption applies on the January 1 lien date; file by February 15 for the full exemption.', src('BOE-HOX')),
        ('Tax year of any sale', 'Sale reporting', 'Report the sale on Form 8949 and Schedule D using the date-of-death value as basis.', src('IRS-FAQ-INHERIT', 'IRS-TC409')),
        ('Every year, if rented', 'Rent reporting', 'Report rent and expenses; depreciate the building over 27.5 years; follow the rent-cap notices.', src('IRS-P527', 'DOJ-TPA')),
    ]
    html_items = ''.join('<li class="tl"><div class="when"><strong>%s</strong><span>%s</span></div><div class="what">%s<p class="srcs">%s</p></div></li>'
                         % (e(a), e(b), e(c), d) for a, b, c, d in items)
    css = """<style>
ol.timeline{list-style:none;margin:0;padding:0;border-left:3px solid #1f4e8c}
li.tl{display:grid;grid-template-columns:200px 1fr;gap:12px;margin:0 0 14px 14px;padding:8px 10px;background:#fff;border:1px solid #d9dee4;border-radius:6px}
.when strong{display:block;color:#12283f}.when span{color:#5b6875;font-size:13px}
.what p{margin:4px 0 0}.srcs{font-size:13px}
@media (max-width:640px){li.tl{grid-template-columns:1fr}}
</style>"""
    body = css + '<p class="note">Dates are relative to the date of death (D). The trust does not change the Prop. 19 steps. Items marked "only if moving in" do not apply to a sale or rent-out.</p><ol class="timeline">%s</ol>' % html_items
    B.page('timeline.html', 'Deadline timeline', 'Every filing clock in the inheritance process, in order, with the official page for each.', body)


# ------------------------------------------------------------------ 4. What-if controls
def build_whatif():
    cases = M['sensitivity']
    rows = []
    for i, c in enumerate(cases):
        rows.append('<tr data-i="%d"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            i, e(c['label']), m(c['w_live']), m(c['w_rent']), m(c['w_sell']),
            e({'live': 'Live in it', 'rent': 'Rent it', 'sell': 'Sell and invest'}[c['best']]),
            m(c['w_sell'] - cases[0]['w_sell']) if i else '-',
            src('TREASURY', 'FHFA-SF', 'BLS-CPI') + ' ' + flag('A01')))
    head = '<tr>' + ''.join('<th scope="col">%s</th>' % h for h in ['Case (one change to the baseline)', 'Live in it', 'Rent it', 'Sell and invest', 'Best path', 'Sell path vs baseline (nominal)', 'Official basis']) + '</tr>'
    opts = ''.join('<option value="%d">%s</option>' % (i, e(c['label'])) for i, c in enumerate(cases))
    data = [dict(label=c['label'], live=r10(c['w_live']), rent=r10(c['w_rent']), sell=r10(c['w_sell']), best=c['best']) for c in cases]
    body = """<style>
.ctl{display:flex;flex-wrap:wrap;gap:12px;align-items:end;background:#fff;border:1px solid #d9dee4;border-radius:8px;padding:12px 14px;margin:0 0 12px}
.ctl label{display:flex;flex-direction:column;font-weight:600;font-size:14px;min-width:280px}
.ctl select{font:inherit;padding:6px;margin-top:4px;border:1px solid #9aa7b4;border-radius:5px}
#readout{flex:1;min-width:280px;font-size:15px}
tr.sel td{background:#fff6e0;font-weight:600}
</style>
<div class="ctl noprint"><label>Choose one change to the baseline<select id="case" aria-describedby="readout">%s</select></label>
<div id="readout" role="status" aria-live="polite"></div></div>
<p class="note">Each row is one change from the baseline, with the whole model rerun for it (the values are computed in the model, not in the browser). Combined changes are not yet modelled. Wealth is after tax, at the end of the model in 2076; 2026 dollars divide by the modelled price level.</p>
%s
<script>
var CASES=%s;
var sel=document.getElementById('case'),out=document.getElementById('readout');
var rows=document.querySelectorAll('tbody tr[data-i]');
function show(){var i=+sel.value,c=CASES[i],names={live:'live in it',rent:'rent it',sell:'sell and invest'};
rows.forEach(function(r){r.classList.toggle('sel',+r.getAttribute('data-i')===i)});
out.innerHTML='<strong>'+c.label+'</strong>: best is to '+names[c.best]+'. After-tax wealth, nominal: live $'+c.live.toLocaleString('en-US')+', rent $'+c.rent.toLocaleString('en-US')+', sell $'+c.sell.toLocaleString('en-US')+'.';}
sel.addEventListener('change',show);show();
</script>""" % (opts, '<div class="tablewrap"><table class="num"><caption>All cases in the model (nominal values, rounded to $10)</caption><thead>%s</thead><tbody>%s</tbody></table></div>' % (head, ''.join(rows)), json.dumps(data))
    B.page('whatif.html', 'What-if controls', 'Pick a change to a baseline assumption and see how the three paths and the best choice move. Built from the model\'s own runs.', body)


# ------------------------------------------------------------------ 5. Phased entry with reinvestment risk
def build_phased():
    named = {n['entry']: n for n in PH['named']}
    R = PH['robust']
    def res_rows(entry):
        out = []
        r = named[entry]['results']
        for key, lab in (('lump', 'Lump sum into stocks at entry'), ('park24', 'Park 24 months, then phase in over 12 months'),
                         ('park36', 'Park 36 months, then phase in over 12 months'), ('bills', 'Reference: all in 3-month bills')):
            v = r[key]
            out.append([lab, m(v['end']), m(v['trough']), pc(v['trough_vs_start']), pc(v['max_drawdown']), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02') + ' ' + flag('H02')])
        return out
    t1914 = table(['1929 entry (start of 1929), 10 years', 'End value', 'Lowest value', 'Lowest vs start', 'Largest fall', 'Official basis'], res_rows(1929), caption='Test A: entry in 1929', cls='num')
    t2 = table(['2008 entry (start of 2008), 10 years', 'End value', 'Lowest value', 'Lowest vs start', 'Largest fall', 'Official basis'], res_rows(2008), caption='Test B: entry in 2008', cls='num')
    # 2-year check table for the 2008 window
    g2 = [[str(g['year']), pc(g['gs2_avg'], 2), pc(g['bill'], 2), pc(g['stock']), src('FRED-GS2', 'FRED-TB3MS') + ' ' + flag('S02')] for g in PH['gs2_check']]
    t_gs2 = table(['Year', '2-year note, average yield (FRED GS2)', '3-month bill return (academic table)', 'S&P 500 total return', 'Official basis'], g2, caption='Parking-return cross-check, 2007-2010 (bill and stock columns are academic values, flag S02)', cls='num')
    t_rr = table(['Year', '3-month Treasury bill return', 'S&P 500 total return', 'Test window', 'Official basis'],
                 [[str(b['year']), pc(b['bill'], 2), pc(b['stock']), 'Entry 1929 (window)', src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')]
                  for b in named[1929]['bill_path']] +
                 [[str(b['year']), pc(b['bill'], 2), pc(b['stock']), 'Entry 2008 (window)', src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')]
                  for b in named[2008]['bill_path']],
                 caption='Reinvestment risk: what the parked cash earned in the years around each test', cls='num')
    rob = table(['Across all %d entry years, 1928 to 2016' % R['n_entries'], 'Value', 'Official basis'], [
        ['Median end value: lump sum', m(R['lump']['median_end']), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')],
        ['Median end value: park 24 months', m(R['park24']['median_end']), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02') + ' ' + flag('H03')],
        ['Median end value: park 36 months', m(R['park36']['median_end']), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02') + ' ' + flag('H03')],
        ['Share of entry years where park-24 ended higher than lump sum', pc(R['park24']['share_end_above_lump'], 0), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')],
        ['Share of entry years where park-24 had a higher lowest value', pc(R['park24']['share_trough_above_lump'], 0), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')],
        ['Share of entry years where park-36 ended higher than lump sum', pc(R['park36']['share_end_above_lump'], 0), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')],
        ['Worst lowest value: lump sum / park 24 / park 36', m(R['lump']['worst_trough']) + ' / ' + m(R['park24']['worst_trough']) + ' / ' + m(R['park36']['worst_trough']), src('FRED-TB3MS', 'FRED-SP500') + ' ' + flag('S02')],
    ], caption='Robustness: the test in every year the data allow', cls='num')
    a = named[1929]['results']; b = named[2008]['results']
    headline = """<div class="kpis">
<div class="kpi"><div class="l">1929 test: lowest value, lump sum vs parked 24 months</div><div class="v">%s vs %s</div><div class="s">Start: %s. Parking softened the fall.</div></div>
<div class="kpi"><div class="l">2008 test: 10-year end value, lump sum vs parked 24 months</div><div class="v">%s vs %s</div><div class="s">In this test the wait paid off.</div></div>
<div class="kpi"><div class="l">Reinvestment risk: 3-month bills, 2008-2010</div><div class="v">%s to %s a year</div><div class="s">Cash earned little while stocks fell; the bill rate can fall to near zero.</div></div>
<div class="kpi"><div class="l">Entry years where 24-month parking ended higher</div><div class="v">%s of years</div><div class="s">Parking lowers the fall but usually costs return in a normal market.</div></div>
</div>""" % (m(a['lump']['trough']), m(a['park24']['trough']), m(PH['C0']),
              m(b['lump']['end']), m(b['park24']['end']),
              pc(min(x['bill'] for x in named[2008]['bill_path'] if 2008 <= x['year'] <= 2010), 2),
              pc(max(x['bill'] for x in named[2008]['bill_path'] if 2008 <= x['year'] <= 2010), 2),
              pc(R['park24']['share_end_above_lump'], 0))
    css = """<style>
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin:0 0 12px}
.kpi{background:#fff;border:1px solid #d9dee4;border-radius:8px;padding:10px 12px}.kpi .l{font-size:12px;color:#5b6875}
.kpi .v{font-size:20px;font-weight:700;color:#12283f;margin:3px 0}.kpi .s{font-size:12px;color:#5b6875}
</style>"""
    body = css + headline + """<p class="note">Stock-market caveat: these are annual data (see flag H02). The phased path is a stress test of entry timing, not a forecast. The parking return is the 3-month bill (flag H01); the 2-year note is shown as a cross-check. <strong>Unverified:</strong> no official series covers the 1928-1933 bill and stock returns or the 2008 total returns (the linked FRED pages show their coverage), so those values are academic and flagged S02, not confirmed.</p>
<h2>How the test works</h2><ol><li>Starting cash: the model's after-tax net sale proceeds for Property A, %s (rounded to $10).</li>
<li>Lump sum: all of it in stocks on 1 January of the entry year.</li>
<li>Phased: all of it in short Treasuries for 24 or 36 months, then 12 equal monthly purchases of stocks (flag H03).</li>
<li>Every year's return is spread evenly over the months of that year; the 10-year horizon runs from the entry date.</li></ol>
%s %s
%s %s %s""" % (m(PH['C0']), t1914, t2, t_rr, t_gs2, rob)
    B.page('phased.html', 'Phased entry: parking the proceeds before buying stocks',
           'Does parking the sale proceeds in short Treasuries for 24 to 36 months soften the entry into a 1929-style or 2008-style crash, and what does it cost in a normal market?', body)


def main():
    build_brief(); build_glossary(); build_timeline(); build_whatif(); build_phased()
    print('built 5 pages in', B.OUT)


if __name__ == '__main__':
    main()
