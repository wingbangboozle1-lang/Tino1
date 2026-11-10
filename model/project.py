"""Projection model: Cupertino (95014) + SF (94122), 2026-2050. All outputs rounded to $10."""
import csv, json, pathlib

def r10(x): return int(round(x/10.0)*10)

# --- Inputs (owner records + official anchors) ---
CUP = dict(value2026=3_100_000, assessed2026=550_537, tax2025=7_207, assessed2025=539_743)
SF  = dict(value2026=1_800_000, assessed2025=114_248, tax2025=2_439)
CUP_RATE = CUP['tax2025']/CUP['assessed2025']   # ~1.335%
SF_RATE  = SF['tax2025']/SF['assessed2025']     # ~2.135% (flagged)
SF_ASSESSED2026 = SF['assessed2025']*1.02

G_HOME=0.03; G_ASSESSED=0.02; G_INS=0.05; G_WATER_C=0.03; G_WATER_SF=0.04
G_ELEC=0.03; G_MAINT=0.03; G_RENT=0.03

def project(base, assessed2026, rate, water_mo, elec_mo, ins_yr, maint_yr, rent_mo=None):
    rows=[]
    for y in range(2026,2051):
        n=y-2026
        value=base*(1+G_HOME)**n
        assessed=assessed2026*(1+G_ASSESSED)**n
        tax=assessed*rate
        water=water_mo*12*(1+G_WATER_C)**n if base>2_000_000 else water_mo*12*(1+G_WATER_SF)**n
        elec=elec_mo*12*(1+G_ELEC)**n
        ins=ins_yr*(1+G_INS)**n
        maint=maint_yr*(1+G_MAINT)**n
        rent=(rent_mo*12*(1+G_RENT)**n) if rent_mo else 0
        rows.append(dict(year=y,value=r10(value),assessed=r10(assessed),tax=r10(tax),
                         water=r10(water),electric=r10(elec),insurance=r10(ins),
                         maintenance=r10(maint),rent=r10(rent),
                         total_cost=r10(tax+water+elec+ins+maint)))
    return rows

cup = project(CUP['value2026'], CUP['assessed2026'], CUP_RATE, 130, -20, 2800, 8000)
sf  = project(SF['value2026'], SF_ASSESSED2026, SF_RATE, 360, 50, 3200, 12000, rent_mo=7150)

out=pathlib.Path('data'); out.mkdir(exist_ok=True)
for name, rows in [('cupertino_projection.csv',cup),('sanfrancisco_projection.csv',sf)]:
    with open(out/name,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# --- Scenario comparison at inheritance year (midpoint 2045; also 2040/2050) ---
def scenario(year):
    n=year-2026
    cval=CUP['value2026']*(1+G_HOME)**n
    cbase=CUP['assessed2026']*(1+G_ASSESSED)**n
    cap=1_044_586*(1.0215)**((year-2026)//2)  # biennial ~2.15% steps (planning est.)
    live_assessed=cbase+max(0,cval-cbase-cap)
    live_tax=live_assessed*CUP_RATE
    full_tax=cval*CUP_RATE
    # Rental income if Cupertino rented: $7,500/mo 2026 (planning est., 95014 SFR) +3%/yr
    gross_rent=7500*12*(1+G_RENT)**n
    vac=0.05; mgmt=0.08
    net_rent=gross_rent*(1-vac-mgmt)
    ins=2800*(1+G_INS)**n; maint=8000*(1+G_MAINT)**n; water=130*12*(1+G_WATER_C)**n
    rent_scenario_net=net_rent-full_tax-ins-maint-water
    # Sell at inheritance: 6% selling costs, step-up basis => ~$0 gain if sold promptly
    sell_net=cval*0.94
    invest_10yr=sell_net*(1.07**10)
    keep_home_10yr=cval*(1+G_HOME)**10  # equity if kept (before future costs)
    return dict(year=year,market=r10(cval),factored_base=r10(cbase),cap=r10(cap),
                live_assessed=r10(live_assessed),live_tax=r10(live_tax),full_tax=r10(full_tax),
                gross_rent=r10(gross_rent),rent_scenario_net=r10(rent_scenario_net),
                sell_net=r10(sell_net),invest_10yr=r10(invest_10yr),keep_home_10yr=r10(keep_home_10yr))

scen=[scenario(y) for y in (2040,2045,2050)]
with open(out/'scenario_comparison.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(scen[0].keys())); w.writeheader(); w.writerows(scen)
with open(out/'model_summary.json','w') as f:
    json.dump(dict(cup_rate=round(CUP_RATE,5),sf_rate=round(SF_RATE,5),scenarios=scen),f,indent=2)
print(f"Cupertino rate {CUP_RATE:.4%}  SF rate {SF_RATE:.4%}")
for s in scen: print(s)
print("Wrote data/*.csv + data/model_summary.json")
