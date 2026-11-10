import json, sys
sys.path.insert(0, "tools")
from model import (SRC, OWNER, ASSUME, YEARS, r10, prop19_cap,
                   build_A, build_B, costs_A, costs_B, rents_B, sf_transfer_tax)

INH = 2045          # base-case transfer year (midpoint of 2040-2050)
APPR = ASSUME["appr_base"]
HPI = ASSUME["appr_base"]

def A_rate(y):
    """Blended effective ad valorem rate: observed 2025 (1.335%) held flat."""
    return OWNER["A_rate_observed"]

A_live = build_A(INH, APPR, HPI, A_rate(0), "live")
A_rent = build_A(INH, APPR, HPI, A_rate(0), "rent")
B = build_B(INH, APPR, OWNER["B_rate_observed"], SRC["sf_secured_rate"])

cA_live = costs_A(A_live, True, APPR)
cA_rent = costs_A(A_rent, False, APPR)
cB      = costs_B(B)
rB      = rents_B(INH, ASSUME["sf_rent_growth"])

# ---------------------------------------------------------------- scenario math
HORIZON = 2070

def npv(flows, rate):
    return sum(f / (1 + rate) ** i for i, f in enumerate(flows))

def scenario_live():
    """Move into Cupertino (Prop 19 exclusion), rent all 3 SF units."""
    flows = []
    for i, y in enumerate(range(INH, HORIZON + 1)):
        a, ca, b, cb, rb = A_live[y-2026], cA_live[y-2026], B[y-2026], cB[y-2026], rB[y-2026]
        # SF: 3 units rented (3rd unit now vacant because owner moved out)
        sf_rent = rb["gross_2units"] * 1.5
        net = sf_rent - cb["total"] - a["tax"] - ca["total"] - b["tax_observed"]
        flows.append(net)
    return flows

def scenario_rent():
    """Rent Cupertino out (no Prop 19 exclusion), live in SF 3rd unit."""
    flows = []
    for i, y in enumerate(range(INH, HORIZON + 1)):
        a, ca, b, cb, rb = A_rent[y-2026], cA_rent[y-2026], B[y-2026], cB[y-2026], rB[y-2026]
        # Cupertino rent: SFH ~3BR/2BA, use 40th pct FMR proxy grown at market
        cupertino_rent = 3483 * 12 * (1 + ASSUME["rent_growth"]) ** (y - 2026)
        sf_rent = rb["gross_2units"]
        net = sf_rent + cupertino_rent - cb["total"] - a["tax"] - ca["total"] - b["tax_observed"]
        flows.append(net)
    return flows

def scenario_sell():
    """Sell Cupertino at transfer, reinvest net proceeds, live in SF 3rd unit."""
    sell_mv = OWNER["A_value_2026"] * (1 + APPR) ** (INH - 2026)
    basis = sell_mv                       # S14 step-up at death
    costs = sell_mv * ASSUME["sell_cost_pct"]
    tax = 0.0                             # basis == FMV, no gain
    net_proceeds = sell_mv - costs - tax
    flows = []
    invest = net_proceeds
    for i, y in enumerate(range(INH, HORIZON + 1)):
        b, cb, rb = B[y-2026], cB[y-2026], rB[y-2026]
        sf_rent = rb["gross_2units"]
        growth = ASSUME["invest_nominal"] - ASSUME["invest_tax_drag"]
        withdrawn = invest * 0.04
        flows_ops = sf_rent - cb["total"] - b["tax_observed"]
        invest = invest * (1 + growth) - withdrawn
        flows.append(flows_ops + withdrawn)
    return flows, net_proceeds

f_live = scenario_live()
f_rent = scenario_rent()
f_sell, proceeds = scenario_sell()

# terminal asset value 2070
A_end_live = A_live[-1]["market"]; B_end = B[-1]["market"]
A_end_rent = A_rent[-1]["market"]

disc = ASSUME["invest_nominal"]
res = {
 "transfer_year": INH,
 "horizon": HORIZON,
 "appreciation": APPR,
 "cupertino": {
   "market_2045": A_live[INH-2026]["market"],
   "assessed_2045_live": A_live[INH-2026]["assessed"],
   "assessed_2045_rent": A_rent[INH-2026]["assessed"],
   "tax_2045_live": A_live[INH-2026]["tax"],
   "tax_2045_rent": A_rent[INH-2026]["tax"],
   "tax_savings_2045": A_rent[INH-2026]["tax"] - A_live[INH-2026]["tax"],
   "prop19_cap_2045": r10(prop19_cap(INH, HPI)),
 },
 "sf": {
   "market_2045": B[INH-2026]["market"],
   "assessed_2045": B[INH-2026]["assessed"],
   "tax_2045_observed": B[INH-2026]["tax_observed"],
   "tax_2045_official": B[INH-2026]["tax_official"],
   "transfer_tax_2045": r10(sf_transfer_tax(B[INH-2026]["market"])),
 },
 "scenarios": {
   "live": {"npv_36y": r10(npv(f_live, disc)), "cum_net": r10(sum(f_live)),
            "end_assets": r10(A_end_live + B_end), "year1_net": r10(f_live[0])},
   "rent": {"npv_36y": r10(npv(f_rent, disc)), "cum_net": r10(sum(f_rent)),
            "end_assets": r10(A_end_rent + B_end), "year1_net": r10(f_rent[0])},
   "sell": {"npv_36y": r10(npv(f_sell, disc)), "cum_net": r10(sum(f_sell)),
            "end_assets": r10(proceeds * (1+disc-0.005) ** (HORIZON-INH) + B_end),
            "year1_net": r10(f_sell[0]), "net_proceeds": r10(proceeds)},
 },
}
print(json.dumps(res, indent=2))
