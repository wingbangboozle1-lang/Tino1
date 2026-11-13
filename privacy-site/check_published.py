"""Fail closed unless Jekyll emits exactly the reviewed publication boundary.

This check validates the Pages output boundary, not the safety of the public Git
repository, its history, or third-party copies.

Two editions are published:

* the rounded-figures analysis at the repository root, whose front door is
  ``index.html``. Every person is a placeholder, every owner-supplied and
  modelled dollar figure is rounded to the nearest $10, and no name, street
  address, parcel number or account number appears. $10 rounding is
  disclosure minimisation, not anonymisation - that is recorded as review item
  G01 on the Suggestions page, together with the narrower options.
* the figure-free guide under ``privacy-site/public/``, which teaches the same
  process with invented examples and carries no household figure at all.

``final/published.txt`` is the single source of truth for the file list. This
checker adds the guide-specific invariants that the root checker does not make:
the guide stays complete, byte-identical, figure-free and self-contained.
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
    'process.html', 'projection.html', 'questions.html', 'stress.html', 'issues.html',
    'suggestions-detail.html', 'suggestions.html', 'style.css',
})
GUIDE_PREFIX = 'privacy-site/public/'


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


def _check_guide_landing(text):
    """The guide's own front door must stay self-contained and script-free.

    It may quote official published thresholds (the federal estate-tax exclusion,
    for example), which are public amounts. It must never carry a household
    figure: the guide's own ``check.py`` enforces that across every guide page,
    and the local-link rule below keeps the guide from pointing at the numeric
    edition.
    """
    low = text.casefold()
    assert 'name="robots" content="noindex,nofollow"' in low or \
        'name="robots" content="noindex, nofollow"' in low, 'Guide landing must be noindex'
    assert 'name="referrer" content="no-referrer"' in low, 'Guide landing must set no-referrer'
    assert '<script' not in low and 'http-equiv="refresh"' not in low, \
        'Guide landing must not execute scripts or redirect'


def check_published(root, public=None):
    root = Path(root)
    public = Path(public) if public is not None else HERE / 'public'
    assert root.is_dir() and public.is_dir(), 'Missing Jekyll output or public source directory'
    source_entries = list(public.iterdir())
    assert all(p.is_file() and not p.is_symlink() for p in source_entries), 'Unexpected public directory entry'
    source_files = {p.name for p in source_entries}
    assert source_files == GUIDE_FILES, f'Unexpected or missing public guide files: {source_files ^ GUIDE_FILES}'

    expected = _allowlist()
    assert {GUIDE_PREFIX + name for name in GUIDE_FILES} <= expected, \
        'The figure-free guide must stay inside the published allowlist'
    entries = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in entries), 'Symlinks are forbidden in the published output'
    actual = {p.relative_to(root).as_posix() for p in entries if p.is_file()}
    assert actual == expected, f'Unexpected or missing published files: {actual ^ expected}'

    for name in sorted(expected):
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
        if name == GUIDE_PREFIX + 'index.html':
            _check_guide_landing(text)
        parser = LocalLinks()
        parser.feed(text)
        for raw in parser.links:
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc or raw.startswith('#'):
                continue
            target = parts.path or name
            base = posixpath.dirname(name)
            resolved = posixpath.normpath(posixpath.join(base, target))
            assert resolved in expected, f'{name} links to non-published path {raw!r}'

    print(f'PASS: exact allowlist, {len(actual)} files ({len(GUIDE_FILES)} guide + '
          f'{len(actual) - len(GUIDE_FILES)} analysis), byte-identical, local links resolve, '
          'guide landing stays figure-free')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
