from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
import requests
import logging

from matching_service_api.utils import mongo_client, handle_exception, role_required
from matching_service_api.models import EmulatorModel

emulators_bp = Blueprint("emulators", __name__)


# ---- Helpers ----
def serialize_emulator(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
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
    """List all emulators for current user; admins see all"""
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
    """Create a new emulator"""
    try:
        data = request.get_json() or {}
        data["owner_id"] = get_jwt_identity()
        # Include publisher_id if provided
        publisher_id = data.get("publisher_id")
        if publisher_id:
            data["publisher_id"] = publisher_id

        emulator_data = EmulatorModel(**data)
        emulator_dict = emulator_data.model_dump()
        try:
            result = mongo_client.db.emulators.insert_one(emulator_dict)
        except DuplicateKeyError:
            return jsonify({"error": f"Emulator '{emulator_dict['name']}' already exists"}), 409
        return jsonify({"id": str(result.inserted_id)}), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
    except Exception as e:
        return handle_exception(e, msg="Failed to create emulator", status_code=500)


@emulators_bp.route("/<emulator_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_emulator(emulator_id):
    """Update emulator fields (e.g., schema, interval, publisher)"""
    try:
        data = request.get_json() or {}
        emulator = mongo_client.db.emulators.find_one({"_id": ObjectId(emulator_id)})
        if not emulator:
            return jsonify({"error": "Emulator not found"}), 404
        check_owner(emulator)

        update_data = {}
        for field in ["name", "topic", "schema", "interval", "running", "publisher_id"]:
            if field in data:
                update_data[field] = data[field]
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        update_data["updated_at"] = datetime.utcnow()

        mongo_client.db.emulators.update_one({"_id": ObjectId(emulator_id)}, {"$set": update_data})
        emulator.update(update_data)
        return jsonify(serialize_emulator(emulator)), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422
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
