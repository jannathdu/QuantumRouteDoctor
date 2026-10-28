import unittest

from fastapi.testclient import TestClient

from backend.api.main import app


class TestConfigurableNetworkAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.endpoint = "/api/network/configurable"

    def test_valid_network(self):
        payload = {
            "nodes": ["A", "B", "C"],
            "links": [
                {"source": "A", "target": "B", "fidelity": 0.95, "noise": 0.05},
                {"source": "B", "target": "C", "fidelity": 0.90, "noise": 0.10},
            ],
        }

        response = self.client.post(self.endpoint, json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["node_count"], 3)
        self.assertEqual(data["link_count"], 2)
        self.assertEqual(data["data_source"], "user_configured")

    def test_unknown_node_rejected(self):
        payload = {
            "nodes": ["A", "B"],
            "links": [
                {"source": "A", "target": "Z", "fidelity": 0.95, "noise": 0.05}
            ],
        }

        response = self.client.post(self.endpoint, json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_fidelity_rejected(self):
        payload = {
            "nodes": ["A", "B"],
            "links": [
                {"source": "A", "target": "B", "fidelity": 1.5, "noise": 0.05}
            ],
        }

        response = self.client.post(self.endpoint, json=payload)
        self.assertEqual(response.status_code, 422)

    def test_duplicate_link_rejected(self):
        payload = {
            "nodes": ["A", "B"],
            "links": [
                {"source": "A", "target": "B", "fidelity": 0.95, "noise": 0.05},
                {"source": "B", "target": "A", "fidelity": 0.90, "noise": 0.10},
            ],
        }

        response = self.client.post(self.endpoint, json=payload)
        self.assertEqual(response.status_code, 422)

    def test_temporal_attributes_preserved(self):
        payload = {
            "nodes": ["A", "B"],
            "links": [
                {
                    "source": "A",
                    "target": "B",
                    "fidelity": 0.95,
                    "noise": 0.05,
                    "measurement_time": 8.0,
                    "storage_time": 2.0,
                    "decoherence_rate": 0.03,
                }
            ],
        }

        response = self.client.post(self.endpoint, json=payload)

        self.assertEqual(response.status_code, 200)
        link = response.json()["links"][0]
        self.assertEqual(link["measurement_time"], 8.0)
        self.assertEqual(link["storage_time"], 2.0)
        self.assertEqual(link["decoherence_rate"], 0.03)

    def test_missing_required_field_rejected(self):
        payload = {
            "nodes": ["A", "B"],
            "links": [
                {"source": "A", "target": "B", "fidelity": 0.95}
            ],
        }

        response = self.client.post(self.endpoint, json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
