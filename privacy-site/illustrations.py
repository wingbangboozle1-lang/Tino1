"""Synthetic teaching examples ONLY. No imports of household/repository data.
All rates are chosen assumptions, not official predictions, quotes or tax advice.
Round only at display time; keep full precision for calculations.
"""
from decimal import Decimal, ROUND_HALF_UP


def r10(value):
    return int((Decimal(str(value))/10).quantize(Decimal('1'), rounding=ROUND_HALF_UP))*10


def money(value):
    n = r10(value)
    return ('−' if n < 0 else '') + f'${abs(n):,}'


def family_assessment(market, factored_base, allowance):
    """Eligible family-home branch before exemptions; no eligibility implied."""
    return factored_base + max(0, market - factored_base - allowance)


def outlook(transfer=2046):
    """Unrelated fictional home, at year-end, full-year transfer simplification.
    Synthetic allowance fixed at $1m; NOT the actual current BOE allowance.
    Prior factored-base growth 2%, market 3%, general expenses 2.5%.
    1.2% tax rate is invented; excludes exemptions/direct/supplemental charges.
    """
    rows = []
    base = 200000.0
    for year in range(2026, 2077):
        age = year - 2026
        market = 1000000 * 1.03**age
        if year == transfer:
            full_base = market
            live_base = family_assessment(market, base, 1000000)
        elif year > transfer:
            full_base *= 1.02
            live_base *= 1.02
        else:
            full_base = live_base = base
        full_taxable = min(full_base, market)
        live_taxable = min(live_base, market)
        factor = 1.025**age
        rows.append(dict(year=year, market=market, live_assessed=live_taxable,
                         rental_assessed=full_taxable, live_tax=.012*live_taxable,
                         rental_tax=.012*full_taxable, insurance=3000*factor,
                         water=2000*factor, electricity=1000*factor,
                         repairs=6000*factor, capex=4000*factor,
                         real_market=market/factor))
        base *= 1.02
    return rows


def investment_path(returns, inflation):
    nominal = 1000000.0
    price = 1.0
    rows = []
    for i, (ret, cpi) in enumerate(zip(returns, inflation), 1):
        nominal *= 1 + ret
        price *= 1 + cpi
        rows.append(dict(year=i, nominal=nominal, real=nominal/price))
    return rows


# Explicit invented regimes, not historical replays; shocks in year 1 unless noted.
STRESS = {
    'Smooth reference': ([.05]*50, [.025]*50),
    'Market crash, then recovery': ([-.40]+[.05]*49, [.025]*50),
    'Five-year inflation shock': ([.03]*5+[.05]*45, [.08]*5+[.025]*45),
    'Ten-year nominal stagnation': ([0]*10+[.05]*40, [.025]*50),
    'Late market crash (year 20)': ([.05]*19+[-.40]+[.05]*30, [.025]*50),
}


def ledger(gross=36000, net_return=.05, house_growth=.03, years=30):
    """One unrelated fictional inherited home, basis $1m, debt-free.
    Step-up assumed; 40% building share, annual straight-line approximation
    (not first/last-year tax convention); no passive loss benefit or carryover.
    Year-end rent/expense cash flows invested at the same effective net return.
    Tax assumptions: ordinary 30%, gain 30%, recapture 35% combined effective.
    Rental costs: 5% vacancy, 8% management on collected rent, 1.2% property tax
    on factored $1m assessment, $3k insurance/$2k water/$1k power/$6k repairs/
    $4k annual capital work. Capital work increases basis but has no depreciation
    in this deliberately simplified illustration. Tax ignores extra depreciation.
    All non-tax expenses and rent grow 2.5%, assessment grows 2%.
    Sale cost 5%, immediate sale at basis => no capital gain or loss benefit.
    Common estate tax/other home excluded from BOTH paths, not counted twice.
    """
    savings = 0.0
    depreciation_total = 0.0
    improvements = 0.0
    annual = []
    for i in range(1, years+1):
        f = 1.025**(i-1)
        collected = gross*f*.95
        management = collected*.08
        tax = 12000*1.02**(i-1)
        other = (3000+2000+1000+6000)*f
        capital = 4000*f
        depreciation = min(400000-depreciation_total, 400000/27.5)
        depreciation_total += depreciation
        improvements += capital
        taxable = collected-management-tax-other-depreciation
        income_tax = max(0, taxable)*.30
        cash = collected-management-tax-other-capital-income_tax
        savings = savings*(1+net_return)+cash
        annual.append(dict(year=i, rent=collected, property_tax=tax,
                           expenses=management+tax+other+capital,
                           income_tax=income_tax, cash=cash))
    sale = 1000000*(1+house_growth)**years*.95
    adjusted_basis = 1000000+improvements-depreciation_total
    gain = max(0, sale-adjusted_basis)
    recapture = min(gain, depreciation_total)
    terminal_tax = recapture*.35+(gain-recapture)*.30
    return dict(rent_wealth=sale-terminal_tax+savings,
                sell_wealth=950000*(1+net_return)**years,
                first_year=annual[0], terminal_tax=terminal_tax,
                invested_cash=savings, annual=annual)


def threshold(year, rate):
    """Arithmetic scenario, NOT statutory CPI indexing or an IRS future amount."""
    return 15480000*(1+rate)**(year-2027)
