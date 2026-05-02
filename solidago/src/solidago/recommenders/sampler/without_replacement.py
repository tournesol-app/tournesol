import numpy as np

from solidago.poll import *
from .sampler import Sampler

class SamplingWithoutReplacement(Sampler):
    def __call__(self, 
        poll: Poll, 
        weighted_entities: Entities, 
        ballots: Scores, 
        limit: int
    ) -> Entities:
        names = weighted_entities.names().to_list()
        weights = weighted_entities.get_column("weight").to_numpy(np.float64)
        selected_entity_names = np.random.choice(names, limit, False, weights)
        return Entities([weighted_entities[name] for name in selected_entity_names])