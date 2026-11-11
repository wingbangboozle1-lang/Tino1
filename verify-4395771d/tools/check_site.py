#!/usr/bin/env python3
"""
Checks the built site.  Exit code 0 only if every check passes.

  1. every internal link and anchor resolves
  2. every table body row carries a link to an official source,
     or is explicitly flagged as unverified with a link to the Flagged page
  3. every dollar amount of four digits or more is a multiple of $10,
     except a short list of exact figures published by the IRS, the BOE and the FTB
  4. privacy patterns: no street address, parcel number, e-mail address or phone number
  5. nothing is loaded from another server (no remote script, stylesheet, font or image)
  6. every page carries the full navigation

Run:  python3 verify-4395771d/tools/check_site.py [site_dir]
The check is rule-based on purpose: it holds no list of the owner's figures.
"""
import os, re, sys, html
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, '..', 'site')

OFFICIAL = ('irs.gov', 'boe.ca.gov', 'sco.ca.gov', 'leginfo.legislature.ca.gov', 'ftb.ca.gov', 'sos.ca.gov', 'sf.gov',
            'sftreasurer.org', 'santaclaracounty.gov', 'huduser.gov', 'cpuc.ca.gov', 'bls.gov', 'treasury.gov', 'cbo.gov',
            'stlouisfed.org', 'usgs.gov', 'oag.ca.gov', 'insurance.ca.gov')
ACADEMIC = ('stern.nyu.edu',)          # one academic dataset, labelled as such on the site
# exact official figures that are not multiples of $10 (IRS Rev. Proc. 2026-35, BOE LTA 2025/009, FTB 2025 schedules)
EXACT_OFFICIAL = {1044586, 661375, 72724, 371479, 445771, 742953, 145448, 742958, 891542, 1485906}

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.ids = set(); self.rows = []; self.remote = []
        self._in_tbody = 0; self._row = None; self.text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag == 'tbody': self._in_tbody += 1
        if tag == 'tr' and self._in_tbody: self._row = dict(links=[], text='', flagged=False)
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
            if self._row is not None: self._row['links'].append(a['href'])
        if tag == 'span' and self._row is not None and 'b-unverified' in a.get('class', ''):
            self._row['flagged'] = True
        if tag in ('script', 'img', 'iframe', 'source', 'video', 'audio') and a.get('src', '').startswith(('http', '//')):
            self.remote.append(a['src'])
        if tag == 'link' and a.get('href', '').startswith(('http', '//')):
            self.remote.append(a['href'])
    def handle_endtag(self, tag):
        if tag == 'tbody': self._in_tbody -= 1
        if tag == 'tr' and self._row is not None:
            self.rows.append(self._row); self._row = None
    def handle_data(self, d):
        self.text.append(d)
        if self._row is not None: self._row['text'] += d

def official(url):
    host = urlparse(url).netloc.lower()
    return any(host == d or host.endswith('.' + d) for d in OFFICIAL + ACADEMIC)

def main():
    pages = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))
    parsed = {}
    for f in pages:
        p = P(); p.feed(open(os.path.join(SITE, f), encoding='utf-8').read()); parsed[f] = p
    errors = []; stats = dict(pages=len(pages), internal=0, external=0, rows=0, rows_official=0, rows_flagged=0, dollars=0)
    ext_hosts = {}
    for f, p in parsed.items():
        # 1. links
        for href in p.links:
            if href.startswith(('http://', 'https://')):
                stats['external'] += 1
                h = urlparse(href).netloc.lower(); ext_hosts[h] = ext_hosts.get(h, 0) + 1
                if href.startswith('http://') and 'insurance.ca.gov' not in href:
                    errors.append(f'{f}: non-https link {href}')
                continue
            if href.startswith(('mailto:', 'tel:')):
                errors.append(f'{f}: contact link {href}'); continue
            stats['internal'] += 1
            path, _, frag = href.partition('#')
            if path.startswith('../'): continue          # link out of this copy to the main dashboard
            target = path or f
            if not os.path.exists(os.path.join(SITE, target)):
                errors.append(f'{f}: broken internal link {href}'); continue
            if frag and target in parsed and frag not in parsed[target].ids:
                errors.append(f'{f}: missing anchor {href}')
        # 2. source on every table row
        for r in p.rows:
            stats['rows'] += 1
            has_official = any(official(h) for h in r['links'])
            has_flag = r['flagged'] or any(h.startswith('flagged.html#') for h in r['links'])
            if has_official: stats['rows_official'] += 1
            elif has_flag: stats['rows_flagged'] += 1
            else: errors.append(f'{f}: table row without an official source or a flag: {r["text"][:90]!r}')
        text = html.unescape(' '.join(p.text))
        # 3. rounding
        for m in re.finditer(r'\$\s?(\d{1,3}(?:,\d{3})+|\d{4,})(?!,\d|\.\d|\d)', text):
            n = int(m.group(1).replace(',', '')); stats['dollars'] += 1
            if n % 10 and n not in EXACT_OFFICIAL:
                errors.append(f'{f}: dollar amount not rounded to $10: {m.group(0)}')
        # 4. privacy patterns
        for name, pat in (('street address', r'\b\d{2,5}\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\s+(?:Avenue|Ave|Street|St|Drive|Dr|Way|Court|Ct|Lane|Ln|Road|Rd|Boulevard|Blvd|Place|Terrace)\b\.?'),
                          ('parcel number', r'\b\d{3}-\d{2}-\d{3}\b|\b(?:APN|block|lot)\s*#?\s*\d{3,4}\b'),
                          ('e-mail', r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
                          ('phone', r'\(\d{3}\)\s?\d{3}[-.]\d{4}|\b\d{3}-\d{3}-\d{4}\b|\b\d{3}\.\d{3}\.\d{4}\b')):
            for m in re.finditer(pat, text):
                errors.append(f'{f}: possible {name}: {m.group(0)!r}')
        # 5. remote resources
        for u in p.remote: errors.append(f'{f}: remote resource {u}')
        # 6. navigation
        for g in pages:
            if g not in p.links: errors.append(f'{f}: navigation lacks {g}')
    unofficial = sorted(h for h in ext_hosts if not any(h == d or h.endswith('.' + d) for d in OFFICIAL + ACADEMIC + ('github.com',)))
    if unofficial: errors.append('external hosts outside the official list: ' + ', '.join(unofficial))
    print(f"pages {stats['pages']} | internal links {stats['internal']} | external links {stats['external']} to {len(ext_hosts)} hosts")
    print(f"table rows {stats['rows']}: {stats['rows_official']} with an official source, {stats['rows_flagged']} flagged as unverified, "
          f"{stats['rows'] - stats['rows_official'] - stats['rows_flagged']} with neither")
    print(f"dollar amounts checked {stats['dollars']}")
    print('hosts:', ', '.join(f'{h} ({n})' for h, n in sorted(ext_hosts.items(), key=lambda kv: -kv[1])))
    if errors:
        print(f'\nFAIL — {len(errors)} problem(s)')
        for x in errors[:60]: print('  -', x)
        sys.exit(1)
    print('\nPASS')

if __name__ == '__main__':
    main()
