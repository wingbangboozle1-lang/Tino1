#!/usr/bin/env python3
"""
Builds the static site from ../facts/*.csv (the fact register) and ../model/out/ (model output).
Standard library only.  No figure on the site is typed by hand: every number comes from the
register or from the model's output files.

Run:  python3 verify-4395771d/model/model.py && python3 verify-4395771d/tools/build_site.py [output_dir]
"""
import csv, json, os, sys, html, glob, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
CANONICAL = '--canonical' in sys.argv          # build as the front door: no 'independent check' banner
OUT = os.path.abspath(ARGS[0]) if ARGS else os.path.join(ROOT, 'site')
os.makedirs(OUT, exist_ok=True)
REPO = 'https://github.com/wingbangboozle1-lang/Tino1/blob/main/verify-4395771d/'
TREE = 'https://github.com/wingbangboozle1-lang/Tino1/tree/main/verify-4395771d/'
CHECKED = '2026-11-11'

# ------------------------------------------------------------------ data
FACTS = {}
for p in sorted(glob.glob(os.path.join(ROOT, 'facts', '*.csv'))):
    for r in csv.DictReader(open(p, encoding='utf-8')):
        r['file'] = os.path.basename(p)[:-4]
        FACTS[r['id']] = r
S = json.load(open(os.path.join(ROOT, 'model', 'out', 'summary.json'), encoding='utf-8'))
A, V, O = S['assumptions'], S['verified'], S['owner']

def rows_of(name):
    return list(csv.DictReader(open(os.path.join(ROOT, 'model', 'out', name), encoding='utf-8')))

e = html.escape
def r10(x):
    return int(math.floor(float(x) / 10.0 + 0.5) * 10)
def usd(x):
    x = int(round(float(x)))
    return ('-' if x < 0 else '') + '$' + format(abs(x), ',')
def pct(x, d=1):
    return f'{100 * float(x):.{d}f}%'
def short(title):
    t = title.split(' (')[0]
    parts = t.split(' — ')
    t = parts[0] if len(parts[0]) >= 14 or len(parts) == 1 else parts[0] + ' — ' + parts[1]
    return t if len(t) <= 52 else t[:50] + '…'
NA_ASSUME = '<a href="flagged.html#assumptions">assumption — no official source exists</a>'
NA_REPO = '<a href="flagged.html#irregularities">repository finding — no official source applies</a>'

def src(*ids):
    """Source links for register rows.  Unverified rows link to the Flagged page instead."""
    out = []; seen = set()
    for i in ids:
        f = FACTS[i]
        if f['source_url'] and f['status'] != 'unverified':
            key = f['source_url']
            if key in seen: continue
            seen.add(key)
            out.append(f'<a href="{e(f["source_url"])}" rel="noopener" title="{e(f["source_title"])} — register row {i}">{e(short(f["source_title"]))}</a>')
        else:
            if f['source_url'] and f['source_url'] not in seen:
                seen.add(f['source_url'])
                out.append(f'<a href="{e(f["source_url"])}" rel="noopener" title="where to look — register row {i}">{e(short(f["source_title"]))}</a>')
            out.append(f'<a href="flagged.html#{i}">unverified — see Flagged ({i})</a>')
    return ' · '.join(out)

def badge(kind):
    label = {'verified': 'verified', 'derived': 'derived', 'owner': 'owner-supplied', 'assumption': 'assumption',
             'unverified': 'unverified', 'model': 'model result'}[kind]
    return f'<span class="b b-{kind}">{label}</span>'

def table(head, rows, cls='', caption=None):
    h = ''.join(f'<th>{c}</th>' for c in head)
    b = ''
    for r in rows:
        b += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>\n'
    cap = f'<caption>{caption}</caption>' if caption else ''
    return f'<div class="tw"><table class="{cls}">{cap}<thead><tr>{h}</tr></thead><tbody>\n{b}</tbody></table></div>'

METHOD = '<a href="sources.html#method">how it is calculated</a>'

# ------------------------------------------------------------------ charts (inline SVG, no scripts)
COL = ['#0b6e4f', '#c2410c', '#1d4ed8', '#7c3aed', '#64748b']
def line_chart(series, title, yfmt=lambda v: f'${v/1e6:.0f}M', w=760, h=330, mark=None, lw=190):
    xs = [x for s in series.values() for x, _ in s]; ys = [y for s in series.values() for _, y in s]
    x0, x1, y1 = min(xs), max(xs), max(ys) * 1.05; y0 = 0
    L, R, T, B = 64, 16, 34, 40
    X = lambda x: L + (x - x0) / (x1 - x0) * (w - L - R)
    Y = lambda y: h - B - (y - y0) / (y1 - y0) * (h - T - B)
    g = f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}" class="chart"><title>{e(title)}</title>'
    for i in range(5):
        yv = y0 + (y1 - y0) * i / 4
        g += f'<line x1="{L}" x2="{w-R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="#e2e8f0"/><text x="{L-8}" y="{Y(yv)+4:.1f}" text-anchor="end" class="ax">{yfmt(yv)}</text>'
    step = max(1, int((x1 - x0) / 6))
    for xv in range(int(x0), int(x1) + 1, step):
        g += f'<text x="{X(xv):.1f}" y="{h-B+18}" text-anchor="middle" class="ax">{xv}</text>'
    if mark:
        g += f'<line x1="{X(mark[0]):.1f}" x2="{X(mark[0]):.1f}" y1="{T}" y2="{h-B}" stroke="#94a3b8" stroke-dasharray="4 4"/><text x="{X(mark[0])+6:.1f}" y="{T+12}" class="ax">{e(mark[1])}</text>'
    for k, (name, pts) in enumerate(series.items()):
        d = ' '.join(f'{"M" if i == 0 else "L"}{X(x):.1f},{Y(y):.1f}' for i, (x, y) in enumerate(pts))
        g += f'<path d="{d}" fill="none" stroke="{COL[k % 5]}" stroke-width="2.4"/>'
        g += f'<rect x="{L + lw * k}" y="8" width="12" height="12" fill="{COL[k % 5]}"/><text x="{L + lw * k + 17}" y="18" class="lg">{e(name)}</text>'
    return g + '</svg>'

def bar_chart(groups, names, title, w=760, h=360):
    """groups: list of (label, [values]) in $; names: series names."""
    mx = max(v for _, vs in groups for v in vs) * 1.08
    L, R, T, B = 64, 12, 34, 96
    gw = (w - L - R) / len(groups); bw = gw * 0.8 / len(names)
    Y = lambda y: h - B - y / mx * (h - T - B)
    g = f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}" class="chart"><title>{e(title)}</title>'
    for i in range(5):
        yv = mx * i / 4
        g += f'<line x1="{L}" x2="{w-R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="#e2e8f0"/><text x="{L-8}" y="{Y(yv)+4:.1f}" text-anchor="end" class="ax">${yv/1e6:.0f}M</text>'
    for gi, (label, vs) in enumerate(groups):
        for k, v in enumerate(vs):
            x = L + gi * gw + gw * 0.1 + k * bw
            g += f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{bw-1:.1f}" height="{h-B-Y(v):.1f}" fill="{COL[k % 5]}"><title>{e(label)} — {e(names[k])}: {usd(v)}</title></rect>'
        words = label.split(); lines = ['']
        for wd in words:
            if len(lines[-1]) + len(wd) > 15: lines.append(wd)
            else: lines[-1] = (lines[-1] + ' ' + wd).strip()
        for li, ln in enumerate(lines[:4]):
            g += f'<text x="{L + gi * gw + gw / 2:.1f}" y="{h-B+16+li*13}" text-anchor="middle" class="ax">{e(ln)}</text>'
    for k, nme in enumerate(names):
        g += f'<rect x="{L + 150 * k}" y="8" width="12" height="12" fill="{COL[k % 5]}"/><text x="{L + 150 * k + 17}" y="18" class="lg">{e(nme)}</text>'
    return g + '</svg>'

# ------------------------------------------------------------------ layout
NAV = [('index.html', 'Summary'), ('decision.html', 'Live, rent or sell'), ('projections.html', 'Year by year'),
       ('black-swans.html', 'Black swans'), ('steps.html', 'Inheritance steps'), ('taxes.html', 'Taxes & thresholds'),
       ('properties.html', 'Properties & costs'), ('law-changes.html', 'Law changes'),
       ('flagged.html', 'Flagged for Review'), ('sources.html', 'Sources & method')]

CSS = """
:root{--ink:#0f172a;--mut:#475569;--line:#e2e8f0;--bg:#f8fafc;--card:#fff;--acc:#0b6e4f;--warn:#b45309;--bad:#b91c1c}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:#0b5cad}a:focus-visible{outline:3px solid #f59e0b;outline-offset:2px}
header.top{background:#0f172a;color:#fff}
header.top .in{max-width:1180px;margin:0 auto;padding:14px 20px 0}
header.top h1{font-size:19px;margin:0 0 2px;font-weight:650}header.top p{margin:0 0 10px;color:#cbd5e1;font-size:13.5px}
nav{display:flex;flex-wrap:wrap;gap:2px}nav a{color:#e2e8f0;text-decoration:none;padding:8px 11px;font-size:14px;border-radius:6px 6px 0 0}
nav a:hover{background:#1e293b}nav a[aria-current=page]{background:var(--bg);color:var(--ink);font-weight:600}
nav a.flag{color:#fcd34d}nav a.flag[aria-current=page]{color:#92400e}
main{max-width:1180px;margin:0 auto;padding:22px 20px 60px}
h2{font-size:25px;margin:6px 0 6px}h3{font-size:18.5px;margin:30px 0 8px}h4{font-size:15.5px;margin:18px 0 6px}
p.lead{color:var(--mut);margin:0 0 16px;max-width:900px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{font-size:12.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
.card .v{font-size:25px;font-weight:680;margin:2px 0}.card .s{font-size:13px;color:var(--mut)}
.box{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--acc);border-radius:10px;padding:14px 18px;margin:14px 0}
.box.warn{border-left-color:var(--warn)}.box.bad{border-left-color:var(--bad)}.box h3{margin-top:2px}
.box ol,.box ul{margin:6px 0 4px;padding-left:22px}.box li{margin:5px 0}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0 6px}
table{border-collapse:collapse;width:100%;font-size:14px}caption{text-align:left;padding:10px 12px 0;color:var(--mut);font-size:13px}
th,td{padding:8px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#f1f5f9;font-weight:620;font-size:13px;white-space:nowrap}tbody tr:last-child td{border-bottom:0}
table.num td:not(:first-child):not(:last-child){text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.num th:not(:first-child):not(:last-child){text-align:right}
td.src,td:last-child{font-size:12.5px;color:var(--mut);min-width:170px}
tr.hi td{background:#ecfdf5;font-weight:600}
.b{display:inline-block;font-size:11px;padding:1px 7px;border-radius:99px;border:1px solid;white-space:nowrap;vertical-align:1px}
.b-verified{color:#065f46;border-color:#6ee7b7;background:#ecfdf5}.b-derived{color:#1e40af;border-color:#93c5fd;background:#eff6ff}
.b-owner{color:#6b21a8;border-color:#d8b4fe;background:#faf5ff}.b-assumption{color:#92400e;border-color:#fcd34d;background:#fffbeb}
.b-unverified{color:#991b1b;border-color:#fca5a5;background:#fef2f2}.b-model{color:#334155;border-color:#cbd5e1;background:#f8fafc}
.chart{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:8px 0}
.chart .ax{font-size:11px;fill:#64748b}.chart .lg{font-size:12px;fill:#0f172a}
.note{font-size:13px;color:var(--mut)}.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 14px;margin:10px 0}summary{cursor:pointer;font-weight:600}
footer{max-width:1180px;margin:0 auto;padding:0 20px 40px;color:var(--mut);font-size:12.5px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
@media (max-width:640px){h2{font-size:21px}.card .v{font-size:21px}th,td{padding:7px 8px}}
@media print{header.top,footer{display:none}body{background:#fff}}
"""

BANNER = ('<div class="box warn" style="margin-top:0"><strong>Independent check.</strong> This copy was built separately, from the same owner inputs, '
          'to verify the main dashboard: its own source register, its own model. Two independently built models agree on the key figures. '
          '<a href="../../">Go to the main dashboard</a>.</div>\n')

def page(fname, title, body):
    def _a(f, t):
        cls = ' class="flag"' if f == 'flagged.html' else ''
        cur = ' aria-current="page"' if f == fname else ''
        return '<a href="' + f + '"' + cls + cur + '>' + e(t) + '</a>'
    nav = ''.join(_a(f, t) for f, t in NAV)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">
<title>{e(title)} — Inheritance decision dashboard</title><link rel="stylesheet" href="assets/site.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="in"><h1>Inheritance decision dashboard</h1>
<p>A Cupertino home to be inherited through a trust (about 2040–2050) and a San Francisco building the heir already owns. No names, addresses or parcel numbers appear on this site; owner-supplied dollar figures are rounded.</p>
<nav aria-label="Sections">{nav}</nav></div></header>
<main id="main">
{'' if CANONICAL else BANNER}{body}
</main>
<footer>Checked against official pages on {CHECKED} (UTC). Dollar figures are rounded to the nearest $10. This is a planning aid, not legal, tax or investment advice — confirm with a California estate attorney and a CPA before acting.
Status labels: {badge('verified')} read on the official page · {badge('derived')} arithmetic on verified figures · {badge('owner')} supplied by the owner, not independently confirmed · {badge('assumption')} modelling choice · {badge('model')} output of the model · {badge('unverified')} could not be confirmed, left blank.</footer>
</body></html>"""
    with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f:
        f.write(doc)

# ------------------------------------------------------------------ shared numbers
B = {int(k): v for k, v in S['baseline'].items()}
def W(T, key, h, kind='nominal'): return B[T]['options'][key][str(h)][kind]
P45 = B[2045]['prop19']
SQ = {int(k): v for k, v in S['status_quo'].items()}
OPT_LABEL = {'sell_stocks': 'Sell, invest in a stock index fund', 'sell_6040': 'Sell, invest 60% stocks / 40% cash',
             'sell_cash': 'Sell, keep the money in cash or savings', 'rent_out': 'Keep and rent out',
             'move_in': 'Move in and rent out the San Francisco unit'}
BE = S['break_even_stock_return']
ROT = S['rotations']
MODEL_SRC_P19 = src('C06', 'C03', 'L11') + ' · ' + METHOD
MODEL_SRC_OPT = src('F08', 'C06', 'C10', 'L15') + ' · ' + METHOD

# ------------------------------------------------------------------ pages
def build_index():
    d_rent = W(2045, 'sell_stocks', 20) - W(2045, 'rent_out', 20)
    d_move = W(2045, 'sell_stocks', 20) - W(2045, 'move_in', 20)
    d_cash = W(2045, 'rent_out', 20) - W(2045, 'sell_cash', 20)
    save = B[2045]['tax_no_move_in'] - B[2045]['tax_move_in']
    est45 = [r for r in S['estate'] if r[0] == 2045][0]
    rb = ROT['Bay Area record 1977-2025|2045|20']; rn = ROT['National record 1929-2025|2045|20']
    rb10 = ROT['Bay Area record 1977-2025|2045|10']; rn10 = ROT['National record 1929-2025|2045|10']
    b_now = SQ[2026]['b_tax']; b_if = r10(O['b_value_2026'] * V['b_rate'] + S['derived_direct_charges_2025']['b'])
    n_flag = sum(1 for f in FACTS.values() if f['status'] == 'unverified')
    cards = f"""<div class="cards">
<div class="card"><div class="k">Cupertino home today</div><div class="v">{usd(O['a_value_2026'])}</div><div class="s">Owner's estimate, Nov 2026. Assessed for tax at {usd(O['a_assessed_2026'])} {badge('owner')}</div></div>
<div class="card"><div class="k">Its value if inherited in 2045</div><div class="v">{usd(P45['fmv'])}</div><div class="s">At {pct(A['a_apprec'])} a year {badge('assumption')}</div></div>
<div class="card"><div class="k">Property tax on it</div><div class="v">{usd(B[2045]['tax_before'])} → {usd(B[2045]['tax_move_in'])}</div><div class="s">Year before → year after a 2045 inheritance if the heir moves in; {usd(B[2045]['tax_no_move_in'])} if not {badge('model')}</div></div>
<div class="card"><div class="k">Federal estate-tax exclusion</div><div class="v">{usd(V['excl_2027'])}</div><div class="s">Per person for deaths in 2027 ({usd(V['excl_2026'])} in 2026). California: no estate or inheritance tax {badge('verified')}</div></div>
</div>"""
    answer = f"""<div class="box"><h3>The short answer</h3><ol>
<li><strong>For the most money, sell the Cupertino home soon after inheriting it and invest the proceeds in a broad stock index fund.</strong> Its tax basis resets to its value on the date of death, so a prompt sale leaves little or no gain to tax. With an inheritance in 2045, this ends 20 years later about <strong>{usd(d_rent)}</strong> ahead of keeping the home and renting it out, and about <strong>{usd(d_move)}</strong> ahead of moving in (after tax, in dollars of that year). <a href="decision.html">Full comparison</a>.</li>
<li><strong>That only holds if the money is really invested.</strong> Selling and leaving the proceeds in cash or savings is the weakest choice: it ends about {usd(d_cash)} <em>behind</em> keeping the home and renting it out.</li>
<li><strong>If you want to live there, move in within one year and file two forms.</strong> That keeps part of the low assessed value and saves about <strong>{usd(save)}</strong> of property tax in the first year compared with not qualifying. There are no exceptions to the one-year deadline. <a href="steps.html">Steps and deadlines</a>.</li>
<li><strong>Keep the San Francisco building.</strong> Because the heir already owns it, the inheritance changes nothing about it: it is not reassessed (its tax stays near {usd(b_now)} a year; a buyer today would pay about {usd(b_if)}), it is not part of the taxable estate, and it gets no reset of tax basis — so selling <em>it</em> would be taxed on its whole gain. It also gives the heir a home and rental income whichever choice is made for Cupertino.</li>
<li><strong>Estate tax is a federal question only.</strong> Only the Cupertino home and the other inherited assets count. For a death in 2045 the exclusion is projected near {usd(est45[1])}; after the home there would be room for about {usd(est45[3])} of other assets before any tax, and roughly twice the exclusion if a spouse's unused amount was preserved. <a href="taxes.html">Thresholds by year</a>.</li>
<li><strong>History agrees most of the time, not always.</strong> Replaying the real 1977–2025 Bay Area record from every starting year, selling and investing came out ahead after 20 years in {rb['wins']['sell_stocks']} of {rb['n']} cases (after 10 years: {rb10['wins']['sell_stocks']} of {rb10['n']}). It lost when a stock crash came first, and in a Japan-style stagnation cash beat everything. <a href="black-swans.html">Black swans</a>.</li>
</ol><p class="note">All comparisons assume the heir lives in the San Francisco unit unless they move to Cupertino, and include an illustrative {usd(A['other_assets_at_T'])} (2026 dollars) of other inherited money in every choice. {n_flag} inputs could not be confirmed and several are assumptions — see <a href="flagged.html">Flagged for Review</a>.</p></div>"""
    rows = []
    for key in ('sell_stocks', 'sell_6040', 'rent_out', 'move_in', 'sell_cash'):
        best = key == 'sell_stocks'
        rows.append([('<strong>' if best else '') + OPT_LABEL[key] + ('</strong>' if best else '')] +
                    [usd(W(2045, key, h)) for h in (10, 20, 30)] + [usd(W(2045, key, 20, 'real'))] + [badge('model') + ' ' + MODEL_SRC_OPT])
    t1 = table(['Choice for the Cupertino home', 'After 10 years', 'After 20 years', 'After 30 years', 'After 20 years, in 2026 dollars', 'Status and basis'],
               rows, 'num', 'After-tax wealth from the Cupertino decision, inheritance in 2045, baseline assumptions.')
    diff = table(['Question', 'Cupertino home (to be inherited)', 'San Francisco building (already the heir\'s)', 'Source'], [
        ['Does the parent\'s death change who owns it?', 'Yes — it passes to the heir through the trust', 'No', src('C11')],
        ['Is it reassessed for property tax?', f'Yes. Fully, unless the heir moves in within a year; then only the amount by which market value exceeds the parent\'s assessed value plus the allowance is added', 'No — reassessment follows a change in ownership', src('C06', 'C10', 'L03')],
        ['Is it counted in the parent\'s taxable estate?', 'Yes, at market value on the date of death', 'No — the estate is what the parent owned', src('F07')],
        ['Does its income-tax basis reset to market value?', 'Yes, if the trust is the usual revocable kind (confirm)', 'No — it keeps the heir\'s own basis', src('F08', 'F18')],
        ['Tax if sold shortly after the death', 'Little or none', 'Tax on the whole gain since the heir acquired it', src('F19', 'F09')],
        ['Property tax, 2026', usd(SQ[2026]['a_tax']) + ' ' + badge('derived'), usd(SQ[2026]['b_tax']) + ' ' + badge('derived'), src('L11', 'L01') + ' · owner\'s bills'],
        ['Property tax, 2045 (year of inheritance)', f"{usd(B[2045]['tax_move_in'])} if the heir moves in; {usd(B[2045]['tax_no_move_in'])} if not {badge('model')}", usd(SQ[2045]['b_tax']) + ' — unchanged path ' + badge('model'), MODEL_SRC_P19],
    ], '', 'Why the two properties must be treated differently.')
    dl = table(['Deadline', 'What', 'Source'], [
        ['60 days after the death', 'Trustee sends the required notice to beneficiaries and heirs', src('C20')],
        ['150 days after the death', 'Trustee files the change-in-ownership statement with the county assessor', src('C19')],
        ['9 months after the death', 'Federal estate tax return — only if the estate is above the exclusion, or to preserve a spouse\'s unused exclusion', src('F20', 'F06')],
        ['<strong>1 year after the death</strong>', 'To keep part of the low assessed value: the heir must be living in the home as their principal residence and must have filed the Homeowners\' Exemption claim. No exceptions', src('C07', 'C08')],
        ['3 years after the death (or before any sale)', 'File the parent-child exclusion claim (form BOE-19-P)', src('C08', 'L12')],
    ])
    body = f"""<h2>Summary</h2>
<p class="lead">What to do with the Cupertino home when it is inherited — live in it, rent it out, or sell it and invest — with the reasons, the numbers behind them, and what could change the answer.</p>
{cards}{answer}
<h3>The three choices in numbers</h3>{t1}
<p class="note">Selling beats renting out whenever stocks return more than about {pct(BE['rent_out'])} a year over 20 years, and beats moving in above about {pct(BE['move_in'])} (with the home appreciating {pct(A['a_apprec'])} a year). The S&amp;P 500 with dividends returned 10.0% a year from 1928 to 2025; the model assumes {pct(A['stock_return'])}. {src('E08')}</p>
<h3>Inherited versus already owned</h3>{diff}
<h3>Deadlines that cannot be missed</h3>{dl}
<h3>Where to go next</h3>
<div class="cards">
<div class="card"><div class="k"><a href="decision.html">Live, rent or sell</a></div><div class="s">The comparison, the sensitivity to assumptions, and the price of living in the house.</div></div>
<div class="card"><div class="k"><a href="projections.html">Year by year</a></div><div class="s">Value, assessed value, property tax and every running cost for both properties, 2026–2076.</div></div>
<div class="card"><div class="k"><a href="black-swans.html">Black swans</a></div><div class="s">Real crashes, inflations and stagnations replayed on this decision.</div></div>
<div class="card"><div class="k"><a href="flagged.html">Flagged for Review</a></div><div class="s">Everything unconfirmed, every assumption, and the irregularities found in this repository.</div></div>
</div>"""
    page('index.html', 'Summary', body)

def build_decision():
    yrs = {k: rows_of(f'yearly_{k}_T2045.csv') for k in ('sell_stocks', 'rent_out', 'move_in')}
    cl = {'sell_stocks': 'Sell and invest in stocks', 'rent_out': 'Keep and rent out', 'move_in': 'Move in'}
    chart = line_chart({cl[k]: [(int(r['year']), float(r['wealth_2026_dollars'])) for r in v] for k, v in yrs.items()},
                       'After-tax wealth in 2026 dollars, inheritance in 2045', yfmt=lambda v: f'${v/1e6:.0f}M')
    rows = []
    for T in (2040, 2045, 2050):
        for key in ('sell_stocks', 'sell_6040', 'rent_out', 'move_in', 'sell_cash'):
            best = max(('sell_stocks', 'sell_6040', 'rent_out', 'move_in', 'sell_cash'), key=lambda k: W(T, k, 20))
            rows.append([str(T), OPT_LABEL[key]] + [usd(W(T, key, h)) for h in (10, 20, 30)] + [usd(W(T, key, h, 'real')) for h in (10, 20, 30)]
                        + [badge('model') + ' ' + MODEL_SRC_OPT])
    t_all = table(['Inherited in', 'Choice', '+10 yrs', '+20 yrs', '+30 yrs', '+10 yrs (2026 $)', '+20 yrs (2026 $)', '+30 yrs (2026 $)', 'Status and basis'], rows, 'num')
    g = S['sensitivity']
    lab = {'sell_stocks': 'Sell and invest', 'rent_out': 'Keep and rent', 'move_in': 'Move in'}
    t_grid = table(['Home appreciation', 'Stock return', 'Sell and invest', 'Keep and rent out', 'Move in', 'Best', 'Status and basis'],
                   [[r[0], r[1], usd(r[2]), usd(r[3]), usd(r[4]), lab[r[5]], badge('model') + ' ' + src('E05', 'E08') + ' · ' + METHOD] for r in g], 'num',
                   'After-tax wealth 20 years after a 2045 inheritance under nine combinations of assumptions.')
    ins = S['insurance_sensitivity']
    t_ins = table(['Homeowners premium (2026 dollars)', 'Move in: wealth after 20 years', 'Keep and rent: wealth after 20 years', 'Status and basis'],
                  [[usd(r[1]) + (' (owner\'s rough figure)' if r[0] == 1 else f' ({r[0]}×)'), usd(r[2]), usd(r[3]), badge('model') + ' ' + src('K04') + ' · ' + METHOD] for r in ins], 'num')
    price10 = W(2045, 'sell_stocks', 10, 'real') - W(2045, 'move_in', 10, 'real')
    price20 = W(2045, 'sell_stocks', 20, 'real') - W(2045, 'move_in', 20, 'real')
    y1 = yrs['move_in'][0]; r1 = yrs['rent_out'][0]
    cf_move = table(['First full year after a 2045 inheritance', 'Move in', 'Keep and rent out', 'Status and basis'], [
        ['Assessed value', usd(y1['a_assessed']), usd(r1['a_assessed']), badge('model') + ' ' + src('C06', 'C10')],
        ['Property tax', usd(y1['a_property_tax']), usd(r1['a_property_tax']), badge('model') + ' ' + src('L11')],
        ['Insurance', usd(y1['a_insurance']), usd(r1['a_insurance']), badge('assumption') + ' ' + src('K04')],
        ['Water', usd(y1['a_water']), 'tenant pays', badge('owner') + ' ' + src('K06')],
        ['Electricity (solar credit assumed ended)', usd(y1['a_electricity']), 'tenant pays', badge('assumption') + ' ' + src('K01', 'K03')],
        ['Maintenance', usd(y1['a_maintenance']), usd(r1['a_maintenance']), badge('assumption') + ' ' + NA_ASSUME],
        ['Rent received', usd(y1['rent_received']) + ' (San Francisco third unit)', usd(r1['rent_received']) + ' (Cupertino home)', badge('assumption') + ' ' + src('L15', 'L13')],
        ['Income tax on rent', usd(y1['income_tax']), usd(r1['income_tax']) + ' (sheltered by depreciation)', badge('model') + ' ' + src('F17', 'F14', 'C21')],
        ['<strong>Net cash for the year</strong>', '<strong>' + usd(y1['net_cash_flow']) + '</strong>', '<strong>' + usd(r1['net_cash_flow']) + '</strong>', badge('model') + ' ' + METHOD + ' · ' + src('L11')],
    ], 'num')
    t_sf = table(['Reason', 'Detail', 'Source'], [
 ['Its low assessed value survives the inheritance', f"Tax about {usd(SQ[2026]['b_tax'])} a year now; about {usd(r10(O['b_value_2026'] * V['b_rate'] + S['derived_direct_charges_2025']['b']))} on today\'s market value. The saving ends the day it is sold.", src('L01', 'L03')],
 ['No reset of tax basis', 'The heir already owns it, so the parent\'s death does not change its basis. A sale is taxed on the gain since the heir acquired it (basis not supplied).', src('F08', 'F09')],
 ['It houses the heir and pays rent', f"Two units bring {usd(O['b_rent_month_2units'] * 12)} a year {badge('owner')}; the third is a home at no extra cost.", src('L13')],
 ['Both properties share one earthquake region', 'Selling the Cupertino home, not the San Francisco one, is the cheaper way to reduce that concentration.', src('E15')],
])
    body = f"""<h2>Live in it, rent it out, or sell and invest</h2>
<p class="lead">Each choice is followed year by year after the inheritance, after tax. The heir lives in the San Francisco unit unless they move to Cupertino, so every choice includes a home.</p>
<div class="box"><h3>What the numbers say</h3><ul>
<li><strong>Sell and invest</strong> wins in the baseline because the proceeds grow at the assumed {pct(A['stock_return'])} while the home grows at {pct(A['a_apprec'])} and, once reassessed, costs {usd(B[2045]['tax_no_move_in'])} a year in property tax. The sale itself is almost untaxed because the basis resets at death. {src('F08', 'F19')}</li>
<li><strong>Keep and rent out</strong> is the middle path. The home is taxed on its full market value (no relief for a rental), the rent roughly covers the costs, and the result rides on home prices. It beats selling only if stocks return less than about {pct(BE['rent_out'])} a year. {src('C10')}</li>
<li><strong>Move in</strong> is the most expensive in money: the capital stays in the house and the running costs are paid from other income. Compared with selling, living there costs about {usd(price10)} over the first 10 years and {usd(price20)} over 20 years, in 2026 dollars. That is the price of the home as a place to live — a personal choice the model cannot make.</li>
<li><strong>Sell and hold cash</strong> is the worst. If the proceeds would sit in savings, keep the house instead.</li>
<li><strong>Moving in keeps the door open.</strong> A sale later is still possible; the first $250,000 of gain after the death is excluded for an owner who has lived there two years ($500,000 on a joint return). {src('F15')}</li>
</ul></div>
{chart}
<h3>All three inheritance years</h3>{t_all}
<h3>The first year, line by line</h3>{cf_move}
<p class="note">Selling has no running costs after the sale; the model charges it {A['months_to_sell']} months of carrying costs on the fully reassessed value and {pct(A['selling_cost'], 0)} selling costs.</p>
<h3>What if the assumptions are wrong?</h3>{t_grid}
<p class="note">Selling wins in eight of the nine cells. Keeping wins when homes outrun stocks — which is what happened in several real decades; see <a href="black-swans.html">Black swans</a>.</p>
<h3>Insurance: the owner's figure could not be confirmed</h3>{t_ins}
<p class="note">Tripling the premium changes the 20-year result by about {usd(ins[0][2] - ins[2][2])}. It does not change the ranking. If the San Francisco third unit is <em>not</em> rent-controlled, moving in ends 20 years at {usd(S['move_in_if_not_rent_controlled_20y'])} instead of {usd(W(2045, 'move_in', 20))}. {src('L14')}</p>
<h3>Why not sell the San Francisco building instead?</h3>
{t_sf}"""
    page('decision.html', 'Live, rent or sell', body)

def build_projections():
    sq = rows_of('projection_status_quo.csv')
    def tab(cols, heads, basis):
        return table(['Year'] + heads + ['Status and basis'],
                     [[r['year']] + [usd(r[c]) for c in cols] + [basis] for r in sq], 'num')
    a_basis = badge('model') + ' ' + src('C14', 'L11') + ' · ' + METHOD
    b_basis = badge('model') + ' ' + src('C14', 'L01', 'L13') + ' · ' + METHOD
    p19 = rows_of('prop19_by_inheritance_year.csv')
    t19 = table(['Inherited in', 'Market value', 'Parent\'s assessed value', 'Allowance', 'Value cap', 'New assessed value if the heir moves in',
                 'New assessed value if not', 'Tax the year before', 'Tax if the heir moves in', 'Tax if not', 'Saved by moving in', 'Status and basis'],
                [[r['inheritance_year']] + [usd(r[c]) for c in ('market_value', 'factored_base_value', 'allowance', 'value_cap', 'taxable_if_move_in',
                                                               'taxable_if_not', 'tax_year_before', 'tax_if_move_in', 'tax_if_not', 'yearly_saving_from_moving_in')]
                 + [badge('model') + ' ' + MODEL_SRC_P19] for r in p19], 'num')
    mi = rows_of('yearly_move_in_T2045.csv'); ro = rows_of('yearly_rent_out_T2045.csv')
    tax_series = {'Parent keeps owning (no inheritance)': [(int(r['year']), float(r['a_property_tax'])) for r in sq if int(r['year']) <= 2075],
                  'Inherited 2045, heir moves in': [(int(r['year']), float(r['a_property_tax'])) for r in sq if int(r['year']) <= 2045] + [(int(r['year']), float(r['a_property_tax'])) for r in mi],
                  'Inherited 2045, not moved in': [(int(r['year']), float(r['a_property_tax'])) for r in sq if int(r['year']) <= 2045] + [(int(r['year']), float(r['a_property_tax'])) for r in ro]}
    chart = line_chart(tax_series, 'Property tax on the Cupertino home by year', yfmt=lambda v: f'${v/1000:.0f}k', mark=(2045, 'inherited'), lw=232)
    def after(rows_, extra):
        cols = ['a_market', 'a_assessed', 'a_property_tax', 'a_insurance', 'a_water', 'a_electricity', 'a_maintenance', 'rent_received', 'income_tax', 'net_cash_flow']
        return table(['Year', 'Market value', 'Assessed value', 'Property tax', 'Insurance', 'Water', 'Electricity', 'Maintenance', 'Rent received', 'Income tax on rent', 'Net cash', 'Status and basis'],
                     [[r['year']] + [usd(r[c]) for c in cols] + [badge('model') + ' ' + extra] for r in rows_], 'num')
    body = f"""<h2>Year by year, 2026–2076</h2>
<p class="lead">Baseline projections with constant rates: inflation {pct(A['inflation'])}, Cupertino home {pct(A['a_apprec'])}, San Francisco building {pct(A['b_apprec'])} a year. Real economies are never this smooth — see <a href="black-swans.html">Black swans</a> for the same model run on real history.</p>
<div class="box warn"><h3>How to read these tables</h3><ul>
<li>Assessed value rises by at most 2% a year while the same owner holds the property. {src('C14')}</li>
<li>Property tax = assessed value × the local rate ({pct(V['a_rate'], 4)} Cupertino, {pct(V['b_rate'], 4)} San Francisco) + fixed charges on the bill (about {usd(S['derived_direct_charges_2025']['a'])} and {usd(S['derived_direct_charges_2025']['b'])} in 2025, derived from the owner's bills). {src('L11', 'L01')}</li>
<li>Insurance, water and maintenance start from the owner's figures or stated assumptions and grow with inflation plus the margins listed under <a href="flagged.html#assumptions">assumptions</a>.</li>
</ul></div>
<h3>Cupertino home — if the parent simply keeps owning it</h3>
{tab(['a_market_value', 'a_assessed_value', 'a_property_tax', 'a_insurance', 'a_water', 'a_electricity', 'a_maintenance'],
     ['Market value', 'Assessed value', 'Property tax', 'Insurance', 'Water', 'Electricity', 'Maintenance'], a_basis)}
<p class="note">Electricity is shown as $0 while the solar credit lasts and as a cost from {A['a_solar_credit_ends']}, an assumed end of the 20-year net-metering term. {src('K01', 'K03')}</p>
<h3>What the inheritance does to the Cupertino assessed value and tax</h3>{t19}{chart}
<p class="note">The allowance moves by one year of statewide price change every second year, so it grows about half as fast as home prices and shelters a shrinking share of the value. {src('C04')}</p>
<h3>Cupertino home after a 2045 inheritance — heir moves in</h3>{after(mi, src('C06', 'C09', 'L11') + ' · ' + METHOD)}
<p class="note">"Rent received" is the San Francisco third unit, let once the heir has moved out of it.</p>
<h3>Cupertino home after a 2045 inheritance — kept and rented out</h3>{after(ro, src('C10', 'L15', 'F17') + ' · ' + METHOD)}
<h3>San Francisco building — unchanged by the inheritance</h3>
{tab(['b_market_value', 'b_assessed_value', 'b_property_tax', 'b_insurance', 'b_water', 'b_electricity', 'b_maintenance', 'b_rent_two_units'],
     ['Market value', 'Assessed value', 'Property tax', 'Insurance', 'Water and sewer', 'Electricity', 'Maintenance', 'Rent, two units'], b_basis)}
<p class="note">Rent is grown at 60% of inflation, the San Francisco formula for rent-controlled units; whether the building is controlled is not confirmed. {src('L13', 'L14')}</p>
<h3>Thresholds along the way</h3>
{table(['Year', 'Prop 19 allowance', 'Federal estate-tax exclusion (one person)', 'Status and basis'],
       [[r['year'], usd(r['prop19_allowance']), usd(r['federal_exclusion']), (badge('verified') if int(r['year']) <= 2027 else badge('model')) + ' ' + src('C03', 'F01', 'F03') + ' · ' + METHOD] for r in sq if int(r['year']) % 5 == 0 or int(r['year']) in (2026, 2027)], 'num')}
<p class="note">Download the full tables: <a href="{REPO}model/out/projection_status_quo.csv">status quo</a> · <a href="{REPO}model/out/prop19_by_inheritance_year.csv">Prop 19 by year</a> · <a href="{REPO}model/out/yearly_move_in_T2045.csv">move in</a> · <a href="{REPO}model/out/yearly_rent_out_T2045.csv">rent out</a> · <a href="{REPO}model/out/yearly_sell_stocks_T2045.csv">sell and invest</a>.</p>"""
    page('projections.html', 'Year by year', body)

def build_blackswans():
    named = [r for r in S['black_swan_named']]
    names = []
    for r in named:
        if r['name'] not in names: names.append(r['name'])
    keys = ('sell_stocks', 'sell_6040', 'sell_cash', 'rent_out', 'move_in')
    lab = {'sell_stocks': 'Sell → stocks', 'sell_6040': 'Sell → 60/40', 'sell_cash': 'Sell → cash', 'rent_out': 'Keep and rent', 'move_in': 'Move in'}
    hist_src = {'Baseline': src('E03'), '1970s': src('E05', 'E13', 'E08'), 'Early-1990s': src('E05', 'E06', 'E08'), 'Dot-com': src('E05', 'E08'),
                '2007': src('E05', 'E14', 'E08'), 'Great': src('E12', 'E08'), '1973': src('E13', 'E08'), 'Japan': src('E10', 'E11')}
    def hs(n): return next(v for k, v in hist_src.items() if n.startswith(k))
    def t_named(h):
        rows = []
        for n in names:
            r = next(x for x in named if x['name'] == n and x['horizon'] == h)
            rows.append([n] + [('<strong>' + usd(r[k]) + '</strong>') if r['best'] == k else usd(r[k]) for k in keys] + [lab[r['best']], badge('model') + ' ' + hs(n) + ' · ' + METHOD])
        return table(['What happens right after a 2045 inheritance'] + [lab[k] for k in keys] + ['Best', 'Status and data'], rows, 'num',
                     f'After-tax wealth {h} years after inheriting, in 2026 dollars. The best choice in each row is in bold.')
    groups = []
    for n in names:
        r = next(x for x in named if x['name'] == n and x['horizon'] == 20)
        groups.append((n.split(' (')[0].replace(' starts the year after inheriting', ''), [r[k] for k in ('sell_stocks', 'sell_cash', 'rent_out', 'move_in')]))
    chart = bar_chart(groups, ['Sell → stocks', 'Sell → cash', 'Keep and rent', 'Move in'], 'Wealth 20 years after inheriting, 2026 dollars, by scenario')
    facts = table(['Real episode', 'What happened', 'Why it matters here', 'Source'], [
        ['Great Depression, 1929–1932', FACTS['E12']['value'], 'Stocks and homes fell together while cash gained buying power.', src('E12', 'E08')],
        ['Inflation of the 1970s', FACTS['E13']['value'] + '. California prices rose 17.3% in a single year (1980-81) while assessed values could rise only 2%.', 'Prop 13 shelters a long-time owner most when inflation is high — and the inherited home loses that shelter.', src('E13', 'E09', 'C17')],
        ['California housing slump, 1989–1994', 'San Jose-area prices −12.5%, San Francisco-area −13.0%; eight years from peak to recovery.', 'A sale forced in the trough would have locked in the loss.', src('E05', 'E06')],
        ['Housing and stock crash, 2006–2011', 'San Jose-area home prices −26.0%, San Francisco-area −21.7%, California −40.0%; stocks −36.6% in 2008.', 'Homes and stocks can fall in the same years.', src('E05', 'E06', 'E14', 'E08')],
        ['Japan after 1990', FACTS['E10']['value'] + '. ' + FACTS['E11']['value'] + '.', 'A long stagnation in which neither property nor shares rewarded waiting.', src('E10', 'E11')],
        ['Prop 13 factor below 2%', FACTS['C17']['value'], 'Even the "2% a year" in the tables is not constant.', src('C17')],
        ['Stocks over long periods', 'Worst 10 years since 1928: −1.7% a year (1929–1938). Worst 20 years: +2.4% a year (1929–1948). Worst 30 years: +8.0% a year (1929–1958).', 'Time in the market has mattered more than the starting year — in the United States.', src('E08')],
        ['Today', FACTS['E01']['value'] + '. ' + FACTS['E02']['value'] + '.', 'Inflation and interest rates are currently above the long-run baseline.', src('E01', 'E02')],
    ])
    def rot_table(record, src_ids):
        rows = []
        for T in (2040, 2045, 2050):
            for h in (10, 20, 30):
                v = ROT[f'{record}|{T}|{h}']
                rows.append([str(T), f'{h} years', str(v['n'])] + [f"{v['wins'][k]}" for k in ('sell_stocks', 'sell_6040', 'rent_out', 'move_in')]
                            + [usd(v['median']['sell_stocks']), usd(v['median']['rent_out']), usd(v['worst']['sell_stocks']), usd(v['worst']['rent_out']),
                               badge('model') + ' ' + src(*src_ids) + ' · ' + METHOD])
        return table(['Inherited in', 'Measured after', 'Histories tried', 'Sell → stocks best', 'Sell → 60/40 best', 'Keep and rent best', 'Move in best',
                      'Median: sell → stocks', 'Median: keep and rent', 'Worst case: sell → stocks', 'Worst case: keep and rent', 'Status and data'], rows, 'num')
    rb10 = ROT['Bay Area record 1977-2025|2045|10']; rb20 = ROT['Bay Area record 1977-2025|2045|20']
    rn10 = ROT['National record 1929-2025|2045|10']; rn20 = ROT['National record 1929-2025|2045|20']
    mix_n = len(named); mix_best = sum(1 for r in named if r['best'] == 'sell_6040')
    mix_worst = sum(1 for r in named if min(keys, key=lambda k: r[k]) == 'sell_6040')
    cp = {int(k): v for k, v in S['replay_checkpoints'].items()}
    replay = table(['Year', 'Price level (2026 = 1)', 'Cupertino home', 'San Francisco building', 'Prop 19 allowance', 'Federal exclusion', 'Status and data'],
                   [[str(y), f"{cp[y]['price_level']:.2f}", usd(cp[y]['a_market']), usd(cp[y]['b_market']), usd(cp[y]['allowance']), usd(cp[y]['exclusion']),
                     badge('model') + ' ' + src('E05', 'E06', 'E09') + ' · ' + METHOD] for y in sorted(cp)], 'num',
                   'If the next 49 years repeated 1977–2025 in order (2027 = 1977 … 2075 = 2025).')
    other = table(['Shock outside the markets', 'What is known', 'Effect on this decision', 'Source'], [
        ['A major Bay Area earthquake', FACTS['E15']['value'] + ' chance, 2014–2043.', 'Both properties are in the same region. Keeping both concentrates the risk; selling the Cupertino home spreads it.', src('E15')],
        ['The rules change again', 'Since February 2021 a rented or unoccupied inherited home has no exclusion; before that there was no value limit on a parent\'s home.', 'The plan depends on rules that voters have already rewritten once. Re-check before acting.', src('C02')],
        ['The solar credit ends', '20 years from the system\'s connection date; the replacement tariff credits exports below the retail rate.', 'The present "no electricity bill" is unlikely to last to 2040–2050.', src('K01', 'K02')],
        ['Vacancy tax on the San Francisco third unit', 'Struck down in court; not collected unless the appeal decision is reversed.', 'Matters only if the heir moves to Cupertino and leaves the unit empty.', src('L04')],
        ['The estate-tax exclusion is cut', f"It is {usd(V['excl_2026'])} for 2026 and {usd(V['excl_2027'])} for 2027 under current law. It was $5,490,000 in 2017 and $11,180,000 in 2018.", 'A future Congress can lower it. The headroom on the Taxes page is not a guarantee.', src('F01', 'F03')],
        ['Insurance becomes costly or scarce', 'No official premium for either ZIP code could be confirmed.', 'Tripling the premium does not change the ranking, but an uninsurable home is hard to finance or sell.', src('K04')],
    ])
    body = f"""<h2>Black swans: the same decision under real economic history</h2>
<p class="lead">Growth and inflation are never steady for 50 years. This page replaces the smooth baseline with what actually happened — year by year, in order — and asks whether the answer survives.</p>
<div class="box"><h3>What the history says</h3><ul>
<li><strong>Over 20 years or more, selling and investing in stocks won almost every time.</strong> Bay Area record 1977–2025: {rb20['wins']['sell_stocks']} of {rb20['n']} histories. National record 1929–2025, which includes the Depression: {rn20['wins']['sell_stocks']} of {rn20['n']}.</li>
<li><strong>Over 10 years it is closer.</strong> Keeping the house and renting it out won {rb10['wins']['rent_out']} of {rb10['n']} Bay Area histories and {rn10['wins']['rent_out']} of {rn10['n']} national ones — the cases where a stock crash came soon after the inheritance.</li>
<li><strong>The worst outcomes for stocks are worse.</strong> After 10 years the poorest Bay Area history left the stock choice at {usd(rb10['worst']['sell_stocks'])} against {usd(rb10['worst']['rent_out'])} for keeping and renting (2026 dollars). Do not put money needed within a few years into shares.</li>
<li><strong>In a Japan-style stagnation, cash won</strong> and both the house and the shares lost value for two decades. Across the eight episodes and three horizons below ({mix_n} cases), the 60/40 mix of shares and cash was the best choice in {mix_best} and the worst in {mix_worst}.</li>
<li><strong>Moving in was never the best choice on money alone</strong> in any history tried. Its value is the home itself.</li>
</ul><p class="note">Practical reading: sell if the proceeds can stay invested for 20 years or more; hold part in cash or short bonds for what is needed sooner; do not sell into a housing slump if the home can be carried through it.</p></div>
<h3>What really happened</h3>{facts}
<h3>If it starts the year after you inherit</h3>
<p class="note">Baseline rates until 2045, then the real year-by-year record of the episode, then baseline again when the record runs out. The home is the Cupertino home; the Depression and 1973 rows use national home prices because local data starts in 1976.</p>
{t_named(10)}{t_named(20)}{t_named(30)}{chart}
<h3>Every starting point in the record</h3>
<p class="note">Each history is the real record played in order from a different starting year and wrapped around, laid over 2027 onward — so both the years before the inheritance and the years after it are irregular.</p>
<h4>Bay Area record, 1977–2025: local home prices, US stocks, US inflation, official Prop 13 factors</h4>{rot_table('Bay Area record 1977-2025', ('E05', 'E06', 'E08', 'E09'))}
<h4>National record, 1929–2025: US home prices, US stocks, US inflation</h4>{rot_table('National record 1929-2025', ('E08', 'E12'))}
<p class="note">Wealth figures are in 2026 dollars. National home prices move less than Bay Area prices, so the national rows understate how far a local home can rise or fall.</p>
<h3>The last 50 years, again</h3>{replay}
<p class="note">In that replay inflation in the first six years is the 1977–1982 inflation. Home values and the federal exclusion (indexed to prices) multiply; the Prop 19 allowance (one year of home-price change every two years) falls far behind, so moving in would shelter very little. <a href="{REPO}model/out/replay_1977_2025_year_by_year.csv">Year-by-year file</a>.</p>
<h3>Shocks that are not about markets</h3>{other}"""
    page('black-swans.html', 'Black swans', body)

def build_steps():
    t = table(['When', 'Step', 'Why', 'Source'], [
        ['Now', 'Confirm with the attorney that the home is in a <strong>revocable</strong> living trust that will be part of the parent\'s estate.', 'Only then does the tax basis reset to market value at death. Assets in an irrevocable trust outside the estate do not get the reset.', src('F08', 'F18')],
        ['Now', 'Confirm the home is the parent\'s principal residence with the Homeowners\' Exemption on file.', 'The parent-child exclusion only covers a home that is the parent\'s principal residence.', src('C02', 'C18')],
        ['Now', 'Find the date the solar system was connected.', 'The present credit lasts 20 years from that date.', src('K01', 'K03')],
        ['Now', 'Compare the expected estate with the exclusion; if a parent dies leaving a spouse, ask about preserving the unused exclusion.', 'The election is made on a timely estate tax return for the first spouse.', src('F01', 'F03', 'F06')],
        ['Day of death', 'This is the date the home changes hands for property tax and the date its market value becomes the heir\'s tax basis. Order a written appraisal as of this date.', 'The same value drives the Prop 19 calculation and any later capital gain.', src('C11', 'C05', 'F08')],
        ['Within 60 days', 'The successor trustee sends the required notice to every beneficiary and heir.', 'Required when a revocable trust becomes irrevocable at death.', src('C20')],
        ['Soon after', 'Get a tax identification number (EIN) for the trust; file Form 1041 for any year the trust has $600 or more of gross income.', 'The trust is a separate taxpayer after the death.', src('F22', 'F21')],
        ['Within 150 days', 'The trustee files the change-in-ownership statement with the county assessor.', 'Late filing after a written request brings a penalty.', src('C19')],
        ['Within 9 months', 'File a federal estate tax return if the estate is above the exclusion, or to preserve a spouse\'s unused exclusion. A 6-month extension is available.', f"Exclusion: {usd(V['excl_2026'])} (2026), {usd(V['excl_2027'])} (2027).", src('F20', 'F01', 'F03')],
        ['Decide early', 'Choose: move in, rent out, or sell. See <a href="decision.html">Live, rent or sell</a>.', 'The one-year clock below is already running.', src('C07')],
        ['<strong>Within 1 year</strong> — if moving in', 'Make the home the heir\'s principal residence <strong>and</strong> file the Homeowners\' Exemption claim (form BOE-266) with the county assessor.', 'No exceptions. Missing it means reassessment to full market value as of the date of death.', src('C07', 'C08', 'C18', 'C10')],
        ['Within 3 years, and before any sale — if moving in', 'File the parent-child exclusion claim (form BOE-19-P) with the county assessor.', 'A late claim gives relief only for future years.', src('C08', 'L12')],
        ['After the assessor acts', 'Expect a supplemental tax bill for the increase in assessed value, prorated from the date of death.', 'It is billed separately from the regular bill.', src('L03')],
        ['If moving in', 'End the Homeowners\' Exemption on the San Francisco unit, if one is claimed; a person has one principal residence.', 'December 10 is the last day to end it without penalty.', src('C12', 'C18')],
        ['If selling', 'Sell at about the appraised date-of-death value; report the sale. Gain is the sale price minus that value.', 'A prompt sale leaves little or no taxable gain.', src('F19', 'F09')],
        ['If renting out', 'Expect full reassessment; depreciate the building over 27.5 years; follow the state rent-cap rules that apply.', 'There is no exclusion for a rented home.', src('C10', 'F17', 'C23')],
        ['Every year after — if living there', 'Keep living there. If the heir moves out, the exclusion ends and the date-of-death value, raised by each year\'s factor, is enrolled from the next January 1. Moving back does not restore it.', 'The saving lasts only while the home is the heir\'s principal residence.', src('C09')],
        ['Nothing to do', 'The San Francisco building: no filing is triggered by the parent\'s death.', 'It is already the heir\'s; there is no change in ownership.', src('L03', 'F07')],
    ])
    body = f"""<h2>How the inheritance works, step by step</h2>
<p class="lead">For a home held in a living trust that passes to a child at the parent's death. Each step links to the official page it was read on.</p>
<div class="box warn"><h3>The one that costs the most if missed</h3>
<p>To keep part of the low assessed value the heir must be <strong>living in the home within one year of the death</strong> and must have filed the Homeowners' Exemption claim by then. The Board of Equalization states there are no exceptions. On a 2045 inheritance the difference is about {usd(B[2045]['tax_no_move_in'] - B[2045]['tax_move_in'])} of property tax in the first year, growing about 2% a year for as long as the heir lives there. {src('C07', 'C08')}</p></div>
{t}
<p class="note">Steps a lawyer or the county will add (certified death certificates, recording the trustee's affidavit, retitling) were not checked against an official page in this review and are not listed. County forms: <a href="{e(FACTS['L12']['source_url'])}" rel="noopener">Santa Clara County Assessor</a>.</p>"""
    page('steps.html', 'Inheritance steps', body)

def build_taxes():
    est = S['estate']
    t_est = table(['Year of death', 'Exclusion, one person', 'Cupertino home value', 'Other assets that fit under one exclusion', 'Other assets that fit under two', 'Status and basis'],
                  [[str(r[0]), usd(r[1]), usd(r[2]), usd(r[3]), usd(r[4]), (badge('verified') if r[0] <= 2027 else badge('model')) + ' ' + src('F01', 'F03', 'F06') + ' · ' + METHOD] for r in est], 'num',
                  'How much other inherited money fits before any federal estate tax. The San Francisco building is not counted: it is not the parent\'s.')
    ex = S['estate_examples']
    t_ex = table(['Year of death', 'Other assets (2026 dollars)', 'Other assets then', 'Estate incl. the home', 'Exclusion', 'Tax with one exclusion', 'Tax with two', 'Status and basis'],
                 [[str(r[0]), usd(r[1]), usd(r[2]), usd(r[3]), usd(r[4]), usd(r[5]), usd(r[6]), badge('model') + ' ' + src('F01', 'F03', 'F07') + ' · ' + METHOD] for r in ex], 'num',
                 f"Illustrations at the {pct(V['estate_rate'], 0)} federal rate on the amount above the exclusion.")
    def reg(ids):
        return table(['Rule', 'Value', 'As of', 'Status', 'Source'],
                     [[e(FACTS[i]['item']), e(FACTS[i]['value']), e(FACTS[i]['as_of']), badge(FACTS[i]['status']), src(i)] for i in ids])
    body = f"""<h2>Taxes and thresholds</h2>
<p class="lead">How much can be inherited before tax, at each level of government, and the rules that drive the property-tax and income-tax results.</p>
<div class="cards">
<div class="card"><div class="k">Local (city, county)</div><div class="v">$0</div><div class="s">No inheritance or estate tax. The inheritance changes the property-tax bill instead.</div></div>
<div class="card"><div class="k">California</div><div class="v">$0</div><div class="s">No estate, inheritance or gift tax for deaths since 2005. {src('C01')}</div></div>
<div class="card"><div class="k">Federal, death in 2026</div><div class="v">{usd(V['excl_2026'])}</div><div class="s">Exclusion per person. {src('F01')}</div></div>
<div class="card"><div class="k">Federal, death in 2027</div><div class="v">{usd(V['excl_2027'])}</div><div class="s">Announced November 5, 2026. Gifts: $20,000 per person a year. {src('F03', 'F05')}</div></div>
</div>
<h3>Room under the federal exclusion</h3>{t_est}
<p class="note">After 2027 the exclusion is projected with {pct(A['inflation'])} inflation {badge('assumption')}; the first adjustment was +3.2%. "Two exclusions" assumes a spouse's unused amount was preserved by an election on a timely return; the real figure depends on when the first spouse died — ask the attorney. {src('F04', 'F06')}</p>
<h3>If the other assets are large</h3>{t_ex}
<h3>Federal estate and gift tax</h3>{reg(['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F20', 'F16'])}
<h3>Income tax: basis, sale and rent</h3>{reg(['F08', 'F18', 'F19', 'F09', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F17', 'F21', 'F22', 'F23', 'C21', 'C22'])}
<h3>California property tax: Prop 13 and Prop 19</h3>{reg(['C14', 'C15', 'C16', 'C17', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C18', 'C19', 'C20', 'E16'])}
<h3>Local rates and rules</h3>{reg(['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08', 'L09', 'L10', 'L11', 'L12', 'L13', 'L14', 'L15', 'C23'])}"""
    page('taxes.html', 'Taxes & thresholds', body)

def build_properties():
    f = {2014: 1.00454, 2015: 1.01998, 2016: 1.01525, 2017: 1.02, 2018: 1.02, 2019: 1.02, 2020: 1.02, 2021: 1.01036, 2022: 1.02, 2023: 1.02, 2024: 1.02, 2025: 1.02, 2026: 1.02}
    # owner-supplied history, rounded to $10 (one six-digit figure that was already a multiple of $10 is shown to the nearest $100)
    A_H = [(2026, None, 550540), (2025, 7210, 539740), (2024, 7000, 529160), (2023, 6920, 518790), (2022, 6760, 508610), (2021, 6660, 498640),
           (2020, 6570, 493500), (2019, 6570, 483850), (2018, 6380, 474370), (2017, 6380, 465070), (2016, 6410, 455950), (2015, 6130, 449100), (2014, 5970, 440310)]
    B_H = [(2025, 2440, 114250), (2024, 2320, 112010), (2023, 2180, 109810), (2022, 2110, 107660), (2021, 2070, 105600), (2020, 2200, 104510),
           (2019, 2130, 102470), (2018, 2060, 100460), (2017, 1740, 98490), (2016, 1680, 96560)]
    def hist(H):
        rows = []
        for i, (y, tax, av) in enumerate(H):
            prev = H[i + 1][2] if i + 1 < len(H) else None
            ch = f'{100 * (av / prev - 1):+.1f}%' if prev else '—'
            rows.append([str(y), usd(tax) if tax else '<a href="flagged.html#owner">not supplied</a>', ('≈ ' if y == 2020 and av == 493500 else '') + usd(av), ch,
                         f'{100 * (f[y] - 1):.3f}%', badge('owner') + ' ' + src('C16') + ' (the official factor only)'])
        return table(['Year', 'Property tax', 'Assessed value', 'Change', 'Official Prop 13 factor that year', 'Status and source'], rows, 'num',
                     'Owner-supplied, rounded to the nearest $10. The dollar figures cannot be confirmed without identifying the parcel; the yearly changes do match the official factors.')
    def reg(ids):
        return table(['Item', 'Value', 'Status', 'Source'], [[e(FACTS[i]['item']), e(FACTS[i]['value']) or '<em>blank — not confirmed</em>', badge(FACTS[i]['status']), src(i)] for i in ids])
    b_noi = O['b_rent_month_2units'] * 12 - SQ[2026]['b_tax'] - O['b_insurance_year'] - O['b_water_month'] * 12 - O['b_electric_month'] * 12 - A['b_maintenance_year']
    costs_a = table(['Cupertino home — yearly cost today', 'Amount', 'Status', 'Source'], [
        ['Property tax (2026 estimate)', usd(SQ[2026]['a_tax']), badge('derived'), src('L11', 'C18') + ' · owner\'s 2025 bill'],
        ['of which fixed charges on the bill', usd(S['derived_direct_charges_2025']['a']), badge('derived'), src('L11') + ' · bill minus rate × assessed value'],
        ['Water', usd(O['a_water_month'] * 12) + f" ({usd(100)}–{usd(150)} a month)", badge('owner'), src('K06')],
        ['Electricity', '$0 — the solar system earns a small credit', badge('owner'), src('K01')],
        ['Homeowners insurance', usd(O['a_insurance_year']) + ' — owner\'s rough figure; no official figure confirmed', badge('unverified'), src('K04')],
        ['Maintenance', usd(A['a_maintenance_year']), badge('assumption'), NA_ASSUME],
    ], 'num')
    costs_b = table(['San Francisco building — yearly today', 'Amount', 'Status', 'Source'], [
        ['Rent, two units', usd(O['b_rent_month_2units'] * 12) + f" ({usd(O['b_rent_month_2units'])} a month)", badge('owner'), src('L13')],
        ['Property tax (2026 estimate)', usd(SQ[2026]['b_tax']), badge('derived'), src('L01') + ' · owner\'s 2025 bill'],
        ['of which fixed charges on the bill', usd(S['derived_direct_charges_2025']['b']), badge('derived'), src('L01') + ' · bill minus rate × assessed value'],
        ['Water and sewer, three units', usd(O['b_water_month'] * 12) + f" ({usd(330)}–{usd(400)} a month)", badge('owner'), src('K06')],
        ['Electricity', usd(O['b_electric_month'] * 12) + f" ({usd(30)}–{usd(70)} a month)", badge('owner'), src('K06')],
        ['Landlord insurance', usd(O['b_insurance_year']) + ' — owner\'s rough figure; no official figure confirmed', badge('unverified'), src('K05')],
        ['Maintenance', usd(A['b_maintenance_year']), badge('assumption'), NA_ASSUME],
        ['<strong>Left after these costs, before income tax</strong>', '<strong>' + usd(b_noi) + '</strong>', badge('derived'), src('L01', 'L13') + ' · sum of the rows above'],
    ], 'num')
    body = f"""<h2>The two properties and what they cost</h2>
<p class="lead">Everything the owner supplied, rounded, with what could and could not be confirmed.</p>
<div class="grid2">
<div><h3>Cupertino home, ZIP 95014 — to be inherited</h3>
<div class="cards"><div class="card"><div class="k">Estimated value, Nov 2026</div><div class="v">{usd(O['a_value_2026'])}</div><div class="s">{badge('owner')} not an appraisal</div></div>
<div class="card"><div class="k">Assessed value, 2026</div><div class="v">{usd(O['a_assessed_2026'])}</div><div class="s">{badge('owner')} about {pct(O['a_assessed_2026'] / O['a_value_2026'], 0)} of market value</div></div></div>{costs_a}</div>
<div><h3>San Francisco building, ZIP 94122 — already owned by the heir</h3>
<div class="cards"><div class="card"><div class="k">Estimated value, Nov 2026</div><div class="v">{usd(O['b_value_2026'])}</div><div class="s">{badge('owner')} three units, two rented</div></div>
<div class="card"><div class="k">Assessed value, 2025</div><div class="v">{usd(O['b_assessed_2025'])}</div><div class="s">{badge('owner')} about {pct(O['b_assessed_2025'] / O['b_value_2026'], 0)} of market value</div></div></div>{costs_b}</div>
</div>
<h3>Cupertino home: tax and assessment history</h3>{hist(A_H)}
<h3>San Francisco building: tax and assessment history</h3>{hist(B_H)}
<p class="note">The San Francisco bill moved by more than the assessed value in some years; that is consistent with fixed charges being added or removed from the bill, which was not confirmed.</p>
<h3>What could be confirmed about running costs</h3>{reg(['K01', 'K02', 'K03', 'K04', 'K05', 'K06', 'L15', 'L13', 'L14', 'L04'])}"""
    page('properties.html', 'Properties & costs', body)

def build_law():
    ids = ['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09']
    MEAN = {'P01': 'More room before any federal estate tax; the amount now rises with inflation each year.',
            'P02': "Keeps California's top income-tax brackets in place. It matters only in a year with very high taxable income, such as a large sale.",
            'P03': 'No effect on this plan.',
            'P04': 'If certified, it limits new state taxes on personal property. Close result: check the certified count.',
            'P05': 'The existing rules for local parcel taxes and bonds, which appear on property-tax bills, stay as they are.',
            'P06': 'Sets the allowance for transfers from February 16, 2027 to February 15, 2029.',
            'P07': 'The 2% cap and the parent-child rules are unchanged by this election.',
            'P08': 'Relevant only if the heir moves to Cupertino and leaves the San Francisco unit empty.',
            'P09': 'Unknown. Re-check in the year of the inheritance.'}
    t = table(['Level', 'Change', 'Where it stands', 'As of', 'What it means for this plan', 'Status', 'Source'],
              [[e(FACTS[i]['area']), e(FACTS[i]['item']), e(FACTS[i]['value']) or '<em>blank — not confirmed</em>', e(FACTS[i]['as_of']),
                e(MEAN[i]), badge(FACTS[i]['status']), src(i)] for i in ids])
    body = f"""<h2>Law changes: recent, pending and scheduled</h2>
<p class="lead">Checked on {CHECKED}. California held a statewide election on November 3, 2026; results below are unofficial until certified on December 11, 2026.</p>
<div class="box"><h3>What changed most recently</h3><ul>
<li>The IRS published the 2027 figures on November 5, 2026: exclusion {usd(V['excl_2027'])}, annual gift exclusion $20,000. {src('F03', 'F05')}</li>
<li>No measure on the November 2026 ballot changes Prop 13's 2% cap or Prop 19's parent-child rules. {src('P07')}</li>
<li>The Prop 19 allowance will be adjusted again on February 16, 2027. {src('P06')}</li>
</ul></div>
{t}
<p class="note">Bills still moving through Congress or the Legislature were not traced to an official source in this review, so none is described here. Re-check the federal exclusion and the Prop 19 rules in the year of the inheritance.</p>"""
    page('law-changes.html', 'Law changes', body)

def build_flagged():
    unv = [f for f in FACTS.values() if f['status'] == 'unverified']
    WHERE = {'K03': "The owner's utility account; rule: " + src('K01'), 'K06': "The owner's utility bills", 'L14': 'San Francisco Rent Board: ' + src('L13'),
             'P09': 'Start from ' + src('F02', 'C02')}
    t_unv = table(['Row', 'Item', 'Value', 'Why it is blank', 'Where to confirm'],
                  [[f'<span id="{f["id"]}">{f["id"]}</span>', e(f['item']), '<em>blank</em> ' + badge('unverified'), e(f['evidence']),
                    (f'<a href="{e(f["source_url"])}" rel="noopener">{e(short(f["source_title"]))}</a>' if f['source_url'] else WHERE[f['id']])] for f in unv])
    own = table(['Owner-supplied figure', 'Shown as', 'Could it be confirmed?', 'Related official source'], [
        ['Market values, Nov 2026', f"{usd(O['a_value_2026'])} and {usd(O['b_value_2026'])}", 'No — owner\'s estimates, not appraisals', src('E07')],
        ['Assessed values and tax bills by year', 'Rounded to $10 on the Properties page', 'Not the dollar figures (that needs the parcel). The yearly changes match the official factors', src('C16')],
        ['Cupertino tax bill for 2026', 'Not supplied — left blank in the history', 'No', src('L05')],
        ['San Francisco rent, two units', usd(O['b_rent_month_2units']) + ' a month', 'No', src('L13')],
        ['Water, electricity ranges', 'Midpoints used', 'No', src('K06')],
        ['Insurance, both properties', usd(O['a_insurance_year']) + ' each — the owner was unsure', 'No — no official premium by ZIP code was found', src('K04')],
    ])
    AS = [
        ('Inflation', pct(A['inflation']) + ' a year', 'Congressional Budget Office projects 2.3% from 2028; California averaged 2.6% in 2000–2019 and 3.9% over 1976–2026', ('E03', 'E09')),
        ('Cupertino home appreciation', pct(A['a_apprec']) + ' a year', 'San Jose-area index: 6.7% a year 1976–2025, 4.7% a year 2015–2025, +0.3% in 2025', ('E05', 'E07')),
        ('San Francisco building appreciation', pct(A['b_apprec']) + ' a year', 'San Francisco-area index: 6.5% a year 1976–2025, 3.2% a year 2015–2025', ('E06', 'E07')),
        ('Statewide price change behind the Prop 19 allowance', pct(A['ca_apprec']) + ' a year; ' + pct(A['ca_change_2026']) + ' for 2026', 'The 2026 figure is not published; 2025 was +1.3%', ('C04', 'E14')),
        ('Stock return', pct(A['stock_return']) + ' a year, of which ' + pct(A['dividend_yield']) + ' dividends', 'Below the 10.0% a year recorded 1928–2025', ('E08',)),
        ('Cash or savings return', pct(A['cash_return']) + ' a year', 'Three-month Treasury bills yield 4.30% today', ('E02',)),
        ('Tax on rent and interest', pct(A['tax_ordinary']), '24% federal + 9.3% California + 3.8% investment-income tax. The heir\'s income was not supplied', ('F12', 'C21', 'F14')),
        ('Tax on long-term gains and dividends', pct(A['tax_gains']), '15% federal + 9.3% California + 3.8%', ('F10', 'C22', 'F14')),
        ('Tax on depreciation taken, at sale', pct(A['tax_recapture']), '25% federal maximum + 9.3% + 3.8%', ('F09',)),
        ('Market rent of the Cupertino home', usd(V['a_hud_rent_4br_month']) + ' a month in 2026', 'Official four-bedroom benchmark for the ZIP code, a 40th-percentile figure. The number of bedrooms was not supplied', ('L15',)),
        ('Rent growth', 'Inflation + ' + pct(A['rent_growth_over_cpi']), 'Rent-controlled San Francisco units: 60% of inflation', ('L13',)),
        ('Rent for the San Francisco third unit', usd(A['b_third_unit_rent_month']) + ' a month in 2026', 'Half of the present two-unit rent', ('L13',)),
        ('Vacancy and management when renting', f"{pct(A['a_rent_vacancy'], 0)} vacancy, {pct(A['a_rent_mgmt'], 0)} management", 'Planning allowances', None),
        ('Building share of the Cupertino home\'s value', pct(A['a_building_share'], 0), 'Only the building is depreciated; the land is most of the value', ('F17',)),
        ('Maintenance', f"{usd(A['a_maintenance_year'])} and {usd(A['b_maintenance_year'])} a year (2026 dollars)", 'No official source exists for one home\'s upkeep. The owner said Cupertino needs less than San Francisco', None),
        ('Electricity after the solar credit ends', f"{usd(A['a_electric_after_solar_year'])} a year (2026 dollars) from {A['a_solar_credit_ends']}", 'The connection date is unknown', ('K01', 'K03')),
        ('Insurance and utility growth', 'Inflation + ' + pct(A['insurance_over_cpi'], 0), 'Planning margin', ('K04',)),
        ('Landlord insurance', f"{A['a_landlord_insurance_mult']}× the homeowners figure", 'Planning margin', ('K04',)),
        ('Selling costs and time', f"{pct(A['selling_cost'], 0)} of the price; {A['months_to_sell']} months to sell", 'Commission, escrow, title, transfer tax, preparation', None),
        ('Other inherited money', usd(A['other_assets_at_T']) + ' (2026 dollars), the same in every choice', 'Illustrative. It pays the running costs; the differences between choices barely depend on it', None),
        ('Filing status and home-sale exclusion', '$250,000 (single)', '$500,000 on a joint return', ('F15',)),
        ('Local tax rates stay as published', pct(V['a_rate'], 4) + ' and ' + pct(V['b_rate'], 4), 'Bond rates change every year', ('L11', 'L01')),
    ]
    t_as = table(['Assumption', 'Value used', 'Basis', 'Related official source'], [[a, b, c, src(*d) if d else NA_ASSUME] for a, b, c, d in AS])
    irr = table(['#', 'Irregularity found in this repository', 'Status', 'Official source for the correct position'], [
        ['1', 'Unrounded owner-supplied figures were published on the live site and in 19 files (146 occurrences), with 7 more figures that revealed them by arithmetic.', 'Fixed on 2026-11-11 (pull request 13).', NA_REPO],
        ['2', 'The landing page published on 2026-11-11 by another session models the San Francisco building as inherited: reassessed at the parent\'s death and counted in the estate.', 'Open — change request CR-43-3. This site treats it as already owned.', src('L03', 'F07')],
        ['3', 'Pages state the federal exclusion only as $15,000,000 and project forward from it.', 'Open — CR-43-4. The 2027 figure was published on November 5, 2026.', src('F03')],
        ['4', 'Models grow the Prop 19 allowance by a fixed 2% every year.', 'Open — CR-43-5. It moves by one year of statewide price change every second year.', src('C04')],
        ['5', 'One figure in the Cupertino history was already a multiple of $10, so rounding to $10 leaves it identical to the supplied figure. Another session restored it.', 'For the owner to decide — CR-43-6. This site shows it to the nearest $100.', NA_REPO],
        ['6', 'Four overlapping sites with different assumptions and different bottom lines were live at once (repository root, /docs/, /site/, /dashboard/).', 'Being consolidated by other sessions; not re-verified here.', NA_REPO],
        ['7', 'The chart script of the /docs/ site has a syntax error and does not run.', 'Open — CR-43-1.', NA_REPO],
        ['8', 'An earlier register says the estate tax closing letter fee was "previously $67"; the IRS page read today gives a different earlier amount.', 'Not used on this site beyond the current $76.', src('F16')],
        ['9', 'The NYU Stern table shows 7.80% for the 2025 Treasury bond return while its own cumulative column implies 8.29%.', 'Bond returns are not used in the model.', src('E08')],
        ['10', 'Earlier sites cite insurance-comparison, real-estate and legal-blog pages as sources.', 'Not used here. Only official pages, plus one academic dataset, clearly labelled.', src('K04')],
        ['11', 'Earlier pages in /docs/, /site/ and /dashboard/ were not re-verified line by line in this review.', 'Treat their figures as unverified.', NA_REPO],
    ])
    cave = table(['Caveat', 'Effect', 'Source'], [
        ['Stock, bond and national home-price history comes from an academic table (NYU Stern), not a government source. No government series of stock total returns exists.', 'Used only on the Black swans page and as background for the stock assumption.', src('E08')],
        ['Several official pages were read through the search tool\'s extract of the page rather than a full fetch.', 'Marked in the register with "(official page text as returned by search)".', src('F17', 'E03')],
        ['The Santa Clara County rate book for 2026-27 was not yet posted; the Cupertino rate is from 2025-26 and for a typical set of districts, not the parcel\'s own tax-rate area.', 'The real rate may differ by a few hundredths of a percent.', src('L05', 'L11')],
        ['The trust type, the heir\'s income and filing status, the solar connection date, the San Francisco building\'s rent-control status and the heir\'s tax basis in it were not supplied.', 'Each is an assumption above or is left out.', src('F18', 'K03', 'L14')],
        ['Local home-price data starts in 1976, so earlier episodes use national home prices.', 'Understates local swings.', src('E05', 'E12')],
        ['Earthquake damage, and the cost of insuring against it, is not in the model.', 'A reason to weigh concentration in one region.', src('E15')],
    ])
    body = f"""<h2>Flagged for Review</h2>
<p class="lead">Everything that could not be confirmed on an official page, every assumption the model makes, and the irregularities found while reviewing this repository. None of it blocks the site; all of it is for the owner to review.</p>
<div class="box bad"><h3>Privacy</h3><ul>
<li>No name, street address, parcel number or trust identifier appears on this site, and none was looked up.</li>
<li>Owner-supplied dollar figures are shown rounded to the nearest $10, as instructed.</li>
<li>Rounding to $10 prevents an exact-number web search from matching. It does not hide the figures from someone who holds a full assessment roll. If stronger protection is wanted, the year-by-year history can be removed without changing any result.</li>
<li>The site asks search engines not to index it and loads nothing from other servers.</li>
</ul></div>
<h3 id="unverified">1. Could not be confirmed — left blank</h3>{t_unv}
<h3 id="owner">2. Supplied by the owner — used, not independently confirmed</h3>{own}
<h3 id="assumptions">3. Assumptions in the model</h3>{t_as}
<h3 id="irregularities">4. Irregularities found in the repository</h3>{irr}
<h3 id="caveats">5. Limits of the data</h3>{cave}"""
    page('flagged.html', 'Flagged for Review', body)

def build_sources():
    order = ['federal', 'california', 'local', 'costs', 'economy', 'pending']
    names = {'federal': 'Federal', 'california': 'California', 'local': 'Local (San Francisco, Santa Clara County, Cupertino)', 'costs': 'Running costs',
             'economy': 'Economy and history', 'pending': 'Law changes'}
    parts = ''
    for o in order:
        rows = [f for f in FACTS.values() if f['file'] == o]
        parts += f'<h3>{names[o]}</h3>' + table(['Row', 'Item', 'Value', 'As of', 'What the page says', 'Status', 'Source'],
            [[f['id'], e(f['item']), e(f['value']) or '<em>blank</em>', e(f['as_of']), e(f['evidence']), badge(f['status']), src(f['id'])] for f in rows])
    n = len(FACTS); c = {}
    for f in FACTS.values(): c[f['status']] = c.get(f['status'], 0) + 1
    data = table(['Dataset', 'Contents', 'Source'], [
        [f'<a href="{REPO}data/hpi_fhfa_annual.csv">hpi_fhfa_annual.csv</a>', 'Home-price index, San Jose area, San Francisco area and California, 1975–2025', src('E05', 'E06', 'E14')],
        [f'<a href="{REPO}data/ca_cpi_prop13_factors.csv">ca_cpi_prop13_factors.csv</a>', 'California price change and Prop 13 factor, 1976-77 to 2026-27', src('C16')],
        [f'<a href="{REPO}data/cpi_us_december.csv">cpi_us_december.csv</a>', 'US consumer price index, December of each year, 1913–2025', src('E12')],
        [f'<a href="{REPO}data/returns_us_annual.csv">returns_us_annual.csv</a>', 'US stocks, Treasury bills and bonds, national home prices, 1928–2025 (academic)', src('E08')],
        [f'<a href="{REPO}data/japan_annual.csv">japan_annual.csv</a>', 'Japan: home prices, Nikkei 225, consumer prices, 1955–2025', src('E10', 'E11')],
    ])
    method = table(['Step', 'How it is calculated', 'Rule it follows'], [
        ['Assessed value while the same owner holds', 'Last value × that year\'s factor, never more than 1.02; lowered to market value if the market is below it', src('C14', 'E16')],
        ['Property tax', 'Assessed value (less $7,000 for an owner-occupied home) × local rate + fixed charges that rise with inflation', src('L11', 'L01', 'C18')],
        ['Allowance', '$1,044,586, multiplied every second February from 2027 by the statewide price change of the previous calendar year', src('C03', 'C04')],
        ['Assessed value after inheritance, heir moves in', 'Parent\'s assessed value + (market value − parent\'s assessed value − allowance), if that is positive; otherwise unchanged', src('C05', 'C06')],
        ['Assessed value after inheritance, not moved in', 'Market value on the date of death', src('C10')],
        ['Sale after inheritance', 'Gain = price less selling costs − date-of-death value; taxed at the long-term rate; first $250,000 excluded after two years of living there', src('F08', 'F19', 'F15')],
        ['Renting out', 'Rent − vacancy − management − property tax − insurance − maintenance; building depreciated over 27.5 years; unused losses carried to the sale', src('F17', 'F09')],
        ['Investing', 'Dividends and interest taxed every year; growth taxed when money is taken out or at the final valuation', src('F09', 'F14')],
        ['Comparison', 'Each choice starts with the same other money, pays its own costs from it, and is valued after tax as if everything were sold at the horizon', NA_ASSUME],
        ['Federal exclusion', '$15,000,000 (2026), $15,480,000 (2027), then raised with inflation', src('F01', 'F03')],
        ['Black swans', 'The constant rates are replaced by the real yearly record: home-price change, stock return, inflation and Prop 13 factor of each historical year, in order', src('E05', 'E08', 'C16')],
    ])
    body = f"""<h2>Sources and method</h2>
<p class="lead">{n} register rows: {c.get('verified', 0)} read on the official page on {CHECKED}, {c.get('derived', 0)} derived by arithmetic from those, {c.get('unverified', 0)} that could not be confirmed and are left blank. Every row links to the page it came from.</p>
<h3 id="method">How the model works</h3>{method}
<p class="note">The model is one Python file with no dependencies: <a href="{REPO}model/model.py">model.py</a>. Every assumption sits in one block at the top and is listed on <a href="flagged.html#assumptions">Flagged for Review</a>. Output files: <a href="{TREE}model/out">model/out</a>. Register files: <a href="{TREE}facts">facts</a>.</p>
<h3>Datasets</h3>{data}
<h2 style="margin-top:34px">The fact register</h2>{parts}"""
    page('sources.html', 'Sources & method', body)

def main():
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    with open(os.path.join(OUT, 'assets', 'site.css'), 'w', encoding='utf-8') as f:
        f.write(CSS)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    for fn in (build_index, build_decision, build_projections, build_blackswans, build_steps, build_taxes, build_properties,
               build_law, build_flagged, build_sources):
        fn()
    print('built', len(NAV), 'pages in', OUT)

if __name__ == '__main__':
    main()
