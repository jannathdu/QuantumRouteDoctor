import unittest

import networkx as nx

from backend.core.configurable_network import create_configurable_network


class TestConfigurableNetwork(unittest.TestCase):

    def setUp(self):
        self.nodes = ["A", "B", "C"]
        self.links = [
            {"source": "A", "target": "B", "fidelity": 0.95, "noise": 0.05},
            {"source": "B", "target": "C", "fidelity": 0.90, "noise": 0.10},
        ]

    def test_valid_network(self):
        graph = create_configurable_network(self.nodes, self.links)

        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertEqual(graph.number_of_edges(), 2)
        self.assertTrue(nx.is_connected(graph))
        self.assertEqual(graph["A"]["B"]["fidelity"], 0.95)

    def test_duplicate_nodes_rejected(self):
        with self.assertRaises(ValueError):
            create_configurable_network(["A", "A"], self.links)

    def test_unknown_node_rejected(self):
        links = [
            {"source": "A", "target": "Z", "fidelity": 0.9, "noise": 0.1}
        ]

        with self.assertRaises(ValueError):
            create_configurable_network(self.nodes, links)

    def test_duplicate_undirected_link_rejected(self):
        links = [
            {"source": "A", "target": "B", "fidelity": 0.9, "noise": 0.1},
            {"source": "B", "target": "A", "fidelity": 0.9, "noise": 0.1},
        ]

        with self.assertRaises(ValueError):
            create_configurable_network(self.nodes, links)

    def test_invalid_fidelity_rejected(self):
        for fidelity in [-0.1, 1.1, float("nan"), True]:
            with self.subTest(fidelity=fidelity):
                links = [
                    {
                        "source": "A",
                        "target": "B",
                        "fidelity": fidelity,
                        "noise": 0.1,
                    }
                ]

                with self.assertRaises(ValueError):
                    create_configurable_network(self.nodes, links)

    def test_invalid_noise_rejected(self):
        links = [
            {"source": "A", "target": "B", "fidelity": 0.9, "noise": -0.1}
        ]

        with self.assertRaises(ValueError):
            create_configurable_network(self.nodes, links)

    def test_temporal_attributes_preserved(self):
        links = [
            {
                "source": "A",
                "target": "B",
                "fidelity": 0.95,
                "noise": 0.05,
                "measurement_time": 8.0,
                "storage_time": 2.0,
                "decoherence_rate": 0.03,
            }
        ]

        graph = create_configurable_network(self.nodes, links)

        self.assertEqual(graph["A"]["B"]["measurement_time"], 8.0)
        self.assertEqual(graph["A"]["B"]["storage_time"], 2.0)
        self.assertEqual(graph["A"]["B"]["decoherence_rate"], 0.03)

    def test_negative_storage_time_rejected(self):
        links = [
            {
                "source": "A",
                "target": "B",
                "fidelity": 0.95,
                "noise": 0.05,
                "storage_time": -1.0,
            }
        ]

        with self.assertRaises(ValueError):
            create_configurable_network(self.nodes, links)


if __name__ == "__main__":
    unittest.main()
