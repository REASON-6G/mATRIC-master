import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "dev")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("ACCESS_TOKEN_EXPIRES", 900))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("REFRESH_TOKEN_EXPIRES", 1209600))

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/telecom")

    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "topics")

    INFLUX_URL = os.getenv("INFLUX_URL")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
    INFLUX_ORG = os.getenv("INFLUX_ORG")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")