"""
Definitive comparison: terminal net worth at horizon + discounted cash flows.
Methodology:
  * Every scenario ends with everything liquidated at HORIZON, after real taxes.
  * Wealth = cumulative free cash flow (invested at portfolio rate) + liquidation proceeds.
  * All flows discounted to the transfer year at the portfolio rate -> single NPV figure.
"""
import json, sys
sys.path.insert(0, "tools")
from model import (SRC, OWNER, ASSUME, r10, prop19_cap,
                   build_A, build_B, costs_A, costs_B, rents_B, sf_transfer_tax)

HORIZON = 2070
BASE_INH = 2045

def ca_cap_gains_tax(gain):
    """CA taxes cap gains as ordinary income. Model blended marginal 9.3%."""
    return max(0.0, gain) * 0.093

def fed_cap_gains_tax(gain, excluded=0):
    g = max(0.0, gain - excluded)
    return g * (SRC["fed_ltcg_top"] + SRC["niit"])   # conservative: top bracket + NIIT

def run(inh, appr, inv_ret, verbose=False):
    A_live = build_A(inh, appr, appr, OWNER["A_rate_observed"], "live")
    A_rent = build_A(inh, appr, appr, OWNER["A_rate_observed"], "rent")
    B      = build_B(inh, appr, OWNER["B_rate_observed"], SRC["sf_secured_rate"])
    cA_l = costs_A(A_live, True, appr); cA_r = costs_A(A_rent, False, appr)
    cB   = costs_B(B); rB = rents_B(inh, ASSUME["sf_rent_growth"])

    gross_g = inv_ret - ASSUME["invest_tax_drag"]
    n = HORIZON - inh + 1
    A_end_mv = A_live[-1]["market"]; A_end_mv_r = A_rent[-1]["market"]
    B_end_mv = B[-1]["market"]

    # ---- liquidation at HORIZON (identical rules for all scenarios) ----
    def liquidate_A(mv):
        """A was inherited -> basis = FMV at 2045. If occupied 2 of last 5 yrs, s121 excludes 500k."""
        basis = OWNER["A_value_2026"]*(1+appr)**(inh-2026)
        gain = mv - basis
        costs = mv*ASSUME["sell_cost_pct"]
        # owner-occupied path gets s121; rental path does not (depreciation not modeled)
        return mv - costs, gain

    res = {}

    # ================= LIVE =================
    flows, port = [], 0.0
    for y in range(inh, HORIZON+1):
        i = y-2026
        rent = rB[i]["gross_2units"]*1.5          # 3 SF units rented
        net = rent - cB[i]["total"] - A_live[i]["tax"] - cA_l[i]["total"] - B[i]["tax_observed"]
        flows.append(net)
    cash_A, gain_A = liquidate_A(A_end_mv)
    cash_B = B_end_mv*(1-ASSUME["sell_cost_pct"]) - sf_transfer_tax(B_end_mv)
    basis_B = OWNER["B_value_2026"]*(1+appr)**(inh-2026)
    gain_B = B_end_mv - basis_B
    tax_B = fed_cap_gains_tax(gain_B) + ca_cap_gains_tax(gain_B)
    tax_A = fed_cap_gains_tax(gain_A, SRC["irc121_joint"]) + ca_cap_gains_tax(max(0,gain_A-SRC["irc121_joint"]))
    res["live"] = {"flows":flows, "term_A":cash_A - tax_A, "term_B":cash_B - tax_B,
                   "a_end":A_end_mv, "taxA_end":A_live[-1]["tax"],
                   "assessA_end":A_live[-1]["assessed"]}

    # ================= RENT =================
    flows = []
    for y in range(inh, HORIZON+1):
        i = y-2026
        cu = 3483*12*(1+ASSUME["rent_growth"])**(y-2026)   # Cupertino SFH gross rent
        net = rB[i]["gross_2units"] + cu - cB[i]["total"] - A_rent[i]["tax"] - cA_r[i]["total"] - B[i]["tax_observed"]
        flows.append(net)
    cash_A, gain_A = liquidate_A(A_end_mv_r)
    cash_B = B_end_mv*(1-ASSUME["sell_cost_pct"]) - sf_transfer_tax(B_end_mv)
    tax_A = fed_cap_gains_tax(gain_A) + ca_cap_gains_tax(gain_A)   # no s121: not owner-occupied
    tax_B = fed_cap_gains_tax(gain_B) + ca_cap_gains_tax(gain_B)
    res["rent"] = {"flows":flows, "term_A":cash_A - tax_A, "term_B":cash_B - tax_B,
                   "a_end":A_end_mv_r, "taxA_end":A_rent[-1]["tax"],
                   "assessA_end":A_rent[-1]["assessed"]}

    # ================= SELL AT TRANSFER =================
    mv_t = OWNER["A_value_2026"]*(1+appr)**(inh-2026)
    basis_t = mv_t                                   # S14 step-up
    gain_t = mv_t - basis_t
    costs_t = mv_t*ASSUME["sell_cost_pct"]
    proceeds = mv_t - costs_t - fed_cap_gains_tax(gain_t) - ca_cap_gains_tax(gain_t)
    flows, port = [], proceeds
    for y in range(inh, HORIZON+1):
        i = y-2026
        wd = port*0.04
        net = rB[i]["gross_2units"] - cB[i]["total"] - B[i]["tax_observed"] + wd
        flows.append(net)
        port = port*(1+gross_g) - wd
    cash_B = B_end_mv*(1-ASSUME["sell_cost_pct"]) - sf_transfer_tax(B_end_mv)
    tax_B = fed_cap_gains_tax(gain_B) + ca_cap_gains_tax(gain_B)
    res["sell"] = {"flows":flows, "term_A":port, "term_B":cash_B - tax_B,
                   "proceeds":proceeds, "a_end":0, "taxA_end":0, "assessA_end":0}

    # ---- wealth accumulation with re-investment at gross_g ----
    for k,v in res.items():
        wealth = 0.0
        for f in v["flows"]:
            wealth = wealth*(1+gross_g) + f
        v["wealth_ops"] = wealth
        v["terminal"] = v["term_A"] + v["term_B"]
        v["net_worth"] = wealth + v["terminal"]
        # NPV of (flows + terminal) discounted to transfer year
        v["npv"] = sum(f/(1+inv_ret)**t for t,f in enumerate(v["flows"])) + v["terminal"]/(1+inv_ret)**(n-1)
        v["y1"] = v["flows"][0]
        v["cum_ops"] = sum(v["flows"])
    return res

def report(res, label):
    print(f"\n=== {label} ===")
    for k in ("live","rent","sell"):
        v = res[k]
        print(f"  {k:5s}  NPV@2045={r10(v['npv']):>13,}  networth2070={r10(v['net_worth']):>13,}"
              f"  cum_ops={r10(v['cum_ops']):>13,}  y1cash={r10(v['y1']):>11,}")
    best = max(("live","rent","sell"), key=lambda k: res[k]["npv"])
    print(f"  --> NPV winner: {best.upper()}")

if __name__ == "__main__":
    out = {}
    for appr in [0.02,0.03,0.04,0.05]:
        for inv in [0.05,0.07,0.085]:
            r = run(BASE_INH, appr, inv)
            out[f"{appr}_{inv}"] = {k:{"npv":r10(r[k]["npv"]),"nw":r10(r[k]["net_worth"])} for k in r}
            report(r, f"appr={appr:.0%} invest={inv:.1%}")
    json.dump(out, open("data/sensitivity.json","w"), indent=1)
