# /wiremq/subscriber_agent_data.py

import time
import logging
from matching_service_client import MSClient
# from app.config import settings
from app.utils.http_callback import send_callback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

class SubscriberAgentData:
    def __init__(self):
        # Initialize MSClient (WireMQ client)
        self.ms_client = MSClient(settings["matching_service_config"])
        self.ms_client.run()
        self.ms_client.connect("127.0.0.1", 15000, block=True)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize InfluxDBReader (for querying data)
        from app.utils.influxdb_reader import InfluxDBReader
        self.influx_reader = InfluxDBReader()

    def start(self):
        # Subscribe to the "agent_data" task topic
        topic = "agent_task/agent_data"
        self.ms_client.subscribe(topic, {}, block=False)
        self.logger.info(f"Subscribed to topic: {topic}")

    def process_message(self, message):
        """
        Process incoming message and handle the "agent_data" task.
        """
        print("message: ", message)
        self.logger.info(f"message: {message}")
        task_type = message["payload"]["data"]["task_type"]
        self.logger.info(f"task_type: {task_type}")
        job_number = message["payload"]["data"]["job_number"]
        self.logger.info(f"job_number: {job_number}")
        data = message["payload"]["data"]["data"]
        self.logger.info(f"data: {data}")

        if task_type == "agent_data":
            self.logger.info(f"Processing {task_type} request with job_number: {job_number}")

            # Extract the agent ID and time range from the message
            agent_id = data.get("agent_id")
            self.logger.info(f"agent_id: {agent_id}")
            start_time = data.get("start_time")
            self.logger.info(f"start_time: {start_time}")
            end_time = data.get("end_time")
            self.logger.info(f"end_time: {end_time}")

            # Query InfluxDB for the agent's data within the time range
            try:
                agent_data = self.influx_reader.query_agent_data(agent_id, start_time, end_time)
                self.logger.info(f"agent_data: {agent_data}")
            except Exception as e:
                self.logger.error(f"Error querying InfluxDB for agent {agent_id}: {e}")
                return

            # Send the agent data to the FastAPI callback endpoint
            callback_url = f"http://127.0.0.1:8000/callback/agent_data"
            send_callback(job_number, callback_url, agent_data)

    def run(self):
        """
        Main loop to listen for messages and process them.
        """
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
        self.influx_reader.close()

if __name__ == "__main__":
    service = SubscriberAgentData()
    service.start()
    service.run()
