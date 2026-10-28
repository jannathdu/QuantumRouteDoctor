import math
import unittest

from backend.core.temporal_network import create_temporal_demo_network
from backend.core.network_evolution import evolve_network_state
from backend.models.temporal_fidelity import predict_memory_fidelity


class TestNetworkEvolution(unittest.TestCase):

    def setUp(self):
        self.graph = create_temporal_demo_network(current_time=10.0)

    def test_aoi_increases_without_refresh(self):
        updated = evolve_network_state(self.graph, 10.0, 15.0)

        self.assertEqual(updated["A"]["B"]["aoi"], 7.0)
        self.assertEqual(updated["A"]["D"]["aoi"], 6.0)

    def test_refresh_resets_aoi(self):
        updated = evolve_network_state(
            self.graph,
            10.0,
            15.0,
            refreshed_links=[("A", "B")],
        )

        self.assertEqual(updated["A"]["B"]["aoi"], 0.0)
        self.assertEqual(updated["A"]["D"]["aoi"], 6.0)
        self.assertEqual(updated["A"]["B"]["measurement_time"], 15.0)

    def test_storage_time_increases(self):
        updated = evolve_network_state(self.graph, 10.0, 15.0)

        self.assertEqual(updated["A"]["B"]["storage_time"], 6.0)
        self.assertEqual(updated["B"]["C"]["storage_time"], 7.0)

    def test_refresh_does_not_reset_storage_time(self):
        updated = evolve_network_state(
            self.graph,
            10.0,
            15.0,
            refreshed_links=[("A", "B")],
        )

        self.assertEqual(updated["A"]["B"]["storage_time"], 6.0)

    def test_predicted_memory_fidelity(self):
        updated = evolve_network_state(self.graph, 10.0, 15.0)

        expected = predict_memory_fidelity(0.95, 6.0, 0.01)

        self.assertAlmostEqual(
            updated["A"]["B"]["predicted_memory_fidelity"],
            expected,
            places=12,
        )

    def test_consecutive_steps(self):
        first = evolve_network_state(
            self.graph,
            10.0,
            15.0,
            refreshed_links=[("A", "B")],
        )

        second = evolve_network_state(first, 15.0, 20.0)

        self.assertEqual(second["A"]["B"]["aoi"], 5.0)
        self.assertEqual(second["A"]["D"]["aoi"], 11.0)
        self.assertEqual(second["A"]["B"]["storage_time"], 11.0)

        self.assertLess(
            second["A"]["B"]["predicted_memory_fidelity"],
            first["A"]["B"]["predicted_memory_fidelity"],
        )

    def test_original_network_unchanged(self):
        original = self.graph["A"]["B"].copy()

        evolve_network_state(
            self.graph,
            10.0,
            15.0,
            refreshed_links=[("A", "B")],
        )

        self.assertEqual(self.graph["A"]["B"], original)

    def test_backward_time_rejected(self):
        with self.assertRaises(ValueError):
            evolve_network_state(self.graph, 10.0, 9.0)

    def test_nonfinite_time_rejected(self):
        with self.assertRaises(ValueError):
            evolve_network_state(self.graph, 10.0, math.nan)

    def test_unknown_refresh_link_rejected(self):
        with self.assertRaises(ValueError):
            evolve_network_state(
                self.graph,
                10.0,
                15.0,
                refreshed_links=[("A", "C")],
            )


if __name__ == "__main__":
    unittest.main()
