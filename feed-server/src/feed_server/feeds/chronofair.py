import logging

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import SkeletonFeedPost

from ..db import db
from ..follows import get_follows
from ..indexer.record import AtprotoCompactRecord
from .base import AtprotoFeed

logger = logging.getLogger(__name__)

CURSOR_PREFIX = "after:"


class ChronofairFeed(AtprotoFeed):
    def __init__(self, max_posts: int = 1000):
        # Upper bound on how many merged posts we rank/paginate over per request.
        self.max_posts = max_posts

    async def get_feed(
        self, limit: int, cursor: str | None, requester_did: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        if requester_did is None:
            return self._skeleton([], None)

        followed_dids = await get_follows(requester_did)
        records = await db.get_records_by_posters(followed_dids)
        records.sort(key=lambda record: record.time_us, reverse=True)
        records = records[: self.max_posts]
        logger.info(
            "Chronofair feed for %s: %d follows, %d posts",
            requester_did,
            len(followed_dids),
            len(records),
        )

        if cursor is not None:
            anchor_cid = self._parse_cursor(cursor)
            if anchor_cid is None:
                return self._skeleton([], None)
            start = next(
                (i + 1 for i, record in enumerate(records) if record.cid == anchor_cid),
                None,
            )
            if start is None:
                # Anchor aged out of the retention window: end of feed.
                return self._skeleton([], None)
            records = records[start:]

        page = records[:limit]
        has_more = len(records) > len(page)
        next_cursor = f"{CURSOR_PREFIX}{page[-1].cid}" if page and has_more else None
        return self._skeleton(page, next_cursor)

    @staticmethod
    def _parse_cursor(cursor: str) -> str | None:
        if not cursor.startswith(CURSOR_PREFIX):
            return None
        cid = cursor[len(CURSOR_PREFIX):]
        return cid or None

    @staticmethod
    def _skeleton(
        records: list[AtprotoCompactRecord], cursor: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        return AppBskyFeedGetFeedSkeleton.Response(
            feed=[SkeletonFeedPost(post=record.at_uri) for record in records],
            cursor=cursor,
        )
