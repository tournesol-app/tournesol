import asyncio
import logging
from contextlib import asynccontextmanager

from feed_server.indexer.record import AtprotoCompactRecord
import orjson
from fastapi import FastAPI

from feed_server.db import db
from feed_server.indexer.jetstream import listen_to_posts, QUEUE_KEY
from feed_server.routes.feed import router as feed_router
from feed_server.routes.well_known import router as well_known_router
from feed_server.feeds import ALL_FEEDS


async def process_posts():
    while True:
        queue_size = await db.redis_client.llen(QUEUE_KEY)
        if queue_size >= 100:
            logging.warning("Many posts to process. Queue size: %s", queue_size)

        result = await db.redis_client.blpop(QUEUE_KEY, timeout=0)
        if result is None:
            await asyncio.sleep(1.0)
            continue
        _, message_json = result
        post = orjson.loads(message_json)
        record = AtprotoCompactRecord.from_raw(post)
        await asyncio.gather(
            db.save_record(record),
            *(feed.on_message(post, record) for feed in ALL_FEEDS.values()),
            return_exceptions=True,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    asyncio.create_task(process_posts())
    asyncio.create_task(listen_to_posts())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(feed_router)
app.include_router(well_known_router)
