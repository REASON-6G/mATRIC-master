from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from pymongo.errors import PyMongoError

from matching_service_api.utils import mongo_client, handle_exception
from matching_service_api.models import mongo_to_dict

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/", methods=["GET"])
@jwt_required()
def list_metrics():
    """
    Return the latest metrics document.
    """
    try:
        metric = mongo_client.db.metrics.find_one(sort=[("timestamp", -1)])
        if not metric:
            return jsonify({"error": "No metrics available"}), 404

        return jsonify(mongo_to_dict(metric)), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
