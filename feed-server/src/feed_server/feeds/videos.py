import dataclasses
import logging
import re
from typing import Self

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import SkeletonFeedPost
from feed_server.indexer.record import AtprotoCompactRecord
import httpx

from ..db import db
from .base import AtprotoFeed

http_client = httpx.AsyncClient()

VIDEO_ID_RE = re.compile(
    r"(?:https?://)?"
    r"(?:www\.|m\.)?"
    r"(?:youtube\.com/(?:watch\?v=|live/|v/|shorts/)|youtu\.be/|tournesol\.app/entities/)"
    r"(?:yt:)?([A-Za-z0-9\-_]{11})"
)


@dataclasses.dataclass
class VideoPost:
    post: dict
    video_id: str

    @classmethod
    def from_post(cls, post: dict) -> Self | None:
        record = post.get("commit", {}).get("record", {})
        if not record:
            return None

        candidate_strings = [record.get("text", "")]
        if embed := record.get("embed"):
            if external := embed.get("external"):
                candidate_strings.append(external.get("uri", ""))

        candidate_strings.extend([
            feature.get("uri", "")
            for facet in record.get("facets", [])
            for feature in facet.get("features", [])
        ])

        for s in candidate_strings:
            if not s:
                continue
            match = VIDEO_ID_RE.search(s)
            if match:
                return cls(post=post, video_id=match.group(1))
        return None

    @property
    def at_uri(self):
        return f"at://{self.post['did']}/{self.post['commit']['collection']}/{self.post['commit']['rkey']}"

    @property
    def cid(self) -> str:
        return self.post["commit"]["cid"]


class VideosFeed(AtprotoFeed):
    def __init__(self, feed_name: str = "videos", max_length=1000):
        self.feed_name = feed_name
        self.max_length = max_length

    def filter_message_str(self, message: str) -> bool:
        return (
            ("youtu.be" in message)
            or ("youtube.com" in message)
            or ("tournesol.app/entities/" in message)
        )

    @staticmethod
    async def check_video(video_id: str) -> bool:
        cache_key = f"cache:tournesol:video_is_safe:{video_id}"
        cache_ttl = 3600
        cached = await db.redis_client.get(cache_key)
        if cached is not None:
            return cached == "1"

        try:
            resp = await http_client.get(
                f"https://api.tournesol.app/polls/videos/entities/yt:{video_id}",
                timeout=5.0,
            )
            if resp.status_code not in (200, 404):
                resp.raise_for_status()
        except (httpx.RequestError, httpx.HTTPError):
            logging.warning("Failed to check video %s in Tournesol", video_id, exc_info=True)
            return False
        if resp.status_code == 404:
            await db.redis_client.set(cache_key, "0", ex=cache_ttl)
            return False
        entity_data = resp.json()
        collective_rating = entity_data.get("collective_rating")
        if not collective_rating:
            await db.redis_client.set(cache_key, "0", ex=cache_ttl)
            return False
        result = not collective_rating["unsafe"]["status"]
        await db.redis_client.set(cache_key, "1" if result else "0", ex=cache_ttl)
        return result

    async def on_message(self, message: dict, record: AtprotoCompactRecord):
        video_post = VideoPost.from_post(message)
        if video_post is None:
            return
        is_video_safe = await self.check_video(video_post.video_id)
        print(f"Video {video_post.video_id} {is_video_safe=}")
        if is_video_safe:
            print(f"Post: {video_post.post}")
            await db.add_to_feed(
                feed_key=self.feed_name, record=record, feed_max_length=self.max_length
            )

    @staticmethod
    def _parse_cursor(cursor: str) -> tuple[str, int] | None:
        """Parse an ``after:<cid>:<idx>`` cursor into ``(cid, idx)``.

        Returns ``None`` for any malformed cursor so the caller can treat it as
        "no results" rather than raising (the cursor is opaque to clients, but
        a bad one should not 500).
        """
        parts = cursor.split(":")
        if len(parts) != 3 or parts[0] != "after":
            return None
        cid = parts[1]
        try:
            idx = int(parts[2])
        except ValueError:
            return None
        if idx < 0 or not cid:
            return None
        return cid, idx

    async def get_feed(
        self, limit: int, cursor: str | None, requester_did: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        if cursor is None:
            # First page: the newest `limit` records, starting at absolute index 0.
            posts = await db.get_feed(self.feed_name, 0, limit - 1)
            start_idx = 0
        else:
            parsed = self._parse_cursor(cursor)
            if parsed is None:
                return self._skeleton([], None)
            cid, idx = parsed
            # Records are only ever inserted at the head, so the anchor's real
            # index can only have grown since the cursor was issued (>= `idx`).
            items = await db.get_feed(self.feed_name, idx, -1)
            anchor = None
            posts = []
            for i, post in enumerate(items):
                if anchor is None:
                    if post.cid == cid:
                        anchor = i
                    continue
                posts.append(post)
                if len(posts) >= limit:
                    break
            if anchor is None:
                # The anchor was trimmed off the tail, so everything after it is
                # gone too: end of feed.
                return self._skeleton([], None)
            start_idx = idx + anchor + 1

        if not posts:
            return self._skeleton([], None)
        last_idx = start_idx + len(posts) - 1
        if len(posts) < limit:
            next_cursor = None
        else:
            next_cursor = f"after:{posts[-1].cid}:{last_idx}"
        return self._skeleton(posts, next_cursor)

    @staticmethod
    def _skeleton(
        posts: list[AtprotoCompactRecord], cursor: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        return AppBskyFeedGetFeedSkeleton.Response(
            feed=[SkeletonFeedPost(post=post.at_uri) for post in posts],
            cursor=cursor,
        )
