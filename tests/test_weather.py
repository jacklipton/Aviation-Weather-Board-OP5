import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.weather_service import WeatherService
from src.light_controller import MockLightController, BoardSpec

class TestWeatherService(unittest.TestCase):
    def setUp(self):
        self.spec = BoardSpec(led_count=50)
        self.controller = MockLightController(self.spec)
        self.service = WeatherService(self.controller)

    @patch('src.weather_service.requests.get')
    @patch('src.config.CHECKWX_API_KEY', 'test_key')
    @patch('src.config.AIRPORTS', 'CYGK')
    @patch('src.config.LED_ORDER', [0])
    def test_fetch_and_update(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"icao": "CYGK", "flight_category": "VFR"}
            ]
        }
        mock_get.return_value = mock_response

        # Run update
        summary = self.service.fetch_and_update()

        # Verify results
        self.assertEqual(summary['count'], 1)
        self.assertEqual(summary['airports'][0]['icao'], "CYGK")
        self.assertEqual(summary['airports'][0]['flight_category'], "VFR")
        
        # Verify LED was set (VFR = Green = (20, 0, 0))
        # Note: MockLightController uses (0,0,0) init, so check internal state if possible or rely on no exception
        # We can check specific pixel in mock controller if we expose it, but for now just running without error is a good step.
        
if __name__ == '__main__':
    unittest.main()
