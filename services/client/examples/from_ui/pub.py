import asyncio
from random import randint
from matching_service_client import MatchingServiceClient


async def main():
    print("Logging in")
    client = MatchingServiceClient("http://localhost:5000")
    print("Logged in")
    await client.login_with_token("WAhNMlvQsQVNsSoP2MwgPbjPmWpTBQdYF1gdQUjPT8Q")
    while True:
        ret = await client.publish("uk/bridgend/wl/ss/aa/ff/ee", {"hello": "world", "random": randint(0, 10)})
        print(ret)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())