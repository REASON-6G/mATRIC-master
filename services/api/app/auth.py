from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash
from datetime import timedelta
from . import mongo

auth_bp = Blueprint("auth", __name__)

# Example: Mongo "users" collection documents:
# { "_id": ObjectId, "username": str, "password_hash": str, "role": "admin"|"user" }

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = mongo.db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(minutes=15))
    refresh = create_refresh_token(identity=str(user["_id"]))
    return jsonify(access_token=access, refresh_token=refresh)

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access = create_access_token(identity=user_id, expires_delta=timedelta(minutes=15))
    return jsonify(access_token=access)

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": user_id}, {"password_hash": 0})
    return jsonify(user)
