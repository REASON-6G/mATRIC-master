from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask import jsonify, current_app

mongo_client = PyMongo()
jwt_client = JWTManager()

def handle_exception(e, status_code=500, msg="Internal server error"):
    """
    Global exception handler for all routes.
    Logs the error and returns a JSON response.
    """
    current_app.logger.error(f"[{type(e).__name__}] {e}")
    return jsonify({"error": msg}), status_code