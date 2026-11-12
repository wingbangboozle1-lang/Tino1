"""Run: python3 -m unittest discover -s privacy-site -p 'test_*.py' -v"""
import unittest
import tempfile
import subprocess
import sys
from pathlib import Path
import shutil
from illustrations import r10, family_assessment, outlook, investment_path, STRESS, threshold, ledger


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
        # Detect numeric vs privacy landing to choose mode
        is_numeric = 'privacy-site/public' not in (repo/'index.html').read_text()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            shutil.copyfile(repo/'index.html',root/'index.html')
            target=root/'privacy-site/public'
            target.mkdir(parents=True)
            for source in (here/'public').iterdir(): shutil.copyfile(source,target/source.name)
            cmd=[sys.executable,str(here/'check_published.py'),str(root)] + (['--allow-extra'] if is_numeric else [])
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            if not is_numeric:
                # Strict mode: extra file must be rejected
                (root/'leaked.json').write_text('{}')
                self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
                (root/'leaked.json').unlink()
            else:
                # Comprehensive mode allows extra numeric files — skip leaked-file check, test tamper instead
                pass
            (target/'index.html').write_text('modified')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)

    def test_reproducible_generation(self):
        here=Path(__file__).resolve().parent
        before={p.name:p.read_bytes() for p in (here/'public').iterdir()}
        subprocess.run([sys.executable,str(here/'build.py')],check=True,capture_output=True)
        self.assertEqual(before,{p.name:p.read_bytes() for p in (here/'public').iterdir()})


if __name__=='__main__': unittest.main()
