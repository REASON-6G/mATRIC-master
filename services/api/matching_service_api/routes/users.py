from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    # Return all users
    return jsonify([])

@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    return jsonify({"id": user_id})

@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    data = request.get_json()
    return jsonify(data), 201

@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    return jsonify({"id": user_id, **data})

@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    return jsonify({"id": user_id}), 204
