from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Dict, Any

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    admin_email: EmailStr
    items_per_user: int = 50
    admin_email: EmailStr

    # PostGres Database settings
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS settings
    backend_cors_origins: list = ["*"]

    # WireMQ settings
    ms_config: Dict[str, Any] = {
        "name": "mapp_publisher",
        "auth_url": "http://localhost:8080",
        "realm": "reason-dev",
        "certs_path": "protocol/openid-connect/certs",
        "resource": "matching-service",
        "client_secret_key": "iC6Rt95FQJEdpIdIPB60DvKhT9Zxp9oa",
        "username": "mo_test_mapp",
        "password": "ubuntu",
        "host": "localhost",
        "port": 16000,
        "data_port": 16001,
        "log_level": "info",
        "socket_family": "inet",
        "advertised_host": "host.docker.internal"
    }

    matching_service_config: Dict[str, Any] = {
        "name": "messaging_service_subscriber",
        "auth_url": "http://localhost:8080",
        "realm": "reason-dev",
        "certs_path": "protocol/openid-connect/certs",
        "resource": "matching-service",
        "client_secret_key": "iC6Rt95FQJEdpIdIPB60DvKhT9Zxp9oa",
        "username": "mo_test_sub",
        "password": "ubuntu",
        "host": "localhost",
        "port": 17001,
        "data_port": 17002,
        "log_level": "info",
        "advertised_host": "host.docker.internal",
        "socket_family": "inet"
    }

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
