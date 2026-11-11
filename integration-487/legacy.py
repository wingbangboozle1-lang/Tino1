"""Safe, empty redirects for previously published HTML routes.

Old data files and old scripts must be removed, not redirected to a download
with a misleading format. Paths are historical, not actual property records.
"""
from __future__ import annotations

import html
import posixpath

PAGE_MAP = {
    'index': 'index.html', 'executive-summary': 'index.html',
    'cupertino': 'properties.html', 'sanfrancisco': 'properties.html',
    'properties': 'properties.html', 'prop19': 'properties.html',
    'decision': 'decisions.html', 'compare-decisions': 'decisions.html',
    'projections': 'projections.html', 'scenarios': 'scenarios.html',
    'black-swan': 'scenarios.html', 'taxes': 'taxes.html',
    'tax-law': 'taxes.html', 'estate-tax': 'taxes.html',
    'inheritance-tax': 'taxes.html', 'pending-legislation': 'taxes.html',
    'process': 'steps.html', 'steps': 'steps.html',
    'inheritance': 'steps.html', 'inheritance-guide': 'steps.html',
    'costs': 'costs.html', 'operating-costs': 'costs.html',
    'sources': 'sources.html', 'flagged': 'flagged.html',
    'flagged-review': 'flagged.html', 'methodology': 'methodology.html',
}
DIRECTORY_STEMS = {
    'docs': ('compare-decisions', 'cupertino', 'decision', 'flagged', 'index',
             'inheritance-tax', 'inheritance', 'operating-costs', 'process',
             'projections', 'properties', 'sanfrancisco', 'scenarios', 'sources',
             'steps', 'taxes'),
    'dashboard': ('black-swan', 'costs', 'executive-summary', 'flagged', 'index',
                  'inheritance-tax', 'methodology', 'pending-legislation', 'process',
                  'projections', 'prop19', 'properties', 'scenarios', 'sources', 'tax-law'),
    'site': ('estate-tax', 'flagged-review', 'index', 'inheritance-guide',
             'projections', 'properties', 'scenarios', 'sources'),
}


def redirect_map() -> dict[str, str]:
    redirects = {f'{directory}/{stem}.html': PAGE_MAP[stem]
                 for directory, stems in DIRECTORY_STEMS.items() for stem in stems}
    redirects.update({
        'black-swan.html': 'scenarios.html',
        'estate-tax.html': 'taxes.html',
        'pending-changes.html': 'taxes.html',
        'process.html': 'steps.html',
        'mirror-archived-2026-11-10.html': 'index.html',
        'archive/root-portal-62c87525.html': 'index.html',
    })
    return redirects


def redirect_html(old_path: str, destination: str) -> str:
    parent = posixpath.dirname(old_path) or '.'
    relative = posixpath.relpath(destination, parent)
    link = html.escape(relative, quote=True)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url={link}"><title>Guide moved</title></head><body><main><h1>This guide has moved</h1><p>The previous page has been replaced. <a href="{link}">Open the current synthetic guide</a>.</p></main></body></html>'''
