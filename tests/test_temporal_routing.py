import unittest
import networkx as nx
from backend.core.temporal_routing import find_temporal_route

class TestTemporalRouting(unittest.TestCase):
    def setUp(self):
        self.g = nx.Graph()
        self.g.add_edge("A","B",fidelity=.95,measurement_time=98,storage_time=0,decoherence_rate=.01)
        self.g.add_edge("B","C",fidelity=.94,measurement_time=98,storage_time=0,decoherence_rate=.01)
        self.g.add_edge("A","D",fidelity=.99,measurement_time=80,storage_time=0,decoherence_rate=.01)
        self.g.add_edge("D","C",fidelity=.99,measurement_time=80,storage_time=0,decoherence_rate=.01)

    def test_stale_route_rejected(self):
        result = find_temporal_route(self.g,"A","C",100,.8,10)
        self.assertEqual(result["route"],["A","B","C"])
        self.assertAlmostEqual(result["predicted_fidelity"],.894)
        self.assertEqual(result["maximum_link_aoi"],2)

    def test_no_feasible_route(self):
        result = find_temporal_route(self.g,"A","C",100,.95,10)
        self.assertIsNone(result)

    def test_decoherence_aware_selection(self):
        for u, v in self.g.edges():
            self.g[u][v]["measurement_time"] = 98
            self.g[u][v]["decoherence_rate"] = 0.05
        self.g["A"]["D"]["storage_time"] = 20
        self.g["D"]["C"]["storage_time"] = 20
        result = find_temporal_route(self.g,"A","C",100,.8,10)
        self.assertIsNotNone(result)
        self.assertEqual(result["route"],["A","B","C"])
        self.assertAlmostEqual(result["predicted_fidelity"],.894)

    def test_future_measurement_timestamp(self):
        self.g["A"]["B"]["measurement_time"] = 110
        with self.assertRaises(ValueError):
            find_temporal_route(self.g,"A","C",100,.8,10)

    def test_disconnected_network(self):
        g = nx.Graph()
        g.add_edge("A","B",fidelity=.95)
        g.add_edge("C","D",fidelity=.94)
        result = find_temporal_route(g,"A","D",100,.8,10)
        self.assertIsNone(result)
