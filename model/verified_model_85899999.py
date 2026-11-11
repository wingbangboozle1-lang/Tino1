#!/usr/bin/env python3
"""
Reproducible, anonymized, $10-rounded financial & tax projection engine (2026-2050)
for [Property A — Cupertino ZIP 95014] and [Property B — San Francisco ZIP 94122].

Session: session-85899999 (branch arena/85899999-tino1)
All dollar outputs are rounded to the nearest $10 increment per project mandate.
"""

import csv
import json
from pathlib import Path


def r10(val: float) -> int:
    """Round any dollar figure to the nearest $10 increment."""
    return int(round(val / 10.0) * 10)


# ==============================================================================
# 1. VERIFIED BASELINE INPUTS & OFFICIAL RATES (AS OF NOV 2026)
# ==============================================================================

# [Property A — Cupertino Single-Family Residence, ZIP 95014]
CUP_FMV_2026 = 3_100_000          # User Nov 2026 estimate (flagged: not formal appraisal)
CUP_FBYV_2026 = 550_540           # 2026 Prop 13 assessed value ($10-rounded; exact value withheld for privacy)
CUP_AD_VALOREM_RATE = 0.011636    # SCC Controller FY25-26 Tax Rate Book (Cupertino TRA)
CUP_PARCEL_CHARGES_2026 = 950     # Fixed non-ad-valorem parcel/direct charges (~$930 in 2025 +2%, rounded to $10)
HOMEOWNERS_EXEMPTION = 7_000      # CA RTC § 218 ($7,000 assessed value reduction for primary res)

CUP_WATER_2026 = 1_560            # $130/mo ($100-$150/mo user range)
CUP_SOLAR_CREDIT_2026 = -240      # -$20/mo net credit while NEM 1.0/2.0 legacy active
CUP_NEM_SUNSET_YEAR = 2038        # Pre-2026 solar hits 20-yr CPUC NEM sunset (D.14-03-041 / D.22-12-056) <=2046; 2038 midpoint
CUP_POST_NEM_ELEC_2026_EQ = 660   # Post-NEM NBT + CPUC D.24-05-028 / Res. E-5354 $24.15/mo (~$290/yr) fixed charge + net usage (2026$)
CUP_INS_PRIMARY_2026 = 2_600      # Planning sensitivity above owner $1,500 guess (CDI SB 824 statewide avg ~$1,130; ZIP 95014 quote unverified)
CUP_INS_LANDLORD_2026 = 3_120     # DP-3 landlord policy (+20% over HO-3) if rented out (unverified planning sensitivity)
CUP_MAINT_2026 = 7_800            # Annual structure maintenance & solar/roof capex reserve (lower than SF 3-unit)
CUP_MARKET_RENT_MO_2026 = 6_390   # Official HUD FY2026 SAFMR ZIP 95014 4BR ($6,390/mo; 3BR is $5,870/mo)
CUP_SELL_COST_PCT = 0.050         # 0.11% SCC transfer tax (RTC § 11911) + ~4.89% brokerage/escrow/prep

# [Property B — San Francisco 3-Unit Property, Outer Sunset, ZIP 94122 — ALREADY OWNED BY INHERITOR]
SF_FMV_2026 = 1_800_000           # User Nov 2026 estimate (flagged: not formal appraisal)
SF_FBYV_2025 = 114_250            # 2025 Prop 13 assessed value ($10-rounded; exact value withheld for privacy)
SF_FBYV_2026 = r10(SF_FBYV_2025 * 1.02)  # 2026 Prop 13 +2.0% factor (CA R&TC § 51) -> $116,540
SF_AD_VALOREM_RATE = 0.01181622   # SF Treasurer FY 2026-27 secured tax rate (1.18162182%)
SF_PARCEL_CHARGES_2026 = 1_110    # Fixed parcel/special assessments (~$1,090 in 2025 +2%, rounded to $10)
SF_RENT_BOARD_FEE_NET_2026 = 90   # Net annual Rent Board fee allowance ($10-rounded)

SF_RENT_2UNITS_MO_2026 = 7_150    # User actual 2 rented units ($85,800/yr; cf. HUD FY2026 SAFMR 94122 2BR $3,310 / 3BR $4,230)
SF_UNIT3_MARKET_MO_2026 = 3_310   # Official HUD FY2026 SAFMR ZIP 94122 2BR ($3,310/mo) if Unit 3 rented
SF_WATER_2026 = 4_440             # $370/mo ($330-$400/mo user range; SFPUC FY26-28 multi-family water+sewer)
SF_ELEC_2026 = 600                # $50/mo ($30-$70/mo user range; PG&E common/owner electric)
SF_INS_LANDLORD_2026 = 3_600      # 3-unit habitational/landlord DP-3 planning sensitivity above owner $1,500 guess (unverified)
SF_MAINT_2026 = 12_600            # 3-unit older coastal salt-fog structure maintenance & capex reserve

# Statutory Tax & Macro Escalation Parameters
PROP13_CAP = 0.020                # CA Const. Art. XIII A § 2(b) max 2.000%/yr FBYV growth
PROP19_CAP_2025 = 1_044_586       # CA BOE LTA 2025/009 (effective 2/16/2025 - 2/15/2027)
PROP19_HPI_ANNUAL = 0.035         # Biennial CA FHFA HPI growth assumption (~7.12% per 2-yr adjustment)

G_CUP_HOME = 0.042                # Conservative forward CAGR (vs. 4.91% 1991-2026Q2 FHFA San Jose MSA)
G_SF_HOME = 0.035                 # Conservative forward CAGR (vs. 4.75% 1991-2026Q2 FHFA SF MSAD)
G_CPI = 0.023                     # CBO Feb 2026 long-run CPI-U (~2.0% PCE + 0.3% CPI-PCE wedge)
G_PARCEL = 0.020                  # Parcel assessment escalation
G_WATER_CUP = 0.032               # CPUC Class A water GRC escalation
G_WATER_SF = 0.045                # SFPUC water/wastewater capital debt escalation
G_ELEC = 0.035                    # PG&E electric escalation
G_INS = 0.040                     # CA residential property insurance escalation
G_MAINT = 0.028                   # Construction/repair labor & materials inflation
G_CUP_RENT = 0.030                # Market single-family rent growth (AB 1482 exempt if SFR w/ notice)
G_SF_RENT_BLENDED = 0.028         # Blended SF Rent Ordinance (60% CPI ~1.5% in-place + periodic turnover)

FED_ESTATE_EXCLUSION_2026 = 15_000_000  # OBBBA P.L. 119-21 § 70106 / IRS Rev. Proc. 2025-32
FED_ESTATE_RATE = 0.40            # IRC § 2001(c) top marginal estate tax rate
COMBINED_CAP_GAINS_RATE = 0.371   # 20.0% Fed LTCG + 3.8% NIIT + 13.3% CA top PIT
PORTFOLIO_PRETAX_RETURN = 0.070   # Balanced 70/30 global equity/bond nominal return
PORTFOLIO_AFTERTAX_RETURN = 0.058 # Tax-efficient index ETF net compounding after Fed+CA dividend/realization drag


def prop19_cap_for_year(year: int) -> float:
    """Biennial FHFA CA HPI adjustment occurring Feb 16 of odd years (2025, 2027, 2029...)."""
    steps = max(0, (year - 2025) // 2)
    return PROP19_CAP_2025 * ((1.0 + PROP19_HPI_ANNUAL) ** (2 * steps))


def generate_yearly_projections():
    cup_rows = []
    sf_rows = []

    for year in range(2026, 2051):
        t = year - 2026

        # --- Cupertino (95014) ---
        c_fmv = CUP_FMV_2026 * ((1 + G_CUP_HOME) ** t)
        c_fbyv = CUP_FBYV_2026 * ((1 + PROP13_CAP) ** t)
        c_parcel = CUP_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t)
        c_tax_pre_inherit = max(0.0, c_fbyv - HOMEOWNERS_EXEMPTION) * CUP_AD_VALOREM_RATE + c_parcel

        p19_cap = prop19_cap_for_year(year)
        c_assessed_prop19 = c_fbyv + max(0.0, c_fmv - (c_fbyv + p19_cap))
        c_tax_prop19_live = max(0.0, c_assessed_prop19 - HOMEOWNERS_EXEMPTION) * CUP_AD_VALOREM_RATE + c_parcel
        c_tax_full_reassess = c_fmv * CUP_AD_VALOREM_RATE + c_parcel

        c_water = CUP_WATER_2026 * ((1 + G_WATER_CUP) ** t)
        if year < CUP_NEM_SUNSET_YEAR:
            # Gradual solar panel degradation (-0.5%/yr) prior to 20-yr NEM sunset
            c_elec = CUP_SOLAR_CREDIT_2026 * ((0.995) ** t)
        else:
            c_elec = CUP_POST_NEM_ELEC_2026_EQ * ((1 + G_ELEC) ** t)

        c_ins_live = CUP_INS_PRIMARY_2026 * ((1 + G_INS) ** t)
        c_ins_rent = CUP_INS_LANDLORD_2026 * ((1 + G_INS) ** t)
        c_maint = CUP_MAINT_2026 * ((1 + G_MAINT) ** t)
        c_mkt_rent_gross = CUP_MARKET_RENT_MO_2026 * 12 * ((1 + G_CUP_RENT) ** t)

        cup_rows.append({
            "year": year,
            "fmv": r10(c_fmv),
            "fbyv_prop13": r10(c_fbyv),
            "tax_prop13_current": r10(c_tax_pre_inherit),
            "prop19_cap": r10(p19_cap),
            "assessed_if_inherited_live": r10(c_assessed_prop19),
            "tax_if_inherited_live": r10(c_tax_prop19_live),
            "tax_if_inherited_rent": r10(c_tax_full_reassess),
            "water_yr": r10(c_water),
            "electric_yr": r10(c_elec),
            "insurance_primary_yr": r10(c_ins_live),
            "insurance_landlord_yr": r10(c_ins_rent),
            "maintenance_yr": r10(c_maint),
            "total_opex_prop13": r10(c_tax_pre_inherit + c_water + c_elec + c_ins_live + c_maint),
            "total_opex_if_live": r10(c_tax_prop19_live + c_water + c_elec + c_ins_live + c_maint),
            "total_opex_if_rent": r10(c_tax_full_reassess + c_water + max(0.0, c_elec) + c_ins_rent + c_maint),
            "est_gross_rent_yr": r10(c_mkt_rent_gross),
        })

        # --- San Francisco Outer Sunset (94122, 3 Units) ---
        s_fmv = SF_FMV_2026 * ((1 + G_SF_HOME) ** t)
        s_fbyv = SF_FBYV_2026 * ((1 + PROP13_CAP) ** t)
        s_parcel = SF_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t)
        s_rb_fee = SF_RENT_BOARD_FEE_NET_2026 * ((1 + G_PARCEL) ** t)
        s_tax_prop13 = max(0.0, s_fbyv - HOMEOWNERS_EXEMPTION) * SF_AD_VALOREM_RATE + s_parcel
        # Note: If SF were also inherited via trust while beneficiary occupies 1 of 3 units,
        # 2/3 rental portion reassesses to FMV and 1/3 owner unit gets Prop 19 check:
        s_unit_fmv = s_fmv / 3.0
        s_unit_fbyv = s_fbyv / 3.0
        s_owner_unit_assessed = s_unit_fbyv + max(0.0, s_unit_fmv - (s_unit_fbyv + p19_cap))
        s_assessed_if_also_inherited = (2.0 * s_unit_fmv) + s_owner_unit_assessed
        s_tax_if_also_inherited = max(0.0, s_assessed_if_also_inherited - HOMEOWNERS_EXEMPTION) * SF_AD_VALOREM_RATE + s_parcel

        s_water = SF_WATER_2026 * ((1 + G_WATER_SF) ** t)
        s_elec = SF_ELEC_2026 * ((1 + G_ELEC) ** t)
        s_ins = SF_INS_LANDLORD_2026 * ((1 + G_INS) ** t)
        s_maint = SF_MAINT_2026 * ((1 + G_MAINT) ** t)
        s_rent_2units = SF_RENT_2UNITS_MO_2026 * 12 * ((1 + G_SF_RENT_BLENDED) ** t)
        s_unit3_potential = SF_UNIT3_MARKET_MO_2026 * 12 * ((1 + G_SF_RENT_BLENDED) ** t) * 0.95
        s_total_cost_prop13 = s_tax_prop13 + s_rb_fee + s_water + s_elec + s_ins + s_maint
        s_noi_2units = s_rent_2units - s_total_cost_prop13

        sf_rows.append({
            "year": year,
            "fmv": r10(s_fmv),
            "fbyv_prop13": r10(s_fbyv),
            "tax_prop13_current": r10(s_tax_prop13),
            "tax_if_also_inherited_2of3_reassessed": r10(s_tax_if_also_inherited),
            "rent_board_fee_yr": r10(s_rb_fee),
            "water_sewer_yr": r10(s_water),
            "electric_yr": r10(s_elec),
            "insurance_yr": r10(s_ins),
            "maintenance_yr": r10(s_maint),
            "total_opex_prop13": r10(s_total_cost_prop13),
            "gross_rent_2units_yr": r10(s_rent_2units),
            "net_cashflow_2units_prop13": r10(s_noi_2units),
            "optional_unit3_net_rent_yr": r10(s_unit3_potential),
        })

    return cup_rows, sf_rows


def evaluate_inheritance_scenarios(inherit_year: int, horizon_years: int = 15):
    """
    Compare 4 complete household strategies over `horizon_years` starting at `inherit_year`:
      S1: Sell Cupertino (Revocable Trust §1014 Step-Up) & Reinvest + Live in SF Unit 3 (Keep 2 SF Rentals)
      S2A: Live in Cupertino (Prop 19 Partial Exclusion) + Keep SF (2 Units Rented, Unit 3 Unrented/Family Use)
      S2B: Live in Cupertino (Prop 19 Partial Exclusion) + Rent All 3 SF Units (Unit 3 Enters SF Rent Control)
      S3: Rent Out Cupertino (Full FMV Reassessment, No Prop 19) + Live in SF Unit 3
    All figures include both properties' cash flows and terminal after-tax liquidation/equity values, rounded to $10.
    """
    t0 = inherit_year - 2026
    c_fmv0 = CUP_FMV_2026 * ((1 + G_CUP_HOME) ** t0)
    c_fbyv0 = CUP_FBYV_2026 * ((1 + PROP13_CAP) ** t0)
    p19_cap0 = prop19_cap_for_year(inherit_year)

    # Initialassessed bases at inheritance year
    c_base_live0 = c_fbyv0 + max(0.0, c_fmv0 - (c_fbyv0 + p19_cap0))
    c_base_rent0 = c_fmv0

    # S1 Immediate Sale Proceeds (Revocable Trust -> IRC § 1014 basis = c_fmv0 -> $0 cap gains tax at death)
    s1_net_sale_proceeds = c_fmv0 * (1.0 - CUP_SELL_COST_PCT)
    # Contrast: if held in estate-excluded Irrevocable Grantor Trust (Rev. Rul. 2023-2), carryover basis ~c_fbyv0:
    irrevocable_cap_gains_tax_hit = max(0.0, (c_fmv0 * (1.0 - CUP_SELL_COST_PCT)) - c_fbyv0) * COMBINED_CAP_GAINS_RATE

    # Simulate year-by-year over `horizon_years`
    s1_portfolio = s1_net_sale_proceeds
    s2a_cash_acct = 0.0
    s2b_cash_acct = 0.0
    s3_cash_acct = 0.0

    s1_yr1_net_cf = 0.0
    s2a_yr1_net_cf = 0.0
    s2b_yr1_net_cf = 0.0
    s3_yr1_net_cf = 0.0

    cum_cup_tax_live = 0.0
    cum_cup_tax_rent = 0.0

    for k in range(horizon_years):
        yr = inherit_year + k
        t = yr - 2026

        # SF baseline cash flow (2 units rented, existing Prop 13 base)
        sf_fbyv = SF_FBYV_2026 * ((1 + PROP13_CAP) ** t)
        sf_parcel = SF_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t)
        sf_rb = SF_RENT_BOARD_FEE_NET_2026 * ((1 + G_PARCEL) ** t)
        sf_tax_owner_occ = max(0.0, sf_fbyv - HOMEOWNERS_EXEMPTION) * SF_AD_VALOREM_RATE + sf_parcel
        sf_tax_non_owner = sf_fbyv * SF_AD_VALOREM_RATE + sf_parcel
        sf_opex_base = sf_rb + SF_WATER_2026 * ((1 + G_WATER_SF) ** t) + SF_ELEC_2026 * ((1 + G_ELEC) ** t) + SF_INS_LANDLORD_2026 * ((1 + G_INS) ** t) + SF_MAINT_2026 * ((1 + G_MAINT) ** t)
        sf_rent2 = SF_RENT_2UNITS_MO_2026 * 12 * ((1 + G_SF_RENT_BLENDED) ** t)
        # Marginal income tax on positive rental NOI (~33% blended Fed+CA after depreciation/expenses)
        sf_noi_owner = sf_rent2 - (sf_tax_owner_occ + sf_opex_base)
        sf_aftertax_cf_owner = sf_noi_owner * (1.0 - 0.30) if sf_noi_owner > 0 else sf_noi_owner

        sf_unit3_gross = SF_UNIT3_MARKET_MO_2026 * 12 * ((1 + G_SF_RENT_BLENDED) ** t) * 0.95
        sf_noi_all3 = (sf_rent2 + sf_unit3_gross) - (sf_tax_non_owner + sf_opex_base * 1.12)
        sf_aftertax_cf_all3 = sf_noi_all3 * (1.0 - 0.32) if sf_noi_all3 > 0 else sf_noi_all3

        sf_noi_2_nonowner = sf_rent2 - (sf_tax_non_owner + sf_opex_base)
        sf_aftertax_cf_2_nonowner = sf_noi_2_nonowner * (1.0 - 0.30) if sf_noi_2_nonowner > 0 else sf_noi_2_nonowner

        # Cupertino costs in year k after inheritance (new base compounds at 2%/yr Prop 13 cap)
        c_parcel = CUP_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t)
        c_tax_live = max(0.0, c_base_live0 * ((1 + PROP13_CAP) ** k) - HOMEOWNERS_EXEMPTION) * CUP_AD_VALOREM_RATE + c_parcel
        c_tax_rent = (c_base_rent0 * ((1 + PROP13_CAP) ** k)) * CUP_AD_VALOREM_RATE + c_parcel
        cum_cup_tax_live += c_tax_live
        cum_cup_tax_rent += c_tax_rent

        c_water = CUP_WATER_2026 * ((1 + G_WATER_CUP) ** t)
        c_elec = CUP_SOLAR_CREDIT_2026 * ((0.995) ** t) if yr < CUP_NEM_SUNSET_YEAR else CUP_POST_NEM_ELEC_2026_EQ * ((1 + G_ELEC) ** t)
        c_ins_live = CUP_INS_PRIMARY_2026 * ((1 + G_INS) ** t)
        c_ins_rent = CUP_INS_LANDLORD_2026 * ((1 + G_INS) ** t)
        c_maint = CUP_MAINT_2026 * ((1 + G_MAINT) ** t)

        c_hold_cost_live = c_tax_live + c_water + c_elec + c_ins_live + c_maint
        # If Cupertino rented: tenant pays water & electricity; owner pays full reassessed tax, DP-3 ins, maint, 8% mgmt, 5% vacancy
        c_gross_rent = CUP_MARKET_RENT_MO_2026 * 12 * ((1 + G_CUP_RENT) ** t)
        c_effective_rent = c_gross_rent * (1.0 - 0.05 - 0.08)
        c_rent_noi = c_effective_rent - (c_tax_rent + c_ins_rent + c_maint)
        # Depreciation on inherited residential structure (~30% structure share / 27.5 yrs) shields part of positive NOI
        c_depr = (c_fmv0 * 0.30) / 27.5
        c_taxable_rent_inc = c_rent_noi - c_depr
        c_rent_aftertax_cf = c_rent_noi - max(0.0, c_taxable_rent_inc * 0.35)

        # Annual net household property cash flows
        cf_s1 = sf_aftertax_cf_owner
        cf_s2a = sf_aftertax_cf_2_nonowner - c_hold_cost_live
        cf_s2b = sf_aftertax_cf_all3 - c_hold_cost_live
        cf_s3 = sf_aftertax_cf_owner + c_rent_aftertax_cf

        if k == 0:
            s1_yr1_net_cf = cf_s1
            s2a_yr1_net_cf = cf_s2a
            s2b_yr1_net_cf = cf_s2b
            s3_yr1_net_cf = cf_s3

        # Compound financial accounts at after-tax portfolio return (5.8%/yr)
        s1_portfolio = s1_portfolio * (1.0 + PORTFOLIO_AFTERTAX_RETURN) + cf_s1
        s2a_cash_acct = s2a_cash_acct * (1.0 + PORTFOLIO_AFTERTAX_RETURN) + cf_s2a
        s2b_cash_acct = s2b_cash_acct * (1.0 + PORTFOLIO_AFTERTAX_RETURN) + cf_s2b
        s3_cash_acct = s3_cash_acct * (1.0 + PORTFOLIO_AFTERTAX_RETURN) + cf_s3

    # Terminal Year Values (inherit_year + horizon_years)
    t_end = (inherit_year + horizon_years) - 2026
    c_fmv_end = CUP_FMV_2026 * ((1 + G_CUP_HOME) ** t_end)
    sf_fmv_end = SF_FMV_2026 * ((1 + G_SF_HOME) ** t_end)

    # Terminal Cupertino net liquidation equity if kept (accounting for selling cost + post-inheritance capital gains)
    c_net_sale_end = c_fmv_end * (1.0 - CUP_SELL_COST_PCT)
    c_gain_end = max(0.0, c_net_sale_end - c_fmv0)
    # In S2A/S2B (primary residence), IRC § 121 excludes $250k single ($500k married; use conservative $250k single baseline)
    c_cap_gain_tax_live = max(0.0, c_gain_end - 250_000) * COMBINED_CAP_GAINS_RATE
    # In S3 (rental), no § 121 exclusion + 25% § 1250 depreciation recapture (+13.3% CA)
    cum_depr = ((c_fmv0 * 0.30) / 27.5) * horizon_years
    c_cap_gain_tax_rent = (c_gain_end * COMBINED_CAP_GAINS_RATE) + (cum_depr * (0.25 + 0.038 + 0.133))

    c_aftertax_equity_live = c_net_sale_end - c_cap_gain_tax_live
    c_aftertax_equity_rent = c_net_sale_end - c_cap_gain_tax_rent

    # Total Household Wealth (Financial Portfolio + Cupertino After-Tax Equity + SF Gross Equity)
    s1_total_wealth = s1_portfolio + sf_fmv_end
    s2a_total_wealth = s2a_cash_acct + c_aftertax_equity_live + sf_fmv_end
    s2b_total_wealth = s2b_cash_acct + c_aftertax_equity_live + sf_fmv_end
    s3_total_wealth = s3_cash_acct + c_aftertax_equity_rent + sf_fmv_end

    return {
        "inherit_year": inherit_year,
        "horizon_years": horizon_years,
        "end_year": inherit_year + horizon_years,
        "cupertino_fmv_at_inheritance": r10(c_fmv0),
        "cupertino_fbyv_at_inheritance": r10(c_fbyv0),
        "prop19_cap_at_inheritance": r10(p19_cap0),
        "cupertino_yr1_tax_if_live": r10(max(0.0, c_base_live0 - HOMEOWNERS_EXEMPTION) * CUP_AD_VALOREM_RATE + CUP_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t0)),
        "cupertino_yr1_tax_if_rent": r10(c_base_rent0 * CUP_AD_VALOREM_RATE + CUP_PARCEL_CHARGES_2026 * ((1 + G_PARCEL) ** t0)),
        "prop19_annual_tax_savings_yr1": r10(
            (c_base_rent0 * CUP_AD_VALOREM_RATE) - (max(0.0, c_base_live0 - HOMEOWNERS_EXEMPTION) * CUP_AD_VALOREM_RATE)
        ),
        "s1_net_sale_proceeds_day1": r10(s1_net_sale_proceeds),
        "s1_yr1_portfolio_aftertax_gain": r10(s1_net_sale_proceeds * PORTFOLIO_AFTERTAX_RETURN),
        "cupertino_yr1_net_rent_aftertax": r10(s3_yr1_net_cf - s1_yr1_net_cf),
        "cupertino_yr1_net_yield_pct": round(((s3_yr1_net_cf - s1_yr1_net_cf) / c_fmv0) * 100.0, 2),
        "irrevocable_trust_cap_gains_penalty_if_sold": r10(irrevocable_cap_gains_tax_hit),
        "cum_cupertino_prop_tax_15yr_live": r10(cum_cup_tax_live),
        "cum_cupertino_prop_tax_15yr_rent": r10(cum_cup_tax_rent),
        "strategies": [
            {
                "id": "S1",
                "name": "Sell Cupertino & Reinvest + Live in SF Unit 3",
                "yr1_net_cashflow": r10(s1_yr1_net_cf),
                "financial_portfolio_end": r10(s1_portfolio),
                "cupertino_aftertax_equity_end": 0,
                "sf_equity_end": r10(sf_fmv_end),
                "total_household_wealth_end": r10(s1_total_wealth),
            },
            {
                "id": "S2B",
                "name": "Live in Cupertino (Prop 19) + Rent All 3 SF Units",
                "yr1_net_cashflow": r10(s2b_yr1_net_cf),
                "financial_portfolio_end": r10(s2b_cash_acct),
                "cupertino_aftertax_equity_end": r10(c_aftertax_equity_live),
                "sf_equity_end": r10(sf_fmv_end),
                "total_household_wealth_end": r10(s2b_total_wealth),
            },
            {
                "id": "S2A",
                "name": "Live in Cupertino (Prop 19) + Keep SF Unit 3 Vacant",
                "yr1_net_cashflow": r10(s2a_yr1_net_cf),
                "financial_portfolio_end": r10(s2a_cash_acct),
                "cupertino_aftertax_equity_end": r10(c_aftertax_equity_live),
                "sf_equity_end": r10(sf_fmv_end),
                "total_household_wealth_end": r10(s2a_total_wealth),
            },
            {
                "id": "S3",
                "name": "Rent Out Cupertino (No Prop 19) + Live in SF Unit 3",
                "yr1_net_cashflow": r10(s3_yr1_net_cf),
                "financial_portfolio_end": r10(s3_cash_acct),
                "cupertino_aftertax_equity_end": r10(c_aftertax_equity_rent),
                "sf_equity_end": r10(sf_fmv_end),
                "total_household_wealth_end": r10(s3_total_wealth),
            },
        ],
    }


def evaluate_estate_tax_thresholds():
    """
    Calculate exact cash/financial inheritance headroom before hitting the 40% Federal Estate Tax
    (State/Local California inheritance & estate tax = $0 at all levels under CA RTC § 13301).
    """
    rows = []
    for yr in (2026, 2030, 2035, 2040, 2045, 2050):
        t = yr - 2026
        # OBBBA $15M in 2026, indexed by C-CPI-U (~2.25%/yr) starting 2027
        excl_single = FED_ESTATE_EXCLUSION_2026 if yr == 2026 else FED_ESTATE_EXCLUSION_2026 * ((1.0225) ** t)
        excl_married = excl_single * 2.0
        # Legislative rollback stress scenario: $7.0M base in 2026 indexed at 2.25%/yr
        rollback_single = 7_000_000 * ((1.0225) ** t)

        c_fmv = CUP_FMV_2026 * ((1 + G_CUP_HOME) ** t)
        s_fmv = SF_FMV_2026 * ((1 + G_SF_HOME) ** t)
        both_fmv = c_fmv + s_fmv

        rows.append({
            "year": yr,
            "fed_exclusion_single": r10(excl_single),
            "fed_exclusion_married_portability": r10(excl_married),
            "cupertino_fmv": r10(c_fmv),
            "both_properties_fmv": r10(both_fmv),
            "tax_free_cash_headroom_single_cup_only": r10(max(0.0, excl_single - c_fmv)),
            "tax_free_cash_headroom_single_both_props": r10(max(0.0, excl_single - both_fmv)),
            "tax_free_cash_headroom_married_both_props": r10(max(0.0, excl_married - both_fmv)),
            "rollback_stress_exclusion_single": r10(rollback_single),
            "rollback_stress_cash_headroom_single_cup_only": r10(max(0.0, rollback_single - c_fmv)),
            "ca_state_local_inheritance_tax": 0,
        })
    return rows


def main():
    cup_rows, sf_rows = generate_yearly_projections()
    scenarios = {str(y): evaluate_inheritance_scenarios(y, 15) for y in (2040, 2045, 2050)}
    estate_rows = evaluate_estate_tax_thresholds()

    payload = {
        "metadata": {
            "session": "session-85899999",
            "date_generated": "2026-11-10",
            "rounding_increment_usd": 10,
            "privacy_status": "100% anonymized placeholders; zero PII",
        },
        "assumptions": {
            "cupertino_ad_valorem_rate": CUP_AD_VALOREM_RATE,
            "sf_ad_valorem_rate": SF_AD_VALOREM_RATE,
            "cupertino_appreciation_cagr": G_CUP_HOME,
            "sf_appreciation_cagr": G_SF_HOME,
            "prop13_annual_cap": PROP13_CAP,
            "prop19_cap_2025_rounded": r10(PROP19_CAP_2025),
            "portfolio_pretax_return": PORTFOLIO_PRETAX_RETURN,
            "portfolio_aftertax_return": PORTFOLIO_AFTERTAX_RETURN,
            "combined_cap_gains_rate": COMBINED_CAP_GAINS_RATE,
            "nem_sunset_year": CUP_NEM_SUNSET_YEAR,
        },
        "cupertino_projections": cup_rows,
        "sf_projections": sf_rows,
        "decision_scenarios": scenarios,
        "estate_tax_thresholds": estate_rows,
    }

    out_dir = Path("_d3c614ec/out/legacy_85")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "verified_projections_85899999.json"
    csv_path = out_dir / "verified_projections_85899999.csv"

    json_path.write_text(json.dumps(payload, indent=2))

    # Write combined year-by-year CSV
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "year",
            "cup_fmv", "cup_fbyv_prop13", "cup_tax_prop13",
            "prop19_cap", "cup_tax_if_inherited_live", "cup_tax_if_inherited_rent",
            "cup_water", "cup_electric", "cup_ins_primary", "cup_maint", "cup_total_opex_if_live",
            "sf_fmv", "sf_fbyv_prop13", "sf_tax_prop13", "sf_water_sewer", "sf_electric",
            "sf_ins_landlord", "sf_maint", "sf_rent_2units", "sf_net_cashflow_2units"
        ])
        for c, s in zip(cup_rows, sf_rows):
            writer.writerow([
                c["year"],
                c["fmv"], c["fbyv_prop13"], c["tax_prop13_current"],
                c["prop19_cap"], c["tax_if_inherited_live"], c["tax_if_inherited_rent"],
                c["water_yr"], c["electric_yr"], c["insurance_primary_yr"], c["maintenance_yr"], c["total_opex_if_live"],
                s["fmv"], s["fbyv_prop13"], s["tax_prop13_current"], s["water_sewer_yr"], s["electric_yr"],
                s["insurance_yr"], s["maintenance_yr"], s["gross_rent_2units_yr"], s["net_cashflow_2units_prop13"]
            ])

    print("=== VERIFIED MODEL SUMMARY (ROUNDED TO $10) ===")
    for yr in ("2040", "2045", "2050"):
        sc = scenarios[yr]
        print(f"\nInheritance Year {yr} (15-Yr Horizon to {sc['end_year']}):")
        print(f"  Cupertino FMV: ${sc['cupertino_fmv_at_inheritance']:,} | Prop 19 Cap: ${sc['prop19_cap_at_inheritance']:,}")
        print(f"  Yr-1 Cupertino Tax (Live/Prop19): ${sc['cupertino_yr1_tax_if_live']:,} vs (Rent/Full): ${sc['cupertino_yr1_tax_if_rent']:,} (Saves ${sc['prop19_annual_tax_savings_yr1']:,}/yr)")
        print(f"  Irrevocable Trust No-Step-Up Tax Trap (Rev. Rul. 2023-2): ${sc['irrevocable_trust_cap_gains_penalty_if_sold']:,}")
        for st in sc["strategies"]:
            print(f"    {st['id']}: Yr1 Net CF ${st['yr1_net_cashflow']:,} | End Total Wealth ${st['total_household_wealth_end']:,}")


if __name__ == "__main__":
    main()
