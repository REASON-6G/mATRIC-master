# /rabbitmq/subscriber_agent_details.py

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

import logging
import json
import asyncio
import websockets
from app.rabbitmq.consumer import RabbitMQConsumer
from app.database_session import SessionLocal
from app.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
WEBSOCKET_URL_TEMPLATE = "ws://backend/api/v1/callback/agent_details/ws/{job_number}"


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

    async def websocket_send(self, job_number, data):
        """
        Sends agent details to the WebSocket server.
        """
        websocket_url = WEBSOCKET_URL_TEMPLATE.format(job_number=job_number)
        logger.info(f"Connecting to WebSocket URL: {websocket_url}")
        try:
            async with websockets.connect(websocket_url) as websocket:
                message = json.dumps(data)
                logger.info(f"Sending data to WebSocket: {message}")
                await websocket.send(message)
                # Wait for an acknowledgment (optional)
                await websocket.recv()
                # Properly close the WebSocket connection
                await websocket.close(code=1000)
                logger.info("WebSocket connection closed successfully")

                logger.info(f"Data sent via WebSocket for job_number: {job_number}")
        except websockets.ConnectionClosedOK:
            logger.info("WebSocket connection closed normally.")
        except websockets.ConnectionClosedError as e:
            logger.error(f"WebSocket connection closed with error: {e}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")

    def process_message(self, message: dict):
        """
        Process the incoming message to fetch and send agent details.
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

            # Send the fetched details directly via WebSocket
            asyncio.run(self.websocket_send(job_number, agent_details))

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
