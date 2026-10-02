import datetime
import os

import redis.asyncio as redis

from feed_server.indexer.record import AtprotoCompactRecord, AtprotoSeenRecord

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
PIPELINE_CHUNK_SIZE = 400  # max LRANGE commands sent in one pipeline


def _make_client(decode_responses: bool) -> redis.Redis:
    # Hard cap: when all connections are busy, redis raises
    # redis.exceptions.MaxConnectionsError (a ConnectionError subclass),
    # so a too-low limit shows up in the logs.
    pool = redis.ConnectionPool.from_url(
        REDIS_URL,
        max_connections=REDIS_MAX_CONNECTIONS,
        decode_responses=decode_responses,
    )
    return redis.Redis(connection_pool=pool)


class RedisDb:
    POSTS_RETENTION_IN_DAYS = 3
    SEEN_RETENTION_IN_DAYS = 7

    def __init__(self) -> None:
        self.redis_client = _make_client(decode_responses=True)
        self.redis_client_bytes = _make_client(decode_responses=False)

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
    def feed_posts_seen_key(feed_key: str, did: str, date: datetime.date):
        return f"feed:seen:{feed_key}:{date.isoformat()}:{did}"

    @staticmethod
    def feed_posts_key(feed_key: str):
        return f"feed:posts:{feed_key}"

    @staticmethod
    async def _lrange_all(client: redis.Redis, keys: list[str]) -> list:
        """Read whole lists for many keys, using a few pipelined round trips."""
        items = []
        for i in range(0, len(keys), PIPELINE_CHUNK_SIZE):
            async with client.pipeline(transaction=False) as pipe:
                for key in keys[i : i + PIPELINE_CHUNK_SIZE]:
                    pipe.lrange(key, 0, -1)
                results = await pipe.execute()
            items.extend(it for result in results for it in result)
        return items

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
        return await self.get_records_by_posters([poster_did])

    async def get_records_by_posters(self, poster_dids: list[str]) -> list[AtprotoCompactRecord]:
        today = datetime.datetime.now(datetime.UTC).date()
        keys = [
            self.account_posts_key(did, today - datetime.timedelta(days=n))
            for did in poster_dids
            for n in range(self.POSTS_RETENTION_IN_DAYS + 1)
        ]
        items = await self._lrange_all(self.redis_client_bytes, keys)
        return [AtprotoCompactRecord.deserialize(it) for it in items]

    async def mark_record_as_seen(
        self, feed_key: str, user_did: str, seen_record: AtprotoSeenRecord
    ):
        key = self.feed_posts_seen_key(feed_key, did=user_did, date=seen_record.dt.date())
        await self.redis_client.lpush(key, seen_record.serialize())
        await self.redis_client.expire(key, self.SEEN_RETENTION_IN_DAYS * 24 * 3600)

    async def get_records_seen_by_user(self, feed_key: str, did: str) -> list[AtprotoSeenRecord]:
        today = datetime.datetime.now(datetime.UTC).date()
        keys = [
            self.feed_posts_seen_key(feed_key, did=did, date=today - datetime.timedelta(days=n))
            for n in range(self.SEEN_RETENTION_IN_DAYS + 1)
        ]
        items = await self._lrange_all(self.redis_client, keys)
        return [AtprotoSeenRecord.deserialize(it) for it in items]


db = RedisDb()
