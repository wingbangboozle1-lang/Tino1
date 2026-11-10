#!/usr/bin/env python3
"""Pre-publish checks for dashboard/: internal links resolve, every page has the nav,
fact-table rows carry a source link or a non-verified status, and no personal
identifiers (emails, street addresses, APN-like numbers) slipped in.
Exit code 1 on failure.  External URLs are listed (they were read manually on the
build date; this sandbox has no outbound access to them)."""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "dashboard")
errors = []
external = set()


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            self.assets.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.assets.append(a["src"])


pages = sorted(f for f in os.listdir(DOCS) if f.endswith(".html"))
if "index.html" not in pages:
    errors.append("dashboard/index.html missing")
if not os.path.exists(os.path.join(DOCS, ".nojekyll")):
    errors.append("dashboard/.nojekyll missing")

pii_patterns = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "email address"),
    (re.compile(r"\b\d{3}-\d{2}-\d{3}\b"), "APN-like number"),
    (re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Street|St\.|Avenue|Ave\.|Road|Rd\.|Drive|Dr\.|Blvd|Boulevard|Court|Ct\.|Lane|Ln\.|Way)\b"), "street address"),
]
allow_pii = {"assessor@sfgov.org", "cpi_info@bls.gov", "PressOffice@bls.gov"}

for f in pages:
    html = open(os.path.join(DOCS, f), encoding="utf-8").read()
    p = LinkParser()
    p.feed(html)
    if 'href="flagged.html"' not in html:
        errors.append(f"{f}: nav missing (no link to flagged.html)")
    for href in p.links + p.assets:
        if href.startswith(("http://", "https://")):
            external.add(href)
            continue
        if href.startswith(("mailto:", "#")):
            continue
        target = href.split("#")[0]
        if target and not os.path.exists(os.path.join(DOCS, target)):
            errors.append(f"{f}: broken internal link {href}")
    for rx, label in pii_patterns:
        for m in rx.finditer(html):
            if m.group(0) in allow_pii:
                continue
            errors.append(f"{f}: possible {label}: {m.group(0)}")
    # facts tables: every row must have either a source link or a non-verified badge
    for tbl in re.findall(r'<table class="facts">(.*?)</table>', html, flags=re.S):
        for row in re.findall(r"<tr>(.*?)</tr>", tbl, flags=re.S)[1:]:
            has_link = 'href="http' in row
            is_verified = 'badge ok">verified' in row
            if is_verified and not has_link:
                errors.append(f"{f}: a row marked verified has no source link: {re.sub('<[^>]+>', ' ', row)[:80]}")

# Repository-level privacy scan (text files). Files in this session's namespace fail the
# check; files owned by other sessions are reported as warnings only (protocol: do not edit them).
MINE = ("analysis/", "dashboard/")
warnings = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
    for fn in filenames:
        if fn.endswith((".csv", ".md", ".py", ".html", ".json", ".css", ".js")):
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            txt = open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore").read()
            for rx, label in pii_patterns:
                for m in rx.finditer(txt):
                    if m.group(0) in allow_pii:
                        continue
                    msg = f"{rel}: possible {label}: {m.group(0)}"
                    (errors if rel.startswith(MINE) else warnings).append(msg)
if warnings:
    print("WARNINGS (files owned by other sessions; not edited — see COORDINATION.md change requests):")
    for w in sorted(set(warnings))[:40]:
        print(" -", w)

print(f"Checked {len(pages)} pages; {len(external)} distinct external URLs.")
if errors:
    print("FAILURES:")
    for e in sorted(set(errors)):
        print(" -", e)
    sys.exit(1)
print("All internal checks passed.")
if "--list-external" in sys.argv:
    for u in sorted(external):
        print(u)
