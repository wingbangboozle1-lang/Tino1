import json, os
d   = json.load(open("data/model_output.json"))
br  = json.load(open("data/breakeven.json"))
B   = d["base"]; G = d["grid"]; BI = d["byinh"]; P = d["proj"]

def m(x):  return f"${x:,.0f}"
def mk(x): return f"${x/1000:,.0f}K"
def mm(x): return f"${x/1e6:,.2f}M"
def pc(x): return f"{x*100:.2f}%"

NAV = [("index.html","Overview"),
       ("findings.html","Findings"),
       ("property-tax.html","Property Tax"),
       ("inheritance.html","Inheritance"),
       ("projections.html","Projections"),
       ("costs.html","Carrying Costs"),
       ("scenarios.html","Scenarios"),
       ("process.html","Step-by-Step"),
       ("law-changes.html","Law Watch"),
       ("sources.html","Sources"),
       ("flagged.html","Flagged for Review")]

def head(title, page):
    nav = "".join(
        f'<a href="{h}"{" class=\"on\"" if h==page else ""}>{t}</a>' for h,t in NAV)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Cupertino &amp; SF Inheritance Analysis</title>
<meta name="description" content="Decision analysis for two inherited Bay Area properties. Every figure sourced to an official government or regulator publication.">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="wrap"><nav class="nav">
<a class="brand" href="index.html">Bay Area <span>Inheritance</span> Analysis</a>
{nav}
</nav></div></header>
<main><div class="wrap">"""

def foot():
    return """</div></main>
<footer><div class="wrap">
<p><strong>Privacy notice.</strong> This site deliberately contains no addresses, parcel numbers,
names, or any other personal identifiers. Both properties are referred to as
<strong>Property A</strong> and <strong>Property B</strong>. All dollar figures are rounded to the
nearest $10. This is an independent financial analysis prepared for internal family
decision-making. It is not legal, tax, or investment advice. Confirm all figures with a
licensed California attorney, CPA, and enrolled agent before acting.</p>
<p>Sources are linked on every table row. Rows that could not be confirmed against an
official source are left blank and listed on the <a href="flagged.html">Flagged for Review</a> page.
Analysis generated 2026-11-10.</p>
</div></footer></body></html>"""

os.makedirs("docs", exist_ok=True)
for h,_ in NAV: pass
print("scaffold ready")
