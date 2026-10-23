import unittest
from backend.models.temporal_fidelity import predict_memory_fidelity as f, calculate_aoi as a

class TestTemporalFidelity(unittest.TestCase):
    def test_initial_fidelity(self):
        self.assertAlmostEqual(f(0.95, 0, 0.1), 0.95)
    def test_fidelity_decay(self):
        self.assertAlmostEqual(f(0.95, 5, 0.1), 0.6745714618)
    def test_aoi(self):
        self.assertEqual(a(20, 15), 5)
    def test_negative_storage(self):
        with self.assertRaises(ValueError): f(0.95, -1, 0.1)
    def test_negative_rate(self):
        with self.assertRaises(ValueError): f(0.95, 5, -0.1)
    def test_invalid_fidelity(self):
        with self.assertRaises(ValueError): f(1.2, 5, 0.1)
    def test_future_timestamp(self):
        with self.assertRaises(ValueError): a(10, 15)
