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
        assert self.receiver is not None, f"{type(self).__name__} without receiver"
        past = poll.past_recommendations.filters(username=self.receiver.name)
        n_recommendations = [len(past.filters(entity_name=e.name)) for e in poll.entities]
        entities = poll.entities.assign(n_recommendations=n_recommendations)
        entities = entities.assign(was_recommended=entities("n_recommendations") > 0)
        entities = entities.filters(was_recommended=True)
        last_timestamps = np.array([
            np.max([t for t in past.filters(entity_name=e.name)("timestamp")])
            for e in entities
        ])
        entities = entities.assign(last_timestamp=last_timestamps)
        delay = self.delay * np.power(self.geometric_base, n_recommendations)
        availability_timestamps = last_timestamps + delay
        entities = entities.assign(availability_timestamp=availability_timestamps)
        if self.date is not None:
            entities = entities.excludes(availability_timestamp=After(self.date.timestamp()))
        return Filtering(entity_names=entities.names())(poll)