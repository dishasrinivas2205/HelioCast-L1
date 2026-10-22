"""
Tests for FastAPI Scientific Server Routes.
"""

import unittest
from fastapi.testclient import TestClient

from heliocast.api.app import app


class TestApiServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("SOLEXS", data["instruments"])
        self.assertIn("HEL1OS", data["instruments"])

    def test_telemetry_latest(self):
        resp = self.client.get("/api/v1/telemetry/latest")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("solexs_flux", data)
        self.assertIn("helios_flux", data)
        self.assertIn("hardness_ratio", data)

    def test_telemetry_lightcurve(self):
        resp = self.client.get("/api/v1/telemetry/lightcurve?limit=60")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 60)
        self.assertGreaterEqual(len(data["data"]), 60)

    def test_master_catalog_endpoint(self):
        resp = self.client.get("/api/v1/catalog/master")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)


if __name__ == "__main__":
    unittest.main()
