"""Regression tests for undirected edge normalization."""

import unittest

import networkx as nx

from backend.core.research_scenarios import generate_research_scenario


class TestResearchScenarioEdgeNormalization(unittest.TestCase):

    def test_twelve_node_scenarios(self):
        for seed in range(300, 350):
            with self.subTest(seed=seed):
                graph = generate_research_scenario(
                    node_count=12,
                    link_count=18,
                    seed=seed,
                    current_time=10.0,
                )

                self.assertEqual(graph.number_of_nodes(), 12)
                self.assertEqual(graph.number_of_edges(), 18)
                self.assertTrue(nx.is_connected(graph))

    def test_reproducibility(self):
        first = generate_research_scenario(12, 18, 300, 10.0)
        second = generate_research_scenario(12, 18, 300, 10.0)

        self.assertEqual(
            nx.node_link_data(first),
            nx.node_link_data(second),
        )

    def test_larger_node_identifiers(self):
        graph = generate_research_scenario(
            node_count=15,
            link_count=24,
            seed=42,
            current_time=10.0,
        )

        self.assertEqual(graph.number_of_nodes(), 15)
        self.assertEqual(graph.number_of_edges(), 24)
        self.assertTrue(nx.is_connected(graph))

    def test_multiple_network_sizes(self):
        for nodes, links in [(8, 12), (10, 15), (12, 18)]:
            with self.subTest(nodes=nodes):
                graph = generate_research_scenario(
                    node_count=nodes,
                    link_count=links,
                    seed=300,
                    current_time=10.0,
                )

                self.assertEqual(graph.number_of_edges(), links)
                self.assertTrue(nx.is_connected(graph))


if __name__ == "__main__":
    unittest.main()
