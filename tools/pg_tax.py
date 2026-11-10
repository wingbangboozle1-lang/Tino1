import json
d=json.load(open("data/model_output.json")); B=d["base"]; BI=d["byinh"]; P=d["proj"]
def m(x):
    return ("&minus;$%s" % f"{abs(x):,.0f}") if x < 0 else f"${x:,.0f}"
def mm(x): return f"${x/1e6:,.2f}M"

def prop_tax(head,FOOT,src):
    r2045_live = P[2045-2026]; r2045_rent = P[2045-2026]
    body=head("Property Tax","property-tax.html","How Proposition 13 and Proposition 19 determine property tax before and after inheritance for both properties.")+f"""
<h1>Property Tax</h1>
<p class="lead">California property tax is governed by two constitutional amendments that pull in
opposite directions at inheritance: <strong>Proposition 13</strong> keeps tax low by capping the
assessed value, and <strong>Proposition 19</strong> decides whether that low basis survives a
transfer to the next generation. For these two properties, Proposition 19 is worth roughly
{m(600210)} over 25 years &mdash; but only if an heir actually moves in.</p>

<h2 id="prop13">1. The baseline: Proposition 13</h2>
<p>Proposition 13 is codified in article XIII A of the California Constitution and implemented by
Revenue &amp; Taxation Code section 51. It does two things:</p>
<ul>
<li><strong>Caps the tax rate</strong> at 1% of taxable value, plus voter-approved bonded debt.
The 1% figure is the <em>general levy</em>; the actual composite rate on a bill is higher.</li>
<li><strong>Caps annual growth</strong> of the assessed value at the rate of inflation, and
never more than <strong>2% per year</strong>, regardless of what the market does.</li>
</ul>
<p>Critically, the assessed value <em>resets to market value</em> on a change in ownership or
completed new construction. Between those events it is frozen at the acquisition value plus at
most 2% per year. That gap &mdash; between a decades-old assessed value and today's market value
&mdash; is the entire value of Proposition 13 to a long-held owner.</p>

<div class="tw"><table><thead><tr><th>Rule</th><th>Value</th><th>Authority</th><th>Status</th></tr></thead><tbody>
<tr><td>General levy rate</td><td>1% of taxable value</td><td>{src('rtc51')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Annual assessment growth cap</td><td>2% maximum</td><td>{src('rtc51')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2026&ndash;27 inflation factor (statewide)</td><td>1.020</td><td>{src('boe26002')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Reassessment trigger</td><td>Change in ownership or new construction</td><td>{src('rtc51')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Homeowners' exemption</td><td>$7,000 off full value</td><td>{src('rtc218')}</td><td><span class="b ok">Verified</span></td></tr>
</tbody></table></div>
<p class="small">The 2026&ndash;27 factor happens to equal the 2% cap. It was set at 1.02 using an
August-to-August CPI change of 3.307% because the federal shutdown in autumn 2025 prevented
publication of the normal October index. Note the 2021&ndash;22 factor was only 1.01036 &mdash; the 2%
figure is a ceiling, not a promise.</p>

<h3>Translating rate to actual dollars</h3>
<p>The 1% general levy is not the rate on the bill. Each parcel sits in a
<strong>tax rate area</strong> with its own overlay of voter-approved bond debt. Santa Clara
County's own published worked example uses a typical rate area of
<strong>1.1488%</strong> &mdash; 1% general levy plus county, school, and water bond rates.</p>
<div class="tw"><table><thead><tr><th>Component</th><th class="n">Rate per $100 of assessed value</th><th>Source</th></tr></thead><tbody>
<tr><td>General levy (Prop 13)</td><td class="n">1.00000</td><td>{src('rtc51')}</td></tr>
<tr><td>County bonds</td><td class="n">0.03880</td><td>{src('sccar')}</td></tr>
<tr><td>School bonds</td><td class="n">0.10000</td><td>{src('sccar')}</td></tr>
<tr><td>Water bonds</td><td class="n">0.01000</td><td>{src('sccar')}</td></tr>
<tr><td><strong>Typical total</strong></td><td class="n"><strong>1.14880</strong></td><td>{src('sccar')}</td></tr>
</tbody></table></div>

<h2 id="prop19">2. The pivotal rule: Proposition 19</h2>
<p>Proposition 19 (2020) replaced the old Propositions 58/193 parent-child exclusion on
16 February 2021. It <strong>narrowed</strong> the exclusion dramatically: a low Prop 13 basis now
survives a parent-to-child transfer <em>only</em> for a family home that becomes the child's own
principal residence.</p>

<div class="note bad"><p><strong>This is the single most important fact in the analysis.</strong>
Before 2021, a child could inherit a rental property and keep the parent's assessed value forever.
Since 16 February 2021 that is gone. The Santa Clara County Assessor states it directly: an
intergenerational transfer of a <em>rental</em> home does <strong>not</strong> qualify for the
exclusion. <span class="src">{src('scc19')}</span></p></div>

<h3>The four conditions, all of which must be met</h3>
<ol class="steps">
<li><strong>The property was the transferor's principal residence.</strong> It must have been
eligible for the homeowners' or disabled veterans' exemption in the parent's name.
<span class="src">{src('boe26026')}</span></li>
<li><strong>It becomes the transferee's principal residence within one year.</strong> There are
"no exceptions to this rule." <span class="src">{src('boe26026')}</span></li>
<li><strong>The heir files for the homeowners' or disabled veterans' exemption within one
year</strong> of the transfer. Missing this forfeits the exclusion entirely.
<span class="src">BOE-19-P / <a href="https://www.boe.ca.gov/prop19/">BOE Prop 19</a></span></li>
<li><strong>Market value at transfer does not exceed</strong> the transferor's factored base year
value <strong>plus $1,044,586</strong> (the 2025&ndash;27 figure). Any excess is added to the new
taxable value. <span class="src">{src('boe25009')}</span></li>
</ol>

<h3>The $1 million cap is not $1 million</h3>
<p>The statute indexes the amount every two years against the FHFA House Price Index for
California. This is frequently missed:</p>
<div class="tw"><table><thead><tr><th>Period in which the transfer occurs</th><th class="n">Applicable cap</th><th>Authority</th><th>Status</th></tr></thead><tbody>
<tr><td>Feb 16, 2021 &ndash; Feb 15, 2023</td><td class="n">$1,000,000</td><td>{src('boe25009')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Feb 16, 2023 &ndash; Feb 15, 2025</td><td class="n">$1,022,600</td><td>{src('boe25009')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td><strong>Feb 16, 2025 &ndash; Feb 15, 2027</strong> (current)</td><td class="n"><strong>$1,044,586</strong></td><td>{src('boe25009')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Feb 16, 2027 &ndash; Feb 15, 2029</td><td class="n" style="color:#6e7f94">&mdash;</td><td>Not yet published</td><td><span class="b warn">Unverified</span></td></tr>
<tr><td>2045 (modeled transfer year)</td><td class="n">≈ {m(BI[1]['cap'])}</td><td>Model projection at 4.0%/yr HPI</td><td><span class="b pur">Projected</span></td></tr>
</tbody></table></div>
<p class="small">The 2045 figure is a <em>projection</em>, not a published number. It compounds the
current $1,044,586 by the assumed annual HPI change on each biennial adjustment date. The Board of
Equalization will publish the actual figure each February.</p>

<h2 id="a">3. Property A &mdash; Cupertino, in detail</h2>
<p>This property carries the entire decision. Its current assessed value is roughly
<strong>18% of market value</strong>, which is exactly the situation Proposition 13 was designed to
create &mdash; and exactly the situation Proposition 19 takes away if the house is not occupied by
an heir.</p>

<h3>Current position</h3>
<div class="tw"><table><thead><tr><th>Item</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Estimated market value, Nov 2026</td><td class="n">{m(3100000)}</td><td>Owner estimate; no appraisal on file</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Assessed value, 2026&ndash;27 roll</td><td class="n">{m(550537)}</td><td>Owner tax records</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Assessed as % of market value</td><td class="n">17.8%</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr><td>Tax paid, 2025</td><td class="n">{m(7207)}</td><td>Owner tax records</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Typical SCC ad valorem rate</td><td class="n">1.1488%</td><td>{src('sccar')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Implied non-ad-valorem charges</td><td class="n">≈ {m(1006)}/yr</td><td>Derived: $7,207 &minus; ($539,743 &times; 1.1488%)</td><td><span class="b pur">Derived</span></td></tr>
</tbody></table></div>
<div class="note"><p>The owner's records imply an effective rate of about <strong>1.335%</strong>,
which is above the county's 1.1488% typical rate. Rather than discard either figure, the model
applies the verified 1.1488% ad valorem rate to assessed value and adds the residual as a fixed
charge that grows with inflation. Rebuilt this way the model reproduces the actual 2025 bill to
within about 1.7%, which is a reasonable check. See
<a href="flagged.html">Flagged for Review</a> for the open question.</p></div>

<h3>The two futures for Property A</h3>
<p>Both columns start from the same facts. They diverge entirely on whether an heir occupies the
house.</p>
<div class="tw"><table><thead><tr>
<th>At transfer in 2045</th><th class="n">Live in it (exclusion claimed)</th><th class="n">Rent it out (no exclusion)</th></tr></thead><tbody>
<tr><td>Market value at transfer</td><td class="n">{m(6531230)}</td><td class="n">{m(6531230)}</td></tr>
<tr><td>Parent's factored base year value</td><td class="n">{m(803000)}</td><td class="n">{m(803000)}</td></tr>
<tr><td>Prop 19 value cap (base + indexed $1M)</td><td class="n">{m(803000+1546240)}</td><td class="n">&mdash;</td></tr>
<tr><td><strong>New taxable value</strong></td><td class="n">{m(4984990)}</td><td class="n">{m(6531230)}</td></tr>
<tr><td>Excess above the cap, taxed at full market</td><td class="n">{m(6531230-803000-1546240)}</td><td class="n">&mdash;</td></tr>
<tr><td>Homeowners' exemption applied</td><td class="n">$7,000</td><td class="n">&mdash;</td></tr>
<tr><td><strong>Annual tax, first year</strong></td><td class="n ok-t"><strong>{m(58950)}</strong></td><td class="n bad-t"><strong>{m(76800)}</strong></td></tr>
<tr><td>Annual tax, 2070</td><td class="n">{m(97570)}</td><td class="n">{m(126790)}</td></tr>
</tbody></table></div>

<p>Note what the $1,044,586 cap does <em>not</em> do here. Because the house is worth
{m(6531230)} against a base of only {m(803000)}, the excess of {m(6531230-803000-1546240)} is
<strong>added back</strong> to the taxable value. The exclusion protects only the first
{m(803000+1546240)} of value. It is a partial shield, not a full one &mdash; and it is a much
smaller benefit than most families expect when the gap between base and market is this large.</p>

<h3>What the exclusion is actually worth</h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Tax if occupied</th><th class="n">Tax if rented</th><th class="n">Annual saving</th></tr></thead><tbody>
""" 
    for y in (2045,2050,2060,2070):
        i=y-2026
        body+=f"""<tr><td class="n">{y}</td><td class="n">{m(P[i]['a_tax'])}</td><td class="n">{m(P[i]['a_tax_rent'])}</td><td class="n ok-t">{m(P[i]['a_tax_rent']-P[i]['a_tax'])}</td></tr>
"""
    body+=f"""<tr><td class="n"><strong>2045&ndash;2070 total</strong></td><td class="n">&mdash;</td><td class="n">&mdash;</td><td class="n ok-t"><strong>{m(600210)}</strong></td></tr>
</tbody></table></div>
<p class="small">Rounded to the nearest $10; totals are the sum of unrounded annual values. Source:
computed from verified rate and statute. <span class="b pur">Projected</span></p>

<div class="note warn"><p><strong>The exclusion is conditional and reversible.</strong> The Board of
Equalization is explicit: the family home must be <em>continually</em> used as the heir's principal
residence. "Once the property is no longer your principal residence, it will receive a new taxable
value as of the lien date following the date you no longer occupy the property." If the heir moves
out &mdash; even years later &mdash; the low basis is revoked retroactively to the date of the move,
and the resulting tax is computed on the value at the original transfer date, indexed forward.
<span class="src">{src('boe26026')}</span> That makes "move in for a while, then rent it" a
trap: it earns the exclusion for the occupancy period, then loses it with a large catch-up.</p></div>

<h2 id="b">4. Property B &mdash; San Francisco, in detail</h2>
<p>Property B is a different animal: three livable units, two currently rented. This has three
consequences that matter.</p>

<h3>Consequence one: it will be fully reassessed on inheritance</h3>
<p>Because it is a rental (and because Proposition 19 covers only <em>one</em> principal residence
per heir, which will be spent on Property A if the family goes that route), Property B gets no
exclusion. Its assessed value resets to market. The tax change is dramatic:</p>
<div class="tw"><table><thead><tr><th>Item</th><th class="n">Value</th><th>Source</th><th>Status</th></tr></thead><tbody>
<tr><td>Estimated market value, Nov 2026</td><td class="n">{m(1800000)}</td><td>Owner estimate</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Assessed value, 2025 roll</td><td class="n">{m(114248)}</td><td>Owner tax records</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>Tax paid, 2025</td><td class="n">{m(2439)}</td><td>Owner tax records</td><td><span class="b warn">Owner</span></td></tr>
<tr><td>SF secured property tax rate, FY2026&ndash;27</td><td class="n">1.18162182%</td><td>{src('sft')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Tax if assessed at 1.18162% today</td><td class="n">≈ {m(1380)}</td><td>Derived</td><td><span class="b pur">Derived</span></td></tr>
<tr><td>Implied fixed charges on the bill</td><td class="n">≈ {m(1089)}/yr</td><td>Derived: $2,439 &minus; ($114,248 &times; 1.18162%)</td><td><span class="b pur">Derived</span></td></tr>
<tr><td><strong>Tax after reassessment at 2045 value of {mm(3792330)}</strong></td><td class="n bad-t"><strong>{m(P[2045-2026]['b_tax'])}</strong></td><td>Projected</td><td><span class="b pur">Projected</span></td></tr>
</tbody></table></div>
<div class="note warn"><p>The owner's 2025 bill of {m(2439)} on an assessed value of {m(114248)}
implies an effective rate of <strong>2.135%</strong> &mdash; roughly 1.8&times; the San Francisco
secured rate. That gap is too large to be explained by fixed charges alone at this low assessed
value, so the residuals are held flat as a dollar amount rather than scaled as a rate. This is a
conservative treatment: it slightly <em>understates</em> the post-reassessment bill. Flagged on
<a href="flagged.html">Flagged for Review</a>.</p></div>

<h3>Consequence two: the rent covers the tax, easily</h3>
<div class="tw"><table><thead><tr><th class="n">Year</th><th class="n">Market value</th><th class="n">Assessed value</th><th class="n">Annual tax</th><th class="n">Annual rent (2 units)</th><th class="n">Rent coverage</th></tr></thead><tbody>
"""
    for y in (2026,2030,2040,2045,2050,2060,2070):
        i=y-2026
        cov = P[i]['b_rent']/P[i]['b_tax']
        body+=f"""<tr><td class="n">{y}</td><td class="n">{m(P[i]['b_market'])}</td><td class="n">{m(P[i]['b_assess'])}</td><td class="n">{m(P[i]['b_tax'])}</td><td class="n">{m(P[i]['b_rent'])}</td><td class="n ok-t">{cov:.1f}&times;</td></tr>
"""
    body+=f"""</tbody></table></div>
<p class="small">Rent grown at 1.6%/yr (the SF Rent Board's current allowable increase) from the
owner's {m(7150)}/month for two units. <span class="b pur">Projected</span></p>

<h3>Consequence three: rent control pins the growth</h3>
<p>San Francisco's Rent Ordinance caps annual increases for covered units at 60% of the Bay Area
CPI increase. The current allowable increase is <strong>1.6%</strong>, effective 1 March 2026
through 28 February 2027. <span class="src">{src('sfrb')}</span> Units not covered by the local
ordinance still fall under the statewide AB 1482 cap of 5% + CPI, hard-capped at 10%.
<span class="src">{src('civ1947')}</span></p>
<p>The practical effect: Property B's rent will very likely grow <em>slower than inflation</em>.
Modeled at 1.6% against 3.0% general inflation, its real rent declines about 1.4% per year. That is
a strong argument for keeping it for its locked-in basis and low tax, and a strong argument against
treating it as a growth asset.</p>

<div class="note"><p><strong>Also note:</strong> under Proposition 19 an heir may claim the
intergenerational exclusion on <em>only one</em> principal residence. If the family occupies
Property A to preserve its basis, Property B is automatically reassessed. The two exclusions
compete. <span class="src">{src('boe26026')}</span></p></div>

<h2>5. Putting it together</h2>
<div class="tw"><table><thead><tr><th>Year</th><th class="n">Property A market</th><th class="n">Property A assessed (occupied)</th><th class="n">Property A tax</th><th class="n">Property A tax (rented)</th><th class="n">Property B tax</th><th class="n">Combined tax (occupied)</th></tr></thead><tbody>
"""
    for r in P:
        if r["year"]%5==0 or r["year"]==2045:
            body+=f"""<tr><td class="n"><strong>{r['year']}</strong></td><td class="n">{m(r['a_market'])}</td><td class="n">{m(r['a_assess'])}</td><td class="n">{m(r['a_tax'])}</td><td class="n">{m(r['a_tax_rent'])}</td><td class="n">{m(r['b_tax'])}</td><td class="n">{m(r['a_tax']+r['b_tax'])}</td></tr>
"""
    body+="""</tbody></table></div>
<p class="small">Full 45-year series on the <a href="projections.html">Projections</a> page.</p>
"""
    return body+FOOT
