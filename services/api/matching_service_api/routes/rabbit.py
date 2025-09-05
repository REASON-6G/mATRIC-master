import json
import pika
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from matching_service_api.config import Config
from matching_service_api.utils import handle_exception

rabbit_bp = Blueprint("queues", __name__)

RABBIT_URL = Config.RABBITMQ_URL
EXCHANGE = Config.RABBITMQ_EXCHANGE


# -------------------
# RabbitMQ Connection Helper
# -------------------
def get_channel():
    """
    Establish a RabbitMQ connection and return the connection and channel.
    """
    try:
        params = pika.URLParameters(RABBIT_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        return connection, channel
    except Exception as e:
        current_app.logger.exception("RabbitMQ connection failed")
        raise RuntimeError(f"RabbitMQ connection failed: {e}")


# -------------------
# Publish
# -------------------
@rabbit_bp.route("/publish", methods=["POST"])
@jwt_required()
def publish():
    """
    Publish a message to a topic.
    Expected JSON: { "topic": str, "payload": dict }
    """
    try:
        body = request.get_json() or {}
        topic = body.get("topic")
        payload = body.get("payload")

        if not topic or payload is None:
            return jsonify({"error": "topic and payload required"}), 400

        connection, channel = get_channel()
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=topic,
            body=json.dumps(payload),
            properties=pika.BasicProperties(content_type="application/json")
        )
        return jsonify({"status": "published", "topic": topic}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to publish message", status_code=503)
    finally:
        if "connection" in locals() and connection:
            connection.close()


# -------------------
# Subscribe (temporary queue)
# -------------------
@rabbit_bp.route("/subscribe", methods=["POST"])
@jwt_required()
def subscribe():
    """
    Create a temporary queue and bind to a topic filter.
    Returns queue name for consumption.
    Expected JSON: { "filter": str }
    """
    try:
        body = request.get_json() or {}
        topic_filter = body.get("filter")
        if not topic_filter:
            return jsonify({"error": "filter required"}), 400

        connection, channel = get_channel()
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=topic_filter)

        return jsonify({"queue": queue_name, "filter": topic_filter}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to create subscription", status_code=503)
    finally:
        if "connection" in locals() and connection:
            connection.close()


# -------------------
# Poll a queue (non-blocking)
# -------------------
@rabbit_bp.route("/poll", methods=["POST"])
@jwt_required()
def poll():
    """
    Poll a given queue for messages (non-blocking).
    Expected JSON: { "queue": str }
    """
    try:
        body = request.get_json() or {}
        queue = body.get("queue")
        if not queue:
            return jsonify({"error": "queue required"}), 400

        connection, channel = get_channel()
        method, props, msg_body = channel.basic_get(queue=queue, auto_ack=True)
        if method:
            return jsonify({"message": json.loads(msg_body)}), 200
        else:
            return jsonify({"message": None}), 200
    except Exception as e:
        return handle_exception(e, msg="Failed to poll queue", status_code=503)
    finally:
        if "connection" in locals() and connection:
            connection.close()


# -------------------
# Health Check
# -------------------
@rabbit_bp.route("/health", methods=["GET"])
def health():
    """
    Check RabbitMQ connection health.
    """
    try:
        connection, channel = get_channel()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return handle_exception(e, msg="RabbitMQ health check failed", status_code=503)
    finally:
        if "connection" in locals() and connection:
            connection.close()
