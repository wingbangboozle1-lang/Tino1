#!/usr/bin/env python3
"""Declare and generate the privacy-first GitHub Pages publication boundary.

Run:
  python3 final/publish.py            # update final/published.txt and _config.yml
  python3 final/publish.py --check    # fail if either file is stale

Only the generic root landing page and the figure-free guide under
privacy-site/public/ are published. Household-derived values, locality cues,
owner histories, and household projections stay out of Pages. Rounding is not
anonymisation, and this allowlist does not hide repository files, Git history,
forks, or prior copies; repository visibility/history remediation is separate.

The exact allowlist is checked against the actual Jekyll output in CI by both
publication checkers. The numeric analysis remains in the repository for
internal review and must not be described as a public-site recommendation.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The figure-free guide: the decision process taught with invented examples.
# Household figures and derived projections are intentionally not in this list.
GUIDE = [
    'privacy-site/public/index.html',
    'privacy-site/public/brief.html',
    'privacy-site/public/decision.html',
    'privacy-site/public/projection.html',
    'privacy-site/public/stress.html',
    'privacy-site/public/phased.html',
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
ALLOW = {'index.html'} | set(GUIDE)
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
    landing = os.path.join(ROOT, 'privacy-site', 'landing.html')
    published_landing = os.path.join(ROOT, 'index.html')
    if not os.path.isfile(landing) or not os.path.isfile(published_landing):
        problems.append('privacy-first root landing template or published copy is missing')
    elif open(landing, 'rb').read() != open(published_landing, 'rb').read():
        problems.append('root index.html differs from privacy-site/landing.html')
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
            print('::error::publication list is out of date: %s (run python3 final/publish.py)' % ', '.join(stale))
            return 1
        print('OK - _config.yml and final/published.txt match the allowlist of %d files' % len(ALLOW))
        return 0
    print('updated %d published file(s); rewrote %s' % (
        len(ALLOW), ', '.join(os.path.relpath(path, ROOT) for path, _ in targets)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
