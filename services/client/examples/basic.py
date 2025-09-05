import asyncio
from typing import Any, Dict, List, Optional
import httpx

from matching_service_client import MatchingServiceClient

async def main():
    client = MatchingServiceClient("http://localhost:5000")
    await client.login("test", "asdasd123")
    print("Logged in")

    # Create a metric
    metric = await client.create_metric("uk/bristol/net/router1", 42.0, "dbm")
    print("Metric created:", metric)

    # List metrics
    metrics = await client.list_metrics()
    print("Metrics:", metrics)

    # Test matching
    matches = await client.test_match("uk/bristol/net/router1")
    print("Matches:", matches)

    # Subscribe to a topic
    queue_name = await client.subscribe_queue("uk/bristol/*")
    print("Subscribed queue:", queue_name)

    # Poll messages
    msg = await client.poll_queue(queue_name)
    print("Polled message:", msg)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())