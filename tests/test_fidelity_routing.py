import unittest
import networkx as nx
from backend.core.network import create_quantum_network
from backend.core.fidelity_routing import find_fidelity_constrained_route as route

class TestFidelityRouting(unittest.TestCase):
    def setUp(self):
        self.g = create_quantum_network(.95,.05,.94,.06,.70,.30,.92,.08)

    def test_best_route(self):
        result = route(self.g,"A","C",.8)
        self.assertEqual(result["route"],["A","B","C"])
        self.assertAlmostEqual(result["end_to_end_fidelity"],.894)

    def test_no_feasible_route(self):
        self.assertIsNone(route(self.g,"A","C",.95))

    def test_invalid_low_threshold(self):
        with self.assertRaises(ValueError): route(self.g,"A","C",.1)

    def test_invalid_high_threshold(self):
        with self.assertRaises(ValueError): route(self.g,"A","C",1.1)

    def test_invalid_source(self):
        with self.assertRaises(ValueError): route(self.g,"X","C",.8)

    def test_same_source_target(self):
        with self.assertRaises(ValueError): route(self.g,"A","A",.8)

    def test_disconnected_network(self):
        g = nx.Graph()
        g.add_edge("A","B",fidelity=.95)
        g.add_edge("C","D",fidelity=.94)
        self.assertIsNone(route(g,"A","D",.8))

    def test_equal_fidelity_tie_break(self):
        g = nx.Graph()
        g.add_edge("A","D",fidelity=1.0)
        g.add_edge("D","E",fidelity=1.0)
        g.add_edge("E","C",fidelity=1.0)
        g.add_edge("A","B",fidelity=1.0)
        g.add_edge("B","C",fidelity=1.0)
        self.assertEqual(route(g,"A","C",.8)["route"],["A","B","C"])
