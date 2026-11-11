#!/usr/bin/env python3
"""Checker (session 07a57a05).  Exit code 1 on any failure.

  python3 final/check.py [site_dir]

1. every internal link and anchor resolves;
2. every table body row links to an official source;
3. every dollar figure is a multiple of $10 unless it is a listed official published figure;
4. no fingerprint of an unrounded owner-supplied figure appears in any published or stored file;
5. no street address, e-mail address, phone number or parcel-number pattern appears;
6. model self-tests (Proposition 19 formula against the county assessor's worked example; Property B never reassessed).
"""
import os, re, sys, hashlib, html, json

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'site')
# official = any .gov host (federal, state, county, city) plus these public-agency hosts
OFFICIAL = ('gov', 'sftreasurer.org', 'fred.stlouisfed.org', 'sccassessor.org', 'valleywater.org', 'sfgov.legistar.com',
            'capropeforms.org')
OTHER_OK = ('github.com', 'pages.stern.nyu.edu')
# official published figures that are not multiples of $10 (each is quoted from the linked page)
OFFICIAL_ODD = {'14,217,212,455', '324,973', '1,176', '601', '1,044,586', '72,724', '371,479', '445,771', '742,953', '109,125', '208,325', '661,375',
                '56', '67', '76', '1.10', '0.55', '24.15'}
errors = []


def err(*a):
    errors.append(' '.join(str(x) for x in a))


def host_ok(url, hosts):
    h = re.sub(r'^https?://', '', url).split('/')[0].lower()
    return any(h == d or h.endswith('.' + d) for d in hosts)


FP = set(open(os.path.join(HERE, 'data', 'privacy_fingerprints.txt')).read().split())


def fingerprint_scan(name, text):
    for tok in set(re.findall(r'(?<![\d,.])\d{1,3}(?:,\d{3})+(?![\d,])|(?<![\d.])\d{5,7}(?![\d])', text)):
        if hashlib.sha256(('tino1:' + tok).encode()).hexdigest() in FP:
            err('PRIVACY: unrounded owner figure fingerprint in', name)


PII = [
    (r'\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b', 'street address'),
    (r'[\w.+-]+@[\w-]+\.[\w.]+', 'e-mail address'),
    (r'\b\d{3}-\d{2}-\d{3}\b', 'parcel-number pattern'),
    (r'\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b', 'phone number'),
]


def check_site():
    pages = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))
    if not pages:
        err('no pages in', SITE)
    ids = {}
    raw = {}
    for p in pages:
        raw[p] = open(os.path.join(SITE, p), encoding='utf-8').read()
        ids[p] = set(re.findall(r'\bid="([^"]+)"', raw[p]))
    n_rows = n_links = n_money = 0
    for p in pages:
        t = raw[p]
        # 1 links
        for href in re.findall(r'(?:href|src)="([^"]+)"', t):
            href = html.unescape(href)
            n_links += 1
            if href.startswith('http://'):
                err(p, 'non-https link', href)
            elif href.startswith('https://'):
                if not (host_ok(href, OFFICIAL) or host_ok(href, OTHER_OK)):
                    err(p, 'link to a non-official domain', href)
            elif href.startswith(('mailto:', 'javascript:', 'data:')):
                err(p, 'disallowed link', href)
            else:
                f, _, a = href.partition('#')
                f = f or p
                if not os.path.exists(os.path.join(SITE, f)):
                    err(p, 'broken internal link', href)
                elif a and f in ids and a not in ids[f]:
                    err(p, 'broken anchor', href)
        # 2 rows
        for body in re.findall(r'<tbody[^>]*>(.*?)</tbody>', t, flags=re.S):
            for row in re.findall(r'<tr>(.*?)</tr>', body, flags=re.S):
                n_rows += 1
                urls = re.findall(r'href="(https://[^"]+)"', row)
                if not any(host_ok(html.unescape(u), OFFICIAL) for u in urls):
                    err(p, 'table row without an official source link:', re.sub(r'<[^>]+>', ' ', row)[:90])
                if '<td></td>' in row:
                    err(p, 'empty cell (blank values must be labelled and flagged):', re.sub(r'<[^>]+>', ' ', row)[:90])
        # 3 money
        text = html.unescape(re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S))
        text = re.sub(r'<[^>]+>', ' ', text)
        for mth in re.finditer(r'\$\s?(\d[\d,]*(?:\.\d+)?)(\s?(?:million|M\b|k\b))?', text):
            num, unit = mth.group(1).rstrip(',.'), mth.group(2)
            n_money += 1
            if unit or num in OFFICIAL_ODD:
                continue
            if '.' in num or int(num.replace(',', '')) % 10 != 0:
                err(p, 'dollar figure not rounded to $10:', mth.group(0), '...', text[max(0, mth.start() - 40):mth.start()].strip()[-40:])
        # 5 PII
        for rx, what in PII:
            for mm_ in re.finditer(rx, text):
                err(p, 'possible', what + ':', mm_.group(0))
        if 'noindex' not in t:
            err(p, 'missing robots noindex')
        fingerprint_scan(p, text)
    for f in os.listdir(SITE):
        if not f.endswith('.html') and os.path.isfile(os.path.join(SITE, f)):
            fingerprint_scan(f, open(os.path.join(SITE, f), encoding='utf-8', errors='ignore').read())
    return len(pages), n_rows, n_links, n_money


def check_repo_files():
    for root, _, files in os.walk(HERE):
        if '__pycache__' in root or os.path.abspath(root).startswith(os.path.join(HERE, 'site')):
            continue
        for f in files:
            if f == 'privacy_fingerprints.txt' or f.endswith('.pyc'):
                continue
            fingerprint_scan(os.path.relpath(os.path.join(root, f), HERE), open(os.path.join(root, f), encoding='utf-8', errors='ignore').read())


def check_model():
    sys.path.insert(0, HERE)
    import model as M
    # county assessor's worked example: base 200,000; market 1,800,000; allowance 1,000,000 -> 800,000
    if M.prop19_taxable(200_000, 1_800_000, 1_000_000) != 800_000:
        err('MODEL: Proposition 19 formula does not reproduce the assessor example')
    if M.prop19_taxable(500_000, 1_200_000, 1_000_000) != 500_000:
        err('MODEL: Proposition 19 formula wrong below the limit')
    paths = [M.baseline_path()] + [M.replay_path(s) for s in range(1976, 2026)]
    for path in paths:
        rows, s = M.simulate(path, M.P)
        prev = None
        for r in rows:
            if prev and r['sf_assessed'] > prev * 1.0200001:
                err('MODEL: Property B assessed value rose more than 2% - it must never be reassessed')
            if r['sf_assessed'] > r['sf_value'] + 1e-6:
                err('MODEL: Property B assessed above market value')
            prev = r['sf_assessed']
            if r['year'] >= M.P['T'] and not (r['live_assessed'] <= r['rent_assessed'] + 1e-6):
                err('MODEL: lived-in assessed value above full reassessment')
        if s['sell_gain'] > 0:
            err('MODEL: sale right after a basis reset shows a taxable gain')
        if not (s['fbyv_T'] <= s['taxable_live_T'] <= s['fmv_T'] + 1e-6):
            err('MODEL: Proposition 19 value outside its bounds')
    for k in ('cup_value', 'cup_assessed', 'cup_tax_2025', 'cup_assessed_2025', 'sf_value', 'sf_assessed_2025', 'sf_tax_2025', 'sf_rent_2units'):
        if M.P[k] % 10:
            err('MODEL: owner input not rounded to $10:', k)
    return len(paths)


if __name__ == '__main__':
    n = check_site()
    check_repo_files()
    npaths = check_model()
    if errors:
        print('FAIL - %d problem(s)' % len(errors))
        kinds = {}
        for x in errors:
            for k in ('row without an official source link', 'not rounded to $10', 'broken internal link', 'broken anchor',
                      'non-official domain', 'PRIVACY', 'possible', 'robots', 'non-https', 'empty cell', 'MODEL'):
                if k in x:
                    kinds[k] = kinds.get(k, 0) + 1
        print('   by kind:', kinds)
        for x in errors[:int(os.environ.get('SHOW', '80'))]:
            print(' -', x)
        sys.exit(1)
    print('OK - %d pages, %d table rows each with an official link, %d links, %d dollar figures rounded to $10, privacy fingerprints clean, model self-tests passed on %d paths' % (n + (npaths,)))
