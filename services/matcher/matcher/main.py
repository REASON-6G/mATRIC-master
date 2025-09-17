# matcher_service.py
import asyncio
import fnmatch
import logging
from datetime import datetime, timezone
import aio_pika
from quart import Quart
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId

from matcher.config import Config

# -------------------
# Configuration
# -------------------
MONGO_URI = Config.MONGO_URI
DB_NAME = "matchingservice"
RABBITMQ_URL = Config.RABBITMQ_URL
EXCHANGE = Config.RABBITMQ_EXCHANGE
POLL_INTERVAL = Config.POLL_INTERVAL

# -------------------
# Logging
# -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("matcher")

# -------------------
# MongoDB Setup
# -------------------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# -------------------
# Helpers
# -------------------
def topic_matches(filter_pattern: str, topic: str) -> bool:
    match = fnmatch.fnmatchcase(topic, filter_pattern)
    logger.info(f"Matching topic '{topic}' against filter '{filter_pattern}' -> {match}")
    return match


async def ensure_queues():
    """
    Reconcile DB subscriptions with RabbitMQ:
    - Create durable queue for each active subscription
    - Bind to all matching topics
    - Drop queues for inactive subscriptions
    """
    try:
        subscriptions = list(db.subscriptions.find({}))
        topics = list(db.topics.find({}))
        logger.info(f"Fetched {len(subscriptions)} subscriptions and {len(topics)} topics")
    except PyMongoError as e:
        logger.error(f"MongoDB error fetching subscriptions/topics: {e}")
        return

    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
    except Exception as e:
        logger.error(f"RabbitMQ connection error: {e}")
        return

    for sub in subscriptions:
        sub_id = str(sub["_id"])
        user_id = sub.get("user_id")
        topic_filter = sub.get("topic_filter")
        active = sub.get("active", True)

        queue_name = f"sub_{user_id}_{sub_id}"

        if not topic_filter:
            logger.warning(f"Subscription {sub_id} missing topic_filter, skipping")
            continue

        if not active:
            # Clean up inactive subscription queues
            try:
                queue = await channel.declare_queue(queue_name, durable=True, passive=True)
                await queue.delete()
                logger.info(f"Deleted queue {queue_name} for inactive subscription {sub_id}")
            except Exception:
                logger.info(f"Queue {queue_name} already gone for inactive sub {sub_id}")
            db.subscriptions.update_one(
                {"_id": sub["_id"]},
                {"$unset": {"queue": ""}, "$set": {"updated_at": datetime.utcnow()}}
            )
            continue

        try:
            # Create or recover durable queue
            queue = await channel.declare_queue(queue_name, durable=True)

            # Always bind to exchange with subscription filter
            await queue.bind(exchange, routing_key=topic_filter)

            # Reconcile against all topics in DB
            matched_topics = [t["topic"] for t in topics if topic_matches(topic_filter, t["topic"])]
            for topic in matched_topics:
                try:
                    await queue.bind(exchange, routing_key=topic)
                    logger.info(f"Bound queue {queue_name} to topic '{topic}' (sub {sub_id})")
                except Exception as e:
                    logger.error(f"Failed to bind queue {queue_name} to topic '{topic}': {e}")

            # Update DB record with latest queue assignment
            db.subscriptions.update_one(
                {"_id": sub["_id"]},
                {"$set": {"queue": queue_name, "updated_at": datetime.utcnow()}}
            )

            logger.info(
                f"Ensured queue {queue_name} for sub {sub_id} "
                f"(user {user_id}, filter '{topic_filter}', matched {len(matched_topics)} topics)"
            )
        except Exception as e:
            logger.error(f"Error ensuring queue {queue_name} for subscription {sub_id}: {e}")

    await connection.close()

# -------------------
# Health endpoint
# -------------------
health_app = Quart(__name__)

@health_app.route("/health", methods=["GET"])
async def health():
    """
    Returns health status of the matcher service.
    Includes DB and in-memory stats.
    """
    try:
        # MongoDB status
        total_topics = await asyncio.to_thread(lambda: db.topics.count_documents({}))
        total_subs = await asyncio.to_thread(lambda: db.subscriptions.count_documents({}))

        # Running asyncio tasks
        running_tasks = len(asyncio.all_tasks())  # optional: track main_loop task separately

        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "topics_total": total_topics,
            "subscriptions_total": total_subs,
            "running_asyncio_tasks": running_tasks,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }, 500
# -------------------
# Main Loop
# -------------------
async def matcher_loop():
    while True:
        await ensure_queues()
        await asyncio.sleep(POLL_INTERVAL)


async def run_all():
    # Start matcher main loop
    matcher_task = asyncio.create_task(matcher_loop())

    # Start Quart health app
    import hypercorn.asyncio
    import hypercorn.config

    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:7000"]
    await hypercorn.asyncio.serve(health_app, config)


# -------------------
# Entry point
# -------------------
def main():
    try:
        logger.info("Starting matcher service...")
        asyncio.run(run_all())
    except KeyboardInterrupt:
        logger.info("Matcher service stopped manually")
    except Exception as e:
        logger.exception(f"Unhandled exception in matcher service: {e}")


if __name__ == "__main__":
    main()
