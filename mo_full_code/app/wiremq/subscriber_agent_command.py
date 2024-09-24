# /wiremq/subscriber_agent_command.py
import requests
import time
import logging
from matching_service_client import MSClient
# from app.database import get_db_manager, DatabaseManager  # Import database manager to retrieve agent config
# from app.config import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import DatabaseManager

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


class CommandSubscriber:
    def __init__(self):
        self.ms_client = MSClient(settings["matching_service_config"])
        self.ms_client.run()
        self.ms_client.connect("127.0.0.1", 15000, block=True)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        # Subscribe to the "send_command" topic
        self.ms_client.subscribe("agent_task/send_command", {}, block=False)
        self.logger.info("Subscribed to 'agent_task/send_command' topic")

    def get_agent_config(self, agent_id: str, db_manager: DatabaseManager):
        """
        Retrieve the agent's configuration from the database using DatabaseManager.
        The configuration includes the agent's base API URL.
        """
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return agent.configuration

    def process_message(self, message, db_manager: DatabaseManager):
        """
        Process the message, extract the agent_id and command,
        and send the command to the agent's API endpoint.
        """
        try:
            print("yes")
            payload = message.get("payload", {}).get("data", {})
            print("payload: ", payload)
            agent_id = payload.get("data").get("agent_id")
            print("agent_id: ", agent_id)
            command = payload.get("data").get("command")
            print("command: ", command)
            self.logger.info(f"Received command for agent {agent_id}: {command}")

            print("before agent_config: ")
            # Step 1: Retrieve the agent's configuration (which includes the base API URL)
            agent_config = self.get_agent_config(agent_id, db_manager)
            print("agent_config: ", agent_config)
            base_api_url = agent_config.get("api_url")

            if not base_api_url:
                self.logger.error(f"No API URL found for agent {agent_id}")
                return

            # Step 2: Construct the full API URL by including the agent_id in the URL
            agent_api_url = f"{base_api_url}/{agent_id}"  # Example: http://agent-api-url/agent_id

            # Step 3: Make an API call to the agent with the command
            response = requests.post(agent_api_url, json={"command": command})
            
            if response.status_code == 200:
                self.logger.info(f"Successfully sent command to agent {agent_id}")
            else:
                self.logger.error(f"Failed to send command to agent {agent_id}. Status code: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")

    def run(self, db_manager: DatabaseManager):
        """
        Continuously receive messages and process them.
        """
        try:
            while True:
                messages = self.ms_client.receive()
                # self.logger.info("message", messages)
                for message in messages:
                    self.process_message(message, db_manager)
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.info("Stopping subscriber...")
        finally:
            self.stop()

    def stop(self):
        self.ms_client.stop()

if __name__ == "__main__":
    # Use the database manager to access agent configurations
    from app.database import get_db_manager
    db = get_db_manager()  # Assume we can instantiate the DB manager here
    subscriber = CommandSubscriber()
    subscriber.start()
    subscriber.run(db)
