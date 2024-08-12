# wiremq/mapp_publisher.py

from matching_service_client import MSClient
from app.config import settings


ms_config = {
    "name": "mapp_publisher",
    "auth_url": "http://localhost:8080",
    "realm": "reason-dev",
    "certs_path": "protocol/openid-connect/certs",
    "resource": "matching-service",
    "client_secret_key": "KmBjqvrTA9PUDwIx9PObKYnTKksTRLtf",
    "username": "mo_test_mapp",
    "password": "mapp@Bristol",
    "host": "localhost",
    "port": 15000,
    "data_port": 15001,
    "log_level": "info",
}

class MAppPublisher:
    def __init__(self):
        self.client = MSClient(ms_config)
        self.client.run()
        self.client.connect(ms_config["host"], ms_config["port"], block=True)

    def publish_data(self, topic: str, payload: dict):
        """Publish data to a given topic."""
        # Add the dynamic topic if not already added
        self.client.add_topic(topic, block=True)
        self.client.publish(topic, {"data": payload})

    def stop(self):
        """Stop the MSClient gracefully."""
        self.client.stop()
