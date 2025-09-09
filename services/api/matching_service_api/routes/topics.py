from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
import logging
import pika
from datetime import datetime
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from matching_service_api.utils import handle_exception, mongo_client, role_required
from matching_service_api.models import TopicModel, PublisherResponse

topics_bp = Blueprint("topics", __name__)


# ---- Helpers ----
def serialize_topic(topic: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    topic = dict(topic)  # avoid mutating original
    topic["id"] = str(topic["_id"])
    topic.pop("_id", None)

    # Convert datetime fields to ISO format
    for field in ["created_at", "updated_at"]:
        if field in topic and isinstance(topic[field], datetime):
            topic[field] = topic[field].isoformat()

    # Include publisher info if available
    publisher_id = topic.get("publisher_id")
    if publisher_id:
        pub_doc = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
        if pub_doc:
            topic["publisher"] = PublisherResponse(**pub_doc, id=str(pub_doc["_id"])).model_dump()
        else:
            topic["publisher"] = None
    else:
        topic["publisher"] = None

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
@role_required("user", "admin")
def create_topic():
    """Create a new topic, optionally associate a publisher, and create a RabbitMQ queue"""
    try:
        data = request.get_json() or {}
        topic_data = TopicModel(**data)
        topic_dict = topic_data.model_dump()

        publisher_id = topic_dict.get("publisher_id")
        if publisher_id:
            # Check publisher exists
            publisher = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
            if not publisher:
                return jsonify({"error": f"Publisher with id {publisher_id} not found"}), 404
            # Ensure publisher not already assigned
            existing = mongo_client.db.topics.find_one({"publisher_id": publisher_id})
            if existing:
                return jsonify({"error": "Publisher already assigned to another topic"}), 409

        # Insert into MongoDB
        try:
            result = mongo_client.db.topics.insert_one(topic_dict)
        except DuplicateKeyError:
            return jsonify({"error": f"Topic '{topic_dict['topic']}' already exists"}), 409

        topic_id = str(result.inserted_id)

        # Create RabbitMQ queue
        queue_name = topic_dict["topic"]
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            connection.close()
        except Exception as e:
            logging.error(f"Failed to create RabbitMQ queue '{queue_name}': {e}")

        return jsonify({"id": topic_id}), 201

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to create topic", status_code=500)


@topics_bp.route("/<topic_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_topic(topic_id):
    """Update a topic (partial updates allowed), optionally assign/change publisher"""
    try:
        data = request.get_json() or {}
        update_data = {}
        if "topic" in data:
            update_data["topic"] = data["topic"]
        if "description" in data:
            update_data["description"] = data["description"]

        if "publisher_id" in data:
            publisher_id = data["publisher_id"]
            if publisher_id:
                # Check publisher exists
                publisher = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
                if not publisher:
                    return jsonify({"error": f"Publisher with id {publisher_id} not found"}), 404
                # Ensure publisher not already assigned to another topic
                existing = mongo_client.db.topics.find_one({
                    "publisher_id": publisher_id,
                    "_id": {"$ne": ObjectId(topic_id)}
                })
                if existing:
                    return jsonify({"error": "Publisher already assigned to another topic"}), 409
            update_data["publisher_id"] = publisher_id

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
@role_required("user", "admin")
def delete_topic(topic_id):
    """Delete a topic"""
    try:
        result = mongo_client.db.topics.delete_one({"_id": ObjectId(topic_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Topic not found"}), 404
        return jsonify({"id": topic_id, "deleted": True}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to delete topic", status_code=500)
