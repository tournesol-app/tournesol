import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from feed_server.indexer.jetstream import posts_to_process, listen_to_posts

from feed_server.routes.feed import router
from feed_server.feeds import ALL_FEEDS


async def process_video_posts():
    while True:
        queue_size = posts_to_process.qsize()
        if queue_size >= 3:
            logging.warning("Many posts to process. Queue size: %s", queue_size)

        post = await posts_to_process.get()
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
    return {
        "posts": [
            {
                "did": p.post["did"],
                "collection": p.post["commit"]["collection"],
                "rkey": p.post["commit"]["rkey"],
            }
            for p in ALL_FEEDS["videos_v0"].posts_in_feed
        ]
    }
