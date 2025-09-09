from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from influxdb_client import InfluxDBClient

from matching_service_api.utils import mongo_client, handle_exception, ADMIN_CONFIG_CACHE, INFLUX_CLIENT_LOCK

admin_bp = Blueprint("admin", __name__)

# ---------------------------
# Helpers
# ---------------------------
def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        from flask import abort
        abort(403, description="Admin privileges required")


# ---------------------------
# Get all config
# ---------------------------
@admin_bp.route("/config", methods=["GET"])
@jwt_required()
def get_config():
    try:
        admin_required()
        # Fetch the admin config document, exclude _id
        result = mongo_client.db.config.find_one({"_id": "admin_config"}, {"_id": 0})
        if not result:
            return jsonify({}), 200
        return jsonify(result), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error", status_code=500)
    except Exception as e:
        return handle_exception(e)


# ---------------------------
# Update config
# ---------------------------
@admin_bp.route("/config", methods=["PUT"])
@jwt_required()
def update_config():
    """
    Update a single config key in the admin config document.
    Ignores '_id' if accidentally included in payload.
    Updates the global cache and refreshes Influx client if needed.
    """
    try:
        admin_required()
        data = request.get_json() or {}
        key = data.get("key")
        value = data.get("value")

        if not key or value is None or key == "_id":
            return jsonify({"error": "Invalid key or value"}), 400

        # Update MongoDB
        mongo_client.db.config.update_one(
            {"_id": "admin_config"},
            {"$set": {key: value, "updated_at": datetime.now(timezone.utc)}},
            upsert=True
        )

        # Update global cache
        ADMIN_CONFIG_CACHE[key] = value

        # ---- Refresh Influx client if relevant ----
        if key in ("influx_bucket", "influx_token", "influx_url", "influx_org"):
            from matching_service_api.utils import _influx_client, _write_api
            with INFLUX_CLIENT_LOCK:
                _influx_client = InfluxDBClient(
                    url=ADMIN_CONFIG_CACHE.get("influx_url"),
                    token=ADMIN_CONFIG_CACHE.get("influx_token"),
                    org=ADMIN_CONFIG_CACHE.get("influx_org")
                )
                _write_api = _influx_client.write_api()

        return jsonify({key: value}), 200

    except PyMongoError as e:
        return handle_exception(e, msg="Database error", status_code=500)
    except Exception as e:
        return handle_exception(e)

