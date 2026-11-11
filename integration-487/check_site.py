#!/usr/bin/env python3
"""Check generated site links, sources, table semantics, rounding and privacy.

Static checks cannot prove anonymity, legal correctness or accessibility. External
links were checked against official pages separately; this checker does not require
network access. Run `python3 integration-487/check_site.py` after a build, or pass
`--site .` to check the integrated repo root.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import model as m
from build_site import PAGES
from legacy import redirect_html, redirect_map
from sources import SOURCES

HERE = Path(__file__).resolve().parent
OFFICIAL_URLS = {item[0] for item in SOURCES.values()}


class Scan(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.text: list[str] = []
        self.in_tbody = False
        self.in_row = False
        self.row_links: list[str] = []
        self.rows: list[list[str]] = []
        self.table_count = 0
        self.caption_count = 0
        self.h1_count = 0
        self.main_count = 0
        self.has_lang = False
        self.has_viewport = False
        self.has_skip = False
        self.th_errors: list[str] = []
        self.in_thead = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'html' and a.get('lang') == 'en':
            self.has_lang = True
        if tag == 'meta' and a.get('name') == 'viewport':
            self.has_viewport = True
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'main':
            self.main_count += 1
        if tag == 'table':
            self.table_count += 1
        if tag == 'caption':
            self.caption_count += 1
        if tag == 'thead':
            self.in_thead = True
        if tag == 'tbody':
            self.in_tbody = True
        if tag == 'tr' and self.in_tbody:
            self.in_row = True
            self.row_links = []
        if tag == 'th' and self.in_thead and a.get('scope') != 'col':
            self.th_errors.append('column header missing scope=col')
        if tag == 'th' and self.in_tbody and a.get('scope') != 'row':
            self.th_errors.append('row header missing scope=row')
        if tag in ('a', 'link') and a.get('href'):
            href = a['href']
            self.links.append(href)
            if tag == 'a' and a.get('class') == 'skip' and href == '#main':
                self.has_skip = True
            if self.in_row:
                self.row_links.append(href)
        if tag in ('img', 'script') and a.get('src'):
            self.links.append(a['src'])

    def handle_endtag(self, tag: str) -> None:
        if tag == 'thead':
            self.in_thead = False
        if tag == 'tbody':
            self.in_tbody = False
        if tag == 'tr' and self.in_row:
            self.rows.append(self.row_links)
            self.in_row = False

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def check(site: Path) -> list[str]:
    errors: list[str] = []
    parsed: dict[Path, Scan] = {}
    pages = [site / name for name, _, _ in PAGES]
    for path in pages:
        if not path.is_file():
            errors.append(f'Missing page: {path}')
            continue
        scan = Scan()
        scan.feed(path.read_text(encoding='utf-8'))
        parsed[path] = scan
        if not scan.has_lang or not scan.has_viewport or scan.h1_count != 1 or scan.main_count != 1 or not scan.has_skip:
            errors.append(f'{path.name}: page landmark, heading, language, viewport or skip link invalid')
        if scan.table_count != scan.caption_count or scan.th_errors:
            errors.append(f'{path.name}: table captions or header scopes invalid')
        for i, row in enumerate(scan.rows, 1):
            if not any(href in OFFICIAL_URLS for href in row):
                errors.append(f'{path.name}: data row {i} has no registered official-source link')
        body = ' '.join(scan.text)
        for match in re.finditer(r'\$(\d[\d,]*(?:\.\d+)?)', body):
            amount = float(match.group(1).replace(',', ''))
            if amount % 10:
                errors.append(f'{path.name}: dollar value is not rounded to $10: {match.group(0)}')
        patterns = (
            (r'[\w.+-]+@[\w-]+\.[\w.]+', 'possible email'),
            (r'\b\d{3}-\d{2}-\d{3}\b', 'possible parcel identifier'),
            (r'\b\d{1,5}\s+[A-Z][a-z]+\s+(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Drive|Dr\.|Boulevard|Blvd\.)\b', 'possible street address'),
        )
        for rx, label in patterns:
            if re.search(rx, body):
                errors.append(f'{path.name}: {label}')
        if 'synthetic' not in body.lower():
            errors.append(f'{path.name}: missing synthetic-data context')

    for path, scan in parsed.items():
        for href in scan.links:
            url = urlsplit(href)
            if url.scheme:
                if url.scheme != 'https' or href not in OFFICIAL_URLS:
                    errors.append(f'{path.name}: non-registered external URL: {href}')
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path.resolve()
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{path.name}: broken local link {href}')
            elif url.fragment and target in parsed and url.fragment not in parsed[target].ids:
                errors.append(f'{path.name}: missing fragment {href}')

    for old, dest in redirect_map().items():
        path = site / old
        if not path.is_file() or path.read_text(encoding='utf-8') != redirect_html(old, dest):
            errors.append(f'Legacy redirect missing or altered: {old}')
        if not (site / dest).is_file():
            errors.append(f'Legacy redirect target missing: {dest}')

    csv_path = site / 'data' / 'annual-projections.csv'
    if not csv_path.exists():
        errors.append('Missing annual CSV')
    else:
        with csv_path.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 150:
            errors.append('Annual CSV must have 3 × 50 rows')
        reference = m.simulate(m.SCENARIOS[0])
        for r in rows:
            if r['classification'] != 'synthetic, not actual' or r['official_methodology_source'] not in OFFICIAL_URLS:
                errors.append('CSV row lacks synthetic status or official method URL')
                continue
            choice, year = r['strategy'], int(r['year'])
            if choice not in m.STRATEGIES or not 2045 <= year <= 2094:
                errors.append('CSV strategy/year outside expected range')
                continue
            expected = reference[choice][year - 2045]
            mapping = {
                'already_owned_market_value_usd': 'b_end_value',
                'inherited_hypothetical_net_sale_usd': 'a_exit_net',
                'account_or_funding_usd': 'account',
                'annual_net_cash_usd': 'net_cash',
                'modeled_position_usd': 'position',
                'modeled_position_in_2026_usd': 'real_position_2026',
            }
            for field, model_field in mapping.items():
                if int(r[field]) != m.round10(expected[model_field]):
                    errors.append(f'CSV/model mismatch for {choice}/{year}/{field}')
    if not (site / '.nojekyll').is_file():
        errors.append('Missing .nojekyll')
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=HERE / 'site')
    args = parser.parse_args()
    errors = check(args.site.resolve())
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f'PASS: {len(PAGES)} pages, {len(redirect_map())} legacy redirects, all table rows sourced, local links, $10 rounding, basic privacy patterns, and 150 CSV/model rows.')
    print('Note: static checks do not prove anonymity, legal correctness, external availability, or complete accessibility.')


if __name__ == '__main__':
    main()
