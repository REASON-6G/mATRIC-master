from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Dict, Any

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    admin_email: EmailStr
    items_per_user: int = 50
    admin_email: EmailStr

    # PostGres Database settings
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_name: str

    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS settings
    backend_cors_origins: str = ["*"]

    # Influxdb settings
    influxdb_url: str = "http://localhost:8086"  # Adjust to your InfluxDB URL
    influxdb_org: str = "University of Bristol"
    influxdb_token: str = "D-VMUk_5WFeKXIg5x9L5NRIMI5CUpi6xrjCSMCi3mSeUPrWjH0oqo6Ci6m9MlqHgnGrD5UsqHkCZ5iM0iaMOcA==",
    influxdb_bucket: str = "MatchingServices"

    # Rabbit MQ settings
    rabbitmq_host: str
    rabbitmq_port: str
    rabbitmq_vhost: str
    rabbitmq_queue: str
    rabbitmq_user: str
    rabbitmq_password: str

    class Config:
        env_file = ".env"

settings = Settings()
