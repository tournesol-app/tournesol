import logging
import time
import uuid

from atproto_client.models import AppBskyFeedGetFeedSkeleton
from atproto_client.models.app.bsky.feed.defs import (
    SkeletonFeedPost,
    SkeletonReasonRepost,
)
from solidago import Entities, Poll, Ratings, Socials, Users
from solidago.recommenders import ChronoFair

from ..db import db
from ..follows import get_follows
from ..indexer.record import AtprotoCompactRecord
from .base import AtprotoFeed

logger = logging.getLogger(__name__)


def _author_did_from_at_uri(at_uri: str) -> str:
    return at_uri.removeprefix("at://").split("/", 1)[0]


class ChronofairFeed(AtprotoFeed):
    def __init__(self, max_posts: int = 1000):
        # Upper bound on how many merged posts we rank/paginate over per request.
        self.max_posts = max_posts
        self.recommender = ChronoFair()

    def get_poll(
        self, records: list[AtprotoCompactRecord], requester_did: str, followed_dids: list[str]
    ) -> Poll:
        # TODO populate past_recommendations (posts with interactionSeen)

        posts = [record for record in records if not record.is_repost]
        reposts = [
            record
            for record in records
            if record.is_repost
            and record.repost_subject_cid is not None
            and record.repost_subject_uri is not None
        ]

        candidate_entities: dict[str, dict] = {}
        indexed_post_cids: set[str] = set()

        for record in posts:
            indexed_post_cids.add(record.cid)
            candidate_entities[record.cid] = dict(author=record.did, timestamp=record.time_us / 1e6)

        # Reposted posts are candidates too, so they surface even when their author is not followed.
        # The reposted post's own timestamp is not indexed so we use the earliest repost time.
        for record in reposts:
            subject_cid = record.repost_subject_cid
            if subject_cid in indexed_post_cids:
                continue
            repost_time = record.time_us / 1e6
            entity = candidate_entities.get(subject_cid)
            if entity is None:
                candidate_entities[subject_cid] = dict(
                    author=_author_did_from_at_uri(record.repost_subject_uri),
                    timestamp=repost_time,
                )
            elif repost_time < entity["timestamp"]:
                entity["timestamp"] = repost_time

        entities = Entities(
            [
                dict(name=cid, authors=(entity["author"],), timestamp=entity["timestamp"])
                for cid, entity in candidate_entities.items()
            ]
        )

        ratings = Ratings(
            [
                dict(
                    username=record.did,
                    entity_name=record.repost_subject_cid,
                    criterion="repost",
                    timestamp=record.time_us / 1e6,
                )
                for record in reposts
            ]
        )

        follow_timestamp = int(time.time())
        socials = Socials(
            [
                [requester_did, followed_did, "follow", 1.0, follow_timestamp]
                for followed_did in followed_dids
            ],
            columns=["by", "to", "kind", "weight", "timestamp"],
        )

        usernames = (
            {requester_did}
            | set(followed_dids)
            | {record.did for record in reposts}
            | {entity["author"] for entity in candidate_entities.values()}
        )
        users = Users(list(usernames))

        return Poll(users=users, entities=entities, socials=socials, ratings=ratings)

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
        if not records:
            return self._skeleton([], None)

        poll = self.get_poll(
            records=records,
            requester_did=requester_did,
            followed_dids=followed_dids,
        )
        feed_entities = self.recommender(
            poll=poll,
            limit=limit,
            receiver_name=requester_did,
        )

        skeleton_post_by_cid = self._skeleton_post_by_cid(records)
        page = [
            skeleton_post_by_cid[cid]
            for cid in feed_entities.names()
            if cid in skeleton_post_by_cid
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
    def _skeleton_post_by_cid(
        records: list[AtprotoCompactRecord],
    ) -> dict[str, SkeletonFeedPost]:
        """Map each candidate entity cid to its skeleton post.

        Posts from followed accounts map to themselves; posts known only through
        a repost map to the original post with a repost reason.
        """
        posts_by_cid: dict[str, SkeletonFeedPost] = {}
        for record in records:
            if not record.is_repost:
                posts_by_cid[record.cid] = SkeletonFeedPost(post=record.at_uri)
        for record in records:
            if not (record.is_repost and record.repost_subject_cid and record.repost_subject_uri):
                continue
            # Skip subjects we already hold as a direct post or an earlier repost.
            if record.repost_subject_cid not in posts_by_cid:
                posts_by_cid[record.repost_subject_cid] = SkeletonFeedPost(
                    post=record.repost_subject_uri,
                    reason=SkeletonReasonRepost(repost=record.at_uri),
                )
        return posts_by_cid

    @staticmethod
    def _skeleton(
        feed: list[SkeletonFeedPost], cursor: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        return AppBskyFeedGetFeedSkeleton.Response(feed=feed, cursor=cursor)
