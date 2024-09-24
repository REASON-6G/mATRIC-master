# wiremq/messaging_service.py

import time
from matching_service_client import MSClient
from app.utils.influxdb_writer import InfluxDBWriter
from app.config import settings

class MessagingService:
    def __init__(self):
        self.ms_client = MSClient(settings.matching_service_config)
        self.ms_client.run()
        self.ms_client.connect(settings.matching_service_config["host"], settings.matching_service_config["port"], block=True)
        self.influx_writer = InfluxDBWriter()

    def start(self):
        # Get all topics for agents dynamically
        topics = self.ms_client.get_topics(block=True)
        print("Available topics:", topics)
        # Subscribe to all agent data topics
        for topic in topics:
            if topic.startswith("agent/"):
                self.ms_client.subscribe(topic, {}, block=False)

    def process_message(self, message):
        # Extract and process the message details
        payload = message.get("payload", {}).get("data", {})
        print(f"Received message: {payload}")
        # Use the topic name for measurement to differentiate data
        self.influx_writer.write_data(message.get("topic"), payload)

    def run(self):
        try:
            while True:
                messages = self.ms_client.receive()
                for message in messages:
                    self.process_message(message)
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nStopping subscriber...")
        finally:
            self.stop()

    def stop(self):
        self.ms_client.stop()
        self.influx_writer.close()
