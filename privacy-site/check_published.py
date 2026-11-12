"""Fail closed unless Jekyll publishes exactly the reviewed public edition.

This is a file-boundary check, not a proof of anonymization or source accuracy.

Contract (updated by the final integration session b724a7d8, 2026-11-12, logged in
COORDINATION.md): the published set is the union allowlist in final/published.txt -
the numeric edition at the root AND the no-figures guide under privacy-site/public/.
Every published file must be byte-identical to its source in the repository, so
Jekyll can neither alter a page nor leak an unplanned file.  The earlier exact
redirect for the root landing is superseded: the root landing is the numeric
edition's summary page, and the no-figures guide stays published at its own path
with a link from the root summary.  Revert path: restore the redirect as
index.html, drop the root pages from final/publish.py's PAGES, and re-run
final/publish.py.
"""
from pathlib import Path
import sys

HERE = Path(__file__).parent
ROOT = HERE.parent

PUBLIC_FILES = frozenset({
    'index.html', 'decision.html', 'projection.html', 'stress.html',
    'process.html', 'law.html', 'costs.html', 'questions.html', 'suggestions.html', 'suggestions-detail.html', 'flagged.html', 'style.css',
})


def check_published(root, public=None):
    root = Path(root)
    public = Path(public) if public is not None else HERE / 'public'
    assert root.is_dir() and public.is_dir(), 'Missing Jekyll output or public source directory'
    source_entries = list(public.iterdir())
    assert all(p.is_file() and not p.is_symlink() for p in source_entries), 'Unexpected public directory entry'
    source_files = {p.name for p in source_entries}
    assert source_files == PUBLIC_FILES, f'Unexpected or missing public source files: {source_files ^ PUBLIC_FILES}'
    allow = {line.strip() for line in (ROOT / 'final' / 'published.txt').read_text().splitlines() if line.strip()}
    assert {f'privacy-site/public/{name}' for name in PUBLIC_FILES} <= allow, 'final/published.txt must include the no-figures guide'
    entries = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in entries), 'Symlinks are forbidden in the published output'
    actual = {p.relative_to(root).as_posix() for p in entries if p.is_file()}
    assert actual == allow, f'Unexpected or missing published files: {actual ^ allow}'
    for name in sorted(allow):
        src = ROOT / name
        assert src.is_file(), f'No repository source for published file: {name}'
        assert (root / name).read_bytes() == src.read_bytes(), f'Content changed by Jekyll: {name}'
    print(f'PASS: exact publication allowlist, {len(actual)} files, all byte-identical to their repository sources')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
