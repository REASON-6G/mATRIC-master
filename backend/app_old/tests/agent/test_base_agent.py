import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from agent.base_agent import BaseAgent
from settings import settings
import time

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.agent = BaseAgent()
        self.agent.token_url = 'http://mocktokenurl.com/token'
        self.agent.update_url = 'http://mockupdateurl.com/update'
        self.agent.ap_id = 'test_ap_id'
        self.agent.agent_password = 'test_password'
        self.agent.update_interval = 1  # Set to 1 second for faster tests

    @patch('requests.post')
    def test_authenticate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "mock_token",
            "expires_in": 3600
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.agent.authenticate()

        self.assertEqual(self.agent.token, 'mock_token')
        self.assertIsNotNone(self.agent.token_expiry)
        print(f"Token expiry set to: {self.agent.token_expiry}")

    @patch('requests.post')
    def test_refresh_token_if_needed(self, mock_post):
        # Initially authenticate
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "mock_token",
            "expires_in": 2  # 2 seconds for quick refresh
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.agent.authenticate()

        # Simulate time passing to force token refresh
        self.agent.token_expiry = datetime.utcnow() + timedelta(seconds=1)
        time.sleep(2)  # Sleep to ensure the token needs refreshing

        self.agent.refresh_token_if_needed()

        self.assertEqual(self.agent.token, 'mock_token')
        self.assertIsNotNone(self.agent.token_expiry)
        print(f"Token refreshed and expiry set to: {self.agent.token_expiry}")

    @patch('requests.post')
    def test_send_data_success(self, mock_post):
        # Mock authenticate
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {
            "access_token": "mock_token",
            "expires_in": 3600
        }
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.side_effect = [mock_auth_response, MagicMock(status_code=200)]

        self.agent.authenticate()

        data = {"test": "data"}
        self.agent.send_data(data)

        self.assertEqual(mock_post.call_count, 2)  # Called for auth and send_data
        print("Data sent successfully.")

    @patch('requests.post')
    def test_run(self, mock_post):
        # Mock authenticate
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {
            "access_token": "mock_token",
            "expires_in": 3600
        }
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response

        # Mock send_data to avoid actual network calls
        self.agent.send_data = MagicMock()

        # Mock collect_data to return dummy data
        self.agent.collect_data = MagicMock(return_value={"test": "data"})

        # Run the agent (for a limited time to avoid an infinite loop in tests)
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            try:
                self.agent.run()
            except KeyboardInterrupt:
                pass

        self.assertEqual(mock_post.call_count, 1)  # Called once for auth
        self.agent.send_data.assert_called()  # Ensure send_data was called

if __name__ == '__main__':
    unittest.main()
