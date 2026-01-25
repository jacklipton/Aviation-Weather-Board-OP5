import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.web_server import app, controller

class TestWebServer(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Reset controller state
        controller.clear()

    def test_index_no_auth(self):
        """Test the main page loads without auth (when auth not configured)."""
        with patch('src.config.AUTH_USERNAME', None):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Weather Board Control', response.data)

    def test_index_with_auth_fail(self):
        """Test 401 if auth is configured but missing."""
        with patch('src.config.AUTH_USERNAME', 'admin'), \
             patch('src.config.AUTH_PASSWORD', 'secret'):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 401)

    def test_start_stop(self):
        """Test start and stop endpoints."""
        with patch('src.config.AUTH_USERNAME', None):
            # Stop
            rv = self.client.post('/stop')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertFalse(data['active'])

            # Start
            rv = self.client.post('/start')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertTrue(data['active'])

    @patch('src.web_server.service.fetch_and_update')
    def test_refresh_success(self, mock_fetch):
        """Test refresh endpoint."""
        mock_fetch.return_value = {"ok": True, "count": 5}
        with patch('src.config.AUTH_USERNAME', None):
            rv = self.client.post('/refresh')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)
            self.assertTrue(data['ok'])
            self.assertEqual(data['count'], 5)

if __name__ == '__main__':
    unittest.main()

