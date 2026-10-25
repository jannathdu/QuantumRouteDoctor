import unittest

from fastapi.testclient import TestClient
from backend.api.main import app


class RoutingAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_valid_route(self):
        response = self.client.get("/api/routes", params={
            "source": "A",
            "destination": "C",
            "minimum_fidelity": 0.8,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["feasible"])
        self.assertEqual(data["selected_route"], ["A", "B", "C"])
        self.assertAlmostEqual(data["end_to_end_fidelity"], 0.894)
        self.assertEqual(data["hop_count"], 2)

    def test_no_feasible_route(self):
        response = self.client.get(
            "/api/routes", params={"minimum_fidelity": 0.99}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["feasible"])
        self.assertIsNone(data["selected_route"])
        self.assertIsNone(data["end_to_end_fidelity"])

    def test_invalid_node(self):
        response = self.client.get(
            "/api/routes", params={"source": "X", "destination": "C"}
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_fidelity(self):
        response = self.client.get(
            "/api/routes", params={"minimum_fidelity": 1.5}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
