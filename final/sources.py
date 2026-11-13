"""Source register (session 07a57a05; updated 2026-11-12 by session a6ec5b1d).

Initial pass opened entries on 2026-11-11 UTC; on 2026-11-12 UTC every remaining
official `excerpt` entry was fetched directly and upgraded to `how = 'page'`, plus
four newly fetched official pages (`BOE-PUB-800-1`, `CUP-WATER`, `IRS-SCHED-A`, `SFPUC-RFB`).

how = 'page'    : the official page / PDF itself was fetched and the quoted value was read on it.
how = 'excerpt' : text of the official page was read through a search-engine excerpt only.
how = 'academic': not a government source; used only where no official series exists.  Flagged.
"""

S = {}


def add(i, label, title, url, how, read):
    S[i] = dict(id=i, label=label, title=title, url=url, how=how, read=read)


# ---- Federal -----------------------------------------------------------------
add('IRS-ESTATE', 'IRS estate tax', 'IRS - Estate tax (filing thresholds by year of death)',
    'https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax', 'page',
    'Filing threshold table: 2011 $5,000,000; 2017 $5,490,000; 2018 $11,180,000; 2025 $13,990,000; 2026 $15,000,000. Portability election needs a timely filed Form 706.')
add('IRS-NEW', "IRS what's new", "IRS - What's new: estate and gift tax",
    'https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax', 'page',
    'Public Law 119-21 (signed 2025-07-04) sets the basic exclusion at $15,000,000 for 2026. Closing-letter fee change effective 2026-10-26 (TD 10055).')
add('RP-2026-35', 'Rev. Proc. 2026-35', 'IRS Revenue Procedure 2026-35 (inflation-adjusted items for 2027)',
    'https://www.irs.gov/pub/irs-drop/rp-26-35.pdf', 'page',
    'Section 3.44: 2027 basic exclusion $15,480,000. Section 3.46: 2027 annual gift exclusion $20,000. Section 3.01: 2027 rate tables (24% bracket for unmarried individuals: over $109,125 to $208,325). Section 3.03: 15% capital-gain rate up to $563,200 (other individuals), $633,600 (joint).')
add('IRS-FAQ-ESTATE', 'IRS estate FAQ', 'IRS - Frequently asked questions on estate taxes',
    'https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes', 'page',
    'Form 706 is due nine months after the date of death; Form 4768 gives an automatic six-month extension; portability needs a timely Form 706; Rev. Proc. 2022-32 late election up to the fifth anniversary when no return was otherwise required.')
add('IRS-FAQ-ETCL', 'IRS closing-letter FAQ', 'IRS - Frequently asked questions on the Estate Tax Closing Letter',
    'https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-the-estate-tax-closing-letter', 'page',
    'Opened in full 2026-11-12 (session 3e79fc01). Fee by request date: $67 before 2025-05-21; $56 from 2025-05-21 until 2026-10-26; $76 after 2026-10-26. Not used in any calculation.')
add('IRS-FAQ-INHERIT', 'IRS inherited-property FAQ', 'IRS FAQ - Is money received from the sale of inherited property taxable?',
    'https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances', 'page',
    'Basis of property inherited from a decedent is generally the fair market value on the date of death (or the alternate valuation date if elected on Form 706); a sale above basis is a taxable gain; Form 8971 consistent-basis rule.')
add('IRS-TC409', 'IRS Topic 409', 'IRS Topic no. 409 - Capital gains and losses',
    'https://www.irs.gov/taxtopics/tc409', 'page',
    'Net capital gain taxed at 0%, 15% or 20%; unrecaptured section 1250 gain taxed at a maximum 25%; property acquired from a decedent is an exception to the holding-period rule (Publication 544).')
add('IRS-TC701', 'IRS Topic 701', 'IRS Topic no. 701 - Sale of your home',
    'https://www.irs.gov/taxtopics/tc701', 'page',
    'Exclusion of up to $250,000 ($500,000 joint) of gain on a main home; must own and use it for 24 months of the 5 years before the sale.')
add('IRS-TC559', 'IRS Topic 559', 'IRS Topic no. 559 - Net investment income tax',
    'https://www.irs.gov/taxtopics/tc559', 'page',
    '3.8% tax on net investment income (includes rents, dividends, interest and gains on real estate) above $200,000 single / $250,000 joint modified AGI.')
add('RR-2023-2', 'Rev. Rul. 2023-2', 'Internal Revenue Bulletin 2023-16 - Revenue Ruling 2023-2',
    'https://www.irs.gov/irb/2023-16_IRB', 'page',
    'The section 1014 basis adjustment generally does not apply to assets of an irrevocable grantor trust that are not included in the deceased grantor\'s gross estate.')
add('IRS-I706', 'Form 706 instructions', 'IRS - Instructions for Form 706 (07/2026), Table A (Unified Rate Schedule)',
    'https://www.irs.gov/instructions/i706', 'page',
    'Read directly 2026-11-12: Table A taxable amount over $1,000,000 -> $345,800 plus 40% of excess; Basic Exclusion table ($15,000,000 in 2026); annual gift exclusion $19,000 (2025-2026).')
add('IRS-P559', 'IRS Pub. 559', 'IRS Publication 559 (2025) - Survivors, Executors, and Administrators',
    'https://www.irs.gov/publications/p559', 'page',
    'Read directly 2026-11-12: Property received as gift, bequest or inheritance is not included in recipient income; later interest, dividends or rents are taxable; inherited traditional IRA distributions may be taxable IRD; 5-yr late portability under Rev. Proc. 2022-32.')
add('IRS-P527', 'IRS Pub. 527', 'IRS Publication 527 (2025) - Residential Rental Property',
    'https://www.irs.gov/publications/p527', 'page',
    'Read directly 2026-11-12: Table 2-1 residential rental property 27.5 years GDS / 30 years ADS straight-line mid-month convention; personal-to-rental conversion basis is lesser of adjusted basis or FMV.')
add('IRS-1041', 'IRS estate income tax', 'IRS - File an estate tax income tax return (Form 1041)',
    'https://www.irs.gov/individuals/file-an-estate-tax-income-tax-return', 'page',
    'Read directly 2026-11-12: Form 1041 required if estate/trust has annual gross income over $600; EIN required first; Schedule K-1 passes income and deductions to beneficiaries.')
add('IRS-SCHED-A', 'IRS Schedule A', 'IRS - Instructions for Schedule A (Form 1040) (2025), State and Local Tax Deduction',
    'https://www.irs.gov/instructions/i1040sca', 'page',
    'Read directly 2026-11-12: Under P.L. 119-21, Schedule A SALT cap raised from $10,000 to $40,000 in 2025 ($40,400 in 2026), phased down above $500,000 MAGI (floor $10,000) and scheduled to revert after 2029; Schedule E rental property taxes are uncapped.')
add('CONG-S587', 'S.587', 'Congress.gov - S.587, Death Tax Repeal Act of 2025',
    'https://www.congress.gov/bill/119th-congress/senate-bill/587', 'page',
    'Read directly 2026-11-12: 119th Congress; introduced 2025-02-13, read twice and referred to Committee on Finance; status remains Introduced.')
add('CONG-HR1301', 'H.R.1301', 'Congress.gov - H.R.1301, Death Tax Repeal Act',
    'https://www.congress.gov/bill/119th-congress/house-bill/1301/all-info', 'page',
    'Read directly 2026-11-12: 119th Congress; introduced 2025-02-13, referred to House Ways and Means; status remains Introduced.')
# ---- California --------------------------------------------------------------
add('SCO-ESTATE', 'CA Controller', 'California State Controller - California Estate Tax',
    'https://www.sco.ca.gov/ardtax_estate_tax.html', 'page',
    'No California estate tax return is required for deaths on or after 2005-01-01. Inheritance tax applies only to deaths before 1982-06-08.')
add('BOE-P19', 'BOE Prop 19', 'California State Board of Equalization - Proposition 19',
    'https://www.boe.ca.gov/prop19/', 'page',
    'Parent-child exclusion applies only to a principal residence of the transferor that becomes the principal residence of the transferee; value limit = taxable value plus $1,000,000 (adjusted every two years); homeowners\' exemption within one year; claim within three years or before transfer to a third party; other real property no longer excluded; effective 2021-02-16.')
add('BOE-LTA-2025-009', 'BOE LTA 2025/009', 'BOE Letter to Assessors 2025/009 - adjustment of the $1 million amount',
    'https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf', 'page',
    '$1,044,586 for transfers 2025-02-16 through 2027-02-15; adjusted every other February 16 by the FHFA California House Price Index change for the prior calendar year (2.15% for 2024); next adjustment February 2027. Re-read 2026-11-13: the letter quotes California Constitution article XIII A section 2.1(c)(4) - "Beginning on February 16, 2023, and every other February 16 thereafter, the State Board of Equalization shall adjust the one million dollar ($1,000,000) amount described in paragraph (1) for inflation to reflect the percentage change in the House Price Index for California for the prior calendar year, as determined by the Federal Housing Finance Agency" - and points to Property Tax Rule 462.520 and Letter To Assessors 2022/012 for how the value cap is applied. Enclosed table: $1,000,000 for 2021-02-16 to 2023-02-15, $1,022,600 for 2023-02-16 to 2025-02-15, $1,044,586 for 2025-02-16 to 2027-02-15.')
add('BOE-SB974', 'BOE analysis of SB 974', 'BOE Legislative Bill Analysis, Senate Bill 974 (Seyarto), amended March 25 2026 - Revenue and Taxation Code section 63.2',
    'https://boe.ca.gov/legdiv/pdf/0974sb032526rd.pdf', 'page',
    'Read directly 2026-11-13. States the value test in words: the existing adjusted base year value remains if the reassessed value is less than that value plus $1 million; if it is more, "the difference between (1) the sum of the adjusted base year value plus $1 million, and (2) the reassessed value is to be added to the property\'s existing adjusted base year value" - the formula this site\'s model implements. Also: the transferee has one year from the transfer to reside in the home; SB 539 (ch. 427, 2021) codified the requirement to claim the homeowners\' or disabled veterans\' exemption before the exclusion applies; the $1 million is adjusted biennially by the FHFA California HPI (section 2.1(c)(4)); no projected revenue impact. SB 974 itself amends section 63.2(e)(9) so that a special needs trust is expressly an eligible medium of transfer.')
add('BOE-LTA-2026-026', 'BOE LTA 2026/026', 'BOE Letter to Assessors 2026/026 - Prop 19 intergenerational exclusion FAQ (2026-08-03)',
    'https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf', 'page',
    'Definitions: excluded amount = factored base year value + adjusted $1 million; new taxable value = factored base year value + excess; transfers through a trust are covered; the home must be continually used as the family home or the full new base year value is enrolled.')
add('BOE-LTA-2026-002', 'BOE LTA 2026/002', 'BOE Letter to Assessors 2026/002 - 2026-27 California Consumer Price Index (2026-01-13)',
    'https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf', 'page',
    'Read in full 2026-11-13 (session da3f2b99): "please prepare your 2026 assessment roll using an inflation factor of 1.02"; CCPI rose 343.108 (Aug 2024) to 354.456 (Aug 2025) = 3.307%, capped at 2% (October 2025 CCPI was not published due to the federal shutdown, so August-to-August was used). The enclosed table lists the final annual factors back to 1976-77.')
add('RTC-51', 'R&TC 51', 'California Revenue and Taxation Code section 51 (base year value, annual inflation factor)',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51', 'page',
    'Taxable value is the base year value compounded by the annual inflation factor (California CPI, subparagraph (B)-(C)); subparagraph (D): in no event shall the percentage increase for any assessment year exceed 2 percent of the prior year\'s value. Re-read in full on 2026-11-11 (session faccd46d) and again 2026-11-13 (session da3f2b99).')
add('RTC-63.2', 'R&TC 63.2', 'California Revenue and Taxation Code section 63.2',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2', 'page',
    'Read in full again 2026-11-13 (session arena/558a0100). (a)(1)(A) the transfer must be of the transferor\'s principal residence and become the transferee\'s principal residence within one year; (a)(1)(B) the transferee must file for the homeowners\' or disabled veterans\' exemption within a year and the exclusion is removed on the date they stop being eligible; (a)(1)(C) on losing the exclusion the date-of-death value, indexed under section 51, is re-enrolled from the next lien date. (d): new taxable value = the transferor\'s taxable value PLUS, only if fair market value exceeds that taxable value plus $1,000,000, the excess over that sum - so below the limit nothing is added and above it only the excess is added. (e)(5) family home = a dwelling eligible for the exemption through the transferor\'s ownership and occupation; (e)(9) "transfer" includes a transfer of present beneficial ownership through an inter vivos or testamentary trust. (f)(1)(A) claim within three years of the transfer, or before the property goes to a third party or the transferee stops occupying it, whichever is first; (f)(1)(B) six months after a supplemental or escape notice is also timely; (g) a 45-day then 60-day notice sequence, with a processing fee up to $175 where the claim is late (authorized by the county). Footer: amended by Stats. 2025, Ch. 539 (SB 293), effective January 1, 2026 - the Palisades/Eaton/Hurst/Lidia/Sunset/Woodley fire relief in (f)(2), which extends claim and exemption filing windows to three years from a notice date for claims filed before January 1, 2031.')
add('RTC-480', 'R&TC 480', 'California Revenue and Taxation Code section 480',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480', 'page',
    'Change in ownership statement: where the change is by reason of death, file within 150 days after the date of death (or with the inventory and appraisal if probated). Re-read 2026-11-13: (b) for a transfer "through the medium of a trust" the statement is filed by the trustee (if the property was held in trust) or the transferee with the county recorder OR assessor in each county where the decedent owned an interest; (c) the statement is declared true under penalty of perjury and must carry a notice of the relief available under section 69.5; late filing after a written assessor request carries a penalty of $100 or 10 percent of the taxes on the new base year value, whichever is greater (capped). The trailing period the register used to carry in the query string was removed on 2026-11-13: leginfo serves the section either way, so no published link was broken.')
add('PROB-16061.7', 'Prob. Code 16061.7', 'California Probate Code section 16061.7',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7', 'page',
    'Trustee notification within 60 days after a revocable trust becomes irrevocable by death; served on beneficiaries and heirs; 120-day contest warning.')
add('BOE-PUB-800-1', 'BOE Pub. 800-1', 'BOE Taxpayers\' Rights Advocate Publication 800-1 - Transfers Between Parents and Children',
    'https://www.boe.ca.gov/pdf/pub800-1.pdf', 'page',
    'Read directly 2026-11-12: BOE-19-P cannot be filed before BOE-266 homeowners\' exemption; 6-month filing window from supplemental notice; if transferee moves out later, reassessment to date-of-death FMV indexed occurs as of next Jan 1 lien date; covers stepchildren and in-law children.')
add('BOE-RULE-462.260', 'BOE Rule 462.260', 'BOE Property Tax Rule 462.260 - Date of change in ownership',
    'https://boe.ca.gov/proptaxes/pdf/rules/Rule462_260.pdf', 'page',
    'Revocable trust: date of change in ownership is the date the trust becomes irrevocable (example: the date of death). Inheritance: the date of death.')
add('BOE-HOX', 'BOE homeowners\' exemption', 'BOE - Homeowners\' Exemption',
    'https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm', 'page',
    '$7,000 reduction in taxable value for an owner-occupied principal residence on the January 1 lien date; one-time claim BOE-266; file by February 15 for the full exemption.')
add('FTB-RATES', 'FTB 2025 rates', 'Franchise Tax Board - 2025 California Tax Rate Schedules',
    'https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf', 'page',
    'Schedule X (single): 9.3% over $72,724; 10.3% over $371,479; 11.3% over $445,771; 12.3% over $742,953.')
add('FTB-MHS', 'FTB Form 540 booklet', 'Franchise Tax Board - 2025 Form 540 Booklet, Line 62 Behavioral Health Services Tax',
    'https://www.ftb.ca.gov/forms/2025/2025-540-booklet.html', 'page',
    'Read directly 2026-11-12: Renamed from Mental Health Services Tax to Behavioral Health Services Tax for tax years >= Jan 1, 2025; Line 62 imposes 1% tax on taxable income over $1,000,000 (whole dollars).')
add('SOS-RESULTS', 'CA Secretary of State', 'California Secretary of State - 2026 General Election, state ballot measures (unofficial)',
    'https://electionresults.sos.ca.gov/returns/ballot-measures', 'page',
    'Unofficial results as of 2026-11-11 6:51 p.m. (re-read 2026-11-12; earlier 2026-11-10 5:31 p.m. reading was Prop 3 Yes 60.6%, Prop 40 No 52.6%, Prop 42 Yes 51.5%); certification due by 2026-12-11. Prop 3 Yes 60.7%; Prop 40 No 52.5%; Prop 41 No 55.1%; Prop 42 Yes 51.4%; Prop 43 No 57.4%. Fourteen measures listed (1-5, 37-45); no Prop 19 repeal measure on ballot or active. Re-read 2026-11-13: page shows "28 Days Left" to certification and 23,860 of 23,860 precincts partially reporting as of 2026-11-12 8:46 p.m.; "Results will be certified by December 11, 2026". Statewide Yes/No: Prop 1 61.0/39.0, Prop 2 61.2/38.8, Prop 3 60.7/39.3, Prop 4 49.7/50.3, Prop 5 51.9/48.1, Prop 37 62.4/37.6, Prop 38 54.0/46.0, Prop 39 39.5/60.5, Prop 40 47.6/52.4, Prop 41 44.9/55.1, Prop 42 51.4/48.6, Prop 43 42.5/57.5, Prop 44 17.9/82.1, Prop 45 43.6/56.4. Every figure moved by less than one point since the 2026-11-11 reading and no outcome changed.')
add('DOJ-TPA', 'CA Attorney General', 'California Department of Justice - Tenant Protection Act consumer alert',
    'https://oag.ca.gov/system/files/media/Tenant-Protection-Act-Landlords-and-Property-Managers-English.pdf', 'page',
    'Read directly 2026-11-12: Rent cap 5% plus CPI or 10% total in 12 months; SB 567 (eff 2024-04-01) adds 1-mo relocation, 90-day/12-mo owner move-in rule, treble damages; exempts <15-yr units and non-corporate SFH with written notice.')
add('CDI-TOOL', 'CDI premium survey', 'California Department of Insurance - Compare insurance premiums (2026 homeowners survey tool)',
    'https://www.insurance.ca.gov/01-consumers/105-type/9-compare-prem/index.cfm', 'page',
    'Official annual premium survey with an interactive tool by ZIP code; results are not quotes; wildfire surcharges of 15% to over 300% are not reflected. The interactive results could not be read by this automated session.')
add('CDI-TOOL-APP', 'CDI homeowners tool', 'California Department of Insurance - 2026 Homeowners Insurance comparison tool',
    'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20', 'page',
    'Landing text read; ZIP-level premium tables require interactive input.')
add('CDI-EQ', 'CDI earthquake guide', 'California Department of Insurance - Earthquake insurance',
    'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/eq-ins.cfm', 'page',
    'Homeowners policies do not cover earthquake damage (fire following an earthquake is covered); the insurer must offer earthquake coverage every other year.')
add('CDI-RES', 'CDI residential guide', 'California Department of Insurance - Residential insurance guide (Form 401, Jan 2026)',
    'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/res-ins-guide.cfm', 'page',
    'Read directly 2026-11-12: Standard homeowners excludes flood, earthquake, earth movement, water seepage, mold, wear/tear and losses to house vacant 60+ days; contents typically 50% of dwelling with sub-limits.')
add('CPUC-NEM', 'CPUC net metering', 'California Public Utilities Commission - Net energy metering and net billing',
    'https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing', 'page',
    'Read directly 2026-11-12: Under D.14-03-041, NEM 2.0 customers keep tariff for 20 years from interconnection (TOU rates, hourly NBCs); Net Billing Tariff (D.22-12-056, eff Apr 15, 2023) gives 9-yr legacy for original customer only.')
add('CPUC-FIXED', 'CPUC fixed charge', 'CPUC Resolution E-5354 (Decision 24-05-028 fixed Base Services Charge)',
    'https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M555/K816/555816677.pdf', 'page',
    'Read directly 2026-11-12: CPUC Res. E-5354 / D.24-05-028 fixed Base Services Charge: reduced fixed tiers for CARE (Tier 1) and FERA/DRAH (Tier 2, SB 1130 expanded), and $24.15/mo for standard Tier 3 customers (PG&E Q1 2026 rollout).')
add('CDI-SB824', 'CDI wildfire-risk data', 'California Department of Insurance - SB 824 residential property data (coverage amounts, wildfire risk and losses)',
    'https://www.insurance.ca.gov/01-consumers/200-wrr/WildfireRiskInfoRpt.cfm', 'page',
    'Statewide totals for 2023, all residential policy forms: earned premium $14,217,212,455 on 12,580,970 earned exposures (about $1,130 a policy); average Coverage A $324,973. ZIP-level sheets exist in the workbook but could not be read by this automated session. Re-read 2026-11-13: the page states the report is produced every two years under Insurance Code section 929 by insurers with $10 million or more of California direct written premium, that it carries premium, ZIP code, protection class and fire-risk score per policy, and that the data may not be used in a rate filing if the Department finds it would make rates excessive, inadequate or unfairly discriminatory. The workbook is a spreadsheet the site builder cannot open, so no ZIP figure is quoted; the only figures used here are the two statewide averages above and the ratio between them, which is labelled as an assumption (flag A14).')
add('CDI-RPI', 'CDI residential report', 'California Department of Insurance - Residential Property Insurance Report (Part I summary workbook)',
    'https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/', 'page',
    'All years 2008-2023 pooled: average written premium $1,176 for homeowners policies and $601 for tenant-occupied dwelling-fire (landlord) policies.')
# ---- Local ---------------------------------------------------------------------
add('SCC-P19', 'Santa Clara Assessor', 'Santa Clara County Assessor - Parent-child transfer (Proposition 19)',
    'https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2', 'page',
    'Worked example: base value $200,000, market value $1,800,000 -> new value $800,000; claim form BOE-19-P; heirs must meet the exemption requirement within the first year; special rules for multi-unit dwellings.')
add('SCC-RATES', 'Santa Clara tax rate book', 'Santa Clara County Controller-Treasurer - Tax Rate Book FY2025-26',
    'https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE', 'page',
    'Rates per $100 (pages A-4 to A-6): 1% levy 1.00000; county retirement 0.03880; library retirement 0.00240; VMC 2008 0.00520; housing bond 0.00560; Cupertino Elementary 0.00010 + 0.01650 + 0.01690; Fremont Union High 0.01040 + 0.00880 + 0.01070 + 0.01180; Foothill-De Anza 0.01010 + 0.01350 + 0.00750; SCVWD State Water Project 0.00390; Midpeninsula Open Space 0.00140. Sum 1.16360. The exact tax rate area of the home was not looked up (privacy).')
add('SCC-DTT', 'Santa Clara Clerk-Recorder', 'Santa Clara County Clerk-Recorder - Recording real estate (documentary transfer tax)',
    'https://clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate', 'page',
    'Documentary transfer tax $0.55 per $500 of value; a higher rate applies only in San Jose, Palo Alto and Mountain View.')
add('SF-TAX', 'SF Treasurer', 'San Francisco Treasurer and Tax Collector - Secured property taxes',
    'https://sftreasurer.org/property/secured-property-taxes', 'page',
    'Fiscal year 2026-27 secured property tax rate 1.18162182%; supplemental bill follows a change in ownership.')
add('SF-EHT', 'SF Empty Homes Tax', 'San Francisco Treasurer and Tax Collector - Empty Homes Tax',
    'https://sftreasurer.org/business/taxes-fees/empty-homes-tax-eht', 'page',
    'Court of Appeal affirmed on 2026-09-11 that the tax is preempted; the City has stopped all collection work; owners are not required to file or pay unless the decision is reversed.')
add('SF-RENT-2026', 'SF Rent Board 2026-27', 'San Francisco Rent Board - Annual rent increase 3/1/26 to 2/28/27',
    'https://www.sf.gov/news--annual-rent-increase-3126-22827-announced', 'page',
    'Allowable annual increase for rent-controlled units is 1.6% (1.4% the year before).')
add('SF-RENT-RULES', 'SF rent increases', 'San Francisco Rent Board - Learn about rent increases',
    'https://www.sf.gov/learn-about-rent-increases-san-francisco/', 'page',
    'Allowed increase is 60% of the Bay Area CPI-U increase; no limit on the first rent for an empty rent-controlled unit; notice posted 2026-11-09 of proposed Board of Supervisors File No. 261020 (not enacted).')
add('SF-RENT-LAW', 'SF rental laws', 'San Francisco Rent Board - Learn about San Francisco rental laws',
    'https://www.sf.gov/learn-about-san-francisco-rental-laws/', 'page',
    'Units built before June 14, 1979 that are not single-family dwellings may have rent control and just-cause eviction protection; owner move-in is a just cause.')
add('CUP-WATER', 'City of Cupertino Water', 'City of Cupertino - Water Service Areas and SJWC Lease',
    'https://www.cupertino.gov/Residents/Utilities/Water', 'page',
    'Read directly 2026-11-12: Cupertino has three water providers (Cal Water NE, San Jose Water Co. SE, and Cupertino Municipal System W leased to SJWC through 2036 with lower rates than SJWC proper).')
add('SFPUC', 'SFPUC rates', 'San Francisco Public Utilities Commission - Water and sewer rate schedules FY2026-27 & FY2027-28',
    'https://www.sfpuc.gov/sites/default/files/accounts-and-services/Rates_Schedule_Water_Sewer_2026-7.pdf', 'page',
    'Read directly 2026-11-12 (Res. 26-0064/26-0066): Schedules W-1A/W-1B, Sewer Schedule A (90% SF / 95% MF flow factors) and Schedule D residential stormwater tiers effective 2026-07-01 & 2027-07-01.')
add('SFPUC-RFB', 'SFPUC Rate Board', 'SFPUC Rate Fairness Board - Proposed Water and Sewer Rate Adjustments (March 19, 2026)',
    'https://www.sfpuc.gov/sites/default/files/agendas-minutes-rate-fairness-board/6a-Rates-Presentation.pdf', 'page',
    'Read directly 2026-11-12: Water +7.0%/yr, residential wastewater +10.8% (FY26-27) / +10.1% (FY27-28), stormwater +53.3% / +43.1%; average SF residential combined bill +10.5% (FY26-27) / +12.5% (FY27-28).')
# ---- Data ----------------------------------------------------------------------
add('HUD-95014', 'HUD SAFMR 95014', 'HUD - FY2026 Small Area Fair Market Rents, ZIP 95014',
    'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026', 'page',
    'FY2026: efficiency $3,340; one-bedroom $3,800; two-bedroom $4,440; three-bedroom $5,870; four-bedroom $6,390 per month (40th-percentile gross rent).')
add('HUD-94122', 'HUD SAFMR 94122', 'HUD - FY2026 Small Area Fair Market Rents, ZIP 94122',
    'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=94122&metro_code=METRO41860MM7360&year=2026', 'page',
    'FY2026: efficiency $2,280; one-bedroom $2,730; two-bedroom $3,310; three-bedroom $4,230; four-bedroom $4,380 per month. Re-read 2026-11-13 (session arena/5a0857f0): unchanged.')
add('HUD-27-95014', 'HUD SAFMR FY2027 95014', 'HUD - FY2027 Small Area Fair Market Rents, ZIP 95014',
    'https://www.huduser.gov/datasets/fmr/fmr2027/zip-calc?year=2027&zip=95014&cbsasub=METRO41940M41940', 'page',
    'Read directly 2026-11-13 (session arena/5a0857f0): FY2027 efficiency $3,040; one-bedroom $3,440; two-bedroom $4,050; three-bedroom $5,440; four-bedroom $5,800 per month (40th-percentile gross rent). The FY2026 reference row printed on the same official page ($3,340 / $3,800 / $4,440 / $5,870 / $6,390) matches the FY2026 figures recorded under HUD-95014.')
add('HUD-27-94122', 'HUD SAFMR FY2027 94122', 'HUD - FY2027 Small Area Fair Market Rents, ZIP 94122',
    'https://www.huduser.gov/datasets/fmr/fmr2027/zip-calc?year=2027&zip=94122&cbsasub=METRO41860M41884', 'page',
    'Read directly 2026-11-13 (session arena/5a0857f0): FY2027 efficiency $2,370; one-bedroom $2,770; two-bedroom $3,410; three-bedroom $4,460; four-bedroom $5,020 per month. The FY2026 reference row printed on the same page ($2,485 / $2,977 / $3,604 / $4,604 / $4,772) differs from the FY2026 computation page recorded under HUD-94122; see finding R55.')
add('FHFA-SJ', 'FHFA index, San Jose', 'FHFA all-transactions house price index, San Jose-Sunnyvale-Santa Clara MSA (via FRED ATNHPIUS41940Q)',
    'https://fred.stlouisfed.org/series/ATNHPIUS41940Q', 'page',
    'Fourth-quarter values 1976-2025 (23.21 to 560.05); 2026 Q2 558.75 against 564.26 a year earlier.')
add('FHFA-SF', 'FHFA index, San Francisco', 'FHFA all-transactions house price index, San Francisco-San Mateo-Redwood City MSAD (via FRED ATNHPIUS41884Q)',
    'https://fred.stlouisfed.org/series/ATNHPIUS41884Q', 'page',
    'Fourth-quarter values 1975-2025 (19.28 to 512.99); 2026 Q2 506.53 against 507.95 a year earlier.')
add('FHFA-CA', 'FHFA index, California', 'FHFA all-transactions house price index, California (via FRED CASTHPI)',
    'https://fred.stlouisfed.org/series/CASTHPI', 'page',
    'Fourth-quarter values 1975-2025 (45.75 to 969.38); 2026 Q2 974.97 against 966.27 a year earlier.')
add('BLS-CPI', 'BLS CPI (FRED)', 'BLS Consumer Price Index for All Urban Consumers (via FRED CPIAUCSL / CPIAUCNS)',
    'https://fred.stlouisfed.org/series/CPIAUCSL', 'page',
    'December values 1974-2025 (51.9 to 326.031); December values 1927-1950 from CPIAUCNS.')
add('BLS-OCT', 'BLS CPI release', 'BLS - Consumer Price Index summary, October 2026 (released 2026-11-10)',
    'https://www.bls.gov/news.release/cpi.nr0.htm', 'page',
    'CPI-U +0.4% in October after +0.6% in September; index level 337.511; no 12-month change published for October because October 2025 data were not collected.')
add('TREASURY', 'Treasury yields', 'U.S. Treasury - Daily par yield curve rates, November 2026',
    'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202611', 'page',
    '2026-11-10: 3-month 4.30%, 1-year 4.56%, 10-year 4.98%, 30-year 5.35%.')
add('CBO', 'CBO outlook', 'Congressional Budget Office - The Budget and Economic Outlook: 2026 to 2036',
    'https://www.cbo.gov/publication/62105', 'page',
    'Read directly 2026-11-12 (Feb 2026 report): PCE inflation 2.7% in 2026 slowing to 2.0% by 2030; 10-year Treasury 4.1% in 2026 and 4.3% in 2027; real potential GDP 1.8%/yr 2031-2036; federal debt 101% to 120% of GDP.')
add('USGS', 'USGS earthquake outlook', 'U.S. Geological Survey Fact Sheet 2016-3020 - Earthquake outlook for the San Francisco Bay region 2014-2043',
    'https://pubs.usgs.gov/fs/2016/3020/fs20163020.pdf', 'page',
    'Read directly 2026-11-12: 2014-2043 SF Bay probabilities: 98% M>=6.0, 72% M>=6.7, 51% M>=7.0, 20% M>=7.5.')
add('FRED-JP', 'Japan series (FRED)', 'Japan: BIS residential property prices, Nikkei 225 and OECD consumer prices (via FRED QJPN368BIS, NIKKEI225, JPNCPIALLMINMEI)',
    'https://fred.stlouisfed.org/series/QJPN368BIS', 'page',
    'Year-end values 1989-2012 read on the FRED download: home prices fell in 21 of the 22 years 1991-2012; Nikkei 225 38,915.87 at end-1989, 8,455.35 at end-2011. Home-price changes for 2013-2020 taken from the file prepared by session 4395771d from the same series.')
add('DAMODARAN', 'NYU Stern returns table', 'NYU Stern (A. Damodaran) - Historical returns on stocks, bonds and bills 1928-2025',
    'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html', 'academic',
    'Annual S&P 500 total return, 3-month T-bill, 10-year T-bond and national real-estate returns. Not a government source.')


# ---- Added 2026-11-12 by session 0adc9b0a (Questions and Suggestions pages; upgraded to full page by a6ec5b1d) ---
add('FDIC', 'FDIC deposit insurance', 'Federal Deposit Insurance Corporation - Deposit insurance at a glance',
    'https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance', 'page',
    'Standard insurance amount $250,000 per depositor, per insured bank, for each account ownership category; a trust owner with five or more beneficiaries is covered up to $1,250,000 at one bank; stocks, bonds and mutual funds are not insured; Treasury bills, bonds and notes are not FDIC-insured but are backed by the full faith and credit of the U.S. government.')
add('SEC-TEN', 'SEC investing basics', 'U.S. Securities and Exchange Commission - Ten things to consider before you make investing decisions',
    'https://www.sec.gov/investor/pubs/tenthingstoconsider.htm', 'page',
    'Read directly 2026-11-12: SEC Investor Alert covers financial roadmap, risk/reward, asset mix, diversification, 6-month emergency fund, paying off high-interest debt, dollar cost averaging, rebalancing, and fraud prevention.')
add('SEC-ALLOC', 'SEC diversification guide', "U.S. Securities and Exchange Commission - Beginners' guide to asset allocation, diversification and rebalancing",
    'https://www.sec.gov/files/investor/pubs/assetallocation.htm', 'page',
    'Read directly 2026-11-12: Asset allocation by time horizon and risk tolerance across stocks, bonds, and cash equivalents; diversifying within and between asset categories; rebalancing.')
add('IRS-TC703', 'IRS Topic 703', 'IRS Topic no. 703 - Basis of assets',
    'https://www.irs.gov/taxtopics/tc703', 'page',
    'Basis is generally cost; for property acquired other than by purchase (a gift or an inheritance) the rules are in Publication 551; basis is increased by improvements and decreased by allowable depreciation.')
add('IRS-1031', 'IRS like-kind exchanges', 'IRS - Like-kind exchanges, real estate tax tips',
    'https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips', 'page',
    'Gain is generally not recognised when real property held for business or investment is exchanged solely for like-kind real property; money or other property received is taxed; reported on Form 8824; property held primarily for sale does not qualify.')
add('CALBAR-SPEC', 'State Bar specialists', 'State Bar of California - Frequently asked questions: legal specialization',
    'https://www.calbar.ca.gov/frequently-asked-questions-legal-specialization', 'page',
    'Read directly 2026-11-12: The California Board of Legal Specialization directly certifies eleven specialty areas including Estate Planning, Trust and Probate Law and Taxation Law; specialists are searchable via Attorney Search.')
add('SCC-P19-EST', 'Santa Clara Prop 19 estimator', 'Santa Clara County Assessor - Proposition 19 assessment estimator (parent-child transfer)',
    'https://asr.santaclaracounty.gov/online-services/prop-19-assessment-estimator-parent-childgrandparent-grandchild-transfer', 'page',
    'Estimator page opened 2026-11-12 (redirects to /online-services/prop19-calculate); interactive client calculator not executed for any household parcel.')
add('CAPF-BOE19P', 'Claim form BOE-19-P', 'California Assessors - form BOE-19-P for Santa Clara County (parent-child exclusion claim)',
    'https://www.capropeforms.org/counties/santa_clara/form/BOE-19-P', 'page',
    'Read directly 2026-11-12: Confirms Santa Clara County BOE-19-P REV.04 (7-25) for 2026 and Property Transfer Unit filing instructions (130 W Tasman Drive, San Jose, CA 95134).')
add('HUD-SAFMR-INDEX', 'HUD SAFMR releases', 'HUD - Small Area Fair Market Rents, list of yearly releases',
    'https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html', 'page',
    'A fiscal year 2027 release is listed with an interactive lookup and a data file. The fiscal year 2026 file is listed twice: effective October 1, 2025 and a revision effective May 21, 2026. ZIP-level 2027 figures need the interactive lookup and could not be read by this automated session. Attempt 2026-11-13: the per-ZIP calculator address that serves fiscal year 2026 (…/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=…&year=2026) was tried with FY2027 substitutions and returned "404 - File or directory not found"; the release page itself offers only the interactive lookup and a spreadsheet. The fiscal year 2027 ZIP figures therefore remain unread and blank (flag U09), and the site keeps the fiscal year 2026 benchmark it read in full.')
add('FR-FMR-2027', 'Federal Register FMR notice', 'Federal Register 2026-09-01 - Fair Market Rents, fiscal year 2027 (notice 2026-17891)',
    'https://www.federalregister.gov/documents/2026/09/01/2026-17891/fair-market-rents-for-the-housing-choice-voucher-program-moderate-rehabilitation-single-room', 'page',
    'Read directly 2026-11-12 (91 FR 56156, Docket No. FR-6553-N-03, Doc. 2026-17891, published 2026-09-01): FY 2027 FMRs notice with comments closing October 1, 2026 and methodology documentation.')
add('SF-LEG-261020', 'SF File No. 261020', 'San Francisco Board of Supervisors - File No. 261020 (limit on banked and capital-improvement rent increases)',
    'https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770', 'page',
    'Read directly 2026-11-12: Ordinance introduced 2026-09-15 (Land Use & Transportation Committee, Pending Committee Action); caps banked + capital-improvement increases at 10% total per year for 3 years; not enacted.')
add('DIGITAL-GOV', 'Digital.gov content guide', 'U.S. General Services Administration, Digital.gov - An introduction to content',
    'https://digital.gov/resources/an-introduction-to-content', 'page',
    'Read directly 2026-11-12: Federal content guide advising HTML over PDFs, plain language, structured searchability, currency reviews, clear labeling of non-government links, and appropriate translation access.')

