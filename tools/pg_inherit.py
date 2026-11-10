import json
d=json.load(open("data/model_output.json")); P=d["proj"]
def m(x):
    return ("&minus;$%s" % f"{abs(x):,.0f}") if x < 0 else f"${x:,.0f}"
def mm(x): return f"${x/1e6:,.2f}M"

def inheritance(head,FOOT,src):
    b=head("Inheritance &amp; Estate Tax","inheritance.html","Federal estate tax and California inheritance tax thresholds for the inherited Bay Area properties and cash.")+f"""
<h1>Inheritance &amp; Estate Tax</h1>
<p class="lead">The short answer is that <strong>there is no inheritance tax on this estate</strong>,
at either the federal or the state level, on any realistic set of values through 2050. That is a
matter of statute, not estimation. The long answer is that the federal exclusion is scheduled to be
indexed for inflation and can be changed by Congress, so the margin should be measured rather than
assumed.</p>

<div class="grid g3" style="margin:22px 0">
<div class="kpi ok"><div class="lab">California inheritance tax</div><div class="val">$0</div>
<div class="sub">Constitutionally prohibited. R&amp;TC §13301.</div></div>
<div class="kpi ok"><div class="lab">Federal exclusion, 2026</div><div class="val">$15,000,000</div>
<div class="sub">Per person. Double for a married couple with portability.</div></div>
<div class="kpi acc"><div class="lab">Combined estate value, 2045</div><div class="val">$10.3M</div>
<div class="sub">Both properties at 4.0%/yr appreciation. Excludes cash.</div></div>
</div>

<h2>1. California: no inheritance tax, by statute</h2>
<p>This is not a policy gap or an oversight. California affirmatively and permanently prohibits the
tax, in the starkest language available:</p>
<blockquote style="border-left:3px solid var(--purple);padding:2px 0 2px 16px;margin:16px 0;color:#cdd9e5;font-style:italic">
"Neither the state nor any political subdivision of the state shall impose any gift, inheritance,
succession, legacy, income, or estate tax, or any other tax, on gifts or on the estate or
inheritance of any person or on or by reason of any transfer occurring by reason of a death."
<br><span class="src" style="font-style:normal">&mdash; Cal. Rev. &amp; Tax. Code §13301 {src('rtc13301')}</span>
</blockquote>
<div class="tw"><table><thead><tr><th>Question</th><th>Answer</th><th>Authority</th><th>Status</th></tr></thead><tbody>
<tr><td>Does California impose an inheritance tax?</td><td>No &mdash; expressly prohibited</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Does California impose an estate tax?</td><td>No &mdash; expressly prohibited</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Does California impose a gift tax?</td><td>No &mdash; expressly prohibited</td><td>{src('rtc13301')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Is inherited <em>property</em> taxable as income?</td><td>No. (Income it later produces <em>is</em> taxable.)</td><td>FTB Form 541 instructions</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>What about a tax on the <em>transfer</em> of real property?</td><td>Yes &mdash; county documentary transfer tax and, in SF, a city transfer tax apply to sales. Not to a death transfer into a trust.</td><td>SF Treasurer</td><td><span class="b ok">Verified</span></td></tr>
</tbody></table></div>
<p>California has no inheritance tax because voters eliminated it in 1982 (Proposition 6), and the
prohibition is part of the Revenue and Taxation Code. Any future California inheritance or wealth
tax would require a constitutional amendment and a statewide vote. See
<a href="law-changes.html">Law Watch</a> for the proposals that have been attempted.</p>

<h2>2. Federal: an exclusion far above this estate</h2>
<p>The federal estate tax applies to the value of everything a person owns at death, above an
exclusion amount. The exclusion is what matters. For 2026 it is:</p>
<div class="tw"><table><thead><tr><th>Year of death</th><th class="n">Federal filing threshold / basic exclusion</th><th>Authority</th><th>Status</th></tr></thead><tbody>
<tr><td>2021</td><td class="n">$11,700,000</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2022</td><td class="n">$12,060,000</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2023</td><td class="n">$12,920,000</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2024</td><td class="n">$13,610,000</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2025</td><td class="n">$13,990,000</td><td>{src('irs_est')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td><strong>2026</strong></td><td class="n"><strong>$15,000,000</strong></td><td>{src('irs_est','irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>2027 and later</td><td class="n" style="color:#6e7f94">&mdash;</td><td>Not yet published</td><td><span class="b warn">Unverified</span></td></tr>
</tbody></table></div>
<div class="note ok"><p><strong>The 2026 jump from $13,990,000 to $15,000,000 was legislated, and it
is permanent.</strong> Public Law 119-21 (the One Big Beautiful Bill Act, enacted 4 July 2025) set
the basic exclusion at $15,000,000 for decedents dying after 31 December 2025 and removed the
scheduled 2026 sunset that would otherwise have cut it roughly in half. The IRS confirmed the figure
in Revenue Procedure 2025-32. The amount is indexed for inflation after 2026.
<span class="src">{src('irs_103')}</span></p></div>

<h3>Key federal figures for 2026</h3>
<div class="tw"><table><thead><tr><th>Item</th><th class="n">2026 amount</th><th>Authority</th><th>Status</th></tr></thead><tbody>
<tr><td>Basic exclusion amount (estate &amp; gift, unified)</td><td class="n">$15,000,000</td><td>{src('irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Generation-skipping transfer tax exemption</td><td class="n">$15,000,000</td><td>{src('irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Top estate / gift / GST tax rate</td><td class="n">40%</td><td>IRC §2001(c)</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Annual gift tax exclusion (per recipient)</td><td class="n">$19,000</td><td>{src('irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Annual exclusion, non-citizen spouse</td><td class="n">$194,000</td><td>{src('irs_103')}</td><td><span class="b ok">Verified</span></td></tr>
<tr><td>Married couple combined, with portability</td><td class="n">$30,000,000</td><td>Derived &mdash; requires Form 706 election</td><td><span class="b pur">Derived</span></td></tr>
</tbody></table></div>
<div class="note warn"><p><strong>Portability is not automatic.</strong> A surviving spouse can only
use a deceased spouse's unused exclusion if the estate files a timely Form 706 electing portability
&mdash; even where no tax is owed and no return would otherwise be required. Families routinely miss
this, and it is worth up to $15,000,000 of additional exclusion. Flag the Form 706 deadline when the
first spouse dies.</p></div>

<h2>3. Applying the thresholds to this estate</h2>
<p>The estate consists of both properties plus an unspecified amount of cash and marketable
securities. Property values are modeled at 4.0% annual appreciation from owner estimates.</p>
<div class="tw"><table><thead><tr><th class="n">Transfer year</th><th class="n">Property A</th><th class="n">Property B</th><th class="n">Real estate total</th><th class="n">Headroom under $15M single</th><th class="n">Headroom under $30M couple</th></tr></thead><tbody>
"""
    for y in (2030,2040,2045,2050,2060,2070):
        i=y-2026
        va=P[i]['a_market']; vb=P[i]['b_market']; t=va+vb
        b+=f"""<tr><td class="n"><strong>{y}</strong></td><td class="n">{m(va)}</td><td class="n">{m(vb)}</td><td class="n">{m(t)}</td><td class="n {"ok-t" if t<15000000 else "bad-t"}">{m(15000000-t) if t<15000000 else "OVER BY "+m(t-15000000)}</td><td class="n {"ok-t" if t<30000000 else "bad-t"}">{m(30000000-t) if t<30000000 else "OVER BY "+m(t-30000000)}</td></tr>
"""
    b+=f"""</tbody></table></div>
<p class="small">Real estate only &mdash; cash and securities are additional. Headroom shrinks as
appreciation compounds. <span class="b pur">Projected</span></p>

<div class="note"><p><strong>Where it could become a problem.</strong> At 4.0%/yr the real-estate
component alone crosses the single-person $15,000,000 exclusion between 2060 and 2065 &mdash; about
$18.6 million by 2060 against the $15 million threshold. A 2045&ndash;2050 transfer is comfortably
inside it. But the estate
also includes "a considerable amount of money." If the cash and securities total more than roughly
$5,600,000 at the time of death in 2045, a single decedent's estate would exceed $15,000,000 and
would owe federal estate tax at 40% on the excess. That threshold is the number to watch. For a
married couple with a properly elected portability, the equivalent figure is about $20,600,000.
<span class="b pur">Derived</span></p></div>

<h2>4. The step-up in basis &mdash; the larger tax benefit</h2>
<p>For most families in this position the estate tax is irrelevant and the <strong>basis
step-up</strong> is the real money. When a beneficiary inherits property, its income-tax basis
becomes the fair market value on the date of death.</p>
<blockquote style="border-left:3px solid var(--acc);padding:2px 0 2px 16px;margin:16px 0;color:#cdd9e5">
"Generally, the basis of property inherited from a decedent is&hellip; <strong>the FMV of the property
at the date of the individual's death</strong>."
<span class="src">{src('irs551')}</span></blockquote>
<p>All of the appreciation that occurred during the parent's lifetime is <em>never taxed</em>. If
Property A is worth {m(3100000)} today against a basis that may be only a few hundred thousand
dollars, the entire gain escapes income tax at death.</p>
<div class="tw"><table><thead><tr><th>Scenario</th><th class="n">Sale price</th><th class="n">Basis</th><th class="n">Taxable gain</th><th class="n">Federal + NIIT (23.8%)</th><th class="n">California (9.3%)</th><th class="n">Total tax</th></tr></thead><tbody>
<tr><td><strong>Inherited, sold promptly</strong></td><td class="n">{m(6531230)}</td><td class="n">{m(6531230)}</td><td class="n ok-t">$0</td><td class="n">$0</td><td class="n">$0</td><td class="n ok-t"><strong>$0</strong></td></tr>
<tr><td>Gifted during life, sold</td><td class="n">{m(6531230)}</td><td class="n">≈ {m(550537)} <span class="small">(carryover)</span></td><td class="n bad-t">{m(6531230-550537)}</td><td class="n">{m((6531230-550537)*0.238)}</td><td class="n">{m((6531230-550537)*0.093)}</td><td class="n bad-t"><strong>{m((6531230-550537)*0.331)}</strong></td></tr>
</tbody></table></div>
<p class="small">The gift scenario uses the current assessed value only as a rough proxy for a
possible low original basis; the true cost basis is not in the record and would need to be
established from the parents' purchase documents. Carries a <span class="b warn">Flagged</span> note.
This comparison is the reason not to transfer the real estate during life without specific advice.
<span class="b pur">Derived</span></p>

<div class="note bad"><p><strong>Do not deed the houses to the children before death.</strong> A
lifetime gift carries over the parent's low basis instead of stepping it up, and because the
properties are in a trust the transfer can be arranged at death with no probate. Gifting them early
would very likely convert a $0 tax into a six-figure one. The one exception is if the estate is
large enough to face a 40% estate tax &mdash; which, on these numbers, it is not.</p></div>

<h2>5. What is actually taxable at inheritance</h2>
<div class="tw"><table><thead><tr><th>Item</th><th>Tax treatment</th><th>Rate</th><th>Authority</th></tr></thead><tbody>
<tr><td>Inherited real property</td><td>Not income. Basis resets to date-of-death value.</td><td>0%</td><td>{src('irs551')}</td></tr>
<tr><td>Inherited cash</td><td>Not income. No basis issue.</td><td>0%</td><td>IRC §102</td></tr>
<tr><td>Inherited securities</td><td>Not income. Basis resets to date-of-death value.</td><td>0%</td><td>{src('irs551')}</td></tr>
<tr><td>Life insurance proceeds</td><td>Generally not income to the beneficiary.</td><td>0%</td><td>IRC §101</td></tr>
<tr><td>Traditional IRA / 401(k)</td><td><strong>Yes</strong> &mdash; ordinary income to a non-spouse beneficiary when distributed. Subject to the 10-year rule.</td><td>Up to 37% federal + 12.3% CA</td><td>{src('irs_est')}</td></tr>
<tr><td>Roth IRA</td><td>Generally tax-free, but the 10-year distribution rule still applies.</td><td>0%</td><td>IRS</td></tr>
<tr><td>Income the estate earns after death</td><td><strong>Yes</strong> &mdash; taxed to the estate or trust.</td><td>Estates hit 37% at $16,100 in 2026</td><td>{src('irs_est')}</td></tr>
</tbody></table></div>
<div class="note warn"><p><strong>Watch the retirement accounts.</strong> These are frequently the
largest single tax exposure in an inheritance and they are routinely overlooked because they are not
"real estate." A distribution from an inherited traditional IRA is ordinary income, and because the
estate or trust brackets compress, it can be taxed at the top rate on a relatively modest amount.
Model the distribution schedule before the estate is funded.</p></div>

<h2>6. Conclusion on inheritance tax</h2>
<div class="verdict">
<div class="tag">Conclusion</div>
<h2>No inheritance tax applies. Plan around income tax instead.</h2>
<p>California imposes none by statute. The federal exclusion of $15,000,000 per person
($30,000,000 for a properly-elected couple) comfortably exceeds this estate's real-estate component
through 2050. The tax work that actually matters here is <strong>preserving the basis step-up</strong>
by letting the property pass at death rather than by gift, and <strong>managing the timing of
retirement account distributions</strong>.</p>
<p style="margin-bottom:0">The one number to track: total estate value over $15,000,000 for a single
decedent, or $30,000,000 for a surviving couple.</p>
</div>
"""
    return b+FOOT
