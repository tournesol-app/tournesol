import datetime
import os

import redis.asyncio as redis

from feed_server.indexer.record import AtprotoCompactRecord

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class RedisDb:
    POSTS_RETENTION_IN_DAYS = 3

    def __init__(self) -> None:
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        self.redis_client_bytes = redis.from_url(REDIS_URL, decode_responses=False)

    @staticmethod
    def cid_processed_key(cid: str):
        return f"cid:processed:{cid}"

    # async def is_post_processed(self, cid: str):
    #     key = self.cid_processed_key(cid)
    #     return await self.redis_client.get(key) == "1"

    # async def mark_post_as_processed(self, cid: str):
    #     key = self.cid_processed_key(cid)
    #     return await self.redis_client.set(key, "1", ex=24 * 3600)

    @staticmethod
    def cid_in_feed_key(feed_key: str, cid: str):
        return f"cid:infeed:{feed_key}:{cid}"

    @staticmethod
    def account_posts_key(did: str, date: datetime.date):
        return f"account:posts:{date.isoformat()}:{did}"

    @staticmethod
    def feed_posts_key(feed_key: str):
        return f"feed:posts:{feed_key}"

    async def is_record_in_feed(self, feed_key: str, cid: str):
        key = self.cid_in_feed_key(feed_key=feed_key, cid=cid)
        return await self.redis_client.get(key) == "1"

    async def mark_cid_in_feed(self, feed_key: str, cid: str):
        key = self.cid_in_feed_key(feed_key=feed_key, cid=cid)
        return await self.redis_client.set(key, "1", ex=12 * 3600)

    async def save_record(self, record: AtprotoCompactRecord):
        date = record.dt.date()
        key = self.account_posts_key(record.did, date)
        await self.redis_client.lpush(key, record.serialize())
        await self.redis_client.expire(key, self.POSTS_RETENTION_IN_DAYS * 24 * 3600)

    async def add_to_feed(self, feed_key: str, record: AtprotoCompactRecord, feed_max_length: int):
        key = self.feed_posts_key(feed_key)
        await self.redis_client.lpush(key, record.serialize())
        await self.redis_client.ltrim(key, 0, feed_max_length - 1)

    async def get_feed(self, feed_key: str, start: int, end: int) -> list[AtprotoCompactRecord]:
        key = self.feed_posts_key(feed_key)
        items = await self.redis_client_bytes.lrange(key, start, end)
        return [AtprotoCompactRecord.deserialize(it) for it in items]

    async def get_records_by_poster(self, poster_did: str):
        items = []
        today = datetime.datetime.now(datetime.UTC).date()
        for n in range(self.POSTS_RETENTION_IN_DAYS + 1):
            day = today - datetime.timedelta(days=n)
            key = self.account_posts_key(poster_did, day)
            items.extend(await self.redis_client_bytes.lrange(key, 0, -1))
        return [AtprotoCompactRecord.deserialize(it) for it in items]


db = RedisDb()
