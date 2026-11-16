"""Fail closed unless Jekyll emits exactly the privacy-first publication boundary.

Only a generic root landing page and the figure-free guide under
``privacy-site/public/`` are published. No rounded household analysis, owner
history, locality cue or derived household forecast is in the Pages allowlist.
This validates the Pages output, not the safety of the public Git repository,
its history, or third-party copies; those remain separate risks.

``final/published.txt`` is the single source of truth for the file list. This
checker verifies the root landing is generic and the guide remains complete,
byte-identical and self-contained.
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
    'brief.html', 'costs.html', 'decision.html', 'flagged.html', 'index.html', 'law.html',
    'process.html', 'projection.html', 'questions.html', 'stress.html', 'phased.html', 'issues.html', 'glossary.html',
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
    landing_template = HERE / 'landing.html'
    assert landing_template.is_file() and (ROOT / 'index.html').read_bytes() == landing_template.read_bytes(), \
        'Published root landing must match the reviewed generic template'
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
        if name == 'index.html':
            forbidden = ('Cupertino', 'San Francisco', '95014', '94122',
                         '3,100,000', '1,800,000', '7,150', '550,540', '114,250')
            assert '$' not in text, 'Root landing must not publish household or modelled dollar figures'
            assert not any(token.casefold() in low for token in forbidden), \
                'Root landing contains a known household signature or locality cue'
            assert '<script' not in low, 'Root landing must not execute scripts'
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

    print(f'PASS: exact allowlist, {len(actual)} files (1 generic landing + '
          f'{len(GUIDE_FILES)} guide files), byte-identical, local links resolve, '
          'root landing has no household signatures, guide landing stays figure-free')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
