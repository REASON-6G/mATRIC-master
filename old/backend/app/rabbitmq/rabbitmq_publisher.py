# /rabbitmq/rabbitmq_publisher.py
import pika
import json
from app.rabbitmq.rabbitmq_connection import RabbitMQConnectionManager
from app.config import settings
import logging

class RabbitMQPublisher:
    def __init__(self, exchange: str = "default_exchange"):
        self.connection_manager = RabbitMQConnectionManager(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            username=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            vhost=settings.rabbitmq_vhost
        )
        self.connection = self.connection_manager.get_connection()
        if not self.connection:
            raise RuntimeError("RabbitMQ connection could not be established")
        logging.info("RabbitMQ connection established.")

        self.channel = self.connection.channel()
        if not self.channel:
            raise RuntimeError("RabbitMQ channel could not be created")
        logging.info("RabbitMQ channel created.")

        self.exchange = exchange
        print("publisher self.exchange: ", self.exchange)
        try:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type="direct", durable=True)
            logging.info(f"Exchange '{self.exchange}' declared successfully.")
            print("publisher exchange after declare: self.exchange")
        except Exception as e:
            logging.error(f"Failed to declare exchange '{self.exchange}': {str(e)}")
            raise

    def publish(self, routing_key: str, message: dict):
        """
        Publish a message to RabbitMQ.
        :param routing_key: The queue or topic name.
        :param message: The message payload as a dictionary.
        """
        try:
            print("publisher start")
            if not self.channel or self.channel.is_closed:
                raise RuntimeError("Cannot publish: RabbitMQ channel is closed")
            if not isinstance(message, dict):
                raise ValueError("Message must be a dictionary")

            message_body = json.dumps(message)
            print("publisher message_body", message_body)
            print("publisher self.exchange before publish", self.exchange)
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key= routing_key,
                body=message_body,
                properties=pika.BasicProperties(content_type="application/json", delivery_mode=2)
            )
            print("publisher after publish")
            logging.info(f"Message published to exchange '{self.exchange}' with routing key '{routing_key}': {message}")
        except Exception as e:
            logging.error(f"Failed to publish message: {str(e)}")
            raise
