from abc import ABC

from atproto_client.models import AppBskyFeedGetFeedSkeleton

from feed_server.indexer.record import AtprotoCompactRecord


class AtprotoFeed(ABC):
    def filter_message_str(self, message: str) -> bool:
        return False

    async def on_message(self, message: dict, record: AtprotoCompactRecord):
        pass

    async def get_feed(
        self, limit: int, cursor: str | None, requester_did: str | None
    ) -> AppBskyFeedGetFeedSkeleton.Response:
        raise NotImplementedError
