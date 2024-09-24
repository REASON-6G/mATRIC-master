# wiremq/mapp_publisher.py

from matching_service_client import MSClient
from app.config import settings


class MAppPublisher:
    def __init__(self):
        self.client = MSClient(settings.ms_config)
        self.client.run()
        self.client.connect("localhost", 15000, block=True)

    def publish_data(self, topic: str, payload: dict):
        """Publish data to a given topic."""
        # Add the dynamic topic if not already added
        self.client.add_topic(topic, block=True, to_db=False)
        #self.client.add_topic(topic, block=True)
        self.client.publish(topic, {"data": payload})

    def stop(self):
        """Stop the MSClient gracefully."""
        self.client.stop()
