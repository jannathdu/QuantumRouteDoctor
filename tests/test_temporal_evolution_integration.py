import unittest

from backend.core.temporal_network import create_temporal_demo_network
from backend.core.network_evolution import evolve_network_state
from backend.core.temporal_routing import find_temporal_route


class TestTemporalEvolutionIntegration(unittest.TestCase):

    def setUp(self):
        self.original = create_temporal_demo_network(
            current_time=10.0
        )

        self.stale = evolve_network_state(
            self.original,
            current_time=10.0,
            next_time=15.0,
        )

        self.refreshed = evolve_network_state(
            self.original,
            current_time=10.0,
            next_time=15.0,
            refreshed_links=[("A", "B"), ("B", "C")],
        )

    def find_route(self, graph, current_time, threshold):
        return find_temporal_route(
            graph,
            "A",
            "C",
            current_time=current_time,
            minimum_fidelity=threshold,
            maximum_aoi=5.0,
        )

    def test_initial_route_feasible(self):
        result = self.find_route(
            self.original, 10.0, 0.8
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["route"], ["A", "B", "C"])

    def test_stale_information_blocks_route(self):
        result = self.find_route(
            self.stale, 15.0, 0.70
        )

        self.assertIsNone(result)

    def test_refresh_resets_controller_aoi(self):
        self.assertEqual(
            self.refreshed["A"]["B"]["aoi"], 0.0
        )
        self.assertEqual(
            self.refreshed["B"]["C"]["aoi"], 0.0
        )

    def test_refresh_does_not_restore_memory_fidelity(self):
        result = self.find_route(
            self.refreshed, 15.0, 0.80
        )

        self.assertIsNone(result)

    def test_refreshed_route_feasible_at_lower_threshold(self):
        result = self.find_route(
            self.refreshed, 15.0, 0.70
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["route"], ["A", "B", "C"])
        self.assertAlmostEqual(
            result["predicted_fidelity"],
            0.741616,
            places=5,
        )

    def test_refresh_preserves_storage_time(self):
        self.assertEqual(
            self.refreshed["A"]["B"]["storage_time"], 6.0
        )
        self.assertEqual(
            self.refreshed["B"]["C"]["storage_time"], 7.0
        )


if __name__ == "__main__":
    unittest.main()
