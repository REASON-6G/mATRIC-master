import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError

from matching_service_api.utils import mongo_client, handle_exception, role_required, is_admin
from matching_service_api.models import PublisherModel, PublisherUpdateRequest, PublisherResponse, mongo_to_dict

pubs_bp = Blueprint("publishers", __name__)


def serialize_publisher(pub: dict) -> dict:
    """Convert Mongo dict to PublisherResponse dict."""
    pub = mongo_to_dict(pub)
    return PublisherResponse(**pub).dict()


@pubs_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_publishers():
    """List all publishers (limit 50)."""
    try:
        user_id = str(get_jwt_identity())
        cursor = mongo_client.db.publishers.find({"user_id": user_id}).sort("created_at", -1)
        pubs = [serialize_publisher(pub) for pub in cursor]
        return jsonify(pubs), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_publisher(pub_id):
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        # Ownership check
        user_id = str(get_jwt_identity())
        if not is_admin() and pub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to view this publisher"}), 403

        return jsonify(serialize_publisher(pub)), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def create_publisher():
    """Create a new publisher and generate an API token."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert relevant string fields to lowercase
        for field in ["name", "description", "country", "city", "organisation"]:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].lower()

        data["api_token"] = secrets.token_urlsafe(32)
        data["created_at"] = datetime.utcnow()
        data["user_id"] = str(get_jwt_identity())

        try:
            publisher = PublisherModel(**data)
            pub_dict = publisher.dict()
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        result = mongo_client.db.publishers.insert_one(pub_dict)
        pub_dict["_id"] = result.inserted_id

        pub = mongo_client.db.publishers.find_one({"_id": pub_dict["_id"]})
        return jsonify(serialize_publisher(pub)), 201

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>", methods=["PUT"])
@jwt_required()
@role_required("user", "admin")
def update_publisher(pub_id):
    """Update an existing publisher."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        # Convert relevant string fields to lowercase
        for field in ["name", "description", "country", "city", "organisation"]:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].lower()

        try:
            publisher = PublisherUpdateRequest(**data)
            update_data = publisher.dict(exclude_unset=True)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        # Fetch publisher to check ownership and existence
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and pub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to update this publisher"}), 403

        # Perform update
        result = mongo_client.db.publishers.update_one(
            {"_id": ObjectId(pub_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Publisher not found"}), 404

        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        return jsonify(serialize_publisher(pub)), 200

    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)



@pubs_bp.route("/<pub_id>", methods=["DELETE"])
@jwt_required()
@role_required("user", "admin")
def delete_publisher(pub_id):
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and pub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to delete this publisher"}), 403

        mongo_client.db.publishers.delete_one({"_id": ObjectId(pub_id)})
        return jsonify({"id": pub_id, "deleted": True}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)
    

@pubs_bp.route("/<publisher_id>/topics", methods=["GET"])
@jwt_required()
def get_publisher_topics(publisher_id: str):
    try:
        # validate ObjectId
        try:
            obj_id = ObjectId(publisher_id)
        except Exception:
            return jsonify({"error": "Invalid publisher ID"}), 400

        topics = list(mongo_client.db.topics.find({"publisher_id": str(obj_id)}))
        # Convert ObjectIds to strings
        for t in topics:
            t["id"] = str(t["_id"])
            t.pop("_id", None)
        return jsonify(topics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pubs_bp.route("/<pub_id>/token/regenerate", methods=["POST"])
@jwt_required()
@role_required("user", "admin")
def regenerate_publisher_token(pub_id):
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and pub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to regenerate token"}), 403

        new_token = secrets.token_urlsafe(32)
        mongo_client.db.publishers.update_one(
            {"_id": ObjectId(pub_id)}, {"$set": {"api_token": new_token}}
        )

        # Return only the token to the caller (UI will show it in modal)
        return jsonify({"api_token": new_token}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)


@pubs_bp.route("/<pub_id>/token", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def get_api_token(pub_id):
    try:
        pub = mongo_client.db.publishers.find_one({"_id": ObjectId(pub_id)})
        if not pub:
            return jsonify({"error": "Publisher not found"}), 404

        user_id = str(get_jwt_identity())
        if not is_admin() and pub.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to view token"}), 403

        return jsonify({"api_token": pub.get("api_token")}), 200
    except PyMongoError as e:
        return handle_exception(e, msg="Database error")
    except Exception as e:
        return handle_exception(e)