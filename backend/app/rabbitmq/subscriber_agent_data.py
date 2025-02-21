# /wiremq/subscriber_agent_data_linux.py

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import logging
import json
from app.rabbitmq.consumer import RabbitMQConsumer
from app.utils.http_callback import send_callback
from dotenv import load_dotenv
from app.utils.influxdb_reader import InfluxDBReader
from datetime import datetime

# Constants
CALLBACK_URL = "http://backend/callback/agent_data"

class SubscriberAgentData:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Initialize RabbitMQ consumer and InfluxDB reader
        self.rabbitmq_consumer = RabbitMQConsumer(queue_name="agent_data")
        self.influxdb_reader = InfluxDBReader()

    def process_message(self, message):
        """
        Process the incoming message from RabbitMQ and query InfluxDB for agent data.
        """
        try:
            job_number = message.get("job_number")
            task_details = message.get("data", {})
            agent_id = task_details.get("agent_id")
            start_time = task_details.get("start_time")
            end_time = task_details.get("end_time")

            # Log task details
            self.logger.info(f"Processing task: {job_number} for agent_id: {agent_id}")

            # Query InfluxDB for agent data
            agent_data = self.influxdb_reader.query_agent_data(agent_id, start_time, end_time)
            self.logger.info(f"Fetched agent data: {agent_data}")

            # Serialize datetime objects in the data
            def serialize_data(record):
                return {
                    key: (value.isoformat() if isinstance(value, datetime) else value)
                    for key, value in record.items()
                }

            serialized_data = [serialize_data(record) for record in agent_data]

            logging.info(f"Serialized agent data: {serialized_data}")

            # Send data back to FastAPI callback
            send_callback(job_number, CALLBACK_URL, serialized_data)

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            # Send failure response to callback
            task_data = json.loads(message)
            send_callback(task_data.get("job_number"), CALLBACK_URL, [{"status": "failed", "error": str(e)}])

    def run(self):
        """
        Run the subscriber to continuously listen for messages from RabbitMQ.
        """
        try:
            self.logger.info("Starting RabbitMQ consumer for agent_data on Linux...")
            self.rabbitmq_consumer.consume(self.process_message)
        except KeyboardInterrupt:
            self.logger.info("Shutting down RabbitMQ consumer...")
        finally:
            self.rabbitmq_consumer.stop()

if __name__ == "__main__":
    subscriber = SubscriberAgentData()
    subscriber.run()
