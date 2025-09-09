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
    # Core
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "dev")
    JWT_ACCESS_TOKEN_EXPIRES = get_int("ACCESS_TOKEN_EXPIRES", 900)
    JWT_REFRESH_TOKEN_EXPIRES = get_int("REFRESH_TOKEN_EXPIRES", 1209600)

    # MongoDB – shared with API
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://admin:changeme@localhost:27017/matchingservice"
    )

    # RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:changeme@localhost:5672/")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "topics")

    # InfluxDB – optional
    INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "devtoken")
    INFLUX_ORG = os.getenv("INFLUX_ORG", "matric")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "topics")

    # Emulator-specific
    PUBLISH_INTERVAL = get_int("PUBLISH_INTERVAL", 5)   # seconds
    EMULATOR_ID = os.getenv("EMULATOR_ID", "default")
    RANDOM_SEED = get_int("RANDOM_SEED", None)

    # API authentication (agent user)
    API_URL = os.getenv("API_URL", "http://api:5000")
    EMULATOR_USERNAME = os.getenv("EMULATOR_USERNAME", f"agent_{EMULATOR_ID}")
    EMULATOR_PASSWORD = os.getenv("EMULATOR_PASSWORD", "changeme")
    EMULATOR_ROLE = os.getenv("EMULATOR_ROLE", "agent")
