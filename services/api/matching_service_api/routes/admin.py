from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from pymongo.errors import PyMongoError

from matching_service_api.utils import mongo_client, handle_exception
from matching_service_api.models import mongo_to_dict, MetricResponse

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/metrics", methods=["GET"])
@jwt_required()
def list_metrics():
    """
    Return all metrics stored in MongoDB.
    Each metric is normalized to JSON-safe format (id as string, datetime as ISO).
    """
    try:
        metrics = list(mongo_client.db.metrics.find({}))
        response = [MetricResponse(**mongo_to_dict(m)).dict() for m in metrics]
        return jsonify(response), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error fetching metrics", status=500)
    except Exception as e:
        return handle_exception(e, msg="Failed to list metrics", status=500)
