"""Shared row-classification rule for the superseded-edition close-out (session 95383689).

A legacy table data row is COMPLIANT when either:
  (a) it links to an official source page (host list below), or
  (b) it carries an explicit non-verification label (regex LABEL below), i.e. the
      value is declared an owner figure, an assumption, a model output, a derived
      figure or otherwise unverified - the owner's rule for values that have no
      official source: flag them, never invent a source.

Anything else counts as WORK and must be given (a) or (b) before the pass is done.
"""
import re

# Official hosts: .gov covers federal/state/city/county domains; the rest are the
# public agencies and utilities whose own sites publish the official figures used
# in these editions (same list as final/check.py plus the utility/agency domains
# the legacy editions already cite).
OFFICIAL_HOSTS = (
    'gov',                      # any *.gov (irs.gov, boe.ca.gov, bls.gov, leginfo..., govinfo.gov, courts.ca.gov)
    'sftreasurer.org',
    'sccassessor.org',
    'sfassessor.org',           # redirects to www.sf.gov/departments--assessor-recorder (read 2026-11-11)
    'fred.stlouisfed.org',      # FHFA/CPI series hosted by the Federal Reserve Bank of St. Louis
    'valleywater.org',
    'sfgov.legistar.com',
    'capropeforms.org',
    'sccgov.org',               # Santa Clara County (payments portal)
    'sfpuc.org',                # San Francisco Public Utilities Commission
    'pge.com',                  # Pacific Gas & Electric (utility of record for its own tariffs)
    'sjwater.com',              # San Jose Water Company (retail supplier)
    'nber.org',                 # NBER business-cycle dating (non-profit research, official chronology)
    'freddiemac.com',           # Freddie Mac (publisher of the PMMS mortgage-rate series)
    'naic.org',                 # National Association of Insurance Commissioners (industry standard-setter)
    'sfplanning.org',           # San Francisco Planning (property information map)
    'earthquakeauthority.com',  # California Earthquake Authority (state-created insurer)
    'pages.stern.nyu.edu',      # academic returns data (listed OK by final/check.py)
)

# Rows that already declare themselves non-verified need no official link.
LABEL = re.compile(
    r'unverified|flagged|assumption|user-supplied|owner[- ]reported|owner figure|'
    r'placeholder|withheld|estimate|model output|model assumption|'
    r'needs (review|quote|bill)|no official source|industry rule|rule of thumb|'
    r'qualitative|owner statement|user statement|derived|same\b|calc\b|'
    r'projections\b|private\b|baysano|owner-provided|user-provided|'
    r'commercial estimate|non-official|status row|checklist|'
    r'user range|owner:|owner\b.*reported|\bEst\.?\b|'
    r'rounding convention|sum of flagged|total of flagged|'
    r'carried from|citation in text|unverified citation|'
    r'market history|index provider|search summar',
    re.I,
)


def host_ok(url: str) -> bool:
    h = re.sub(r'^https?://', '', url).split('/')[0].lower()
    return any(h == d or h.endswith('.' + d) for d in OFFICIAL_HOSTS)


def row_state(row_html: str) -> str:
    """'sourced' | 'labelled' | 'work'"""
    urls = re.findall(r'href="(https?://[^"]+)"', row_html)
    if any(host_ok(u) for u in urls):
        return 'sourced'
    if LABEL.search(row_html):
        return 'labelled'
    return 'work'


def strip_tags(s: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()
