"""Regression tests for the AoI threshold sweep API."""

import unittest

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.temporal_network import create_temporal_demo_network
from backend.core.temporal_routing import find_temporal_route


class AoISweepAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_default_sweep(self):
        response = self.client.get("/api/research/aoi-sweep")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["points"]), 11)
        self.assertEqual(data["data_source"], "synthetic_demo")

    def test_threshold_transitions(self):
        response = self.client.get("/api/research/aoi-sweep")
        points = response.json()["points"]

        for threshold in range(3):
            self.assertFalse(points[threshold]["feasible"])
            self.assertIsNone(
                points[threshold]["predicted_fidelity"]
            )

        for threshold in (3, 4):
            self.assertTrue(points[threshold]["feasible"])
            self.assertEqual(
                points[threshold]["selected_route"],
                ["A", "D", "C"],
            )

        for threshold in range(5, 11):
            self.assertTrue(points[threshold]["feasible"])
            self.assertEqual(
                points[threshold]["selected_route"],
                ["A", "B", "C"],
            )

    def test_matches_existing_router(self):
        response = self.client.get("/api/research/aoi-sweep")
        self.assertEqual(response.status_code, 200)

        graph = create_temporal_demo_network(10.0)

        for point in response.json()["points"]:
            expected = find_temporal_route(
                graph,
                "A",
                "C",
                current_time=10.0,
                minimum_fidelity=0.8,
                maximum_aoi=float(point["maximum_aoi"]),
            )

            self.assertEqual(
                point["feasible"],
                expected is not None,
            )

            self.assertEqual(
                point["selected_route"],
                expected["route"] if expected else None,
            )

            if expected:
                self.assertAlmostEqual(
                    point["predicted_fidelity"],
                    expected["predicted_fidelity"],
                )

    def test_invalid_maximum_aoi(self):
        response = self.client.get(
            "/api/research/aoi-sweep",
            params={"maximum_aoi": -1},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_minimum_fidelity(self):
        response = self.client.get(
            "/api/research/aoi-sweep",
            params={"minimum_fidelity": 1.5},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_source(self):
        response = self.client.get(
            "/api/research/aoi-sweep",
            params={"source": "X"},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
