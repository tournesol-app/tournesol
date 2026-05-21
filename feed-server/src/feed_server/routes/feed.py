from typing import Annotated

from atproto_client.models import (
    AppBskyFeedGetFeedSkeleton,
    AppBskyFeedDescribeFeedGenerator,
)
from fastapi import APIRouter, Query, Request

from ..feeds import ALL_FEEDS

router = APIRouter()


@router.get("/xrpc/app.bsky.feed.getFeedSkeleton")
def get_feed_skeleton(
    params: Annotated[AppBskyFeedGetFeedSkeleton.Params, Query()],
) -> AppBskyFeedGetFeedSkeleton.Response:
    # TODO handle feed id
    feed = ALL_FEEDS["videos_v0"]

    return feed.get_feed(limit=params.limit or 50, cursor=params.cursor)


@router.get("/xrpc/app.bsky.feed.describeFeedGenerator")
def describe_feed_generator(
    request: Request,
) -> AppBskyFeedDescribeFeedGenerator.Response:
    host = request.url.hostname
    did = f"did:web:{host}"
    return AppBskyFeedDescribeFeedGenerator.Response(
        did=did,
        feeds=[
            AppBskyFeedDescribeFeedGenerator.Feed(
                uri=f"at://{did}/app.bsky.feed.generator/videos_v0"
            )
        ],
    )
