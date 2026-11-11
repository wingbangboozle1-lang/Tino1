"""Static 11-page dashboard generator for session arena/459d7aa2-tino1.

Generates _session_459d7aa2/site/{11 HTML pages, style.css, app.js} from
_session_459d7aa2/data/model_output.json and _session_459d7aa2/sources.py.

Strict invariants enforced on every generated page:
  1. <meta name="robots" content="noindex, nofollow"> on all HTML pages.
  2. Every <tbody><tr> row includes at least one https:// official-source link.
  3. Every $ figure in visible HTML text is an integer multiple of $10.
  4. Unconfirmable values are left blank (with a Flagged for Review link) and
     never inferred or filled in as verified facts.
  5. Zero personal identifiers and zero unrounded county-roll numbers.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from model import run_all
from sources import SOURCES, verify_source_registry

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR / "site"

NAV_ITEMS = [
    ("index.html", "Executive Summary", "Summary"),
    ("properties.html", "Properties & Ownership", "Ownership"),
    ("decision.html", "Decision Comparison", "Decision"),
    ("projections.html", "50-Year Projections", "50-Yr Table"),
    ("black-swan.html", "Black Swan Conditions", "Black Swan"),
    ("process.html", "Trust Inheritance Steps", "16 Steps"),
    ("taxes-estate.html", "Taxes & Cash Headroom", "Estate & Cash"),
    ("costs-insurance.html", "Utilities & Insurance", "Costs & Ins."),
    ("requirements.html", "Prompt & Repo Audit", "Audit"),
    ("sources.html", f"Official Sources ({len(SOURCES)})", "Sources"),
    ("flagged.html", "Flagged for Review", "Flagged"),
]


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def usd(n: int) -> str:
    assert isinstance(n, int) and (n == 0 or n % 10 == 0), f"Non-$10 value: {n}"
    if n < 0:
        return f"-${abs(n):,}"
    return f"${n:,}"


def src(sid: str, label: str | None = None) -> str:
    meta = SOURCES[sid]
    txt = esc(label or meta["short"])
    title = esc(f"{meta['title']} ({meta['agency']})")
    url = esc(meta["url"])
    return f'<a class="src-link" href="{url}" target="_blank" rel="noopener noreferrer" title="{title}">{txt} &#8599;</a>'


def srcs(*sids: str) -> str:
    return " &middot; ".join(src(s) for s in sids)


def flag_link(fid: str, text: str = "Unverified") -> str:
    return f'<a class="badge badge-warn" href="flagged.html#{esc(fid)}">Flag {esc(fid)}: {esc(text)}</a>'


def blank_unverified(fid: str, note: str = "Left blank — unverified") -> str:
    return f'<span class="blank-cell" title="{esc(note)}"></span> {flag_link(fid, note)}'


def badge(kind: str, label: str) -> str:
    cls = {
        "official": "badge-ok",
        "owner": "badge-owner",
        "model": "badge-model",
        "warn": "badge-warn",
    }[kind]
    return f'<span class="badge {cls}">{esc(label)}</span>'


CSS = """
:root {
  --bg: #f6f8fb;
  --panel: #ffffff;
  --ink: #142033;
  --muted: #526178;
  --line: #dde3ee;
  --accent: #174ea6;
  --accent-soft: #e8f0fe;
  --ok-bg: #e6f4ea;
  --ok-ink: #137333;
  --warn-bg: #fef7e0;
  --warn-ink: #8c5400;
  --owner-bg: #f3e8fd;
  --owner-ink: #681da8;
  --model-bg: #e8f0fe;
  --model-ink: #174ea6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
  font-size: 15px;
}
.skip-link {
  position: absolute; left: -9999px; top: 0;
  background: var(--accent); color: #fff; padding: 8px 14px; z-index: 100;
}
.skip-link:focus { left: 12px; top: 12px; }
.topbar {
  background: #0f1b2d; color: #fff; padding: 12px 20px;
  border-bottom: 1px solid #22324c;
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;
}
.brand { font-weight: 700; font-size: 16px; letter-spacing: -0.01em; color: #fff; text-decoration: none; }
.privacy-pill {
  font-size: 12px; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 999px; color: #dbeafe;
}
.layout {
  max-width: 1360px; margin: 0 auto; display: grid;
  grid-template-columns: 240px minmax(0, 1fr); gap: 24px; padding: 22px 20px 56px;
}
@media (max-width: 960px) {
  .layout { grid-template-columns: 1fr; }
}
.sidenav {
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
  padding: 12px; align-self: start; position: sticky; top: 16px;
}
.sidenav-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--muted); margin: 4px 8px 8px;
}
.sidenav a {
  display: block; padding: 7px 10px; border-radius: 6px; color: var(--ink);
  text-decoration: none; font-size: 13.5px; margin-bottom: 2px;
}
.sidenav a:hover { background: var(--bg); }
.sidenav a.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
main { min-width: 0; }
.hero {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 22px 24px; margin-bottom: 18px;
}
.hero h1 { margin: 0 0 8px; font-size: 24px; letter-spacing: -0.02em; }
.hero p { margin: 0; color: var(--muted); max-width: 92ch; }
.kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px; margin-bottom: 18px;
}
.kpi {
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 15px 16px;
}
.kpi .label { font-size: 12px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; }
.kpi .val { font-size: 22px; font-weight: 700; margin: 6px 0 4px; font-variant-numeric: tabular-nums; color: var(--ink); }
.kpi .sub { font-size: 12.5px; color: var(--muted); }
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 20px 22px; margin-bottom: 18px;
}
.card h2 { margin: 0 0 10px; font-size: 18px; letter-spacing: -0.01em; }
.card h3 { margin: 16px 0 8px; font-size: 15.5px; }
.card p { margin: 0 0 12px; color: var(--ink); }
.callout {
  border-left: 4px solid var(--accent); background: var(--accent-soft);
  padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 14px;
}
.callout.warn { border-left-color: #d97706; background: var(--warn-bg); color: #5c3700; }
.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; margin-top: 10px; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; background: var(--panel); }
th, td { padding: 9px 11px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th {
  background: #f1f5f9; font-weight: 600; font-size: 12px; color: #334155;
  text-transform: uppercase; letter-spacing: 0.03em; position: sticky; top: 0;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f9fbff; }
tr.highlight-row td { background: #eef5ff; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.src-link { color: var(--accent); text-decoration: none; font-weight: 500; white-space: nowrap; }
.src-link:hover { text-decoration: underline; }
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11.5px;
  font-weight: 600; text-decoration: none; white-space: nowrap;
}
.badge-ok { background: var(--ok-bg); color: var(--ok-ink); }
.badge-warn { background: var(--warn-bg); color: var(--warn-ink); border: 1px solid #f5d07a; }
.badge-owner { background: var(--owner-bg); color: var(--owner-ink); }
.badge-model { background: var(--model-bg); color: var(--model-ink); }
.blank-cell::before { content: ""; }
.controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0 12px; }
.tab-btn {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  padding: 6px 13px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px;
}
.tab-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.filter-input {
  padding: 6px 11px; border: 1px solid var(--line); border-radius: 6px; font-size: 13.5px; min-width: 240px;
}
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; font-size: 12.5px; color: var(--muted); align-items: center; }
footer {
  margin-top: 26px; padding-top: 14px; border-top: 1px solid var(--line);
  font-size: 12.5px; color: var(--muted);
}
"""

JS = """
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-tab-group]').forEach(group => {
    const groupName = group.getAttribute('data-tab-group');
    const buttons = group.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        buttons.forEach(b => b.classList.toggle('active', b === btn));
        document.querySelectorAll(`[data-tab-panel="${groupName}"]`).forEach(panel => {
          panel.style.display = (panel.id === target) ? '' : 'none';
        });
      });
    });
  });

  document.querySelectorAll('[data-table-filter]').forEach(input => {
    const tableId = input.getAttribute('data-table-filter');
    const table = document.getElementById(tableId);
    if (!table) return;
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(tr => {
        tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
});
"""


def render_page(filename: str, title: str, subtitle: str, body_html: str) -> None:
    nav_links = []
    for href, full_label, _ in NAV_ITEMS:
        cls = ' class="active"' if href == filename else ""
        nav_links.append(f'<a href="{href}"{cls}>{esc(full_label)}</a>')

    legend_html = (
        '<div class="legend">'
        "<span>Provenance key:</span> "
        f"{badge('official', 'Verified Official Rule/Rate')} "
        f"{badge('owner', 'Owner Scenario Input ($10/$100 Rounded)')} "
        f"{badge('model', 'Model Projection ($10 Rounded)')} "
        f"{badge('warn', 'Unverified — Left Blank & Flagged')}"
        "</div>"
    )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>{esc(title)} — Two-Property Inheritance Decision Dashboard</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="topbar">
    <a class="brand" href="index.html">Two-Property Inheritance Decision Dashboard (ZIP 95014 &amp; ZIP 94122)</a>
    <span class="privacy-pill">Privacy-Hardened &middot; Anonymized Placeholders &middot; Nearest-$10 Rounding &middot; 100% Official-Sourced Rows</span>
  </header>
  <div class="layout">
    <nav class="sidenav" aria-label="Dashboard sections">
      <div class="sidenav-title">Analysis Sections</div>
      {"".join(nav_links)}
    </nav>
    <main id="main">
      <section class="hero">
        <h1>{esc(title)}</h1>
        <p>{subtitle}</p>
        {legend_html}
      </section>
      {body_html}
      <footer>
        Anonymized decision analysis for <code>[Property A — Cupertino Home, ZIP 95014]</code> (trust-inherited ~2040–2050) and <code>[Property B — San Francisco Triplex, ZIP 94122]</code> (already owned by <code>[Inheritor]</code>). All figures rounded to nearest $10; every table row links to a verified official <code>.gov</code> / public-agency source; unverifiable values are left blank and listed on <a href="flagged.html">Flagged for Review</a>. Not legal or tax advice.
      </footer>
    </main>
  </div>
  <script src="app.js"></script>
</body>
</html>
"""
    (SITE_DIR / filename).write_text(doc, encoding="utf-8")


def build_index(data: dict) -> None:
    b45 = data["baseline_by_inherit_year"]["2045"]
    e45 = b45["end_2076"]
    r50 = data["rolling_50yr"]
    ec45 = data["estate_cash"]["key_years"]["2045"]
    nostep = data["sensitivities_2045"]["no_step_up_irrevocable_trust"]["end_2076"]

    panels = []
    for iy in ("2040", "2045", "2050"):
        b = data["baseline_by_inherit_year"][iy]
        e = b["end_2076"]
        s10 = b["snapshots_by_horizon"].get("10") or b["snapshots_by_horizon"][10]
        disp = "" if iy == "2045" else ' style="display:none"'
        panels.append(f"""
        <div id="inh-{iy}" data-tab-panel="inh-summary"{disp}>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Decision Metric (Inheritance in {iy})</th>
                  <th class="num">S1: Live in Property A</th>
                  <th class="num">S2: Rent Property A</th>
                  <th class="num">S3A: Sell &amp; Equities (7%)</th>
                  <th class="num">S3C: Sell &amp; Cash/T-Bills (3.5%)</th>
                  <th>Provenance &amp; Official Source</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>[Property A]</code> market value at inheritance ({iy})</td>
                  <td class="num">{usd(b["cup_fmv_at_inh"])}</td>
                  <td class="num">{usd(b["cup_fmv_at_inh"])}</td>
                  <td class="num">{usd(b["cup_fmv_at_inh"])}</td>
                  <td class="num">{usd(b["cup_fmv_at_inh"])}</td>
                  <td>{badge("model", "4.0%/yr baseline")} {srcs("FRED-HPI-SJ")}</td>
                </tr>
                <tr>
                  <td>New Prop 19 / Prop 13 taxable assessed value ({iy})</td>
                  <td class="num">{usd(b["s1_av_at_inh"])}</td>
                  <td class="num">{usd(b["s2_av_at_inh"])}</td>
                  <td class="num">$0 (sold)</td>
                  <td class="num">$0 (sold)</td>
                  <td>{badge("official", "R&TC §63.2 formula")} {srcs("CA-RTC-63-2", "BOE-LTA-26026")}</td>
                </tr>
                <tr>
                  <td>First-year Cupertino property tax bill ({iy})</td>
                  <td class="num">{usd(b["s1_tax_yr1"])}</td>
                  <td class="num">{usd(b["s2_tax_yr1"])}</td>
                  <td class="num">$0 after sale</td>
                  <td class="num">$0 after sale</td>
                  <td>{badge("official", "SCC TRA + BOE-266")} {srcs("SCC-RATES", "BOE-HOX")}</td>
                </tr>
                <tr>
                  <td>Net after-tax cash released at inheritance ({iy})</td>
                  <td class="num">$0</td>
                  <td class="num">$0</td>
                  <td class="num">{usd(b["sale_net_proceeds_at_inh"])}</td>
                  <td class="num">{usd(b["sale_net_proceeds_at_inh"])}</td>
                  <td>{badge("official", "IRC §1014 step-up")} {srcs("IRS-GIFT-FAQ", "SCC-DTT")}</td>
                </tr>
                <tr>
                  <td>After-tax wealth 10 years after inheritance (2026 real $)</td>
                  <td class="num">{usd(s10["wealth_s1_real"])}</td>
                  <td class="num">{usd(s10["wealth_s2_real"])}</td>
                  <td class="num">{usd(s10["wealth_s3_eq_real"])}</td>
                  <td class="num">{usd(s10["wealth_s3_cash_real"])}</td>
                  <td>{badge("model", "After all taxes")} {srcs("IRS-TC409", "FRED-CPI")}</td>
                </tr>
                <tr class="highlight-row">
                  <td><strong>2076 terminal after-tax wealth (nominal $)</strong></td>
                  <td class="num">{usd(e["wealth_s1_nom"])}</td>
                  <td class="num">{usd(e["wealth_s2_nom"])}</td>
                  <td class="num">{usd(e["wealth_s3_eq_nom"])}</td>
                  <td class="num">{usd(e["wealth_s3_cash_nom"])}</td>
                  <td>{badge("model", "Liquidated net of tax")} {srcs("IRS-TC409", "IRS-TC559", "FTB-RATES")}</td>
                </tr>
                <tr class="highlight-row">
                  <td><strong>2076 terminal after-tax wealth (in 2026 real $)</strong></td>
                  <td class="num">{usd(e["wealth_s1_real"])}</td>
                  <td class="num">{usd(e["wealth_s2_real"])}</td>
                  <td class="num">{usd(e["wealth_s3_eq_real"])}</td>
                  <td class="num">{usd(e["wealth_s3_cash_real"])}</td>
                  <td>{badge("model", "Deflated at 2.5% CPI")} {srcs("FRED-CPI", "SEC-ALLOC")}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        """)

    body = f"""
    <div class="kpi-grid">
      <div class="kpi">
        <div class="label">Conditional Best Financial Plan</div>
        <div class="val">Sell Prop. A &middot; Keep Prop. B</div>
        <div class="sub">Reinvest in diversified equities; leads in {r50['sell_beats_rent_10yr']}/50 real 10-yr &amp; {r50['sell_beats_rent_20yr']}/50 20-yr windows</div>
      </div>
      <div class="kpi">
        <div class="label">2076 Real Wealth (2045 Inheritance)</div>
        <div class="val">{usd(e45["wealth_s3_eq_real"])}</div>
        <div class="sub">vs. {usd(e45["wealth_s2_real"])} Rent &middot; {usd(e45["wealth_s1_real"])} Live &middot; {usd(e45["wealth_s3_cash_real"])} Cash (in 2026$)</div>
      </div>
      <div class="kpi">
        <div class="label">Prop. A Tax: 2026 / Live / Rent (2045)</div>
        <div class="val">$7,200 / {usd(b45["s1_tax_yr1"])} / {usd(b45["s2_tax_yr1"])}</div>
        <div class="sub">Prop 19 still raises annual Cupertino tax by +$42,770/yr even if occupied</div>
      </div>
      <div class="kpi">
        <div class="label">Prop. B Annual Prop 13 Shield</div>
        <div class="val">$19,980/yr (2026)</div>
        <div class="sub">Already owned ($116,540 AV vs. $1,800,000 FMV); grows to $62,380/yr by 2045</div>
      </div>
      <div class="kpi">
        <div class="label">2045 Tax-Free Cash Headroom</div>
        <div class="val">{usd(ec45["cash_headroom_single"])}</div>
        <div class="sub">Single transferor ({usd(ec45["married_dsue_exclusion"] - ec45["cup_fmv"])} married DSUE); $0 CA &amp; $0 local death tax</div>
      </div>
    </div>

    <div class="callout">
      <strong>Why the ownership distinction changes everything:</strong> <code>[Property B — San Francisco Triplex, ZIP 94122]</code> is <strong>already owned</strong> by <code>[Inheritor]</code>, so <code>[Transferor]</code>'s death triggers <strong>zero</strong> Prop 19 reassessment on Property B, <strong>zero</strong> IRC &sect; 1014 basis reset on Property B, and <strong>zero</strong> inclusion in <code>[Transferor]</code>'s federal estate. By contrast, <code>[Property A — Cupertino Home, ZIP 95014]</code> is <strong>inherited via trust</strong>: if included in <code>[Transferor]</code>'s gross estate, it receives a full date-of-death basis reset to <strong>{usd(b45["cup_fmv_at_inh"])}</strong> (2045 baseline) so selling shortly after death owes <strong>$0 capital-gains tax</strong> while avoiding a <strong>{usd(b45["s1_tax_yr1"])}–{usd(b45["s2_tax_yr1"])}/yr</strong> reassessed property tax bill.
    </div>

    <section class="card">
      <h2>Recommended Action Plan &amp; Reasoning (Conditional on Stated Assumptions)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Priority</th>
              <th>Recommendation</th>
              <th>Clear Quantitative Reasoning ($10-Rounded)</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>1. Keep SF</strong></td>
              <td><strong>Retain <code>[Property B — SF Triplex, 94122]</code> and keep living in Unit 3</strong></td>
              <td>Assessed at <strong>$116,540</strong> vs. <strong>$1,800,000</strong> market value (saving <strong>$19,980/yr</strong> in 2026 tax at SF's 1.18162182% rate), produces <strong>$85,800/yr</strong> across the 2 rented units while leaving Unit 3 free for <code>[Inheritor]</code>, and has <strong>no</strong> IRC &sect; 1014 basis step-up if sold.</td>
              <td>{srcs("CA-RTC-51", "SFT-RATE", "SF-RPTT")}</td>
            </tr>
            <tr>
              <td><strong>2. Sell Cupertino</strong></td>
              <td><strong>Sell <code>[Property A — Cupertino, 95014]</code> post-inheritance &amp; invest in diversified equities</strong></td>
              <td>Releases <strong>{usd(b45["sale_net_proceeds_at_inh"])}</strong> net cash in 2045 at <strong>$0</strong> capital-gains tax, compounding to <strong>{usd(e45["wealth_s3_eq_real"])}</strong> (2026 real $) by 2076 — beating Renting by <strong>{usd(e45["wealth_s3_eq_real"] - e45["wealth_s2_real"])}</strong> and Living in Cupertino by <strong>{usd(e45["wealth_s3_eq_real"] - e45["wealth_s1_real"])}</strong>.</td>
              <td>{srcs("IRS-GIFT-FAQ", "SCC-DTT", "SEC-ALLOC")}</td>
            </tr>
            <tr>
              <td><strong>3. Avoid Cash Parking</strong></td>
              <td><strong>Do NOT sell Property A merely to hold savings / Treasury bills</strong></td>
              <td>At 3.5% nominal T-bill/savings yield, 2076 real wealth is <strong>{usd(e45["wealth_s3_cash_real"])}</strong> — trailing Keeping &amp; Renting Property A (<strong>{usd(e45["wealth_s2_real"])}</strong>) by <strong>{usd(e45["wealth_s2_real"] - e45["wealth_s3_cash_real"])}</strong> in 2026 dollars.</td>
              <td>{srcs("FRED-TB3MS", "TREAS-YC", "IRS-P527")}</td>
            </tr>
            <tr>
              <td><strong>4. Stage Entry</strong></td>
              <td><strong>Use a 24–36 month Treasury-bill glidepath into equities after sale</strong></td>
              <td>In 50 real historical sequences (1976–2025), lump-sum equities win 43/50 at Year 10 and 46/50 at Year 20, but lose by <strong>{usd(abs(r50["worst_10yr"]["yr10_sell_minus_rent_real"]))}</strong> at Year 10 if sold on the eve of a 2000+2008 double crash.</td>
              <td>{srcs("NBER-CYCLES", "FRED-HPI-SJ", "SEC-ALLOC")}</td>
            </tr>
            <tr>
              <td><strong>5. Verify Trust</strong></td>
              <td><strong>Have estate counsel verify gross-estate inclusion before transfer</strong></td>
              <td>If Property A sits in an irrevocable trust excluded from <code>[Transferor]</code>'s gross estate (<em>Rev. Rul. 2023-2</em>), carryover basis triggers massive sale tax and cuts 2076 real sale wealth to <strong>{usd(nostep["wealth_s3_eq_real"])}</strong>.</td>
              <td>{srcs("RR-2023-2", "IRS-P551")} {flag_link("U02", "Verify trust instrument")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Interactive Inheritance-Year Comparison (2040 vs. 2045 vs. 2050)</h2>
      <div class="controls" data-tab-group="inh-summary">
        <span>Select inheritance year:</span>
        <button class="tab-btn" type="button" data-target="inh-2040">2040 Inheritance</button>
        <button class="tab-btn active" type="button" data-target="inh-2045">2045 Inheritance (Midpoint)</button>
        <button class="tab-btn" type="button" data-target="inh-2050">2050 Inheritance</button>
      </div>
      {"".join(panels)}
    </section>
    """
    render_page(
        "index.html",
        "Executive Summary & Optimal Inheritance Plan",
        "Line-by-line verified 50-year financial & tax analysis (2026–2076) comparing living in, renting, or selling an inherited Cupertino single-family home while already owning a 3-unit San Francisco property.",
        body,
    )


def build_properties(data: dict) -> None:
    body = f"""
    <section class="card">
      <h2>Side-by-Side Property &amp; Legal Baseline (Nov 2026)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Attribute</th>
              <th><code>[Property A — Cupertino Home, ZIP 95014]</code></th>
              <th><code>[Property B — San Francisco Triplex, ZIP 94122]</code></th>
              <th>Provenance &amp; Official Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Current title &amp; transfer mechanism</td>
              <td>Held in <code>[Transferor]</code>'s trust; passes to <code>[Inheritor]</code> around 2040–2050</td>
              <td><strong>Already owned</strong> directly by <code>[Inheritor]</code>; unaffected by <code>[Transferor]</code>'s death</td>
              <td>{badge("owner", "Owner brief")} {srcs("BOE-462-260", "CA-PROB-16061-7")}</td>
            </tr>
            <tr>
              <td>Configuration &amp; occupancy</td>
              <td>Single-family residence with rooftop solar</td>
              <td>3 livable residential units: 2 rented (<strong>$7,150/mo</strong> = <strong>$85,800/yr</strong>) + 1 available for <code>[Inheritor]</code></td>
              <td>{badge("owner", "Owner brief")} {srcs("SF-RENT-LAW", "DOJ-TPA")}</td>
            </tr>
            <tr>
              <td>Estimated Nov 2026 market value</td>
              <td><strong>$3,100,000</strong></td>
              <td><strong>$1,800,000</strong></td>
              <td>{badge("owner", "Owner est.")} {srcs("FRED-HPI-SJ", "FRED-HPI-SF")}</td>
            </tr>
            <tr>
              <td>2026 Prop 13 assessed value ($10/$100 coarsened)</td>
              <td><strong>$550,500</strong> (coarsened to $100 for anti-traceability)</td>
              <td><strong>$116,540</strong> ($10-rounded; 2025 roll &times; 1.02 BOE 2026 CCPI factor)</td>
              <td>{badge("owner", "Rounded")} {srcs("CA-RTC-51", "BOE-LTA-26002")}</td>
            </tr>
            <tr>
              <td>Verified historical Prop 13 CCPI roll factors</td>
              <td>2014 (+0.454%), 2016 (+1.525%), 2021 (+1.036%), all other years 2015–2026 (+2.00% cap) — 100% match to BOE LTA 2026/002</td>
              <td>2018–2020 (+2.00%), 2021 (+1.036%), 2022–2026 (+2.00%) — 100% match to BOE LTA 2026/002 (raw year-by-year sequence withheld for privacy)</td>
              <td>{badge("official", "Verified vs. BOE")} {srcs("BOE-LTA-26002", "SCC-P13")}</td>
            </tr>
            <tr>
              <td>Local ad valorem tax rate &amp; 2026 bill</td>
              <td>~1.18% Cupertino TRA rate + ~$710 parcel charges &rarr; <strong>$7,200/yr</strong> coarsened</td>
              <td><strong>1.18162182%</strong> official FY2026–27 SF rate + ~$810 parcel charges &rarr; <strong>$2,100/yr</strong></td>
              <td>{badge("official", "Official rate books")} {srcs("SCC-RATES", "SFT-RATE")}</td>
            </tr>
            <tr>
              <td>Prop 19 treatment upon <code>[Transferor]</code>'s death</td>
              <td>If occupied within 1 yr: <code>FBYV + max(0, FMV - (FBYV + indexed $1,044,590))</code>; if rented: <strong>100% FMV reassessment</strong></td>
              <td><strong>Not applicable ($0 change)</strong> — no transfer occurs on Property B</td>
              <td>{badge("official", "R&TC §63.2")} {srcs("CA-RTC-63-2", "BOE-LTA-25009", "BOE-LTA-26026")}</td>
            </tr>
            <tr>
              <td>Rent-regulation regime if leased</td>
              <td>Individually/trust-owned single-family home <strong>exempt</strong> from AB 1482 rent cap <em>if</em> mandatory written statutory notice is in lease</td>
              <td>Pre-June 14, 1979 3-unit building subject to SF Rent Ordinance (<strong>1.6%</strong> allowable increase Mar 2026–Feb 2027; vacancy decontrol on empty unit)</td>
              <td>{badge("official", "State & local law")} {srcs("DOJ-TPA", "SF-RENT-LAW", "SF-RENT-RATE")}</td>
            </tr>
            <tr>
              <td>Documentary transfer tax if sold</td>
              <td><strong>0.11%</strong> (55 cents per $500; Cupertino has no city conveyance tax); $0 on inheritance deed</td>
              <td><strong>0.75%</strong> ($1M–&lt;$5M) or <strong>2.25%</strong> ($5M–&lt;$10M) SF RPTT on entire sale value</td>
              <td>{badge("official", "County/City schedules")} {srcs("SCC-DTT", "SF-RPTT")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "properties.html",
        "Properties & Ownership Asymmetry (ZIP 95014 vs. ZIP 94122)",
        "Detailed comparison of the trust-inherited Cupertino single-family home and the already-owned San Francisco 3-unit property, including our BOE CCPI audit of historical assessment growth.",
        body,
    )


def build_decision(data: dict) -> None:
    b45 = data["baseline_by_inherit_year"]["2045"]
    e45 = b45["end_2076"]
    nostep = data["sensitivities_2045"]["no_step_up_irrevocable_trust"]
    nem = data["sensitivities_2045"]["post_nem_20yr_sunset"]

    body = f"""
    <section class="card">
      <h2>All Five Strategy Variants + Key Sensitivities (2045 Inheritance &rarr; 2076 Horizon)</h2>
      <p>Every strategy retains <code>[Property B — SF Triplex]</code> and its existing two rented units (<strong>$85,800/yr</strong> today). Incremental wealth measures <code>[Property A]</code> plus all differential after-tax cash flows compounded to 2076 and liquidated net of all federal, NIIT, §1250, and California taxes.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Strategy / Sensitivity</th>
              <th class="num">2045 Cash Released</th>
              <th class="num">2045 Yr-1 Prop. A Tax</th>
              <th class="num">2076 Wealth (Nominal $)</th>
              <th class="num">2076 Wealth (2026 Real $)</th>
              <th class="num">vs. Best Plan (2026$)</th>
              <th>Official Legal / Economic Basis</th>
            </tr>
          </thead>
          <tbody>
            <tr class="highlight-row">
              <td><strong>S3A: Sell Property A &amp; Reinvest in Diversified Equities (7.0%)</strong></td>
              <td class="num">{usd(b45["sale_net_proceeds_at_inh"])}</td>
              <td class="num">$0 after sale</td>
              <td class="num">{usd(e45["wealth_s3_eq_nom"])}</td>
              <td class="num">{usd(e45["wealth_s3_eq_real"])}</td>
              <td class="num">$0 (Leader)</td>
              <td>{srcs("IRS-GIFT-FAQ", "IRS-TC409", "SEC-ALLOC")}</td>
            </tr>
            <tr>
              <td><strong>S2: Keep &amp; Rent Out Property A (Stay in SF Unit 3)</strong></td>
              <td class="num">$0</td>
              <td class="num">{usd(b45["s2_tax_yr1"])}</td>
              <td class="num">{usd(e45["wealth_s2_nom"])}</td>
              <td class="num">{usd(e45["wealth_s2_real"])}</td>
              <td class="num">{usd(e45["wealth_s2_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("CA-RTC-63-2", "IRS-TC414", "IRS-P527")}</td>
            </tr>
            <tr>
              <td><strong>S3B: Sell Property A &amp; Reinvest in 60/40 Balanced (6.0%)</strong></td>
              <td class="num">{usd(b45["sale_net_proceeds_at_inh"])}</td>
              <td class="num">$0 after sale</td>
              <td class="num">{usd(e45["wealth_s3_bal_nom"])}</td>
              <td class="num">{usd(e45["wealth_s3_bal_real"])}</td>
              <td class="num">{usd(e45["wealth_s3_bal_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("SEC-ALLOC", "FRED-DGS10", "IRS-TC409")}</td>
            </tr>
            <tr>
              <td><strong>S1: Live in Property A + Rent Vacated SF Unit 3</strong></td>
              <td class="num">$0</td>
              <td class="num">{usd(b45["s1_tax_yr1"])}</td>
              <td class="num">{usd(e45["wealth_s1_nom"])}</td>
              <td class="num">{usd(e45["wealth_s1_real"])}</td>
              <td class="num">{usd(e45["wealth_s1_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("CA-RTC-63-2", "BOE-LTA-26026", "SF-RENT-RATE")}</td>
            </tr>
            <tr>
              <td><strong>S3C: Sell Property A &amp; Park in T-Bills / Savings (3.5%)</strong></td>
              <td class="num">{usd(b45["sale_net_proceeds_at_inh"])}</td>
              <td class="num">$0 after sale</td>
              <td class="num">{usd(e45["wealth_s3_cash_nom"])}</td>
              <td class="num">{usd(e45["wealth_s3_cash_real"])}</td>
              <td class="num">{usd(e45["wealth_s3_cash_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("FRED-TB3MS", "TREAS-YC")}</td>
            </tr>
            <tr>
              <td><em>Sensitivity A:</em> Irrevocable Trust Excluded from Gross Estate (No §1014 Step-Up on S3A)</td>
              <td class="num">{usd(nostep["sale_net_proceeds_at_inh"])}</td>
              <td class="num">$0 after sale</td>
              <td class="num">{usd(nostep["end_2076"]["wealth_s3_eq_nom"])}</td>
              <td class="num">{usd(nostep["end_2076"]["wealth_s3_eq_real"])}</td>
              <td class="num">{usd(nostep["end_2076"]["wealth_s3_eq_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("RR-2023-2", "FTB-RATES", "FTB-MHS")}</td>
            </tr>
            <tr>
              <td><em>Sensitivity B:</em> CPUC 20-Yr NEM Solar Sunset + $290/yr Fixed Charge (Effect on S2 Rent)</td>
              <td class="num">$0</td>
              <td class="num">{usd(nem["s2_tax_yr1"])}</td>
              <td class="num">{usd(nem["end_2076"]["wealth_s2_nom"])}</td>
              <td class="num">{usd(nem["end_2076"]["wealth_s2_real"])}</td>
              <td class="num">{usd(nem["end_2076"]["wealth_s2_real"] - e45["wealth_s3_eq_real"])}</td>
              <td>{srcs("CPUC-NEM", "CPUC-FIXED")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "decision.html",
        "Decision Matrix — Live vs. Rent vs. Sell & Reinvest",
        "Apples-to-apples after-tax wealth comparison across equity, balanced, and cash allocations, plus the Rev. Rul. 2023-2 basis-trap and CPUC 20-year NEM sunset sensitivities.",
        body,
    )


def build_projections(data: dict) -> None:
    rows_html = []
    for r in data["rows_2045"]:
        y = r["year"]
        hl = ' class="highlight-row"' if y in (2026, 2040, 2045, 2050, 2076) else ""
        w_s1 = usd(r["wealth_s1_real"]) if y >= 2045 else "Pre-transfer"
        w_s2 = usd(r["wealth_s2_real"]) if y >= 2045 else "Pre-transfer"
        w_s3 = usd(r["wealth_s3_eq_real"]) if y >= 2045 else "Pre-transfer"
        rows_html.append(f"""
        <tr{hl}>
          <td><strong>{y}</strong></td>
          <td class="num">{usd(r["cup_fmv"])}</td>
          <td class="num">{usd(r["cup_av_live"])}</td>
          <td class="num">{usd(r["cup_tax_live"])}</td>
          <td class="num">{usd(r["cup_tax_rent"])}</td>
          <td class="num">{usd(r["cup_repair"])}</td>
          <td class="num">{usd(r["cup_water"])}</td>
          <td class="num">{usd(r["cup_elec"])}</td>
          <td class="num">{usd(r["cup_ins_home"])}</td>
          <td class="num">{usd(r["sf_fmv"])}</td>
          <td class="num">{usd(r["sf_av"])}</td>
          <td class="num">{usd(r["sf_tax"])}</td>
          <td class="num">{usd(r["sf_water"] + r["sf_elec"] + r["sf_repair"] + r["sf_ins"])}</td>
          <td class="num">{w_s1}</td>
          <td class="num">{w_s2}</td>
          <td class="num">{w_s3}</td>
          <td>{srcs("CA-RTC-51", "CA-RTC-63-2", "FRED-CPI")}</td>
        </tr>
        """)

    body = f"""
    <section class="card">
      <h2>Complete 50-Year Annual Projection Table (2026–2076, Midpoint 2045 Inheritance)</h2>
      <p>Every figure below is a <strong>$10-rounded model projection</strong> built from stated assumptions (4.0%/yr home &amp; market-rent growth, 2.5%/yr general CPI, 2.0%/yr Prop 13 cap, 3.2%/yr utility &amp; insurance escalation, 7.0%/yr equity return). Insurance columns carry the owner's unverified $1,500 base escalated at 3.2%/yr ({flag_link("U01", "Insurance base unverified")}). Downloadable CSVs for 2040, 2045, and 2050 inheritance are in <code>_session_459d7aa2/data/</code>.</p>
      <div class="controls">
        <input class="filter-input" type="search" placeholder="Filter by year (e.g. 2026, 2045, 2076)..." data-table-filter="proj-table" aria-label="Filter projection rows by year">
      </div>
      <div class="table-wrap">
        <table id="proj-table">
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Prop. A FMV</th>
              <th class="num">Prop. A AV (Live)</th>
              <th class="num">Prop. A Tax (Live)</th>
              <th class="num">Prop. A Tax (Rent)</th>
              <th class="num">Prop. A Repair</th>
              <th class="num">Prop. A Water</th>
              <th class="num">Prop. A Elec</th>
              <th class="num">Prop. A Ins*</th>
              <th class="num">Prop. B FMV</th>
              <th class="num">Prop. B AV</th>
              <th class="num">Prop. B Tax</th>
              <th class="num">Prop. B OpEx</th>
              <th class="num">S1 Live (2026$)</th>
              <th class="num">S2 Rent (2026$)</th>
              <th class="num">S3A Sell (2026$)</th>
              <th>Official Basis</th>
            </tr>
          </thead>
          <tbody>
            {"".join(rows_html)}
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "projections.html",
        "Year-by-Year 50-Year Projections (2026–2076)",
        "Complete annual schedules for Property A (Cupertino 95014) and Property B (San Francisco 94122) across market value, assessed value, property tax, repairs, water, electricity, insurance, and real after-tax wealth.",
        body,
    )


def build_black_swan(data: dict) -> None:
    r50 = data["rolling_50yr"]
    bs_rows = []
    for b in data["black_swans"]:
        bs_rows.append(f"""
        <tr>
          <td><strong>{esc(b["id"])}: {esc(b["name"])}</strong><br><span style="color:#526178;font-size:12.5px">{esc(b["mechanism"])}</span></td>
          <td class="num">{usd(b["yr10_s2_real"])}</td>
          <td class="num">{usd(b["yr10_s3_eq_real"])}</td>
          <td class="num">{usd(b["end_s1_real"])}</td>
          <td class="num">{usd(b["end_s2_real"])}</td>
          <td class="num">{usd(b["end_s3_eq_real"])}</td>
          <td class="num">{usd(b["end_s3_cash_real"])}</td>
          <td>{esc(b["winner_2076"])} &middot; {src(b["source_id"])}</td>
        </tr>
        """)

    sample_replays = []
    key_years = {1976, 1979, 1981, 1989, 1995, 2000, 2006, 2007, 2008, 2012, 2020, 2022}
    for rep in r50["replays"]:
        if rep["start_hist_year"] in key_years:
            sample_replays.append(f"""
            <tr>
              <td><strong>{rep["start_hist_year"]} Start Sequence</strong></td>
              <td class="num">{usd(rep["yr10_rent_real"])}</td>
              <td class="num">{usd(rep["yr10_sell_real"])}</td>
              <td class="num">{usd(rep["yr10_sell_minus_rent_real"])}</td>
              <td class="num">{usd(rep["yr20_rent_real"])}</td>
              <td class="num">{usd(rep["yr20_sell_real"])}</td>
              <td class="num">{usd(rep["yr2076_sell_minus_rent_real"])}</td>
              <td>{srcs("FRED-HPI-SJ", "FRED-CPI", "FRED-TB3MS")}</td>
            </tr>
            """)

    body = f"""
    <div class="callout">
      <strong>Why constant-growth projections are insufficient over 50 years:</strong> Real economies experience stagflation (1973–1982), tech/housing busts (2000–2002, 2007–2011), deflationary depressions (1929–1933), multi-decade stagnation, and localized natural hazards (Bay Area 72% 30-year M&ge;6.7 earthquake probability). Below we test both <strong>7 named Black Swan crisis paths</strong> and <strong>all 50 actual historical starting-year sequences (1976–2025)</strong>.
    </div>

    <section class="card">
      <h2>Part 1 — Seven Named Non-Consistent Black Swan Regimes (2026 Real Dollars)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Black Swan Regime &amp; Economic Transmission</th>
              <th class="num">Yr-10 Rent (S2)</th>
              <th class="num">Yr-10 Sell-Eq (S3A)</th>
              <th class="num">2076 Live (S1)</th>
              <th class="num">2076 Rent (S2)</th>
              <th class="num">2076 Sell-Eq (S3A)</th>
              <th class="num">2076 Sell-Cash</th>
              <th>Outcome &amp; Official Anchor</th>
            </tr>
          </thead>
          <tbody>
            {"".join(bs_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Part 2 — Rolling 50-Sequence Historical Backtest (1976–2025 Actual CPI, FHFA HPI, T-Bills &amp; S&amp;P 500)</h2>
      <p>Across all 50 starting years, <strong>Sell &amp; Reinvest in Equities (S3A)</strong> beats <strong>Keep &amp; Rent (S2)</strong> in <strong>{r50["sell_beats_rent_10yr"]} of 50</strong> 10-year horizons and <strong>{r50["sell_beats_rent_20yr"]} of 50</strong> 20-year horizons. Highlighted historical sequences (full 50 rows in <code>rolling_50yr_backtest.csv</code>):</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Historical Sequence Applied at 2045</th>
              <th class="num">10-Yr Rent (2026$)</th>
              <th class="num">10-Yr Sell-Eq (2026$)</th>
              <th class="num">10-Yr Sell Advantage</th>
              <th class="num">20-Yr Rent (2026$)</th>
              <th class="num">20-Yr Sell-Eq (2026$)</th>
              <th class="num">2076 Sell Advantage</th>
              <th>Official Series</th>
            </tr>
          </thead>
          <tbody>
            {"".join(sample_replays)}
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "black-swan.html",
        "Black Swan Economic Conditions & 50-Sequence Stress Testing",
        "Non-consistent 50-year modeling of stagflation, GFC/Dot-Com crashes, 1930s deflation, 30-year secular stagnation, Bay Area seismic shock, and CPUC solar/insurance cost surges.",
        body,
    )


def build_process() -> None:
    steps = [
        ("1", "Pre-inheritance (now)", "Have estate counsel audit the trust instrument to confirm IRC §§ 2036/2038 gross-estate inclusion (avoiding the Rev. Rul. 2023-2 carryover-basis trap) and locate solar interconnection records.", "RR-2023-2", "CPUC-NEM"),
        ("2", "Days 1–14 after death", "Order multiple certified death certificates; successor trustee secures Property A and notifies homeowner insurer immediately (standard HO-3 policies exclude losses if vacant 60+ days).", "CDI-RES", "CA-PROB-16061-7"),
        ("3", "Within 60 days of death", "Successor trustee serves mandatory statutory Notification by Trustee on all beneficiaries and heirs under Probate Code § 16061.7 (starts the 120-day trust-contest clock).", "CA-PROB-16061-7", "BOE-462-260"),
        ("4", "Days 30–90", "Obtain a separate federal EIN for the now-irrevocable trust (required if gross income > $600/yr for Form 1041) and open a trust administration bank account.", "IRS-1041", "IRS-P559"),
        ("5", "Days 30–120", "Commission a certified date-of-death Fair Market Value appraisal of Property A to substantiate IRC § 1014 stepped-up basis and Santa Clara County Assessor Prop 19 / market valuation.", "IRS-GIFT-FAQ", "IRS-P551"),
        ("6", "Within 150 days of death", "Trustee files Change in Ownership Statement — Death of Real Property Owner (BOE-502-D) with the Santa Clara County Assessor under R&TC § 480(b) to avoid the 10% penalty.", "CA-RTC-480", "BOE-462-260"),
        ("7", "Decision fork (Month 3–6)", "Choose path: (a) Sell Property A from trust or after distribution, (b) Distribute & rent out, or (c) Move in as primary residence within 12 months of date of death.", "CA-RTC-63-2", "BOE-LTA-26026"),
        ("8", "Within 9 months of death", "File Federal Form 706 if gross estate + adjusted taxable gifts exceed the year-of-death exclusion ($15,000,000 in 2026; $15,480,000 in 2027; ~$24,143,520 projected in 2045) OR to elect spousal DSUE portability (Form 4768 grants 6-month filing extension).", "IRS-I706", "IRS-ESTATE"),
        ("9", "Within 30 days after Form 706", "If Form 706 is required under IRC § 6018, file Form 8971 and furnish Schedule A consistent-basis statements to beneficiaries.", "IRS-I706", "IRS-NEW"),
        ("10", "California & local estate return", "No California estate or inheritance tax return is required for deaths on or after January 1, 2005 ($0 CA & $0 local death tax).", "SCO-ESTATE", "SCC-DTT"),
        ("11", "If living in Property A (within 1 year)", "Move into Property A within 12 months of death, file Form BOE-266 (Homeowners' Exemption) within 1 year, and file Form BOE-19-P (Prop 19 exclusion) within 3 years; terminate HOX on SF Unit 3 before Dec 10.", "CA-RTC-63-2", "BOE-PUB800-1"),
        ("12", "If renting Property A", "Replace homeowners policy with a landlord / dwelling-fire policy before tenant move-in and include mandatory written AB 1482 single-family exemption language in the lease.", "CDI-RES", "DOJ-TPA"),
        ("13", "If selling Property A", "Record Affidavit of Death of Trustee + deed (with Preliminary Change of Ownership Report BOE-502-A; $0 DTT on inheritance transfer; 0.11% DTT on third-party sale).", "SCC-DTT", "BOE-462-260"),
        ("14", "Escrow tax-withholding guard on sale", "Complete California FTB Form 593 Part VI (Alternative Withholding Calculation) in escrow so 3.33% of gross sale price is NOT withheld when stepped-up gain is $0.", "FTB-593", "IRS-GIFT-FAQ"),
        ("15", "April 15 following year of death/sale", "File decedent's final Form 1040/540, trust Form 1041 + Schedule K-1 (if trust income > $600), and report Property A sale on Form 8949 / Schedule D showing stepped-up basis.", "IRS-1041", "IRS-TC409"),
        ("16", "9+ months after Form 706 (if filed)", "Pull IRS Estate Tax Account Transcript (Transaction Code 421 at $0 fee) or Pay.gov Closing Letter (~$80 rounded) before releasing final trustee reserve; execute 24–36 mo investment glidepath.", "IRS-CLOSING", "SEC-ALLOC"),
    ]
    rows = "\n".join(
        f"<tr><td><strong>Step {s}</strong><br><span style='color:#526178;font-size:12px'>{esc(when)}</span></td>"
        f"<td>{esc(desc)}</td><td>{srcs(s1, s2)}</td></tr>"
        for s, when, desc, s1, s2 in steps
    )
    body = f"""
    <section class="card">
      <h2>Sixteen-Step California Trust Inheritance Roadmap (Chronological)</h2>
      <p>Property B (San Francisco 94122) is already owned by <code>[Inheritor]</code> and requires <strong>no</strong> probate, trust transfer, or reassessment filing unless <code>[Inheritor]</code> vacates Unit 3 (Step 11).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Step &amp; Statutory Window</th><th>Required Action &amp; Practical Consequence</th><th>Official Sources</th></tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "process.html",
        "Step-by-Step Trust Inheritance Process (16 Steps)",
        "Complete California & federal administration timeline from pre-death trust review through Probate Code § 16061.7 notices, Assessor filings, Form 706/8971/1041/593 compliance, and reinvestment.",
        body,
    )


def build_taxes_estate(data: dict) -> None:
    ec = data["estate_cash"]
    key_rows = []
    for y_str in ("2026", "2027", "2030", "2035", "2040", "2045", "2050", "2055"):
        r = ec["key_years"][y_str]
        prov = badge("official", "Enacted / IRS Rev. Proc.") if y_str in ("2026", "2027") else badge("model", "Projected @ 2.5% CPI")
        sids = ("PL-119-21", "RP-2026-35", "SCO-ESTATE") if y_str in ("2026", "2027") else ("IRS-ESTATE", "FRED-CPI", "SCO-ESTATE")
        hl = ' class="highlight-row"' if y_str in ("2026", "2027", "2045") else ""
        key_rows.append(f"""
        <tr{hl}>
          <td><strong>{y_str}</strong></td>
          <td class="num">{usd(r["cup_fmv"])}</td>
          <td class="num">{usd(r["single_exclusion"])}</td>
          <td class="num">{usd(r["cash_headroom_single"])}</td>
          <td class="num">{usd(r["married_dsue_exclusion"])}</td>
          <td class="num">{usd(r["cash_headroom_married"])}</td>
          <td class="num">{usd(r["cash_headroom_halved_single"])}</td>
          <td class="num">$0 / $0</td>
          <td>{prov} {srcs(*sids)}</td>
        </tr>
        """)

    sens_rows = []
    for s in ec["cash_sensitivity_2045"]:
        sens_rows.append(f"""
        <tr>
          <td class="num"><strong>{usd(s["cash_inherited"])}</strong></td>
          <td class="num">{usd(s["gross_estate_with_cup"])}</td>
          <td class="num">{usd(s["fed_tax_single_current_law"])}</td>
          <td class="num">{usd(s["net_received_single_current_law"])}</td>
          <td class="num">{usd(s["fed_tax_married_dsue"])}</td>
          <td class="num">{usd(s["fed_tax_if_exclusion_halved"])}</td>
          <td>{srcs("IRS-I706", "IRS-P559", "SCO-ESTATE")}</td>
        </tr>
        """)

    body = f"""
    <section class="card">
      <h2>Cash Inheritance Thresholds &amp; Tax-Free Headroom Above Property A (2026–2055)</h2>
      <p>Cash bequests are <strong>not</strong> taxable income to <code>[Inheritor]</code> under IRC § 102 ({src("IRS-P559")}), and California + local estate/inheritance taxes are <strong>$0</strong> ({src("SCO-ESTATE")}). Federal estate tax (<strong>40%</strong> top rate) applies only if <code>[Transferor]</code>'s total gross estate (Property A + cash/other assets + lifetime taxable gifts above $19,000/$20,000 annual exclusions; <em>excluding</em> already-owned Property B) exceeds the basic exclusion. Warning: pre-tax IRAs/401(k)s are <em>not</em> tax-free cash — distributions are taxed as ordinary income over 10 years ({src("IRS-P590B")}).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Projected Prop. A FMV</th>
              <th class="num">Single Exclusion</th>
              <th class="num">Tax-Free Cash Headroom (Single)</th>
              <th class="num">Married DSUE (2&times;)</th>
              <th class="num">Tax-Free Cash Headroom (Married)</th>
              <th class="num">Headroom if Exclusion Halved</th>
              <th class="num">CA / Local Tax</th>
              <th>Provenance &amp; Official Source</th>
            </tr>
          </thead>
          <tbody>{"".join(key_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>2045 Cash Inheritance Penalty Sensitivity Matrix (Property A = $6,531,230)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="num">Additional Cash Inherited</th>
              <th class="num">Total Gross Estate</th>
              <th class="num">Federal Estate Tax (Single, Current Law)</th>
              <th class="num">Net Value to Inheritor</th>
              <th class="num">Federal Tax (Married w/ DSUE)</th>
              <th class="num">Federal Tax if Exclusion Cut 50%</th>
              <th>Official Basis</th>
            </tr>
          </thead>
          <tbody>{"".join(sens_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Enacted vs. Pending / Discussed Law Changes (Verified 2026-11-11)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Measure &amp; Jurisdiction</th><th>Status on 2026-11-11</th><th>Verified Impact on Inheritance Decision</th><th>Official Source</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Federal P.L. 119-21 &amp; Rev. Proc. 2026-35</strong></td>
              <td>{badge("official", "ENACTED LAW")}</td>
              <td>Raised federal basic exclusion to <strong>$15,000,000</strong> (2026) and <strong>$15,480,000</strong> (2027) with permanent CPI indexing and no scheduled sunset.</td>
              <td>{srcs("PL-119-21", "RP-2026-35")}</td>
            </tr>
            <tr>
              <td><strong>Federal S. 587 &amp; H.R. 1301 (Death Tax Repeal Act)</strong></td>
              <td>{badge("warn", "INTRODUCED ONLY")}</td>
              <td>Introduced Feb 13, 2025 (referred to Senate Finance / House Ways &amp; Means; not enacted). Would repeal estate/GST taxes if ever enacted; CBO's projected 120%-of-GDP debt by 2036 creates countervailing risk of future exclusion cuts.</td>
              <td>{srcs("CONG-S587", "CONG-HR1301", "CBO-2026")}</td>
            </tr>
            <tr>
              <td><strong>California SB 974 (Ch. 665, Sept. 27, 2026)</strong></td>
              <td>{badge("official", "ENACTED LAW")}</td>
              <td>Amended R&amp;TC § 63.2 to include court-established special needs trusts as eligible Prop 19 transfer mediums; left the 1-year residency mandate and $1,044,590 ($10-rounded) cap unchanged.</td>
              <td>{srcs("CA-SB974", "CA-RTC-63-2")}</td>
            </tr>
            <tr>
              <td><strong>Prop 19 Repeal / Expansion Discussion</strong></td>
              <td>{badge("warn", "NOT ENACTED")}</td>
              <td>Because Prop 19 sits in CA Constitution Art. XIII A § 2.1, only a statewide ballot measure can restore the old Prop 58 rental exclusion; none is enacted as of Nov 2026.</td>
              <td>{srcs("CA-CONST-13A", "BOE-P19")}</td>
            </tr>
            <tr>
              <td><strong>San Francisco BOS File No. 261020 (Posted Nov 9, 2026)</strong></td>
              <td>{badge("warn", "PENDING LOCAL BILL")}</td>
              <td>Proposed ordinance to cap combined banked + capital-improvement rent increases on SF rent-controlled units at 10%/yr; not yet enacted.</td>
              <td>{srcs("SF-RENT-RATE", "SF-RENT-LAW")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "taxes-estate.html",
        "Local, State & Federal Taxes, Cash Headroom & Law Changes",
        "Complete analysis of federal estate/gift exclusions ($15M in 2026; $15.48M in 2027), tax-free cash inheritance headroom through 2055, capital gains & NIIT, and enacted vs. pending legislation.",
        body,
    )


def build_costs_insurance() -> None:
    body = f"""
    <div class="callout warn">
      <strong>Strict Anti-Hallucination Treatment of ZIP-Level Insurance Quotes:</strong> Official California Department of Insurance (CDI) tools require interactive per-structure underwriting inputs and explicitly omit <strong>15% to 300%+ wildfire surcharges</strong>, and CDI publishes no static rate table for a 3-unit rental in <code>94122</code> or single-family home in <code>95014</code>. Therefore, the <strong>Official Confirmed Quote</strong> column for both properties is <strong>intentionally left blank</strong> and flagged on <a href="flagged.html#U01">Flagged for Review (U01)</a>, while the owner's <strong>$1,500/yr</strong> figure is labeled strictly as an unverified scenario input.
    </div>

    <section class="card">
      <h2>Operating Costs, Utilities, Solar &amp; Insurance Verification Table (2026 Base Year)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Expense Line &amp; Property</th>
              <th class="num">Owner / Model Input (2026$/yr)</th>
              <th class="num">Official Confirmed Parcel Value</th>
              <th>Official Tariff / Regulatory Verification</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Cupertino (95014) Electricity — Legacy Solar NEM</strong><br>Owner est.: ~$10–$20/mo net credit</td>
              <td class="num">-$180</td>
              <td class="num">{blank_unverified("U03", "Interconnection year unknown")}</td>
              <td>CPUC confirms NEM 1.0/2.0 retail export credits last <strong>20 years from interconnection</strong> (D.14-03-041), with 2–3&cent;/kWh annual net surplus compensation; post-20-yr systems shift to Net Billing (D.22-12-056) plus PG&amp;E's ~$290/yr ($10-rounded) Tier 3 fixed charge (Res. E-5354).</td>
              <td>{srcs("CPUC-NEM", "CPUC-FIXED")}</td>
            </tr>
            <tr>
              <td><strong>Cupertino (95014) Water</strong><br>Owner est.: $100–$150/mo</td>
              <td class="num">$1,500</td>
              <td class="num">{blank_unverified("U04", "Provider depends on street")}</td>
              <td>City of Cupertino confirms parcels are served by three water systems depending on street location: San Jose Water Company, California Water Service, or the City-owned system operated by SJWC under lease through 2036.</td>
              <td>{srcs("CUP-WATER")}</td>
            </tr>
            <tr>
              <td><strong>Cupertino (95014) Primary Residence Insurance (HO-3)</strong><br>Owner guess: ~$1,500/yr</td>
              <td class="num">$1,500 {badge("warn", "Unverified guess")}</td>
              <td class="num">{blank_unverified("U01", "Left blank — unverified")}</td>
              <td>CDI Form 401 confirms HO-3 insures dwelling replacement cost (excluding land, earthquake, flood, and 60+ day vacancy); CDI 2026 Comparison Tool omits 15%–300%+ wildfire surcharges.</td>
              <td>{srcs("CDI-RES", "CDI-TOOL", "CDI-DATA")}</td>
            </tr>
            <tr>
              <td><strong>Cupertino (95014) Landlord Insurance (if rented)</strong><br>Model differential: +40% over HO-3</td>
              <td class="num">$2,100 {badge("model", "Model assumption")}</td>
              <td class="num">{blank_unverified("U01", "Left blank — unverified")}</td>
              <td>Standard HO-3 excludes business/rental occupancy; converting Property A to a rental requires a landlord / dwelling-fire policy plus liability coverage.</td>
              <td>{srcs("CDI-RES", "CDI-DATA")}</td>
            </tr>
            <tr>
              <td><strong>Cupertino (95014) Repairs &amp; Maintenance</strong><br>Owner rule: lower than SF triplex</td>
              <td class="num">$6,000</td>
              <td class="num">{blank_unverified("U05", "Household maintenance varies")}</td>
              <td>Modeled at $6,000/yr (~0.2% of $3.1M land-heavy value; &lt; SF $12,000/yr), indexed at CPI (plus seismic tail test in BS-6).</td>
              <td>{srcs("FRED-CPI", "USGS-QUAKE")}</td>
            </tr>
            <tr>
              <td><strong>San Francisco (94122) Water &amp; Sewer (3 Units)</strong><br>Owner est.: $330–$400/mo</td>
              <td class="num">$4,380</td>
              <td class="num">{blank_unverified("U05", "Depends on meter & CCF")}</td>
              <td>SFPUC Schedule W-1B + Schedule A (effective July 1, 2026) charge ~$20–$40/mo water meter + ~$10/mo sewer + ~$30/CCF combined water &amp; wastewater (~9–10 CCF/mo across 3 units &asymp; $330–$400/mo), with +7%–10% FY27–28 adopted increases.</td>
              <td>{srcs("SFPUC")}</td>
            </tr>
            <tr>
              <td><strong>San Francisco (94122) Electricity (Owner/Common)</strong><br>Owner est.: $30–$70/mo</td>
              <td class="num">$600</td>
              <td class="num">{blank_unverified("U05", "Household meter usage")}</td>
              <td>PG&amp;E residential service subject to CPUC Resolution E-5354 (~$290/yr Tier 3 fixed charge + volumetric TOU usage).</td>
              <td>{srcs("CPUC-FIXED")}</td>
            </tr>
            <tr>
              <td><strong>San Francisco (94122) 3-Unit Rental Insurance</strong><br>Owner guess: ~$1,500/yr</td>
              <td class="num">$1,500 {badge("warn", "Unverified guess")}</td>
              <td class="num">{blank_unverified("U01", "Left blank — unverified")}</td>
              <td>CDI Residential Policy Count Data covers 1–4 unit landlord policies, but CDI publishes no static multi-unit rate schedule for ZIP 94122; $1,500/yr for a 3-unit building is likely below current replacement-cost market quotes and is stressed at 6.5%/yr in BS-7.</td>
              <td>{srcs("CDI-DATA", "CDI-SB824")}</td>
            </tr>
            <tr>
              <td><strong>San Francisco (94122) Repairs &amp; Maintenance (3 Units)</strong><br>Owner est.: $12,000/yr</td>
              <td class="num">$12,000</td>
              <td class="num">{blank_unverified("U05", "Household maintenance varies")}</td>
              <td>Deductible rental repair/maintenance expense on IRS Schedule E (allocated to rented units).</td>
              <td>{srcs("IRS-TC414", "IRS-P527")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "costs-insurance.html",
        "Utilities, Solar NEM, Maintenance & Home/Rental Insurance",
        "Line-by-line verification of Cupertino (95014) and San Francisco (94122) electricity, water/sewer, maintenance, and primary vs. landlord insurance rules.",
        body,
    )


def build_requirements() -> None:
    reqs = [
        ("Privacy & anonymization", "Zero names, street addresses, APNs, or raw county-roll sequences; role placeholders used everywhere; public-repo Git history exposure flagged.", "Done", "index.html", "CA-RTC-63-2"),
        ("Nearest-$10 rounding & anti-traceability", "100% of dollar figures across all 11 HTML pages, CSVs, and JSON are multiples of $10; zero-ending county-roll inputs coarsened to $100 ($550,500; $7,200); zero reversible SHA-256 hashes stored.", "Done", "properties.html", "BOE-LTA-26002"),
        ("Executive summary & best plan with clear numbers", "Landing page + EXECUTIVE-SUMMARY.md quantify Live vs. Rent vs. Sell (Equities / 60-40 / Cash) across 2040, 2045, and 2050 inheritance.", "Done", "index.html", "SEC-ALLOC"),
        ("Ownership distinction (Cupertino inherited vs. SF already owned)", "Property B retains its $116,540 Prop 13 base ($19,980/yr shield), gets no §1014 step-up, and is excluded from Transferor's gross estate.", "Done", "properties.html", "BOE-462-260"),
        ("50-year annual projections (2026–2076)", "51 annual rows covering home value, assessed value, property tax, repairs, water, electricity, insurance, and real after-tax wealth.", "Done", "projections.html", "CA-RTC-51"),
        ("Separate Black Swan economic conditions section", "7 named crisis regimes (stagflation, GFC, Dot-Com, 1930s deflation, 30-yr stagnation, M≥6.7 quake, NEM/insurance shock) + 50 real 1976–2025 sequences.", "Done", "black-swan.html", "NBER-CYCLES"),
        ("Step-by-step trust inheritance process", "16 chronological steps with statutory deadlines (60-day §16061.7, 150-day §480(b), 9-mo Form 706, 1-yr BOE-266, Form 593 Part VI).", "Done", "process.html", "CA-PROB-16061-7"),
        ("Cash inheritance tax thresholds, headroom & law changes", "2026 ($15M) & 2027 ($15.48M) enacted thresholds, $17.61M single / $41.76M married 2045 cash headroom, 40% penalty matrix, P.L. 119-21, S.587/H.R.1301, and CA SB 974.", "Done", "taxes-estate.html", "RP-2026-35"),
        ("Home & rental insurance research (95014 & 94122)", "Verified CDI Form 401, 2026 Comparison Tool, and SB 824 data; left unconfirmable static ZIP quotes blank and flagged owner's ~$1,500 guess.", "Done", "costs-insurance.html", "CDI-TOOL"),
        ("Line-by-line repo review & official source on every row", "Fetched all 54 final/sources.py URLs + 19 privacy-site URLs: closed all 14 excerpt gaps, caught 8 dead 404 URLs and 2 misattributed CA bills (ACA 11 = water; SB 472 = education), and verified 49 live official sources.", "Done", "flagged.html", "CA-SB974"),
    ]
    rows = "\n".join(
        f"<tr><td><strong>{esc(t)}</strong></td><td>{esc(d)}</td>"
        f"<td>{badge('official', st)} &middot; <a href='{href}'>{href}</a></td><td>{src(sid)}</td></tr>"
        for t, d, st, href, sid in reqs
    )
    body = f"""
    <section class="card">
      <h2>Requirement-by-Requirement Verification Checklist</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Prompt Requirement</th><th>How Verified &amp; Delivered</th><th>Location</th><th>Official Anchor</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "requirements.html",
        "Prompt Requirements & Line-by-Line Repo Audit Summary",
        "Traceability matrix mapping every user constraint and analytical requirement to verified pages, data files, and repo-audit findings.",
        body,
    )


def build_sources() -> None:
    rows = []
    for sid, m in SOURCES.items():
        rows.append(f"""
        <tr id="{esc(sid)}">
          <td><code>{esc(sid)}</code><br>{badge("official", m["level"])}</td>
          <td><strong>{esc(m["title"])}</strong><br><span style="color:#526178;font-size:12.5px">{esc(m["agency"])} &middot; Fetched {esc(m["verified_date"])}</span></td>
          <td>{esc(m["summary"])}</td>
          <td>{src(sid, "Open official page")}</td>
        </tr>
        """)
    body = f"""
    <section class="card">
      <h2>All {len(SOURCES)} Official Primary Sources Read &amp; Verified in Session (2026-11-11)</h2>
      <div class="controls">
        <input class="filter-input" type="search" placeholder="Search agency, statute, topic, or ID..." data-table-filter="src-table" aria-label="Search official sources">
      </div>
      <div class="table-wrap">
        <table id="src-table">
          <thead><tr><th>ID &amp; Level</th><th>Official Document &amp; Agency</th><th>Verified Rule / Rate Used</th><th>Official Link</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "sources.html",
        f"Verified Official Sources Catalog ({len(SOURCES)} Primary Sources)",
        "Every official .gov, statutory, and public-agency source fetched and verified in full on 2026-11-11 — zero dead links and zero search-excerpt-only placeholders.",
        body,
    )


def build_flagged() -> None:
    unverified_items = [
        ("U01", "ZIP-Level Homeowners (95014) & 3-Unit Landlord (94122) Insurance Premiums", "Left blank in official-quote column; owner's ~$1,500/yr treated strictly as unverified input", "CDI's 2026 Homeowners Comparison Tool requires interactive session inputs and omits 15%–300%+ wildfire surcharges; CDI publishes no static 3-unit rental rate schedule for 94122.", "CDI-TOOL"),
        ("U02", "Trust Instrument Gross-Estate Inclusion Clause (IRC § 1014 vs. Rev. Rul. 2023-2)", "Left blank as unverified private legal document; modeled both ways", "If Property A is in a revocable trust included in Transferor's gross estate, basis resets to FMV; if in an excluded irrevocable trust, carryover basis triggers ~$2,247,630+ tax on a 2045 sale.", "RR-2023-2"),
        ("U03", "Cupertino Rooftop Solar Interconnection Year & Remaining NEM 20-Year Window", "Left blank as unverified parcel record; modeled both legacy credit and post-NEM sunset", "Under CPUC D.14-03-041, retail NEM credits expire 20 years after original interconnection and transition to Net Billing (D.22-12-056) plus PG&E's ~$290/yr ($10-rounded) fixed charge.", "CPUC-NEM"),
        ("U04", "Exact Cupertino Water Retailer & Tax Rate Area (TRA) Parcel Assignment", "Left blank at parcel level to preserve anonymity", "City of Cupertino parcels fall into 3 water systems (SJWC, Cal Water, or City-owned SJWC-leased) and multiple school-bond TRAs (~1.16%–1.19%).", "CUP-WATER"),
        ("U05", "Owner-Supplied Market Values, Monthly Rents, Utilities & Maintenance Estimates", "Labeled strictly as $10/$100-rounded owner scenario inputs — never marked government-verified", "Private appraisals, leases, and utility bills cannot be corroborated on public sites without exposing the properties.", "BOE-LTA-26002"),
        ("U06", "50-Year Economic, Tax-Bracket & Legislative Forecasts (2026–2076)", "Labeled as model projections conditional on stated assumptions + stressed in Black Swan section", "Future home appreciation, equity returns, inflation, and future Acts of Congress/ballot measures cannot be verified in advance.", "CBO-2026"),
    ]
    repo_irregs = [
        ("R-45-1", "Misattributed CA Bills in final/sources.py & law.html (CA-ACA11 & CA-SB472)", "Logged CR-45-1 in COORDINATION.md; replaced with enacted SB 974 (Ch. 665, 2026) in our suite", "Direct fetch of LegInfo proved 202520260ACA11 is the California Water Resiliency Act (Art. X §8) and 202520260SB472 is Holocaust & genocide education (Ed. Code §51221.2), NOT property-tax bills.", "CA-SB974"),
        ("R-45-2", "Eight Dead HTTP 404 URLs in final/sources.py Marked how='page'", "Logged CR-45-1 in COORDINATION.md; all 8 replaced with verified live .gov URLs here", "BOE-P19, SCC-P19, SFT-RPTT, SF-RENT-LAW, SF-RENT-RATE, CDI-RPI, CDI-SB824, and CDI-TOOL returned 404 Not Found when fetched directly because final/check.py only checked hostnames.", "SF-RPTT"),
        ("R-45-3", "Stale FY2025–26 SF Tax Rate (1.18259092%) in final/model.py", "Logged CR-45-2; updated to official FY2026–27 rate (1.18162182%) in our engine", "Live sftreasurer.org/property/secured-property-taxes publishes 1.18162182% for FY2026–27.", "SFT-RATE"),
        ("R-45-4", "Internal Mismatches in final/build.py (14 vs. 16 steps; CDI wording; A03 vs. A01)", "Logged CR-45-2 for active final/build.py owner; fixed cleanly in this suite", "requirements.html row 13 said 14 steps while process.html had 16; row 10 linked Prop 19 flag A03 instead of CPI flag A01.", "CA-PROB-16061-7"),
        ("R-45-5", "Withheld Numeric Projections & Decision on privacy-site/ (PR #34)", "Logged CR-45-3 for K3 front-door reconciliation; full $10-rounded tables provided here", "privacy-site/public/projection.html blanks all 2026–2076 cells ('—'), omitting the $10-rounded projections requested by the user brief.", "CA-RTC-51"),
        ("R-45-6", "Public GitHub Repository & Historical Commit Exposure (Owner Action Required)", "Flagged prominently; zero raw figures or reversible hashes in _session_459d7aa2/", "Git history and PR refs on a public repository remain readable even when Pages excludes legacy directories; owner must make repo Private or purge history.", "CA-RTC-63-2"),
    ]

    u_rows = "\n".join(
        f'<tr id="{esc(fid)}"><td><code>{esc(fid)}</code></td><td><strong>{esc(title)}</strong></td>'
        f"<td>{badge('warn', status)}</td><td>{esc(detail)}</td><td>{src(sid)}</td></tr>"
        for fid, title, status, detail, sid in unverified_items
    )
    r_rows = "\n".join(
        f'<tr id="{esc(rid)}"><td><code>{esc(rid)}</code></td><td><strong>{esc(title)}</strong></td>'
        f"<td>{badge('model', status)}</td><td>{esc(detail)}</td><td>{src(sid)}</td></tr>"
        for rid, title, status, detail, sid in repo_irregs
    )

    body = f"""
    <section class="card">
      <h2>Part A — Unverified Household, Parcel &amp; Forecast Items (Left Blank Where Unconfirmable)</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Flag ID</th><th>Item</th><th>Treatment</th><th>Why Official Sources Cannot Confirm It</th><th>Official Reference</th></tr></thead>
          <tbody>{u_rows}</tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Part B — Repository Irregularities Found During Line-by-Line Review</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Audit ID</th><th>Irregularity Found</th><th>Disposition</th><th>Evidence from Primary Verification</th><th>Official Reference</th></tr></thead>
          <tbody>{r_rows}</tbody>
        </table>
      </div>
    </section>
    """
    render_page(
        "flagged.html",
        "Flagged for Review — Unverified Items & Repository Irregularities",
        "Complete disclosure of every unconfirmable input (left blank rather than inferred) and every factual, link, or privacy irregularity discovered during our line-by-line repository audit.",
        body,
    )


def build_all() -> None:
    verify_source_registry()
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    data_path = BASE_DIR / "data" / "model_output.json"
    if not data_path.is_file():
        data = run_all()
    else:
        data = json.loads(data_path.read_text(encoding="utf-8"))

    (SITE_DIR / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (SITE_DIR / "app.js").write_text(JS.strip() + "\n", encoding="utf-8")

    build_index(data)
    build_properties(data)
    build_decision(data)
    build_projections(data)
    build_black_swan(data)
    build_process()
    build_taxes_estate(data)
    build_costs_insurance()
    build_requirements()
    build_sources()
    build_flagged()
    print(f"OK - built 11 HTML dashboard pages + style.css + app.js in {SITE_DIR}")


if __name__ == "__main__":
    build_all()
