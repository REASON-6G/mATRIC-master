import json
import pika
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from influxdb_client import InfluxDBClient, Point, WritePrecision

from matching_service_api.config import Config
from matching_service_api.utils import handle_exception, mongo_client, ADMIN_CONFIG_CACHE, get_influx_client


rabbit_bp = Blueprint("queues", __name__)




def flatten_dict(d, parent_key="", sep="_"):
    """Flatten nested dictionaries for Influx fields."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# -------------------
# RabbitMQ Connection Helper
# -------------------
RABBIT_URL = Config.RABBITMQ_URL
EXCHANGE = Config.RABBITMQ_EXCHANGE

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
    try:
        body = request.get_json() or {}
        topic = body.get("topic")
        payload = body.get("payload")

        if not topic or payload is None:
            return jsonify({"error": "topic and payload required"}), 400

        # ---- Publish to RabbitMQ ----
        connection, channel = get_channel()
        channel.basic_publish(
            exchange=Config.RABBITMQ_EXCHANGE,
            routing_key=topic,
            body=json.dumps(payload),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )

        # ---- Write to InfluxDB ----
        import logging
        write_api, influx_bucket = get_influx_client()
        fields = flatten_dict(payload)
        logging.critical(fields)
        point = Point("messages").tag("topic", topic).time(datetime.utcnow(), WritePrecision.NS)
        for k, v in fields.items():
            if isinstance(v, (int, float, bool, str)):
                point = point.field(k, v)

        write_api.write(bucket=influx_bucket, record=point)
        logging.critical(topic)
        logging.critical(point)

        return jsonify({"status": "published", "topic": topic}), 200

    except Exception as e:
        return handle_exception(e, msg="Failed to publish message", status_code=503)

    finally:
        if "connection" in locals() and connection:
            connection.close()


# -------------------
# Subscribe (durable queue)
# -------------------
@rabbit_bp.route("/subscribe", methods=["POST"])
@jwt_required()
def subscribe():
    """
    Create a durable queue and bind it to a topic filter.
    Returns subscription ID + queue name for consumption.
    Expected JSON: { "filter": str }
    """
    try:
        body = request.get_json() or {}
        user_id = get_jwt_identity()
        topic_filter = body.get("filter")

        if not topic_filter:
            return jsonify({"error": "filter required"}), 400

        # Check if a subscription already exists
        sub = mongo_client.db.subscriptions.find_one({"user_id": user_id, "topic_filter": topic_filter})

        if sub:
            queue_name = sub["queue"]
            subscription_id = str(sub["_id"])
        else:
            # Create a durable queue per subscription
            connection, channel = get_channel()
            # Generate a unique queue name using ObjectId
            from bson import ObjectId
            subscription_id = str(ObjectId())
            queue_name = f"sub_{user_id}_{subscription_id}"
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=topic_filter)

            # Save subscription to MongoDB
            mongo_client.db.subscriptions.insert_one({
                "_id": ObjectId(subscription_id),
                "user_id": user_id,
                "topic_filter": topic_filter,
                "queue": queue_name,
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return jsonify({"subscription_id": subscription_id, "queue": queue_name, "filter": topic_filter}), 200

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

        # Validate queue exists in MongoDB subscriptions
        sub = mongo_client.db.subscriptions.find_one({"queue": queue})
        if not sub:
            return jsonify({"error": f"Queue '{queue}' not registered in subscriptions"}), 404

        connection, channel = get_channel()
        method, props, msg_body = channel.basic_get(queue=queue, auto_ack=True)
        if method:
            try:
                payload = json.loads(msg_body)
            except Exception:
                payload = msg_body.decode("utf-8")
            return jsonify({"message": payload}), 200
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
