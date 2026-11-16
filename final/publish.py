#!/usr/bin/env python3
"""Declare and generate the privacy-first GitHub Pages publication boundary.

Run:
  python3 final/publish.py            # update final/published.txt and _config.yml
  python3 final/publish.py --check    # fail if either file is stale

Two things are published together:

  * the rounded-figures analysis at the repository root (the decision dashboard
    and every page it links to), and
  * the figure-free guide under privacy-site/public/, which teaches the same
    method with invented examples and carries no household figure at all.

The owner brief asks for a live site that contains all the entries and findings
and includes the analysis, with every amount rounded to the nearest $10 and
personal information replaced by placeholders. That is the privacy control the
brief sets, and it is what this boundary implements: no name, street address,
parcel number, account number or ZIP code appears in the visible text of any
published page, and every owner-supplied and modelled dollar figure is a
multiple of ten.

Rounding is disclosure minimisation, not anonymisation. This allowlist does not
hide repository files, Git history, forks, or prior copies; repository
visibility/history remediation is separate and is recorded on the Flagged for
Review page.

The exact allowlist is checked against the actual Jekyll output in CI by both
publication checkers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The rounded-figures edition: the analysis itself, published as the brief asks.
# Personal information is replaced by placeholders ("the Transferor", "the
# Inheritor", "Property A", "Property B") and every dollar figure is rounded to
# the nearest $10 by final/model.py and final/build.py.
ANALYSIS = [
    'index.html',                       # the dashboard front door
    'summary.html', 'decision.html', 'projections.html', 'black-swan.html',
    'phased.html', 'what-if.html', 'process.html', 'timeline.html',
    'law.html', 'pending.html', 'estate-cash.html', 'costs.html',
    'glossary.html', 'brief.html', 'attorney-cpa-briefing.html',
    'precommit.html', 'decisions.html', 'questions.html', 'suggestions.html',
    'flagged.html', 'sources.html', 'verification.html', 'requirements.html',
    'review.html', 'versions.html',
    'style.css', 'app.js', 'whatif.js',
    # retired addresses, kept working as redirects
    'properties.html', 'scenarios.html', 'taxes.html', 'estate-tax.html',
    'methodology.html', 'pending-changes.html', 'steps.html',
    'mirror-archived-2026-11-10.html',
]

# The figure-free guide: the decision process taught with invented examples.
# Household figures and derived projections are intentionally not in this list.
GUIDE = [
    'privacy-site/public/index.html',
    'privacy-site/public/brief.html',
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
    'privacy-site/public/glossary.html',
    'privacy-site/public/style.css',
]

# This is the public output boundary, not a list of all tracked or internal files.
ALLOW = set(ANALYSIS) | set(GUIDE)
TITLE = 'Two-home inheritance analysis'


def config(entries):
    """Exclude every root entry except the generic landing and privacy-site/public/.

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
    front_door = os.path.join(ROOT, 'index.html')
    if not os.path.isfile(front_door):
        problems.append('the published front door index.html is missing')
    else:
        head = open(front_door, encoding='utf-8', errors='ignore').read(4000)
        if 'Two-home inheritance analysis' not in head:
            problems.append('the published front door is not the generated dashboard')
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
    # every file the analysis publishes must exist in the repository and be written by
    # the generator, so that the published bytes are the generated bytes
    for name in ANALYSIS:
        if not os.path.isfile(os.path.join(ROOT, name)):
            problems.append('published analysis file is missing from the repository: %s' % name)
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
            print('::error::publication list is out of date: %s (run python3 final/publish.py)' % ', '.join(stale))
            return 1
        print('OK - _config.yml and final/published.txt match the allowlist of %d files' % len(ALLOW))
        return 0
    print('updated %d published file(s); rewrote %s' % (
        len(ALLOW), ', '.join(os.path.relpath(path, ROOT) for path, _ in targets)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
