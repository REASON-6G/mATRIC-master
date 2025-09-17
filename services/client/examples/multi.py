import asyncio
import random
import logging
from datetime import datetime
from matching_service_client import MatchingServiceClient

# -------------------------------
# Example configuration
# -------------------------------
PUBLISHERS = [
    {
        "name": "TelecomUK",
        "country": "uk",
        "city": "bristol",
        "organisation": "telecomuk",
        "topics": ["net/router1", "net/router2", "cell/tower1"],
    },
    {
        "name": "TelecomFR",
        "country": "fr",
        "city": "paris",
        "organisation": "telecomfr",
        "topics": ["net/router1", "net/router2", "cell/tower1"],
    },
    {
        "name": "TelecomDE",
        "country": "de",
        "city": "berlin",
        "organisation": "telecomde",
        "topics": ["net/router1", "net/router2", "cell/tower1"],
    },
]

SUBSCRIBERS = [
    {"username": "sub1", "filters": ["uk/bristol/*"]},
    {"username": "sub2", "filters": ["fr/*/*"]},
    {"username": "sub3", "filters": ["de/berlin/net/*", "uk/bristol/cell/*"]},
    {"username": "sub4", "filters": ["*/paris/*"]},
    {"username": "sub5", "filters": ["*/*/cell/*"]},
]


# -------------------------------
# Example helper: fake metrics
# -------------------------------
def generate_payload(topic: str):
    if "router" in topic:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "signal_strength": random.randint(-90, -30),
            "uptime": random.randint(1000, 50000),
        }
    elif "tower" in topic:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "connected_users": random.randint(10, 1000),
            "throughput": round(random.uniform(10, 200), 2),
        }
    else:
        return {"timestamp": datetime.utcnow().isoformat(), "value": random.random()}


# -------------------------------
# Publisher coroutine
# -------------------------------
async def publisher_task(client: MatchingServiceClient, pub_config: dict):
    # Create topics if they don’t exist
    for t in pub_config["topics"]:
        full_topic = f"{pub_config['country']}/{pub_config['city']}/{t}"
        try:
            await client.create_topic(full_topic, description=f"Topic for {pub_config['name']}")
        except Exception:
            pass  # ignore duplicates

    # Publish every 5 seconds
    while True:
        for t in pub_config["topics"]:
            full_topic = f"{pub_config['country']}/{pub_config['city']}/{t}"
            payload = generate_payload(full_topic)
            await client.publish(full_topic, payload)
            logging.info(f"[Publisher {pub_config['name']}] Published to {full_topic}: {payload}")
        await asyncio.sleep(5)


# -------------------------------
# Subscriber coroutine
# -------------------------------
async def subscriber_task(client: MatchingServiceClient, sub_config: dict):
    # Set up per-subscriber logger
    logger = logging.getLogger(sub_config["username"])
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(f"{sub_config['username']}.log", mode="w")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    queues = []
    for f in sub_config["filters"]:
        subscription = await client.subscribe(f)
        queues.append(subscription["queue"])
        logger.info(f"Subscribed to {f} -> {subscription['queue']}")

    async def print_callback(msg, user=sub_config["username"]):
        logger.info(f"Received: {msg}")

    for q in queues:
        client.async_subscribe(q, print_callback)


# -------------------------------
# Main demo
# -------------------------------
async def main():
    # Create clients for publishers and subscribers
    pub_clients = [MatchingServiceClient("http://localhost:5000") for _ in PUBLISHERS]
    sub_clients = [MatchingServiceClient("http://localhost:5000") for _ in SUBSCRIBERS]

    # Log in all clients
    for c in pub_clients + sub_clients:
        await c.login("test", "asdasd123")

    # Launch publishers
    pub_tasks = [asyncio.create_task(publisher_task(c, cfg)) for c, cfg in zip(pub_clients, PUBLISHERS)]

    # Launch subscribers
    sub_tasks = [asyncio.create_task(subscriber_task(c, cfg)) for c, cfg in zip(sub_clients, SUBSCRIBERS)]

    # Run for 30 seconds
    await asyncio.sleep(30)

    # Cancel publishers
    for task in pub_tasks:
        task.cancel()

    # Close clients
    for c in pub_clients + sub_clients:
        await c.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    asyncio.run(main())
