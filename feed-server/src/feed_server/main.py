import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from feed_server.db.redis import redis_client
from feed_server.feeds.videos import VideoPost
from feed_server.indexer.jetstream import listen_to_posts, QUEUE_KEY
from feed_server.routes.feed import router
from feed_server.feeds import ALL_FEEDS


async def process_video_posts():
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
    asyncio.create_task(process_video_posts())
    asyncio.create_task(listen_to_posts())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/")
async def root():
    items = await redis_client.lrange(ALL_FEEDS["videos_v0"].feed_key, 0, -1)
    posts = [VideoPost(**json.loads(p)) for p in items]
    return {
        "posts": [
            {
                "did": p.post["did"],
                "collection": p.post["commit"]["collection"],
                "rkey": p.post["commit"]["rkey"],
            }
            for p in posts
        ]
    }
