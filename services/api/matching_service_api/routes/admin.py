from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/", methods=["GET"])
def list_metrics():
    # Return admin config
    return jsonify([])
