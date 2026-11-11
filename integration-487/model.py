#!/usr/bin/env python3
"""A reproducible, *synthetic* California inheritance decision illustration.

No user-provided property values are used. Results are not tax returns, appraisals,
forecasts, or advice. Dollar values are rounded only for presentation, so a sum of
rounded table cells can differ by $10. See methodology.html for every assumption.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

START_YEAR = 2026
EXAMPLE_TRANSFER_YEAR = 2045
YEARS = 50

# All property-specific inputs below are invented, not estimates of any real home.
A_VALUE_2026 = 2_200_000.0
A_FACTORED_2026 = 880_000.0
B_VALUE_2026 = 2_600_000.0
B_FACTORED_2026 = 680_000.0
A_RENT_2026 = 52_800.0
B_TWO_RENTS_2026 = 72_000.0
B_BUILDING_BASIS_2026 = 1_200_000.0
A_BUILDING_SHARE = 0.65
B_RENTED_SHARE = 2.0 / 3.0

# Approximate current BOE number, displayed and used to the nearest $10. The
# future allowance below is an invented smooth growth path, not the legal index.
PROP19_ALLOWANCE_2026 = 1_044_590.0
HOMEOWNERS_EXEMPTION = 7_000.0
SINGLE_HOME_SALE_EXCLUSION = 250_000.0

# These are invented illustrative rates, NOT official rates or forecasts.
HOME_GROWTH = 0.03
ASSESSED_GROWTH = 0.02
ALLOWANCE_GROWTH = 0.025
A_RENT_GROWTH = 0.03
B_RENT_GROWTH = 0.016
VACANCY = 0.05
MANAGEMENT = 0.06
CLOSING_COST = 0.05
RENTAL_TAX = 0.30
GAIN_TAX = 0.30
RECAPTURE_TAX = 0.35
PORTFOLIO_AFTER_TAX_RETURN = 0.04
FUNDING_RATE = 0.06
DEPRECIATION_YEARS = 27.5
A_AD_VALOREM = 0.0115
B_AD_VALOREM = 0.0118

# Full-year synthetic operating inputs, in 2026 dollars, per property.
OPERATING_2026 = {
    'a_water': 1_800.0, 'a_power': 2_400.0, 'a_insurance': 3_200.0,
    'a_maintenance': 10_000.0, 'a_fixed': 1_200.0,
    'b_water': 3_000.0, 'b_power': 3_600.0, 'b_insurance': 4_000.0,
    'b_maintenance': 14_000.0, 'b_fixed': 1_200.0,
}


@dataclass(frozen=True)
class Scenario:
    key: str
    label: str
    description: str
    source_key: str


SCENARIOS = (
    Scenario('base', 'Base path', 'Steady illustrative growth; no shock.', 'fhfa'),
    Scenario('market', 'Market and housing crash',
             'In 2050 both home values fall 25% and the positive investment account falls 35%; rents are frozen for 2050–2052.', 'fhfa'),
    Scenario('inflation', 'Inflation and insurance squeeze',
             'In 2048–2054, utilities rise 9%, insurance 12%, maintenance 7% annually and the after-tax investment return is 1%.', 'bls'),
    Scenario('disaster', 'Uninsured damage',
             'In 2055, an assumed uninsured repair costs the inherited home $250,000 if retained and the already-owned home $100,000; assets are assumed restored.', 'cdi'),
    Scenario('no_relief', 'No family-home relief',
             'The live option does not qualify for the family-home exclusion from the date of transfer.', 'prop19'),
    Scenario('lower_basis', 'Lower inherited basis',
             'All options assume an inherited income-tax basis equal to 50% of the transfer-date market value instead of the full value.', 'basis_ruling'),
)
STRATEGIES = ('live', 'rent', 'sell')
LABELS = {'live': 'Live in inherited home', 'rent': 'Rent inherited home', 'sell': 'Sell and invest'}


def round10(value: float) -> int:
    """Round dollars for display, half away from zero (not banker's rounding)."""
    if value < 0:
        return -int((-value + 5) // 10) * 10
    return int((value + 5) // 10) * 10


def initial_state(transfer_year: int) -> Dict[str, float]:
    """Beginning-of-year synthetic values at the assumed transfer date."""
    n = transfer_year - START_YEAR
    if n < 0:
        raise ValueError('Transfer year cannot precede 2026')
    state = {
        'a_value': A_VALUE_2026 * (1 + HOME_GROWTH) ** n,
        'a_factored_pre': A_FACTORED_2026 * (1 + ASSESSED_GROWTH) ** n,
        'b_value': B_VALUE_2026 * (1 + HOME_GROWTH) ** n,
        'b_factored': B_FACTORED_2026 * (1 + ASSESSED_GROWTH) ** n,
        'a_rent': A_RENT_2026 * (1 + A_RENT_GROWTH) ** n,
        'b_rent': B_TWO_RENTS_2026 * (1 + B_RENT_GROWTH) ** n,
        'allowance': PROP19_ALLOWANCE_2026 * (1 + ALLOWANCE_GROWTH) ** n,
    }
    for key, amount in OPERATING_2026.items():
        rate = 0.04 if key.endswith('_insurance') else 0.03 if key.endswith(('_water', '_power')) else 0.025 if key.endswith('_maintenance') else 0.02
        state[key] = amount * (1 + rate) ** n
    return state


def first_sale(value: float, basis: float) -> dict[str, float]:
    """Simplified immediate sale; loss is not used as a tax benefit."""
    selling_cost = value * CLOSING_COST
    amount_realized = value - selling_cost
    gain = max(0.0, amount_realized - basis)
    tax = gain * GAIN_TAX
    return {'price': value, 'selling_cost': selling_cost, 'basis': basis,
            'taxable_gain': gain, 'tax': tax, 'net': amount_realized - tax}


def end_sale(value: float, original_basis: float, depreciation: float,
             choice: str, years: int) -> dict[str, float]:
    """Illustrative hypothetical disposition. The retained B is not sold."""
    selling_cost = value * CLOSING_COST
    amount_realized = value - selling_cost
    adjusted_basis = max(0.0, original_basis - depreciation)
    gain = max(0.0, amount_realized - adjusted_basis)
    # Home-sale exclusion is assumed available to the live strategy after two
    # full years; no other sale within the lookback period is assumed.
    exclusion = min(gain, SINGLE_HOME_SALE_EXCLUSION) if choice == 'live' and years >= 2 else 0.0
    recapture = min(depreciation, gain) if choice == 'rent' else 0.0
    appreciation_gain = max(0.0, gain - exclusion - recapture)
    tax = recapture * RECAPTURE_TAX + appreciation_gain * GAIN_TAX
    return {'price': value, 'selling_cost': selling_cost, 'basis': adjusted_basis,
            'gain': gain, 'exclusion': exclusion, 'recapture': recapture,
            'tax': tax, 'net': amount_realized - tax}


def simulate(scenario: Scenario, transfer_year: int = EXAMPLE_TRANSFER_YEAR,
             years: int = YEARS) -> dict[str, list[dict[str, float]]]:
    """Return annual end-of-year snapshots for each strategy.

    A is transferred on January 1; A is sold at once only in sell. B is already
    owned in every strategy; its two rented units remain rented, while a third
    unit is owner-occupied for rent/sell and kept unrented for live. There is no
    imputed rent or hypothetical third-unit income. No mortgage is assumed.
    """
    if years < 1:
        raise ValueError('years must be positive')
    answer: dict[str, list[dict[str, float]]] = {}
    for choice in STRATEGIES:
        state = initial_state(transfer_year)
        a_transfer_value = state['a_value']
        a_basis = a_transfer_value * (0.5 if scenario.key == 'lower_basis' else 1.0)
        a_factored = (max(state['a_factored_pre'], a_transfer_value - state['allowance'])
                      if choice == 'live' and scenario.key != 'no_relief' else a_transfer_value)
        event_sale = first_sale(a_transfer_value, a_basis)
        account = event_sale['net'] if choice == 'sell' else 0.0
        a_depreciation_accum = 0.0
        rows = []

        for i in range(years):
            year = transfer_year + i
            if i:
                state['b_factored'] *= 1 + ASSESSED_GROWTH
                a_factored *= 1 + ASSESSED_GROWTH
                freeze = scenario.key == 'market' and 2050 <= year <= 2052
                state['a_rent'] *= 1 + (0 if freeze else A_RENT_GROWTH)
                state['b_rent'] *= 1 + (0 if freeze else B_RENT_GROWTH)
                for key in OPERATING_2026:
                    if scenario.key == 'inflation' and 2048 <= year <= 2054:
                        rate = 0.12 if key.endswith('_insurance') else 0.09 if key.endswith(('_water', '_power')) else 0.07 if key.endswith('_maintenance') else 0.02
                    else:
                        rate = 0.04 if key.endswith('_insurance') else 0.03 if key.endswith(('_water', '_power')) else 0.025 if key.endswith('_maintenance') else 0.02
                    state[key] *= 1 + rate

            # Property taxes use January-1 market and factored values. A Prop 8
            # decline-in-value adjustment is applied as a simple min(). County
            # assessment procedures and supplemental bills are not modeled.
            a_assessed = min(a_factored, state['a_value'])
            b_assessed = min(state['b_factored'], state['b_value'])
            a_exemption = HOMEOWNERS_EXEMPTION if choice == 'live' else 0.0
            b_exemption = HOMEOWNERS_EXEMPTION if choice in ('rent', 'sell') else 0.0
            a_tax = max(0.0, a_assessed - a_exemption) * A_AD_VALOREM + state['a_fixed'] if choice != 'sell' else 0.0
            b_tax = max(0.0, b_assessed - b_exemption) * B_AD_VALOREM + state['b_fixed']
            a_operating = sum(state['a_' + k] for k in ('water', 'power', 'insurance', 'maintenance'))
            b_operating = sum(state['b_' + k] for k in ('water', 'power', 'insurance', 'maintenance'))
            b_rent_collected = state['b_rent'] * (1 - VACANCY)
            b_management = b_rent_collected * MANAGEMENT
            # Invented 2026 placement date, simple straight-line approximation.
            b_depreciable_year = max(0.0, min(1.0, DEPRECIATION_YEARS - (year - START_YEAR)))
            b_depreciation = B_BUILDING_BASIS_2026 * B_RENTED_SHARE / DEPRECIATION_YEARS * b_depreciable_year
            b_taxable = max(0.0, b_rent_collected - b_management - (b_tax + b_operating) * B_RENTED_SHARE - b_depreciation)
            b_rental_tax = b_taxable * RENTAL_TAX
            b_extra = 100_000.0 if scenario.key == 'disaster' and year == 2055 else 0.0
            b_net = b_rent_collected - b_management - b_tax - b_operating - b_rental_tax - b_extra

            a_rent_collected = a_management = a_depreciation = a_rental_tax = a_extra = 0.0
            if choice == 'rent':
                a_rent_collected = state['a_rent'] * (1 - VACANCY)
                a_management = a_rent_collected * MANAGEMENT
                year_fraction = max(0.0, min(1.0, DEPRECIATION_YEARS - i))
                a_depreciation = a_basis * A_BUILDING_SHARE / DEPRECIATION_YEARS * year_fraction
                a_depreciation_accum += a_depreciation
                a_taxable = max(0.0, a_rent_collected - a_management - a_tax - a_operating - a_depreciation)
                a_rental_tax = a_taxable * RENTAL_TAX
            if choice != 'sell' and scenario.key == 'disaster' and year == 2055:
                a_extra = 250_000.0
            a_net = (a_rent_collected - a_management - a_tax - a_operating - a_rental_tax - a_extra) if choice != 'sell' else 0.0

            # Jan 1 sale proceeds / beginning balance earn one full year's return.
            # Annual income and costs are added at year-end. Loss years on the
            # positive account and interest on a negative account are distinct.
            if account >= 0:
                rate = -0.35 if scenario.key == 'market' and year == 2050 else 0.01 if scenario.key == 'inflation' and 2048 <= year <= 2054 else PORTFOLIO_AFTER_TAX_RETURN
            else:
                rate = FUNDING_RATE
            investment_change = account * rate
            account += investment_change + a_net + b_net

            # End-of-year marks; the 2050 market shock is substituted for that
            # year's regular appreciation, so 2051's lien date sees the drop.
            price_rate = -0.25 if scenario.key == 'market' and year == 2050 else HOME_GROWTH
            a_end = state['a_value'] * (1 + price_rate)
            b_end = state['b_value'] * (1 + price_rate)
            disposal = end_sale(a_end, a_basis, a_depreciation_accum, choice, i + 1) if choice != 'sell' else None
            a_exit_net = disposal['net'] if disposal else 0.0
            position = b_end + account + a_exit_net
            rows.append({
                'year': year, 'years': i + 1, 'a_start_value': state['a_value'], 'a_end_value': a_end,
                'a_factored': a_factored, 'a_assessed': a_assessed, 'a_tax': a_tax,
                'a_water': state['a_water'] if choice != 'sell' else 0.0,
                'a_power': state['a_power'] if choice != 'sell' else 0.0,
                'a_insurance': state['a_insurance'] if choice != 'sell' else 0.0,
                'a_maintenance': state['a_maintenance'] if choice != 'sell' else 0.0,
                'a_rent_gross': state['a_rent'] if choice == 'rent' else 0.0,
                'a_rent_collected': a_rent_collected, 'a_management': a_management,
                'a_rental_tax': a_rental_tax, 'a_depreciation': a_depreciation,
                'a_depreciation_accum': a_depreciation_accum, 'a_extra': a_extra, 'a_net': a_net,
                'a_exit_net': a_exit_net, 'a_exit_tax': disposal['tax'] if disposal else 0.0,
                'b_start_value': state['b_value'], 'b_end_value': b_end,
                'b_factored': state['b_factored'], 'b_assessed': b_assessed, 'b_tax': b_tax,
                'b_water': state['b_water'], 'b_power': state['b_power'],
                'b_insurance': state['b_insurance'], 'b_maintenance': state['b_maintenance'],
                'b_rent_gross': state['b_rent'], 'b_rent_collected': b_rent_collected,
                'b_management': b_management, 'b_rental_tax': b_rental_tax,
                'b_depreciation': b_depreciation, 'b_extra': b_extra, 'b_net': b_net,
                'account': account, 'investment_change': investment_change,
                'net_cash': a_net + b_net, 'position': position,
                'allowance_at_transfer': state['allowance'], 'a_basis': a_basis,
                'event_sale_price': event_sale['price'], 'event_selling_cost': event_sale['selling_cost'],
                'event_gain': event_sale['taxable_gain'], 'event_tax': event_sale['tax'],
                'event_sale_net': event_sale['net'],
            })
            state['a_value'] = a_end
            state['b_value'] = b_end
        answer[choice] = rows
    return answer


def pre_transfer_projections(start: int = 2026, end: int = 2050) -> list[dict[str, float]]:
    """Independent no-transfer baseline at January 1 each year (illustrative)."""
    rows = []
    for year in range(start, end + 1):
        s = initial_state(year)
        rows.append({'year': year, **s})
    return rows


def estate_table(start: int = 2026, end: int = 2050) -> list[dict[str, float]]:
    """Synthetic transferor's estate; already-owned B is NOT added to it.

    2026 and 2027 basic exclusions are official. From 2028 the basic exclusion
    grows by an assumed 2.5%. Estate amount is an invented $12m in 2026, growing
    at an invented 3.5%. Zero gifts, DSUE and deductions are assumed. This is a
    high-level exposure estimate, not a Form 706 calculation or filing test.
    """
    rows = []
    for year in range(start, end + 1):
        if year < 2026:
            raise ValueError('Years before 2026 not supported')
        exclusion = 15_000_000.0 if year == 2026 else 15_480_000.0 * 1.025 ** (year - 2027)
        hypothetical_estate = 12_000_000.0 * 1.035 ** (year - 2026)
        excess = max(0.0, hypothetical_estate - exclusion)
        rows.append({'year': year, 'exclusion': exclusion, 'estate': hypothetical_estate,
                     'headroom': exclusion - hypothetical_estate, 'estimated_tax': excess * 0.40,
                     'official_exclusion': year in (2026, 2027)})
    return rows


if __name__ == '__main__':
    for scenario in SCENARIOS:
        series = simulate(scenario)
        print(scenario.label, {k: round10(v[-1]['position']) for k, v in series.items()})
