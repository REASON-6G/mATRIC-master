from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

topics_bp = Blueprint("topics", __name__)

@topics_bp.route("/", methods=["GET"])
def list_topics():
    return jsonify([])

@topics_bp.route("/<topic_id>", methods=["GET"])
def get_topic(topic_id):
    return jsonify({"id": topic_id})

@topics_bp.route("/", methods=["POST"])
def create_topic():
    data = request.get_json()
    return jsonify(data), 201

@topics_bp.route("/<topic_id>", methods=["PUT"])
def update_topic(topic_id):
    data = request.get_json()
    return jsonify({"id": topic_id, **data})

@topics_bp.route("/<topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    return jsonify({"id": topic_id}), 204
