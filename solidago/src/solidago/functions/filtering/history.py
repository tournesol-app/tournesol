import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction
from solidago.primitives.datastructure.named_objects import After
from solidago.primitives.time import Date, DateInput, Duration, DurationInput
from .filtering import Filtering


class RemoveRecommendedEntities(PollFunction):
    default_delay: Duration = Duration(weeks=1)

    def __init__(self, 
        delay: DurationInput | None = None, 
        geometric_base: float = 2.,
        username: str | None = None,
        date: DateInput | None = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.delay = self.default_delay if delay is None else Duration(delay)
        self.geometric_base = geometric_base
        self.username = username
        self.date = None if date is None else Date(date)

    def fn(self, poll: Poll) -> Poll:
        assert self.username is not None, f"{type(self).__name__} without receiver"
        if self.date is None:
            return poll
        past = poll.past_recommendations.filters(username=self.username)
        n_recommendations = [len(past.filters(entity_name=e.name)) for e in poll.entities]
        entities = poll.entities.assign(n_recommendations=n_recommendations)
        entities = entities.assign(was_recommended=entities("n_recommendations") > 0)
        recommended_entities = entities.filters(was_recommended=True)
        last_timestamps = np.array([
            np.max([t for t in past.filters(entity_name=e.name)("timestamp")])
            for e in recommended_entities
        ])
        recommended_entities = recommended_entities.assign(last_timestamp=last_timestamps)
        n_recommendations =  recommended_entities("n_recommendations")
        delays = self.delay.total_seconds * np.power(self.geometric_base, n_recommendations - 1)
        availability_timestamps = last_timestamps + delays
        removed_entity_names = recommended_entities\
            .assign(availability_timestamp=availability_timestamps)\
            .filters(availability_timestamp=After(self.date.timestamp()))\
            .names()
        entity_names = set(poll.entities.names()) - set(removed_entity_names)
        return Filtering(entity_names=entity_names)(poll)