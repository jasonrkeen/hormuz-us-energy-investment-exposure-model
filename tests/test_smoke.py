import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model import run_all
from src.valuation import valuation_score
from src.cycle_normalization import build_cycle_scenarios, cycle_resilience

class ModelSmokeTests(unittest.TestCase):
    def test_core_model_produces_all_scenarios(self):
        company = pd.read_csv(ROOT/"data/company_metrics.csv")
        factors, scores = run_all(company, market_perf=None)
        self.assertEqual(set(scores["scenario"].unique()),
                         {"normalization","persistent_disruption","severe_disruption"})
        self.assertEqual(len(factors), 5)

    def test_valuation_scores_are_bounded(self):
        valuation = pd.read_csv(ROOT/"data/valuation_current.csv")
        scored = valuation_score(valuation)
        self.assertTrue(((scored["valuation_score"] >= 0) &
                         (scored["valuation_score"] <= 100)).all())

    def test_cycle_scenarios_include_midcycle(self):
        cycle = pd.read_csv(ROOT/"data/cycle_normalization_inputs.csv")
        scenarios = build_cycle_scenarios(cycle)
        resilience = cycle_resilience(scenarios)
        self.assertIn("mid_cycle", set(scenarios["scenario"]))
        self.assertEqual(set(resilience["ticker"]), {"VLO","MPC","PSX"})

if __name__ == "__main__":
    unittest.main()
