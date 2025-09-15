from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
import requests
import logging

from matching_service_api.utils import mongo_client, handle_exception, role_required
from matching_service_api.models import EmulatorModel, EmulatorCreateRequest, EmulatorUpdateRequest

emulators_bp = Blueprint("emulators", __name__)


# ---- Helpers ----
def serialize_emulator(doc: dict) -> dict:
    if not doc:
        return {}
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()

    # Embed topic
    if "topic_id" in doc:
        topic = mongo_client.db.topics.find_one({"_id": ObjectId(doc["topic_id"])})
        if topic:
            doc["topic"] = {
                "id": str(topic["_id"]),
                "topic": topic.get("topic"),
                "description": topic.get("description"),
                "device_name": topic.get("device_name"),
                "device_type": topic.get("device_type"),
                "component": topic.get("component"),
                "subject": topic.get("subject"),
                "user_id": topic.get("user_id"),
                "publisher_id": topic.get("publisher_id"),
                "created_at": topic.get("created_at").isoformat()
                if topic.get("created_at")
                else None,
            }
    return doc



def is_admin() -> bool:
    claims = get_jwt()
    return claims.get("role") == "admin"


def check_owner(emulator: dict):
    user_id = get_jwt_identity()
    if not is_admin() and emulator.get("owner_id") != user_id:
        raise PermissionError("Not authorized to manage this emulator")


@emulators_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_emulators():
    try:
        user_id = get_jwt_identity()
        query = {} if is_admin() else {"owner_id": user_id}
        emulators = list(mongo_client.db.emulators.find(query))
        return jsonify([serialize_emulator(e) for e in emulators]), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to list emulators", status_code=500)


@emulators_bp.route("/<emulator_id>", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_emulator(emulator_id):
    """Get a single emulator"""
    try:
        emulator = mongo_client.db.emulators.find_one({"_id": ObjectId(emulator_id)})
        if not emulator:
            return jsonify({"error": "Emulator not found"}), 404
        check_owner(emulator)
        return jsonify(serialize_emulator(emulator)), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return handle_exception(e, msg="Failed to fetch emulator", status_code=500)


@emulators_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def create_emulator():
    try:
        payload = request.get_json() or {}
        payload["owner_id"] = get_jwt_identity()

        # Validate request
        emulator_req = EmulatorCreateRequest(**payload)
        emulator_data = EmulatorModel(**emulator_req.model_dump(), owner_id=payload["owner_id"])

        result = mongo_client.db.emulators.insert_one(emulator_data.model_dump())
        new_emulator = mongo_client.db.emulators.find_one({"_id": result.inserted_id})

        return jsonify(serialize_emulator(new_emulator)), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except DuplicateKeyError:
        return jsonify({"error": f"Emulator '{payload.get('name')}' already exists"}), 409
    except Exception as e:
        return handle_exception(e, msg="Failed to create emulator", status_code=500)


@emulators_bp.route("/<emulator_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_emulator(emulator_id):
    try:
        payload = request.get_json() or {}
        emulator_req = EmulatorUpdateRequest(**payload)

        emulator = mongo_client.db.emulators.find_one({"_id": ObjectId(emulator_id)})
        if not emulator:
            return jsonify({"error": "Emulator not found"}), 404
        check_owner(emulator)

        update_data = emulator_req.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        mongo_client.db.emulators.update_one({"_id": ObjectId(emulator_id)}, {"$set": update_data})
        updated = mongo_client.db.emulators.find_one({"_id": ObjectId(emulator_id)})

        return jsonify(serialize_emulator(updated)), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return handle_exception(e, msg="Failed to update emulator", status_code=500)



@emulators_bp.route("/<emulator_id>", methods=["DELETE"])
@jwt_required()
@role_required("user", "admin")
def delete_emulator(emulator_id):
    """Delete an emulator"""
    try:
        emulator = mongo_client.db.emulators.find_one({"_id": ObjectId(emulator_id)})
        if not emulator:
            return jsonify({"error": "Emulator not found"}), 404
        check_owner(emulator)

        mongo_client.db.emulators.delete_one({"_id": ObjectId(emulator_id)})
        return jsonify({"id": emulator_id, "deleted": True}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return handle_exception(e, msg="Failed to delete emulator", status_code=500)
