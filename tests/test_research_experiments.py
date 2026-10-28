import unittest

from backend.core.research_experiments import run_research_experiments


class TestResearchExperiments(unittest.TestCase):

    def run_experiment(self, seeds=None):
        return run_research_experiments(
            seeds=[42, 43, 44, 45, 46] if seeds is None else seeds,
            node_count=10,
            link_count=15,
            current_time=10.0,
            minimum_fidelity=0.5,
            maximum_aoi=5.0,
        )

    def test_record_count(self):
        records = self.run_experiment()
        self.assertEqual(len(records), 10)

    def test_algorithm_pairing(self):
        records = self.run_experiment()

        for seed in [42, 43, 44, 45, 46]:
            pair = [r for r in records if r["seed"] == seed]
            self.assertEqual(len(pair), 2)
            self.assertEqual(
                {r["algorithm"] for r in pair},
                {"baseline", "temporal"},
            )

    def test_reproducibility(self):
        first = self.run_experiment()
        second = self.run_experiment()
        self.assertEqual(first, second)

    def test_record_fields(self):
        required = {
            "seed",
            "node_count",
            "link_count",
            "algorithm",
            "selected_route",
            "hop_count",
            "memory_adjusted_fidelity",
            "maximum_link_aoi",
            "feasible",
            "data_source",
        }

        for record in self.run_experiment():
            self.assertTrue(required.issubset(record))

    def test_selected_route_metrics(self):
        for record in self.run_experiment():
            if record["route_selected"]:
                self.assertIsNotNone(record["selected_route"])
                self.assertIsNotNone(
                    record["memory_adjusted_fidelity"]
                )
                self.assertEqual(
                    record["hop_count"],
                    len(record["selected_route"]) - 1,
                )

    def test_no_route_metrics_are_none(self):
        for record in self.run_experiment():
            if not record["route_selected"]:
                self.assertIsNone(record["selected_route"])
                self.assertIsNone(
                    record["memory_adjusted_fidelity"]
                )
                self.assertFalse(record["feasible"])

    def test_temporal_selected_routes_feasible(self):
        for record in self.run_experiment():
            if record["algorithm"] == "temporal" and record["route_selected"]:
                self.assertTrue(record["feasible"])

    def test_invalid_seed_rejected(self):
        with self.assertRaises(ValueError):
            self.run_experiment(seeds=["invalid"])

    def test_duplicate_seeds_rejected(self):
        with self.assertRaises(ValueError):
            self.run_experiment(seeds=[42, 42])

    def test_empty_seeds_rejected(self):
        with self.assertRaises(ValueError):
            self.run_experiment(seeds=[])


if __name__ == "__main__":
    unittest.main()
