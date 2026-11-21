import unittest

import app as systempulse


class SystemPulseApiTests(unittest.TestCase):
    def setUp(self):
        self.client = systempulse.app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "online")
        self.assertIn("hostname", payload)

    def test_system_endpoint_shape(self):
        response = self.client.get("/api/system")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        for key in (
            "cpu_percent", "memory_percent", "memory_used", "memory_total",
            "disk_percent", "disk_used", "disk_total", "uptime_seconds",
            "hostname", "os", "cpu_cores", "updated_at",
        ):
            self.assertIn(key, payload)

    def test_processes_endpoint_shape(self):
        response = self.client.get("/api/processes")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_performance_endpoint_shape(self):
        response = self.client.get("/api/performance")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("cpu_percent", payload)
        self.assertIn("memory_percent", payload)

    def test_allowed_origin_private_network_preflight(self):
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "https://systempulse-mocha.vercel.app",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Private-Network": "true",
            },
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "https://systempulse-mocha.vercel.app",
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Private-Network"), "true"
        )
        self.assertIn("GET", response.headers.get("Access-Control-Allow-Methods", ""))

    def test_untrusted_origin_gets_no_cors_permission(self):
        response = self.client.get(
            "/api/health", headers={"Origin": "https://example.com"}
        )
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)


if __name__ == "__main__":
    unittest.main()
