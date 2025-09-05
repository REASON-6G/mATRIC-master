from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from pymongo.errors import PyMongoError

from matching_service_api.utils import mongo_client, handle_exception
from matching_service_api.models import mongo_to_dict

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/config", methods=["UPDATE"])
@jwt_required()
def update_config():
    pass