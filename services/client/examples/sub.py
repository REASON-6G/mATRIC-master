import asyncio
from matching_service_client import MatchingServiceClient

async def main():
    client = MatchingServiceClient("http://localhost:5000")
    await client.login_with_token("hinTX2AP-jUZsDkfn6oqlfH-rIxNnf4kUIYvqexOyjc")
    print("Logged in")

    # List topics
    topics = await client.list_topics()
    print("Topics:", topics)

    

    # Subscribe to a topic filter
    subscription = await client.subscribe("/test/test")
    print("Subscription created:", subscription)

    queue_name = subscription["queue"]

    # Async callback for polled messages
    async def print_callback(msg):
        print("Received message:", msg)

    # Start background polling
    client.async_subscribe(queue_name, print_callback)

    # Keep script running for demonstration
    print("Polling messages for 15 seconds...")
    await asyncio.sleep(15)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
