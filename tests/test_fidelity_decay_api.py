"""Regression tests for the fidelity decay research API."""

import unittest

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.models.temporal_fidelity import predict_memory_fidelity


class FidelityDecayAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_numerical_accuracy(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={
                "initial_fidelity": 0.95,
                "decoherence_rate": 0.03,
                "maximum_time": 20,
                "samples": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(
            data["model"],
            "simplified_depolarizing_memory",
        )
        self.assertEqual(len(data["points"]), 5)

        for index, point in enumerate(data["points"]):
            expected_time = index * 5.0

            self.assertAlmostEqual(
                point["storage_time"],
                expected_time,
            )

            self.assertAlmostEqual(
                point["predicted_fidelity"],
                predict_memory_fidelity(
                    0.95,
                    expected_time,
                    0.03,
                ),
            )

    def test_initial_fidelity(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={"initial_fidelity": 0.95},
        )

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(
            response.json()["points"][0]["predicted_fidelity"],
            0.95,
        )

    def test_fidelity_nonincreasing(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={"initial_fidelity": 0.95},
        )

        values = [
            point["predicted_fidelity"]
            for point in response.json()["points"]
        ]

        self.assertTrue(
            all(a >= b for a, b in zip(values, values[1:]))
        )

    def test_invalid_initial_fidelity(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={"initial_fidelity": 1.5},
        )
        self.assertEqual(response.status_code, 422)

    def test_negative_decoherence_rate(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={"decoherence_rate": -0.1},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_sample_count(self):
        response = self.client.get(
            "/api/research/fidelity-decay",
            params={"samples": 1},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
