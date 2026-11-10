import sys
sys.path.insert(0,"tools")
from gen import head, FOOT, src
import pg_tax, pg_inherit, pg_rest

PAGES = [
 ("property-tax.html", pg_tax.prop_tax),
 ("inheritance.html",  pg_inherit.inheritance),
 ("projections.html",  pg_rest.projections),
 ("costs.html",        pg_rest.costs),
 ("scenarios.html",    pg_rest.scenarios),
 ("process.html",      pg_rest.process),
 ("law-changes.html",  pg_rest.lawchanges),
 ("findings.html",     pg_rest.findings),
 ("sources.html",      pg_rest.sources),
 ("flagged.html",      pg_rest.flagged),
]
for fn, renderer in PAGES:
    html = renderer(head, FOOT, src)
    open("docs/"+fn,"w").write(html)
    print(f"{fn:22s} {len(html):>8,} bytes")
