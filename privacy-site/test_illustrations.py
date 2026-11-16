"""Run: python3 -m unittest discover -s privacy-site -p 'test_*.py' -v"""
import unittest
import tempfile
import subprocess
import sys
from pathlib import Path
import shutil
from illustrations import (r10, family_assessment, outlook, investment_path, phased_entry, STRESS, threshold, ledger,
                           CPI_ANNUAL, cpi_decades, cpi_extremes, cpi_display_rows, episode_replay, cash_leg,
                           all_start_years, staged_summary, lump_sum_return, STOCK, BILL, GS2, HISTORY)
from check import pii_kinds


class PrivacyPatternTests(unittest.TestCase):
    def test_synthetic_pii_patterns_are_detected_without_echoing_values(self):
        self.assertEqual(pii_kinds('Generic guidance; no contact or property identifier.'), [])
        examples = {
            'street address': '123 Example Street',
            'email address': 'person@example.invalid',
            'phone number': '(555) 234-6789',
            'parcel-number pattern': '123-45-678',
        }
        for kind, example in examples.items():
            with self.subTest(kind=kind):
                self.assertIn(kind, pii_kinds(example))


class ArithmeticTests(unittest.TestCase):
    def test_round_half_up(self):
        self.assertEqual(r10(105),110)
        self.assertEqual(r10(-105),-110)
        self.assertEqual(r10(104.99),100)

    def test_family_home_threshold_branches(self):
        self.assertEqual(family_assessment(1000000,200000,1000000),200000)
        self.assertEqual(family_assessment(1200000,200000,1000000),200000)
        self.assertEqual(family_assessment(2000000,200000,1000000),1000000)

    def test_full_annual_series_and_transfer(self):
        for transfer in (2040,2045,2050):
            rows=outlook(transfer)
            self.assertEqual([r['year'] for r in rows], list(range(2026,2077)))
            before=rows[transfer-2026-1]
            at=rows[transfer-2026]
            after=rows[transfer-2026+1]
            self.assertAlmostEqual(at['rental_assessed'], at['market'])
            self.assertAlmostEqual(at['live_assessed'], family_assessment(at['market'],before['live_assessed']*1.02,1000000))
            self.assertAlmostEqual(after['live_assessed'], at['live_assessed']*1.02)
            for r in rows:
                self.assertLessEqual(r['live_assessed'],r['market'])
                self.assertLessEqual(r['live_assessed'],r['rental_assessed'])
                self.assertAlmostEqual(r['live_tax'],r['live_assessed']*.012)
        self.assertEqual(outlook()[0]['real_market'],1000000)
        self.assertAlmostEqual(outlook()[-1]['insurance'],3000*1.025**50)

    def test_stress_and_real_value(self):
        crash=investment_path(*STRESS['Market crash, then recovery'])
        late=investment_path(*STRESS['Late market crash (year 20)'])
        self.assertEqual(crash[0]['nominal'],600000)
        self.assertAlmostEqual(crash[-1]['nominal'],late[-1]['nominal'])
        self.assertAlmostEqual(crash[-1]['real'],crash[-1]['nominal']/1.025**50)
        for r,c in STRESS.values(): self.assertEqual(len(r),50); self.assertEqual(len(c),50)

    def test_phased_entry_helps_front_loaded_crash_but_lags_bull_market(self):
        crash=[-.37,.26,.15,.02,.16,.07,.07,.07,.07,.07]
        bull=[.12,.10,.08,.07,.07,.07,.07,.07,.07,.07]
        immediate_crash=100000
        for ret in crash: immediate_crash*=1+ret
        immediate_bull=100000
        for ret in bull: immediate_bull*=1+ret
        staged_crash=phased_entry(crash,wait_months=30,park_rate=.03)['staged']
        staged_bull=phased_entry(bull,wait_months=30,park_rate=.03)['staged']
        self.assertGreater(staged_crash,immediate_crash)
        self.assertLess(staged_bull,immediate_bull)
        low=phased_entry(crash,wait_months=30,park_rate=.02)['staged']
        high=phased_entry(crash,wait_months=30,park_rate=.04)['staged']
        self.assertLess(low,staged_crash)
        self.assertGreater(high,staged_crash)

    def test_first_year_independent_bridge(self):
        r=ledger(years=1)
        first=r['first_year']
        self.assertEqual(first['rent'],34200)
        self.assertEqual(first['expenses'],30736)
        self.assertEqual(first['income_tax'],0)
        self.assertEqual(first['cash'],3464)
        self.assertAlmostEqual(r['sell_wealth'],997500)
        # Independently compute liquidated one-year rental outcome.
        dep=400000/27.5
        gain=1000000*1.03*.95-(1000000+4000-dep)
        self.assertAlmostEqual(r['rent_wealth'],978500-max(0,gain)*.35+3464)

    def test_official_cpi_series_is_complete_and_has_no_gaps(self):
        self.assertEqual(sorted(CPI_ANNUAL), list(range(1970, 2017)))
        for year, value in CPI_ANNUAL.items():
            self.assertGreater(value, -5, year)
            self.assertLess(value, 20, year)
        # Published decade figures, checked against the BLS table by hand.
        self.assertEqual(CPI_ANNUAL[1974], 11.0)
        self.assertEqual(CPI_ANNUAL[1980], 13.5)
        self.assertEqual(CPI_ANNUAL[2009], -0.4)
        self.assertEqual(CPI_ANNUAL[2015], 0.1)

    def test_cpi_summary_matches_independent_arithmetic(self):
        rows = {r['label']: r for r in cpi_decades()}
        self.assertEqual(rows['1970s']['count'], 10)
        self.assertEqual(rows['1970s']['at_least_5'], 8)
        self.assertAlmostEqual(rows['1970s']['mean'], 70.8 / 10, places=6)
        total = rows['1970–2016 total']
        self.assertEqual(total['count'], 47)
        self.assertEqual(total['at_least_5'], 12)
        self.assertEqual(total['below_2'], 9)
        self.assertAlmostEqual(total['mean'], sum(CPI_ANNUAL.values()) / 47, places=6)
        high, negative = cpi_extremes()
        self.assertEqual(high, [1974, 1975, 1979, 1980, 1981])
        self.assertEqual(negative, [2009])

    def test_cpi_display_rows_are_formatted_not_altered(self):
        rows = {r[0]: r for r in cpi_display_rows()}
        self.assertEqual(rows['1970s'][1:], ('10', '+3.2%', '+11.3%', '+7.08%', '8', 'none'))
        self.assertEqual(rows['2000s'][5:], ('none', '2 (1 is a deflation year)'))
        self.assertEqual(len(rows), 6)

    def test_sensitivity_direction(self):
        self.assertGreater(ledger(gross=60000)['rent_wealth'],ledger()['rent_wealth'])
        self.assertGreater(ledger(house_growth=.05)['rent_wealth'],ledger()['rent_wealth'])
        self.assertEqual(threshold(2027,.04),15480000)
        self.assertEqual(threshold(2050,0),15480000)


class PublicationTests(unittest.TestCase):
    def test_source_allowlist_rejects_extra_file_and_modified_content(self):
        here=Path(__file__).resolve().parent
        repo=here.parent
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            # Fixture mirrors the privacy-first allowlist: one generic root landing
            # plus the figure-free guide. Numeric analysis pages stay repository-only.
            names=(repo/'final'/'published.txt').read_text().split()
            self.assertIn('index.html',names)
            self.assertIn('privacy-site/public/index.html',names)
            self.assertIn('privacy-site/public/brief.html',names)
            self.assertIn('privacy-site/public/issues.html',names)
            self.assertNotIn('summary.html',names)
            self.assertNotIn('black-swan.html',names)
            self.assertNotIn('projections.html',names)
            self.assertNotIn('properties.html',names)
            self.assertNotIn('dashboard/index.html',names)
            for name in names:
                dst=root/name
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(repo/name,dst)
            target=root/'privacy-site/public'
            cmd=[sys.executable,str(here/'check_published.py'),str(root)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            (root/'leaked.json').write_text('{}')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            (root/'leaked.json').unlink()
            (root/'properties.html').write_text('<p>not public</p>')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            (root/'properties.html').unlink()
            (target/'index.html').write_text('modified')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)

    def test_reproducible_generation(self):
        here=Path(__file__).resolve().parent
        before={p.name:p.read_bytes() for p in (here/'public').iterdir()}
        landing=(here.parent/'index.html').read_bytes()
        template=(here/'landing.html').read_bytes()
        self.assertEqual(landing,template)
        subprocess.run([sys.executable,str(here/'build.py')],check=True,capture_output=True)
        self.assertEqual(before,{p.name:p.read_bytes() for p in (here/'public').iterdir()})
        self.assertEqual(template,(here.parent/'index.html').read_bytes())


if __name__=='__main__': unittest.main()


class HistoricalStagedEntryTests(unittest.TestCase):
    """The staged-entry page is the one page built on real history: check its engine."""

    def test_history_file_is_complete_and_monotonic(self):
        self.assertEqual(sorted(STOCK), list(range(1928, 2026)))
        self.assertEqual(sorted(BILL), list(range(1934, 2026)))
        self.assertEqual(sorted(GS2), list(range(1977, 2026)))
        # Spot values re-read on the official and academic pages on 2026-11-16.
        self.assertEqual(round(STOCK[1929], 2), -0.08)
        self.assertEqual(round(STOCK[2008], 4), -0.3655)
        self.assertEqual(HISTORY['stock']['status'].startswith('non-government'), True)
        self.assertEqual(HISTORY['bill3m']['status'].startswith('official'), True)

    def test_cash_leg_never_invents_a_missing_series(self):
        self.assertIsNone(cash_leg(1929, 3))            # before the bill series
        self.assertEqual(cash_leg(1973, 3)['mode'], 'bill')    # no 2-year leg yet
        self.assertEqual(cash_leg(2007, 3)['mode'], 'ladder')  # both legs official
        leg = cash_leg(2007, 3)
        self.assertAlmostEqual(leg['rate'], ((BILL[2007]+GS2[2007])/2+(BILL[2008]+GS2[2008])/2
                                             + (BILL[2009]+GS2[2009])/2)/3)

    def test_empty_park_reproduces_the_lump_sum(self):
        for year in (1990, 2008, 2015):
            r = episode_replay(year, park_years=0, phase_years=1)
            self.assertAlmostEqual(r['staged'], r['lump_sum'], places=12)
            self.assertAlmostEqual(r['staged'], lump_sum_return(year), places=12)

    def test_proceeds_are_conserved_and_direction_is_as_stated(self):
        # 1929: the parked leg is an explicit 0% assumption, and staging still wins.
        self.assertGreater(episode_replay(1929, cash_fallback=0.0)['staged'],
                           episode_replay(1929, cash_fallback=0.0)['lump_sum'])
        # 2008: official legs, small advantage, not a large one.
        r08 = episode_replay(2008)
        self.assertGreater(r08['staged'], r08['lump_sum'])
        self.assertLess(r08['staged']/r08['lump_sum'] - 1, 0.10)
        # 1950: a strong rising market, so the wait is a large cost.
        self.assertLess(episode_replay(1950)['staged'], episode_replay(1950)['lump_sum'])
        # An unverifiable window returns blanks rather than a number.
        blank = episode_replay(1929)
        self.assertIsNone(blank['staged'])
        self.assertIsNotNone(blank['lump_sum'])

    def test_distribution_counts_match_the_rows(self):
        rows = [r for r in all_start_years(3, 3, 10) if r['staged'] is not None]
        s = staged_summary(rows)
        self.assertEqual(s['n'], len(rows))
        self.assertEqual(s['wins'] + s['losses'] + s['ties'], s['n'])
        self.assertGreater(s['losses'], s['wins'])   # stated on the page
        self.assertGreaterEqual(s['high'], s['median'])
        self.assertGreaterEqual(s['median'], s['low'])
        for r in rows:
            self.assertTrue(-10 < r['difference'] < 10)


class StagedEntryPageTests(unittest.TestCase):
    def test_page_is_inside_the_allowlist_and_links_its_sources(self):
        page = Path(__file__).parent/'public'/'phased.html'
        self.assertTrue(page.is_file())
        text = page.read_text()
        self.assertIn('noindex,nofollow', text)
        for phrase in ('What would change the answer', 'Reinvestment risk',
                       'Limits, stated plainly', 'not a forecast'):
            self.assertIn(phrase, text)
