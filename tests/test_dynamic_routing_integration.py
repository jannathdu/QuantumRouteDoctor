import unittest

from backend.core.configurable_network import create_configurable_network
from backend.core.dynamic_link_simulator import simulate_dynamic_links
from backend.core.fidelity_routing import find_fidelity_constrained_route
from backend.core.temporal_routing import find_temporal_route


class TestDynamicRoutingIntegration(unittest.TestCase):

    def setUp(self):
        self.graph = create_configurable_network(
            ["A", "B", "C", "D"],
            [
                {
                    "source": "A", "target": "B",
                    "fidelity": 0.98, "noise": 0.01,
                    "measurement_time": 9.0,
                    "storage_time": 1.0,
                    "decoherence_rate": 0.01,
                },
                {
                    "source": "B", "target": "C",
                    "fidelity": 0.98, "noise": 0.01,
                    "measurement_time": 9.0,
                    "storage_time": 1.0,
                    "decoherence_rate": 0.01,
                },
                {
                    "source": "A", "target": "D",
                    "fidelity": 0.95, "noise": 0.01,
                    "measurement_time": 8.0,
                    "storage_time": 1.0,
                    "decoherence_rate": 0.01,
                },
                {
                    "source": "D", "target": "C",
                    "fidelity": 0.95, "noise": 0.01,
                    "measurement_time": 8.0,
                    "storage_time": 1.0,
                    "decoherence_rate": 0.01,
                },
            ],
        )

    def test_baseline_normal_route(self):
        graph = simulate_dynamic_links(
            self.graph, current_time=10.0, noise_amplitude=0.0
        )
        result = find_fidelity_constrained_route(
            graph, "A", "C", minimum_fidelity=0.8
        )
        self.assertEqual(result["route"], ["A", "B", "C"])

    def test_baseline_reroutes_after_failure(self):
        graph = simulate_dynamic_links(
            self.graph,
            current_time=10.0,
            noise_amplitude=0.0,
            failed_links=[("B", "C")],
        )
        result = find_fidelity_constrained_route(
            graph, "A", "C", minimum_fidelity=0.8
        )
        self.assertEqual(result["route"], ["A", "D", "C"])

    def test_temporal_normal_route(self):
        graph = simulate_dynamic_links(
            self.graph, current_time=10.0, noise_amplitude=0.0
        )
        result = find_temporal_route(
            graph, "A", "C",
            current_time=10.0,
            minimum_fidelity=0.8,
            maximum_aoi=5.0,
        )
        self.assertEqual(result["route"], ["A", "B", "C"])

    def test_temporal_reroutes_after_failure(self):
        graph = simulate_dynamic_links(
            self.graph,
            current_time=10.0,
            noise_amplitude=0.0,
            failed_links=[("B", "C")],
        )
        result = find_temporal_route(
            graph, "A", "C",
            current_time=10.0,
            minimum_fidelity=0.8,
            maximum_aoi=5.0,
        )
        self.assertEqual(result["route"], ["A", "D", "C"])
        self.assertGreaterEqual(result["predicted_fidelity"], 0.8)

    def test_original_network_preserved(self):
        simulate_dynamic_links(
            self.graph,
            current_time=10.0,
            failed_links=[("B", "C")],
        )
        self.assertTrue(self.graph.has_edge("B", "C"))
        self.assertEqual(self.graph["B"]["C"]["fidelity"], 0.98)

    def test_disconnected_network_is_infeasible(self):
        graph = simulate_dynamic_links(
            self.graph,
            current_time=10.0,
            noise_amplitude=0.0,
            failed_links=[("B", "C"), ("D", "C")],
        )
        baseline = find_fidelity_constrained_route(
            graph, "A", "C", minimum_fidelity=0.8
        )
        temporal = find_temporal_route(
            graph, "A", "C",
            current_time=10.0,
            minimum_fidelity=0.8,
            maximum_aoi=5.0,
        )
        self.assertIsNone(baseline)
        self.assertIsNone(temporal)


if __name__ == "__main__":
    unittest.main()
