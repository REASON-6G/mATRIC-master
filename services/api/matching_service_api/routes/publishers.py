import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError

from matching_service_api.utils import mongo_client, handle_exception, role_required
from matching_service_api.models import PublisherModel

pubs_bp = Blueprint("publishers", __name__)


@pubs_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_publishers():
    """
    List all publishers (limit 50).
    """
    try:
        cursor = mongo_client.db.publishers.find().sort("created_at", -1).limit(50)
        pubs = []
        for pub in cursor:
            pub["id"] = str(pub["_id"])
            pubs.append(pub)
        return jsonify(pubs), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_publisher(pub_id):
    """
    Get a publisher by ID.
    """
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        pub["id"] = str(pub["_id"])
        return jsonify(pub), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)

@pubs_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def create_publisher():
    """
    Create a new publisher and generate an API token.
    """
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Generate API token and created_at first
        data["api_token"] = secrets.token_urlsafe(32)
        data["created_at"] = datetime.utcnow()

        # Validate with Pydantic
        try:
            publisher = PublisherModel(**data)
            pub_dict = publisher.dict()
        except ValidationError as e:
            print(e.errors())
            return jsonify({"errors": e.errors()}), 422

        # Insert into DB
        result = mongo_client.db.publishers.insert_one(pub_dict)
        pub_dict["_id"] = str(result.inserted_id)

        # Return publisher info + token
        return jsonify({
            "id": pub_dict["_id"],
            "name": pub_dict["name"],
            "organisation": pub_dict.get("organisation"),
            "api_token": pub_dict["api_token"]
        }), 201

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)



@pubs_bp.route("/<pub_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
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
@role_required("user", "admin")
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

@pubs_bp.route("/<pub_id>/token/regenerate", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def regenerate_publisher_token(pub_id):
    """
    Regenerate API token for a publisher.
    """
    try:
        # Check publisher exists
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        # Generate new token
        new_token = secrets.token_urlsafe(32)
        mongo_client.db.publishers.update_one(
            {"_id": ObjectId(pub_id)},
            {"$set": {"api_token": new_token}}
        )

        return jsonify({"api_token": new_token}), 200

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
    

@pubs_bp.route("/<pub_id>/token", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_api_token(pub_id):
    """Return the API token for a publisher."""
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404
        return jsonify({"api_token": pub.get("api_token")}), 200
    except Exception as e:
        return handle_exception(e)

