"""Tests for descriptive paired quantum routing statistics."""

import unittest

from backend.core.research_experiments import run_research_experiments
from backend.core.research_statistics import (
    summarize_paired_experiments,
    wilson_interval,
)


class TestResearchStatistics(unittest.TestCase):

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
        cls.summary = summarize_paired_experiments(cls.records)

    def test_scenario_count(self):
        self.assertEqual(self.summary["scenario_count"], 5)

    def test_baseline_feasibility_rate(self):
        result = self.summary["algorithms"]["baseline"]
        self.assertEqual(result["feasible_count"], 3)
        self.assertAlmostEqual(result["feasibility_rate"], 0.6)

    def test_temporal_feasibility_rate(self):
        result = self.summary["algorithms"]["temporal"]
        self.assertEqual(result["feasible_count"], 4)
        self.assertAlmostEqual(result["feasibility_rate"], 0.8)

    def test_paired_outcomes(self):
        self.assertEqual(
            self.summary["paired_outcomes"],
            {
                "both_feasible": 3,
                "baseline_only": 0,
                "temporal_only": 1,
                "neither_feasible": 1,
            },
        )

    def test_wilson_interval(self):
        low, high = wilson_interval(3, 5)
        self.assertAlmostEqual(low, 0.2307, places=4)
        self.assertAlmostEqual(high, 0.8824, places=4)

    def test_wilson_extreme_proportions(self):
        for successes in [0, 10]:
            low, high = wilson_interval(successes, 10)
            self.assertGreaterEqual(low, 0.0)
            self.assertLessEqual(high, 1.0)
            self.assertLessEqual(low, high)

    def test_feasible_only_mean_fidelity(self):
        algorithms = self.summary["algorithms"]
        self.assertAlmostEqual(
            algorithms["baseline"]["mean_fidelity_given_feasible"],
            0.862867,
            places=5,
        )
        self.assertAlmostEqual(
            algorithms["temporal"]["mean_fidelity_given_feasible"],
            0.850941,
            places=5,
        )

    def test_duplicate_algorithm_rejected(self):
        records = self.records + [self.records[0]]
        with self.assertRaises(ValueError):
            summarize_paired_experiments(records)

    def test_missing_pair_rejected(self):
        records = self.records[:-1]
        with self.assertRaises(ValueError):
            summarize_paired_experiments(records)

    def test_empty_records_rejected(self):
        with self.assertRaises(ValueError):
            summarize_paired_experiments([])

    def test_invalid_wilson_counts_rejected(self):
        for successes, total in [(-1, 5), (6, 5), (0, 0)]:
            with self.subTest(successes=successes, total=total):
                with self.assertRaises(ValueError):
                    wilson_interval(successes, total)


if __name__ == "__main__":
    unittest.main()
