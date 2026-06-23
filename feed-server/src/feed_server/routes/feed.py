import logging
import time
import uuid
from typing import Annotated

from atproto_client.models import (
    AppBskyFeedGetFeedSkeleton,
    AppBskyFeedDescribeFeedGenerator,
    AppBskyFeedSendInteractions,
    AppBskyFeedDefs,
)
from fastapi import APIRouter, Header, HTTPException, Query
from feed_server.indexer.record import AtprotoSeenRecord
from pydantic import ConfigDict

from ..auth import get_requester_did
from ..db import db
from ..feeds import ALL_FEEDS
from ..config import FEED_SERVER_DID

logger = logging.getLogger(__name__)
router = APIRouter()


class FeedParams(AppBskyFeedGetFeedSkeleton.Params):
    model_config = ConfigDict(strict=False)


@router.get("/xrpc/app.bsky.feed.getFeedSkeleton", response_model_exclude_none=True)
async def get_feed_skeleton(
    params: Annotated[FeedParams, Query()],
    authorization: Annotated[str | None, Header()] = None,
) -> AppBskyFeedGetFeedSkeleton.Response:
    rkey = params.feed.split("/")[-1]
    feed = ALL_FEEDS.get(rkey)
    if feed is None:
        raise HTTPException(404, "Unknown feed")
    requester_did = get_requester_did(authorization)
    logger.info("Feed %s requested by %s", rkey, requester_did)
    skeleton = await feed.get_feed(
        limit=params.limit or 50, cursor=params.cursor, requester_did=requester_did
    )
    skeleton.req_id = str(uuid.uuid4())
    return skeleton


@router.get("/xrpc/app.bsky.feed.describeFeedGenerator", response_model_exclude_none=True)
def describe_feed_generator() -> AppBskyFeedDescribeFeedGenerator.Response:
    return AppBskyFeedDescribeFeedGenerator.Response(
        did=FEED_SERVER_DID,
        feeds=[
            AppBskyFeedDescribeFeedGenerator.Feed(
                uri=f"at://{FEED_SERVER_DID}/app.bsky.feed.generator/{rkey}"
            )
            for rkey in ALL_FEEDS.keys()
        ],
    )


@router.post("/xrpc/app.bsky.feed.sendInteractions")
async def send_interactions(
    body: AppBskyFeedSendInteractions.Data,
    authorization: Annotated[str | None, Header()] = None,
) -> AppBskyFeedSendInteractions.Response:
    requester_did = get_requester_did(authorization)
    if body.feed:
        feed_rkey = body.feed.split("/")[-1]
    else:
        feed_rkey = "none"

    time_us_now = time.time_ns() // 1000
    for interaction in body.interactions:
        logger.info("Received interaction on feed %s: %s", feed_rkey, interaction)
        if (
            requester_did
            and interaction.event == AppBskyFeedDefs.InteractionSeen
            and interaction.item
        ):
            await db.mark_record_as_seen(
                feed_rkey,
                user_did=requester_did,
                seen_record=AtprotoSeenRecord(at_uri=interaction.item, time_us=time_us_now),
            )
    return AppBskyFeedSendInteractions.Response()
