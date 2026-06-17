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
        try:
            post = orjson.loads(message_json)
            record = AtprotoCompactRecord.from_raw(post)
            await asyncio.gather(
                db.save_record(record),
                *(feed.on_message(post, record) for feed in ALL_FEEDS.values()),
                return_exceptions=True,
            )
        except Exception:
            logging.exception("Failed to process message, skipping: %s", message_json)


def log_unexpected_task_exit(task: asyncio.Task):
    if task.cancelled():
        return
    exception = task.exception()
    if exception is not None:
        logging.error("Background task %s crashed", task.get_name(), exc_info=exception)
    else:
        logging.error("Background task %s exited unexpectedly", task.get_name())


@asynccontextmanager
async def lifespan(app: FastAPI):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    background_tasks = [
        asyncio.create_task(process_posts(), name="process_posts"),
        asyncio.create_task(listen_to_posts(), name="listen_to_posts"),
    ]
    for task in background_tasks:
        task.add_done_callback(log_unexpected_task_exit)

    yield

    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)
app.include_router(feed_router)
app.include_router(well_known_router)
