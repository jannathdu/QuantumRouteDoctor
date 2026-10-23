import unittest

from backend.core.network import create_quantum_network
from backend.core.diagnostics import (
    scan_faulty_links,
    create_link_diagnosis,
)
from backend.core.routing import (
    calculate_route_metrics,
    find_safe_route,
    compare_all_routes,
    add_route_safety_status,
)


class TestQuantumRouting(unittest.TestCase):

    def setUp(self):
        self.network = create_quantum_network(
            0.95, 0.05,
            0.94, 0.06,
            0.70, 0.30,
            0.92, 0.08,
        )

    def test_network_creation(self):
        self.assertEqual(self.network.number_of_nodes(), 4)
        self.assertEqual(self.network.number_of_edges(), 4)

    def test_fault_detection(self):
        faulty = scan_faulty_links(self.network, 0.88, 0.25)
        self.assertEqual(
            {frozenset(edge) for edge in faulty},
            {frozenset(("A", "D"))},
        )

    def test_link_diagnosis(self):
        results = create_link_diagnosis(
            self.network, 0.88, 0.25
        )
        self.assertEqual(len(results), 4)
        self.assertEqual(
            sum(r["Status"] == "FAULTY" for r in results), 1
        )

    def test_safe_route(self):
        faulty = scan_faulty_links(
            self.network, 0.88, 0.25
        )
        route = find_safe_route(
            self.network, "A", "C", faulty
        )
        self.assertEqual(route, ["A", "B", "C"])

    def test_route_comparison(self):
        routes = compare_all_routes(
            self.network, "A", "C"
        )
        self.assertEqual(len(routes), 2)

    def test_route_safety(self):
        faulty = scan_faulty_links(
            self.network, 0.88, 0.25
        )
        routes = compare_all_routes(
            self.network, "A", "C"
        )
        results = add_route_safety_status(routes, faulty)

        statuses = [r["Safety Status"] for r in results]
        self.assertEqual(statuses.count("SAFE"), 1)
        self.assertEqual(statuses.count("UNSAFE"), 1)

    def test_disconnected_network(self):
        faulty = list(self.network.edges())
        result = find_safe_route(
            self.network, "A", "C", faulty
        )
        self.assertIsNone(result)

    def test_temporal_health(self):
        fresh = self.network.copy()
        stale = self.network.copy()

        for u, v in fresh.edges():
            fresh[u][v]["age"] = 1.0

        for u, v in stale.edges():
            stale[u][v]["age"] = 15.0

        fresh_metrics = calculate_route_metrics(
            fresh, ["A", "B", "C"]
        )
        stale_metrics = calculate_route_metrics(
            stale, ["A", "B", "C"]
        )

        self.assertAlmostEqual(
            fresh_metrics[0], stale_metrics[0]
        )
        self.assertGreater(
            fresh_metrics[2], stale_metrics[2]
        )


if __name__ == "__main__":
    unittest.main()
