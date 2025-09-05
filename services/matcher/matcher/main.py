# matcher_service.py
import asyncio
import fnmatch
import logging
from datetime import datetime
import aio_pika
from pymongo import MongoClient
from pymongo.errors import PyMongoError

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
    level=logging.INFO,  # Set to DEBUG for detailed workflow
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
    logger.debug(f"Matching topic '{topic}' against filter '{filter_pattern}' -> {match}")
    return match


async def bind_queue(channel: aio_pika.Channel, queue_name: str, topic_filter: str):
    """Bind a queue to the exchange with the given topic filter."""
    try:
        await channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=topic_filter)
        logger.debug(f"Queue {queue_name} successfully bound to filter {topic_filter}")
    except Exception as e:
        logger.error(f"Failed to bind queue {queue_name} to {topic_filter}: {e}")


async def ensure_queues():
    """
    Poll subscriptions and topics, ensuring each subscriber has a queue
    bound for their topic filter. Skips subscriptions that already have a queue.
    """
    try:
        subscriptions = list(db.subscriptions.find({"active": True}))
        topics = list(db.topics.find({}))
        logger.debug(f"Fetched {len(subscriptions)} active subscriptions and {len(topics)} topics")
    except PyMongoError as e:
        logger.error(f"MongoDB error fetching subscriptions/topics: {e}")
        return

    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
    except Exception as e:
        logger.error(f"RabbitMQ connection error: {e}")
        return

    for sub in subscriptions:
        sub_id = str(sub["_id"])
        user_id = sub.get("user_id")
        topic_filter = sub.get("topic_filter")
        queue_name = sub.get("queue")

        if not topic_filter:
            logger.warning(f"Subscription {sub_id} missing topic_filter, skipping")
            continue

        if queue_name:
            logger.debug(f"Skipping subscription {sub_id}, already has queue {queue_name}")
            continue

        logger.info(f"Processing subscription {sub_id} for user {user_id} with filter '{topic_filter}'")

        # Check if any topic matches before creating a queue
        matched_topics = [t["topic"] for t in topics if topic_matches(topic_filter, t["topic"])]
        if not matched_topics:
            logger.debug(f"No topics match filter '{topic_filter}' for subscription {sub_id}")
            continue

        try:
            result = await channel.declare_queue(exclusive=True)
            queue_name = result.name
            await bind_queue(channel, queue_name, topic_filter)
            db.subscriptions.update_one(
                {"_id": sub["_id"]},
                {"$set": {"queue": queue_name, "updated_at": datetime.utcnow()}}
            )
            logger.info(
                f"Created queue {queue_name} for subscription {sub_id}, "
                f"user {user_id}, filter '{topic_filter}', matched {len(matched_topics)} topics"
            )
        except Exception as e:
            logger.error(f"Error creating queue for subscription {sub_id}: {e}")

    await connection.close()


# -------------------
# Main Loop
# -------------------
async def main_loop():
    while True:
        await ensure_queues()
        await asyncio.sleep(POLL_INTERVAL)


# -------------------
# Entry point
# -------------------
def main():
    try:
        logger.info("Starting matcher service...")
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Matcher service stopped manually")
    except Exception as e:
        logger.exception(f"Unhandled exception in matcher service: {e}")


if __name__ == "__main__":
    main()
