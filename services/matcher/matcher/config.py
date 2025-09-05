import os


class Config:
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 5))
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:changeme@localhost:27017/matchingservice")
    DB_NAME = os.getenv("DB_NAME", "matchingservice")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:changeme@localhost:5672/")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "topics")

