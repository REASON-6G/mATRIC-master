from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

subs_bp = Blueprint("subscriptions", __name__)

@subs_bp.route("/", methods=["GET"])
@jwt_required()
def list_subscriptions():
    return jsonify([])

@subs_bp.route("/<sub_id>", methods=["GET"])
@jwt_required()
def get_subscription(sub_id):
    return jsonify({"id": sub_id})

@subs_bp.route("/", methods=["POST"])
@jwt_required()
def create_subscription():
    data = request.get_json()
    return jsonify(data), 201

@subs_bp.route("/<sub_id>", methods=["PUT"])
@jwt_required()
def update_subscription(sub_id):
    data = request.get_json()
    return jsonify({"id": sub_id, **data})

@subs_bp.route("/<sub_id>", methods=["DELETE"])
@jwt_required()
def delete_subscription(sub_id):
    return jsonify({"id": sub_id}), 204
