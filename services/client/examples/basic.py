import asyncio
from matching_service_client import MatchingServiceClient

async def main():
    client = MatchingServiceClient("http://localhost:5000")
    await client.login("test", "asdasd123")
    print("Logged in")

    # Create a topic
    topic = await client.create_topic("uk/bristol/net/router8", description="Router telemetry stream")
    print("Topic created:", topic)

    # List topics
    topics = await client.list_topics()
    print("Topics:", topics)

    # Publish a message
    message = {"signal_strength": -42, "uptime": 12345}
    result = await client.publish(topic="uk/bristol/net/router8", payload=message)
    print("Message published:", result)

    # Subscribe to a topic filter
    subscription = await client.subscribe("uk/bristol/*")
    print("Subscription created:", subscription)

    queue_name = subscription["queue"]

    # Async callback for polled messages
    async def print_callback(msg):
        print("Received message:", msg)

    # Start background polling
    client.async_subscribe(queue_name, print_callback)

    # Keep script running for demonstration
    print("Polling messages for 5 seconds...")
    await asyncio.sleep(5)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
