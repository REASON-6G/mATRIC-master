import time
import logging
from matching_service_client import MSClient
#from app.utils.influxdb_writer import InfluxDBWriter  # Assuming InfluxDBWriter is implemented here

# Define the configuration for the matching service
settings = {"matching_service_config": {
    "name": "messaging_service_subscriber",
    "auth_url": "http://localhost:8080",
    "realm": "reason-dev",
    "certs_path": "protocol/openid-connect/certs",
    "resource": "matching-service",
    "client_secret_key": "iC6Rt95FQJEdpIdIPB60DvKhT9Zxp9oa",
    "username": "mo_test_sub",
    "password": "ubuntu",
    "host": "localhost",
    "port": 17001,
    "data_port": 17002,
    "log_level": "info",
    "advertised_host": "host.docker.internal",
    "socket_family": "inet"
    }
}


class MessagingService:
    def __init__(self):
        self.ms_client = MSClient(settings["matching_service_config"])
        self.ms_client.run()
        self.ms_client.connect("127.0.0.1", 15000, block=True)
        #self.influx_writer = InfluxDBWriter()  # Using the existing class from another file

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        # Get all topics for agents dynamically
        topics = self.ms_client.get_topics(block=True)
        self.logger.info(f"Available topics: {topics}")
        # Subscribe to all agent data topics
        for topic in topics:
            if topic.startswith("agent/"):
                self.ms_client.subscribe(topic, {}, block=False)
                self.logger.info(f"Subscribed to topic: {topic}")

    def process_message(self, message):
        # Extract and process the message details
        payload = message.get("payload", {}).get("data", {})
        self.logger.info(f"Received message: {payload}")
        # Use the topic name for measurement to differentiate data
        #self.influx_writer.write_data(message.get("topic"), payload)

    def run(self):
        try:
            while True:
                messages = self.ms_client.receive()
                for message in messages:
                    try:
                        self.process_message(message)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.info("Stopping subscriber...")
        except Exception as e:
            self.logger.error(f"Fatal error in messaging service: {e}")
        finally:
            self.stop()

    def stop(self):
        self.ms_client.stop()
        # self.influx_writer.close()

if __name__ == "__main__":
    service = MessagingService()
    service.start()
    service.run()
