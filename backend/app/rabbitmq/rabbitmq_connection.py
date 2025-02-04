import pika
import logging

class RabbitMQConnectionManager:
    def __init__(self, host: str = "mq", port: int = 5672, username: str = "guest", password: str = "guest"):
        """
        Initialize the RabbitMQ connection manager with default or custom RabbitMQ server configurations.

        :param host: The hostname or IP address of the RabbitMQ server.
        :param port: The port on which RabbitMQ is running (default: 5672).
        :param username: The username for RabbitMQ authentication (default: guest).
        :param password: The password for RabbitMQ authentication (default: guest).
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def connect(self):
        """
        Establish a connection to the RabbitMQ server.
        """
        try:
            self.logger.info("Connecting to RabbitMQ...")
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials, virtual_host='mq', heartbeat=0)
            self.connection = pika.BlockingConnection(parameters)
            self.logger.info("Connected to RabbitMQ.")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def get_connection(self):
        """
        Get the RabbitMQ connection. If not already connected, establish a connection.

        :return: A RabbitMQ connection object.
        """
        if not self.connection or self.connection.is_closed:
            self.connect()
        return self.connection

    def close_connection(self):
        """
        Close the RabbitMQ connection if it is open.
        """
        if self.connection and not self.connection.is_closed:
            self.logger.info("Closing RabbitMQ connection...")
            self.connection.close()
            self.logger.info("RabbitMQ connection closed.")

    def __enter__(self):
        """
        Context manager entry point. Ensures a connection is established when used with 'with'.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point. Ensures the connection is closed when exiting the context.
        """
        self.close_connection()
