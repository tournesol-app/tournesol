import numpy as np

from solidago.poll import *
from .sampler import Sampler

class SamplingWithoutReplacement(Sampler):
    def __call__(self, poll: Poll, limit: int) -> Entities:
        names = poll.entities.names().to_list()
        weights = poll.entities.get_column("weight").to_numpy(np.float64)
        selected_entity_names = np.random.choice(names, limit, False, weights)
        return Entities([poll.entities[name] for name in selected_entity_names])