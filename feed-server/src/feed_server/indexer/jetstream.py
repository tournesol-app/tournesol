import asyncio
import logging
from typing import Any
from urllib.parse import urlencode

import orjson
import websockets

from ..db import db

JETSTREAM_BASE_URL = "wss://jetstream1.us-east.bsky.network/subscribe"

QUEUE_KEY = "queue:posts_to_process"
CURSOR_KEY = "jetstream:cursor"
CURSOR_TOLERANCE_MICROSECONDS = 1_000
CURSOR_UPDATE_INTERVAL = 100  # parse 1 out of N messages to update the cursor

WANTED_COLLECTIONS = [
    "app.bsky.feed.post",
    "app.bsky.feed.repost",
]


def is_reply(data: dict) -> bool:
    record = data.get("commit", {}).get("record", {})
    return record.get("reply") is not None


async def get_jetstream_url():
    params: dict[str, Any] = {"wantedCollections": WANTED_COLLECTIONS}
    cursor = await db.redis_client.get(CURSOR_KEY)
    if cursor is not None:
        params["cursor"] = int(cursor) - CURSOR_TOLERANCE_MICROSECONDS
    return f"{JETSTREAM_BASE_URL}?{urlencode(params, doseq=True)}"


async def listen_to_posts():
    retry_delay = 1.0
    while True:
        try:
            uri = await get_jetstream_url()
            async with websockets.connect(uri) as websocket:
                retry_delay = 1.0  # reset delay on successful connection
                message: str
                async for message in websocket:  # type: ignore
                    data = orjson.loads(message)
                    if "commit" not in data:
                        print(data)
                        continue
                    if data["commit"].get("operation") == "create" and not is_reply(data):
                        await db.redis_client.rpush(QUEUE_KEY, message)
                    if time_us := data.get("time_us"):
                        await db.redis_client.set(CURSOR_KEY, time_us)
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
        except Exception:
            logging.exception("unexpected error")

        logging.info("Reopening jetstream connection in %s seconds", retry_delay)
        await asyncio.sleep(retry_delay)
        retry_delay *= 2
