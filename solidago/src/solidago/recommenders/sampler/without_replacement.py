from copy import deepcopy

import numpy as np

from solidago.poll import *
from .sampler import Sampler

class SamplingWithoutReplacement(Sampler):
    def __init__(self, criterion: str = "main"):
        super().__init__(criterion)

    def __call__(self, poll: Poll, limit: int) -> Entities:
        scores = poll.global_model(None, self.criterion)
        scores = deepcopy(scores)\
            .add_columns(positive=scores.value > 0)\
            .filters(positive=True)
        if len(scores) == 0:
            return Entities()
        probs = scores("value") / scores("value").sum()
        sample_size = min(limit, len(scores))
        feed = np.random.choice(scores("entity_name"), sample_size, False, probs)
        return poll.entities.filters(feed)