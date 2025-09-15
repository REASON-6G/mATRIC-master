from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from pydantic import ValidationError
from pymongo.errors import PyMongoError

from matching_service_api.utils import mongo_client, handle_exception, role_required
from matching_service_api.models import UserModel, UserResponse, mongo_to_dict
from matching_service_api.config import Config

auth_bp = Blueprint("auth", __name__)


# --- Registration endpoint ---
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}

        # Enforce allowed roles
        allowed_roles = {"user", "agent"}
        role = data.get("role", "user").lower()
        if role not in allowed_roles:
            role = "user"

        # Validate input with Pydantic
        user_data = UserModel(
            username=data.get("username"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            role=role,
            created_at=datetime.utcnow()
        )

        password = data.get("password")
        if not password or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        if mongo_client.db.users.find_one({"username": user_data.username}):
            return jsonify({"error": "Username already exists"}), 409

        hashed_pw = generate_password_hash(password)
        user_dict = user_data.dict()
        user_dict["password_hash"] = hashed_pw
        result = mongo_client.db.users.insert_one(user_dict)

        return jsonify({"id": str(result.inserted_id)}), 201

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except PyMongoError as e:
        return handle_exception(e, status=500, msg="Database error")
    except Exception as e:
        return handle_exception(e)


# --- Login endpoint ---
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = mongo_client.db.users.find_one({"username": username})
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        additional_claims = {"role": user.get("role", "user")}
        access = create_access_token(
            identity=str(user["_id"]),
            expires_delta=timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES),
            additional_claims=additional_claims
        )
        refresh = create_refresh_token(
            identity=str(user["_id"]),
            additional_claims=additional_claims
        )
        return jsonify(access_token=access, refresh_token=refresh)

    except PyMongoError as e:
        return handle_exception(e, status=500, msg="Database error")
    except Exception as e:
        return handle_exception(e)


# --- Refresh token endpoint ---
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")

        access = create_access_token(
            identity=identity,
            expires_delta=timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES),
            additional_claims={"role": role}
        )
        return jsonify({"access_token": access}), 200

    except Exception as e:
        return handle_exception(e)


# --- Current user info ---
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def me():
    try:
        user_id = get_jwt_identity()
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return jsonify({"error": "Invalid user ID in token"}), 400

        user = mongo_client.db.users.find_one({"_id": obj_id}, {"password_hash": 0})
        if not user:
            return jsonify({"error": "User not found"}), 404

        response = UserResponse(**mongo_to_dict(user)).dict()
        return jsonify(response), 200

    except PyMongoError as e:
        return handle_exception(e, status=500, msg="Database error")
    except Exception as e:
        return handle_exception(e)


# --- Change password ---
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        old_password = data.get("old_password")
        new_password = data.get("new_password")
        if not old_password or not new_password:
            return jsonify({"error": "Old and new password are required"}), 400
        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters"}), 400

        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return jsonify({"error": "Invalid user ID"}), 400

        user = mongo_client.db.users.find_one({"_id": obj_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not check_password_hash(user["password_hash"], old_password):
            return jsonify({"error": "Old password is incorrect"}), 401

        hashed_pw = generate_password_hash(new_password)
        mongo_client.db.users.update_one({"_id": obj_id}, {"$set": {"password_hash": hashed_pw}})

        return jsonify({"message": "Password changed successfully"}), 200

    except PyMongoError as e:
        return handle_exception(e, status=500, msg="Database error")
    except Exception as e:
        return handle_exception(e)


# --- Validate token for publisher/subscriber ---
@auth_bp.route("/validate", methods=["POST"])
def validate_token():
    try:
        # Extract token from header or body
        auth_header = request.headers.get("Authorization", "")
        api_token = auth_header.split(" ", 1)[1].strip() if auth_header.startswith("Bearer ") else None
        if not api_token:
            data = request.get_json(silent=True) or {}
            api_token = data.get("api_token") or data.get("token")
        if not api_token:
            return jsonify({"error": "Token is required"}), 400

        # Check publishers
        publisher = mongo_client.db.publishers.find_one({"api_token": api_token})
        if publisher:
            identity = str(publisher["_id"])
            claims = {"role": "publisher"}
        else:
            # Check subscribers
            subscriber = mongo_client.db.subscribers.find_one({"api_token": api_token})
            if subscriber:
                identity = str(subscriber["_id"])
                claims = {"role": "subscriber"}
            else:
                return jsonify({"error": "Invalid token"}), 401

        access = create_access_token(identity=identity, expires_delta=timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES), additional_claims=claims)
        refresh = create_refresh_token(identity=identity, additional_claims=claims)

        return jsonify({
            "access_token": access,
            "refresh_token": refresh,
            "id": identity,
            "role": claims["role"],
            "name": publisher.get("name") if publisher else subscriber.get("name")
        }), 200

    except Exception as e:
        return handle_exception(e, status_code=500, msg="Failed to validate token")
