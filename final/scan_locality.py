#!/usr/bin/env python3
"""Ad-hoc scan: which published pages still name a place in the text a reader sees.

Not part of the gates; kept because the same pattern is enforced by
final/check_published.py. Run: python3 final/scan_locality.py [dir]
"""
import collections
import re
import sys
from pathlib import Path

PAT = re.compile(
    r"San Francisco|Santa Clara|Cupertino|San Jose|Bay Area|SCVWD|SFPUC|SFMTA|sftreasurer|"
    r"SJWC|Cal Water|California Water|\bSF\b|Midpen|VMC|asr\.santa|cupertino\.gov|sccassessor",
    re.I)
URL = re.compile(r"https?://[^\s\"<>'" + "`" + r"]+")

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
tot = collections.Counter()
files = collections.Counter()
for f in sorted(root.glob('**/*.html')):
    t = f.read_text(encoding='utf-8', errors='ignore')
    v = URL.sub(' ', t)
    for m in PAT.finditer(v):
        files[str(f)] += 1
        tot[re.sub(r'\s+', ' ', v[max(0, m.start() - 50):m.end() + 40])] += 1
print('pages with leftovers:', len(files), dict(files))
for c, n in tot.most_common(60):
    print(n, '|', c)
