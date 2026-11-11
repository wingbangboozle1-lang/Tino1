import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model as m


class ModelTests(unittest.TestCase):
    def test_r10_nearest_and_negative(self):
        self.assertEqual([m.round10(n) for n in (100, 104.99, 105, -104.99, -105)],
                         [100, 100, 110, -100, -110])

    def test_separate_property_and_preserved_rents(self):
        series = m.simulate(m.SCENARIOS[0])
        for i in range(m.YEARS):
            live, rent, sell = [series[s][i] for s in m.STRATEGIES]
            self.assertAlmostEqual(live['b_assessed'], rent['b_assessed'])
            self.assertAlmostEqual(rent['b_assessed'], sell['b_assessed'])
            self.assertAlmostEqual(live['b_rent_gross'], rent['b_rent_gross'])
            self.assertAlmostEqual(rent['b_rent_gross'], sell['b_rent_gross'])
            self.assertGreater(live['b_rent_gross'], 0)
            self.assertAlmostEqual(live['b_tax'] - rent['b_tax'], m.HOMEOWNERS_EXEMPTION * m.B_AD_VALOREM)

    def test_prop19_event_assessment_and_no_qualification(self):
        s = m.initial_state(2045)
        baseline = m.simulate(m.SCENARIOS[0])
        live = baseline['live'][0]
        rent = baseline['rent'][0]
        expected = max(s['a_factored_pre'], s['a_value'] - s['allowance'])
        self.assertAlmostEqual(live['a_assessed'], expected)
        self.assertAlmostEqual(rent['a_assessed'], s['a_value'])
        self.assertAlmostEqual(live['a_tax'], (expected - 7000) * m.A_AD_VALOREM + s['a_fixed'])
        no_relief = m.simulate(next(x for x in m.SCENARIOS if x.key == 'no_relief'))['live'][0]
        self.assertAlmostEqual(no_relief['a_assessed'], s['a_value'])
        self.assertAlmostEqual(no_relief['a_tax'], (s['a_value'] - 7000) * m.A_AD_VALOREM + s['a_fixed'])

    def test_sale_step_up_not_guaranteed_and_account_timing(self):
        base = m.simulate(m.SCENARIOS[0])['sell'][0]
        self.assertEqual(base['event_gain'], 0)
        self.assertEqual(base['event_tax'], 0)
        self.assertAlmostEqual(base['event_sale_net'], base['event_sale_price'] * .95)
        self.assertAlmostEqual(base['account'], base['event_sale_net'] * 1.04 + base['a_net'] + base['b_net'])
        low = m.simulate(next(x for x in m.SCENARIOS if x.key == 'lower_basis'))['sell'][0]
        self.assertGreater(low['event_tax'], 0)
        self.assertAlmostEqual(low['event_tax'], low['event_gain'] * .30)
        self.assertAlmostEqual(low['event_sale_net'], low['event_sale_price'] * .95 - low['event_tax'])

    def test_hypothetical_sale_limits_and_depreciation(self):
        base = m.simulate(m.SCENARIOS[0])
        self.assertEqual(base['rent'][-1]['a_depreciation'], 0)
        self.assertAlmostEqual(base['rent'][-1]['a_depreciation_accum'], base['rent'][0]['a_basis'] * m.A_BUILDING_SHARE)
        self.assertEqual(base['rent'][9]['b_depreciation'], 0)  # 2054
        self.assertGreater(base['rent'][8]['b_depreciation'], 0)  # half year 2053
        early = m.end_sale(2_000_000, 1_000_000, 0, 'live', 1)
        later = m.end_sale(2_000_000, 1_000_000, 0, 'live', 2)
        self.assertEqual(early['exclusion'], 0)
        self.assertEqual(later['exclusion'], 250_000)
        self.assertAlmostEqual(early['tax'] - later['tax'], 250_000 * m.GAIN_TAX)
        rental = m.end_sale(2_000_000, 1_000_000, 200_000, 'rent', 10)
        self.assertEqual(rental['recapture'], 200_000)
        self.assertAlmostEqual(rental['tax'], 200_000 * .35 + 900_000 * .30)

    def test_model_decomposition_and_horizons(self):
        for event in (2040, 2045, 2050):
            res = m.simulate(m.SCENARIOS[0], event)
            for choice in m.STRATEGIES:
                self.assertEqual(len(res[choice]), 50)
                self.assertEqual(res[choice][9]['year'], event + 9)
                self.assertEqual(res[choice][-1]['year'], event + 49)
                for r in res[choice]:
                    self.assertAlmostEqual(r['position'], r['b_end_value'] + r['account'] + r['a_exit_net'])
                    self.assertAlmostEqual(r['net_cash'], r['a_net'] + r['b_net'])
                    self.assertTrue(math.isfinite(r['position']))

    def test_shocks_only_at_specified_time_and_tax_lag(self):
        base = m.simulate(m.SCENARIOS[0])
        market = m.simulate(next(x for x in m.SCENARIOS if x.key == 'market'))
        for choice in m.STRATEGIES:
            self.assertAlmostEqual(base[choice][4]['position'], market[choice][4]['position']) # 2049
            self.assertAlmostEqual(market[choice][5]['b_end_value'], market[choice][5]['b_start_value'] * .75)
            self.assertAlmostEqual(market[choice][6]['b_start_value'], market[choice][5]['b_end_value'])
            self.assertAlmostEqual(market[choice][6]['b_assessed'], min(market[choice][6]['b_factored'], market[choice][6]['b_start_value']))
            self.assertAlmostEqual(market[choice][5]['b_rent_gross'], market[choice][4]['b_rent_gross'])
        disaster = m.simulate(next(x for x in m.SCENARIOS if x.key == 'disaster'))
        self.assertEqual(disaster['live'][10]['a_extra'], 250_000)
        self.assertEqual(disaster['sell'][10]['a_extra'], 0)
        self.assertEqual(disaster['sell'][10]['b_extra'], 100_000)

    def test_estate_is_transferor_only_and_future_is_a_scenario(self):
        estate = m.estate_table()
        self.assertEqual(estate[0]['exclusion'], 15_000_000)
        self.assertEqual(estate[1]['exclusion'], 15_480_000)
        self.assertTrue(estate[1]['official_exclusion'])
        self.assertFalse(estate[2]['official_exclusion'])
        self.assertEqual(estate[0]['estate'], 12_000_000)
        self.assertAlmostEqual(estate[2]['exclusion'], 15_480_000 * 1.025)
        for row in estate:
            self.assertAlmostEqual(row['estimated_tax'], max(0, row['estate'] - row['exclusion']) * .4)


if __name__ == '__main__':
    unittest.main()
