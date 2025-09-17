from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import logging
from app.rabbitmq.consumer import RabbitMQConsumer
from app.utils.http_callback import send_callback
from app.database_session import SessionLocal
from app.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentDetailsSubscriber:
    def __init__(self):
        self.queue_name = "agent_details"  # Queue for agent details
        self.consumer = RabbitMQConsumer(queue_name=self.queue_name)

    def agent_to_dict(self, agent) -> dict:
        """
        Convert an agent object to a dictionary format.
        """
        return {
            "id": str(agent.id),
            "ap_id": agent.ap_id,
            "configuration": agent.configuration,
            "onboard": agent.onboard,
        }

    def fetch_agent_details(self):
        """
        Fetch all agents' details from the database.
        """
        db = SessionLocal()
        try:
            db_manager = DatabaseManager(db)
            agents = db_manager.get_all_agents()
            logger.info(f"Fetched agent details: {agents}")
            return [self.agent_to_dict(agent) for agent in agents]
        except Exception as e:
            logger.error(f"Error fetching agent details from database: {e}")
            return []
        finally:
            db.close()

    def process_message(self, message: dict):
        """
        Process the incoming message to fetch and return agent details.
        """
        try:
            logger.info(f"Received message: {message}")

            # Extract job_number and task_type
            job_number = message.get("job_number")
            task_type = message.get("task_type")

            if task_type != "all_agents_details":
                logger.error("Unsupported task type")
                return

            logger.info(f"Processing task: {task_type} for job: {job_number}")

            # Fetch agent details from the database
            agent_details = self.fetch_agent_details()

            # Send the fetched details back through callback
            callback_url = f"http://localhost:8000/callback/agent_details"
            send_callback(job_number, callback_url, agent_details)
            logger.info(f"Agent details sent to callback for job: {job_number}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def start(self):
        """
        Start the RabbitMQ consumer to listen for messages.
        """
        logger.info("Starting AgentDetailsSubscriber...")
        self.consumer.consume(self.process_message)

    def stop(self):
        """
        Stop the RabbitMQ consumer gracefully.
        """
        logger.info("Stopping AgentDetailsSubscriber...")
        self.consumer.stop()


if __name__ == "__main__":
    subscriber = AgentDetailsSubscriber()
    try:
        subscriber.start()
    except KeyboardInterrupt:
        subscriber.stop()
