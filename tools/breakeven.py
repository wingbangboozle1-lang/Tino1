import sys, json
sys.path.insert(0,"tools")
from build_data import run
from model import ASSUME

def be(inv, metric="npv"):
    lo,hi=0.0,0.20
    for _ in range(70):
        m=(lo+hi)/2
        r,_,_,_=run(2045,m,inv)
        hold=max(r["live"][metric],r["rent"][metric])
        if hold<r["sell"][metric]: lo=m
        else: hi=m
    return lo

out={"breakeven_appreciation_pct":{}}
for iv in [0.05,0.07,0.085]:
    v=be(iv); out["breakeven_appreciation_pct"][f"invest_{iv}"]=round(v*100,2)
    print(f"portfolio {iv:.1%} -> hold wins only if appreciation > {v*100:.2f}%/yr")

# how much is the Prop 19 exclusion actually worth?
print("\n--- Prop 19 exclusion value (annual tax delta, 2045 transfer) ---")
r1,_,_,_=run(2045,0.04,0.07)
import model
Al=model.build_A(2045,0.04,0.04,"live"); Ar=model.build_A(2045,0.04,0.04,"rent")
for y in (2045,2050,2060,2070):
    i=y-2026
    print(f" {y}: live tax {Al[i]['tax']:>8,}  rent tax {Ar[i]['tax']:>8,}  saving {Ar[i]['tax']-Al[i]['tax']:>8,}")
out["prop19_annual_saving"]={str(y):Ar[y-2026]["tax"]-Al[y-2026]["tax"] for y in (2045,2050,2060,2070)}
tot=sum(Ar[i]["tax"]-Al[i]["tax"] for i in range(2045-2026,2071-2026))
out["prop19_total_saving_2045_2070"]=tot
print(f" cumulative 2045-2070: {tot:,}")

# Hold-then-sell-later scenarios
print("\n--- Sell timing ---")
for sell_yr in (2045,2047,2050,2055,2060):
    import model
    A=model.build_A(sell_yr,0.04,0.04,"live")
    mv=A[sell_yr-2026]["market"]
    basis=model.OWNER["A_value_2026"]*1.04**(2045-2026)
    gain=mv-basis
    costs=mv*0.05
    fed=max(0,gain-500000)*(0.20+0.038); ca=max(0,gain-500000)*0.093
    net=mv-costs-fed-ca
    print(f" sell {sell_yr}: MV {mv:>12,}  after costs+tax {net:>12,}")
    out.setdefault("sell_timing",{})[str(sell_yr)]=round(net,0)
json.dump(out,open("data/breakeven.json","w"),indent=1)
