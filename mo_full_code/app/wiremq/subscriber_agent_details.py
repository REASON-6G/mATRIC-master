import time
import logging
from matching_service_client import MSClient
from app.utils.http_callback import send_callback  # Assuming this handles HTTP callbacks
from dotenv import load_dotenv  # Load environment variables from .env file
import os
from app.models import Agent
import json


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


class AgentDetailsSubscriber:
    def __init__(self):
        # Initialize the WireMQ client with matching service config from settings
        self.ms_client = MSClient(settings["matching_service_config"])
        self.ms_client.run()
        self.ms_client.connect("127.0.0.1", 15000, block=True)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        # Subscribe to the topic that handles all agent details
        self.ms_client.subscribe("agent_task/all_agents_details", {}, block=False)
        self.logger.info("Subscribed to topic: agent_task/all_agents_details")

    def agent_to_dict(self, agent: Agent) -> dict:
        return {
            "id": str(agent.id),
            "ap_id": agent.ap_id,
            "configuration": agent.configuration,
            "onboard": agent.onboard,
        }

    def process_message(self, message):
        print("message: ", message)
        self.logger.info(f"message: {message}")
        task_type = message["payload"]["data"]["task_type"]
        self.logger.info(f"task_type: {task_type}")
        job_number = message["payload"]["data"]["job_number"]
        self.logger.info(f"job_number: {job_number}")

        # Ensure the task is to retrieve agent details
        if task_type == "all_agents_details":
            self.logger.info(f"Processing task: {task_type} for job: {job_number}")

            # Open a new SQLAlchemy session
            from app.database_session import SessionLocal  # SessionLocal from database_session.py
            db = SessionLocal()

            try:
                # Initialize DatabaseManager with the session
                from app.database import DatabaseManager  # DatabaseManager to interact with the database
                db_manager = DatabaseManager(db)

                # Fetch all agents' details from the database
                agent_details = db_manager.get_all_agents()
                self.logger.info(f"Fetched agent details: {agent_details}")

                if isinstance(agent_details, list):
                    agent_details_dict = [self.agent_to_dict(agent) for agent in agent_details]
                    print("type(agent_details): ", type(agent_details))
                    self.logger.info(f"agent_details_dict: {agent_details_dict}")
                else:
                    agent_details_dict = self.agent_to_dict(agent_details)


                self.logger.info(f"agent_details_dict: {agent_details_dict}")

                # Send the fetched details back through callback
                callback_url = f"http://127.0.0.1:8000/callback/agent_details"
                send_callback(job_number, callback_url, agent_details_dict)
                self.logger.info(f"Sent agent details to callback for job: {job_number}")

            except Exception as e:
                # Log any errors that occur during message processing
                self.logger.error(f"Error processing message: {e}")

            finally:
                # Ensure that the session is closed after use
                db.close()

    def run(self):
        self.logger.info("before 83")
        try:
            self.logger.info("before 85")
            while True:
                # self.logger.info("start of loop")
                # Receive messages from the WireMQ client
                messages = self.ms_client.receive()
                for message in messages:
                    self.logger.info("message", message)
                    self.process_message(message)
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.info("Shutting down subscriber...")
        finally:
            # Ensure the client is stopped gracefully
            self.ms_client.stop()


if __name__ == "__main__":
    # Start and run the subscriber
    service = AgentDetailsSubscriber()
    service.start()
    service.run()