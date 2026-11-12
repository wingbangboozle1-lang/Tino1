"""Validate the bounded public edition. This is not a whole-repo privacy audit."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re

ROOT = Path(__file__).parent/'public'
NAV = {'index.html','decision.html','projection.html','stress.html','process.html','law.html','costs.html','questions.html','suggestions.html','suggestions-detail.html','flagged.html'}
FILES = NAV | {'style.css'}
SOURCES = {s['url'] for s in json.loads((ROOT.parent/'research.json').read_text())['sources'].values()}


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

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        assert tag not in {'script','iframe','object','embed','form','input','video','audio'}, tag
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
    actual = {p.name for p in ROOT.iterdir() if p.is_file()}
    assert actual == FILES, f'Unexpected public files: {actual ^ FILES}'
    assert not any(p.is_dir() for p in ROOT.iterdir()), 'Unexpected public directory'
    pages = {}
    for name in sorted(NAV):
        text = (ROOT/name).read_text()
        assert 'noindex,nofollow' in text and 'no-referrer' in text
        assert 'Content-Security-Policy' in text
        assert 'CHECKED 12 NOV 2026' in text
        # Defense in depth against known rounded household signatures. Not a claim
        # that these tokens capture all possible identifying combinations/history.
        for token in ('3,100,000','1,800,000','550,540','539,740','114,250','7,150','85,800','94122','95014'):
            assert token not in text, f'Household signature in {name}'
        for amount in re.findall(r'\$([\d,]+)(?![\d,])', text):
            assert int(amount.replace(',','')) % 10 == 0, (name,amount)
        p = Check(); p.feed(text)
        assert p.headings == 1 and p.current == 1 and p.captions == p.tables
        pages[name] = p
    for name,p in pages.items():
        for target,fragment in p.links:
            target = target or name
            assert target in FILES, (name,target)
            if fragment: assert target in pages and fragment in pages[target].ids, (name,target,fragment)
    css = (ROOT/'style.css').read_text()
    assert '@import' not in css and 'url(' not in css, 'Remote CSS resource'
    print(f'PASS: {len(NAV)} public pages, {sum(p.rows for p in pages.values())} official-context-linked data rows, '
          'captions, anchors, local resources, $10 display rounding and known household-signature checks. '
          'Not a privacy audit of Git history or a verification of synthetic assumptions.')


if __name__ == '__main__': main()
