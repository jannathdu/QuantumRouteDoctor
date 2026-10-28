import unittest

import networkx as nx

from backend.core.research_scenarios import generate_research_scenario


class TestResearchScenarios(unittest.TestCase):

    def scenario(self, nodes=10, links=15, seed=42, time=10.0):
        return generate_research_scenario(
            node_count=nodes,
            link_count=links,
            seed=seed,
            current_time=time,
        )

    @staticmethod
    def signature(graph):
        return sorted(
            (
                tuple(sorted((u, v))),
                tuple(sorted(data.items())),
            )
            for u, v, data in graph.edges(data=True)
        )

    def test_node_and_link_counts(self):
        graph = self.scenario()
        self.assertEqual(graph.number_of_nodes(), 10)
        self.assertEqual(graph.number_of_edges(), 15)

    def test_network_connected(self):
        graph = self.scenario()
        self.assertTrue(nx.is_connected(graph))

    def test_same_seed_reproducible(self):
        first = self.scenario(seed=42)
        second = self.scenario(seed=42)
        self.assertEqual(self.signature(first), self.signature(second))

    def test_different_seed_changes_scenario(self):
        first = self.scenario(seed=42)
        second = self.scenario(seed=99)
        self.assertNotEqual(self.signature(first), self.signature(second))

    def test_minimum_connected_topology(self):
        graph = self.scenario(nodes=6, links=5)
        self.assertEqual(graph.number_of_edges(), 5)
        self.assertTrue(nx.is_tree(graph))

    def test_complete_topology(self):
        graph = self.scenario(nodes=5, links=10)
        self.assertEqual(graph.number_of_edges(), 10)
        self.assertEqual(nx.density(graph), 1.0)

    def test_temporal_attributes(self):
        graph = self.scenario()

        required = {
            "fidelity",
            "noise",
            "measurement_time",
            "storage_time",
            "decoherence_rate",
        }

        for _, _, data in graph.edges(data=True):
            self.assertTrue(required.issubset(data))
            self.assertGreaterEqual(data["fidelity"], 0.85)
            self.assertLessEqual(data["fidelity"], 0.99)
            self.assertLessEqual(data["measurement_time"], 10.0)
            self.assertGreaterEqual(data["storage_time"], 0.0)

    def test_invalid_node_count_rejected(self):
        with self.assertRaises(ValueError):
            self.scenario(nodes=1, links=0)

    def test_invalid_link_count_rejected(self):
        with self.assertRaises(ValueError):
            self.scenario(nodes=5, links=2)

    def test_invalid_seed_rejected(self):
        with self.assertRaises(ValueError):
            self.scenario(seed="invalid")

    def test_invalid_time_rejected(self):
        with self.assertRaises(ValueError):
            self.scenario(time=-1.0)

    def test_metadata_preserved(self):
        graph = self.scenario(seed=42)
        self.assertEqual(graph.graph["seed"], 42)
        self.assertEqual(
            graph.graph["scenario_type"],
            "synthetic_random_connected",
        )


if __name__ == "__main__":
    unittest.main()
