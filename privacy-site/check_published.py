"""Fail closed unless Jekyll emits exactly the reviewed published edition.

  python3 privacy-site/check_published.py _site

The published edition is the root decision dashboard (rounded-figures analysis,
placeholders for people, every owner or model dollar figure rounded to the
nearest $10) together with the no-figures general guide under
privacy-site/public/. This boundary settles the owner brief's open publication
decisions G01/G02: costs and numbers are reported for clarity as the brief
requires, personal information is anonymised to placeholders, and rounding is
labelled disclosure-minimisation, not anonymisation.

This check validates the Pages output boundary, not the safety of the public Git
repository, its history, or third-party copies. Both this checker and
final/publish.py hard-code the reviewed set on purpose: changing the boundary
requires editing both.
"""
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).parent
ROOT = HERE.parent

GUIDE_FILES = frozenset({
    'costs.html', 'decision.html', 'flagged.html', 'index.html', 'law.html',
    'process.html', 'projection.html', 'questions.html', 'stress.html',
    'suggestions-detail.html', 'suggestions.html', 'style.css',
})
SITE_FILES = frozenset({
    'index.html', 'summary.html', 'decision.html', 'questions.html',
    'suggestions.html', 'projections.html', 'black-swan.html', 'process.html',
    'law.html', 'estate-cash.html', 'costs.html', 'flagged.html', 'sources.html',
    'verification.html', 'requirements.html', 'review.html', 'versions.html',
    'style.css', 'app.js', 'properties.html', 'scenarios.html', 'taxes.html',
    'estate-tax.html', 'methodology.html', 'pending-changes.html', 'steps.html',
    'mirror-archived-2026-11-10.html',
})
EXPECTED_FILES = frozenset(SITE_FILES | {
    f'privacy-site/public/{name}' for name in GUIDE_FILES
})

PII = [
    (r'\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b', 'street address'),
    (r'[\w.+-]+@[\w-]+\.[\w.]+', 'e-mail address'),
    (r'\b\d{3}-\d{2}-\d{3}\b', 'parcel-number pattern'),
    (r'\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b', 'phone number'),
]


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append(value)


def _allowlist():
    return frozenset(line.strip() for line in
                     (ROOT / 'final' / 'published.txt').read_text().splitlines()
                     if line.strip())


def _check_landing(text):
    low = text.casefold()
    assert 'name="robots" content="noindex, nofollow"' in low, 'Root landing must be noindex'
    assert 'name="referrer" content="no-referrer"' in low, 'Root landing must set no-referrer'
    assert 'privacy-site/public/index.html' in text, 'Root landing must link to the no-figures guide'
    assert 'rounded to the nearest' in low, 'Root landing must state the $10 rounding rule'
    assert 'placeholder' in low, 'Root landing must state the placeholder rule'
    assert '<script' not in low and 'http-equiv="refresh"' not in low, \
        'Root landing must not execute scripts or redirect'


def check_published(root, public=None):
    root = Path(root)
    public = Path(public) if public is not None else HERE / 'public'
    assert root.is_dir() and public.is_dir(), 'Missing Jekyll output or public source directory'
    source_entries = list(public.iterdir())
    assert all(p.is_file() and not p.is_symlink() for p in source_entries), 'Unexpected public directory entry'
    source_files = {p.name for p in source_entries}
    assert source_files == GUIDE_FILES, f'Unexpected or missing public guide files: {source_files ^ GUIDE_FILES}'

    allow = _allowlist()
    assert allow == EXPECTED_FILES, f'Published allowlist differs from the reviewed set: {allow ^ EXPECTED_FILES}'
    entries = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in entries), 'Symlinks are forbidden in the published output'
    actual = {p.relative_to(root).as_posix() for p in entries if p.is_file()}
    assert actual == EXPECTED_FILES, f'Unexpected or missing published files: {actual ^ EXPECTED_FILES}'

    for name in sorted(EXPECTED_FILES):
        src = ROOT / name
        assert src.is_file(), f'No repository source for published file: {name}'
        built = root / name
        assert built.read_bytes() == src.read_bytes(), f'Content changed by Jekyll: {name}'
        if not name.endswith('.html'):
            continue
        text = built.read_text(encoding='utf-8')
        low = text.casefold()
        assert 'noindex,nofollow' in low or 'noindex, nofollow' in low, f'Missing noindex: {name}'
        assert 'no-referrer' in low, f'Missing referrer policy: {name}'
        for rx, what in PII:
            assert not re.search(rx, text), f'{name} contains a {what}'
        if name == 'index.html':
            _check_landing(text)
        parser = LocalLinks()
        parser.feed(text)
        for raw in parser.links:
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc or raw.startswith('#'):
                continue
            target = parts.path or name
            base = posixpath.dirname(name)
            resolved = posixpath.normpath(posixpath.join(base, target))
            assert resolved in EXPECTED_FILES, f'{name} links to non-published path {raw!r}'

    print(f'PASS: exact reviewed allowlist, {len(actual)} files, byte-identical, '
          f'noindex/no-referrer, no personal-identifier patterns, local links resolve')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
