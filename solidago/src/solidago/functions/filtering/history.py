from datetime import timedelta
from typing import Self

import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction
from solidago.primitives.datastructure.named_objects import After
from .filtering import Filtering

import logging
logger = logging.getLogger(__name__)


class RemoveRecommendedEntities(PollFunction):
    default_delay: dict[str, int] = dict(weeks=1)

    def __init__(self, 
        delay: dict[str, int] | None = None, 
        geometric_base: float = 2.,
        receiver: User | None = None,
        time: int | float = float("inf"),
    ):
        self.delay = timedelta(**delay or self.default_delay).seconds
        self.geometric_base = geometric_base
        self.receiver = receiver
        self.time = time

    def fn(self, poll: Poll) -> Poll:
        if self.receiver is None:
            self.log_warning("RemoveRecommendedEntities without receiver. Identity used instead.")
            return poll
        past = poll.past_recommendations.filters(username=self.receiver.name)
        n_recommendations = poll.entities.names().map(lambda e: len(past.filters(entity_name=e)))
        entities = poll.entities.assign(n_recommendations=n_recommendations)
        entities = entities.assign(was_recommended=n_recommendations.to_numpy() > 0)
        entities = entities.filters(was_recommended=True)
        last_dates = entities.names().map(lambda e: past.filters(entity_name=e)("date").max())
        entities = entities.assign(last_date=last_dates)
        availability_dates = last_dates + self.delay * np.power(self.geometric_base, n_recommendations)
        entities = entities.assign(availability_date=availability_dates)
        entities = entities.excludes(availability_date=After(self.time or float("inf")))
        return Filtering(entity_names=entities.names())(poll)