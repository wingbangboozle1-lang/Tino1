#!/usr/bin/env python3
"""Checker (session 07a57a05).  Exit code 1 on any failure.

  python3 final/check.py [site_dir]

1. every internal link and anchor resolves;
2. every table body row links to an official source;
3. every dollar figure is a multiple of $10 unless it is a listed official published figure;
4. no unrounded owner-supplied figure appears in any published or stored file (needs TINO1_PRIVATE_FIGURES, see below);
5. no street address, e-mail address, phone number or parcel-number pattern appears;
6. model self-tests (Proposition 19 formula against the county assessor's worked example; Property B never reassessed);
7. no git merge-conflict marker in any published page or any repository source file (these markers have reached the
   deployed site before - finding R38 - while every other check passed).
"""
import os, re, sys, html, json

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'site')
# official = any .gov host (federal, state, county, city) plus these public-agency hosts
OFFICIAL = ('gov', 'sftreasurer.org', 'fred.stlouisfed.org', 'sccassessor.org', 'valleywater.org', 'sfgov.legistar.com',
            'capropeforms.org', 'federalreservehistory.org')
OTHER_OK = ('github.com', 'pages.stern.nyu.edu')
# official published figures that are not multiples of $10 (each is quoted from the linked page)
OFFICIAL_ODD = {'38,915.87', '8,455.35', '14,217,212,455', '324,973', '1,176', '601', '1,044,586', '72,724', '371,479', '445,771', '742,953', '109,125', '208,325', '661,375',
                '56', '67', '76', '1.10', '0.55', '24.15'}
errors = []
# A git merge-conflict marker left in a file publishes as literal text. R38: a marker and a duplicated fragment were
# live on the published Verification page while every other check passed. Scan pages and repository files alike.
CONFLICT = re.compile(r'^<{7} |^>{7} |^={7}$', flags=re.M)


def err(*a):
    errors.append(' '.join(str(x) for x in a))


def host_ok(url, hosts):
    h = re.sub(r'^https?://', '', url).split('/')[0].lower()
    return any(h == d or h.endswith('.' + d) for d in hosts)


# The unrounded owner figures are never stored in this repository in any form. A hash of a 4- to 6-digit number is
# reversible in seconds, so the fingerprint file that used to be read here was itself an exposure and has been removed
# (session 8fc06844, K1). To run this scan, list the unrounded figures one per line in a file OUTSIDE the repository and
# set TINO1_PRIVATE_FIGURES to its path. Without it the scan is skipped and the result line says so.
_PF = os.environ.get('TINO1_PRIVATE_FIGURES', '')
FP = set(re.sub(r'\D', '', x) for x in open(_PF).read().split()) - {''} if _PF and os.path.isfile(_PF) else set()


def fingerprint_scan(name, text):
    if not FP:
        return
    # digits with any separator a figure has been written with so far: comma, optional comma in a pattern, underscore, space
    for tok in set(re.findall(r'(?<![\d.])\d{1,3}(?:(?:,\??|\\,|[_ \u00a0]|&#44;)\d{3})+(?![\d])|(?<![\d.])\d{4,7}(?![\d])', text)):
        if re.sub(r'\D', '', tok) in FP and (len(re.sub(r'\D', '', tok)) > 4 or not tok.isdigit()):
            err('PRIVACY: unrounded owner figure in', name)


PII = [
    (r'\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b', 'street address'),
    (r'[\w.+-]+@[\w-]+\.[\w.]+', 'e-mail address'),
    (r'\b\d{3}-\d{2}-\d{3}\b', 'parcel-number pattern'),
    (r'\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b', 'phone number'),
]

# ---------------------------------------------------------------------------------------------
# Unrounded owner-figure scan that needs NO secret (session 767b3f51).
#
# Until now the only real scan read the unrounded figures from a file outside the repository
# named by TINO1_PRIVATE_FIGURES (K1 rule). CI has no such file, so on every pull request the
# scan printed SKIPPED and exited 0. A page that accidentally published an unrounded owner
# figure would therefore have passed every gate. That is a silent gate, not a gate.
#
# This invariant needs no secret because it is a property of the site, not of the private
# numbers. Every owner-supplied dollar input is stored rounded to the nearest $10, so it can
# only ever be published ending in 0. County assessed values and tax bills, the values that
# identify a parcel, are not round numbers (480,000 / 96,000 / 6,000 are typical shapes). Therefore:
#
#   any 6-digit integer published in a page that does NOT end in 0, is not an official
#   published figure, and is not a model output, is a probable unrounded owner figure.
#
# Scoped to pages and to 6 digits on purpose. 4- and 5-digit integers collide heavily with
# index values, rates, years and file numbers (the independent run found only false positives
# at those lengths), and a noisy gate gets switched off. 6 digits is the range of a California
# assessed value and of a large tax bill.
#
# PRIVACY NOTE (session b3e23e79, 2026-11-13): this comment used to quote two real assessed values as
# examples. A public repository exposes every tracked file, so the examples are now invented round
# numbers. See flag P01 on public-guide/flagged.html.
# ---------------------------------------------------------------------------------------------
SAFE_6DIGIT = {
    '155782',   # "Session 155782b5" on the repo-review page: a session id, not a figure
    # California FTB 2025 tax rate schedule thresholds, tax brackets higher than the federal ones:
    '109125', '208325', '371479', '445771', '661375', '742953',
}


def load_model_numbers():
    """Every integer the model produced, so a legitimate model output is never flagged."""
    nums = set()
    p = os.path.join(HERE, 'out', 'model.json')
    if not os.path.isfile(p):
        return nums

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, bool):
            return
        elif isinstance(o, (int, float)):
            nums.add(int(round(abs(o))))

    walk(json.load(open(p)))
    return nums


def scan_unrounded_pages(pages, raw):
    """Fail on a published integer that looks like an unrounded owner figure. No secret needed."""
    model_nums = load_model_numbers()
    for p in pages:
        t = raw[p]
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
        # normalise thousands separators first: "480,000" must be tested as 480000
        text = re.sub(r'(?<=\d)[, _\u00a0](?=\d{3}(?!\d))', '', text)
        for tok in sorted(set(re.findall(r'(?<![\d.])\d{6}(?![\d.])', text))):
            if tok in SAFE_6DIGIT or tok in OFFICIAL_ODD:
                continue
            if int(tok) % 10 == 0:          # owner inputs are stored rounded to $10
                continue
            if int(tok) in model_nums:      # a legitimate model output
                continue
            err('PRIVACY: probable unrounded owner figure in', p, '-', tok)
    return model_nums


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
        if CONFLICT.search(t):
            err(p, 'merge conflict marker published on the page')
        fingerprint_scan(p, text)
    for f in os.listdir(SITE):
        if not f.endswith('.html') and os.path.isfile(os.path.join(SITE, f)):
            fingerprint_scan(f, open(os.path.join(SITE, f), encoding='utf-8', errors='ignore').read())
    n_safe = len(scan_unrounded_pages(pages, raw))
    return len(pages), n_rows, n_links, n_money, n_safe


def check_repo_files():
    for root, _, files in os.walk(HERE):
        if '__pycache__' in root or os.path.abspath(root).startswith(os.path.join(HERE, 'site')):
            continue
        for f in files:
            if f == 'privacy_fingerprints.txt' or f.endswith('.pyc'):
                continue
            data = open(os.path.join(root, f), encoding='utf-8', errors='ignore').read()
            rel = os.path.relpath(os.path.join(root, f), HERE)
            if CONFLICT.search(data):
                err(rel, 'merge conflict marker in a repository source file')
            fingerprint_scan(rel, data)


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
    for k in ('cup_value', 'cup_assessed', 'cup_tax_2025', 'sf_value', 'sf_assessed', 'sf_tax_2025', 'sf_rent_2units', 'dc_cup', 'dc_sf'):
        if M.P[k] % 10:
            err('MODEL: owner input not rounded to $10:', k)
    return len(paths)


if __name__ == '__main__':
    npages, nrows, nlinks, nmoney, nsafe = check_site()
    check_repo_files()
    npaths = check_model()
    if errors:
        print('FAIL - %d problem(s)' % len(errors))
        kinds = {}
        for x in errors:
            for k in ('row without an official source link', 'not rounded to $10', 'broken internal link', 'broken anchor',
                      'non-official domain', 'PRIVACY', 'possible', 'robots', 'non-https', 'empty cell', 'MODEL', 'merge conflict marker'):
                if k in x:
                    kinds[k] = kinds.get(k, 0) + 1
        print('   by kind:', kinds)
        for x in errors[:int(os.environ.get('SHOW', '80'))]:
            print(' -', x)
        sys.exit(1)
    print('OK - %d pages, %d table rows each with an official link, %d links, %d dollar figures rounded to $10, %s, '
          '6-digit scan against %d model numbers clean, model self-tests passed on %d paths'
          % (npages, nrows, nlinks, nmoney,
             'secret-list scan: none found' if FP else 'secret-list scan SKIPPED, see the secretless scan',
             nsafe, npaths))
