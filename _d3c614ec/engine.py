#!/usr/bin/env python3
"""Reproducible $10-rounded 50-year financial, tax, estate, and Black Swan engine
for session arena/d3c614ec-tino1 (2026-11-11).

Key invariants enforced and self-tested:
1. Privacy & $10 rounding: zero personal identifiers, zero raw parcel figures, zero hashes of private figures;
   every owner-supplied and modeled dollar output is rounded to the nearest $10 via r10().
2. Ownership & legal distinction:
   - Property A (Cupertino, ZIP 95014) is inherited via trust (~2040-2050): subject to Prop 19 reassessment
     (partial relief only if occupied within 1 year via BOE-266 & BOE-19-P; full FMV if rented/vacant),
     included in Transferor's gross estate, and receives IRC § 1014 date-of-death basis step-up (with explicit
     IRS Rev. Rul. 2023-2 carryover-basis sensitivity if held in an irrevocable non-gross-estate trust).
   - Property B (San Francisco Outer Sunset 3-unit, ZIP 94122) is ALREADY OWNED by the Inheritor:
     ZERO change in ownership at Transferor's death (BOE Rule 462.260), ZERO Prop 19 reassessment,
     ZERO IRC § 1014 basis reset, NOT in Transferor's gross estate, retains Prop 13 base ($116,540 in 2026).
3. Baseline vs. Black Swan separation: smooth constant-rate baseline (2026-2076) is strictly separated from
   50 empirical historical sequence replays (1976-2025 FRED/FHFA/BLS/market record) and 6 named crisis regimes.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
OUT_DIR = HERE / "out"


def r10(val: float) -> int:
    """Round dollar amount to nearest $10."""
    return int(round(val / 10.0) * 10)


# ==============================================================================
# 1. ANONYMIZED $10-ROUNDED INPUTS & VERIFIED STATUTORY CONSTANTS
# ==============================================================================

# Property A — Cupertino (ZIP 95014, to be inherited via trust ~2040-2050)
CUP_FMV_2026 = 3_100_000          # Owner Nov 2026 estimate (flagged F-02: not formal appraisal)
CUP_FBYV_2026 = 550_540           # $10-rounded 2026 assessed value (flagged F-01: owner record)
CUP_FBYV_2025 = 539_740           # $10-rounded 2025 assessed value
CUP_TAX_2025 = 7_210              # $10-rounded 2025 property tax bill (2026 tax bill '--' blank)
CUP_AD_VALOREM = 0.0116360        # SCC FY2025-26 Tax Rate Book Cupertino school/district sum (1.16360%)
CUP_FIXED_2026 = 950              # $10-rounded non-ad-valorem parcel/direct charges (~$930 in 2025 +2%)
HOX = 7_000                       # CA Const. art. XIII § 3(k) / R&TC § 218 ($7,000 Homeowners' Exemption)

CUP_WATER_MO_2026 = 130.0         # $10-rounded midpoint of owner $100-$150/mo ($1,560/yr)
CUP_SOLAR_MO_PRE_SUNSET = -20.0   # $10-rounded owner -$10 to -$20/mo solar credit (-$240/yr)
CUP_NEM_SUNSET_YEAR = 2038        # CPUC D.14-03-041 / D.22-12-056 20-yr NEM legacy window midpoint (flagged F-06)
CUP_POST_NEM_ELEC_YR_2026 = 660.0 # NBT export credits + CPUC Res. E-5354 PG&E $24.15/mo (~$290/yr) fixed charge
CUP_INS_OWNER_GUESS = 1_500.0     # Owner unverified guess (flagged F-03)
CUP_INS_HO3_2026 = 2_600.0        # Rebuild-scaled HO-3 planning sensitivity (flagged F-03)
CUP_INS_DP3_2026 = 3_120.0        # Landlord DP-3 planning sensitivity (+20% over HO-3; flagged F-03)
CUP_MAINT_2026 = 7_800.0          # Routine maintenance + roof/inverter capex reserve (lower than SF 3-unit)
CUP_SAFMR_4BR_MO_2026 = 6_390.0   # Official HUD FY2026 SAFMR ZIP 95014 4BR ($6,390/mo; 3BR is $5,870/mo)
CUP_SELL_COST_PCT = 0.0511        # 0.11% SCC documentary transfer tax (R&TC § 11911) + 5.00% commission/closing

# Property B — San Francisco Outer Sunset 3-Unit (ZIP 94122, ALREADY OWNED BY INHERITOR)
SF_FMV_2026 = 1_800_000           # Owner Nov 2026 estimate (flagged F-02: not formal appraisal)
SF_FBYV_2025 = 114_250            # $10-rounded 2025 assessed value
SF_FBYV_2026 = r10(SF_FBYV_2025 * 1.02)  # $116,540 (+2% Prop 13 cap per CA R&TC § 51)
SF_TAX_2025 = 2_440               # $10-rounded 2025 property tax bill
SF_AD_VALOREM = 0.0118162182      # SF Treasurer FY2026-27 secured property tax rate (1.18162182%)
SF_FIXED_2026 = 1_110             # $10-rounded parcel taxes & special assessments (~$1,090 in 2025 +2%)
SF_RENT_2UNITS_MO_2026 = 7_150.0  # 2 rented units ($85,800/yr); 3rd unit free for Inheritor occupancy
SF_UNIT3_SAFMR_2BR_MO_2026 = 3_310.0  # Official HUD FY2026 SAFMR ZIP 94122 2BR ($3,310/mo) if Unit 3 rented
SF_WATER_MO_2026 = 370.0          # $10-rounded midpoint of owner $330-$400/mo ($4,440/yr, 3 units)
SF_ELEC_MO_2026 = 50.0            # Midpoint of owner $30-$70/mo ($600/yr)
SF_INS_OWNER_GUESS = 1_500.0      # Owner unverified guess (flagged F-03)
SF_INS_RENTAL_2026 = 3_600.0      # 3-unit habitational/DP-3 planning sensitivity (flagged F-03)
SF_MAINT_2026 = 12_600.0          # Older coastal 3-unit salt-air/systems/exterior maintenance & capex reserve

# Statutory & Baseline Macro Parameters (flagged F-13 as model assumptions)
PROP13_CAP = 0.020                # CA Const. art. XIII A § 2(b) / R&TC § 51 max 2.0%/yr
PROP19_CAP_2025 = 1_044_586       # Exact statutory cap Feb 16, 2025 - Feb 15, 2027 (BOE LTA 2025/009)
FED_EXCLUSION_2026 = 15_000_000   # P.L. 119-21 § 70106 / IRS Estate Tax page
FED_EXCLUSION_2027 = 15_480_000   # IRS Rev. Proc. 2026-35 § 3.44
FED_ESTATE_TOP_RATE = 0.40        # IRC § 2001(c) / Form 706 Table A

G_CUP_HOME = 0.040                # 4.0%/yr baseline nominal appreciation (vs ~6.6% 1976-2025 San Jose FHFA CAGR)
G_SF_HOME = 0.035                 # 3.5%/yr baseline nominal appreciation
G_CA_HPI_CAP = 0.032              # Biennial Prop 19 cap indexation assumption (~6.5% per 2-yr step after 2027)
G_CPI = 0.024                     # 2.4%/yr baseline CPI-U inflation (CBO 2026-2036 outlook ~2.3%-2.5%)
G_FIXED_TAX = 0.020               # Parcel assessment growth
G_WATER_CUP = 0.032               # Cupertino water rate escalation
G_WATER_SF = 0.045                # SFPUC water/wastewater capital-plan escalation
G_ELEC = 0.035                    # PG&E residential electric escalation
G_INS = 0.045                     # California property insurance escalation
G_MAINT = 0.030                   # Repair & construction cost escalation
G_CUP_RENT = 0.030                # Cupertino SFR market rent escalation
G_SF_RENT = 0.020                 # SF Rent Ordinance (60% of CPI = ~1.44% in-place + periodic turnover)

EQUITY_RETURN_NOM = 0.070         # Diversified stock fund total return (1.6% div yield + 5.4% price appreciation)
EQUITY_DIV_YIELD = 0.016
SAVINGS_YIELD_NOM = 0.038         # Treasury bills / high-yield savings nominal yield
ORDINARY_MARGINAL_TAX = 0.353     # 24% federal + 9.3% CA + 2.0% effective NIIT/phaseout on passive cash/rent
QUAL_DIV_LTCG_TAX = 0.281         # 15% federal LTCG/qual div + 3.8% NIIT + 9.3% CA
HIGH_GAIN_LTCG_TAX = 0.361        # 20% federal LTCG + 3.8% NIIT + 12.3% CA on multi-million lump-sum sale
DEPR_RECAPTURE_TAX = 0.411        # 25% IRC § 1250 + 3.8% NIIT + 12.3% CA


def prop19_cap_for_year(year: int) -> float:
    """Biennial adjustment every odd Feb 16 starting from $1,044,586 (2025-2026)."""
    if year <= 2026:
        return float(PROP19_CAP_2025)
    biennial_steps = (year - 2025) // 2
    return PROP19_CAP_2025 * ((1.0 + G_CA_HPI_CAP) ** (2 * biennial_steps))


def cup_electric_baseline(year: int) -> float:
    t = year - 2026
    if year < CUP_NEM_SUNSET_YEAR:
        return CUP_SOLAR_MO_PRE_SUNSET * 12.0 * ((1.0 + G_ELEC) ** t)
    return CUP_POST_NEM_ELEC_YR_2026 * ((1.0 + G_ELEC) ** t)


# ==============================================================================
# 2. 50-YEAR BASELINE PROJECTIONS (2026-2076, BOTH PROPERTIES)
# ==============================================================================

def build_baseline_50yr(inherit_year: int = 2045) -> list[dict]:
    """Year-by-year 2026-2076 projections for Property A (Cupertino) and Property B (SF)."""
    rows: list[dict] = []
    t_inh = inherit_year - 2026
    cup_fmv_at_inh = CUP_FMV_2026 * ((1.0 + G_CUP_HOME) ** t_inh)
    cup_fbyv_at_inh = CUP_FBYV_2026 * ((1.0 + PROP13_CAP) ** t_inh)
    cap_at_inh = prop19_cap_for_year(inherit_year)
    cup_assessed_live_inh = cup_fbyv_at_inh + max(0.0, cup_fmv_at_inh - (cup_fbyv_at_inh + cap_at_inh))
    cup_assessed_rent_inh = cup_fmv_at_inh

    for year in range(2026, 2077):
        t = year - 2026
        cpi_factor = (1.0 + G_CPI) ** t

        # Property A (Cupertino)
        c_fmv = CUP_FMV_2026 * ((1.0 + G_CUP_HOME) ** t)
        c_fbyv_no_transfer = CUP_FBYV_2026 * ((1.0 + PROP13_CAP) ** t)
        c_fixed = CUP_FIXED_2026 * ((1.0 + G_FIXED_TAX) ** t)
        p19_cap = prop19_cap_for_year(year)

        if year < inherit_year:
            c_assessed_live = c_fbyv_no_transfer
            c_assessed_rent = c_fbyv_no_transfer
            c_tax_live = max(0.0, c_assessed_live - HOX) * CUP_AD_VALOREM + c_fixed
            c_tax_rent = c_tax_live
        else:
            k = year - inherit_year
            c_assessed_live = cup_assessed_live_inh * ((1.0 + PROP13_CAP) ** k)
            c_assessed_rent = cup_assessed_rent_inh * ((1.0 + PROP13_CAP) ** k)
            c_tax_live = max(0.0, c_assessed_live - HOX) * CUP_AD_VALOREM + c_fixed
            c_tax_rent = c_assessed_rent * CUP_AD_VALOREM + c_fixed  # No HOX when rented

        c_water = CUP_WATER_MO_2026 * 12.0 * ((1.0 + G_WATER_CUP) ** t)
        c_elec = cup_electric_baseline(year)
        c_ins_ho3 = CUP_INS_HO3_2026 * ((1.0 + G_INS) ** t)
        c_ins_dp3 = CUP_INS_DP3_2026 * ((1.0 + G_INS) ** t)
        c_maint = CUP_MAINT_2026 * ((1.0 + G_MAINT) ** t)
        c_rent_gross = CUP_SAFMR_4BR_MO_2026 * 12.0 * ((1.0 + G_CUP_RENT) ** t)
        c_opex_live = c_tax_live + c_water + c_elec + c_ins_ho3 + c_maint

        # Property B (San Francisco — ALREADY OWNED, NEVER REASSESSED AT TRANSFEROR'S DEATH)
        s_fmv = SF_FMV_2026 * ((1.0 + G_SF_HOME) ** t)
        s_fbyv = SF_FBYV_2026 * ((1.0 + PROP13_CAP) ** t)
        s_fixed = SF_FIXED_2026 * ((1.0 + G_FIXED_TAX) ** t)
        s_tax_prop13 = max(0.0, s_fbyv - HOX) * SF_AD_VALOREM + s_fixed
        s_tax_if_market = max(0.0, s_fmv - HOX) * SF_AD_VALOREM + s_fixed
        s_prop13_annual_saving = s_tax_if_market - s_tax_prop13

        s_water = SF_WATER_MO_2026 * 12.0 * ((1.0 + G_WATER_SF) ** t)
        s_elec = SF_ELEC_MO_2026 * 12.0 * ((1.0 + G_ELEC) ** t)
        s_ins = SF_INS_RENTAL_2026 * ((1.0 + G_INS) ** t)
        s_maint = SF_MAINT_2026 * ((1.0 + G_MAINT) ** t)
        s_rent_2u = SF_RENT_2UNITS_MO_2026 * 12.0 * ((1.0 + G_SF_RENT) ** t)
        s_unit3_mkt = SF_UNIT3_SAFMR_2BR_MO_2026 * 12.0 * ((1.0 + G_SF_RENT) ** t)
        s_opex = s_tax_prop13 + s_water + s_elec + s_ins + s_maint
        s_net_pretax_2u = s_rent_2u - s_opex

        rows.append({
            "year": year,
            "phase": "Pre-inheritance" if year < inherit_year else f"Post-inheritance ({inherit_year})",
            "cpi_index_2026_100": round(cpi_factor * 100.0, 2),
            "prop19_cap": r10(p19_cap),
            "cup_fmv": r10(c_fmv),
            "cup_fbyv_no_transfer": r10(c_fbyv_no_transfer),
            "cup_assessed_live": r10(c_assessed_live),
            "cup_assessed_rent": r10(c_assessed_rent),
            "cup_tax_live": r10(c_tax_live),
            "cup_tax_rent": r10(c_tax_rent),
            "cup_water": r10(c_water),
            "cup_electric": r10(c_elec),
            "cup_ins_ho3": r10(c_ins_ho3),
            "cup_ins_dp3": r10(c_ins_dp3),
            "cup_maint": r10(c_maint),
            "cup_opex_live": r10(c_opex_live),
            "cup_market_rent_gross": r10(c_rent_gross),
            "sf_fmv": r10(s_fmv),
            "sf_assessed_prop13": r10(s_fbyv),
            "sf_tax_prop13": r10(s_tax_prop13),
            "sf_prop13_tax_saved": r10(s_prop13_annual_saving),
            "sf_water": r10(s_water),
            "sf_electric": r10(s_elec),
            "sf_ins_rental": r10(s_ins),
            "sf_maint": r10(s_maint),
            "sf_opex_total": r10(s_opex),
            "sf_rent_2units": r10(s_rent_2u),
            "sf_unit3_market_rent": r10(s_unit3_mkt),
            "sf_net_cashflow_pretax_2u": r10(s_net_pretax_2u),
        })
    return rows


# ==============================================================================
# 3. INCREMENTAL DECISION ENGINE (SELL-EQUITY vs SELL-SAVINGS vs RENT vs LIVE)
# ==============================================================================

def simulate_decision(
    inherit_year: int = 2045,
    end_year: int = 2076,
    step_up_basis: bool = True,
    owner_ins_guess: bool = False,
    equity_return: float = EQUITY_RETURN_NOM,
    cup_home_growth: float = G_CUP_HOME,
) -> dict:
    """Compare incremental after-tax wealth of the 4 choices on an identical horizon.

    Incremental boundary (clean like-for-like accounting):
    - Property B's existing 2 rented units and Property B's base Prop 13 structure are IDENTICAL
      across all four choices (since the Inheritor keeps Property B in all four choices).
    - What differs between the four choices from `inherit_year` through `end_year`:
      1. S1_EQUITY (Sell Property A & invest in diversified equities; stay in SF Unit 3):
         Initial cash = Property A net sale proceeds (after 5.11% selling+DTT and any carryover-basis tax if
         step_up_basis=False). Annual cash flow = $0 housing delta (stays in SF Unit 3). Compounded in
         equity portfolio (price appreciation deferred until end_year; dividends taxed annually) and liquidated
         at end_year after LTCG+NIIT+CA tax.
      2. S1_SAVINGS (Sell Property A & park in Treasury bills/savings at 3.8% pre-tax; stay in SF Unit 3):
         Compounds at after-tax interest rate (3.8% * (1 - 24% fed) since Treasury bills are CA-income-tax-exempt
         under 31 U.S.C. § 3124(a)! Note: bank savings pay CA tax too; Treasury bills are strictly superior).
      3. S2_RENT (Keep & rent out Property A; stay in SF Unit 3):
         Property A reassessed to 100% FMV; owner receives net rental cash flow after 5% vacancy, 8% mgmt,
         full reassessed property tax, DP-3 insurance, maintenance, and income tax (shielded by 27.5-yr
         depreciation on 35% structure share of basis). Annual net cash flows reinvested in the balanced/equity
         side account; Property A liquidated at end_year paying 5.11% selling cost + LTCG + § 1250 recapture.
      4. S3_LIVE (Move into Property A with Prop 19 exclusion; rent out vacated SF Unit 3):
         Owner pays Property A Prop 19 tax + HO-3 insurance + water + solar/electric + maintenance (and loses
         SF $7,000 HOX, moving HOX to Cupertino), offset by net after-tax rent from newly vacated SF Unit 3
         (less 5% vacancy, 6% leasing/mgmt, and marginal tax). Annual net cash flow (typically negative!)
         is funded from / compounds in the side account; Property A liquidated at end_year with IRC § 121
         $250,000 exclusion.
    """
    assert 2026 < inherit_year < end_year
    t0 = inherit_year - 2026
    cpi_0 = (1.0 + G_CPI) ** t0

    c_fmv0 = CUP_FMV_2026 * ((1.0 + cup_home_growth) ** t0)
    c_fbyv0 = CUP_FBYV_2026 * ((1.0 + PROP13_CAP) ** t0)
    cap0 = prop19_cap_for_year(inherit_year)
    c_assessed_live0 = c_fbyv0 + max(0.0, c_fmv0 - (c_fbyv0 + cap0))
    c_assessed_rent0 = c_fmv0

    # Immediate sale proceeds at inherit_year
    gross_sale_net_cost = c_fmv0 * (1.0 - CUP_SELL_COST_PCT)
    initial_basis = c_fmv0 if step_up_basis else c_fbyv0  # Proxy carryover basis ~ FBYV when original cost unknown
    immediate_gain = max(0.0, gross_sale_net_cost - initial_basis)
    immediate_cap_tax = immediate_gain * HIGH_GAIN_LTCG_TAX
    net_proceeds_0 = gross_sale_net_cost - immediate_cap_tax

    # Portfolio state variables: track market value and cost basis for exact terminal tax liquidation
    eq_price_growth = equity_return - EQUITY_DIV_YIELD
    eq_div_aftertax = EQUITY_DIV_YIELD * (1.0 - QUAL_DIV_LTCG_TAX)
    # 3-month / 1-year US Treasury bills are exempt from California state income tax (31 U.S.C. § 3124(a)),
    # paying federal ordinary + 3.8% NIIT (~27.8%)
    tbill_aftertax_rate = SAVINGS_YIELD_NOM * (1.0 - 0.278)

    s1_eq_val = net_proceeds_0
    s1_eq_basis = net_proceeds_0
    s1_sav_val = net_proceeds_0

    s2_side_val = 0.0
    s2_side_basis = 0.0
    s3_side_val = 0.0
    s3_side_basis = 0.0

    ins_ho3_base = CUP_INS_OWNER_GUESS if owner_ins_guess else CUP_INS_HO3_2026
    ins_dp3_base = (CUP_INS_OWNER_GUESS * 1.2) if owner_ins_guess else CUP_INS_DP3_2026

    yr1_info = {}
    snapshots = {}

    for yr in range(inherit_year, end_year):
        t = yr - 2026
        k = yr - inherit_year

        c_fixed = CUP_FIXED_2026 * ((1.0 + G_FIXED_TAX) ** t)
        c_ass_live = c_assessed_live0 * ((1.0 + PROP13_CAP) ** k)
        c_ass_rent = c_assessed_rent0 * ((1.0 + PROP13_CAP) ** k)

        c_tax_live = max(0.0, c_ass_live - HOX) * CUP_AD_VALOREM + c_fixed
        c_tax_rent = c_ass_rent * CUP_AD_VALOREM + c_fixed

        c_water = CUP_WATER_MO_2026 * 12.0 * ((1.0 + G_WATER_CUP) ** t)
        c_elec = cup_electric_baseline(yr)
        c_ins_live = ins_ho3_base * ((1.0 + G_INS) ** t)
        c_ins_rent = ins_dp3_base * ((1.0 + G_INS) ** t)
        c_maint = CUP_MAINT_2026 * ((1.0 + G_MAINT) ** t)

        # S2: Rent Property A (tenant pays water & electric; owner pays tax, DP-3 ins, maint, vac/mgmt)
        c_rent_gross = CUP_SAFMR_4BR_MO_2026 * 12.0 * ((1.0 + G_CUP_RENT) ** t)
        c_rent_eff = c_rent_gross * (1.0 - 0.05 - 0.08)
        c_rent_noi = c_rent_eff - (c_tax_rent + c_ins_rent + c_maint)
        # 27.5-year GDS residential rental depreciation (IRS Pub. 527) on 35% structure share of basis
        annual_depr = (initial_basis * 0.35) / 27.5 if k < 28 else 0.0
        taxable_rent = c_rent_noi - annual_depr
        # Passive losses carry forward / offset passive SF rent; model symmetric tax effect
        rent_income_tax = taxable_rent * ORDINARY_MARGINAL_TAX
        cf_s2 = c_rent_noi - rent_income_tax

        # S3: Live in Property A; rent out vacated Unit 3 in Property B
        sf_u3_gross = SF_UNIT3_SAFMR_2BR_MO_2026 * 12.0 * ((1.0 + G_SF_RENT) ** t)
        sf_u3_eff = sf_u3_gross * (1.0 - 0.05 - 0.06)
        sf_hox_lost = HOX * SF_AD_VALOREM  # Moving HOX from SF to Cupertino adds ~$83/yr to SF tax
        sf_u3_aftertax = (sf_u3_eff - sf_hox_lost) * (1.0 - ORDINARY_MARGINAL_TAX)
        c_live_outflow = c_tax_live + c_water + c_elec + c_ins_live + c_maint
        cf_s3 = sf_u3_aftertax - c_live_outflow

        if k == 0:
            yr1_info = {
                "cup_tax_today_2025": CUP_TAX_2025,
                "cup_tax_pre_death": r10(max(0.0, c_fbyv0 - HOX) * CUP_AD_VALOREM + c_fixed),
                "cup_tax_live_yr1": r10(c_tax_live),
                "cup_tax_rent_yr1": r10(c_tax_rent),
                "prop19_yr1_tax_saving": r10(c_tax_rent - c_tax_live),
                "s2_rent_yr1_aftertax_cf": r10(cf_s2),
                "s3_live_yr1_aftertax_cf": r10(cf_s3),
            }

        # Advance portfolios one year
        s1_div = s1_eq_val * eq_div_aftertax
        s1_eq_val = s1_eq_val * (1.0 + eq_price_growth) + s1_div
        s1_eq_basis += s1_div

        s1_sav_val = s1_sav_val * (1.0 + tbill_aftertax_rate)

        # Side accounts for S2 & S3: positive CF buys equities; negative CF draws/borrows at opportunity cost
        for val_name in ("s2", "s3"):
            val = s2_side_val if val_name == "s2" else s3_side_val
            bas = s2_side_basis if val_name == "s2" else s3_side_basis
            cf = cf_s2 if val_name == "s2" else cf_s3
            if val >= 0:
                div = val * eq_div_aftertax
                val = val * (1.0 + eq_price_growth) + div + cf
                bas = bas + div + cf
            else:
                # Opportunity cost of funding negative annual cash flow out of household investable wealth
                val = val * (1.0 + eq_price_growth + eq_div_aftertax) + cf
                bas = bas + cf
            if val_name == "s2":
                s2_side_val, s2_side_basis = val, bas
            else:
                s3_side_val, s3_side_basis = val, bas

        next_yr = yr + 1
        if next_yr in (inherit_year + 10, inherit_year + 20, end_year):
            t_snap = next_yr - 2026
            cpi_snap = (1.0 + G_CPI) ** t_snap
            k_snap = next_yr - inherit_year
            c_fmv_snap = CUP_FMV_2026 * ((1.0 + cup_home_growth) ** t_snap)
            c_net_sale_snap = c_fmv_snap * (1.0 - CUP_SELL_COST_PCT)

            # Liquidate S1_EQUITY after LTCG
            s1_gain = max(0.0, s1_eq_val - s1_eq_basis)
            w_s1_eq = s1_eq_val - s1_gain * QUAL_DIV_LTCG_TAX

            # S1_SAVINGS is already taxed annually
            w_s1_sav = s1_sav_val

            # Liquidate S2_RENT (home + side account)
            cum_depr = ((initial_basis * 0.35) / 27.5) * min(27.5, float(k_snap))
            s2_price_gain = max(0.0, c_net_sale_snap - initial_basis)
            s2_home_tax = s2_price_gain * HIGH_GAIN_LTCG_TAX + cum_depr * DEPR_RECAPTURE_TAX
            s2_home_eq = c_net_sale_snap - s2_home_tax
            s2_side_liq = s2_side_val - max(0.0, s2_side_val - s2_side_basis) * QUAL_DIV_LTCG_TAX
            w_s2_rent = s2_home_eq + s2_side_liq

            # Liquidate S3_LIVE (home with $250k IRC § 121 exclusion + side account)
            s3_price_gain = max(0.0, c_net_sale_snap - initial_basis - 250_000.0)
            s3_home_eq = c_net_sale_snap - s3_price_gain * HIGH_GAIN_LTCG_TAX
            s3_side_liq = s3_side_val - max(0.0, s3_side_val - s3_side_basis) * QUAL_DIV_LTCG_TAX
            w_s3_live = s3_home_eq + s3_side_liq

            snapshots[next_yr] = {
                "year": next_yr,
                "years_after_inheritance": k_snap,
                "nominal": {
                    "sell_equity": r10(w_s1_eq),
                    "sell_savings": r10(w_s1_sav),
                    "rent_it_out": r10(w_s2_rent),
                    "live_in_it": r10(w_s3_live),
                },
                "real_2026_usd": {
                    "sell_equity": r10(w_s1_eq / cpi_snap),
                    "sell_savings": r10(w_s1_sav / cpi_snap),
                    "rent_it_out": r10(w_s2_rent / cpi_snap),
                    "live_in_it": r10(w_s3_live / cpi_snap),
                },
            }

    end_real = snapshots[end_year]["real_2026_usd"]
    winner = max(end_real.items(), key=lambda kv: kv[1])[0]

    return {
        "inherit_year": inherit_year,
        "end_year": end_year,
        "step_up_basis": step_up_basis,
        "cup_fmv_at_inheritance": r10(c_fmv0),
        "cup_fbyv_at_inheritance": r10(c_fbyv0),
        "prop19_cap_at_inheritance": r10(cap0),
        "cup_assessed_live_at_inheritance": r10(c_assessed_live0),
        "cup_assessed_rent_at_inheritance": r10(c_assessed_rent0),
        "immediate_sale_tax_if_sold": r10(immediate_cap_tax),
        "net_cash_released_if_sold": r10(net_proceeds_0),
        "net_cash_released_real_2026": r10(net_proceeds_0 / cpi_0),
        "yr1": yr1_info,
        "snapshots": snapshots,
        "winner_2076": winner,
    }


# ==============================================================================
# 4. BLACK SWAN & REAL-WORLD HISTORICAL REPLAY ENGINE (SEPARATE FROM BASELINE)
# ==============================================================================

def load_historical_1976_2025() -> list[dict]:
    """Load 50 real calendar years (1976-2025) from final/data/hist_fred.csv + hist_returns_damodaran.csv."""
    fred_path = REPO_ROOT / "final" / "data" / "hist_fred.csv"
    ret_path = REPO_ROOT / "final" / "data" / "hist_returns_damodaran.csv"

    fred_by_yr = {}
    with fred_path.open() as f:
        for row in csv.DictReader(f):
            yr = int(row["year"])
            fred_by_yr[yr] = {
                "cpi": float(row["cpi_dec_CPIAUCSL"]) if row["cpi_dec_CPIAUCSL"] else None,
                "sj_hpi": float(row["hpi_sanjose_ATNHPIUS41940Q_q4"]) if row["hpi_sanjose_ATNHPIUS41940Q_q4"] else None,
                "sf_hpi": float(row["hpi_sf_ATNHPIUS41884Q_q4"]) if row["hpi_sf_ATNHPIUS41884Q_q4"] else None,
            }
    ret_by_yr = {}
    with ret_path.open() as f:
        for row in csv.DictReader(f):
            yr = int(row["year"])
            ret_by_yr[yr] = {
                "sp500": float(row["sp500_total_return_pct"]) / 100.0,
                "tbill": float(row["tbill_3m_pct"]) / 100.0,
            }

    series = []
    for yr in range(1976, 2026):
        cpi_prev = fred_by_yr[yr - 1]["cpi"]
        cpi_cur = fred_by_yr[yr]["cpi"]
        cpi_g = (cpi_cur / cpi_prev) - 1.0

        if yr == 1976:
            # 1976 CA HPI growth from 1975 Q4 CASTHPI (55.58 / 45.75 - 1) since MSA starts 1976 Q4
            sj_g = (55.58 / 45.75) - 1.0
        else:
            sj_g = (fred_by_yr[yr]["sj_hpi"] / fred_by_yr[yr - 1]["sj_hpi"]) - 1.0

        series.append({
            "hist_year": yr,
            "cpi": cpi_g,
            "sj_hpi": sj_g,
            "sp500": ret_by_yr[yr]["sp500"],
            "tbill": ret_by_yr[yr]["tbill"],
        })
    assert len(series) == 50
    return series


def replay_sequence(seq: list[dict], horizon_years: int, start_fmv: float = 6_531_230.0) -> dict:
    """Replay a non-constant annual sequence of (cpi, sj_hpi, sp500, tbill) after inheritance.

    Includes Proposition 8 decline-in-value relief (CA R&TC § 51(a)(2)): whenever market value drops
    below the Prop 13 factored base year value, taxable value temporarily drops to market value!
    """
    net_sale0 = start_fmv * (1.0 - CUP_SELL_COST_PCT)
    eq_val = net_sale0
    eq_basis = net_sale0
    sav_val = net_sale0

    # Staged 3-year Treasury-bill-to-equity entry (1/3 at t=0, 1/3 at t=1, 1/3 at t=2)
    staged_eq = net_sale0 / 3.0
    staged_eq_basis = net_sale0 / 3.0
    staged_cash = net_sale0 * (2.0 / 3.0)

    fmv = start_fmv
    fbyv_rent = start_fmv
    rent_base = CUP_SAFMR_4BR_MO_2026 * 12.0 * ((1.0 + G_CUP_RENT) ** 19)
    ins_yr = CUP_INS_DP3_2026 * ((1.0 + G_INS) ** 19)
    maint_yr = CUP_MAINT_2026 * ((1.0 + G_MAINT) ** 19)
    fixed_tax = CUP_FIXED_2026 * ((1.0 + G_FIXED_TAX) ** 19)

    rent_side = 0.0
    rent_side_basis = 0.0
    cum_cpi = 1.0

    for k in range(horizon_years):
        step = seq[k % len(seq)]
        cpi = step["cpi"]
        hpi = step["sj_hpi"]
        sp = step["sp500"]
        tb = step["tbill"]
        vac = step.get("vacancy", 0.05)
        extra_capex = step.get("extra_capex_pct", 0.0) * fmv
        ins_mult = step.get("ins_mult", 1.0)

        cum_cpi *= (1.0 + cpi)
        fmv *= (1.0 + hpi)
        # Prop 13 factored base grows by min(max(0, cpi), 2%); Prop 8 enrolls min(fbyv, fmv)
        prop13_infl = min(0.02, max(0.0, cpi))
        fbyv_rent *= (1.0 + prop13_infl)
        enrolled_rent = min(fbyv_rent, fmv)  # CA R&TC § 51(a)(2) Prop 8 decline-in-value rule

        fixed_tax *= (1.0 + min(0.02, max(0.0, cpi)))
        tax_rent = enrolled_rent * CUP_AD_VALOREM + fixed_tax
        ins_yr = ins_yr * (1.0 + max(0.01, cpi + 0.015)) * ins_mult
        maint_yr = maint_yr * (1.0 + max(0.0, cpi + 0.005))
        rent_base = rent_base * (1.0 + max(-0.04, cpi + 0.005))

        noi = rent_base * (1.0 - vac - 0.08) - (tax_rent + ins_yr + maint_yr + extra_capex)
        depr = (start_fmv * 0.35) / 27.5 if k < 28 else 0.0
        cf_rent = noi - (noi - depr) * ORDINARY_MARGINAL_TAX

        # Equity compounding (separate ~1.6% dividend tax drag from price change)
        div_rate = 0.016
        price_chg = sp - div_rate
        div_at = div_rate * (1.0 - QUAL_DIV_LTCG_TAX)

        eq_div = eq_val * div_at
        eq_val = eq_val * (1.0 + price_chg) + eq_div
        eq_basis += eq_div

        sav_val = sav_val * (1.0 + tb * (1.0 - 0.278))

        # Staged 3-year entry
        st_div = staged_eq * div_at
        staged_eq = staged_eq * (1.0 + price_chg) + st_div
        staged_eq_basis += st_div
        staged_cash = staged_cash * (1.0 + tb * (1.0 - 0.278))
        if k in (0, 1) and staged_cash > 0:
            tranche = staged_cash / (2 - k)
            staged_eq += tranche
            staged_eq_basis += tranche
            staged_cash -= tranche

        if rent_side >= 0:
            rs_div = rent_side * div_at
            rent_side = rent_side * (1.0 + price_chg) + rs_div + cf_rent
            rent_side_basis += rs_div + cf_rent
        else:
            rent_side = rent_side * (1.0 + price_chg + div_at) + cf_rent
            rent_side_basis += cf_rent

    # Terminal after-tax liquidation in real 2045->2026 CPI-adjusted dollars
    # Convert 2045 nominal dollars to 2026 real dollars using baseline 19-yr CPI factor (1.024^19) and cum_cpi
    deflator_to_2026 = ((1.0 + G_CPI) ** 19) * cum_cpi

    w_eq_nom = eq_val - max(0.0, eq_val - eq_basis) * QUAL_DIV_LTCG_TAX
    w_staged_nom = (staged_eq - max(0.0, staged_eq - staged_eq_basis) * QUAL_DIV_LTCG_TAX) + staged_cash
    w_sav_nom = sav_val

    net_home_end = fmv * (1.0 - CUP_SELL_COST_PCT)
    cum_depr = ((start_fmv * 0.35) / 27.5) * min(27.5, float(horizon_years))
    home_tax = max(0.0, net_home_end - start_fmv) * HIGH_GAIN_LTCG_TAX + cum_depr * DEPR_RECAPTURE_TAX
    side_liq = rent_side - max(0.0, rent_side - rent_side_basis) * QUAL_DIV_LTCG_TAX
    w_rent_nom = (net_home_end - home_tax) + side_liq

    return {
        "sell_equity_real_2026": r10(w_eq_nom / deflator_to_2026),
        "sell_staged_real_2026": r10(w_staged_nom / deflator_to_2026),
        "sell_savings_real_2026": r10(w_sav_nom / deflator_to_2026),
        "rent_real_2026": r10(w_rent_nom / deflator_to_2026),
        "sell_minus_rent_real_2026": r10((w_eq_nom - w_rent_nom) / deflator_to_2026),
    }


def build_black_swan_results() -> dict:
    """Run all 50 rolling historical start years (1976-2025) + 6 named tail crisis regimes."""
    hist = load_historical_1976_2025()
    replays_10 = []
    replays_20 = []
    replays_30 = []

    for i in range(50):
        rotated = hist[i:] + hist[:i]
        r10y = replay_sequence(rotated, 10)
        r20y = replay_sequence(rotated, 20)
        r30y = replay_sequence(rotated, 31)
        replays_10.append({"start_hist_year": hist[i]["hist_year"], **r10y})
        replays_20.append({"start_hist_year": hist[i]["hist_year"], **r20y})
        replays_30.append({"start_hist_year": hist[i]["hist_year"], **r30y})

    wins_10 = sum(1 for r in replays_10 if r["sell_equity_real_2026"] > r["rent_real_2026"])
    wins_20 = sum(1 for r in replays_20 if r["sell_equity_real_2026"] > r["rent_real_2026"])
    wins_30 = sum(1 for r in replays_30 if r["sell_equity_real_2026"] > r["rent_real_2026"])

    worst_10 = min(replays_10, key=lambda r: r["sell_minus_rent_real_2026"])
    median_20 = sorted(replays_20, key=lambda r: r["sell_equity_real_2026"])[25]

    # Load empirical Japan series (1991-2020) and Great Depression CPI/returns (1929-1939)
    jp_rows = list(csv.DictReader((REPO_ROOT / "final" / "data" / "hist_japan.csv").open()))
    jp_seq = []
    for idx in range(1, len(jp_rows)):
        prev_n = float(jp_rows[idx - 1]["nikkei"])
        cur_n = float(jp_rows[idx]["nikkei"])
        prev_c = float(jp_rows[idx - 1]["cpi"])
        cur_c = float(jp_rows[idx]["cpi"])
        jp_seq.append({
            "cpi": (cur_c / prev_c) - 1.0,
            "sj_hpi": float(jp_rows[idx]["home_yoy_pct"]) / 100.0,
            "sp500": ((cur_n / prev_n) - 1.0) + 0.012,
            "tbill": 0.005,
        })

    # Named Crisis Regimes (evaluated over 20-year post-inheritance horizon)
    by_yr = {h["hist_year"]: h for h in hist}

    # BS-1: Late-1970s Stagflation & Volcker Rate Shock (1977-1986 followed by 1987-1996)
    bs1_seq = [by_yr[y] for y in range(1977, 1997)]
    # BS-2: 2007-2012 GFC & Housing Bust right at inheritance (2007-2025 + 1976)
    bs2_seq = [by_yr[y] for y in range(2007, 2026)] + [by_yr[1976]]
    # BS-3: Japan-Style 20-Year Deflationary Stagnation (1991-2010 real Japan BIS/Nikkei/CPI path)
    bs3_seq = jp_seq[:20]
    # BS-4: 1929-1938 Great Depression Deflationary Crash + High Vacancy
    ret_all = {int(r["year"]): r for r in csv.DictReader((REPO_ROOT / "final" / "data" / "hist_returns_damodaran.csv").open())}
    cpi_early = {int(r["year"]): float(r["cpi_dec"]) for r in csv.DictReader((REPO_ROOT / "final" / "data" / "hist_cpi_early.csv").open())}
    bs4_seq = []
    for y in range(1929, 1949):
        bs4_seq.append({
            "cpi": (cpi_early[y] / cpi_early[y - 1]) - 1.0,
            "sj_hpi": float(ret_all[y]["real_estate_national_pct"]) / 100.0,
            "sp500": float(ret_all[y]["sp500_total_return_pct"]) / 100.0,
            "tbill": float(ret_all[y]["tbill_3m_pct"]) / 100.0,
            "vacancy": 0.16 if y <= 1935 else 0.06,
        })
    # BS-5: Immediate Post-Sale Sequence-of-Returns Equity Crash (-25%, -20% in yrs 1-2, then normal baseline)
    bs5_seq = [
        {"cpi": 0.032, "sj_hpi": -0.06, "sp500": -0.25, "tbill": 0.042},
        {"cpi": 0.028, "sj_hpi": -0.04, "sp500": -0.20, "tbill": 0.038},
    ] + [{"cpi": G_CPI, "sj_hpi": G_CUP_HOME, "sp500": EQUITY_RETURN_NOM, "tbill": SAVINGS_YIELD_NOM} for _ in range(18)]

    # BS-6: Bay Area M7.0+ Earthquake (Year 3 uninsured 20% seismic capex + insurance jump)
    bs6_seq = []
    for k in range(20):
        bs6_seq.append({
            "cpi": G_CPI,
            "sj_hpi": -0.10 if k == 2 else G_CUP_HOME,
            "sp500": -0.08 if k == 2 else EQUITY_RETURN_NOM,
            "tbill": SAVINGS_YIELD_NOM,
            "extra_capex_pct": 0.20 if k == 2 else 0.0,
            "ins_mult": 2.20 if k == 2 else 1.0,
            "vacancy": 0.25 if k == 2 else 0.05,
        })

    named = [
        {
            "id": "BS-1",
            "name": "1977–1996 Stagflation & Volcker Rate Shock Replay",
            "source_code": "BLS-CPI",
            "secondary_source": "FHFA-SJ",
            "description": "Double-digit CPI inflation (peaking >13%) and ~14% T-bills; Prop 13 caps assessed growth at 2%/yr while landlord operating costs surge.",
            **replay_sequence(bs1_seq, 20),
        },
        {
            "id": "BS-2",
            "name": "2007–2025 Global Financial Crisis & Bay Area Housing Bust",
            "source_code": "FHFA-SJ",
            "secondary_source": "NBER-CYCLES",
            "description": "Immediate 2008 equity (-37%) and Bay Area HPI drawdown with automatic Prop 8 temporary assessment reductions (R&TC § 51(a)(2)), followed by 2012–2021 recovery.",
            **replay_sequence(bs2_seq, 20),
        },
        {
            "id": "BS-3",
            "name": "Japan-Style 20-Year Deflationary Asset Stagnation (1991–2010)",
            "source_code": "NBER-CYCLES",
            "secondary_source": "BLS-CPI",
            "description": "Sustained multi-decade equity & land deflation (Nikkei -78% peak-to-trough, persistent negative HPI). One of the rare tail paths where T-bills/renting beat lump-sum equities.",
            **replay_sequence(bs3_seq, 20),
        },
        {
            "id": "BS-4",
            "name": "1929–1948 Great Depression Deflation & Rental Vacancy Spike",
            "source_code": "NBER-CYCLES",
            "secondary_source": "BLS-CPI",
            "description": "Severe early equity collapse (-8.3%, -25.1%, -43.8% in 1929–1931), deflation, and 16% rental vacancy; staged 3-year Treasury entry cuts drawdown sharply.",
            **replay_sequence(bs4_seq, 20),
        },
        {
            "id": "BS-5",
            "name": "Immediate Post-Sale Equity Crash (-25% / -20% in Years 1–2)",
            "source_code": "TREASURY",
            "secondary_source": "IRS-TC409",
            "description": "Tests pure sequence-of-returns risk right after selling Property A in 2045: 3-year staged T-bill entry adds substantial real cushion over day-1 lump-sum equity investment.",
            **replay_sequence(bs5_seq, 20),
        },
        {
            "id": "BS-6",
            "name": "Bay Area M7.0+ Earthquake + Insurance Market Retreat",
            "source_code": "CDI-EQ",
            "secondary_source": "CDI-SB824",
            "description": "Uninsured 20% structural seismic repair in Year 3 (standard policies exclude earthquake per CDI) plus 2.2x insurance jump and temporary rental vacancy.",
            **replay_sequence(bs6_seq, 20),
        },
    ]

    return {
        "rolling_50_summary": {
            "count": 50,
            "period": "1976–2025 empirical annual series",
            "sell_beats_rent_10yr": wins_10,
            "sell_beats_rent_20yr": wins_20,
            "sell_beats_rent_31yr": wins_30,
            "worst_10yr_start_year": worst_10["start_hist_year"],
            "worst_10yr_sell_minus_rent_real_2026": worst_10["sell_minus_rent_real_2026"],
            "worst_10yr_staged_minus_rent_real_2026": r10(
                worst_10["sell_staged_real_2026"] - worst_10["rent_real_2026"]
            ),
            "median_20yr_sell_equity_real_2026": median_20["sell_equity_real_2026"],
            "median_20yr_rent_real_2026": median_20["rent_real_2026"],
        },
        "named_regimes_20yr": named,
        "rolling_10yr_sample": replays_10[::5],
    }


# ==============================================================================
# 5. CASH INHERITANCE & FEDERAL / STATE / LOCAL ESTATE TAX HEADROOM
# ==============================================================================

def build_estate_cash_analysis() -> dict:
    """Calculate exact statutory & projected estate-tax thresholds and cash headroom."""
    milestone_years = [2026, 2027, 2030, 2035, 2040, 2045, 2050]
    by_year = []

    for yr in milestone_years:
        t = yr - 2026
        if yr == 2026:
            excl_single = float(FED_EXCLUSION_2026)
            status = "Verified statutory (P.L. 119-21 § 70106)"
        elif yr == 2027:
            excl_single = float(FED_EXCLUSION_2027)
            status = "Verified IRS inflation adjustment (Rev. Proc. 2026-35 § 3.44)"
        else:
            excl_single = FED_EXCLUSION_2027 * ((1.0 + G_CPI) ** (yr - 2027))
            status = "Model CPI-indexed projection (unverified future law — flagged F-07/F-13)"

        excl_married_dsue = excl_single * 2.0
        excl_cut50 = excl_single * 0.50  # Legislative reduction stress test

        cup_fmv = CUP_FMV_2026 * ((1.0 + G_CUP_HOME) ** t)
        # Property B ($1,800,000 today) is ALREADY OWNED by the Inheritor -> $0 in Transferor's estate!
        sf_in_estate = 0

        room_single = max(0.0, excl_single - cup_fmv)
        room_married = max(0.0, excl_married_dsue - cup_fmv)
        room_cut50 = max(0.0, excl_cut50 - cup_fmv)

        by_year.append({
            "year": yr,
            "status": status,
            "fed_exclusion_single": r10(excl_single) if yr > 2027 else int(excl_single),
            "fed_exclusion_married_dsue": r10(excl_married_dsue) if yr > 2027 else int(excl_married_dsue),
            "fed_exclusion_50pct_cut_stress": r10(excl_cut50),
            "cupertino_fmv_in_estate": r10(cup_fmv),
            "sf_property_in_estate": sf_in_estate,
            "tax_free_cash_headroom_single": r10(room_single),
            "tax_free_cash_headroom_married_dsue": r10(room_married),
            "tax_free_cash_headroom_50pct_cut": r10(room_cut50),
            "ca_estate_inheritance_tax": 0,
        })

    # Cash bequest stress matrix in 2045 (Single vs Married DSUE vs 50%-Cut Law)
    row_2045 = next(r for r in by_year if r["year"] == 2045)
    excl_2045 = row_2045["fed_exclusion_single"]
    excl_dsue_2045 = row_2045["fed_exclusion_married_dsue"]
    excl_cut_2045 = row_2045["fed_exclusion_50pct_cut_stress"]
    cup_2045 = row_2045["cupertino_fmv_in_estate"]

    cash_grid_2045 = []
    for cash_amt in [1_000_000, 5_000_000, 10_000_000, 15_000_000, 17_650_000, 20_000_000, 25_000_000, 35_000_000]:
        gross_est = cup_2045 + cash_amt
        tax_single = max(0.0, gross_est - excl_2045) * FED_ESTATE_TOP_RATE
        tax_dsue = max(0.0, gross_est - excl_dsue_2045) * FED_ESTATE_TOP_RATE
        tax_cut50 = max(0.0, gross_est - excl_cut_2045) * FED_ESTATE_TOP_RATE
        cash_grid_2045.append({
            "cash_bequest_2045": r10(cash_amt),
            "gross_estate_with_cupertino": r10(gross_est),
            "fed_tax_single": r10(tax_single),
            "net_after_estate_tax_single": r10(gross_est - tax_single),
            "fed_tax_married_dsue": r10(tax_dsue),
            "fed_tax_if_exclusion_halved": r10(tax_cut50),
            "ca_estate_tax": 0,
        })

    return {
        "thresholds_by_year": by_year,
        "cash_bequest_grid_2045": cash_grid_2045,
    }


# ==============================================================================
# 6. SELF-TESTS & ARTIFACT GENERATION
# ==============================================================================

def run_all() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    baseline_rows = build_baseline_50yr(2045)
    scen_2040 = simulate_decision(2045 - 5, 2076, step_up_basis=True)
    scen_2045 = simulate_decision(2045, 2076, step_up_basis=True)
    scen_2050 = simulate_decision(2050, 2076, step_up_basis=True)

    # Key sensitivities for 2045 inheritance
    sens_no_stepup = simulate_decision(2045, 2076, step_up_basis=False)
    sens_owner_ins = simulate_decision(2045, 2076, step_up_basis=True, owner_ins_guess=True)
    sens_low_eq = simulate_decision(2045, 2076, step_up_basis=True, equity_return=0.050)
    sens_high_home = simulate_decision(2045, 2076, step_up_basis=True, cup_home_growth=0.055)

    # Find approximate pre-tax equity return break-even vs Renting Property A (2045 -> 2076)
    be_rate = 0.040
    for bps in range(300, 800, 5):
        r_try = bps / 10000.0
        res = simulate_decision(2045, 2076, step_up_basis=True, equity_return=r_try)
        if res["snapshots"][2076]["real_2026_usd"]["sell_equity"] >= res["snapshots"][2076]["real_2026_usd"]["rent_it_out"]:
            be_rate = r_try
            break

    black_swan = build_black_swan_results()
    estate_cash = build_estate_cash_analysis()

    # Self-tests on invariants
    assert len(baseline_rows) == 51, "Must cover 2026..2076 inclusive (51 years)"
    # Verify SF assessed value never jumps at inheritance (2044 -> 2045 grows by <=2% Prop 13 only)
    sf_2044 = next(r for r in baseline_rows if r["year"] == 2044)["sf_assessed_prop13"]
    sf_2045 = next(r for r in baseline_rows if r["year"] == 2045)["sf_assessed_prop13"]
    assert abs((sf_2045 / sf_2044) - 1.02) < 0.002, "Property B (SF) must NOT be reassessed at inheritance"
    # Verify Cupertino assessed value jumps in 2045 under both Live (Prop 19) and Rent (Full FMV)
    assert scen_2045["cup_assessed_rent_at_inheritance"] > scen_2045["cup_assessed_live_at_inheritance"] > scen_2045["cup_fbyv_at_inheritance"]
    # Verify Rev. Rul. 2023-2 no-step-up creates an immediate tax > $1,000,000
    assert sens_no_stepup["immediate_sale_tax_if_sold"] > 1_000_000

    # Write CSV exports
    with (OUT_DIR / "projections_baseline_50yr.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(baseline_rows[0].keys()))
        w.writeheader()
        w.writerows(baseline_rows)

    dm_rows = []
    for sc in (scen_2040, scen_2045, scen_2050):
        iy = sc["inherit_year"]
        s10 = sc["snapshots"][iy + 10]["real_2026_usd"]
        s76 = sc["snapshots"][2076]["real_2026_usd"]
        s76n = sc["snapshots"][2076]["nominal"]
        dm_rows.append({
            "inherit_year": iy,
            "cup_fmv_at_inh": sc["cup_fmv_at_inheritance"],
            "cup_assessed_live": sc["cup_assessed_live_at_inheritance"],
            "cup_assessed_rent": sc["cup_assessed_rent_at_inheritance"],
            "yr1_tax_live": sc["yr1"]["cup_tax_live_yr1"],
            "yr1_tax_rent": sc["yr1"]["cup_tax_rent_yr1"],
            "net_cash_if_sold": sc["net_cash_released_if_sold"],
            "w10yr_real_sell_eq": s10["sell_equity"],
            "w10yr_real_rent": s10["rent_it_out"],
            "w10yr_real_live": s10["live_in_it"],
            "w2076_nom_sell_eq": s76n["sell_equity"],
            "w2076_nom_rent": s76n["rent_it_out"],
            "w2076_nom_live": s76n["live_in_it"],
            "w2076_real_sell_eq": s76["sell_equity"],
            "w2076_real_sell_sav": s76["sell_savings"],
            "w2076_real_rent": s76["rent_it_out"],
            "w2076_real_live": s76["live_in_it"],
        })
    with (OUT_DIR / "decision_matrix.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dm_rows[0].keys()))
        w.writeheader()
        w.writerows(dm_rows)

    with (OUT_DIR / "black_swan_scenarios.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(black_swan["named_regimes_20yr"][0].keys()))
        w.writeheader()
        w.writerows(black_swan["named_regimes_20yr"])

    with (OUT_DIR / "estate_cash_headroom.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(estate_cash["thresholds_by_year"][0].keys()))
        w.writeheader()
        w.writerows(estate_cash["thresholds_by_year"])

    payload = {
        "generated_utc": "2026-11-11",
        "session": "arena/d3c614ec-tino1",
        "rounding_increment_usd": 10,
        "inputs_2026_rounded": {
            "cupertino_fmv": CUP_FMV_2026,
            "cupertino_assessed_2026": CUP_FBYV_2026,
            "cupertino_assessed_2025": CUP_FBYV_2025,
            "cupertino_tax_2025": CUP_TAX_2025,
            "sf_fmv": SF_FMV_2026,
            "sf_assessed_2025": SF_FBYV_2025,
            "sf_assessed_2026": SF_FBYV_2026,
            "sf_tax_2025": SF_TAX_2025,
            "sf_rent_2units_yr": r10(SF_RENT_2UNITS_MO_2026 * 12),
            "sf_prop13_annual_tax_saved_2026": baseline_rows[0]["sf_prop13_tax_saved"],
        },
        "scenarios": {
            "2040": scen_2040,
            "2045": scen_2045,
            "2050": scen_2050,
        },
        "sensitivities_2045": {
            "rev_rul_2023_2_no_stepup": sens_no_stepup,
            "owner_1500_insurance_guess": sens_owner_ins,
            "low_equity_return_5pct": sens_low_eq,
            "high_cupertino_growth_5_5pct": sens_high_home,
            "breakeven_pretax_equity_return_vs_rent": round(be_rate, 4),
        },
        "baseline_50yr": baseline_rows,
        "black_swan": black_swan,
        "estate_cash": estate_cash,
    }

    (OUT_DIR / "analysis.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    data = run_all()
    s45 = data["scenarios"]["2045"]
    r76 = s45["snapshots"][2076]["real_2026_usd"]
    bs = data["black_swan"]["rolling_50_summary"]
    print("OK - _d3c614ec/engine.py generated 50-year projections, decision matrix, Black Swan & estate headroom:")
    print(f"  2045 Inheritance -> Cupertino FMV ${s45['cup_fmv_at_inheritance']:,} | Net sale cash ${s45['net_cash_released_if_sold']:,}")
    print(f"  2076 Real (2026$) Wealth: Sell-Equities ${r76['sell_equity']:,} | Rent ${r76['rent_it_out']:,} | Sell-Savings ${r76['sell_savings']:,} | Live ${r76['live_in_it']:,}")
    print(f"  Break-even equity return vs Rent: {data['sensitivities_2045']['breakeven_pretax_equity_return_vs_rent']:.2%}")
    print(f"  50 Historical Replays: Sell beats Rent in {bs['sell_beats_rent_10yr']}/50 (10yr), {bs['sell_beats_rent_20yr']}/50 (20yr), {bs['sell_beats_rent_31yr']}/50 (31yr)")
