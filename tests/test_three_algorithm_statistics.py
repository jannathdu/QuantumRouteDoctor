import unittest

from backend.core.three_algorithm_experiments import (
    run_three_algorithm_experiments,
)
from backend.core.three_algorithm_statistics import (
    summarize_three_algorithm_experiments,
)


class TestThreeAlgorithmStatistics(unittest.TestCase):

    def setUp(self):
        self.records = run_three_algorithm_experiments(
            seeds=[100, 101],
            aoi_thresholds=[2.0, 4.0],
            minimum_fidelity_thresholds=[0.5, 0.7],
        )

    def test_summary_dimensions(self):
        summary = summarize_three_algorithm_experiments(self.records)
        self.assertEqual(summary["parameter_combinations"], 4)
        self.assertEqual(summary["scenario_count"], 8)

    def test_all_algorithms_summarized(self):
        summary = summarize_three_algorithm_experiments(self.records)
        self.assertEqual(
            summary["algorithms"],
            ["baseline", "memory_aware", "temporal"],
        )
        for result in summary["results"]:
            self.assertEqual(
                set(result["algorithms"]),
                {"baseline", "memory_aware", "temporal"},
            )

    def test_feasibility_rates_are_valid(self):
        summary = summarize_three_algorithm_experiments(self.records)
        for result in summary["results"]:
            for metrics in result["algorithms"].values():
                self.assertGreaterEqual(metrics["feasibility_rate"], 0.0)
                self.assertLessEqual(metrics["feasibility_rate"], 1.0)
                low, high = metrics["feasibility_ci_95"]
                self.assertLessEqual(low, high)
                self.assertGreaterEqual(low, 0.0)
                self.assertLessEqual(high, 1.0)

    def test_paired_counts_sum_to_scenario_count(self):
        summary = summarize_three_algorithm_experiments(self.records)
        for result in summary["results"]:
            for comparison in result["paired_comparisons"].values():
                total = (
                    comparison["both_feasible"]
                    + sum(
                        value
                        for key, value in comparison.items()
                        if key.endswith("_only")
                    )
                    + comparison["neither_feasible"]
                )
                self.assertEqual(total, result["scenario_count"])

    def test_empty_records_rejected(self):
        with self.assertRaises(ValueError):
            summarize_three_algorithm_experiments([])

    def test_missing_algorithm_rejected(self):
        with self.assertRaises(ValueError):
            summarize_three_algorithm_experiments(self.records[:-1])


if __name__ == "__main__":
    unittest.main()
