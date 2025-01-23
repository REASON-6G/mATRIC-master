from pydantic import BaseSettings, EmailStr

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
    backend_cors_origins: list = []

    # WireMQ settings
    ms_config = {
        "name": "mapp_publisher",
        "auth_url": "http://localhost:8080",
        "realm": "reason-dev",
        "certs_path": "protocol/openid-connect/certs",
        "resource": "matching-service",
        "client_secret_key": "X66VLRwEsuc8eV1YMeTHkzhiGnVSxg9K",
        "username": "mo_test_mapp",
        "password": "mapp@Bristol",
        "host": "localhost",
        "port": 15000,
        "data_port": 15001,
        "log_level": "info",
    }

    matching_service_config = {
        "name": "mapp_subscriber",
        "auth_url": "http://localhost:8080",
        "realm": "reason-dev",
        "certs_path": "protocol/openid-connect/certs",
        "resource": "matching-service",
        "client_secret_key": "X66VLRwEsuc8eV1YMeTHkzhiGnVSxg9K",
        "username": "mo-test-subscriber",
        "password": "subscriber@Bristol",
        "host": "localhost",
        "port": 15002,
        "data_port": 15003,
        "log_level": "info",
    }

    # Influxdb settings
    influxdb_config = {
        "influx_url": "http://localhost:8086",  # Adjust to your InfluxDB URL
        "influx_org": "your_org",
        "influx_token": "your_token",
        "influx_bucket": "your_bucket"
    }

    class Config:
        env_file = ".env"

settings = Settings()
