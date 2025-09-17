from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from pymongo.errors import PyMongoError
import fnmatch
from pydantic import ValidationError

from matching_service_api.utils import mongo_client, handle_exception, role_required
from matching_service_api.models import MatchRequest, MatchResponse, MatchResult

match_bp = Blueprint("match", __name__)

# --- Topic matcher ---
def topic_matches(filter_pattern: str, topic: str) -> bool:
    return fnmatch.fnmatchcase(topic, filter_pattern)


# --- Routes ---
@match_bp.route("/test", methods=["POST"])
@jwt_required()
def test_match():
    """
    Input: { "topic": "<full_topic>" }
    Returns: list of subscriptions (subscription_id, user_id, filter) that match
    """
    try:
        body = request.get_json() or {}
        try:
            req = MatchRequest(**body)
        except ValidationError as e:
            return jsonify({"errors": e.errors()}), 422

        try:
            subs_cursor = mongo_client.db.subscriptions.find({"active": True})
        except PyMongoError as e:
            return handle_exception(e, status=500, msg="Database error")

        matches: list[MatchResult] = []
        for sub in subs_cursor:
            if "topic_filter" not in sub:
                continue
            try:
                if topic_matches(sub["topic_filter"], req.topic):
                    matches.append(
                        MatchResult(
                            subscription_id=str(sub["_id"]),
                            user_id=sub.get("user_id"),
                            filter=sub["topic_filter"],
                        )
                    )
            except Exception as e:
                current_app.logger.warning(
                    f"[MATCH] Failed to evaluate subscription {sub.get('_id')}: {e}"
                )

        resp = MatchResponse(topic=req.topic, matches=matches)
        return jsonify(resp.dict()), 200

    except Exception as e:
        return handle_exception(e)


@match_bp.route("/subscriptions", methods=["GET"])
@jwt_required()
@role_required("user", "admin")
def list_subscriptions():
    """
    Admin-only: list all active subscriptions with user and filter.
    """
    try:
        claims = get_jwt()
        role = claims.get("role", "user")
        if role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        try:
            cursor = mongo_client.db.subscriptions.find({"active": True})
        except PyMongoError as e:
            return handle_exception(e, status=500, msg="Database error")

        subs: list[MatchResult] = []
        for sub in cursor:
            subs.append(
                MatchResult(
                    subscription_id=str(sub["_id"]),
                    user_id=sub.get("user_id"),
                    filter=sub.get("topic_filter", ""),
                )
            )

        return jsonify([s.dict() for s in subs]), 200

    except Exception as e:
        return handle_exception(e)
