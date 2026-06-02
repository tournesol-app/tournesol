import asyncio
import json
import logging
import websockets

from ..db.redis import redis_client
from ..feeds import ALL_FEEDS

JETSTREAM_URI = (
    "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
)

QUEUE_KEY = "queue:posts_to_process"
CURSOR_KEY = "jetstream:cursor"
CURSOR_TOLERANCE_US = 5_000_000  # 5 seconds in microseconds
CURSOR_UPDATE_INTERVAL = 100  # parse 1 out of N messages to update the cursor


async def get_jetstream_url():
    cursor = await redis_client.get(CURSOR_KEY)
    if cursor is None:
        return JETSTREAM_URI
    cursor = int(cursor) - CURSOR_TOLERANCE_US
    return f"{JETSTREAM_URI}&cursor={cursor}"


async def listen_to_posts():
    message_count = 0
    retry_delay = 1.0
    while True:
        try:
            uri = await get_jetstream_url()
            async with websockets.connect(uri) as websocket:
                retry_delay = 1.0   # reset delay on successful connection
                message: str
                async for message in websocket:  # type: ignore
                    if any(f.filter_message_str(message) for f in ALL_FEEDS.values()):
                        await redis_client.rpush(QUEUE_KEY, message)

                    message_count += 1
                    if message_count % CURSOR_UPDATE_INTERVAL == 0:
                        data = json.loads(message)
                        if time_us := data.get("time_us"):
                            await redis_client.set(CURSOR_KEY, time_us)
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
        except Exception:
            logging.exception("unexpected error")

        logging.info("Reopening jetstream connection in %s seconds", retry_delay)
        await asyncio.sleep(retry_delay)
        retry_delay *= 2
