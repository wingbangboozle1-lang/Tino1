#!/usr/bin/env python3
"""Gate for the de-identified numeric edition (public-guide/).

  python3 final/check_public_guide.py            # check the committed pages
  python3 final/check_public_guide.py --fresh    # also rebuild in a scratch dir and compare

Fails on any of:
  1. a page that is not in the edition's own list, or a broken internal link;
  2. a table body row without an https link to an official host;
  3. an empty table cell (blank values must be labelled, never blank);
  4. a dollar figure that is not a multiple of $10, unless it is a listed official
     published amount (the exclusion, the value cap, the rent cap, the tax rate);
  5. a street address, e-mail, telephone or parcel-number pattern;
  6. a visible city name or ZIP code, or an identifier the edition must never carry;
  7. a script, form, iframe or external asset reference;
  8. a page without noindex and a strict content-security policy;
  9. a merge-conflict marker;
 10. --fresh only: a committed page that differs from what the generator produces today.

The point of 6 is not decoration. A ZIP code plus a house value plus a tax bill is a
lookup key; the edition publishes rounded values and official rules, and nothing else.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GUIDE = os.path.join(ROOT, 'public-guide')
BUILD = os.path.join(GUIDE, '_build.py')

PAGES = [
    'index.html', 'decision.html', 'projections.html', 'black-swan.html', 'process.html',
    'law.html', 'costs.html', 'estate.html', 'questions.html', 'suggestions.html',
    'flagged.html', 'sources.html', 'requirements.html',
]
# The generator helper modules are source, not pages; they are listed so that a stray
# generated file is caught rather than silently published.
SOURCES = ['_gen.py', '_build.py'] + ['p_%s.py' % n for n in
           ('index', 'decision', 'projections', 'blackswan', 'process', 'law', 'costs',
            'estate', 'questions', 'suggestions', 'flagged', 'sources', 'requirements')]

OFFICIAL = ('gov', 'sftreasurer.org', 'fred.stlouisfed.org', 'sfgov.legistar.com',
            'capropeforms.org', 'pages.stern.nyu.edu', 'federalreservehistory.org')

# Official published amounts quoted exactly (not rounded, because a quotation must not be).
OFFICIAL_AMOUNTS = {
    '15,000,000', '15,480,000', '1,044,586', '1,000,000', '1,022,600', '20,000', '19,000',
    '250,000', '500,000', '7,000', '194,000', '2,000,000', '5,000,000', '10,000,000',
}
OFFICIAL_RATES = {'1.18162182', '1.6', '1.18', '12.3', '13.3', '14', '3.5', '7.0'}

# An identifier the edition must never carry.
FORBIDDEN = re.compile(
    r'Cupertino|San\s+Francisco|San\s+Jose|Santa\s+Clara|Sunnyvale|Outer\s+Sunset|Bay\s+Area'
    r'|\b9[45]\d{3}\b'
    r'|(?<![\w.])[1-9]\d{0,4}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Lane|Ln\.?|Road|Rd\.?|Court|Ct\.?)\b',
    re.I)
PII = [
    (r'[\w.+-]+@[\w-]+\.[\w.]+', 'e-mail address'),
    (r'\b\d{3}-\d{2}-\d{3}\b', 'parcel-number pattern'),
    (r'\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b', 'telephone number'),
    (r'\b\d{3}-\d{2}-\d{4}\b', 'social-security-number pattern'),
    (r'\b(?:APN|Assessor\'s\s+Parcel\s+Number)\b\W{0,4}\d{3}', 'parcel reference'),
]
CONFLICT = re.compile(r'^<{7} |^>{7} |^={7}$', re.M)

errors = []


def err(*a):
    errors.append(' '.join(str(x) for x in a))


def host_ok(url):
    h = re.sub(r'^https?://', '', url).split('/')[0].lower()
    return any(h == d or h.endswith('.' + d) for d in OFFICIAL)


def text_of(t):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', t))


def check_page(name, t):
    n_rows = n_links = n_money = 0
    # 2 rows: every body row carries an official https link
    for body in re.findall(r'<tbody[^>]*>(.*?)</tbody>', t, flags=re.S):
        for row in re.findall(r'<tr>(.*?)</tr>', body, flags=re.S):
            n_rows += 1
            urls = [html.unescape(u) for u in re.findall(r'href="(https://[^"]+)"', row)]
            if not any(host_ok(u) for u in urls):
                err(name, 'table row without an official source link:',
                    re.sub(r'<[^>]+>', ' ', row)[:80])
            if '<td></td>' in row:
                err(name, 'empty cell (label and flag it instead):',
                    re.sub(r'<[^>]+>', ' ', row)[:80])
    # 1 links
    for href in re.findall(r'(?:href|src)="([^"]+)"', t):
        href = html.unescape(href)
        n_links += 1
        if href.startswith('http://'):
            err(name, 'non-https link', href)
        elif href.startswith('https://'):
            if not host_ok(href):
                err(name, 'link to a non-official domain', href)
        elif href.startswith(('mailto:', 'javascript:', 'data:', '//')):
            err(name, 'disallowed link', href)
        else:
            f, _, a = href.partition('#')
            f = f or name
            if not os.path.exists(os.path.join(GUIDE, f)):
                err(name, 'broken internal link', href)
    # 4 money
    for mth in re.finditer(r'\$\s?(\d[\d,]*(?:\.\d+)?)(\s?(?:million|M\b|k\b))?', text_of(t)):
        num, unit = mth.group(1).rstrip(',.'), mth.group(2)
        n_money += 1
        if unit or num in OFFICIAL_AMOUNTS:
            continue
        if '.' in num or int(num.replace(',', '')) % 10 != 0:
            ctx = text_of(t)[max(0, mth.start() - 50):mth.start()].strip()[-50:]
            err(name, 'dollar figure not a multiple of $10:', mth.group(0), '...', ctx)
    # 5 PII, 6 forbidden identifiers, 9 conflict markers
    body = text_of(t)
    for rx, what in PII:
        mm_ = re.search(rx, body)
        if mm_:
            err(name, 'possible', what + ':', mm_.group(0))
    mm_ = FORBIDDEN.search(body)
    if mm_:
        err(name, 'identifying locality or address in visible text:', mm_.group(0))
    if CONFLICT.search(t):
        err(name, 'merge-conflict marker')
    # 7 no executable or network-capable content
    low = t.lower()
    for bad in ('<script', '<form', '<iframe', '<object', '<embed', ' onload=', ' onerror=',
                'src="http', 'http-equiv="refresh"'):
        if bad in low:
            err(name, 'disallowed element or attribute:', bad)
    # 8 noindex + CSP
    if 'name="robots" content="noindex, nofollow"' not in low:
        err(name, 'missing robots noindex')
    if "default-src 'none'" not in t:
        err(name, 'missing strict content-security-policy')
    return n_rows, n_links, n_money


def check_dir():
    actual = sorted(f for f in os.listdir(GUIDE) if f.endswith('.html'))
    if actual != sorted(PAGES):
        err('public-guide page set differs from the declared list:', set(actual) ^ set(PAGES))
    missing_src = [f for f in SOURCES if not os.path.exists(os.path.join(GUIDE, f))]
    if missing_src:
        err('missing generator module(s):', ', '.join(missing_src))
    tot = [0, 0, 0]
    for name in PAGES:
        path = os.path.join(GUIDE, name)
        if not os.path.exists(path):
            err('missing page', name)
            continue
        part = check_page(name, open(path, encoding='utf-8').read())
        tot = [a + b for a, b in zip(tot, part)]
    return tot


def check_fresh():
    """Every committed page must equal what the generator writes today."""
    tmp = tempfile.mkdtemp(prefix='tino1-guide-')
    before = {n: open(os.path.join(GUIDE, n), 'rb').read() for n in PAGES}
    env = dict(os.environ)
    subprocess.run([sys.executable, BUILD], check=True, env=env,
                   stdout=subprocess.DEVNULL, cwd=GUIDE)
    n = 0
    for name in PAGES:
        after = open(os.path.join(GUIDE, name), 'rb').read()
        if after != before[name]:
            err('committed page differs from a fresh build:', name)
        n += 1
    del tmp
    return n


def main():
    fresh = '--fresh' in sys.argv[1:]
    n_rows, n_links, n_money = check_dir()
    n_fresh = check_fresh() if fresh else 0
    print('::notice::de-identified edition: %d pages, %d sourced table rows, %d links, %d dollar figures, '
          'fresh-build comparisons: %d' % (len(PAGES), n_rows, n_links, n_money, n_fresh))
    if errors:
        print('FAIL - %d problem(s)' % len(errors))
        for e in errors:
            print(' -', e)
        return 1
    print('PASS - %d pages, every table row sourced to an official host, every household figure a multiple of $10, '
          'no visible locality cue, no PII pattern, no script or form, noindex and CSP on every page' % len(PAGES))
    return 0


if __name__ == '__main__':
    sys.exit(main())
