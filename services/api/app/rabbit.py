import os
import pika
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.config import Config

bp = Blueprint("rabbitmq", __name__)

RABBIT_URL = Config.RABBITMQ_URL
EXCHANGE = Config.RABBITMQ_EXCHANGE

# Connection helper
def get_channel():
    params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    return connection, channel

@bp.route("/publish", methods=["POST"])
@jwt_required()
def publish():
    body = request.get_json() or {}
    topic = body.get("topic")
    payload = body.get("payload")

    if not topic or not payload:
        return jsonify({"msg": "topic and payload required"}), 400

    connection, channel = get_channel()
    try:
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=topic,
            body=json.dumps(payload),
            properties=pika.BasicProperties(content_type="application/json")
        )
        return jsonify({"status": "published", "topic": topic})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@bp.route("/subscribe", methods=["POST"])
@jwt_required()
def subscribe():
    """
    Creates a temporary queue, binds it to a topic filter.
    Returns queue name so a worker can consume.
    """
    body = request.get_json() or {}
    topic_filter = body.get("filter")

    if not topic_filter:
        return jsonify({"msg": "filter required"}), 400

    connection, channel = get_channel()
    try:
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=topic_filter)

        return jsonify({"queue": queue_name, "filter": topic_filter})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@bp.route("/poll", methods=["POST"])
@jwt_required()
def poll():
    """
    Poll a given queue for available messages (non-blocking).
    """
    body = request.get_json() or {}
    queue = body.get("queue")
    if not queue:
        return jsonify({"msg": "queue required"}), 400

    connection, channel = get_channel()
    try:
        method, props, body = channel.basic_get(queue=queue, auto_ack=True)
        if method:
            return jsonify({"message": json.loads(body)})
        else:
            return jsonify({"message": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
