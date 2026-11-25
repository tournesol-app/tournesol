from feed_server.config import FEED_SERVER_ENABLED_FEEDS

from .base import AtprotoFeed
from .chronofair import ChronofairFeed
from .chronofair_d4g import ChronofairD4gFeed
from .videos import VideosFeed


ALL_FEEDS: dict[str, AtprotoFeed] = {
    "videos_v0": VideosFeed("videos_v0"),
    "chronofair": ChronofairFeed("chronofair"),
    "chronofair-d4g": ChronofairD4gFeed("chronofair-d4g"),
}


if FEED_SERVER_ENABLED_FEEDS is None:
    ENABLED_FEEDS = ALL_FEEDS
else:
    ENABLED_FEEDS = {f: ALL_FEEDS[f] for f in FEED_SERVER_ENABLED_FEEDS}
