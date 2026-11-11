"""Projection model: Property A (Cupertino 95014, trust-inherited ~2040-2050) +
Property B (San Francisco 94122, already owned by the Inheritor — NOT transferred).

Remediated in session arena/d3c614ec-tino1 (2026-11-11):
- Purged exact unrounded parcel figures; all owner/modeled dollar inputs & outputs rounded to $10.
- Closed CR-43-3: Property B (SF 94122) is already owned by the Inheritor (no transfer/reassessment/step-up).
- Closed CR-85-5: Separated ad valorem tax rate from fixed parcel/direct charges + $7,000 Homeowners' Exemption.
- Closed CR-85-6: Added CPUC 20-yr NEM sunset (D.14-03-041 / D.22-12-056), PG&E $24.15/mo fixed charge
  (D.24-05-028 / Res. E-5354), SF Rent Board 60%-of-CPI rule, and IRS Rev. Rul. 2023-2 basis sensitivity.
- Default output directory moved to _d3c614ec/out/legacy_36 so data/ (claimed by active session 8f259271) is untouched.
"""
import csv
import json
import pathlib
import sys


def r10(x: float) -> int:
    return int(round(x / 10.0) * 10)


# --- $10-rounded owner inputs + official statutory anchors (zero raw parcel figures) ---
CUP = dict(
    value2026=3_100_000,
    assessed2026=550_540,
    assessed2025=539_740,
    tax2025=7_210,
    ad_valorem_rate=0.0116360,   # Santa Clara County FY2025-26 Tax Rate Book (Cupertino school/district sum)
    fixed_charges2026=950,       # Non-ad-valorem parcel/direct charges (~$930 in 2025 +2%, rounded to $10)
    hox=7_000,                   # CA Const. art. XIII § 3(k) / R&TC § 218 ($7,000 Homeowners' Exemption)
)
SF = dict(
    value2026=1_800_000,
    assessed2025=114_250,
    assessed2026=116_540,        # r10(114_250 * 1.02) per CA R&TC § 51
    tax2025=2_440,
    ad_valorem_rate=0.01181622,  # SF Treasurer FY2026-27 secured property tax rate (1.18162182%)
    fixed_charges2026=1_110,     # Parcel taxes & special assessments (~$1,090 in 2025 +2%, rounded to $10)
    hox=7_000,                   # Owner occupies Unit 3 -> $7,000 Homeowners' Exemption eligible
)

G_HOME_CUP = 0.040
G_HOME_SF = 0.035
G_ASSESSED = 0.020
G_FIXED = 0.020
G_INS = 0.045
G_WATER_C = 0.032
G_WATER_SF = 0.045
G_ELEC = 0.035
G_MAINT = 0.030
G_RENT_CUP = 0.030
G_RENT_SF = 0.022  # Reflects SF Rent Ordinance 60%-of-CPI cap (1.6% in 2026-27) + periodic turnover
NEM_SUNSET_YEAR = 2038  # Pre-2026 NEM 1.0/2.0 20-year legacy window expires <=2046; 2038 midpoint


def cup_electric_yr(year: int) -> float:
    n = year - 2026
    if year < NEM_SUNSET_YEAR:
        return -180.0 * ((1 + G_ELEC) ** n)  # -$15/mo midpoint (-$10 to -$20/mo owner range) under NEM legacy
    # Post-NEM sunset: NBT export credits + PG&E Tier 3 $24.15/mo (~$290/yr in 2026$) Base Services Charge
    return 660.0 * ((1 + G_ELEC) ** n)


def project_cupertino() -> list[dict]:
    rows = []
    for y in range(2026, 2077):
        n = y - 2026
        value = CUP["value2026"] * ((1 + G_HOME_CUP) ** n)
        assessed = CUP["assessed2026"] * ((1 + G_ASSESSED) ** n)
        fixed = CUP["fixed_charges2026"] * ((1 + G_FIXED) ** n)
        tax = max(0.0, assessed - CUP["hox"]) * CUP["ad_valorem_rate"] + fixed
        water = 125.0 * 12 * ((1 + G_WATER_C) ** n)  # Midpoint of $100-$150/mo rounded
        elec = cup_electric_yr(y)
        ins = 2_600.0 * ((1 + G_INS) ** n)
        maint = 7_800.0 * ((1 + G_MAINT) ** n)
        rows.append(
            dict(
                year=y,
                value=r10(value),
                assessed=r10(assessed),
                tax=r10(tax),
                water=r10(water),
                electric=r10(elec),
                insurance=r10(ins),
                maintenance=r10(maint),
                rent=0,
                total_cost=r10(tax + water + elec + ins + maint),
            )
        )
    return rows


def project_sf() -> list[dict]:
    """Property B (SF 94122) is ALREADY OWNED by the Inheritor: never reassessed at Transferor's death."""
    rows = []
    for y in range(2026, 2077):
        n = y - 2026
        value = SF["value2026"] * ((1 + G_HOME_SF) ** n)
        assessed = SF["assessed2026"] * ((1 + G_ASSESSED) ** n)
        fixed = SF["fixed_charges2026"] * ((1 + G_FIXED) ** n)
        tax = max(0.0, assessed - SF["hox"]) * SF["ad_valorem_rate"] + fixed
        water = 365.0 * 12 * ((1 + G_WATER_SF) ** n)  # Midpoint of $330-$400/mo
        elec = 50.0 * 12 * ((1 + G_ELEC) ** n)        # Midpoint of $30-$70/mo
        ins = 3_600.0 * ((1 + G_INS) ** n)
        maint = 12_600.0 * ((1 + G_MAINT) ** n)
        rent = 7_150.0 * 12 * ((1 + G_RENT_SF) ** n)  # 2 rented units; Unit 3 owner-occupiable
        rows.append(
            dict(
                year=y,
                value=r10(value),
                assessed=r10(assessed),
                tax=r10(tax),
                water=r10(water),
                electric=r10(elec),
                insurance=r10(ins),
                maintenance=r10(maint),
                rent=r10(rent),
                total_cost=r10(tax + water + elec + ins + maint),
            )
        )
    return rows


def scenario(year: int) -> dict:
    n = year - 2026
    cval = CUP["value2026"] * ((1 + G_HOME_CUP) ** n)
    cbase = CUP["assessed2026"] * ((1 + G_ASSESSED) ** n)
    fixed = CUP["fixed_charges2026"] * ((1 + G_FIXED) ** n)
    # Biennial CA FHFA HPI cap indexing from BOE LTA 2025/009 ($1,044,586 for 2025-02-16..2027-02-15)
    steps = max(0, (year - 2025) // 2)
    cap = 1_044_586 * ((1.0215) ** steps)
    live_assessed = cbase + max(0.0, cval - cbase - cap)
    live_tax = max(0.0, live_assessed - CUP["hox"]) * CUP["ad_valorem_rate"] + fixed
    full_tax = cval * CUP["ad_valorem_rate"] + fixed  # No HOX when rented out
    # Official HUD FY2026 SAFMR 95014 4BR = $6,390/mo escalated
    gross_rent = 6_390.0 * 12 * ((1 + G_RENT_CUP) ** n)
    net_rent = gross_rent * (1.0 - 0.05 - 0.08)
    ins = 3_120.0 * ((1 + G_INS) ** n)
    maint = 7_800.0 * ((1 + G_MAINT) ** n)
    rent_scenario_net = net_rent - full_tax - ins - maint
    # Sell at inheritance: 5.11% selling + SCC transfer tax; IRC § 1014 step-up if included in gross estate
    sell_net_stepup = cval * (1.0 - 0.0511)
    # Sensitivity under IRS Rev. Rul. 2023-2 (irrevocable trust outside gross estate -> no § 1014 step-up)
    approx_carryover_gain = max(0.0, sell_net_stepup - cbase)
    rev_rul_2023_2_tax_hit = approx_carryover_gain * (0.20 + 0.038 + 0.123)
    sell_net_no_stepup = sell_net_stepup - rev_rul_2023_2_tax_hit
    invest_10yr_stocks = sell_net_stepup * (1.058 ** 10)  # After-tax diversified equity compounding
    invest_10yr_savings = sell_net_stepup * (1.024 ** 10)  # After-tax T-bill/savings compounding
    keep_home_10yr = (cval * ((1 + G_HOME_CUP) ** 10)) * (1.0 - 0.0511)
    return dict(
        year=year,
        market=r10(cval),
        factored_base=r10(cbase),
        cap=r10(cap),
        live_assessed=r10(live_assessed),
        live_tax=r10(live_tax),
        full_tax=r10(full_tax),
        gross_rent=r10(gross_rent),
        rent_scenario_net=r10(rent_scenario_net),
        sell_net=r10(sell_net_stepup),
        sell_net_no_stepup_rr2023_2=r10(sell_net_no_stepup),
        invest_10yr=r10(invest_10yr_stocks),
        invest_10yr_savings=r10(invest_10yr_savings),
        keep_home_10yr=r10(keep_home_10yr),
    )


def main() -> None:
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("_d3c614ec/out/legacy_36")
    target.mkdir(parents=True, exist_ok=True)
    cup = project_cupertino()
    sf = project_sf()
    for name, rows in [("cupertino_projection.csv", cup), ("sanfrancisco_projection.csv", sf)]:
        with open(target / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    scen = [scenario(y) for y in (2040, 2045, 2050)]
    with open(target / "scenario_comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(scen[0].keys()))
        w.writeheader()
        w.writerows(scen)
    with open(target / "model_summary.json", "w") as f:
        json.dump(
            dict(
                cup_ad_valorem_rate=CUP["ad_valorem_rate"],
                sf_ad_valorem_rate=SF["ad_valorem_rate"],
                sf_reassessed_at_inheritance=False,
                scenarios=scen,
            ),
            f,
            indent=2,
        )
    print(f"Cupertino ad valorem {CUP['ad_valorem_rate']:.5%} | SF ad valorem {SF['ad_valorem_rate']:.6%} (SF never reassessed)")
    for s in scen:
        print(s)
    print(f"Wrote {target}/*.csv + model_summary.json")


if __name__ == "__main__":
    main()
