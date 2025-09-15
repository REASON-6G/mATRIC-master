import logging
import threading
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask import jsonify, current_app
from functools import wraps
from influxdb_client import InfluxDBClient
from matching_service_api.config import Config

mongo_client = PyMongo()
jwt_client = JWTManager()

# -------------------
# Global Influx client and lock
# -------------------
ADMIN_CONFIG_CACHE = {}
INFLUX_CLIENT_LOCK = threading.Lock()
_influx_client: InfluxDBClient | None = None
_write_api = None


def get_influx_client():
    """
    Returns a cached InfluxDBClient, recreates if config changed or first call.
    Thread-safe for Flask.
    """
    global _influx_client, _write_api

    with INFLUX_CLIENT_LOCK:
        # Ensure admin config cache is loaded
        if not ADMIN_CONFIG_CACHE:
            load_admin_config()

        influx_bucket = ADMIN_CONFIG_CACHE.get("influx_bucket")
        influx_token = ADMIN_CONFIG_CACHE.get("influx_token")
        influx_url = ADMIN_CONFIG_CACHE.get("influx_url")
        influx_org = ADMIN_CONFIG_CACHE.get("influx_org")

        if not all([influx_bucket, influx_token, influx_url, influx_org]):
            raise RuntimeError("InfluxDB configuration missing in ADMIN_CONFIG_CACHE")

        # Create client if not exists or config has changed
        if (_influx_client is None or
            _influx_client.url != influx_url or
            _influx_client.token != influx_token or
            _influx_client.org != influx_org):
            
            _influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
            _write_api = _influx_client.write_api()

        return _write_api, influx_bucket


def handle_exception(e, status_code=500, msg="Internal server error"):
    """
    Global exception handler for all routes.
    Logs the error and returns a JSON response.
    """
    current_app.logger.error(f"[{type(e).__name__}] {e}")
    return jsonify({"error": msg}), status_code


def role_required(*roles):
    """
    Restrict access to routes by role(s).
    Example:
        @role_required("publisher")
        def publish():
            ...
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "Forbidden", "required_roles": roles}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

DEFAULT_CONFIG = {
    "influx_token": Config.INFLUX_TOKEN,
    "influx_url": Config.INFLUX_URL,
    "influx_org": Config.INFLUX_ORG,
    "influx_bucket": Config.INFLUX_BUCKET,
}


def initialize_config():
    """
    Ensure the admin config document exists in MongoDB on startup
    """
    try:
        # Try to get existing config
        doc = mongo_client.db.config.find_one({"_id": "admin_config"})

        if not doc:
            # Insert default config if missing
            doc = {"_id": "admin_config", **DEFAULT_CONFIG}
            mongo_client.db.config.insert_one(doc)
            logging.info("Admin config initialized with default values.")
        else:
            logging.info("Admin config already exists.")

    except Exception as e:
        logging.exception("Failed to initialize/load admin config: %s", e)


def load_admin_config():
    """Load admin config from MongoDB into the global cache."""
    global ADMIN_CONFIG_CACHE
    if mongo_client.db is None:
        # mongo_client not initialized yet
        return
    doc = mongo_client.db.config.find_one({"_id": "admin_config"}) or {}
    doc.pop("_id", None)
    ADMIN_CONFIG_CACHE = doc


def is_admin() -> bool:
    claims = get_jwt()
    return claims.get("role") == "admin"

