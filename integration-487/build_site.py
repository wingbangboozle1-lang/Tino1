#!/usr/bin/env python3
"""Build the self-contained, privacy-safe static Pages site.

Default output is a staging directory. At integration, pass --output . from
repository root. All numerical property inputs are synthetic; no network or
interactive input is required. Python's standard library is sufficient.
"""
from __future__ import annotations

import argparse
import csv
import html
import math
import shutil
from pathlib import Path

import model as m
from sources import SOURCES

HERE = Path(__file__).resolve().parent

PAGES = [
    ('index.html', 'Overview', '◫'),
    ('decisions.html', 'Decision paths', '↗'),
    ('projections.html', 'Year-by-year', '▦'),
    ('properties.html', 'Property & assessment', '⌂'),
    ('costs.html', 'Costs & rental income', '◇'),
    ('taxes.html', 'Estate & tax', '§'),
    ('steps.html', 'Trust checklist', '✓'),
    ('scenarios.html', 'Stress tests', '⌁'),
    ('methodology.html', 'Assumptions & method', '≋'),
    ('sources.html', 'Official sources', '↗'),
    ('flagged.html', 'Flagged for review', '!'),
]


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def money(value: float) -> str:
    n = m.round10(value)
    return ('−' if n < 0 else '') + '${:,.0f}'.format(abs(n))


def source(key: str, label: str = 'Official source') -> str:
    url, title, _ = SOURCES[key]
    return (f'<a class="source-link" href="{e(url)}" aria-label="{e(label)} — {e(title)}">'
            f'{e(label)} <span aria-hidden="true">↗</span></a>')


def table(headers: list[str], rows: list[tuple[list[str], str]], caption: str) -> str:
    heads = ''.join(f'<th scope="col">{e(h)}</th>' for h in [*headers, 'Source'])
    body = []
    for cells, key in rows:
        assert len(cells) == len(headers), (caption, cells)
        row = [f'<th scope="row">{cells[0]}</th>']
        for cell in cells[1:]:
            cls = ' class="num"' if cell.startswith(('$', '−$')) else ''
            row.append(f'<td{cls}>{cell}</td>')
        row.append(f'<td>{source(key)}</td>')
        body.append('<tr>' + ''.join(row) + '</tr>')
    return (f'<div class="table-wrap" tabindex="0" role="region" aria-label="{e(caption)}">'
            f'<table><caption>{e(caption)}</caption><thead><tr>{heads}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def header(kicker: str, title: str, description: str) -> str:
    return (f'<header class="page-header"><div class="eyebrow">{e(kicker)}</div>'
            f'<h1>{e(title)}</h1><p>{description}</p></header>')


def notice(message: str, warn: bool = False) -> str:
    return f'<div class="notice{" warn" if warn else ""}"><span class="notice-icon" aria-hidden="true">{"!" if warn else "i"}</span><div>{message}</div></div>'


def section(title: str, body: str, eyebrow: str = '', extra: str = '') -> str:
    eyebrow_html = f'<div class="eyebrow">{e(eyebrow)}</div>' if eyebrow else ''
    return (f'<section class="section"><div class="section-head"><div>'
            f'{eyebrow_html}<h2>{e(title)}</h2></div>{extra}</div>{body}</section>')


def page(filename: str, title: str, content: str) -> str:
    nav_items = []
    for name, label, icon in PAGES:
        current = ' aria-current="page"' if filename == name else ''
        nav_items.append(f'<a class="nav-link" href="{name}"{current}>'
                         f'<span class="nav-icon" aria-hidden="true">{e(icon)}</span><span>{e(label)}</span></a>')
    nav = ''.join(nav_items)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · Stewardship</title><meta name="description" content="A synthetic, source-linked California inheritance decision guide.">
<link rel="stylesheet" href="assets/style.css"></head><body>
<a class="skip" href="#main">Skip to main content</a>
<div class="app"><aside class="sidebar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 18V7l8-4 8 4v11l-8 4-8-4Z" stroke="currentColor" stroke-width="1.6"/><path d="m8 16 4-7 4 7M9.2 14h5.6" stroke="currentColor" stroke-width="1.5"/></svg></span><span><strong>stewardship<span style="color:#6d9b78">.</span></strong><small>Inheritance field guide</small></span></a>
<div class="nav-title">Explore the guide</div><nav class="nav-list" aria-label="Main navigation">{nav}</nav><div class="nav-mobile-hint" aria-hidden="true">More sections →</div>
<div class="sidebar-foot">Built for informed decisions.<br>Public guide · synthetic examples</div></aside>
<main class="main" id="main"><div class="main-inner"><div class="topline"><span>Inheritance field guide <span aria-hidden="true">/</span> <span class="crumb-current">{e(title)}</span></span><span class="topline-date"><span class="live-dot"></span>Sources reviewed 11 Nov 2026</span></div>
{content}
<footer><span>Stewardship · A public, synthetic decision framework.</span><span>Not legal, tax or investment advice · <a href="flagged.html">Limitations &amp; privacy</a></span></footer>
</div></main></div></body></html>'''


def overview_chart(data: dict[str, list[dict[str, float]]]) -> str:
    width, height = 640, 245
    left, right, top, bottom = 78, 22, 15, 34
    values = [r['position'] for v in data.values() for r in v]
    ymax = math.ceil(max(values) / 20_000_000) * 20_000_000
    ymin = min(0, math.floor(min(values) / 20_000_000) * 20_000_000)
    def x(i: int) -> float:
        return left + i / 49 * (width - left - right)
    def y(value: float) -> float:
        return height - bottom - (value - ymin) / (ymax - ymin) * (height - top - bottom)
    parts = []
    for n in range(4):
        val = ymin + n * (ymax - ymin) / 3
        yy = y(val)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#e7eee7"/>')
        parts.append(f'<text x="{left-9}" y="{yy+4:.1f}" text-anchor="end" fill="#536c60" font-size="10">{e(money(val))}</text>')
    for i in (0, 9, 19, 29, 39, 49):
        parts.append(f'<text x="{x(i):.1f}" y="{height-8}" text-anchor="middle" fill="#536c60" font-size="10">{2045+i}</text>')
    colors = {'live': '#2d856d', 'rent': '#b4782a', 'sell': '#7158af'}
    for choice in m.STRATEGIES:
        coords = ' '.join(f'{"M" if i == 0 else "L"}{x(i):.1f},{y(row["position"]):.1f}' for i, row in enumerate(data[choice]))
        parts.append(f'<path d="{coords}" fill="none" stroke="{colors[choice]}" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>')
    return (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Synthetic modeled position from 2045 through 2094. The full values appear in the year-by-year table.">'
            + ''.join(parts) + '</svg>')


def overview() -> str:
    base = m.simulate(m.SCENARIOS[0])
    cards = []
    for choice, marker, label in [('live', '', 'Live in inherited home'), ('rent', ' rent', 'Rent inherited home'), ('sell', ' sell', 'Sell & invest')]:
        cards.append(f'<div class="card metric-card"><div class="metric-top"><span class="dot{marker}"></span>{label}</div>'
                     f'<strong class="metric-number">{money(base[choice][9]["position"])}</strong>'
                     f'<div class="metric-caption">Illustrative position after 10 years</div></div>')
    chart = overview_chart(base)
    return f'''
<section class="hero" aria-labelledby="hero-title"><div><div class="eyebrow">A clearer view of what comes next</div>
<h1 id="hero-title">One inheritance.<br><em>Three possible paths.</em></h1>
<p>A practical framework for comparing a future trust inheritance with the home already owned—across property taxes, rental income, investing and uncertainty.</p>
<div class="hero-actions"><a class="button button-light" href="decisions.html">Explore the options <span aria-hidden="true">↗</span></a><a class="button button-ghost" href="steps.html">See the checklist <span aria-hidden="true">→</span></a></div></div>
<aside class="hero-note"><div class="note-label">Planning window</div><div class="window">2040 — 2050</div><p>One inherited home. One already-owned home. A longer view of the decisions between them.</p><div class="hero-stat-line"><span><strong>3</strong> choices</span><span><strong>50</strong> years modeled</span></div></aside></section>
{notice('<strong>Public and intentionally synthetic.</strong> Every property amount in this guide is invented to protect privacy; none is a valuation, quote or forecast. <a href="methodology.html">See the assumptions</a>.')}
<section class="section"><div class="section-head"><div><div class="eyebrow">The comparison · hypothetical transfer in 2045</div><h2>A starting point, not an answer</h2><p>Year-end 2054 position in the steady illustrative path.</p></div><a class="text-link" href="projections.html">View every year →</a></div><div class="cards">{''.join(cards)}</div>
<p class="table-note">Position includes the retained, already-owned home at market value (not sold or taxed on sale), an assumed investment/funding account, and the inherited home’s hypothetical after-tax sale proceeds if retained. It is not a complete household net worth.</p></section>
<section class="section split"><div class="panel"><div class="chart-head"><div><div class="eyebrow">50-year base path · nominal dollars</div><h2>How the paths can diverge</h2><p>Compounding assumptions, not predicted outcomes.</p></div><div class="legend"><span><i class="dot"></i> Live</span><span><i class="dot rent"></i> Rent</span><span><i class="dot sell"></i> Sell</span></div></div><figure class="chart">{chart}<figcaption>Figures are synthetic. Assumes a 2045 transfer. See the <a href="projections.html">data table</a>, <a href="methodology.html">methodology</a> and {source('fhfa', 'FHFA background')}.</figcaption></figure></div>
<div class="panel"><div class="eyebrow">Before the numbers</div><h2>What matters most</h2><ul class="insight-list"><li><strong>The other home is already owned.</strong> Inheriting one property does not by itself trigger reassessment of the separately owned home. {source('sf_assessment', 'Assessment rules')}</li><li><strong>Two rents stay in every path.</strong> The third unit is assumed available for the owner; the model does not displace the existing tenants. Coverage and vacancy rules remain unverified.</li><li><strong>Relief and basis are conditional.</strong> Occupancy, relationship, trust terms and estate inclusion can change the result. {source('prop19', 'BOE guidance')}</li></ul><a class="small-link" href="flagged.html">See what needs review →</a></div></section>
<section class="section"><div class="section-head"><div><div class="eyebrow">Explore by decision</div><h2>Start where you need to</h2></div></div><div class="cards"><article class="card path-card"><span class="path-icon" aria-hidden="true">⌂</span><div class="path-number">01 / property</div><h3>Understand assessments</h3><p>See the difference between market value, assessed value and the family-home exclusion.</p><a href="properties.html">Property detail →</a></article><article class="card path-card"><span class="path-icon" aria-hidden="true">⌁</span><div class="path-number">02 / resilience</div><h3>Test the uncomfortable</h3><p>Explore market declines, rising costs, disaster and changes to assumed tax treatment.</p><a href="scenarios.html">Stress tests →</a></article><article class="card path-card"><span class="path-icon" aria-hidden="true">✓</span><div class="path-number">03 / action</div><h3>Know the next steps</h3><p>A sourced sequence of trust, assessment, tax and practical tasks.</p><a href="steps.html">Trust checklist →</a></article></div></section>'''


def decisions() -> str:
    base = m.simulate(m.SCENARIOS[0])
    sale = base['sell'][0]
    low = m.simulate(next(s for s in m.SCENARIOS if s.key == 'lower_basis'))['sell'][0]
    sale_rows = [
        (['Transfer-date sale price', money(sale['event_sale_price']), money(low['event_sale_price'])], 'basis'),
        (['Selling costs, 5% assumed', money(sale['event_selling_cost']), money(low['event_selling_cost'])], 'scc_transfer'),
        (['Income-tax basis assumed', money(sale['a_basis']), money(low['a_basis'])], 'basis_ruling'),
        (['Taxable gain after selling costs', money(sale['event_gain']), money(low['event_gain'])], 'basis'),
        (['Illustrative gain tax at 30%', money(sale['event_tax']), money(low['event_tax'])], 'ca_capital'),
        (['Net invested at the beginning of 2045', money(sale['event_sale_net']), money(low['event_sale_net'])], 'sec'),
    ]
    investment_rows = [
        (['Insured deposits', 'Qualifying deposits are insured at FDIC-insured banks; standard coverage is $250,000 per depositor, insured bank and ownership category, with aggregation rules.', 'Interest is generally taxable; rates change. Non-deposit funds are not FDIC-insured.', 'fdic']),
        (['Treasury securities', 'Different maturities, liquidity and inflation sensitivity; a sale before maturity can differ from face value.', 'Treasury interest is generally federally taxable but exempt from state and local income tax.', 'treasury']),
        (['Diversified funds', 'Funds can spread exposure across holdings but still lose value; fees reduce returns.', 'Dividends and realized gains may be taxable. The model uses a hypothetical after-tax return, not a security-specific forecast.', 'sec']),
    ]
    investment_rows_fmt = [([a, b, c], key) for a, b, c, key in investment_rows]
    horizon_rows = []
    for event in (2040, 2045, 2050):
        paths = m.simulate(m.SCENARIOS[0], event)
        for choice in m.STRATEGIES:
            horizon_rows.append(([str(event), m.LABELS[choice], money(paths[choice][9]['position']), money(paths[choice][-1]['position'])], 'fhfa'))
    return header('Decision paths / 02', 'Three choices, one framework', 'Compare the inherited home on an equal footing while keeping the separately owned home and its two existing rental streams in every path.') + f'''
{notice('<strong>These are invented examples, not personalized estimates.</strong> Each strategy assumes debt-free ownership, no separate housing rent, and no third-unit rent. The owner uses the third unit in the rent and sell paths; in the live path it remains unrented. Tenant rights and vacancy charges are not modeled.', True)}
<div class="cards"><article class="card path-card"><div class="path-number">01 / occupy</div><h3>Live in the inherited home</h3><p>Potential family-home relief if all eligibility and filing conditions are met. You bear the home’s running costs and keep the other building’s two rents.</p>{source('prop19', 'BOE family-home rules')}</article>
<article class="card path-card"><div class="path-number">02 / hold as rental</div><h3>Rent the inherited home</h3><p>No family-home relief in this example. Gross rent is reduced for vacancy, management, operating costs and a simplified income-tax estimate.</p>{source('rental', 'IRS rental guidance')}</article>
<article class="card path-card"><div class="path-number">03 / exit</div><h3>Sell and invest</h3><p>Sale proceeds reflect a hypothetical closing cost and income-tax basis; an assumed after-tax return is not guaranteed and can be negative.</p>{source('basis', 'IRS basis guidance')}</article></div>
{section('What an immediate sale could look like', '<p class="table-note">Two deliberately hypothetical basis treatments, at the start of 2045. A loss generates no modeled tax benefit. Costs include an assumed allowance for transaction and transfer charges; actual allocation and taxes differ.</p>' + table(['Component', 'Full-value basis', '50% basis stress'], sale_rows, 'Synthetic immediate sale, before investment returns'))}
<div class="notice warn"><span class="notice-icon" aria-hidden="true">!</span><div><strong>A step-up is not automatic.</strong> The base illustration assumes a basis adjustment to transfer-date value. Whether a trust asset qualifies depends on the facts; under the specific grantor-trust facts in {source('basis_ruling', 'Rev. Rul. 2023-2')}, the asset did not receive that adjustment. Alternate valuation may apply.</div></div>
{section('Reinvestment choices are different risks', '<p class="table-note">These are general options, not a recommended allocation. The modeled account is a single simplified proxy and is not identified with any specific product.</p>' + table(['Type', 'Risk and access', 'Tax / coverage'], investment_rows_fmt, 'Official context for possible reinvestment categories'))}
{section('Does timing matter?', '<p class="table-note">Each transfer-year illustration runs for 10 and 50 full years from January 1 of the transfer year. The 2040, 2045 and 2050 values use the same synthetic growth assumptions; later law and prices are unknown.</p>' + table(['Transfer year', 'Strategy', 'After 10 years', 'After 50 years'], horizon_rows, 'Synthetic position by transfer year and holding period'))}
<div class="panel prose"><h2>What the comparison counts</h2><p>End-of-year position = already-owned home’s market value + modeled account (or negative funding gap) + the inherited home’s hypothetical net sale proceeds, if retained. The inherited home’s sale estimate includes a simplified gain and depreciation tax; the other home is retained at market value without a sale-tax adjustment.</p><p>The model includes both existing rental streams, operating expenses and a simplified rental tax in every option. It does not include wages, other assets, mortgages, trust expenses, estate-tax payments, the tax on a future sale of the already-owned home, financing limits, or lifestyle preferences. The ordering is specific to invented inputs—not a recommendation.</p><a href="methodology.html">Read all assumptions and formulas →</a></div>'''


def projections() -> str:
    base = m.simulate(m.SCENARIOS[0])
    rows = []
    for i in range(m.YEARS):
        r = [base[s][i] for s in m.STRATEGIES]
        rows.append(([str(r[0]['year']), money(r[0]['position']), money(r[1]['position']), money(r[2]['position']), money(r[0]['b_end_value'])], 'fhfa'))
    real_rows = []
    for i in range(m.YEARS):
        real_rows.append(([str(base['live'][i]['year']), money(base['live'][i]['real_position_2026']), money(base['rent'][i]['real_position_2026']), money(base['sell'][i]['real_position_2026'])], 'bls'))
    detail = []
    for choice in m.STRATEGIES:
        parts = []
        for r in base[choice]:
            parts.append(([str(r['year']), money(r['b_end_value']), money(r['a_exit_net']), money(r['account']), money(r['net_cash']), money(r['position'])], 'rental'))
        detail.append(f'<details><summary>{e(m.LABELS[choice])}: annual components</summary><div class="details-body">'
                      + table(['Year', 'Already-owned home', 'Inherited home net sale', 'Account / funding', 'Annual net cash', 'Position'], parts, f'Synthetic {m.LABELS[choice].lower()} components, 2045–2094') + '</div></details>')
    return header('Projections / 03', 'Fifty years, year by year', 'A transparent view of the illustrative 2045 transfer, with the same other property and two rental streams in all three strategies.') + f'''
{notice('<strong>Read the number before comparing it.</strong> Position is not liquid wealth: the already-owned property is shown at market value and is not sold or reduced for future sale taxes. The inherited home is hypothetically sold at each year-end if retained. Cash flows are invested or financed, and a negative account is a funding gap.', True)}
<div class="panel prose"><h2>What changes each year</h2><p>Values and rent follow invented growth rates; tax bills use a simplified assessed-value model; operating costs and rental income tax are deducted. The sell path invests its net proceeds at the beginning of the transfer year. All results are nominal dollars, rounded to the nearest $10; displayed sums may differ slightly from sums of rounded cells.</p><p><a href="data/annual-projections.csv">Download the synthetic annual CSV</a> · <a href="methodology.html">View every assumption</a> · {source('fhfa', 'FHFA context')}</p></div>
{section('The base-path comparison', table(['Year', 'Live: position', 'Rent: position', 'Sell: position', 'Already-owned market value'], rows, 'Synthetic year-end modeled position, transfer in 2045') + '<p class="table-note">The common property is retained in all scenarios; a homeowner exemption produces a small tax difference by occupancy. The higher figure in this hypothetical case is not evidence that an actual sale is best.</p>')}
{section('Adjusting for purchasing power', '<p class="table-note">These are the same modeled positions divided by a purely assumed 2.5% annual CPI index, expressed in January 2026 purchasing power. This is not a forecast or a substitute for a discount rate; actual inflation will differ.</p>' + table(['Year', 'Live: 2026 dollars', 'Rent: 2026 dollars', 'Sell: 2026 dollars'], real_rows, 'Synthetic inflation-adjusted positions, 2045–2094'))}
{section('Show the components', ''.join(detail), '50 annual observations per path')}
'''


def properties() -> str:
    real_rows = [
        (['Inherited home: actual market value', '—', 'Withheld / not officially verified'], 'fhfa'),
        (['Inherited home: actual assessed value and bill', '—', 'Withheld / not officially verified'], 'prop8'),
        (['Already-owned home: actual assessment and bill', '—', 'Withheld / not officially verified'], 'sf_assessment'),
        (['Actual rents, lease coverage and owner-unit availability', '—', 'Withheld / not officially verified'], 'sf_rent'),
        (['Actual trust terms, ownership fractions and basis', '—', 'Not independently verified'], 'basis_ruling'),
    ]
    start = m.initial_state(2045)
    base = m.simulate(m.SCENARIOS[0])
    live, rent = base['live'][0], base['rent'][0]
    formula_rows = [
        (['Transfer-date market value of inherited home', money(start['a_value'])], 'prop19'),
        (['Transferor’s synthetic factored value', money(start['a_factored_pre'])], 'prop19'),
        (['Assumed future family-home allowance', money(start['allowance'])], 'allowance'),
        (['Eligible live-path base: factored value + excess, if any', money(live['a_factored'])], 'prop19'),
        (['Rent-path base: transfer-date value', money(rent['a_factored'])], 'prop8'),
        (['Live-path inherited-home annual property tax', money(live['a_tax'])], 'homeowner'),
        (['Rent-path inherited-home annual property tax', money(rent['a_tax'])], 'prop8'),
        (['Already-owned home factored value, all paths', money(live['b_factored'])], 'sf_assessment'),
    ]
    annual_rows, annual_costs = [], []
    for r in m.pre_transfer_projections():
        annual_rows.append(([str(r['year']), money(r['a_value']), money(r['a_factored_pre']), money(r['b_value']), money(r['b_factored']), money(r['b_rent'])], 'prop8'))
        a_assessed = min(r['a_factored_pre'], r['a_value'])
        b_assessed = min(r['b_factored'], r['b_value'])
        a_tax = max(0, a_assessed - m.HOMEOWNERS_EXEMPTION) * m.A_AD_VALOREM + r['a_fixed']
        b_tax = max(0, b_assessed - m.HOMEOWNERS_EXEMPTION) * m.B_AD_VALOREM + r['b_fixed']
        annual_costs.append(([str(r['year']), money(a_tax), money(r['a_water']), money(r['a_power']), money(r['a_insurance']), money(r['a_maintenance']), money(b_tax), money(r['b_water']), money(r['b_power']), money(r['b_insurance']), money(r['b_maintenance'])], 'prop8'))
    return header('Property & assessment / 04', 'Two homes. Different histories.', 'The inherited home is modeled as a future transfer; the other home is already owned. Their assessments do not reset together.') + f'''
{notice('<strong>Fact fields are deliberately blank.</strong> Publicly searchable assessment histories and combinations of rounded property details can identify a household. No private values are reproduced here; the numbers below are wholly synthetic.', True)}
{section('Property-specific facts', table(['Fact', 'Actual value', 'Status'], real_rows, 'Actual property facts intentionally withheld or unverified'))}
<div class="grid-two"><article class="panel prose"><div class="eyebrow">Inherited home</div><h2>Relief is conditional</h2><p>For a qualifying parent–child family-home transfer, the transferor’s principal residence must become the transferee’s principal residence under the applicable rules. The value-limit calculation can retain part of the old factored value, not necessarily all of it. {source('prop19', 'BOE fact sheet')}</p><p>For transfers from February 16, 2025 through February 15, 2027, BOE’s adjusted allowance is <strong>$1,044,590</strong>, rounded to $10. Future allowances are unknown; the model’s smooth growth is only an assumption. {source('allowance', 'BOE adjustment')}</p></article>
<article class="panel prose"><div class="eyebrow">Already-owned home</div><h2>No automatic reset</h2><p>Its factored base continues on its own track. An inheritance involving a different property is not itself a change in ownership of this home. A later independent change, qualifying new construction, decline in value, or exemption change may affect a bill. {source('sf_assessment', 'SF Assessor')}</p><p>The model preserves income from the two existing rented units in all paths and assumes a third unit is available without displacing those tenants. It does not establish that availability as a verified fact.</p></article></div>
{section('A synthetic 2045 assessment example', '<p class="table-note">Family-home relief is assumed only in the live path. The hypothetical future allowance is not a published BOE amount. Property tax includes separately modeled fixed charges, not only the ad valorem rate.</p>' + table(['Component', 'Illustrative amount'], formula_rows, 'Synthetic transfer-date assessment and first full-year bill'))}
<div class="panel prose"><h2>Why assessed value is not market value</h2><p>The factored base generally grows by the applicable inflation factor, not more than 2% annually absent a qualifying event. In a decline, a temporary Proposition 8 value can be lower than the factored base; recovery may exceed 2% until that ceiling is reached. This model approximates the assessed value as the lower of January 1 market value and factored base. It omits supplemental bills, apportionment, construction and appeals. {source('prop8', 'BOE assessment guidance')}</p><p>The model applies an illustrative $7,000 homeowners’ exemption to one principal residence depending on occupancy; eligibility and use of another exemption are not verified. {source('homeowner', 'BOE exemption')}</p></div>
{section('Before any illustrative transfer', '<p class="table-note">No-transfer baseline at the start of each year. This table holds the inherited property on its pre-transfer factored-value track through 2050 only to show the baseline; it is <em>not</em> the 2045-transfer assessment in the other tables. All values and rents below are invented.</p>' + table(['Year', 'Inherited: market', 'Inherited: factored', 'Already-owned: market', 'Already-owned: factored', 'Two rents / year'], annual_rows, 'Synthetic no-transfer property baseline, 2026–2050'))}
{section('Before-transfer cost baseline', '<p class="table-note">No-transfer comparison through 2050, not the 2045-transfer case. Each synthetic owner is assumed to qualify for a principal-residence exemption on their own home. Inherited-home costs are borne by the transferor before a transfer and are not charged to the beneficiary account. The projection does not verify any actual bill.</p>' + table(['Year', 'Inherited tax', 'Inherited water', 'Inherited power', 'Inherited insurance', 'Inherited maintenance', 'Already-owned tax', 'Already-owned water', 'Already-owned power', 'Already-owned insurance', 'Already-owned maintenance'], annual_costs, 'Synthetic annual no-transfer costs, 2026–2050'))}
'''


def costs() -> str:
    base = m.simulate(m.SCENARIOS[0])
    a_rows, b_rows = [], []
    for live, rented, sold in zip(base['live'], base['rent'], base['sell']):
        a_rows.append(([str(live['year']), money(live['a_assessed']), money(live['a_tax']), money(rented['a_assessed']), money(rented['a_tax']), money(live['a_water']), money(live['a_power']), money(live['a_insurance']), money(live['a_maintenance']), money(rented['a_rent_gross'])], 'prop8'))
        b_rows.append(([str(rented['year']), money(rented['b_assessed']), money(rented['b_tax']), money(live['b_tax']), money(rented['b_water']), money(rented['b_power']), money(rented['b_insurance']), money(rented['b_maintenance']), money(rented['b_rent_gross']), money(rented['b_net'])], 'sf_rent'))
    cost_inputs = [
        (['Inherited home', money(m.OPERATING_2026['a_water']), money(m.OPERATING_2026['a_power']), money(m.OPERATING_2026['a_insurance']), money(m.OPERATING_2026['a_maintenance']), money(m.OPERATING_2026['a_fixed'])], 'cdi'),
        (['Already-owned home', money(m.OPERATING_2026['b_water']), money(m.OPERATING_2026['b_power']), money(m.OPERATING_2026['b_insurance']), money(m.OPERATING_2026['b_maintenance']), money(m.OPERATING_2026['b_fixed'])], 'cdi'),
    ]
    return header('Costs & rental income / 05', 'The cost of keeping the keys', 'See annual property taxes, utilities, insurance, maintenance and rent separately. No property-specific bill or quote is treated as verified.') + f'''
{notice('All amounts below are <strong>synthetic annual assumptions</strong>, not actual invoices. The table links to official guidance about the method—not a source for these invented values. Future bills, insurance availability and tariff changes are unknown.')}
{section('Invented 2026 cost inputs', table(['Property', 'Water / sewer', 'Electricity', 'Insurance', 'Maintenance', 'Fixed charges'], cost_inputs, 'Synthetic annual operating inputs, 2026') + '<p class="table-note">Water / sewer and electricity rise 3%, insurance 4%, maintenance 2.5%, and fixed charges 2% per year in the base path. Property taxes are added separately. These are not official forecasts.</p>')}
<div class="grid-two"><div class="panel prose"><h2>Solar and electricity</h2><p>No solar credit or guaranteed payment is assumed. The interconnection date, tariff, production, charges and true-up are unverified. The CPUC explains that eligible legacy tariffs generally have a 20-year period from interconnection; other tariffs and circumstances differ. {source('solar', 'CPUC tariff information')}</p></div><div class="panel prose"><h2>Insurance and upkeep</h2><p>Insurance values are neither quotes nor confirmation of cover. Obtain actual homeowner or landlord terms, exclusions, deductibles and replacement limits; earthquake and flood coverage may require separate review. {source('cdi', 'CA insurance guide')}</p></div></div>
{section('Inherited home · after transfer', '<p class="table-note">Live and rent paths keep the inherited home; sell incurs no inherited-home operating cost after the immediate sale. “Property tax” includes hypothetical fixed charges. Water and power are paid by the modeled owner; the real lease allocation is unknown.</p>' + table(['Year', 'Live assessed', 'Live tax', 'Rent assessed', 'Rent tax', 'Water / sewer', 'Electricity', 'Insurance', 'Maintenance', 'Rent potential'], a_rows, 'Synthetic inherited-home annual costs and potential rent, 2045–2094'))}
{section('Already-owned home · all paths', '<p class="table-note">Two existing rents are included for every strategy; the third unit earns no rent. Gross rent is before a 5% vacancy allowance. Net cash below is after vacancy, management, property tax, all listed operating costs and an illustrative rental income tax. Owner occupancy affects the modeled homeowner exemption; assessed value itself is the same across paths.</p>' + table(['Year', 'Assessed', 'Tax: owner here', 'Tax: owner at inherited home', 'Water / sewer', 'Electricity', 'Insurance', 'Maintenance', 'Two rents gross', 'Net cash: owner here'], b_rows, 'Synthetic already-owned-home annual costs and two existing rents, 2045–2094'))}
<div class="panel prose"><h2>Rent-law caution</h2><p>For covered San Francisco units, the Rent Board published a 1.6% allowable annual increase for March 2026 through February 2027. Whether either particular unit is covered, eligible notices and future rates are unverified. The model uses 1.6% as an arbitrary long-term assumption—not a claim that future legal increases will be 1.6%. {source('sf_rent', 'Rent Board current rates')}</p></div>'''


def taxes() -> str:
    rule_rows = [
        (['Federal basic estate exclusion', '$15,000,000 for 2026; $15,480,000 for 2027', 'Current IRS announcement; individual circumstances and gifts matter'], 'estate_2027'),
        (['Annual gift exclusion', '$19,000 for 2026; $20,000 for 2027 per recipient', 'Separate from the basic estate exclusion'], 'estate_2027'),
        (['Estate return', 'Generally 9 months from death', 'Filing requirements also consider adjusted taxable gifts and specific exemption; portability can call for filing below the threshold'], 'estate'),
        (['Portability relief', 'Up to fifth death anniversary for eligible estates', 'Simplified late-election relief has specific conditions; not available to all estates'], 'portability'),
        (['California estate / inheritance', 'No state estate return required for deaths on or after 2005', 'The state controller discusses inheritance tax for deaths before June 8, 1982'], 'ca_estate'),
        (['Family-home allowance', '$1,044,590 rounded, for transfers Feb 16, 2025–Feb 15, 2027', 'Not a future 2040–2050 allowance; eligibility required'], 'allowance'),
        (['Homeowners’ exemption', '$7,000 reduction in eligible taxable value', 'Qualifying principal residence; not a $7,000 tax credit'], 'homeowner'),
        (['San Francisco secured rate', '1.18162182% for fiscal 2026–27', 'Published rate, not a property-specific bill; fixed charges can be separate'], 'sf_tax'),
        (['Net investment income tax', '3.8% of the lesser of qualifying net investment income or applicable MAGI excess', 'Trust and individual thresholds differ; not automatically due on every gain'], 'niit'),
        (['California income tax on capital gains', 'Generally taxed as ordinary income', 'Actual federal and state rates depend on the taxpayer'], 'ca_capital'),
        (['Home-sale exclusion', 'Up to $250,000 for an eligible single filer; higher limit may apply to eligible joint filers', 'Ownership, use, lookback and rental/depreciation rules apply'], 'sale'),
    ]
    estate_rows = []
    for r in m.estate_table():
        status = 'Official IRS amount' if r['official_exclusion'] else 'Hypothetical 2.5% index'
        estate_rows.append(([str(r['year']), money(r['exclusion']), status, money(r['estate']), money(r['headroom']), money(r['estimated_tax'])], 'estate_2027' if r['official_exclusion'] else 'estate'))
    proposals = [
        (['Federal S.587', 'Introduced / referred, not enacted as of review', 'Estate and generation-skipping transfer tax repeal proposal'], 's587'),
        (['California SB 288', 'Held in committee August 2026; not enacted as of review', 'Proposed family-home timing accommodation in specified court-order circumstances'], 'sb288'),
        (['San Francisco File 261020', 'Proposed, not enacted as of November 9, 2026 notice', 'Would affect certain combined banked and capital-improvement rent increases if enacted'], 'sf_rent'),
    ]
    return header('Estate & tax / 06', 'Separate the taxes', 'Estate tax, a property assessment and income tax on a sale are different questions. Future amounts and eligibility cannot be verified today.') + f'''
{notice('Official figures below are dated and jurisdiction-specific. Property values, basis, estate composition, filing status and the future law applicable to an actual transfer remain unverified. Consult an estate attorney and tax adviser before acting.', True)}
{section('Rules in effect or published as of review', table(['Topic', 'Official rule or amount', 'Qualification'], rule_rows, 'Federal, California and local tax reference, reviewed November 2026'))}
<div class="panel prose"><h2>Federal filing is not just a house-value test</h2><p>For a U.S. citizen or resident, Form 706 instructions describe a filing test involving gross estate, adjusted taxable gifts and a specific exemption. A smaller estate may file to elect portability for a surviving spouse. Filing extensions do not automatically extend time to pay tax. Nonresident noncitizen rules differ. {source('estate', 'IRS Form 706 instructions')}</p><p>The already-owned home belongs to the inheritor in this model, so it is <strong>not added to the transferor’s estate</strong> merely because a different home is inherited. Actual ownership and retained interests would still need review.</p></div>
{section('An estate-threshold illustration', '<p class="table-note">Invented transferor estate: $12,000,000 in 2026, including the inherited home and other assets as one independent pool, growing 3.5% annually; assumes no taxable gifts, deductions or portability. IRS exclusions for 2026–27 are official; 2028 onward is a hypothetical 2.5% annual index. Estimated tax = 40% × positive excess, a rough scenario—not the Form 706 calculation or a filing determination. The separate already-owned home is not added.</p>' + table(['Year', 'Basic exclusion', 'Exclusion status', 'Synthetic estate', 'Headroom / (excess)', 'Illustrative tax'], estate_rows, 'Synthetic transferor estate against federal exclusion, 2026–2050'))}
{section('Changes worth monitoring', '<p class="table-note">Status reviewed November 11, 2026. A proposal is not current law and these statuses can change.</p>' + table(['Measure', 'Status', 'Possible relevance'], proposals, 'Pending measures, not assumed to be enacted'))}
<div class="panel prose"><h2>Sale and investment tax caveats</h2><p>A qualifying inherited asset generally takes a date-of-death or applicable alternate-value basis; trust structure matters. An inherited-property assessment and income-tax basis are not the same thing. The scenario uses simplified effective rates, not a complete federal or California return. Depreciation may affect future basis and gain, and the federal home-sale exclusion has separate conditions. {source('basis', 'IRS basis')} · {source('rental', 'IRS rental property')} · {source('sale', 'IRS home sales')}</p></div>'''


def steps() -> str:
    steps_data = [
        ('Before any transfer: read the documents', 'Identify the current owner, successor trustee, beneficiaries, property interests, trust powers, loans and occupancy rules. Ask a California trust lawyer how the instrument and any incapacity provisions operate; do not assume every trust is administered alike.', 'notice'),
        ('At death: secure records and the property', 'The responsible fiduciary should obtain the death certificate and trust documents, protect the property, notify insurers, preserve records, review existing leases and arrange a qualified date-of-death valuation where needed.', 'basis'),
        ('Check trustee notice deadlines', 'California Probate Code §16061.7 generally requires specified notices within 60 days of the triggering event, with statutory exceptions. Identify who must receive notice and which event starts the clock.', 'notice'),
        ('Report the change in ownership', 'For a death transfer through a trust outside probate, the trustee or transferee generally files the change-of-ownership statement in each relevant county within 150 days of death. Probate property follows the inventory-and-appraisal timing in the statute.', 'reporting'),
        ('Decide promptly whether the family-home exclusion is possible', 'Confirm relationship, transferor’s principal residence, transferred interest and the transferee’s occupancy. BOE generally describes occupancy within one year and filing the homeowners’ or disabled-veterans’ exemption within one year for relief from transfer. Ask the assessor about late and prospective relief.', 'prop19'),
        ('Make the separate exclusion claim', 'Use the applicable county claim, such as BOE-19-P for eligible parent–child transfers. BOE describes a general three-year / before-third-party-transfer claim period and notice-related alternatives; prospective relief may be available after a late claim. Check the current form and exact circumstances.', 'prop19'),
        ('Review federal estate filing and portability', 'Form 706 is generally due nine months after death if required; consider timely extensions and payment separately. A return may be useful for portability even below a size-based filing threshold. Limited late portability relief can extend to the fifth death anniversary for eligible estates.', 'estate'),
        ('Document basis and choose a path', 'Determine whether the asset is included in the gross estate and qualifies for a basis adjustment; gather valuations and improvement records. Compare occupancy, leases, insurance, sale costs, depreciation and income tax before any disposition.', 'basis_ruling'),
        ('Carry out and monitor', 'If renting, follow applicable rental law and maintain records. If selling or investing, consider transaction taxes, tax payments, diversification and liquidity. Recheck the law and official guidance near the actual event.', 'sf_rent'),
    ]
    items = ''.join(f'<li><h3>{e(title)}</h3><p>{e(text)}</p>{source(key)}</li>' for title, text, key in steps_data)
    return header('Trust checklist / 07', 'From documents to decision', 'An ordered starting point for the trustee and beneficiary. Specific deadlines, exemptions and responsibilities depend on the trust and the law in effect at the time.') + f'''
{notice('This is a general checklist, not a determination of who the trustee is or which rule applies. Do not wait for the outer deadline when an earlier filing, notice or eligibility requirement may apply.', True)}
<ol class="step-list">{items}</ol>
<div class="panel prose"><h2>Keep the properties separate</h2><p>Only the inherited property is assumed to transfer at the event. The already-owned property is not added to the transferor’s estate or reassessed just because the other property transfers. Check whether moving changes the principal-residence exemption and review existing leases before taking any action. {source('sf_assessment', 'SF Assessor')}</p></div>'''


def scenarios() -> str:
    baseline = m.simulate(m.SCENARIOS[0])
    summary = []
    sections = []
    for sc in m.SCENARIOS:
        paths = m.simulate(sc)
        for choice in m.STRATEGIES:
            r10, r50 = paths[choice][9], paths[choice][-1]
            delta = r50['position'] - baseline[choice][-1]['position']
            summary.append(([e(sc.label), e(m.LABELS[choice]), money(r10['position']), money(r50['position']), money(r50['real_position_2026']), money(delta)], sc.source_key))
        annual = []
        for i in range(m.YEARS):
            annual.append(([str(paths['live'][i]['year']), money(paths['live'][i]['position']), money(paths['rent'][i]['position']), money(paths['sell'][i]['position'])], sc.source_key))
        sections.append(f'<details><summary>{e(sc.label)} · annual path</summary><div class="details-body"><p class="table-note">{e(sc.description)} These shocks are invented; the official source describes background, not the hypothetical shock.</p>'
                        + table(['Year', 'Live position', 'Rent position', 'Sell position'], annual, f'{sc.label}: synthetic annual positions, 2045–2094') + '</div></details>')
    history_rows = [([str(year), rate, 'Annual average CPI-U change vs prior year'], 'bls_history')
                    for year, rate in ((1974, '11.0%'), (1980, '13.5%'), (1990, '5.4%'),
                                       (2000, '3.4%'), (2009, '−0.4%'), (2010, '1.6%'),
                                       (2020, '1.2%'), (2022, '8.0%'))]
    observed = [
        (['Inflation', 'U.S. CPI-U increased 3.7% over the 12 months ending September 2026.', 'An observed historical measure, not a future assumption.'], 'bls'),
        (['Housing', 'U.S. FHFA purchase-only home price index rose 2.1% over the year through 2026 Q2; California fell 0.2%.', 'Indexes are not appraisals and can diverge from an individual property.'], 'fhfa'),
        (['Risk and fees', 'Diversification may reduce some risks; mutual funds and ETFs can lose money and have expenses.', 'The model does not prescribe an allocation or guarantee a return.'], 'sec'),
    ]
    descriptions = ''.join(f'<article class="card"><div class="eyebrow">{e(sc.label)}</div><p>{e(sc.description)}</p>{source(sc.source_key, "Official context")}</article>' for sc in m.SCENARIOS)
    return header('Stress tests / 08', 'Plan for a different future', 'A steady line is not a probability distribution. These deliberately severe, variable-condition paths illustrate sensitivities over 50 years—not forecasts.') + f'''
{notice('The scenarios are constructed thought experiments, not historical replays, probability estimates, insurance quotes or legal forecasts. Losses can coincide, last longer, be larger or occur before the assumed transfer.', True)}
{section('A little context', table(['Signal', 'Official observation', 'Limit'], observed, 'Observed economic context; not used as a forecast'))}
{section('A half-century of different inflation regimes', '<p class="table-note">Selected annual-average CPI-U changes, not year-end changes. These historical observations provide context; the model does not replay them or assign them as future probabilities.</p>' + table(['Year', 'Annual-average CPI change', 'Measure'], history_rows, 'Selected U.S. inflation observations, 1974–2022'))}
{section('Six hypothetical paths', '<div class="cards">' + descriptions + '</div>')}
{section('After 10 and 50 years', '<p class="table-note">Transfer on January 1, 2045. Delta compares each path to its own strategy in the base scenario at year 50. The first and last comparison figures are nominal; the purchasing-power column uses an assumed CPI path. The already-owned home is retained at market value.</p>' + table(['Scenario', 'Strategy', '10-year nominal', '50-year nominal', '50-year in 2026 dollars', '50-year nominal change vs base'], summary, 'Synthetic stress-test comparisons'))}
{section('See the full annual paths', ''.join(sections), '2045–2094')}
<div class="panel prose"><h2>How to interpret the shocks</h2><p>A 2050 market shock is applied to year-end property values and to a positive investment account; the following January’s simplified assessment can reflect the decline. The insurance squeeze permanently raises the cost level over its seven years. The repair example assumes work immediately restores the asset’s value and no modeled rental interruption—both optimistic simplifications. Relief and basis scenarios are not predictions of law.</p><p>The purchasing-power column assumes 2.5% annual CPI growth, except 6% in 2048–2054 in the inflation stress. There is no probability weighting, mortgage stress, loss carryforward or guarantee that a negative funding gap can actually be financed. See the <a href="methodology.html">full method</a> and <a href="flagged.html">flags</a>.</p></div>'''


def methodology() -> str:
    input_rows = [
        (['Inherited market value', money(m.A_VALUE_2026), '2026 synthetic beginning value', 'fhfa']),
        (['Inherited factored value', money(m.A_FACTORED_2026), '2026 synthetic starting assessment base', 'prop8']),
        (['Already-owned market value', money(m.B_VALUE_2026), '2026 synthetic beginning value', 'fhfa']),
        (['Already-owned factored value', money(m.B_FACTORED_2026), '2026 synthetic starting assessment base', 'sf_assessment']),
        (['Inherited potential annual rent', money(m.A_RENT_2026), '2026 gross; rented path only', 'rental']),
        (['Already-owned annual rent', money(m.B_TWO_RENTS_2026), '2026 gross from two retained rented units', 'sf_rent']),
        (['Already-owned building tax basis', money(m.B_BUILDING_BASIS_2026), 'Invented building-only basis; 2/3 allocated to rentals', 'rental']),
        (['Synthetic transferor estate', '$12,000,000', '2026 synthetic total; separately owned home not added', 'estate']),
    ]
    input_rows_fmt = [([a, b, c], d) for a, b, c, d in input_rows]
    rate_rows = [
        (['Home market-value growth', '3% per year', 'Both homes; not a forecast'], 'fhfa'),
        (['Factored-base growth', '2% per year', 'Illustrative upper bound, actual annual factor may be lower'], 'prop8'),
        (['Future family-home allowance growth', '2.5% per year', 'Smooth illustration; actual BOE adjustment is biennial and unknown'], 'allowance'),
        (['CPI for purchasing power', '2.5% per year; 6% during the inflation stress in 2048–2054', 'Invented price index, relative to January 2026'], 'bls'),
        (['Gross rent growth', '3% inherited home; 1.6% already-owned', 'Invented future assumptions; actual rent limits vary'], 'sf_rent'),
        (['Vacancy and management', '5% gross vacancy; 6% of rent collected', 'Both rented properties; no third-unit income'], 'rental'),
        (['Property tax rates', '1.15% inherited; 1.18% already-owned', 'Invented ad valorem rates; fixed charges separately'], 'sf_tax'),
        (['Operating growth', '3% utilities; 4% insurance; 2.5% maintenance; 2% fixed charges', 'Synthetic annual assumptions; stress path varies these'], 'cdi'),
        (['Inherited building share', '65% of assumed basis', 'Synthetic depreciable share; land not depreciated'], 'rental'),
        (['Selling costs', '5% of sales price', 'Assumed all-in selling and transfer costs'], 'scc_transfer'),
        (['Rental income tax', '30% of positive modeled taxable rental income', 'Simplified effective proxy, no loss benefit or carryforward'], 'rental'),
        (['Sale gain / depreciation tax', '30% / 35% effective', 'Invented proxies, not statutory federal or California rates'], 'ca_capital'),
        (['Investment / funding account', '4% annual after-tax return; 6% interest on negative balance', 'Proxy net of assumed investment taxes and fees; no financing guarantee'], 'sec'),
        (['Federal estate proxy', '3.5% estate growth; 2.5% exclusion index after 2027; 40% of positive excess', 'No gifts, deductions, DSUE or state changes; not a Form 706'], 'estate'),
    ]
    return header('Assumptions & method / 09', 'A model you can inspect', 'All property-specific inputs are invented. The underlying Python model is deterministic, requires no personal input and generates every figure shown here.') + f'''
{notice('<strong>Official sources establish rules and methods, not the synthetic property amounts or growth rates.</strong> These numbers have deliberately not been derived from an individual’s records.')}
{section('2026 synthetic starting points', table(['Input', 'Assumed amount', 'Interpretation'], input_rows_fmt, 'Invented property and estate inputs'))}
{section('Rates and treatment', table(['Input', 'Model assumption', 'Limit'], rate_rows, 'Synthetic assumptions and official methodological references'))}
<div class="grid-two"><div class="panel prose"><h2>Annual timing</h2><p>Values start January 1, 2026. The chosen transfer occurs January 1 in 2040, 2045 or 2050. The sell option closes immediately and invests net proceeds for the year. The other paths hold for the year. Taxes use start-of-year assessed values; market values change during the year; property cash flows are added at year-end. All costs are annual, in nominal dollars.</p></div>
<div class="panel prose"><h2>Assessment arithmetic</h2><p>For an eligible live-path family home, initial factored value = old factored value + max(0, market value − old factored value − hypothetical allowance). Otherwise the inherited home resets to transfer value. Each year’s taxable assessment is approximated as the lower of factored value and January 1 market value, less a $7,000 exemption if assumed eligible. The separate property is not reassessed on the other home’s transfer. {source('prop19', 'BOE method')} · {source('prop8', 'BOE decline in value')}</p></div>
<div class="panel prose"><h2>Rent and depreciation</h2><p>Collected rent = gross × 95%; management = 6% of collected rent. The taxable rental proxy subtracts management, allowable assumed rental shares of operating and property costs, and straight-line residential-building depreciation over 27.5 years. The already-owned property’s invented building is placed in service in 2026; two-thirds of costs and building basis are assigned to rentals. Full-year conventions are simplified. Negative taxable income yields no assumed tax benefit or carryforward. {source('rental', 'IRS Publication 527')}</p></div>
<div class="panel prose"><h2>Retained-home exit</h2><p>Each year-end value assumes a hypothetical sale of the inherited home after 5% selling costs. Rental basis is reduced by accumulated depreciation; the modeled gain is split into depreciation and other gain and taxed at the assumed 35% and 30% proxies. For a live path after two full years, the example assumes the $250,000 single-filer exclusion is available and no disqualifying lookback. Actual eligibility, depreciation rules and tax brackets require a return-specific calculation. {source('sale', 'IRS home-sale guidance')} · {source('rental', 'IRS rental guidance')}</p></div>
<div class="panel prose"><h2>Account and final position</h2><p>Positive beginning account balances earn the assumed 4% after-tax, after-fee annual return. This is a proxy for investment taxation, including eventual realization; no separate account liquidation tax is computed. Negative balances accrue 6% as an illustrative funding gap. The account starts at zero immediately before the assumed transfer (apart from immediate sale proceeds); no pre-transfer rental savings are included. It receives each modeled year’s net cash from both properties. Position = account + retained already-owned home’s market value + inherited-home hypothetical net sale proceeds, if any.</p></div>
<div class="panel prose"><h2>What is missing</h2><p>No other assets, wages, household consumption, debt, capital improvements, selling tax on the retained already-owned home, estate-tax payments, trust fees, time-value discounting, portfolio cost-basis ledger, tax-loss carryforwards, or funding constraints are included. These omissions can change the outcome. Stress results are not probabilities. {source('estate', 'IRS estate instructions')} · {source('sec', 'SEC investment guidance')}</p></div></div>
<section class="section prose"><h2>Reproduce and audit</h2><p>The repository includes <code>integration-487/model.py</code>, <code>integration-487/build_site.py</code> and automated checks. Run <code>python3 -m unittest discover -s integration-487/tests</code> to test the formulas. Run <code>python3 integration-487/build_site.py --output .</code> from the repository root to rebuild. No user-entered data, network requests, scripts or tracking are needed by the site.</p></section>'''


def sources_page() -> str:
    cards = []
    for key, (url, title, what) in SOURCES.items():
        cards.append(f'<article class="card"><div class="eyebrow">Official primary source</div><h3>{e(title)}</h3><p>{e(what)}</p><a href="{e(url)}">Open source <span aria-hidden="true">↗</span></a></article>')
    return header('Official sources / 10', 'The source library', 'A dated register of the official material used for legal rules and methodological context. A citation does not verify invented assumptions or an individual property fact.') + f'''
{notice('Reviewed November 11, 2026. Sources and laws can change; revisit the original agency guidance near any actual transfer. For statutes and proposals, the current official status controls.')}
<div class="cards">{''.join(cards)}</div>'''


def flagged() -> str:
    flags = [
        (['Privacy and prior publication', 'Prior public versions included linkable financial details. Current files can be replaced, but Git history, deployments, third-party copies and search caches may retain them.', 'flagged / historical exposure'], 'prop8'),
        (['Actual values and history', '—', 'Intentionally withheld and not independently verified; no real assessment anchors are used'], 'sf_assessment'),
        (['Trust, date and relationship', '—', 'Trust terms, date of death, relationship and ownership fractions are unverified'], 'notice'),
        (['Income-tax basis', '—', 'A full-value basis is a scenario, not a guarantee; trust and estate inclusion matter'], 'basis_ruling'),
        (['Family-home eligibility', '—', 'Transferor and transferee residence, filing and continued eligibility are unverified'], 'prop19'),
        (['Already-owned home assessment', '—', 'Actual bill, factored value, improvements and homeowner-exemption status are unverified'], 'sf_assessment'),
        (['Rents and third unit', '—', 'Actual amounts, coverage, vacancies, third-unit availability, tenant rights and notices are unverified'], 'sf_rent'),
        (['Insurance, utility and solar', '—', 'Actual coverage, premiums, meters, tariff, interconnection date and true-up are unverified'], 'cdi'),
        (['Debts, repairs and closing charges', '—', 'No mortgage or liens are modeled; actual costs and transfer-tax liability are unverified'], 'scc_transfer'),
        (['Tax and estate inputs', '—', 'Filing status, citizenship, other estate assets, gifts, deductions, portability and realized tax rates are unverified'], 'estate'),
        (['Future law and economic conditions', '—', 'Future statutory thresholds, rent caps, inflation, returns and growth are unknown'], 'estate_2027'),
        (['Funding and omitted taxes', '—', 'Negative account assumes financing at 6%; no future sale tax on the already-owned home or estate tax is included'], 'sec'),
        (['Older site contradiction', 'Superseded', 'An older page wrongly treated inheritance of one home as an automatic reassessment of the separately owned home'], 'sf_assessment'),
    ]
    return header('Flagged for review / 11', 'What remains unknown', 'A useful model should show its limits. Blank fact cells are intentional; no missing personal data has been inferred or filled in.') + f'''
{notice('Public privacy cannot be guaranteed by rounding alone. This version uses invented inputs and withholds historical property details. Replacing current files does not erase older Git commits, Pages builds, search caches or third-party copies.', True)}
{section('Open items and irregularities', table(['Issue', 'Actual fact / status', 'Reason'], flags, 'Unverified facts and known limitations'))}
<div class="panel prose"><h2>How to use this guide safely</h2><p>Never send sensitive tax rolls, trust documents, addresses or personal identifiers to a public issue, PR or repository. Obtain real appraisals, bills, coverage and legal advice privately. This page is a research and scenario framework, not a personalized financial plan.</p><p>Previous statements that an older version was fully private or comprehensively verified are superseded. The official links in this guide support the cited rules, not the invented inputs.</p></div>'''


def write_csv(output: Path) -> None:
    target = output / 'data' / 'annual-projections.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    baseline = m.simulate(m.SCENARIOS[0])
    with target.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['classification', 'scenario', 'strategy', 'year', 'already_owned_market_value_usd', 'inherited_hypothetical_net_sale_usd', 'account_or_funding_usd', 'annual_net_cash_usd', 'modeled_position_usd', 'modeled_position_in_2026_usd', 'official_methodology_source'])
        for choice in m.STRATEGIES:
            for row in baseline[choice]:
                writer.writerow(['synthetic, not actual', 'base', choice, row['year'], m.round10(row['b_end_value']), m.round10(row['a_exit_net']), m.round10(row['account']), m.round10(row['net_cash']), m.round10(row['position']), m.round10(row['real_position_2026']), SOURCES['rental'][0]])


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(HERE / 'theme.css', output / 'assets' / 'style.css')
    contents = {
        'index.html': overview(), 'decisions.html': decisions(), 'projections.html': projections(),
        'properties.html': properties(), 'costs.html': costs(), 'taxes.html': taxes(),
        'steps.html': steps(), 'scenarios.html': scenarios(), 'methodology.html': methodology(),
        'sources.html': sources_page(), 'flagged.html': flagged(),
    }
    for name, label, _ in PAGES:
        (output / name).write_text(page(name, label, contents[name]), encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    write_csv(output)
    print(f'Built {len(contents)} pages and a synthetic CSV in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'site', help='Destination directory (default: staged site)')
    args = parser.parse_args()
    build(args.output.resolve())
