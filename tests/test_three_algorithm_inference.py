import unittest

from backend.core.three_algorithm_inference import (
    exact_mcnemar_p_value,
    holm_adjust,
    analyze_three_algorithm_inference,
)
from backend.core.three_algorithm_experiments import (
    run_three_algorithm_experiments,
)
from backend.core.three_algorithm_statistics import (
    summarize_three_algorithm_experiments,
)


class TestThreeAlgorithmInference(unittest.TestCase):

    def test_exact_mcnemar_balanced_pairs(self):
        self.assertAlmostEqual(
            exact_mcnemar_p_value(5, 5), 1.0
        )

    def test_exact_mcnemar_no_discordant_pairs(self):
        self.assertEqual(exact_mcnemar_p_value(0, 0), 1.0)

    def test_exact_mcnemar_known_result(self):
        self.assertAlmostEqual(
            exact_mcnemar_p_value(0, 4), 0.125
        )

    def test_invalid_discordant_count(self):
        with self.assertRaises(ValueError):
            exact_mcnemar_p_value(-1, 3)

    def test_holm_adjustment(self):
        adjusted = holm_adjust([0.01, 0.04, 0.03])
        self.assertEqual(adjusted, [0.03, 0.06, 0.06])

    def test_holm_preserves_input_order(self):
        adjusted = holm_adjust([0.04, 0.001])
        self.assertEqual(adjusted, [0.04, 0.002])

    def test_invalid_p_value(self):
        with self.assertRaises(ValueError):
            holm_adjust([0.01, 1.5])

    def test_invalid_alpha(self):
        with self.assertRaises(ValueError):
            analyze_three_algorithm_inference({}, alpha=1.0)

    def test_all_pairwise_comparisons_included(self):
        records = run_three_algorithm_experiments(
            seeds=[100, 101],
            aoi_thresholds=[2.0, 4.0],
            minimum_fidelity_thresholds=[0.5, 0.7],
        )
        summary = summarize_three_algorithm_experiments(records)
        inference = analyze_three_algorithm_inference(summary)

        self.assertEqual(inference["family_size"], 12)
        self.assertEqual(len(inference["comparisons"]), 12)

    def test_adjusted_p_values_are_valid(self):
        records = run_three_algorithm_experiments(
            seeds=[100, 101],
            aoi_thresholds=[2.0],
            minimum_fidelity_thresholds=[0.5],
        )
        summary = summarize_three_algorithm_experiments(records)
        inference = analyze_three_algorithm_inference(summary)

        for result in inference["comparisons"]:
            self.assertGreaterEqual(
                result["holm_adjusted_p_value"], result["p_value"]
            )
            self.assertLessEqual(
                result["holm_adjusted_p_value"], 1.0
            )
            self.assertEqual(
                result["significant_after_holm"],
                result["holm_adjusted_p_value"] < 0.05,
            )


if __name__ == "__main__":
    unittest.main()
