from solidago.poll import *
from .recommender import Recommender


class Chronological(Recommender):
    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        followings = poll.socials.filters(by=username, kind="follow").get_column("to")
        entities = poll.entities.filters(author=followings)
        recommended_entities = poll.past_recommendations.filters(username=username).keys("entity_name")
        entities = entities[list(set(entities.names()) - recommended_entities)]
        assert isinstance(entities, Entities)
        return type(entities)(entities.df.tail(limit)[::-1])
    