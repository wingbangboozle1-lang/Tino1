"""Validate the bounded public edition. This is not a whole-repo privacy audit."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re

ROOT = Path(__file__).parent/'public'
NAV = {'index.html','decision.html','projection.html','stress.html','process.html','law.html','costs.html','questions.html','brief.html','glossary.html','suggestions.html','suggestions-detail.html','issues.html','flagged.html'}
FILES = NAV | {'style.css'}
REGISTRY = json.loads((ROOT.parent/'research.json').read_text())
SOURCES = {s['url'] for s in REGISTRY['sources'].values()}
# www.sfmta.com: the San Francisco Municipal Transportation Agency is a City and County department (official City site, not .gov); used for the Proposition H rate table.
OFFICIAL_PUBLISHED_RATES = {'129', '249', '65', '799', '392', '549', '969', '3,174', '34,999', '202,999', '177'}  # SFMTA Proposition H rate table and examples, plus the Controller's $177 million estimate, read 2026-11-16
# www.law.cornell.edu: non-government mirror of the U.S. Code, used only for IRC §1250 text (flagged 9B-F1 on the public Flagged page); the GPO copy was not retrieved on 2026-11-16.
REVIEWED_NON_GOV_HOSTS = {'docs.github.com', 'federalreservehistory.org', 'www.federalreservehistory.org', 'www.sfmta.com', 'www.sfelections.org', 'www.law.cornell.edu'}  # www.sfelections.org: Department of Elections results page (Proposition H count)
PII_PATTERNS = {
    'street address': r'\b\d{1,5}\s+[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+)?\s+(?:Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b',
    'email address': r'[\w.+-]+@[\w-]+\.[\w.-]+',
    'phone number': r'(?<!\d)(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?!\d)',
    'parcel-number pattern': r'\b\d{3}-\d{2}-\d{3}\b',
}


def pii_kinds(text):
    """Return only PII-pattern categories, never the matched value."""
    return [label for label, pattern in PII_PATTERNS.items() if re.search(pattern, text)]


class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_row = False
        self.header = False
        self.sourced = False
        self.rows = 0
        self.links = []
        self.ids = set()
        self.headings = 0
        self.current = 0
        self.tables = 0
        self.captions = 0
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        assert tag not in {'script','iframe','object','embed','form','video','audio'}, tag
        if tag == 'input':
            assert a.get('type') == 'radio', 'Only local radio review controls are allowed'
            assert 'form' not in a, 'Review controls must not be associated with a submitting form'
            name = a.get('name','')
            assert name == 'implementation-path' or name in {f'review-s{i}' for i in range(1,10)}, name
            allowed = {'privacy-guide','private-workspace','pause-pages','rounded-public'} if name == 'implementation-path' else {'adopt','hold','reject'}
            assert a.get('value') in allowed, f'Unexpected review choice: {a.get("value")}'
            self.inputs.append((name,a.get('value'), 'checked' in a))
        assert not any(k.startswith('on') for k in a), 'Inline event handler'
        if a.get('id'):
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
        if tag == 'h1': self.headings += 1
        if tag == 'table':
            assert a.get('data-kind') in {'verified','unverified','illustration'}
            self.tables += 1
        if tag == 'caption': self.captions += 1
        if tag == 'tr': self.in_row = True; self.header = False; self.sourced = False
        if self.in_row and tag == 'th': self.header = True
        if tag == 'a' and 'aria-current' in a: self.current += 1
        if tag in ('a','link','img'):
            u = a.get('href') or a.get('src')
            if not u: return
            parsed = urlparse(u)
            if parsed.scheme:
                assert tag == 'a' and u in SOURCES, f'Unreviewed external URL or remote asset: {u}'
                if self.in_row: self.sourced = True
            else:
                assert not parsed.netloc and not parsed.query and '..' not in unquote(parsed.path)
                self.links.append((unquote(parsed.path), parsed.fragment))

    def handle_endtag(self, tag):
        if tag == 'tr':
            if not self.header:
                assert self.sourced, 'Data row has no reviewed official-context link'
                self.rows += 1
            self.in_row = False


def main():
    landing_template = ROOT.parent/'landing.html'
    root_landing = ROOT.parent.parent/'index.html'
    assert landing_template.is_file(), 'Missing the figure-free front-door template'
    assert root_landing.is_file(), 'Missing the published front door'
    # The published front door is the generated decision dashboard (final/build.py) since
    # 2026-11-16. The figure-free template above is the fallback variant (suggestion G01)
    # and is checked here as a template only; the dashboard itself is checked by
    # final/check.py and final/check_published.py.
    landing_text = landing_template.read_text(encoding='utf-8')
    assert not pii_kinds(landing_text), 'Personal-data pattern in the figure-free front-door template'
    for token in ('Cupertino','San Francisco','95014','94122','3,100,000','1,800,000','7,150'):
        assert token.casefold() not in landing_text.casefold(), 'Known household signature/locality in root landing'
    for source in REGISTRY['sources'].values():
        parsed=urlparse(source['url'])
        host=(parsed.hostname or '').casefold()
        assert parsed.scheme=='https', f'Official source must use HTTPS: {source["url"]}'
        assert host.endswith('.gov') or host in REVIEWED_NON_GOV_HOSTS, \
            f'Unreviewed non-government source host: {host}'
    actual = {p.name for p in ROOT.iterdir() if p.is_file()}
    assert actual == FILES, f'Unexpected public files: {actual ^ FILES}'
    assert not any(p.is_dir() for p in ROOT.iterdir()), 'Unexpected public directory'
    pages = {}
    for name in sorted(NAV):
        text = (ROOT/name).read_text()
        assert 'noindex,nofollow' in text and 'no-referrer' in text
        assert 'Content-Security-Policy' in text
        assert 'SOURCE CHECKS <i></i> 12–16 NOV 2026' in text
        if name == 'flagged.html':
            # Keep the urgent exposure warning actionable and avoid implying that
            # a Pages update or ordinary delete commit erases GitHub history.
            for required in ('Priority 0 · exposure-containment checklist',
                             'Status: not completed.',
                             'Safe order of operations · no repository change is made by this checklist',
                             'This session has not changed repository visibility or rewritten history.',
                             'A normal delete commit leaves earlier Git objects in history.',
                             'Rewriting cannot erase clones, forks or third-party copies'):
                assert required in text, f'Missing or weakened P0 privacy guidance: {required}'
        pii = pii_kinds(text)
        assert not pii, f'Personal-data pattern(s) in {name}: {", ".join(pii)}'
        # Defense in depth against known rounded household signatures and location
        # cues. These checks cover only the public build, not Git history or every
        # possible inference from public context.
        for token in ('3,100,000','1,800,000','550,540','539,740','114,250','7,150','85,800','94122','95014'):
            assert token not in text, f'Household signature in {name}'
        for token in ('Cupertino','San Francisco','sftreasurer.org','sf.gov'):
            assert token.casefold() not in text.casefold(), f'Household-locality cue in {name}'
        for amount in re.findall(r'\$([\d,]+(?:\.\d+)?)(?![\d,])', text):
            if '.' in amount:
                # per-unit rates below $10 (for example $0.195 per square foot) are not household totals
                assert float(amount.replace(',', '')) < 10, (name, amount)
                continue
            # official published rates quoted from their own source page (SFMTA Proposition H table; not household figures)
            if amount in OFFICIAL_PUBLISHED_RATES:
                continue
            assert int(amount.replace(',','')) % 10 == 0, (name,amount)
        p = Check(); p.feed(text)
        assert p.headings == 1 and p.current == 1 and p.captions == p.tables
        pages[name] = p
    for name,p in pages.items():
        for target,fragment in p.links:
            target = target or name
            assert target in FILES, (name,target)
            if fragment: assert target in pages and fragment in pages[target].ids, (name,target,fragment)
        if name != 'suggestions.html':
            assert not p.inputs, f'Unexpected input controls outside Suggestions: {name}'
    controls=pages['suggestions.html'].inputs
    assert len(controls)==31, f'Expected nine review groups and four path choices, found {len(controls)} controls'
    selected={}
    for group,value,checked in controls:
        if checked: selected.setdefault(group,[]).append(value)
    assert selected.get('implementation-path')==['privacy-guide'], 'Privacy-first path must be the safe default'
    for i in range(1,10):
        assert selected.get(f'review-s{i}')==['hold'], f'Suggestion {i} must default to Hold'
    css = (ROOT/'style.css').read_text()
    assert '@import' not in css and 'url(' not in css, 'Remote CSS resource'
    print(f'PASS: {len(NAV)} public pages, {sum(p.rows for p in pages.values())} official-context-linked data rows, '
          'captions, anchors, local resources, PII-pattern checks, $10 display rounding and known household-signature checks. '
          'Not a privacy audit of Git history or a verification of synthetic assumptions.')


if __name__ == '__main__': main()
