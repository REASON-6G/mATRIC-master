# /rabbitmq/subscriber_agent_update_linux.py

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import logging
import json
from app.rabbitmq.consumer import RabbitMQConsumer
from app.utils.influxdb_writer import InfluxDBWriter


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentUpdateSubscriber:
    def __init__(self):
        self.queue_name = "agent_update"  # Static queue name
        self.consumer = RabbitMQConsumer(self.queue_name)
        self.influx_writer = InfluxDBWriter()

    def process_message(self, message: dict):
        """
        Process the agent update message and store it in InfluxDB.
        """
        try:
            logger.info(f"Received message: {message}")
            ap_id = message.get("ap_id")
            payload = message.get("payload")

            if not ap_id or not payload:
                logger.error("Invalid message format")
                return

            # If payload is a string, deserialize it to a dictionary
            if isinstance(payload, str):
                import json
                payload = json.loads(payload)

            # Construct the measurement name dynamically
            measurement = f"agent/{ap_id}/data"

            # Write to InfluxDB
            data = {
                **payload  # Include the payload fields dynamically
            }
            self.influx_writer.write_data(measurement, data)
            logger.info(f"Successfully saved update for Agent ID: {ap_id} to InfluxDB")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def start(self):
        """
        Start the RabbitMQ consumer.
        """
        logger.info("Starting AgentUpdateSubscriberLinux...")
        self.consumer.consume(self.process_message)

    def stop(self):
        """
        Stop the RabbitMQ consumer and close the InfluxDB writer.
        """
        logger.info("Shutting down AgentUpdateSubscriberLinux...")
        self.influx_writer.close()

if __name__ == "__main__":
    subscriber = AgentUpdateSubscriber()
    try:
        subscriber.start()
    except KeyboardInterrupt:
        subscriber.stop()
