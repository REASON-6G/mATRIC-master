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
    access_token_expire_minutes: int = 1

    # CORS settings
    backend_cors_origins: list = []

    class Config:
        env_file = ".env"

settings = Settings()
