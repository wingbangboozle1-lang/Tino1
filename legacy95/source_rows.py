#!/usr/bin/env python3
"""Close-out pass for the superseded editions (session 95383689, task L95-1).

Adds an official source link - or an explicit unverified/assumption label - to
every legacy table row that had neither (CR-07-5), and replaces the
non-official commercial citations named in CR-85-1 / CR-85-2.

Rules:
  * a link is only added where the official page was read in this session or is
    listed in final/sources.py (re-read 2026-11-11 by session 07a57a05);
  * model outputs get a link to the official input series they are driven by and
    a visible "model output" label;
  * values with no official source keep their number and gain an explicit
    "unverified" label - never a made-up source, never a blanked archive row.

Run:  python3 legacy95/source_rows.py
Idempotent: rows already compliant are skipped.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowrule import LABEL, host_ok, row_state, strip_tags  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- sources ----
# V = page fetched and read in this session on 2026-11-11
# S = listed in final/sources.py (re-read 2026-11-11 by session 07a57a05) or
#     already linked by a prior session in the same edition (carried over)
FRED_A = 'https://fred.stlouisfed.org/series/ATNHPIUS41940Q'          # S
FRED_SF = 'https://fred.stlouisfed.org/series/ATNHPIUS41884Q'         # S
CPIAUCSL = 'https://fred.stlouisfed.org/series/CPIAUCSL'              # S
BLS_CPI = 'https://www.bls.gov/news.release/cpi.nr0.htm'             # S
IRS_ESTATE = 'https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax'  # S
IRS_WHATSNEW = 'https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax'  # V (fee $56 -> $76 read here)
IRS_FAQ = 'https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances'  # S
IRS_TC701 = 'https://www.irs.gov/taxtopics/tc701'                     # S
IRS_TC409 = 'https://www.irs.gov/taxtopics/tc409'                     # S
IRS_TC559 = 'https://www.irs.gov/taxtopics/tc559'                     # S
IRS_I706 = 'https://www.irs.gov/instructions/i706'                    # S
IRS_IRB2316 = 'https://www.irs.gov/irb/2023-16_IRB'                   # S
IRS_DECEASED = 'https://www.irs.gov/individuals/deceased-person'      # S (dashboard register)
IRS_P527 = 'https://www.irs.gov/publications/p527'                    # S
IRS_P551 = 'https://www.irs.gov/publications/p551'                    # V
IRS_P523 = 'https://www.irs.gov/publications/p523'                    # V
IRS_P946 = 'https://www.irs.gov/publications/p946'                    # V
IRS_GIFT = 'https://www.irs.gov/businesses/small-businesses-self-employed/gift-tax'  # S (linked from IRS page read today)
RP2532 = 'https://www.irs.gov/pub/irs-drop/rp-25-32.pdf'              # S (linked across editions)
GOV1014 = 'https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapO-partII-sec1014.htm'  # V
GOV2001 = 'https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleB-chap11-subchapA-partI-sec2001.htm'  # V
RTC51 = 'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51'  # V (2% cap read here)
PROB160617 = 'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.'  # S
BOE_PROP19 = 'https://www.boe.ca.gov/prop19/'                          # S
LTA25009 = 'https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf'         # S
LTA26026 = 'https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf'         # S
BOE_HOX = 'https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm'  # S
ASR_HOME = 'https://asr.santaclaracounty.gov/home'                     # V (sccassessor.org redirects here)
ASR_P2C = 'https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2'  # S
TRB = 'https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE'  # S
RECORDER = 'https://clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate'  # S
SFT = 'https://sftreasurer.org/property/secured-property-taxes'        # S
SF_ASSESSOR = 'https://www.sf.gov/departments--assessor-recorder'      # V (sfassessor.org redirects here)
SF_RENT = 'https://www.sf.gov/learn-about-san-francisco-rental-laws/'  # S
SF_RENTINC = 'https://www.sf.gov/news--annual-rent-increase-3126-22827-announced'  # S
HUD95014 = 'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=95014&metro_code=METRO41940M41940&year=2026'  # S
HUD94122 = 'https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2026_code/2026zip_code_calc.odn?zcta=94122&metro_code=METRO41860MM7360&year=2026'  # S
CDI_COMPARE = 'https://www.insurance.ca.gov/01-consumers/105-type/9-compare-prem/index.cfm'  # S
CDI_EQ = 'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/eq-ins.cfm'  # S
CDI_RES = 'https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/res-ins-guide.cfm'  # S
CDI_STUDY = 'https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/'  # S
CDI_DATA = 'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20'  # S
CPUC_NEM = 'https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing'  # S
SFPUC_RATES = 'https://www.sfpuc.gov/sites/default/files/accounts-and-services/Rates_Schedule_Water_Sewer_2026-7.pdf'  # S
SOS_BALLOT = 'https://electionresults.sos.ca.gov/returns/ballot-measures'  # S
COURTS = 'https://selfhelp.courts.ca.gov/'                             # V
FTB = 'https://www.ftb.ca.gov/'                                        # V
NBER = 'https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions'  # V
PGND = 'https://www.freddiemac.com/'                                   # S (domain already cited in these editions)

MODEL = ('model output &mdash; official input series: '
         '<a href="%s" title="FHFA house price index (via FRED) - official series the growth assumption is calibrated to">FHFA HPI</a>')
MODEL_CPI = ('model output &mdash; official input series: '
             '<a href="%s" title="CPI-U (via FRED) - official series the inflation assumption is calibrated to">CPI</a>')
MODEL_IRS = ('model output &mdash; official rules: '
             '<a href="%s" title="IRS estate tax - official exclusion and rate the grid applies">IRS estate tax</a>')
MODEL_BOE = ('model output &mdash; official formula: '
             '<a href="%s" title="BOE LTA 2026/026 - official Proposition 19 formula the grid applies">BOE LTA 2026/026</a>')


def L(url, text, title=None):
    t = title or text
    return '<a href="%s" title="%s" rel="noopener">%s</a>' % (url, t, text)


def label_span(text):
    return '<span class="flag-unverified" style="color:#8a4b00">[%s]</span>' % text


def append_last_td(row, frag):
    i = row.rfind('</td>')
    if i == -1:
        return row, False
    return row[:i] + ' ' + frag + row[i:], True


# ------------------------------------------------------------- strategies ----
# mode per (file, table index): 'fred' | 'cpi' | 'irs' | 'boe' | ('map', [...]) | ('label', text)
# map entries: (substring, fragment) - first match on the tag-stripped row wins.
# unmatched rows fall back to the table's FALLBACK.
FRED_FRAG = MODEL % FRED_A
CPI_FRAG = MODEL_CPI % CPIAUCSL
IRS_FRAG = MODEL_IRS % IRS_ESTATE
BOE_FRAG = MODEL_BOE % LTA26026

MAP_PROC0 = [
    ('Secure property', L(COURTS, 'California Courts self-help (trusts & estates)')),
    ('Record Affidavit', L(RECORDER, 'SCC Clerk-Recorder - recording')),
    ('Inventory & date-of-death', L(IRS_P551, 'IRS Pub 551 (basis)')),
    ('Notify county assessors', L(ASR_HOME, 'SCC Assessor - change in ownership')),
    ('Supplemental / Escape', L(ASR_HOME, 'SCC Assessor - assessments')),
    ('12 months', L(BOE_HOX, 'BOE homeowners\' exemption')),
    ('3 years', L(ASR_P2C, 'SCC Assessor - parent-to-child exclusion')),
    ('9 months of death', L(IRS_I706, 'IRS Form 706 instructions')),
    ('Apr 15', L(IRS_DECEASED, 'IRS - deceased persons')),
    ('Ongoing', L(SFT, 'SF Treasurer - secured tax due dates (statewide dates)')),
    ('If selling Cupertino', L(IRS_TC409, 'IRS Topic 409')),
    ('If keeping & renting', L(IRS_P527, 'IRS Pub 527')),
]
MAP_PROC1 = [
    ('Probate', L(COURTS, 'California Courts self-help')),
    ('Property tax', L(ASR_HOME, 'SCC Assessor')),
    ('Step-up in basis', L(GOV1014, 'IRC 1014 (govinfo)')),
    ('Control', L(COURTS, 'California Courts self-help')),
    ('Irrevocable trust warning', L(IRS_IRB2316, 'IRS IRB 2023-16 (Rev. Rul. 2023-2)')),
]
MAP_PROC2 = [
    ('Affidavit', L(RECORDER, 'SCC Clerk-Recorder')),
    ('PCOR', L(ASR_HOME, 'SCC Assessor')),
    ('BOE-266', L(BOE_HOX, 'BOE homeowners\' exemption')),
    ('BOE-19-P', L(ASR_P2C, 'SCC Assessor - parent-to-child')),
    ('Form 706', L(IRS_I706, 'IRS Form 706 instructions')),
    ('Form 593', L(FTB, 'FTB (withholding)')),
    ('Form 3840', L(FTB, 'FTB (Form 3840)')),
]
MAP_PROC3 = [
    ('Sell promptly', L(IRS_TC701, 'IRS Topic 701 (home sale exclusion)')),
    ('Move in (live-in)', L(ASR_P2C, 'SCC Assessor - parent-to-child exclusion')),
    ('Rent out', L(SF_RENT, 'SF rental laws')),
]
MAP_INH2 = [
    ('Month 0||Death' if False else 'Death; successor trustee', L(COURTS, 'California Courts self-help')),
    ('Attorney reviews trust', L(PROB160617, 'Prob. Code 16061.7')),
    ('PCOR filed', L(ASR_HOME, 'SCC Assessor')),
    ('Heir moves into Cupertino', L(BOE_HOX, 'BOE homeowners\' exemption')),
    ('Form 706 due', L(IRS_I706, 'IRS Form 706 instructions')),
    ('File BOE-19-P', L(ASR_P2C, 'SCC Assessor - parent-to-child')),
    ('IRS/state clearance', L(IRS_ESTATE, 'IRS estate tax')),
]
MAP_ITAX1 = [
    ('Cash, brokerage', L(IRS_FAQ, 'IRS - gifts and inheritances (basis)')),
    ('Primary home', L(IRS_FAQ, 'IRS - gifts and inheritances (basis)')),
    ('Traditional IRA', label_span('unverified citation - IRA rules not re-read in this session')),
    ('Roth IRA', label_span('unverified citation - IRA rules not re-read in this session')),
]
MAP_ITAX3 = [
    ('Stepped-up basis', L(IRS_P551, 'IRS Pub 551')),
    ('Holding period', label_span('unverified citation - IRC 1223 text not re-read in this session')),
    ('Net Investment Income', L(IRS_TC559, 'IRS Topic 559')),
    ('CA state on gain', L(FTB, 'FTB')),
    ('Primary residence exclusion', L(IRS_P523, 'IRS Pub 523')),
    ('1031 exchange', L(FTB, 'FTB (Form 3840)')),
]
MAP_ITAX4 = [
    ('Rental income', L(IRS_P527, 'IRS Pub 527')),
    ('Depreciation', L(IRS_P946, 'IRS Pub 946')),
    ('Recapture', label_span('unverified citation - IRC 1250 text not re-read in this session')),
]
MAP_INDEX5 = [
    ('Sale price', label_span('owner figure - no official source (estimate, not an appraisal)')),
    ('Selling costs', label_span('assumption - no official source')),
    ('Capital gains', L(IRS_FAQ, 'IRS - inherited property basis')),
    ('Net to reinvest', label_span('calculation from flagged rows')),
    ('At 7%', FRED_FRAG),
]
MAP_INDEX2 = [
    ('Move in + file', L(BOE_PROP19, 'BOE Proposition 19')),
    ('Don', L(BOE_PROP19, 'BOE Proposition 19')),
    ('Miss 1-year', L(LTA25009, 'BOE LTA 2025/009 (allowance)')),
]
MAP_CUP2 = [
    ('A. Live in', L(ASR_P2C, 'SCC Assessor - parent-to-child exclusion')),
    ('B. Rent', L(SFT, 'SF Treasurer - reassessment on change in ownership')),
    ('C. Sell', L(IRS_FAQ, 'IRS - inherited property basis (step-up)')),
]
MAP_OPC0 = [
    ('HO-3 standard policy', L(CDI_RES, 'CDI homeowners insurance guide') + ' ' + label_span('NAIC figure - non-official')),
    ('All forms statewide', L(CDI_DATA, 'CDI data call')),
    ('Statewide avg', L(CDI_STUDY, 'CDI homeowners study')),
    ('Landlord policy median', L(CDI_COMPARE, 'CDI comparison guide') + ' ' + label_span('industry estimate - non-official')),
]
MAP_OPC1 = [
    ('Water', L(SFPUC_RATES, 'SFPUC rate schedule (B); A supplied by SJ Water')),
    ('Electric', L(CPUC_NEM, 'CPUC net energy metering')),
    ('Gas', label_span('PG&E G-1 tariff - utility page not re-read in this session')),
    ('Trash', label_span('sewer/trash usually on the tax bill - no separate official figure')),
]
MAP_OPC2 = [
    ('Annual maintenance', label_span('industry rule of thumb - no official source')),
    ('Major capex', label_span('estimate - no official source')),
    ('Total implied', label_span('estimate - no official source')),
]
MAP_OPC3 = [
    ('Property tax', L(ASR_HOME, 'SCC Assessor') + ' ' + L(SFT, 'SF Treasurer')),
    ('Insurance', L(CDI_STUDY, 'CDI homeowners study')),
    ('Water', L(SFPUC_RATES, 'SFPUC rate schedule')),
    ('Electric', L(CPUC_NEM, 'CPUC NEM')),
    ('Maintenance (1%', label_span('rule of thumb - no official source')),
    ('Total', label_span('sum of flagged rows')),
    ('Rental income', label_span('owner-reported rent - unverified')),
    ('Net if SF', label_span('calculation from flagged rows')),
    ('2045 projected', FRED_FRAG),
    ('2045 carrying', BOE_FRAG),
]
MAP_DOCPROJ0 = [
    ('Projected 2% cap', L(RTC51, 'RTC 51 (2% cap)') + ' ' + FRED_FRAG),
    ('Same', FRED_FRAG),
]
MAP_DOCPROJ1 = [('If inherited', L(LTA25009, 'BOE LTA 2025/009 (allowance)'))]
MAP_DOCPROJ5 = [
    ('FHFA HPI sensitivity', FRED_FRAG),
    ('Tax live-in', L(RTC51, 'RTC 51 (2% cap)')),
    ('Tax full', L(RTC51, 'RTC 51 (2% cap)')),
]
MAP_IDX8 = [
    ('Home insurance', L(CDI_COMPARE, 'CDI comparison guide') + ' ' + label_span('commercial estimate - non-official')),
    ('Total', label_span('sum of flagged rows')),
]
MAP_SOURCES1 = [
    ('Estate $15M', L(RP2532, 'Rev. Proc. 2025-32')),
    ('Prop 19 $1,044,586', L(LTA25009, 'BOE LTA 2025/009')),
    ('Stepped-up basis', L(GOV1014, 'IRC 1014 (govinfo)')),
    ('Property tax rates', L(TRB, 'SCC Tax Rate Book') + ' ' + L(SFT, 'SF Treasurer')),
]
MAP_TAXES0 = [('Top rate above exemption', L(GOV2001, 'IRC 2001(c) (govinfo)'))]
MAP_TAXES2 = [('Primary residence exclusion', L(IRS_P523, 'IRS Pub 523'))]
MAP_FLAGGED9 = [('Earthquake insurance', L(CDI_EQ, 'CDI earthquake guide'))]
MAP_IDX2B = MAP_INDEX2
MAP_PROJ5B = MAP_DOCPROJ5

MAP_ARCH_PROC0 = [
    ('Death certificates', L(COURTS, 'California Courts self-help')),
    ('Trustee notice', L(PROB160617, 'Prob. Code 16061.7')),
    ('Asset inventory', label_span('Prob. Code 16062 citation - text not re-read in this session')),
    ('Federal estate return', L(IRS_I706, 'IRS Form 706 instructions')),
    ('Heir occupies A', L(BOE_HOX, 'BOE homeowners\' exemption')),
    ('Parent', L(ASR_P2C, 'SCC Assessor - parent-to-child')),
    ('Rents', L(SF_RENTINC, 'SF annual rent increase')),
]
MAP_ARCH_METH0 = [
    ('Prop 13 cap', L(RTC51, 'RTC 51 / Cal. Const. art. XIII A sec. 2(b)')),
    ('B — ad valorem rate', L(SFT, 'SF Treasurer')),
    ('A — ad valorem', L(TRB, 'SCC Tax Rate Book')),
    ('Prop 19 cap', L(LTA25009, 'BOE LTA 2025/009')),
    ('Rent growth', L(SF_RENTINC, 'SF annual rent increase')),
]
MAP_ARCH_PROP2 = [('20', L(ASR_HOME, 'SCC Assessor') + ' ' + L(SF_ASSESSOR, 'SF Assessor-Recorder'))]
MAP_ARCH_PROP0 = [
    ('Market value', label_span('owner figure - no official source (estimate)')),
    ('Water', label_span('owner-reported range - unverified')),
    ('Electricity', label_span('owner-reported - unverified')),
    ('carrying cost', label_span('model sum of flagged rows')),
]
MAP_ARCH_PROP1 = [
    ('Market value', label_span('owner figure - no official source (estimate)')),
    ('factored assessed', L(ASR_HOME, 'SCC Assessor') + ' ' + label_span('model: prior value x 1.02')),
    ('Units', label_span('owner statement - unverified')),
    ('Gross rent', label_span('owner-reported rent - unverified')),
    ('Water', label_span('owner-reported range - unverified')),
    ('Electricity', label_span('owner-reported range - unverified')),
    ('carrying cost', label_span('model sum of flagged rows')),
    ('Net rental', label_span('calculation from flagged rows')),
]
MAP_ARCH_IDX1 = [('Executive summary', label_span('status row - points to the section that answers it')),
                 ('', label_span('status row - points to the section that answers it'))]
MAP_ARCH_COSTS0 = [('Total 2026', label_span('sum of flagged rows'))]
MAP_ARCH_COSTS1 = [
    ('Electricity', label_span('owner-reported range grown by assumption - unverified')),
    ('Total carrying', label_span('sum of flagged rows')),
    ('Net cash flow', label_span('calculation from flagged rows')),
]
MAP_ARCH_COSTS2 = [
    ('Income: A rent', L(HUD95014, 'HUD FY2026 rent benchmark')),
    ('Income: B rents', label_span('owner-reported rent - unverified')),
    ('Costs:', label_span('model sum of flagged rows')),
    ('Net household', label_span('calculation from flagged rows')),
]
MAP_ARCH_COSTS3 = [('Discounts', L(CDI_COMPARE, 'CDI comparison guide')),
                   ('', label_span('advice row - no official source'))]
MAP_ARCH_TAXES0 = [('', FRED_FRAG)]
MAP_ARCH_TAXES1 = [('combined top rate', L(IRS_TC559, 'IRS Topic 559 (NIIT)') + ' ' + L(FTB, 'FTB rates'))]
MAP_ARCH_TAXES2 = [('Primary residence exclusion', L(IRS_P523, 'IRS Pub 523'))]
MAP_ARCH_SOURCES2 = [('SCC DTAC', L(ASR_HOME, 'SCC Assessor'))]
MAP_ARCH_SOURCES3 = [('NBER', L(NBER, 'NBER business-cycle dating (read 2026-11-11)'))]
MAP_ARCH_SOURCES5 = [
    ('Freddie Mac PMMS', L(PGND, 'Freddie Mac (PMMS publisher)')),
    ('S&P Dow Jones', label_span('index provider - non-official, figure not re-read')),
    ('World Bank', label_span('international statistical agencies - figures not re-read in this session')),
    ('', label_span('source row - figure not re-read in this session')),
]
MAP_ARCH_FL0 = [('', label_span('flagged item - see register'))]
MAP_ARCH_FL1 = [('', label_span('flagged item - see register'))]
MAP_ARCH_PENDING = [('', label_span('pending-change row - see cited measure on its official page'))]
MAP_DASH_FL = [('X08', label_span('flagged - ownership structure unresolved'))]
MAP_SF1 = [
    ('Vacancy', label_span('assumption - no official source')),
    ('Net operating income', label_span('calculation from flagged rows')),
]
MAP_DOCPROJ6 = [('', label_span('rounding convention - no source needed'))]
MAP_BS0 = [
    ('1979-1982', L(BLS_CPI, 'BLS CPI') + ' ' + L(NBER, 'NBER cycle dates')),
    ('Early-1990s', L(BLS_CPI, 'BLS CPI') + ' ' + L(NBER, 'NBER cycle dates')),
    ('Dot-com', L(BLS_CPI, 'BLS CPI') + ' ' + L(NBER, 'NBER cycle dates')),
    ('Global financial crisis', L(BLS_CPI, 'BLS CPI') + ' ' + L(NBER, 'NBER cycle dates')),
    ('COVID-19', L(BLS_CPI, 'BLS CPI') + ' ' + L(NBER, 'NBER cycle dates')),
    ('Black Monday', label_span('market-history figure - not re-read from an official page in this session')),
]
MAP_IDX5B = MAP_INDEX5
MAP_CMP2 = [
    ('Property tax', BOE_FRAG),
    ('Rent collected', L(HUD94122, 'HUD FY2026 rent benchmark')),
    ('', FRED_FRAG),
]
MAP_CMP0 = [('', FRED_FRAG + ' ' + label_span('C.A.R. forecast cited by the edition - non-official'))]
MAP_CMP1 = [('', FRED_FRAG)]
MAP_CMP3 = [('', label_span('qualitative scenario row - no official source'))]
MAP_CMP4 = [('', FRED_FRAG)]
MAP_DEC0 = [('', FRED_FRAG)]
MAP_DEC1 = [('', FRED_FRAG)]
MAP_DEC2 = [('', FRED_FRAG)]
MAP_DEC3 = [('', label_span('qualitative assessment - no official source'))]
MAP_IDX7 = [('', FRED_FRAG)]
MAP_IDX6 = [('', label_span('calculation from flagged rows'))]
MAP_IDX4 = [('', label_span('sum of flagged rows'))]
MAP_CUP1 = [('', label_span('sum of flagged rows'))]
MAP_INH1 = MAP_ITAX1
MAP_DASH_IDX = MAP_ARCH_IDX1

# (file, table) -> (mode, map_or_none, fallback_fragment)
TABLES = {
    ('dashboard/black-swan.html', 0): ('map', MAP_BS0, label_span('flagged - episode row')),
    ('dashboard/black-swan.html', 2): ('map', None, FRED_FRAG),
    ('dashboard/black-swan.html', 3): ('map', None, FRED_FRAG),
    ('dashboard/black-swan.html', 4): ('map', None, IRS_FRAG),
    ('dashboard/costs.html', 3): ('map', None, FRED_FRAG),
    ('dashboard/costs.html', 4): ('map', None, FRED_FRAG),
    ('dashboard/executive-summary.html', 1): ('map', None, FRED_FRAG),
    ('dashboard/flagged.html', 0): ('map', MAP_DASH_FL, label_span('flagged item - see register')),
    ('dashboard/inheritance-tax.html', 2): ('map', None, IRS_FRAG),
    ('dashboard/methodology.html', 0): ('map', [
        ('av_growth', L(RTC51, 'RTC 51 (2% cap)')),
        ('rate_a', L(TRB, 'SCC Tax Rate Book')),
        ('rate_b', L(SFT, 'SF Treasurer')),
        ('hox', L(BOE_HOX, 'BOE homeowners\' exemption')),
        ('prop19_cap_2025', L(LTA25009, 'BOE LTA 2025/009')),
        ('estate_exclusion_2026', L(RP2532, 'Rev. Proc. 2025-32')),
        ('estate_rate', L(GOV2001, 'IRC 2001(c)')),
        ('sec121', L(IRS_TC701, 'IRS Topic 701')),
        ('transfer_tax_sf', L(SFT, 'SF Treasurer')),
        ('transfer_tax_scc', L(RECORDER, 'SCC Clerk-Recorder')),
        ('controlled_rent_growth', L(SF_RENTINC, 'SF annual rent increase')),
        ('rent_a_market', L(HUD95014, 'HUD FY2026 rent benchmark')),
    ], label_span('assumption - no official source')),
    ('dashboard/prop19.html', 1): ('map', None, BOE_FRAG),
    ('dashboard/projections.html', 0): ('map', None, FRED_FRAG),
    ('dashboard/projections.html', 1): ('map', None, FRED_FRAG),
    ('dashboard/projections.html', 2): ('map', None, FRED_FRAG),
    ('dashboard/projections.html', 3): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 0): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 1): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 2): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 3): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 4): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 5): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 6): ('map', None, FRED_FRAG),
    ('dashboard/scenarios.html', 7): ('map', None, FRED_FRAG),

    ('docs/compare-decisions.html', 0): ('map', MAP_CMP0, FRED_FRAG),
    ('docs/compare-decisions.html', 1): ('map', MAP_CMP1, FRED_FRAG),
    ('docs/compare-decisions.html', 2): ('map', MAP_CMP2, FRED_FRAG),
    ('docs/compare-decisions.html', 3): ('map', MAP_CMP3, label_span('qualitative scenario - no official source')),
    ('docs/compare-decisions.html', 4): ('map', MAP_CMP4, FRED_FRAG),
    ('docs/cupertino.html', 1): ('map', MAP_CUP1, label_span('sum of flagged rows')),
    ('docs/cupertino.html', 2): ('map', MAP_CUP2, BOE_FRAG),
    ('docs/decision.html', 0): ('map', MAP_DEC0, FRED_FRAG),
    ('docs/decision.html', 1): ('map', MAP_DEC1, FRED_FRAG),
    ('docs/decision.html', 2): ('map', MAP_DEC2, FRED_FRAG),
    ('docs/decision.html', 3): ('map', MAP_DEC3, label_span('qualitative assessment - no official source')),
    ('docs/flagged.html', 0): ('map', MAP_FLAGGED9, label_span('flagged item - see register')),
    ('docs/index.html', 2): ('map', MAP_INDEX2, BOE_FRAG),
    ('docs/index.html', 4): ('map', MAP_IDX4, label_span('sum of flagged rows')),
    ('docs/index.html', 5): ('map', MAP_INDEX5, FRED_FRAG),
    ('docs/index.html', 6): ('map', MAP_IDX6, label_span('calculation from flagged rows')),
    ('docs/index.html', 7): ('map', MAP_IDX7, FRED_FRAG),
    ('docs/index.html', 8): ('map', MAP_IDX8, label_span('sum of flagged rows')),
    ('docs/inheritance-tax.html', 1): ('map', MAP_ITAX1, label_span('unverified citation - not re-read in this session')),
    ('docs/inheritance-tax.html', 3): ('map', MAP_ITAX3, label_span('unverified citation - not re-read in this session')),
    ('docs/inheritance-tax.html', 4): ('map', MAP_ITAX4, label_span('unverified citation - not re-read in this session')),
    ('docs/inheritance.html', 2): ('map', MAP_INH2, label_span('step row - citation not re-read in this session')),
    ('docs/operating-costs.html', 0): ('map', MAP_OPC0, label_span('estimate - non-official')),
    ('docs/operating-costs.html', 1): ('map', MAP_OPC1, label_span('estimate - no official source')),
    ('docs/operating-costs.html', 2): ('map', MAP_OPC2, label_span('estimate - no official source')),
    ('docs/operating-costs.html', 3): ('map', MAP_OPC3, FRED_FRAG),
    ('docs/process.html', 0): ('map', MAP_PROC0, label_span('step row - citation not re-read in this session')),
    ('docs/process.html', 1): ('map', MAP_PROC1, label_span('step row - citation not re-read in this session')),
    ('docs/process.html', 2): ('map', MAP_PROC2, label_span('form row - see official IRS/FTB source')),
    ('docs/process.html', 3): ('map', MAP_PROC3, BOE_FRAG),
    ('docs/projections.html', 0): ('map', MAP_DOCPROJ0, FRED_FRAG),
    ('docs/projections.html', 1): ('map', MAP_DOCPROJ1, L(LTA25009, 'BOE LTA 2025/009')),
    ('docs/projections.html', 2): ('map', None, FRED_FRAG),
    ('docs/projections.html', 3): ('map', None, CPI_FRAG),
    ('docs/projections.html', 4): ('map', None, CPI_FRAG),
    ('docs/projections.html', 5): ('map', MAP_DOCPROJ5, FRED_FRAG),
    ('docs/projections.html', 6): ('map', MAP_DOCPROJ6, label_span('rounding convention - no source needed')),
    ('docs/sanfrancisco.html', 1): ('map', MAP_SF1, label_span('calculation from flagged rows')),
    ('docs/sources.html', 1): ('map', MAP_SOURCES1, label_span('source row - not re-read in this session')),
    ('docs/taxes.html', 0): ('map', MAP_TAXES0, L(GOV2001, 'IRC 2001(c)')),
    ('docs/taxes.html', 2): ('map', MAP_TAXES2, L(IRS_P523, 'IRS Pub 523')),

    ('site/sources.html', 0): ('map', [('', label_span('source row - not re-read in this session'))],
                               label_span('source row - not re-read in this session')),

    ('archive/root-site-2026-11-11/black-swan.html', 0): ('map', MAP_BS0, label_span('flagged - episode row')),
    ('archive/root-site-2026-11-11/black-swan.html', 1): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/costs.html', 0): ('map', MAP_ARCH_COSTS0, label_span('sum of flagged rows')),
    ('archive/root-site-2026-11-11/costs.html', 1): ('map', MAP_ARCH_COSTS1, label_span('sum of flagged rows')),
    ('archive/root-site-2026-11-11/costs.html', 2): ('map', MAP_ARCH_COSTS2, FRED_FRAG),
    ('archive/root-site-2026-11-11/costs.html', 3): ('map', MAP_ARCH_COSTS3, label_span('advice row - no official source')),
    ('archive/root-site-2026-11-11/estate-tax.html', 1): ('map', None, IRS_FRAG),
    ('archive/root-site-2026-11-11/flagged.html', 0): ('map', MAP_ARCH_FL0, label_span('flagged item - see register')),
    ('archive/root-site-2026-11-11/flagged.html', 1): ('map', MAP_ARCH_FL1, label_span('flagged item - see register')),
    ('archive/root-site-2026-11-11/index.html', 0): ('map', MAP_ARCH_IDX1, label_span('status row - points to the section')),
    ('archive/root-site-2026-11-11/index.html', 1): ('map', MAP_ARCH_IDX1, label_span('status row - points to the section')),
    ('archive/root-site-2026-11-11/methodology.html', 0): ('map', MAP_ARCH_METH0, label_span('assumption - no official source')),
    ('archive/root-site-2026-11-11/pending-changes.html', 0): ('map', MAP_ARCH_PENDING, label_span('pending-change row - see official measure page')),
    ('archive/root-site-2026-11-11/process.html', 0): ('map', MAP_ARCH_PROC0, label_span('step row - citation not re-read in this session')),
    ('archive/root-site-2026-11-11/projections.html', 0): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/projections.html', 1): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/projections.html', 2): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/properties.html', 0): ('map', MAP_ARCH_PROP0, label_span('owner figure - unverified')),
    ('archive/root-site-2026-11-11/properties.html', 1): ('map', MAP_ARCH_PROP1, label_span('owner figure - unverified')),
    ('archive/root-site-2026-11-11/properties.html', 2): ('map', MAP_ARCH_PROP2, label_span('owner history - unverified')),
    ('archive/root-site-2026-11-11/scenarios.html', 0): ('map', [
        ('Prop 19 applies', L(BOE_PROP19, 'BOE Proposition 19')),
        ('A rental income', L(HUD95014, 'HUD FY2026 rent benchmark')),
        ('', FRED_FRAG),
    ], FRED_FRAG),
    ('archive/root-site-2026-11-11/scenarios.html', 1): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/scenarios.html', 2): ('map', None, FRED_FRAG),
    ('archive/root-site-2026-11-11/sources.html', 2): ('map', MAP_ARCH_SOURCES2, L(ASR_HOME, 'SCC Assessor')),
    ('archive/root-site-2026-11-11/sources.html', 3): ('map', MAP_ARCH_SOURCES3, L(NBER, 'NBER')),
    ('archive/root-site-2026-11-11/sources.html', 4): ('map', [('', label_span('source row - not re-read in this session'))],
                                                       label_span('source row - not re-read in this session')),
    ('archive/root-site-2026-11-11/sources.html', 5): ('map', MAP_ARCH_SOURCES5, label_span('source row - not re-read in this session')),
    ('archive/root-site-2026-11-11/taxes.html', 0): ('map', MAP_ARCH_TAXES0, FRED_FRAG),
    ('archive/root-site-2026-11-11/taxes.html', 1): ('map', MAP_ARCH_TAXES1, L(IRS_TC559, 'IRS Topic 559')),
    ('archive/root-site-2026-11-11/taxes.html', 2): ('map', MAP_ARCH_TAXES2, L(IRS_P523, 'IRS Pub 523')),
}

# ------------------------------------------------------------ citation fix ----
# CR-85-1 / CR-85-2: commercial or non-official citations.
# Rule: never re-attribute a commercial figure to an official page. The anchor
# text stays (it names the real origin), the href is dropped or pointed at the
# official companion source, and the row gains the official context link.
CORNELL = 'https://www.law.cornell.edu'
CORNELL_MAP = {
    '/uscode/text/26/1014': GOV1014,
    '/uscode/text/26/2001': GOV2001,
    '/uscode/text/26/2010': IRS_WHATSNEW,   # page read today: "amends 2010(c)(3) ... $15,000,000"
    '/uscode/text/26/1411': IRS_TC559,
    '/uscode/text/26/121': IRS_P523,
    '/uscode/text/26/2503': IRS_GIFT,
    '/uscode/text/26/401': None,            # unlink only (companion official link stays in the cell)
}
UNLINK = ('policygenius.com', 'nerdwallet.com', 'zillow.com', 'rentometer.com',
          'ballotpedia.org', 'car.org', 'gethomeinsurancequotes.com')
UNLINK_NOTE = {
    'policygenius.com': (CDI_COMPARE, 'official CDI guide'),
    'nerdwallet.com': (CDI_STUDY, 'official CDI study'),
    'zillow.com': (FRED_A, 'official FHFA HPI'),
    'rentometer.com': (HUD94122, 'official HUD rent benchmark'),
    'ballotpedia.org': (SOS_BALLOT, 'official CA election returns'),
    'car.org': (FRED_A, 'official FHFA HPI'),
    'gethomeinsurancequotes.com': (CDI_COMPARE, 'official CDI guide'),
}
REPLACEMENTS = [
    # CR-07-7: note contradicted the very IRS page the row cites (read 2026-11-11:
    # "increased the user fee ... from $56 to $76, effective October 26, 2026")
    ('previously $67', 'previously $56'),
    # CR-85-2: anchor says "Rev Proc 2025-32" but pointed at an unrelated newsroom page
    ('https://www.irs.gov/newsroom/irs-releases-2025-amounts-for-retirement-plans-and-other-benefits',
     RP2532),
    # CR-85-2: 404 FTB link and unverified Fed link (research/*.md)
    ('https://www.ftb.ca.gov/file/personal/income-types/capital-gains.html',
     'https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html'),
    ('https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm',
     'https://www.cbo.gov/publication/62105'),
]


def process_file(path, stats):
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding='utf-8') as f:
        html = f.read()
    orig = html

    # ---- citation replacements (whole file) ----
    for old, new in REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            stats['repl'].append((path, old[:60], new[:60]))

    # law.cornell -> official publisher (href swap; text keeps the citation)
    def anchor_sub(m):
        href, text = m.group(1), m.group(2)
        for suffix, target in CORNELL_MAP.items():
            if suffix in href:
                if target is None:
                    stats['repl'].append((path, 'cornell ' + suffix, 'unlinked'))
                    return text
                stats['repl'].append((path, 'cornell ' + suffix, target))
                return '<a href="%s" title="%s" rel="noopener">%s</a>' % (target, target, text)
        return m.group(0)
    html = re.sub(r'<a href="(https?://www\.law\.cornell\.edu[^"]*)"[^>]*>([^<]*)</a>',
                  anchor_sub, html)

    # commercial citations: unlink + official companion link
    def commercial_sub(m):
        href, inner = m.group(1), m.group(0)
        host = re.sub(r'^https?://(www\.)?', '', href).split('/')[0]
        for dom, (off, off_text) in UNLINK_NOTE.items():
            if dom in host:
                stats['repl'].append((path, href, 'unlinked + ' + off))
                plain = re.sub(r'<[^>]+>', '', inner)
                return ('<span class="non-official" style="color:#7a5b00" title="commercial source - not official">%s</span> '
                        '&middot; %s' % (plain, L(off, off_text)))
        return inner
    html = re.sub(
        r'<a href="(https?://(?:www\.)?(?:policygenius\.com|nerdwallet\.com|zillow\.com|'
        r'rentometer\.com|ballotpedia\.org|car\.org|gethomeinsurancequotes\.com)[^"]*)"[^>]*>(.*?)</a>',
        commercial_sub, html, flags=re.S)

    # ---- row sourcing ----
    def tbody_sub(m):
        body = m.group(0)
        parts = re.split(r'(<tr>.*?</tr>)', body, flags=re.S)
        out = []
        for part in parts:
            if not part.startswith('<tr>'):
                out.append(part)
                continue
            if '<td' not in part:
                out.append(part)
                continue
            state = row_state(part)
            if state != 'work':
                out.append(part)
                continue
            # find strategy from caller-supplied table key
            key = tbody_sub.key
            mode, mp, fallback = TABLES.get(key, ('map', None, label_span('flagged - no official source re-read; see Flagged for Review')))
            frag = None
            if mp:
                plain = strip_tags(part)
                for sub, f in mp:
                    if sub == '' or sub in plain:
                        frag = f
                        break
            if frag is None:
                frag = fallback
            new_part, ok = append_last_td(part, frag)
            if ok:
                stats['rows'] += 1
                stats['by_file'][key[0]] = stats['by_file'].get(key[0], 0) + 1
                if frag == fallback and fallback.startswith('<span') and 'unverified citation' in fallback:
                    stats['flagged'].append((key[0], key[1], strip_tags(part)[:80]))
            else:
                stats['failed'].append((key[0], key[1], strip_tags(part)[:80]))
            out.append(new_part)
        return ''.join(out)

    # process tables one at a time so each tbody knows its key
    table_i = {}
    def one_tbody(m, _path=rel):
        ti = table_i.get(_path, 0)
        table_i[_path] = ti + 1
        tbody_sub.key = (_path, ti)
        return tbody_sub(m)
    html = re.sub(r'<tbody[^>]*>.*?</tbody>', one_tbody, html, flags=re.S)

    if html != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def process_text_file(path, stats):
    """Citation-only fixes for research/*.md and docs/data/*.json (CR-85-1/2)."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    orig = text
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            stats['repl'].append((path, old[:70], new[:70]))
    # law.cornell raw URLs -> official publisher
    for suffix, target in CORNELL_MAP.items():
        pat = re.compile(r'https?://www\.law\.cornell\.edu' + re.escape(suffix) + r'[\w\-/.]*')
        if target and pat.search(text):
            text = pat.sub(target, text)
            stats['repl'].append((path, 'cornell' + suffix, target))
        elif target is None and pat.search(text):
            # no official single-section page verified for this cite: keep as plain
            # text and flag it - never silently keep a non-official link.
            text = pat.sub(lambda m: m.group(0) + ' (non-official mirror; official code not re-read)',
                           text)
            stats['repl'].append((path, 'cornell' + suffix, 'flagged non-official mirror'))
    # commercial / advocacy raw URLs -> official context, origin kept visible
    for dom, (off, off_text) in UNLINK_NOTE.items():
        pat = re.compile(r'https?://(?:www\.)?' + re.escape(dom) + r'[\w\-/.]*')
        if pat.search(text):
            text = pat.sub(lambda m: '%s (commercial estimate - non-official; official context %s: %s)'
                           % (m.group(0), off_text, off), text)
            stats['repl'].append((path, dom, 'flagged + ' + off))
    hjta = re.compile(r'https?://(?:www\.)?hjta\.org[\w\-/.]*')
    if hjta.search(text):
        text = hjta.sub(lambda m: '%s (advocacy site - non-official; official context: %s)'
                        % (m.group(0), 'https://www.boe.ca.gov/prop13/'), text)
        stats['repl'].append((path, 'hjta.org', 'flagged + BOE prop13'))
    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    return False


def main():
    stats = {'rows': 0, 'by_file': {}, 'repl': [], 'flagged': [], 'failed': []}
    trees = ['dashboard', 'docs', 'site', 'archive/root-site-2026-11-11']
    files = []
    for t in trees:
        for root, _, fnames in os.walk(os.path.join(ROOT, t)):
            for fn in fnames:
                if fn.endswith('.html'):
                    files.append(os.path.relpath(os.path.join(root, fn), ROOT))
    changed = 0
    for rel in sorted(files):
        if process_file(os.path.join(ROOT, rel), stats):
            changed += 1
    # citation-only pass for research notes and data files
    for folder in ('research', 'docs/data'):
        for root, _, fnames in os.walk(os.path.join(ROOT, folder)):
            for fn in sorted(fnames):
                if fn.endswith(('.md', '.json')):
                    rel = os.path.relpath(os.path.join(root, fn), ROOT)
                    if process_text_file(os.path.join(ROOT, rel), stats):
                        changed += 1
    print('files changed: %d' % changed)
    print('rows given a source link or label: %d' % stats['rows'])
    for k, v in sorted(stats['by_file'].items()):
        print('   %3d  %s' % (v, k))
    print('citation replacements: %d' % len(stats['repl']))
    for r in stats['repl']:
        print('   %s: %s -> %s' % r)
    print('rows flagged without a matched source: %d' % len(stats['flagged']))
    for r in stats['flagged']:
        print('   %s T%s: %s' % r)
    print('rows failed to edit: %d' % len(stats['failed']))
    for r in stats['failed']:
        print('   %s T%s: %s' % r)


if __name__ == '__main__':
    main()
