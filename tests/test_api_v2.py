import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.web_app import app
from src.light_controller import MockLightController

class TestFastAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # We can patch the controller or service if needed
        # but for integration tests, using the MockController (default in test env) is fine.

    def test_status(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("active", data)
        self.assertIn("uptime_seconds", data)

    @patch("src.weather_service.requests.get")
    @patch("src.config.CHECKWX_API_KEY", "test_key")
    def test_weather_endpoint(self, mock_get):
        # Mock CheckWX response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "icao": "CYGK", 
                    "flight_category": "VFR", 
                    "wind": {"speed_kts": 10},
                    "visibility": {"miles": "15"}
                }
            ]
        }
        mock_get.return_value = mock_response

        # Trigger update via service directly or endpoint?
        # The endpoint just returns cached data. We need to populate it first.
        # We can call the service method directly to populate cache.
        from src.web_app import service
        service.fetch_and_update()

        response = self.client.get("/api/weather")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["icao"], "CYGK")
        self.assertEqual(data[0]["wind"]["speed_kts"], 10)

    def test_control_stop_start(self):
        # Stop
        r = self.client.post("/api/control/stop")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["ok"], True)

        # Check status
        r = self.client.get("/api/status")
        self.assertEqual(r.json()["active"], False)

        # Start
        r = self.client.post("/api/control/start")
        self.assertEqual(r.status_code, 200)

        # Check status
        r = self.client.get("/api/status")
        self.assertEqual(r.json()["active"], True)

if __name__ == '__main__':
    unittest.main()
