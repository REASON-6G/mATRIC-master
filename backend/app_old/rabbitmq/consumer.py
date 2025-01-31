from rabbitmq_connection import RabbitMQConnectionManager
import logging
import json
from typing import Callable

class RabbitMQConsumer:
    def __init__(self, queue_name: str, exchange: str = "default_exchange"):
        """
        Initializes the RabbitMQConsumer.

        :param queue_name: The name of the RabbitMQ queue to consume from.
        :param exchange: The name of the RabbitMQ exchange to bind to.
        """
        self.queue_name = queue_name
        print("consumer.py queue_name: ", self.queue_name)
        self.exchange = exchange
        print("consumer.py exchange: ", self.exchange)
        self.connection_manager = RabbitMQConnectionManager()
        self.connection = self.connection_manager.get_connection()
        if not self.connection:
            raise RuntimeError("RabbitMQ connection could not be established")

        self.channel = self.connection.channel()
        if not self.channel:
            raise RuntimeError("RabbitMQ channel could not be created")

        # Declare the exchange and queue
        print("consumer.py befor binding queue_name: ", self.queue_name)
        print("consumer.py before binding exchange: ", self.exchange)
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="direct", durable=True)
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        # Bind the queue to the exchange
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=self.queue_name)
        logging.info(f"Binding queue '{self.queue_name}' to exchange '{self.exchange}' with routing key '{self.queue_name}'")

        # self.channel.queue_bind(exchange="default_exchange", queue="agent_update_1", routing_key="agent_update_1")
        # logging.info("Queue 'agent_update_1' successfully bound to exchange 'default_exchange'")

    def consume(self, callback: Callable[[dict], None]):
        """
        Starts consuming messages from the queue and processes them using the given callback.

        :param callback: A function that processes each received message.
        """
        print("start")
        def wrapped_callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                logging.info(f"Received message: {message}")
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        print("above")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=wrapped_callback)
        logging.info(f"Started consuming from queue: {self.queue_name}")
        self.channel.start_consuming()

    def stop(self):
        """Closes the RabbitMQ connection."""
        self.connection_manager.close_connection()

