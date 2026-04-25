import numpy as np

from solidago.poll import *
from .recommender import Recommender


class Chronological(Recommender):
    def __call__(self, 
        poll: Poll, 
        username: str, 
        limit: int, 
        cursor: str | None = None
    ) -> Entities:
        followings = poll.socials.filters(by=username, kind="follow").get_column("to")
        entities = poll.entities.filters(author=followings)
        reposts = poll.ratings.filters(username=list(followings), criterion="repost")
        entity_dates = {e.name: e["date"] for e in entities}
        for repost in reposts:
            entity_name = repost["entity_name"]
            if entity_name in entity_dates:
                entity_dates[entity_name] = repost["timestamp"]
            else:
                date = entity_dates[entity_name]
                entity_dates[entity_name] = np.max(repost["timestamp"], date)
        dates = np.array(entity_dates.values())
        argsort = np.argsort(dates)[::-1][:limit]
        entity_names = np.array(entity_dates.keys())[argsort]
        recommendations = entities[entity_names]
        assert isinstance(recommendations, Entities)
        return recommendations