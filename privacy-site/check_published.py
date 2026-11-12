"""Fail closed if Jekyll publishes anything outside the allowlist, or if a published page has a broken local link.

Usage: python3 privacy-site/check_published.py _site

Session 1e0d3aeb (K3): the published edition is the current root edition (see _config.yml).
"""
from pathlib import Path
import re
import sys
from html.parser import HTMLParser

ROOT_DIR = Path(__file__).resolve().parent.parent
site = Path(sys.argv[1])
CURRENT = ['index.html', 'decision.html', 'projections.html', 'black-swan.html', 'process.html', 'law.html',
           'estate-cash.html', 'costs.html', 'flagged.html', 'sources.html', 'requirements.html', 'review.html',
           'versions.html', 'style.css', 'app.js']
expected = set(CURRENT)
actual = {str(p.relative_to(site)) for p in site.rglob('*') if p.is_file()}
assert actual == expected, f'Unexpected or missing published files: {sorted(actual ^ expected)}'
for name in CURRENT:
    assert (site / name).read_bytes() == (ROOT_DIR / name).read_bytes(), f'Content changed by Jekyll: {name}'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ('href', 'src') and v:
                self.out.append(v)


broken = []
for name in CURRENT:
    if not name.endswith('.html'):
        continue
    parser = Links()
    parser.feed((site / name).read_text(encoding='utf-8'))
    for u in parser.out:
        if re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|#|mailto:)', u, flags=re.I):
            continue                      # external link or in-page anchor
        target = u.split('#')[0].split('?')[0]
        if target == '' or not (site / target).is_file():
            broken.append((name, u))
assert not broken, f'Broken local links on the published site: {broken}'
print(f'PASS: exact publication allowlist, {len(actual)} files, no broken local links')
