import uuid
from typing import Annotated

from atproto_client.models import (
    AppBskyFeedGetFeedSkeleton,
    AppBskyFeedDescribeFeedGenerator,
)
from fastapi import APIRouter, HTTPException, Query
from pydantic import ConfigDict

from ..feeds import ALL_FEEDS
from ..config import FEED_SERVER_DID

router = APIRouter()


class FeedParams(AppBskyFeedGetFeedSkeleton.Params):
    model_config = ConfigDict(strict=False)


@router.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(
    params: Annotated[FeedParams, Query()],
) -> AppBskyFeedGetFeedSkeleton.Response:
    rkey = params.feed.split("/")[-1]
    feed = ALL_FEEDS.get(rkey)
    if feed is None:
        raise HTTPException(404, "Unknown feed")
    skeleton = await feed.get_feed(limit=params.limit or 50, cursor=params.cursor)
    skeleton.req_id = str(uuid.uuid4())
    return skeleton


@router.get("/xrpc/app.bsky.feed.describeFeedGenerator")
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
