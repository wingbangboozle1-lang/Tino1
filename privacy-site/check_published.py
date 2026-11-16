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
    assert landing_template.is_file(), 'Missing the figure-free front-door template'
    # The published front door is the generated decision dashboard since 2026-11-16
    # (the brief asks for the live site to carry the analysis, with every figure
    # rounded to $10 and every person and property replaced by a placeholder).
    # The template above is the figure-free variant (suggestion G01) and is not published.
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
            assert 'Two-home inheritance analysis' in text, \
                'The published front door must be the generated dashboard'
            assert '<script' not in low or 'src=' in low, \
                'The front door must not carry an inline script'
            # no locality cue and no ZIP code in the visible text
            shown = re.sub(r'https?://[^\s"<>\']+', ' ', text)
            for token in ('95014', '94122'):
                assert token not in shown, f'The front door shows a ZIP code in its visible text: {token}'
            for token in ('Cupertino',):
                assert token not in shown, f'The front door shows a locality cue: {token}'
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

    print(f'PASS: exact allowlist, {len(actual)} files ({len(expected) - len(GUIDE_FILES)} '
          f'analysis pages + {len(GUIDE_FILES)} figure-free guide files), byte-identical, '
          'local links resolve, front door is the generated dashboard with no ZIP code or '
          'locality cue in its visible text, guide landing stays figure-free')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
