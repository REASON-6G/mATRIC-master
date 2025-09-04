from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

pubs_bp = Blueprint("publishers", __name__)

@pubs_bp.route("/", methods=["GET"])
def list_publishers():
    return jsonify([])

@pubs_bp.route("/<pub_id>", methods=["GET"])
def get_publisher(pub_id):
    return jsonify({"id": pub_id})

@pubs_bp.route("/", methods=["POST"])
def create_publisher():
    data = request.get_json()
    return jsonify(data), 201

@pubs_bp.route("/<pub_id>", methods=["PUT"])
def update_publisher(pub_id):
    data = request.get_json()
    return jsonify({"id": pub_id, **data})

@pubs_bp.route("/<pub_id>", methods=["DELETE"])
def delete_publisher(pub_id):
    return jsonify({"id": pub_id}), 204
