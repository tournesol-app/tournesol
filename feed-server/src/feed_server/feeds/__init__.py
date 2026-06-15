from .base import AtprotoFeed
from .chronofair import ChronofairFeed
from .videos import VideosFeed

ALL_FEEDS: dict[str, AtprotoFeed] = {
    "videos_v0": VideosFeed("videos_v0"),
    "chronofair_v0": ChronofairFeed(),
}
