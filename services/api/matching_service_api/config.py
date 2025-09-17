import os


def get_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def get_bool(name, default=False):
    val = os.getenv(name, str(default)).lower()
    return val in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev")
    JWT_ACCESS_TOKEN_EXPIRES = get_int("ACCESS_TOKEN_EXPIRES", 30)
    JWT_REFRESH_TOKEN_EXPIRES = get_int("REFRESH_TOKEN_EXPIRES", 1209600)

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:changeme@localhost:27017/matchingservice")

    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:changeme@localhost:5672/")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "topics")

    INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "devtoken")
    INFLUX_ORG = os.getenv("INFLUX_ORG", "matric")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "topics")
