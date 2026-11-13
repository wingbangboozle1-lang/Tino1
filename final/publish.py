#!/usr/bin/env python3
"""Declare and generate the privacy-first GitHub Pages file boundary.

Run:
  python3 final/publish.py            # update final/published.txt and _config.yml
  python3 final/publish.py --check    # fail if either file is stale

Only the generic root landing page and the figure-free guide under
privacy-site/public/ are in the public allowlist. Household-specific numeric
analysis and earlier editions are deliberately excluded from Pages: rounded
values are not anonymized, and this repository is public. The allowlist is
checked against the actual Jekyll output in CI by both publication checkers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LANDING = ['index.html']
# The original no-figures guide stays published; the numeric edition is additive.
GUIDE = [
    'privacy-site/public/index.html',
    'privacy-site/public/decision.html',
    'privacy-site/public/projection.html',
    'privacy-site/public/stress.html',
    'privacy-site/public/process.html',
    'privacy-site/public/law.html',
    'privacy-site/public/costs.html',
    'privacy-site/public/questions.html',
    'privacy-site/public/suggestions.html',
    'privacy-site/public/suggestions-detail.html',
    'privacy-site/public/flagged.html',
    'privacy-site/public/style.css',
]

# The de-identified numeric edition: figures rounded to $10, official amounts quoted
# exactly, every table row sourced, no locality name, no bill history, no script.
NUMERIC = [
    'public-guide/index.html',
    'public-guide/decision.html',
    'public-guide/projections.html',
    'public-guide/black-swan.html',
    'public-guide/process.html',
    'public-guide/law.html',
    'public-guide/costs.html',
    'public-guide/estate.html',
    'public-guide/questions.html',
    'public-guide/suggestions.html',
    'public-guide/flagged.html',
    'public-guide/sources.html',
    'public-guide/requirements.html',
]

# This is the public output boundary, not a list of all tracked or internal files.
ALLOW = set(LANDING) | set(GUIDE) | set(NUMERIC)
TITLE = 'Privacy-first inheritance decision guide'


def config(entries):
    """Exclude every root entry except the safe landing and privacy-site guide.

    privacy-site/ must remain traversable so that its public/ subdirectory can be
    published; its builder, source registry and other files are excluded one by one.
    """
    keep = sorted(ALLOW)
    out = ['title: %s' % TITLE, 'exclude:']
    for name in sorted(entries):
        if name in keep or name in ('privacy-site', 'public-guide'):
            continue
        out.append("  - '%s'" % name)
    pg = os.path.join(ROOT, 'public-guide')
    if os.path.isdir(pg):
        for name in sorted(os.listdir(pg)):
            rel = 'public-guide/%s' % name
            if rel in ALLOW:
                continue
            out.append("  - '%s'" % rel)
    ps = os.path.join(ROOT, 'privacy-site')
    if os.path.isdir(ps):
        out.append("  - 'privacy-site/__pycache__'")
        for name in sorted(os.listdir(ps)):
            if name in ('public', '__pycache__'):
                continue
            out.append("  - 'privacy-site/%s'" % name)
    out.append('')
    return '\n'.join(out)


def current_entries():
    return [name for name in sorted(os.listdir(ROOT)) if name != '.git']


def main():
    check = '--check' in sys.argv[1:]
    cfg = config(current_entries())
    published = '\n'.join(sorted(ALLOW)) + '\n'
    targets = [(os.path.join(ROOT, '_config.yml'), cfg),
               (os.path.join(HERE, 'published.txt'), published)]
    stale = []
    for path, text in targets:
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(os.path.relpath(path, ROOT))
            if not check:
                open(path, 'w', encoding='utf-8').write(text)
    if check:
        if stale:
            print('::error::privacy-first publication list is out of date: %s (run python3 final/publish.py)' % ', '.join(stale))
            return 1
        print('OK - _config.yml and final/published.txt match the privacy-first allowlist of %d files' % len(ALLOW))
        return 0
    print('updated %d privacy-first published file(s); rewrote %s' % (
        len(ALLOW), ', '.join(os.path.relpath(path, ROOT) for path, _ in targets)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
