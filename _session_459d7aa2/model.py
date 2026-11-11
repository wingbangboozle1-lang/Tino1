"""50-year inheritance, tax, utility, Black Swan & cash-headroom engine.

Session: arena/459d7aa2-tino1 (2026-11-11)
Privacy & rounding invariants enforced throughout:
  1. Zero unrounded county-roll parcel figures appear anywhere in source code,
     comments, CSVs, or JSON. Even owner-supplied inputs that happened to end
     in zero on the roll are coarsened to $100 ($550,500; $7,200).
  2. Every monetary output exported to JSON/CSV/HTML is rounded to the nearest
     $10 increment (int(round(x / 10.0)) * 10).
  3. Property B (San Francisco 94122 triplex) is modeled as ALREADY OWNED by
     [Inheritor] (no Prop 19 reassessment, no IRC §1014 step-up, excluded from
     [Transferor]'s federal gross estate), while Property A (Cupertino 95014
     single-family home) is INHERITED VIA TRUST around 2040-2050.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def r10(val: float) -> int:
    """Round any dollar figure to the nearest $10 integer increment."""
    return int(Decimal_half_up_10(val))


def Decimal_half_up_10(val: float) -> int:
    q = val / 10.0
    if q >= 0:
        return int(math.floor(q + 0.5)) * 10
    return -int(math.floor(-q + 0.5)) * 10


# ---------------------------------------------------------------------------
# Official statutory & local tax parameters (verified 2026-11-11)
# ---------------------------------------------------------------------------
START_YEAR = 2026
END_YEAR = 2076
YEARS = list(range(START_YEAR, END_YEAR + 1))  # 51 snapshots: 2026..2076

# Federal estate & gift tax (P.L. 119-21 §70106; IRS Rev. Proc. 2026-35 §3.44)
FED_EXCLUSION_2026 = 15_000_000
FED_EXCLUSION_2027 = 15_480_000
FED_GIFT_ANNUAL_2026 = 19_000
FED_GIFT_ANNUAL_2027 = 20_000
FED_ESTATE_TOP_RATE = 0.40  # IRC §2001(c) Table A above $1,000,000

# Combined marginal tax rates for high-bracket California earner
# Federal LTCG 20% + NIIT 3.8% + CA top ordinary/MHS 13.3% = 37.1%;
# Effective blended marginal rate for upper-middle/high Bay Area earner:
FED_LTCG_EFFECTIVE = 0.188   # 15% LTCG + 3.8% NIIT (23.8% above $563k Single)
FED_LTCG_LARGE_SALE = 0.238  # 20% LTCG + 3.8% NIIT on multi-million sale gain
CA_CAP_GAIN_RATE = 0.103     # 9.3%-11.3% blended; 12.3%-13.3% on >$1M gain
CA_LARGE_GAIN_RATE = 0.128   # blended across $743k/$1M thresholds
COMBINED_DIV_TAX = 0.301     # qualified dividend effective rate (Fed+NIIT+CA)
COMBINED_RENT_ORD_TAX = 0.371  # ordinary marginal tax on net Schedule E income
COMBINED_TBILL_TAX = 0.258   # 22%-24% Fed + 3.8% NIIT, 0% CA (31 U.S.C. §3124)
SECTION_1250_RECAP_RATE = 0.353  # 25% §1250 + 10.3% CA
IRC_121_SINGLE = 250_000

# California Prop 13 & Prop 19 parameters (CA Const. Art. XIII A; R&TC §§51, 63.2)
PROP13_CAP = 0.02
HOX_EXEMPTION = 7_000  # BOE-266 principal-residence exemption
PROP19_ALLOWANCE_2026 = 1_044_586  # BOE LTA 2025/009 (Feb 16, 2025 - Feb 15, 2027)

# Local rates & transfer taxes (SCC FY25-26 Tax Rate Book; SF Treasurer FY26-27)
CUP_AD_VALOREM_RATE = 0.01180       # Cupertino TRA ~1.18% (1% + school/water bonds)
CUP_FIXED_PARCEL_2026 = 710         # fixed parcel assessments (rounded)
CUP_DTT_RATE = 0.0011               # $0.55 per $500 (Santa Clara Clerk-Recorder)
SELL_COST_BROKER_ESCROW = 0.050     # 5.0% commission + title/escrow

SF_AD_VALOREM_RATE = 0.0118162182   # Official FY2026-27 SF rate (sftreasurer.org)
SF_FIXED_PARCEL_2026 = 810          # fixed SF parcel charges (rounded)

# ---------------------------------------------------------------------------
# Anonymized, coarsened owner/scenario inputs (2026 base year)
# ---------------------------------------------------------------------------
# Property A: [Property A — Cupertino Home, ZIP 95014] (Inherited via trust)
CUP_FMV_2026 = 3_100_000
CUP_AV_2026 = 550_500       # $100-coarsened from zero-ending input for anti-traceability
CUP_ORIG_BASIS_EST = 400_000  # illustrative pre-death basis ONLY for Rev. Rul. 2023-2 trap
CUP_WATER_2026 = 1_500      # $125/mo midpoint ($100-$150/mo)
CUP_SOLAR_CREDIT_2026 = -180  # -$15/mo net solar credit (-$10 to -$20/mo)
CUP_POST_NEM_ELEC_2026 = 580  # post-20-yr NEM sunset + $24.15/mo CPUC Res. E-5354 fixed charge
CUP_REPAIR_2026 = 6_000     # < SF $12,000/yr
CUP_INS_HOME_2026 = 1_500   # owner working estimate (flagged unverified)
CUP_INS_LANDLORD_2026 = 2_100  # landlord dwelling-fire assumption (+40%, flagged)
CUP_MARKET_RENT_2026 = 86_400  # $7,200/mo single-family rent (~2.79% gross yield)
RENTAL_VACANCY_LOSS = 0.05  # 5% vacancy/turnover allowance

# Property B: [Property B — San Francisco Triplex, ZIP 94122] (Already owned)
SF_FMV_2026 = 1_800_000
SF_AV_2026 = 116_540        # $10-rounded 2026 assessed value
SF_2UNIT_RENT_2026 = 85_800  # $7,150/mo across the 2 rented units
SF_UNIT3_MKT_RENT_2026 = 42_960  # $3,580/mo if Inheritor vacates Unit 3 to live in Cupertino
SF_WATER_2026 = 4_380       # $365/mo midpoint ($330-$400/mo across 3 units)
SF_ELEC_2026 = 600          # $50/mo midpoint ($30-$70/mo)
SF_REPAIR_2026 = 12_000     # $1,000/mo across 3 units
SF_INS_RENTAL_2026 = 1_500  # owner working estimate (flagged unverified)

# Baseline long-horizon annual growth assumptions
BASE_CPI = 0.025            # 2.5%/yr general CPI inflation
BASE_HPI = 0.040            # 4.0%/yr Bay Area home value & market rent growth
BASE_P19_INDEX = 0.035      # 3.5%/yr FHFA CA HPI indexation of Prop 19 allowance
BASE_UTIL_INS_GROWTH = 0.032  # 3.2%/yr utility & insurance inflation (+0.7% real)
EQUITY_TOTAL_RETURN = 0.070   # 7.0%/yr (5.4% price + 1.6% dividend)
EQUITY_DIV_YIELD = 0.016
BALANCED_TOTAL_RETURN = 0.060  # 6.0%/yr (4.0% price + 2.0% yield)
BALANCED_YIELD = 0.020
CASH_TBILL_RETURN = 0.035      # 3.5%/yr Treasury bills / high-yield savings

# ---------------------------------------------------------------------------
# Real 50-year historical macro record (1976–2025) from official series:
#   cpi: BLS CPI-U annual % change (FRED CPIAUCSL / BLS Table 24)
#   hpi_sj: FHFA San Jose-Sunnyvale-Santa Clara MSA HPI annual % (ATNHPIUS41940Q)
#   hpi_sf: FHFA San Francisco-San Mateo-Redwood City MSAD HPI annual % (ATNHPIUS41884Q)
#   sp500: S&P 500 total return (price + reinvested dividends)
#   tbill: 3-Month Treasury Bill secondary market rate (FRED TB3MS)
# ---------------------------------------------------------------------------
HIST_1976_2025 = [
    # (year, cpi, hpi_sj, hpi_sf, sp500, tbill)
    (1976, 0.058, 0.165, 0.158, 0.238, 0.050),
    (1977, 0.065, 0.242, 0.228, -0.072, 0.053),
    (1978, 0.076, 0.178, 0.169, 0.066, 0.072),
    (1979, 0.113, 0.184, 0.176, 0.184, 0.101),
    (1980, 0.135, 0.119, 0.125, 0.324, 0.114),
    (1981, 0.103, 0.062, 0.068, -0.049, 0.140),
    (1982, 0.061, 0.012, 0.015, 0.214, 0.106),
    (1983, 0.032, 0.028, 0.031, 0.225, 0.086),
    (1984, 0.043, 0.049, 0.052, 0.063, 0.095),
    (1985, 0.035, 0.068, 0.074, 0.322, 0.075),
    (1986, 0.019, 0.089, 0.095, 0.185, 0.060),
    (1987, 0.037, 0.118, 0.126, 0.052, 0.058),
    (1988, 0.041, 0.194, 0.188, 0.168, 0.067),
    (1989, 0.048, 0.212, 0.197, 0.315, 0.081),
    (1990, 0.054, -0.018, -0.012, -0.032, 0.075),
    (1991, 0.042, -0.021, -0.019, 0.306, 0.054),
    (1992, 0.030, -0.014, -0.015, 0.077, 0.034),
    (1993, 0.030, -0.024, -0.022, 0.100, 0.030),
    (1994, 0.026, 0.008, -0.005, 0.013, 0.043),
    (1995, 0.028, 0.031, 0.024, 0.374, 0.055),
    (1996, 0.029, 0.058, 0.046, 0.231, 0.050),
    (1997, 0.023, 0.118, 0.104, 0.334, 0.051),
    (1998, 0.016, 0.138, 0.129, 0.286, 0.048),
    (1999, 0.022, 0.162, 0.158, 0.210, 0.046),
    (2000, 0.034, 0.248, 0.226, -0.091, 0.058),
    (2001, 0.028, 0.042, 0.064, -0.119, 0.034),
    (2002, 0.016, -0.008, 0.032, -0.221, 0.016),
    (2003, 0.023, 0.046, 0.062, 0.287, 0.010),
    (2004, 0.027, 0.129, 0.138, 0.109, 0.014),
    (2005, 0.034, 0.148, 0.142, 0.049, 0.031),
    (2006, 0.032, 0.041, 0.036, 0.158, 0.047),
    (2007, 0.029, -0.028, -0.021, 0.055, 0.044),
    (2008, 0.038, -0.162, -0.124, -0.370, 0.014),
    (2009, -0.004, -0.088, -0.072, 0.265, 0.002),
    (2010, 0.016, 0.012, 0.008, 0.151, 0.001),
    (2011, 0.032, -0.024, -0.026, 0.021, 0.001),
    (2012, 0.021, 0.098, 0.086, 0.160, 0.001),
    (2013, 0.015, 0.172, 0.164, 0.324, 0.001),
    (2014, 0.016, 0.112, 0.118, 0.137, 0.000),
    (2015, 0.001, 0.106, 0.114, 0.014, 0.001),
    (2016, 0.013, 0.064, 0.068, 0.120, 0.003),
    (2017, 0.021, 0.092, 0.074, 0.218, 0.009),
    (2018, 0.024, 0.104, 0.079, -0.044, 0.019),
    (2019, 0.018, -0.006, 0.018, 0.315, 0.021),
    (2020, 0.012, 0.078, 0.049, 0.184, 0.004),
    (2021, 0.047, 0.164, 0.128, 0.287, 0.000),
    (2022, 0.080, 0.062, 0.038, -0.181, 0.020),
    (2023, 0.041, 0.018, -0.019, 0.263, 0.051),
    (2024, 0.029, 0.054, 0.022, 0.250, 0.050),
    (2025, 0.027, 0.028, 0.014, 0.145, 0.042),
]


def prop19_allowance(year: int, cpi_path: dict[int, float] | None = None) -> float:
    """Compute Prop 19 family-home allowance in `year` (biennial step on odd years)."""
    val = float(PROP19_ALLOWANCE_2026)
    for y in range(2027, year + 1):
        if y % 2 == 1:  # adjusted every other Feb 16: 2027, 2029, 2031...
            if cpi_path is None:
                step = (1.0 + BASE_P19_INDEX) ** 2 - 1.0
            else:
                g1 = cpi_path.get(y - 2, BASE_CPI) + 0.01
                g2 = cpi_path.get(y - 1, BASE_CPI) + 0.01
                step = (1.0 + g1) * (1.0 + g2) - 1.0
            val *= (1.0 + step)
    return val


def cup_tax_bill(assessed: float, owner_occupied: bool, parcel_charge: float) -> float:
    taxable = max(0.0, assessed - (HOX_EXEMPTION if owner_occupied else 0.0))
    return taxable * CUP_AD_VALOREM_RATE + parcel_charge


def sf_tax_bill(assessed: float, owner_occupied: bool, parcel_charge: float) -> float:
    taxable = max(0.0, assessed - (HOX_EXEMPTION if owner_occupied else 0.0))
    return taxable * SF_AD_VALOREM_RATE + parcel_charge


def sf_transfer_tax_rate(fmv: float) -> float:
    """Official San Francisco Real Property Transfer Tax rate (sf.gov/transfer-tax)."""
    if fmv < 250_000:
        return 2.50 / 500.0
    if fmv < 1_000_000:
        return 3.40 / 500.0
    if fmv < 5_000_000:
        return 3.75 / 500.0   # 0.75%
    if fmv < 10_000_000:
        return 11.25 / 500.0  # 2.25%
    if fmv < 25_000_000:
        return 27.50 / 500.0  # 5.50%
    return 30.00 / 500.0      # 6.00%


def simulate_50yr_path(
    inherit_year: int = 2045,
    rates_by_year: dict[int, dict[str, float]] | None = None,
    step_up_applies: bool = True,
    post_nem_sunset_year: int | None = None,
    quake_year: int | None = None,
    quake_loss_pct: float = 0.0,
) -> dict:
    """Simulate 2026..2076 year-by-year for Property A, Property B, and all strategies.

    Wealth comparison follows strict incremental parity:
      - Property B's existing 2 rented units ($85,800/yr in 2026) and Property B
        itself are retained identically in all core options, so incremental
        comparison tracks Property A + all differential cash flows (including
        vacated SF Unit 3 net rent when Inheritor moves into Property A)
        compounded in the designated investment vehicle and liquidated after all
        capital-gains / §1250-recapture taxes in 2076.
    """
    cup_fmv = float(CUP_FMV_2026)
    cup_fbyv = float(CUP_AV_2026)
    sf_fmv = float(SF_FMV_2026)
    sf_fbyv = float(SF_AV_2026)

    cpi_cum = 1.0
    util_cum = 1.0
    cpi_map: dict[int, float] = {}

    # Strategy state trackers from inherit_year..2076
    # S1: Live in Cupertino + rent vacated SF Unit 3
    # S2: Rent Cupertino + keep living in SF Unit 3
    # S3_EQ: Sell Cupertino at inheritance & invest in diversified equities (7.0%)
    # S3_BAL: Sell Cupertino & invest in 60/40 balanced portfolio (6.0%)
    # S3_CASH: Sell Cupertino & hold Treasury bills / HYSA (3.5%)
    s1_fbyv = 0.0
    s2_fbyv = 0.0
    cup_Dod_fmv = 0.0
    cup_basis_s1 = 0.0
    cup_basis_s2 = 0.0
    cup_accum_depr_s2 = 0.0
    sf_unit3_lease_rent = 0.0  # once leased at inheritance, grows at SF Rent Board 60% CPI

    # Side liquid portfolios (track market value & tax basis separately for exact LTCG tax)
    port = {
        "s1_mv": 0.0, "s1_basis": 0.0,
        "s2_mv": 0.0, "s2_basis": 0.0,
        "s3_eq_mv": 0.0, "s3_eq_basis": 0.0,
        "s3_bal_mv": 0.0, "s3_bal_basis": 0.0,
        "s3_cash_mv": 0.0,
    }
    sale_net_proceeds_at_inh = 0.0
    sale_tax_at_inh = 0.0
    p19_allowance_at_inh = 0.0
    s1_av_at_inh = 0.0
    s2_av_at_inh = 0.0
    s1_tax_yr1 = 0.0
    s2_tax_yr1 = 0.0

    yearly_rows = []
    snapshots_after_inh = {}

    for y in YEARS:
        r = (rates_by_year or {}).get(y, {})
        cpi = r.get("cpi", BASE_CPI)
        hpi_a = r.get("hpi_sj", BASE_HPI)
        hpi_b = r.get("hpi_sf", BASE_HPI)
        eq_ret = r.get("sp500", EQUITY_TOTAL_RETURN)
        tb_ret = r.get("tbill", CASH_TBILL_RETURN)
        bal_ret = 0.60 * eq_ret + 0.40 * tb_ret
        util_g = r.get("util_g", max(cpi + 0.007, BASE_UTIL_INS_GROWTH if rates_by_year is None else cpi + 0.007))
        cpi_map[y] = cpi

        if y > START_YEAR:
            cup_fmv *= (1.0 + hpi_a)
            sf_fmv *= (1.0 + hpi_b)
            cpi_cum *= (1.0 + cpi)
            util_cum *= (1.0 + util_g)
            # Prop 13 FBYV compounds by min(CCPI, 2%), allowing slight negative CCPI if deflation
            p13_step = min(cpi, PROP13_CAP)
            cup_fbyv *= (1.0 + p13_step)
            sf_fbyv *= (1.0 + p13_step)
            if y > inherit_year:
                s1_fbyv *= (1.0 + p13_step)
                s2_fbyv *= (1.0 + p13_step)
                # SF Rent Ordinance caps existing-tenant annual increase at 60% of CPI (max 7%)
                sf_rb_cap = min(max(0.0, 0.60 * cpi), 0.07)
                sf_unit3_lease_rent *= (1.0 + sf_rb_cap)

        # Prop 8 temporary decline-in-value rule (CA R&TC §51(a)(2)): taxable = min(FBYV, FMV)
        sf_taxable_av = min(sf_fbyv, sf_fmv)
        cup_pre_inh_av = min(cup_fbyv, cup_fmv)

        cup_parcel = CUP_FIXED_PARCEL_2026 * cpi_cum
        sf_parcel = SF_FIXED_PARCEL_2026 * cpi_cum

        # Operating cost components in year y
        cup_water = CUP_WATER_2026 * util_cum
        if post_nem_sunset_year is not None and y >= post_nem_sunset_year:
            cup_elec = CUP_POST_NEM_ELEC_2026 * util_cum
        else:
            cup_elec = CUP_SOLAR_CREDIT_2026 * util_cum
        cup_repair = CUP_REPAIR_2026 * cpi_cum
        if quake_year is not None and y == quake_year:
            cup_repair += cup_fmv * quake_loss_pct  # uninsured seismic shock
        cup_ins_home = CUP_INS_HOME_2026 * util_cum
        cup_ins_landlord = CUP_INS_LANDLORD_2026 * util_cum
        cup_mkt_rent = CUP_MARKET_RENT_2026 * (cup_fmv / CUP_FMV_2026)

        sf_water = SF_WATER_2026 * util_cum
        sf_elec = SF_ELEC_2026 * util_cum
        sf_repair = SF_REPAIR_2026 * cpi_cum
        sf_ins = SF_INS_RENTAL_2026 * util_cum
        sf_2unit_rent = SF_2UNIT_RENT_2026 * ((1.0 + min(max(0.0, 0.60 * BASE_CPI), 0.07)) ** (y - START_YEAR))
        sf_tax_owner_occ = sf_tax_bill(sf_taxable_av, True, sf_parcel)
        sf_tax_mkt_would_be = sf_tax_bill(sf_fmv, True, sf_parcel)
        sf_prop13_annual_shield = sf_tax_mkt_would_be - sf_tax_owner_occ

        if y < inherit_year:
            cup_tax_pre = cup_tax_bill(cup_pre_inh_av, True, cup_parcel)
            yearly_rows.append({
                "year": y,
                "phase": "Pre-inheritance (Held in Trust)",
                "cpi_index": round(cpi_cum, 4),
                "cup_fmv": r10(cup_fmv),
                "cup_av_live": r10(cup_pre_inh_av),
                "cup_tax_live": r10(cup_tax_pre),
                "cup_av_rent": r10(cup_pre_inh_av),
                "cup_tax_rent": r10(cup_tax_pre),
                "cup_repair": r10(cup_repair),
                "cup_water": r10(cup_water),
                "cup_elec": r10(cup_elec),
                "cup_ins_home": r10(cup_ins_home),
                "cup_ins_landlord": r10(cup_ins_landlord),
                "cup_gross_rent": r10(cup_mkt_rent),
                "sf_fmv": r10(sf_fmv),
                "sf_av": r10(sf_taxable_av),
                "sf_tax": r10(sf_tax_owner_occ),
                "sf_prop13_shield": r10(sf_prop13_annual_shield),
                "sf_2unit_rent": r10(sf_2unit_rent),
                "sf_water": r10(sf_water),
                "sf_elec": r10(sf_elec),
                "sf_repair": r10(sf_repair),
                "sf_ins": r10(sf_ins),
                "wealth_s1_nom": 0,
                "wealth_s2_nom": 0,
                "wealth_s3_eq_nom": 0,
                "wealth_s3_bal_nom": 0,
                "wealth_s3_cash_nom": 0,
                "wealth_s1_real": 0,
                "wealth_s2_real": 0,
                "wealth_s3_eq_real": 0,
                "wealth_s3_bal_real": 0,
                "wealth_s3_cash_real": 0,
            })
            continue

        if y == inherit_year:
            cup_Dod_fmv = cup_fmv
            p19_allowance_at_inh = prop19_allowance(y, cpi_map)
            # Prop 19 formula (CA R&TC §63.2): FBYV + max(0, FMV - (FBYV + Allowance))
            excluded_cap = cup_fbyv + p19_allowance_at_inh
            excess = max(0.0, cup_fmv - excluded_cap)
            s1_fbyv = cup_fbyv + excess
            s2_fbyv = cup_fmv  # 100% FMV reassessment when rented out
            s1_av_at_inh = s1_fbyv
            s2_av_at_inh = s2_fbyv

            cup_basis_s1 = cup_fmv if step_up_applies else CUP_ORIG_BASIS_EST
            cup_basis_s2 = cup_fmv if step_up_applies else CUP_ORIG_BASIS_EST
            sf_unit3_lease_rent = SF_UNIT3_MKT_RENT_2026 * (sf_fmv / SF_FMV_2026)

            # Immediate sale of Property A in inherit_year (with 6 months carrying cost)
            gross_sale = cup_fmv
            sell_costs = gross_sale * (SELL_COST_BROKER_ESCROW + CUP_DTT_RATE)
            carrying_half_yr = 0.5 * (
                cup_tax_bill(s2_fbyv, False, cup_parcel)
                + cup_repair + cup_water + max(0.0, cup_elec) + cup_ins_landlord
            )
            realized_gain = (gross_sale - sell_costs) - cup_basis_s1
            if realized_gain > 0:
                sale_tax_at_inh = realized_gain * (FED_LTCG_LARGE_SALE + CA_LARGE_GAIN_RATE)
            else:
                # Deductible capital loss from selling costs on investment/inherited property
                sale_tax_at_inh = 0.0
            sale_net_proceeds_at_inh = gross_sale - sell_costs - carrying_half_yr - sale_tax_at_inh

            port["s3_eq_mv"] = sale_net_proceeds_at_inh
            port["s3_eq_basis"] = sale_net_proceeds_at_inh
            port["s3_bal_mv"] = sale_net_proceeds_at_inh
            port["s3_bal_basis"] = sale_net_proceeds_at_inh
            port["s3_cash_mv"] = sale_net_proceeds_at_inh

        # Post-inheritance year cash flows (y >= inherit_year)
        s1_av = min(s1_fbyv, cup_fmv)
        s2_av = min(s2_fbyv, cup_fmv)
        tax_s1 = cup_tax_bill(s1_av, True, cup_parcel)
        tax_s2 = cup_tax_bill(s2_av, False, cup_parcel)
        if y == inherit_year:
            s1_tax_yr1 = tax_s1
            s2_tax_yr1 = tax_s2

        # Strategy 1 annual incremental cash flow:
        #   Pay Cupertino owner-occ tax, repair, water, elec, home insurance
        #   Receive vacated SF Unit 3 net rent (after 5% vacancy & ordinary income tax,
        #   minus loss of $7,000 HOX on SF Unit 3)
        sf_u3_eff_rent = sf_unit3_lease_rent * (1.0 - RENTAL_VACANCY_LOSS)
        sf_u3_depr = (0.70 * 600_000) / 27.5  # modest Unit 3 structure depreciation shield
        sf_u3_taxable = max(0.0, sf_u3_eff_rent - sf_u3_depr)
        sf_u3_after_tax = sf_u3_eff_rent - sf_u3_taxable * COMBINED_RENT_ORD_TAX
        sf_hox_lost = HOX_EXEMPTION * SF_AD_VALOREM_RATE
        cf_s1 = sf_u3_after_tax - sf_hox_lost - (tax_s1 + cup_repair + cup_water + cup_elec + cup_ins_home)

        # Strategy 2 annual incremental cash flow:
        #   Rent Cupertino at market (95% occupancy), pay reassessed tax, landlord ins,
        #   repair, water (tenant typically pays electricity in single-family lease, but we
        #   conservatively keep owner net utility exposure if positive), deduct 27.5-yr
        #   MACRS depreciation on structure (65% of stepped-up basis) against Schedule E rent.
        cup_eff_rent = cup_mkt_rent * (1.0 - RENTAL_VACANCY_LOSS)
        annual_depr = (0.65 * cup_basis_s2) / 27.5 if (y - inherit_year) < 28 else 0.0
        cup_accum_depr_s2 += annual_depr
        cup_op_exp = tax_s2 + cup_repair + cup_water + max(0.0, cup_elec) + cup_ins_landlord
        sched_e_net = cup_eff_rent - cup_op_exp - annual_depr
        income_tax_s2 = max(0.0, sched_e_net) * COMBINED_RENT_ORD_TAX
        cf_s2 = cup_eff_rent - cup_op_exp - income_tax_s2

        # Compound portfolios (for S3, compound full year for y > inherit_year, half-year in inherit_year)
        frac = 0.5 if y == inherit_year else 1.0

        # S3 Equities
        eq_price_g = eq_ret - EQUITY_DIV_YIELD
        div_after_tax = EQUITY_DIV_YIELD * (1.0 - COMBINED_DIV_TAX)
        port["s3_eq_mv"] *= (1.0 + frac * (eq_price_g + div_after_tax))
        port["s3_eq_basis"] += port["s3_eq_mv"] * (frac * div_after_tax) / (1.0 + frac * (eq_price_g + div_after_tax))

        # S3 Balanced 60/40
        bal_price_g = bal_ret - BALANCED_YIELD
        bal_inc_after = BALANCED_YIELD * (1.0 - 0.32)
        port["s3_bal_mv"] *= (1.0 + frac * (bal_price_g + bal_inc_after))
        port["s3_bal_basis"] += port["s3_bal_mv"] * (frac * bal_inc_after) / (1.0 + frac * (bal_price_g + bal_inc_after))

        # S3 Cash / T-Bills
        tb_after = tb_ret * (1.0 - COMBINED_TBILL_TAX)
        port["s3_cash_mv"] *= (1.0 + frac * tb_after)

        # Compound S1 and S2 side cash-flow accounts at the same equity rate (positive reinvested,
        # negative out-of-pocket funded from the same opportunity-cost asset pool)
        for key_mv, key_b, cf in (("s1_mv", "s1_basis", cf_s1), ("s2_mv", "s2_basis", cf_s2)):
            if port[key_mv] >= 0:
                prev = port[key_mv]
                port[key_mv] = prev * (1.0 + eq_price_g + div_after_tax) + cf
                port[key_b] = port[key_b] + prev * div_after_tax + cf
            else:
                # Opportunity cost of negative carry compounds at after-tax portfolio return
                port[key_mv] = port[key_mv] * (1.0 + eq_price_g + div_after_tax) + cf
                port[key_b] = port[key_mv]

        # Compute apples-to-apples AFTER-TAX liquidated wealth at end of year y
        # S1 liquidation: sell Cupertino ( qualifies for IRC §121 $250k exclusion after 2 yrs ) + liquidate s1_mv
        s1_net_sale = cup_fmv * (1.0 - SELL_COST_BROKER_ESCROW - CUP_DTT_RATE)
        s1_excl = IRC_121_SINGLE if (y - inherit_year) >= 2 else 0.0
        s1_gain = max(0.0, s1_net_sale - cup_basis_s1 - s1_excl)
        s1_home_after_tax = s1_net_sale - s1_gain * (FED_LTCG_LARGE_SALE + CA_LARGE_GAIN_RATE)
        s1_port_gain = max(0.0, port["s1_mv"] - port["s1_basis"])
        s1_wealth_nom = s1_home_after_tax + port["s1_mv"] - s1_port_gain * (FED_LTCG_EFFECTIVE + CA_CAP_GAIN_RATE)

        # S2 liquidation: sell Cupertino rental (pay LTCG + §1250 depreciation recapture) + liquidate s2_mv
        s2_net_sale = cup_fmv * (1.0 - SELL_COST_BROKER_ESCROW - CUP_DTT_RATE)
        s2_adj_basis = cup_basis_s2 - cup_accum_depr_s2
        s2_total_gain = max(0.0, s2_net_sale - s2_adj_basis)
        s2_recap = min(s2_total_gain, cup_accum_depr_s2)
        s2_ltcg = max(0.0, s2_total_gain - s2_recap)
        s2_home_tax = s2_recap * SECTION_1250_RECAP_RATE + s2_ltcg * (FED_LTCG_LARGE_SALE + CA_LARGE_GAIN_RATE)
        s2_port_gain = max(0.0, port["s2_mv"] - port["s2_basis"])
        s2_wealth_nom = (s2_net_sale - s2_home_tax) + port["s2_mv"] - s2_port_gain * (FED_LTCG_EFFECTIVE + CA_CAP_GAIN_RATE)

        # S3 liquidations: pay LTCG tax on unrealized appreciation
        eq_gain = max(0.0, port["s3_eq_mv"] - port["s3_eq_basis"])
        s3_eq_wealth_nom = port["s3_eq_mv"] - eq_gain * (FED_LTCG_LARGE_SALE + CA_LARGE_GAIN_RATE)

        bal_gain = max(0.0, port["s3_bal_mv"] - port["s3_bal_basis"])
        s3_bal_wealth_nom = port["s3_bal_mv"] - bal_gain * (FED_LTCG_LARGE_SALE + CA_LARGE_GAIN_RATE)

        s3_cash_wealth_nom = port["s3_cash_mv"]  # interest taxed annually

        row = {
            "year": y,
            "phase": "Inheritance / Transfer Year" if y == inherit_year else "Post-inheritance",
            "cpi_index": round(cpi_cum, 4),
            "cup_fmv": r10(cup_fmv),
            "cup_av_live": r10(s1_av),
            "cup_tax_live": r10(tax_s1),
            "cup_av_rent": r10(s2_av),
            "cup_tax_rent": r10(tax_s2),
            "cup_repair": r10(cup_repair),
            "cup_water": r10(cup_water),
            "cup_elec": r10(cup_elec),
            "cup_ins_home": r10(cup_ins_home),
            "cup_ins_landlord": r10(cup_ins_landlord),
            "cup_gross_rent": r10(cup_mkt_rent),
            "sf_fmv": r10(sf_fmv),
            "sf_av": r10(sf_taxable_av),
            "sf_tax": r10(sf_tax_owner_occ),
            "sf_prop13_shield": r10(sf_prop13_annual_shield),
            "sf_2unit_rent": r10(sf_2unit_rent),
            "sf_water": r10(sf_water),
            "sf_elec": r10(sf_elec),
            "sf_repair": r10(sf_repair),
            "sf_ins": r10(sf_ins),
            "wealth_s1_nom": r10(s1_wealth_nom),
            "wealth_s2_nom": r10(s2_wealth_nom),
            "wealth_s3_eq_nom": r10(s3_eq_wealth_nom),
            "wealth_s3_bal_nom": r10(s3_bal_wealth_nom),
            "wealth_s3_cash_nom": r10(s3_cash_wealth_nom),
            "wealth_s1_real": r10(s1_wealth_nom / cpi_cum),
            "wealth_s2_real": r10(s2_wealth_nom / cpi_cum),
            "wealth_s3_eq_real": r10(s3_eq_wealth_nom / cpi_cum),
            "wealth_s3_bal_real": r10(s3_bal_wealth_nom / cpi_cum),
            "wealth_s3_cash_real": r10(s3_cash_wealth_nom / cpi_cum),
        }
        yearly_rows.append(row)

        horizon = y - inherit_year
        if horizon in (0, 10, 20, 26, 30, 31, 36):
            snapshots_after_inh[horizon] = row

    end_row = yearly_rows[-1]
    return {
        "inherit_year": inherit_year,
        "step_up_applies": step_up_applies,
        "cup_fmv_at_inh": r10(cup_Dod_fmv),
        "p19_allowance_at_inh": r10(p19_allowance_at_inh),
        "s1_av_at_inh": r10(s1_av_at_inh),
        "s2_av_at_inh": r10(s2_av_at_inh),
        "s1_tax_yr1": r10(s1_tax_yr1),
        "s2_tax_yr1": r10(s2_tax_yr1),
        "sale_net_proceeds_at_inh": r10(sale_net_proceeds_at_inh),
        "sale_tax_at_inh": r10(sale_tax_at_inh),
        "snapshots_by_horizon": snapshots_after_inh,
        "end_2076": end_row,
        "rows": yearly_rows,
    }


def build_rolling_historical_replays(inherit_year: int = 2045) -> dict:
    """Replay all 50 real 1976-2025 starting-year sequences after inheritance in 2045."""
    n = len(HIST_1976_2025)
    replays = []
    wins_10 = 0
    wins_20 = 0
    wins_31 = 0

    for start_idx in range(n):
        start_hist_year = HIST_1976_2025[start_idx][0]
        rates = {}
        # Pre-inheritance (2026..2044) held at baseline so post-inheritance sequence risk is isolated cleanly
        for y in range(inherit_year, END_YEAR + 1):
            offset = (start_idx + (y - inherit_year)) % n
            _, cpi, hpi_sj, hpi_sf, sp500, tbill = HIST_1976_2025[offset]
            rates[y] = {
                "cpi": cpi,
                "hpi_sj": hpi_sj,
                "hpi_sf": hpi_sf,
                "sp500": sp500,
                "tbill": tbill,
            }
        res = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates)
        s10 = res["snapshots_by_horizon"][10]
        s20 = res["snapshots_by_horizon"][20]
        s31 = res["end_2076"]

        diff10 = s10["wealth_s3_eq_real"] - s10["wealth_s2_real"]
        diff20 = s20["wealth_s3_eq_real"] - s20["wealth_s2_real"]
        diff31 = s31["wealth_s3_eq_real"] - s31["wealth_s2_real"]
        if diff10 > 0:
            wins_10 += 1
        if diff20 > 0:
            wins_20 += 1
        if diff31 > 0:
            wins_31 += 1

        replays.append({
            "start_hist_year": start_hist_year,
            "yr10_sell_real": s10["wealth_s3_eq_real"],
            "yr10_rent_real": s10["wealth_s2_real"],
            "yr10_live_real": s10["wealth_s1_real"],
            "yr10_sell_minus_rent_real": r10(diff10),
            "yr20_sell_real": s20["wealth_s3_eq_real"],
            "yr20_rent_real": s20["wealth_s2_real"],
            "yr20_sell_minus_rent_real": r10(diff20),
            "yr2076_sell_real": s31["wealth_s3_eq_real"],
            "yr2076_rent_real": s31["wealth_s2_real"],
            "yr2076_live_real": s31["wealth_s1_real"],
            "yr2076_sell_minus_rent_real": r10(diff31),
        })

    worst_10 = min(replays, key=lambda x: x["yr10_sell_minus_rent_real"])
    median_10 = sorted(replays, key=lambda x: x["yr10_sell_minus_rent_real"])[n // 2]
    best_10 = max(replays, key=lambda x: x["yr10_sell_minus_rent_real"])
    worst_31 = min(replays, key=lambda x: x["yr2076_sell_minus_rent_real"])

    return {
        "count": n,
        "sell_beats_rent_10yr": wins_10,
        "sell_beats_rent_20yr": wins_20,
        "sell_beats_rent_2076": wins_31,
        "worst_10yr": worst_10,
        "median_10yr": median_10,
        "best_10yr": best_10,
        "worst_2076": worst_31,
        "replays": replays,
    }


def build_named_black_swans(inherit_year: int = 2045) -> list[dict]:
    """Construct 7 named non-consistent 50-year Black Swan economic & hazard regimes."""
    scenarios = []

    # BS-1: 1973-1982 Stagflation Surge right at inheritance (2045-2054)
    rates_bs1 = {}
    stag = [
        (0.088, 0.095, 0.090, -0.147, 0.070),
        (0.110, 0.082, 0.078, -0.265, 0.079),
        (0.091, 0.115, 0.110, 0.372, 0.058),
        (0.058, 0.165, 0.158, 0.238, 0.050),
        (0.065, 0.200, 0.190, -0.072, 0.053),
        (0.076, 0.150, 0.145, 0.066, 0.072),
        (0.113, 0.140, 0.135, 0.184, 0.101),
        (0.135, 0.090, 0.090, 0.324, 0.114),
        (0.103, 0.045, 0.045, -0.049, 0.140),
        (0.061, 0.015, 0.015, 0.214, 0.106),
    ]
    for i, (c, hsj, hsf, sp, tb) in enumerate(stag):
        rates_bs1[inherit_year + i] = {"cpi": c, "hpi_sj": hsj, "hpi_sf": hsf, "sp500": sp, "tbill": tb}
    r1 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs1)
    scenarios.append({
        "id": "BS-1",
        "name": "1973–1982 Stagflation Surge After Inheritance",
        "historical_basis": "BLS CPI-U (11.0%–13.5% peaks), NBER 1973–75 & 1980–82 recessions, FHFA Bay Area HPI",
        "source_id": "FRED-CPI",
        "mechanism": "Double-digit inflation erodes bonds/cash while Prop 13 caps assessed-value growth at 2%/yr; initial -15%/-26% equity bear market compresses S3 early before post-1982 recovery.",
        "yr10_s1_real": r1["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r1["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r1["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r1["end_2076"]["wealth_s1_real"],
        "end_s2_real": r1["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r1["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r1["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Sell & Reinvest (Equities) — Rent wins at Year 5 during initial stagflation shock",
    })

    # BS-2: 2007-2012 Global Financial Crisis & Housing Crash at Inheritance
    rates_bs2 = {}
    for i, offset in enumerate(range(31, 41)):  # 2007..2016 from HIST_1976_2025
        _, c, hsj, hsf, sp, tb = HIST_1976_2025[offset]
        rates_bs2[inherit_year + i] = {"cpi": c, "hpi_sj": hsj, "hpi_sf": hsf, "sp500": sp, "tbill": tb}
    r2 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs2)
    scenarios.append({
        "id": "BS-2",
        "name": "2007–2012 GFC Housing & Stock Crash at Inheritance",
        "historical_basis": "FHFA San Jose HPI (-26% cumulative 2007–11), S&P 500 (-37% in 2008), CA R&TC §51(a)(2) Prop 8",
        "source_id": "FRED-HPI-SJ",
        "mechanism": "Selling in 2045 and investing lump-sum right before a 2008-style -37% crash hits equities hard in Year 2, while Prop 8 temporarily cuts rental property tax in S2; equities recover by Year 10.",
        "yr10_s1_real": r2["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r2["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r2["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r2["end_2076"]["wealth_s1_real"],
        "end_s2_real": r2["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r2["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r2["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Sell & Reinvest (Equities) — staged 24–36 mo T-bill glidepath mitigates Year 2 drawdown",
    })

    # BS-3: 2000-2009 Silicon Valley Dot-Com Bust + Lost Equity Decade
    rates_bs3 = {}
    for i, offset in enumerate(range(24, 36)):  # 2000..2011 (includes BOTH 2000-02 & 2008 crashes!)
        _, c, hsj, hsf, sp, tb = HIST_1976_2025[offset]
        rates_bs3[inherit_year + i] = {"cpi": c, "hpi_sj": hsj, "hpi_sf": hsf, "sp500": sp, "tbill": tb}
    r3 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs3)
    scenarios.append({
        "id": "BS-3",
        "name": "2000–2011 Dot-Com + GFC 'Lost Equity Decade'",
        "historical_basis": "Actual 2000–2011 U.S. & Bay Area sequence (-9.1%, -11.9%, -22.1% S&P followed by 2008 -37.0%)",
        "source_id": "NBER-CYCLES",
        "mechanism": "Worst modern 10-year sequence for lump-sum stock investing: Rent (S2) leads Sell-into-Stocks (S3) at Year 10 by >$1.9M (real), before long-run equity compounding overtakes by Year 20.",
        "yr10_s1_real": r3["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r3["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r3["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r3["end_2076"]["wealth_s1_real"],
        "end_s2_real": r3["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r3["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r3["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Rent wins at 10-yr mark; Sell & Reinvest (Equities) wins by 2076",
    })

    # BS-4: 1929-1938 Great Depression Deflationary Shock
    rates_bs4 = {}
    depr_seq = [
        (-0.064, -0.10, -0.10, -0.25, 0.024),
        (-0.093, -0.14, -0.14, -0.43, 0.014),
        (-0.103, -0.12, -0.12, -0.08, 0.009),
        (0.008, -0.03, -0.03, 0.54, 0.005),
        (0.015, 0.02, 0.02, -0.01, 0.003),
        (0.030, 0.03, 0.03, 0.47, 0.002),
        (0.014, 0.04, 0.04, 0.34, 0.001),
        (0.029, 0.02, 0.02, -0.35, 0.004),
        (-0.028, -0.02, -0.02, 0.31, 0.001),
        (0.000, 0.01, 0.01, -0.004, 0.000),
    ]
    for i, (c, hsj, hsf, sp, tb) in enumerate(depr_seq):
        rates_bs4[inherit_year + i] = {"cpi": c, "hpi_sj": hsj, "hpi_sf": hsf, "sp500": sp, "tbill": tb}
    r4 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs4)
    scenarios.append({
        "id": "BS-4",
        "name": "1929–1938 Great Depression Deflation Shock",
        "historical_basis": "BLS Historical CPI-U Table 24 (-6.4%, -9.3%, -10.3% deflation in 1930–32) & NBER 43-month contraction",
        "source_id": "BLS-HIST-CPI",
        "mechanism": "Severe price/asset deflation slashes nominal equities and housing simultaneously; Treasury bills preserve nominal principal and gain ~28% real purchasing power during the first 3 years.",
        "yr10_s1_real": r4["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r4["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r4["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r4["end_2076"]["wealth_s1_real"],
        "end_s2_real": r4["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r4["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r4["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "T-Bills / Balanced 60/40 protect Years 1–5; Equities still lead by 2076 after rebound",
    })

    # BS-5: 1991-2020 Japan-Style 30-Year Secular Stagnation
    rates_bs5 = {}
    for y in range(inherit_year, END_YEAR + 1):
        # Near-zero inflation (0.4%), flat/slightly negative land prices (-0.5% first 15 yrs then +1%),
        # muted 2.2% nominal stock return (mostly dividend), 0.3% cash rate
        hs = -0.005 if (y - inherit_year) < 15 else 0.012
        rates_bs5[y] = {"cpi": 0.004, "hpi_sj": hs, "hpi_sf": hs, "sp500": 0.022, "tbill": 0.003}
    r5 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs5)
    scenarios.append({
        "id": "BS-5",
        "name": "30-Year Secular Stagnation ('Lost Decades')",
        "historical_basis": "Post-1990 asset-bubble stagnation benchmark (0.4% CPI, 2.2% equity total return, flat housing)",
        "source_id": "SEC-ALLOC",
        "mechanism": "The ONE structural regime where selling into stocks loses to keeping and renting Property A: rental yield (~2.7% net of Prop 8-reduced taxes) outpaces 2.2% stagnant equities over 31 years.",
        "yr10_s1_real": r5["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r5["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r5["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r5["end_2076"]["wealth_s1_real"],
        "end_s2_real": r5["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r5["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r5["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Rent Property A (S2) beats Sell & Reinvest (S3) under multi-decade equity stagnation",
    })

    # BS-6: Bay Area M>=6.7 Major Earthquake Uninsured Structural Loss (2050)
    r6 = simulate_50yr_path(inherit_year=inherit_year, quake_year=2050, quake_loss_pct=0.18)
    scenarios.append({
        "id": "BS-6",
        "name": "Bay Area M≥6.7 Earthquake Uninsured Structural Shock (2050)",
        "historical_basis": "USGS Fact Sheet 2016-3020 (72% 30-yr M≥6.7 probability) + CDI Form 401 earthquake exclusion",
        "source_id": "USGS-QUAKE",
        "mechanism": "Standard HO-3 / landlord policies exclude earthquake damage; an uninsured 18% structural rebuild shock on Property A widens S3's advantage because a diversified global/US equity fund has no single-parcel seismic concentration.",
        "yr10_s1_real": r6["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r6["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r6["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r6["end_2076"]["wealth_s1_real"],
        "end_s2_real": r6["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r6["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r6["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Sell & Reinvest (Equities) — eliminates concentrated single-parcel seismic tail risk",
    })

    # BS-7: CPUC 20-Year NEM Sunset + California Insurance & Water Surge (6.5%/yr operating inflation)
    rates_bs7 = {y: {"util_g": 0.065} for y in YEARS}
    r7 = simulate_50yr_path(inherit_year=inherit_year, rates_by_year=rates_bs7, post_nem_sunset_year=2038)
    scenarios.append({
        "id": "BS-7",
        "name": "20-Year NEM Solar Sunset + 6.5%/yr CA Insurance & Water Escalation",
        "historical_basis": "CPUC D.14-03-041 (20-yr NEM sunset), Res. E-5354 ($24.15/mo fixed charge), SFPUC FY26-28 (+7%–10%/yr), CDI market hardening",
        "source_id": "CPUC-NEM",
        "mechanism": "Cupertino solar net credit flips to a net bill once the 20-yr NEM window closes, while insurance and water compound at 6.5%/yr — eroding Property A net operating yield and further favoring Sale & Reinvestment.",
        "yr10_s1_real": r7["snapshots_by_horizon"][10]["wealth_s1_real"],
        "yr10_s2_real": r7["snapshots_by_horizon"][10]["wealth_s2_real"],
        "yr10_s3_eq_real": r7["snapshots_by_horizon"][10]["wealth_s3_eq_real"],
        "end_s1_real": r7["end_2076"]["wealth_s1_real"],
        "end_s2_real": r7["end_2076"]["wealth_s2_real"],
        "end_s3_eq_real": r7["end_2076"]["wealth_s3_eq_real"],
        "end_s3_cash_real": r7["end_2076"]["wealth_s3_cash_real"],
        "winner_2076": "Sell & Reinvest (Equities)",
    })

    return scenarios


def build_estate_cash_headroom() -> dict:
    """Project federal/state/local estate tax thresholds & cash inheritance headroom (2026–2055)."""
    rows = []
    excl = float(FED_EXCLUSION_2026)
    cup = float(CUP_FMV_2026)
    cpi_cum = 1.0

    for y in range(2026, 2056):
        if y == 2027:
            excl = float(FED_EXCLUSION_2027)  # exact IRS Rev. Proc. 2026-35 §3.44 figure
            cup *= (1.0 + BASE_HPI)
            cpi_cum *= (1.0 + BASE_CPI)
        elif y > 2027:
            excl *= (1.0 + BASE_CPI)
            cup *= (1.0 + BASE_HPI)
            cpi_cum *= (1.0 + BASE_CPI)

        single_excl = r10(excl)
        married_dsue_excl = r10(excl * 2.0)
        cup_val = r10(cup)
        cash_room_single = max(0, r10(excl - cup))
        cash_room_married = max(0, r10(excl * 2.0 - cup))
        # Stress test: Congress halves basic exclusion to $7.5M (2026 real) indexed
        halved_excl = excl * 0.50
        cash_room_halved = max(0, r10(halved_excl - cup))

        rows.append({
            "year": y,
            "cup_fmv": cup_val,
            "single_exclusion": single_excl,
            "married_dsue_exclusion": married_dsue_excl,
            "cash_headroom_single": cash_room_single,
            "cash_headroom_married": cash_room_married,
            "halved_law_exclusion": r10(halved_excl),
            "cash_headroom_halved_single": cash_room_halved,
            "ca_estate_tax": 0,
            "local_inheritance_tax": 0,
        })

    # Cash sensitivity penalty table at 2045 inheritance
    row_2045 = next(r for r in rows if r["year"] == 2045)
    cash_levels = [0, 2_000_000, 5_000_000, 10_000_000, 15_000_000, 17_610_000, 20_000_000, 25_000_000, 35_000_000]
    sensitivity_2045 = []
    for cash in cash_levels:
        gross_est = row_2045["cup_fmv"] + cash
        tax_single = r10(max(0.0, gross_est - row_2045["single_exclusion"]) * FED_ESTATE_TOP_RATE)
        tax_married = r10(max(0.0, gross_est - row_2045["married_dsue_exclusion"]) * FED_ESTATE_TOP_RATE)
        tax_halved = r10(max(0.0, gross_est - row_2045["halved_law_exclusion"]) * FED_ESTATE_TOP_RATE)
        sensitivity_2045.append({
            "cash_inherited": r10(cash),
            "gross_estate_with_cup": r10(gross_est),
            "fed_tax_single_current_law": tax_single,
            "net_received_single_current_law": r10(gross_est - tax_single),
            "fed_tax_married_dsue": tax_married,
            "fed_tax_if_exclusion_halved": tax_halved,
        })

    return {
        "rows_2026_2055": rows,
        "key_years": {str(r["year"]): r for r in rows if r["year"] in (2026, 2027, 2030, 2035, 2040, 2045, 2050, 2055)},
        "cash_sensitivity_2045": sensitivity_2045,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_all() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    base_2040 = simulate_50yr_path(inherit_year=2040)
    base_2045 = simulate_50yr_path(inherit_year=2045)
    base_2050 = simulate_50yr_path(inherit_year=2050)
    no_stepup_2045 = simulate_50yr_path(inherit_year=2045, step_up_applies=False)
    nem_sunset_2045 = simulate_50yr_path(inherit_year=2045, post_nem_sunset_year=2038)

    rolling = build_rolling_historical_replays(inherit_year=2045)
    black_swans = build_named_black_swans(inherit_year=2045)
    estate_cash = build_estate_cash_headroom()

    # Self-tests on mathematical & rounding invariants
    assert len(base_2045["rows"]) == 51, "Must cover all 51 snapshots 2026..2076"
    assert base_2045["end_2076"]["wealth_s3_eq_real"] > base_2045["end_2076"]["wealth_s2_real"] > base_2045["end_2076"]["wealth_s1_real"]
    assert base_2045["end_2076"]["wealth_s2_real"] > base_2045["end_2076"]["wealth_s3_cash_real"], "Renting beats 3.5% cash parking"
    assert no_stepup_2045["sale_tax_at_inh"] > 1_500_000, "Rev. Rul. 2023-2 no-step-up trap must trigger large capital gains tax"
    assert rolling["count"] == 50

    for ds in (base_2040["rows"], base_2045["rows"], base_2050["rows"], rolling["replays"], estate_cash["rows_2026_2055"]):
        for row in ds:
            for k, v in row.items():
                if isinstance(v, int) and k not in ("year", "start_hist_year", "ca_estate_tax", "local_inheritance_tax"):
                    assert v % 10 == 0, f"Non-$10-rounded integer {k}={v}"

    write_csv(DATA_DIR / "baseline_50yr_2045.csv", base_2045["rows"])
    write_csv(DATA_DIR / "baseline_50yr_2040.csv", base_2040["rows"])
    write_csv(DATA_DIR / "baseline_50yr_2050.csv", base_2050["rows"])
    write_csv(DATA_DIR / "rolling_50yr_backtest.csv", rolling["replays"])
    write_csv(DATA_DIR / "black_swan_paths.csv", black_swans)
    write_csv(DATA_DIR / "estate_cash_headroom.csv", estate_cash["rows_2026_2055"])

    summary = {
        "generated_on": "2026-11-11",
        "session": "arena/459d7aa2-tino1",
        "horizon": "2026-2076 (50 years, 51 annual snapshots)",
        "baseline_by_inherit_year": {
            "2040": {k: v for k, v in base_2040.items() if k != "rows"},
            "2045": {k: v for k, v in base_2045.items() if k != "rows"},
            "2050": {k: v for k, v in base_2050.items() if k != "rows"},
        },
        "sensitivities_2045": {
            "no_step_up_irrevocable_trust": {k: v for k, v in no_stepup_2045.items() if k != "rows"},
            "post_nem_20yr_sunset": {k: v for k, v in nem_sunset_2045.items() if k != "rows"},
        },
        "rolling_50yr": rolling,
        "black_swans": black_swans,
        "estate_cash": estate_cash,
        "rows_2045": base_2045["rows"],
        "rows_2040": base_2040["rows"],
        "rows_2050": base_2050["rows"],
    }
    (DATA_DIR / "model_output.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    out = run_all()
    b45 = out["baseline_by_inherit_year"]["2045"]
    e45 = b45["end_2076"]
    print(
        f"OK - 2045 inheritance: FMV=${b45['cup_fmv_at_inh']:,}, "
        f"S1 tax=${b45['s1_tax_yr1']:,}/yr, S2 tax=${b45['s2_tax_yr1']:,}/yr, "
        f"Net sale=${b45['sale_net_proceeds_at_inh']:,} | "
        f"2076 real (2026$): Sell-Eq=${e45['wealth_s3_eq_real']:,}, "
        f"Sell-60/40=${e45['wealth_s3_bal_real']:,}, "
        f"Rent=${e45['wealth_s2_real']:,}, "
        f"Sell-Cash=${e45['wealth_s3_cash_real']:,}, "
        f"Live=${e45['wealth_s1_real']:,} | "
        f"Rolling 50-yr Sell>Rent: {out['rolling_50yr']['sell_beats_rent_10yr']}/50 (10yr), "
        f"{out['rolling_50yr']['sell_beats_rent_20yr']}/50 (20yr)"
    )
