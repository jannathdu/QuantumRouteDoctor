"""Regression tests for the temporal routing API."""

import unittest

from fastapi.testclient import TestClient

from backend.api.main import app


class TemporalRoutingAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_feasible_temporal_route(self):
        response = self.client.get(
            "/api/routes/temporal",
            params={"current_time": 10, "maximum_aoi": 10},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["feasible"])
        self.assertEqual(data["algorithm"], "temporal_state_aware")
        self.assertEqual(data["selected_route"], ["A", "B", "C"])
        self.assertAlmostEqual(data["predicted_fidelity"], 0.8504616200194306)
        self.assertEqual(data["maximum_link_aoi"], 5.0)
        self.assertEqual(data["hop_count"], 2)

    def test_stale_links_rejected(self):
        response = self.client.get(
            "/api/routes/temporal",
            params={"current_time": 10, "maximum_aoi": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["feasible"])
        self.assertIsNone(data["selected_route"])
        self.assertIsNone(data["predicted_fidelity"])

    def test_invalid_source(self):
        response = self.client.get(
            "/api/routes/temporal",
            params={"source": "X"},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_maximum_aoi(self):
        response = self.client.get(
            "/api/routes/temporal",
            params={"maximum_aoi": -1},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
