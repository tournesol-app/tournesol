import asyncio
import logging

from feed_server.indexer.jetstream import listen_to_posts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(listen_to_posts())
