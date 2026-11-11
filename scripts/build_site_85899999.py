#!/usr/bin/env python3
"""
Deterministic static site generator for `site/` (8 pages + assets/data.js + assets/app.js).
Enforces:
  1. Strict $10 rounding on all dollar figures.
  2. Strict anonymization (placeholders only; zero PII).
  3. Official .gov / .ca.gov / public utility source link on EVERY table row (`<tr>`).
  4. Blank cells (`<td class="blank-cell"></td>`) for unverified historical values, flagged on `flagged-review.html`.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "data" / "verified_projections_85899999.json"
SITE_DIR = ROOT / "site"
ASSETS_DIR = SITE_DIR / "assets"


def fmt(val: int) -> str:
    val10 = int(round(val / 10.0) * 10)
    if val10 < 0:
        return f"-${abs(val10):,}"
    return f"${val10:,}"


# Official Verified Primary Sources (Zero Commercial Websites)
SRC = {
    "BOE_LTA_24053": ("CA BOE LTA 2024/053 (Prop 13 CCPI 1976–2025)", "https://boe.ca.gov/proptaxes/pdf/lta24053.pdf"),
    "BOE_LTA_13059": ("CA BOE LTA 2013/059 (2014–15 CCPI)", "https://boe.ca.gov/proptaxes/pdf/lta13059.pdf"),
    "BOE_LTA_26002": ("CA BOE LTA 2026/002 (2026–27 CCPI)", "https://boe.ca.gov/proptaxes/pdf/lta26002.pdf"),
    "BOE_PUB_801": ("CA BOE Pub 801 — Prop 19 Fact Sheet", "https://www.boe.ca.gov/pdf/pub801.pdf"),
    "BOE_LTA_25015": ("CA BOE LTA 2025/015 — Prop 19 Guidance", "https://boe.ca.gov/proptaxes/pdf/lta25015.pdf"),
    "BOE_LTA_26026": ("CA BOE LTA 2026/026 — Multi-Unit Prop 19", "https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf"),
    "BOE_19P": ("CA BOE Form BOE-19-P Sample & Rules", "https://www.boe.ca.gov/proptaxes/pdf/sample-boe19p.pdf"),
    "BOE_DEATH": ("CA BOE Pub 800-9 — Death of Property Owner", "https://www.boe.ca.gov/pdf/pub800-9.pdf"),
    "SCC_RATES": ("Santa Clara County FY 2025–26 Tax Rate Book", "https://controller.santaclaracounty.gov/property-tax-distribution/property-tax-rate-book"),
    "SCC_ASSESSOR": ("Santa Clara County Office of the Assessor", "https://www.sccassessor.org/"),
    "SF_TREASURER": ("SF Treasurer — Secured Property Tax Rates (FY26–27)", "https://sftreasurer.org/property/secured-property-taxes"),
    "SF_ASSESSOR_TT": ("SF Assessor-Recorder — Transfer Tax Schedule", "https://www.sfassessor.org/recorder-information/recording-document/transfer-tax"),
    "SF_RENT_BOARD": ("SF Rent Board — 2026–27 Allowable Increase & Fee", "https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit"),
    "IRS_706": ("IRS Form 706 Instructions (Rev. 07/2026)", "https://www.irs.gov/instructions/i706"),
    "IRS_RP_2532": ("IRS Rev. Proc. 2025-32 (2026 OBBBA Adjustments)", "https://www.irs.gov/pub/irs-drop/rp-25-32.pdf"),
    "IRS_RR_2302": ("IRS Rev. Rul. 2023-2 (Grantor Trust Basis)", "https://www.irs.gov/pub/irs-drop/rr-23-02.pdf"),
    "IRS_TC409": ("IRS Topic 409 — Capital Gains & Losses", "https://www.irs.gov/taxtopics/tc409"),
    "IRS_TC559": ("IRS Topic 559 — 3.8% Net Investment Income Tax", "https://www.irs.gov/taxtopics/tc559"),
    "IRS_P523": ("IRS Pub 523 — Selling Your Home (IRC § 121)", "https://www.irs.gov/publications/p523"),
    "FTB_CAP": ("CA FTB — Capital Gains Taxed as Ordinary Income (Max 13.3%)", "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html"),
    "RTC_13301": ("CA Rev. & Tax. Code § 13301 (Death Tax Prohibition)", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=13301"),
    "RTC_13302": ("CA Rev. & Tax. Code § 13302 (Dormant Pick-Up Tax)", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=13302"),
    "RTC_11930": ("CA Rev. & Tax. Code § 11930 (Inheritance Transfer Tax Exemption)", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11930"),
    "RTC_11911": ("CA Rev. & Tax. Code § 11911 (County Documentary Transfer Tax)", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11911"),
    "PROB_16061": ("CA Probate Code § 16061.7 (60-Day Trustee Notice)", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB"),
    "CPUC_SJW": ("CPUC Decision D.24-12-077 — San Jose Water GRC", "https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M551/K128/551128522.PDF"),
    "SFPUC_2026": ("SFPUC FYE 2026–2028 Water & Wastewater Prop 218 Notice", "https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice"),
    "CPUC_NEM": ("CPUC EO N-5-24 Report — 20-Yr NEM Sunset & Fixed Charge", "https://www.cpuc.ca.gov/-/media/cpuc-website/industries-and-topics/reports/cpuc-response-to-executive-order-n-5-24.pdf"),
    "CPUC_NBT": ("CPUC Resolution — D.22-12-056 NBT & D.24-05-028 Flat Charge", "https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M559/K800/559800004.PDF"),
    "CDI_AVG": ("CA Dept. of Insurance — Sustainable Insurance Strategy", "https://www.insurance.ca.gov/01-consumers/180-climate-change/sustainable-insurance-strategy.Cfm"),
    "CDI_TOOL": ("CA Dept. of Insurance — 2026 Homeowners Comparison Tool", "https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111%3A20"),
    "CDI_GUIDE": ("CA Dept. of Insurance — Residential Insurance Guide", "https://www.insurance.ca.gov/0150-seniors/0200beforebuy/Shop4ResIns.cfm"),
    "HUD_FMR": ("U.S. HUD FY 2026 Fair Market Rent Schedule (CA)", "https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY2026_FMR_Schedule.pdf"),
    "FHFA_HPI": ("FHFA House Price Index Report (2026Q2)", "https://www.fhfa.gov/document/d/hpi/fhfa-house-price-index-report-2026q2"),
    "CBO_2026": ("CBO Budget & Economic Outlook: 2026 to 2036", "https://www.cbo.gov/system/files/2026-02/61882-Executive-Summary.pdf"),
    "FED_H15": ("Federal Reserve H.15 Selected Interest Rates", "https://www.federalreserve.gov/releases/h15/"),
}


def slink(key: str, custom_label: str = None) -> str:
    label, url = SRC[key]
    text = custom_label if custom_label else label
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'


NAV_ITEMS = [
    ("index.html", "Executive Summary"),
    ("properties.html", "Properties & Costs"),
    ("projections.html", "2026–2050 Projections"),
    ("scenarios.html", "Live vs. Rent vs. Sell"),
    ("estate-tax.html", "Estate & Tax Laws"),
    ("inheritance-guide.html", "Step-by-Step Guide"),
    ("flagged-review.html", "Flagged for Review"),
    ("sources.html", "Official Sources"),
]


def render_shell(active_file: str, title: str, eyebrow: str, heading: str, subtitle: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a href="{href}" class="{"active " if href == active_file else ""}{"nav-flag" if "flagged" in href else ""}">{label}</a>'
        for href, label in NAV_ITEMS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — CA Trust Inheritance Decision Suite</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="index.html">
        <span class="brand-mark">CA</span>
        <span>Trust Inheritance Decision Suite (95014 &amp; 94122)</span>
      </a>
      <nav class="nav-links" aria-label="Primary Navigation">
        {nav_html}
      </nav>
    </div>
  </header>
  <div class="privacy-strip">
    <div class="privacy-strip-inner">
      <span><strong>Privacy Mandate Active:</strong> All personal names, street addresses, APNs, and trust identifiers are strictly anonymized using placeholders (<code>[Property A]</code>, <code>[Property B]</code>, <code>[Grantor]</code>, <code>[Beneficiary]</code>).</span>
      <span><strong>Precision Standard:</strong> All dollar figures rounded to nearest <code>$10</code> · 100% official <code>.gov</code> / utility sources</span>
    </div>
  </div>
  <main class="container">
    <section class="page-header">
      <span class="eyebrow">{eyebrow}</span>
      <h1>{heading}</h1>
      <p>{subtitle}</p>
    </section>
    {body_html}
  </main>
  <footer class="site-footer">
    <div class="site-footer-inner">
      <span>Educational &amp; analytical decision-support framework verified as of November 2026. Consult a California Certified Specialist in Estate Planning, Trust &amp; Probate Law and a CPA prior to executing trust distributions or tax filings.</span>
      <span><a href="flagged-review.html">Review Flagged Items</a> · <a href="sources.html">Official Source Registry</a></span>
    </div>
  </footer>
  <script src="assets/data.js"></script>
  <script src="assets/app.js"></script>
</body>
</html>
"""


def build_index_page(d: dict) -> str:
    sc2045 = d["decision_scenarios"]["2045"]
    s_map = {s["id"]: s for s in sc2045["strategies"]}
    s1, s2b, s2a, s3 = s_map["S1"], s_map["S2B"], s_map["S2A"], s_map["S3"]
    est2045 = [r for r in d["estate_tax_thresholds"] if r["year"] == 2045][0]

    body = f"""
    <div class="grid-4">
      <div class="kpi-card">
        <span class="kpi-label">[Property A] Cupertino (95014)</span>
        <div class="kpi-value">$3,100,000</div>
        <span class="kpi-meta">Nov 2026 user est. · 2045 proj: <strong>{fmt(sc2045["cupertino_fmv_at_inheritance"])}</strong> ({slink("FHFA_HPI", "FHFA HPI")})</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">[Property B] SF Outer Sunset (94122)</span>
        <div class="kpi-value">$1,800,000</div>
        <span class="kpi-meta">3 units (2 rented at <strong>$85,800/yr</strong> + 1 owner-ready) ({slink("HUD_FMR", "HUD FMR")})</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Federal Estate Tax Threshold (2026)</span>
        <div class="kpi-value">$15,000,000</div>
        <span class="kpi-meta">Per person (<strong>$30,000,000</strong> married w/ DSUE) · 40% above ({slink("IRS_706", "IRS Form 706")})</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">CA State &amp; Local Inheritance Tax</span>
        <div class="kpi-value">$0</div>
        <span class="kpi-meta">Prohibited by statute at state &amp; local levels ({slink("RTC_13301", "CA RTC § 13301")})</span>
      </div>
    </div>

    <div class="callout callout-emerald">
      <strong>Executive Recommendation (2040–2050 Trust Inheritance):</strong>
      From a pure profit-maximization and cost-minimization standpoint, <strong>Strategy S1 — Inherit <code>[Property A — Cupertino 95014]</code> via a Revocable Living Trust, Sell Promptly Using the 100% <code>IRC § 1014</code> Step-Up in Basis ($0 Capital Gains Tax), Reinvest Net Proceeds ({fmt(sc2045["s1_net_sale_proceeds_day1"])} at 2045 midpoint), and Live in the Vacant 3rd Unit of <code>[Property B — San Francisco 94122]</code> while Retaining Its $85,800/yr (escalated) 2-Unit Rental Income</strong> — is the clear financial winner. Over a 15-year post-inheritance horizon (2045–2060), Strategy S1 builds <strong>{fmt(s1["total_household_wealth_end"])}</strong> in after-tax household wealth, outperforming <strong>Renting Cupertino (S3) by +{fmt(s1["total_household_wealth_end"] - s3["total_household_wealth_end"])}</strong> and <strong>Living in Cupertino (S2B/S2A) by +{fmt(s1["total_household_wealth_end"] - s2b["total_household_wealth_end"])} to +{fmt(s1["total_household_wealth_end"] - s2a["total_household_wealth_end"])}</strong>.
    </div>

    <div class="card">
      <h2>Executive Summary: Five Decisive Findings</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Decision Pillar</th>
              <th>Verified Finding &amp; Dollar Impact (Rounded to $10)</th>
              <th>Strategic Implication</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>1. Prop 19 Property Tax Shock on Cupertino</strong></td>
              <td>At the 2045 midpoint (projected FMV <strong>{fmt(sc2045["cupertino_fmv_at_inheritance"])}</strong>), Cupertino property taxes jump from <strong>$10,630/yr</strong> (parent's Prop 13 base) to <strong>{fmt(sc2045["cupertino_yr1_tax_if_live"])}/yr</strong> even <em>with</em> Prop 19 primary-residence occupancy (cap <strong>{fmt(sc2045["prop19_cap_at_inheritance"])}</strong>), and to <strong>{fmt(sc2045["cupertino_yr1_tax_if_rent"])}/yr</strong> if rented out (0% Prop 19 relief).</td>
              <td>Prop 19 saves <strong>{fmt(sc2045["prop19_annual_tax_savings_yr1"])}/yr</strong> if <code>[Beneficiary]</code> moves in within 1 year, yet annual taxes still surge 5.3x — eroding holding returns.</td>
              <td>{slink("BOE_PUB_801", "CA BOE Pub 801")} · {slink("SCC_RATES", "SCC Tax Rate Book")}</td>
            </tr>
            <tr>
              <td><strong>2. Single Primary Residence Conflict (SF vs. Cupertino)</strong></td>
              <td>California allows only <strong>one</strong> Homeowners' Exemption / principal residence at a time (<code>RTC § 218</code>). Occupying <code>[Property B — SF 94122]</code> Unit 3 forfeits Prop 19 on Cupertino; occupying Cupertino preserves Prop 19 on Cupertino while leaving SF Unit 3 vacant or subject to SF Rent Control if leased.</td>
              <td>Because SF Unit 3 provides free primary housing alongside 2 existing rental units, selling Cupertino unlocks <strong>{fmt(sc2045["s1_net_sale_proceeds_day1"])}</strong> liquid capital with zero housing displacement.</td>
              <td>{slink("BOE_LTA_26026", "CA BOE LTA 2026/026")} · {slink("SF_RENT_BOARD", "SF Rent Board")}</td>
            </tr>
            <tr>
              <td><strong>3. Why Renting Out Cupertino (S3) Underperforms</strong></td>
              <td>Full FMV reassessment (<strong>{fmt(sc2045["cupertino_yr1_tax_if_rent"])}/yr</strong> tax in 2045) plus landlord DP-3 insurance and maintenance compresses Cupertino's net after-tax rental yield to just <strong>{sc2045["cupertino_yr1_net_yield_pct"]}%/yr</strong> (<strong>{fmt(sc2045["cupertino_yr1_net_rent_aftertax"])}/yr</strong> on <strong>{fmt(sc2045["cupertino_fmv_at_inheritance"])}</strong> equity), while forfeiting tax-free step-up liquidity on future gains.</td>
              <td>Reinvesting net sale proceeds at 5.8% after-tax generates <strong>{fmt(sc2045["s1_yr1_portfolio_aftertax_gain"])}/yr</strong> in Year 1 — more than 13x Cupertino's net rental cash flow.</td>
              <td>{slink("BOE_LTA_25015", "CA BOE LTA 2025/015")} · {slink("HUD_FMR", "HUD FY26 FMR")}</td>
            </tr>
            <tr>
              <td><strong>4. Critical Trust Structure Trap (Revocable vs. Irrevocable)</strong></td>
              <td>Inheriting via a <strong>Revocable Living Trust</strong> grants a 100% FMV basis step-up under <code>IRC § 1014</code> (<strong>$0</strong> capital gains tax on immediate sale). Under <strong><code>IRS Rev. Rul. 2023-2</code></strong>, an estate-excluded <strong>Irrevocable Grantor Trust</strong> receives <strong>no step-up</strong>, triggering a <strong>{fmt(sc2045["irrevocable_trust_cap_gains_penalty_if_sold"])}</strong> combined 37.1% Fed+CA tax hit if sold in 2045.</td>
              <td>Keep Cupertino inside a revocable/estate-included trust unless total taxable estate exceeds the federal estate exclusion; never transfer low-basis real estate to an IDGT without modeling the 37.1% vs. 40% trade-off.</td>
              <td>{slink("IRS_RR_2302", "IRS Rev. Rul. 2023-2")} · {slink("FTB_CAP", "CA FTB Cap Gains")}</td>
            </tr>
            <tr>
              <td><strong>5. Cash Inheritance &amp; Estate Tax Headroom + Solar Sunset</strong></td>
              <td>CA &amp; local inheritance tax is <strong>$0</strong>. Federal estate tax (40%) begins above <strong>$15,000,000</strong> single / <strong>$30,000,000</strong> married in 2026 (projected to <strong>{fmt(est2045["fed_exclusion_single"])}</strong> single / <strong>{fmt(est2045["fed_exclusion_married_portability"])}</strong> married in 2045, leaving <strong>{fmt(est2045["tax_free_cash_headroom_single_cup_only"])}</strong> to <strong>{fmt(est2045["tax_free_cash_headroom_married_both_props"])}</strong> in tax-free cash headroom above real estate). Also note: Cupertino's NEM solar profit sunsets 20 years after interconnection.</td>
              <td>Elect spousal portability (<code>Form 706</code>) at the first parent's death even if $0 tax is due, and budget for post-NEM electricity &amp; inverter replacement by 2040–2050.</td>
              <td>{slink("IRS_RP_2532", "IRS Rev. Proc. 2025-32")} · {slink("CPUC_NEM", "CPUC EO N-5-24")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Unified Household Decision Matrix (2045 Midpoint Inheritance · 15-Year Horizon to 2060)</h2>
      <p>All four strategies account for <strong>both</strong> properties (<code>[Property A — Cupertino 95014]</code> and <code>[Property B — San Francisco 94122]</code>), separated ad valorem vs. parcel property taxes, operating expenses, income/capital-gains taxes, and reinvested cash flows, rounded to the nearest <code>$10</code>.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Primary Residence</th>
              <th class="num">Yr-1 Property Net Cash Flow</th>
              <th class="num">Yr-1 Portfolio After-Tax Return</th>
              <th class="num">2060 Financial Portfolio</th>
              <th class="num">2060 Total Household Net Worth</th>
              <th>Official Rule Anchor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>S1: Sell Cupertino &amp; Reinvest (Recommended)</strong></td>
              <td>SF Unit 3 (2 SF units rented)</td>
              <td class="num">{fmt(s1["yr1_net_cashflow"])}</td>
              <td class="num">{fmt(sc2045["s1_yr1_portfolio_aftertax_gain"])}</td>
              <td class="num">{fmt(s1["financial_portfolio_end"])}</td>
              <td class="num"><strong>{fmt(s1["total_household_wealth_end"])}</strong></td>
              <td>{slink("IRS_RR_2302", "IRC § 1014 Step-Up")} · {slink("RTC_11911", "CA RTC § 11911")}</td>
            </tr>
            <tr>
              <td><strong>S3: Rent Out Cupertino + Live in SF Unit 3</strong></td>
              <td>SF Unit 3 (Cupertino + 2 SF rented)</td>
              <td class="num">{fmt(s3["yr1_net_cashflow"])}</td>
              <td class="num">$0</td>
              <td class="num">{fmt(s3["financial_portfolio_end"])}</td>
              <td class="num">{fmt(s3["total_household_wealth_end"])}</td>
              <td>{slink("BOE_LTA_25015", "CA BOE LTA 2025/015 (Full Reassess)")}</td>
            </tr>
            <tr>
              <td><strong>S2B: Live in Cupertino (Prop 19) + Rent All 3 SF Units</strong></td>
              <td>Cupertino (All 3 SF units rented)</td>
              <td class="num">{fmt(s2b["yr1_net_cashflow"])}</td>
              <td class="num">$0</td>
              <td class="num">{fmt(s2b["financial_portfolio_end"])}</td>
              <td class="num">{fmt(s2b["total_household_wealth_end"])}</td>
              <td>{slink("BOE_PUB_801", "CA BOE Pub 801")} · {slink("SF_RENT_BOARD", "SF Rent Board")}</td>
            </tr>
            <tr>
              <td><strong>S2A: Live in Cupertino (Prop 19) + Keep SF Unit 3 Vacant</strong></td>
              <td>Cupertino (2 SF units rented, 1 vacant)</td>
              <td class="num">{fmt(s2a["yr1_net_cashflow"])}</td>
              <td class="num">$0</td>
              <td class="num">{fmt(s2a["financial_portfolio_end"])}</td>
              <td class="num">{fmt(s2a["total_household_wealth_end"])}</td>
              <td>{slink("BOE_PUB_801", "CA BOE Pub 801")} · {slink("IRS_P523", "IRS Pub 523 (§ 121)")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Dashboard Directory by Category</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Category Subpage</th>
              <th>Contents &amp; Verification Scope</th>
              <th>Primary Official Sources Linked</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><a href="properties.html"><strong>Properties &amp; Operating Costs</strong></a></td>
              <td>Line-by-line historical tax &amp; assessment audit (2014–2026 Cupertino; 2016–2026 SF), ad valorem vs. parcel charge split, water, solar NEM sunset, CDI insurance, and maintenance.</td>
              <td>{slink("BOE_LTA_24053", "CA BOE CCPI")} · {slink("SCC_RATES", "SCC Controller")} · {slink("SF_TREASURER", "SF Treasurer")} · {slink("CDI_TOOL", "CA Dept. of Insurance")}</td>
            </tr>
            <tr>
              <td><a href="projections.html"><strong>2026–2050 Yearly Projections</strong></a></td>
              <td>Year-by-year table and multi-series visual chart from 2026 to 2050 for both properties (FMV, Prop 13 FBYV, Prop 19 cap, taxes under live vs. rent, utilities, insurance, NOI) + CSV export.</td>
              <td>{slink("FHFA_HPI", "FHFA 2026Q2 HPI")} · {slink("BOE_LTA_26002", "CA BOE LTA 2026/002")} · {slink("CBO_2026", "CBO 2026 Outlook")}</td>
            </tr>
            <tr>
              <td><a href="scenarios.html"><strong>Live vs. Rent vs. Sell Analysis</strong></a></td>
              <td>2040, 2045, and 2050 inheritance comparisons plus an interactive calculator to test appreciation, portfolio return, horizon, and revocable vs. irrevocable trust assumptions.</td>
              <td>{slink("IRS_RR_2302", "IRS Rev. Rul. 2023-2")} · {slink("BOE_PUB_801", "CA BOE Prop 19")} · {slink("HUD_FMR", "HUD FY26 FMR")}</td>
            </tr>
            <tr>
              <td><a href="estate-tax.html"><strong>Estate, Cash Inheritance &amp; Law Changes</strong></a></td>
              <td>Federal $15,000,000 / $30,000,000 threshold math, exact cash headroom tables (2026–2050), $0 CA/local death tax statutes, and legislative rollback / wealth-tax stress tests.</td>
              <td>{slink("IRS_706", "IRS Form 706")} · {slink("IRS_RP_2532", "IRS Rev. Proc. 2025-32")} · {slink("RTC_13301", "CA RTC § 13301")}</td>
            </tr>
            <tr>
              <td><a href="inheritance-guide.html"><strong>Step-by-Step Trust Inheritance Guide</strong></a></td>
              <td>12-step chronological execution checklist with statutory deadlines (60-day Probate Code notice, 150-day BOE-502-D, 9-month Form 706, 365-day Prop 19 occupancy &amp; BOE-19-P).</td>
              <td>{slink("PROB_16061", "CA Prob. Code § 16061.7")} · {slink("BOE_DEATH", "CA BOE Pub 800-9")} · {slink("RTC_11930", "CA RTC § 11930")}</td>
            </tr>
            <tr>
              <td><a href="flagged-review.html"><strong>Flagged for Review</strong></a></td>
              <td>All unverified blank cells (2026 county bills), user-supplied market/rent estimates, solar NEM sunset risks, SF tax-spike explanations, and cross-session repo audit findings.</td>
              <td>{slink("SCC_ASSESSOR", "SCC Assessor")} · {slink("SF_TREASURER", "SF Treasurer")} · {slink("CPUC_NEM", "CPUC Solar Report")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "index.html",
        "Executive Summary",
        "Executive Decision Dashboard · Nov 2026 Baseline",
        "Cupertino (95014) & San Francisco (94122) Trust Inheritance Analysis",
        "Comprehensive, anonymized, $10-rounded financial and legal decision framework for inheriting real estate and liquid assets by trust between 2040 and 2050.",
        body,
    )


def build_properties_page(d: dict) -> str:
    # Historical tables rounded strictly to $10 for de-identification & clarity; missing 2026 values left blank!
    cup_hist = [
        (2026, None, "—", 550540, "+2.0%", "2.000%", "BOE_LTA_26002", "badge-blank", "Flagged: 2026 tax bill unverified (left blank; never inferred)"),
        (2025, 7210, "+2.9%", 539740, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record ($10-rounded); includes ~$930 fixed parcel charges"),
        (2024, 7000, "+1.2%", 529160, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; assessment growth matches 2.000% BOE CCPI cap"),
        (2023, 6920, "+2.4%", 518790, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap + FUHSD 2022 bond"),
        (2022, 6760, "+1.4%", 508610, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2021, 6660, "+1.5%", 498640, "+1.0%", "1.036%", "BOE_LTA_24053", "badge-verified", "Assessment +1.0% matches exact 1.036% FY21–22 BOE CCPI factor"),
        (2020, 6570, "0.0%", 493500, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "Flagged: Flat tax vs. 2019 despite +2.0% assessment — verify bill"),
        (2019, 6570, "+2.8%", 483850, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2018, 6380, "0.0%", 474370, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "Flagged: Flat tax vs. 2017 despite +2.0% assessment — verify bill"),
        (2017, 6380, "-0.5%", 465070, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2016, 6410, "+4.6%", 455950, "+1.5%", "1.525%", "BOE_LTA_24053", "badge-verified", "Assessment +1.5% matches exact 1.525% FY16–17 BOE CCPI factor"),
        (2015, 6130, "+2.8%", 449100, "+2.0%", "1.998%", "BOE_LTA_24053", "badge-verified", "Assessment +2.0% matches exact 1.998% FY15–16 BOE CCPI factor"),
        (2014, 5970, "—", 440310, "+0.5%", "0.454%", "BOE_LTA_13059", "badge-verified", "Assessment +0.5% matches exact 0.454% FY14–15 BOE CCPI factor"),
    ]

    sf_hist = [
        (2026, None, "—", None, "—", "2.000%", "BOE_LTA_26002", "badge-blank", "Flagged: 2026 SF bill & assessment not provided (left blank)"),
        (2025, 2440, "+5.3%", 114250, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "Apparent 2.14% = 1.1827% ad valorem (~$1,350) + ~$1,090 parcel fees"),
        (2024, 2320, "+6.2%", 112010, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record ($10-rounded); matches 2.000% BOE CCPI cap"),
        (2023, 2180, "+3.4%", 109810, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2022, 2110, "+2.0%", 107660, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2021, 2070, "-5.9%", 105600, "+1.0%", "1.036%", "SF_RENT_BOARD", "badge-verified", "-5.9% drop explained: SF Rent Board fee moved off tax bill in 2022"),
        (2020, 2200, "+3.0%", 104510, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2019, 2130, "+3.5%", 102470, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2018, 2060, "+18.4%", 100460, "+2.0%", "2.000%", "SF_TREASURER", "badge-flagged", "Flagged: +18.4% jump caused by flat SF parcel tax added to low base"),
        (2017, 1740, "+3.9%", 98490, "+2.0%", "2.000%", "BOE_LTA_24053", "badge-flagged", "User record; matches 2.000% BOE CCPI cap"),
        (2016, 1680, "+1.6%", 96560, "+1.5%", "1.525%", "BOE_LTA_24053", "badge-verified", "Assessment +1.5% matches exact 1.525% FY16–17 BOE CCPI factor"),
    ]

    cup_rows_html = ""
    for yr, tax, tax_chg, assd, assd_chg, boe_fac, skey, bcls, note in cup_hist:
        tax_cell = '<td class="blank-cell" title="Unverified — left blank"></td>' if tax is None else f'<td class="num">{fmt(tax)} <small>({tax_chg})</small></td>'
        cup_rows_html += f"""
        <tr>
          <td><strong>{yr}</strong></td>
          {tax_cell}
          <td class="num">{fmt(assd)} <small>({assd_chg})</small></td>
          <td class="num">{boe_fac}</td>
          <td><span class="badge {bcls}">{note}</span></td>
          <td>{slink(skey)} · {slink("SCC_RATES", "SCC Tax Book")}</td>
        </tr>"""

    sf_rows_html = ""
    for yr, tax, tax_chg, assd, assd_chg, boe_fac, skey, bcls, note in sf_hist:
        tax_cell = '<td class="blank-cell" title="Unverified — left blank"></td>' if tax is None else f'<td class="num">{fmt(tax)} <small>({tax_chg})</small></td>'
        assd_cell = '<td class="blank-cell" title="Unverified — left blank"></td>' if assd is None else f'<td class="num">{fmt(assd)} <small>({assd_chg})</small></td>'
        sf_rows_html += f"""
        <tr>
          <td><strong>{yr}</strong></td>
          {tax_cell}
          {assd_cell}
          <td class="num">{boe_fac}</td>
          <td><span class="badge {bcls}">{note}</span></td>
          <td>{slink(skey)} · {slink("SF_TREASURER", "SF Treasurer")}</td>
        </tr>"""

    body = f"""
    <div class="callout callout-amber">
      <strong>Privacy &amp; Verification Note:</strong> Historical parcel dollar amounts are rounded to the nearest <code>$10</code> increment both to meet the clarity mandate and to prevent reverse parcel identification on public county assessment rolls. Unconfirmed 2026 county bills are left <strong>strictly blank</strong> below (never inferred) and published on <a href="flagged-review.html">Flagged for Review</a>.
    </div>

    <div class="card">
      <h2>2026 Baseline Operating Cost &amp; Tax Rate Decomposition (Both Properties)</h2>
      <p>Separating ad valorem percentage rates from flat parcel assessments is critical: upon Prop 19 or rental reassessment, <strong>only the ad valorem rate scales with Fair Market Value</strong>.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Cost / Revenue Line Item</th>
              <th class="num">[Property A] Cupertino (95014)</th>
              <th class="num">[Property B] San Francisco (94122)</th>
              <th>Underwriting &amp; Regulatory Basis</th>
              <th>Official Primary Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Estimated Market Value (Nov 2026)</strong></td>
              <td class="num">$3,100,000</td>
              <td class="num">$1,800,000</td>
              <td>User-supplied baseline (flagged: obtain date-of-death MAI appraisal at inheritance).</td>
              <td>{slink("FHFA_HPI", "FHFA 2026Q2 HPI")}</td>
            </tr>
            <tr>
              <td><strong>Verified Ad Valorem Tax Rate</strong></td>
              <td class="num">1.1636%</td>
              <td class="num">1.1816%</td>
              <td>Cupertino TRA (1% + SCC/CUSD/FUHSD/FHDA/SCVWD bonds); SF FY26–27 secured rate.</td>
              <td>{slink("SCC_RATES", "SCC FY25–26 Book")} · {slink("SF_TREASURER", "SF Treasurer")}</td>
            </tr>
            <tr>
              <td><strong>Fixed Parcel &amp; Direct Charges (2026)</strong></td>
              <td class="num">$950/yr</td>
              <td class="num">$1,110/yr</td>
              <td>Flat school/water/open-space parcel taxes (+ $180/yr gross / $90/yr net direct SF Rent Board fee).</td>
              <td>{slink("SCC_RATES", "SCC Controller")} · {slink("SF_RENT_BOARD", "SF Rent Board")}</td>
            </tr>
            <tr>
              <td><strong>Water &amp; Wastewater (2026)</strong></td>
              <td class="num">$1,560/yr ($130/mo)</td>
              <td class="num">$4,440/yr ($370/mo)</td>
              <td>Cupertino $100–$150/mo (SJW GRC); SF 3 units $330–$400/mo (SFPUC +10.5%–12.5% FY27 hike).</td>
              <td>{slink("CPUC_SJW", "CPUC D.24-12-077")} · {slink("SFPUC_2026", "SFPUC Prop 218")}</td>
            </tr>
            <tr>
              <td><strong>Electricity &amp; Solar (2026 vs. 2038+)</strong></td>
              <td class="num">-$240/yr (now) → +$960/yr (2038)</td>
              <td class="num">$600/yr ($50/mo)</td>
              <td>Cupertino -$10 to -$20/mo solar profit expires at 20-yr NEM sunset + $290/yr flat charge; SF $30–$70/mo.</td>
              <td>{slink("CPUC_NEM", "CPUC EO N-5-24")} · {slink("CPUC_NBT", "CPUC D.24-05-028")}</td>
            </tr>
            <tr>
              <td><strong>Homeowners / Landlord Insurance (2026)</strong></td>
              <td class="num">$2,600/yr (HO-3) / $3,120/yr (DP-3)</td>
              <td class="num">$3,600/yr (3-Unit DP-3)</td>
              <td>CDI CA avg is $1,570/yr; user $1,500 guess is understated for SV rebuild &amp; 3-unit SF habitational policy.</td>
              <td>{slink("CDI_AVG", "CDI Strategy")} · {slink("CDI_TOOL", "CDI 2026 Tool")}</td>
            </tr>
            <tr>
              <td><strong>Maintenance &amp; Capex Reserve (2026)</strong></td>
              <td class="num">$7,800/yr</td>
              <td class="num">$12,600/yr</td>
              <td>Structure rebuild reserve (roof/HVAC/solar inverter in 95014; higher 3-unit coastal fog wear in 94122).</td>
              <td>{slink("CDI_GUIDE", "CDI Rebuild Guide")} · {slink("CBO_2026", "CBO Inflation")}</td>
            </tr>
            <tr>
              <td><strong>Gross Rental Income (2026)</strong></td>
              <td class="num">$0 (or $84,000/yr if rented)</td>
              <td class="num">$85,800/yr ($7,150/mo)</td>
              <td>SF 2 units rented ($7,150/mo) + 1 livable unit vacant; Cupertino SFR benchmark $7,000/mo if leased.</td>
              <td>{slink("HUD_FMR", "HUD FY26 FMR")} · {slink("SF_RENT_BOARD", "SF Rent Cap 1.6%")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>[Property A — Cupertino ZIP 95014] Historical Tax &amp; Assessment Audit (2014–2026)</h2>
      <p>Every assessment change from 2014 to 2026 aligns with the official California BOE Proposition 13 CCPI inflation factor (notably <code>0.454%</code> in 2014, <code>1.525%</code> in 2016, and <code>1.036%</code> in 2021).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Property Tax ($10 Rounded)</th>
              <th class="num">Tax Assessment ($10 Rounded)</th>
              <th class="num">Official BOE Prop 13 Cap</th>
              <th>Line-by-Line Verification Status</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            {cup_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>[Property B — San Francisco Outer Sunset ZIP 94122] Historical Audit (2016–2026)</h2>
      <p>Audit resolves two major anomalies in the raw history: the <code>+18.4%</code> bill jump in 2018 (flat parcel tax addition onto a ~$100,460 Prop 13 base) and the <code>-5.9%</code> bill drop in 2021–2022 (SF Rent Board per-unit fee removed from the secured property tax roll starting in 2022).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Property Tax ($10 Rounded)</th>
              <th class="num">Tax Assessment ($10 Rounded)</th>
              <th class="num">Official BOE Prop 13 Cap</th>
              <th>Line-by-Line Verification Status</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            {sf_rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "properties.html",
        "Properties & Operating Costs",
        "Property Audit & Cost Baseline",
        "Historical Property Tax Audit & Verified Operating Costs (95014 & 94122)",
        "Line-by-line verification of historical assessments against California BOE CCPI multipliers, ad valorem tax rate decomposition, utilities, solar NEM rules, and insurance benchmarks.",
        body,
    )


def build_projections_page(d: dict) -> str:
    cup_rows_html = ""
    for r in d["cupertino_projections"]:
        yr = r["year"]
        in_win = " style='background:#f0f9ff'" if 2040 <= yr <= 2050 else ""
        cup_rows_html += f"""
        <tr{in_win}>
          <td><strong>{yr}</strong>{" <span class='badge badge-projected'>Target Window</span>" if yr in (2040, 2045, 2050) else ""}</td>
          <td class="num">{fmt(r["fmv"])}</td>
          <td class="num">{fmt(r["fbyv_prop13"])}</td>
          <td class="num">{fmt(r["tax_prop13_current"])}</td>
          <td class="num">{fmt(r["prop19_cap"])}</td>
          <td class="num"><strong>{fmt(r["tax_if_inherited_live"])}</strong></td>
          <td class="num">{fmt(r["tax_if_inherited_rent"])}</td>
          <td class="num">{fmt(r["water_yr"])}</td>
          <td class="num">{fmt(r["electric_yr"])}</td>
          <td class="num">{fmt(r["insurance_primary_yr"])}</td>
          <td class="num">{fmt(r["maintenance_yr"])}</td>
          <td class="num"><strong>{fmt(r["total_opex_if_live"])}</strong></td>
          <td>{slink("BOE_PUB_801", "BOE Prop 19")} · {slink("SCC_RATES", "SCC 1.1636%")} · {slink("FHFA_HPI", "FHFA")}</td>
        </tr>"""

    sf_rows_html = ""
    for r in d["sf_projections"]:
        yr = r["year"]
        in_win = " style='background:#f0f9ff'" if 2040 <= yr <= 2050 else ""
        sf_rows_html += f"""
        <tr{in_win}>
          <td><strong>{yr}</strong>{" <span class='badge badge-projected'>Target Window</span>" if yr in (2040, 2045, 2050) else ""}</td>
          <td class="num">{fmt(r["fmv"])}</td>
          <td class="num">{fmt(r["fbyv_prop13"])}</td>
          <td class="num">{fmt(r["tax_prop13_current"])}</td>
          <td class="num">{fmt(r["water_sewer_yr"])}</td>
          <td class="num">{fmt(r["electric_yr"])}</td>
          <td class="num">{fmt(r["insurance_yr"])}</td>
          <td class="num">{fmt(r["maintenance_yr"])}</td>
          <td class="num">{fmt(r["total_opex_prop13"])}</td>
          <td class="num">{fmt(r["gross_rent_2units_yr"])}</td>
          <td class="num"><strong>{fmt(r["net_cashflow_2units_prop13"])}</strong></td>
          <td>{slink("SF_TREASURER", "SF 1.1816%")} · {slink("SFPUC_2026", "SFPUC")} · {slink("SF_RENT_BOARD", "SF Rent Board")}</td>
        </tr>"""

    body = f"""
    <div class="card">
      <h2>Visual Trajectory: Property Market Values &amp; Cupertino Tax Regimes (2026–2050)</h2>
      <p>Interactive SVG projection comparing <code>[Property A — Cupertino 95014]</code> and <code>[Property B — San Francisco 94122]</code> valuations alongside the Prop 13 vs. Prop 19 vs. Full Reassessment property tax cliff upon inheritance (2040–2050 shaded).</p>
      <div class="grid-2">
        <div class="chart-box">
          <h3>Projected Market Value vs. Prop 13 Assessed Base (2026–2050)</h3>
          <div class="chart-legend">
            <span><span class="legend-dot" style="background:#0284c7"></span>Cupertino FMV (4.2%/yr)</span>
            <span><span class="legend-dot" style="background:#059669"></span>SF 3-Unit FMV (3.5%/yr)</span>
            <span><span class="legend-dot" style="background:#64748b"></span>Cupertino Prop 13 Base (2.0%/yr)</span>
          </div>
          <div id="chart-values"></div>
        </div>
        <div class="chart-box">
          <h3>Cupertino Annual Property Tax: Prop 13 vs. Prop 19 Live-In vs. Rental</h3>
          <div class="chart-legend">
            <span><span class="legend-dot" style="background:#dc2626"></span>If Rented (Full FMV Tax)</span>
            <span><span class="legend-dot" style="background:#d97706"></span>If Lived In (Prop 19 Partial)</span>
            <span><span class="legend-dot" style="background:#059669"></span>Pre-Inheritance Prop 13</span>
          </div>
          <div id="chart-taxes"></div>
        </div>
      </div>
      <div style="display:flex;gap:0.75rem;flex-wrap:wrap;align-items:center">
        <button type="button" class="btn btn-primary" id="btn-download-csv">Download Full 2026–2050 Projections CSV ($10 Rounded)</button>
        <span style="font-size:0.82rem;color:var(--text-muted)">Note: Cupertino electricity flips from net solar credit (<code>-$240/yr</code>) to net cost (<code>+$960/yr</code>+) in 2038 upon modeled 20-year CPUC NEM 2.0 sunset + mandatory fixed charge.</span>
      </div>
    </div>

    <div class="card">
      <h2>[Property A — Cupertino 95014] Year-by-Year Projections (2026–2050 · Rounded to $10)</h2>
      <p>Columns <em>Tax (Inherit Live)</em> and <em>Tax (Inherit Rent)</em> show the Year-1 property tax that locks in if trust transfer occurs in that specific year.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Est. Market Value</th>
              <th class="num">Prop 13 Base</th>
              <th class="num">Prop 13 Tax</th>
              <th class="num">Prop 19 Cap</th>
              <th class="num">Tax (Inherit Live)</th>
              <th class="num">Tax (Inherit Rent)</th>
              <th class="num">Water</th>
              <th class="num">Solar/Elec</th>
              <th class="num">HO-3 Ins.</th>
              <th class="num">Maint.</th>
              <th class="num">Total Cost (If Live)</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>
            {cup_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>[Property B — San Francisco 94122] Year-by-Year Projections (2026–2050 · Rounded to $10)</h2>
      <p>Assumes existing Prop 13 base continues while 2 units remain rented and 1 livable unit remains available for primary residence occupancy (if <code>[Property B]</code> were also inherited via parent-child transfer, 2/3 rental share would reassess to FMV per <code>BOE LTA 2026/026</code> — e.g., <strong>{fmt(d["sf_projections"][19]["tax_if_also_inherited_2of3_reassessed"])}/yr</strong> tax in 2045).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Est. Market Value</th>
              <th class="num">Prop 13 Base</th>
              <th class="num">Prop 13 Tax</th>
              <th class="num">Water &amp; Sewer</th>
              <th class="num">Electric</th>
              <th class="num">3-Unit Ins.</th>
              <th class="num">Maint.</th>
              <th class="num">Total OpEx (incl. RB Fee)</th>
              <th class="num">2-Unit Gross Rent</th>
              <th class="num">Pre-Tax Net Cash Flow</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>
            {sf_rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "projections.html",
        "2026–2050 Projections",
        "25-Year Financial & Tax Trajectory",
        "Year-by-Year Property Value, Assessment, Tax & Utility Projections (2026–2050)",
        "Every figure is rounded to the nearest $10 increment and anchored to CA BOE Prop 13/19 rules, Santa Clara & SF ad valorem schedules, CPUC/SFPUC tariffs, CDI insurance data, and FHFA/CBO benchmarks.",
        body,
    )


def build_scenarios_page(d: dict) -> str:
    milestone_rows = ""
    for yr_key in ("2040", "2045", "2050"):
        sc = d["decision_scenarios"][yr_key]
        for st in sc["strategies"]:
            is_best = st["id"] == "S1"
            milestone_rows += f"""
            <tr{" style='background:#ecfdf5'" if is_best else ""}>
              <td><strong>{sc["inherit_year"]} → {sc["end_year"]}</strong></td>
              <td><strong>{st["id"]}</strong>: {st["name"]}{" <span class='badge badge-verified'>Optimal</span>" if is_best else ""}</td>
              <td class="num">{fmt(sc["cupertino_fmv_at_inheritance"])}</td>
              <td class="num">{fmt(sc["cupertino_yr1_tax_if_live"] if "Live in Cupertino" in st["name"] else (0 if st["id"] == "S1" else sc["cupertino_yr1_tax_if_rent"]))}</td>
              <td class="num">{fmt(st["yr1_net_cashflow"])}</td>
              <td class="num">{fmt(st["financial_portfolio_end"])}</td>
              <td class="num"><strong>{fmt(st["total_household_wealth_end"])}</strong></td>
              <td>{slink("IRS_RR_2302", "IRC § 1014")} · {slink("BOE_PUB_801", "BOE Prop 19")}</td>
            </tr>"""

    body = f"""
    <div class="card">
      <h2>Interactive Scenario Explorer (Customize Inheritance Year, Returns &amp; Trust Type)</h2>
      <p>Adjust any assumption below to stress-test the decision in real time. All outputs automatically round to the nearest <code>$10</code> increment.</p>
      <div class="controls-bar">
        <div class="control-group">
          <label for="sim-year">Inheritance Year: <span id="lbl-sim-year">2045</span></label>
          <input type="range" id="sim-year" min="2040" max="2050" step="1" value="2045">
        </div>
        <div class="control-group">
          <label for="sim-horizon">Post-Inheritance Horizon: <span id="lbl-sim-horizon">15</span> yrs</label>
          <input type="range" id="sim-horizon" min="10" max="25" step="5" value="15">
        </div>
        <div class="control-group">
          <label for="sim-cup-g">Cupertino Home Growth: <span id="lbl-sim-cup-g">4.2%</span>/yr</label>
          <input type="range" id="sim-cup-g" min="2.5" max="5.5" step="0.1" value="4.2">
        </div>
        <div class="control-group">
          <label for="sim-port-r">After-Tax Portfolio Return: <span id="lbl-sim-port-r">5.8%</span>/yr</label>
          <input type="range" id="sim-port-r" min="3.5" max="8.0" step="0.1" value="5.8">
        </div>
        <div class="control-group">
          <label for="sim-trust">Trust Basis Treatment</label>
          <select id="sim-trust">
            <option value="revocable" selected>Revocable Living Trust (100% IRC § 1014 Step-Up)</option>
            <option value="irrevocable">Estate-Excluded Irrevocable Trust (No Step-Up — Rev. Rul. 2023-2)</option>
          </select>
        </div>
      </div>

      <div id="sim-verdict-banner" class="callout callout-emerald"></div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Strategy</th>
              <th class="num">Day-1 Net Sale Cash</th>
              <th class="num">Yr-1 Cupertino Prop Tax</th>
              <th class="num">Yr-1 Household Prop Cash Flow</th>
              <th class="num">Terminal Financial Portfolio</th>
              <th class="num">Terminal Total Net Worth</th>
              <th>Official Tax / Legal Authority</th>
            </tr>
          </thead>
          <tbody id="sim-results-tbody"></tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Baseline Benchmark Comparison Across 2040, 2045 &amp; 2050 (15-Year Post-Inheritance Horizon)</h2>
      <p>Assumes Revocable Trust (full <code>IRC § 1014</code> basis step-up at death), 4.2%/yr Cupertino appreciation, 3.5%/yr SF appreciation, and 5.8%/yr after-tax balanced portfolio compounding (7.0% pre-tax).</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Window</th>
              <th>Household Strategy</th>
              <th class="num">Cupertino FMV at Death</th>
              <th class="num">Yr-1 Cupertino Tax</th>
              <th class="num">Yr-1 Property Net CF</th>
              <th class="num">End Financial Portfolio</th>
              <th class="num">End Total Net Worth</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>
            {milestone_rows}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Why "Sell Cupertino &amp; Live in San Francisco" (S1) Wins — And When "Live in Cupertino" (S2B) Makes Sense</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Decision Factor</th>
              <th>Sell Cupertino &amp; Reinvest + Live in SF (S1)</th>
              <th>Live in Cupertino + Keep SF (S2A / S2B)</th>
              <th>Rent Out Cupertino + Live in SF (S3)</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Capital Gains Tax Efficiency</strong></td>
              <td><strong>Maximum:</strong> Captures 100% tax-free step-up at death (<code>IRC § 1014</code>); avoids future 37.1% tax on post-death home gains above $250,000/$500,000.</td>
              <td><strong>Moderate:</strong> Post-inheritance appreciation above <code>IRC § 121</code> ($250,000 single / $500,000 MFJ) faces up to 37.1% combined tax if later sold.</td>
              <td><strong>Poor:</strong> Loses <code>IRC § 121</code> exclusion; post-death gain taxed up to 37.1% plus 25% federal + 13.3% CA depreciation recapture.</td>
              <td>{slink("IRS_TC409", "IRS Topic 409")} · {slink("IRS_P523", "IRS Pub 523")} · {slink("FTB_CAP", "CA FTB")}</td>
            </tr>
            <tr>
              <td><strong>Property Tax Burden</strong></td>
              <td><strong>Lowest ($3,600/yr SF in 2045):</strong> Zero Cupertino tax; retains ultra-low Prop 13 base on SF 3-unit property.</td>
              <td><strong>High ($55,940/yr Cup in 2045):</strong> Prop 19 saves $24,270/yr vs. renting, but still imposes a 5.3x tax jump.</td>
              <td><strong>Highest ($80,210/yr Cup in 2045):</strong> 100% full market reassessment on Cupertino.</td>
              <td>{slink("BOE_PUB_801", "CA BOE Pub 801")} · {slink("SCC_RATES", "SCC Controller")}</td>
            </tr>
            <tr>
              <td><strong>When to Choose This Plan</strong></td>
              <td>Choose when <strong>maximizing net worth, liquidity, and passive income</strong> is the primary objective.</td>
              <td>Choose <strong>only</strong> if non-financial lifestyle/school preference for living in Cupertino outweighs ~$260,000–$380,000/yr in opportunity cost (or if an Irrevocable Trust blocks § 1014 step-up!).</td>
              <td><strong>Avoid</strong> unless Cupertino home appreciation exceeds ~6.5%/yr while stock returns fall below 4.0%/yr.</td>
              <td>{slink("IRS_RR_2302", "IRS Rev. Rul. 2023-2")} · {slink("CBO_2026", "CBO Outlook")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "scenarios.html",
        "Decision Scenarios",
        "Live vs. Rent vs. Sell & Reinvest",
        "Household Strategy Comparison & Interactive Decision Simulator",
        "Side-by-side cash-flow and net-worth modeling across 2040, 2045, and 2050 inheritance horizons — integrating both Cupertino (95014) and San Francisco (94122).",
        body,
    )


def build_estate_tax_page(d: dict) -> str:
    est_rows_html = ""
    for r in d["estate_tax_thresholds"]:
        est_rows_html += f"""
        <tr>
          <td><strong>{r["year"]}</strong></td>
          <td class="num">{fmt(r["fed_exclusion_single"])}</td>
          <td class="num">{fmt(r["fed_exclusion_married_portability"])}</td>
          <td class="num">{fmt(r["cupertino_fmv"])}</td>
          <td class="num">{fmt(r["both_properties_fmv"])}</td>
          <td class="num"><strong>{fmt(r["tax_free_cash_headroom_single_cup_only"])}</strong></td>
          <td class="num">{fmt(r["tax_free_cash_headroom_single_both_props"])}</td>
          <td class="num"><strong>{fmt(r["tax_free_cash_headroom_married_both_props"])}</strong></td>
          <td class="num">{fmt(r["rollback_stress_cash_headroom_single_cup_only"])}</td>
          <td>{slink("IRS_706", "IRS Form 706")} · {slink("IRS_RP_2532", "Rev. Proc. 2025-32")} · {slink("RTC_13301", "CA RTC § 13301")}</td>
        </tr>"""

    body = f"""
    <div class="callout callout-emerald">
      <strong>How Much Money + Real Estate Can Be Inherited Tax-Free?</strong>
      Under current law enacted in <strong>Public Law 119-21 § 70106 (OBBBA)</strong> and confirmed in <strong>IRS Rev. Proc. 2025-32</strong>, the 2026 Federal Estate &amp; Gift Tax Basic Exclusion is <strong>$15,000,000 per individual</strong> (<strong>$30,000,000 for a married couple</strong> filing <code>Form 706</code> to elect Deceased Spousal Unused Exclusion [DSUE] portability), indexed for inflation starting in 2027. California State and local governments (Cupertino, Santa Clara County, San Francisco) impose <strong>$0 inheritance tax and $0 estate tax</strong> at any dollar threshold (<code>CA RTC § 13301</code>). Above the federal threshold, the estate pays a flat <strong>40% marginal tax</strong> on the excess.
    </div>

    <div class="card">
      <h2>Projected Tax-Free Cash &amp; Financial Asset Headroom Above Real Estate (2026–2050)</h2>
      <p>Because federal estate tax applies to the <strong>combined gross estate</strong> (real estate Fair Market Value at death + cash, brokerage, bonds, life insurance owned by decedent, and retirement accounts), the table below shows exactly <strong>how much additional cash/securities can be inherited before incurring $10 of federal estate tax</strong>.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th class="num">Fed Exemption (1 Grantor)</th>
              <th class="num">Fed Exemption (Married DSUE)</th>
              <th class="num">Cupertino FMV</th>
              <th class="num">Cupertino + SF FMV</th>
              <th class="num">Tax-Free Cash Headroom (1 Grantor, Cup Only)</th>
              <th class="num">Tax-Free Cash Headroom (1 Grantor, Both Props)</th>
              <th class="num">Tax-Free Cash Headroom (Married, Both Props)</th>
              <th class="num">Stress-Test Cash Headroom ($7,000,000 Rollback)</th>
              <th>Official Sources</th>
            </tr>
          </thead>
          <tbody>
            {est_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Federal, California State &amp; Local Tax Rules Governing Cash + Property Inheritance</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tax Layer</th>
              <th>2026 Threshold &amp; Rate ($10 Rounded)</th>
              <th>Impact on Inherited Cash, Securities &amp; Real Estate</th>
              <th>Official Statutory Source</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Federal Estate Tax (<code>IRC §§ 2001, 2010</code>)</strong></td>
              <td><strong>$15,000,000</strong> single / <strong>$30,000,000</strong> married; <strong>40%</strong> top rate above threshold</td>
              <td>Paid by the estate/trust on <code>Form 706</code> within 9 months of death. Cash &amp; brokerage securities receive full step-up (cash basis = face value; stocks = date-of-death mean price).</td>
              <td>{slink("IRS_706", "IRS Form 706 (07/2026)")} · {slink("IRS_RP_2532", "Rev. Proc. 2025-32")}</td>
            </tr>
            <tr>
              <td><strong>Inherited Retirement Accounts (<code>IRC § 401(a)(9)</code>)</strong></td>
              <td>Included in estate value; <strong>10-year payout rule</strong> for non-spouse beneficiaries</td>
              <td>Important exception: Traditional IRA / 401(k) balances do <strong>not</strong> receive an income-tax step-up (Income in Respect of a Decedent, <code>IRC § 691</code>); distributions are taxed as ordinary Fed + CA income (Roth IRAs distribute tax-free).</td>
              <td>{slink("IRS_706", "IRS Form 706 Instructions")} · {slink("FTB_CAP", "CA FTB PIT Rates")}</td>
            </tr>
            <tr>
              <td><strong>Federal Annual Gift Exclusion (<code>IRC § 2503(b)</code>)</strong></td>
              <td><strong>$19,000/yr</strong> per recipient per donor (<strong>$38,000/yr</strong> married couple)</td>
              <td>If total estate approaches the federal limit, parents can gift cash/liquid assets annually (+ unlimited direct tuition/medical payments under <code>IRC § 2503(e)</code>) without touching the $15,000,000 exemption, while keeping low-basis Cupertino real estate in the revocable trust for the § 1014 step-up!</td>
              <td>{slink("IRS_RP_2532", "IRS Rev. Proc. 2025-32")}</td>
            </tr>
            <tr>
              <td><strong>California Inheritance &amp; Estate Tax (<code>CA RTC §§ 13301–13302</code>)</strong></td>
              <td><strong>$0</strong> threshold penalty · <strong>0%</strong> tax rate</td>
              <td>Proposition 6 (1982) abolished CA inheritance and gift taxes and barred local governments from imposing death taxes. Enacting a CA estate tax would require a statewide voter ballot measure.</td>
              <td>{slink("RTC_13301", "CA RTC § 13301")} · {slink("RTC_13302", "CA RTC § 13302")}</td>
            </tr>
            <tr>
              <td><strong>Documentary Transfer Tax at Death vs. Sale (<code>CA RTC §§ 11930, 11911</code>)</strong></td>
              <td><strong>$0</strong> upon trust inheritance; <strong>0.11%</strong> SCC / <strong>0.75%–2.25%</strong> SF upon sale</td>
              <td><code>RTC § 11930</code> exempts deeds distributing trust/inherited realty for zero consideration. Selling Cupertino later incurs only 0.11% county transfer tax ($7,450 on $6,774,050 in 2045), whereas selling SF between $5,000,000 and $10,000,000 incurs 2.25% SF transfer tax!</td>
              <td>{slink("RTC_11930", "CA RTC § 11930")} · {slink("RTC_11911", "CA RTC § 11911")} · {slink("SF_ASSESSOR_TT", "SF Transfer Tax")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>Legislative &amp; Policy Proposals Monitored Through 2040–2050</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Policy / Proposal Area</th>
              <th>Potential Change Discussed</th>
              <th>Impact on Decision Plan &amp; Mitigation</th>
              <th>Official Reference</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Federal Estate Exemption Rollback</strong></td>
              <td>Future Congresses have proposed reducing the basic exclusion back to $3,500,000–$7,000,000 and raising top rates to 45%–55%.</td>
              <td>Under a $7,000,000 rollback (indexed to ~$10,680,000 in 2045), a single parent owning Cupertino ($6,774,050) would have only <strong>$3,900,000</strong> of cash headroom before 40%+ estate tax. <strong>Mitigation:</strong> File <code>Form 706</code> DSUE portability at first spouse's death and gift high-basis cash/treasuries first, never low-basis real estate.</td>
              <td>{slink("IRS_706", "IRS Form 706 DSUE")} · {slink("IRS_RP_2532", "OBBBA P.L. 119-21")}</td>
            </tr>
            <tr>
              <td><strong>Repeal or Cap on <code>IRC § 1014</code> Step-Up at Death</strong></td>
              <td>Periodic federal budget proposals have floated taxing unrealized gains at death above a $5,000,000 per-person exclusion (with primary-residence exemptions).</td>
              <td>If <code>§ 1014</code> were capped, holding vs. selling would face symmetrical realization rules, increasing the relative value of deferring sale via living in Cupertino (S2B). Monitor federal tax bills prior to 2040.</td>
              <td>{slink("IRS_TC409", "IRS Topic 409")} · {slink("IRS_RR_2302", "IRS Rev. Rul. 2023-2")}</td>
            </tr>
            <tr>
              <td><strong>California Prop 19 Amendment / Repeal Initiatives</strong></td>
              <td>Taxpayer groups have repeatedly sought ballot initiatives to restore pre-2021 Prop 58 parent-child exclusions (while other proposals target Prop 13 commercial rolls).</td>
              <td>If Prop 58 were ever restored by CA voters before 2040–2050, Cupertino's parent-child primary residence tax would stay near ~$10,630/yr (and up to $1,000,000 of assessed rental value could be excluded), dramatically improving S2 and S3. Under current law, plan strictly for Prop 19.</td>
              <td>{slink("BOE_PUB_801", "CA BOE Pub 801")} · {slink("BOE_LTA_25015", "CA BOE LTA 2025/015")}</td>
            </tr>
            <tr>
              <td><strong>California Wealth / Estate Tax Proposals</strong></td>
              <td>Periodic CA legislative bills (e.g., proposed wealth taxes or estate taxes above $15,000,000–$30,000,000) require statewide voter repeal of Prop 6 (<code>RTC § 13301</code>).</td>
              <td>Currently <strong>not enacted ($0 tax)</strong>; any future ballot measure would appear on a statewide November election ballot with advance planning runway.</td>
              <td>{slink("RTC_13301", "CA RTC § 13301")}</td>
            </tr>
            <tr>
              <td><strong>CPUC Solar NEM Legacy Shortening &amp; Fixed Charges</strong></td>
              <td>In Feb 2025 (<code>EO N-5-24</code> response), CPUC staff identified shortening the 20-year NEM 1.0/2.0 legacy period as an option to reduce non-solar ratepayer cost shifts, alongside the 2026 flat charge.</td>
              <td>Reinforces our model's refusal to project perpetual solar profits into 2040–2050. Budget ~$960–$1,450/yr post-NEM electricity or battery storage capex.</td>
              <td>{slink("CPUC_NEM", "CPUC EO N-5-24 Report")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "estate-tax.html",
        "Estate & Tax Laws",
        "Federal, State & Local Tax Law Hub",
        "Cash + Real Estate Inheritance Thresholds, Trust Step-Up & Legislative Outlook",
        "Exact federal estate tax cash-headroom projections (2026–2050), California $0 death-tax statutes, Revocable vs. Irrevocable Trust basis mechanics, and policy change stress tests.",
        body,
    )


def build_guide_page() -> str:
    steps = [
        (1, "Pre-Inheritance Audit (2026–2039)", "Confirm Revocable Trust Title & Portability Plan", "Verify <code>[Property A — Cupertino 95014]</code> is titled in <code>[Family Revocable Living Trust]</code> (preserving <code>IRC § 1014</code> step-up and avoiding CA statutory probate fees on $3,100,000+ gross value), confirm solar PTO interconnection date, and ensure married <code>[Grantors]</code> plan to file <code>Form 706</code> at first death to lock in $15,000,000+ DSUE portability.", "IRS_RR_2302", "IRS_706"),
        (2, "Days 1–15 Post-Death", "Obtain Certified Death Certificates & Locate Trust Instrument", "Order 10–15 certified death certificates through the County Health Department / mortuary; locate the executed <code>[Family Trust]</code>, all amendments, and property deeds.", "BOE_DEATH", "PROB_16061"),
        (3, "Within 60 Days of Death", "Serve Mandatory Statutory Notice by Trustee (<code>Prob. Code § 16061.7</code>)", "<code>[Successor Trustee]</code> must serve formal <code>§ 16061.7</code> Notification by Trustee on all trust beneficiaries and legal heirs within 60 days of settlor's death (starts the 120-day trust contest statute of limitations under <code>§ 16061.8</code>).", "PROB_16061", "BOE_DEATH"),
        (4, "Days 30–60 Post-Death", "Obtain Trust EIN (<code>IRS Form SS-4</code>) & Execute Certification of Trust", "Because the revocable trust becomes irrevocable at the settlor's death, apply online for a dedicated Trust EIN (do not use decedent's SSN for post-death interest/rent) and execute a <code>Certification of Trust</code> (<code>CA Prob. Code § 18100.5</code>) for financial institutions.", "IRS_706", "PROB_16061"),
        (5, "Days 30–90 Post-Death", "Update Insurance, Utilities & SF Rent Board Portal Immediately", "Notify the homeowners insurer on <code>[Property A]</code> immediately upon death (vacant/trust-administered homes risk coverage lapse without a vacancy/trust endorsement!), maintain water/PG&E service, and keep <code>[Property B]</code> Rent Board housing inventory current.", "CDI_GUIDE", "SF_RENT_BOARD"),
        (6, "Within 150 Days of Death", "File Change in Ownership Statement — Death of Real Property Owner (<code>BOE-502-D</code>)", "Under <code>CA RTC § 480(b)</code>, the trustee must file <code>Form BOE-502-D</code> with the Santa Clara County Assessor (and SF Assessor-Recorder if SF is in the decedent's trust) within 150 days of death to avoid statutory penalties.", "BOE_DEATH", "SCC_ASSESSOR"),
        (7, "Months 2–6 Post-Death", "Commission Certified Date-of-Death Real Estate Appraisal (<code>IRC § 1014</code>)", "Hire a licensed MAI / certified residential appraiser to document retroactive Date-of-Death Fair Market Value for <code>[Property A]</code> (and <code>[Property B]</code> if included). This establishes indisputable stepped-up tax basis under <code>IRC § 1014</code> and consistent-basis reporting on <code>Form 8971</code>.", "IRS_706", "IRS_TC409"),
        (8, "Months 3–6 Post-Death", "Execute Strategic Decision: Sell & Reinvest (S1) vs. Move In Under Prop 19 (S2)", "Compare appraisal FMV, prevailing interest/market conditions, and household residency preference using the <a href='scenarios.html'>Scenario Simulator</a>. Note: if selling (S1), the trust itself can sell directly from successor trustee title or distribute first.", "BOE_PUB_801", "IRS_RR_2302"),
        (9, "Within 9 Months of Death", "File Federal Estate Tax Return (<code>IRS Form 706</code>) & Final Income Returns", "If gross estate (real estate + cash/securities) exceeds the federal exclusion ($15,000,000+ indexed) — OR to elect spousal DSUE portability on a first spouse's death — file <code>Form 706</code> within 9 months (6-month automatic filing extension via <code>Form 4768</code>; tax payment still due at 9 months). Also file decedent's final <code>Form 1040</code> / <code>CA Form 540</code> and fiduciary <code>Form 1041</code> / <code>CA Form 541</code>.", "IRS_706", "FTB_CAP"),
        (10, "CRITICAL: Within 1 Year (365 Days) of Death", "Prop 19 Occupancy + <code>BOE-266</code> + <code>BOE-19-P</code> (ONLY If Choosing Strategy S2)", "If keeping <code>[Property A]</code> as primary residence, <code>[Beneficiary]</code> <strong>must physically move in within 365 days of date of death</strong> and file <code>Form BOE-266</code> (Homeowners' Exemption) + <code>Form BOE-19-P</code> (Parent-Child Exclusion) with the Santa Clara County Assessor to receive full retroactive partial exclusion from date of death.", "BOE_19P", "BOE_LTA_25015"),
        (11, "Months 6–12 Post-Death", "Record Affidavit of Death of Trustee & Trust Distribution Deed (<code>RTC § 11930</code>)", "Record <code>Affidavit of Death of Trustee</code> with certified death certificate and Preliminary Change of Ownership Report (<code>BOE-502-A</code>). Cite <code>CA Rev. & Tax. Code § 11930</code> on the deed face for <strong>$0 Documentary Transfer Tax</strong> (and claim <code>SB 2</code> exemption if owner-occupied).", "RTC_11930", "SCC_ASSESSOR"),
        (12, "Months 6–15 Post-Death", "Close Sale & Reinvest (S1) OR Establish Property Reserve Escrows (S2/S3)", "Under Strategy S1, sell <code>[Property A]</code> with ~$0 capital gains tax (deducting selling costs for a modest capital loss carryforward if sold near date-of-death FMV!), deploy proceeds into a diversified low-cost ETF/Treasury allocation, and occupy <code>[Property B — SF Unit 3]</code>.", "IRS_TC409", "FED_H15"),
    ]

    rows_html = ""
    for num, window, title, detail, s1, s2 in steps:
        rows_html += f"""
        <tr>
          <td><span class="step-num">{num}</span></td>
          <td><strong>{window}</strong></td>
          <td><strong>{title}</strong></td>
          <td>{detail}</td>
          <td>{slink(s1)} · {slink(s2)}</td>
        </tr>"""

    body = f"""
    <div class="callout callout-amber">
      <strong>Two Non-Negotiable Deadlines Upon Inheritance:</strong>
      <strong>(1) 150 Days:</strong> County Assessor notification (<code>Form BOE-502-D</code> under <code>CA RTC § 480(b)</code>).
      <strong>(2) 365 Days (1 Year):</strong> Physical move-in + <code>BOE-266</code> Homeowners' Exemption + <code>BOE-19-P</code> filing if claiming the Proposition 19 partial reassessment exclusion on <code>[Property A — Cupertino 95014]</code> (missing the 1-year deadline forfeits retroactive relief back to date of death!).
    </div>

    <div class="card">
      <h2>12-Step California Trust Real Estate &amp; Cash Inheritance Playbook</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Step</th>
              <th>Statutory Window</th>
              <th>Action Milestone</th>
              <th>Anonymized Execution Details &amp; Filing Forms</th>
              <th>Official Statutory Sources</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "inheritance-guide.html",
        "Step-by-Step Trust Guide",
        "Trust Administration Timeline",
        "Step-by-Step Process for Inheriting California Real Estate & Assets by Trust",
        "Chronological statutory roadmap from pre-inheritance trust verification through county recording, IRS basis documentation, Prop 19 deadlines, and reinvestment execution.",
        body,
    )


def build_flagged_page() -> str:
    flags = [
        ("FLG-01", "Unverified — Left Blank", "[Property A] 2026 Billed Property Tax (`--`)", "User-provided Cupertino table listed `--` for 2026 property taxes alongside $550,540 ($10-rounded) assessed value. Per strict verification rules, the 2026 actual billed tax cell is left blank in historical tables (modeled separately at $7,340 in forward projections).", "SCC_RATES", "SCC_ASSESSOR"),
        ("FLG-02", "Unverified — Left Blank", "[Property B] 2026 Billed Tax & Roll Assessment", "User-provided San Francisco table ended at 2025 ($2,440 tax / $114,250 assessment, $10-rounded). Both 2026 historical cells are left strictly blank and never inferred.", "SF_TREASURER", "BOE_LTA_26002"),
        ("FLG-03", "User Estimate — Needs Appraisal", "Nov 2026 Market Valuations ($3,100,000 Cupertino / $1,800,000 SF)", "Current market values are owner estimates, not certified appraisals. At trust inheritance, a formal Date-of-Death MAI appraisal is required to substantiate IRC § 1014 basis and Form 706 / 8971 reporting.", "FHFA_HPI", "IRS_706"),
        ("FLG-04", "User Guess — Understated Quote", "Insurance Guesses ($1,500/yr Cupertino & $1,500/yr SF 3-Unit Rental)", "CDI statewide HO-3 average is $1,570/yr, and insuring Silicon Valley structure replacement cost (~$1,000,000–$1,300,000) plus a 3-unit SF rental building (DP-3 + $85,800/yr loss-of-rents + landlord liability) typically costs ~$2,600/yr (Cupertino) and ~$3,600/yr (SF). Obtain carrier quotes via CDI's tool.", "CDI_TOOL", "CDI_AVG"),
        ("FLG-05", "Tariff Sunset Irregularity", "Cupertino Solar Credit (-$10 to -$20/mo) Expires Before/During 2040–2050", "CPUC NEM 1.0/2.0 retail export grandfathering lasts 20 years from interconnection (D.22-12-056), defaulting systems onto NBT (~75% lower export rates), while D.24-05-028 adds a ~$290/yr flat monthly charge. Verify PTO year and budget inverter/battery capex.", "CPUC_NEM", "CPUC_NBT"),
        ("FLG-06", "Tax Bill Irregularity Explained", "SF Historical Tax Anomalies (+18.4% in 2018; -5.9% in 2021; 2.14% Implied Rate)", "SF's official FY26–27 ad valorem rate is 1.18162182%, NOT 2.14%. Because assessed value is ~$114,250, ~$1,090 of fixed parcel charges make the ratio look like 2.14%. Also, the -5.9% drop in 2021–2022 reflects SF moving the per-unit Rent Board fee off the property tax roll to direct billing.", "SF_TREASURER", "SF_RENT_BOARD"),
        ("FLG-07", "Historical Record Anomaly", "Cupertino Identical Tax Bills in 2017–2018 ($6,380) and 2019–2020 ($6,570)", "Despite +2.0% Prop 13 assessment increases in 2018 and 2020, user-supplied tax bills were flat year-over-year — likely reflecting bond rate offsets or third-party portal rounding. Cross-check original Santa Clara County DTAC bills.", "SCC_RATES", "BOE_LTA_24053"),
        ("FLG-08", "Legal Ownership Clarification", "Confirm Whether [Property B — SF 94122] Is Already Beneficiary-Owned vs. Also in Parents' Trust", "User prompt notes having SF 94122 to live in without losing $7,150/mo rent. If [Beneficiary] already holds title to SF, its $116,530 Prop 13 base stays intact; if SF is ALSO inherited from parents' trust, the 2 rental units undergo mandatory 2/3 FMV reassessment under BOE LTA 2026/026!", "BOE_LTA_26026", "SF_TREASURER"),
        ("FLG-09", "Trust Structure Verification", "Verify Revocable vs. Irrevocable Trust Status (`IRC § 1014` vs. `Rev. Rul. 2023-2`)", "If Cupertino were held in an estate-tax-excluded Irrevocable Grantor Trust, IRS Rev. Rul. 2023-2 denies basis step-up at death, creating a ~$1,674,100 to ~$2,604,290 capital gains tax liability if sold in 2040–2050.", "IRS_RR_2302", "FTB_CAP"),
        ("FLG-10", "Cross-Session Repo Audit", "Prior-Session Files Logged via Change Requests (`CR-85-1`..`CR-85-6`)", "Line-by-line repo audit identified commercial aggregator links, unrounded parcel figures, unsourced table rows, and unseparated 2.14% SF tax rates in earlier parallel-session directories; logged in COORDINATION.md and corrected in `site/`.", "BOE_LTA_24053", "IRS_RP_2532"),
    ]

    rows_html = ""
    for fid, status, item, desc, s1, s2 in flags:
        bcls = "badge-blank" if "Blank" in status else "badge-flagged"
        rows_html += f"""
        <tr>
          <td><code>{fid}</code></td>
          <td><span class="badge {bcls}">{status}</span></td>
          <td><strong>{item}</strong></td>
          <td>{desc}</td>
          <td>{slink(s1)} · {slink(s2)}</td>
        </tr>"""

    body = f"""
    <div class="callout callout-rose">
      <strong>Audit &amp; Review Policy:</strong> Every item below was flagged during line-by-line verification of the user's records and repository files. Unverifiable values are left blank in historical tables rather than inferred; planning assumptions in forward projections are explicitly separated and linked to official primary sources for manual review.
    </div>

    <div class="card">
      <h2>Master Register of Flagged Irregularities &amp; Unverified Items</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Flag ID</th>
              <th>Verification Status</th>
              <th>Item / Field</th>
              <th>Detailed Finding &amp; Action Required</th>
              <th>Official Verification Links</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "flagged-review.html",
        "Flagged for Review",
        "Verification & Irregularity Log",
        "Flagged for Review — Unverified Items, Anomalies & Audit Register",
        "Complete register of blank unverified county tax cells, owner estimates requiring formal quotes/appraisals, utility sunset risks, and cross-session repository audit items.",
        body,
    )


def build_sources_page() -> str:
    rows_html = ""
    for idx, (key, (label, url)) in enumerate(SRC.items(), start=1):
        domain = url.split("/")[2]
        rows_html += f"""
        <tr>
          <td><code>SRC-{idx:02d}</code></td>
          <td><strong>{label}</strong></td>
          <td><code>{domain}</code></td>
          <td><span class="badge badge-verified">Verified Official Primary Source</span></td>
          <td><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></td>
        </tr>"""

    body = f"""
    <div class="callout callout-emerald">
      <strong>100% Official Source Standard:</strong> Every statutory threshold, tax rate, CCPI inflation factor, utility tariff, insurance benchmark, rent cap, and economic series used in this suite comes directly from official federal, state, county, or regulated utility authorities. Zero commercial aggregator links are used.
    </div>

    <div class="card">
      <h2>Master Official Primary Source Registry ({len(SRC)} Verified Authorities)</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ref ID</th>
              <th>Document / Authority Title</th>
              <th>Official Domain</th>
              <th>Verification Status</th>
              <th>Direct Primary Link</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_shell(
        "sources.html",
        "Official Sources",
        "Primary Source Verification Index",
        "Official Government & Regulated Utility Source Registry",
        "Direct links to every IRS, California BOE, FTB, California Legislature, Santa Clara County, San Francisco, CPUC, SFPUC, CDI, HUD, FHFA, CBO, and Federal Reserve source.",
        body,
    )


APP_JS = r"""
(function () {
  "use strict";
  const D = window.VERIFIED_SUITE_DATA;
  if (!D) return;

  function r10(v) {
    return Math.round(v / 10) * 10;
  }

  function fmt(v) {
    const n = r10(v);
    return n < 0 ? "-$" + Math.abs(n).toLocaleString("en-US") : "$" + n.toLocaleString("en-US");
  }

  // 1. Render SVG Line Charts on Projections Page
  function renderSvgChart(containerId, seriesList, yMaxOverride) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const W = 560, H = 250, padL = 68, padR = 18, padT = 16, padB = 32;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;
    const years = D.cupertino_projections.map(r => r.year);
    let maxVal = yMaxOverride || 0;
    if (!maxVal) {
      seriesList.forEach(s => s.values.forEach(v => { if (v > maxVal) maxVal = v; }));
      maxVal = maxVal * 1.08;
    }
    const xPos = i => padL + (i / (years.length - 1)) * plotW;
    const yPos = v => padT + plotH - (Math.max(0, v) / maxVal) * plotH;

    // Shade 2040-2050 inheritance window
    const idx2040 = years.indexOf(2040);
    const idx2050 = years.indexOf(2050);
    const winX = xPos(idx2040);
    const winW = xPos(idx2050) - winX;

    let gridHtml = `<rect x="${winX.toFixed(1)}" y="${padT}" width="${winW.toFixed(1)}" height="${plotH}" fill="#e0f2fe" opacity="0.55"/>`;
    for (let g = 0; g <= 4; g++) {
      const val = (maxVal / 4) * g;
      const y = yPos(val);
      const label = val >= 1000000 ? "$" + (val / 1000000).toFixed(1) + "M" : "$" + Math.round(val / 1000) + "k";
      gridHtml += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e2e8f0" stroke-width="1"/>`;
      gridHtml += `<text x="${padL - 6}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="10" fill="#64748b">${label}</text>`;
    }
    [2026, 2030, 2035, 2040, 2045, 2050].forEach(yr => {
      const idx = years.indexOf(yr);
      if (idx >= 0) {
        const x = xPos(idx);
        gridHtml += `<text x="${x.toFixed(1)}" y="${H - 10}" text-anchor="middle" font-size="10" fill="#475569">${yr}</text>`;
      }
    });

    let pathsHtml = "";
    seriesList.forEach(s => {
      const pts = s.values.map((v, i) => `${xPos(i).toFixed(1)},${yPos(v).toFixed(1)}`).join(" ");
      pathsHtml += `<polyline fill="none" stroke="${s.color}" stroke-width="2.4" points="${pts}"/>`;
    });

    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="auto" role="img" aria-label="Projection chart">${gridHtml}${pathsHtml}</svg>`;
  }

  renderSvgChart("chart-values", [
    { color: "#0284c7", values: D.cupertino_projections.map(r => r.fmv) },
    { color: "#059669", values: D.sf_projections.map(r => r.fmv) },
    { color: "#64748b", values: D.cupertino_projections.map(r => r.fbyv_prop13) }
  ]);

  renderSvgChart("chart-taxes", [
    { color: "#dc2626", values: D.cupertino_projections.map(r => r.tax_if_inherited_rent) },
    { color: "#d97706", values: D.cupertino_projections.map(r => r.tax_if_inherited_live) },
    { color: "#059669", values: D.cupertino_projections.map(r => r.tax_prop13_current) }
  ]);

  // 2. CSV Download on Projections Page
  const csvBtn = document.getElementById("btn-download-csv");
  if (csvBtn) {
    csvBtn.addEventListener("click", function () {
      const headers = [
        "year", "cup_fmv", "cup_fbyv_prop13", "cup_tax_prop13", "prop19_cap",
        "cup_tax_if_inherited_live", "cup_tax_if_inherited_rent", "cup_total_opex_if_live",
        "sf_fmv", "sf_fbyv_prop13", "sf_tax_prop13", "sf_total_opex", "sf_rent_2units", "sf_net_cashflow_2units"
      ];
      const lines = [headers.join(",")];
      D.cupertino_projections.forEach((c, idx) => {
        const s = D.sf_projections[idx];
        lines.push([
          c.year, c.fmv, c.fbyv_prop13, c.tax_prop13_current, c.prop19_cap,
          c.tax_if_inherited_live, c.tax_if_inherited_rent, c.total_opex_if_live,
          s.fmv, s.fbyv_prop13, s.tax_prop13_current, s.total_opex_prop13, s.gross_rent_2units_yr, s.net_cashflow_2units_prop13
        ].join(","));
      });
      const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "verified_projections_2026_2050_rounded10.csv";
      a.click();
    });
  }

  // 3. Interactive Scenario Simulator on Scenarios Page
  const elYear = document.getElementById("sim-year");
  const elHor = document.getElementById("sim-horizon");
  const elCupG = document.getElementById("sim-cup-g");
  const elPortR = document.getElementById("sim-port-r");
  const elTrust = document.getElementById("sim-trust");
  const tbody = document.getElementById("sim-results-tbody");
  const banner = document.getElementById("sim-verdict-banner");

  function runSimulator() {
    if (!tbody || !elYear) return;
    const inheritYr = parseInt(elYear.value, 10);
    const horizon = parseInt(elHor.value, 10);
    const gCup = parseFloat(elCupG.value) / 100.0;
    const rPort = parseFloat(elPortR.value) / 100.0;
    const isRevocable = elTrust.value === "revocable";

    document.getElementById("lbl-sim-year").textContent = String(inheritYr);
    document.getElementById("lbl-sim-horizon").textContent = String(horizon);
    document.getElementById("lbl-sim-cup-g").textContent = (gCup * 100).toFixed(1) + "%";
    document.getElementById("lbl-sim-port-r").textContent = (rPort * 100).toFixed(1) + "%";

    const t0 = inheritYr - 2026;
    const cFmv0 = 3100000 * Math.pow(1 + gCup, t0);
    const cFbyv0 = 550540 * Math.pow(1.02, t0);
    const steps = Math.floor((inheritYr - 2025) / 2);
    const p19Cap0 = 1044586 * Math.pow(1.035, 2 * steps);

    const cBaseLive0 = cFbyv0 + Math.max(0, cFmv0 - (cFbyv0 + p19Cap0));
    const cBaseRent0 = cFmv0;

    let day1SaleCash = cFmv0 * 0.95;
    if (!isRevocable) {
      // IRS Rev. Rul. 2023-2: carryover basis (~cFbyv0) triggers 37.1% combined Fed+NIIT+CA capital gains tax!
      const capGainTax = Math.max(0, day1SaleCash - cFbyv0) * 0.371;
      day1SaleCash -= capGainTax;
    }

    let s1Port = day1SaleCash, s2aCash = 0, s2bCash = 0, s3Cash = 0;
    let yr1CfS1 = 0, yr1CfS2a = 0, yr1CfS2b = 0, yr1CfS3 = 0;
    let yr1TaxLive = 0, yr1TaxRent = 0;

    for (let k = 0; k < horizon; k++) {
      const yr = inheritYr + k;
      const t = yr - 2026;
      const sfFbyv = 114250 * 1.02 * Math.pow(1.02, t);
      const sfParcel = 1110 * Math.pow(1.02, t);
      const sfRb = 90 * Math.pow(1.02, t);
      const sfTaxOwner = Math.max(0, sfFbyv - 7000) * 0.01181622 + sfParcel;
      const sfTaxNon = sfFbyv * 0.01181622 + sfParcel;
      const sfOpex = sfRb + 4440 * Math.pow(1.045, t) + 600 * Math.pow(1.035, t) + 3600 * Math.pow(1.04, t) + 12600 * Math.pow(1.028, t);
      const sfRent2 = 7150 * 12 * Math.pow(1.028, t);
      const sfUnit3 = 3600 * 12 * Math.pow(1.028, t) * 0.95;

      const sfAfOwner = (sfRent2 - (sfTaxOwner + sfOpex)) * 0.70;
      const sfAfNon2 = (sfRent2 - (sfTaxNon + sfOpex)) * 0.70;
      const sfAfAll3 = ((sfRent2 + sfUnit3) - (sfTaxNon + sfOpex * 1.12)) * 0.68;

      const cParcel = 950 * Math.pow(1.02, t);
      const cTaxLive = Math.max(0, cBaseLive0 * Math.pow(1.02, k) - 7000) * 0.011636 + cParcel;
      const cTaxRent = (cBaseRent0 * Math.pow(1.02, k)) * 0.011636 + cParcel;

      const cWater = 1560 * Math.pow(1.032, t);
      const cElec = yr < 2038 ? -240 * Math.pow(0.995, t) : 660 * Math.pow(1.035, t);
      const cInsLive = 2600 * Math.pow(1.04, t);
      const cInsRent = 3120 * Math.pow(1.04, t);
      const cMaint = 7800 * Math.pow(1.028, t);

      const cHoldLive = cTaxLive + cWater + cElec + cInsLive + cMaint;
      const cEffRent = (7000 * 12 * Math.pow(1.03, t)) * 0.87;
      const cRentNoi = cEffRent - (cTaxRent + cInsRent + cMaint);
      const cDepr = ((isRevocable ? cFmv0 : cFbyv0) * 0.30) / 27.5;
      const cRentAf = cRentNoi - Math.max(0, (cRentNoi - cDepr) * 0.35);

      const cf1 = sfAfOwner;
      const cf2a = sfAfNon2 - cHoldLive;
      const cf2b = sfAfAll3 - cHoldLive;
      const cf3 = sfAfOwner + cRentAf;

      if (k === 0) {
        yr1CfS1 = cf1; yr1CfS2a = cf2a; yr1CfS2b = cf2b; yr1CfS3 = cf3;
        yr1TaxLive = cTaxLive; yr1TaxRent = cTaxRent;
      }

      s1Port = s1Port * (1 + rPort) + cf1;
      s2aCash = s2aCash * (1 + rPort) + cf2a;
      s2bCash = s2bCash * (1 + rPort) + cf2b;
      s3Cash = s3Cash * (1 + rPort) + cf3;
    }

    const tEnd = (inheritYr + horizon) - 2026;
    const cFmvEnd = 3100000 * Math.pow(1 + gCup, tEnd);
    const sfFmvEnd = 1800000 * Math.pow(1.035, tEnd);
    const cNetEnd = cFmvEnd * 0.95;
    const basisStart = isRevocable ? cFmv0 : cFbyv0;
    const gainEnd = Math.max(0, cNetEnd - basisStart);
    const capTaxLive = Math.max(0, gainEnd - 250000) * 0.371;
    const cumDepr = ((basisStart * 0.30) / 27.5) * horizon;
    const capTaxRent = gainEnd * 0.371 + cumDepr * 0.421;

    const eqLive = cNetEnd - capTaxLive;
    const eqRent = cNetEnd - capTaxRent;

    const rows = [
      { id: "S1", label: "Sell Cupertino & Reinvest + Live in SF Unit 3", cash0: day1SaleCash, tax1: 0, cf1: yr1CfS1, portEnd: s1Port, total: s1Port + sfFmvEnd, src: '<a href="https://www.irs.gov/pub/irs-drop/rr-23-02.pdf" target="_blank" rel="noopener noreferrer">IRS Rev. Rul. 2023-2 / § 1014</a>' },
      { id: "S3", label: "Rent Out Cupertino (No Prop 19) + Live in SF Unit 3", cash0: 0, tax1: yr1TaxRent, cf1: yr1CfS3, portEnd: s3Cash, total: s3Cash + eqRent + sfFmvEnd, src: '<a href="https://boe.ca.gov/proptaxes/pdf/lta25015.pdf" target="_blank" rel="noopener noreferrer">CA BOE LTA 2025/015</a>' },
      { id: "S2B", label: "Live in Cupertino (Prop 19) + Rent All 3 SF Units", cash0: 0, tax1: yr1TaxLive, cf1: yr1CfS2b, portEnd: s2bCash, total: s2bCash + eqLive + sfFmvEnd, src: '<a href="https://www.boe.ca.gov/pdf/pub801.pdf" target="_blank" rel="noopener noreferrer">CA BOE Pub 801</a>' },
      { id: "S2A", label: "Live in Cupertino (Prop 19) + Keep SF Unit 3 Vacant", cash0: 0, tax1: yr1TaxLive, cf1: yr1CfS2a, portEnd: s2aCash, total: s2aCash + eqLive + sfFmvEnd, src: '<a href="https://www.irs.gov/publications/p523" target="_blank" rel="noopener noreferrer">IRS Pub 523 (§ 121)</a>' }
    ];

    rows.sort((a, b) => b.total - a.total);
    const best = rows[0];
    const runnerUp = rows[1];

    banner.innerHTML = `<strong>Simulated Winner (${inheritYr}–${inheritYr + horizon}): ${best.id} — ${best.label}</strong> · Builds <strong>${fmt(best.total)}</strong> in total household net worth, leading runner-up (${runnerUp.id}) by <strong>+${fmt(best.total - runnerUp.total)}</strong> (${isRevocable ? "Revocable Trust 100% § 1014 Step-Up active" : "WARNING: Irrevocable Trust carryover basis deducts 37.1% tax on sale!"}).`;

    tbody.innerHTML = rows.map((r, i) => `
      <tr${i === 0 ? ' style="background:#ecfdf5"' : ""}>
        <td><strong>${r.id}</strong>: ${r.label}${i === 0 ? ' <span class="badge badge-verified">#1 Net Worth</span>' : ""}</td>
        <td class="num">${fmt(r.cash0)}</td>
        <td class="num">${fmt(r.tax1)}</td>
        <td class="num">${fmt(r.cf1)}</td>
        <td class="num">${fmt(r.portEnd)}</td>
        <td class="num"><strong>${fmt(r.total)}</strong></td>
        <td>${r.src}</td>
      </tr>
    `).join("");
  }

  if (elYear) {
    [elYear, elHor, elCupG, elPortR, elTrust].forEach(el => el.addEventListener("input", runSimulator));
    runSimulator();
  }
})();
"""


def main():
    SITE_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    (SITE_DIR / ".nojekyll").write_text("")

    data = json.loads(DATA_JSON.read_text())
    (ASSETS_DIR / "data.js").write_text("window.VERIFIED_SUITE_DATA = " + json.dumps(data) + ";\n")
    (ASSETS_DIR / "app.js").write_text(APP_JS.strip() + "\n")

    pages = {
        "index.html": build_index_page(data),
        "properties.html": build_properties_page(data),
        "projections.html": build_projections_page(data),
        "scenarios.html": build_scenarios_page(data),
        "estate-tax.html": build_estate_tax_page(data),
        "inheritance-guide.html": build_guide_page(),
        "flagged-review.html": build_flagged_page(),
        "sources.html": build_sources_page(),
    }

    for fname, html in pages.items():
        (SITE_DIR / fname).write_text(html)
        print(f"Generated site/{fname} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
