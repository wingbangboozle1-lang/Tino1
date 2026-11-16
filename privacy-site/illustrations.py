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


def phased_entry(stock_returns, principal=100000, park_rate=.03,
                 wait_months=24, phase_months=12):
    """Synthetic 10-year comparison of immediate stock entry vs Treasury parking.

    ``stock_returns`` contains annual assumed equity returns. The phased path
    parks principal at a constant assumed annual Treasury rate, then invests
    equal installments over ``phase_months``. Interest-rate resets, taxes, fees,
    inflation, dividend conventions and actual Treasury maturity yields are
    omitted deliberately; the output is an educational timing-risk stress only.
    """
    if not stock_returns or any(r <= -1 for r in stock_returns):
        raise ValueError('stock returns must be nonempty and greater than -100%')
    horizon_months = 12 * len(stock_returns)
    if wait_months < 0 or phase_months < 1 or wait_months + phase_months > horizon_months:
        raise ValueError('parking and phasing must fit inside the modeled horizon')
    equity_now = float(principal)
    equity_staged = 0.0
    treasury = float(principal)
    monthly_treasury = (1 + park_rate) ** (1 / 12) - 1
    for month in range(horizon_months):
        annual_equity = stock_returns[month // 12]
        monthly_equity = (1 + annual_equity) ** (1 / 12) - 1
        equity_now *= 1 + monthly_equity
        equity_staged *= 1 + monthly_equity
        treasury *= 1 + monthly_treasury
        if wait_months <= month < wait_months + phase_months:
            remaining_phases = wait_months + phase_months - month
            installment = treasury / remaining_phases
            treasury -= installment
            equity_staged += installment
    return dict(immediate=equity_now, staged=equity_staged + treasury,
                staged_equity=equity_staged, residual_treasury=treasury)


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


# Annual change in the CPI-U (U.S. city average, all items), percent, copied from
# the BLS historical table linked in research.json ('cpi'). These are OFFICIAL
# observations, not assumptions and not a forecast. Transcribed once, checked by
# test_illustrations.py against the published decade ranges, and never extrapolated.
CPI_ANNUAL = {
    1970: 5.7, 1971: 4.4, 1972: 3.2, 1973: 6.2, 1974: 11.0, 1975: 9.1,
    1976: 5.8, 1977: 6.5, 1978: 7.6, 1979: 11.3, 1980: 13.5, 1981: 10.3,
    1982: 6.2, 1983: 3.2, 1984: 4.3, 1985: 3.6, 1986: 1.9, 1987: 3.6,
    1988: 4.1, 1989: 4.8, 1990: 5.4, 1991: 4.2, 1992: 3.0, 1993: 3.0,
    1994: 2.6, 1995: 2.8, 1996: 3.0, 1997: 2.3, 1998: 1.6, 1999: 2.2,
    2000: 3.4, 2001: 2.8, 2002: 1.6, 2003: 2.3, 2004: 2.7, 2005: 3.4,
    2006: 3.2, 2007: 2.8, 2008: 3.8, 2009: -0.4, 2010: 1.6, 2011: 3.2,
    2012: 2.1, 2013: 1.5, 2014: 1.6, 2015: 0.1, 2016: 1.3,
}


def cpi_decades(values=None):
    """Plain arithmetic over the official annual CPI-U changes.

    Returns one row per decade plus an overall row. Nothing here is a forecast:
    the point is only to show that a single constant rate is a simplification.
    """
    values = CPI_ANNUAL if values is None else values

    def block(label, years):
        series = [values[y] for y in years]
        return dict(label=label, count=len(series), low=min(series),
                    high=max(series), mean=sum(series) / len(series),
                    at_least_5=sum(1 for v in series if v >= 5),
                    below_2=sum(1 for v in series if v < 2))

    years = sorted(values)
    rows = []
    for start in range(1970, 2020, 10):
        chunk = [y for y in years if start <= y < start + 10]
        if chunk:
            rows.append(block(f'{start}s', chunk))
    rows.append(block(f'{years[0]}–{years[-1]} total', years))
    return rows


def cpi_extremes(values=None, threshold=8.0):
    """Official years at or above a threshold, and any negative years."""
    values = CPI_ANNUAL if values is None else values
    high = [y for y in sorted(values) if values[y] >= threshold]
    negative = [y for y in sorted(values) if values[y] < 0]
    return high, negative


def cpi_display_rows(values=None):
    """Display rows for the official CPI table. Formatting only; no new numbers."""
    values = CPI_ANNUAL if values is None else values
    negative = [y for y in values if values[y] < 0]

    def signed(x, places):
        return ('+' if x >= 0 else '−') + f'{abs(x):.{places}f}%'

    rows = []
    for r in cpi_decades(values):
        label = r['label']
        if label.endswith('s'):
            start = int(label[:4])
            neg = len([y for y in negative if y // 10 * 10 == start])
        else:
            neg = len(negative)
        five = 'none' if r['at_least_5'] == 0 else str(r['at_least_5'])
        if r['below_2'] == 0:
            under = 'none'
        elif neg:
            under = f"{r['below_2']} (1 is a deflation year)"
        else:
            under = str(r['below_2'])
        rows.append((label, str(r['count']), signed(r['low'], 1), signed(r['high'], 1),
                     signed(r['mean'], 2), five, under))
    return rows


# ---------------------------------------------------------------------------
# Historical episode test of staged entry. Data: data/phased-history.json.
# The stock leg is academic (non-government); the cash leg is official FRED.
# ---------------------------------------------------------------------------
import json as _json
from pathlib import Path as _Path

HISTORY = _json.loads((_Path(__file__).parent/'data'/'phased-history.json').read_text())
STOCK = {int(k): v/100 for k, v in HISTORY['stock']['years'].items()}
BILL = {int(k): v/100 for k, v in HISTORY['bill3m']['years'].items()}
GS2 = {int(k): v/100 for k, v in HISTORY['gs2']['years'].items()}
EPS = 1e-4


def cash_leg(year, park_years):
    """Official cash ingredient for the parked window [year, year+park_years).

    Returns dict(rate, mode, years) or None. Modes:
      'bill'   - mean of the official annual average 3-month bill rate for each
                 parked year (available from 1934).
      'ladder' - mean of the bill and 2-year par-yield annual averages, a proxy for
                 a bill-to-2-year ladder (needs both series, so 1977 onward).
    A yield is not a total return. The 2-year leg is a holding-price proxy only, and
    a missing official value is never filled in: ``None`` is returned instead.
    """
    years = list(range(year, year+park_years))
    if not years or any(y not in BILL for y in years):
        return None
    if all(y in GS2 for y in years):
        return dict(rate=sum((BILL[y]+GS2[y])/2 for y in years)/park_years,
                    mode='ladder', years=tuple(years))
    return dict(rate=sum(BILL[y] for y in years)/park_years, mode='bill', years=tuple(years))


def ladder_rate(year, park_years):
    """Backwards-compatible accessor: the official rate, or None."""
    leg = cash_leg(year, park_years)
    return None if leg is None else leg['rate']


def lump_sum_return(start_year, horizon=10):
    """Growth of 1.0 from the start of the crisis year to the start of year
    ``start_year+horizon`` on the academic annual total-return series."""
    if any(y not in STOCK for y in range(start_year, start_year+horizon)):
        raise ValueError('no stock observation for the whole horizon')
    value = 1.0
    for j in range(horizon):
        value *= 1+STOCK[start_year+j]
    return value


def episode_replay(start_year, park_years=3, phase_years=3, horizon=10, cash_fallback=None):
    """Equal-installment staged entry on the real calendar-year path starting at ``start_year``.

    Year 0 is the crisis year in which the proceeds arrive. The lump-sum comparison
    invests at the start of year 0; the staged comparison keeps everything in the
    cash leg for ``park_years`` years and then moves equal shares into stocks at the
    start of years ``park_years`` .. ``park_years+phase_years-1``. The last tranche
    takes whatever is still in cash. Arithmetic annual returns, no tax, fees or
    inflation; parked cash earns the same ``cash_leg`` rate each parked year.

    ``cash_fallback`` is an explicit assumed rate (0.0 on the page) used only when no
    official series reaches back far enough; the result then carries mode
    'assumed' so the assumption is visible. Without a fallback, ``staged`` is None
    rather than an unverified number.
    """
    lump = lump_sum_return(start_year, horizon)
    if park_years == 0:      # nothing is parked, so the cash rate cannot matter
        rate, mode = 0.0, 'none'
        leg = dict(mode='none', rate=0.0, years=())
    else:
        leg = cash_leg(start_year, park_years)
    if park_years:
        mode = leg['mode'] if leg else None
        rate = leg['rate'] if leg else None
    if leg is None and cash_fallback is not None:
        rate, mode = cash_fallback, 'assumed'
    if leg is None and rate is None:
        return dict(start_year=start_year, park_years=park_years, phase_years=phase_years,
                    cash_rate=None, cash_mode=None, lump_sum=lump, staged=None, difference=None)
    cash, equity = 1.0, 0.0
    for j in range(horizon):
        if park_years <= j < park_years+phase_years:
            move = cash/(park_years+phase_years-j)
            cash -= move
            equity += move
        if j < park_years:
            cash *= 1+rate
        equity *= 1+STOCK[start_year+j]
    staged = cash+equity
    return dict(start_year=start_year, park_years=park_years, phase_years=phase_years,
                cash_rate=rate, cash_mode=mode, lump_sum=lump, staged=staged,
                difference=staged-lump)


def all_start_years(park_years=3, phase_years=3, horizon=10, first=1934, last=2015):
    """Every entry year on which the official cash leg and the stock leg both exist."""
    out = []
    for year in range(first, last+1):
        try:
            out.append(episode_replay(year, park_years, phase_years, horizon))
        except ValueError:
            continue
    return out


def staged_summary(rows):
    """Counts and medians of staged-minus-lump-sum across complete entry years.

    ``difference`` is in units of the starting amount (1.0 == the whole principal).
    ``ratio`` is the same gap relative to the lump-sum endpoint, which is the number a
    reader can act on: -0.21 means the staged path ended 21% below the lump sum.
    """
    rows = [r for r in rows if r['staged'] is not None]
    diffs = sorted(r['difference'] for r in rows)
    ratios = sorted(r['staged']/r['lump_sum']-1 for r in rows)
    n = len(diffs)
    wins = sum(1 for d in diffs if d > EPS)
    losses = sum(1 for d in diffs if d < -EPS)
    def median(xs):
        m = len(xs)//2
        return xs[m] if len(xs) % 2 else (xs[m-1]+xs[m])/2
    return dict(n=n, wins=wins, losses=losses, ties=n-wins-losses,
                median=median(ratios) if ratios else None,
                low=ratios[0] if ratios else None, high=ratios[-1] if ratios else None,
                median_principal=median(diffs) if diffs else None,
                low_principal=diffs[0] if diffs else None, high_principal=diffs[-1] if diffs else None)
