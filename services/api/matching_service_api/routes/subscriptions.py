from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
import logging

from matching_service_api.utils import handle_exception, mongo_client
from matching_service_api.models import SubscriptionModel

subs_bp = Blueprint("subscriptions", __name__)


# ---- Helpers ----
def serialize_subscription(sub):
    """Convert MongoDB document to JSON-serializable dict"""
    sub["_id"] = str(sub["_id"])
    return sub


# ---- Routes ----
@subs_bp.route("/", methods=["GET"])
@jwt_required()
def list_subscriptions():
    """List subscriptions for current user"""
    try:
        user_id = get_jwt_identity()
        subs = list(mongo_client.db.subscriptions.find({"user_id": user_id}))
        subs = [serialize_subscription(s) for s in subs]
        return jsonify(subs), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list subscriptions", status_code=500)


@subs_bp.route("/<sub_id>", methods=["GET"])
@jwt_required()
def get_subscription(sub_id):
    """Get subscription by ID"""
    try:
        sub = mongo_client.db.subscriptions.find_one({"_id": ObjectId(sub_id)})
        if not sub:
            return jsonify({"error": "Subscription not found"}), 404
        return jsonify(serialize_subscription(sub)), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to fetch subscription", status_code=500)


@subs_bp.route("/", methods=["POST"])
@jwt_required()
def create_subscription():
    """Create a new subscription for the current user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        # Validate with Pydantic
        try:
            sub_data = SubscriptionModel(**data)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        sub_dict = sub_data.model_dump()
        sub_dict["user_id"] = user_id

        try:
            result = mongo_client.db.subscriptions.insert_one(sub_dict)
            queue_name = sub_dict["queue"]
            return jsonify(sub_dict), 201
        except DuplicateKeyError:
            return jsonify({"warning": "Subscription already exists"}), 409

    except Exception as e:
        return handle_exception(e, msg="Failed to create subscription", status_code=500)


@subs_bp.route("/<sub_id>", methods=["PUT"])
@jwt_required()
def update_subscription(sub_id):
    """Update a subscription (partial updates allowed)"""
    try:
        data = request.get_json() or {}
        update_data = {}

        if "topic_filter" in data:
            update_data["topic_filter"] = data["topic_filter"]
        if "active" in data:
            update_data["active"] = bool(data["active"])

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = mongo_client.db.subscriptions.update_one(
            {"_id": ObjectId(sub_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Subscription not found"}), 404

        return jsonify({"id": sub_id, **update_data}), 200

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to update subscription", status_code=500)


@subs_bp.route("/<sub_id>", methods=["DELETE"])
@jwt_required()
def delete_subscription(sub_id):
    """Delete a subscription"""
    try:
        result = mongo_client.db.subscriptions.delete_one({"_id": ObjectId(sub_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Subscription not found"}), 404
        return jsonify({"id": sub_id, "deleted": True}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to delete subscription", status_code=500)
