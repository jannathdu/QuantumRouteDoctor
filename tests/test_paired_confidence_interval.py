"""Tests for paired bootstrap feasibility confidence intervals."""

import unittest

from backend.core.research_experiments import run_research_experiments
from backend.core.paired_confidence_interval import (
    paired_bootstrap_feasibility_ci,
)


class TestPairedConfidenceInterval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = run_research_experiments(
            seeds=list(range(100, 200)),
            node_count=10,
            link_count=15,
            current_time=10.0,
            minimum_fidelity=0.5,
            maximum_aoi=5.0,
        )
        cls.result = paired_bootstrap_feasibility_ci(
            cls.records,
            bootstrap_samples=1000,
            random_seed=2026,
        )

    def test_scenario_count(self):
        self.assertEqual(self.result["scenario_count"], 100)

    def test_observed_difference(self):
        self.assertAlmostEqual(
            self.result["observed_difference"], 0.27
        )

    def test_confidence_level(self):
        self.assertEqual(self.result["confidence_level"], 0.95)

    def test_interval_order(self):
        low, high = self.result["confidence_interval"]
        self.assertLessEqual(low, high)

    def test_interval_bounds(self):
        low, high = self.result["confidence_interval"]
        self.assertGreaterEqual(low, -1.0)
        self.assertLessEqual(high, 1.0)

    def test_observed_difference_inside_interval(self):
        low, high = self.result["confidence_interval"]
        self.assertLessEqual(
            low, self.result["observed_difference"]
        )
        self.assertGreaterEqual(
            high, self.result["observed_difference"]
        )

    def test_reproducibility(self):
        repeat = paired_bootstrap_feasibility_ci(
            self.records,
            bootstrap_samples=1000,
            random_seed=2026,
        )
        self.assertEqual(
            self.result["confidence_interval"],
            repeat["confidence_interval"],
        )

    def test_bootstrap_sample_count(self):
        self.assertEqual(self.result["bootstrap_samples"], 1000)

    def test_method_label(self):
        self.assertEqual(
            self.result["method"], "paired_percentile_bootstrap"
        )

    def test_invalid_bootstrap_sample_count(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_feasibility_ci(
                self.records, bootstrap_samples=1
            )

    def test_invalid_confidence_level(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_feasibility_ci(
                self.records, confidence_level=1.0
            )

    def test_invalid_random_seed(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_feasibility_ci(
                self.records, random_seed=True
            )

    def test_empty_records_rejected(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_feasibility_ci([])


if __name__ == "__main__":
    unittest.main()
