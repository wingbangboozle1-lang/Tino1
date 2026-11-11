#!/usr/bin/env python3
"""Reproduce model concerns with invented inputs; no personal data is printed."""
import importlib.util
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('existing_model', repo / 'final' / 'model.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Fully invented values, deliberately chosen to create a gain in year one.
p = m.with_(T=2027, cup_value=1_000_000, cup_assessed=500_000,
            sf_value=1_000_000, sf_assessed=500_000, sf_tax_2025=10_000,
            sf_rent_2units=0, sf_unit3_rent=0, dc_cup=0, dc_sf=0,
            cup_tax_2025=10_000, cup_water=0, cup_elec=0, sf_water=0,
            sf_elec=0, ins_home=0, ins_rental=0, maint_cup=0, maint_sf=0,
            cup_rent_month=0, sell_cost=0, doc_transfer_tax=0,
            g_cup=1.0, r_stock=0, r_bond=0, r_bill=0, div_yield=0)
# Equal inherited basis and market value in 2027 means we need appreciation
# during the same calendar year to make the difference visible. Setting the
# fallback basis branch to the invented assessed value isolates the exclusion.
p['step_up'] = False
p['sec121'] = 0
row_without = m.run(p)[0][2027 - m.Y0]
p['sec121'] = 250_000
row_with = m.run(p)[0][2027 - m.Y0]
assert row_with['w_live'] > row_without['w_live'], 'Exclusion no longer affects year-one liquidation; review audit.'
print('CONFIRMED: model applies the home-sale exclusion to year-one liquidation before two years of modeled residence.')

# A zero assumed NIIT changes the return on an otherwise identical taxable
# account even though the account itself contains no MAGI or filing status.
a, b = m.Acct(), m.Acct()
a.add(100_000); b.add(100_000)
p2 = m.with_(w_stock=1, w_bond=0, w_bill=0, r_stock=0, div_yield=.02,
             t_fed_ltcg=0, t_ca=0, niit=.038)
e = {'r_stock': 0, 'r_bond': 0, 'r_bill': 0}
a.grow(e, p2)
p2['niit'] = 0
b.grow(e, p2)
assert a.bal < b.bal
print('CONFIRMED: model applies assumed NIIT without an account-level MAGI threshold test.')
print('Checks use invented data only; results identify model behavior, not individual tax outcomes.')
