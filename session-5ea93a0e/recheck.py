#!/usr/bin/env python3
"""Read-only ranking recheck for the independent audit.

Imports final/model.py without calling main(), so final/out/model.json and the
generated pages are not rewritten. Prints strategy rankings and win counts only;
it does not emit household dollar totals, ZIPs or historical bill series.
"""
from collections import Counter
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tino_model", ROOT / "final" / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

STRATEGIES = ("live", "rent", "sell")


def order(summary, prefix="w_"):
    return " > ".join(sorted(STRATEGIES, key=lambda k: summary[prefix + k], reverse=True))


def main():
    variants = [
        ("baseline", {}),
        ("no inferred third-unit rent", {"rent_sf_unit3": False}),
        ("HUD 3BR benchmark", {"cup_rent_month": 5870}),
        ("rent benchmark +30%", {"cup_rent_month": m.r10(6390 * 1.3)}),
        ("insurance x3", {"ins_home": 4500, "ins_rental": 4500}),
        ("maintenance x2", {"maint_cup": 12000}),
        ("vacancy 10%", {"vacancy": 0.10}),
        ("vacancy 15%", {"vacancy": 0.15}),
        ("management 10%", {"mgmt": 0.10}),
        ("stocks 5%", {"r_stock": 0.05}),
        ("60/40 stocks/bonds", {"w_stock": 0.6, "w_bond": 0.4}),
        ("T-bills only", {"w_stock": 0.0, "w_bill": 1.0}),
        ("no basis step-up", {"step_up": False}),
        ("transfer 2040", {"T": 2040}),
        ("transfer 2050", {"T": 2050}),
    ]
    print("Terminal rankings (assumption-dependent model output, not a forecast):")
    for label, kw in variants:
        print(f"  {label}: {order(m.run(m.with_(**kw))[1])}")

    corrected = m.with_(rent_sf_unit3=False)
    terminal = Counter()
    horizons = {"10": Counter(), "20": Counter()}
    for start in range(1976, 2026):
        summary = m.run(corrected, m.replay_path(start))[1]
        terminal[summary["best"]] += 1
        for h in horizons:
            d = summary["w" + h]
            horizons[h][max(STRATEGIES, key=lambda k: d[k])] += 1
    print("Replays with inferred third-unit rent removed:")
    print(f"  terminal: {dict(terminal)}")
    for h, counts in horizons.items():
        print(f"  {h}-year: {dict(counts)}")

    T = corrected["T"]
    named = [
        ("crash at transfer", m.overlay_path(corrected, m.HIST, 2007, 2012, T)),
        ("stagflation at transfer", m.overlay_path(corrected, m.HIST, 1977, 1982, T)),
        ("lost decade at transfer", m.overlay_path(corrected, m.HIST, 2000, 2009, T)),
        ("California slump at transfer", m.overlay_path(corrected, m.HIST, 1990, 1996, T)),
        ("Depression at transfer", m.overlay_path(corrected, m.NAT, 1929, 1941, T)),
        ("Japan at transfer", m.overlay_path(corrected, m.JPN, 1991, 2020, T)),
    ]
    print("Named overlays with inferred third-unit rent removed:")
    for label, path in named:
        print(f"  {label}: {order(m.run(corrected, path)[1])}")


if __name__ == "__main__":
    main()
