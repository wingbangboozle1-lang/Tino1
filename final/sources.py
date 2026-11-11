"""Source register (session 07a57a05).  Every entry was opened on 2026-11-11 UTC.

how = 'page'    : the official page / PDF itself was fetched and the quoted value was read on it.
how = 'excerpt' : text of the official page was read through a search-engine excerpt of that page
                  (official domain), not through a full fetch.  Listed on the Flagged page for a manual re-read.
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
add('IRS-I706', 'Form 706 instructions', 'IRS - Instructions for Form 706, Table A (Unified Rate Schedule)',
    'https://www.irs.gov/instructions/i706', 'excerpt',
    'Table A: taxable amount over $1,000,000 - tax $345,800 plus 40% of the excess.')
add('IRS-P559', 'IRS Pub. 559', 'IRS Publication 559 - Survivors, Executors, and Administrators',
    'https://www.irs.gov/publications/p559', 'excerpt',
    'Property received as a gift, bequest or inheritance is not included in income; income it later produces (interest, dividends, rents) is taxable. Lump sums from an inherited traditional IRA may be taxable.')
add('IRS-P527', 'IRS Pub. 527', 'IRS Publication 527 - Residential Rental Property',
    'https://www.irs.gov/publications/p527', 'excerpt',
    'Residential rental property is depreciated straight-line over 27.5 years under GDS.')
add('IRS-1041', 'IRS estate income tax', 'IRS - File an estate tax income tax return',
    'https://www.irs.gov/individuals/file-an-estate-tax-income-tax-return', 'excerpt',
    'Form 1041 is required when the estate has more than $600 of annual gross income; an EIN is needed first.')
add('CONG-S587', 'S.587', 'Congress.gov - S.587, Death Tax Repeal Act of 2025',
    'https://www.congress.gov/bill/119th-congress/senate-bill/587', 'excerpt',
    'Introduced 2025-02-13, read twice and referred to the Committee on Finance. Status shown: Introduced.')
add('CONG-HR1301', 'H.R.1301', 'Congress.gov - H.R.1301, Death Tax Repeal Act',
    'https://www.congress.gov/bill/119th-congress/house-bill/1301/all-info', 'excerpt',
    'Introduced 2025-02-13, referred to House Ways and Means. Status shown: Introduced.')
# ---- California --------------------------------------------------------------
add('SCO-ESTATE', 'CA Controller', 'California State Controller - California Estate Tax',
    'https://www.sco.ca.gov/ardtax_estate_tax.html', 'page',
    'No California estate tax return is required for deaths on or after 2005-01-01. Inheritance tax applies only to deaths before 1982-06-08.')
add('BOE-P19', 'BOE Prop 19', 'California State Board of Equalization - Proposition 19',
    'https://www.boe.ca.gov/prop19/', 'page',
    'Parent-child exclusion applies only to a principal residence of the transferor that becomes the principal residence of the transferee; value limit = taxable value plus $1,000,000 (adjusted every two years); homeowners\' exemption within one year; claim within three years or before transfer to a third party; other real property no longer excluded; effective 2021-02-16.')
add('BOE-LTA-2025-009', 'BOE LTA 2025/009', 'BOE Letter to Assessors 2025/009 - adjustment of the $1 million amount',
    'https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf', 'page',
    '$1,044,586 for transfers 2025-02-16 through 2027-02-15; adjusted every other February 16 by the FHFA California House Price Index change for the prior calendar year (2.15% for 2024); next adjustment February 2027.')
add('BOE-LTA-2026-026', 'BOE LTA 2026/026', 'BOE Letter to Assessors 2026/026 - Prop 19 intergenerational exclusion FAQ (2026-08-03)',
    'https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf', 'page',
    'Definitions: excluded amount = factored base year value + adjusted $1 million; new taxable value = factored base year value + excess; transfers through a trust are covered; the home must be continually used as the family home or the full new base year value is enrolled.')
add('RTC-63.2', 'R&TC 63.2', 'California Revenue and Taxation Code section 63.2',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2.', 'page',
    'Principal residence of the transferor; becomes the transferee\'s principal residence within one year; homeowners\' exemption filed within a year; exclusion removed when the transferee is no longer eligible.')
add('RTC-480', 'R&TC 480', 'California Revenue and Taxation Code section 480',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.', 'page',
    'Change in ownership statement: where the change is by reason of death, file within 150 days after the date of death (or with the inventory and appraisal if probated).')
add('PROB-16061.7', 'Prob. Code 16061.7', 'California Probate Code section 16061.7',
    'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.', 'page',
    'Trustee notification within 60 days after a revocable trust becomes irrevocable by death; served on beneficiaries and heirs; 120-day contest warning.')
add('BOE-RULE-462.260', 'BOE Rule 462.260', 'BOE Property Tax Rule 462.260 - Date of change in ownership',
    'https://boe.ca.gov/proptaxes/pdf/rules/Rule462_260.pdf', 'page',
    'Revocable trust: date of change in ownership is the date the trust becomes irrevocable (example: the date of death). Inheritance: the date of death.')
add('BOE-HOX', 'BOE homeowners\' exemption', 'BOE - Homeowners\' Exemption',
    'https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm', 'page',
    '$7,000 reduction in taxable value for an owner-occupied principal residence on the January 1 lien date; one-time claim BOE-266; file by February 15 for the full exemption.')
add('FTB-RATES', 'FTB 2025 rates', 'Franchise Tax Board - 2025 California Tax Rate Schedules',
    'https://www.ftb.ca.gov/forms/2025/2025-540-tax-rate-schedules.pdf', 'page',
    'Schedule X (single): 9.3% over $72,724; 10.3% over $371,479; 11.3% over $445,771; 12.3% over $742,953.')
add('FTB-MHS', 'FTB Form 540 booklet', 'Franchise Tax Board - Form 540 booklet, Mental Health Services Tax',
    'https://www.ftb.ca.gov/forms/2024/2024-540-booklet.html', 'excerpt',
    'Additional 1% tax on taxable income over $1,000,000.')
add('SOS-RESULTS', 'CA Secretary of State', 'California Secretary of State - 2026 General Election, state ballot measures (unofficial)',
    'https://electionresults.sos.ca.gov/returns/ballot-measures', 'page',
    'Unofficial results as of 2026-11-10 5:31 p.m.; certification by 2026-12-11. Prop 3 Yes 60.6%; Prop 40 No 52.6%; Prop 41 No 55.0%; Prop 42 Yes 51.5%; Prop 43 No 57.4%. Fourteen measures listed (1-5, 37-45).')
add('DOJ-TPA', 'CA Attorney General', 'California Department of Justice - Tenant Protection Act consumer alert',
    'https://oag.ca.gov/system/files/media/Tenant-Protection-Act-Landlords-and-Property-Managers-English.pdf', 'excerpt',
    'Rent may not rise more than 5% plus the change in CPI, or 10% total, whichever is lower, in any 12 months; exemptions include certain single-family homes not owned by a corporation or REIT.')
add('CDI-TOOL', 'CDI premium survey', 'California Department of Insurance - Compare insurance premiums (2026 homeowners survey tool)',
    'https://www.insurance.ca.gov/01-consumers/105-type/9-compare-prem/index.cfm', 'page',
    'Official annual premium survey with an interactive tool by ZIP code; results are not quotes; wildfire surcharges of 15% to over 300% are not reflected. The interactive results could not be read by this automated session.')
add('CDI-TOOL-APP', 'CDI homeowners tool', 'California Department of Insurance - 2026 Homeowners Insurance comparison tool',
    'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20', 'page',
    'Landing text read; ZIP-level premium tables require interactive input.')
add('CDI-EQ', 'CDI earthquake guide', 'California Department of Insurance - Earthquake insurance',
    'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/eq-ins.cfm', 'page',
    'Homeowners policies do not cover earthquake damage (fire following an earthquake is covered); the insurer must offer earthquake coverage every other year.')
add('CDI-RES', 'CDI residential guide', 'California Department of Insurance - Residential insurance guide',
    'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/res-ins-guide.cfm', 'excerpt',
    'Perils generally not covered include flood, earthquake, earth movement and losses to a house vacant for 60 days or more.')
add('CPUC-NEM', 'CPUC net metering', 'California Public Utilities Commission - Net energy metering and net billing',
    'https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing', 'excerpt',
    'NEM customers may stay on their tariff for 20 years from interconnection; customers moving from NEM to the net billing tariff get no legacy period.')
add('CPUC-FIXED', 'CPUC fixed charge', 'CPUC resolution on PG&E advice letter 7351-E (Decision 24-05-028 fixed charge)',
    'https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M555/K816/555816677.pdf', 'excerpt',
    'Residential fixed charge of $24.15 per month for customers not in a discount tier.')
add('CDI-SB824', 'CDI wildfire-risk data', 'California Department of Insurance - SB 824 residential property data (coverage amounts, wildfire risk and losses)',
    'https://www.insurance.ca.gov/01-consumers/200-wrr/WildfireRiskInfoRpt.cfm', 'page',
    'Statewide totals for 2023, all residential policy forms: earned premium $14,217,212,455 on 12,580,970 earned exposures (about $1,130 a policy); average Coverage A $324,973. ZIP-level sheets exist in the workbook but could not be read by this automated session.')
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
add('SFPUC', 'SFPUC rates', 'San Francisco Public Utilities Commission - Water and sewer rate schedules FY2026-27',
    'https://www.sfpuc.gov/sites/default/files/accounts-and-services/Rates_Schedule_Water_Sewer_2026-7.pdf', 'excerpt',
    'Rate schedule for 7/1/26 and 7/1/27. Rate Fairness Board presentation: water +7.0% each year; residential wastewater +10.8% then +10.1%.')
# ---- Data ----------------------------------------------------------------------
add('HUD-95014', 'HUD SAFMR 95014', 'HUD - FY2026 Small Area Fair Market Rents, ZIP 95014',
    'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026', 'page',
    'FY2026: efficiency $3,340; one-bedroom $3,800; two-bedroom $4,440; three-bedroom $5,870; four-bedroom $6,390 per month (40th-percentile gross rent).')
add('HUD-94122', 'HUD SAFMR 94122', 'HUD - FY2026 Small Area Fair Market Rents, ZIP 94122',
    'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=94122&metro_code=METRO41860MM7360&year=2026', 'page',
    'FY2026: efficiency $2,280; one-bedroom $2,730; two-bedroom $3,310; three-bedroom $4,230; four-bedroom $4,380 per month.')
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
    'https://www.cbo.gov/publication/62105', 'excerpt',
    'PCE inflation 2.7% in 2026, 2.0% by 2030; 10-year Treasury rate 4.1% in 2026 and 4.3% in 2027; real GDP growth averages 1.8% a year 2027-2036.')
add('USGS', 'USGS earthquake outlook', 'U.S. Geological Survey Fact Sheet 2016-3020 - Earthquake outlook for the San Francisco Bay region 2014-2043',
    'https://pubs.usgs.gov/fs/2016/3020/fs20163020.pdf', 'excerpt',
    '72% probability of at least one magnitude 6.7 or greater earthquake in the Bay region before 2043; 51% for magnitude 7.0 or greater.')
add('FRED-JP', 'Japan series (FRED)', 'Japan: BIS residential property prices, Nikkei 225 and OECD consumer prices (via FRED QJPN368BIS, NIKKEI225, JPNCPIALLMINMEI)',
    'https://fred.stlouisfed.org/series/QJPN368BIS', 'page',
    'Year-end values 1989-2012 read on the FRED download: home prices fell in 21 of the 22 years 1991-2012; Nikkei 225 38,915.87 at end-1989, 8,455.35 at end-2011. Home-price changes for 2013-2020 taken from the file prepared by session 4395771d from the same series.')
add('DAMODARAN', 'NYU Stern returns table', 'NYU Stern (A. Damodaran) - Historical returns on stocks, bonds and bills 1928-2025',
    'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html', 'academic',
    'Annual S&P 500 total return, 3-month T-bill, 10-year T-bond and national real-estate returns. Not a government source.')
