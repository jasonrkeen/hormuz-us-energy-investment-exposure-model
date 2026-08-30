import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.market_data import performance_table
from src.crack_regimes import summarize_crack_regimes
from src.cycle_normalization import build_cycle_scenarios, cycle_resilience
from src.normalized_valuation import build_q2_replacement_bridge, build_pass_through_sensitivity


class V051Tests(unittest.TestCase):
    def test_performance_table_records_sample_dates(self):
        idx = pd.to_datetime(["2026-01-02", "2026-08-28"])
        px = pd.DataFrame({"VLO": [100.0, 120.0]}, index=idx)
        result = performance_table(px)
        self.assertEqual(result.loc[0, "sample_start"], "2026-01-02")
        self.assertEqual(result.loc[0, "sample_end"], "2026-08-28")

    def test_crack_regime_records_observation_cutoff(self):
        idx = pd.to_datetime(["2026-07-01", "2026-08-28"])
        crack = pd.DataFrame({"crack_321_usd_per_bbl": [50.0, 75.0]}, index=idx)
        result = summarize_crack_regimes(crack)
        row = result[result["regime"] == "extreme_jul_aug_2026"].iloc[0]
        self.assertEqual(row["defined_window_end"], "2026-08-31")
        self.assertEqual(row["observed_through"], "2026-08-28")

    def test_normalized_valuation_outputs_are_positive(self):
        valuation = pd.read_csv(ROOT/"data/valuation_current.csv")
        cycle = pd.read_csv(ROOT/"data/cycle_normalization_inputs.csv")
        fundamentals = pd.read_csv(ROOT/"data/normalized_valuation_fundamentals.csv")
        scenarios = build_cycle_scenarios(cycle)
        resilience = cycle_resilience(scenarios)
        bridge = build_q2_replacement_bridge(valuation, resilience, cycle, fundamentals)
        sensitivity = build_pass_through_sensitivity(valuation, resilience)
        self.assertEqual(set(bridge["ticker"]), {"VLO", "MPC", "PSX"})
        self.assertTrue((bridge["implied_ev_ebitda_after_q2_replacement"] > 0).all())
        self.assertTrue((sensitivity["stressed_ev_ebitda"] > 0).all())

    def test_vlo_midcycle_bridge_is_below_mpc(self):
        valuation = pd.read_csv(ROOT/"data/valuation_current.csv")
        cycle = pd.read_csv(ROOT/"data/cycle_normalization_inputs.csv")
        fundamentals = pd.read_csv(ROOT/"data/normalized_valuation_fundamentals.csv")
        resilience = cycle_resilience(build_cycle_scenarios(cycle))
        bridge = build_q2_replacement_bridge(valuation, resilience, cycle, fundamentals)
        mid = bridge[bridge["scenario"] == "mid_cycle"].set_index("ticker")
        self.assertLess(
            mid.loc["VLO", "implied_ev_ebitda_after_q2_replacement"],
            mid.loc["MPC", "implied_ev_ebitda_after_q2_replacement"],
        )


if __name__ == "__main__":
    unittest.main()
