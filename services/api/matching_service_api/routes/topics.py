from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from pydantic import ValidationError

from matching_service_api.utils import handle_exception, mongo_client
from matching_service_api.models import TopicModel

topics_bp = Blueprint("topics", __name__)


# ---- Helpers ----
def serialize_topic(topic):
    """Convert MongoDB document to JSON-serializable dict"""
    topic["_id"] = str(topic["_id"])
    return topic


# ---- Routes ----
@topics_bp.route("/", methods=["GET"])
@jwt_required()
def list_topics():
    """List all topics"""
    try:
        topics = list(mongo_client.db.topics.find())
        topics = [serialize_topic(t) for t in topics]
        return jsonify(topics), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list topics", status_code=500)


@topics_bp.route("/<topic_id>", methods=["GET"])
@jwt_required()
def get_topic(topic_id):
    """Get a topic by ID"""
    try:
        topic = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
        if not topic:
            return jsonify({"error": "Topic not found"}), 404
        return jsonify(serialize_topic(topic)), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to fetch topic", status_code=500)


@topics_bp.route("/", methods=["POST"])
@jwt_required()
def create_topic():
    """Create a new topic"""
    try:
        data = request.get_json() or {}
        topic_data = TopicModel(**data)
        topic_dict = topic_data.dict()
        result = mongo_client.db.topics.insert_one(topic_dict)
        return jsonify({"id": str(result.inserted_id)}), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to create topic", status_code=500)


@topics_bp.route("/<topic_id>", methods=["PUT"])
@jwt_required()
def update_topic(topic_id):
    """Update a topic (partial updates allowed)"""
    try:
        data = request.get_json() or {}

        update_data = {}
        if "topic" in data:
            update_data["topic"] = data["topic"]
        if "description" in data:
            update_data["description"] = data["description"]

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = mongo_client.db.topics.update_one(
            {"_id": ObjectId(topic_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Topic not found"}), 404

        return jsonify({"id": topic_id, **update_data}), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to update topic", status_code=500)


@topics_bp.route("/<topic_id>", methods=["DELETE"])
@jwt_required()
def delete_topic(topic_id):
    """Delete a topic"""
    try:
        result = mongo_client.db.topics.delete_one({"_id": ObjectId(topic_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Topic not found"}), 404
        return jsonify({"id": topic_id, "deleted": True}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to delete topic", status_code=500)
