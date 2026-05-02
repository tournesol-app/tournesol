from solidago.primitives.datastructure import Contains
from solidago.poll import *
from .recommender import Recommender


class Chronological(Recommender):
    def __init__(self, follow_kind: str = "follow", rating_criteria: list | None = None):
        self.follow_kind = follow_kind
        self.rating_criteria = rating_criteria or ["repost"]

    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        time: int | None = None,
    ) -> Entities:
        followings = poll.socials.filters(by=receiver_name, kind=self.follow_kind).get_column("to")
        reposts = poll.ratings.filters(username=followings, criterion=self.rating_criteria)
        names = set(poll.entities.filters(authors=Contains(followings)).names())
        entities = poll.entities.filters(names | reposts.keys("entity_name"))
        entities = entities.assign(last_date=entities.get_column("date"))
        
        if receiver_name is not None:
            entities = entities.excludes(authors=Contains(receiver_name))
        
        for repost in reposts:
            name = repost["entity_name"]
            if receiver_name not in poll.entities[name]["authors"].split(","):
                last_date = max(repost["date"], entities[name]["last_date"])
                entities[name, "last_date"] = last_date
        
        try:
            offset = 0 if cursor is None else int(cursor)
        except ValueError:
            offset = 0
        
        entities = entities.sort_by("last_date", ascending=False)
        return entities.tail(len(entities) - offset).head(limit)