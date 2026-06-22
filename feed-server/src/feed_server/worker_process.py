import asyncio
import logging

from feed_server.main import process_posts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_posts())
