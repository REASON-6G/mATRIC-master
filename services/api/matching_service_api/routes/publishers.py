from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError

from matching_service_api.utils import mongo_client, handle_exception
from matching_service_api.models import PublisherModel

pubs_bp = Blueprint("publishers", __name__)


@pubs_bp.route("/", methods=["GET"])
@jwt_required()
def list_publishers():
    """
    List all publishers (limit 50).
    """
    try:
        cursor = mongo_client.db.publishers.find().sort("created_at", -1).limit(50)
        pubs = []
        for pub in cursor:
            pub["_id"] = str(pub["_id"])
            pubs.append(pub)
        return jsonify(pubs), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["GET"])
@jwt_required()
def get_publisher(pub_id):
    """
    Get a publisher by ID.
    """
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        pub["_id"] = str(pub["_id"])
        return jsonify(pub), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/", methods=["POST"])
@jwt_required()
def create_publisher():
    """
    Create a new publisher.
    """
    try:
        data = request.get_json() or {}
        if not data.get("name") or not data.get("location"):
            return jsonify({"error": "Missing required fields: name, location"}), 400

        # Validate with Pydantic
        try:
            publisher = PublisherModel(**data)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        doc = publisher.dict()
        doc["created_at"] = datetime.utcnow()

        result = mongo_client.db.publishers.insert_one(doc)
        return jsonify({"id": str(result.inserted_id)}), 201
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["PUT"])
@jwt_required()
def update_publisher(pub_id):
    """
    Update an existing publisher.
    """
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        # Optional: validate fields with Pydantic (partial update)
        try:
            publisher = PublisherModel(**data)
            update_data = publisher.dict(exclude_unset=True)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        result = mongo_client.db.publishers.update_one(
            {"_id": ObjectId(pub_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Publisher not found"}), 404

        return jsonify({"id": pub_id, "updated": True}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["DELETE"])
@jwt_required()
def delete_publisher(pub_id):
    """
    Delete a publisher.
    """
    try:
        result = mongo_client.db.publishers.delete_one({"_id": ObjectId(pub_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Publisher not found"}), 404

        return jsonify({"id": pub_id, "deleted": True}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
