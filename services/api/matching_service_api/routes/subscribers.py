import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import ValidationError

from matching_service_api.utils import mongo_client, handle_exception, role_required, is_admin
from matching_service_api.models import SubscriberModel, SubscriberResponse, SubscriberUpdateRequest, mongo_to_dict

subs_bp = Blueprint("subscribers", __name__)


def serialize_subscriber(sub: dict) -> dict:
    """Convert Mongo dict to SubscriberModel dict."""
    sub = mongo_to_dict(sub)
    return SubscriberResponse(**sub).dict()


@subs_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_subscribers():
    """List all subscribers."""
    try:
        user_id = str(get_jwt_identity())
        cursor = mongo_client.db.subscribers.find({"user_id": user_id}).sort("created_at", -1)
        subs = [serialize_subscriber(sub) for sub in cursor]
        return jsonify(subs), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/<sub_id>", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_subscriber(sub_id):
    try:
        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscriber not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and sub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to view this subscriber"}), 403

        return jsonify(serialize_subscriber(sub)), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def create_subscriber():
    """Create a new subscriber and generate an API token."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert string fields to lowercase
        for field in ["name", "description"]:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        data["api_token"] = secrets.token_urlsafe(32)
        data["created_at"] = datetime.now(timezone.utc)
        data["user_id"] = str(get_jwt_identity())

        try:
            subscriber = SubscriberModel(**data)
            sub_dict = subscriber.dict()
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        result = mongo_client.db.subscribers.insert_one(sub_dict)
        sub_dict["_id"] = result.inserted_id

        sub = mongo_client.db.subscribers.find_one({"_id": sub_dict["_id"]})
        return jsonify(serialize_subscriber(sub)), 201

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/<sub_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_subscriber(sub_id):
    """Update an existing subscriber."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        for field in ["name", "description"]:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        try:
            subscriber = SubscriberUpdateRequest(**data)
            update_data = subscriber.dict(exclude_unset=True)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscriber not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and sub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to update this subscriber"}), 403

        update_data["updated_at"] = datetime.now(timezone.utc)
        result = mongo_client.db.subscribers.update_one(
            {"_id": ObjectId(sub_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Subscriber not found"}), 404

        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        return jsonify(serialize_subscriber(sub)), 200

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/<sub_id>", methods=["DELETE"])
@jwt_required()
@role_required("user", "admin")
def delete_subscriber(sub_id):
    try:
        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscriber not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and sub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to delete this subscriber"}), 403

        mongo_client.db.subscribers.delete_one({"_id": ObjectId(sub_id)})
        return jsonify({"id": sub_id, "deleted": True}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/<sub_id>/token/regenerate", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def regenerate_subscriber_token(sub_id):
    try:
        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscriber not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and sub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to regenerate token"}), 403

        new_token = secrets.token_urlsafe(32)
        mongo_client.db.subscribers.update_one(
            {"_id": ObjectId(sub_id)}, {"$set": {"api_token": new_token}}
        )

        return jsonify({"api_token": new_token}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@subs_bp.route("/<sub_id>/token", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_subscriber_token(sub_id):
    try:
        sub = mongo_client.db.subscribers.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscriber not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and sub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to view token"}), 403

        return jsonify({"api_token": sub.get("api_token")}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
