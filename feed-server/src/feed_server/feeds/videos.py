import dataclasses
from itertools import islice
import re
from collections import deque
from typing import Self

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import SkeletonFeedPost
import httpx

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
            record.get("embed", {}).get("uri", ""),
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
    def __init__(self):
        self.posts_in_feed: deque[VideoPost] = deque["VideoPost"](maxlen=1000)

    def filter_message_str(self, message: str) -> bool:
        return ("youtu.be" in message) or ("youtube.com" in message) or ("tournesol.app/entities/" in message)

    @staticmethod
    async def check_video(video_id: str):
        resp = await http_client.get(
            f"https://api.tournesol.app/polls/videos/entities/yt:{video_id}"
        )
        if resp.status_code == 404:
            return False
        entity_data = resp.json()
        collective_rating = entity_data.get("collective_rating")
        if not collective_rating:
            return False
        return not collective_rating["unsafe"]["status"]

    async def on_message(self, message: dict):
        video_post = VideoPost.from_post(message)
        if video_post is None:
            return
        is_video_safe = await self.check_video(video_post.video_id)
        print(f"Video {video_post.video_id} {is_video_safe=}")
        if is_video_safe:
            print(f"Post: {video_post.post}")
            self.posts_in_feed.append(video_post)

    def get_feed(self, limit, cursor):
        return AppBskyFeedGetFeedSkeleton.Response(
            # TODO handle limit
            # TODO handle cursor
            feed=[
                SkeletonFeedPost(post=post.at_uri)
                for post in islice(self.posts_in_feed, 0, limit)
            ],
        )
