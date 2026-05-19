from datetime import timedelta

import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction
from solidago.primitives.datastructure.named_objects import After
from solidago.primitives.time import Date, DateInput, Duration, DurationInput
from .filtering import Filtering


class RemoveRecommendedEntities(PollFunction):
    default_delay: dict[str, int] = dict(weeks=1)

    def __init__(self, 
        delay: DurationInput | None = None, 
        geometric_base: float = 2.,
        receiver: User | None = None,
        date: DateInput | None = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.delay = None if delay is None else Duration(delay)
        self.geometric_base = geometric_base
        self.receiver = receiver
        self.date = None if date is None else Date(date)

    def fn(self, poll: Poll) -> Poll:
        if self.receiver is None:
            self.log_warning("RemoveRecommendedEntities without receiver. Identity used instead.")
            return poll
        past = poll.past_recommendations.filters(username=self.receiver.name)
        n_recommendations = poll.entities.names()\
            .map(lambda e: len(past.filters(entity_name=e)))
        entities = poll.entities.assign(n_recommendations=n_recommendations)
        entities = entities.assign(was_recommended=n_recommendations.to_numpy() > 0)
        entities = entities.filters(was_recommended=True)
        last_dates = entities.names().map(lambda e:
            np.max([Date(d).timestamp() for d in past.filters(entity_name=e)("date")])
        )
        entities = entities.assign(last_date=last_dates)
        delay = self.delay * np.power(self.geometric_base, n_recommendations)
        availability_dates = last_dates + delay
        entities = entities.assign(availability_date=availability_dates)
        if self.date is not None:
            entities = entities.excludes(availability_date=After(self.date.timestamp()))
        return Filtering(entity_names=entities.names())(poll)