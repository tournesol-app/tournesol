import numpy as np

from solidago.poll import *
from .recommender import Recommender


class Chronological(Recommender):
    def __init__(self, follow_kind: str = "follow", rating_criteria: list | None = None):
        self.follow_kind = follow_kind
        self.rating_criteria = rating_criteria or ["repost"]

    def __call__(self, 
        poll: Poll, 
        username: str, 
        limit: int, 
        cursor: str | None = None
    ) -> Entities:
        followings = poll.socials.filters(by=username, kind=self.follow_kind).get_column("to")
        reposts = poll.ratings.filters(username=followings, criterion=self.rating_criteria)
        names = set(poll.entities.filters(author=followings).names()) | reposts.keys("entity_name")
        entities = poll.entities.filters(names)
        entities = entities.excludes(author=username)
        entities = entities.assign(last_date=entities.get_column("date"))
        
        for repost in reposts:
            name = repost["entity_name"]
            if poll.entities[name]["author"] != username:
                last_date = max(repost["timestamp"], entities[name]["last_date"])
                entities[name, "last_date"] = last_date
        
        try:
            offset = 0 if cursor is None else int(cursor)
        except ValueError:
            offset = 0
        
        entities = entities.sort_by("last_date", ascending=False)
        return entities.tail(len(entities) - offset).head(limit)