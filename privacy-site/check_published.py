"""Fail closed unless Jekyll publishes exactly the reviewed public edition.

This is a file-boundary check, not a proof of anonymization or source accuracy.
"""
from pathlib import Path
import sys

PUBLIC_FILES = frozenset({
    'index.html', 'decision.html', 'projection.html', 'stress.html',
    'process.html', 'law.html', 'costs.html', 'suggestions.html', 'flagged.html', 'style.css',
})


def check_published(root, public=None):
    root = Path(root)
    public = Path(public) if public is not None else Path(__file__).parent / 'public'
    assert root.is_dir() and public.is_dir(), 'Missing Jekyll output or public source directory'
    source_entries = list(public.iterdir())
    assert all(p.is_file() and not p.is_symlink() for p in source_entries), 'Unexpected public directory entry'
    source_files = {p.name for p in source_entries}
    assert source_files == PUBLIC_FILES, f'Unexpected or missing public source files: {source_files ^ PUBLIC_FILES}'
    expected = {'index.html'} | {f'privacy-site/public/{name}' for name in PUBLIC_FILES}
    entries = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in entries), 'Symlinks are forbidden in the published output'
    actual = {p.relative_to(root).as_posix() for p in entries if p.is_file()}
    assert actual == expected, f'Unexpected or missing published files: {actual ^ expected}'
    for name in PUBLIC_FILES:
        assert (root / 'privacy-site/public' / name).read_bytes() == (public / name).read_bytes(), f'Content changed by Jekyll: {name}'
    redirect = (root / 'index.html').read_bytes()
    assert redirect == (Path(__file__).parent.parent / 'index.html').read_bytes(), 'Root landing differs from reviewed source'
    assert b'privacy-site/public/index.html' in redirect, 'Root landing must link to the privacy-first guide'
    print(f'PASS: exact publication allowlist, {len(actual)} files')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 privacy-site/check_published.py _site')
    check_published(sys.argv[1])
