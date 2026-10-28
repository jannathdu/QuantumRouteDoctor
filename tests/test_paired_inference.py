"""Tests for exact McNemar inference on paired routing outcomes."""

import unittest

from backend.core.paired_inference import (
    analyze_paired_feasibility,
    mcnemar_exact_test,
)
from backend.core.research_experiments import run_research_experiments


class TestPairedInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = run_research_experiments(
            seeds=[42, 43, 44, 45, 46],
            node_count=10,
            link_count=15,
            current_time=10.0,
            minimum_fidelity=0.5,
            maximum_aoi=5.0,
        )

        cls.result = analyze_paired_feasibility(cls.records)

    def test_scenario_count(self):
        self.assertEqual(self.result["scenario_count"], 5)

    def test_baseline_feasibility_rate(self):
        self.assertAlmostEqual(
            self.result["baseline_feasibility_rate"], 0.6
        )

    def test_temporal_feasibility_rate(self):
        self.assertAlmostEqual(
            self.result["temporal_feasibility_rate"], 0.8
        )

    def test_paired_feasibility_difference(self):
        self.assertAlmostEqual(
            self.result["paired_feasibility_difference"], 0.2
        )

    def test_discordant_pairs(self):
        self.assertEqual(
            self.result["mcnemar"]["discordant_pairs"], 1
        )

    def test_exact_p_value_for_demo(self):
        self.assertEqual(
            self.result["mcnemar"]["p_value"], 1.0
        )

    def test_no_discordant_pairs(self):
        result = mcnemar_exact_test(0, 0)
        self.assertEqual(result["p_value"], 1.0)
        self.assertEqual(result["discordant_pairs"], 0)

    def test_balanced_discordant_pairs(self):
        result = mcnemar_exact_test(5, 5)
        self.assertEqual(result["p_value"], 1.0)

    def test_strong_imbalance(self):
        result = mcnemar_exact_test(0, 10)
        self.assertAlmostEqual(
            result["p_value"], 0.001953125
        )

    def test_symmetry(self):
        first = mcnemar_exact_test(2, 8)
        second = mcnemar_exact_test(8, 2)
        self.assertEqual(first["p_value"], second["p_value"])

    def test_invalid_negative_count(self):
        with self.assertRaises(ValueError):
            mcnemar_exact_test(-1, 3)

    def test_invalid_boolean_count(self):
        with self.assertRaises(ValueError):
            mcnemar_exact_test(True, 3)

    def test_not_statistically_significant_demo(self):
        self.assertFalse(
            self.result["statistically_significant_at_0_05"]
        )


if __name__ == "__main__":
    unittest.main()
