from datetime import timedelta

import numpy as np

from solidago.poll import *
from solidago.poll import Poll
from solidago.primitives.datastructure.named_objects import After
from .moderation import Moderation


class RemovePastRecommendations(Moderation):
    default_delay: dict[str, int] = dict(weeks=1)

    def __init__(self, 
        delay: dict[str, int] | None = None, 
        geometric_base: float = 2.,
    ):
        self.delay = timedelta(**delay or self.default_delay).seconds
        self.geometric_base = geometric_base
    
    def __call__(self, poll: Poll, receiver: User, time: int) -> Poll:
        poll = poll.copy()
        past = poll.past_recommendations.filters(username=receiver.name)
        n_recommendations = poll.entities.names().map(lambda e: len(past.filters(entity_name=e)))
        entities = poll.entities.assign(n_recommendations=n_recommendations)
        entities = entities.assign(was_recommended=n_recommendations.to_numpy() > 0)
        entities = entities.filters(was_recommended=True)
        last_dates = entities.names()\
            .map(lambda e: past.filters(entity_name=e).get_column("date").max())\
            .to_numpy(np.int64)
        entities = entities.assign(last_date=last_dates)
        availability_dates = last_dates + self.delay * np.power(self.geometric_base, n_recommendations)
        entities = entities.assign(availability_date=availability_dates)
        poll.entities = entities.excludes(availability_date=After(time))
        return poll