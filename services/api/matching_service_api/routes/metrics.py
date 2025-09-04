from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

metrics_bp = Blueprint("metrics", __name__)

@metrics_bp.route("/", methods=["GET"])
def list_metrics():
    # Could return high-level stats or last values
    return jsonify([])

@metrics_bp.route("/<metric_id>", methods=["GET"])
def get_metric(metric_id):
    return jsonify({"id": metric_id})

@metrics_bp.route("/", methods=["POST"])
def create_metric():
    data = request.get_json()
    return jsonify(data), 201
