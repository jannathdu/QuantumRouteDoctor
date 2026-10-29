import unittest
import networkx as nx

from backend.core.memory_aware_routing import find_memory_aware_route


def add_link(graph, u, v, fidelity, storage_time=0.0,
             decoherence_rate=0.0, measurement_time=0.0):
    graph.add_edge(
        u, v,
        fidelity=fidelity,
        storage_time=storage_time,
        decoherence_rate=decoherence_rate,
        measurement_time=measurement_time,
    )


class TestMemoryAwareRouting(unittest.TestCase):

    def test_selects_best_memory_adjusted_route(self):
        graph = nx.Graph()

        # High initial fidelity, but severe memory decoherence.
        add_link(graph, "S", "A", 0.99, 10.0, 0.1)
        add_link(graph, "A", "T", 0.99, 10.0, 0.1)

        # Lower initial fidelity, but negligible memory decay.
        add_link(graph, "S", "B", 0.90)
        add_link(graph, "B", "T", 0.90)

        result = find_memory_aware_route(
            graph, "S", "T", minimum_fidelity=0.5
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["route"], ["S", "B", "T"])
        self.assertEqual(result["hop_count"], 2)
        self.assertGreaterEqual(result["predicted_fidelity"], 0.5)

    def test_does_not_reject_route_for_stale_measurement(self):
        graph = nx.Graph()
        add_link(
            graph, "S", "T", 0.95,
            measurement_time=-1000.0,
        )

        result = find_memory_aware_route(
            graph, "S", "T", minimum_fidelity=0.8
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["route"], ["S", "T"])

    def test_no_route_meets_fidelity_threshold(self):
        graph = nx.Graph()
        add_link(graph, "S", "T", 0.60)

        result = find_memory_aware_route(
            graph, "S", "T", minimum_fidelity=0.90
        )

        self.assertIsNone(result)

    def test_disconnected_network(self):
        graph = nx.Graph()
        graph.add_nodes_from(["S", "T"])

        result = find_memory_aware_route(graph, "S", "T")

        self.assertIsNone(result)

    def test_invalid_source(self):
        graph = nx.Graph()
        graph.add_edge("S", "T", fidelity=0.95)

        with self.assertRaises(ValueError):
            find_memory_aware_route(graph, "X", "T")

    def test_same_source_and_target(self):
        graph = nx.Graph()
        graph.add_node("S")

        with self.assertRaises(ValueError):
            find_memory_aware_route(graph, "S", "S")

    def test_invalid_fidelity_threshold(self):
        graph = nx.Graph()
        graph.add_edge("S", "T", fidelity=0.95)

        for threshold in (0.1, 1.1, float("nan"), float("inf"), True):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    find_memory_aware_route(
                        graph, "S", "T",
                        minimum_fidelity=threshold,
                    )


if __name__ == "__main__":
    unittest.main()
