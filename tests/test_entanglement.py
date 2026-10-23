import unittest
from backend.models.entanglement import werner_swap_fidelity, multi_hop_fidelity

class TestEntanglement(unittest.TestCase):
    def test_two_link(self):
        self.assertAlmostEqual(werner_swap_fidelity(.95,.94),.894)
    def test_three_link(self):
        self.assertAlmostEqual(multi_hop_fidelity([.95,.94,.93]),.8338933333333333)
    def test_perfect_links(self):
        self.assertEqual(multi_hop_fidelity([1,1,1]),1)
    def test_empty_route(self):
        with self.assertRaises(ValueError): multi_hop_fidelity([])
    def test_invalid_fidelity(self):
        with self.assertRaises(ValueError): werner_swap_fidelity(.2,.9)
    def test_single_link(self):
        self.assertAlmostEqual(multi_hop_fidelity([.95]),.95)
