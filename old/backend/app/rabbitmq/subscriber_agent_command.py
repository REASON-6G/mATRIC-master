from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import logging
import requests
from app.rabbitmq.consumer import RabbitMQConsumer
from app.database_session import SessionLocal
from app.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandSubscriber:
    def __init__(self):
        # Initialize RabbitMQ consumer with the "agent_task_send_command" queue
        self.consumer = RabbitMQConsumer(queue_name="send_command")
        self.db_session = SessionLocal()

    def get_agent_config(self, agent_id: str, db_manager: DatabaseManager):
        """
        Retrieve the agent's configuration from the database using DatabaseManager.
        The configuration includes the agent's base API URL.
        """
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return agent.configuration

    def process_message(self, message):
        """
        Process the message, extract the agent_id and command,
        and send the command to the agent's API endpoint.
        """
        db_manager = DatabaseManager(self.db_session)

        try:
            agent_id = message.get("agent_id")
            command = message.get("command")

            if not agent_id or not command:
                logger.error("Invalid message payload: Missing 'agent_id' or 'command'")
                return False

            logger.info(f"Processing command for agent {agent_id}: {command}")

            # Step 1: Retrieve the agent's configuration
            agent_config = self.get_agent_config(agent_id, db_manager)
            base_api_url = agent_config.get("api_url")

            if not base_api_url:
                logger.error(f"No API URL found for agent {agent_id}")
                return False

            # Step 2: Construct the full API URL
            agent_api_url = f"{base_api_url}/{agent_id}"

            # Step 3: Make an API call to the agent with the command
            response = requests.post(agent_api_url, json={"command": command})

            if response.status_code == 200:
                logger.info(f"Successfully sent command to agent {agent_id}")
            else:
                logger.error(f"Failed to send command to agent {agent_id}. Status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def run(self):
        """
        Run the subscriber to listen for RabbitMQ messages continuously.
        """
        logger.info("Starting CommandSubscriber...")
        try:
            self.consumer.consume(self.process_message)
        except KeyboardInterrupt:
            logger.info("Shutting down CommandSubscriber...")
        finally:
            self.stop()

    def stop(self):
        """
        Close database session and stop RabbitMQ consumer gracefully.
        """
        self.db_session.close()
        self.consumer.stop()


if __name__ == "__main__":
    subscriber = CommandSubscriber()
    subscriber.run()
