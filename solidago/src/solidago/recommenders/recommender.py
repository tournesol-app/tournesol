from solidago.poll import *


class Recommender:
    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        raise NotImplemented
    