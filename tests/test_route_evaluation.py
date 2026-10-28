import unittest

from backend.core.temporal_network import create_temporal_demo_network
from backend.core.route_evaluation import evaluate_route
from backend.core.network_evolution import evolve_network_state


class TestRouteEvaluation(unittest.TestCase):

    def setUp(self):
        self.graph = create_temporal_demo_network(current_time=10.0)

    def evaluate(self, graph=None, route=None, threshold=0.8, aoi=5.0, time=10.0):
        return evaluate_route(
            self.graph if graph is None else graph,
            ["A", "B", "C"] if route is None else route,
            current_time=time,
            minimum_fidelity=threshold,
            maximum_aoi=aoi,
        )

    def test_reference_fidelity(self):
        result = self.evaluate()
        self.assertAlmostEqual(result["reference_fidelity"], 0.894, places=6)

    def test_memory_adjusted_fidelity(self):
        result = self.evaluate()
        self.assertAlmostEqual(
            result["memory_adjusted_fidelity"],
            0.8504616200194306,
            places=10,
        )

    def test_hop_count(self):
        result = self.evaluate()
        self.assertEqual(result["hop_count"], 2)

    def test_maximum_link_aoi(self):
        result = self.evaluate()
        self.assertEqual(result["maximum_link_aoi"], 5.0)

    def test_feasible_route(self):
        result = self.evaluate()
        self.assertTrue(result["feasible"])

    def test_strict_fidelity_threshold(self):
        result = self.evaluate(threshold=0.9)
        self.assertFalse(result["fidelity_feasible"])
        self.assertFalse(result["feasible"])

    def test_strict_aoi_threshold(self):
        result = self.evaluate(aoi=2.0)
        self.assertFalse(result["aoi_feasible"])
        self.assertFalse(result["feasible"])

    def test_missing_link_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(route=["A", "C"])

    def test_repeated_nodes_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(route=["A", "B", "A", "D", "C"])

    def test_evolved_memory_fidelity_decreases(self):
        evolved = evolve_network_state(self.graph, 10.0, 15.0)

        initial = self.evaluate()
        later = self.evaluate(graph=evolved, time=15.0, aoi=20.0)

        self.assertLess(
            later["memory_adjusted_fidelity"],
            initial["memory_adjusted_fidelity"],
        )


if __name__ == "__main__":
    unittest.main()
