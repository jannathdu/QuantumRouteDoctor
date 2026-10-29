import unittest

from backend.core.three_algorithm_experiments import (
    run_three_algorithm_experiments,
)


class TestThreeAlgorithmExperiments(unittest.TestCase):

    def run_small_experiment(self, seeds=(100, 101)):
        return run_three_algorithm_experiments(
            seeds=list(seeds),
            aoi_thresholds=[2.0, 4.0],
            minimum_fidelity_thresholds=[0.5, 0.7],
        )

    def test_record_count(self):
        self.assertEqual(len(self.run_small_experiment()), 24)

    def test_all_three_algorithms_present(self):
        records = self.run_small_experiment()
        self.assertEqual(
            {record["algorithm"] for record in records},
            {"baseline", "memory_aware", "temporal"},
        )

    def test_each_scenario_has_three_algorithms(self):
        records = self.run_small_experiment()
        groups = {}

        for record in records:
            key = (
                record["seed"],
                record["maximum_aoi"],
                record["minimum_fidelity"],
            )
            groups.setdefault(key, []).append(record["algorithm"])

        self.assertEqual(len(groups), 8)

        for algorithms in groups.values():
            self.assertEqual(
                set(algorithms),
                {"baseline", "memory_aware", "temporal"},
            )
            self.assertEqual(len(algorithms), 3)

    def test_reproducibility(self):
        self.assertEqual(
            self.run_small_experiment(),
            self.run_small_experiment(),
        )

    def test_selected_routes_have_metrics(self):
        for record in self.run_small_experiment():
            if record["route_selected"]:
                self.assertIsNotNone(record["selected_route"])
                self.assertIsNotNone(record["hop_count"])
                self.assertIsNotNone(
                    record["memory_adjusted_fidelity"]
                )
                self.assertIsInstance(record["feasible"], bool)

    def test_temporal_selected_routes_are_feasible(self):
        for record in self.run_small_experiment():
            if record["algorithm"] == "temporal":
                if record["route_selected"]:
                    self.assertTrue(record["feasible"])

    def test_empty_seeds_rejected(self):
        with self.assertRaises(ValueError):
            run_three_algorithm_experiments(seeds=[])

    def test_duplicate_seeds_rejected(self):
        with self.assertRaises(ValueError):
            run_three_algorithm_experiments(seeds=[100, 100])

    def test_invalid_fidelity_threshold_rejected(self):
        with self.assertRaises(ValueError):
            run_three_algorithm_experiments(
                seeds=[100],
                minimum_fidelity_thresholds=[1.5],
            )

    def test_invalid_aoi_threshold_rejected(self):
        with self.assertRaises(ValueError):
            run_three_algorithm_experiments(
                seeds=[100],
                aoi_thresholds=[-1.0],
            )


if __name__ == "__main__":
    unittest.main()
