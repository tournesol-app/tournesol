import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from feed_server.db.redis import redis_client
from feed_server.indexer.jetstream import listen_to_posts, QUEUE_KEY
from feed_server.routes.feed import router as feed_router
from feed_server.routes.well_known import router as well_known_router
from feed_server.feeds import ALL_FEEDS


async def process_posts():
    while True:
        queue_size = await redis_client.llen(QUEUE_KEY)
        if queue_size >= 3:
            logging.warning("Many posts to process. Queue size: %s", queue_size)

        result = await redis_client.blpop(QUEUE_KEY, timeout=0)
        if result is None:
            await asyncio.sleep(1.0)
            continue
        _, message_json = result
        post = json.loads(message_json)
        await asyncio.gather(*(feed.on_message(post) for feed in ALL_FEEDS.values()))


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(process_posts())
    asyncio.create_task(listen_to_posts())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(feed_router)
app.include_router(well_known_router)
