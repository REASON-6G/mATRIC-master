class Settings:
    ap_id: str = "12345678"
    token_url: str = "http://127.0.0.1:8000/token"
    agent_password: str = "agent"
    update_url: str = ""
    update_interval: int = 10  # Time in seconds
    token_refresh_threshold: int = 30  # Time in seconds before token expiry to refresh

settings = Settings()
