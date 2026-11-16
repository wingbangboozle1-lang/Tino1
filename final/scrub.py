#!/usr/bin/env python3
"""Publication scrub (owner brief: personal information must not appear on the website).

Everything here replaces *identifying geography* in the text a reader sees, and leaves
official-source URLs untouched, so that every table row still links to a verifiable
official page. Two exposures are handled:

  1. The two ZIP codes (session 6f85fbe1). They survive only inside official URLs - a
     HUD rent calculator is addressed by ZIP - and that residual is flagged for the owner.

  2. City and county names (session 3adb817a). The published analysis names no city,
     no county, no ZIP and no neighbourhood. The two places involved are called
     **Jurisdiction A** - the county, and the city inside it, where Property A sits -
     and **Jurisdiction B** - the city and county where Property B sits. Official bodies
     are named by role ("the assessor of Jurisdiction A"), and the local house-price
     index is named by the property it belongs to ("Property A metro"). Both labels are
     defined in the page footer and on the glossary page.

`scrub()` protects the bodies of http(s) URLs and rewrites everything else: visible
text, link titles, and fragment identifiers. Standard library only.
"""
import re

# Fragment identifiers (ids and #links) must follow the same mapping as the visible text.
ID_MAP = [
    ('HUD-27-95014', 'HUD-27-ZIPA'), ('HUD-27-94122', 'HUD-27-ZIPB'),
    ('HUD-95014', 'HUD-ZIPA'), ('HUD-94122', 'HUD-ZIPB'),
]

A = 'Jurisdiction A'   # the county, and the city inside it, where Property A sits
B = 'Jurisdiction B'   # the city and county where Property B sits

# Order matters: the longest and most specific phrase is replaced first, so that
# "San Francisco Treasurer" becomes a role before "San Francisco" becomes a place.
LOC_MAP = [
    # --- official statistics named after a place -------------------------------------
    (r'San Jose-Sunnyvale-Santa Clara MSA', 'the metropolitan area that contains Property A'),
    (r'San Francisco-San Mateo-Redwood City MSAD?', 'the metropolitan area that contains Property B'),
    (r'NBC Bay Area', 'a local news outlet'),
    (r'Bay Area earthquake', 'regional earthquake'),
    (r'Bay Area M>', 'regional M>'),
    (r'Bay Area CPI-U', 'regional CPI-U'),
    (r'Bay Area consumer price', 'regional consumer-price'),
    (r'Bay Area quake', 'regional quake'),
    (r'Bay Area inflation|Bay Area CPI', 'regional inflation'),
    (r'San Francisco Bay Area|Bay Area', 'the region'),
    # --- offices and agencies, named by role -----------------------------------------
    (r'San Francisco Treasurer and Tax Collector', 'Treasurer and tax collector of ' + B),
    (r'San Francisco Treasurer', 'Treasurer of ' + B),
    (r'San Francisco Rent Board', 'Rent board of ' + B),
    (r'San Francisco Public Utilities Commission', 'Water and sewer utility of ' + B),
    (r'San Francisco Board of Supervisors', 'Legislature of ' + B),
    (r'Santa Clara County Controller-Treasurer', 'Controller-treasurer of ' + A),
    (r"Santa Clara County (?:Clerk-Recorder|Clerk-Recorder's office)", 'Clerk-recorder of ' + A),
    (r'Santa Clara Clerk-Recorder', 'Clerk-recorder of ' + A),
    (r'Santa Clara County Assessor', 'Assessor of ' + A),
    (r'Santa Clara Assessor', 'Assessor of ' + A),
    (r'Santa Clara tax rate book', 'Tax rate book of ' + A),
    (r'Santa Clara(?: County)? water', 'The ' + A + ' water'),
    # --- the two jurisdictions themselves --------------------------------------------
    (r'City and County of San Francisco', B),
    (r'Santa Clara County|Santa Clara', A),
    (r'San Francisco', B),
    (r'Cupertino Elementary', 'the elementary-school district'),
    (r'Cupertino Union', 'the unified school district'),
    (r'Cupertino Municipal', 'the municipal water system'),
    (r'City of Cupertino Water', 'Water service areas of the city in ' + A),
    (r'Cupertino Water', 'the water service areas of ' + A),
    (r'City of Cupertino', 'the city in ' + A),
    (r'[Cc]upertino', A),
    (r'San Jose Water Company', 'a neighbouring water company'),
    (r'San Jose', 'Property A metro'),
    # --- abbreviations and agency short names ----------------------------------------
    (r'SFPUC rates', 'Water and sewer rates of ' + B),
    (r'SFPUC Rate Fairness Board', 'Rate fairness board of the ' + B + ' water utility'),
    (r'SFPUC Rate Board', 'Rate board of the ' + B + ' water utility'),
    (r'SFPUC', 'the water and sewer utility of ' + B),
    (r'SFMTA Prop H', 'Proposition H parcel tax'),
    (r'SFMTA', 'the transit agency of ' + B),
    (r'SF rental laws', 'Rental laws of ' + B),
    (r'SF Treasurer', 'Treasurer of ' + B),
    (r'\bSF\b', B),
    (r'SJWC', 'the neighbouring water company'),
    (r'Cal Water|California Water Service', 'an investor-owned water company'),
    (r'Fremont Union High School District|Fremont Union High|Fremont Union bonds|Fremont Union|Fremont High', 'the high-school district'),
    (r'Foothill-De ?Anza', 'the community-college district'),
    (r'Santa Clara Valley Water|SCVWD', 'the valley water district'),
    (r'Midpen', 'the open-space district'),
    (r'VMC 2008', 'the 2008 medical-centre bond'),
    # --- bare official domains printed as text (URLs are protected, these are not) ----
    (r'asr\.santaclaracounty\.gov|santaclaracounty\.gov|sccassessor\.org', "the assessor's site"),
    (r'files\.santaclaracounty\.gov', "the county site"),
    (r'cupertino\.gov', "the city site"),
    (r'sftreasurer\.org', "the treasurer's site"),
    (r'sfmta\.com', "the transit agency's site"),
    (r'sfpuc\.gov', "the water utility's site"),
]

PROTECT = re.compile(r'(https?://[^\s"<>' + "'" + r']+)')
COMPILED = [(re.compile(rx), rep) for rx, rep in LOC_MAP]


# The mappings above are phrase-level, so an article can occasionally end up doubled
# ("60% of the the region inflation"). Tidied here rather than in the source text.
TIDY = [(re.compile(rx), rep) for rx, rep in [
    (r'\bthe the\b', 'the'),
    (r'\bof of\b', 'of'),
    (r'[^\S\n]+', ' '),   # collapse runs of blanks, but never join lines together
]]


def _scrub_plain(s):
    for a, b in ID_MAP:
        s = s.replace(a, b)
    s = s.replace('ZIP 95014', '[ZIP A]').replace('ZIP 94122', '[ZIP B]')
    s = s.replace('95014', '[ZIP A]').replace('94122', '[ZIP B]')
    for rx, rep in COMPILED:
        s = rx.sub(rep, s)
    for rx, rep in TIDY:
        s = rx.sub(rep, s)
    return s


def scrub(text):
    """Scrub everything except the bodies of http(s) URLs."""
    out, last = [], 0
    for m in PROTECT.finditer(text):
        out.append(_scrub_plain(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_scrub_plain(text[last:]))
    return ''.join(out)


if __name__ == '__main__':
    import sys
    sample = ('Cupertino home (ZIP 95014) <a href="https://x.gov/?zcta=95014">HUD 95014</a> '
              'City of Cupertino, Santa Clara County Assessor, San Francisco Rent Board, '
              'San Jose index 1976-2025')
    print(scrub(sample))
