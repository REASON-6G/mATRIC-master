from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import logging
import pika
from datetime import datetime
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from matching_service_api.utils import handle_exception, mongo_client, role_required, is_admin
from matching_service_api.models import TopicModel, TopicCreateRequest, mongo_to_dict

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
        publisher_doc.get("country", "unknown").lower(),
        publisher_doc.get("city", "unknown").lower(),
        publisher_doc.get("organisation", "unknown").lower(),
        topic_doc.get("device_name").lower(),
        topic_doc.get("device_type").lower(),
        topic_doc.get("component").lower(),
        topic_doc.get("subject").lower()

    ]
    return "/".join(parts)


def check_topic_ownership(topic: dict, user_id: str):
    """Return True if current user owns the topic, False otherwise"""
    if is_admin():
        return True

    publisher_id = topic.get("publisher_id")
    if publisher_id:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
        if not pub:
            raise ValueError("Publisher not found")
        return pub.get("user_id") == user_id
    else:
        return topic.get("user_id") == user_id


# ---- Routes ----
@topics_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_topics():
    """List all topics (everyone can see)."""
    try:
        topics = list(mongo_client.db.topics.find())
        return jsonify([serialize_topic(t) for t in topics]), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list topics", status_code=500)
    
@topics_bp.route("/mine", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_my_topics():
    """List only the current user's topics.c"""
    try:
        user_id = str(get_jwt_identity())
        topics = list(mongo_client.db.topics.find({"user_id": user_id}))
        return jsonify([serialize_topic(t) for t in topics]), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list user topics", status_code=500)


@topics_bp.route("/<topic_id>", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_topic(topic_id):
    try:
        topic = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
        if not topic:
            return jsonify({"error": "Topic not found"}), 404

        user_id = str(get_jwt_identity())
        if not check_topic_ownership(topic, user_id):
            return jsonify({"error": "Not authorized to view this topic"}), 403

        return jsonify(serialize_topic(topic)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return handle_exception(e, msg="Failed to fetch topic", status_code=500)


@topics_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def create_topic():
    try:
        data = request.get_json() or {}
        topic_data = TopicCreateRequest(**data)
        topic_dict = topic_data.model_dump()

        publisher_id = topic_dict.get("publisher_id")
        if not publisher_id:
            return jsonify({"error": "publisher_id is required"}), 400

        # Validate publisher exists + ownership
        publisher = mongo_client.db.publishers.find_one({"_id": ObjectId(publisher_id)})
        if not publisher:
            return jsonify({"error": f"Publisher with id {publisher_id} not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and publisher.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to create topic under this publisher"}), 403

        # Build the full topic name
        topic_dict["topic"] = build_full_topic(topic_dict, publisher)
        topic_dict["created_at"] = datetime.utcnow()
        topic_dict["user_id"] = user_id

        # Insert into Mongo
        try:
            result = mongo_client.db.topics.insert_one(topic_dict)
        except DuplicateKeyError:
            return jsonify({"error": f"Topic '{topic_dict['topic']}' already exists"}), 409

        # Create RabbitMQ queue (non-blocking error)
        queue_name = topic_dict["topic"]
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
            channel = conn.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            conn.close()
        except Exception as e:
            logging.error(f"Failed to create RabbitMQ queue '{queue_name}': {e}")

        return jsonify({"id": str(result.inserted_id)}), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to create topic", status_code=500)



@topics_bp.route("/<topic_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_topic(topic_id):
    try:
        data = request.get_json() or {}
        update_data = {k: data[k] for k in ["description", "device_name", "device_type", "component", "subject"] if k in data}

        topic = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
        if not topic:
            return jsonify({"error": "Topic not found"}), 404

        user_id = str(get_jwt_identity())
        if not check_topic_ownership(topic, user_id):
            return jsonify({"error": "Not authorized to update this topic"}), 403

        # Handle publisher reassignment
        if "publisher_id" in data:
            new_pub_id = data["publisher_id"]
            new_pub = mongo_client.db.publishers.find_one({"_id": ObjectId(new_pub_id)})
            if not new_pub:
                return jsonify({"error": f"Publisher {new_pub_id} not found"}), 404
            if not is_admin() and new_pub.get("user_id") != user_id:
                return jsonify({"error": "Not authorized to assign to this publisher"}), 403
            update_data["publisher_id"] = new_pub_id
            update_data["topic"] = build_full_topic({**topic, **update_data}, new_pub)

        if update_data:
            mongo_client.db.topics.update_one({"_id": ObjectId(topic_id)}, {"$set": update_data})
            updated = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
            return jsonify(serialize_topic(updated)), 200

        return jsonify({"error": "No valid fields to update"}), 400
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to update topic", status_code=500)


@topics_bp.route("/<topic_id>", methods=["DELETE"])
@jwt_required()
@role_required("user", "admin")
def delete_topic(topic_id):
    try:
        topic = mongo_client.db.topics.find_one({"_id": ObjectId(topic_id)})
        if not topic:
            return jsonify({"error": "Topic not found"}), 404

        user_id = str(get_jwt_identity())
        if not check_topic_ownership(topic, user_id):
            return jsonify({"error": "Not authorized to delete this topic"}), 403

        mongo_client.db.topics.delete_one({"_id": ObjectId(topic_id)})
        return jsonify({"id": topic_id, "deleted": True}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to delete topic", status_code=500)