from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
import logging
import pika
from datetime import datetime
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from matching_service_api.utils import handle_exception, mongo_client, role_required
from matching_service_api.models import TopicModel, TopicCreateRequest, PublisherResponse, mongo_to_dict

topics_bp = Blueprint("topics", __name__)


# ---- Helpers ----
def serialize_topic(topic: dict) -> dict:
    """Serialize topic with publisher info and full_topic field."""
    t_dict = mongo_to_dict(topic)
    publisher = None
    full_topic = None

    if t_dict.get("publisher_id"):
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(t_dict["publisher_id"])})
        if pub:
            pub_dict = mongo_to_dict(pub)
            publisher = pub_dict
            parts = [
                pub_dict.get("country"),
                pub_dict.get("city"),
                pub_dict.get("organisation"),
                t_dict.get("topic"),
            ]
            # Filter out None/empty strings
            full_topic = "/".join(parts)
            t_dict["country"] = pub_dict.get("country")
            t_dict["city"] = pub_dict.get("city")
            t_dict["organisation"] = pub_dict.get("organisation")

    t_dict["publisher"] = publisher
    t_dict["full_topic"] = full_topic or t_dict["topic"]
    return t_dict


def build_full_topic(topic_doc: dict, publisher_doc: dict) -> str:
    """
    Combine publisher fields + topic string.
    """
    parts = [
        publisher_doc.get("country"),
        publisher_doc.get("city"),
        publisher_doc.get("organisation"),
        topic_doc.get("device_name"),
        topic_doc.get("device_type"),
        topic_doc.get("component"),
        topic_doc.get("subject")

    ]
    return "/".join(parts)


# ---- Routes ----
@topics_bp.route("/", methods=["GET"])
@jwt_required()
def list_topics():
    """List all topics with publisher prefix"""
    try:
        topics = list(mongo_client.db.topics.find())
        topics = [serialize_topic(t) for t in topics]
        return jsonify(topics), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list topics", status_code=500)


@topics_bp.route("/<topic_id>", methods=["GET"])
@jwt_required()
def get_topic(topic_id):
    """Get a topic by ID (with publisher prefix)"""
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
    """Create a new topic (publisher required), and create a RabbitMQ queue"""
    try:
        data = request.get_json() or {}
        print(data)
        topic_data = TopicCreateRequest(**data)
        topic_dict = topic_data.model_dump()

        publisher_id = topic_dict.get("publisher_id")
        if not publisher_id:
            return jsonify({"error": "publisher_id is required"}), 400

        # Validate publisher exists
        publisher = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
        if not publisher:
            return jsonify({"error": f"Publisher with id {publisher_id} not found"}), 404
        
        # Build the full topic name
        topic_dict["topic"] = build_full_topic(topic_dict, publisher)

        # Insert into MongoDB
        try:
            result = mongo_client.db.topics.insert_one(topic_dict)
        except DuplicateKeyError:
            return jsonify({"error": f"Topic '{topic_dict['topic']}' already exists"}), 409

        topic_id = str(result.inserted_id)

        # Create RabbitMQ queue (still relative name)
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
        print(e)
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
        print(data)
        update_data = {}

        # Updatable fields
        for field in ["topic", "description", "device_name", "device_type", "component", "subject"]:
            if field in data:
                update_data[field] = data[field]

        # Handle publisher change
        if "publisher_id" in data:
            publisher_id = data["publisher_id"]
            if publisher_id:
                # Check publisher exists
                publisher = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
                if not publisher:
                    return jsonify({"error": f"Publisher with id {publisher_id} not found"}), 404
            update_data["publisher_id"] = publisher_id

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = mongo_client.db.topics.update_one(
            {"_id": ObjectId(topic_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Topic not found"}), 404

        updated = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
        return jsonify(serialize_topic(updated)), 200

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
