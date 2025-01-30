# /wiremq/agent_task_publisher.py

from matching_service_client import MSClient
from app.config import settings

settings = {"ms_config": {
        "name": "task_publisher",
        "auth_url": "http://localhost:8080",
        "realm": "reason-dev",
        "certs_path": "protocol/openid-connect/certs",
        "resource": "matching-service",
        "client_secret_key": "iC6Rt95FQJEdpIdIPB60DvKhT9Zxp9oa",
        "username": "mo_test_mapp",
        "password": "ubuntu",
        "host": "localhost",
        "port": 18000,
        "data_port": 18001,
        "log_level": "info",
        "socket_family": "inet",
        "advertised_host": "host.docker.internal"
    }
}

class AgentTaskPublisher:
    def __init__(self):
        # Step 1: Set up the MSClient (WireMQ client) with the matching service configuration
        self.ms_client = MSClient(settings["ms_config"])
        self.ms_client.run()
        print("before connect")
        self.ms_client.connect(
            "localhost",
            15000,
            block=True
        )
        print("after connect")
    
    def publish_agent_task(self, job_number: str, task_type: str, additional_data: dict = None):
        """
        Publishes a request to WireMQ based on the task type.

        Args:
        - job_number (str): Unique identifier for tracking the request.
        - task_type (str): The type of task ('all_agents_details', 'agent_data', 'send_command').
        - additional_data (dict): Any additional data required for the task (optional).
        """
        # Step 2: Construct the message payload
        message_payload = {
            "job_number": job_number,
            "task_type": task_type,
        }
        if additional_data:
            message_payload["data"] = additional_data

        print("message_payload: ", message_payload)

        # Step 3: Publish the message to the appropriate topic
        print("before topic: ")
        topic = f"agent_task/{task_type}"
        print("topic: ", topic)
        self.ms_client.add_topic(topic, block=True)
        print("after add topic: ")
        self.ms_client.publish(topic, message_payload)

        print(f"Published {task_type} task with job_number {job_number}")
