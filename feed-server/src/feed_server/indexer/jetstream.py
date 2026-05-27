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


async def listen_to_posts():
    cursor = await redis_client.get(CURSOR_KEY)
    if cursor is not None:
        cursor = int(cursor) - CURSOR_TOLERANCE_US
        uri = f"{JETSTREAM_URI}&cursor={cursor}"
    else:
        uri = JETSTREAM_URI

    message_count = 0
    async for websocket in websockets.connect(uri):
        try:
            while True:
                message: str | None = await websocket.recv()  # type: ignore
                if message is None:
                    continue

                if any(f.filter_message_str(message) for f in ALL_FEEDS.values()):
                    await redis_client.rpush(QUEUE_KEY, message)

                message_count += 1
                if message_count % CURSOR_UPDATE_INTERVAL == 0:
                    data = json.loads(message)
                    if time_us := data.get("time_us"):
                        await redis_client.set(CURSOR_KEY, time_us)
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
            continue
        except Exception:
            logging.exception("unexpected error")
