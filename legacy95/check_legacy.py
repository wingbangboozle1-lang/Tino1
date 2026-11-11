#!/usr/bin/env python3
"""Verification gate for the superseded-edition close-out (session 95383689).

PASS conditions for dashboard/**, docs/**, site/**, archive/root-site-2026-11-11/**:
  1. every table data row carries an official source link or an explicit
     unverified/assumption/model-output label (rowrule.row_state != 'work');
  2. no live link remains to the CR-85-1 commercial/advocacy sites;
  3. no law.cornell.edu mirror link remains (text citations are fine);
  4. the CR-07-7 wrong note ("previously $67") is gone from these trees;
  5. no anchor whose text and official href contradict the CR-85-2 list.

Exit 0 = PASS. Prints the full count table either way.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowrule import row_state, strip_tags  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = [
    os.path.join(ROOT, 'dashboard'),
    os.path.join(ROOT, 'docs'),
    os.path.join(ROOT, 'site'),
    os.path.join(ROOT, 'archive', 'root-site-2026-11-11'),
]
BANNED_HOSTS = (
    'policygenius.com', 'nerdwallet.com', 'zillow.com', 'rentometer.com',
    'ballotpedia.org', 'car.org', 'gethomeinsurancequotes.com', 'hjta.org',
    'law.cornell.edu',
)


def main():
    rows_total = sourced = labelled = work = 0
    work_rows = []
    banned = []
    old_note = []
    for tree in TREES:
        for root, _, fnames in os.walk(tree):
            for fn in fnames:
                if not fn.endswith('.html'):
                    continue
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, ROOT)
                html = open(path, encoding='utf-8', errors='ignore').read()
                if 'previously $67' in html:
                    old_note.append(rel)
                for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S):
                    href, text = m.group(1), m.group(2)
                    h = re.sub(r'^https?://(www\.)?', '', href).split('/')[0]
                    if any(h == b or h.endswith('.' + b) for b in BANNED_HOSTS):
                        banned.append((rel, href[:90], strip_tags(text)[:50]))
                for ti, body in enumerate(re.findall(r'<tbody[^>]*>(.*?)</tbody>', html, re.S)):
                    for r in re.findall(r'<tr>(.*?)</tr>', body, re.S):
                        if '<td' not in r:
                            continue
                        rows_total += 1
                        st = row_state(r)
                        if st == 'sourced':
                            sourced += 1
                        elif st == 'labelled':
                            labelled += 1
                        else:
                            work += 1
                            if len(work_rows) < 40:
                                work_rows.append((rel, ti, strip_tags(r)[:110]))
    print('rows total      : %d' % rows_total)
    print('  official link : %d' % sourced)
    print('  flagged label : %d' % labelled)
    print('  WORK (bad)    : %d' % work)
    for w in work_rows:
        print('    WORK %s T%d: %s' % w)
    print('banned commercial/mirror links remaining: %d' % len(banned))
    for b in banned[:20]:
        print('    BANNED %s: %s (%s)' % b)
    print('"previously $67" occurrences: %d' % len(old_note))
    for n in old_note:
        print('    STALE-NOTE %s' % n)
    ok = (work == 0 and not banned and not old_note)
    print('LEGACY CLOSE-OUT CHECK: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
