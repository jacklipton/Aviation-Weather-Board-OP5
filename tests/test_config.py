import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to reload config to test environment variable parsing
import importlib
from src import config

class TestConfig(unittest.TestCase):
    def test_defaults(self):
        # Assuming defaults in .env.example or hardcoded
        self.assertEqual(config.WS2812_SPI_BUS, 0)
        self.assertEqual(config.WS2812_SPI_DEVICE, 0)

    @patch.dict(os.environ, {"AIRPORTS": "CYGK,CYHM,CYYZ", "LED_ORDER": "0,5,10"}, clear=True)
    def test_csv_parsing(self):
        # Reload config module to pick up env vars
        importlib.reload(config)
        self.assertEqual(config.AIRPORTS, "CYGK,CYHM,CYYZ")
        self.assertEqual(config.LED_ORDER, [0, 5, 10])

    @patch.dict(os.environ, {"LED_ORDER": "bad,data"}, clear=True)
    def test_bad_led_order(self):
        with self.assertRaises(ValueError):
            importlib.reload(config)

if __name__ == '__main__':
    unittest.main()
