import json, sys, csv
sys.path.insert(0, "tools")
import model
from model import SRC, OWNER, ASSUME, YEARS, r10, prop19_cap, build_A, build_B, costs_A, costs_B, rents_B, sf_transfer_tax

HORIZON=2070; BASE_INH=2045
def npv(f,r): return sum(v/(1+r)**i for i,v in enumerate(f))

def ca_tax(g): return max(0.,g)*SRC["ca_capgain_rate"]
def fed_tax(g,excl=0): return max(0.,g-excl)*(SRC["fed_ltcg_top"]+SRC["niit"])

def run(inh, appr, inv):
    Al=build_A(inh,appr,appr,"live"); Ar=build_A(inh,appr,appr,"rent")
    B=build_B(inh,appr); cAl=costs_A(Al); cAr=costs_A(Ar); cB=costs_B(B); rB=rents_B(ASSUME["sf_rent_growth"])
    g=inv-ASSUME["invest_tax_drag"]; n=HORIZON-inh+1
    basisA=OWNER["A_value_2026"]*(1+appr)**(inh-2026)
    basisB=OWNER["B_value_2026"]*(1+appr)**(inh-2026)
    Aend=Al[-1]["market"]; Arend=Ar[-1]["market"]; Bend=B[-1]["market"]

    def liqB():
        c=Bend*(1-ASSUME["sell_cost_pct"])-sf_transfer_tax(Bend)
        gb=Bend-basisB
        return c-fed_tax(gb)-ca_tax(gb), gb

    res={}
    # LIVE
    fl=[rB[i]["gross_2units"]*1.5 - cB[i]["total"] - Al[i]["tax"] - cAl[i]["total"] - B[i]["tax"] for i in range(len(YEARS))][inh-2026:]
    ga=Aend-basisA
    ta=fed_tax(ga,SRC["irc121_joint"])+ca_tax(max(0,ga-SRC["irc121_joint"]))
    tb,_=liqB()
    res["live"]={"flows":fl,"termA":Aend*(1-ASSUME["sell_cost_pct"])-ta,"termB":tb,
                 "a_end":Aend,"a_tax_end":Al[-1]["tax"],"a_assess_end":Al[-1]["assessed"],
                 "gainA":ga,"taxA_terminal":ta}
    # RENT
    fr=[]
    for i in range(inh-2026, len(YEARS)):
        y=YEARS[i]; cu=ASSUME["cupertino_rent_month"]*12*(1+ASSUME["rent_growth"])**(y-2026)
        fr.append(rB[i]["gross_2units"]+cu - cB[i]["total"] - Ar[i]["tax"] - cAr[i]["total"] - B[i]["tax"])
    gara=Arend-basisA
    tara=fed_tax(gara)+ca_tax(gara)
    res["rent"]={"flows":fr,"termA":Arend*(1-ASSUME["sell_cost_pct"])-tara,"termB":tb,
                 "a_end":Arend,"a_tax_end":Ar[-1]["tax"],"a_assess_end":Ar[-1]["assessed"],
                 "gainA":gara,"taxA_terminal":tara}
    # SELL
    mvt=OWNER["A_value_2026"]*(1+appr)**(inh-2026)
    proceeds=mvt*(1-ASSUME["sell_cost_pct"])   # basis==FMV step-up => no gain
    fs=[]; port=proceeds
    for i in range(inh-2026, len(YEARS)):
        wd=port*0.04
        fs.append(rB[i]["gross_2units"]-cB[i]["total"]-B[i]["tax"]+wd)
        port=port*(1+g)-wd
    res["sell"]={"flows":fs,"termA":port,"termB":tb,"a_end":0,"a_tax_end":0,"a_assess_end":0,
                 "proceeds":proceeds,"transfer_tax":sf_transfer_tax(mvt),"gainA":0,"taxA_terminal":0}

    for k,v in res.items():
        w=0.
        for f in v["flows"]: w=w*(1+g)+f
        v["wealth_ops"]=w; v["terminal"]=v["termA"]+v["termB"]
        v["net_worth"]=w+v["terminal"]
        v["npv"]=npv(v["flows"],inv)+v["terminal"]/(1+inv)**(n-1)
        v["y1"]=v["flows"][0]; v["cum_ops"]=sum(v["flows"])
    return res, mvt, Aend, Bend

OUT={}
base, mvt, Aend, Bend = run(BASE_INH, ASSUME["appr_base"], ASSUME["invest_nominal"])
OUT["base"]={k:{kk:r10(vv) for kk,vv in v.items() if isinstance(vv,(int,float))} for k,v in base.items()}
OUT["base"]["mvt"]=r10(mvt); OUT["base"]["Aend"]=r10(Aend); OUT["base"]["Bend"]=r10(Bend)

grid=[]
for a in [0.02,0.03,0.04,0.05]:
    for iv in [0.05,0.07,0.085]:
        r,_,_,_=run(BASE_INH,a,iv)
        win=max(("Live","Rent","Sell"),key=lambda k:r[{"Live":"live","Rent":"rent","Sell":"sell"}[k]]["npv"])
        grid.append({"appr":a,"invest":iv,"live":r10(r["live"]["npv"]),"rent":r10(r["rent"]["npv"]),
                     "sell":r10(r["sell"]["npv"]),"winner":win})
OUT["grid"]=grid

byinh=[]
for inh in [2040,2045,2050]:
    r,m,ae,be=run(inh,ASSUME["appr_base"],ASSUME["invest_nominal"])
    byinh.append({"inh":inh,"mv":r10(m),"cap":r10(prop19_cap(inh,ASSUME["appr_base"])),
                  "a_assess_live":r10(r["live"]["a_assess_end"]),"a_tax_live":r10(r["live"]["a_tax_end"]),
                  "a_assess_rent":r10(r["rent"]["a_assess_end"]),"a_tax_rent":r10(r["rent"]["a_tax_end"]),
                  "npv_live":r10(r["live"]["npv"]),"npv_rent":r10(r["rent"]["npv"]),"npv_sell":r10(r["sell"]["npv"]),
                  "proceeds":r10(r["sell"]["proceeds"])})
OUT["byinh"]=byinh

Al=build_A(BASE_INH,ASSUME["appr_base"],ASSUME["appr_base"],"live")
Ar=build_A(BASE_INH,ASSUME["appr_base"],ASSUME["appr_base"],"rent")
B=build_B(BASE_INH,ASSUME["appr_base"]); cAl=costs_A(Al); cAr=costs_A(Ar); cB=costs_B(B); rB=rents_B(ASSUME["sf_rent_growth"])
proj=[]
for i,y in enumerate(YEARS):
    proj.append({"year":y,
      "a_market":Al[i]["market"],"a_assess":Al[i]["assessed"],"a_tax":Al[i]["tax"],
      "a_assess_rent":Ar[i]["assessed"],"a_tax_rent":Ar[i]["tax"],
      "a_water":cAl[i]["water"],"a_elec":cAl[i]["electric"],"a_ins":cAl[i]["insurance"],
      "a_maint":cAl[i]["maintenance"],"a_carry":cAl[i]["total"],
      "b_market":B[i]["market"],"b_assess":B[i]["assessed"],"b_tax":B[i]["tax"],
      "b_water":cB[i]["water"],"b_elec":cB[i]["electric"],"b_ins":cB[i]["insurance"],
      "b_maint":cB[i]["maintenance"],"b_carry":cB[i]["total"],"b_rent":rB[i]["gross_2units"],
      "cap19":r10(prop19_cap(y,ASSUME["appr_base"])),
      "a_cf_live":r10(rB[i]["gross_2units"]*1.5 - Al[i]["tax"] - cAl[i]["total"] - B[i]["tax"] - cB[i]["total"]),
      "a_cf_rent":r10(rB[i]["gross_2units"] + ASSUME["cupertino_rent_month"]*12*(1+ASSUME["rent_growth"])**(y-2026) - Ar[i]["tax"] - cAr[i]["total"] - B[i]["tax"] - cB[i]["total"]),
    })
OUT["proj"]=proj
json.dump(OUT, open("data/model_output.json","w"), indent=1)
with open("data/projections.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(proj[0].keys())); w.writeheader(); w.writerows(proj)

print("BASE:", json.dumps(OUT["base"], indent=1))
from collections import Counter
print("Grid winners:", Counter(g["winner"] for g in grid))
for b in byinh: print(b)
