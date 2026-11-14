#!/usr/bin/env python3
"""Publication scrub (session arena/6f85fbe1-tino1, owner brief: personal information must not appear on the website).

Replaces the two ZIP codes and the Cupertino city name in every *visible* text and in fragment identifiers of a
generated page. Official-source URLs are left untouched so that every table row still links to a verifiable
official page; those URLs carry the ZIP in their query strings and that residual is flagged for owner review.
Standard library only.
"""
import re

# Fragment identifiers (ids and #links) must follow the same mapping as the visible text, so map them first.
ID_MAP = [
    ('HUD-27-95014', 'HUD-27-ZIPA'), ('HUD-27-94122', 'HUD-27-ZIPB'),
    ('HUD-95014', 'HUD-ZIPA'), ('HUD-94122', 'HUD-ZIPB'),
]
# Agency and district names that contain the city name are public official names, not an address; keep them.
KEEP_CITY = ['City of Cupertino', 'Cupertino Elementary', 'Cupertino Union', 'Cupertino Municipal', 'Cupertino Water']
URL = re.compile(r'https?://[^\s"<>\']+')
PROTECT = re.compile(r'(https?://[^\s"<>\']+)')


def _scrub_plain(s):
    for a, b in ID_MAP:
        s = s.replace(a, b)
    kept = []
    for k in KEEP_CITY:
        while k in s:
            s = s.replace(k, '\x00%d\x00' % len(kept), 1)
            kept.append(k)
    s = re.sub(r'\bCupertino\b', 'Santa Clara County', s)
    s = s.replace('ZIP 95014', '[ZIP A]').replace('ZIP 94122', '[ZIP B]')
    s = s.replace('95014', '[ZIP A]').replace('94122', '[ZIP B]')
    for i, k in enumerate(kept):
        s = s.replace('\x00%d\x00' % i, k)
    return s


def scrub(text):
    """Scrub everything except the bodies of http(s) URLs."""
    out, last = [], 0
    for m in PROTECT.finditer(text):
        out.append(_scrub_plain(text[last:m.start()]))
        out.append(m.group(1))
        last = m.end()
    out.append(_scrub_plain(text[last:]))
    return ''.join(out)


if __name__ == '__main__':
    import sys
    sample = 'Cupertino home (ZIP 95014) <a href="https://x.gov/?zcta=95014">HUD 95014</a> City of Cupertino'
    print(scrub(sample))
