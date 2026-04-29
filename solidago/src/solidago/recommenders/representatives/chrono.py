from datetime import datetime, timedelta

from solidago.poll import *
from .representative import Representative

class ChronoRepresentative(Representative):
    default_default_lifetime: dict = dict(weeks=1)
    default_criteria_weights: dict = dict(repost=1, report=-1)

    def __init__(self, 
        poll: Poll, 
        user: User | str, 
        default_lifetime: dict | None = None,
        criteria_weights: dict | None = None,
    ):
        super().__init__(poll, user)
        default_lifetime = default_lifetime or self.default_default_lifetime
        self.default_lifetime = timedelta(**default_lifetime)
        self.criteria_weights = criteria_weights or self.default_criteria_weights

    def __call__(self, target_user: User | None = None) -> Scores:
        scores = Scores(keynames=["entity_name"])
        now = datetime.now().second
        reactions = self.poll.ratings.filters(username=self.user.name, criterion=self.criteria_weights.keys())
        for publication in self.poll.entities.filters(author=self.user.name):
            score = (int(publication["date"]) - now)
            scores.append(Score(score), entity_name=publication.name, )


        
        return self.poll.entities