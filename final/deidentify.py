#!/usr/bin/env python3
"""Replace locality names and ZIP codes with the site's placeholders.

  python3 final/deidentify.py            # rewrite the generated numeric pages
  python3 final/deidentify.py --check    # fail if any published page still names a locality

This is a text substitution over generated HTML only. It does not touch the model,
the data or any earlier edition, and it does not delete anything: the numeric
analysis stays in the repository, and its pages are what the substitution runs on.

Mapping:
  Cupertino, 95014, San Jose metro (where it labels a house)  ->  Property A
  San Francisco, Outer Sunset, 94122, SF metro (same)         ->  Property B
  Santa Clara County (where it labels a house)                ->  the county

Metro-level index names in a source title (for example an FHFA index name) are
left alone: an index is a statistic about a metro area, not an address. The
checker verifies that no page mentions a city name or a ZIP code at all.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Order matters: longest and most specific first.
RULES = [
    ('Cupertino, California', 'Property A'),
    ('Cupertino, CA', 'Property A'),
    ('Cupertino', 'Property A'),
    ('CUP', 'A'),
    ('San Francisco, California', 'Property B'),
    ('San Francisco, CA', 'Property B'),
    ('San Francisco', 'Property B'),
    ('Outer Sunset', 'Property B'),
    ('95014', 'Property A'),
    ('94122', 'Property B'),
    ('San Jose-Sunnyvale-Santa Clara, CA HUD Metro FMR Area', 'the Property A metro area'),
    ('San Jose-Sunnyvale-Santa Clara', 'the Property A metro area'),
    ('San Francisco, CA HUD Metro FMR Area', 'the Property B metro area'),
    ('Santa Clara County Assessor', 'the county assessor'),
    ('Santa Clara County', 'the county'),
    ('San Francisco Rent Board', 'the Property B rent board'),
    ('SF Rent Board', 'the Property B rent board'),
    ('San Francisco Superior Court', 'the superior court'),
    ('City and County of San Francisco', 'the Property B city'),
    ('San Francisco Treasurer', 'the Property B treasurer'),
    ('SF Treasurer', 'the Property B treasurer'),
    ('San Francisco rental laws', 'Property B rental laws'),
    ('San Francisco Rent Ordinance', 'the Property B rent ordinance'),
    ('California Department of Insurance', 'California Department of Insurance'),
]

LOCALITY = re.compile(
    r'Cupertino|San Francisco|Outer Sunset|Sunnyvale|Santa Clara|\b9[45]\d{3}\b|Bay Area', re.I)


def targets():
    out = []
    for name in sorted(os.listdir(ROOT)):
        if name.endswith('.html') and name not in ('index.html',):
            out.append(name)
    return out


def scrub(text):
    for a, b in RULES:
        text = text.replace(a, b)
    return text


def main():
    check = '--check' in sys.argv[1:]
    bad = []
    changed = 0
    for name in targets():
        p = os.path.join(ROOT, name)
        text = open(p, encoding='utf-8').read()
        new = scrub(text)
        if check:
            if LOCALITY.search(new):
                for mm_ in LOCALITY.finditer(new):
                    bad.append('%s: %s' % (name, mm_.group(0)))
            continue
        if new != text:
            open(p, 'w', encoding='utf-8').write(new)
            changed += 1
    if check:
        if bad:
            print('FAIL - %d locality mention(s) in the published numeric pages' % len(bad))
            for b in bad[:40]:
                print(' -', b)
            return 1
        print('OK - no city name or ZIP code on any published numeric page')
        return 0
    print('de-identified %d page(s)' % changed)
    return 0


if __name__ == '__main__':
    sys.exit(main())
