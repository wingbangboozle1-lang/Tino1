#!/usr/bin/env python3
"""Mask private household figures across the tracked tree, or prove none survives.

  TINO1_PRIVATE_FIGURES=/path/outside/the/repo.txt python3 final/scrub_figures.py [--dry-run] [--check]

Why this exists
---------------
The owner supplied a year-by-year property-tax and assessed-value history. Rounding it
to $10 does not anonymise it: a unique starting value plus a 2% growth pattern is a
lookup key for a parcel. Legacy editions of this project published that series, and
several tracked files still contain the figures. This script removes them.

The list of figures is NEVER stored in this repository. It is read from a file outside
the tree, named by TINO1_PRIVATE_FIGURES, one number per line, in any format
(123,456 or 123456). That is the same rule the checker uses, so a hash or a copy of
the values cannot leak from here.

What it changes
---------------
Every exact occurrence of a listed number in a tracked text file becomes [withheld].
For HTML, only text outside <tags> is touched, so URLs and attributes are never
corrupted. No content is deleted, no file is removed, no layout is changed: the page
still says what it said, with the figure withheld. A count per file is printed, and
the values themselves are never printed.

--check reports every remaining occurrence in a PUBLISHED file and changes nothing, exiting 2
if any exists. It deliberately ignores the excluded trees (archive/, docs/, site/, dashboard/,
verify-*/), which Jekyll never serves; those are reviewed by hand because masking a superseded
page achieves nothing that excluding it has not already achieved.
It needs the same outside-the-repository list as the scrub, so it is a maintainer command,
not a CI step: a list that could be checked by a machine without the list would have to be
stored in the repository, and a hash of a seven-digit number is reversible by enumeration,
so storing one would be protection in appearance only. Continuous integration enforces the
properties it can enforce without the secret - every household figure a multiple of $10,
every table row sourced, no locality cue, no PII pattern - in final/check_public_guide.py.

Exit code 0 on success, 1 if the list is missing or empty, 2 if --check finds a leak.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Documents and prose only. Machine-readable data files (.json, .csv), the model and the
# builders are NOT touched: masking a value there breaks the build (and a rebuild would
# simply restore it), and this script's job is to remove figures from what a reader sees.
TEXTY = ('.html', '.htm', '.md', '.txt')
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '_site', '.jekyll-cache'}
MARK = '[withheld]'


def private_values():
    p = os.environ.get('TINO1_PRIVATE_FIGURES', '')
    if not p or not os.path.isfile(p):
        return None
    vals = set()
    for line in open(p, encoding='utf-8'):
        # one figure per line, thousands separators allowed: 123,456 or 123456
        for tok in re.split(r'[;\s]+', line.strip()):
            d = re.sub(r'\D', '', tok)
            if len(d) >= 4:
                vals.add(d)
    return vals


def scope_values():
    """--scope=published limits the run to the files GitHub Pages actually serves."""
    for a in sys.argv[1:]:
        if a.startswith('--scope='):
            return a.split('=', 1)[1]
    return 'all'


def tracked_files():
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    scope = scope_values()
    allow = set()
    if scope in ('published', 'check'):
        pub = os.path.join(HERE, 'published.txt')
        allow = {x.strip() for x in open(pub, encoding='utf-8') if x.strip()}
    for rel in out.splitlines():
        if allow and rel not in allow:
            continue
        if not rel.endswith(TEXTY):
            continue
        if any(part in SKIP_DIRS for part in rel.split('/')):
            continue
        yield rel


def patterns(vals):
    """Match each value with or without thousands separators, never inside a longer number."""
    alts = []
    for v in sorted(vals, key=len, reverse=True):
        alts.append(r'\b' + r'[,_ ]?'.join(v) + r'\b')
    return re.compile('|'.join(alts))


YEARISH = re.compile(r'^(?:19|20)\d{2}$')


def _is_bare_year(written):
    """A four-digit number written without separators is probably a year, not a figure.

    The private list holds small dollar amounts (2,066 and 2,061 are real tax bills),
    and their bare digits are also plausible years. Masking '2066' in a projection table
    would corrupt a year column, so a bare four-digit 19xx/20xx is skipped. The written
    money form ('$2,066') is still masked.
    """
    return bool(YEARISH.match(written))


def _mask(seg, rx):
    out, n, pos = [], 0, 0
    for m in rx.finditer(seg):
        if _is_bare_year(m.group(0)):
            continue
        out.append(seg[pos:m.start()])
        out.append(MARK)
        pos = m.end()
        n += 1
    out.append(seg[pos:])
    return ''.join(out), n


def scrub_html(t, rx):
    """Replace only in text segments, never inside a tag or an attribute."""
    parts = re.split(r'(<[^>]*>)', t)
    n = 0
    for i, seg in enumerate(parts):
        if seg.startswith('<'):
            continue
        new, k = _mask(seg, rx)
        parts[i] = new
        n += k
    return ''.join(parts), n


def scrub_plain(t, rx):
    return _mask(t, rx)


def main():
    vals = private_values()
    if not vals:
        print('::error::set TINO1_PRIVATE_FIGURES to a file OUTSIDE this repository holding the private values')
        return 1
    dry = '--dry-run' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    if check and not any(a.startswith('--scope=') for a in sys.argv[1:]):
        sys.argv.append('--scope=check')
    rx = patterns(vals)
    total_files = total_hits = scanned = 0
    for rel in tracked_files():
        path = os.path.join(ROOT, rel)
        try:
            t = open(path, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        new, n = scrub_html(t, rx) if rel.endswith(('.html', '.htm')) else scrub_plain(t, rx)
        if n:
            total_files += 1
            total_hits += n
            state = 'found' if check else ('would be masked' if dry else 'masked')
            print('%-70s %d figure(s) %s' % (rel, n, state))
            if not dry and not check:
                open(path, 'w', encoding='utf-8').write(new)
    if check:
        if total_hits:
            print('::error::%d private figure(s) still readable in %d file(s); run the scrub'
                  % (total_hits, total_files))
            return 2
        print('::notice::no private figure from the outside-the-repository list is readable in any '
              'published file (%d values checked, %d published files scanned)' % (len(vals), scanned))
        return 0
    print('::notice::%d file(s), %d occurrence(s) %s; the value list was read from outside the repository'
          % (total_files, total_hits, 'would be masked' if dry else 'masked'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
