import logging
import json
import time
from ansible_runner import run
from app.utils.http_callback import send_callback
from dotenv import load_dotenv
from app.rabbitmq.rabbitmq_connection import RabbitMQConnectionManager
from app.rabbitmq.consumer import RabbitMQConsumer

load_dotenv()

# Callback URL for emulator task completion
EMULATOR_CALLBACK_URL = "http://localhost:8000/callback/emulator"


class EmulatorTaskSubscriber:
    def __init__(self, queue_name="emulator_tasks"):
        """
        Initialize the EmulatorTaskSubscriber with RabbitMQ consumer and queue name.
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize RabbitMQ connection and consumer
        self.rabbitmq_connection_manager = RabbitMQConnectionManager()
        self.rabbitmq_consumer = RabbitMQConsumer(
            self.rabbitmq_connection_manager, queue_name=queue_name
        )

    def process_message(self, body: dict):
        """
        Process the emulator spin-up task and run the Ansible playbook using ansible-runner.
        """
        task_data = body.get("data", {})
        logging.info(f"Received task data: {task_data}")

        # Extract task details
        job_number = task_data.get("job_number")
        access_point_type = task_data.get("access_point_type")
        num_access_points = task_data.get("num_access_points")
        locations = task_data.get("locations")
        num_devices = task_data.get("num_devices")
        duration = task_data.get("duration")

        logging.info(f"Task received for job_number {job_number}: {access_point_type} emulator")

        try:
            # Get the appropriate playbook path based on the access_point_type
            playbook = self.get_playbook(access_point_type)

            # Prepare extra vars for Ansible
            extra_vars = {
                "num_access_points": num_access_points,
                "locations": locations,
                "num_devices": num_devices,
                "duration": duration,
            }

            # Run the Ansible playbook using ansible-runner
            result = run(
                private_data_dir="/tmp",  # Required for ansible-runner
                playbook=playbook,
                extravars=extra_vars,
            )

            # Determine the playbook execution status
            if result.status == "successful":
                logging.info(f"Playbook executed successfully for job {job_number}")
                payload = {
                    "job_number": job_number,
                    "status": "completed",
                    "details": task_data,
                }
            else:
                logging.error(f"Playbook failed for job {job_number}")
                payload = {
                    "job_number": job_number,
                    "status": "failed",
                    "details": result.stdout.read(),
                }

            # Send the callback
            send_callback(job_number, EMULATOR_CALLBACK_URL, [payload])

        except Exception as e:
            logging.error(f"Error processing job {job_number}: {str(e)}")
            payload = {
                "job_number": job_number,
                "status": "failed",
                "error": str(e),
            }
            send_callback(job_number, EMULATOR_CALLBACK_URL, [payload])

    def get_playbook(self, access_point_type):
        """
        Returns the appropriate playbook based on the access_point_type.
        """
        playbook_mapping = {
            "5G": "spinup_5g.yml",
            "WiFi": "spinup_wifi.yml",
            "LiFi": "spinup_lifi.yml",
        }
        if access_point_type not in playbook_mapping:
            raise ValueError(f"Unsupported access point type: {access_point_type}")
        return playbook_mapping[access_point_type]

    def run(self):
        """
        Run the subscriber to listen for messages continuously.
        """
        self.logger.info("Starting EmulatorTaskSubscriber...")
        try:
            self.rabbitmq_consumer.start_consuming(self.process_message)
        except KeyboardInterrupt:
            self.logger.info("Shutting down EmulatorTaskSubscriber...")
        finally:
            self.rabbitmq_connection_manager.close()


if __name__ == "__main__":
    # Start the Emulator Task Subscriber
    subscriber = EmulatorTaskSubscriber(queue_name="emulator_tasks")
    subscriber.run()
