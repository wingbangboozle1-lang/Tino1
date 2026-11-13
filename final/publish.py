#!/usr/bin/env python3
"""Declare and generate the GitHub Pages publication boundary.

Run:
  python3 final/publish.py            # update final/published.txt and _config.yml
  python3 final/publish.py --check    # fail if either file is stale

The allowlist is the rounded-figures analysis (placeholders for every person and
property, every owner-supplied and modelled dollar figure rounded to the nearest
$10) plus the figure-free guide under privacy-site/public/. It is the
disclosure-minimisation boundary the brief asks for: no name, street address,
parcel number or account number is published, and no figure is published to the
dollar. Rounding is not anonymisation and this repository is public - that is
recorded as review item G01 on the Suggestions page, together with the narrower
options.

Earlier editions, audit directories, generators and data files are excluded.
The allowlist is checked against the actual Jekyll output in CI by both
publication checkers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LANDING = [
    'index.html',
    'style.css',
    'app.js',
]

# The rounded-figures analysis. Personal information is replaced by placeholders
# ("the Transferor", "the Inheritor", "Property A", "Property B") and every
# owner-supplied and modelled dollar figure is rounded to the nearest $10, which
# is the disclosure-minimisation control the brief asks for. Publishing this set
# is option D of suggestion G01; the owner can still choose a narrower boundary.
NUMERIC = [
    'summary.html',
    'decision.html',
    'questions.html',
    'suggestions.html',
    'projections.html',
    'black-swan.html',
    'process.html',
    'law.html',
    'estate-cash.html',
    'costs.html',
    'flagged.html',
    'sources.html',
    'verification.html',
    'requirements.html',
    'review.html',
    'versions.html',
]

# The figure-free guide: the same process and cost categories taught with
# invented examples, for anyone who wants to share the method without any
# household figure.
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

# This is the public output boundary, not a list of all tracked or internal files.
ALLOW = set(LANDING) | set(NUMERIC) | set(GUIDE)
TITLE = 'Two-home inheritance analysis'


def config(entries):
    """Exclude every root entry except the published landing, the rounded-figures
    pages and privacy-site/public/.

    privacy-site/ must remain traversable so that its public/ subdirectory can be
    published; its builder, source registry and other files are excluded one by one.
    """
    keep = sorted(ALLOW)
    out = ['title: %s' % TITLE, 'exclude:']
    for name in sorted(entries):
        if name in keep or name == 'privacy-site':
            continue
        out.append("  - '%s'" % name)
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
            print('::error::publication list is out of date: %s (run python3 final/publish.py)' % ', '.join(stale))
            return 1
        print('OK - _config.yml and final/published.txt match the allowlist of %d files' % len(ALLOW))
        return 0
    print('updated %d published file(s); rewrote %s' % (
        len(ALLOW), ', '.join(os.path.relpath(path, ROOT) for path, _ in targets)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
