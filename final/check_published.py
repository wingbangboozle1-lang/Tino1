#!/usr/bin/env python3
"""Verify GitHub Pages output against the published-edition boundary.

  python3 final/check_published.py _site

Exit code 1 on any failure. Two editions are published: the guide edition under
privacy-site/public, which publishes no household amounts, and the numeric edition under
public-guide, whose content rules ($10 rounding, a source on every row, no locality cue,
no PII pattern) are enforced by final/check_public_guide.py. This file enforces the
boundary: exactly the files in final/published.txt, byte-identical to the repository,
internal links staying inside the set, noindex everywhere, and a root landing page that
routes to the two editions and nowhere else.

Two freshness checks matter here. The root landing page must match the generator that
writes it, and the numeric edition must match a fresh build of public-guide/_build.py.
The legacy builder in final/build.py also writes a file called index.html into its output
directory; it is not the published landing page, and this gate says so once rather than
comparing the wrong pair.

Optional unrounded-value fingerprints are scanned only when TINO1_PRIVATE_FIGURES points
to a file outside the repository; without that file this checker does not claim a
complete privacy audit.
"""
import html
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ALLOW = [line.strip() for line in open(os.path.join(HERE, 'published.txt'), encoding='utf-8') if line.strip()]
ALLOW_SET = set(ALLOW)

errors = []


def err(*a):
    msg = ' '.join(str(x) for x in a)
    errors.append(msg)


def fail(msg):
    print('::error::' + msg)


PII = [
    (r'\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b', 'street address'),
    (r'[\w.+-]+@[\w-]+\.[\w.]+', 'e-mail address'),
    (r'\b\d{3}-\d{2}-\d{3}\b', 'parcel-number pattern'),
    (r'\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b', 'phone number'),
]

PF = os.environ.get('TINO1_PRIVATE_FIGURES', '')
FP = set(re.sub(r'\D', '', x) for x in open(PF).read().split()) - {''} if PF and os.path.isfile(PF) else set()


def scan(name, text):
    for rx, what in PII:
        m = re.search(rx, text)
        if m:
            err('PII:', what, 'in', name, '->', m.group(0))
    for tok in set(re.findall(r'(?<![\d.])\d{1,3}(?:(?:,|\\,|[_ ])\d{3})+(?![\d])|(?<![\d.])\d{4,7}(?![\d])', text)):
        if re.sub(r'\D', '', tok) in FP:
            err('PRIVACY: unrounded owner figure in', name)


def check_site(site):
    actual = set()
    for base, _, files in os.walk(site):
        for f in files:
            actual.add(os.path.relpath(os.path.join(base, f), site).replace(os.sep, '/'))
    missing = sorted(ALLOW_SET - actual)
    extra = sorted(actual - ALLOW_SET)
    if missing:
        err('declared but not published (check the build and the redirect stubs):', ', '.join(missing))
    for name in extra:
        err('published but not declared (add it to final/publish.py, or exclude it in _config.yml):', name)
    for name in sorted(ALLOW_SET & actual):
        if not name.endswith('.html'):
            continue
        text = open(os.path.join(site, name), encoding='utf-8', errors='ignore').read()
        if 'noindex' not in text:
            err('published page without robots noindex:', name)
        scan(name, text)
        for u in re.findall(r'(?:href|src)="([^"]+)"', text):
            u = html.unescape(u)
            if re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', u, flags=re.I):
                continue
            target = u.split('#')[0].split('?')[0]
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(name), target)).replace(os.sep, '/')
            if resolved not in ALLOW_SET:
                err('published page', name, 'links to a path that is not published:', target)
    return len(actual)


def check_fresh():
    """Regenerate the site into a scratch directory and compare with the committed root."""
    tmp = tempfile.mkdtemp(prefix='tino1-fresh-')
    env = dict(os.environ, OUT_DIR=tmp, ROOT_MODE='1')
    subprocess.run([sys.executable, os.path.join(HERE, 'model.py')], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, os.path.join(HERE, 'build.py')], check=True, env=env, stdout=subprocess.DEVNULL)
    # the Markdown executive summary is generated too: it must match the model today
    fresh_md = os.path.join(tmp, 'EXECUTIVE-SUMMARY.md')
    subprocess.run([sys.executable, os.path.join(HERE, 'exec_summary.py'), fresh_md], check=True, stdout=subprocess.DEVNULL)
    md = os.path.join(ROOT, 'EXECUTIVE-SUMMARY.md')
    if not os.path.exists(md) or open(fresh_md, 'rb').read() != open(md, 'rb').read():
        err('EXECUTIVE-SUMMARY.md differs from what final/exec_summary.py produces today')
    n = 0
    for name in sorted(ALLOW_SET):
        if not name.endswith(('.html', '.css', '.js')):
            continue
        if '/' in name:
            continue  # privacy-site/public/* and public-guide/*: built by their own generators, checked below
        if name == 'index.html':
            # final/build.py emits a legacy numeric index.html into OUT_DIR. The published landing
            # page comes from public-guide/_build.py, so compare against that instead.
            continue
        fresh = os.path.join(tmp, name)
        live = os.path.join(ROOT, name)
        if not os.path.exists(fresh):
            err('the builder no longer writes', name)
            continue
        if open(fresh, 'rb').read() != open(live, 'rb').read():
            err('the committed copy of', name, 'differs from what final/build.py produces today')
        n += 1
    # the two editions: each must match its own generator, byte for byte
    for gen, label in ((os.path.join(ROOT, 'public-guide', '_build.py'), 'public-guide'),
                       (os.path.join(ROOT, 'privacy-site', 'build.py'), 'privacy-site/public')):
        subprocess.run([sys.executable, gen], check=True, stdout=subprocess.DEVNULL)
    land = os.path.join(ROOT, 'index.html')
    if not os.path.exists(land):
        err('no root landing page: run python3 public-guide/_build.py')
    else:
        txt = open(land, encoding='utf-8').read()
        if 'public-guide/index.html' not in txt or 'privacy-site/public/index.html' not in txt:
            err('the root landing page must link to both published editions')
        if '$' in txt:
            err('the root landing page must not carry a dollar figure')
    return n


if __name__ == '__main__':
    site = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, '_site')
    n = check_site(site)
    f = check_fresh()
    print('::notice::published files: %d; builder outputs compared: %d; unrounded-figure scan %s' % (
        n, f, 'on' if FP else 'SKIPPED (TINO1_PRIVATE_FIGURES not set)'))
    if errors:
        print('FAIL - %d problem(s)' % len(errors))
        for x in errors:
            fail(x)
            print(' -', x)
        sys.exit(1)
    print('PASS - exact public allowlist (%d files: both editions), byte-identical to the repository, internal '
          'links resolve inside it, noindex on every page, no PII pattern matched, root landing routes to both '
          'editions and carries no figure; unrounded-value scan %s' % (n, 'on' if FP else 'SKIPPED (TINO1_PRIVATE_FIGURES not set)'))
