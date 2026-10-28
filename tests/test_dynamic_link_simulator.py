import math
import unittest

from backend.core.configurable_network import create_configurable_network
from backend.core.dynamic_link_simulator import simulate_dynamic_links


class TestDynamicLinkSimulator(unittest.TestCase):

    def setUp(self):
        self.graph = create_configurable_network(
            ["A", "B", "C"],
            [
                {
                    "source": "A",
                    "target": "B",
                    "fidelity": 0.95,
                    "noise": 0.05,
                    "measurement_time": 8.0,
                    "storage_time": 2.0,
                    "decoherence_rate": 0.03,
                },
                {
                    "source": "B",
                    "target": "C",
                    "fidelity": 0.90,
                    "noise": 0.10,
                },
            ],
        )

    def test_original_graph_unchanged(self):
        original = self.graph["A"]["B"].copy()

        simulate_dynamic_links(self.graph, current_time=10.0)

        self.assertEqual(self.graph["A"]["B"], original)

    def test_deterministic_output(self):
        first = simulate_dynamic_links(self.graph, current_time=10.0)
        second = simulate_dynamic_links(self.graph, current_time=10.0)

        self.assertEqual(
            first["A"]["B"]["fidelity"],
            second["A"]["B"]["fidelity"],
        )

    def test_link_failure_removes_edge(self):
        result = simulate_dynamic_links(
            self.graph,
            current_time=10.0,
            failed_links=[("B", "C")],
        )

        self.assertEqual(result.number_of_edges(), 1)
        self.assertFalse(result.has_edge("B", "C"))
        self.assertEqual(self.graph.number_of_edges(), 2)

    def test_updated_fidelity_within_bounds(self):
        result = simulate_dynamic_links(self.graph, current_time=10.0)

        for _, _, data in result.edges(data=True):
            self.assertGreaterEqual(data["fidelity"], 0.25)
            self.assertLessEqual(data["fidelity"], 1.0)
            self.assertGreaterEqual(data["noise"], 0.0)
            self.assertLessEqual(data["noise"], 1.0)

    def test_temporal_attributes_preserved(self):
        result = simulate_dynamic_links(self.graph, current_time=10.0)

        self.assertEqual(result["A"]["B"]["measurement_time"], 8.0)
        self.assertEqual(result["A"]["B"]["storage_time"], 2.0)
        self.assertEqual(result["A"]["B"]["decoherence_rate"], 0.03)

    def test_invalid_noise_amplitude_rejected(self):
        with self.assertRaises(ValueError):
            simulate_dynamic_links(
                self.graph,
                current_time=10.0,
                noise_amplitude=-0.1,
            )

    def test_nonfinite_time_rejected(self):
        with self.assertRaises(ValueError):
            simulate_dynamic_links(
                self.graph,
                current_time=math.nan,
            )

    def test_unknown_failed_link_rejected(self):
        with self.assertRaises(ValueError):
            simulate_dynamic_links(
                self.graph,
                current_time=10.0,
                failed_links=[("A", "C")],
            )


if __name__ == "__main__":
    unittest.main()
