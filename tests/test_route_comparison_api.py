"""Tests for baseline-versus-temporal routing comparison."""

import unittest

from fastapi.testclient import TestClient
from backend.api.main import app


class RouteComparisonAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_both_routes_feasible(self):
        response = self.client.get(
            "/api/routes/compare",
            params={"maximum_aoi": 10},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["baseline"]["feasible"])
        self.assertTrue(data["temporal"]["feasible"])
        self.assertEqual(
            data["baseline"]["selected_route"], ["A", "B", "C"]
        )
        self.assertEqual(
            data["temporal"]["selected_route"], ["A", "B", "C"]
        )
        self.assertAlmostEqual(
            data["baseline"]["end_to_end_fidelity"], 0.894
        )
        self.assertAlmostEqual(
            data["temporal"]["predicted_fidelity"],
            0.8504616200194306,
        )

    def test_strict_aoi_rejects_temporal_route(self):
        response = self.client.get(
            "/api/routes/compare",
            params={"maximum_aoi": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["baseline"]["feasible"])
        self.assertFalse(data["temporal"]["feasible"])
        self.assertIsNone(data["temporal"]["selected_route"])
        self.assertIsNone(data["temporal"]["predicted_fidelity"])

    def test_invalid_source(self):
        response = self.client.get(
            "/api/routes/compare",
            params={"source": "X"},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_maximum_aoi(self):
        response = self.client.get(
            "/api/routes/compare",
            params={"maximum_aoi": -1},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
