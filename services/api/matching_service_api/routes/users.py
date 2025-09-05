from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId
from pydantic import ValidationError

from matching_service_api.utils import handle_exception, mongo_client
from matching_service_api.models import UserModel

users_bp = Blueprint("users", __name__)


# ---- Helpers ----
def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"


def can_modify(user_id):
    """Return True if current user can read/update/delete the given user_id"""
    if is_admin():
        return True
    return get_jwt_identity() == str(user_id)


def serialize_user(user_doc):
    """Convert MongoDB user document to JSON-serializable dict"""
    user_doc["_id"] = str(user_doc["_id"])
    if "password_hash" in user_doc:
        user_doc.pop("password_hash")
    return user_doc


# ---- Routes ----
@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    """List all users (admin only)"""
    try:
        if not is_admin():
            return jsonify({"error": "Admin privilege required"}), 403
        users = list(mongo_client.db.users.find({}, {"password_hash": 0}))
        users = [serialize_user(u) for u in users]
        return jsonify(users), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list users", status_code=500)


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get a single user by ID"""
    try:
        if not can_modify(user_id):
            return jsonify({"error": "Access denied"}), 403
        user = mongo_client.db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(serialize_user(user)), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to fetch user", status_code=500)


@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    """Create a new user (admin only)"""
    try:
        if not is_admin():
            return jsonify({"error": "Admin privilege required"}), 403

        data = request.get_json() or {}
        role = data.get("role", "user").lower()
        if role not in {"user", "agent", "admin"}:
            role = "user"

        user_data = UserModel(
            username=data.get("username"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            role=role
        )

        password = data.get("password")
        if not password or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        if mongo_client.db.users.find_one({"username": user_data.username}):
            return jsonify({"error": "Username already exists"}), 409

        user_dict = user_data.dict()
        user_dict["password_hash"] = generate_password_hash(password)

        result = mongo_client.db.users.insert_one(user_dict)
        return jsonify({"id": str(result.inserted_id)}), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to create user", status_code=500)


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Update user (self or admin)"""
    try:
        if not can_modify(user_id):
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json() or {}
        update_data = {}

        if "username" in data:
            if mongo_client.db.users.find_one({"username": data["username"], "_id": {"$ne": ObjectId(user_id)}}):
                return jsonify({"error": "Username already exists"}), 409
            update_data["username"] = data["username"]

        if "email" in data:
            update_data["email"] = data["email"]

        if "full_name" in data:
            update_data["full_name"] = data["full_name"]

        if "role" in data and is_admin() and data["role"].lower() in {"user", "agent", "admin"}:
            update_data["role"] = data["role"].lower()

        if "password" in data:
            if len(data["password"]) < 6:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            update_data["password_hash"] = generate_password_hash(data["password"])

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = mongo_client.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"id": user_id, **update_data}), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to update user", status_code=500)


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Delete user (self or admin)"""
    try:
        if not can_modify(user_id):
            return jsonify({"error": "Access denied"}), 403

        result = mongo_client.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"id": user_id, "deleted": True}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to delete user", status_code=500)
