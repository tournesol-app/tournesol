import asyncio
import json
import logging
import websockets

from ..feeds import ALL_FEEDS


JETSTREAM_URI = (
    "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
)

posts_to_process = asyncio.Queue[dict]()


async def listen_to_posts():
    async with websockets.connect(JETSTREAM_URI) as websocket:
        while True:
            try:
                message: str | None = await websocket.recv()  # type: ignore
                if message is None:
                    continue

                if any(f.filter_message_str(message) for f in ALL_FEEDS.values()):
                    posts_to_process.put_nowait(json.loads(message))
            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break
            except Exception:
                logging.exception("unexpected error")
