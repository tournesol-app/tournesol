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
        reposts = poll.ratings.filters(username=list(followings), criterion="repost")
        
        entity_dates = {e.name: e["date"] for e in poll.entities.filters(author=followings)}
        for repost in reposts:
            entity_name = repost["entity_name"]
            if poll.entities[entity_name]["author"] == username:
                continue
            elif entity_name not in entity_dates:
                entity_dates[entity_name] = repost["timestamp"]
            else:
                date = entity_dates[entity_name]
                entity_dates[entity_name] = max(repost["timestamp"], date)
        
        dates = np.array(list(entity_dates.values()))
        argsort = np.argsort(dates)[::-1][:limit]
        entity_names = np.array(list(entity_dates.keys()))[argsort]
        return poll.entities.filters(list(entity_names))