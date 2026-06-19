import logging
import uuid

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import SkeletonFeedPost
from solidago import Poll, Socials, Users, Entities
from solidago.recommenders import ChronoFair

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
        self.recommender = ChronoFair()

    def get_poll(self, records: list[AtprotoCompactRecord], requester_did: str, followed_dids: list[str]) -> Poll:
        # TODO populate poll ratings (reposts) and past_recommendations (posts with interactionSeen)
        usernames = set(r.did for r in records)
        users = Users(list(usernames))
        entities = Entities([dict(name=r.cid, authors=(r.did,)) for r in records])
        socials = Socials([dict(kind="follow", by=requester_did, to=followed_did) for followed_did in followed_dids])
        return Poll(users=users, entities=entities, socials=socials)

    async def get_feed(
        self, limit: int, cursor: str | None, requester_did: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        if requester_did is None:
            return self._skeleton([], None)

        if cursor is None:
            # TODO try to return feed from cache (ttl ~1 minute), to avoid recomputing a new feed unnecessarily
            pass

        followed_dids = await get_follows(requester_did)
        records = await db.get_records_by_posters(followed_dids)
        # we will use the "cid" as the entity name
        cid_to_record = {
            r.cid: r
            for r in records
        }

        poll = self.get_poll(records=records, requester_did=requester_did, followed_dids=followed_dids)
        feed_entities = self.recommender(
            poll=poll,
            limit=limit,
            receiver_name=requester_did,
        )
        page = [
            cid_to_record[cid] for cid in feed_entities.names() 
        ]

        # TODO Do we want to keep track of specific cursors?
        # Or should we just check the presence of a cursor to decide whether "past_recommendations"
        # should be populated based on the "interactionSeen" events?
        if len(page) < limit:
            next_cursor = None
        else:
            next_cursor = uuid.uuid4().hex

        return self._skeleton(page, next_cursor)

    @staticmethod
    def _skeleton(
        records: list[AtprotoCompactRecord], cursor: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        return AppBskyFeedGetFeedSkeleton.Response(
            feed=[SkeletonFeedPost(post=record.at_uri) for record in records],
            cursor=cursor,
        )
