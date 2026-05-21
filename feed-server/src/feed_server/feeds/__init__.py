from .base import AtprotoFeed
from .videos import VideosFeed

ALL_FEEDS: dict[str, AtprotoFeed] = {
    "videos_v0": VideosFeed(),
}
