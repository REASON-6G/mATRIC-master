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
    influxdb_config : Dict[str, Any] = {
        "influx_url": "http://localhost:8086",  # Adjust to your InfluxDB URL
        "influx_org": "University of Bristol",
        "influx_token": "D-VMUk_5WFeKXIg5x9L5NRIMI5CUpi6xrjCSMCi3mSeUPrWjH0oqo6Ci6m9MlqHgnGrD5UsqHkCZ5iM0iaMOcA==",
        "influx_bucket": "MatchingServices"
    }

    class Config:
        env_file = ".env"

settings = Settings()
