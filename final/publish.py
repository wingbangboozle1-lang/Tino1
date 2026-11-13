#!/usr/bin/env python3
"""Declare and generate the GitHub Pages file boundary.

Run:
  python3 final/publish.py            # update final/published.txt and _config.yml
  python3 final/publish.py --check    # fail if either file is stale

The published site is the decision dashboard and its subpages (the rounded-figures
analysis the owner's brief requires to be reported for clarity, with people kept as
placeholders and every owner or model dollar figure rounded to the nearest $10),
together with the no-figures general guide under privacy-site/public/. This boundary
settles the open publication decisions G01/G02 from the owner's brief: costs and
numbers are reported rounded to $10, personal information stays anonymised, and
rounding is labelled disclosure-minimisation rather than anonymisation. The
repository and its history remain public and are described as such on the landing
page. The allowlist is checked against the actual Jekyll output in CI by both
publication checkers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The decision dashboard at the root: landing, the analysis pages, the generated
# assets, and the redirect stubs that keep older addresses working.
SITE = [
    'index.html',
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
    'style.css',
    'app.js',
    # redirect stubs written by final/build.py for retired addresses
    'properties.html',
    'scenarios.html',
    'taxes.html',
    'estate-tax.html',
    'methodology.html',
    'pending-changes.html',
    'steps.html',
    'mirror-archived-2026-11-10.html',
]
# The figure-free general guide: same rules and process, invented teaching examples.
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
ALLOW = set(SITE) | set(GUIDE)
TITLE = 'Two-home inheritance analysis - decision dashboard'


def config(entries):
    """Exclude every root entry except the published site and the privacy-site guide.

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
    if stale and check:
        print('STALE - regenerate with: python3 final/publish.py')
        for name in stale:
            print(' ', name)
        sys.exit(1)
    print('OK - _config.yml and final/published.txt match the allowlist of %d files' % len(ALLOW))


if __name__ == '__main__':
    main()
