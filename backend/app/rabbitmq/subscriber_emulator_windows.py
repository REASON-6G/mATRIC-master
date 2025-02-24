import logging
import json
import subprocess
import os
from app.rabbitmq.consumer import RabbitMQConsumer
from app.utils.http_callback import send_callback

# Define constants
EMULATOR_CALLBACK_URL = "http://localhost:8000/callback/emulator"
WSL_PLAYBOOKS_DIR = "/mnt/c/Users/hg24245/PycharmProjects/mATRIC/app/playbooks/"


class EmulatorTaskSubscriberWindows:
    def __init__(self, queue_name="emulator_spinup"):
        self.queue_name = queue_name
        self.consumer = RabbitMQConsumer(queue_name=self.queue_name)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_message(self, channel, method, properties, body):
        """
        Process the emulator spin-up task.
        """
        try:
            # Decode the message body
            task_data = json.loads(body.decode('utf-8'))
            self.logger.info(f"Received message: {task_data}")

            job_number = task_data.get("job_number")
            emulators = task_data.get("emulators", [])

            for emulator in emulators:
                access_point_type = emulator.get("access_point_type")
                num_access_points = emulator.get("num_access_points")
                locations = emulator.get("locations")
                num_devices = emulator.get("num_devices")
                duration = emulator.get("duration")

                self.logger.info(f"Processing task {job_number} for {access_point_type} emulator")

                # Get the appropriate playbook
                playbook = self.get_playbook(access_point_type)
                playbook_path = os.path.join(WSL_PLAYBOOKS_DIR, playbook)

                # Build the ansible-playbook command to run inside WSL
                env_vars = {
                    "num_access_points": num_access_points,
                    "locations": locations,
                    "num_devices": num_devices,
                    "duration": duration,
                }
                ansible_command = [
                    "wsl",
                    "ansible-playbook",
                    playbook_path,
                    "--extra-vars",
                    json.dumps(env_vars),
                ]
                self.logger.info(f"Running command: {' '.join(ansible_command)}")

                # Execute the Ansible playbook
                result = subprocess.run(ansible_command, capture_output=True, text=True)

                # Check for successful execution
                if result.returncode == 0:
                    self.logger.info(f"Playbook executed successfully for job {job_number}")
                    # Send success callback
                    payload = {
                        "job_number": job_number,
                        "status": "completed",
                        "details": emulator,
                    }
                    send_callback(job_number, EMULATOR_CALLBACK_URL, [payload])
                else:
                    self.logger.error(f"Playbook failed with error: {result.stderr}")
                    # Send failure callback
                    payload = {
                        "job_number": job_number,
                        "status": "failed",
                        "error": result.stderr,
                    }
                    send_callback(job_number, EMULATOR_CALLBACK_URL, [payload])

            # Acknowledge the message
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            # Send failure callback
            payload = {
                "job_number": task_data.get("job_number") if "task_data" in locals() else None,
                "status": "failed",
                "error": str(e),
            }
            send_callback(payload["job_number"], EMULATOR_CALLBACK_URL, [payload])
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def get_playbook(self, access_point_type):
        """
        Returns the appropriate playbook based on the access_point_type.
        """
        if access_point_type == "5G":
            return "spinup_5g.yml"
        elif access_point_type == "WiFi":
            return "spinup_wifi.yml"
        elif access_point_type == "LiFi":
            return "spinup_lifi.yml"
        else:
            raise ValueError(f"Unsupported access point type: {access_point_type}")

    def run(self):
        """
        Start consuming messages from the RabbitMQ queue.
        """
        self.consumer.consume(self.process_message)


if __name__ == "__main__":
    subscriber = EmulatorTaskSubscriberWindows()
    subscriber.run()
