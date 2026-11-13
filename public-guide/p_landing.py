"""The root landing page: a chooser between the two published editions.

This page is deliberately tiny and figure-free. It is generated, not hand-edited, so the
gate in final/check_published.py can insist that it contains no dollar sign, no locality
name, no script and no form.
"""
import os

from _gen import CSS, BUILD_DATE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def build():
    doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<title>Two-home inheritance decision guide</title>
<style>{css}
main{{max-width:1040px;margin:0 auto;padding:48px 22px 60px}}
.crumb{{font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}}
h1{{font:600 clamp(1.9rem,4vw,2.7rem)/1.15 Georgia,serif;margin:.6rem 0 .6rem;color:var(--accent2)}}
p.lead{{font-size:1.1rem;color:var(--ink2);max-width:70ch}}
.choice{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;margin:30px 0 10px}}
.choice a.card{{display:block;text-decoration:none;color:inherit;border-top:4px solid var(--accent)}}
.choice a.card:hover{{background:#fbfdfc}}
.choice .tag{{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:var(--accent)}}
.choice h2{{font:600 1.25rem/1.25 Georgia,serif;margin:.4rem 0 .4rem;border:0;padding:0;color:var(--accent2)}}
.choice p{{color:var(--ink2);font-size:.92rem}}
.choice ul{{margin:.6rem 0 0;padding-left:1.1rem;font-size:.88rem;color:var(--muted)}}
.choice .go{{margin-top:.9rem;font-weight:700;color:var(--accent)}}
</style></head>
<body>
<main>
<p class="crumb">PUBLIC EDITION · PRIVACY FIRST</p>
<h1>Two-home inheritance decision guide</h1>
<p class="lead">One question, two ways to read the answer. Both editions are static pages with no accounts, no
forms and no tracking. Choose the one that matches what you need to do today.</p>

<div class="choice">
<a class="card" href="public-guide/index.html">
<span class="tag">Numeric edition</span>
<h2>Numbers, projections and the recommendation</h2>
<p>Amounts rounded to the nearest ten dollars, statutory amounts quoted exactly, every table row linked to the
official page behind it. No names, addresses or parcel numbers appear anywhere.</p>
<ul>
<li>The recommended path, with the figures and the conditions that would change it</li>
<li>Year-by-year projections, then named crisis paths and fifty real historical replays</li>
<li>The questions that must be answered first, and how to discover each answer</li>
<li>Suggestions to review before anything is implemented</li>
</ul>
<p class="go">Open the numeric edition</p>
</a>

<a class="card" href="privacy-site/public/index.html">
<span class="tag">Guide edition</span>
<h2>Process, rules and questions, without figures</h2>
<p>The original guide. It explains the legal sequence, the operating-cost categories and the decision gates
using illustrations only, and publishes no household amounts at all.</p>
<ul>
<li>Step-by-step trust inheritance process with statutory clocks</li>
<li>Current federal, state and local rules</li>
<li>Operational cost categories, with blanks where a value is unverified</li>
<li>The review queue, and the register of open questions</li>
</ul>
<p class="go">Open the guide edition</p>
</a>
</div>

<div class="banner warn"><b>Privacy boundary, stated plainly.</b> Amounts in the numeric edition are household
figures rounded to the nearest ten dollars, and rounding is disclosure minimisation, not anonymisation. No
street address, parcel number, account number, person, trust or year-by-year bill history is published in
either edition. The source repository is public and its history is a separate exposure surface; that
limitation is recorded on the numeric edition's flagged page and is an owner decision.</div>

<div class="banner"><b>Not advice.</b> Neither edition is legal, tax, investment or insurance advice. They
prepare the questions and the arithmetic for a licensed estate attorney, a tax adviser and an insurance broker.
Every figure that could not be confirmed from an official source is left blank and listed for review.</div>

<footer>
<p>Built {date}. No scripts, no forms, no cookies, no network requests other than the page you asked for.</p>
</footer>
</main></body></html>
""".format(css=CSS, date=BUILD_DATE)
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(doc)
    return 'index.html'


if __name__ == '__main__':
    print(build())
