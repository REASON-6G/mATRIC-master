import asyncio
from matching_service_client import MatchingServiceClient


async def main():
    print("Logging in")
    client = MatchingServiceClient("http://localhost:5000")
    print("Logged in")
    await client.login_with_token("WAhNMlvQsQVNsSoP2MwgPbjPmWpTBQdYF1gdQUjPT8Q")

    subscription = await client.subscribe("uk/bridgend/wl/ss/aa/ff/ee")

    while True:
        msg = await client.poll(subscription["queue"])
        if msg:
            print(msg)
    


if __name__ == "__main__":
    asyncio.run(main())