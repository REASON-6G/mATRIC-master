import asyncio
from matching_service_client import MatchingServiceClient

async def main():
    print("Logging in")
    client = MatchingServiceClient("http://localhost:5000")
    print("Logged in")
    await client.login_with_token("4k7NRf56iv7SbHRWppPo_9VB0z8p4GrynmjjFfm7rGU")

    subscription = await client.subscribe("uk/bridgend/wl/*/*/*/*")

    async def print_callback(msg):
        print("Received message:", msg)

    subscription = await client.async_poll(subscription["queue"], print_callback)
    
    await asyncio.sleep(10)
    await client.close()
    


if __name__ == "__main__":
    asyncio.run(main())