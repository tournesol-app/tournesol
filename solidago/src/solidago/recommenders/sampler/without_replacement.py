import numpy as np

from solidago.poll import *
from .sampler import Sampler

class SamplingWithoutReplacement(Sampler):
    def __call__(self, entities: Entities, limit: int) -> Entities:
        names = entities.names().to_list()
        weights = entities.get_column("weight").to_numpy(np.float64)
        selected_entity_names = np.random.choice(names, limit, False, weights)
        return entities.filters(selected_entity_names)