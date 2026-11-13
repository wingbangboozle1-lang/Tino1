"""Run: python3 -m unittest discover -s privacy-site -p 'test_*.py' -v"""
import unittest
import tempfile
import subprocess
import sys
from pathlib import Path
import shutil
from illustrations import r10, family_assessment, outlook, investment_path, STRESS, threshold, ledger
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
            # Fixture mirrors the allowlist in final/published.txt: the rounded-figures
            # analysis at the root plus the no-household-figures guide. Superseded root
            # stubs such as properties.html stay out of the published set.
            names=(repo/'final'/'published.txt').read_text().split()
            self.assertIn('index.html',names)
            self.assertIn('privacy-site/public/index.html',names)
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
        subprocess.run([sys.executable,str(here/'build.py')],check=True,capture_output=True)
        self.assertEqual(before,{p.name:p.read_bytes() for p in (here/'public').iterdir()})


if __name__=='__main__': unittest.main()
