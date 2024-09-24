# /wiremq/subscriber_agent_details.py

import time
import logging
from matching_service_client import MSClient
from dotenv import load_dotenv
import os
# from app.database import DatabaseManager
# from app.config import settings
from app.utils.http_callback import send_callback

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

class SubscriberAgentDetails:
    def __init__(self):
        # Initialize MSClient (WireMQ client)
        self.ms_client = MSClient(settings["matching_service_config"])
        self.ms_client.run()
        self.ms_client.connect("127.0.0.1", 15000, block=True)
        # self.ms_client.connect(
        #     settings.matching_service_config["host"],
        #     settings.matching_service_config["port"],
        #     block=True
        # )

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize database manager
        from app.database import DatabaseManager
        self.db_manager = DatabaseManager()

    def start(self):
        # Subscribe to agent task topics
        topic = "agent_task/all_agents_details"
        self.ms_client.subscribe(topic, {}, block=False)
        self.logger.info(f"Subscribed to topic: {topic}")

    def process_message(self, message):
        """
        Process incoming message and handle task based on task_type.
        """
        task_type = message.get("task_type")
        job_number = message.get("job_number")

        if task_type == "all_agents_details":
            self.logger.info(f"Processing {task_type} request with job_number: {job_number}")
            
            # Query the database for all agent details
            agent_details = self.db_manager.get_all_agents()  # Implement this method in your DatabaseManager

            # Send the agent details to the FastAPI callback endpoint
            callback_url = f"{settings.fastapi_base_url}/callback/agent_details"
            send_callback(callback_url, job_number, agent_details)

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

if __name__ == "__main__":
    service = SubscriberAgentDetails()
    service.start()
    service.run()
