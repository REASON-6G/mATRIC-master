from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from matching_service_api.utils import mongo_client
import fnmatch

match_bp = Blueprint("match", __name__)

def topic_matches(filter_pattern: str, topic: str) -> bool:
    """
    Match topics against filters using Unix shell-style wildcards (*).
    e.g. filter: "uk/bristol/*/*/*/attenuation/*"
         topic:  "uk/bristol/org1/net/router/attenuation/dbm"
    """
    return fnmatch.fnmatchcase(topic, filter_pattern)

@match_bp.route("/test", methods=["POST"])
@jwt_required()
def test_match():
    """
    Input: { "topic": "<full_topic>" }
    Returns: list of subscriptions (subscriber_id + filter) that match
    """
    body = request.get_json() or {}
    topic = body.get("topic")
    if not topic:
        return jsonify({"msg": "topic required"}), 400

    subs_cursor = mongo_client.db.subscriptions.find({"active": True})
    matches = []
    for sub in subs_cursor:
        if topic_matches(sub["topic_filter"], topic):
            matches.append({
                "subscription_id": str(sub["_id"]),
                "user_id": sub["user_id"],
                "filter": sub["topic_filter"]
            })

    return jsonify({"topic": topic, "matches": matches})
