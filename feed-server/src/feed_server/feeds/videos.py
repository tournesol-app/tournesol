import dataclasses
import json
import logging
import re
from typing import Self

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import SkeletonFeedPost
import httpx

from ..db.redis import redis_client
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

        candidate_strings = [
            record.get("embed", {}).get("external", {}).get("uri", ""),
            record.get("text", ""),
        ] + [
            feature.get("uri", "")
            for facet in record.get("facets", [])
            for feature in facet.get("features", [])
        ]

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


class VideosFeed(AtprotoFeed):
    def __init__(self, feed_name: str = "videos", max_length=1000):
        self.feed_key = f"feed:{feed_name}:posts"
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
        cached = await redis_client.get(cache_key)
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
            await redis_client.set(cache_key, "0", ex=cache_ttl)
            return False
        entity_data = resp.json()
        collective_rating = entity_data.get("collective_rating")
        if not collective_rating:
            await redis_client.set(cache_key, "0", ex=cache_ttl)
            return False
        result = not collective_rating["unsafe"]["status"]
        await redis_client.set(cache_key, "1" if result else "0", ex=cache_ttl)
        return result

    async def on_message(self, message: dict):
        video_post = VideoPost.from_post(message)
        if video_post is None:
            return
        is_video_safe = await self.check_video(video_post.video_id)
        print(f"Video {video_post.video_id} {is_video_safe=}")
        if is_video_safe:
            print(f"Post: {video_post.post}")
            await redis_client.lpush(self.feed_key, json.dumps(dataclasses.asdict(video_post)))
            await redis_client.ltrim(self.feed_key, 0, self.max_length - 1)

    async def get_feed(
        self, limit: int, cursor: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        items = await redis_client.lrange(self.feed_key, 0, limit - 1)
        # TODO handle cursor
        if cursor:
            posts = []
        else:
            posts = [VideoPost(**json.loads(item)) for item in items]
        return AppBskyFeedGetFeedSkeleton.Response(
            feed=[SkeletonFeedPost(post=post.at_uri) for post in posts],
            cursor="dummy",
        )
