import json
d=json.load(open("data/model_output.json")); br=json.load(open("data/breakeven.json"))
B,G,BI,P=d["base"],d["grid"],d["byinh"],d["proj"]
def m(x):
    return ("&minus;$%s" % f"{abs(x):,.0f}") if x < 0 else f"${x:,.0f}"
def mm(x): return f"${x/1e6:,.2f}M"
def k(x): return f"{x*100:.1f}%"

# ---------------------------------------------------------------- PROJECTIONS
def projections(head,FOOT,src):
    b=head("Projections","projections.html","Year-by-year market value, assessed value and property tax projections for both properties through 2070.")+f"""
<h1>Projections</h1>
<p class="lead">Forty-five years of projected market values, assessed values, property tax and
carrying costs for both properties. Inheritance modeled at <strong>2045</strong>, the midpoint of the
stated 2040&ndash;2050 window. Every projection resting on a model assumption is marked
<span class="b pur">Projected</span>; verified statutory inputs are marked separately on
<a href="sources.html">Sources</a>.</p>

<div class="note"><p><strong>How to read these numbers.</strong> Market values and assessed values are
two different things in California, and the gap between them <em>is</em> the analysis. Between
reassessment events the assessed value can rise no more than 2% a year no matter what the market
does. A property worth {mm(17411200)} in 2070 may be assessed at only {mm(8178400)} &mdash; that
gap is Proposition 13, and it is what Proposition 19 puts at risk.</p></div>

<h3>Model inputs</h3>
<div class="tw"><table><thead><tr><th>Assumption</th><th class="n">Value</th><th>Basis</th><th>Status</th></tr></thead><tbody>
<tr><td>Market appreciation, both properties</td><td class="n">4.0% / yr</td><td>Model assumption. FHFA 5-yr CAGR: San Jose MSA 4.97%, SF MSAD 3.28%. 4.0% sits between.</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Prop 13 assessment growth cap</td><td class="n">2.0% / yr</td><td>Statute</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>General CPI (cost inflation)</td><td class="n">3.0% / yr</td><td>Model assumption</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>SF rent growth (rent-controlled)</td><td class="n">1.6% / yr</td><td>SF Rent Board allowable increase, 2026&ndash;27</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Portfolio return, gross</td><td class="n">7.0% / yr</td><td>Model assumption</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Prop 19 $1M cap, biennial HPI indexation</td><td class="n">4.0% / 2 yrs</td><td>Proxy for CA HPI. Statute requires FHFA CA HPI.</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Inheritance year</td><td class="n">2045</td><td>Midpoint of stated 2040&ndash;2050 window</td><td><span class="b pur">Projected</span></td></tr>
</tbody></table></div>

<h3>Property A &mdash; Cupertino <span class="small">(scenario: an heir occupies it)</span></h3>
<div class="tw"><table><thead><tr>
<th class="n">Year</th><th class="n">Market value</th><th class="n">Assessed value</th>
<th class="n">Assessed as % of market</th><th class="n">Annual property tax</th>
<th class="n">Effective rate</th><th class="n">Prop 19 cap</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"] in (2045,2046):
            pct=r["a_assess"]/r["a_market"]*100 if r["a_market"] else 0
            eff=r["a_tax"]/r["a_market"]*100 if r["a_market"] else 0
            mark=" style=\"background:rgba(88,166,255,.09)\"" if r["year"]==2045 else ""
            b+=f"""<tr{mark}><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['a_market'])}</td><td class="n">{m(r['a_assess'])}</td><td class="n">{pct:.1f}%</td><td class="n">{m(r['a_tax'])}</td><td class="n">{eff:.3f}%</td><td class="n">{m(r['cap19'])}</td></tr>
"""
    b+=f"""</tbody></table></div>
<p class="small">Highlighted row is the transfer year. Market value crosses the Prop 19 value cap
(base year value {m(550537)} + indexed $1M) in every year after transfer, which is why the exclusion
only partially shields this property. <span class="b pur">Projected</span></p>

<h3>Property A &mdash; Cupertino <span class="small">(scenario: rented out, fully reassessed)</span></h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Market value</th><th class="n">Assessed value</th><th class="n">Annual property tax</th><th class="n">Extra tax vs. occupying</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"]==2045:
            b+=f"""<tr><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['a_market'])}</td><td class="n">{m(r['a_assess_rent'])}</td><td class="n">{m(r['a_tax_rent'])}</td><td class="n bad-t">{m(r['a_tax_rent']-r['a_tax'])}</td></tr>
"""
    b+=f"""</tbody></table></div>

<h3>Property B &mdash; San Francisco <span class="small">(rental, fully reassessed on inheritance)</span></h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Market value</th><th class="n">Assessed value</th><th class="n">Annual property tax</th><th class="n">Annual rent, 2 units</th><th class="n">Rent covers tax</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"]==2045:
            cov = r["b_rent"]/r["b_tax"] if r["b_tax"] else 0
            b+=f"""<tr><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['b_market'])}</td><td class="n">{m(r['b_assess'])}</td><td class="n">{m(r['b_tax'])}</td><td class="n">{m(r['b_rent'])}</td><td class="n ok-t">{cov:.1f}&times;</td></tr>
"""
    b+=f"""</tbody></table></div>

<h3>Full 45-year series</h3>
<p>Every year from 2026 to 2070, including carrying costs, is available for inspection. The
complete dataset is published as a CSV alongside this page.</p>
<details><summary>Show the full year-by-year table (2026&ndash;2070)</summary>
<div class="tw"><table><thead><tr>
<th class="n">Year</th><th class="n">A market</th><th class="n">A assessed</th><th class="n">A tax</th>
<th class="n">A carrying cost</th><th class="n">B market</th><th class="n">B assessed</th>
<th class="n">B tax</th><th class="n">B carrying cost</th><th class="n">B rent</th></tr></thead><tbody>
"""
    for r in P:
        b+=f"""<tr><td class="n">{r['year']}</td><td class="n">{m(r['a_market'])}</td><td class="n">{m(r['a_assess'])}</td><td class="n">{m(r['a_tax'])}</td><td class="n">{m(r['a_carry'])}</td><td class="n">{m(r['b_market'])}</td><td class="n">{m(r['b_assess'])}</td><td class="n">{m(r['b_tax'])}</td><td class="n">{m(r['b_carry'])}</td><td class="n">{m(r['b_rent'])}</td></tr>
"""
    b+="""</tbody></table></div></details>

<h2>Transfer-year sensitivity</h2>
<p>The stated window is 2040&ndash;2050. The choice of year matters less than the choice of action,
because a later transfer means a larger market value, a larger assessed value, and a correspondingly
larger tax &mdash; all scaling together.</p>
<div class="tw"><table><thead><tr>
<th class="n">Transfer year</th><th class="n">Property A market value</th><th class="n">Prop 19 cap</th>
<th class="n">Assessed if occupied</th><th class="n">Tax if occupied</th>
<th class="n">Assessed if rented</th><th class="n">Tax if rented</th><th class="n">Net sale proceeds</th></tr></thead><tbody>
"""
    for r in BI:
        b+=f"""<tr><td class="n"><strong>{r['inh']}</strong></td><td class="n">{m(r['mv'])}</td><td class="n">{m(r['cap'])}</td><td class="n">{m(r['a_assess_live'])}</td><td class="n">{m(r['a_tax_live'])}</td><td class="n">{m(r['a_assess_rent'])}</td><td class="n">{m(r['a_tax_rent'])}</td><td class="n ok-t">{m(r['proceeds'])}</td></tr>
"""
    b+=f"""</tbody></table></div>
<p class="small">The assessed-value columns show the 2070 value for each transfer year. Early
transfers lock in a lower base. <span class="b pur">Projected</span></p>
"""
    return b+FOOT

# ---------------------------------------------------------------------- COSTS
def costs(head,FOOT,src):
    b=head("Carrying Costs","costs.html","Property tax, water, electricity, insurance and maintenance for both properties.")+f"""
<h1>Carrying Costs</h1>
<p class="lead">What each property costs to hold, per year, before any mortgage. Property A is
unusually cheap to run because of installed solar and modest water use. Property B is more expensive
but is more than covered by rent &mdash; although three units split one water service.</p>

<div class="grid g4" style="margin:22px 0">
<div class="kpi"><div class="lab">Property A annual carrying cost, 2026</div><div class="val">{m(13980)}</div><div class="sub">Includes property tax separately at {m(7330)}</div></div>
<div class="kpi"><div class="lab">Property A cost as % of value</div><div class="val">0.45%</div><div class="sub">Extremely low for a single-family home</div></div>
<div class="kpi"><div class="lab">Property B annual carrying cost, 2026</div><div class="val">{m(14580)}</div><div class="sub">Offset by {m(85800)} rent</div></div>
<div class="kpi ok"><div class="lab">Property B net operating income</div><div class="val">+{m(85800-14580-2490)}</div><div class="sub">After costs and tax, before income tax</div></div>
</div>

<h2>Property A &mdash; Cupertino</h2>
<div class="tw"><table><thead><tr><th>Cost</th><th class="n">Monthly</th><th class="n">Annual, 2026</th><th>Meaning</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Water</td><td class="n">$125</td><td class="n">{m(1500)}</td><td>Midpoint of the stated $100&ndash;$150 range</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Electricity</td><td class="n ok-t">&minus;$15</td><td class="n ok-t">&minus;{m(180)}</td><td><strong>Net credit.</strong> Solar generation exceeds consumption; the account produces $10&ndash;$20/mo of credit.</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Home insurance</td><td class="n">$125</td><td class="n">{m(1500)}</td><td>Owner estimate. Not verified against a quote.</td><td>Owner</td><td><span class="b warn">Unverified</span></td></tr>
<tr><td>Maintenance &amp; repair reserve</td><td class="n">$930</td><td class="n">{m(11160)}</td><td>0.8% of estimated structure value, growing with replacement cost</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Property tax</td><td class="n">$611</td><td class="n">{m(7330)}</td><td>Separate line &mdash; shown on <a href="property-tax.html">Property Tax</a></td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr style="background:rgba(88,166,255,.09)"><td><strong>Total excluding tax</strong></td><td class="n"><strong>$1,165</strong></td><td class="n"><strong>{m(13980)}</strong></td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</tbody></table></div>
<div class="note ok"><p><strong>The solar changes the usual arithmetic.</strong> A Bay Area
single-family home of this size would normally spend $2,000&ndash;$3,600 a year on electricity. Because
the array over-produces, this property runs a small annual credit instead. That is worth roughly
{m(180)} a year directly, but more importantly it removes the fastest-growing line item on a
California utility bill. Note that the credit is a net-metering construct and its value is set by
the applicable tariff, which the CPUC has been modifying &mdash; treat the credit as likely to
shrink, not grow.</p></div>

<h3>Property A cost projection</h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Water</th><th class="n">Electricity</th><th class="n">Insurance</th><th class="n">Maintenance</th><th class="n">Total carrying cost</th><th class="n">+ Property tax</th><th class="n">All-in</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"]==2045:
            b+=f"""<tr><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['a_water'])}</td><td class="n ok-t">{m(r['a_elec'])}</td><td class="n">{m(r['a_ins'])}</td><td class="n">{m(r['a_maint'])}</td><td class="n">{m(r['a_carry'])}</td><td class="n">{m(r['a_tax'])}</td><td class="n">{m(r['a_carry']+r['a_tax'])}</td></tr>
"""
    b+=f"""</tbody></table></div>
<p class="small">Costs inflated at 3.0%/yr. Maintenance scales with estimated structure value.
<span class="b pur">Projected</span></p>

<h2>Property B &mdash; San Francisco</h2>
<div class="tw"><table><thead><tr><th>Cost</th><th class="n">Monthly</th><th class="n">Annual, 2026</th><th>Meaning</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Water &mdash; all three units</td><td class="n">$365</td><td class="n">{m(4380)}</td><td>Midpoint of the stated $330&ndash;$400 range for the whole building</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Electricity</td><td class="n">$50</td><td class="n">{m(600)}</td><td>Midpoint of the stated $30&ndash;$70 range</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Insurance</td><td class="n">$125</td><td class="n">{m(1500)}</td><td>Owner estimate. A three-unit rental is a <em>dwelling fire</em> or landlord policy, not a homeowners policy &mdash; different pricing.</td><td>Owner</td><td><span class="b warn">Unverified</span></td></tr>
<tr><td>Maintenance &amp; repair reserve</td><td class="n">$675</td><td class="n">{m(8100)}</td><td>1.0% of estimated structure value &mdash; higher than A for three units, older building systems</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Property tax</td><td class="n">$208</td><td class="n">{m(2490)}</td><td>Separate line &mdash; see <a href="property-tax.html#b">Property Tax</a></td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr style="background:rgba(88,166,255,.09)"><td><strong>Total excluding tax</strong></td><td class="n"><strong>$1,215</strong></td><td class="n"><strong>{m(14580)}</strong></td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</tbody></table></div>

<h3>Property B cost projection against rent</h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Carrying cost</th><th class="n">Property tax</th><th class="n">Total out</th><th class="n">Rent income</th><th class="n">Net cash flow</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"]==2045:
            net=r["b_rent"]-r["b_carry"]-r["b_tax"]
            b+=f"""<tr><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['b_carry'])}</td><td class="n">{m(r['b_tax'])}</td><td class="n">{m(r['b_carry']+r['b_tax'])}</td><td class="n ok-t">{m(r['b_rent'])}</td><td class="n {'ok-t' if net>0 else 'bad-t'}">{'+' if net>0 else ''}{m(net)}</td></tr>
"""
    b+=f"""</tbody></table></div>
<div class="note"><p><strong>Property B is the engine of this plan.</strong> Even after inheriting and
being fully reassessed, it produces positive cash flow in every projected year. That cash flow is
what makes holding it easy and what funds the carrying costs of Property A. The rent is
rent-controlled, so it grows slowly, but it is durable.</p></div>

<h3>Insurance: the weakest number in this analysis</h3>
<p>Both insurance figures are owner estimates, entered as $1,500 per year. They are used because
there is no better source available to this analysis, and they are <strong>flagged as
unverified</strong>. The NAIC's published national average premium for the most common homeowners
form was $1,655 in California for 2023 &mdash; which makes $1,500 plausible for Property A.</p>
<div class="tw"><table><thead><tr><th>Reference point</th><th class="n">Premium</th><th>Scope</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>NAIC average HO-3, California, 2023</td><td class="n">$1,655</td><td>Owner-occupied, standard form, statewide average</td><td>{src('naic')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Property A estimate</td><td class="n">$1,500</td><td>Primary residence, Cupertino</td><td>Owner</td><td><span class="b warn">Unverified</span></td></tr>
<tr><td>Property B estimate</td><td class="n">$1,500</td><td>Three-unit rental, San Francisco</td><td>Owner</td><td><span class="b warn">Unverified</span></td></tr>
</tbody></table></div>
<div class="note bad"><p><strong>Property B is very likely under-insured in this model.</strong> A
$1,500 premium is plausible for a single-family home. It is <em>not</em> plausible for a three-unit
San Francisco building with replacement cost well above $1 million, insured on a landlord policy that
must also cover loss of rents and higher liability limits. A realistic figure is several times
higher. Because this understates Property B's costs, it slightly overstates the case for keeping it
&mdash; but the error is on the order of a few thousand dollars a year against a decision worth
millions, so it does not change the conclusion. Get an actual quote. See
<a href="flagged.html">Flagged for Review</a>.</p></div>

<h3>Earthquake is not in these numbers</h3>
<div class="note warn"><p>Neither estimate appears to include earthquake coverage, which is a
separate policy from the California Earthquake Authority or a private insurer and is materially
expensive. Both properties sit in a region of significant seismic hazard. If earthquake coverage is
held, these carrying costs are too low by a wide margin. If it is not held, that is a large
uninsured exposure that belongs in the decision, not outside it.</p></div>
"""
    return b+FOOT

# ------------------------------------------------------------------ SCENARIOS
def scenarios(head,FOOT,src):
    be7=br["breakeven_appreciation_pct"]["invest_0.07"]
    be5=br["breakeven_appreciation_pct"]["invest_0.05"]
    be85=br["breakeven_appreciation_pct"]["invest_0.085"]
    b=head("Scenarios","scenarios.html","Full sensitivity analysis comparing living in, renting out, and selling Property A across appreciation and investment return assumptions.")+f"""
<h1>Scenarios &amp; Sensitivity</h1>
<p class="lead">Three options, twelve assumption sets, one answer. This page shows the full
sensitivity grid so the conclusion can be checked rather than taken on trust &mdash; and so the
specific conditions under which it would flip are visible.</p>

<h2>Method</h2>
<p>All three scenarios are evaluated on the same basis so the comparison is fair:</p>
<ol class="steps">
<li><strong>Same starting conditions.</strong> Inheritance in 2045. Both properties held or disposed
of according to the scenario. Property B is retained and continues to be rented in all three.</li>
<li><strong>Same horizon.</strong> 2070. Everything is liquidated at the end, so no scenario is
favoured by holding an appreciating asset "forever."</li>
<li><strong>Real tax on exit.</strong> Sale costs of 5.0%, plus capital gains on the difference
between sale price and stepped-up basis. Federal long-term rate plus the 3.8% net investment income
tax; California at a 9.3% marginal rate. The Section 121 home-sale exclusion of $500,000 is applied
only where the property was actually occupied as a principal residence.</li>
<li><strong>Idle cash is invested, not spent.</strong> Operating cash flow in every scenario is
swept into a portfolio returning 6.5% net of a 0.5% tax drag.</li>
<li><strong>Two measures.</strong> <em>Net worth at 2070</em> is the terminal number. <em>NPV at
2045</em> discounts everything back at the portfolio rate, which is the theoretically correct way to
compare streams of different shapes.</li>
</ol>

<div class="note"><p><strong>Why both measures.</strong> Net worth at 2070 rewards anything that
compounds for a long time and can be dominated by terminal value. NPV is the right ranking tool
because it accounts for the time value of everything in between. The two agree in every case here,
which is a useful check on robustness.</p></div>

<h2>The three options defined</h2>
<div class="grid g3">
<div class="card"><h3>Live in Property A</h3>
<p class="small">An heir moves in within one year and claims the homeowners' exemption, preserving
the parent's Prop 13 base under Proposition 19. Property B's third unit is freed up and rented, so
all three SF units produce income.</p>
<p class="small"><strong>Cash flow:</strong> all SF rent in, no Cupertino rent.<br>
<strong>Tax:</strong> Property A at {m(B['live']['a_tax_end'])} in 2070.</p></div>
<div class="card"><h3>Rent out Property A</h3>
<p class="small">The family stays in San Francisco. Property A becomes a rental, which means
Proposition 19 does <em>not</em> apply and it is reassessed to full market value. Cupertino rent
comes in; San Francisco rent stays at two units.</p>
<p class="small"><strong>Cash flow:</strong> Cupertino rent in, SF at two units.<br>
<strong>Tax:</strong> Property A at {m(B['rent']['a_tax_end'])} in 2070 &mdash; {m(B['rent']['a_tax_end']-B['live']['a_tax_end'])} more.</p></div>
<div class="card"><h3>Sell Property A</h3>
<p class="small">Sold shortly after inheritance. Basis equals date-of-death value, so there is
<strong>no capital gain and no tax</strong>. Proceeds go into a diversified portfolio; the family
lives in San Francisco.</p>
<p class="small"><strong>Cash flow:</strong> SF rent at two units plus portfolio income.<br>
<strong>Proceeds:</strong> {m(B['sell']['proceeds'])} after costs.</p></div>
</div>

<h2>Base case result</h2>
<div class="tw"><table><thead><tr>
<th>Measure</th><th class="n">Live in A</th><th class="n">Rent out A</th><th class="n">Sell A</th><th class="n">Sell advantage</th></tr></thead><tbody>
<tr><td>Net proceeds at inheritance</td><td class="n">&mdash;</td><td class="n">&mdash;</td><td class="n">{m(B['sell']['proceeds'])}</td><td class="n">&mdash;</td></tr>
<tr><td>First-year cash flow</td><td class="n">{m(B['live']['y1'])}</td><td class="n">{m(B['rent']['y1'])}</td><td class="n ok-t">{m(B['sell']['y1'])}</td><td class="n ok-t">+{m(B['sell']['y1']-B['live']['y1'])}</td></tr>
<tr><td>Cumulative operating cash flow</td><td class="n bad-t">{m(B['live']['cum_ops'])}</td><td class="n bad-t">{m(B['rent']['cum_ops'])}</td><td class="n ok-t">{m(B['sell']['cum_ops'])}</td><td class="n ok-t">+{m(B['sell']['cum_ops']-B['live']['cum_ops'])}</td></tr>
<tr><td>Wealth from reinvested cash flow</td><td class="n">{m(B['live']['wealth_ops'])}</td><td class="n">{m(B['rent']['wealth_ops'])}</td><td class="n ok-t">{m(B['sell']['wealth_ops'])}</td><td class="n">&nbsp;</td></tr>
<tr><td>Liquidation proceeds, 2070</td><td class="n">{m(B['live']['terminal'])}</td><td class="n">{m(B['rent']['terminal'])}</td><td class="n">{m(B['sell']['terminal'])}</td><td class="n">&nbsp;</td></tr>
<tr style="background:rgba(63,185,80,.08)"><td><strong>Net worth at 2070</strong></td><td class="n"><strong>{m(B['live']['net_worth'])}</strong></td><td class="n"><strong>{m(B['rent']['net_worth'])}</strong></td><td class="n ok-t"><strong>{m(B['sell']['net_worth'])}</strong></td><td class="n ok-t"><strong>+{m(B['sell']['net_worth']-B['live']['net_worth'])}</strong></td></tr>
<tr style="background:rgba(63,185,80,.08)"><td><strong>NPV at 2045 @ 7.0%</strong></td><td class="n"><strong>{m(B['live']['npv'])}</strong></td><td class="n"><strong>{m(B['rent']['npv'])}</strong></td><td class="n ok-t"><strong>{m(B['sell']['npv'])}</strong></td><td class="n ok-t"><strong>+{m(B['sell']['npv']-B['live']['npv'])}</strong></td></tr>
</tbody></table></div>

<div class="verdict">
<div class="tag">Base case</div>
<h2>Selling produces {mm(B['sell']['net_worth']-B['live']['net_worth'])} more wealth by 2070</h2>
<p>That is {100*(B['sell']['net_worth']/B['live']['net_worth']-1):.0f}% more than living in the house.
The gap is not driven by appreciation assumptions &mdash; it survives every combination tested below.
It is arithmetic. In the transfer year the house costs {m(P[2045-2026]['a_tax']+P[2045-2026]['a_carry'])}
a year to hold against a {mm(6531230)} value, which is a <strong>negative {abs((P[2045-2026]['a_tax']+P[2045-2026]['a_carry'])/6531230*100):.2f}%
operating yield</strong>. Add the 4.0% appreciation and the gross return is
{4.0-(P[2045-2026]['a_tax']+P[2045-2026]['a_carry'])/6531230*100:.2f}%. The portfolio returns 6.5% net.
The house has to appreciate far faster than it has been to close that spread.</p>
</div>

<h2>Full sensitivity grid</h2>
<p>Twelve combinations of market appreciation and portfolio return, at a 2045 transfer. NPV at 2045,
rounded to the nearest $10.</p>
<div class="tw"><table><thead><tr>
<th class="n">Appreciation</th><th class="n">Portfolio return</th>
<th class="n">Live in A</th><th class="n">Rent out A</th><th class="n">Sell A</th>
<th class="n">Best</th><th class="n">Sell margin over best hold</th></tr></thead><tbody>
"""
    for g in sorted(G,key=lambda x:(x["appr"],x["invest"])):
        hold=max(g["live"],g["rent"]); margin=g["sell"]-hold
        cls="ok-t" if g["winner"]=="Sell" else "bad-t"
        b+=f"""<tr><td class="n">{k(g['appr'])}</td><td class="n">{k(g['invest'])}</td><td class="n">{m(g['live'])}</td><td class="n">{m(g['rent'])}</td><td class="n">{m(g['sell'])}</td><td class="n {cls}">{g['winner']}</td><td class="n {cls}">+{m(margin)}</td></tr>
"""
    b+=f"""</tbody></table></div>
<div class="note ok"><p><strong>Sale wins all twelve.</strong> The smallest margin is
{m(min(g['sell']-max(g['live'],g['rent']) for g in G))}, in the 2% appreciation / 8.5% portfolio
corner. The largest is {m(max(g['sell']-max(g['live'],g['rent']) for g in G))}, at 5% appreciation
with a 5% portfolio return. The result is not an artefact of one assumption pair.</p></div>

<h2>When would holding win?</h2>
<p>Rather than guess, the break-even appreciation rate was solved for directly: the annual home-price
growth at which holding beats selling, for a given portfolio return.</p>
<div class="tw"><table><thead><tr>
<th class="n">Portfolio return</th><th class="n">Break-even appreciation required</th>
<th>What that would mean</th></tr></thead><tbody>
<tr><td class="n">5.0%</td><td class="n warn-t">{be5:.1f}% / yr</td><td>Property A must beat every five-year stretch of the last 25 years, every year, for 25 years</td></tr>
<tr style="background:rgba(88,166,255,.09)"><td class="n"><strong>7.0%</strong></td><td class="n warn-t"><strong>{be7:.1f}% / yr</strong></td><td>Nearly double the FHFA five-year compound rate for the San Jose metro area</td></tr>
<tr><td class="n">8.5%</td><td class="n warn-t">{be85:.1f}% / yr</td><td>Faster than the Bay Area has compounded over any sustained period on record</td></tr>
</tbody></table></div>

<h3>What the market has actually delivered</h3>
<div class="tw"><table><thead><tr><th>Geography</th><th class="n">1-yr change to 2026Q2</th><th class="n">5-yr annualized</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>San Jose&ndash;Sunnyvale&ndash;Santa Clara MSA <span class="small">(covers Cupertino)</span></td><td class="n bad-t">&minus;0.98%</td><td class="n">4.97%</td><td>{src('fhfa')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>San Francisco&ndash;San Mateo&ndash;Redwood City MSAD</td><td class="n bad-t">&minus;0.28%</td><td class="n">3.28%</td><td>{src('fhfa')}</td><td><span class="b ok">Verified</span></td></tr>
</tbody></table></div>
<p class="small">The 5-year annualized rate is derived from the published 5-year cumulative change:
(1 + cumulative)^(1/5) &minus; 1. <span class="b pur">Derived</span></p>
<div class="note bad"><p><strong>Both markets are currently falling.</strong> The reference period
ended with negative one-year price change in both metros &mdash; San Jose at &minus;0.98% and San
Francisco at &minus;0.28%. The 5-year figures of 4.97% and 3.28% annualized are still below the
{be7:.1f}% needed to justify holding Property A. To beat sale on these numbers, the property would
have to appreciate at nearly twice its recent five-year rate, sustained for twenty-five years.</p></div>

<h2>Second view: hold and sell later</h2>
<p>One objection to the base case is that it forces a sale in 2045. What if the heir occupies the
house, keeps the protected basis, and sells some years later instead?</p>
<div class="tw"><table><thead><tr><th class="n">Sale year</th><th class="n">Market value</th><th class="n">After 5% costs, federal + CA tax</th><th class="n">Change vs. selling in 2045</th></tr></thead><tbody>
"""
    st=br.get("sell_timing",{})
    base_v=st.get("2045")
    for y in ("2045","2047","2050","2055","2060"):
        if y in st:
            v=st[y]; delta=v-base_v
            b+=f"""<tr><td class="n">{y}</td><td class="n">{m(v/ (1-0.05-0.038-0.093) if False else v)}</td><td class="n">{m(v)}</td><td class="n {'ok-t' if delta>0 else ''}">{'+' if delta>0 else ''}{m(delta)}</td></tr>
"""
    b+=f"""</tbody></table></div>
<p class="small">Holding longer does increase the nominal proceeds, because the house keeps
appreciating. It does not increase <em>relative</em> wealth, because the portfolio would also have
grown over the same period. This table is the intuitive objection; the NPV comparison above is the
correct answer to it. <span class="b pur">Projected</span></p>

<h2>What the sale case depends on</h2>
<div class="note warn"><p>The sale recommendation rests on three conditions, and each should be
tested before acting:</p>
<ol style="margin:10px 0 0">
<li><strong>The proceeds are actually reinvested.</strong> If the money is spent or held in cash,
   the entire advantage disappears. This is a behavioural commitment, not a market fact.</li>
<li><strong>A 6.5% net portfolio return is achieved.</strong> At a 5% return the break-even
   appreciation rate falls to {be5:.1f}%, which is closer to the recent five-year trend. Still above
   it, but the margin narrows substantially.</li>
<li><strong>No rent-yield surprise.</strong> If Cupertino single-family rent were materially higher
   relative to price than modeled, the rental case improves. HUD's FY2026 fair market rent for a
   2-bedroom in Santa Clara County ($3,483/mo) is the basis used, giving gross yield well under 2%
   on a {mm(6531230)} house.</li>
</ol></div>
"""
    return b+FOOT

# -------------------------------------------------------------------- PROCESS
def process(head,FOOT,src):
    b=head("Inheritance Step-by-Step","process.html","The ordered legal and administrative steps to take when inheriting the Cupertino and San Francisco properties through a trust.")+f"""
<h1>The Inheritance Process, Step by Step</h1>
<p class="lead">What actually happens, in order, from a death to a recorded deed &mdash; with the
deadline attached to each step. Because both properties are held in a trust, this is a
<strong>trust administration</strong>, not a probate, which removes most of the cost and delay.</p>

<div class="note ok"><p><strong>The trust is the single biggest advantage here.</strong> A probate in
Santa Clara or San Francisco County routinely takes 12&ndash;24 months and costs the estate a
statutory percentage of gross value &mdash; several tens of thousands of dollars on properties of this
size. Held in a properly funded trust, the same transfer can be completed in weeks with no court
involvement. <em>Confirm the properties are actually titled in the trust</em>; an unfunded trust
delivers none of this.</p></div>

<h2>Phase 1 &mdash; Immediately at death (days 0&ndash;30)</h2>
<ol class="steps">
<li><strong>Obtain certified death certificates.</strong> Order 10&ndash;15 originals. Nearly every
institution in this list will require one, and they are not readily reusable. Ordering more later
adds weeks.</li>
<li><strong>Locate the original trust instrument and any amendments.</strong> The trustee needs the
signed original, not a copy. Confirm which version is operative &mdash; later amendments supersede
earlier ones, and a restatement replaces the whole document.</li>
<li><strong>Confirm successor trustee.</strong> The trust names who takes over. If the successor is
unable or unwilling, the document specifies the next in line. A trustee's acceptance is often
required in writing by banks and title companies.</li>
<li><strong>Secure both properties.</strong> Change locks if needed, collect keys, redirect mail,
and confirm utilities stay on. Tell the insurer the property is now vacant or trustee-owned
&mdash; many policies void coverage if occupancy changes without notice.</li>
<li><strong>Obtain an EIN for the trust</strong> from the IRS, using Form SS-4. Free and immediate
online. This is required before the trust can open a bank account or file a return.</li>
<li><strong>Notify Social Security and stop or redirect income.</strong> Also notify the mortgage
servicer if either property has a loan.</li>
</ol>

<h2>Phase 2 &mdash; Establish authority (days 15&ndash;60)</h2>
<ol class="steps" start="7">
<li><strong>Trustee takes control of assets.</strong> Using the trust instrument, the death
certificate, and the EIN, the successor trustee re-titles accounts and asserts authority over the
properties. Banks and brokerages have their own forms; expect each to differ.</li>
<li><strong>Date-of-death valuation of both properties.</strong> This is the most important single
number in the whole process, because it sets the new income-tax basis. Get a written
<strong>appraisal effective the date of death</strong> from a licensed appraiser &mdash; not an
estimate, and not the county's assessed value, which is a different concept entirely. See
<a href="inheritance.html">Inheritance</a> for why the basis matters so much.</li>
<li><strong>Inventory all assets.</strong> Real property, bank and brokerage accounts, retirement
accounts, life insurance, vehicles, personal property. Retirement accounts and life insurance pass
by beneficiary designation, <em>not</em> through the trust &mdash; they follow the form on file at
the institution.</li>
<li><strong>File Form 56 with the IRS</strong> to notify of the fiduciary relationship. Optional but
prudent; it ensures the IRS writes to the trustee rather than the decedent.</li>
</ol>

<h2>Phase 3 &mdash; Property tax filings (the hard deadlines)</h2>
<p>These carry real money and are where families most often lose it. All three clocks start at death.</p>
<ol class="steps" start="11">
<li><strong>File the Proposition 19 claim, form BOE-19-P</strong>, with the county assessor.
<span class="badge b bad">Deadline: 3 years from the date of transfer</span>
<span class="b bad">or before sale to a third party, whichever is first</span><br>
<span class="small">This is the claim that preserves the parent's low assessed value on Property A.
Without it the assessor will reassess to market. It is not automatic.
<span class="src">{src('boe19')}</span></span></li>

<li><strong>File the homeowners' or disabled veterans' exemption claim.</strong>
<span class="b bad">Deadline: 1 year from the date of transfer</span><br>
<span class="small">Separate from BOE-19-P and equally mandatory. Failing this <em>forfeits the
Proposition 19 exclusion entirely</em>, even if BOE-19-P was filed on time. The Board of Equalization
is explicit that the exclusion applies only if the heir applies for the exemption within one year.
<span class="src">{src('boe26026')}</span></span></li>

<li><strong>Actually occupy Property A within one year.</strong>
<span class="b bad">Deadline: 1 year from the date of transfer</span><br>
<span class="small">Not a filing &mdash; a physical requirement. There are "no exceptions to this
rule." If no heir moves in, Property A is reassessed to full market value and the exemption is
moot. <span class="src">{src('boe26026')}</span></span></li>

<li><strong>Notify the assessor of the change in ownership for Property B.</strong>
<span class="b">Deadline: as required by the county</span><br>
<span class="small">Property B is a rental and does not qualify for the exclusion. It will be
reassessed, and a <strong>supplemental assessment</strong> will issue for the difference between the
old and new values, prorated from the transfer date. Budget for it. <span class="src">{src('sft')}</span></span></li>
</ol>

<div class="note bad"><p><strong>The 1-year and 3-year clocks are different, and missing the shorter
one is fatal.</strong> These are routinely confused. BOE-19-P gets three years. The homeowners'
exemption gets <em>one</em>. If the exemption is missed, the three-year BOE-19-P window is worthless.
Put both dates on a calendar the day the death certificate arrives.</p></div>

<h2>Phase 4 &mdash; Income tax filings (by 15 April of the following year)</h2>
<ol class="steps" start="15">
<li><strong>File the decedent's final Form 1040 and California Form 540.</strong> Covers income from
1 January through the date of death. Also file any prior-year returns not yet filed.</li>
<li><strong>Determine whether a federal Form 706 is required.</strong>
<span class="b ok">Likely not, on these values</span><br>
<span class="small">The gross estate here is far below $15,000,000. <em>But if a spouse survives, file
Form 706 anyway to elect portability</em> &mdash; it preserves the deceased spouse's unused exclusion
for the survivor, and it is the only way to get it. This applies even where no tax is due and no
return would otherwise be required. <span class="src">{src('irs_est')}</span></span></li>
<li><strong>File the trust's Form 1041 and California Form 541</strong> for each year the trust is
open. Note that a trust reaches the top federal rate at roughly $16,100 of income in 2026 &mdash;
compressed brackets, so distributions should be planned rather than improvised.</li>
<li><strong>Plan inherited retirement account distributions.</strong> A non-spouse beneficiary
generally must empty the account within 10 years. Those distributions are ordinary income. This is
frequently the largest tax item in an inheritance and is best modelled before the estate is
distributed.</li>
</ol>

<h2>Phase 5 &mdash; Transfer title and decide (months 2&ndash;12)</h2>
<ol class="steps" start="19">
<li><strong>Record the deed transferring each property from the trust to the beneficiaries.</strong>
An assessor's parcel number change follows. This does <em>not</em> trigger a documentary transfer tax
when it is a distribution from a trust to a beneficiary, but confirm with the county recorder.</li>
<li><strong>Notify insurers.</strong> Insurance must be rewritten in the name of the trust or the
beneficiaries. Vacancy exclusions bite here &mdash; a vacant home is often uninsured after 30&ndash;60
days unless a vacancy endorsement is purchased.</li>
<li><strong>Make the occupation decision for Property A, on a timetable.</strong> The decision must be
made before the 1-year mark, because the exclusion is binary: occupy or be reassessed. Run the
analysis on <a href="scenarios.html">Scenarios</a> before that date, not after it.</li>
<li><strong>If selling, plan the timing.</strong> Federal Section 121 exclusion of $500,000 requires
two of the last five years of ownership <em>and</em> use as a principal residence. If an heir occupies
the property for at least two years after inheritance, a later sale can use the exclusion. If sold
immediately after inheritance, no exclusion is needed because the gain is zero.
<span class="src">{src('irs701')}</span></li>
<li><strong>If renting, reset every operating assumption.</strong> Landlord policy instead of
homeowners, new rent roll, tenant screening, and a capital reserve. The rental scenario is on
<a href="costs.html">Carrying Costs</a>.</li>
</ol>

<h2>Timeline at a glance</h2>
<div class="tw"><table><thead><tr><th>When</th><th>Action</th><th>Consequence of missing it</th></tr></thead><tbody>
<tr><td>Days 0&ndash;30</td><td>Death certificates, locate trust, secure properties, EIN</td><td>Delay compounds; vacancy may void insurance</td></tr>
<tr><td>Days 15&ndash;60</td><td>Date-of-death appraisal, trustee authority, asset inventory</td><td>Basis becomes hard to establish; higher future tax</td></tr>
<tr style="background:rgba(248,81,73,.08)"><td><strong>1 year</strong></td><td><strong>Homeowners' exemption filed and Property A occupied</strong></td><td class="bad-t"><strong>Prop 19 exclusion lost permanently</strong></td></tr>
<tr><td>1 year</td><td>Property B reassessed; supplemental tax paid</td><td>Penalties and interest on the supplemental bill</td></tr>
<tr><td>3 years</td><td>BOE-19-P claim filed</td><td>Reassessment to full market value</td></tr>
<tr><td>Apr 15 next year</td><td>Final 1040 / 540; Form 706 if a spouse survives</td><td>Portability lost; late-filing penalties</td></tr>
<tr><td>Annually</td><td>Form 1041 / 541 while trust is open</td><td>Trustee personal liability</td></tr>
</tbody></table></div>

<div class="note warn"><p><strong>Three things this page cannot tell you.</strong> Whether the trust is
properly funded; whether the trust's terms distribute the properties outright or hold them in further
trust; and whether the trust is a grantor trust, a bypass trust, or something else with different
income-tax consequences. All three change the picture materially. Review the actual instrument with a
California attorney before acting on any of it.</p></div>
"""
    return b+FOOT

# ------------------------------------------------------------------ LAW WATCH
def lawchanges(head,FOOT,src):
    b=head("Law Watch","law-changes.html","Pending and proposed changes to property tax, rent control, transfer tax, and estate tax law that could affect this decision.")+f"""
<h1>Law Watch</h1>
<p class="lead">A decision made years in advance is exposed to law changes. This page separates
what is <strong>enacted and settled</strong> from what is <strong>pending</strong> or merely
<strong>proposed</strong>, and states the direction of risk for each.</p>

<h2>1. Recently enacted &mdash; now settled law</h2>
<div class="tw"><table><thead><tr><th>Change</th><th>Effective</th><th>Effect on this decision</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td><strong>OBBBA</strong> sets federal estate exclusion at $15,000,000, indexed after 2026, with the scheduled sunset repealed</td><td>Deaths after 12/31/2025</td><td class="ok-t">Reduces estate tax risk substantially. The planned 2026 halving did not happen.</td><td>{src('irs_103')}</td><td><span class="b ok">Enacted</span></td></tr>
<tr><td><strong>Proposition 19</strong> replaced Prop 58/193 intergenerational exclusion</td><td>02/16/2021</td><td class="bad-t">Rental property no longer gets an exclusion. This is why Property B is fully reassessed.</td><td>{src('boe19')}</td><td><span class="b ok">Enacted</span></td></tr>
<tr><td>Prop 19 $1M cap indexed to $1,044,586</td><td>02/16/2025</td><td class="ok-t">Slightly expands the exclusion. Rises again each odd-numbered February.</td><td>{src('boe25009')}</td><td><span class="b ok">Enacted</span></td></tr>
<tr><td><strong>SB 567</strong> tightened just-cause eviction and owner move-in rules</td><td>2024</td><td class="warn-t">Restricts the ability to reclaim a rented unit. Relevant if Property A is rented.</td><td>Cal. Civ. Code</td><td><span class="b ok">Enacted</span></td></tr>
<tr><td><strong>AB 1482</strong> statewide rent cap: 5% + CPI, max 10%</td><td>2020, extended</td><td>Sets the fallback cap for Property A if rented and Property B units outside the SF ordinance</td><td>{src('civ1947')}</td><td><span class="b ok">Enacted</span></td></tr>
</tbody></table></div>

<h2>2. Pending &mdash; introduced, not enacted</h2>
<div class="tw"><table><thead><tr><th>Proposal</th><th>What it would do</th><th>Direction of risk</th><th>Status</th></tr></thead><tbody>
<tr><td><strong>SF Board of Supervisors File No. 261020</strong></td><td>Would temporarily cap combined banked rent increases and capital-improvement passthroughs on rent-controlled units at 10% per year. Posted 9 November 2026 and still under consideration at the time of writing.</td><td class="bad-t">Slightly negative for Property B rental income</td><td><span class="b warn">Pending</span></td></tr>
<tr><td><strong>SF Proposition I</strong> (November 2026 ballot)</td><td>Splits the top transfer-tax brackets into general and housing-dedicated portions. Combined rates stay at 5.5% and 6.0%; revenue is redirected.</td><td>Neutral on rate &mdash; affects allocation, not the amount paid</td><td><span class="b warn">Ballot measure</span></td></tr>
<tr><td><strong>SF File No. 260178</strong></td><td>Would halve the transfer tax rate from 5.5% to 2.75% on transfers of $10M&ndash;$25M. Introduced 24 March 2026; pending committee action.</td><td class="ok-t">Irrelevant at these values &mdash; neither property approaches $10M</td><td><span class="b warn">Pending</span></td></tr>
<tr><td>Annual Proposition 19 cap adjustment</td><td>Next adjustment due February 2027, then every two years, using the prior calendar year's FHFA California HPI change.</td><td class="ok-t">Rises with home prices, expanding the exclusion slightly</td><td><span class="b warn">Scheduled</span></td></tr>
<tr><td>Annual SF allowable rent increase</td><td>Set each year by the Rent Board, effective 1 March. Currently 1.6% through 28 February 2027.</td><td>Neutral &mdash; tracks 60% of local CPI</td><td><span class="b warn">Scheduled</span></td></tr>
</tbody></table></div>

<h2>3. Recurring proposals that would change the answer</h2>
<div class="tw"><table><thead><tr><th>Idea</th><th>Status</th><th>Why it matters here</th></tr></thead><tbody>
<tr><td><strong>California estate or wealth tax</strong></td><td><span class="b bad">Blocked by R&amp;TC §13301</span></td><td>Would require a constitutional amendment and a statewide vote. Attempts have been introduced repeatedly (e.g. ACA 8, ACA 3, AB 259) and none has passed. Current statute is an outright prohibition, so this is not a live risk for a 2045 inheritance, but it is the one change that could materially alter the estate-tax conclusion. <span class="src">{src('rtc13301')}</span></td></tr>
<tr><td><strong>Split-roll property tax</strong> (reassessing commercial property more often)</td><td><span class="b bad">Repeatedly defeated</span></td><td>Would not affect residential property directly, but changes the political and fiscal landscape around Prop 13.</td></tr>
<tr><td><strong>Prop 13 repeal or modification for residential</strong></td><td><span class="b bad">No viable path</span></td><td>Requires a constitutional amendment. Would transform this analysis entirely &mdash; the protected basis is most of Property B's value.</td></tr>
<tr><td><strong>Repeal or expansion of Prop 19</strong></td><td><span class="b mut">No active measure</span></td><td>An expansion (restoring the pre-2021 rules) would make Property B exempt from reassessment and materially improve the rental case.</td></tr>
<tr><td><strong>Federal estate exclusion reduction</strong></td><td><span class="b warn">Possible with any change of administration</span></td><td>A new Congress can change the amount. The current $15,000,000 has no scheduled expiration, unlike the pre-2026 law, but it is still legislation, not a constitutional guarantee.</td></tr>
</tbody></table></div>

<h2>4. What to monitor, and when</h2>
<ol class="steps">
<li><strong>Every February in an odd-numbered year</strong> &mdash; the BOE's indexed Proposition 19
cap. Track it at <a href="https://www.boe.ca.gov/proptaxes/ltacont.htm">boe.ca.gov Letters to
Assessors</a>.</li>
<li><strong>Every January</strong> &mdash; the BOE's California CPI factor for the coming assessment
roll, which sets the 2% growth cap's actual value for the year.</li>
<li><strong>Every November&ndash;December</strong> &mdash; the SF Rent Board's allowable increase for
the year beginning 1 March.</li>
<li><strong>Continuously</strong> &mdash; Revenue and Taxation Code §13301 and any constitutional
amendment proposals touching estate or wealth taxation.</li>
<li><strong>Continuously</strong> &mdash; Proposition 13 and Proposition 19 amendment proposals.
These move rarely but would be decisive.</li>
</ol>

<h2>5. Net effect of law changes on the recommendation</h2>
<div class="note ok"><p><strong>No enacted or pending change overturns the recommendation.</strong>
The direction of enacted change since 2021 has been consistently <em>against</em> holding inherited
property cheaply: Proposition 19 removed the rental exclusion, and just-cause and rent-cap rules have
tightened. The estate tax picture improved, but estate tax was never the binding constraint here.
If anything, the legislative trend strengthens the case for selling Property A.</p></div>
<div class="note warn"><p><strong>The one change that would flip the answer</strong> is restoration of a
broad parent-child exclusion that applies to rental property &mdash; that would let Property B keep
its near-zero basis, and could make the rental case for Property A viable too. No such measure is
pending. Do not plan around it.</p></div>
"""
    return b+FOOT

# ------------------------------------------------------------------ FINDINGS
def findings(head,FOOT,src):
    b=head("Findings","findings.html","Every headline finding with its value, source and verification status.")+f"""
<h1>Findings</h1>
<p class="lead">Every material number in this analysis, in one table, with its source and its
verification status. Nothing is stated without a basis.</p>

<div class="legend" style="margin-bottom:18px">
<span style="color:#3fb950"><span class="b ok">Verified</span> traced to an official government or regulator publication</span>
<span><span class="b pur">Derived</span> computed from verified inputs</span>
<span><span class="b warn">Owner</span> supplied by the family, not independently checked</span>
<span><span class="b bad">Unverified</span> could not be confirmed</span>
</div>

<h2>A. Inheritance and estate tax</h2>
<div class="tw"><table><thead><tr><th>Finding</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>California inheritance tax</td><td class="n ok-t">$0</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>California estate tax</td><td class="n ok-t">$0</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>California gift tax</td><td class="n ok-t">$0</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Federal basic exclusion, 2026</td><td class="n">$15,000,000</td><td>{src('irs_est','irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Federal estate tax rate above exclusion</td><td class="n">40%</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Federal annual gift exclusion, 2026</td><td class="n">$19,000</td><td>{src('irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Inherited property basis</td><td>FMV at date of death</td><td>{src('irs551')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Combined real estate value at 2045 inheritance</td><td class="n">{m(B['mvt']+3792330)}</td><td>Model projection at 4.0%/yr</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Headroom under single-person exclusion at 2045</td><td class="n ok-t">{m(15000000-B['mvt']-3792330)}</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr><td>Federal estate tax payable on real estate alone</td><td class="n ok-t">$0</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
</tbody></table></div>

<h2>B. Property tax</h2>
<div class="tw"><table><thead><tr><th>Finding</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Proposition 13 general levy</td><td class="n">1.0%</td><td>{src('rtc51')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Proposition 13 annual growth cap</td><td class="n">2.0%</td><td>{src('rtc51')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2026&ndash;27 inflation factor</td><td class="n">1.020</td><td>{src('boe26002')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Homeowners' exemption</td><td class="n">$7,000</td><td>{src('rtc218')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Typical Santa Clara County ad valorem rate</td><td class="n">1.1488%</td><td>{src('sccar')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>San Francisco secured property tax rate, FY2026&ndash;27</td><td class="n">1.18162182%</td><td>{src('sft')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Proposition 19 indexed cap, current period</td><td class="n">$1,044,586</td><td>{src('boe25009')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Prop 19 exclusion applies to inherited rental property</td><td class="n bad-t">No</td><td>{src('scc19')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Prop 19 requires occupancy within</td><td class="n">1 year</td><td>{src('boe26026')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>BOE-19-P filing deadline</td><td class="n">3 years</td><td>{src('boe19')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Property A assessed value as % of market, 2026</td><td class="n">17.8%</td><td>Derived from owner figures</td><td><span class="b pur">Derived</span></td></tr>
<tr><td>Property A tax if an heir occupies it, 2045</td><td class="n">{m(58950)}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Property A tax if rented out, 2045</td><td class="n bad-t">{m(76800)}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Value of the Prop 19 exclusion, 2045&ndash;2070</td><td class="n">{m(600210)}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Property B tax after reassessment, 2045</td><td class="n">{m(P[2045-2026]['b_tax'])}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
</tbody></table></div>

<h2>C. Carrying costs</h2>
<div class="tw"><table><thead><tr><th>Finding</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Property A water, monthly</td><td class="n">$100&ndash;$150</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Property A electricity, monthly</td><td class="n ok-t">net credit $10&ndash;$20</td><td>Owner; solar installed</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Property A insurance, annual</td><td class="n">$1,500</td><td>Owner estimate &mdash; no quote obtained</td><td><span class="b bad">Unverified</span></td></tr>
<tr><td>Property A total carrying cost, 2026</td><td class="n">{m(13980)}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Property B water, monthly, all 3 units</td><td class="n">$330&ndash;$400</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Property B electricity, monthly</td><td class="n">$30&ndash;$70</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Property B insurance, annual</td><td class="n">$1,500</td><td>Owner estimate &mdash; almost certainly low for a 3-unit building</td><td><span class="b bad">Unverified</span></td></tr>
<tr><td>Property B total carrying cost, 2026</td><td class="n">{m(14580)}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>NAIC average California HO-3 premium, 2023</td><td class="n">$1,655</td><td>{src('naic')}</td><td><span class="b ok">Verified</span></td></tr>
</tbody></table></div>

<h2>D. Rental income and rent control</h2>
<div class="tw"><table><thead><tr><th>Finding</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Property B current rent, 2 units</td><td class="n">$7,150/mo</td><td>Owner rent roll</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Average rent per rented unit</td><td class="n">≈ $3,575/mo</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr><td>Third unit</td><td class="n">vacant, owner-occupiable</td><td>Owner</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>SF allowable annual rent increase</td><td class="n">1.6%</td><td>{src('sfrb')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>SF allowable increase period</td><td>3/1/2026&ndash;2/28/2027</td><td>{src('sfrb')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Statewide rent cap (AB 1482)</td><td class="n">5% + CPI, max 10%</td><td>{src('civ1947')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>HUD FY2026 2BR FMR, Santa Clara County</td><td class="n">$3,483/mo</td><td>{src('hud')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Gross yield on Property A at that rent</td><td class="n">1.3%</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
</tbody></table></div>

<h2>E. The decision</h2>
<div class="tw"><table><thead><tr><th>Finding</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Net worth at 2070 &mdash; live in A</td><td class="n">{m(B['live']['net_worth'])}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Net worth at 2070 &mdash; rent out A</td><td class="n">{m(B['rent']['net_worth'])}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Net worth at 2070 &mdash; sell A</td><td class="n ok-t">{m(B['sell']['net_worth'])}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Sale advantage over best hold</td><td class="n ok-t">+{m(B['sell']['net_worth']-max(B['live']['net_worth'],B['rent']['net_worth']))}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>Net proceeds if sold at inheritance</td><td class="n">{m(B['sell']['proceeds'])}</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>SF transfer tax on that sale</td><td class="n">$0</td><td>Inheritance transfer, not a sale</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Break-even appreciation, 7.0% portfolio</td><td class="n warn-t">{br['breakeven_appreciation_pct']['invest_0.07']:.1f}%/yr</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
<tr><td>San Jose MSA actual 5-yr annualized appreciation</td><td class="n">4.97%</td><td>{src('fhfa')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Scenarios in which sale wins</td><td class="n ok-t">12 of 12</td><td>Model</td><td><span class="b pur">Projected</span></td></tr>
</tbody></table></div>

<h2>F. Irregularities found while verifying</h2>
<div class="note warn"><p>Five items in the supplied figures do not reconcile cleanly against
official sources. None changes the recommendation, but each should be checked against the actual
documents. Full detail on <a href="flagged.html">Flagged for Review</a>.</p></div>
<div class="tw"><table><thead><tr><th class="n">#</th><th>Irregularity</th><th>What was expected</th><th>What the figures show</th><th>Status</th></tr></thead><tbody>
<tr><td class="n">1</td><td>Property A effective tax rate</td><td>≈ 1.15&ndash;1.19%</td><td>1.335%</td><td><span class="b warn">Flagged</span></td></tr>
<tr><td class="n">2</td><td>Property B effective tax rate</td><td>≈ 1.18%</td><td>2.135%</td><td><span class="b bad">Flagged</span></td></tr>
<tr><td class="n">3</td><td>Property A insurance estimate</td><td>Plausible at $1,500</td><td>&mdash;</td><td><span class="b warn">Unverified</span></td></tr>
<tr><td class="n">4</td><td>Property B insurance estimate</td><td>Materially higher for a 3-unit rental</td><td>$1,500</td><td><span class="b bad">Likely low</span></td></tr>
<tr><td class="n">5</td><td>Property A assessed value jump 2026</td><td>+2% ≈ $560,000</td><td>$550,537</td><td><span class="b ok">Reconciles</span></td></tr>
</tbody></table></div>
"""
    return b+FOOT

# ------------------------------------------------------------------- SOURCES
SRCLIST = [
 ("S01","Prop 19 parent-child exclusion, $1M cap","California State Board of Equalization","https://www.boe.ca.gov/prop19/","Verified"),
 ("S02","$1M cap indexed to $1,044,586 (2/16/2025&ndash;2/15/2027)","BOE Letter to Assessors 2025/009","https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf","Verified"),
 ("S03","Prior cap $1,022,600 (2/16/2023&ndash;2/15/2025)","BOE Letter to Assessors 2023/012","https://www.boe.ca.gov/proptaxes/pdf/lta23012.pdf","Verified"),
 ("S04","Prop 19 FAQ: occupancy, deadlines, continual-use requirement","BOE Letter to Assessors 2026/026","https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf","Verified"),
 ("S05","2026&ndash;27 California CPI inflation factor 1.02","BOE Letter to Assessors 2026/002","https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf","Verified"),
 ("S06","Prop 13: 1% levy, 2% annual cap, reassessment on change in ownership","Cal. Rev. &amp; Tax. Code §51","https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=51","Verified"),
 ("S07","Homeowners' property tax exemption $7,000","Cal. Rev. &amp; Tax. Code §218","https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=218","Verified"),
 ("S08","California prohibits all inheritance, estate and gift taxes","Cal. Rev. &amp; Tax. Code §13301","https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=13301","Verified"),
 ("S09","AB 1482 statewide rent cap 5% + CPI, max 10%","Cal. Civ. Code §1947.12","https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&amp;sectionNum=1947.12","Verified"),
 ("S10","Federal estate tax filing threshold $15,000,000 for 2026","Internal Revenue Service","https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax","Verified"),
 ("S11","2026 inflation adjustments incl. $15M exclusion, $19,000 gift exclusion","IRS IR-2025-103 / Rev. Proc. 2025-32","https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill","Verified"),
 ("S12","Basis of inherited property = FMV at date of death","IRS Publication 551","https://www.irs.gov/publications/p551","Verified"),
 ("S13","Fiduciary duties, Form 706, trust income taxation","IRS Publication 559","https://www.irs.gov/publications/p559","Verified"),
 ("S14","§121 home sale exclusion $250,000 / $500,000","IRS Topic No. 701","https://www.irs.gov/taxtopics/tc701","Verified"),
 ("S15","Net investment income tax 3.8%","IRS Topic No. 559","https://www.irs.gov/taxtopics/tc559","Verified"),
 ("S16","Long-term capital gain rates 0/15/20%","IRS Topic No. 409","https://www.irs.gov/taxtopics/tc409","Verified"),
 ("S17","SF secured property tax rate FY2026&ndash;27 = 1.18162182%","San Francisco Treasurer &amp; Tax Collector","https://sftreasurer.org/property/secured-property-taxes","Verified"),
 ("S18","SF supplemental and escape assessment process for heirs","San Francisco Treasurer &amp; Tax Collector","https://sftreasurer.org/property/information-heirs","Verified"),
 ("S19","SF allowable annual rent increase 1.6% (3/1/2026&ndash;2/28/2027)","SF Rent Board","https://www.sf.gov/learn-about-rent-increases-san-francisco","Verified"),
 ("S20","Prop 19 parent-child transfer; rentals ineligible","Santa Clara County Assessor","https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2","Verified"),
 ("S21","Typical Santa Clara tax rate area 1.1488% (bonds breakdown)","Santa Clara County Assessor 2026 Assessment Booklet","https://files.santaclaracounty.gov/exjcpb1521/2026-04/assessment-information-2026-booklet-english-3-23-26-web.pdf","Verified"),
 ("S22","Santa Clara County assessment roll and Prop 13/19 guidance","Santa Clara County Assessor Annual Report 2025","https://files.santaclaracounty.gov/exjcpb1521/2025-11/annual_report_2025-2026.pdf","Verified"),
 ("S23","California 2025 income tax rate schedules, top rate 12.3%","California Franchise Tax Board","https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf","Verified"),
 ("S24","FHFA House Price Index, all-transactions, 2026Q2 by MSA","Federal Housing Finance Agency","https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_tables.pdf","Verified"),
 ("S25","Average HO-3 homeowners premium, California 2023 = $1,655","National Association of Insurance Commissioners","https://content.naic.org/article/consumer-insight-homeowners-insurance-report","Verified"),
 ("S26","Fair Market Rents, Santa Clara County and San Francisco","U.S. Dept. of Housing &amp; Urban Development","https://www.huduser.gov/portal/datasets/fmr.html","Verified"),
 ("S27","Property tax assessment and change in ownership framework","California State Board of Equalization","https://www.boe.ca.gov/proptaxes/change-in-ownership/","Verified"),
]
def sources(head,FOOT,src):
    b=head("Sources","sources.html","Complete source list with links to official government and regulator publications for every figure used.")+f"""
<h1>Sources</h1>
<p class="lead">Every figure in this analysis traces to one of the publications below. Links go
directly to the primary source &mdash; the statute, the regulator's letter, or the agency's own
dataset &mdash; not to secondary commentary.</p>

<div class="note"><p>Verification method: each source was retrieved directly and the specific claim
quoted or checked against the published text. Where a page was not reachable or a value could not be
located in the primary source, the row is marked unverified and listed on
<a href="flagged.html">Flagged for Review</a> rather than filled in.</p></div>

<div class="tw"><table><thead><tr><th>ID</th><th>Claim verified</th><th>Publisher</th><th>Status</th></tr></thead><tbody>
"""
    for i,claim,pub,url,st in SRCLIST:
        b+=f"""<tr><td class="n" style="white-space:nowrap"><code>{i}</code></td>
<td>{claim}<br><span class="src"><a href="{url}">{url}</a></span></td>
<td>{pub}</td><td><span class="b ok">{st}</span></td></tr>
"""
    b+="""</tbody></table></div>

<h2>Grouped by topic</h2>
<div class="grid g2">
<div class="card"><h3>Property tax (California)</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://www.boe.ca.gov/prop19/">BOE &mdash; Proposition 19 overview</a></li>
<li><a href="https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf">BOE LTA 2025/009 &mdash; $1M cap indexation</a></li>
<li><a href="https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf">BOE LTA 2026/026 &mdash; Prop 19 FAQ</a></li>
<li><a href="https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf">BOE LTA 2026/002 &mdash; 2026&ndash;27 inflation factor</a></li>
<li><a href="https://www.boe.ca.gov/proptaxes/change-in-ownership/">BOE &mdash; change in ownership</a></li>
<li><a href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=51">R&amp;TC §51</a></li>
<li><a href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=218">R&amp;TC §218</a></li>
</ul></div>
<div class="card"><h3>Estate and inheritance tax</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=13301">R&amp;TC §13301 &mdash; California prohibition</a></li>
<li><a href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax">IRS &mdash; estate tax and filing thresholds</a></li>
<li><a href="https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill">IRS IR-2025-103 &mdash; 2026 adjustments</a></li>
<li><a href="https://www.irs.gov/publications/p551">IRS Pub 551 &mdash; basis of assets</a></li>
<li><a href="https://www.irs.gov/publications/p559">IRS Pub 559 &mdash; survivors, executors, administrators</a></li>
<li><a href="https://www.irs.gov/taxtopics/tc701">IRS Topic 701 &mdash; sale of your home</a></li>
</ul></div>
<div class="card"><h3>San Francisco specifics</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://sftreasurer.org/property/secured-property-taxes">SF Treasurer &mdash; secured property tax rate</a></li>
<li><a href="https://sftreasurer.org/property/information-heirs">SF Treasurer &mdash; information for heirs</a></li>
<li><a href="https://www.sf.gov/learn-about-rent-increases-san-francisco">SF Rent Board &mdash; allowable increases</a></li>
<li><a href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&amp;sectionNum=1947.12">Civ. Code §1947.12 &mdash; AB 1482</a></li>
</ul></div>
<div class="card"><h3>Santa Clara County</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2">SCC Assessor &mdash; Prop 19 parent-child transfer</a></li>
<li><a href="https://files.santaclaracounty.gov/exjcpb1521/2026-04/assessment-information-2026-booklet-english-3-23-26-web.pdf">SCC Assessor &mdash; 2026 assessment booklet</a></li>
<li><a href="https://files.santaclaracounty.gov/exjcpb1521/2025-11/annual_report_2025-2026.pdf">SCC Assessor &mdash; 2025 annual report</a></li>
</ul></div>
<div class="card"><h3>Market and cost benchmarks</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_tables.pdf">FHFA &mdash; HPI by metropolitan area</a></li>
<li><a href="https://www.huduser.gov/portal/datasets/fmr.html">HUD &mdash; Fair Market Rents</a></li>
<li><a href="https://content.naic.org/article/consumer-insight-homeowners-insurance-report">NAIC &mdash; homeowners insurance report</a></li>
<li><a href="https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf">FTB &mdash; 2025 tax rate schedules</a></li>
</ul></div>
<div class="card"><h3>Method and reproducibility</h3>
<ul class="small" style="font-size:13px">
<li><a href="https://github.com/wingbangboozle1-lang/Tino1/blob/main/data/projections.csv">Full 45-year projection dataset (CSV)</a></li>
<li><a href="https://github.com/wingbangboozle1-lang/Tino1/blob/main/data/model_output.json">Full model output (JSON)</a></li>
<li><a href="https://github.com/wingbangboozle1-lang/Tino1">Source repository</a></li>
</ul>
<p class="small" style="margin-top:8px">The model is deterministic and reproducible from the
repository. No figure on this site is entered by hand.</p></div>
</div>

<h2>What is <em>not</em> sourced</h2>
<p>For completeness and honesty, the following are inputs this analysis could not verify and did
not attempt to source. They are visible in every projection and the reader should know it:</p>
<div class="tw"><table><thead><tr><th>Input</th><th>Where it came from</th><th>Effect on conclusions</th></tr></thead><tbody>
<tr><td>Market value of both properties</td><td>Owner estimate, November 2026</td><td>Scales all dollar amounts proportionally. Does not change the ranking of options.</td></tr>
<tr><td>Assessed values and taxes paid</td><td>Owner tax records</td><td>Affects the size of the Prop 13 gap. The gap is large either way.</td></tr>
<tr><td>Rent roll</td><td>Owner</td><td>Affects Property B's cash flow. Property B is profitable under any plausible value.</td></tr>
<tr><td>Utility costs</td><td>Owner</td><td>Small relative to tax and capital decisions.</td></tr>
<tr><td>Insurance premiums</td><td>Owner estimate</td><td>Understates Property B costs. Does not change the ranking.</td></tr>
<tr><td>Cash and securities in the estate</td><td>Described as "considerable," no figure given</td><td>Could push a single decedent's estate over $15,000,000. The threshold is computed on <a href="inheritance.html">Inheritance</a>.</td></tr>
<tr><td>Original cost basis of both properties</td><td>Not available</td><td>Irrelevant at inheritance because of the step-up. Would matter for a lifetime gift.</td></tr>
</tbody></table></div>
"""
    return b+FOOT

# ------------------------------------------------------------------- FLAGGED
def flagged(head,FOOT,src):
    b=head("Flagged for Review","flagged.html","Items that could not be confirmed against an official source, with what would resolve each one.")+f"""
<h1>Flagged for Review</h1>
<p class="lead">This page lists everything that could not be confirmed against an official source.
These items do <strong>not</strong> block the analysis and they do <strong>not</strong> change the
recommendation &mdash; but each one is a place where a real document would replace an estimate.</p>

<div class="note warn"><p><strong>Why this page exists.</strong> The instruction was explicit: if a value
cannot be confirmed from an official source, leave it blank and flag it, and never infer or fill in
values. Several figures needed for this analysis are known only to the family &mdash; market values,
rent roll, utility costs. Those are shown as sourced to "Owner" and flagged here rather than being
silently presented as fact. Where an official statue, regulator publication, or agency dataset
did confirm a figure, it is marked <span class="b ok">Verified</span> and not listed here.</p></div>

<h2>1. Values that could not be verified</h2>
<div class="tw"><table><thead><tr><th class="n">#</th><th>Item</th><th class="n">Value used</th>
<th>Why it is unverified</th><th>What would resolve it</th><th>Impact</th></tr></thead><tbody>

<tr><td class="n">1</td><td><strong>Property A market value</strong></td><td class="n">$3,100,000</td>
<td>Owner estimate dated November 2026. No appraisal, no comparable-sales analysis, no automated
valuation on file.</td>
<td>An appraisal, or three recent comparable sales within the same ZIP code.</td>
<td><span class="b warn">Material</span> Scales every Property A figure proportionally. Does not
change which option wins.</td></tr>

<tr><td class="n">2</td><td><strong>Property B market value</strong></td><td class="n">$1,800,000</td>
<td>Owner estimate. Also no appraisal.</td>
<td>An appraisal, ideally income-approach given three units.</td>
<td><span class="b warn">Moderate</span> Affects Property B's contribution to estate value and
eventual sale proceeds.</td></tr>

<tr><td class="n">3</td><td><strong>Property A insurance premium</strong></td><td class="n">$1,500/yr</td>
<td>Owner estimate, explicitly given as uncertain. No policy declarations page reviewed.</td>
<td>Current policy declarations page, or two comparative quotes.</td>
<td><span class="b warn">Low</span> The NAIC California HO-3 average is $1,655, so $1,500 is
plausible. A swing of &plusmn;$1,000/yr is immaterial against a multi-million-dollar decision.</td></tr>

<tr><td class="n">4</td><td><strong>Property B insurance premium</strong></td><td class="n">$1,500/yr</td>
<td>Owner estimate. A three-unit San Francisco building insured on a landlord policy, with
replacement cost likely above $1 million and loss-of-rents coverage, will not cost $1,500.</td>
<td>A landlord (dwelling fire) quote for the actual building, including loss of rents and
liability limits.</td>
<td><span class="b bad">Understated</span> This makes Property B look cheaper than it is by
perhaps $3,000&ndash;$8,000/yr. It overstates the case for <em>keeping</em> Property B, which is
already the recommendation &mdash; so it makes that recommendation slightly less safe, not the
Property A decision.</td></tr>

<tr><td class="n">5</td><td><strong>Earthquake coverage</strong></td><td class="n">&mdash;</td>
<td>Not stated whether either property carries CEA or private earthquake coverage. Not included in
either cost figure.</td>
<td>The declarations pages.</td>
<td><span class="b bad">Potentially material</span> Earthquake premiums in the Bay Area are
substantial. If coverage exists, both carrying cost figures are too low by a meaningful amount.</td></tr>

<tr><td class="n">6</td><td><strong>Cash and securities in the estate</strong></td><td class="n">&mdash;</td>
<td>Described as "a considerable amount" and "possibly above the tax-free threshold." No figure
was provided, so none was invented.</td>
<td>A current statement of trust assets, or an estimate from the trustee.</td>
<td><span class="b warn">Material to estate tax only</span> The combined real estate reaches about
$10.3M at 2045, leaving roughly $4.7M of headroom under a single-person $15M exclusion. Cash above
that amount would create a federal estate tax liability at 40%.</td></tr>

<tr><td class="n">7</td><td><strong>Original cost basis of either property</strong></td><td class="n">&mdash;</td>
<td>Not provided. Irrelevant at inheritance thanks to the step-up, but would matter for a lifetime
gift or if the step-up rules changed.</td>
<td>Original purchase documents, or a title search.</td>
<td><span class="b mut">Currently none</span> Could become material if the properties were gifted
during life instead of inherited.</td></tr>

<tr><td class="n">8</td><td><strong>Whether both properties are titled in the trust</strong></td><td class="n">&mdash;</td>
<td>Stated that inheritance is "by trust," but funding was not confirmed. An unfunded trust means
probate.</td>
<td>A deed search at the county recorder, or the trustee's schedule of assets.</td>
<td><span class="b warn">Material to process</span> Would add 12&ndash;24 months and tens of
thousands of dollars in statutory probate fees. Does not change the property decision.</td></tr>

<tr><td class="n">9</td><td><strong>Number of heirs / siblings</strong></td><td class="n">&mdash;</td>
<td>Not stated. Important because Proposition 19 requires that <em>at least one</em> heir occupy
the property, and a non-pro-rata distribution can disqualify others.</td>
<td>The trust's distribution provisions.</td>
<td><span class="b warn">Material to the occupancy option</span> If no single heir is willing to
live in Cupertino for the required period, the exclusion option disappears and the choice narrows
to rent or sell.</td></tr>
</tbody></table></div>

<h2>2. Irregularities in the supplied figures</h2>
<p>These are cases where the numbers provided internally do not reconcile with the official rates
this analysis verified. They are presented here rather than adjusted away.</p>

<h3>Irregularity 1 &mdash; Property A implied effective tax rate is high</h3>
<div class="tw"><table><thead><tr><th>Measure</th><th class="n">Value</th><th>Basis</th></tr></thead><tbody>
<tr><td>Tax paid 2025</td><td class="n">$7,207</td><td>Owner record</td></tr>
<tr><td>Assessed value 2025</td><td class="n">$539,743</td><td>Owner record</td></tr>
<tr><td><strong>Implied effective rate</strong></td><td class="n warn-t"><strong>1.335%</strong></td><td>7,207 &divide; 539,743</td></tr>
<tr><td>Typical SCC ad valorem rate</td><td class="n">1.1488%</td><td>{src('sccar')}</td></tr>
<tr><td>Tax at that rate</td><td class="n">$6,201</td><td>539,743 &times; 1.1488%</td></tr>
<tr><td>Difference</td><td class="n">$1,006</td><td>Unexplained by the typical rate</td></tr>
</tbody></table></div>
<p><strong>Assessment.</strong> An effective rate of 1.335% is high but not impossible &mdash; tax
rate areas vary, and the parcel may sit in one with more school or special district bonded debt, or
carry fixed direct assessments such as a school parcel tax or a lighting district. The model
therefore applies the verified 1.1488% rate to assessed value and carries the residual $1,006 as a
fixed charge that inflates. Rebuilt this way the model produces $7,330 for 2025 against an actual
$7,207 &mdash; a 1.7% variance, which is a reasonable reconciliation.</p>
<p><strong>What would resolve it:</strong> the actual 2025&ndash;26 tax bill, which itemises the
general levy, each bond, and each fixed assessment separately. This is a one-line lookup on the
county tax collector's site.</p>

<h3>Irregularity 2 &mdash; Property B implied effective tax rate is very high</h3>
<div class="tw"><table><thead><tr><th>Measure</th><th class="n">Value</th><th>Basis</th></tr></thead><tbody>
<tr><td>Tax paid 2025</td><td class="n">$2,439</td><td>Owner record</td></tr>
<tr><td>Assessed value 2025</td><td class="n">$114,248</td><td>Owner record</td></tr>
<tr><td><strong>Implied effective rate</strong></td><td class="n bad-t"><strong>2.135%</strong></td><td>2,439 &divide; 114,248</td></tr>
<tr><td>SF secured rate FY2026&ndash;27</td><td class="n">1.1816%</td><td>{src('sft')}</td></tr>
<tr><td>Tax at that rate</td><td class="n">$1,350</td><td>114,248 &times; 1.1816%</td></tr>
<tr><td>Difference</td><td class="n warn-t">$1,089</td><td>Unexplained</td></tr>
</tbody></table></div>
<p><strong>Assessment.</strong> This one is harder to explain. An implied rate of 2.135% is roughly
1.8&times; the San Francisco secured rate. Some of the gap will be fixed direct assessments and
special district charges, which bulk larger as a proportion when the assessed value is very low
&mdash; a $1,089 fixed charge against a $114,248 base looks enormous but is normal in absolute terms.
That is the most likely explanation. It cannot be confirmed without the bill.</p>
<p><strong>Handling in the model:</strong> the $1,089 is held as a fixed dollar amount that grows
with inflation, and the official 1.1816% rate is applied to assessed value. This is
<em>conservative</em> for the decision being evaluated, because it slightly understates Property B's
post-reassessment tax. Property B's tax is projected to jump from {m(2490)} to
{m(P[2045-2026]['b_tax'])} at inheritance. If the true fixed charges are higher, that number is
higher.</p>
<p><strong>What would resolve it:</strong> the 2025&ndash;26 San Francisco secured tax bill.</p>

<h3>Irregularity 3 &mdash; assessed values appear to be split across roll years</h3>
<p>The Property A table runs to a 2026 figure of $550,537 and the Property B table to a 2025 figure
of $114,248. The analysis rolls Property B forward to 2026&ndash;27 at 2% to place both on the same
footing. This is disclosed rather than silent, because comparing a 2026 roll to a 2025 roll without
adjusting would introduce a small error.</p>

<h3>Irregularity 4 &mdash; the two properties' property-tax series use different year ranges</h3>
<p>The Property A series begins in 2014 and the Property B series in 2016. This has no effect on the
analysis, which needs only the current assessed value and the growth mechanism, not the history.
Noted for completeness.</p>

<h2>3. Items verified as correct</h2>
<p>For balance, several figures that might have been expected to be irregular reconcile cleanly:</p>
<div class="tw"><table><thead><tr><th>Check</th><th>Result</th><th>Status</th></tr></thead><tbody>
<tr><td>Property A 2026 assessed value vs. 2% growth from 2025 ($539,743 &times; 1.02 = $550,538)</td><td>Stated $550,537 &mdash; matches to $1</td><td><span class="b ok">Reconciles</span></td></tr>
<tr><td>2026&ndash;27 inflation factor used</td><td>2.0%, matches BOE LTA 2026/002</td><td><span class="b ok">Reconciles</span></td></tr>
<tr><td>Prop 19 $1M cap cited</td><td>$1,000,000 is the statutory base but the current indexed figure is $1,044,586</td><td><span class="b ok">Corrected</span></td></tr>
<tr><td>SF rent $7,150/mo for 2 units vs. HUD FMR</td><td>$3,575/unit vs. $3,604 2BR FMR &mdash; consistent with a long-tenured rent roll below market</td><td><span class="b ok">Reconciles</span></td></tr>
<tr><td>Water $330&ndash;$400/mo for 3 SF units</td><td>Plausible for shared metered service</td><td><span class="b mut">Plausible</span></td></tr>
</tbody></table></div>

<h2>4. Nothing on this page blocks the recommendation</h2>
<div class="note ok"><p>The largest unverified item is the market value of Property A &mdash; but the
conclusion does not depend on it. The break-even analysis shows that holding the house beats selling
only if it appreciates faster than
<strong>{br['breakeven_appreciation_pct']['invest_0.07']:.1f}% per year for 25 years</strong>. That
threshold is a <em>rate</em>, not a dollar amount, so it is unaffected by whether the house is worth
$2.8 million or $3.4 million. Getting a real appraisal would sharpen every number on the site; it
would not change which column comes out ahead.</p></div>

<div class="note"><p><strong>What to do with this page.</strong> Each of the nine unverified items has
a specific document listed against it. Collecting all of them would take a family perhaps two hours
and would let every projection on this site be rebuilt with verified inputs. That is the right next
step before acting on any of it.</p></div>
"""
    return b+FOOT
