from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from pymongo.errors import PyMongoError
from bson import ObjectId
from pydantic import ValidationError
from datetime import datetime

from matching_service_api.utils import mongo_client, handle_exception
from matching_service_api.models import MetricModel, MetricResponse

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/", methods=["GET"])
@jwt_required()
def list_metrics():
    """
    List latest metrics (limit 50).
    """
    try:
        cursor = mongo_client.db.metrics.find().sort("timestamp", -1).limit(50)
        metrics = []
        for m in cursor:
            metrics.append(
                MetricResponse(
                    id=str(m["_id"]),
                    topic=m.get("topic"),
                    value=m.get("value"),
                    unit=m.get("unit"),
                    timestamp=m.get("timestamp"),
                ).dict()
            )
        return jsonify(metrics), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@metrics_bp.route("/<metric_id>", methods=["GET"])
@jwt_required()
def get_metric(metric_id):
    """
    Get a specific metric by ID.
    """
    try:
        metric = mongo_client.db.metrics.find_one({"_id": ObjectId(metric_id)})
        if not metric:
            return jsonify({"error": "Metric not found"}), 404

        resp = MetricResponse(
            id=str(metric["_id"]),
            topic=metric.get("topic"),
            value=metric.get("value"),
            unit=metric.get("unit"),
            timestamp=metric.get("timestamp"),
        )
        return jsonify(resp.dict()), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@metrics_bp.route("/", methods=["POST"])
@jwt_required()
def create_metric():
    """
    Create a new metric entry.
    """
    try:
        data = request.get_json() or {}

        try:
            metric = MetricModel(**data)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        doc = metric.dict()
        if not doc.get("timestamp"):
            doc["timestamp"] = datetime.utcnow()

        result = mongo_client.db.metrics.insert_one(doc)
        return jsonify({"id": str(result.inserted_id)}), 201
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@metrics_bp.route("/stats", methods=["GET"])
@jwt_required()
def metrics_stats():
    """
    Admin-only: return aggregate stats for metrics by topic.
    """
    try:
        claims = get_jwt()
        role = claims.get("role", "user")
        if role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        pipeline = [
            {
                "$group": {
                    "_id": "$topic",
                    "count": {"$sum": 1},
                    "avg_value": {"$avg": "$value"},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = list(mongo_client.db.metrics.aggregate(pipeline))
        stats = []
        for r in results:
            stats.append(
                {
                    "topic": r["_id"],
                    "count": r.get("count", 0),
                    "avg_value": r.get("avg_value"),
                    "min_value": r.get("min_value"),
                    "max_value": r.get("max_value"),
                }
            )

        return jsonify(stats), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
