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
    'privacy-site/public/issues.html',
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
            if name == '__pycache__' or name.startswith('.'):
                continue  # interpreter and editor droppings: never published, never allowlisted
            rel = 'public-guide/%s' % name
            if rel in ALLOW:
                continue
            out.append("  - '%s'" % rel)
    ps = os.path.join(ROOT, 'privacy-site')
    if os.path.isdir(ps):
        for name in sorted(os.listdir(ps)):
            if name in ('public', '__pycache__') or name.startswith('.'):
                continue
            out.append("  - 'privacy-site/%s'" % name)
    out.append('')
    return '\n'.join(out)


def current_entries():
    # The allowlist must depend only on what is tracked, never on what a local run left behind:
    # a build that writes .pyc files into public-guide/__pycache__ used to add an exclude line that
    # CI never saw, so publish.py --check passed here and failed there.
    return [name for name in sorted(os.listdir(ROOT))
            if name != '.git' and name != '__pycache__']


def build_mismatches(allow):
    """Fail if the guide's generated output and the allowlist disagree.

    The guide builder writes exactly one HTML file per navigation entry plus a fixed
    CSS file. If a page is added to the builder and not to the allowlist (or the
    reverse), Pages would silently publish a stale set. Checked here so the two
    cannot drift apart without a red gate; Jekyll itself is only available in CI.
    """
    import re
    builder = os.path.join(ROOT, 'privacy-site', 'build.py')
    checker = os.path.join(ROOT, 'privacy-site', 'check.py')
    problems = []
    if not os.path.isfile(builder):
        return ['privacy-site/build.py is missing']
    text = open(builder, encoding='utf-8').read()
    nav = re.search(r"^nav=\[(.*?)\]\s*$", text, re.M | re.S)
    if not nav:
        return ['could not read the navigation table in privacy-site/build.py']
    generated = {f"privacy-site/public/{name}"
                 for name in re.findall(r"\('([^']+\.html)'", nav.group(1))}
    generated.add('privacy-site/public/style.css')
    if generated != set(GUIDE):
        problems.append('privacy-site/build.py pages and the allowlist disagree: %s'
                        % ', '.join(sorted(generated ^ set(GUIDE))))
    if os.path.isfile(checker):
        check_text = open(checker, encoding='utf-8').read()
        nav_set = re.search(r"^NAV = \{(.*?)\}\s*$", check_text, re.M | re.S)
        if nav_set:
            checked = set(re.findall(r"'([^']+\.html)'", nav_set.group(1)))
            if checked != {os.path.basename(f) for f in generated if f.endswith('.html')}:
                problems.append('privacy-site/check.py NAV and the builder disagree')
    return problems


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
    mismatches = build_mismatches(ALLOW)
    if check:
        if mismatches:
            for m in mismatches:
                print('::error::' + m)
            return 1
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
