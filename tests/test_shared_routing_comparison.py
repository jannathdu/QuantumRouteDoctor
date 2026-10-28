import unittest

from backend.core.temporal_network import create_temporal_demo_network
from backend.core.fidelity_routing import find_fidelity_constrained_route
from backend.core.temporal_routing import find_temporal_route
from backend.core.route_evaluation import evaluate_route


class TestSharedRoutingComparison(unittest.TestCase):

    def setUp(self):
        self.graph = create_temporal_demo_network(current_time=10.0)

        self.baseline = find_fidelity_constrained_route(
            self.graph, "A", "C", minimum_fidelity=0.8
        )

        self.temporal = find_temporal_route(
            self.graph, "A", "C",
            current_time=10.0,
            minimum_fidelity=0.8,
            maximum_aoi=3.0,
        )

    def evaluate(self, route):
        return evaluate_route(
            self.graph,
            route,
            current_time=10.0,
            minimum_fidelity=0.8,
            maximum_aoi=3.0,
        )

    def test_baseline_selects_reference_fidelity_route(self):
        self.assertEqual(self.baseline["route"], ["A", "B", "C"])

    def test_temporal_selects_aoi_feasible_route(self):
        self.assertEqual(self.temporal["route"], ["A", "D", "C"])

    def test_baseline_violates_aoi_constraint(self):
        result = self.evaluate(self.baseline["route"])

        self.assertFalse(result["aoi_feasible"])
        self.assertFalse(result["feasible"])

    def test_temporal_satisfies_both_constraints(self):
        result = self.evaluate(self.temporal["route"])

        self.assertTrue(result["aoi_feasible"])
        self.assertTrue(result["fidelity_feasible"])
        self.assertTrue(result["feasible"])

    def test_shared_fidelity_comparison(self):
        baseline = self.evaluate(self.baseline["route"])
        temporal = self.evaluate(self.temporal["route"])

        self.assertAlmostEqual(
            baseline["memory_adjusted_fidelity"],
            0.8504616200194306,
            places=10,
        )
        self.assertAlmostEqual(
            temporal["memory_adjusted_fidelity"],
            0.816481,
            places=5,
        )

    def test_route_freshness_tradeoff(self):
        baseline = self.evaluate(self.baseline["route"])
        temporal = self.evaluate(self.temporal["route"])

        self.assertGreater(
            baseline["memory_adjusted_fidelity"],
            temporal["memory_adjusted_fidelity"],
        )
        self.assertGreater(
            baseline["maximum_link_aoi"],
            temporal["maximum_link_aoi"],
        )


if __name__ == "__main__":
    unittest.main()
