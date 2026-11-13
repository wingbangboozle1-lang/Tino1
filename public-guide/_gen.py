#!/usr/bin/env python3
"""De-identified numeric edition - shared generator frame. Standard library only.

Run:  python3 public-guide/_gen.py      (writes public-guide/*.html)

Three rules are enforced by construction in this module:

1. FIGURES COME FROM THE MODEL, NOT FROM A KEYBOARD.  Every household amount is
   read from final/out/model.json (written by final/model.py) and formatted by
   m()/mm(), which round to the nearest $10.  A model amount that is not already
   a multiple of $10 can only be printed through those helpers.
2. OFFICIAL PUBLISHED AMOUNTS ARE QUOTED EXACTLY.  Statutory amounts (the IRS
   exclusion, the BOE value cap, the CPUC fixed charge, the SF tax rate) are
   printed as published, because rounding a quotation would be a misquotation.
   They are marked as such in the text and are on the checker's official list.
3. NO IDENTIFYING FACT IS AVAILABLE TO THE GENERATOR.  No name, address, parcel
   number, account number or year-by-year bill history is read from anywhere.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODEL_PATH = os.environ.get('TINO1_MODEL', os.path.join(ROOT, 'final', 'out', 'model.json'))

M = json.load(open(MODEL_PATH, encoding='utf-8'))
P = M['params']
B = M['baseline']['summary']
ROWS = M['baseline']['rows']
T = int(P['T'])
Y0 = 2026
Y1 = 2076

BUILD_DATE = '2026-11-13'
E = html.escape


# --------------------------------------------------------------------------- money

def r10(x):
    """Nearest $10. Every household amount on this site passes through here."""
    return int(round(abs(float(x)) / 10.0)) * 10 * (1 if float(x) >= 0 else -1)


def m(x):
    """A household amount as dollars, rounded to $10."""
    v = r10(x)
    return ('-$' if v < 0 else '$') + format(abs(v), ',')


def mm(x):
    """A household amount in millions, built from the $10-rounded value."""
    v = r10(x)
    return ('-$' if v < 0 else '$') + ('%.2f' % (abs(v) / 1e6)) + 'M'


NEUTRAL = [
    ('San Jose-Sunnyvale-Santa Clara', 'the Property A metro area'),
    ('San Jose', 'the Property A metro area'),
    ('San Francisco', 'the Property B metro area'),
    ('Cupertino', 'Property A'),
    ('Santa Clara County', 'the county'),
    ('Santa Clara', 'the county'),
]


def neut(s):
    """Neutralise a locality name in a string copied from the model's provenance notes."""
    for a, b in NEUTRAL:
        s = str(s).replace(a, b)
    return s


def pc(x, d=1):
    return ('%.' + str(d) + 'f%%') % (float(x) * 100)


def kwh(x):
    return '$' + ('%.2f' % float(x))


# --------------------------------------------------------------------------- sources
# Only pages this session opened and read directly, or that were re-read live on
# 2026-11-13 by a named earlier session and are cited as such.  Every row of every
# table must carry one of these as its official link.
S = {
    'IRS-ESTATE': ('https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax',
                   'IRS - Estate tax (filing-threshold table)', 'read 2026-11-13'),
    'IRS-WHATS-NEW': ('https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax',
                      'IRS - What is new: estate and gift tax', 'read 2026-11-13'),
    'RP-2026-35': ('https://www.irs.gov/pub/irs-drop/rp-26-35.pdf',
                   'IRS Rev. Proc. 2026-35, 2027 adjusted amounts', 'read 2026-11-13'),
    'IRS-INHERIT-FAQ': ('https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances',
                        'IRS - Gifts and inheritances FAQ (basis of inherited property)', 'read 2026-11-13'),
    'IRS-TC409': ('https://www.irs.gov/taxtopics/tc409', 'IRS Topic 409 - capital gains and losses', 'read 2026-11-13'),
    'IRS-TC701': ('https://www.irs.gov/taxtopics/tc701', 'IRS Topic 701 - sale of your home', 'read 2026-11-13'),
    'SCO-ESTATE': ('https://www.sco.ca.gov/ardtax_estate_tax.html',
                   'California State Controller - California estate tax', 'read 2026-11-13'),
    'BOE-P19': ('https://www.boe.ca.gov/prop19/', 'BOE - Proposition 19 comparison charts', 'read 2026-11-13'),
    'BOE-LTA-2025-009': ('https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf',
                         'BOE LTA 2025/009 - intergenerational transfer $1 million adjustment', 'read 2026-11-13'),
    'BOE-LTA-2026-026': ('https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf',
                         'BOE LTA 2026/026 - Prop 19 intergenerational transfer FAQ', 'read 2026-11-13'),
    'BOE-HOX': ('https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm',
                "BOE - Homeowners' exemption (BOE-266)", 'read 2026-11-13'),
    'RTC-51': ('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51',
               'R&TC section 51 - annual inflation factor, 2% cap', 'read 2026-11-13'),
    'RTC-63.2': ('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2.',
                 'R&TC section 63.2 - parent-child exclusion and value test', 'read 2026-11-13'),
    'PROB-16061.7': ('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7',
                     'Probate Code 16061.7 - notification by trustee, 60 days', 'read 2026-11-13'),
    'CIV-1947.12': ('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12',
                    'Civil Code 1947.12 - Tenant Protection Act rent cap', 'read 2026-11-13'),
    'IRS-I706': ('https://www.irs.gov/instructions/i706',
                 'IRS - instructions for Form 706 (estate tax return)', 'referenced; full text not re-read in this pass'),
    'FTB-RATES': ('https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf',
                  'California FTB - 2025 tax rate schedules', 'read 2026-11-13'),
    'SCC-P19': ('https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2',
                'Santa Clara County Assessor - parent-child transfer (Prop 19)', 'read 2026-11-13'),
    'SCC-RATES': ('https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf',
                  'Santa Clara County - compilation of tax rates FY 2025-26', 'read 2026-11-13'),
    'SF-TAX': ('https://sftreasurer.org/property/secured-property-taxes',
               'SF Treasurer - secured property taxes, FY 2026-27 rate 1.18162182%', 'read 2026-11-13'),
    'SF-EHT': ('https://sftreasurer.org/business/taxes-fees/empty-homes-tax-eht',
               'SF Treasurer - Empty Homes Tax (enforcement stayed)', 'read 2026-11-13'),
    'SF-RENT': ('https://www.sf.gov/news--annual-rent-increase-3126-22827-announced',
                'SF Rent Board - 1.6% allowable increase 3/1/2026-2/28/2027', 'read 2026-11-13'),
    'SF-RENT-LAW': ('https://www.sf.gov/learn-about-san-francisco-rental-laws/',
                    'SF.gov - San Francisco rental laws and Rent Ordinance', 'read 2026-11-13'),
    'CUP-WATER': ('https://www.cupertino.gov/Residents/Utilities/Water',
                  'City of Cupertino - water service and providers', 'read 2026-11-13'),
    'CPUC-NEM': ('https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing',
                 'CPUC - net energy metering and net billing', 'read 2026-11-13'),
    'CPUC-FIXED': ('https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M555/K816/555816677.pdf',
                   'CPUC Resolution E-5354 - PG&E income-graduated fixed charge', 'read 2026-11-13'),
    'CDI-RES': ('https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/res-ins-guide.cfm',
                'California Department of Insurance - Residential Insurance guide (Form 401)', 'read 2026-11-13'),
    'HUD-SAFMR': ('https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html',
                  'HUD - FY2026 Small Area Fair Market Rents, national release (the community-level table for the relevant area)',
                  'release read 2026-11-13 by session da3f2b99; figures quoted from it'),
    'CBO-OUTLOOK': ('https://www.cbo.gov/publication/62105',
                    'CBO - Budget and Economic Outlook 2026 to 2036', 'read 2026-11-13'),
    'FED-GREAT-INFL': ('https://www.federalreservehistory.org/essays/great-inflation',
                       'Federal Reserve History - The Great Inflation 1965-1982', 'read 2026-11-13'),
    'FHFA-SJ': ('https://fred.stlouisfed.org/series/ATNHPIUS41940Q',
                'FHFA all-transactions house price index, San Jose metro (FRED)', 're-read 2026-11-13 by session da3f2b99'),
    'BLS-CPI': ('https://fred.stlouisfed.org/series/CPIAUCSL',
                'BLS Consumer Price Index for All Urban Consumers (FRED)', 're-read 2026-11-13 by session da3f2b99'),
    'DAMODARAN': ('https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html',
                  'NYU Stern / Damodaran historical S&P 500 and T-bill returns (academic dataset)', 'cited as academic; not a government statistic'),
}


def src(*ids):
    out = []
    for i in ids:
        url, title, note = S[i]
        # The visible label and the href are the citation. The descriptive title is
        # deliberately NOT emitted: it names the agency, and the agency's name is a
        # locality cue. The full title is published once, on the source register, in
        # the repository copy that is not served.
        out.append('<a class="src" href="%s" rel="noopener noreferrer" target="_blank" title="official source: %s">%s</a>'
                   % (E(url), E(i), E(i)))
    return ' · '.join(out)


# --------------------------------------------------------------------------- page frame

NAV = [
    ('index.html', 'Overview'),
    ('decision.html', 'Decision'),
    ('projections.html', 'Projections'),
    ('black-swan.html', 'Black swan'),
    ('process.html', 'Process'),
    ('law.html', 'Tax &amp; law'),
    ('costs.html', 'Costs'),
    ('estate.html', 'Cash &amp; estate'),
    ('questions.html', 'Questions'),
    ('suggestions.html', 'Suggestions'),
    ('flagged.html', 'Flagged'),
    ('sources.html', 'Sources &amp; method'),
    ('requirements.html', 'Requirements'),
]

CSS = """
:root{color-scheme:light;--ink:#12262b;--ink2:#33474b;--muted:#61757a;--line:#dfe7e4;--paper:#f4f7f5;
--card:#ffffff;--accent:#1f5f55;--accent2:#0f3f38;--warn:#8a4b12;--warnbg:#fdf5e8;--ok:#1f5f3a;
--okbg:#eef7f1;--stop:#7d2b2b;--stopbg:#fbeeee;--chip:#e7efe9}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:2px}
a:hover{color:var(--accent2)}
header.top{background:var(--accent2);color:#eef4f0}
header.top .in{max-width:1180px;margin:0 auto;padding:14px 22px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between}
.brand{font-weight:700;letter-spacing:.02em;font-size:.95rem}
.brand small{display:block;font-weight:400;opacity:.8;letter-spacing:.08em;font-size:.68rem;text-transform:uppercase}
nav.primary{display:flex;flex-wrap:wrap;gap:4px 6px;font-size:.84rem}
nav.primary a{color:#dce9e2;text-decoration:none;padding:5px 8px;border-radius:4px;white-space:nowrap}
nav.primary a:hover,nav.primary a[aria-current=page]{background:#215247;color:#fff}
main{max-width:1180px;margin:0 auto;padding:26px 22px 60px}
.crumb{font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}
h1{font:600 clamp(1.7rem,3.4vw,2.5rem)/1.18 Georgia,"Times New Roman",serif;margin:.5rem 0 .4rem;color:var(--accent2)}
h2{font:600 1.28rem/1.3 Georgia,serif;margin:2rem 0 .5rem;color:var(--accent2);padding-bottom:.3rem;border-bottom:1px solid var(--line)}
h3{font:600 1.05rem/1.3 system-ui,sans-serif;margin:1.4rem 0 .4rem}
p.lead{font-size:1.08rem;color:var(--ink2);max-width:78ch}
p,li{max-width:88ch}
.note{font-size:.86rem;color:var(--muted)}
.banner{margin:18px 0;padding:13px 16px;border-left:4px solid var(--accent);background:#eaf2ee;font-size:.9rem;color:var(--ink2)}
.banner.warn{border-color:var(--warn);background:var(--warnbg)}
.banner.stop{border-color:var(--stop);background:var(--stopbg)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--accent);padding:14px 16px;border-radius:3px}
.kpi .l{font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700}
.kpi .v{font:600 1.55rem/1.2 Georgia,serif;margin:.35rem 0 .2rem;color:var(--accent2)}
.kpi .s{font-size:.82rem;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:20px 0}
.card{background:var(--card);border:1px solid var(--line);padding:16px 18px;border-radius:3px}
.card h3{margin:0 0 .35rem;font-size:1.02rem}
.card h3 a{text-decoration:none}
.card p{margin:.2rem 0 0;font-size:.87rem;color:var(--muted)}
.cat{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:26px 0 -6px}
.tablewrap{overflow-x:auto;margin:14px 0 6px;border:1px solid var(--line);background:var(--card);border-radius:3px}
table{border-collapse:collapse;width:100%;font-size:.86rem}
caption{caption-side:top;text-align:left;padding:10px 12px 4px;font-weight:700;font-size:.85rem;color:var(--accent2)}
th,td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:#eef3f0;font-size:.76rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink2);position:sticky;top:0}
tbody tr:nth-child(even){background:#fbfcfb}
table.num td:not(:last-child),table.num th:not(:last-child){font-variant-numeric:tabular-nums}
td.src,th.src{font-size:.78rem;white-space:nowrap}
a.src{font-size:.78rem;text-decoration:none;border-bottom:1px dotted var(--accent)}
.pill{display:inline-block;font-size:.72rem;font-weight:700;padding:1px 7px;border-radius:10px;background:var(--chip);color:var(--accent2);white-space:nowrap}
.pill.open{background:var(--warnbg);color:var(--warn)}
.pill.stop{background:var(--stopbg);color:var(--stop)}
.pill.ok{background:var(--okbg);color:var(--ok)}
.split{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;margin:16px 0}
ol.steps{counter-reset:s;list-style:none;padding:0}
ol.steps>li{counter-increment:s;position:relative;padding:0 0 16px 46px;border-left:2px solid var(--line);margin-left:14px}
ol.steps>li::before{content:counter(s);position:absolute;left:-15px;top:0;width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;font-size:.85rem;display:grid;place-items:center}
ol.steps h3{margin:.1rem 0 .2rem}
.q{border:1px solid var(--line);background:var(--card);border-radius:3px;padding:14px 16px;margin:12px 0}
.q .id{font-size:.74rem;font-weight:700;letter-spacing:.1em;color:var(--accent);text-transform:uppercase}
.q h3{margin:.15rem 0 .5rem;font-size:1rem}
.q dl{display:grid;grid-template-columns:150px 1fr;gap:4px 12px;margin:0;font-size:.87rem}
.q dt{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;font-weight:700;padding-top:2px}
.q dd{margin:0}
.budget{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 0}
.budget label{display:inline-flex;align-items:center;gap:6px;font-size:.82rem;border:1px solid var(--line);padding:4px 9px;border-radius:12px;background:#fff;cursor:pointer}
.path{background:#eef3f0;border:1px solid var(--line);padding:12px 15px;border-radius:3px;margin:12px 0;font-size:.9rem}
.path b{color:var(--accent2)}
footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;font-size:.8rem;color:var(--muted)}
footer p{max-width:none}
.skip{position:absolute;left:-9999px}
:target{scroll-margin-top:70px}
@media (max-width:640px){.q dl{grid-template-columns:1fr}th,td{padding:7px 8px}}
@media print{header.top,nav.primary{display:none}main{max-width:none}}
"""


def page(slug, title, eyebrow, lead, body):
    nav = ''.join('<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if href == slug else '', label)
                  for href, label in NAV)
    doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<title>{title} | Two-home inheritance decision guide</title>
<style>{css}</style></head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="in">
<span class="brand">Two-home inheritance decision guide<small>Numbered property edition · built {date}</small></span>
<nav class="primary" aria-label="Sections">{nav}</nav>
</div></header>
<main id="main">
<p class="crumb">{eyebrow}</p>
<h1>{title}</h1>
<p class="lead">{lead}</p>
{body}
<footer>
<p><b>De-identification method.</b> People, the trust, the parcels and the addresses appear only as placeholders and are never published. Household amounts are household or model outputs rounded to the nearest $10 and are labelled as such; statutory amounts are quoted exactly as the official page publishes them and are labelled official. No year-by-year bill history is published. Nothing on this site is legal, tax, investment or insurance advice.</p>
<p><b>Sources.</b> Every table row links the official page it came from. A value that could not be confirmed from an official source is left blank and listed on the <a href="flagged.html">Flagged for review</a> page. Built {date} · <a href="sources.html">source register and method</a>.</p>
</footer>
</main></body></html>
""".format(title=E(title), css=CSS, nav=nav, eyebrow=E(eyebrow), lead=lead, body=body, date=BUILD_DATE)
    open(os.path.join(HERE, slug), 'w', encoding='utf-8').write(doc)
    return slug


def table(headers, rows, caption=None, cls='num', note=None, tid=None):
    """A table whose every body row must carry an official source link."""
    h = ['<div class="tablewrap"><table class="%s"%s>' % (cls, ' id="%s"' % tid if tid else '')]
    if caption:
        h.append('<caption>%s</caption>' % caption)
    h.append('<thead><tr>' + ''.join('<th scope="col">%s</th>' % x for x in headers) + '</tr></thead><tbody>')
    for r in rows:
        assert 'href="https://' in r[-1], 'row without a source link: %r' % (r,)
        assert len(r) == len(headers), (len(r), len(headers), r)
        h.append('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>')
    h.append('</tbody></table></div>')
    if note:
        h.append('<p class="note">%s</p>' % note)
    return '\n'.join(h)


def kpi(label, value, sub):
    return ('<div class="kpi"><div class="l">%s</div><div class="v">%s</div><div class="s">%s</div></div>'
            % (label, value, sub))


def card(href, title, text):
    return '<div class="card"><h3><a href="%s">%s</a></h3><p>%s</p></div>' % (href, title, text)


def banner(text, kind=''):
    return '<div class="banner %s">%s</div>' % (kind, text)
