from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from pydantic import ValidationError
from matching_service_api.utils import mongo_client
from matching_service_api.models import UserModel

auth_bp = Blueprint("auth", __name__)

# --- Registration endpoint ---
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user (public endpoint)
    Expected JSON: { "username": str, "password": str, "email": str, "full_name": str (optional) }
    """
    data = request.get_json() or {}

    # Enforce allowed roles
    allowed_roles = {"user", "agent"}
    role = data.get("role", "user").lower()
    if role not in allowed_roles:
        role = "user"  # default to user if invalid

    # Validate input with Pydantic (exclude password for validation)
    try:
        user_data = UserModel(
            username=data.get("username"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            role=role,
            created_at=datetime.utcnow()
        )
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    # Validate password
    password = data.get("password")
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check for existing username
    if mongo_client.db.users.find_one({"username": user_data.username}):
        return jsonify({"error": "Username already exists"}), 409

    # Hash password
    hashed_pw = generate_password_hash(password)

    # Insert user
    user_dict = user_data.dict()
    user_dict["password_hash"] = hashed_pw
    result = mongo_client.db.users.insert_one(user_dict)

    return jsonify({"id": str(result.inserted_id)}), 201


# --- Login ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = mongo_client.db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(minutes=15))
    refresh = create_refresh_token(identity=str(user["_id"]))
    return jsonify(access_token=access, refresh_token=refresh)


# --- Refresh ---
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access = create_access_token(identity=user_id, expires_delta=timedelta(minutes=15))
    return jsonify(access_token=access)


# --- Current user info ---
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user ID in token"}), 400

    user = mongo_client.db.users.find_one({"_id": obj_id}, {"password_hash": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user["_id"] = str(user["_id"])
    return jsonify(user)
