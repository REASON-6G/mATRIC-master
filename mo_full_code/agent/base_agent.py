import time
import requests
from typing import Dict, Any
from datetime import datetime, timedelta
from settings import settings

class BaseAgent:
    def __init__(self):
        self.ap_id = settings.ap_id
        self.agent_password = settings.agent_password
        self.token_url = settings.token_url
        self.update_url = settings.update_url
        self.update_interval = settings.update_interval
        self.token_refresh_threshold = settings.token_refresh_threshold
        self.token = None
        self.token_expiry = None

    def authenticate(self) -> None:
        try:
            response = requests.post(
                self.token_url,
                params={"login_type": "agent"},
                data={
                    "username": self.ap_id,
                    "password": self.agent_password
                }
            )
            response.raise_for_status()
            response_data = response.json()
            self.token = response.json()["access_token"]
            # Using the expires_in value from the response to set the token expiry time
            self.token_expiry = datetime.utcnow() + timedelta(seconds=int(response_data["expires_in"]))
            print("token_expiry: ", self.token_expiry)
            print(f"Authenticated with token: {self.token}")
        except Exception as e:
            print(str(e))

    def refresh_token_if_needed(self) -> None:
        try:
            if self.token_expiry is None:
                print("Token expiry not set. Authenticating...")
                self.authenticate()

            time_remaining = (self.token_expiry - datetime.utcnow()).total_seconds()
            print("time_remaining: ", time_remaining)
            if self.token_expiry and (self.token_expiry - datetime.utcnow()).total_seconds() < self.token_refresh_threshold:
                print("Refreshing token...")
                self.authenticate()


            if self.token_expiry and (self.token_expiry - datetime.utcnow()).total_seconds() < settings.token_refresh_threshold:
                print("Refreshing token...")
                self.authenticate()
        except Exception as e:
            print(str(e))

    def send_data(self, data: Dict[str, Any]) -> None:
        try:
            self.refresh_token_if_needed()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(self.update_url, json=data, headers=headers)
            if response.status_code != 200:
                print(f"Failed to send data: {response.status_code}, {response.text}")
            print("Sent data: ", data)
        except Exception as e:
            print(str(e))

    def collect_data(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this method")

    def run(self) -> None:
        try:
            self.authenticate()
            while True:
                data = self.collect_data()
                self.send_data(data)
                time.sleep(self.update_interval)
        except Exception as e:
            print(str(e))
