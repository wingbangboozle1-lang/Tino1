#!/usr/bin/env python3
"""Build the static GitHub Pages site in docs/ from data/*.csv and the model output.

Run after analysis/model.py:  python3 analysis/build_site.py
No external dependencies. Every table row that states a fact carries a source link
(or an explicit status such as user-supplied / assumption / unverified).
"""
from __future__ import annotations

import csv
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)

BUILD_DATE = "2026-11-10"
SITE_TITLE = "Property Inheritance Decision Dashboard"

NAV = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("properties.html", "Properties"),
    ("process.html", "Inheritance process"),
    ("prop19.html", "Prop 19"),
    ("inheritance-tax.html", "Estate tax"),
    ("tax-law.html", "Tax law"),
    ("costs.html", "Operating costs"),
    ("projections.html", "Projections"),
    ("scenarios.html", "Scenarios & plan"),
    ("pending-legislation.html", "Pending changes"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
]


def esc(x) -> str:
    return html.escape("" if x is None else str(x))


def read_csv(name: str) -> list[dict]:
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


def money(x, blank="—") -> str:
    if x is None or x == "":
        return blank
    try:
        v = float(x)
    except ValueError:
        return esc(x)
    s = f"{abs(v):,.0f}"
    return ("−$" if v < 0 else "$") + s


def pct(x, nd=2) -> str:
    try:
        return f"{float(x) * 100:.{nd}f}%"
    except (TypeError, ValueError):
        return esc(x)


def badge(status: str) -> str:
    s = (status or "").strip().lower()
    key = s.split()[0] if s else "unverified"
    cls = {
        "verified": "ok", "derived": "warn", "user-supplied": "info", "assumption": "muted",
        "unverified": "bad", "pending": "warn", "ambiguity": "bad", "privacy": "info",
        "irregularity": "bad", "repo": "warn", "enacted": "ok", "passed": "ok", "leading": "warn",
        "failed": "muted", "current": "ok", "scheduled": "warn", "various;": "muted",
        "unenforceable": "warn", "annual": "warn", "effective": "ok",
    }.get(key, "muted")
    return f'<span class="badge {cls}">{esc(status)}</span>'


def link(url: str, text: str | None = None) -> str:
    if not url:
        return '<span class="nosrc">no official source — see status</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text or "source")}</a>'


def table(headers: list[str], rows: list[list[str]], cls: str = "") -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for r in rows:
        body.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def fact_table(rows: list[dict], cols=("item", "value", "unit", "as_of", "status", "source", "notes")) -> str:
    out = []
    for r in rows:
        val = r.get("value", "")
        try:
            fv = float(val)
            val_s = money(fv) if (r.get("unit", "").startswith("USD") and abs(fv) >= 1000) else esc(val)
        except ValueError:
            val_s = esc(val)
        out.append([
            f'<strong>{esc(r.get("item"))}</strong>',
            val_s or "<em>blank</em>",
            esc(r.get("unit")),
            esc(r.get("as_of")),
            badge(r.get("status")),
            link(r.get("source_url"), r.get("source_title") or "source"),
            esc(r.get("notes")),
        ])
    return table(["Item", "Value", "Unit", "As of", "Status", "Official source", "Notes"], out, "facts")


def page(fname: str, title: str, body: str, intro: str = "") -> None:
    nav = "".join(
        f'<a href="{f}" class="{"active" if f == fname else ""}">{t}</a>' for f, t in NAV
    )
    import re as _re
    def _slug(m):
        txt = _re.sub(r"<[^>]+>", "", m.group(1))
        sid = _re.sub(r"[^a-z0-9]+", "-", html.unescape(txt).lower()).strip("-")
        return f'<h2 id="{sid}">{m.group(1)}</h2>'
    body = _re.sub(r"<h2>(.*?)</h2>", _slug, body)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {SITE_TITLE}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html">{SITE_TITLE}</a>
    <div class="sub">Property A (Cupertino 95014) · Property B (San Francisco Outer Sunset 94122) · trust inheritance expected 2040–2050 · anonymized</div>
  </div>
  <nav class="wrap">{nav}</nav>
</header>
<main class="wrap">
<h1>{esc(title)}</h1>
{f'<p class="lead">{intro}</p>' if intro else ''}
{body}
</main>
<footer class="wrap">
  <p><strong>Status legend:</strong> {badge('verified')} read from an official source on {BUILD_DATE} ·
  {badge('derived')} computed from verified or user figures · {badge('user-supplied')} stated by the owner, not independently verified ·
  {badge('assumption')} model input, not a fact · {badge('unverified')} no official confirmation obtained (left blank where a value would be a guess).</p>
  <p>All amounts are rounded to the nearest $10. No names, addresses or parcel numbers appear anywhere on this site. This is an independent research summary, <strong>not legal, tax or investment advice</strong>; confirm every item with a California estate attorney and CPA before acting. Built {BUILD_DATE}. <a href="https://github.com/wingbangboozle1-lang/Tino1" target="_blank" rel="noopener">Repository</a> · <a href="flagged.html">Flagged for Review</a>.</p>
</footer>
</body>
</html>
"""
    with open(os.path.join(DOCS, fname), "w") as f:
        f.write(doc)


CSS = """
:root{--ink:#1b2430;--muted:#5c6b7a;--line:#dde3ea;--bg:#f6f8fa;--card:#fff;--accent:#0b5fff;--ok:#1b7f3b;--warn:#b26a00;--bad:#b3261e;--info:#1f5fa8}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.5;font-size:15px}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line)}
header.top .wrap:first-child{padding-top:16px;padding-bottom:6px}
.brand{font-weight:700;font-size:20px;color:var(--ink);text-decoration:none}
.sub{color:var(--muted);font-size:13px;margin-top:2px}
nav{display:flex;flex-wrap:wrap;gap:4px 2px;padding-bottom:8px}
nav a{padding:6px 10px;border-radius:6px;text-decoration:none;color:var(--ink);font-size:13.5px}
nav a:hover{background:var(--bg)}
nav a.active{background:var(--accent);color:#fff}
main{padding:22px 20px 40px}
h1{font-size:26px;margin:0 0 8px}
h2{font-size:20px;margin:30px 0 8px;padding-top:6px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:20px 0 6px}
p.lead{font-size:16px;color:var(--muted);margin:0 0 16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{font-size:12.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}
.card .v{font-size:24px;font-weight:700;margin:4px 0 2px}
.card .d{font-size:13px;color:var(--muted)}
.card a{color:var(--accent);text-decoration:none}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0 18px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{background:#eef2f6;position:sticky;top:0;font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#fafbfc}
td.num,th.num{text-align:right;white-space:nowrap}
table.num td:not(:first-child){text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap;border:1px solid transparent}
.badge.ok{background:#e6f4ea;color:var(--ok);border-color:#bfe3c8}
.badge.warn{background:#fff4e0;color:var(--warn);border-color:#f3d59a}
.badge.bad{background:#fdecea;color:var(--bad);border-color:#f5c2be}
.badge.info{background:#e8f0fb;color:var(--info);border-color:#bfd3f2}
.badge.muted{background:#eef0f2;color:#4b5563;border-color:#d6dadf}
.callout{background:#fff;border-left:4px solid var(--accent);border:1px solid var(--line);border-left-width:4px;border-radius:8px;padding:12px 16px;margin:14px 0}
.callout.warn{border-left-color:var(--warn)}
.callout.bad{border-left-color:var(--bad)}
.callout.ok{border-left-color:var(--ok)}
.nosrc{color:var(--bad);font-size:12.5px}
footer{padding:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
ol.steps li{margin-bottom:8px}
.small{font-size:12.5px;color:var(--muted)}
.best{background:#e6f4ea !important;font-weight:600}
code{background:#eef0f2;padding:1px 5px;border-radius:4px;font-size:12.5px}
"""


# ---------------------------------------------------------------------------
def main():
    with open(os.path.join(DOCS, "data", "model_output.json")) as f:
        M = json.load(f)
    P = M["params"]
    fed = read_csv("federal_tax.csv")
    ca = read_csv("california_tax.csv")
    loc = read_csv("local_rules.csv")
    ops = read_csv("operating_costs.csv")
    econ = read_csv("economic_indicators.csv")
    pend = read_csv("pending_changes.csv")
    flagged = read_csv("flagged.csv")
    hist_a = read_csv("property_a_history.csv")
    hist_b = read_csv("property_b_history.csv")
    scen = M["scenarios"]
    sens = M["sensitivity"]
    estate = M["estate_tax"]

    with open(os.path.join(DOCS, "assets", "style.css"), "w") as f:
        f.write(CSS)
    with open(os.path.join(DOCS, ".nojekyll"), "w") as f:
        f.write("")

    def S(key, field):
        return scen[key][field]

    s1, s2, s4, s6 = scen["S1"], scen["S2"], scen["S4"], scen["S6"]
    proj_a = M["projections"]["A_base"]
    proj_a_alt = M["projections"]["A_no_prop19"]
    proj_b = M["projections"]["B_base"]
    pa_2026 = proj_a[0]
    pa_2044 = next(r for r in proj_a if r["year"] == 2044)
    pa_2045 = next(r for r in proj_a if r["year"] == 2045)
    pa_alt_2045 = next(r for r in proj_a_alt if r["year"] == 2045)
    pb_2045 = next(r for r in proj_b if r["year"] == 2045)

    # Ranking of scenarios in the base case
    ranked = sorted(scen.values(), key=lambda r: -r["terminal_wealth_after_tax"])
    best_counts = {}
    for row in sens:
        best_counts[row["best"]] = best_counts.get(row["best"], 0) + 1

    # ------------------------------------------------------------------ index
    cards = [
        ("Federal estate-tax exclusion (2026)", "$15,000,000", "per decedent; indexed after 2026; 40% above it. <a href='inheritance-tax.html'>Estate tax →</a>"),
        ("California estate / inheritance tax", "$0", "none for deaths since 2005. <a href='tax-law.html'>Tax law →</a>"),
        ("Prop 19 value cap (2025–27)", "$1,044,586", "+ factored base value; only the transferor's home, heir must move in within 1 year. <a href='prop19.html'>Prop 19 →</a>"),
        ("Property A tax: 2044 → 2045 (base case)", f"{money(pa_2044['property_tax'])} → {money(pa_2045['property_tax'])}", "even with the Prop 19 exclusion, because value far exceeds base + cap. <a href='projections.html'>Projections →</a>"),
        ("Property B tax after reassessment (2045)", money(pb_2045["property_tax"]), "all rental units reassessed to market value. <a href='projections.html'>Projections →</a>"),
        ("Best plan (base case, after tax, 2055)", f"{ranked[0]['key']}: {money(ranked[0]['terminal_wealth_after_tax'])}", f"{esc(ranked[0]['name'])}. <a href='scenarios.html'>Scenarios →</a>"),
        ("Flagged items", str(len(flagged)), "unverified, derived or irregular items listed openly. <a href='flagged.html'>Flagged for Review →</a>"),
        ("Official sources cited", str(len({r['source_url'] for r in fed + ca + loc + econ + pend if r.get('source_url')})), f"read on {BUILD_DATE}. <a href='sources.html'>Sources →</a>"),
    ]
    cards_html = "".join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div><div class="d">{d}</div></div>' for k, v, d in cards)
    sections = "".join(
        f'<div class="card"><div class="k"><a href="{f}">{t}</a></div><div class="d">{d}</div></div>'
        for (f, t), d in zip(NAV[1:], [
            "The whole analysis on one page: facts, numbers, recommendation and reasoning.",
            "What is known about Property A and Property B (user-supplied data, benchmarks, privacy handling).",
            "Step-by-step timeline from the transferor's death to a settled, correctly assessed title.",
            "How the parent–child exclusion works, the value cap, the one-year move-in rule, multi-unit rule, worked numbers.",
            "Federal estate tax thresholds, rates, step-up in basis, and projected exposure 2040–2050.",
            "California and local rules: Prop 13, income tax, transfer tax, rent control, vacancy tax, tax rates.",
            "Insurance, water, electricity, maintenance and property tax — what is verified and what is not.",
            "Year-by-year 2026–2055 tables: value, assessed value, property tax and carrying costs.",
            "Live in / rent / sell-and-invest compared after tax, with sensitivity analysis and the recommended plan.",
            "Enacted and pending law changes at the federal, state and city level, and what they do to the plan.",
            "Every unverified, derived, ambiguous or irregular item, with what would resolve it.",
            "All official sources used, grouped by authority.",
            "Model parameters, formulas, privacy rules and how to re-run the analysis.",
        ])
    )
    headline = f"""
<div class="callout ok"><strong>Headline findings</strong>
<ol>
<li><strong>No estate tax is expected on the two properties alone.</strong> They are worth about $4.9 million today and roughly {money(estate[0]['properties_value'])}–{money([r for r in estate if r['death_year']==2050][0]['properties_value'])} in 2040–2050 (base appreciation), versus a federal exclusion of $15 million in 2026 that is indexed for inflation (about {money(estate[0]['exclusion_per_person'])} per person by 2040 at 2.5%/yr). California has no estate or inheritance tax. Estate tax only becomes relevant if <em>other</em> assets push the estate above the exclusion — see the <a href="inheritance-tax.html">exposure table</a>.</li>
<li><strong>Inheriting (not gifting) gives a full step-up in basis</strong> (26 U.S.C. §1014): decades of appreciation become tax-free if the heir sells soon after death. This is the single most valuable tax feature of the plan.</li>
<li><strong>Prop 19 helps far less than most people expect.</strong> Only the transferor's principal residence qualifies, the heir must move in within one year, and the excluded amount is capped at the factored base value plus about $1.04–1.6 million. For Property A (base case, 2045) the assessed value still jumps from about {money(pa_2044['assessed_value'])} to {money(pa_2045['assessed_value'])} and the tax bill from {money(pa_2044['property_tax'])} to {money(pa_2045['property_tax'])} per year. Property B's rental units get no exclusion at all and are reassessed to full market value ({money(pb_2045['property_tax'])}/yr in 2045).</li>
<li><strong>Keeping a reassessed $6–7 million house is expensive:</strong> about {money(S('S2','year1_net_cash')*-1)} per year of carrying cost in 2045 for Property A alone. Selling it at the stepped-up basis (little or no capital-gains tax) and investing the proceeds produces the highest after-tax wealth in {best_counts.get('S4',0)+best_counts.get('S6',0)} of {len(sens)} sensitivity cases; keeping both properties wins only when appreciation is high (≥6%/yr) <em>and</em> investment returns are low (≤5%).</li>
<li><strong>Recommended plan (base case):</strong> {esc(ranked[0]['name'])} — after-tax wealth of {money(ranked[0]['terminal_wealth_after_tax'])} in 2055 versus {money(scen['S1']['terminal_wealth_after_tax'])} for living in A and keeping B. The lifestyle difference (a 2-bedroom flat vs a large Cupertino house) is real and is priced in the <a href="scenarios.html">scenario page</a>; if the heir wants to live in Property A, the next-best plan is to live in A and sell B (S2).</li>
</ol></div>"""
    page("index.html", "Dashboard", f"""
{headline}
<h2>Key numbers</h2>
<div class="cards">{cards_html}</div>
<h2>Sections</h2>
<div class="cards">{sections}</div>
<div class="callout warn"><strong>How to read this site.</strong> Every table row shows a status badge and an official source link. Where no official confirmation could be obtained, the value is left blank and the row is listed on the <a href="flagged.html">Flagged for Review</a> page — nothing has been filled in by guesswork. Numbers that come from the owner are marked <em>user-supplied</em>; numbers computed by the model are marked <em>derived</em> or <em>assumption</em>.</div>
""", "A self-contained research and decision dashboard for inheriting two California properties through a revocable trust. All figures rounded to the nearest $10.")

    # ------------------------------------------------------- executive summary
    key_facts = [
        ["Federal estate-tax basic exclusion", "$15,000,000 (2026), indexed from 2027; 40% rate above it; portability doubles it for married transferors", badge("verified"), link("https://www.irs.gov/pub/irs-drop/rp-25-32.pdf", "Rev. Proc. 2025-32") + " · " + link("https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleB-chap11-subchapA-partI-sec2001.htm", "26 U.S.C. §2001")],
        ["California estate / inheritance / gift tax", "None (deaths on or after Jan 1 2005)", badge("verified"), link("https://www.sco.ca.gov/ardtax_estate_tax.html", "State Controller")],
        ["Income-tax basis of inherited property", "Fair market value at date of death (step-up), including revocable-trust property", badge("verified"), link("https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapO-partII-sec1014.htm", "26 U.S.C. §1014")],
        ["Property-tax reassessment on inheritance", "Change in ownership at the trustor's death; reassessed to market value unless an exclusion applies", badge("verified"), link("https://www.boe.ca.gov/prop19/", "BOE Prop 19")],
        ["Prop 19 parent–child exclusion", "Transferor's principal residence only; heir must move in and file BOE-266 within 1 year; excluded amount = factored base value + $1,044,586 (2025–27); claim BOE-19-P within 3 years", badge("verified"), link("https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf", "BOE LTA 2026/026") + " · " + link("https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf", "LTA 2025/009")],
        ["Multi-unit building (Property B)", "Only the unit the transferor lived in can qualify; the other units are reassessed to full market value", badge("verified"), link("https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf", "BOE LTA 2026/026 Q5/Q15")],
        ["Property-tax rates", "San Francisco 1.18162182% (FY2026-27); Cupertino about 1.1636% (derived from FY2025-26 rate book components) + direct charges", badge("verified") + " " + badge("derived"), link("https://sftreasurer.org/property/secured-property-taxes", "SF TTX") + " · " + link("https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE", "SCC rate book")],
        ["Capital-gains tax on a later sale", "Federal 20% + 3.8% NIIT; California up to 12.3% + 1% above $1 million taxable income (gains taxed as ordinary income) → about 37.1% combined on large gains; $250,000/$500,000 exclusion only for the heir's own home (2 of 5 years)", badge("verified"), link("https://www.irs.gov/taxtopics/tc409", "IRS 409") + " · " + link("https://www.irs.gov/taxtopics/tc701", "IRS 701") + " · " + link("https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf", "FTB") + " · " + link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17043.", "R&TC §17043")],
        ["Transfer tax", "None on the inheritance itself (R&TC §11930). On a later sale: SF 0.75% ($1M–<$5M tier); Santa Clara County 0.11%", badge("verified"), link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11930.", "R&TC §11930") + " · " + link("https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco", "SF fees")],
        ["San Francisco rent rules", "Pre-June-14-1979 multi-unit buildings: rent control (1.6% allowable increase 2026–27) + just-cause eviction; rents reset to market on voluntary vacancy", badge("verified"), link("https://www.sf.gov/news--annual-rent-increase-3126-22827-announced", "sf.gov") + " · " + link("https://www.sf.gov/learn-about-san-francisco-rental-laws", "SF rental laws")],
        ["San Francisco Empty Homes Tax", "Struck down (Court of Appeal, Sept 11 2026); not collected; could be revived on further review", badge("verified"), link("https://sftreasurer.org/business/taxes-fees/empty-homes-tax-eht", "SF TTX")],
    ]
    base_rows = []
    for r in ranked:
        base_rows.append([f"<strong>{esc(r['key'])}</strong> {esc(r['name'])}",
                          money(r["year1_net_cash"]), money(r["year1_housing_value_consumed"]),
                          money(r["terminal_wealth_after_tax"]), money(r["terminal_wealth_2026_dollars"])])
    page("executive-summary.html", "Executive summary", f"""
<h2>1. Situation</h2>
<p>The Heir expects to inherit, through the Transferor's revocable trust, sometime between 2040 and 2050:</p>
<ul>
<li><strong>Property A</strong> — single-family home in Cupertino (ZIP 95014), estimated value $3,100,000 (Nov 2026, user estimate). Low Prop 13 assessed value (about $539,740 in 2025, user-supplied) and a 2025 tax bill of about $7,210. Solar (net electricity credit), water $100–150/month, lower maintenance.</li>
<li><strong>Property B</strong> — three-unit building in San Francisco's Outer Sunset (ZIP 94122), estimated value $1,800,000. Two units rented for a combined $7,150/month; one unit vacant and available for the Heir. Water $330–400/month, electricity $30–70/month.</li>
</ul>
<p>The model assumes Property A is the Transferor's principal residence and that both properties are held 100% in the trust (both assumptions are <a href="flagged.html">flagged</a> because they change the answer).</p>

<h2>2. The rules that decide the outcome (all verified)</h2>
{table(["Rule", "What it says", "Status", "Source"], key_facts)}

<h2>3. What happens at inheritance (base case: death in 2045)</h2>
<ul>
<li><strong>Estate tax:</strong> the two properties are projected at {money(s1['value_a_at_inheritance'])} (A) and {money(s1['value_b_at_inheritance'])} (B) — a combined {money(s1['value_a_at_inheritance'] + s1['value_b_at_inheritance'])}, well under a projected per-person exclusion of about {money([r for r in estate if r['death_year']==2045][0]['exclusion_per_person'])}. Only if the Transferor's <em>other</em> assets exceed roughly {money([r for r in estate if r['death_year']==2045][0]['exclusion_per_person'] - s1['value_a_at_inheritance'] - s1['value_b_at_inheritance'])} (single) would federal estate tax (40% on the excess) arise. No California estate tax. See <a href="inheritance-tax.html">Estate tax</a>.</li>
<li><strong>Income tax:</strong> both properties receive a stepped-up basis equal to date-of-death value; selling within a year or so produces essentially no capital-gains tax.</li>
<li><strong>Property tax, Property A:</strong> if the Heir moves in within one year, the Prop 19 exclusion limits the new assessed value to {money(pa_2045['assessed_value'])} instead of {money(pa_alt_2045['assessed_value'])} — a saving of about {money(s1['prop19_tax_saving_year1'])} per year — but the bill still rises from {money(pa_2044['property_tax'])} (2044) to {money(pa_2045['property_tax'])} (2045). If the Heir does not move in, the bill is {money(pa_alt_2045['property_tax'])}.</li>
<li><strong>Property tax, Property B:</strong> all three units are reassessed to market value; the bill becomes about {money(pb_2045['property_tax'])} per year (from a very low Prop 13 base today).</li>
<li><strong>Rents:</strong> existing tenancies in B continue under rent control (if the building pre-dates 1979 — unverified); the vacant unit can be rented at market (about $3,500/month today, HUD benchmark) or occupied by the Heir.</li>
</ul>

<h2>4. Options compared (after tax, inheritance 2045, evaluated at 2055)</h2>
<p>Terminal wealth = after-tax value of whatever is still owned (properties sold at 2055 values net of selling costs, capital-gains and depreciation-recapture tax) plus an investment account that receives all net cash flows (or funds shortfalls) at a 7% nominal return. "Housing value consumed" shows the market rent of the home the Heir occupies (or pays) in year 1, because the options differ in how much housing the Heir enjoys.</p>
{table(["Scenario", "Year-1 net cash flow (2045)", "Housing value consumed (2045)", "After-tax wealth 2055 (nominal)", "In 2026 dollars"], base_rows, "num")}
<p class="small">Full tables, yearly detail and 27 sensitivity cases (inheritance year × appreciation × investment return) are on the <a href="scenarios.html">Scenarios page</a>.</p>

<h2>5. Recommendation and reasoning</h2>
<div class="callout ok">
<p><strong>Best plan to maximize after-tax wealth and minimize cost (base case): {esc(ranked[0]['key'])} — {esc(ranked[0]['name'])}.</strong> Close second: {esc(ranked[1]['key'])} — {esc(ranked[1]['name'])} ({money(ranked[1]['terminal_wealth_after_tax'])}).</p>
<ol>
<li><strong>Sell Property A soon after inheritance.</strong> The stepped-up basis makes the sale almost tax-free (only post-death appreciation is taxed), and it eliminates a carrying cost of about {money(-S('S2','year1_net_cash'))} per year in 2045 (property tax {money(pa_2045['property_tax'])} even with Prop 19, plus insurance, water and maintenance). Net proceeds of about {money(s4['sale_at_inheritance_a']['net'])} invested at 7% earn about {money(s4['sale_at_inheritance_a']['net']*0.07)} a year — far more than the house's expected appreciation of 4% minus its costs. Prop 19's capped exclusion only saves about {money(s1['prop19_tax_saving_year1'])}/yr, not enough to change this.</li>
<li><strong>Keep Property B and live in the vacant unit</strong> if the Heir is content with that home: it provides rent-free housing, two rent-controlled units produce modest net income (about {money(s4['yearly'][0]['b_rent_net'] - s4['yearly'][0]['b_costs'])} after costs in 2045 before income tax), and B's land in San Francisco keeps appreciating. If the Heir does not want to live in B, selling both and renting (S6, {money(s6['terminal_wealth_after_tax'])}) is nearly as good as S4 and avoids landlord obligations under San Francisco's rent ordinance.</li>
<li><strong>If living in Property A is a priority</strong>, choose S2 (live in A, sell B and invest the proceeds: {money(s2['terminal_wealth_after_tax'])}). It costs about {money(ranked[0]['terminal_wealth_after_tax'] - s2['terminal_wealth_after_tax'])} of 2055 wealth versus the best plan — the price of living in a {money(s1['value_a_at_inheritance'])} house whose market rent is about {money(s1['year1_housing_value_consumed'])}/yr. Move in and file the Homeowners' Exemption within one year of death to keep the Prop 19 exclusion; staying at least two years also unlocks the $250,000/$500,000 home-sale exclusion on later gains.</li>
<li><strong>Do not hold both properties as pure rentals (S5)</strong>: it is the worst outcome in every sensitivity case — after reassessment, net rental yields are about 2–3% of value while the Heir also pays rent elsewhere.</li>
<li><strong>Do not accept a lifetime gift of either property.</strong> A gift carries over the Transferor's low basis (no step-up), triggers the same Prop 19 reassessment rules, and uses estate/gift exclusion. Inheritance through the trust is strictly better.</li>
</ol>
<p><strong>When the answer flips:</strong> keeping Property A (S1) wins only when home prices rise ≥6%/yr <em>and</em> portfolio returns are ≤5%/yr. The ranking is insensitive to the inheritance year (2040/2045/2050).</p>
</div>

<h2>6. Actions now (2026–2039), by the Transferor and Heir together</h2>
<ol class="steps">
<li>Confirm the trust is a revocable living trust holding title to both properties (avoids probate; preserves the §1014 step-up). Keep the Homeowners' Exemption on Property A in the Transferor's name (it evidences the "family home").</li>
<li>Keep records: purchase documents, improvements and depreciation on B (needed for the final returns and the trust's Form 1041 if rents are earned before distribution).</li>
<li>Decide now whether the Heir would realistically move into A within 12 months of death — the exclusion has no grace period. If not, plan for a sale and for roughly {money(pa_alt_2045['property_tax'])}/yr of tax while the house is marketed (2045 base case).</li>
<li>Verify the flagged inputs that matter most: B's build year / rent-control status, both insurance premiums, and which property carries the Homeowners' Exemption. See <a href="flagged.html">Flagged for Review</a>.</li>
<li>Re-check the law every two years: Prop 19 cap adjustment (next Feb 16 2027), the federal exclusion (any Congress can change it), certified results of Props 3 and 42, and the Empty Homes Tax litigation. See <a href="pending-legislation.html">Pending changes</a>.</li>
</ol>
""", "The complete analysis in one page. Figures are nominal dollars unless marked, rounded to the nearest $10, from a transparent model whose inputs are listed on the Methodology page.")

    # ------------------------------------------------------------- properties
    def ops_table(prop):
        rows = []
        for r in ops:
            if r["property"] not in (prop, "Both"):
                continue
            lo, hi = r["value_low"], r["value_high"]
            val = money(lo) if lo == hi else f"{money(lo)} – {money(hi)}"
            if r["unit"].startswith("percent"):
                val = f"{lo}%" if lo == hi else f"{lo}–{hi}%"
            rows.append([f"<strong>{esc(r['item'])}</strong>", val, esc(r["unit"]), esc(r["as_of"]), badge(r["status"]), link(r["source_url"], r["source_title"]) if r["source_url"] else esc(r["source_title"]), esc(r["notes"])])
        return table(["Item", "Value", "Unit", "As of", "Status", "Source", "Notes"], rows, "facts")

    def hist_table(rows):
        return table(["Year", "Assessed value", "Property tax", "Status", "Source", "Notes"],
                     [[esc(r["year"]), money(r["assessed_value_usd"], "<em>withheld</em>"), money(r["property_tax_usd"], "<em>withheld</em>"), badge(r["status"]), esc(r["source"]), esc(r["notes"])] for r in rows], "facts")

    bench = [r for r in loc if r["id"] in ("L18", "L19")]
    page("properties.html", "Properties", f"""
<div class="callout"><strong>Privacy.</strong> The repository is public. Properties are identified only by ZIP code; people only as Transferor and Heir. Year-by-year assessed values supplied by the owner are <em>not</em> published because exact assessed values can be matched to public assessment rolls; only a rounded 2025 anchor (A) and a derived ratio (B) are retained.</div>
<h2>Property A — Cupertino, ZIP 95014 (single-family, solar)</h2>
{ops_table('A')}
<h3>Assessment history</h3>
{hist_table(hist_a)}
<h2>Property B — San Francisco Outer Sunset, ZIP 94122 (3 units; 2 rented, 1 vacant)</h2>
{ops_table('B')}
<h3>Assessment history</h3>
{hist_table(hist_b)}
<h2>Official rent benchmarks (HUD FY2026 Fair Market Rents)</h2>
{fact_table(bench)}
<p class="small">HUD FMRs are 40th-percentile gross rents used for housing-voucher payment standards; they are a conservative floor, not an appraisal of what either property would rent for.</p>
""", "What is known about each property, with the owner's figures clearly separated from verified benchmarks.")

    # ---------------------------------------------------------------- process
    steps = [
        ["Before death", "Transferor keeps both properties titled in the revocable trust; keeps the Homeowners' Exemption on the home actually occupied; keeps records of basis, improvements and rental depreciation; names a successor trustee.", "Preserves the §1014 step-up and the Prop 19 'family home' status; avoids probate.", link("https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapO-partII-sec1014.htm", "26 U.S.C. §1014") + " · " + link("https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm", "BOE HOX")],
        ["Day 0 — death", "Trust becomes irrevocable; change in ownership for property-tax purposes occurs on this date (R&TC §61(h)); values on this date set the income-tax basis and the Prop 19 full cash value.", "Order date-of-death appraisals for both properties.", link("https://www.boe.ca.gov/prop19/", "BOE Prop 19")],
        ["Within 60 days", "Successor trustee serves the Probate Code §16061.7 notice on all beneficiaries and heirs (starts the 120-day contest period). Obtain death certificates; get an EIN for the now-irrevocable trust; open a trust account.", "Statutory duty of the trustee.", link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.", "Prob. Code §16061.7")],
        ["Within 150 days", "File BOE-502-D (Change in Ownership Statement — Death of Real Property Owner) with the Santa Clara County Assessor (A) and the San Francisco Assessor-Recorder (B); record affidavits of death of trustee / trustee's deeds as needed. Transfers by reason of death are exempt from documentary transfer tax (R&TC §11930).", "Late filing penalty: greater of $100 or 10% of the new tax if not filed within 90 days of the assessor's request.", link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.", "R&TC §480") + " · " + link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11930.", "R&TC §11930")],
        ["Within 1 year", "If the Heir will keep Property A as a home: move in and file BOE-266 (Homeowners' Exemption) with the Santa Clara County Assessor. There is no extension to this deadline.", "Required for any Prop 19 exclusion; also claims the $7,000 exemption.", link("https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf", "BOE LTA 2026/026 Q7") + " · " + link("https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2", "SCC Assessor")],
        ["Within 9 months (+6 month extension)", "File federal Form 706 only if the gross estate plus adjusted taxable gifts exceeds the year-of-death exclusion ($15 million in 2026, indexed) — or to elect portability for a surviving spouse. If filed, Form 8971 basis statements go to the heirs.", "Most likely not required for the two properties alone; required if other assets are large.", link("https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes", "IRS estate FAQs") + " · " + link("https://www.irs.gov/individuals/deceased-person", "IRS deceased person")],
        ["By April 15 of the following year", "Trustee files the Transferor's final Form 1040 / 540 and, if the trust received rent or sale proceeds, Form 1041 / 541 for the trust.", "Rents from Property B after death belong to the trust until distribution.", link("https://www.irs.gov/individuals/deceased-person", "IRS deceased person")],
        ["Within 3 years", "File BOE-19-P (parent–child exclusion claim) for Property A with the Santa Clara County Assessor. Late claims receive prospective relief only. San Francisco's Assessor follows the same forms for Property B's owner-occupied unit if applicable.", "Secures the exclusion back to the date of death.", link("https://www.boe.ca.gov/prop19/", "BOE Prop 19") + " · " + link("https://media.api.sf.gov/documents/ASR_Factsheet_Prop19_Family_Transfers_English_BosXWmZ.pdf", "SF Assessor fact sheet")],
        ["When supplemental bills arrive", "Both counties issue supplemental assessments for the reassessed value from the date of death; pay by the Dec 10 / Apr 10 delinquency dates (10% penalty).", "Budget for the jump shown on the Projections page.", link("https://sftreasurer.org/property/secured-property-taxes", "SF TTX") + " · " + link("https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE", "SCC rate book")],
        ["Distribution", "Trustee distributes the properties (or sale proceeds) per the trust; record deeds from trustee to Heir (exempt from transfer tax as a distribution under a trust by reason of death). Heir's holding period is automatically long-term.", "Then execute the chosen scenario.", link("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11930.", "R&TC §11930")],
        ["If selling", "List soon after the appraisal so the sale price ≈ stepped-up basis (minimal gain). Selling costs: ~5% commissions/closing (assumption) + transfer tax (SF 0.75%; Santa Clara County 0.11%). For a rental sold later: depreciation recapture at up to 25% federal + California ordinary rates.", "Property B tenants keep their tenancies through a sale (rent ordinance).", link("https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco", "SF transfer tax") + " · " + link("https://www.irs.gov/taxtopics/tc409", "IRS 409")],
        ["If keeping B as a rental", "Register with the SF Rent Board as required, follow the annual allowable increase (1.6% for Mar 2026–Feb 2027), keep all units occupied (Empty Homes Tax risk if revived), report rents on Schedule E with depreciation.", "Owner move-in into an occupied unit is a just-cause eviction with strict conditions — the vacant unit avoids this.", link("https://www.sf.gov/learn-about-san-francisco-rental-laws", "SF rental laws") + " · " + link("https://sftreasurer.org/business/taxes-fees/empty-homes-tax-eht", "EHT")],
    ]
    page("process.html", "Inheritance process (step by step)", table(["When", "What to do", "Why / consequence", "Official source"], steps) + """
<div class="callout warn"><strong>Not covered here:</strong> trust-contest procedures, creditor claims, Medi-Cal estate recovery, and non-California assets. A California estate attorney should run the administration; the deadlines above are the ones that cost money when missed.</div>
""", "From the Transferor's death to a settled title, with every statutory deadline and form.")

    # ----------------------------------------------------------------- prop19
    def p19_calc(T):
        n = T - 2025
        fbyv = P["av_a_2025"] * (1 + P["av_growth"]) ** n
        cap = P["prop19_cap_2025"] * (1 + P["prop19_cap_growth"]) ** n
        fmv = P["value_a_2026"] * (1 + P["appreciation_a"]) ** (T - 2026)
        limit = fbyv + cap
        new_av = fbyv if fmv <= limit else fbyv + (fmv - limit)
        tax_excl = (new_av - P["hox"]) * P["rate_a"]
        tax_full = fmv * P["rate_a"]
        r10 = lambda x: round(x / 10.0) * 10
        return [str(T), money(r10(fbyv)), money(r10(cap)), money(r10(limit)), money(r10(fmv)), money(r10(new_av)), money(r10(tax_excl)), money(r10(tax_full)), money(r10(tax_full - tax_excl))]
    p19rows = [p19_calc(T) for T in (2040, 2045, 2050)]
    p19_rules = [r for r in ca if r["id"] in ("C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11")] + [r for r in loc if r["id"] in ("L16", "L17")]
    page("prop19.html", "Proposition 19 — parent–child exclusion", f"""
<h2>Rules (verified)</h2>
{fact_table(p19_rules)}
<h2>Worked calculation for Property A (model, base case)</h2>
<p>Formula (BOE LTA 2026/026 definitions): <em>excluded amount</em> = factored base year value (FBYV) + adjusted $1 million; if full cash value (FMV) exceeds it, <em>new taxable value</em> = FBYV + (FMV − excluded amount). FBYV grows 2%/yr from the user-supplied 2025 value; the cap grows 2%/yr (assumption) from $1,044,586; FMV grows 4%/yr (assumption).</p>
{table(["Death year", "FBYV", "Adjusted $1M cap", "Excluded amount", "FMV at death", "New taxable value (heir occupies)", "Tax with exclusion (1.1636%, after HOX)", "Tax if reassessed in full", "Annual saving"], p19rows, "num")}
<div class="callout warn"><strong>Interpretation.</strong> Because Property A's market value is many times its Prop 13 base, the exclusion shelters only about $1.5 million of value in the 2040s. The saving (about $18,000–20,000 per year) is real but small relative to a $59,000+ tax bill, and it is lost the moment the Heir stops living there (the date-of-death market value, factored, is then enrolled — LTA 2026/026 "continual use").</div>
<h2>Property B (three units)</h2>
<ul>
<li>If the Transferor's principal residence is Property A, <strong>no part of Property B qualifies</strong>: all three units are reassessed to market value at death (rental/investment property — BOE Prop 19 page; LTA 2026/026 Q5).</li>
<li>If the Transferor instead lives in one unit of B, only that unit (about one-third of the value) can be excluded, and only if the Heir moves into <em>that</em> unit within one year; the two tenant-occupied units are reassessed regardless (Q5, Q15).</li>
<li>The Heir can claim the Homeowners' Exemption on only one home, so living in A and claiming B's unit (or vice-versa) is not possible.</li>
</ul>
<h2>Common pitfalls</h2>
<ul>
<li>Missing the one-year move-in / BOE-266 deadline — no exceptions (Q7).</li>
<li>Adding the Heir to title during life, or gifting the property: triggers change-in-ownership analysis now and forfeits the income-tax step-up.</li>
<li>Transferring a property into an LLC or to a non-child: the exclusion is personal to parent–child (and grandparent–grandchild with deceased middle generation).</li>
<li>Step-transaction: temporary occupancy or paper moves to qualify are disregarded (Q9).</li>
</ul>
""", "How the 2021 rules limit the old parent–child exclusion, and what they mean for each property.")

    # --------------------------------------------------------- inheritance tax
    est_rows = []
    for r in estate:
        est_rows.append([str(r["death_year"]), esc(r["transferor"]), money(r["exclusion_per_person"]), money(r["properties_value"]), money(r["other_assets"]), money(r["gross_estate"]), money(r["amount_over_exclusion"]), money(r["federal_estate_tax"]), money(r["california_estate_tax"])])
    page("inheritance-tax.html", "Estate and inheritance tax", f"""
<h2>Federal rules (verified)</h2>
{fact_table([r for r in fed if r['topic'] in ('Estate tax', 'Gift tax')])}
<h2>State and local</h2>
{fact_table([r for r in ca if r['id'] == 'C01'])}
<p>Neither Santa Clara County, Cupertino nor San Francisco levies an inheritance or estate tax; the only death-related local charge is the property-tax reassessment covered on the <a href="prop19.html">Prop 19</a> page. Transfers by reason of death are exempt from documentary transfer tax (R&TC §11930).</p>
<h2>Projected exposure — "a considerable amount of money" beyond the two properties</h2>
<p>Model: exclusion of $15,000,000 (2026) indexed at 2.5%/yr (assumption; the statute indexes to chained CPI); properties appreciate at the base rates (A 4%, B 3%). The tax is 40% of the amount above the exclusion. "Married (portability)" assumes the first spouse's unused exclusion was preserved by a timely Form 706.</p>
{table(["Death year", "Transferor", "Exclusion per person", "Two properties", "Other assets", "Gross estate", "Amount over exclusion", "Federal estate tax", "California"], est_rows, "num")}
<div class="callout"><strong>Reading the table.</strong> In 2045 a single Transferor can leave roughly {money([r for r in estate if r['death_year']==2045][0]['exclusion_per_person'])} free of federal estate tax; after the two properties ({money([r for r in estate if r['death_year']==2045][0]['properties_value'])}) that leaves about {money([r for r in estate if r['death_year']==2045][0]['exclusion_per_person'] - [r for r in estate if r['death_year']==2045][0]['properties_value'])} of room for cash and investments. Above that, each extra $1,000,000 costs $400,000 of estate tax — which is where lifetime annual-exclusion gifts ($19,000 per donee in 2026), charitable planning, or spousal portability matter. Inherited cash and securities also receive a stepped-up basis.</div>
<h2>Income-tax consequences for the Heir</h2>
{fact_table([r for r in fed if r['topic'] == 'Income tax'])}
""", "Thresholds, rates, filing duties and how large the estate must be before any tax is due.")

    # ---------------------------------------------------------------- tax law
    page("tax-law.html", "California and local tax law", f"""
<h2>California (state) rules</h2>
{fact_table(ca)}
<h2>Local rules — Santa Clara County / Cupertino and San Francisco</h2>
{fact_table(loc)}
""", "Every state and local rule that affects the properties, each with its official source.")

    # ------------------------------------------------------------------ costs
    cost_cols = ["Year", "Property tax", "Insurance", "Water/sewer", "Electricity", "Maintenance", "Total carrying cost"]
    def cost_rows(proj, years):
        return [[str(r["year"]), money(r["property_tax"]), money(r["insurance"]), money(r["water_sewer"]), money(r["electricity"]), money(r["maintenance"]), money(r["total_carrying_cost"])] for r in proj if r["year"] in years]
    yrs = (2026, 2030, 2035, 2040, 2044, 2045, 2050, 2055)
    page("costs.html", "Operating costs", f"""
<h2>Inputs</h2>
<h3>Property A</h3>{ops_table('A')}
<h3>Property B</h3>{ops_table('B')}
<h2>Verified cost-related references</h2>
{fact_table([r for r in loc if r['id'] in ('L01','L08','L09','L13','L20','L21')])}
<h2>Projected annual carrying costs (base case; heir occupies A from 2045; B fully reassessed in 2045)</h2>
<h3>Property A</h3>{table(cost_cols, cost_rows(proj_a, yrs), 'num')}
<h3>Property B (owner-paid costs for all 3 units, before rent)</h3>{table(cost_cols, cost_rows(proj_b, yrs), 'num')}
<p class="small">Growth assumptions: assessed value 2%/yr (constitutional maximum), insurance 5%/yr, utilities 4%/yr, maintenance 2.5%/yr (CPI). Property B's pre-2045 property tax is left blank because the pre-inheritance assessed-value series is not published (privacy) and is the Transferor's cost in any case.</p>
""", "What each property costs to hold, now and after inheritance, with the status of every input.")

    # ------------------------------------------------------------ projections
    pcols = ["Year", "Owner", "Market value", "Assessed value", "Property tax", "Insurance", "Water/sewer", "Electricity", "Maintenance", "Total carrying cost", "Note"]
    def proj_rows(proj, y0=2026, y1=2055):
        return [[str(r["year"]), esc(r["owner"]), money(r["market_value"]), money(r["assessed_value"]), money(r["property_tax"]), money(r["insurance"]), money(r["water_sewer"]), money(r["electricity"]), money(r["maintenance"]), money(r["total_carrying_cost"]), esc(r["note"])] for r in proj if y0 <= r["year"] <= y1]
    rents = M["projections"]["rents"]
    rent_rows = [[str(r["year"]), money(r["two_units_rent_controlled_path"]), money(r["two_units_market_path"]), money(r["third_unit_market"]), money(r["property_a_market_rent"])] for r in rents if r["year"] in (2026, 2030, 2035, 2040, 2045, 2050, 2055)]
    page("projections.html", "Year-by-year projections (2026–2055)", f"""
<div class="callout"><strong>Assumptions (see <a href="methodology.html">Methodology</a>):</strong> inheritance in 2045; home values +4%/yr (A) and +3%/yr (B) — FHFA 5-year averages were 5.0% (San Jose MSA) and 3.3% (San Francisco MSAD) to 2026Q2; assessed values +2%/yr (Prop 13 maximum); Cupertino rate 1.1636% + direct charges (derived); San Francisco rate 1.18162%; CPI 2.5%; utilities 4%; insurance 5%. Everything is nominal dollars rounded to $10.</div>
<h2>Property A — base case (heir moves in; Prop 19 partial exclusion)</h2>
{table(pcols, proj_rows(proj_a), 'num')}
<h2>Property A — if the heir does not occupy it (full reassessment)</h2>
{table(pcols, proj_rows(proj_a_alt, 2043, 2055), 'num')}
<h2>Property B — base case (all units reassessed at inheritance)</h2>
{table(pcols, proj_rows(proj_b), 'num')}
<h2>Rent paths used by the model (per year)</h2>
{table(["Year", "B: two existing units (rent-controlled, +1.6%/yr)", "B: two units if re-let at market (+3%/yr)", "B: third unit at market", "A: market rent (HUD 4BR SAFMR base)"], rent_rows, 'num')}
<p class="small">Raw CSVs: <code>data/projections/</code> in the repository.</p>
""", "Market value, assessed value, property tax, insurance, water, electricity and maintenance for each property, every year.")

    # -------------------------------------------------------------- scenarios
    sc_rows = []
    for r in ranked:
        sc_rows.append([f"<strong>{esc(r['key'])}</strong>", esc(r["name"]), esc(r["description"]),
                        money(r["assessed_a_year1"]), money(r["assessed_b_year1"]),
                        money(r["year1_property_tax_a"]), money(r["year1_property_tax_b"]),
                        money(r["year1_net_cash"]), money(r["year1_housing_value_consumed"]),
                        money(r["cumulative_net_cash"]), money(r["portfolio_end_after_tax"]), money(r["property_liquidation_after_tax"]),
                        f"<strong>{money(r['terminal_wealth_after_tax'])}</strong>", money(r["terminal_wealth_2026_dollars"])])
    yearly_blocks = ""
    for key in ("S1", "S2", "S3", "S4", "S5", "S6"):
        r = scen[key]
        hdr = ["Year", "A: property tax", "A: all costs", "A: net rent", "B: property tax", "B: all costs", "B: net rent", "Income tax on rents", "Housing paid elsewhere", "Net cash flow", "Investment account (end)"]
        rows = []
        for y in r["yearly"]:
            rows.append([str(y["year"]), money(y.get("a_property_tax")), money(y.get("a_costs")), money(y.get("a_rent_net")), money(y.get("b_property_tax")), money(y.get("b_costs")), money(y.get("b_rent_net")),
                         money((y.get("a_income_tax") or 0) + (y.get("b_income_tax") or 0)), money(y.get("housing_paid")), money(y.get("net_cash")), money(y.get("portfolio_end"))])
        sale_bits = []
        if r["sale_at_inheritance_a"]:
            s_ = r["sale_at_inheritance_a"]; sale_bits.append(f"A sold 2045: gross {money(s_['gross'])}, costs {money(s_['selling_costs'])}, tax {money(s_['cap_gains_tax'])}, net {money(s_['net'])}")
        if r["sale_at_inheritance_b"]:
            s_ = r["sale_at_inheritance_b"]; sale_bits.append(f"B sold 2045: gross {money(s_['gross'])}, costs {money(s_['selling_costs'])}, tax {money(s_['cap_gains_tax'])}, net {money(s_['net'])}")
        for k2, lab in (("a_sale_at_horizon", "A sold 2055"), ("b_sale_at_horizon", "B sold 2055")):
            if k2 in r["details"]:
                s_ = r["details"][k2]; sale_bits.append(f"{lab}: gross {money(s_['gross'])}, costs {money(s_['selling_costs'])}, gain {money(s_['gain'])}, capital-gains tax {money(s_['cap_gains_tax'])}, recapture tax {money(s_['recapture_tax'])}, net {money(s_['net'])}")
        yearly_blocks += f"<h3>{esc(key)} — {esc(r['name'])}</h3><p class='small'>{esc(r['description'])}<br>{'<br>'.join(esc(b) for b in sale_bits)}</p>" + table(hdr, rows, "num")
    sens_rows = []
    for row in sens:
        cells = [str(row["inherit_year"]), esc(row["appreciation_case"]), f"{row['portfolio_return']*100:.0f}%"]
        for k in ("S1", "S2", "S3", "S4", "S5", "S6"):
            v = money(row[k])
            cells.append(f'<span class="best">{v}</span>' if row["best"] == k else v)
        cells.append(f"<strong>{esc(row['best'])}</strong>")
        sens_rows.append(cells)
    tally = ", ".join(f"{k}: {v}" for k, v in sorted(best_counts.items()))
    page("scenarios.html", "Scenarios and recommended plan", f"""
<h2>Six options, evaluated after tax</h2>
<p>All options start at the date of death (base case 2045) and are measured at 2055. Properties kept are valued at a hypothetical 2055 sale net of selling costs, capital-gains tax (37.1% combined on gains above the stepped-up basis; $250,000 §121 exclusion for the heir's home) and depreciation recapture (41.1%). Net cash flows are swept into (or drawn from) an investment account earning 7% nominal, taxed 30% on gains at the end. Income tax on net rents: 37.1%. Rent-controlled units grow 1.6%/yr, market rents 3%/yr, 5% vacancy, 6% management.</p>
{table(["#", "Scenario", "Description", "A assessed (yr 1)", "B assessed (yr 1)", "A property tax (yr 1)", "B property tax (yr 1)", "Net cash flow (yr 1)", "Housing value consumed (yr 1)", "Cumulative net cash 10 yrs", "Investment account 2055 (after tax)", "Properties 2055 (after tax)", "Total after-tax wealth 2055", "In 2026 dollars"], sc_rows, "num")}
<div class="callout ok"><strong>Recommended plan:</strong> {esc(ranked[0]['key'])} — {esc(ranked[0]['name'])}; see the reasoning on the <a href="executive-summary.html#5-recommendation-and-reasoning">Executive summary</a>. Across the 27 sensitivity cases below the best option is: {tally}. S1 (keep both, live in A) wins only with high appreciation and low returns; S5 never wins.</div>
<h2>Sensitivity: inheritance year × appreciation × investment return (after-tax wealth 10 years after inheritance)</h2>
{table(["Death year", "Appreciation case", "Portfolio return", "S1", "S2", "S3", "S4", "S5", "S6", "Best"], sens_rows, "num")}
<h2>Qualitative factors not in the numbers</h2>
<ul>
<li><strong>Housing quality:</strong> S1/S2 give the Heir a large Cupertino house (market rent about {money(s1['year1_housing_value_consumed'])}/yr in 2045); S3/S4 a 2-bedroom flat; S5/S6 a rental chosen by the Heir ($4,500/month in 2026 dollars assumed).</li>
<li><strong>Concentration risk:</strong> keeping both properties leaves roughly $10 million in two Bay Area parcels; selling diversifies. FHFA shows both metros flat-to-down over the year to 2026Q2 and well below national appreciation over five years.</li>
<li><strong>Landlord obligations:</strong> San Francisco rent control, just-cause eviction, relocation payments and (if revived) the Empty Homes Tax add cost and friction to S1/S3/S4/S5. Professional management (6%) is assumed.</li>
<li><strong>Liquidity and simplicity:</strong> S6 is the simplest and most liquid; S4 keeps one building to manage.</li>
<li><strong>Legal risk:</strong> Prop 19 could be loosened (initiatives have failed so far) or the federal exclusion lowered by a future Congress — neither changes the ranking much because the drivers are carrying cost vs. investment return.</li>
</ul>
<h2>Year-by-year detail per scenario</h2>
{yearly_blocks}
""", "Live in it, rent it, or sell and reinvest — compared after tax with the same yardstick.")

    # ---------------------------------------------------- pending legislation
    prow = [[esc(r["level"]), esc(r["measure"]), badge(r["status"]), esc(r["as_of"]), esc(r["effect_on_plan"]), link(r["source_url"], r["source_title"]), esc(r["notes"])] for r in pend]
    page("pending-legislation.html", "Enacted and pending law changes", table(["Level", "Measure", "Status", "As of", "Effect on the plan", "Source", "Notes"], prow) + """
<div class="callout warn">November 3 2026 results are unofficial until the Secretary of State certifies them (due Dec 11 2026). Nothing currently pending would restore the pre-2021 unlimited parent–child exclusion or create a California estate tax.</div>
""", "What has changed recently and what could change, at each level of government.")

    # ---------------------------------------------------------------- flagged
    frow = [[esc(r["id"]), badge(r["category"]), f"<strong>{esc(r['item'])}</strong>", esc(r["why_flagged"]), esc(r["impact"]), esc(r["what_would_resolve_it"]), link(r["source_url"], "source") if r["source_url"] else "—"] for r in flagged]
    page("flagged.html", "Flagged for Review", f"""
<div class="callout bad"><strong>{len(flagged)} items</strong> could not be verified from an official source, were derived or assumed, are ambiguous, or look irregular. They are published here rather than silently filled in. None of them blocks the analysis, but items marked <em>high impact</em> should be resolved before acting.</div>
{table(["ID", "Type", "Item", "Why flagged", "Impact", "What would resolve it", "Link"], frow)}
""", "Everything unverified, derived, ambiguous or irregular — in one place.")

    # ---------------------------------------------------------------- sources
    srcs = {}
    for r in fed + ca + loc + econ + pend:
        u = r.get("source_url")
        if u:
            srcs.setdefault(u, r.get("source_title") or u)
    for r in ops + flagged:
        u = r.get("source_url")
        if u and u not in srcs:
            srcs[u] = r.get("source_title") or r.get("item") or u
    groups = {"Federal (IRS / U.S. Code / Treasury / BLS / HUD / FHFA)": [], "California (BOE / FTB / SCO / Legislature / SOS / CDI)": [], "Santa Clara County / Cupertino": [], "San Francisco": [], "Other": []}
    for u, t in sorted(srcs.items(), key=lambda kv: kv[1].lower()):
        if any(d in u for d in ("irs.gov", "govinfo.gov", "treasury.gov", "bls.gov", "huduser.gov", "fhfa.gov")):
            g = "Federal (IRS / U.S. Code / Treasury / BLS / HUD / FHFA)"
        elif any(d in u for d in ("boe.ca.gov", "ftb.ca.gov", "sco.ca.gov", "leginfo", "sos.ca.gov", "insurance.ca.gov")):
            g = "California (BOE / FTB / SCO / Legislature / SOS / CDI)"
        elif "santaclaracounty" in u:
            g = "Santa Clara County / Cupertino"
        elif any(d in u for d in ("sf.gov", "sftreasurer", "sfpuc")):
            g = "San Francisco"
        else:
            g = "Other"
        groups[g].append([link(u, t), f'<span class="small">{esc(u)}</span>', badge("verified") if "github.com" not in u else badge("repo")])
    src_html = "".join(f"<h2>{esc(g)}</h2>" + table(["Source", "URL", "Read on " + BUILD_DATE], rows) for g, rows in groups.items() if rows)
    page("sources.html", "Sources", src_html + """
<p class="small">All pages were retrieved and read on the build date. Items the tools could not read (interactive premium-comparison tool; pages of the Santa Clara rate book beyond page 30) are recorded on the Flagged page rather than cited as verified. Third-party news sites were used only to locate official pages, never as the source of a figure.</p>
""", "Official sources only, each read on the build date.")

    # ------------------------------------------------------------ methodology
    prow2 = []
    labels = {
        "inherit_year": ("Base-case inheritance year", "assumption"), "hold_years": ("Evaluation horizon after inheritance (years)", "assumption"),
        "av_growth": ("Assessed-value growth (Prop 13 max)", "verified"), "rate_a": ("Cupertino ad valorem rate", "derived"), "rate_b": ("San Francisco rate FY2026-27", "verified"),
        "hox": ("Homeowners' Exemption", "verified"), "prop19_cap_2025": ("Prop 19 cap 2025–27", "verified"), "prop19_cap_growth": ("Prop 19 cap growth", "assumption"),
        "estate_exclusion_2026": ("Federal exclusion 2026", "verified"), "estate_rate": ("Federal estate tax rate", "verified"), "sec121_exclusion": ("§121 exclusion (single)", "verified"),
        "transfer_tax_sf": ("SF transfer tax ($1M–<$5M)", "verified"), "transfer_tax_scc": ("Santa Clara County transfer tax", "verified"),
        "ltcg_combined": ("Combined tax on long-term gains", "assumption"), "recapture_combined": ("Combined tax on depreciation recapture", "assumption"), "ordinary_combined": ("Combined tax on net rent", "assumption"),
        "portfolio_liquidation_tax": ("Tax on portfolio gains at horizon", "assumption"), "building_share": ("Depreciable building share", "assumption"), "depreciation_years": ("Depreciation period (years)", "unverified"),
        "cpi": ("CPI", "assumption"), "appreciation_a": ("Appreciation A", "assumption"), "appreciation_b": ("Appreciation B", "assumption"), "market_rent_growth": ("Market rent growth", "assumption"),
        "controlled_rent_growth": ("Rent-controlled increase", "verified"), "utility_growth": ("Utility cost growth", "assumption"), "insurance_growth": ("Insurance growth", "assumption"),
        "exclusion_index": ("Estate exclusion indexation", "assumption"), "portfolio_return": ("Portfolio return", "assumption"), "safe_return": ("Safe return (10-yr Treasury ≈ 4.9%)", "assumption"),
        "value_a_2026": ("Value A 2026", "user-supplied"), "value_b_2026": ("Value B 2026", "user-supplied"), "av_a_2025": ("Assessed value A 2025", "user-supplied"), "fixed_a_2025": ("Direct charges A 2025", "derived"),
        "fixed_b_2026": ("Direct charges B", "assumption"), "water_a": ("Water A (per year)", "user-supplied"), "elec_a": ("Electricity A (per year)", "user-supplied"), "ins_a": ("Insurance A", "user-supplied"), "maint_a": ("Maintenance A", "assumption"),
        "water_b": ("Water B (per year)", "user-supplied"), "elec_b": ("Electricity B (per year)", "user-supplied"), "ins_b": ("Insurance B", "user-supplied"), "maint_b": ("Maintenance B", "assumption"),
        "rent_b_2units": ("Rent, two B units (per year)", "user-supplied"), "rent_b_unit3_market": ("Market rent, third B unit (per year)", "derived"), "rent_a_market": ("Market rent A (per year, HUD SAFMR)", "verified"),
        "alt_housing_rent": ("Heir's rent if living elsewhere (per year)", "assumption"), "mgmt_fee": ("Management fee", "assumption"), "vacancy": ("Vacancy allowance", "assumption"), "selling_cost": ("Selling costs", "assumption"),
    }
    for k, (lab, st) in labels.items():
        v = P[k]
        if isinstance(v, float) and v < 1 and k not in ("elec_a",):
            vs = f"{v*100:.4g}%"
        elif isinstance(v, (int, float)) and abs(v) >= 1000:
            vs = money(v)
        else:
            vs = esc(v)
        prow2.append([f"<code>{k}</code>", lab, vs, badge(st)])
    page("methodology.html", "Methodology, parameters and privacy", f"""
<h2>How the numbers are produced</h2>
<ol>
<li><code>data/*.csv</code> hold every verified fact with its official URL and a status.</li>
<li><code>analysis/model.py</code> projects values, assessed values, taxes and costs year by year (2026–2060), runs the six scenarios and the 27-case sensitivity grid, and writes <code>data/projections/*.csv</code>, <code>data/scenarios.csv</code> and <code>docs/data/model_output.json</code>.</li>
<li><code>analysis/build_site.py</code> renders this site from those files. Re-run both scripts after changing any parameter.</li>
</ol>
<h2>Core formulas</h2>
<ul>
<li>Assessed value (no change in ownership): AV<sub>t</sub> = AV<sub>t−1</sub> × 1.02 (Cal. Const. art. XIII A §2(b) maximum).</li>
<li>Prop 19 at death: excluded amount = FBYV + cap; new taxable value = FBYV if FMV ≤ excluded amount, else FBYV + (FMV − excluded amount); without the exclusion, new taxable value = FMV.</li>
<li>Property tax = (AV − $7,000 if owner-occupied) × rate + direct charges (grown 2%/yr).</li>
<li>Net rent = gross rent × (1 − vacancy − management); income tax = max(net rent − costs − depreciation, 0) × 37.1%.</li>
<li>Sale proceeds = price − 5% selling costs − transfer tax − 37.1% × (gain − §121 exclusion if applicable) − 41.1% × accumulated depreciation; basis = value at death (§1014).</li>
<li>Investment account: balance<sub>t</sub> = balance<sub>t−1</sub> × (1 + r) + net cash<sub>t</sub>; at the horizon, gains above contributions are taxed at 30%.</li>
<li>Estate tax = 40% × max(gross estate − exclusion × (2 if portability), 0); exclusion = $15,000,000 × 1.025<sup>(year − 2026)</sup>.</li>
</ul>
<h2>Parameters</h2>
{table(["Parameter", "Meaning", "Value", "Status"], prow2)}
<h2>Economic anchors</h2>
{table(["Indicator", "Value", "Unit", "As of", "Status", "Source", "Use in model"], [[esc(r['indicator']), esc(r['value']), esc(r['unit']), esc(r['as_of']), badge(r['status']), link(r['source_url'], r['source_title']) if r['source_url'] else esc(r['source_title']), esc(r['use_in_model'])] for r in econ], "facts")}
<h2>Privacy rules applied</h2>
<ul>
<li>No names, street addresses, parcel numbers, account numbers or dates of birth anywhere in the repository or site.</li>
<li>Properties identified by ZIP code only; people as Transferor / Heir.</li>
<li>Owner-supplied year-by-year assessment histories are not published (they are searchable identifiers); only a rounded anchor and a ratio are kept.</li>
<li>All amounts rounded to the nearest $10.</li>
</ul>
<h2>Limitations</h2>
<ul>
<li>Deterministic model: no probability distributions; see the sensitivity grid for ranges.</li>
<li>Heir's personal tax situation, filing status, other income and residence are assumed (high-income single California resident).</li>
<li>Rent-control status of Property B and the Transferor's principal residence are assumed (flagged).</li>
<li>Not legal, tax or investment advice.</li>
</ul>
""", "Transparent inputs, formulas and rules so every number can be reproduced.")

    print("Built", len(NAV), "pages into", DOCS)


if __name__ == "__main__":
    main()
